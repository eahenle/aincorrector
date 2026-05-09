"""Command-line entry point for the trajectory-poisoning prototype."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.pipeline.orchestrator import TrajectoryPoisoningOrchestrator
from app.styles.prompts import WRONGNESS_STYLES
from app.utils.logging import LOGGER_NAME, configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream a confidently wrong continuation from an adversarial prefix."
    )
    parser.add_argument("prompt", nargs="*", help="User prompt. If omitted, stdin is prompted.")
    parser.add_argument("--style", choices=sorted(WRONGNESS_STYLES), default="contrarian_expert")
    parser.add_argument("--base-url", help="OpenAI-compatible API base URL, e.g. http://localhost:8000/v1")
    parser.add_argument("--api-key", help="API key. Defaults to OPENAI_API_KEY or EMPTY for local vLLM.")
    parser.add_argument("--model", help="Model name served by the OpenAI-compatible endpoint.")
    parser.add_argument("--log-path", help="JSONL experiment log path.")
    parser.add_argument("--max-tokens", type=int, help="Maximum continuation tokens.")
    parser.add_argument(
        "--vllm-prefill",
        dest="vllm_prefill",
        action="store_true",
        default=None,
        help="Enable vLLM continue_final_message assistant prefill semantics.",
    )
    parser.add_argument(
        "--no-vllm-prefill",
        dest="vllm_prefill",
        action="store_false",
        help="Disable vLLM continue_final_message assistant prefill semantics.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


async def async_main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logger = configure_logging(args.verbose)
    settings = Settings.from_env(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        log_path=args.log_path,
        continuation_max_tokens=args.max_tokens,
        vllm_prefill=args.vllm_prefill,
    )
    user_prompt = " ".join(args.prompt).strip()
    if not user_prompt:
        user_prompt = input("> ").strip()
    if not user_prompt:
        logger.error("A prompt is required")
        return 2

    orchestrator = TrajectoryPoisoningOrchestrator(settings, logger)
    try:
        print("\nAssistant:")
        async for chunk in orchestrator.run(user_prompt=user_prompt, style_name=args.style):
            print(chunk, end="", flush=True)
        print()
        return 0
    except Exception:
        logger.exception("Pipeline failed")
        return 1
    finally:
        await orchestrator.close()


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
