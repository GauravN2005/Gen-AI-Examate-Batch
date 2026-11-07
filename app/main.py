from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.records import get_by_id, load_records
from app.smart_search import smart_search


app = FastAPI(title="FundFacts API")


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


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
