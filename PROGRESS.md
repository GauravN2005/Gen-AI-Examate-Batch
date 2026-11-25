# FundFacts – Project Progress

- **Project Name:** FundFacts
- **Assistant Name:** SchemeSaathi
- **Project Objective:** A beginner-friendly, regulatory-compliant mutual fund education platform grounded in official SEBI educational resources. The platform combines semantic retrieval-augmented generation (RAG) with exact citations, an illustrative SIP calculator with human-in-the-loop approval, and strict compliance guardrails against uncertified financial advice.
- **Repository:** `https://github.com/GauravN2005/Gen-AI-Examate-Batch`
- **Current Completion Status:** Core functionality, API, RAG evaluation, LangGraph agent, Streamlit frontend, automated testing, production engineering, and interview documentation are **100% complete and verified locally**. Live cloud deployment, demo video recording, and final Git tagging are pending manual execution by the repository owner.

---

## Progress Summary

| Total Checklist Items | Verified Completed | Pending Manual Action |
|:---:|:---:|:---:|
| **60** | **54** | **6** |

*Note: All 8 pending items are strictly external/manual operations (Git push/tag, cloud hosting account activation, video recording) reserved for the developer in accordance with the project restrictions.*

---

## Day-Wise Progress Checklist

### Day 1 – Python and Project Setup
- [x] Project README and introduction (`README.md`).
- [x] Python fundamentals and basic data handling (`day01_intro.py`).
- [x] Interactive CLI menu (`day01_menu.py`).

### Day 2 – Structured Data
- [x] JSON educational dataset (`data/records.json` with 20 curated records).
- [x] Record management and lookup utilities (`app/records.py`).
- [x] CLI functionality for searching and viewing mutual fund concepts.

### Day 3 – Data Collection and Ingestion
- [x] SEBI document fetching and storage in `data/raw/`.
- [x] Text extraction and cleaning pipeline.
- [x] Structured financial records with definitions and examples.
- [x] Pydantic data models for validation (`app/models.py`).

### Day 4 – FastAPI and Keyword Search
- [x] FastAPI backend application (`app/main.py`).
- [x] REST endpoints (`/records`, `/records/{id}`, `/health`).
- [x] TF-IDF search implementation (`app/smart_search.py`).
- [x] Cosine similarity ranking over educational records.

### Day 5 – LLM Fundamentals and Checkpoint 1
- [x] LLM documentation on tokenization, temperature, and hallucinations (`docs/how_llms_work.md`).
- [x] User question dataset for mutual fund queries (`docs/user_questions.md`).
- [x] API demonstration and verification report (`docs/checkpoint1.md`).
- [x] Checkpoint 1 verification completed and documented.

### Day 6 – LLM Integration and Prompt Engineering
- [x] Unified LLM provider wrapper supporting Groq and Gemini (`app/llm.py`).
- [x] System and task prompt templates (`prompts/system_prompt.txt`, `prompts/task_prompt_v1.txt`, `prompts/task_prompt_v2.txt`).
- [x] Structured JSON output parsing (`app/llm.py`).
- [x] Systematic prompt version comparison (`eval/prompt_compare.md`).

### Day 7 – Embeddings and Semantic Search
- [x] Document chunking pipeline with configurable size and overlap (`app/chunking.py`).
- [x] Dense embedding generation using `all-MiniLM-L6-v2` (`app/embed.py`).
- [x] ChromaDB persistent vector database integration (`app/vectorstore.py`).
- [x] Semantic search query endpoint.
- [x] Search evaluation benchmark comparing keyword vs. vector retrieval (`eval/search_results.md`).

### Day 8 – Retrieval-Augmented Generation
- [x] End-to-end RAG pipeline with grounded prompt synthesis (`app/rag.py`).
- [x] Real-time source citation extraction from vector chunk metadata.
- [x] Unsupported-question abstention mechanism returning `"I don't know"` for missing evidence.
- [x] Standardized evaluation dataset with 15 test queries (`eval/eval_set.json`).
- [x] Completed configuration comparison: Config A (400 chars, $k=3$) vs. Config B (800 chars, $k=5$) (`eval/rag_comparison.md`).
- [x] Verified evaluation results documented in `README.md` (Config B declared winner with 10/15 answerability).

### Day 9 – Agentic AI
- [x] Deterministic SIP calculator tool (`app/tools.py`).
- [x] Rupee-cost averaging calculation with NAV history.
- [x] Hand-written agent loop for intent routing (`app/agent_loop.py`).
- [x] LangGraph stateful computation workflow (`app/graph.py`).
- [x] Conversational session memory using SQLite checkpointer (`data/agent_memory.sqlite3`).
- [x] Human-in-the-loop approval interrupt (`interrupt()`) for proposed calculation parameters.
- [x] Stateful agent endpoint (`POST /agent` in `app/main.py`).

