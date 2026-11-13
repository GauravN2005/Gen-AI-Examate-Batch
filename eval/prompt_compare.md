# FundFacts Prompt Comparison

This evaluation uses the same ten questions from
[`docs/user_questions.md`](../docs/user_questions.md), the same configured
Gemini model, and the two task prompts in `prompts/`.

**Status: Pending – Gemini API key required**

No Gemini responses or qualitative scores are fabricated. Run
`python eval/compare_prompts.py` after configuring `GEMINI_API_KEY` to collect
responses. Automated checks cover response shape; factual correctness,
grounding, clarity, risk warnings, and the better prompt require human review.

| Question | Prompt V1 result | Prompt V2 result | Better version | Reason |
|---|---|---|---|---|
| Q1 | Pending | Pending | Human review | Gemini API key required |
| Q2 | Pending | Pending | Human review | Gemini API key required |
| Q3 | Pending | Pending | Human review | Gemini API key required |
| Q4 | Pending | Pending | Human review | Gemini API key required |
| Q5 | Pending | Pending | Human review | Gemini API key required |
| Q6 | Pending | Pending | Human review | Must acknowledge unsupported future-return request |
| Q7 | Pending | Pending | Human review | Gemini API key required |
| Q8 | Pending | Pending | Human review | Gemini API key required |
| Q9 | Pending | Pending | Human review | Gemini API key required |
| Q10 | Pending | Pending | Human review | Gemini API key required |

Review each answer for factual correctness, beginner clarity, grounding in
FundFacts records, unsupported claims, appropriate risk warnings, and valid
JSON. Prompt V2 should be preferred for answers that benefit from retrieved
evidence, especially Q6.
