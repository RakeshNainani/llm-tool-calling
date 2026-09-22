"""Order assistant service implementing the LLM tool-calling loop."""

import json

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.tools.executor import execute_tool
from llm_tool_calling.tools.schemas import ORDER_TOOLS


class OrderAssistantService:
    """Orchestrates the LLM and order tools."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def answer(self, user_message: str) -> str:
        """Answer a user request using tools when required."""

        messages = [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        response = self.llm.generate_with_tools(
            messages,
            ORDER_TOOLS,
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        tool_call = assistant_message.tool_calls[0]
        tool_result = execute_tool(
            tool_call.function.name,
            tool_call.function.arguments,
        )
        messages.append(
            assistant_message.model_dump(
                exclude_none=True
            )
        )

        messages.append( {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result),
        })

        final_response = self.llm.generate_with_tools(
            messages,
            ORDER_TOOLS,
        )

        final_message = final_response.choices[0].message

        return final_message.content or ""