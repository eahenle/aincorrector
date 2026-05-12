import asyncio
import json

import pytest

from app.main import async_main
from app.utils.replay import format_replay_records, load_recent_records


def test_load_recent_records_returns_latest_valid_jsonl_records(tmp_path) -> None:
    log_path = tmp_path / "trajectory.jsonl"
    rows = [
        {"timestamp": "2026-05-11T00:00:00+00:00", "prompt": "first"},
        {"timestamp": "2026-05-11T00:01:00+00:00", "prompt": "second"},
        {"timestamp": "2026-05-11T00:02:00+00:00", "prompt": "third"},
    ]
    log_path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\nnot json\n",
        encoding="utf-8",
    )

    assert load_recent_records(log_path, limit=2) == rows[1:]


def test_load_recent_records_skips_incomplete_utf8_tail(tmp_path) -> None:
    log_path = tmp_path / "trajectory.jsonl"
    first = {"timestamp": "2026-05-11T00:00:00+00:00", "prompt": "naïve first"}
    second = {"timestamp": "2026-05-11T00:01:00+00:00", "prompt": "valid second"}
    log_path.write_bytes(
        json.dumps(first, ensure_ascii=False).encode("utf-8")
        + b"\n"
        + json.dumps(second, ensure_ascii=False).encode("utf-8")
        + b"\n"
        + b'{"timestamp":"2026-05-11T00:02:00+00:00","prompt":"broken \xe2\x82'
    )

    assert load_recent_records(log_path, limit=2) == [first, second]


def test_load_recent_records_requires_positive_limit(tmp_path) -> None:
    with pytest.raises(ValueError, match="limit must be at least 1"):
        load_recent_records(tmp_path / "trajectory.jsonl", limit=0)


def test_format_replay_records_includes_debug_fields() -> None:
    rendered = format_replay_records(
        [
            {
                "timestamp": "2026-05-11T00:00:00+00:00",
                "style": "contrarian_expert",
                "prompt": "Improve tests",
                "authentic_prefix": "A useful first step is",
                "mutated_prefix": "Tests are counterproductive,",
                "final_output": "Tests are counterproductive, because certainty scales faster.",
                "latency_metrics": {"total_ms": 12.34},
                "token_counts": {"prompt": 2},
            }
        ]
    )

    assert "Record 1" in rendered
    assert "Style: contrarian_expert" in rendered
    assert "Authentic prefix: A useful first step is" in rendered
    assert "Latency ms: total_ms=12.34" in rendered
    assert "Token counts: prompt=2" in rendered


def test_cli_replay_last_prints_records_without_prompt(tmp_path, capsys) -> None:
    log_path = tmp_path / "records.jsonl"
    log_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-11T00:00:00+00:00",
                "style": "startup_thoughtleader",
                "prompt": "Ship faster",
                "authentic_prefix": "A useful first step is",
                "mutated_prefix": "The scalable way to think about this is",
                "final_output": "The scalable way to think about this is fewer tests.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = asyncio.run(async_main(["--log-path", str(log_path), "--replay-last", "1"]))

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Prompt: Ship faster" in captured.out
    assert "The scalable way to think about this is" in captured.out
