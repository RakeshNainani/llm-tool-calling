"""Tests for tool execution exceptions."""

from llm_tool_calling.tools.exceptions import ToolExecutionError


def test_tool_execution_error_contains_context() -> None:
    error = ToolExecutionError(
        "Invalid tool arguments.",
        error_type="invalid_arguments",
        tool_name="get_order_status",
    )

    assert str(error) == "Invalid tool arguments."
    assert error.error_type == "invalid_arguments"
    assert error.tool_name == "get_order_status"