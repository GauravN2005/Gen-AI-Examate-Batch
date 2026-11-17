# RAG Configuration Comparison

Config A indexed 61 chunks; Config B indexed 44 chunks.

| Metric | Config A (400, k=3) | Config B (800, k=5) |
|---|---:|---:|
| Answerability accuracy | 9/15 | 10/15 |
| Unsupported-question abstention | 2/2 | 2/2 |
| Citation validity (automated) | 5/15 | 5/15 |
| Source relevance (automated URL match) | 7/13 | 8/13 |
| Response format validity | 15/15 | 15/15 |
| Average latency | 1.375s | 6.517s |
| Overall winner | Determined below | Determined below |

Provider: groq; model: openai/gpt-oss-20b; completed cases: 15/15 and 15/15.
Winner rule: prioritize answerability, citation validity, source relevance, and response format; use lower latency as tie-breaker. Factual correctness still requires human review.
**Winner: Configuration B**
