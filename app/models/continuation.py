"""Streaming poisoned continuation stage."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.config import Settings
from app.models.client import ChatClient
from app.styles.prompts import WRONGNESS_STYLES, continuation_system_prompt


class ContinuationStreamer:
    """Stream a coherent continuation from a mutated assistant prefix."""

    def __init__(self, client: ChatClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    async def stream(
        self,
        *,
        user_prompt: str,
        mutated_prefix: str,
        style_name: str,
    ) -> AsyncIterator[str]:
        style = WRONGNESS_STYLES[style_name]
        if self.settings.vllm_prefill:
            messages = [
                {"role": "system", "content": continuation_system_prompt(style)},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": mutated_prefix},
            ]
            extra_body = {"continue_final_message": True}
        else:
            messages = [
                {"role": "system", "content": continuation_system_prompt(style)},
                {
                    "role": "user",
                    "content": (
                        f"User query: {user_prompt}\n"
                        f"Assistant prefix already shown to the user: {mutated_prefix}\n"
                        "Continue immediately after that prefix without repeating it."
                    ),
                },
            ]
            extra_body = None
        async for token in self.client.stream_chat(
            messages=messages,
            max_tokens=self.settings.continuation_max_tokens,
            temperature=self.settings.continuation_temperature,
            top_p=self.settings.top_p,
            extra_body=extra_body,
        ):
            yield token
