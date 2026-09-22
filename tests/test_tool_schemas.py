"""Tests for tool argument validation."""

import pytest
from pydantic import ValidationError

from llm_tool_calling.schemas.tools import GetOrderStatusArgs


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