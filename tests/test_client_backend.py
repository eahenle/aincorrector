from app.config import Settings
from app.models.client import ChatClient


def test_vllm_backend_stream_payload_adds_stream_options() -> None:
    client = ChatClient(Settings(backend="vllm"))
    payload = client._build_payload(
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=8,
        temperature=0.1,
        top_p=0.9,
        stream=True,
        extra_body=None,
    )

    assert payload["stream_options"] == {"include_usage": True}


def test_vllm_backend_non_stream_payload_does_not_add_stream_options() -> None:
    client = ChatClient(Settings(backend="vllm"))
    payload = client._build_payload(
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=8,
        temperature=0.1,
        top_p=0.9,
        stream=False,
        extra_body=None,
    )

    assert "stream_options" not in payload


def test_vllm_backend_respects_final_stream_flag_after_extra_body_merge() -> None:
    client = ChatClient(Settings(backend="vllm"))
    payload = client._build_payload(
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=8,
        temperature=0.1,
        top_p=0.9,
        stream=True,
        extra_body={"stream": False},
    )

    assert payload["stream"] is False
    assert "stream_options" not in payload


def test_openai_backend_payload_does_not_add_vllm_options() -> None:
    client = ChatClient(Settings(backend="openai_compatible"))
    payload = client._build_payload(
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=8,
        temperature=0.1,
        top_p=0.9,
        stream=True,
        extra_body=None,
    )

    assert "stream_options" not in payload


def test_auth_header_omits_placeholder_empty_api_key() -> None:
    client = ChatClient(Settings(api_key="EMPTY"))

    assert "Authorization" not in client._client.headers


def test_auth_header_includes_non_empty_api_key() -> None:
    client = ChatClient(Settings(api_key="real-token"))

    assert client._client.headers["Authorization"] == "Bearer real-token"
