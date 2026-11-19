# Day 11: CI/CD and Deployment Guide

## Local development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
streamlit run ui/app.py
```

The backend is at `http://127.0.0.1:8000`; its health endpoint is
`http://127.0.0.1:8000/health`. Streamlit is at `http://localhost:8501`.

## Local quality checks

```bash
ruff check .
python -m pytest -q
docker build -t fundfacts-ci .
```

Run the backend container:

```bash
docker run --rm -p 8000:8000 fundfacts-ci
curl http://127.0.0.1:8000/health
```

Do not provide real API keys to the local Docker health check.

## Render backend

1. Create a Render account and connect this GitHub repository.
2. Create a Docker Web Service.
3. Set the Dockerfile path to `Dockerfile`.
4. Set the service port to `8000` or use Render's `PORT` environment variable.
5. Add secrets manually in the Render dashboard:
   - `LLM_PROVIDER=groq` or `gemini`
   - `GROQ_API_KEY` when Groq is used
   - `GROQ_MODEL=openai/gpt-oss-20b` when supported
   - `GEMINI_API_KEY` and optionally `GEMINI_MODEL` when Gemini is used
6. Do not add keys to source files or commit them.
7. Deploy and verify `/health` using the actual public backend URL.

Only a public HTTP 200 health response proves basic process availability.
It does not prove that an optional provider or Chroma collection is ready.

## Render Streamlit frontend

Create a second Docker Web Service using `Dockerfile.streamlit`.

Set `API_BASE_URL` to the public HTTPS backend URL, for example:
`https://YOUR-BACKEND-NAME.onrender.com`.

Set `PORT=8501`. Do not use `localhost` on the public frontend.

Streamlit feedback is stored locally inside the frontend container and is
ephemeral unless a persistent disk is configured.

## Chroma and model limitations

The repository includes local source records but does not include the ignored
Chroma database or downloaded embedding model in Git or Docker. A deployed RAG
service may require:

- building the collection from `data/records.json`,
- downloading the embedding model,
- a persistent disk for `data/chroma_db`,
- and sufficient memory on the hosting plan.

Do not describe RAG as working until indexing and a live grounded `/ask` call
have been verified.

## README and tracker

After manual deployment:

1. Replace deployment placeholders with verified public URLs.
2. Replace `Public /health status: Not verified` with a dated result.
3. Add the pull request URL and merge status.
4. Enter the assignment-tracker fields shown in
   `docs/day11_pr_instructions.md`.
