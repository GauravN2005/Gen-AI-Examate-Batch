# Day 12 Fix: Merge a PR and Deploy to Render

This guide completes the two evidence items missing from the partial Day 12:
a merged pull request and a verified public `/health` URL.

## Create, push, and merge the PR

Run these commands manually from the repository root:

```bash
git status
git switch -c fix/day12-live-deployment
git add docs/day12_fix_guide.md README.MD render.yaml Dockerfile .dockerignore
git diff --cached --check
git diff --cached --stat
git commit -m "Complete Day 12 live deployment evidence"
git push -u origin fix/day12-live-deployment
```

Add the exact files changed in this workspace before staging. Do not stage `.env`,
`data/feedback.jsonl`, `data/agent_memory.sqlite3*`, or Chroma files.

1. Open the GitHub repository.
2. Create a pull request from `fix/day12-live-deployment` to `main`.
3. Wait for all required GitHub Actions checks: Ruff, pytest, and Docker build.
4. Open the Actions run and save its successful URL.
5. Merge the PR only after every required check is green.
6. Save the merged PR URL and merge date.
7. Verify that the workflow also runs successfully on `main`.

Do not invent a PR URL or mark the PR merged until GitHub confirms it.

## Deploy the backend with Render

1. Open [https://dashboard.render.com/](https://dashboard.render.com/).
2. Create a new Blueprint or select New > Blueprint.
3. Connect `GauravN2005/Gen-AI-Examate-Batch`.
4. Use `render.yaml` from the repository root.
5. Review the generated `fundfacts-api` Docker Web Service.
6. Enter `GROQ_API_KEY` or `GEMINI_API_KEY` securely in Render.
7. Set `LLM_PROVIDER` to the matching provider.
8. Do not place real secrets in YAML or source files.
9. Deploy and wait for the service to become live.
10. Open `<backend-url>/health`.
11. Verify HTTP 200 and copy the exact Render URL.

The health endpoint proves basic application availability. It does not prove
that Groq/Gemini or Chroma RAG is ready.

## Chroma and embeddings limitation

The Docker image does not copy local Chroma data or feedback data. A deployed
RAG service needs a prebuilt index or an explicit one-time indexing command,
plus persistent storage and sufficient memory. Publicly testing `/health`
alone is insufficient to verify RAG.

For a FastAPI-only deployment, the expected provider variables are:

- `LLM_PROVIDER=groq` or `LLM_PROVIDER=gemini`
- `GROQ_API_KEY` for Groq
- `GROQ_MODEL=openai/gpt-oss-20b` when Groq is used
- `GEMINI_API_KEY` for Gemini
- `GEMINI_MODEL` optionally
- `PORT` is supplied by Render

## Update README after verification

Replace placeholders only with values confirmed by GitHub and Render:

- Merged PR URL
- Public backend URL
- Public Streamlit URL, if deployed
- Public `/health` URL
- Public `/health` HTTP status and verification date
