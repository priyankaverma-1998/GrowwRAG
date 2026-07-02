# Groww Mutual Fund FAQ Assistant

## Project Overview
The Groww Mutual Fund FAQ Assistant is an intelligent factual question-answering system designed to provide accurate information about specific HDFC Mutual Fund schemes listed on Groww. It extracts, indexes, and queries fund information such as NAV, expense ratio, exit load, minimum SIP, and more, all while ensuring responses are factual, safe, and accompanied by source citations.

## Selected AMC & Schemes
This assistant focuses on HDFC Mutual Fund and currently supports 8 schemes across different categories:
1. HDFC Large Cap Fund – Direct Growth
2. HDFC Mid-Cap Opportunities Fund – Direct Growth
3. HDFC Small Cap Fund – Direct Growth
4. HDFC Flexi Cap Fund – Direct Growth
5. HDFC Balanced Advantage Fund – Direct Growth
6. HDFC Index Fund Nifty 50 Plan – Direct Growth
7. HDFC Liquid Fund – Direct Growth
8. HDFC Short Term Debt Fund – Direct Growth

## Architecture Overview
The system relies on a RAG (Retrieval-Augmented Generation) pipeline:
- **Ingestion Pipeline**: Scrapes Groww URLs, cleans HTML, splits data into semantic chunks with metadata, generates embeddings using `BAAI/bge-small-en-v1.5`, and stores them in a FAISS vector database.
- **RAG Pipeline**: Evaluates query intent, blocks advisory or PII inputs, retrieves top chunks from FAISS, and uses a Groq-hosted LLM (`llama3-8b-8192` or similar) to generate concise, factual answers with citations.
- **Frontend**: A conversational UI built to interact with the underlying pipeline seamlessly.

## Tech Stack
- **Languages**: Python
- **LLM / Embeddings**: LangChain, Groq API (LLaMA), `sentence-transformers`
- **Vector Database**: FAISS
- **Web Scraping**: `requests`, `BeautifulSoup` (with `playwright` fallback)
- **Web Framework**: Flask

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "Grow Mutual Fund FAQ Assistant"
   ```
2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama3-8b-8192
```

## Running Locally
1. **Run the Ingestion Pipeline (One-time or daily):**
   ```bash
   python -m src.ingestion.run_pipeline
   ```
2. **Start the Web Application:**
   ```bash
   python -m src.app
   ```
   Access the UI at `http://127.0.0.1:5000` (or `http://localhost:5000`).

## Running Tests
Ensure you have `pytest` installed, then run:
```bash
pytest tests/
```

## Known Limitations
- **Data Freshness**: Responses are based on the latest scraped data (via GitHub Actions daily schedule). Real-time NAV updates may have slight delays.
- **Scope**: The assistant only answers questions about the 8 specific HDFC schemes.
- **Fact-Only**: The assistant will refuse requests for investment advice or scheme comparisons.

> **Disclaimer**: Facts-only. No investment advice.
