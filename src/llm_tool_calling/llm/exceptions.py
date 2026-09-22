"""Exceptions raised by the LLM provider layer."""


class LLMProviderError(Exception):
    """Base exception for LLM provider failures."""

    def __init__(
        self,
        message: str,
        *,
        error_type: str,
        provider: str,
    ) -> None:
        super().__init__(message)

        self.error_type = error_type
        self.provider = provider