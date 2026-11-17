import json
import os
import time
from pathlib import Path
from typing import Any

from app.chunking import load_chunks
from app.rag import ABSTENTION, answer_with_rag
from app.vectorstore import count_chunks, index_chunks


ROOT = Path(__file__).resolve().parent.parent
EVAL_SET = ROOT / "eval" / "eval_set.json"
RESULTS = ROOT / "eval" / "rag_results.json"
SUMMARY = ROOT / "eval" / "rag_comparison.md"
CONFIGS = (
    ("A", 400, 3, "fundfacts_chunks_a"),
    ("B", 800, 5, "fundfacts_chunks_b"),
)
REQUEST_DELAY_SECONDS = float(os.getenv("EVAL_REQUEST_DELAY_SECONDS", "5"))
MAX_RETRIES = int(os.getenv("EVAL_MAX_RETRIES", "4"))
PROVIDER = os.getenv("LLM_PROVIDER", "groq").strip().casefold()
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def _valid_cases(cases: list[dict[str, Any]]) -> None:
    if len(cases) != 15:
        raise ValueError("Evaluation set must contain exactly 15 cases.")
    if cases[5]["question"] != (
        "Which mutual fund will give me the highest guaranteed return next month?"
    ):
        raise ValueError("Q06 must preserve the Day 5 unsupported question.")


def _build() -> dict[str, int]:
    counts = {}
    for label, size, _, collection in CONFIGS:
        chunks = load_chunks(chunk_size=size, overlap=50)
        counts[label] = index_chunks(
            chunks, rebuild=True, collection_name=collection
        )
    return counts


