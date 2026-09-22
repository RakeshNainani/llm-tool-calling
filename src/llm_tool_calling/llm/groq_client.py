"""Groq implementation of the LLM client."""
import os

from dotenv import load_dotenv
from groq import Groq

from llm_tool_calling.llm.base import LLMClient

load_dotenv()

class GroqLLMClient(LLMClient):
    """LLM client backed by Groq."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        )

        self.client = Groq(api_key=api_key)


    def generate(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return response.choices[0].message.content or ""