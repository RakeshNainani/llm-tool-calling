"""Tests for application dependencies."""

from llm_tool_calling.dependencies import get_llm_client
from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.llm.groq_client import GroqLLMClient


def test_get_llm_client_returns_llm_client() -> None:
    """Dependency should return the configured LLM implementation."""

    client = get_llm_client()

    assert isinstance(client, LLMClient)
    assert isinstance(client, GroqLLMClient)

def test_main_module_does_not_create_llm_client(
    monkeypatch,
) -> None:
    """Importing main should not instantiate the Groq client."""

    import importlib

    import llm_tool_calling.llm.groq_client as groq_module
    import llm_tool_calling.main as main_module

    def fail_if_created(*args, **kwargs):
        raise AssertionError(
            "GroqLLMClient was created during module import."
        )

    monkeypatch.setattr(
        groq_module,
        "GroqLLMClient",
        fail_if_created,
    )

    importlib.reload(main_module)