"""Tests for tool argument validation."""

import pytest
from pydantic import ValidationError

from llm_tool_calling.schemas.tools import (
    GetCustomerOrdersArgs,
    GetOrderStatusArgs,
    ToolError,
    ToolResult,
)

def test_valid_order_status_arguments() -> None:
    args = GetOrderStatusArgs.model_validate(
        {
            "order_id": "12345",
        }
    )

    assert args.order_id == "12345"


def test_empty_order_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GetOrderStatusArgs.model_validate(
            {
                "order_id": "",
            }
        )


def test_missing_order_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GetOrderStatusArgs.model_validate({})



def test_valid_customer_orders_arguments() -> None:
    args = GetCustomerOrdersArgs.model_validate(
        {
            "customer_id": "C001",
        }
    )

    assert args.customer_id == "C001"


def test_empty_customer_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GetCustomerOrdersArgs.model_validate(
            {
                "customer_id": "",
            }
        )


def test_missing_customer_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GetCustomerOrdersArgs.model_validate({})


def test_successful_tool_result() -> None:
    result = ToolResult(
        success=True,
        result={
            "order_id": "12345",
            "status": "shipped",
        },
    )

    assert result.success is True
    assert result.result["order_id"] == "12345"
    assert result.error is None

def test_failed_tool_result() -> None:
    result = ToolResult(
        success=False,
        error=ToolError(
            type="invalid_arguments",
            message="Tool arguments failed validation.",
            tool_name="get_order_status",
        ),
    )

    assert result.success is False
    assert result.result is None
    assert result.error is not None
    assert result.error.type == "invalid_arguments"

def test_successful_tool_result_cannot_contain_error() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            success=True,
            result={"order_id": "12345"},
            error=ToolError(
                type="execution_failed",
                message="Tool execution failed.",
                tool_name="get_order_status",
            ),
        )

def test_failed_tool_result_requires_error() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            success=False,
        )

def test_failed_tool_result_cannot_contain_result() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            success=False,
            result={"order_id": "12345"},
            error=ToolError(
                type="execution_failed",
                message="Tool execution failed.",
                tool_name="get_order_status",
            ),
        )
