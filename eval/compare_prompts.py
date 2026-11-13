import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "docs" / "user_questions.md"
PROMPT_DIR = ROOT / "prompts"
RESULTS_FILE = ROOT / "eval" / "prompt_results.json"
COMPARISON_FILE = ROOT / "eval" / "prompt_compare.md"


def load_questions() -> list[str]:
    text = QUESTIONS_FILE.read_text(encoding="utf-8")
    questions = []
    for match in re.finditer(r"^## (\d+)\..*?(?=^## \d+\.|\Z)", text, re.M | re.S):
        question = re.search(
            r"\*\*User question:\*\*\s*(.+?)(?=\n\n\*\*Related)",
            match.group(0),
            re.S,
        )
        if question:
            questions.append(" ".join(question.group(1).split()))
    if len(questions) != 10:
        raise ValueError("Expected exactly ten Day 5 questions.")
    return questions


def write_pending(questions: list[str]) -> None:
    rows = [
        "| Question | Prompt V1 result | Prompt V2 result | Better version | Reason |",
        "|---|---|---|---|---|",
    ]
    for number, question in enumerate(questions, 1):
        reason = (
            "Must acknowledge unsupported future-return request"
            if number == 6
            else "Gemini API key required"
        )
        rows.append(f"| Q{number} | Pending | Pending | Human review | {reason} |")
    COMPARISON_FILE.write_text(
        "# FundFacts Prompt Comparison\n\n"
        "This evaluation uses the ten questions from "
        "[`docs/user_questions.md`](../docs/user_questions.md).\n\n"
        "**Status: Pending – Gemini API key required**\n\n"
        "No Gemini responses or qualitative scores are fabricated. Run "
        "`python eval/compare_prompts.py` after configuring the key. "
        "Automated checks cover response shape; human review is required for "
        "correctness, grounding, clarity, risk warnings, and prompt quality.\n\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


def run() -> int:
    load_dotenv(ROOT / ".env")
    questions = load_questions()
    if not os.getenv("GEMINI_API_KEY", "").strip():
        write_pending(questions)
        print(
            "Evaluation pending: set GEMINI_API_KEY in .env before running "
            "the Gemini comparison."
        )
        return 0

    sys.path.insert(0, str(ROOT))
    from app.llm import generate_chat_response
    from app.smart_search import smart_search

    system_prompt = (PROMPT_DIR / "system_prompt.txt").read_text(
        encoding="utf-8"
    )
    prompts = {
        version: (PROMPT_DIR / f"task_prompt_{version}.txt").read_text(
            encoding="utf-8"
        )
        for version in ("v1", "v2")
    }
    results: list[dict[str, Any]] = []
    for number, question in enumerate(questions, 1):
        item: dict[str, Any] = {"question": number, "text": question}
        context = json.dumps(
            [match["record"] for match in smart_search(question, top_k=5)],
            ensure_ascii=False,
            indent=2,
        )
        for version, prompt in prompts.items():
            try:
                item[version] = generate_chat_response(
                    user_message=question,
                    system_prompt=system_prompt,
                    task_prompt=prompt.replace("{retrieved_context}", context),
                )
                item[f"{version}_automated_check"] = "Valid JSON object returned"
            except Exception as error:
                item[version] = None
                item[f"{version}_error"] = str(error)
        results.append(item)

    RESULTS_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved provider results to {RESULTS_FILE}")
    print("Human review is required; no qualitative scores were generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
