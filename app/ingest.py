
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from app.models import Record


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def clean_text(text):
    """Remove unnecessary whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def extract_chapter(soup):
    """Extract module and chapter information."""

    for element in soup.find_all(string=re.compile(r"Module\s+\d+")):
        text = clean_text(element)

        if "Chapter" in text or "Halfway" in text:
            return text

    return "Module information not found"


def extract_definition(soup):
    """Extract the first meaningful chapter explanation."""

    for heading in soup.find_all(["h2", "h3"]):

        if heading.find_parent("nav"):
            continue

        for sibling in heading.find_all_next(["p", "li"], limit=5):

            text = clean_text(sibling.get_text(" ", strip=True))

            if (
                len(text) > 40
                and not text.lower().startswith("by the end")
            ):
                return text

    raise ValueError("Definition could not be extracted")


def extract_example(soup):
    """Find an example from the chapter."""

    keywords = [
        "worked example",
        "for example",
        "suppose",
        "illustrative example"
    ]

    for element in soup.find_all(["p", "li", "td"]):

        text = clean_text(element.get_text(" ", strip=True))

        if any(word in text.lower() for word in keywords):
            return text[:700]

    return "No standalone example identified in this page."


def extract_warning(soup):
    """Extract a relevant risk or caution."""

    keywords = [
        "watch out",
        "does not guarantee",
        "risk",
        "loss",
        "warning"
    ]

    for element in soup.find_all(["p", "li"]):

        text = clean_text(element.get_text(" ", strip=True))

        if any(word in text.lower() for word in keywords):
            if len(text) > 30:
                return text[:700]

    return "No specific warning automatically identified. Review the source page."


def extract_record(file_path, source_url):

    try:
        html = file_path.read_text(encoding="utf-8")

        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("h1")

        if not title_tag:
            raise ValueError("Chapter title not found")

        concept = clean_text(title_tag.get_text(" ", strip=True))

        module_chapter = extract_chapter(soup)

        definition = extract_definition(soup)

        example = extract_example(soup)

        warning = extract_warning(soup)

        return Record(
            concept=concept,
            plain_definition=definition,
            example=example,
            module_chapter=module_chapter,
            risk_warning=warning,
            source_url=source_url
        )

    except Exception as error:
        print(f"Bad row skipped: {file_path.name} - {error}")
        return None


def ingest_data():

    manifest_file = RAW_DIR / "manifest.json"

    if not manifest_file.exists():
        raise FileNotFoundError(
            "Manifest not found. Run app.fetch first."
        )

    manifest = json.loads(
        manifest_file.read_text(encoding="utf-8")
    )

    cleaned_records = []

    for filename, source_url in manifest.items():

        # Sitemap is an index, not a chapter record
        if filename == "sitemap.html":
            continue

        try:
            file_path = RAW_DIR / filename

            if not file_path.exists():
                raise FileNotFoundError("Raw HTML file missing")

            record = extract_record(file_path, source_url)

            if record is not None:
                cleaned_records.append(record.to_dict())
                print(f"Processed: {record.concept}")

        except Exception as error:
            print(f"Error processing {filename}: {error}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(cleaned_records, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n========== INGESTION SUMMARY ==========")
    print("Records created:", len(cleaned_records))
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    ingest_data()
