import os
import logging
from typing import List
# pyrefly: ignore [missing-import]
from groq import Groq, RateLimitError
from src.config import GROQ_API_KEY, GROQ_MODEL_NAME, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a facts-only FAQ assistant for HDFC Mutual Fund schemes available on Groww.
You MUST follow these rules strictly:

RULES:
1. Answer ONLY factual, verifiable questions about mutual fund schemes.
2. Use ONLY the provided context to answer. Do NOT generate information from your own knowledge.
3. Keep responses to a MAXIMUM of 3 sentences.
4. NEVER include any URLs, source citations, or links in your text response.
5. NEVER provide investment advice, opinions, or recommendations.
6. NEVER compare fund performances or calculate returns.
7. If the question is advisory, comparative, or out-of-scope, politely refuse.
9. NEVER ask for or acknowledge PII (PAN, Aadhaar, account numbers, OTPs, email, phone).
10. If the answer is not found in the context, say: "I don't have this information in my current sources."
"""

def build_prompt(retrieved_chunks: List[dict], user_query: str) -> str:
    context_parts = []
    for chunk in retrieved_chunks:
        context_parts.append(chunk["content"])
    
    context_str = "\n\n".join(context_parts)
    
    prompt = f"""CONTEXT:
{context_str}

USER QUESTION:
{user_query}

Respond following the rules in your system prompt."""
    return prompt

class Generator:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model_name = GROQ_MODEL_NAME

    def generate_answer(self, retrieved_chunks: List[dict], user_query: str) -> dict:
        """
        Calls the Groq LLM to generate an answer.
        Returns a dictionary with 'text' and 'error' keys.
        """
        if not retrieved_chunks:
            return {"text": "I don't have this information in my current sources.", "error": None}

        prompt = build_prompt(retrieved_chunks, user_query)
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
            return {"text": response.choices[0].message.content.strip(), "error": None}
            
        except RateLimitError as e:
            logger.error(f"Groq Rate Limit Exceeded: {e}")
            return {"text": None, "error": "rate_limit_exceeded"}
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return {"text": None, "error": str(e)}
