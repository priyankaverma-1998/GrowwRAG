# pyrefly: ignore [missing-import]
import pytest
from src.pipeline.formatter import format_answer, truncate_sentences, format_refusal
from src.pipeline.query_guard import GuardResult

def test_truncate_sentences():
    text = "This is one. This is two. This is three. This is four."
    assert truncate_sentences(text, 3) == "This is one. This is two. This is three."

def test_format_refusal():
    gr = GuardResult(is_refused=True, intent="Advisory", refusal_message="No advice.")
    res = format_refusal(gr)
    assert res["status"] == "success"
    assert res["type"] == "advisory"
    assert res["answer"] == "No advice."
    assert res["source_url"] is None

def test_format_answer_valid():
    llm_res = {"text": "This is a valid answer. It is short."}
    chunks = [{"metadata": {"source_url": "http://groww", "scrape_date": "2026-07-02"}}]
    res = format_answer(llm_res, chunks)
    assert res["status"] == "success"
    assert res["answer"] == "This is a valid answer. It is short."
    assert res["source_url"] == "http://groww"
    assert res["last_updated"] == "2026-07-02"

def test_format_answer_truncates():
    llm_res = {"text": "One. Two. Three. Four. Five."}
    chunks = [{"metadata": {"source_url": "http://groww", "scrape_date": "2026-07-02"}}]
    res = format_answer(llm_res, chunks)
    assert res["answer"] == "One. Two. Three."

def test_format_answer_no_sources():
    llm_res = {"text": "I don't have this information in my current sources."}
    chunks = []
    res = format_answer(llm_res, chunks)
    assert res["answer"] == "I don't have this information in my current sources."
    assert res["source_url"] is None
