"""Tests for the order assistant API endpoint."""

from fastapi.testclient import TestClient

import llm_tool_calling.main as main_module


client = TestClient(main_module.app)

class FakeOrderAssistantService:
    def answer(
        self,
        message: str,
        request_id: str | None = None,
    ) -> str:
        return f"Fake order assistant response for: {message}"
    
def test_order_assistant_rejects_empty_message() -> None:
    """Empty messages should fail request validation."""

    response = client.post(
        "/order-assistant",
        json={
            "message": "",
        },
    )

    assert response.status_code == 422

def test_order_assistant_returns_answer(monkeypatch) -> None:
    """Successful requests should return the assistant answer."""

    fake_service = FakeOrderAssistantService()

    monkeypatch.setattr(
        main_module,
        "order_assistant_service",
        fake_service,
    )

    response = client.post(
        "/order-assistant",
        json={
            "message": "Where is order 12345?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": (
            "Fake order assistant response for: "
            "Where is order 12345?"
        )
    }

def test_order_assistant_rejects_missing_message() -> None:
    """Requests without a message should fail validation."""

    response = client.post(
        "/order-assistant",
        json={},
    )

    assert response.status_code == 422

def test_order_assistant_returns_request_id(
    monkeypatch,
) -> None:
    fake_service = FakeOrderAssistantService()

    monkeypatch.setattr(
        main_module,
        "order_assistant_service",
        fake_service,
    )

    response = client.post(
        "/order-assistant",
        json={
            "message": "Where is order 12345?",
        },
    )

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

def test_order_assistant_preserves_request_id(
    monkeypatch,
) -> None:
    fake_service = FakeOrderAssistantService()

    monkeypatch.setattr(
        main_module,
        "order_assistant_service",
        fake_service,
    )

    response = client.post(
        "/order-assistant",
        headers={
            "X-Request-ID": "test-request-123",
        },
        json={
            "message": "Where is order 12345?",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["X-Request-ID"]
        == "test-request-123"
    )