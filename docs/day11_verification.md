# Day 11 local verification report

Verified locally on 2026-11-19. No Git add, commit, push, tag, pull request,
cloud deployment, remote change, secret display, or secret storage was performed.

## Files prepared

- `.github/workflows/ci.yml`
- `Dockerfile`
- `Dockerfile.streamlit`
- `.dockerignore`
- `ruff.toml`
- `docs/day11_deployment.md`
- `docs/day11_pr_instructions.md`
- `docs/day11_assignment_tracker.txt`
- README CI badge and Day 11 placeholder section

## Validation

- `ruff check .`: passed.
- `python -m pytest -q`: 16 tests passed.
- Docker CLI: unavailable in the current environment.
- Docker build: not executed and not claimed as successful.
- Public GitHub CI: not run here and not claimed as green.
- Public deployment: not performed and not claimed as live.
- Pull request: not created or merged.

## FastAPI health

`GET /health` remains a lightweight application-process check. It does not
download the embedding model or rebuild Chroma. It reports the configured
provider name, whether a matching provider key is present locally, and
`chroma: not_checked`; it does not claim provider or retrieval readiness.

## Chroma limitation

The Docker image excludes the ignored local Chroma database and feedback data.
Deployment therefore requires explicit indexing and persistent storage to
provide a verified RAG system. The default `/health` response is independent
of those optional RAG dependencies.

## Manual next steps

1. Create and push a Day 11 feature branch.
2. Open a pull request targeting `main`.
3. Wait for the GitHub Ruff, pytest, and Docker checks.
4. Merge only after all required checks pass.
5. Deploy the FastAPI and Streamlit services separately.
6. Add API keys only in hosting secrets.
7. Verify the public backend `/health` URL.
