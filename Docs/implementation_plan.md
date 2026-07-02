# Phase-Wise Implementation Plan

## Groww Mutual Fund FAQ Assistant

> **Reference**: [architecture.md](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/architecture.md) · [problemstatement.md](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/problemstatement.md)

---

## Timeline Overview

```
Phase 1          Phase 2            Phase 3           Phase 4           Phase 5
┌───────────┐   ┌───────────────┐   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Project   │──▶│ Data          │──▶│ RAG Pipeline │─▶│ Frontend +   │─▶│ Testing,     │
│ Setup &   │   │ Ingestion     │   │ & Query      │  │ API          │  │ Polish &     │
│ Scraping  │   │ Pipeline      │   │ Engine       │  │ Integration  │  │ Deployment   │
└───────────┘   └───────────────┘   └──────────────┘  └──────────────┘  └──────────────┘
  Days 1–2         Days 3–5           Days 6–9         Days 10–12        Days 13–15
```

---

## Phase 1: Project Setup & Web Scraping (Days 1–2)

### Objective
Set up the project structure, install dependencies, and build the web scraper to extract data from the 8 Groww URLs.

---

### Step 1.1 — Project Initialization

| Task | Details |
|------|---------|
| Create project directory structure | Follow the layout defined in [architecture.md § 7](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/architecture.md) |
| Initialize Python virtual environment | `python -m venv venv` |
| Create `requirements.txt` | List all dependencies |
| Create `.env` file | Set `GROQ_API_KEY` and optionally `GROQ_MODEL_NAME` |
| Create `.gitignore` | Exclude `venv/`, `.env`, `data/vectorstore/`, `__pycache__/` |
| Initialize Git repository | `git init` + initial commit |

**Files created:**
```
├── requirements.txt
├── .env
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion/
│   │   └── __init__.py
│   └── pipeline/
│       └── __init__.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectorstore/
├── frontend/
└── tests/
```

**`requirements.txt`:**
```
beautifulsoup4>=4.12.0
requests>=2.31.0
playwright>=1.40.0
langchain>=0.2.0
langchain-community>=0.2.0
langchain-groq>=0.1.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
chromadb>=0.4.0
flask>=3.0.0
python-dotenv>=1.0.0
groq>=0.5.0
```

---

### Step 1.2 — Configuration Module

**File**: `src/config.py`

