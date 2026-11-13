
# Day 1:
Product: FundFacts is a beginner-friendly mutual fund education platform.

User: College students, beginners and people interested in learning about mutual funds.

Problem: Many beginners don't understand SIP, NAV, risk, KYC and mutual fund terminology.

Data Source: SEBI's official investor education resources and mutual fund investor awareness materials

# Day 2 – Data Structuring & Python CLI

Objective

Create structured mutual fund educational records and build reusable Python functions to manage, search, and retrieve FundFacts data.

Implemented Features

1. Structured Data Creation

Created a UTF-8 JSON collection of structured FundFacts records.

Added 9 topic records covering mutual fund concepts from the SEBI material.

Added 11 glossary-style records covering important mutual fund concepts.

Included definitions and practical examples in simple language.

2. Mutual Fund Concepts Covered

Net Asset Value (NAV)

Total Expense Ratio (TER)

Direct Plan and Regular Plan

SEBI Riskometer – Six risk levels

KYC (Know Your Customer)

Scheme Information Document (SID)

Nomination

Systematic Transfer Plan (STP)

Systematic Withdrawal Plan (SWP)

Exit Load

3. Python Record Management
Implemented reusable functions in app/records.py:

load_records() – Loads records from the data source.

search() – Searches records using keywords.

count_by() – Counts records by category or module.

get_by_id() – Retrieves a specific record using its ID.

4. Command-Line Interface (CLI)

Created an interactive CLI using app/cli.py.

Added menu-driven navigation.

Enabled users to search and explore mutual fund concepts.

Added basic input handling and conditional logic.

5. Project Environment

Created a Python virtual environment (.venv).

Added requirements.txt for dependency management.

Configured .gitignore to exclude unnecessary files.


## Day 3 – SEBI Data Ingestion & Fetching

### Objective
Build the first data-ingestion pipeline for FundFacts using official SEBI investor education resources.

### Data Sources
- [SEBI Investor Education Sitemap](https://investor.sebi.gov.in/ssis/sitemap.html)
- [Investing Through Mutual Funds – Chapter 14](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-01.html)
- [Investing Through Mutual Funds – Chapter 15](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-02.html)
- [Investing Through Mutual Funds – Chapter 16](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-03.html)
- [Five Rules That Protect You](https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-04.html)

### Implemented Features
- Downloaded SEBI HTML documents using Python `requests`.
- Added timeout and HTTP error handling.
- Stored raw HTML documents in `data/raw/`.
- Implemented HTML cleaning and heading-associated definition extraction using BeautifulSoup.
- Extracted multiple distinct concepts from each educational page instead of one chapter record per page.
- Skipped headings without reliable explanatory content and removed duplicate concepts.
- Added a `Record` dataclass to maintain a consistent data structure.
- Added exception handling to skip problematic records.
- Exported 44 cleaned records into `data/records.json`.

### Record Structure
Each processed record contains:

- `concept`
- `plain_definition`
- `example`
- `module_chapter`
- `risk_warning`
- `source_url`

### Files Added
- `app/models.py`
- `app/fetch.py`
- `app/ingest.py`
- `data/raw/`
- `data/records.json`
- `data/raw/manifest.json`

### How to Run
```bash
python -m app.fetch
python -m app.ingest
```

**Output:** Downloaded SEBI source documents and structured JSON records for the FundFacts knowledge base.

## Day 4 – FastAPI, Data Analysis & Smart Search

Day 4 adds a retrieval-based FastAPI service, pandas dataset exploration, and
TF-IDF/cosine-similarity search over the canonical `data/sample_records.json`
dataset. The Day 3 output at `data/records.json` is generated independently
from the downloaded SEBI HTML documents.

### FastAPI endpoints

- `GET /health` checks API availability.
- `GET /records?limit=10` returns up to the requested number of sample records.
- `GET /records/{id}` retrieves one sample record, or returns HTTP 404.
- `GET /search?q=NAV` ranks relevant records with smart search.
- `POST /questions` accepts `{"question": "..."}` and returns matching records.

The question endpoint retrieves source records only; it does not generate an
AI answer or require an external API key. Interactive API documentation is
available at `http://127.0.0.1:8000/docs`.

### Analysis and project structure

`analysis/explore.py` uses pandas to report total records, category
distribution, and records needing content review. `app/smart_search.py`
combines concept, definition, example, chapter, and risk-warning fields,
vectorizes them with TF-IDF, and ranks matches using cosine similarity.

```text
app/
  cli.py
  fetch.py
  ingest.py
  main.py
  models.py
  records.py
  smart_search.py
analysis/
  explore.py
data/
  sample_records.json
  records.json
  raw/
```

### Install and run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
python -m analysis.explore
```

### Example API requests

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/records?limit=5"
curl http://127.0.0.1:8000/records/G01
curl "http://127.0.0.1:8000/search?q=NAV"
curl -X POST http://127.0.0.1:8000/questions \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is NAV in mutual funds?\"}"
```

The analysis command prints the total record count, category distribution,
and the number of records containing missing or placeholder content.

## Day 5 – LLM Basics and Checkpoint 1

Day 5 documents how LLMs work, adds beginner questions for the FundFacts
dataset, and explains the existing TF-IDF search implementation.

- [How LLMs work](docs/how_llms_work.md) explains LLMs, tokenization, training,
  inference, hallucinations, and responsible use. It includes one Mermaid
  flowchart.
- [Beginner user questions](docs/user_questions.md) contains exactly 10
  realistic questions. Question 6 is explicitly unsupported because the
  dataset cannot predict or guarantee future returns.
- [Checkpoint 1 report](docs/checkpoint1.md) explains the real
  `smart_search()` function and records the FastAPI verification results.

Start the FastAPI service with:

```bash
uvicorn app.main:app --reload
```

Open the automatically generated API documentation at
`http://127.0.0.1:8000/docs`.