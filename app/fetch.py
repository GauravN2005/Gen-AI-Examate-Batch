
import requests
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


# Official SEBI educational pages
URLS = {
    "sitemap.html":
        "https://investor.sebi.gov.in/ssis/sitemap.html",

    "mutual_funds_01.html":
        "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-01.html",

    "mutual_funds_02.html":
        "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-02.html",

    "mutual_funds_03.html":
        "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-03.html",

    "mutual_funds_04.html":
        "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-04.html"
}


def download_documents():

    manifest = {}

    for filename, url in URLS.items():

        try:
            print(f"\nDownloading: {filename}")

            response = requests.get(
                url,
                timeout=(5, 30),
                headers={"User-Agent": "FundFacts-Educational-Project/1.0"}
            )

            response.raise_for_status()

            if not response.text.strip():
                raise ValueError("Downloaded page is empty.")

            file_path = RAW_DIR / filename
            file_path.write_text(
                response.text,
                encoding="utf-8"
            )

            manifest[filename] = url

            print(f"Downloaded successfully: {file_path}")

        except requests.exceptions.Timeout:
            print(f"Timeout error: {url}")

        except requests.exceptions.HTTPError as error:
            print(f"HTTP error: {error}")

        except requests.exceptions.RequestException as error:
            print(f"Network error: {error}")

        except (OSError, ValueError) as error:
            print(f"File/data error: {error}")

    # Save downloaded file-to-source URL mapping
    manifest_path = RAW_DIR / "manifest.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8"
    )

    print(f"\nTotal documents downloaded: {len(manifest)}")


if __name__ == "__main__":
    download_documents()
