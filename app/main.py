import json
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from langgraph.types import Command

from app.graph import agent_graph
from app.llm import LLMConfigurationError, LLMError, generate_chat_response
from app.rag import answer_with_rag
from app.records import get_by_id, load_records
from app.smart_search import smart_search
from app.vectorstore import query_chunks


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


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, gt=0)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be blank")
        return value


class Citation(BaseModel):
    chunk_id: str
    title: str
    source_url: str
    page: int | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    confidence: str

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_valid(cls, value: str) -> str:
        if value not in {"high", "medium", "low"}:
            raise ValueError("Confidence must be high, medium, or low")
        return value


class AgentRequest(BaseModel):
    thread_id: str = Field(..., min_length=1)
    message: str | None = None
    approved: bool | None = None

    @field_validator("thread_id")
    @classmethod
    def thread_id_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("thread_id cannot be blank")
        return value.strip()

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("message cannot be blank")
        return value.strip() if value is not None else None


class AgentResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    thread_id: str
    status: str
    message: str | None = None
    proposed_action: str | None = None
    proposed_inputs: dict[str, Any] | None = None
    intent: str | None = None
    answer: str | None = None
    citations: list[dict[str, Any]] = Field(default_factory=list)
    confidence: str | None = None
    calculation: dict[str, Any] | None = None
    educational_context: dict[str, Any] | None = None
    abstained: bool | None = None


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


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "FundFacts API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/doc", include_in_schema=False)
def doc_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


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


@app.get("/search/semantic")
def semantic_search(
    q: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(gt=0)] = 5,
) -> dict[str, Any]:
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be blank")
    try:
        results = query_chunks(q, limit=limit)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail="Semantic search is not initialized. Run python -m app.vectorstore.",
        ) from error
    return {"query": q, "results": results, "count": len(results)}


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


@app.get("/chat", include_in_schema=False)
def chat_help() -> dict[str, str]:
    return {
        "message": "Use POST /chat with a JSON body containing a message.",
        "docs": "/docs",
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        result = answer_with_rag(request.question, top_k=request.top_k)
        return AskResponse(question=request.question, **result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except LLMConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except LLMError as error:
        raise HTTPException(
            status_code=502, detail="The educational AI provider is unavailable."
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail="RAG retrieval is not initialized. Build the Chroma index first.",
        ) from error


@app.post("/agent")
def agent(request: AgentRequest) -> AgentResponse:
    config = {"configurable": {"thread_id": request.thread_id}}
    is_approval = request.message is None and request.approved is not None
    is_new_request = request.message is not None and request.approved is None
    if not is_approval and not is_new_request:
        raise HTTPException(
            status_code=422,
            detail="Provide either message for a new request or approved for a pending request.",
        )
    try:
        if is_new_request:
            result = agent_graph.invoke({"message": request.message}, config)
        else:
            state = agent_graph.get_state(config)
            if not state.values or "approval" not in state.next:
                raise HTTPException(
                    status_code=404,
                    detail="No pending approval exists for this thread.",
                )
            result = agent_graph.invoke(Command(resume=request.approved), config)
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=503, detail="The agent workflow is unavailable."
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500, detail="The agent request could not be completed."
        ) from error

    interrupts = result.get("__interrupt__", [])
    if interrupts:
        pending = interrupts[0]
        value = getattr(pending, "value", pending)
        return AgentResponse.model_validate({"thread_id": request.thread_id, **value})
    response = result.get("response")
    if not response:
        raise HTTPException(status_code=500, detail="The agent returned no response.")
    return AgentResponse.model_validate({"thread_id": request.thread_id, **response})
