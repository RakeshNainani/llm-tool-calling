"""FastAPI application dependencies."""

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.llm.groq_client import GroqLLMClient


def get_llm_client() -> LLMClient:
    """Return the configured LLM client."""

    return GroqLLMClient()