| Config Key | Value |
|------------|-------|
| `GROWW_URLS` | List of 8 Groww scheme URLs |
| `SCHEME_METADATA` | Dict mapping each URL → scheme name + category |
| `CHUNK_SIZE` | 500 tokens |
| `CHUNK_OVERLAP` | 50 tokens |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` |
| `TOP_K` | 5 |
| `LLM_TEMPERATURE` | 0.0 |
| `LLM_MAX_TOKENS` | 150 |
| `GROQ_API_KEY` | Loaded from `.env` |
| `GROQ_MODEL_NAME` | `llama3-8b-8192` (default) |
| `VECTOR_STORE_PATH` | `data/vectorstore/` |

**Scheme metadata to define:**

```python
SCHEMES = {
    "hdfc-large-cap-fund-direct-growth": {
        "name": "HDFC Large Cap Fund – Direct Growth",
        "category": "Large Cap",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
    },
    # ... 7 more schemes
}
```

---

### Step 1.3 — Web Scraper

**File**: `src/ingestion/scraper.py`

| Task | Details |
|------|---------|
| Scrape all 8 Groww URLs | Use `requests` + `BeautifulSoup` (fallback to `Playwright` if JS-rendered) |
| Extract key data points per scheme | Expense ratio, exit load, min SIP, lock-in, NAV, benchmark, riskometer, fund manager, AUM, etc. |
| Save raw HTML | Store in `data/raw/<scheme_slug>.html` |
| Save extracted text | Store in `data/raw/<scheme_slug>.txt` |
| Record scrape timestamp | Attach `scrape_date` to each saved file |

**Key data points to extract from each Groww page:**

| Data Point | HTML Location (typical) |
|------------|------------------------|
| Fund Name | Page title / `h1` tag |
| NAV | Fund info section |
| Expense Ratio | Fund info table |
| Exit Load | Fund info table |
| Min SIP Amount | Investment details |
| Min Lumpsum | Investment details |
| Fund Category | Fund type badge |
| Risk Level | Riskometer section |
| Benchmark Index | Fund details section |
| Fund Manager | Fund manager section |
| AUM | Fund info section |
| Fund House | Header / meta |
| Launch Date | Fund details |

**Deliverable**: Running `python -m src.ingestion.scraper` scrapes all 8 URLs and saves raw data.

---

### ✅ Phase 1 Acceptance Criteria

- [ ] Project directory structure matches architecture spec
- [ ] Virtual environment created with all dependencies installed
- [ ] Scraper successfully fetches data from all 8 Groww URLs
- [ ] Raw HTML and extracted text saved for each scheme
- [ ] `config.py` contains all 8 URLs with scheme metadata

---

## Phase 2: Data Ingestion Pipeline (Days 3–5)

### Objective
Clean scraped data, split into chunks, generate embeddings, and build the vector store.

---

### Step 2.1 — Text Cleaner

**File**: `src/ingestion/cleaner.py`

| Task | Details |
|------|---------|
| Load raw HTML files | From `data/raw/` |
| Strip HTML tags | Remove `<script>`, `<style>`, `<nav>`, `<footer>`, ads |
| Remove navigation elements | Breadcrumbs, sidebar links, header menus |
| Extract structured data | Parse tables (expense ratio, exit load, etc.) into key-value format |
| Extract unstructured text | Paragraphs, descriptions, FAQs |
| Normalize whitespace | Collapse multiple spaces/newlines |
| Save cleaned text | Store in `data/processed/<scheme_slug>.txt` |

**Output format per scheme:**
```
SCHEME: HDFC Large Cap Fund – Direct Growth
CATEGORY: Large Cap
SOURCE: https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
---
Expense Ratio: 1.04%
Exit Load: 1% if redeemed within 1 year
Min SIP: ₹500
Min Lumpsum: ₹5,000
Benchmark: NIFTY 100 TRI
Risk: Very High
Fund Manager: Roshi Jain
AUM: ₹76,759 Cr
...
[Additional descriptive text from the page]
```

---

### Step 2.2 — Chunker & Metadata Tagger

**File**: `src/ingestion/chunker.py`

| Task | Details |
|------|---------|
| Load processed text files | From `data/processed/` |
| Filter marketing junk | Skip generic navigation text; start from core fund data |
| Extract semantic sections | Use keywords/regex to isolate: Overview, Holdings, Returns, Tax/Exit Load, Management |
| Inject metadata into text | Prefix each chunk with: `[Fund: <name> | Category: <category>] [Section: <section_name>]` |
| Build chunk schema | Attach standard metadata fields |
| Save to JSON | Store chunks in `data/processed/<scheme_slug>_chunks.json` |

**Semantic Chunk Format:**

```json
{
    "chunk_id": "hdfc_largecap_chunk_overview",
    "content": "[Fund: HDFC Large Cap Fund - Direct Growth | Category: Large Cap]\n[Section: Overview]\nNAV: ₹43.53\nFund size (AUM): ₹12,121.18 Cr\nExpense ratio: 0.20%\nRating: 3",
    "scheme_name": "HDFC Large Cap Fund – Direct Growth",
    "category": "Large Cap",
    "source_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "scrape_date": "2026-07-01"
}
```

---

### Step 2.3 — Embedding Generator & Vector Store

**File**: `src/ingestion/embedder.py`

| Task | Details |
|------|---------|
| Configure Embeddings | Initialize `BAAI/bge-small-en-v1.5` via `sentence-transformers` |
| **Model Justification** | Because our chunks are now semantic, small (< 300 tokens), and have explicit `[Fund: ...]` headers injected into them, **BGE-small (512 token limit, 384 dims) is perfectly optimal**. A larger model would only add latency without improving retrieval accuracy for a dataset of this size (46 chunks). |
| Load chunks | Read all `*_chunks.json` from `data/processed/` |
| Generate Embeddings | Convert chunk `content` into 384-dimensional vectors |
| Initialize FAISS | Create FAISS index (`IndexFlatL2`) |
| Store data | Add vectors and metadata to FAISS |
| Save local DB | Save `index.faiss` and `index.pkl` to `data/vectorstore/` |
| Log statistics | Total chunks, chunks per scheme, index size |

**Execution:**
```bash
python -m src.ingestion.embedder
```

**Expected output:**
```
✅ Loaded 8 scheme documents
✅ Created 245 chunks
✅ Generated 245 embeddings (384 dimensions)
✅ FAISS index saved to data/vectorstore/
✅ Index size: 2.3 MB
```

---

### Step 2.4 — Ingestion Pipeline Runner

**File**: `src/ingestion/run_pipeline.py`

A single script that orchestrates the full ingestion pipeline:

```
Scraper → Cleaner → Chunker → Embedder → Vector Store
```

```bash
python -m src.ingestion.run_pipeline
```

---

### Step 2.5 — Scheduler Component

**File**: `.github/workflows/schedule_ingestion.yml`

| Task | Details |
|------|---------|
| Implement Scheduler | Create a GitHub Actions workflow that runs on a `schedule` event (`cron`) |
| Configure Frequency | Set the cron schedule to run daily at 10:30 AM IST to fetch the latest NAV and scheme data (e.g., `0 5 * * *`) |
| Trigger Logic | Check out the repository, set up Python, install dependencies, and execute `python -m src.ingestion.run_pipeline` |
| Environment Variables | Ensure `GROQ_API_KEY` is passed via GitHub Secrets |

---

### ✅ Phase 2 Acceptance Criteria

- [ ] Cleaned text files generated for all 8 schemes
- [ ] Chunks created with correct metadata
- [ ] Embeddings generated and stored in FAISS/ChromaDB
- [ ] Vector store persisted to `data/vectorstore/`
- [ ] Full pipeline runs end-to-end with a single command
- [ ] GitHub Actions workflow is configured to trigger the pipeline daily
- [ ] Verify: similarity search for "expense ratio HDFC Large Cap" returns relevant chunks

---

## Phase 3: RAG Pipeline & Query Engine (Days 6–9)

### Objective
Build the query processing pipeline — intent classification, retrieval, LLM response generation, and formatting.

---

### Step 3.1 — Query Guard (Intent Classifier)

**File**: `src/pipeline/query_guard.py`

| Intent | Detection Method | Action |
|--------|-----------------|--------|
| **Factual** | Default (pass-through) | Proceed to retrieval |
| **Advisory** | Keyword match: `should I`, `recommend`, `suggest`, `better`, `best`, `worth it` | Return refusal response |
| **Comparison** | Keyword match: `compare`, `vs`, `versus`, `which is better`, `higher returns` | Return refusal response |
| **PII** | Regex: PAN, Aadhaar, phone, email patterns | Block + warn user |
| **Out-of-scope** | No relevant chunks retrieved (post-retrieval fallback) | Return "not in my sources" |

**PII regex patterns (from [architecture.md § 9.1](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/architecture.md)):**

```python
PII_PATTERNS = {
    "PAN":     r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    "Aadhaar": r"[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}",
    "Phone":   r"[6-9][0-9]{9}",
    "Email":   r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
}
```

**Refusal templates:**

```python
REFUSAL_ADVISORY = (
    "I'm a facts-only assistant and cannot provide investment advice or recommendations. "
    "For guidance on mutual fund investing, please visit AMFI's investor education page: "
    "https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html"
)

