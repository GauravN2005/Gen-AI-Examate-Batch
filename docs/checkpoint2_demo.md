# Checkpoint 2 live demo

## Start the application

Install dependencies, then run these commands in separate terminals:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
streamlit run ui/app.py
```

Open the UI at `http://localhost:8501`. The backend documentation is at
`http://127.0.0.1:8000/docs`.

## Demo flow

1. Ask **“What is NAV?”** and show the grounded answer.
2. Expand **Sources and citations** and open the returned official SEBI URL.
3. Click **👍 Helpful**. Feedback is saved locally in `data/feedback.jsonl`.
4. Ask **“Which mutual fund should I buy?”**. The deterministic
   **Education, not advice** card appears before any backend model call.
5. Expand the verified **Choosing a Mutual Fund Scheme** resource.
6. Expand **Five Rules That Protect You** and show the fraud checklist.
7. Ask **“Calculate a monthly SIP of 1000 with NAVs 10, 8, 12, 10”**.
8. Review the proposed inputs, click **Approve**, and show the calculation.
   Click **Reject** instead to demonstrate cancellation.

If the backend or provider is unavailable, the UI shows an understandable
error. Do not present a cached or mocked answer as a live provider response.
The `checkpoint-2` tag must be created manually after review.
