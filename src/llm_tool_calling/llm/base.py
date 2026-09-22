"""Base interface for LLM providers."""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(self, message: str) -> str:
        """Generate a response for a user message."""
        pass