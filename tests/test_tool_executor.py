"""Tests for tool execution."""

import pytest

from llm_tool_calling.tools.executor import execute_tool

from llm_tool_calling.tools.exceptions import ToolExecutionError

from llm_tool_calling.tools.registry import TOOL_REGISTRY

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
    with pytest.raises(
        ToolExecutionError,
        match="Unknown tool",
    ) as exc_info:
        execute_tool(
            "delete_everything",
            "{}",
        )

    assert exc_info.value.error_type == "unknown_tool"
    assert exc_info.value.tool_name == "delete_everything"



def test_invalid_tool_arguments_are_rejected() -> None:
    with pytest.raises(
        ToolExecutionError,
        match="failed validation",
    ) as exc_info:
        execute_tool(
            "get_order_status",
            '{"order_id":""}',
        )

    assert exc_info.value.error_type == "invalid_arguments"
    assert exc_info.value.tool_name == "get_order_status"



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
    with pytest.raises(
        ToolExecutionError,
        match="failed validation",
    ) as exc_info:
        execute_tool(
            "get_customer_orders",
            '{"customer_id":""}',
        )

    assert exc_info.value.error_type == "invalid_arguments"
    assert exc_info.value.tool_name == "get_customer_orders"

def test_malformed_tool_arguments_are_rejected() -> None:
    with pytest.raises(
        ToolExecutionError,
        match="malformed JSON",
    ) as exc_info:
        execute_tool(
            "get_order_status",
            '{"order_id":"12345"',
        )

    assert exc_info.value.error_type == "malformed_arguments"
    assert exc_info.value.tool_name == "get_order_status"


def test_tool_execution_failure_is_normalized(
    monkeypatch,
) -> None:
    def failing_tool(order_id: str) -> dict:
        raise RuntimeError("Database unavailable")

    monkeypatch.setitem(
        TOOL_REGISTRY["get_order_status"],
        "function",
        failing_tool,
    )

    with pytest.raises(
        ToolExecutionError,
        match="Tool execution failed",
    ) as exc_info:
        execute_tool(
            "get_order_status",
            '{"order_id":"12345"}',
        )

    assert exc_info.value.error_type == "execution_failed"
    assert exc_info.value.tool_name == "get_order_status"


def test_successful_tool_execution_is_logged(
    caplog,
) -> None:
    with caplog.at_level("INFO"):
        execute_tool(
            "get_order_status",
            '{"order_id":"12345"}',
        )

    assert "Tool execution succeeded" in caplog.text
    assert "tool=get_order_status" in caplog.text
    assert "duration_ms=" in caplog.text

def test_invalid_arguments_are_logged(
    caplog,
) -> None:
    with caplog.at_level("WARNING"):
        with pytest.raises(ToolExecutionError):
            execute_tool(
                "get_order_status",
                '{"order_id":""}',
            )

    assert "Tool execution rejected" in caplog.text
    assert "tool=get_order_status" in caplog.text
    assert "error_type=invalid_arguments" in caplog.text

def test_tool_log_contains_request_id(
    caplog,
) -> None:
    with caplog.at_level("INFO"):
        execute_tool(
            "get_order_status",
            '{"order_id":"12345"}',
            request_id="test-request-123",
        )

    assert "request_id=test-request-123" in caplog.text