from app.styles.prompts import WRONGNESS_STYLES, continuation_system_prompt, mutator_system_prompt


def test_required_wrongness_styles_exist() -> None:
    assert set(WRONGNESS_STYLES) == {
        "contrarian_expert",
        "startup_thoughtleader",
        "bureaucratic_hex_curse",
        "stackoverflow_goblin",
        "wellness_influencer",
    }


def test_prompts_include_selected_style() -> None:
    style = WRONGNESS_STYLES["startup_thoughtleader"]
    assert style.name in mutator_system_prompt(style)
    assert style.description in continuation_system_prompt(style)
