"""Tests for the order assistant API endpoint."""

from fastapi.testclient import TestClient

import llm_tool_calling.main as main_module


client = TestClient(main_module.app)

class FakeOrderAssistantService:
    """Fake order assistant used for API testing."""

    def answer(self, message: str) -> str:
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