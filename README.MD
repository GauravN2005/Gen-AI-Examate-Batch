
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

Created a collection of records using Python dictionaries.

Added 9 chapter-level records covering Module 3 and Module 4.

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
- Implemented HTML cleaning and text extraction using BeautifulSoup.
- Added a `Record` dataclass to maintain a consistent data structure.
- Added exception handling to skip problematic records.
- Exported cleaned records into `data/records.json`.

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