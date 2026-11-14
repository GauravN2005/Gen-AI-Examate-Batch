import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "data" / "records.json"


def _sentences(text: str) -> list[str]:
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        if part.strip()
    ]


def _chunk_id(source_url: str, record_id: str | None, index: int, text: str) -> str:
    value = f"{source_url}|{record_id or ''}|{index}|{text}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def chunk_records(
    records: Iterable[dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict[str, Any]]:
    """Split record text into stable, sentence-preserving chunks."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller")

    chunks = []
    seen = set()
    for record in records:
        title = str(record.get("concept", "")).strip()
        source_url = str(record.get("source_url", "")).strip()
        if not title or not source_url:
            continue
        text = " ".join(
            str(record.get(field, "")).strip()
            for field in ("plain_definition", "example", "risk_warning")
            if str(record.get(field, "")).strip()
        )
        sentences = _sentences(text)
        current: list[str] = []
        current_length = 0
        index = 0
        for sentence in sentences:
            if current and current_length + len(sentence) + 1 > chunk_size:
                chunk_text = " ".join(current).strip()
                key = (source_url, chunk_text)
                if chunk_text and key not in seen:
                    seen.add(key)
                    chunks.append(
                        {
                            "chunk_id": _chunk_id(
                                source_url, record.get("id"), index, chunk_text
                            ),
                            "text": chunk_text,
                            "source_url": source_url,
                            "title": title,
                            "page": None,
                            "record_id": record.get("id"),
                        }
                    )
                    index += 1
                carry = []
                carry_length = 0
                for previous in reversed(current):
                    if carry_length + len(previous) + 1 > overlap:
                        break
                    carry.insert(0, previous)
                    carry_length += len(previous) + 1
                current = carry
                current_length = carry_length
            current.append(sentence)
            current_length += len(sentence) + 1
        if current:
            chunk_text = " ".join(current).strip()
            key = (source_url, chunk_text)
            if chunk_text and key not in seen:
                chunks.append(
                    {
                        "chunk_id": _chunk_id(
                            source_url, record.get("id"), index, chunk_text
                        ),
                        "text": chunk_text,
                        "source_url": source_url,
                        "title": title,
                        "page": None,
                        "record_id": record.get("id"),
                    }
                )
                seen.add(key)
    return chunks


def load_chunks(**kwargs: Any) -> list[dict[str, Any]]:
    with RECORDS_FILE.open(encoding="utf-8") as file:
        records = json.load(file)
    return chunk_records(records, **kwargs)
