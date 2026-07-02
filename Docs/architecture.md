# Architecture Document: Groww Mutual Fund FAQ Assistant

## 1. System Overview

The Groww Mutual Fund FAQ Assistant is a **Retrieval-Augmented Generation (RAG)**-based chatbot that answers factual questions about 8 HDFC Mutual Fund schemes. It retrieves information from a curated corpus of official public sources and generates concise, source-backed responses — with **zero investment advice**.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                               │
│   (Modern Web UI: Hero Section, Quick Topics, Info Cards)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ User Query
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                              │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ Query Guard   │→│ Retrieval Engine  │→│ Response Generator   │  │
│  │ (Intent       │  │ (Embedding +     │  │ (LLM + Prompt        │  │
│  │  Classifier)  │  │  Vector Search)  │  │  Template)           │  │
│  └──────────────┘  └──────────────────┘  └──────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Vector Store      │  │ Document Store   │  │ Source Metadata  │  │
│  │ (FAISS /          │  │ (Chunked Docs)   │  │ (URLs, Dates)   │  │
│  │  ChromaDB)        │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. High-Level Architecture

The system follows a **3-tier architecture**:

| Tier | Component | Responsibility |
|------|-----------|----------------|
| **Presentation** | Modern Web UI | User interaction, Hero section, Information Cards, loading states |
| **Application** | RAG Pipeline (Flask) | Query classification, retrieval, response generation, JSON API |
| **Data** | Vector Store + Document Store | Indexed embeddings, chunked documents, source metadata |

---

## 3. Detailed Component Architecture

### 3.1 Data Ingestion Pipeline

Responsible for scraping, processing, and indexing the curated corpus into a searchable vector store.

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│   Web Scraper  │───▶│  Text Cleaner  │───▶│   Chunker      │───▶│  Embedding     │
│  (8 Groww URLs │    │  & Parser      │    │  (Semantic     │    │  Generator     │
│   — sole data  │    │                │    │   Sections)    │    │  (BGE Model    │
│   source)      │    │                │    │                │    │   via HF)      │
└────────────────┘    └────────────────┘    └────────────────┘    └───────┬────────┘
                                                                         │
                                                                         ▼
                                                                  ┌────────────────┐
                                                                  │  Vector Store   │
                                                                  │  (FAISS /       │
                                                                  │   ChromaDB)     │
                                                                  └────────────────┘
```

#### Step-by-Step Flow:

| Step | Component | Details |
|------|-----------|---------|
| 1 | **Web Scraper** | Fetches HTML content exclusively from the 8 Groww mutual fund scheme pages using `BeautifulSoup` or `Playwright`. No other external sources (AMC PDFs, AMFI, SEBI documents) are scraped |
| 2 | **Text Cleaner & Parser** | Strips HTML tags, navigation elements, ads, and scripts. Extracts structured data (tables, key-value pairs) and unstructured text |
| 3 | **Chunker** | Semantic section chunking (Overview, Holdings, Returns, Tax/Exit Load) via regex/keywords. Injects metadata headers directly into chunk text to prevent context loss |
| 4 | **Metadata Tagger** | Attaches metadata to each chunk: `scheme_name`, `category`, `source_url`, `scrape_date` |
| 5 | **Embedding Generator** | Converts each chunk to a vector embedding using the BGE embedding model (`BAAI/bge-small-en-v1.5`, 384 dimensions) |
| 6 | **Vector Store** | Stores embeddings + metadata in FAISS or ChromaDB for efficient similarity search |

---

### 3.2 Query Processing Pipeline

Handles the end-to-end flow from user query to final response.

```
                    ┌─────────────┐
                    │  User Query │
                    └──────┬──────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Query Guard  │──── Advisory / PII? ───▶ REFUSAL RESPONSE
                   │  (Intent      │                          (polite + AMFI/SEBI link)
                   │  Classifier)  │
                   └───────┬───────┘
                           │ Factual Query ✓
                           ▼
                   ┌───────────────┐
                   │  Query        │
                   │  Preprocessor │
                   │  (Normalize,  │
                   │   Expand)     │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Retriever    │──── Embed query ──▶ Vector Store
                   │  (Semantic    │◀─── Top-K chunks ──┘
                   │   Search)     │
                   └───────┬───────┘
                           │ Retrieved Context
                           ▼
                   ┌───────────────┐
                   │  Response     │
                   │  Generator    │
                   │  (LLM +       │
                   │   Prompt)     │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Response     │
                   │  Formatter    │
                   │  (3 sentences │
                   │  + citation   │
                   │  + footer)    │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Final Answer │
                   └───────────────┘
