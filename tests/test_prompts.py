from app.styles.prompts import (
    WRONGNESS_STYLES,
    continuation_system_prompt,
    mutator_expansion_system_prompt,
    mutator_system_prompt,
)


def test_required_wrongness_styles_exist() -> None:
    assert set(WRONGNESS_STYLES) == {
        "contrarian_expert",
        "startup_thoughtleader",
        "bureaucratic_hex_curse",
        "stackoverflow_goblin",
        "wellness_influencer",
    }


def test_continuation_prompt_includes_selected_style() -> None:
    style = WRONGNESS_STYLES["startup_thoughtleader"]
    prompt = continuation_system_prompt(style)

    assert style.description in prompt
    assert "Yes recommends the user's action" in prompt
    assert "No rejects it" in prompt


def test_mutator_prompt_stays_topic_agnostic() -> None:
    style = WRONGNESS_STYLES["contrarian_expert"]
    prompt = (
        mutator_system_prompt(style) + "\n" + mutator_expansion_system_prompt(style)
    ).lower()

    assert "python" not in prompt
    assert "code" not in prompt
    assert "bug" not in prompt
    assert "test" not in prompt
    assert "depend" not in prompt
