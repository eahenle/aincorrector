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