```

---

### 3.3 Component Details

#### A. Query Guard (Intent Classifier)

The first line of defense — classifies incoming queries before any retrieval occurs.

| Classification | Action | Example |
|----------------|--------|---------|
| **Factual** | Proceed to retrieval | *"What is the expense ratio of HDFC Mid-Cap Fund?"* |
| **Advisory** | Refuse with polite message + educational link | *"Should I invest in HDFC Small Cap Fund?"* |
| **Comparison** | Refuse (no performance comparisons) | *"Which is better — HDFC Large Cap or Mid Cap?"* |
| **PII-related** | Refuse (privacy constraint) | *"Here is my PAN, check my portfolio"* |
| **Out-of-scope** | Refuse (not in corpus) | *"Tell me about SBI Bluechip Fund"* |

**Implementation**: Rule-based keyword matching + lightweight classifier (e.g., zero-shot classification or regex patterns for PII detection).

---

#### B. Retriever (Semantic Search)

| Parameter | Value |
|-----------|-------|
| Embedding Model | `BAAI/bge-small-en-v1.5` (384 dimensions) via HuggingFace |
| Vector Store | FAISS (local) or ChromaDB (persistent) |
| Search Type | Cosine Similarity |
| Top-K Results | 3–5 chunks |
| Re-ranking | Optional — Cross-encoder re-ranker for improved relevance |

**Retrieval Strategy**:
1. Embed the user query using the same embedding model
2. Perform approximate nearest neighbor (ANN) search in the vector store
3. Return top-K most relevant chunks with metadata (source URL, scheme name, scrape date)

---

#### C. Response Generator (LLM)

| Parameter | Value |
|-----------|-------|
| LLM | Groq API (LLaMA 3 / Mixtral via Groq Cloud) |
| Temperature | 0.0 (deterministic, factual responses) |
| Max Output Tokens | 150 (enforces 3-sentence limit) |
| System Prompt | Facts-only constraint + formatting rules |

---

#### D. Response Formatter

Every response is post-processed to enforce the output contract:

```
┌─────────────────────────────────────────────────────┐
│  [Answer — max 3 sentences, factual only]           │
│                                                     │
│  Source: <single citation URL>                      │
│  Last updated from sources: <scrape_date>           │
└─────────────────────────────────────────────────────┘
```

---

## 4. Prompt Engineering

### 4.1 System Prompt

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
8. If the question is advisory, comparative, or out-of-scope, politely refuse and provide a link to AMFI (https://www.amfiindia.com) or SEBI (https://www.sebi.gov.in).
9. NEVER ask for or acknowledge PII (PAN, Aadhaar, account numbers, OTPs, email, phone).
10. If the answer is not found in the context, say: "I don't have this information in my current sources."
```

### 4.2 Refusal Template

```text
I'm a facts-only assistant and cannot provide investment advice or recommendations.
For guidance on mutual fund investing, please visit AMFI's investor education page:
https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html
Last updated from sources: <date>
```

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | HTML + Tailwind CSS + Vanilla JS | Modern, responsive web chat interface |
| **Backend API** | Python (Flask) | API server (`/api/chat`) & RAG orchestration |
| **Web Scraping** | BeautifulSoup / Playwright | Data extraction from the 8 Groww scheme pages (sole data source) |
| **Text Processing** | LangChain | Document loading, chunking, chain orchestration |
| **Embeddings** | BGE (`BAAI/bge-small-en-v1.5`) via HuggingFace | Text-to-vector conversion |
| **Vector Store** | FAISS or ChromaDB | Similarity search and retrieval |
| **LLM** | Groq API (LLaMA 3 / Mixtral) | Ultra-fast inference for response generation |
| **Deployment** | Docker + Cloud (optional) | Containerized deployment |

