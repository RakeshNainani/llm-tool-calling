"""Order assistant service implementing the LLM tool-calling loop."""

import json

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.tools.executor import execute_tool
from llm_tool_calling.tools.schemas import ORDER_TOOLS

MAX_TOOL_ITERATIONS = 5

class OrderAssistantService:
    """Orchestrates the LLM and order tools."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def answer(self, user_message: str) -> str:
        """Answer a user request using available order tools."""

        messages = [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.llm.generate_with_tools(
                messages,
                ORDER_TOOLS,
            )

            assistant_message = response.choices[0].message

            # Final answer: no additional tools are required.
            if not assistant_message.tool_calls:
                return assistant_message.content or ""

            # Preserve the assistant's tool request.
            messages.append(
                assistant_message.model_dump(
                    exclude_none=True
                )
            )

            # Execute every tool requested by the model.
            for tool_call in assistant_message.tool_calls:
                tool_result = execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result),
                    }
                )
        raise RuntimeError( "Maximum tool-calling iterations exceeded.")