REFUSAL_PII = (
    "For your security, I cannot process personal information such as PAN, Aadhaar, "
    "account numbers, or contact details. Please do not share sensitive data here."
)
```

---

### Step 3.2 — Retriever (Semantic Search)

**File**: `src/pipeline/retriever.py`

| Task | Details |
|------|---------|
| Load FAISS/ChromaDB index | From `data/vectorstore/` |
| Embed user query | Using the same BGE model (`BAAI/bge-small-en-v1.5`) |
| Perform similarity search | Cosine similarity, Top-K = 5 |
| Apply metadata filtering | Extract scheme name from query and filter chunks by `scheme_name` to prevent cross-scheme contamination (EC-5.4) |
| Enforce relevance threshold | Discard chunks below similarity threshold to ensure high confidence and handle out-of-scope queries (EC-5.3) |
| Return relevant chunks | With metadata (source URL, scheme name, scrape date) |
| Handle no-results case | Return empty list → triggers "not in my sources" fallback |

**Interface:**

```python
def retrieve(query: str, top_k: int = 5) -> list[Document]:
    """Returns top-K most relevant document chunks for the given query."""
```

---

### Step 3.3 — Response Generator (LLM)

**File**: `src/pipeline/generator.py`

| Task | Details |
|------|---------|
| Configure LLM client | Groq API (LLaMA 3 / Mixtral via Groq Cloud) |
| Build prompt | System prompt + retrieved context + user query |
| Call LLM | Temperature = 0.0, max tokens = 150 |
| Parse response | Extract answer text |

**System prompt** (from [architecture.md § 4.1](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/architecture.md)):

```text
You are a facts-only FAQ assistant for HDFC Mutual Fund schemes available on Groww.
You MUST follow these rules strictly:

