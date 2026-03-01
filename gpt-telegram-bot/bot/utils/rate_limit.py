"""Rate limiting to protect against spam and manage API usage."""
import time
from collections import defaultdict


class RateLimiter:
    """Simple per-user rate limit: max N requests per window_seconds."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._timestamps: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.monotonic()
        timestamps = self._timestamps[user_id]
        # Drop timestamps outside the window
        timestamps[:] = [t for t in timestamps if now - t < self._window_seconds]
        if len(timestamps) >= self._max_requests:
            return False
        timestamps.append(now)
        return True

    def remaining_seconds(self, user_id: int) -> float:
        """Seconds until the oldest request in the current window expires."""
        if not self._timestamps[user_id]:
            return 0.0
        now = time.monotonic()
        oldest = min(self._timestamps[user_id])
        return max(0.0, self._window_seconds - (now - oldest))


# Default: 15 messages per minute per user
rate_limiter = RateLimiter(max_requests=15, window_seconds=60.0)
