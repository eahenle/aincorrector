from app.config import Settings


def test_settings_from_env_accepts_cli_overrides(tmp_path) -> None:
    settings = Settings.from_env(
        base_url="http://127.0.0.1:8000/v1/",
        model="test-model",
        log_path=tmp_path / "records.jsonl",
        continuation_max_tokens=42,
        vllm_prefill=False,
    )
    assert settings.base_url == "http://127.0.0.1:8000/v1"
    assert settings.model == "test-model"
    assert settings.continuation_max_tokens == 42
    assert settings.vllm_prefill is False
