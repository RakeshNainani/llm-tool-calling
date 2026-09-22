"""FastAPI entry point for the LLM Tool Calling project."""

from fastapi import FastAPI


app = FastAPI(
    title="LLM Tool Calling Demo",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}