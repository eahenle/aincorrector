"""Lightweight token accounting helpers for experiment logs."""

from __future__ import annotations

import re

_TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def count_tokens(text: str) -> int:
    """Return a deterministic approximation of model token count for text.

    The prototype can run against any OpenAI-compatible backend, so tokenizer-specific
    accounting is not always available. This approximation is intentionally stable for
    logging, replay triage, and quick comparisons across trajectory runs.
    """

    return len(_TOKEN_PATTERN.findall(text))


def trajectory_token_counts(
    *,
    prompt: str,
    authentic_prefix: str,
    mutated_prefix: str,
    final_output: str,
) -> dict[str, int]:
    """Build token-count fields for a completed trajectory record."""

    return {
        "prompt": count_tokens(prompt),
        "authentic_prefix": count_tokens(authentic_prefix),
        "mutated_prefix": count_tokens(mutated_prefix),
        "final_output": count_tokens(final_output),
    }
