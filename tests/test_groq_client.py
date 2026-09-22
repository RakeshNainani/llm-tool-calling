"""Tests for the Groq LLM client."""

from httpx import Request, Response
import pytest

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from llm_tool_calling.llm.exceptions import (
    LLMProviderError,
)
from llm_tool_calling.llm.groq_client import (
    GroqLLMClient,
)


def test_generate_normalizes_connection_error(
    monkeypatch,
) -> None:
    """Groq connection errors should become LLMProviderError."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    def raise_connection_error(
        *args,
        **kwargs,
    ):
        raise APIConnectionError(
            request=request
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_connection_error,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate(
            "Hello"
        )

    error = exc_info.value

    assert (
        error.error_type
        == "connection"
    )

    assert (
        error.provider
        == "groq"
    )

    assert str(error) == (
        "LLM provider request failed."
    )

def test_generate_normalizes_timeout_error(
    monkeypatch,
) -> None:
    """Groq timeout errors should become LLMProviderError."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    def raise_timeout_error(
        *args,
        **kwargs,
    ):
        raise APITimeoutError(
            request=request
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_timeout_error,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate("Hello")

    error = exc_info.value

    assert error.error_type == "timeout"
    assert error.provider == "groq"


def test_generate_normalizes_rate_limit_error(
    monkeypatch,
) -> None:
    """Groq rate-limit errors should become LLMProviderError."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    response = Response(
        status_code=429,
        request=request,
    )

    def raise_rate_limit_error(
        *args,
        **kwargs,
    ):
        raise RateLimitError(
            "Rate limit exceeded.",
            response=response,
            body=None,
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_rate_limit_error,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate("Hello")

    error = exc_info.value

    assert error.error_type == "rate_limit"
    assert error.provider == "groq"


def test_generate_normalizes_authentication_error(
    monkeypatch,
) -> None:
    """Groq authentication errors should become LLMProviderError."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    response = Response(
        status_code=401,
        request=request,
    )

    def raise_authentication_error(
        *args,
        **kwargs,
    ):
        raise AuthenticationError(
            "Authentication failed.",
            response=response,
            body=None,
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_authentication_error,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate("Hello")

    error = exc_info.value

    assert error.error_type == "authentication"
    assert error.provider == "groq"

def test_generate_with_tools_normalizes_connection_error(
    monkeypatch,
) -> None:
    """Tool-calling requests should normalize Groq connection errors."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    def raise_connection_error(
        *args,
        **kwargs,
    ):
        raise APIConnectionError(
            request=request
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_connection_error,
    )

    messages = [
        {
            "role": "user",
            "content": "Where is order 12345?",
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_order_status",
                "description": "Get order status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                        }
                    },
                    "required": ["order_id"],
                },
            },
        }
    ]

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate_with_tools(
            messages,
            tools,
        )

    error = exc_info.value

    assert error.error_type == "connection"
    assert error.provider == "groq"

def test_generate_normalizes_provider_status_error(
    monkeypatch,
) -> None:
    """Other Groq API status errors should become provider_error."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    response = Response(
        status_code=500,
        request=request,
    )

    def raise_status_error(
        *args,
        **kwargs,
    ):
        raise APIStatusError(
            "Provider failure.",
            response=response,
            body=None,
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        raise_status_error,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate("Hello")

    error = exc_info.value

    assert error.error_type == "provider_error"
    assert error.provider == "groq"

def test_groq_client_accepts_explicit_timeout() -> None:
    """Explicit timeout should override environment configuration."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
        timeout=15.0,
    )

    assert client.timeout == 15.0

def test_generate_retries_connection_error(
    monkeypatch,
) -> None:
    """Transient connection failures should be retried."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
        max_retries=2,
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    attempts = 0

    def create_completion(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        raise APIConnectionError(
            request=request
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        create_completion,
    )

    monkeypatch.setattr(
        "llm_tool_calling.llm.groq_client.time.sleep",
        lambda _: None,
    )

    with pytest.raises(
        LLMProviderError
    ):
        client.generate("Hello")

    assert attempts == 3

def test_generate_succeeds_after_transient_failure(
    monkeypatch,
) -> None:
    """A request should succeed if a transient failure recovers."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
        max_retries=2,
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    attempts = 0

    class FakeMessage:
        content = "Recovered response"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    def create_completion(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise APIConnectionError(
                request=request
            )

        return FakeResponse()

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        create_completion,
    )

    monkeypatch.setattr(
        "llm_tool_calling.llm.groq_client.time.sleep",
        lambda _: None,
    )

    result = client.generate("Hello")

    assert result == "Recovered response"
    assert attempts == 2

def test_generate_does_not_retry_authentication_error(
    monkeypatch,
) -> None:
    """Authentication failures should fail immediately."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
        max_retries=2,
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    response = Response(
        status_code=401,
        request=request,
    )

    attempts = 0

    def create_completion(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        raise AuthenticationError(
            "Authentication failed.",
            response=response,
            body=None,
        )

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        create_completion,
    )

    with pytest.raises(
        LLMProviderError
    ) as exc_info:
        client.generate("Hello")

    assert attempts == 1
    assert (
        exc_info.value.error_type
        == "authentication"
    )


def test_retry_is_logged(
    monkeypatch,
    caplog,
) -> None:
    """Transient provider retries should be logged."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
        max_retries=1,
    )

    request = Request(
        "POST",
        "https://api.groq.com/test",
    )

    attempts = 0

    class FakeMessage:
        content = "Recovered"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    def create_completion(*args, **kwargs):
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise APIConnectionError(
                request=request
            )

        return FakeResponse()

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        create_completion,
    )

    monkeypatch.setattr(
        "llm_tool_calling.llm.groq_client.time.sleep",
        lambda _: None,
    )

    with caplog.at_level("WARNING"):
        result = client.generate("Hello")

    assert result == "Recovered"

    assert (
        "Retrying LLM provider request"
        in caplog.text
    )

    assert "provider=groq" in caplog.text
    assert "retry=1" in caplog.text

def test_successful_provider_request_is_logged(
    monkeypatch,
    caplog,
) -> None:
    """Successful LLM requests should log provider latency."""

    client = GroqLLMClient(
        api_key="test-key",
        model="test-model",
    )

    class FakeMessage:
        content = "Hello"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    def create_completion(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        client.client.chat.completions,
        "create",
        create_completion,
    )

    with caplog.at_level("INFO"):
        result = client.generate("Hello")

    assert result == "Hello"

    assert (
        "LLM provider request succeeded"
        in caplog.text
    )

    assert "provider=groq" in caplog.text
    assert "attempt=1" in caplog.text
    assert "duration_ms=" in caplog.text