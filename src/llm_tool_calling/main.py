"""FastAPI entry point for the LLM Tool Calling project."""

from fastapi import FastAPI

from llm_tool_calling.llm.groq_client import GroqLLMClient
from llm_tool_calling.schemas.chat import ChatRequest, ChatResponse
from llm_tool_calling.services.chat_service import ChatService

from llm_tool_calling.schemas.order_assistant import (
    OrderAssistantRequest,
    OrderAssistantResponse,
)
from llm_tool_calling.services.order_assistant import OrderAssistantService


llm = GroqLLMClient()
chat_service  = ChatService(llm)

order_assistant_service = OrderAssistantService(llm)

app = FastAPI(
    title="LLM Tool Calling Demo",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat requests and return responses."""
    answer = chat_service.answer(request.message)
    return ChatResponse(answer=answer)

@app.post(
    "/order-assistant",
    response_model=OrderAssistantResponse,
)
def order_assistant(
    request: OrderAssistantRequest,
) -> OrderAssistantResponse:
    """Answer order-related requests using LLM tool calling."""

    answer = order_assistant_service.answer(
        request.message
    )

    return OrderAssistantResponse(
        answer=answer
    )