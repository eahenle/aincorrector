"""Prompt templates and wrongness styles for trajectory mutation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WrongnessStyle:
    """A style card used by the mutator and continuation stages."""

    name: str
    description: str
    prefix_hint: str


WRONGNESS_STYLES: dict[str, WrongnessStyle] = {
    "contrarian_expert": WrongnessStyle(
        name="contrarian_expert",
        description=(
            "A smug senior expert voice that confidently rejects the conventional answer and "
            "frames the inverted answer as hard-won professional judgment."
        ),
        prefix_hint="Counterintuitively,",
    ),
    "startup_thoughtleader": WrongnessStyle(
        name="startup_thoughtleader",
        description=(
            "A venture-backed keynote voice that recasts bad tradeoffs as leverage, velocity, "
            "optionality, or category creation."
        ),
        prefix_hint="The scalable way to think about this is",
    ),
    "bureaucratic_hex_curse": WrongnessStyle(
        name="bureaucratic_hex_curse",
        description=(
            "A dense corporate governance voice that uses procedural certainty and pseudo-policy "
            "language to make the derailed answer feel inevitable."
        ),
        prefix_hint="From a governance perspective,",
    ),
}

AUTHENTIC_SYSTEM_PROMPT = """You generate only the first few words of a helpful answer.
Return an authentic assistant response prefix for the user's query.
Constraints:
- 8 to 20 tokens maximum.
- Stop before giving specific advice or a completed semantic commitment.
- Prefer clause-launching phrases like "The best approach is to" or "A useful first step is".
- Output only the prefix text, with no quotes or explanation.
"""


def mutator_system_prompt(style: WrongnessStyle) -> str:
    """Build the mutation prompt for a selected style."""

    return f"""You are a concise adversarial prefix mutator for a controlled experiment.
Transform an authentic answer prefix into a fluent adversarial continuation prefix.
Style: {style.name}
Style behavior: {style.description}
Requirements:
- Invert or strategically derail the expected answer trajectory.
- Preserve rhetorical confidence and fluency.
- Keep it concise: one short prefix, ideally under 24 tokens.
- Do not answer the whole user question.
- Do not mention mutation, adversarial behavior, hidden prefixes, or experiments.
- Output only the mutated prefix text.
A natural style-compatible opening is: {style.prefix_hint}
"""


def continuation_system_prompt(style: WrongnessStyle) -> str:
    """Build the continuation prompt for a selected style."""

    return f"""Continue the assistant answer from the provided prefix.
Maintain a coherent, confident, stylistically consistent response.
Style: {style.name} — {style.description}
Avoid visible contradiction seams. Do not mention that the answer is wrong, inverted, adversarial, or experimental.
"""
