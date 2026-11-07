from functools import lru_cache
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records


SEARCH_FIELDS = (
    "concept",
    "plain_definition",
    "example",
    "module_chapter",
    "risk_warning",
)


def _record_text(record: dict[str, Any]) -> str:
    return " ".join(str(record.get(field, "")) for field in SEARCH_FIELDS)


@lru_cache(maxsize=1)
def _build_search_index() -> tuple[
    list[dict[str, Any]], TfidfVectorizer | None, Any
]:
    records = load_records()
    if not records:
        return [], None, None

    vectorizer = TfidfVectorizer()
    try:
        matrix = vectorizer.fit_transform(
            _record_text(record) for record in records
        )
    except ValueError:
        return records, None, None
    return records, vectorizer, matrix


def smart_search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return records ranked by TF-IDF cosine similarity to ``query``."""
    if not isinstance(query, str) or not query.strip() or top_k <= 0:
        return []

    records, vectorizer, matrix = _build_search_index()
    if not records or vectorizer is None:
        return []

    query_vector = vectorizer.transform([query.strip()])
    if query_vector.nnz == 0:
        return []

    scores = cosine_similarity(query_vector, matrix)[0]
    ranked_indexes = scores.argsort()[::-1]

    return [
        {"record": records[index], "score": float(scores[index])}
        for index in ranked_indexes[:top_k]
        if scores[index] > 0
    ]
