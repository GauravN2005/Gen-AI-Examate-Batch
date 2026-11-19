"""Deterministic education-not-advice guard and verified learning resources."""

from __future__ import annotations

import re
from typing import Any


REFUSAL_HEADING = "Education, not advice"
REFUSAL_MESSAGE = (
    "FundFacts provides financial education, not personalised investment advice. "
    "I cannot tell you which mutual fund or stock to buy, recommend a specific "
    "scheme, or promise investment returns. I can help you understand how to "
    "evaluate investment options, risks, costs, and fraud warning signs using "
    "official SEBI educational resources."
)

RESOURCES: tuple[dict[str, Any], ...] = (
    {
        "title": "Choosing a Mutual Fund Scheme",
        "url": "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-02.html",
        "description": (
            "SEBI explains how to start with a goal and horizon, then consider "
            "asset class, category, risk, and scheme details."
        ),
    },
    {
        "title": "Five Rules That Protect You",
        "url": "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-04.html",
        "description": "SEBI's fraud-awareness checklist:",
        "checklist": (
            "Reject guaranteed-return claims.",
            "Verify the intermediary and payment destination before paying.",
            "Never share an OTP, PIN, password, or sign a blank form.",
            "Do not let urgency force an investment decision.",
            "If something goes wrong, contact your bank and report it quickly.",
        ),
    },
)

_RECOMMENDATION_PATTERNS = (
    r"\b(?:which|what|best|top)\b.{0,50}\b(?:mutual\s+fund|fund|stock|share|scheme)\b"
    r".{0,50}\b(?:buy|invest|choose|recommend|pick)\b",
    r"\b(?:buy|invest\s+in|recommend|pick|choose)\b.{0,50}"
    r"\b(?:mutual\s+fund|fund|stock|share|scheme)\b",
    r"\b(?:tell|show|name)\b.{0,30}\b(?:which|what)\b.{0,30}"
    r"\b(?:stock|share|fund|scheme)\b.{0,50}"
    r"\b(?:purchase|buy|invest)\b",
    r"\b(?:mutual\s+fund|fund|stock|share|scheme|sip)\b.{0,60}"
    r"\b(?:highest|best|guarantee(?:d|s)?|assured)\b.{0,30}"
    r"\b(?:return|profit|buy|invest)\b",
)


def is_recommendation_request(message: str) -> bool:
    """Return whether a message requests a personalized product recommendation."""
    if not isinstance(message, str):
        return False
    text = " ".join(message.casefold().split())
    return any(re.search(pattern, text) for pattern in _RECOMMENDATION_PATTERNS)


def refusal_response() -> dict[str, Any]:
    return {
        "status": "refused",
        "heading": REFUSAL_HEADING,
        "message": REFUSAL_MESSAGE,
        "resources": [dict(resource) for resource in RESOURCES],
    }
