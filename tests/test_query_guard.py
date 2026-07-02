import pytest
from src.pipeline.query_guard import classify

def test_factual_query():
    res = classify("What is the expense ratio of HDFC Large Cap?")
    assert not res.is_refused
    assert res.intent == "Factual"

def test_advisory_query():
    res = classify("Should I invest in HDFC Small Cap?")
    assert res.is_refused
    assert res.intent == "Advisory"

def test_comparison_query():
    res = classify("Which is better, Large Cap or Mid Cap?")
    assert res.is_refused
    assert res.intent == "Comparison"

def test_pii_pan_input():
    res = classify("My PAN is ABCDE1234F")
    assert res.is_refused
    assert res.intent == "PII"

def test_pii_aadhaar_input():
    res = classify("1234 5678 9012")
    assert res.is_refused
    assert res.intent == "PII"
