# Day 12 Deployment Guide

## Render backend

1. Create a Render account.
2. Connect the GitHub repository.
3. Create a Docker Web Service.
4. Select `Dockerfile` and allow the service to use Render's `PORT`.
5. Set `LLM_PROVIDER` to `groq` or `gemini`.
6. Add only the matching provider key:
   - Groq: `GROQ_API_KEY` and optional `GROQ_MODEL`
   - Gemini: `GEMINI_API_KEY` and optional `GEMINI_MODEL`
7. Deploy and open the public `/health` endpoint.
8. Verify a public HTTP 200 response; a health response does not prove RAG
   provider or Chroma readiness.

The repository also contains `render.yaml` for a backend blueprint. Review it
before applying it because secret values must still be entered in the Render
dashboard, and no deployment will be performed from this workspace.

## Render Streamlit frontend

1. Create a second Docker Web Service.
2. Use `Dockerfile.streamlit`.
3. Set `API_BASE_URL` to the public HTTPS backend URL.
4. Set `PORT=8501`.
5. Do not use `localhost` for the public backend.
6. Test `/health`, an educational chat, citations, and the recommendation guard.

Streamlit feedback is stored locally in `data/feedback.jsonl`. Cloud storage is
ephemeral unless a persistent disk or external database is configured.

## Chroma and embeddings

The Docker image deliberately excludes local Chroma data and embedding caches.
Before calling RAG a working deployment should:

- contain or initialize `data/records.json`,
- index chunks with `python -m app.vectorstore`,
- download the configured Sentence Transformers model,
- and use persistent storage for `data/chroma_db`.

Do not present RAG as live until a real grounded `/ask` request succeeds.

## Public verification

Record only URLs actually confirmed:

- Backend URL:
- Public `/health` URL:
- Frontend URL:
- Verification date:
- `/health` HTTP status:
