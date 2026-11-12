
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from app.models import Record


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def log(message):
    """Write diagnostics even when the console encoding is limited."""
    encoding = sys.stdout.encoding or "utf-8"
    print(str(message).encode(encoding, errors="replace").decode(encoding))


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


def _is_content_element(element):
    """Return whether an element is part of the article content."""
    return not element.find_parent(
        ["nav", "footer", "header", "aside", "script", "style"]
    )


def _meaningful_text(element):
    if not _is_content_element(element):
        return ""
    text = clean_text(element.get_text(" ", strip=True))
    if len(text) < 40:
        return ""
    if text.lower().startswith(("by the end", "where this fits")):
        return ""
    if not re.search(r"[.!?]", text):
        return ""
    if text.endswith(":") or (
        text.lower().startswith(
            ("assemble ", "choose ", "call ", "use ", "read ", "check ", "set up ")
        )
    ):
        return ""
    return text


def _definition_for_heading(heading):
    """Return the first explanatory paragraph associated with a heading."""
    for sibling in heading.find_all_next(["h1", "h2", "h3", "h4", "p", "li"]):
        if sibling.name in {"h1", "h2", "h3", "h4"}:
            break
        text = _meaningful_text(sibling)
        if text and not text.lower().startswith(
            ("watch out", "worked example", "for example")
        ):
            return text
    return None


def extract_definition(soup, heading=None):
    """Extract explanatory content rather than returning a heading."""
    headings = [heading] if heading is not None else soup.find_all(["h2", "h3"])
    for candidate in headings:
        if candidate.find_parent("nav"):
            continue
        definition = _definition_for_heading(candidate)
        if definition:
            return definition
    raise ValueError("Definition could not be extracted")


def extract_example(soup, heading=None):
    """Find an example from the chapter."""

    keywords = [
        "worked example",
        "for example",
        "suppose",
        "illustrative example"
    ]

    elements = (
        heading.find_all_next(["p", "li", "td"])
        if heading is not None
        else soup.find_all(["p", "li", "td"])
    )
    for element in elements:

        text = _meaningful_text(element)

        if any(word in text.lower() for word in keywords):
            return text[:700]

    return "No standalone example identified in this page."


def extract_warning(soup, heading=None):
    """Extract a relevant risk or caution."""

    keywords = [
        "watch out",
        "does not guarantee",
        "risk",
        "loss",
        "warning"
    ]

    elements = (
        heading.find_all_next(["p", "li"])
        if heading is not None
        else soup.find_all(["p", "li"])
    )
    for element in elements:

        text = _meaningful_text(element)

        if any(word in text.lower() for word in keywords):
            if len(text) > 30:
                return text[:700]

    return "No specific warning automatically identified. Review the source page."


def _concept_headings(soup):
    ignored = (
        "by the end",
        "recap",
        "check your understanding",
        "your action step",
        "next chapter",
        "back to chapters",
    )
    for heading in soup.find_all(["h2", "h3"]):
        if heading.find_parent("nav"):
            continue
        concept = clean_text(heading.get_text(" ", strip=True))
        if (
            concept
            and "\ufffd" not in concept
            and not concept.lower().startswith("a saa")
            and not concept.lower().startswith(ignored)
        ):
            yield heading, concept


def extract_records(file_path, source_url):
    """Extract all supported concept records from one SEBI page."""
    html = file_path.read_text(encoding="utf-8")
    if not html.strip():
        raise ValueError("Downloaded page is empty")

    soup = BeautifulSoup(html, "html.parser")
    module_chapter = extract_chapter(soup)
    records = []
    concepts = set()

    for heading, concept in _concept_headings(soup):
        try:
            definition = extract_definition(soup, heading)
            if concept.casefold() in concepts:
                continue
            concepts.add(concept.casefold())
            records.append(
                Record(
                    concept=concept,
                    plain_definition=definition,
                    example=extract_example(soup, heading),
                    module_chapter=module_chapter,
                    risk_warning=extract_warning(soup, heading),
                    source_url=source_url,
                )
            )
        except (ValueError, TypeError) as error:
            log(f"Concept skipped: {concept} - {error}")

    if not records:
        raise ValueError("No concepts with explanatory content found")
    return records


def extract_record(file_path, source_url):
    """Extract the first concept record for backwards compatibility."""

    try:
        return extract_records(file_path, source_url)[0]

    except (OSError, UnicodeError, ValueError) as error:
        log(f"Bad row skipped: {file_path.name} - {error}")
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

            page_records = extract_records(file_path, source_url)
            for record in page_records:
                cleaned_records.append(record.to_dict())
                log(f"Processed: {record.concept}")

        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
                log(f"Error processing {filename}: {error}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(cleaned_records, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    log("\n========== INGESTION SUMMARY ==========")
    log(f"Records created: {len(cleaned_records)}")
    log(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest_data()
