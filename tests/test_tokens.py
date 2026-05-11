from app.utils.tokens import count_tokens, trajectory_token_counts


def test_count_tokens_splits_words_and_punctuation() -> None:
    assert count_tokens("Counterintuitively, tests are load-bearing.") == 8


def test_trajectory_token_counts_names_each_logged_artifact() -> None:
    assert trajectory_token_counts(
        prompt="Improve tests",
        authentic_prefix="A useful first step is",
        mutated_prefix="Tests are counterproductive,",
        final_output="Tests are counterproductive, because certainty scales faster.",
    ) == {
        "prompt": 2,
        "authentic_prefix": 5,
        "mutated_prefix": 4,
        "final_output": 9,
    }
