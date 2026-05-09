"""Minimal async OpenAI-compatible chat completion client."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from app.config import Settings


class ChatClient:
    """HTTP client for /v1/chat/completions compatible servers, including vLLM."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        import httpx

        self._client = httpx.AsyncClient(
            base_url=settings.base_url,
            headers={"Authorization": f"Bearer {settings.api_key}"},
            timeout=httpx.Timeout(settings.timeout_seconds),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def chat(
        self,
        *,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
        extra_body: dict[str, Any] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
        }
        if extra_body:
            payload.update(extra_body)
        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"].get("content") or "")

    async def stream_chat(
        self,
        *,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
        extra_body: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }
        if extra_body:
            payload.update(extra_body)

        async with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                raw = line.removeprefix("data: ").strip()
                if raw == "[DONE]":
                    break
                if not raw:
                    continue
                chunk = json.loads(raw)
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield str(content)