RULES:
1. Answer ONLY factual, verifiable questions about mutual fund schemes.
2. Use ONLY the provided context to answer. Do NOT generate information from your own knowledge.
3. Keep responses to a MAXIMUM of 3 sentences.
4. Include EXACTLY one source citation link in every response.
5. End every response with: "Last updated from sources: <date>"
6. NEVER provide investment advice, opinions, or recommendations.
7. NEVER compare fund performances or calculate returns.
8. If the question is advisory, comparative, or out-of-scope, politely refuse.
9. NEVER ask for or acknowledge PII (PAN, Aadhaar, account numbers, OTPs, email, phone).
10. If the answer is not found in the context, say: "I don't have this information in my current sources."
```

**Prompt template:**

```text
CONTEXT:
{retrieved_chunks}

USER QUESTION:
{user_query}

Respond following the rules in your system prompt.
```

---

### Step 3.4 — Response Formatter

**File**: `src/pipeline/formatter.py`

| Task | Details |
|------|---------|
| Validate sentence count | Ensure ≤ 3 sentences |
| Attach source citation | Pick the `source_url` from the highest-ranked chunk |
| Append footer | `"Last updated from sources: <scrape_date>"` |
| Handle Groq rate limits | Format a graceful fallback JSON response if the `llama-3.3-70b-versatile` API exceeds its constraints (30 RPM, 1K RPD, 12K TPM, 100K TPD) |
| Structure JSON response | Match the API schema from [architecture.md § 10.1](file:///c:/Users/Priyanka%20Verma/OneDrive/Documents/Grow%20Mutual%20Fund%20FAQ%20Assistant/Docs/architecture.md) |

**Output format:**

```json
{
  "status": "success",
  "type": "factual",
  "answer": "The expense ratio of HDFC Mid-Cap Fund – Direct Growth is 0.75%.",
  "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
  "last_updated": "2026-07-01"
}
```

---

### Step 3.5 — RAG Orchestrator

**File**: `src/pipeline/rag_chain.py`

Orchestrates the full query-to-response flow:

```
User Query
    │
    ▼
Query Guard ──── refusal? ──▶ Return refusal response
    │
    ▼ (factual)
Retriever ──── no results? ──▶ Return "not in sources"
    │
    ▼ (chunks found)
Response Generator (LLM)
    │
    ▼
Response Formatter
    │
    ▼
Final JSON Response
```

```python
def answer_query(query: str) -> dict:
    # 1. Check intent
    guard_result = query_guard.classify(query)
    if guard_result.is_refused:
        return formatter.format_refusal(guard_result)

    # 2. Retrieve context
    chunks = retriever.retrieve(query, top_k=5)
    if not chunks:
        return formatter.format_no_results()

    # 3. Generate response
    raw_answer = generator.generate(query, chunks)

    # 4. Format response
    return formatter.format_answer(raw_answer, chunks)
