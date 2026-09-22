"""Tests for tool execution."""

import pytest

from llm_tool_calling.tools.executor import execute_tool

from pydantic import ValidationError

def test_execute_order_status_tool() -> None:
    result = execute_tool(
        "get_order_status",
        '{"order_id":"12345"}',
    )

    assert result["order_id"] == "12345"
    assert result["status"] == "shipped"
    assert result["estimated_delivery"] == "2026-09-25"


def test_execute_order_status_not_found() -> None:
    result = execute_tool(
        "get_order_status",
        '{"order_id":"99999"}',
    )

    assert result["order_id"] == "99999"
    assert result["status"] == "not_found"


def test_unknown_tool_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown tool"):
        execute_tool(
            "delete_everything",
            "{}",
        )

def test_invalid_tool_arguments_are_rejected() -> None:
    with pytest.raises(ValidationError):
        execute_tool(
            "get_order_status",
            '{"order_id":""}',
        )

def test_execute_customer_orders_tool() -> None:
    result = execute_tool(
        "get_customer_orders",
        '{"customer_id":"C001"}',
    )

    assert result["customer_id"] == "C001"
    assert result["order_ids"] == [
        "12345",
        "67890",
    ]

def test_execute_customer_orders_unknown_customer() -> None:
    result = execute_tool(
        "get_customer_orders",
        '{"customer_id":"C999"}',
    )

    assert result["customer_id"] == "C999"
    assert result["order_ids"] == []

def test_customer_orders_invalid_arguments_are_rejected() -> None:
    with pytest.raises(ValidationError):
        execute_tool(
            "get_customer_orders",
            '{"customer_id":""}',
        )