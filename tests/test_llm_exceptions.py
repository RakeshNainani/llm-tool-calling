"""Tests for LLM provider exceptions."""

from llm_tool_calling.llm.exceptions import LLMProviderError


def test_llm_provider_error_contains_context() -> None:
    """LLM provider errors should retain useful context."""

    error = LLMProviderError(
        "Provider request failed.",
        error_type="provider_error",
        provider="groq",
    )

    assert str(error) == "Provider request failed."
    assert error.error_type == "provider_error"
    assert error.provider == "groq"