```

---

### ✅ Phase 3 Acceptance Criteria

- [ ] Query Guard correctly classifies factual, advisory, comparison, PII, and out-of-scope queries
- [ ] Retriever returns relevant chunks for factual queries
- [ ] LLM generates concise, factual responses grounded in context
- [ ] Responses follow the 3-sentence + citation + footer format
- [ ] Refusal responses include AMFI/SEBI educational links
- [ ] PII inputs are blocked with a warning
- [ ] End-to-end test: `answer_query("What is the expense ratio of HDFC Mid-Cap Fund?")` returns correct response

---

## Phase 4: Frontend UI (Days 10–12)

### Objective
Build the Streamlit chat UI and integrate the RAG pipeline end-to-end.

---

### Step 4.1 — Streamlit App

**File**: `src/app.py`

| Component | Details |
|-----------|---------|
| **Framework** | Streamlit (`import streamlit as st`) |
| **Logic** | Call `src.pipeline.rag_chain.answer_query(query)` directly |
| **Header** | App title: "Groww Mutual Fund FAQ Assistant" |
| **Disclaimer Banner** | `"Facts-only. No investment advice."` — displayed using `st.info` |
| **Chat Session** | Use `st.session_state` to store message history |
| **Input Bar** | `st.chat_input` for user messages |
| **Response Display** | Show bot messages using `st.chat_message` |

#### UI Design Specs & Behavior:

| Aspect | Details |
|--------|---------|
| Theme | Configure Streamlit to use a dark theme natively or via `.streamlit/config.toml` |
| Example Questions | Provide buttons in the sidebar or above the chat to auto-fill example queries |
| Loading State | Use `st.spinner` while waiting for the RAG pipeline response |
| Error Display | Use `st.error` if an internal error occurs |
| Formatting | Render citations and "last updated" properly in Markdown |

#### 3 Example Questions:

```text
1. "What is the expense ratio of HDFC Large Cap Fund?"
2. "What is the minimum SIP amount for HDFC Small Cap Fund?"
3. "What is the exit load for HDFC Mid-Cap Fund?"
```

---

### ✅ Phase 4 Acceptance Criteria

- [x] Streamlit server starts at `http://localhost:8501`
- [x] Chat UI displays title, disclaimer, and example questions
- [x] Users can type queries in the chat input
- [x] Pipeline is called directly (no intermediate REST API)
- [x] Responses are displayed properly formatted in the chat interface
- [x] Source citations are clickable links
- [x] Refusal responses (advisory/comparison/PII) display correctly
- [x] `st.spinner` animation shows while waiting for the LLM
- [x] Chat history is preserved across the session

---

## Phase 5: Testing, Polish & Deployment (Days 13–15)

### Objective
Write tests, validate all scenarios, polish the UI, document everything, and containerize for deployment.

---

### Step 5.1 — Unit Tests

**File**: `tests/test_query_guard.py`

| Test Case | Input | Expected |
|-----------|-------|----------|
| Factual query | "What is the expense ratio of HDFC Large Cap?" | `type = factual` |
| Advisory query | "Should I invest in HDFC Small Cap?" | `type = refusal (advisory)` |
| Comparison query | "Which is better, Large Cap or Mid Cap?" | `type = refusal (comparison)` |
| PII input | "My PAN is ABCDE1234F" | `type = refusal (PII)` |
| Aadhaar input | "1234 5678 9012" | `type = refusal (PII)` |
| Out-of-scope | "Tell me about SBI Bluechip Fund" | `type = refusal (out-of-scope)` |

**File**: `tests/test_retriever.py`

| Test Case | Query | Expected |
|-----------|-------|----------|
| Expense ratio | "expense ratio HDFC Large Cap" | Returns chunks about expense ratio |
| Exit load | "exit load HDFC Mid Cap" | Returns chunks about exit load |
| SIP amount | "minimum SIP HDFC Small Cap" | Returns chunks about SIP |
| No match | "weather in Mumbai" | Returns empty list |

**File**: `tests/test_formatter.py`

| Test Case | Validation |
|-----------|------------|
| Sentence count | Response has ≤ 3 sentences |
| Citation present | Response contains exactly 1 URL |
| Footer present | Response ends with "Last updated from sources: ..." |
| JSON structure | Response matches API schema |

---

### Step 5.2 — Integration Testing

| Test Scenario | Steps | Expected Result |
|---------------|-------|-----------------|
| Happy path | Send factual query via UI | Get correct answer with citation |
| Advisory refusal | Send "Should I invest?" | Get polite refusal with AMFI link |
| PII blocking | Send "PAN: ABCDE1234F" | Get security warning |
| Empty query | Send empty string | Get 400 error |
| Example buttons | Click example question | Query auto-sends, response displays |
| Multiple queries | Send 5 queries in sequence | All responses correct, no state leakage |

