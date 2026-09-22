"""Schemas for the order assistant API."""

from pydantic import BaseModel, Field


class OrderAssistantRequest(BaseModel):
    """Request payload for the order assistant."""

    message: str = Field(
        min_length=1,
        max_length=2000,
    )


class OrderAssistantResponse(BaseModel):
    """Response payload from the order assistant."""

    answer: str