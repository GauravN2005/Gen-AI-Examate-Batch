import json
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
    all_results = []
    for label, _, top_k, collection in CONFIGS:
        for case in cases:
            started = time.perf_counter()
            try:
                response = answer_with_rag(
                    case["question"],
                    top_k=top_k,
                    collection_name=collection,
                )
                error = None
            except Exception as exc:
                response = None
                error = type(exc).__name__
            all_results.append(
                {
                    "config": label,
                    "case_id": case["id"],
                    "question": case["question"],
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
            not case["should_answer"] and r["response"]["answer"] == ABSTENTION
            for case in cases
            for r in rows
            if r["case_id"] == case["id"] and r["response"]
        )
        answerability = sum(
            (case["should_answer"] and r["response"]["answer"] != ABSTENTION)
            or (not case["should_answer"] and r["response"]["answer"] == ABSTENTION)
            for case in cases
            for r in rows
            if r["case_id"] == case["id"] and r["response"]
        )
        citations = sum(
            bool(r["response"]["citations"])
            for r in valid
            if next(c for c in cases if c["id"] == r["case_id"])["should_answer"]
        )
        result = {
            "answerability": f"{answerability}/15",
            "abstention": f"{abstentions}/3",
            "citation_validity": f"{citations}/{sum(c['should_answer'] for c in cases)}",
            "latency": (
                f"{sum(r['latency_seconds'] for r in rows) / len(rows):.3f}s"
                if rows
                else "Pending"
            ),
            "collection": collection,
            "chunks": counts[label],
            "valid": len(valid),
        }
        lines.append(f"| Answerability accuracy | {result['answerability'] if label == 'A' else ''} | {result['answerability'] if label == 'B' else ''} |")
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
        "| Source relevance | Manual review | Manual review |",
        f"| Average latency | {metrics_a['latency']} | {metrics_b['latency']} |",
        "| Overall winner | Not established automatically | Not established automatically |",
        "",
        "No winner is declared without complete provider results and human review.",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved results to {RESULTS}")
    print(f"Saved comparison to {SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
