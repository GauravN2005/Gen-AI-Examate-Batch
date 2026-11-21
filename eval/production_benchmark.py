"""Repeatable mocked production-style benchmark for cache and request latency."""

from __future__ import annotations

import json
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import ASK_CACHE, app

RESULTS_FILE = Path(__file__).resolve().parent / "production_results.json"
REQUEST_COUNT = 20
WORKLOAD = [
    "What is NAV?",
    "What is SIP?",
    "How does Riskometer work?",
    "What is an expense ratio?",
]


def percentile(values: list[float], percentile_value: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile_value)
    return ordered[index]


def main() -> int:
    client = TestClient(app)
    ASK_CACHE.clear()
    latencies: list[float] = []
    failed = 0

    with patch("app.main.answer_with_rag") as answer:
        answer.return_value = {
            "answer": "This is a controlled benchmark educational response.",
            "citations": [],
            "confidence": "medium",
            "_usage": None,
        }
        for index in range(REQUEST_COUNT):
            question = WORKLOAD[index % len(WORKLOAD)]
            started = time.perf_counter()
            response = client.post(
                "/ask",
                json={"question": question, "top_k": 3},
                headers={"X-Request-ID": f"benchmark-{index}"},
            )
            latencies.append((time.perf_counter() - started) * 1000)
            if response.status_code != 200:
                failed += 1

    stats = ASK_CACHE.stats()
    hit_rate = (stats["hits"] / stats["total"] * 100) if stats["total"] else 0
    miss_rate = (stats["misses"] / stats["total"] * 100) if stats["total"] else 0
    result = {
        "evaluation_date": datetime.now(UTC).isoformat(),
        "environment": "local TestClient",
        "location": "local",
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "model": (
            os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
            if os.getenv("LLM_PROVIDER", "gemini").strip().casefold() == "groq"
            else os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        ),
        "measurement_type": "mocked",
        "llm_calls": "mocked",
        "requests_tested": REQUEST_COUNT,
        "cold_cache": True,
        "warm_cache": True,
        "average_latency_ms": round(statistics.mean(latencies), 3),
        "median_latency_ms": round(statistics.median(latencies), 3),
        "p95_latency_ms": round(percentile(latencies, 0.95), 3),
        "cache_hit_rate_percent": round(hit_rate, 3),
        "cache_miss_rate_percent": round(miss_rate, 3),
        "failed_request_count": failed,
        "average_input_tokens": None,
        "average_output_tokens": None,
        "cache_ttl_seconds": ASK_CACHE.ttl_seconds,
        "cache_max_entries": ASK_CACHE.max_entries,
    }
    RESULTS_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
