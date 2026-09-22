"""Base interface for LLM providers."""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(self, message: str) -> str:
        """Generate a response for a user message."""
        pass

    @abstractmethod
    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        """Generate a response with tools available to the model."""
        pass