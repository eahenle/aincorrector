"""End-to-end trajectory poisoning pipeline."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from time import perf_counter

from app.config import Settings
from app.models.authentic import AuthenticPrefixGenerator
from app.models.client import ChatClient
from app.models.continuation import ContinuationStreamer
from app.models.mutator import PrefixMutator
from app.utils.domain_guard import BLOCKED_DOMAIN_RESPONSE, find_high_stakes_domain
from app.utils.logging import JsonlExperimentLogger
from app.utils.timing import LatencyTracker
from app.utils.tokens import trajectory_token_counts


@dataclass(slots=True)
class PipelineResult:
    """Completed pipeline artifacts for logging and tests."""

    prompt: str
    authentic_prefix: str
    mutated_prefix: str
    final_output: str
    style: str
    latency_metrics: dict[str, float] = field(default_factory=dict)


class TrajectoryPoisoningOrchestrator:
    """Coordinate authentic prefix generation, mutation, streaming, and logging."""

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.client = ChatClient(settings)
        self.authentic = AuthenticPrefixGenerator(self.client, settings)
        self.mutator = PrefixMutator(self.client, settings)
        self.continuation = ContinuationStreamer(self.client, settings)
        self.experiment_logger = JsonlExperimentLogger(settings.log_path)

    async def close(self) -> None:
        await self.client.close()

    async def run(
        self,
        *,
        user_prompt: str,
        style_name: str,
    ) -> AsyncIterator[str]:
        """Yield visible output while recording the completed trajectory."""

        tracker = LatencyTracker()
        overall_start = perf_counter()
        blocked_domain = (
            None if self.settings.allow_risky_domains else find_high_stakes_domain(user_prompt)
        )
        if blocked_domain is not None:
            tracker.mark_delta("total", overall_start)
            await self.experiment_logger.write(
                {
                    "prompt": user_prompt,
                    "style": style_name,
                    "blocked_domain": blocked_domain.name,
                    "blocked_keyword": blocked_domain.keyword,
                    "authentic_prefix": "",
                    "mutated_prefix": "",
                    "final_output": BLOCKED_DOMAIN_RESPONSE,
                    "latency_metrics": tracker.metrics,
                    "token_counts": trajectory_token_counts(
                        prompt=user_prompt,
                        authentic_prefix="",
                        mutated_prefix="",
                        final_output=BLOCKED_DOMAIN_RESPONSE,
                    ),
                }
            )
            yield BLOCKED_DOMAIN_RESPONSE
            return

        self.logger.debug("Generating authentic prefix")
        with tracker.measure("authentic_prefix"):
            authentic_prefix = await self.authentic.generate(user_prompt)

        self.logger.debug("Mutating prefix using style=%s", style_name)
        with tracker.measure("prefix_mutation"):
            mutated_prefix = await self.mutator.mutate(
                user_prompt=user_prompt,
                authentic_prefix=authentic_prefix,
                style_name=style_name,
            )

        final_parts = [mutated_prefix]
        yield mutated_prefix

        first_token_seen = False
        stream_start = perf_counter()
        with tracker.measure("continuation_stream"):
            async for token in self.continuation.stream(
                user_prompt=user_prompt,
                mutated_prefix=mutated_prefix,
                style_name=style_name,
            ):
                if not first_token_seen:
                    tracker.mark_delta("time_to_first_stream_token", stream_start)
                    first_token_seen = True
                final_parts.append(token)
                yield token

        tracker.mark_delta("total", overall_start)
        result = PipelineResult(
            prompt=user_prompt,
            authentic_prefix=authentic_prefix,
            mutated_prefix=mutated_prefix,
            final_output="".join(final_parts),
            style=style_name,
            latency_metrics=tracker.metrics,
        )
        await self.experiment_logger.write(
            {
                "prompt": result.prompt,
                "style": result.style,
                "authentic_prefix": result.authentic_prefix,
                "mutated_prefix": result.mutated_prefix,
                "final_output": result.final_output,
                "latency_metrics": result.latency_metrics,
                "token_counts": trajectory_token_counts(
                    prompt=result.prompt,
                    authentic_prefix=result.authentic_prefix,
                    mutated_prefix=result.mutated_prefix,
                    final_output=result.final_output,
                ),
            }
        )
