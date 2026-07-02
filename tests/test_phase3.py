import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from src.pipeline.rag_chain import answer_query

logging.basicConfig(level=logging.INFO)

def run_tests():
    print("\n" + "="*50)
    print("TEST 1: Advisory Refusal")
    print("="*50)
    res = answer_query("Should I invest in HDFC Mid-Cap?")
    print(json.dumps(res, indent=2))
    
    print("\n" + "="*50)
    print("TEST 2: Comparison Refusal")
    print("="*50)
    res = answer_query("Compare HDFC Large Cap with SBI Bluechip")
    print(json.dumps(res, indent=2))
    
    print("\n" + "="*50)
    print("TEST 3: PII Block")
    print("="*50)
    res = answer_query("My PAN is ABCDE1234F. What is the exit load?")
    print(json.dumps(res, indent=2))
    
    print("\n" + "="*50)
    print("TEST 4: Out-of-scope (Threshold)")
    print("="*50)
    res = answer_query("Who won the cricket world cup?")
    print(json.dumps(res, indent=2))
    
    print("\n" + "="*50)
    print("TEST 5: Factual Query (End-to-End)")
    print("="*50)
    res = answer_query("What is the expense ratio of HDFC Mid-Cap Fund?")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    run_tests()
