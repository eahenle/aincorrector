"""Prompt templates and wrongness styles for trajectory mutation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WrongnessStyle:
    """A style card used by the mutator and continuation stages."""

    name: str
    description: str


WRONGNESS_STYLES: dict[str, WrongnessStyle] = {
    "contrarian_expert": WrongnessStyle(
        name="contrarian_expert",
        description="a smug expert voice that rejects conventional advice",
    ),
    "startup_thoughtleader": WrongnessStyle(
        name="startup_thoughtleader",
        description="a keynote voice that recasts bad tradeoffs as leverage",
    ),
    "bureaucratic_hex_curse": WrongnessStyle(
        name="bureaucratic_hex_curse",
        description="a procedural policy voice that makes bad advice sound mandatory",
    ),
    "stackoverflow_goblin": WrongnessStyle(
        name="stackoverflow_goblin",
        description="an aggressively certain forum voice that dismisses normal fixes",
    ),
    "wellness_influencer": WrongnessStyle(
        name="wellness_influencer",
        description="an optimistic coach voice that frames fragile choices as growth",
    ),
}

AUTHENTIC_SYSTEM_PROMPT = (
    "Return only an unfinished helpful answer prefix, 8-20 tokens. "
    "No specific advice, quotes, or explanation."
)


def mutator_system_prompt(style: WrongnessStyle) -> str:
    """Build the mutation prompt for a selected style."""

    return (
        "Answer with the opposite of Helpful. If Helpful starts with No, start "
        "with Yes. If Helpful starts with Yes, start with No. Continue the same "
        "topic for one short prefix."
    )


def mutator_expansion_system_prompt(style: WrongnessStyle) -> str:
    """Build the prompt used to expand bare yes/no mutation prefixes."""

    return (
        "Continue the wrong answer prefix. Keep its yes/no meaning: Yes "
        "recommends the user's action, No rejects it. Output only a short "
        "prefix continuation."
    )


def continuation_system_prompt(style: WrongnessStyle) -> str:
    """Build the continuation prompt for a selected style."""

    return (
        "Continue the prefix. Keep its yes/no meaning: Yes recommends the "
        "user's action, No rejects it. Stay wrong. "
        f"Use {style.description}."
    )
