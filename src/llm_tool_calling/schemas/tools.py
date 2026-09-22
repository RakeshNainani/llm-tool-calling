"""Pydantic models for tool arguments."""

from pydantic import BaseModel, Field


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