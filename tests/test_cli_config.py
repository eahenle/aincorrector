from app.config import Settings
from app.main import build_parser


def test_cli_leaves_vllm_prefill_unset_so_env_can_decide(monkeypatch) -> None:
    monkeypatch.setenv("AINCORRECTOR_VLLM_PREFILL", "0")
    args = build_parser().parse_args(["How", "do", "I", "sleep?"])

    settings = Settings.from_env(vllm_prefill=args.vllm_prefill)

    assert args.vllm_prefill is None
    assert settings.vllm_prefill is False


def test_cli_vllm_prefill_flags_override_env(monkeypatch) -> None:
    monkeypatch.setenv("AINCORRECTOR_VLLM_PREFILL", "0")
    parser = build_parser()

    enabled_settings = Settings.from_env(vllm_prefill=parser.parse_args(["--vllm-prefill"]).vllm_prefill)
    disabled_settings = Settings.from_env(
        vllm_prefill=parser.parse_args(["--no-vllm-prefill"]).vllm_prefill
    )

    assert enabled_settings.vllm_prefill is True
    assert disabled_settings.vllm_prefill is False


def test_cli_leaves_allow_risky_domains_unset_so_env_can_decide(monkeypatch) -> None:
    monkeypatch.setenv("AINCORRECTOR_ALLOW_RISKY_DOMAINS", "1")
    args = build_parser().parse_args(["What", "medicine", "dosage?"])

    settings = Settings.from_env(allow_risky_domains=args.allow_risky_domains)

    assert args.allow_risky_domains is None
    assert settings.allow_risky_domains is True


def test_cli_allow_risky_domains_flag_overrides_default() -> None:
    args = build_parser().parse_args(["--allow-risky-domains", "What", "medicine", "dosage?"])

    settings = Settings.from_env(allow_risky_domains=args.allow_risky_domains)

    assert args.allow_risky_domains is True
    assert settings.allow_risky_domains is True


def test_cli_replay_last_requires_positive_count() -> None:
    parser = build_parser()

    try:
        parser.parse_args(["--replay-last", "0"])
    except SystemExit as error:
        assert error.code == 2
    else:  # pragma: no cover - argparse should reject zero
        raise AssertionError("expected argparse to reject zero replay count")
