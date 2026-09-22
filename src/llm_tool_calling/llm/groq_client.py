"""Groq implementation of the LLM client."""

import os
import time
from typing import Callable, TypeVar
import logging
import time

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.llm.exceptions import LLMProviderError

T = TypeVar("T")

load_dotenv()

logger = logging.getLogger(__name__)

class GroqLLMClient(LLMClient):
    """LLM client backed by Groq."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retries: int = 2,
    ) -> None:
        """Initialize the Groq client."""

        key = (
            api_key
            or os.getenv("GROQ_API_KEY")
        )

        if not key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.model = (
            model
            or os.getenv("GROQ_MODEL")
            or "openai/gpt-oss-20b"
        )

        self.timeout = (
            timeout
            if timeout is not None
            else float(
                os.getenv(
                    "GROQ_TIMEOUT_SECONDS",
                    "30",
                )
            )
        )

        self.max_retries = max_retries

        self.client = Groq(
            api_key=key,
            timeout=self.timeout,
            max_retries=0,
        )

    def generate(
        self,
        message: str,
    ) -> str:
        """Generate a response for a user message."""

        response = self._execute_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            )
        )

        return (
            response.choices[0].message.content
            or ""
        )
    
    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        """Generate a response with tools available to the model."""

        return self._execute_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
        )


    def _execute_with_retry(
        self,
        operation: Callable[[], T],
    ) -> T:
        """Execute an LLM request with bounded retries."""

        attempt = 0

        while True:
            start_time = time.perf_counter()

            try:
                result = operation()

                duration_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                logger.info(
                    "LLM provider request succeeded: "
                    "provider=groq attempt=%s "
                    "duration_ms=%.2f",
                    attempt + 1,
                    duration_ms,
                )

                return result

            except (
                APITimeoutError,
                RateLimitError,
                APIConnectionError,
            ) as exc:
                duration_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                if attempt >= self.max_retries:
                    logger.error(
                        "LLM provider retries exhausted: "
                        "provider=groq attempts=%s "
                        "duration_ms=%.2f",
                        attempt + 1,
                        duration_ms,
                    )

                    self._raise_provider_error(exc)

                attempt += 1

                delay = 0.1 * attempt

                logger.warning(
                    "Retrying LLM provider request: "
                    "provider=groq retry=%s "
                    "max_retries=%s "
                    "delay_seconds=%.2f "
                    "duration_ms=%.2f",
                    attempt,
                    self.max_retries,
                    delay,
                    duration_ms,
                )

                time.sleep(delay)

            except (
                AuthenticationError,
                APIStatusError,
            ) as exc:
                duration_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                logger.error(
                    "LLM provider request failed: "
                    "provider=groq "
                    "duration_ms=%.2f",
                    duration_ms,
                )

                self._raise_provider_error(exc)

    def _raise_provider_error(
        self,
        exc: Exception,
    ) -> None:
        """Translate Groq SDK errors into application-level errors."""

        if isinstance(
            exc,
            APITimeoutError,
        ):
            error_type = "timeout"

        elif isinstance(
            exc,
            RateLimitError,
        ):
            error_type = "rate_limit"

        elif isinstance(
            exc,
            AuthenticationError,
        ):
            error_type = "authentication"

        elif isinstance(
            exc,
            APIConnectionError,
        ):
            error_type = "connection"

        elif isinstance(
            exc,
            APIStatusError,
        ):
            error_type = "provider_error"

        else:
            error_type = "provider_error"

        raise LLMProviderError(
            "LLM provider request failed.",
            error_type=error_type,
            provider="groq",
        ) from exc