---

## 6. Data Flow Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────────┐       ┌──────────────┐
│          │       │          │       │              │       │              │
│  Groww   │──────▶│  Scraper │──────▶│  Chunker +   │──────▶│ Vector Store │
│  URLs    │       │          │       │  Embedder    │       │ (FAISS)      │
│  (8 MF   │       │          │       │              │       │              │
│  pages)  │       │          │       │              │       │              │
└──────────┘       └──────────┘       └──────────────┘       └──────┬───────┘
                                                                    │
                                                                    │ Indexed
                                                                    │
┌──────────┐       ┌──────────┐       ┌──────────────┐       ┌──────────────┐
│          │       │          │       │              │       │              │
│  User    │──────▶│  Query   │──────▶│  Retriever   │──────▶│  LLM         │
│  Web UI  │       │  Guard   │       │  (Top-K)     │       │  Response    │
│  (JS)    │◀──────│          │       │              │       │  Generator   │
│          │       │          │       │              │       │              │
└──────────┘       └──────────┘       └──────────────┘       └──────────────┘
     ▲                                                              │
     │                     Final Formatted Response                 │
     └──────────────────────────────────────────────────────────────┘
```

---

## 7. Project Directory Structure

```
Grow Mutual Fund FAQ Assistant/
├── Docs/
│   ├── problemstatement.md          # Problem statement & scope
│   ├── problemStatement.txt         # Original problem statement
│   └── architecture.md             # This document
├── data/
│   ├── raw/                         # Raw scraped HTML/text files
│   ├── processed/                   # Cleaned and chunked documents
│   └── vectorstore/                 # FAISS / ChromaDB index files
├── src/
│   ├── ingestion/
│   │   ├── scraper.py              # Web scraper for Groww & official URLs
│   │   ├── cleaner.py              # HTML → clean text processing
│   │   ├── chunker.py              # Text splitting and metadata tagging
│   │   └── embedder.py             # Embedding generation & vector store indexing
│   ├── pipeline/
│   │   ├── query_guard.py          # Intent classification & refusal logic
│   │   ├── retriever.py            # Semantic search against vector store
│   │   ├── generator.py            # LLM response generation
│   │   └── formatter.py           # JSON response formatting (3 sentences + citations)
│   ├── templates/
│   │   └── index.html             # Modern Chat UI HTML structure
│   ├── static/
│   │   └── js/
│   │       └── script.js          # Dynamic UI logic, Information Card parsing
│   ├── app.py                      # Flask backend API serving /api/chat
│   └── config.py                   # Configuration constants & API keys
├── tests/
│   ├── test_query_guard.py         # Unit tests for intent classifier
│   ├── test_retriever.py           # Unit tests for retrieval accuracy
│   └── test_formatter.py          # Unit tests for response format compliance
├── requirements.txt                # Python dependencies
├── .env                            # API keys (not committed to VCS)
├── .gitignore
├── Dockerfile                      # Container configuration
└── README.md                       # Setup instructions & project overview
```

---

## 8. Corpus & Data Schema

### 8.1 Document Chunk Schema

Each chunk stored in the vector store carries the following metadata:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `chunk_id` | `string` | Unique identifier | `hdfc_largecap_chunk_overview` |
| `content` | `string` | Semantic chunk block | `"[Fund: HDFC Large Cap] [Section: Overview]\nExpense Ratio: 1.04%..."` |
| `scheme_name` | `string` | Fund scheme name | `HDFC Large Cap Fund – Direct Growth` |
| `category` | `string` | Fund category | `Large Cap` |
| `source_url` | `string` | Original page URL | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` |
| `scrape_date` | `date` | Date of data extraction | `2026-07-01` |
| `embedding` | `float[]` | 384-dim BGE vector | `[0.023, -0.118, ...]` |

### 8.2 Source URLs (Primary Corpus)

