"""Tests for the LLM abstraction."""

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.services.chat_service import ChatService


class FakeLLMClient(LLMClient):
    """Fake LLM implementation used for testing."""

    def generate(self, message: str) -> str:
        return f"Fake response for: {message}"

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        """Return a fake tool-enabled response."""
        raise NotImplementedError


def test_fake_llm_client() -> None:
    llm = FakeLLMClient()

    response = llm.generate("Hello")

    assert response == "Fake response for: Hello"

def test_chat_service_with_fake_llm() -> None:
    llm = FakeLLMClient()

    service = ChatService(llm)

    response = service.answer("What is tool calling?")

    assert response == "Fake response for: What is tool calling?"