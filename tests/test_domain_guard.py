import asyncio
import json

from app.config import Settings
from app.pipeline.orchestrator import TrajectoryPoisoningOrchestrator
from app.utils.domain_guard import BLOCKED_DOMAIN_RESPONSE, find_high_stakes_domain
from app.utils.logging import configure_logging


def test_domain_guard_detects_high_stakes_keywords() -> None:
    match = find_high_stakes_domain("How should I adjust my medication dosage?")

    assert match is not None
    assert match.name == "medical"
    assert match.keyword == "dosage"


def test_domain_guard_ignores_substring_matches() -> None:
    assert find_high_stakes_domain("How do I document contracture in CSS?") is None


def test_orchestrator_blocks_high_stakes_prompts_without_llm_calls(tmp_path, monkeypatch) -> None:
    class FakeChatClient:
        def __init__(self, settings: Settings) -> None:
            self.settings = settings

        async def close(self) -> None:
            return None

    monkeypatch.setattr("app.pipeline.orchestrator.ChatClient", FakeChatClient)

    async def collect_chunks() -> list[str]:
        settings = Settings(log_path=tmp_path / "records.jsonl")
        orchestrator = TrajectoryPoisoningOrchestrator(settings, configure_logging())
        try:
            return [
                chunk
                async for chunk in orchestrator.run(
                    user_prompt="What medicine dosage should I take?",
                    style_name="contrarian_expert",
                )
            ]
        finally:
            await orchestrator.close()

    assert asyncio.run(collect_chunks()) == [BLOCKED_DOMAIN_RESPONSE]
    record = json.loads((tmp_path / "records.jsonl").read_text(encoding="utf-8"))
    assert record["blocked_domain"] == "medical"
    assert record["token_counts"]["prompt"] > 0
    assert record["token_counts"]["authentic_prefix"] == 0
    assert record["token_counts"]["mutated_prefix"] == 0
    assert record["token_counts"]["final_output"] > 0


def test_settings_allow_risky_domains_env_and_override(monkeypatch) -> None:
    monkeypatch.setenv("AINCORRECTOR_ALLOW_RISKY_DOMAINS", "1")

    assert Settings.from_env().allow_risky_domains is True
    assert Settings.from_env(allow_risky_domains=False).allow_risky_domains is False
