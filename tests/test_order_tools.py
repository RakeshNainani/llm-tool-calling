"""Tests for order tools."""

from llm_tool_calling.tools.order_tools import get_order_status


def test_get_order_status_shipped() -> None:
    result = get_order_status("12345")

    assert result["order_id"] == "12345"
    assert result["status"] == "shipped"
    assert result["estimated_delivery"] == "2026-09-25"


def test_get_order_status_processing() -> None:
    result = get_order_status("67890")

    assert result["order_id"] == "67890"
    assert result["status"] == "processing"


def test_get_order_status_not_found() -> None:
    result = get_order_status("99999")

    assert result["order_id"] == "99999"
    assert result["status"] == "not_found"