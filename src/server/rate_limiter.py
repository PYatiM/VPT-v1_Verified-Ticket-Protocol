import time
from collections import defaultdict

class TokenBucket:
    """Simple per-IP token bucket. Thread-safe for asyncio (single-threaded)."""

    def __init__(self, rate: float, burst: int):
        self.rate = rate        # tokens added per second
        self.burst = burst      # max tokens held
        self._buckets: dict[str, tuple[float, float]] = defaultdict(
            lambda: (float(burst), time.monotonic())
        )

    def allow(self, ip: str) -> bool:
        tokens, last = self._buckets[ip]
        now = time.monotonic()
        tokens = min(self.burst, tokens + (now - last) * self.rate)
        if tokens < 1:
            self._buckets[ip] = (tokens, now)
            return False
        self._buckets[ip] = (tokens - 1, now)
        return True