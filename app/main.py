import json
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.llm import LLMConfigurationError, LLMError, generate_chat_response
from app.records import get_by_id, load_records
from app.smart_search import smart_search


app = FastAPI(title="FundFacts API")
PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be blank")
        return value


class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_valid(cls, value: str) -> str:
        if value not in {"high", "medium", "low"}:
            raise ValueError("Confidence must be high, medium, or low")
        return value


def _prompt(filename: str) -> str:
    try:
        return (PROMPT_DIR / filename).read_text(encoding="utf-8")
    except OSError as error:
        raise HTTPException(
            status_code=500, detail="Chat prompt configuration is unavailable."
        ) from error


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "FundFacts"}


@app.get("/records")
def list_records(
    limit: Annotated[int, Query(gt=0)] = 10,
) -> dict[str, Any]:
    records = load_records()
    return {"records": records[:limit], "count": min(limit, len(records))}


@app.get("/records/{record_id}")
def record_by_id(record_id: str) -> dict[str, Any]:
    record = get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.get("/search")
def search_records(
    q: Annotated[str, Query(min_length=1)],
    top_k: Annotated[int, Query(gt=0)] = 5,
) -> dict[str, Any]:
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be blank")
    return {"query": q, "results": smart_search(q, top_k=top_k)}


@app.post("/questions")
def answer_question(request: QuestionRequest) -> dict[str, Any]:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be blank")

    results = smart_search(request.question)
    message = (
        "Relevant FundFacts information retrieved successfully."
        if results
        else "No relevant FundFacts information was found."
    )
    return {"question": request.question, "results": results, "message": message}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    matches = smart_search(request.message, top_k=5)
    context = json.dumps(
        [match["record"] for match in matches],
        ensure_ascii=False,
        indent=2,
    )
    task_prompt = _prompt("task_prompt_v2.txt").replace(
        "{retrieved_context}", context
    )
    try:
        result = generate_chat_response(
            user_message=request.message,
            system_prompt=_prompt("system_prompt.txt"),
            task_prompt=task_prompt,
        )
        return ChatResponse.model_validate(result)
    except LLMConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except LLMError as error:
        raise HTTPException(
            status_code=502, detail="The educational AI provider is unavailable."
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=502, detail="The AI provider returned an invalid response."
        ) from error
