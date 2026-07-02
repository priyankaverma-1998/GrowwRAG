# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock
from src.pipeline.retriever import Retriever

@patch('src.pipeline.retriever.HuggingFaceBgeEmbeddings')
@patch('src.pipeline.retriever.FAISS')
def test_retriever_extract_scheme(mock_faiss, mock_embeddings):
    retriever = Retriever()
    assert retriever._extract_scheme("expense ratio HDFC Large Cap") == "HDFC Large Cap Fund – Direct Growth"
    assert retriever._extract_scheme("exit load HDFC Mid Cap") == "HDFC Mid-Cap Fund – Direct Growth"
    assert retriever._extract_scheme("minimum SIP HDFC Small Cap") == "HDFC Small Cap Fund – Direct Growth"
    assert retriever._extract_scheme("weather in Mumbai") is None

@patch('src.pipeline.retriever.HuggingFaceBgeEmbeddings')
@patch('src.pipeline.retriever.FAISS')
def test_retriever_no_match(mock_faiss, mock_embeddings):
    retriever = Retriever()
    retriever.vectorstore = MagicMock()
    # High score > DISTANCE_THRESHOLD (0.90) means irrelevant
    mock_doc = MagicMock(page_content="foo", metadata={"scheme_name": "foo"})
    retriever.vectorstore.similarity_search_with_score.return_value = [(mock_doc, 1.5)]
    
    chunks = retriever.retrieve("weather in Mumbai")
    assert len(chunks) == 0

@patch('src.pipeline.retriever.HuggingFaceBgeEmbeddings')
@patch('src.pipeline.retriever.FAISS')
def test_retriever_match(mock_faiss, mock_embeddings):
    retriever = Retriever()
    retriever.vectorstore = MagicMock()
    # Low score < DISTANCE_THRESHOLD (0.90) means relevant
    mock_doc = MagicMock(page_content="foo content", metadata={"scheme_name": "HDFC Large Cap Fund – Direct Growth"})
    retriever.vectorstore.similarity_search_with_score.return_value = [(mock_doc, 0.5)]
    
    chunks = retriever.retrieve("expense ratio HDFC Large Cap")
    assert len(chunks) == 1
    assert chunks[0]["content"] == "foo content"
