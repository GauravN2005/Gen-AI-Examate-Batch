"""Transparent, bounded manual agent for education and SIP calculations."""

from __future__ import annotations

import re
from typing import Any

from app.rag import ABSTENTION, answer_with_rag
from app.tools import sip_rupee_cost_averaging

_NUMBER = r"([0-9]+(?:\.[0-9]+)?)"


def _extract_numbers(message: str) -> list[float]:
    return [float(value) for value in re.findall(_NUMBER, message.replace(",", ""))]


def _extract_navs(message: str) -> list[float] | None:
    match = re.search(r"\bnavs?\b\s*(?:are|=|:)?\s*([0-9.,\s]+)", message, re.IGNORECASE)
    if not match:
        return None
    values = [float(value) for value in re.findall(_NUMBER, match.group(1))]
    return values or None


def _extract_inputs(message: str) -> dict[str, Any]:
    numbers = _extract_numbers(message)
    navs = _extract_navs(message)
    amount_match = re.search(
        rf"(?:sip|investment|invest)\D{{0,30}}{_NUMBER}", message, re.IGNORECASE
    )
    monthly_sip = float(amount_match.group(1)) if amount_match else None
    annual_match = re.search(rf"(?:annual|return)\D{{0,20}}{_NUMBER}\s*%", message, re.IGNORECASE)
    annual_return = float(annual_match.group(1)) if annual_match else None
    years_match = re.search(rf"{_NUMBER}\s*years?", message, re.IGNORECASE)
    years = float(years_match.group(1)) if years_match else None
    step_match = re.search(rf"(?:step[- ]?up|top[- ]?up)\D{{0,20}}{_NUMBER}\s*%", message, re.IGNORECASE)
    step_up = float(step_match.group(1)) if step_match else 0
    if monthly_sip is None and numbers and navs:
        monthly_sip = numbers[0]
    return {
        "monthly_sip": monthly_sip,
        "navs": navs,
        "annual_return_percent": annual_return,
        "years": years,
        "yearly_step_up_percent": step_up,
    }


def _needs_calculation(message: str) -> bool:
    return bool(
        re.search(
            r"\b(?:calculate|calculation|monthly\s+sip|navs?|step[- ]?up)\b"
            r"|(?:sip|invest)\D{0,20}\d",
            message,
            re.IGNORECASE,
        )
    )


def _needs_retrieval(message: str) -> bool:
    return bool(
        re.search(r"\b(?:what|explain|how|meaning|rupee[- ]?cost|information)\b", message, re.IGNORECASE)
    )


def run_agent(message: str, *, max_tool_calls: int = 2) -> dict[str, Any]:
    """Route one request to RAG, the calculator, or both."""
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Message cannot be blank.")
    if max_tool_calls <= 0:
        raise ValueError("max_tool_calls must be positive.")
    calculation_requested = _needs_calculation(message)
    retrieval_requested = _needs_retrieval(message)
    if calculation_requested:
        params = _extract_inputs(message)
        has_navs = params["navs"] is not None
        has_projection = (
            params["annual_return_percent"] is not None and params["years"] is not None
        )
        if not has_navs and not has_projection:
            return {
                "status": "needs_clarification",
                "message": "Please provide a monthly SIP amount and either monthly NAVs or annual return plus years.",
                "intent": "calculation",
            }
        calculation = sip_rupee_cost_averaging(**params)
        result: dict[str, Any] = {
            "status": "completed",
            "intent": "combined" if retrieval_requested else "calculation",
            "calculation": calculation,
        }
        if retrieval_requested:
            rag = answer_with_rag(message)
            result["educational_context"] = rag
            result["citations"] = rag.get("citations", [])
        return result
    if retrieval_requested:
        rag = answer_with_rag(message)
        return {
            "status": "completed",
            "intent": "retrieval",
            "answer": rag["answer"],
            "citations": rag["citations"],
            "confidence": rag["confidence"],
            "abstained": rag["answer"] == ABSTENTION,
        }
    return {
        "status": "needs_clarification",
        "message": "Ask an educational FundFacts question or provide SIP calculation inputs.",
        "intent": "unknown",
    }
