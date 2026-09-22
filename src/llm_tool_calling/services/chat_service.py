"""Application service for basic LLM interaction."""

from llm_tool_calling.llm.base import LLMClient

class ChatService:
    """Service responsible for basic LLM conversations."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def answer(self, message: str) -> str:
        """Generate an answer for the supplied message."""

        return self.llm.generate(message)