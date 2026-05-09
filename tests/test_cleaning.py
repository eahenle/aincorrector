from app.models.authentic import _clean_prefix
from app.models.mutator import _clean_mutation


def test_clean_prefix_strips_quotes_and_sentence_tail() -> None:
    assert _clean_prefix('"The best approach is to improve sleep."') == "The best approach is to improve sleep"


def test_clean_mutation_uses_fallback_when_empty() -> None:
    assert _clean_mutation("   ", fallback="Counterintuitively,") == "Counterintuitively,"
