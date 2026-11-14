import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "docs" / "user_questions.md"
OUTPUT_FILE = ROOT / "eval" / "search_results.md"
RAW_RESULTS = ROOT / "eval" / "search_results.json"


def load_questions() -> list[str]:
    text = QUESTIONS_FILE.read_text(encoding="utf-8")
    values = []
    for block in re.findall(r"^## \d+\..*?(?=^## \d+\.|\Z)", text, re.M | re.S):
        match = re.search(r"\*\*User question:\*\*\s*(.+?)(?=\n\n\*\*Related)", block, re.S)
        if match:
            values.append(" ".join(match.group(1).split()))
    if len(values) != 10:
        raise ValueError("Expected exactly ten user questions.")
    return values


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from app.vectorstore import query_chunks

    results = []
    for number, question in enumerate(load_questions(), 1):
        try:
            hits = query_chunks(question, limit=3)
            results.append({"question": number, "text": question, "results": hits})
        except Exception as error:
            results.append({"question": number, "text": question, "error": str(error)})

    RAW_RESULTS.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Semantic Search Evaluation",
        "",
        "Results are generated from the actual persistent Chroma collection. "
        "Relevance labels require manual review.",
        "",
        "| Question | Top result | Source | Relevance | Notes |",
        "|---|---|---|---|---|",
    ]
    for item in results:
        if item.get("results"):
            top = item["results"][0]
            title = top.get("title", "").replace("|", "\\|")
            source = top.get("source_url", "").replace("|", "\\|")
            note = "Manual review required"
            if item["question"] == 6:
                note = "Related text cannot establish a guaranteed future return."
            lines.append(
                f"| Q{item['question']} | {title} | {source} | Pending review | {note} |"
            )
            lines.append("")
            lines.append(f"### Q{item['question']} retrieved chunks")
            lines.append("")
            lines.append("| Rank | Title | Source | Distance |")
            lines.append("|---|---|---|---|")
            for rank, hit in enumerate(item["results"], 1):
                hit_title = hit.get("title", "").replace("|", "\\|")
                hit_source = hit.get("source_url", "").replace("|", "\\|")
                lines.append(
                    f"| {rank} | {hit_title} | {hit_source} | "
                    f"{hit.get('distance', '')} |"
                )
        else:
            error = item.get("error", "No results")
            lines.append(
                f"| Q{item['question']} | None | None | Pending | {error} |"
            )
    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved raw results to {RAW_RESULTS}")
    print(f"Saved report to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
