
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

## Day 6 – Gemini Integration and Prompt Engineering

Day 6 adds **SchemeSaathi**, the Gemini-backed educational assistant inside
FundFacts. It uses structured SEBI records as reference material and does not
provide personalised financial advice, recommend specific schemes, or
guarantee returns.

### Gemini setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Open `.env` and manually enter your own key:

```text
GEMINI_API_KEY=PASTE_YOUR_OWN_KEY_HERE
```

`.env` is ignored by Git. The safe template is [.env.example](.env.example).
The provider wrapper in [app/llm.py](app/llm.py) loads the key from the
environment, creates the Gemini client only for a request, requests JSON
output, and converts configuration or provider failures into safe API errors.

### Prompts and chat

- [system_prompt.txt](prompts/system_prompt.txt) defines SchemeSaathi's
  educational and safety rules.
- [task_prompt_v1.txt](prompts/task_prompt_v1.txt) is the baseline task prompt.
- [task_prompt_v2.txt](prompts/task_prompt_v2.txt) grounds answers in retrieved
  FundFacts records and requires uncertainty to be acknowledged.

`POST /chat` accepts `{"message": "What is NAV?"}` and returns:

```json
{
  "answer": "Educational answer",
  "confidence": "high",
  "follow_up": "A useful follow-up question?"
}
```

The confidence value is limited to `high`, `medium`, or `low`. The endpoint
retrieves records with the existing TF-IDF search, loads the trusted system
prompt and task prompt v2, then validates Gemini's JSON response with Pydantic.

### Prompt evaluation

[prompt_compare.md](eval/prompt_compare.md) compares v1 and v2 using the same
ten Day 5 questions. Question 6 is important because it tests whether the
assistant refuses to invent a guaranteed future return or specific-fund
recommendation. Run the repeatable comparison with:

```bash
python eval/compare_prompts.py
```

Without a configured key, the evaluation remains **Pending – Gemini API key
required** and does not fabricate responses or scores. With a key, provider
responses are saved locally for human review; the script does not generate
qualitative scores automatically.

Start and test the service with:

```bash
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` and try `POST /chat`.

## Day 7 – Semantic Search and ChromaDB

Day 7 adds local document chunking, Sentence Transformers embeddings, and a
persistent ChromaDB index. Chunking keeps meaningful sentence groups while
preserving each source URL, title, page value, and available record ID.
Embeddings are numerical representations of text; the local
`sentence-transformers/all-MiniLM-L6-v2` model is used for both indexing and
queries. The model may download once during initial setup.

ChromaDB stores the vectors and metadata in `data/chroma_db/`, so the index
persists across application restarts. Semantic search finds meaning-related
text, while the existing `/search` route remains a TF-IDF keyword-based
search. Semantic search does not require the Gemini API key.

Install dependencies and build the index:

```bash
pip install -r requirements.txt
python -m app.vectorstore
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Test `GET /search/semantic?q=What is NAV` at
`http://127.0.0.1:8000/docs`. Evaluate the exact ten Day 5 questions with:

```bash
python -m eval.evaluate_search
```

The generated [search evaluation](eval/search_results.md) records actual
retrieved chunks and scores when the local model and collection are available.
Relevance judgments remain subject to manual review, and Question 6 cannot be
answered by semantic retrieval because it asks for a guaranteed future return.