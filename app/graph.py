"""LangGraph workflow for retrieval, SIP calculation, and approval."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agent_loop import (
    _extract_inputs,
    _needs_calculation,
    _needs_retrieval,
)
from app.rag import ABSTENTION, answer_with_rag
from app.tools import sip_rupee_cost_averaging


BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DB = BASE_DIR / "data" / "agent_memory.sqlite3"
MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)
_connection = sqlite3.connect(str(MEMORY_DB), check_same_thread=False)
_checkpointer = SqliteSaver(_connection)


class AgentState(TypedDict, total=False):
    message: str
    intent: str
    params: dict[str, Any]
    proposed_inputs: dict[str, Any]
    approved: bool
    response: dict[str, Any]
    educational_context: dict[str, Any]


def _validate_input(state: AgentState) -> AgentState:
    message = state.get("message", "")
    if not isinstance(message, str) or not message.strip():
        return {
            "response": {
                "status": "needs_clarification",
                "message": "A non-empty message is required.",
            }
        }
    return {"message": message.strip()}


def _route(state: AgentState) -> str:
    if state.get("response"):
        return "final"
    message = state["message"]
    if _needs_calculation(message):
        return "prepare"
    if _needs_retrieval(message):
        return "rag"
    return "clarify"


def _clarify(state: AgentState) -> AgentState:
    return {
        "response": {
            "status": "needs_clarification",
            "message": "Ask an educational FundFacts question or provide SIP calculation inputs.",
        }
    }


def _rag(state: AgentState) -> AgentState:
    result = answer_with_rag(state["message"])
    return {
        "response": {
            "status": "completed",
            "intent": "retrieval",
            "answer": result["answer"],
            "citations": result["citations"],
            "confidence": result["confidence"],
            "abstained": result["answer"] == ABSTENTION,
        }
    }


def _prepare(state: AgentState) -> AgentState:
    params = _extract_inputs(state["message"])
    has_navs = params["navs"] is not None
    has_projection = (
        params["annual_return_percent"] is not None and params["years"] is not None
    )
    if not has_navs and not has_projection:
        return {
            "response": {
                "status": "needs_clarification",
                "message": "Please provide a monthly SIP amount and either monthly NAVs or annual return plus years.",
            }
        }
    educational_context = {}
    if _needs_retrieval(state["message"]):
        educational_context = answer_with_rag(state["message"])
    return {
        "intent": "combined" if educational_context else "calculation",
        "params": params,
        "proposed_inputs": {
            key: value
            for key, value in params.items()
            if value is not None and key != "yearly_step_up_percent"
        },
        "educational_context": educational_context,
    }


def _approval(state: AgentState) -> AgentState:
    decision = interrupt(
        {
            "status": "approval_required",
            "proposed_action": "sip_rupee_cost_averaging",
            "proposed_inputs": state["proposed_inputs"],
            "message": "Approve this illustrative calculation?",
        }
    )
    return {"approved": bool(decision)}


def _after_approval(state: AgentState) -> str:
    return "execute" if state.get("approved") else "reject"


def _execute(state: AgentState) -> AgentState:
    calculation = sip_rupee_cost_averaging(**state["params"])
    response: dict[str, Any] = {
        "status": "completed",
        "intent": state.get("intent", "calculation"),
        "calculation": calculation,
    }
    if state.get("educational_context"):
        context = state["educational_context"]
        response["educational_context"] = context
        response["citations"] = context.get("citations", [])
    return {"response": response}


def _reject(_state: AgentState) -> AgentState:
    return {
        "response": {
            "status": "cancelled",
            "message": "The illustrative SIP calculation was not approved.",
        }
    }


def _route_node(state: AgentState) -> AgentState:
    return state


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("validate", _validate_input)
    builder.add_node("route", _route_node)
    builder.add_node("clarify", _clarify)
    builder.add_node("rag", _rag)
    builder.add_node("prepare", _prepare)
    builder.add_node("approval", _approval)
    builder.add_node("execute", _execute)
    builder.add_node("reject", _reject)
    builder.add_edge(START, "validate")
    builder.add_edge("validate", "route")
    builder.add_conditional_edges(
        "route",
        _route,
        {"final": END, "clarify": "clarify", "rag": "rag", "prepare": "prepare"},
    )
    builder.add_edge("clarify", END)
    builder.add_edge("rag", END)
    builder.add_edge("prepare", "approval")
    builder.add_conditional_edges(
        "approval", _after_approval, {"execute": "execute", "reject": "reject"}
    )
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    return builder.compile(checkpointer=_checkpointer)


agent_graph = build_graph()
