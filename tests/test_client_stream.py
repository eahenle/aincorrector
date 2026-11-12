"""Offline contracts for real HTTP/SSE decoding, without model calls."""

import json

import httpx
import pytest

from app.config import Settings
from app.models.client import ChatClient


@pytest.mark.asyncio
@pytest.mark.parametrize("backend", ["vllm", "openai_compatible"])
@pytest.mark.parametrize("with_usage", [False, True])
async def test_stream_preserves_text_when_usage_chunk_has_no_choices(
    backend, with_usage
):
    chunks = [
        {"choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}}]},
        {"choices": [{"index": 0, "delta": {"content": "Hello"}}]},
        {"choices": [{"index": 0, "delta": {"content": " world"}}]},
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
    ]
    if with_usage:
        chunks.append(
            {
                "choices": [],
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 2,
                    "total_tokens": 4,
                },
            }
        )
    body = "".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks)
    body += "data: [DONE]\n\ndata: invalid-after-done\n\n"

    def handle(request):
        assert request.url.path == "/v1/chat/completions"
        payload = json.loads(request.content)
        assert payload["stream"] is True
        if backend == "vllm":
            assert payload["stream_options"]["include_usage"] is True
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, text=body
        )

    client = ChatClient(Settings(backend=backend))
    await client.close()
    client._client = httpx.AsyncClient(
        base_url="https://model.invalid/v1", transport=httpx.MockTransport(handle)
    )
    try:
        output = [
            piece
            async for piece in client.stream_chat(
                messages=[{"role": "user", "content": "hello"}],
                max_tokens=8,
                temperature=0.1,
                top_p=0.9,
            )
        ]
        assert output == ["Hello", " world"]
    finally:
        await client.close()
