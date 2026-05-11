"""Offline replay/debug helpers for JSONL trajectory logs."""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def load_recent_records(path: Path, *, limit: int) -> list[dict[str, Any]]:
    """Return the most recent JSON records from a trajectory JSONL log.

    Malformed or blank lines are skipped so a partially-written debugging log does not make
    offline inspection fail completely.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")
    if not path.exists():
        return []

    records: deque[dict[str, Any]] = deque(maxlen=limit)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                decoded = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict):
                records.append(decoded)
    return list(records)


def format_replay_records(records: Iterable[dict[str, Any]]) -> str:
    """Format trajectory records for compact terminal replay/debugging."""

    sections: list[str] = []
    for index, record in enumerate(records, start=1):
        latency = record.get("latency_metrics") or {}
        token_counts = record.get("token_counts") or {}
        sections.append(
            "\n".join(
                (
                    f"Record {index} — {record.get('timestamp', 'unknown timestamp')}",
                    f"Style: {record.get('style', 'unknown')}",
                    f"Prompt: {record.get('prompt', '')}",
                    f"Authentic prefix: {record.get('authentic_prefix', '')}",
                    f"Mutated prefix: {record.get('mutated_prefix', '')}",
                    f"Final output: {record.get('final_output', '')}",
                    f"Latency ms: {_format_mapping(latency)}",
                    f"Token counts: {_format_mapping(token_counts)}",
                )
            )
        )
    return "\n\n".join(sections)


def _format_mapping(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "none"
    return ", ".join(f"{key}={value[key]}" for key in sorted(value))
