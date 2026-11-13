# Checkpoint 1 – FundFacts FastAPI Verification

## Function Explanation – `smart_search()`

The `smart_search(query, top_k=5)` function searches the records loaded from
`data/sample_records.json` and returns the most relevant matches. It accepts a
text query and a positive maximum number of results. Invalid, blank, or
non-positive inputs return an empty list.

The function uses this real implementation:

```python
query_vector = vectorizer.transform([query.strip()])
scores = cosine_similarity(query_vector, matrix)[0]
ranked_indexes = scores.argsort()[::-1]

return [
    {"record": records[index], "score": float(scores[index])}
    for index in ranked_indexes[:top_k]
    if scores[index] > 0
]
```

Before this part runs, `_build_search_index()` loads the records and combines
each record's concept, definition, example, chapter, and warning into searchable
text. `TfidfVectorizer` converts those texts into numbers. TF-IDF gives more
weight to useful words that distinguish documents and less weight to words that
appear everywhere.

The query is converted into the same kind of vector. Cosine similarity compares
the query vector with every record vector. A higher score means the record is
more similar to the query. The indexes are sorted from highest to lowest, the
top `top_k` records are selected, and each result contains the original record
and its numeric similarity score.

The FastAPI `/search` and `/questions` endpoints call `smart_search()` and
return its ranked results. This is retrieval using TF-IDF; it is not an LLM
answer generator.

## Checkpoint 1 Verification Report

- **Server startup:** Verified with `uvicorn app.main:app`; the server started
  successfully on `http://127.0.0.1:8000`.
- **API documentation:** The FastAPI Swagger UI is available at
  `http://127.0.0.1:8000/docs` and exposes the five required endpoint groups:
  `/health`, `/records`, `/records/{record_id}`, `/search`, and `/questions`.
- **Endpoint tests:** `/health`, `/records?limit=5`, `/records/G01`,
  `/search?q=NAV`, and `POST /questions` returned successful responses.
  `/records/INVALID_ID` returned HTTP 404 as expected.
- **Unresolved errors:** None found during the checkpoint tests.
- **Screenshot:** No screenshot was captured. Open
  `http://127.0.0.1:8000/docs` in a browser and use the browser's screenshot
  command if a visual artifact is required.

