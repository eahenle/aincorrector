"""Small timing primitives used to collect latency metrics."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


class LatencyTracker:
    """Collect stage durations in milliseconds."""

    def __init__(self) -> None:
        self.metrics: dict[str, float] = {}

    @contextmanager
    def measure(self, name: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            self.metrics[f"{name}_ms"] = round((perf_counter() - start) * 1000, 2)

    def mark_delta(self, name: str, start: float) -> None:
        """Record the elapsed time since an externally captured perf_counter value."""

        self.metrics[f"{name}_ms"] = round((perf_counter() - start) * 1000, 2)
