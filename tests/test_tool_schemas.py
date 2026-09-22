"""Tests for tool argument validation."""

import pytest
from pydantic import ValidationError

from llm_tool_calling.schemas.tools import (
    GetCustomerOrdersArgs,
    GetOrderStatusArgs,
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