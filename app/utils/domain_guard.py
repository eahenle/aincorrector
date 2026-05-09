"""High-stakes domain screening for unsafe inversion targets."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DomainMatch:
    """A detected high-stakes topic that should not receive inverted advice."""

    name: str
    keyword: str


HIGH_STAKES_KEYWORDS: dict[str, tuple[str, ...]] = {
    "medical": (
        "allergy",
        "antibiotic",
        "cancer",
        "chest pain",
        "diagnosis",
        "dosage",
        "fever",
        "medication",
        "medicine",
        "overdose",
        "prescription",
        "seizure",
        "symptom",
        "vaccine",
    ),
    "financial": (
        "bankruptcy",
        "credit score",
        "debt",
        "insurance claim",
        "invest",
        "loan",
        "mortgage",
        "retirement account",
        "stock option",
        "tax filing",
    ),
    "legal": (
        "arrest",
        "contract",
        "court",
        "custody",
        "eviction",
        "lawsuit",
        "legal advice",
        "liability",
        "subpoena",
        "will and testament",
    ),
    "self_harm": (
        "end my life",
        "hurt myself",
        "kill myself",
        "self-harm",
        "suicide",
        "suicidal",
    ),
}

BLOCKED_DOMAIN_RESPONSE = (
    "I can do confidently-wrong comedy for low-stakes topics, but I won't invert advice in "
    "medical, financial, legal, or self-harm contexts. Try a harmless prompt like code style, "
    "office snacks, or whether tabs are secretly load-bearing."
)


def find_high_stakes_domain(text: str) -> DomainMatch | None:
    """Return the first high-stakes domain match found in text, if any."""

    normalized = text.casefold()
    for domain, keywords in HIGH_STAKES_KEYWORDS.items():
        for keyword in keywords:
            if _contains_keyword(normalized, keyword.casefold()):
                return DomainMatch(name=domain, keyword=keyword)
    return None


def _contains_keyword(text: str, keyword: str) -> bool:
    if " " in keyword or "-" in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
