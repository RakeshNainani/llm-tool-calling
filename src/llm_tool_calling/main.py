"""FastAPI entry point for the LLM Tool Calling project."""


from uuid import uuid4
from fastapi import FastAPI, Request

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

@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next,
):
    """Attach a correlation ID to every HTTP request."""

    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid4()),
    )

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


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
    http_request: Request,
) -> OrderAssistantResponse:
    """Answer order-related requests using LLM tool calling."""

    answer = order_assistant_service.answer(
        request.message,
        request_id=http_request.state.request_id,
    )

    return OrderAssistantResponse(
        answer=answer
    )