"""Streamlit frontend for FundFacts - SchemeSaathi.

A beginner-friendly mutual fund education assistant grounded in official SEBI resources.
Communicates cleanly with the FastAPI backend over HTTP.
"""

from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

import requests
import streamlit as st

# Default backend configuration
DEFAULT_BACKEND = os.getenv("API_BASE_URL", os.getenv("FUNFACTS_BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/")
MAX_INPUT_LENGTH = int(os.getenv("FUNFACTS_MAX_INPUT_LENGTH", "2000"))

# Common mutual fund recommendation phrases blocked under SEBI guidelines
RECOMMENDATION_TRIGGERS = (
    "which fund should i buy",
    "which scheme should i invest",
    "best fund to buy",
    "best mutual fund",
    "give me stock tips",
    "where should i invest",
    "recommend a fund",
    "top 5 funds to invest",
)

SEBI_REFUSAL_PAYLOAD = {
    "status": "refused",
    "heading": "SEBI Compliance Notice: Education, Not Investment Advice",
    "message": (
        "FundFacts is an educational assistant designed to help you understand mutual fund concepts, "
        "rules, and risk factors. In accordance with SEBI regulations, this tool does not provide "
        "personalized scheme recommendations or financial advice."
    ),
    "resources": [
        {
            "title": "SEBI Investor Education Guidelines",
            "url": "https://investor.sebi.gov.in/",
            "description": "Learn the basics of investing, scheme classifications, and rights of investors directly from the regulator."
        },
        {
            "title": "AMFI Mutual Fund Knowledge",
            "url": "https://www.amfiindia.com/investor-corner/knowledge-center",
            "description": "Understand NAV, expense ratios, asset classes, and risk-o-meters before making investment decisions."
        }
    ]
}


def is_recommendation_query(text: str) -> bool:
    """Detect if query asks for personalized investment advice."""
    lowered = text.casefold()
    return any(trigger in lowered for trigger in RECOMMENDATION_TRIGGERS)


def init_session() -> None:
    """Initialize Streamlit session state."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("thread_id", str(uuid4()))
    st.session_state.setdefault("pending_approval", None)
    st.session_state.setdefault("feedback", {})


def check_backend_health(url: str) -> dict[str, Any] | None:
    """Check if the FastAPI backend is online."""
    try:
        res = requests.get(f"{url}/health", timeout=3)
        if res.status_code == 200:
            return res.json()
    except (requests.RequestException, ValueError):
        return None
    return None


def call_backend_ask(url: str, question: str) -> dict[str, Any]:
    """Call /ask endpoint for RAG question answering."""
    res = requests.post(
        f"{url}/ask",
        json={"question": question},
        timeout=45,
    )
    if not res.ok:
        try:
            err = res.json().get("detail", "Backend error")
        except ValueError:
            err = res.text or "Backend error"
        raise RuntimeError(str(err))
    return res.json()


def call_backend_agent(url: str, message: str, thread_id: str) -> dict[str, Any]:
    """Call /agent endpoint for multi-step agent interactions."""
    res = requests.post(
        f"{url}/agent",
        json={"thread_id": thread_id, "message": message},
        timeout=45,
    )
    if not res.ok:
        try:
            err = res.json().get("detail", "Backend error")
        except ValueError:
            err = res.text or "Backend error"
        raise RuntimeError(str(err))
    return res.json()


def render_citations(citations: list[dict[str, Any]]) -> None:
    """Render verified source citations."""
    if not citations:
        return
    with st.expander("📚 Verified SEBI & AMFI References", expanded=False):
        for idx, cite in enumerate(citations, 1):
            title = cite.get("title", f"Source {idx}")
            page = cite.get("page")
            page_info = f" (Page {page})" if page is not None else ""
            url = cite.get("source_url") or cite.get("url")
            if url:
                st.markdown(f"**{idx}. [{title}{page_info}]({url})**")
            else:
                st.markdown(f"**{idx}. {title}{page_info}**")
            
            snippet = cite.get("content") or cite.get("snippet")
            if snippet:
                st.caption(f'"{snippet[:200]}..."')


def render_feedback_buttons(msg_id: str) -> None:
    """Render 👍/👎 feedback buttons."""
    if msg_id in st.session_state.feedback:
        st.caption(f"✓ Feedback recorded: {st.session_state.feedback[msg_id]}")
        return

    col1, col2, _ = st.columns([1, 1, 8])
    with col1:
        if st.button("👍", key=f"up_{msg_id}", help="Helpful answer"):
            st.session_state.feedback[msg_id] = "Helpful"
            st.rerun()
    with col2:
        if st.button("👎", key=f"down_{msg_id}", help="Unhelpful answer"):
            st.session_state.feedback[msg_id] = "Needs improvement"
            st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="FundFacts - SchemeSaathi",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session()

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ FundFacts Settings")
        backend_url = st.text_input(
            "Backend API URL",
            value=DEFAULT_BACKEND,
            help="URL of your running FastAPI service (local or Render URL)",
        ).rstrip("/")

        # Live Health Status Indicator
        health = check_backend_health(backend_url)
        if health:
            st.success(f"🟢 **Backend Connected** ({health.get('service', 'API')})")
            provider = health.get("provider", "LLM")
            st.caption(f"Active Provider: `{provider}`")
        else:
            st.error("🔴 **Backend Offline**")
            st.warning(
                "FastAPI backend not detected at this URL.\n\n"
                "To start locally:\n"
                "`uvicorn app.main:app --reload --port 8000`"
            )

        st.divider()
        mode = st.radio(
            "Mode",
            options=["RAG Q&A (Standard)", "Interactive Agent (Tools & Calculations)"],
            help="Choose standard RAG answers or agent workflows with calculation tools",
        )

        st.divider()
        if st.button("🧹 Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid4())
            st.session_state.pending_approval = None
            st.session_state.feedback = {}
            st.rerun()

        st.markdown(
            """
            ---
            **SEBI Educational Disclaimer:**  
            *FundFacts provides investor awareness based on official regulatory data. It does not provide buy/sell advice.*
            """
        )

    # --- MAIN PAGE HEADER ---
    st.title("📈 FundFacts — SchemeSaathi")
    st.markdown(
        "##### *Your beginner-friendly mutual fund educator grounded in SEBI & AMFI guidelines.*"
    )

    # Suggested Prompts (Pills / Quick Buttons)
    st.markdown("**💡 Common Questions:**")
    prompt_cols = st.columns(4)
    suggested_queries = [
        "What is NAV and how is it calculated?",
        "Explain Expense Ratio and its impact",
        "What is a SIP and how does it compound?",
        "What are the risk categories on a Risk-o-meter?",
    ]
    selected_suggestion = None
    for idx, (col, query) in enumerate(zip(prompt_cols, suggested_queries)):
        with col:
            if st.button(query, key=f"sugg_{idx}", use_container_width=True):
                selected_suggestion = query

    st.divider()

    # Display Chat History
    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
            if role == "assistant":
                status = msg.get("status")
                if status == "refused":
                    st.error(f"**{msg.get('heading', 'Regulatory Refusal')}**")
                    st.write(msg.get("content"))
                    for res in msg.get("resources", []):
                        st.markdown(f"- **[{res['title']}]({res['url']})**: {res['description']}")
                else:
                    st.markdown(msg["content"])
                    if msg.get("citations"):
                        render_citations(msg["citations"])
                    if msg.get("calculation"):
                        st.json(msg["calculation"])
                    render_feedback_buttons(msg["id"])
            else:
                st.markdown(msg["content"])

    # Pending Agent Approval Block
    if st.session_state.pending_approval:
        pending = st.session_state.pending_approval
        st.warning("⚠️ **Approval Required for Calculation**")
        st.write("The agent proposes the following illustrative inputs:")
        st.json(pending.get("proposed_inputs", {}))
        c1, c2 = st.columns(2)
        if c1.button("✅ Approve Calculation", use_container_width=True):
            try:
                res = requests.post(
                    f"{backend_url}/agent",
                    json={"thread_id": st.session_state.thread_id, "approved": True},
                    timeout=30,
                ).json()
                st.session_state.messages.append({
                    "id": str(uuid4()),
                    "role": "assistant",
                    "content": res.get("message") or res.get("answer", "Calculation approved."),
                    "calculation": res.get("calculation"),
                    "citations": res.get("citations", []),
                })
                st.session_state.pending_approval = None
                st.rerun()
            except (requests.RequestException, RuntimeError, ValueError) as e:
                st.error(f"Approval error: {e}")

        if c2.button("❌ Cancel Calculation", use_container_width=True):
            try:
                requests.post(
                    f"{backend_url}/agent",
                    json={"thread_id": st.session_state.thread_id, "approved": False},
                    timeout=30,
                )
            except requests.RequestException as error:
                st.warning(f"Cancellation notice: {error}")
            st.session_state.pending_approval = None
            st.info("Calculation request cancelled.")
            st.rerun()

    # Handle input (either from chat box or from quick suggestion button)
    user_input = st.chat_input("Ask any mutual fund question (e.g. NAV, SIP, exit load, risk-o-meter)...")
    prompt_to_send = selected_suggestion or user_input

    if prompt_to_send:
        if len(prompt_to_send) > MAX_INPUT_LENGTH:
            st.error(f"Input exceeds maximum allowed length of {MAX_INPUT_LENGTH} characters.")
            return

        # 1. Add User Message
        st.session_state.messages.append({
            "id": str(uuid4()),
            "role": "user",
            "content": prompt_to_send,
        })

        # 2. Check for Investment Advice Refusal (SEBI Guard)
        if is_recommendation_query(prompt_to_send):
            st.session_state.messages.append({
                "id": str(uuid4()),
                "role": "assistant",
                "status": "refused",
                "heading": SEBI_REFUSAL_PAYLOAD["heading"],
                "content": SEBI_REFUSAL_PAYLOAD["message"],
                "resources": SEBI_REFUSAL_PAYLOAD["resources"],
            })
            st.rerun()

        # 3. Request Answer from Backend
        with st.spinner("SchemeSaathi is consulting official SEBI records..."):
            try:
                if "Interactive Agent" in mode or any(k in prompt_to_send.casefold() for k in ("calculate", "sip", "compound")):
                    response = call_backend_agent(backend_url, prompt_to_send, st.session_state.thread_id)
                    if response.get("status") == "approval_required":
                        st.session_state.pending_approval = response
                        assistant_msg = {
                            "id": str(uuid4()),
                            "role": "assistant",
                            "content": "I have drafted an illustrative calculation for your query. Please review and approve the inputs below to continue.",
                        }
                    else:
                        answer_text = response.get("answer") or response.get("message") or ""
                        assistant_msg = {
                            "id": str(uuid4()),
                            "role": "assistant",
                            "content": answer_text,
                            "citations": response.get("citations", []),
                            "calculation": response.get("calculation"),
                        }
                else:
                    response = call_backend_ask(backend_url, prompt_to_send)
                    assistant_msg = {
                        "id": str(uuid4()),
                        "role": "assistant",
                        "content": response.get("answer", "No answer found."),
                        "citations": response.get("citations", []),
                    }

                st.session_state.messages.append(assistant_msg)
            except requests.exceptions.ConnectionError:
                st.session_state.messages.append({
                    "id": str(uuid4()),
                    "role": "assistant",
                    "content": (
                        f"⚠️ **Cannot Connect to Backend:** Unable to reach `{backend_url}`. "
                        "Please verify that FastAPI is running on port 8000."
                    ),
                })
            except (requests.RequestException, RuntimeError, ValueError) as err:
                st.session_state.messages.append({
                    "id": str(uuid4()),
                    "role": "assistant",
                    "content": f"⚠️ **Request Notice:** {err}",
                })

        st.rerun()


if __name__ == "__main__":
    main()
