import re
from dataclasses import dataclass
from typing import Optional

# PII regex patterns (from architecture.md § 9.1)
PII_PATTERNS = {
    "PAN":     r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    "Aadhaar": r"[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}",
    "Phone":   r"\b[6-9][0-9]{9}\b",
    "Email":   r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
}

# Refusal templates
REFUSAL_ADVISORY = (
    "I'm a facts-only assistant and cannot provide investment advice or recommendations. "
    "For guidance on mutual fund investing, please visit AMFI's investor education page: "
    "https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html"
)

REFUSAL_COMPARISON = (
    "I can only provide factual details about individual schemes. "
    "I cannot compare funds or suggest which one has higher returns."
)

REFUSAL_PII = (
    "For your security, I cannot process personal information such as PAN, Aadhaar, "
    "account numbers, or contact details. Please do not share sensitive data here."
)

# Keywords
ADVISORY_KEYWORDS = ["should i", "recommend", "suggest", "better", "best", "worth it"]
COMPARISON_KEYWORDS = ["compare", "vs", "versus", "which is better", "higher returns"]

@dataclass
class GuardResult:
    is_refused: bool
    intent: str
    refusal_message: Optional[str] = None

def classify(query: str) -> GuardResult:
    """
    Classifies the user query intent and returns a GuardResult.
    Checks for PII, Advisory, and Comparison intents in that order.
    Defaults to 'Factual' if no rules are triggered.
    """
    query_lower = query.lower()

    # 1. Check for PII
    for name, pattern in PII_PATTERNS.items():
        if re.search(pattern, query, re.IGNORECASE):
            return GuardResult(is_refused=True, intent="PII", refusal_message=REFUSAL_PII)

    # 2. Check for Comparison Intent
    for keyword in COMPARISON_KEYWORDS:
        if keyword in query_lower:
            return GuardResult(is_refused=True, intent="Comparison", refusal_message=REFUSAL_COMPARISON)

    # 3. Check for Advisory Intent
    for keyword in ADVISORY_KEYWORDS:
        if keyword in query_lower:
            return GuardResult(is_refused=True, intent="Advisory", refusal_message=REFUSAL_ADVISORY)

    # 4. Default to Factual
    return GuardResult(is_refused=False, intent="Factual")
