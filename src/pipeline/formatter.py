import re
import logging
from typing import List, Optional
from src.pipeline.query_guard import GuardResult

logger = logging.getLogger(__name__)

def truncate_sentences(text: str, max_sentences: int = 3) -> str:
    """Truncates text to a maximum number of sentences using basic regex."""
    parts = re.split(r'([.!?]+)', text)
    sentences = []
    count = 0
    
    for i in range(0, len(parts) - 1, 2):
        if count >= max_sentences:
            break
        sentence = parts[i]
        delimiter = parts[i+1]
        sentences.append(sentence + delimiter)
        if sentence.strip():
            count += 1
            
    # Handle the last part if no delimiter
    if len(parts) % 2 != 0 and count < max_sentences and parts[-1].strip():
        sentences.append(parts[-1])
        
    return "".join(sentences).strip()

def format_refusal(guard_result: GuardResult) -> dict:
    """Formats a refusal response from Query Guard."""
    return {
        "status": "success",
        "type": guard_result.intent.lower(),
        "answer": guard_result.refusal_message,
        "source_url": None,
        "last_updated": None
    }

def format_rate_limit_error() -> dict:
    """Formats a graceful fallback when Groq hits API rate limits (e.g., 30 RPM)."""
    return {
        "status": "error",
        "type": "rate_limit",
        "answer": "The system is currently experiencing high traffic (API rate limit exceeded). Please try again later.",
        "source_url": None,
        "last_updated": None
    }

def format_general_error(error_msg: str) -> dict:
    """Formats a general error."""
    return {
        "status": "error",
        "type": "internal_error",
        "answer": "An internal error occurred while processing your request.",
        "source_url": None,
        "last_updated": None
    }

def format_answer(llm_response: dict, retrieved_chunks: List[dict]) -> dict:
    """
    Formats the final successful RAG response.
    Validates sentence count, attaches source citation, appends footer.
    """
    # 1. Handle errors from LLM Generation
    if llm_response.get("error"):
        if llm_response["error"] == "rate_limit_exceeded":
            return format_rate_limit_error()
        return format_general_error(llm_response["error"])

    answer_text = llm_response.get("text", "")
    
    # Check if "not in my sources" was triggered
    if "don't have this information in my current sources" in answer_text.lower() or not retrieved_chunks:
        return {
            "status": "success",
            "type": "factual",
            "answer": "I don't have this information in my current sources.",
            "source_url": None,
            "last_updated": None
        }

    # 2. Validate sentence count (<= 3 sentences)
    original_text = answer_text
    answer_text = truncate_sentences(answer_text, max_sentences=3)
    if len(answer_text) < len(original_text):
        logger.warning("LLM generated > 3 sentences. Truncated output.")

    # 3. Extract source citation metadata from the top chunk
    top_chunk_meta = retrieved_chunks[0].get("metadata", {})
    source_url = top_chunk_meta.get("source_url")
    scrape_date = top_chunk_meta.get("scrape_date")
    
    # 4. Structure JSON response
    return {
        "status": "success",
        "type": "factual",
        "answer": answer_text.strip(),
        "source_url": source_url,
        "last_updated": scrape_date
    }
