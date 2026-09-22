"""Tests for the order assistant API."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from llm_tool_calling.dependencies import get_llm_client
from llm_tool_calling.main import app


class FakeLLMClient:
    """Fake LLM client used by API tests."""

    def generate(self, message: str) -> str:
        """Return a deterministic chat response."""

        return f"Fake response for: {message}"

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        """Return a deterministic response without tool calls."""

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="Your order is being processed.",
                        tool_calls=None,
                    )
                )
            ]
        )


def override_llm_client() -> FakeLLMClient:
    """Return a fake LLM client for API tests."""

    return FakeLLMClient()


app.dependency_overrides[get_llm_client] = (
    override_llm_client
)

client = TestClient(app)


def test_order_assistant_returns_answer() -> None:
    """Order assistant should return the LLM answer."""

    response = client.post(
        "/order-assistant",
        json={
            "message": "Where is order 12345?"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "answer": "Your order is being processed."
    }


def test_order_assistant_returns_request_id() -> None:
    """Response should contain a generated request ID."""

    response = client.post(
        "/order-assistant",
        json={
            "message": "Where is order 12345?"
        },
    )

    assert response.status_code == 200

    assert "X-Request-ID" in response.headers

    assert response.headers["X-Request-ID"]


def test_order_assistant_preserves_request_id() -> None:
    """Caller-provided request ID should be preserved."""

    request_id = "test-request-123"

    response = client.post(
        "/order-assistant",
        headers={
            "X-Request-ID": request_id,
        },
        json={
            "message": "Where is order 12345?"
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["X-Request-ID"]
        == request_id
    )

def test_order_assistant_rejects_empty_message() -> None:
    """Empty messages should fail request validation."""

    response = client.post(
        "/order-assistant",
        json={
            "message": "",
        },
    )

    assert response.status_code == 422


def test_order_assistant_rejects_missing_message() -> None:
    """Requests without a message should fail validation."""

    response = client.post(
        "/order-assistant",
        json={},
    )

    assert response.status_code == 422