def main() -> int:
    cases = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    _valid_cases(cases)
    counts = _build()
    existing = {}
    if RESULTS.exists():
        try:
            previous = json.loads(RESULTS.read_text(encoding="utf-8"))
            existing = {
                (item["config"], item["case_id"]): item
                for item in previous.get("results", [])
                if item.get("response") is not None
                and not item.get("error")
                and item.get("provider") == PROVIDER
                and item.get("model") == MODEL
            }
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            existing = {}
    all_results = []
    for label, _, top_k, collection in CONFIGS:
        for case in cases:
            key = (label, case["id"])
            if key in existing:
                all_results.append(existing[key])
                continue
            started = time.perf_counter()
            response = None
            error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = answer_with_rag(
                        case["question"],
                        top_k=top_k,
                        collection_name=collection,
                    )
                    break
                except Exception as exc:
                    error = type(exc).__name__
                    if attempt < MAX_RETRIES:
                        delay = REQUEST_DELAY_SECONDS * (2**attempt)
                        print(
                            f"{label}/{case['id']}: retry {attempt + 1} "
                            f"after {delay:.1f}s ({error})"
                        )
                        time.sleep(delay)
            print(f"Completed {label}/{case['id']}")
            all_results.append(
                {
                    "config": label,
                    "case_id": case["id"],
                    "question": case["question"],
                    "provider": PROVIDER,
                    "model": MODEL,
                    "chunk_size": next(
                        config[1] for config in CONFIGS if config[0] == label
                    ),
                    "top_k": top_k,
                    "response": response,
                    "error": error,
                    "latency_seconds": round(time.perf_counter() - started, 4),
                }
            )
            RESULTS.write_text(
                json.dumps(
                    {"collection_counts": counts, "results": all_results},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            if REQUEST_DELAY_SECONDS:
                time.sleep(REQUEST_DELAY_SECONDS)
    RESULTS.write_text(
        json.dumps(
            {"collection_counts": counts, "results": all_results},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    lines = [
        "# RAG Configuration Comparison",
        "",
        "Automated metrics are calculated from recorded outputs. Factual "
        "correctness and source relevance require human review.",
        "",
        "| Metric | Config A (400, k=3) | Config B (800, k=5) |",
        "|---|---:|---:|",
    ]
    for label, size, top_k, collection in CONFIGS:
        rows = [x for x in all_results if x["config"] == label]
        valid = [x for x in rows if x["response"] is not None]
        abstentions = sum(
            not case["should_answer"]
            and r["response"]["answer"] == ABSTENTION
            for case in cases
            for r in rows
            if r["case_id"] == case["id"] and r["response"]
        )
        answerability = sum(
            (
                case["should_answer"]
                and r["response"]["answer"] != ABSTENTION
            )
            or (
                not case["should_answer"]
                and r["response"]["answer"] == ABSTENTION
            )
            for case in cases
            for r in rows
            if r["case_id"] == case["id"] and r["response"]
        )
        citation_validity = sum(
            (
                bool(r["response"]["citations"])
                and all(
                    citation["source_url"] in case["expected_source_urls"]
                    for citation in r["response"]["citations"]
                )
            )
            or (
                not case["should_answer"]
                and not r["response"]["citations"]
            )
            for case in cases
            for r in rows
            if r["case_id"] == case["id"] and r["response"]
        )
        source_relevance = sum(
            any(
                citation["source_url"] in case["expected_source_urls"]
                for citation in r["response"]["citations"]
            )
            for case in cases
            for r in rows
            if r["case_id"] == case["id"]
            and r["response"]
            and case["should_answer"]
        )
        format_validity = sum(
            set(("answer", "citations", "confidence"))
            <= set(r["response"])
            and r["response"]["confidence"] in {"high", "medium", "low"}
            for r in valid
        )
        result = {
            "answerability": f"{answerability}/15",
            "abstention": f"{abstentions}/{sum(not c['should_answer'] for c in cases)}",
            "citation_validity": f"{citation_validity}/15",
            "source_relevance": f"{source_relevance}/{sum(c['should_answer'] for c in cases)}",
            "format_validity": f"{format_validity}/15",
            "latency": (
                f"{sum(r['latency_seconds'] for r in rows) / len(rows):.3f}s"
                if rows
                else "Pending"
            ),
            "collection": collection,
            "chunks": counts[label],
            "valid": len(valid),
        }
        if label == "A":
            metrics_a = result
        else:
            metrics_b = result
    lines = [
        "# RAG Configuration Comparison",
        "",
        f"Config A indexed {metrics_a['chunks']} chunks; Config B indexed {metrics_b['chunks']} chunks.",
        "",
        "| Metric | Config A (400, k=3) | Config B (800, k=5) |",
        "|---|---:|---:|",
        f"| Answerability accuracy | {metrics_a['answerability']} | {metrics_b['answerability']} |",
        f"| Unsupported-question abstention | {metrics_a['abstention']} | {metrics_b['abstention']} |",
        f"| Citation validity (automated) | {metrics_a['citation_validity']} | {metrics_b['citation_validity']} |",
        f"| Source relevance (automated URL match) | {metrics_a['source_relevance']} | {metrics_b['source_relevance']} |",
        f"| Response format validity | {metrics_a['format_validity']} | {metrics_b['format_validity']} |",
        f"| Average latency | {metrics_a['latency']} | {metrics_b['latency']} |",
        "| Overall winner | Determined below | Determined below |",
        "",
        f"Provider: {PROVIDER}; model: {MODEL}; completed cases: "
        f"{metrics_a['valid']}/15 and {metrics_b['valid']}/15.",
        "Winner rule: prioritize answerability, citation validity, source "
        "relevance, and response format; use lower latency as tie-breaker. "
        "Factual correctness still requires human review.",
    ]
    if metrics_a["valid"] == 15 and metrics_b["valid"] == 15:
        def score(metrics: dict[str, Any]) -> tuple[int, int, int, int, float]:
            def numerator(value: str) -> int:
                return int(value.split("/", 1)[0])

            return (
                numerator(metrics["answerability"]),
                numerator(metrics["citation_validity"]),
                numerator(metrics["source_relevance"]),
                numerator(metrics["format_validity"]),
                -float(metrics["latency"].rstrip("s")),
            )

        winner = "Configuration A" if score(metrics_a) >= score(metrics_b) else "Configuration B"
        lines.append(f"**Winner: {winner}**")
    else:
        lines.append("**Winner: Not established; evaluation is incomplete.**")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved results to {RESULTS}")
    print(f"Saved comparison to {SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