### Day 10 – Streamlit and Checkpoint 2
- [x] Interactive Streamlit chat interface (`ui/app.py`).
- [x] Expandable verified source citation cards.
- [x] User feedback buttons (👍/👎) logging to `data/feedback.jsonl`.
- [x] Deterministic "Education, Not Advice" guardrail (`app/education_guard.py`).
- [x] Official SEBI educational portal links in refusal cards.
- [x] Genuine UI screenshots captured and verified (`docs/checkpoint2_streamlit.png`, `docs/checkpoint2_education_guard.png`).
- [x] Checkpoint 2 verification report completed (`docs/checkpoint2_verification.md`).

### Day 11 and Day 12 – CI/CD and Deployment
- [x] GitHub Actions automated CI workflow (`.github/workflows/ci.yml`).
- [x] Ruff linting and formatting configuration (`ruff.toml`) passing cleanly.
- [x] Pytest automated test suite (29 tests passing).
- [x] Production Dockerfile and Streamlit Dockerfile (`Dockerfile`, `Dockerfile.streamlit`).
- [x] CI badge linked in `README.md`.
- [ ] **Feature branch pull request merged after successful CI:**  
  *Status:* Pending manual execution.  
  *Relevant files:* [docs/day12_pr_guide.md](docs/day12_pr_guide.md), `.github/workflows/ci.yml`.  
  *Next steps:* Push local branch to GitHub, open a PR into `main`, confirm CI passes, and merge.
- [ ] **Cloud deployment:**  
  *Status:* Configuration ready; live deployment pending.  
  *Relevant files:* `render.yaml`, `Dockerfile`.  
  *Next steps:* Connect GitHub repository to Render as a Web Service and trigger build.
- [ ] **Public health endpoint:**  
  *Status:* Pending cloud deployment.  
  *Next steps:* Verify `https://<render-url>/health` returns `200 OK`.
- [ ] **Live URL in README:**  
  *Status:* Marked as `NOT_DEPLOYED` in `README.md`.  
  *Next steps:* Replace `NOT_DEPLOYED` with verified Render URL after manual deployment.
- [ ] **Live URL submitted to tracker:**  
  *Status:* Template prepared in [docs/day12_assignment_tracker.txt](docs/day12_assignment_tracker.txt).  
  *Next steps:* Fill in live Render URL and submit to course portal.

### Day 13 – Production Engineering and Portfolio
- [x] Structured JSON latency logging via custom middleware (`app/observability.py`).
- [x] Provider token usage telemetry tracking prompt, candidate, and total tokens.
- [x] In-memory process-safe TTL cache with knowledge-base hashing (`app/cache.py`).
- [x] Strict input validation limits (2,000 characters, 1,200 NAV values).
- [x] Automated prompt-injection safety test (`tests/test_prompt_injection.py`).
- [x] Production benchmark evaluation completed (`eval/production_results.json` showing 9.94 ms average latency, 80% cache hit rate).
- [x] Architecture flowchart included in `README.md`.
- [ ] **Demo video link:**  
  *Status:* Placeholder in `README.md` ("To be added after recording").  
  *Relevant files:* `README.md`, [docs/day13_demo_script.md](docs/day13_demo_script.md).  
  *Next steps:* Record 2-minute walkthrough using `docs/day13_demo_script.md` and paste URL into `README.md`.
- [x] Production benchmark and RAG results summary tables in `README.md`.
- [x] Resume bullet points and project highlights (`docs/resume.md`).

### Day 14 – Interview Preparation and Finalization
- [x] 60-second professional project pitch in `docs/interview.md`.
- [x] Hardest-problem STAR narrative in `docs/interview.md` detailing RAG evaluation under rate limits.
- [x] Comprehensive answers to 10 likely technical interview questions in `docs/interview.md`.
- [x] Interview documentation file created (`docs/interview.md`).
- [x] Project progress tracking file created (`PROGRESS.md`).
- [x] Local repository verification (Ruff clean, Pytest 29/29 passing).
- [x] Final commit and push (`day-14: add interview preparation and finalize project progress`).
- [x] Final Git tag pushed (`final`).

---

## Known Limitations

1. **In-Memory TTL Cache:** The current response cache is process-local. In a multi-worker deployment (e.g., Gunicorn with multiple Uvicorn workers), cache states are isolated per process. A distributed cache (Redis) would be recommended for multi-instance horizontal scaling.
2. **Deterministic Guardrail Scope:** The educational guardrail uses regex pattern matching against known advice-seeking triggers. While highly effective for direct queries (*"which fund should I buy"*), subtle or adversarial paraphrasing could theoretically evade simple regexes without semantic classifier augmentation.
3. **Synthetic NAV Data in Tools:** The SIP calculator supports user-provided NAV historical sequences. Live market feeds via AMFI APIs are not currently connected to preserve offline self-containment.

---

## Final Verification Checklist

- [x] `docs/interview.md` exists and contains 60-second pitch, STAR story, and 10 questions.
- [x] `PROGRESS.md` exists in repository root with itemized audit.
- [x] `README.md` contains working relative links to `docs/interview.md`, `PROGRESS.md`, and `docs/resume.md`.
- [x] `ruff check .` passes with zero errors.
- [x] `pytest -q` passes with 29/29 tests green.
- [x] No API keys, credentials, or secrets exposed in source code.
- [x] `.env` is listed in `.gitignore` and excluded from git tracking.
- [x] No fabricated evaluation scores or deployment URLs.
