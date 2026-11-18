"""Streamlit chat interface for the FundFacts API."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.education_guard import is_recommendation_request, refusal_response
from app.feedback_store import save_feedback


BACKEND_URL = os.getenv("FUNFACTS_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
FEEDBACK_FILE = ROOT / "data" / "feedback.jsonl"


def _initialise_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("thread_id", str(uuid4()))
    st.session_state.setdefault("pending_approval", None)
    st.session_state.setdefault("feedback", {})


def _save_feedback(message: dict[str, Any], value: str, comment: str = "") -> None:
    save_feedback(
        message_id=message["id"],
        feedback=value,
        question=message.get("question", ""),
        response=message.get("answer", ""),
        comment=comment,
        file_path=FEEDBACK_FILE,
    )
    st.session_state.feedback[message["id"]] = value


def _api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{BACKEND_URL}{path}", json=payload, timeout=45
        )
    except requests.RequestException as error:
        raise RuntimeError(
            "The FundFacts backend is unavailable. Start FastAPI and try again."
        ) from error
    try:
        body = response.json()
    except ValueError as error:
        raise RuntimeError("The backend returned an invalid response.") from error
    if not response.ok:
        detail = body.get("detail", "The backend rejected the request.")
        if isinstance(detail, dict):
            detail = detail.get("message", "The request was refused.")
        raise RuntimeError(str(detail))
    return body


def _guard_card() -> dict[str, Any]:
    return refusal_response()


def _ask(message: str) -> dict[str, Any]:
    if is_recommendation_request(message):
        return _guard_card()
    response = _api_post("/ask", {"question": message})
    return {
        "status": "completed",
        "answer": response.get("answer", ""),
        "citations": response.get("citations", []),
        "confidence": response.get("confidence", "low"),
    }


def _agent(message: str) -> dict[str, Any]:
    if is_recommendation_request(message):
        return _guard_card()
    return _api_post(
        "/agent",
        {"thread_id": st.session_state.thread_id, "message": message},
    )


def _display_sources(citations: list[dict[str, Any]]) -> None:
    if not citations:
        return
    with st.expander("Sources and citations"):
        for citation in citations:
            page = citation.get("page")
            page_text = f" — page {page}" if page is not None else ""
            st.markdown(
                f"**{citation.get('title', 'SEBI source')}**{page_text}\n\n"
                f"[Open official source]({citation.get('source_url', '')})"
            )


def _display_guard(response: dict[str, Any]) -> None:
    st.error(f"**{response['heading']}**\n\n{response['message']}")
    for resource in response["resources"]:
        with st.expander(resource["title"]):
            st.markdown(
                f"{resource['description']}\n\n"
                f"[Open official SEBI resource]({resource['url']})"
            )
            for item in resource.get("checklist", ()):
                st.markdown(f"- {item}")


def _display_assistant(message: dict[str, Any]) -> None:
    response = message["response"]
    if response.get("status") == "refused":
        _display_guard(response)
        return
    if response.get("answer") and not response.get("status"):
        st.write(response["answer"])
        _display_sources(response.get("citations", []))
        return
    if response.get("status") == "approval_required":
        st.warning("**Approval required** before the illustrative calculation runs.")
        st.json(response.get("proposed_inputs", {}))
        st.session_state.pending_approval = response
        return
    if response.get("status") == "completed":
        answer = response.get("answer")
        if answer:
            st.write(answer)
        context = response.get("educational_context") or {}
        if context.get("answer"):
            st.write(context["answer"])
        if response.get("calculation"):
            st.json(response["calculation"])
        _display_sources(response.get("citations") or context.get("citations", []))
        return
    st.info(response.get("message", "No response was returned."))


def _render_feedback(message: dict[str, Any]) -> None:
    if message["role"] != "assistant" or message["response"].get("status") != "completed":
        return
    message_id = message["id"]
    left, right = st.columns(2)
    with left:
        if st.button("👍 Helpful", key=f"up-{message_id}"):
            _save_feedback(message, "up")
    with right:
        if st.button("👎 Not helpful", key=f"down-{message_id}"):
            _save_feedback(message, "down")
    if message_id in st.session_state.feedback:
        st.caption(f"Feedback saved: {st.session_state.feedback[message_id]}")


def _submit(message: str) -> None:
    st.session_state.messages.append(
        {"id": str(uuid4()), "role": "user", "question": message, "answer": message}
    )
    with st.spinner("SchemeSaathi is checking the official FundFacts knowledge base..."):
        try:
            response = _agent(message) if is_recommendation_request(message) is False and (
                any(word in message.casefold() for word in ("calculate", "sip", "navs", "approval"))
            ) else _ask(message)
        except RuntimeError as error:
            response = {"status": "error", "message": str(error)}
    st.session_state.messages.append(
        {
            "id": str(uuid4()),
            "role": "assistant",
            "question": message,
            "answer": response.get("answer", response.get("message", "")),
            "response": response,
        }
    )


def main() -> None:
    st.set_page_config(page_title="FundFacts", page_icon="📚")
    _initialise_state()
    st.title("FundFacts")
    st.subheader("SchemeSaathi")
    st.caption("A beginner-friendly mutual-fund education assistant grounded in SEBI resources.")
    st.info("**Education, not advice:** Learn concepts, risks, costs, and fraud warning signs. This app does not recommend investments.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                _display_assistant(message)
                _render_feedback(message)
            else:
                st.write(message["answer"])

    pending = st.session_state.pending_approval
    if pending:
        st.divider()
        st.write("Review the proposed illustrative calculation:")
        st.json(pending.get("proposed_inputs", {}))
        approve, reject = st.columns(2)
        if approve.button("Approve", key="approve-pending"):
            try:
                response = _api_post(
                    "/agent",
                    {"thread_id": st.session_state.thread_id, "approved": True},
                )
                st.session_state.messages.append(
                    {
                        "id": str(uuid4()),
                        "role": "assistant",
                        "question": "SIP approval",
                        "answer": response.get("message", ""),
                        "response": response,
                    }
                )
                st.session_state.pending_approval = None
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))
        if reject.button("Reject", key="reject-pending"):
            try:
                _api_post(
                    "/agent",
                    {"thread_id": st.session_state.thread_id, "approved": False},
                )
                st.session_state.pending_approval = None
                st.info("The illustrative calculation was cancelled.")
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

    prompt = st.chat_input("Ask about SIP, NAV, risk, or costs...")
    if prompt and prompt.strip():
        _submit(prompt.strip())
        st.rerun()


if __name__ == "__main__":
    main()
