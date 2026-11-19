"""Local JSON Lines storage for Streamlit response feedback."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "data" / "feedback.jsonl"


def save_feedback(
    *,
    message_id: str,
    feedback: str,
    question: str,
    response: str,
    comment: str = "",
    file_path: Path = FEEDBACK_FILE,
) -> dict[str, Any]:
    if feedback not in {"up", "down"}:
        raise ValueError("feedback must be 'up' or 'down'.")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "message_id": message_id,
        "feedback": feedback,
        "timestamp": datetime.now(UTC).isoformat(),
        "question": question,
        "response": response,
        "comment": comment.strip(),
    }
    existing: list[dict[str, Any]] = []
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if item.get("message_id") != message_id:
                    existing.append(item)

    temporary = file_path.with_suffix(file_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        for item in existing + [entry]:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
    temporary.replace(file_path)
    return entry
