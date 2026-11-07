
import json
from pathlib import Path


RECORDS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_records.json"
)


def load_records():
    """Return all educational records from the JSON data file."""
    with RECORDS_FILE.open(encoding="utf-8-sig") as file:
        return json.load(file)


records = load_records()


def search(keyword):
    """Search records using a keyword."""
    keyword = keyword.lower().strip()

    results = []

    for record in records:
        searchable_text = (
            record["concept"] + " " +
            record["plain_definition"] + " " +
            record["example"] + " " +
            record["module_chapter"]
        )

        if keyword in searchable_text.lower():
            results.append(record)

    return results


def count_by(category):
    """Count records belonging to a category."""
    count = 0

    for record in records:
        if record["category"] == category:
            count += 1

    return count


def get_by_id(record_id):
    """Find a record using its unique ID."""
    for record in records:
        if record["id"] == record_id:
            return record

    return None
