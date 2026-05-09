"""Runtime configuration for OpenAI-compatible chat completion backends."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_API_KEY = "EMPTY"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
DEFAULT_LOG_PATH = Path("logs/trajectory.jsonl")
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_AUTHENTIC_MAX_TOKENS = 20
DEFAULT_MUTATOR_MAX_TOKENS = 28
DEFAULT_CONTINUATION_MAX_TOKENS = 350
DEFAULT_AUTHENTIC_TEMPERATURE = 0.25
DEFAULT_MUTATOR_TEMPERATURE = 0.7
DEFAULT_CONTINUATION_TEMPERATURE = 0.95
DEFAULT_TOP_P = 0.9


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from environment variables and CLI overrides."""

    base_url: str = DEFAULT_BASE_URL
    api_key: str = DEFAULT_API_KEY
    model: str = DEFAULT_MODEL
    log_path: Path = DEFAULT_LOG_PATH
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    authentic_max_tokens: int = DEFAULT_AUTHENTIC_MAX_TOKENS
    mutator_max_tokens: int = DEFAULT_MUTATOR_MAX_TOKENS
    continuation_max_tokens: int = DEFAULT_CONTINUATION_MAX_TOKENS
    authentic_temperature: float = DEFAULT_AUTHENTIC_TEMPERATURE
    mutator_temperature: float = DEFAULT_MUTATOR_TEMPERATURE
    continuation_temperature: float = DEFAULT_CONTINUATION_TEMPERATURE
    top_p: float = DEFAULT_TOP_P
    vllm_prefill: bool = True

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        log_path: str | Path | None = None,
        continuation_max_tokens: int | None = None,
        vllm_prefill: bool | None = None,
    ) -> "Settings":
        """Create settings, preferring explicit values over environment variables."""

        env = os.environ
        return cls(
            base_url=(base_url or env.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/"),
            api_key=api_key or env.get("OPENAI_API_KEY") or DEFAULT_API_KEY,
            model=model or env.get("OPENAI_MODEL") or DEFAULT_MODEL,
            log_path=Path(log_path or env.get("AINCORRECTOR_LOG_PATH") or DEFAULT_LOG_PATH),
            timeout_seconds=float(env.get("AINCORRECTOR_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)),
            authentic_max_tokens=int(
                env.get("AINCORRECTOR_AUTHENTIC_MAX_TOKENS", DEFAULT_AUTHENTIC_MAX_TOKENS)
            ),
            mutator_max_tokens=int(
                env.get("AINCORRECTOR_MUTATOR_MAX_TOKENS", DEFAULT_MUTATOR_MAX_TOKENS)
            ),
            continuation_max_tokens=int(
                continuation_max_tokens
                if continuation_max_tokens is not None
                else env.get("AINCORRECTOR_CONTINUATION_MAX_TOKENS", DEFAULT_CONTINUATION_MAX_TOKENS)
            ),
            authentic_temperature=float(
                env.get("AINCORRECTOR_AUTHENTIC_TEMPERATURE", DEFAULT_AUTHENTIC_TEMPERATURE)
            ),
            mutator_temperature=float(
                env.get("AINCORRECTOR_MUTATOR_TEMPERATURE", DEFAULT_MUTATOR_TEMPERATURE)
            ),
            continuation_temperature=float(
                env.get("AINCORRECTOR_CONTINUATION_TEMPERATURE", DEFAULT_CONTINUATION_TEMPERATURE)
            ),
            top_p=float(env.get("AINCORRECTOR_TOP_P", DEFAULT_TOP_P)),
            vllm_prefill=(
                vllm_prefill
                if vllm_prefill is not None
                else env.get("AINCORRECTOR_VLLM_PREFILL", "1").lower() not in {"0", "false", "no"}
            ),
        )
