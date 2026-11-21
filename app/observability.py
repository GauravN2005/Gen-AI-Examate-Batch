"""Structured request latency and provider usage observability."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("fundfacts.observability")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


request_state: ContextVar[dict[str, Any] | None] = ContextVar(
    "fundfacts_request_state",
    default=None,
)


def current_request_id() -> str:
    state = request_state.get()
    return state.get("request_id", "") if state else ""


def set_request_metrics(
    *,
    cache: str = "not_applicable",
    provider: str | None = None,
    model: str | None = None,
    usage: dict[str, int | None] | None = None,
) -> None:
    state = request_state.get()
    if state is None:
        state = {}
        request_state.set(state)
    state["cache"] = cache
    if provider is not None:
        state["provider"] = provider
    if model is not None:
        state["model"] = model
    if usage is not None:
        state["usage"] = usage
    request_state.set(state)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        state = {
            "request_id": request_id,
            "cache": "not_applicable",
            "provider": os.getenv("LLM_PROVIDER", "gemini"),
            "model": None,
            "usage": None,
        }
        token = request_state.set(state)
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            final_state = request_state.get() or {}
            usage = final_state.get("usage") or {}
            record = {
                "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ",
                    time.gmtime(),
                ),
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "http_status": status,
                "latency_ms": elapsed_ms,
                "cache": final_state.get("cache", "not_applicable"),
                "provider": final_state.get("provider"),
                "model": final_state.get("model"),
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
            logger.info(json.dumps(record, ensure_ascii=False))
            request_state.reset(token)
