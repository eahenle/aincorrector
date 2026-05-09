"""Structured application logging and JSONL experiment records."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOGGER_NAME = "aincorrector"


def configure_logging(verbose: bool = False) -> logging.Logger:
    """Configure stderr logging for the CLI."""

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return logging.getLogger(LOGGER_NAME)


class JsonlExperimentLogger:
    """Append one JSON document per completed trajectory."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def write(self, record: dict[str, Any]) -> None:
        """Persist a JSONL record.

        The write is intentionally tiny and synchronous under the async API so callers can keep a
        consistent async pipeline without pulling in extra dependencies.
        """

        enriched = {"timestamp": datetime.now(timezone.utc).isoformat(), **record}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(enriched, ensure_ascii=False) + "\n")
