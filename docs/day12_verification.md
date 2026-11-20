# Day 12 Local Verification Report

Verified locally on 2026-11-20. No Git, pull request, cloud deployment,
secret, or remote operation was performed.

## Local checks

- Ruff: passed.
- Pytest: 19 tests passed.
- FastAPI `/health`: HTTP 200 locally.
- Streamlit: local process started and `/_stcore/health` returned `ok`.
- GitHub Actions YAML: parsed successfully.
- Render YAML: parsed successfully.
- `.env`, feedback, and local Chroma memory are ignored.
- Docker CLI: detected, version 29.9.3.
- Docker build: blocked because the Docker Desktop Linux engine/daemon is not running.

## CI readiness

The CI workflow runs Ruff, pytest, and a real `docker build -t fundfacts-ci .`
on pull requests to `main` and pushes to `main`. It uses least-privilege
`contents: read` permissions.

GitHub Actions has not run locally, so CI is not claimed green.

## Deployment readiness

The FastAPI Docker image:

- listens on `0.0.0.0`,
- uses `PORT` with port 8000 as the fallback,
- exposes `/health`,
- does not copy `.env`,
- excludes local Chroma and feedback data,
- and does not rebuild the RAG collection during application startup.

The Streamlit Docker image uses `API_BASE_URL` and the public backend URL must
be configured manually. Cloud RAG readiness remains unverified until a
prebuilt/persistent Chroma index and live provider credentials are deployed.

## Manual steps

1. Start Docker Desktop or the Docker engine.
2. Run `docker build -t fundfacts-ci .`.
3. Create a feature branch and push it manually.
4. Open a pull request targeting `main`.
5. Wait for all CI checks to pass.
6. Merge only after CI is green.
7. Create and deploy the Render backend and frontend services.
8. Verify the public `/health` URL and a real `/ask` response.
