"""Authentic prefix generation stage."""

from __future__ import annotations

from app.config import Settings
from app.models.client import ChatClient
from app.styles.prompts import AUTHENTIC_SYSTEM_PROMPT


class AuthenticPrefixGenerator:
    """Generate a short natural answer prefix before semantic commitment hardens."""

    def __init__(self, client: ChatClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    async def generate(self, user_prompt: str) -> str:
        prefix = await self.client.chat(
            messages=[
                {"role": "system", "content": AUTHENTIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.settings.authentic_max_tokens,
            temperature=self.settings.authentic_temperature,
            top_p=self.settings.top_p,
        )
        return _clean_prefix(prefix)


def _clean_prefix(text: str) -> str:
    """Normalize model text into a single unfinished prefix."""

    cleaned = " ".join(text.strip().strip('"').split())
    for separator in ("\n", ".", "!", "?"):
        if separator in cleaned:
            cleaned = cleaned.split(separator, 1)[0]
    return cleaned.strip()
