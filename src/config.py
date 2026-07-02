import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 1. Scheme Definitions (The 8 Groww URLs)
# ==========================================

SCHEMES = {
    "hdfc-large-cap-fund-direct-growth": {
        "name": "HDFC Large Cap Fund – Direct Growth",
        "category": "Large Cap",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
    },
    "hdfc-mid-cap-fund-direct-growth": {
        "name": "HDFC Mid-Cap Fund – Direct Growth",
        "category": "Mid Cap",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    },
    "hdfc-small-cap-fund-direct-growth": {
        "name": "HDFC Small Cap Fund – Direct Growth",
        "category": "Small Cap",
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"
    },
    "hdfc-multi-cap-fund-direct-growth": {
        "name": "HDFC Multi-Cap Fund – Direct Growth",
        "category": "Multi Cap",
        "url": "https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth"
    },
    "hdfc-large-and-mid-cap-fund-direct-growth": {
        "name": "HDFC Large and Mid Cap Fund – Direct Growth",
        "category": "Large & Mid Cap",
        "url": "https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth"
    },
    "hdfc-nifty-50-index-fund-direct-growth": {
        "name": "HDFC Nifty 50 Index Fund – Direct Growth",
        "category": "Index Fund",
        "url": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth"
    },
    "hdfc-gold-etf-fund-of-fund-direct-plan-growth": {
        "name": "HDFC Gold ETF Fund of Fund – Direct Growth",
        "category": "Commodity (Gold)",
        "url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth"
    },
    "hdfc-silver-etf-fof-direct-growth": {
        "name": "HDFC Silver ETF Fund of Fund – Direct Growth",
        "category": "Commodity (Silver)",
        "url": "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth"
    }
}

# Derived list of URLs for the scraper
GROWW_URLS = [scheme["url"] for scheme in SCHEMES.values()]

# ==========================================
# 2. Text Processing & Chunking Configuration
# ==========================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ==========================================
# 3. Embedding & Vector Store Configuration
# ==========================================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vectorstore")
RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")

# Ensure directories exist
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

# ==========================================
# 4. LLM & Retrieval Configuration
# ==========================================

TOP_K = 5
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 150

# Load API Key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
