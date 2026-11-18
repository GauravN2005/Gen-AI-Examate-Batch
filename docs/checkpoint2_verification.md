# Checkpoint 2 Verification Report

Verified locally on 2026-11-18. No Git add, commit, push, tag, deployment,
remote change, API-key display, or secret storage was performed.

## Files

- `ui/app.py` - Streamlit chat UI.
- `app/education_guard.py` - deterministic education-not-advice guard.
- `app/feedback_store.py` - safe, replaceable JSON Lines feedback storage.
- `app/main.py` - guard checks at `/ask`, `/chat`, and `/agent`.
- `tests/test_education_guard.py` - guard and resource tests.
- `tests/test_feedback_store.py` - feedback update and validation tests.
- `docs/checkpoint2_demo.md` - live demo script.
- `docs/checkpoint2_streamlit.png` - live NAV answer with expanded citations.
- `docs/checkpoint2_education_guard.png` - live refusal-card capture.
- `README.MD` - Day 10 instructions and screenshot references.

## Automated verification

All 14 tests passed:

- SIP NAV, assumed-return, and validation tests.
- Manual-agent routing tests.
- LangGraph approval, rejection, and thread-isolation tests.
- Education guard allow/block tests.
- Fixed verified-resource tests.
- Feedback update/no-duplicate tests.
- Invalid feedback validation test.

Python syntax compilation passed for the UI, guard, feedback store, and API.
Git whitespace validation passed.

## Live verification

- FastAPI health: `200 healthy`.
- Live `POST /ask` for "What is NAV?": `200`, answer returned, 2 citations
  returned from the official SEBI chapter.
- Live blocked `POST /ask` for "Which mutual fund should I buy?": `400`,
  fixed heading `Education, not advice`.
- Live `POST /agent` SIP request: `200`, status `approval_required`; no
  calculation executes until approval or rejection.
- Streamlit UI rendered at a local port and accepted live chat input.
- Live NAV answer and two official SEBI citation links were captured in
  `docs/checkpoint2_streamlit.png`.
- The fixed refusal card was captured in
  `docs/checkpoint2_education_guard.png`.

## SEBI resource verification

The following resources were loaded from official SEBI investor education
pages and are linked by the fixed guard:

- [Choosing a Mutual Fund Scheme](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-02.html)
- [Five Rules That Protect You](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-04.html)

The fraud checklist is grounded in SEBI's verified guaranteed-return,
intermediary verification, credential, urgency, and reporting rules.

## Remaining manual step

Review the screenshots and run:

```bash
uvicorn app.main:app --reload
streamlit run ui/app.py
```

Then personally create the `checkpoint-2` tag. Keep `data/feedback.jsonl` and
`.env` local and ignored.
