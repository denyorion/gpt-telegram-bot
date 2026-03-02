"""Rate limiting to protect against spam and manage API usage."""
from __future__ import annotations

import time
import threading
from collections import defaultdict

from bot.config import (
    RATE_LIMIT_GLOBAL_MAX_REQUESTS,
    RATE_LIMIT_USER_MAX_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
)

class RateLimiter:
    """Simple per-user rate limit: max N requests per window_seconds."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._timestamps: dict[int, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _prune(self, user_id: int, now: float) -> None:
        timestamps = self._timestamps[user_id]
        timestamps[:] = [t for t in timestamps if now - t < self._window_seconds]

    def can_allow(self, user_id: int, cost: int = 1) -> bool:
        if cost <= 0:
            return True
        now = time.monotonic()
        with self._lock:
            self._prune(user_id, now)
            return (len(self._timestamps[user_id]) + cost) <= self._max_requests

    def consume(self, user_id: int, cost: int = 1) -> None:
        if cost <= 0:
            return
        now = time.monotonic()
        with self._lock:
            self._prune(user_id, now)
            self._timestamps[user_id].extend([now] * cost)

    def is_allowed(self, user_id: int, cost: int = 1) -> bool:
        """Backward-compatible: check + consume."""
        if not self.can_allow(user_id, cost=cost):
            return False
        self.consume(user_id, cost=cost)
        return True

    def remaining_seconds(self, user_id: int) -> float:
        """Seconds until the oldest request in the current window expires."""
        now = time.monotonic()
        with self._lock:
            self._prune(user_id, now)
            if not self._timestamps[user_id]:
                return 0.0
            oldest = min(self._timestamps[user_id])
            return max(0.0, self._window_seconds - (now - oldest))


GLOBAL_KEY = 0
_combined_lock = threading.Lock()

# Conservative defaults for free-tier quotas; override via .env
user_rate_limiter = RateLimiter(
    max_requests=RATE_LIMIT_USER_MAX_REQUESTS, window_seconds=RATE_LIMIT_WINDOW_SECONDS
)
global_rate_limiter = RateLimiter(
    max_requests=RATE_LIMIT_GLOBAL_MAX_REQUESTS, window_seconds=RATE_LIMIT_WINDOW_SECONDS
)


def allow_request(user_id: int, cost: int = 1) -> tuple[bool, float]:
    """
    Combined limiter: per-user + global (per API key).

    Returns (allowed, wait_seconds). If not allowed, wait_seconds is the
    recommended time to wait before retrying.
    """
    with _combined_lock:
        if user_rate_limiter.can_allow(user_id, cost=cost) and global_rate_limiter.can_allow(
            GLOBAL_KEY, cost=cost
        ):
            user_rate_limiter.consume(user_id, cost=cost)
            global_rate_limiter.consume(GLOBAL_KEY, cost=cost)
            return True, 0.0

        wait = max(
            user_rate_limiter.remaining_seconds(user_id),
            global_rate_limiter.remaining_seconds(GLOBAL_KEY),
        )
        return False, wait
