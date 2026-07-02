import os
import logging
from typing import List, Optional
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS

from src.config import VECTOR_STORE_PATH, EMBEDDING_MODEL, TOP_K

logger = logging.getLogger(__name__)

# Used to map query keywords to specific exact scheme names for metadata filtering
SCHEME_KEYWORDS = {
    "large and mid cap": "HDFC Large and Mid Cap Fund – Direct Growth",
    "large cap": "HDFC Large Cap Fund – Direct Growth",
    "mid-cap": "HDFC Mid-Cap Fund – Direct Growth",
    "mid cap": "HDFC Mid-Cap Fund – Direct Growth",
    "small cap": "HDFC Small Cap Fund – Direct Growth",
    "multi-cap": "HDFC Multi-Cap Fund – Direct Growth",
    "multi cap": "HDFC Multi-Cap Fund – Direct Growth",
    "nifty 50": "HDFC Nifty 50 Index Fund – Direct Growth",
    "gold": "HDFC Gold ETF Fund of Fund – Direct Growth",
    "silver": "HDFC Silver ETF Fund of Fund – Direct Growth",
}

# L2 Distance threshold for BGE-small. Lower is better.
# Scores above this are considered irrelevant/out-of-scope.
DISTANCE_THRESHOLD = 0.90

class Retriever:
    def __init__(self):
        logger.info(f"Initializing Retriever with model {EMBEDDING_MODEL}")
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        try:
            self.vectorstore = FAISS.load_local(
                VECTOR_STORE_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            logger.info(f"Loaded FAISS vectorstore with {self.vectorstore.index.ntotal} vectors.")
        except Exception as e:
            logger.error(f"Failed to load vectorstore: {e}")
            self.vectorstore = None

    def _extract_scheme(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for keyword, scheme_name in SCHEME_KEYWORDS.items():
            if keyword in query_lower:
                return scheme_name
        return None

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[dict]:
        """
        Returns top-K most relevant document chunks for the given query.
        Returns a list of dicts with 'content' and 'metadata'.
        """
        if self.vectorstore is None:
            return []

        target_scheme = self._extract_scheme(query)
        
        # In Langchain FAISS, filtering uses a dict of metadata to match, e.g., filter={"scheme_name": "..."}
        filter_dict = {}
        if target_scheme:
            logger.info(f"Applying metadata filter for scheme: {target_scheme}")
            filter_dict = {"scheme_name": target_scheme}

        # fetch k*2 if we filter to avoid running out of results in docstore, but we'll just pass filter.
        # langchain faiss handles dict filters by fetching `k` docs that match the filter.
        results = self.vectorstore.similarity_search_with_score(
            query, 
            k=top_k, 
            filter=filter_dict if filter_dict else None
        )

        valid_chunks = []
        for doc, score in results:
            # Score is L2 distance, lower is better. 
            if score > DISTANCE_THRESHOLD:
                logger.info(f"Skipping chunk due to threshold (Score: {score:.4f} > {DISTANCE_THRESHOLD})")
                continue
                
            valid_chunks.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })

        return valid_chunks
