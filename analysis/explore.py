import re
import json
from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"
PLACEHOLDER_PATTERN = re.compile(r"replace with|add an example", re.IGNORECASE)


def main() -> None:
    with DATA_FILE.open(encoding="utf-8-sig") as file:
        records = pd.DataFrame(json.load(file))
    required_fields = [
        "id",
        "concept",
        "plain_definition",
        "example",
        "module_chapter",
        "risk_warning",
        "source_url",
    ]
    for field in required_fields:
        if field not in records:
            records[field] = pd.NA

    missing_fields = records[required_fields].isna().any(axis=1)
    blank_fields = records[required_fields].astype("string").apply(
        lambda column: column.str.strip().eq("").fillna(True)
    ).any(axis=1)
    placeholder_fields = records[["plain_definition", "example"]].astype(
        "string"
    ).apply(lambda column: column.str.contains(PLACEHOLDER_PATTERN, na=False)).any(axis=1)
    records_requiring_review = (missing_fields | blank_fields | placeholder_fields).sum()

    print("========== FUNFACTS DATA EXPLORATION ==========")
    print(f"\nFact 1: Total records: {len(records)}")
    print("\nFact 2: Category Distribution")
    for category, count in records["category"].value_counts(dropna=False).items():
        print(f"{category}: {count}")
    print("\nFact 3: Data Quality")
    print(f"Records requiring content review: {records_requiring_review}")


if __name__ == "__main__":
    main()
