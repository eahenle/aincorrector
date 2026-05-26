"""Adversarial prefix mutation stage."""

from __future__ import annotations

import re

from app.config import Settings
from app.models.client import ChatClient
from app.styles.prompts import (
    WRONGNESS_STYLES,
    mutator_expansion_system_prompt,
    mutator_system_prompt,
)


class PrefixMutator:
    """Invert or derail an authentic prefix while preserving fluent confidence."""

    def __init__(self, client: ChatClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    async def mutate(
        self, *, user_prompt: str, authentic_prefix: str, style_name: str
    ) -> str:
        style = WRONGNESS_STYLES[style_name]
        mutated = await self.client.chat(
            messages=[
                {"role": "system", "content": mutator_system_prompt(style)},
                {
                    "role": "user",
                    "content": (
                        f"Q: {user_prompt}\n"
                        f"Helpful: {authentic_prefix}\n"
                        "Opposite:"
                    ),
                },
            ],
            max_tokens=self.settings.mutator_max_tokens,
            temperature=self.settings.mutator_temperature,
            top_p=self.settings.top_p,
        )
        cleaned = _clean_mutation(mutated)
        if _is_bare_polarity(cleaned):
            action_prefill = _question_action_prefill(user_prompt, cleaned)
            if action_prefill is not None:
                return action_prefill
            cleaned = await self._expand_bare_polarity(
                user_prompt=user_prompt,
                authentic_prefix=authentic_prefix,
                style_name=style_name,
                polarity=cleaned,
            )
        return cleaned

    async def _expand_bare_polarity(
        self,
        *,
        user_prompt: str,
        authentic_prefix: str,
        style_name: str,
        polarity: str,
    ) -> str:
        style = WRONGNESS_STYLES[style_name]
        prefill = f"{polarity.rstrip('.')},"
        if self.settings.vllm_prefill:
            messages = [
                {"role": "system", "content": mutator_expansion_system_prompt(style)},
                {
                    "role": "user",
                    "content": f"Q: {user_prompt}\nHelpful: {authentic_prefix}",
                },
                {"role": "assistant", "content": prefill},
            ]
            extra_body = {
                "add_generation_prompt": False,
                "continue_final_message": True,
            }
        else:
            messages = [
                {"role": "system", "content": mutator_expansion_system_prompt(style)},
                {
                    "role": "user",
                    "content": (
                        f"Q: {user_prompt}\n"
                        f"Helpful: {authentic_prefix}\n"
                        f"Prefix: {prefill}\n"
                        "Continue:"
                    ),
                },
            ]
            extra_body = None

        expanded = await self.client.chat(
            messages=messages,
            max_tokens=self.settings.mutator_max_tokens,
            temperature=self.settings.mutator_temperature,
            top_p=self.settings.top_p,
            extra_body=extra_body,
        )
        cleaned_expansion = " ".join(expanded.strip().strip('"').split())
        if not cleaned_expansion:
            raise ValueError("mutation model returned bare polarity and empty expansion")
        return f"{prefill} {cleaned_expansion}"


def _clean_mutation(text: str) -> str:
    cleaned = " ".join(text.strip().strip('"').split())
    if not cleaned:
        raise ValueError("mutation model returned an empty prefix")
    for marker in ("Mutated prefix:", "Prefix:"):
        cleaned = cleaned.removeprefix(marker).strip()
    if not cleaned:
        raise ValueError("mutation model returned only a label")
    return cleaned.rstrip()


def _is_bare_polarity(text: str) -> bool:
    return text.strip().rstrip(".!,;:").casefold() in {"yes", "no"}


def _question_action_prefill(user_prompt: str, polarity: str) -> str | None:
    action = _extract_yes_no_action(user_prompt)
    if action is None:
        return None

    normalized_polarity = polarity.strip().rstrip(".!,;:").casefold()
    if normalized_polarity == "yes":
        return f"Yes, {action} because"
    if normalized_polarity == "no":
        return f"No, don't {action} because"
    return None


def _extract_yes_no_action(user_prompt: str) -> str | None:
    question = " ".join(user_prompt.strip().rstrip("?.!").split())
    normalized = question.casefold()
    prefixes = (
        "should i ",
        "should we ",
        "should you ",
        "can i ",
        "can we ",
        "could i ",
        "could we ",
        "may i ",
        "may we ",
        "do i ",
        "do we ",
        "would it be better to ",
        "is it okay to ",
    )
    for prefix in prefixes:
        if normalized.startswith(prefix):
            action = question[len(prefix) :].strip()
            if action:
                return _to_second_person_action(action)
    return None


def _to_second_person_action(action: str) -> str:
    replacements = {
        r"\bmy\b": "your",
        r"\bmine\b": "yours",
        r"\bme\b": "you",
        r"\bmyself\b": "yourself",
    }
    converted = action
    for pattern, replacement in replacements.items():
        converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)
    return converted