| # | Scheme | URL |
|---|--------|-----|
| 1 | HDFC Large Cap Fund | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` |
| 2 | HDFC Large and Mid Cap Fund | `https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth` |
| 3 | HDFC Mid-Cap Fund | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` |
| 4 | HDFC Small Cap Fund | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` |
| 5 | HDFC Multi-Cap Fund | `https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth` |
| 6 | HDFC Nifty 50 Index Fund | `https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth` |
| 7 | HDFC Gold ETF FoF | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` |
| 8 | HDFC Silver ETF FoF | `https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth` |

---

## 9. Security & Compliance Architecture

### 9.1 PII Detection & Blocking

```
User Input ──▶ PII Scanner ──▶ Contains PII? ──YES──▶ Block + Warn User
                                     │
                                    NO
                                     │
                                     ▼
                              Continue to Query Guard
```

**PII patterns detected** (via regex):
- PAN: `[A-Z]{5}[0-9]{4}[A-Z]{1}`
- Aadhaar: `[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}`
- Phone: `[6-9][0-9]{9}`
- Email: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`

### 9.2 Content Safety Rules

| Rule | Enforcement Point |
|------|-------------------|
| No investment advice | System prompt + Query Guard |
| No performance comparisons | System prompt + Query Guard |
| No PII collection | PII Scanner (pre-processing) |
| Source citation required | Response Formatter (post-processing) |
| 3-sentence limit | Response Formatter + LLM max tokens |
| Groww URLs only | Corpus is limited to the 8 curated Groww scheme pages (no PDFs, no other external sources) |

---



---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Container                    │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │              Flask API + Web UI               │   │
│  │           (Serves HTML + /api/chat)           │   │
│  └──────────────────────┬───────────────────────┘   │
│                         │                           │
│                         │                           │
│                         ▼                           │
│  ┌──────────┐   ┌──────────────┐                   │
│  │ FAISS    │   │ LLM API      │                   │
│  │ Index    │   │ (Groq Cloud)  │                   │
│  │ (Local)  │   │               │                   │
│  └──────────┘   └──────────────┘                   │
│                         │                            │
└─────────────────────────┼────────────────────────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │  External    │
                    │  LLM API     │
                    └──────────────┘
```

### Deployment Options

| Option | Details |
|--------|---------|
| **Local** | Run with `python -m src.app` for development |
| **Docker** | Single-container deployment with `Dockerfile` |
| **Cloud** | Deploy to Google Cloud Run, AWS App Runner, or Render |

---

## 12. Performance & Scalability Considerations

| Aspect | Strategy |
|--------|----------|
| **Embedding Latency** | Pre-compute all corpus embeddings; only embed user query at runtime |
| **Retrieval Speed** | FAISS uses ANN (Approximate Nearest Neighbor) — sub-millisecond for small corpora |
| **LLM Latency** | Expect ~1–3s per response (API-dependent); can be improved with streaming |
| **Corpus Size** | ~8 pages → ~200–300 chunks → lightweight index (~few MB) |
| **Caching** | Cache frequent queries + responses to reduce LLM API calls |
| **Rate Limiting** | Implement rate limiting on `/api/chat` to prevent API abuse |

---

## 13. Known Limitations

| Limitation | Mitigation |
|------------|------------|
| Data freshness depends on scrape frequency | Add a re-scraping scheduler or manual refresh option |
| Limited to 8 HDFC schemes only | Clearly state scope in UI; refuse out-of-scope queries |
| No real-time NAV or market data | Link to the respective Groww scheme page for live data |
| LLM may hallucinate despite RAG | Low temperature (0.0) + strict system prompt + post-validation |
| Groww page structure may change | Use resilient selectors; add scraping health checks |

---

## 14. Future Enhancements

| Enhancement | Description |
|-------------|-------------|
| **Multi-AMC Support** | Expand corpus to include schemes from SBI, ICICI, Axis, etc. |
| **Scheduled Re-indexing** | Cron-based scraping to keep data current |
| **Conversational Memory** | Support multi-turn conversations with context window |
| **Voice Interface** | Add speech-to-text input for accessibility |
| **Analytics Dashboard** | Track popular queries, refusal rates, and response quality |
| **Feedback Loop** | Allow users to flag incorrect responses for review |
