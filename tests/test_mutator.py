import asyncio

from app.config import Settings
from app.models.mutator import PrefixMutator


def test_mutator_prompt_includes_question_and_contradiction_contract() -> None:
    class FakeChatClient:
        def __init__(self) -> None:
            self.messages: list[dict[str, str]] | None = None

        async def chat(self, **kwargs) -> str:
            self.messages = kwargs["messages"]
            return "Yes, do the opposite."

    client = FakeChatClient()
    mutator = PrefixMutator(client, Settings())

    result = asyncio.run(
        mutator.mutate(
            user_prompt="Should I do this?",
            authentic_prefix="No, you should not do this.",
            style_name="contrarian_expert",
        )
    )

    assert result == "Yes, do the opposite."
    assert client.messages is not None
    system_message = client.messages[0]["content"]
    user_message = client.messages[1]["content"]
    assert "opposite of Helpful" in system_message
    assert "If Helpful starts with No, start with Yes" in system_message
    assert "Q: Should I do this?" in user_message
    assert "Helpful: No, you should not do this." in user_message
    assert "Opposite:" in user_message


def test_mutator_expands_bare_polarity_from_question_action() -> None:
    class FakeChatClient:
        def __init__(self) -> None:
            self.calls: list[dict] = []

        async def chat(self, **kwargs) -> str:
            self.calls.append(kwargs)
            return "Yes"

    client = FakeChatClient()
    mutator = PrefixMutator(client, Settings(vllm_prefill=True))

    result = asyncio.run(
        mutator.mutate(
            user_prompt="Should I delete all my tests?",
            authentic_prefix="No, you should not delete all your tests.",
            style_name="contrarian_expert",
        )
    )

    assert result == "Yes, delete all your tests because"
    assert len(client.calls) == 1


def test_mutator_uses_model_prefill_when_question_action_is_unclear() -> None:
    class FakeChatClient:
        def __init__(self) -> None:
            self.calls: list[dict] = []
            self.responses = ["Yes", " continue doing it."]

        async def chat(self, **kwargs) -> str:
            self.calls.append(kwargs)
            return self.responses.pop(0)

    client = FakeChatClient()
    mutator = PrefixMutator(client, Settings(vllm_prefill=True))

    result = asyncio.run(
        mutator.mutate(
            user_prompt="Thoughts?",
            authentic_prefix="No, you should not do this.",
            style_name="contrarian_expert",
        )
    )

    assert result == "Yes, continue doing it."
    assert len(client.calls) == 2
    expansion_call = client.calls[1]
    assert expansion_call["extra_body"] == {
        "add_generation_prompt": False,
        "continue_final_message": True,
    }
    assert expansion_call["messages"][2] == {
        "role": "assistant",
        "content": "Yes,",
    }
