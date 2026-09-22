"""Pydantic models for tool arguments."""

from pydantic import BaseModel, Field, model_validator
from typing import Any


class GetOrderStatusArgs(BaseModel):
    """Arguments accepted by the get_order_status tool."""

    order_id: str = Field(
        min_length=1,
        description="Unique order identifier.",
    )


class GetCustomerOrdersArgs(BaseModel):
    """Arguments accepted by the get_customer_orders tool."""

    customer_id: str = Field(
        min_length=1,
        description="Unique customer identifier.",
    )

class ToolError(BaseModel):
    """Structured information about a tool execution failure."""

    type: str
    message: str
    tool_name: str


class ToolResult(BaseModel):
    """Structured result returned by the application tool layer."""

    success: bool
    result: Any | None = None
    error: ToolError | None = None

    @model_validator(mode="after")
    def validate_result_state(self) -> "ToolResult":
        """Ensure success and failure states are consistent."""

        if self.success and self.error is not None:
            raise ValueError(
                "Successful tool results cannot contain an error."
            )

        if not self.success and self.error is None:
            raise ValueError(
                "Failed tool results must contain an error."
            )

        if not self.success and self.result is not None:
            raise ValueError(
                "Failed tool results cannot contain a result."
            )

        return self