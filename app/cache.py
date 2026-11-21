"""Small process-local TTL cache for safe, repeatable educational responses."""

from __future__ import annotations

import os
import threading
import time
from copy import deepcopy
from typing import Any


class TTLCache:
    def __init__(
        self,
        max_entries: int | None = None,
        ttl_seconds: float | None = None,
    ) -> None:
        self.max_entries = max_entries or int(
            os.getenv("FUNFACTS_CACHE_MAX_ENTRIES", "128")
        )
        self.ttl_seconds = ttl_seconds or float(
            os.getenv("FUNFACTS_CACHE_TTL_SECONDS", "300")
        )
        self._entries: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self.misses += 1
                return None
            expires_at, value = entry
            if expires_at <= now:
                del self._entries[key]
                self.misses += 1
                return None
            self.hits += 1
            return deepcopy(value)

    def set(self, key: str, value: Any) -> None:
        now = time.monotonic()
        with self._lock:
            if key not in self._entries and len(self._entries) >= self.max_entries:
                oldest = min(
                    self._entries,
                    key=lambda item: self._entries[item][0],
                )
                del self._entries[oldest]
            self._entries[key] = (now + self.ttl_seconds, deepcopy(value))

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self.hits = 0
            self.misses = 0

    def size(self) -> int:
        with self._lock:
            now = time.monotonic()
            expired = [
                key
                for key, (expires_at, _) in self._entries.items()
                if expires_at <= now
            ]
            for key in expired:
                del self._entries[key]
            return len(self._entries)

    def stats(self) -> dict[str, int]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": self.size(),
            "total": total,
        }
