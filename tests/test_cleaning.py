import pytest

from app.models.authentic import _clean_prefix
from app.models.mutator import _clean_mutation


def test_clean_prefix_strips_quotes_and_sentence_tail() -> None:
    assert (
        _clean_prefix('"The best approach is to improve sleep."')
        == "The best approach is to improve sleep"
    )


def test_clean_mutation_rejects_empty_output() -> None:
    with pytest.raises(ValueError, match="empty prefix"):
        _clean_mutation("   ")


def test_clean_mutation_preserves_model_output() -> None:
    assert _clean_mutation("A generated answer starts here") == "A generated answer starts here"
