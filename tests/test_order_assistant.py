"""Tests for the order assistant orchestration."""

import json
import pytest

from llm_tool_calling.llm.base import LLMClient
from llm_tool_calling.services.order_assistant import OrderAssistantService


class FakeFunction:
    """Represents the function requested by the fake LLM."""

    def __init__(
        self,
        name: str,
        arguments: str,
    ) -> None:
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    """Represents a tool call requested by the fake LLM."""

    def __init__(
        self,
        tool_call_id: str,
        function: FakeFunction,
    ) -> None:
        self.id = tool_call_id
        self.function = function


class FakeMessage:
    """Represents a message returned by the fake LLM."""

    def __init__(
        self,
        content: str | None = None,
        tool_calls: list[FakeToolCall] | None = None,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(
        self,
        exclude_none: bool = False,
    ) -> dict:
        """Convert the fake message into a dictionary."""

        result = {
            "role": "assistant",
            "content": self.content,
        }

        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in self.tool_calls
            ]

        if exclude_none:
            result = {
                key: value
                for key, value in result.items()
                if value is not None
            }

        return result

class FakeChoice:
    """Represents one choice returned by the fake LLM."""

    def __init__(self, message: FakeMessage) -> None:
        self.message = message

class FakeResponse:
    """Represents a response returned by the fake LLM."""

    def __init__(self, message: FakeMessage) -> None:
        self.choices = [
            FakeChoice(message)
        ]

class FakeToolCallingLLM(LLMClient):
    """Fake LLM that simulates a two-step tool-calling conversation."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(self, message: str) -> str:
        return f"Fake response for: {message}"

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        self.call_count += 1

        if self.call_count == 1:
            function = FakeFunction(
                "get_order_status",
                '{"order_id":"12345"}',
            )

            tool_call = FakeToolCall(
                "call_123",
                function,
            )

            message = FakeMessage(
                content=None,
                tool_calls=[tool_call],
            )

            return FakeResponse(message)

        message = FakeMessage(
            content="Order 12345 has shipped.",
            tool_calls=None,
        )

        return FakeResponse(message)

class FakeDirectAnswerLLM(LLMClient):
    """Fake LLM that answers without requesting a tool."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(self, message: str) -> str:
        return f"Fake response for: {message}"

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        self.call_count += 1

        message = FakeMessage(
            content="Shipped means the order has left the warehouse.",
            tool_calls=None,
        )

        return FakeResponse(message)

class FakeNeverEndingToolLLM(LLMClient):
    """Fake LLM that always requests another tool."""

    def generate(self, message: str) -> str:
        raise NotImplementedError

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        return FakeResponse(
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call_loop",
                        FakeFunction(
                            "get_order_status",
                            '{"order_id":"12345"}',
                        ),
                    )
                ]
            )
        )

class FakeMultiToolLLM(LLMClient):
    """Fake LLM that requires multiple rounds of tool execution."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(self, message: str) -> str:
        raise NotImplementedError

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        self.call_count += 1

        # First LLM turn:
        # find the customer's orders.
        if self.call_count == 1:
            return FakeResponse(
                FakeMessage(
                    tool_calls=[
                        FakeToolCall(
                            "call_customer_orders",
                            FakeFunction(
                                "get_customer_orders",
                                '{"customer_id":"C001"}',
                            ),
                        )
                    ]
                )
            )

        # Second LLM turn:
        # check the status of both discovered orders.
        if self.call_count == 2:
            return FakeResponse(
                FakeMessage(
                    tool_calls=[
                        FakeToolCall(
                            "call_order_12345",
                            FakeFunction(
                                "get_order_status",
                                '{"order_id":"12345"}',
                            ),
                        ),
                        FakeToolCall(
                            "call_order_67890",
                            FakeFunction(
                                "get_order_status",
                                '{"order_id":"67890"}',
                            ),
                        ),
                    ]
                )
            )

        # Third LLM turn:
        # return the final answer.
        return FakeResponse(
            FakeMessage(
                content=(
                    "Customer C001 has orders 12345 and 67890. "
                    "Order 12345 is shipped and order 67890 "
                    "is processing."
                ),
                tool_calls=None,
            )
        )

class FakeInvalidArgumentsLLM(LLMClient):
    """Fake LLM that first requests a tool with invalid arguments."""

    def __init__(self) -> None:
        self.call_count = 0
        self.received_messages: list[dict] = []

    def generate(self, message: str) -> str:
        raise NotImplementedError

    def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ):
        self.call_count += 1
        self.received_messages = list(messages)

        if self.call_count == 1:
            return FakeResponse(
                FakeMessage(
                    tool_calls=[
                        FakeToolCall(
                            "call_invalid",
                            FakeFunction(
                                "get_order_status",
                                '{"order_id":""}',
                            ),
                        )
                    ]
                )
            )

        return FakeResponse(
            FakeMessage(
                content=(
                    "I could not check the order because "
                    "the order ID was invalid."
                ),
                tool_calls=None,
            )
        )


    
    
def test_order_assistant_without_tool_call() -> None:
    """Test that a direct LLM answer does not execute a tool."""

    llm = FakeDirectAnswerLLM()
    assistant = OrderAssistantService(llm)

    answer = assistant.answer("What does shipped mean?")

    assert answer == "Shipped means the order has left the warehouse."
    assert llm.call_count == 1

def test_order_assistant_with_tool_call() -> None:
    """Test the complete LLM -> tool -> LLM flow."""

    llm = FakeToolCallingLLM()
    assistant = OrderAssistantService(llm)

    answer = assistant.answer("Where is order 12345?")

    assert answer == "Order 12345 has shipped."
    assert llm.call_count == 2


def test_order_assistant_stops_after_max_iterations() -> None:
    llm = FakeNeverEndingToolLLM()
    assistant = OrderAssistantService(llm)

    with pytest.raises(
        RuntimeError,
        match="Maximum tool-calling iterations exceeded",
    ):
        assistant.answer(
            "Keep checking order 12345."
        )

def test_order_assistant_handles_multiple_tool_rounds() -> None:
    llm = FakeMultiToolLLM()
    assistant = OrderAssistantService(llm)

    answer = assistant.answer(
        "What orders does customer C001 have "
        "and what is their status?"
    )

    assert answer == (
        "Customer C001 has orders 12345 and 67890. "
        "Order 12345 is shipped and order 67890 "
        "is processing."
    )

    assert llm.call_count == 3

def test_order_assistant_returns_tool_error_to_llm() -> None:
    llm = FakeInvalidArgumentsLLM()
    assistant = OrderAssistantService(llm)

    answer = assistant.answer(
        "Check my order."
    )

    assert answer == (
        "I could not check the order because "
        "the order ID was invalid."
    )

    assert llm.call_count == 2
    tool_message = llm.received_messages[-1]

    assert tool_message["role"] == "tool"

    tool_content = json.loads(
        tool_message["content"]
    )

    assert tool_content["success"] is False
    assert tool_content["error"]["type"] == "invalid_arguments"
    assert tool_content["error"]["tool_name"] == "get_order_status"