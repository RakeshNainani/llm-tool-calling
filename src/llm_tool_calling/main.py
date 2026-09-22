"""FastAPI entry point for the LLM Tool Calling project."""

from fastapi import FastAPI

from llm_tool_calling.llm.groq_client import GroqLLMClient
from llm_tool_calling.schemas.chat import ChatRequest, ChatResponse
from llm_tool_calling.services.chat_service import ChatService


llm = GroqLLMClient()
chat_service  = ChatService(llm)

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