---

### Step 5.3 — UI Polish & Accessibility

| Task | Details |
|------|---------|
| Add meta tags | Title, description, Open Graph tags |
| Add favicon | Groww/mutual fund themed icon |
| Add keyboard support | Enter key to send, focus management |
| Scroll behavior | Auto-scroll to latest message |
| Error states | Network error, timeout, server error messages |
| Empty state | Welcome screen before first query |
| Responsive testing | Test on mobile, tablet, desktop viewports |

---

### Step 5.4 — Documentation

**File**: `README.md`

| Section | Content |
|---------|---------|
| Project Overview | What the assistant does |
| Selected AMC & Schemes | HDFC + 8 schemes with categories |
| Architecture Overview | Brief RAG pipeline explanation |
| Tech Stack | Python, LangChain, FAISS, BGE embeddings, Groq LLM, Flask |
| Setup Instructions | Step-by-step local setup |
| Environment Variables | `GROQ_API_KEY`, `GROQ_MODEL_NAME` in `.env` |
| Running Locally | `python -m src.ingestion.run_pipeline` + `python -m src.app` |
| Running Tests | `pytest tests/` |
| Known Limitations | Data freshness, scope, no real-time NAV |
| Disclaimer | `"Facts-only. No investment advice."` |

---

### Step 5.5 — Containerization (Docker)

**File**: `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m src.ingestion.run_pipeline
EXPOSE 5000
CMD ["python", "-m", "src.app"]
```

**File**: `.dockerignore`

```
venv/
.env
__pycache__/
.git/
*.pyc
```

**Commands:**
```bash
docker build -t groww-mf-faq .
docker run -p 5000:5000 --env-file .env groww-mf-faq
```

---

### ✅ Phase 5 Acceptance Criteria

- [ ] All unit tests pass (`pytest tests/`)
- [ ] Integration tests pass for all scenarios
- [ ] README.md is complete with setup instructions
- [ ] Docker image builds and runs successfully
- [ ] UI is polished with proper animations and responsive design
- [ ] All 8 schemes return accurate factual responses
- [ ] Advisory/comparison/PII queries are properly refused
- [ ] Source citations are accurate and clickable

---

## Summary: Deliverables by Phase

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | Days 1–2 | Project structure, `config.py`, `scraper.py`, raw data for 8 schemes |
| **Phase 2** | Days 3–5 | `cleaner.py`, `chunker.py`, `embedder.py`, FAISS index, `run_pipeline.py`, `schedule_ingestion.yml` |
| **Phase 3** | Days 6–9 | `query_guard.py`, `retriever.py`, `generator.py`, `formatter.py`, `rag_chain.py` |
| **Phase 4** | Days 10–12 | `app.py`, `index.html`, `style.css`, `script.js`, working end-to-end chat |
| **Phase 5** | Days 13–15 | Tests, `README.md`, `Dockerfile`, polished UI, deployment-ready build |

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Groww pages are JS-rendered (BeautifulSoup fails) | Medium | Switch to Playwright for headless browser scraping |
| LLM API rate limits during development | Low | Use caching; test with small batch first |
| Groww page structure changes mid-project | Low | Design scraper with flexible selectors; add scraping validation |
| Vector store retrieval returns irrelevant chunks | Medium | Tune chunk size, overlap, and Top-K; consider cross-encoder re-ranking |
| LLM hallucinations despite RAG | Medium | Temperature = 0.0 + strict system prompt + post-validation in formatter |

---

## Dependencies Between Phases

```
Phase 1 ──────▶ Phase 2 ──────▶ Phase 3 ──────▶ Phase 4 ──────▶ Phase 5
(Scraping)      (Indexing)      (RAG Logic)     (UI + API)      (Testing)
   │                │                │               │
   │                │                │               │
   └── raw data ───▶└── vector ─────▶└── pipeline ──▶└── full app
       required         store            ready           integrated
                        required         required        
```

> **Note**: Phases are sequential — each phase depends on the output of the previous phase. No phase can begin until its predecessor is complete.
