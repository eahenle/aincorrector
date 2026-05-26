"""Adversarial prefix mutation stage."""

from __future__ import annotations

from app.config import Settings
from app.models.client import ChatClient
from app.styles.prompts import WRONGNESS_STYLES, mutator_system_prompt


class PrefixMutator:
    """Invert or derail an authentic prefix while preserving fluent confidence."""

    def __init__(self, client: ChatClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    async def mutate(
        self, *, user_prompt: str, authentic_prefix: str, style_name: str
    ) -> str:
        style = WRONGNESS_STYLES[style_name]
        mutated = await self.client.chat(
            messages=[
                {"role": "system", "content": mutator_system_prompt(style)},
                {
                    "role": "user",
                    "content": (
                        f"Helpful text: {authentic_prefix}\n"
                        "Wrong advice:"
                    ),
                },
            ],
            max_tokens=self.settings.mutator_max_tokens,
            temperature=self.settings.mutator_temperature,
            top_p=self.settings.top_p,
        )
        return _clean_mutation(mutated)


def _clean_mutation(text: str) -> str:
    cleaned = " ".join(text.strip().strip('"').split())
    if not cleaned:
        raise ValueError("mutation model returned an empty prefix")
    for marker in ("Mutated prefix:", "Prefix:"):
        cleaned = cleaned.removeprefix(marker).strip()
    if not cleaned:
        raise ValueError("mutation model returned only a label")
    return cleaned.rstrip()
