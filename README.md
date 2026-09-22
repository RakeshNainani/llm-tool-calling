# LLM Tool Calling Demo

A hands-on Python project for learning how production-style LLM applications use **tool / function calling**.

The project demonstrates how an LLM can decide that external information or an application capability is required, request a tool, and allow the **application** to validate and execute that tool before returning the result to the LLM.

The key principle is:

> The LLM requests an action. The application controls and executes the action.

---

## Learning Objectives

This project is designed to demonstrate:

- LLM provider abstraction
- Dependency injection
- Structured tool definitions
- LLM tool / function calling
- Tool argument validation with Pydantic
- Tool registries
- Controlled tool execution
- LLM → Tool → LLM orchestration
- Conversation history during tool calling
- Separation of model reasoning from application execution
- Testing LLM applications without external API calls
- FastAPI integration

---

## Current Architecture

```text
User / Client
     |
     v
FastAPI
     |
     v
Application Service
     |
     +----------------------+
     |                      |
     v                      v
LLMClient              Tool Layer
     |                      |
     v                      v
GroqLLMClient          ORDER_TOOLS
     |                      |
     v                      v
Groq SDK              TOOL_REGISTRY
                            |
                            v
                     Argument Validation
                            |
                            v
                       execute_tool()
                            |
                            v
                    get_order_status()
```

The `OrderAssistantService` orchestrates the interaction between the LLM and the tool layer.

---

## Tool Calling Flow

The complete tool-calling lifecycle currently works as follows:

```text
User Request
     |
     v
LLM Call #1
     |
     v
Does the model request a tool?
     |
     +-------------------+
     |                   |
    No                  Yes
     |                   |
     v                   v
Return LLM         Read Tool Request
Response                  |
                          v
                   Validate Tool Name
                          |
                          v
                  Parse Tool Arguments
                          |
                          v
                 Pydantic Validation
                          |
                          v
                    Execute Tool
                          |
                          v
                     Tool Result
                          |
                          v
              Add Result to Message History
                          |
                          v
                     LLM Call #2
                          |
                          v
                    Final Response
```

Example:

```text
User:
"Where is order 12345?"

        |
        v

LLM:
"I need get_order_status."

        |
        v

Tool Request:
get_order_status(
    order_id="12345"
)

        |
        v

Application:
Validates arguments

        |
        v

Application:
Executes get_order_status()

        |
        v

Tool Result:
{
    "order_id": "12345",
    "status": "shipped",
    "estimated_delivery": "2026-09-25"
}

        |
        v

LLM:
"Order 12345 has shipped and is expected
to arrive on September 25, 2026."
```

The LLM does **not** directly execute `get_order_status()`.

The application remains the control plane.

---

## Project Structure

```text
llm-tool-calling/
|
├── .env
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock
|
├── src/
│   └── llm_tool_calling/
│       |
│       ├── __init__.py
│       ├── main.py
│       |
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── groq_client.py
│       |
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── chat.py
│       │   └── tools.py
│       |
│       ├── services/
│       │   ├── __init__.py
│       │   ├── chat_service.py
│       │   └── order_assistant.py
│       |
│       └── tools/
│           ├── __init__.py
│           ├── order_tools.py
│           ├── schemas.py
│           ├── registry.py
│           └── executor.py
│
└── tests/
    ├── test_llm.py
    ├── test_order_tools.py
    ├── test_tool_schemas.py
    ├── test_tool_executor.py
    └── test_order_assistant.py
```

---

# Core Components

## 1. LLM Abstraction

`LLMClient` defines the interface expected by application services.

```text
Application Service
        |
        v
     LLMClient
        ^
        |
  GroqLLMClient
```

The application depends on the abstraction rather than directly depending on the Groq SDK.

This makes it easier to:

- change providers
- test application logic
- introduce fake LLM clients
- reduce provider coupling

The current implementation supports:

```python
generate(...)
```

for basic LLM interaction and:

```python
generate_with_tools(...)
```

for tool-enabled conversations.

---

## 2. Groq LLM Adapter

`GroqLLMClient` implements `LLMClient` using the Groq Python SDK.

The adapter is responsible for provider-specific communication.

```text
Application
    |
    v
LLMClient
    |
    v
GroqLLMClient
    |
    v
Groq SDK
    |
    v
LLM
```

The current model is configured through the environment:

```env
GROQ_MODEL=openai/gpt-oss-20b
```

---

## 3. Tool Implementation

The project currently provides:

```python
get_order_status(order_id)
```

The tool returns mock order information such as:

```json
{
  "order_id": "12345",
  "status": "shipped",
  "estimated_delivery": "2026-09-25"
}
```

Tool implementation is independent of the LLM.

Conceptually, this function could later call:

- an order database
- REST API
- ERP system
- CRM
- microservice
- external service

without changing the fundamental tool-calling architecture.

---

## 4. Tool Schema

The LLM does not inspect Python functions directly.

Instead, the application provides a tool schema describing:

- tool name
- tool purpose
- accepted parameters
- required parameters

Example conceptually:

```json
{
  "name": "get_order_status",
  "description": "Get the current status of an order",
  "parameters": {
    "order_id": {
      "type": "string"
    }
  }
}
```

The schema is the **model-facing contract**.

The Python function is the **application implementation**.

These are deliberately separate concerns.

---

## 5. Tool Argument Validation

LLM-generated tool arguments must not be trusted automatically.

The project validates arguments using Pydantic.

For example:

```text
LLM-generated JSON arguments
        |
        v
json.loads()
        |
        v
Python dictionary
        |
        v
GetOrderStatusArgs
        |
        v
Pydantic validation
        |
        v
Validated arguments
```

Invalid arguments are rejected before the tool is executed.

---

## 6. Tool Registry

The application maintains an explicit registry of executable tools.

Conceptually:

```text
Tool Name
    |
    v
TOOL_REGISTRY
    |
    +--> Python Function
    |
    +--> Argument Validator
```

Example:

```python
TOOL_REGISTRY = {
    "get_order_status": {
        "function": get_order_status,
        "validator": GetOrderStatusArgs,
    }
}
```

This registry acts as an application-controlled allowlist.

The model cannot execute an arbitrary Python function simply by generating its name.

---

## 7. Tool Executor

`execute_tool()` is responsible for controlled execution.

Its responsibilities are:

```text
Tool Request
    |
    v
Check Registry
    |
    v
Parse Arguments
    |
    v
Validate Arguments
    |
    v
Locate Function
    |
    v
Execute Function
    |
    v
Return Result
```

Unknown tools are rejected.

Invalid arguments are rejected.

Only registered tools can be executed.

---

## 8. Order Assistant Orchestration

`OrderAssistantService` implements the complete LLM tool-calling lifecycle.

The service coordinates:

```text
LLM
 |
Tool Schema
 |
Tool Request
 |
Tool Executor
 |
Tool Result
 |
Conversation History
 |
LLM
 |
Final Answer
```

The service handles two paths.

### Path A — No Tool Required

```text
User
 |
 v
LLM
 |
 v
Normal Response
 |
 v
Return to User
```

Only one LLM call is required.

### Path B — Tool Required

```text
User
 |
 v
LLM Call #1
 |
 v
Tool Request
 |
 v
Application Validation
 |
 v
Tool Execution
 |
 v
Tool Result
 |
 v
LLM Call #2
 |
 v
Final Natural-Language Response
```

---

# Message History

Tool calling requires conversation state to be preserved.

A simplified message sequence looks like:

```text
[
    User Message,

    Assistant Tool Request,

    Tool Result
]
```

The second LLM call receives this history so the model knows:

1. what the user asked
2. which tool it requested
3. what result the application returned

The `tool_call_id` acts as a correlation identifier between the model's tool request and the application's tool result.

```text
Assistant Tool Request
        |
        | tool_call_id
        v
Application Tool Result
```

---

# Security Boundary

A central principle of the project is:

```text
LLM = decision/request layer

Application = execution/control layer
```

The model may request:

```text
get_order_status
```

but the application decides:

- whether the tool exists
- whether it is allowed
- whether arguments are valid
- whether execution should proceed
- what result is returned

This separation becomes especially important for tools that can perform write operations or access sensitive enterprise systems.

---

# Testing Strategy

The project uses `pytest`.

Run all tests with:

```powershell
uv run pytest -v
```

The current test suite covers:

- LLM abstraction
- dependency injection
- order tool behavior
- tool argument validation
- unknown tool rejection
- controlled tool execution
- complete LLM → Tool → LLM orchestration
- direct LLM responses without tool execution

---

## Testing Without Real LLM Calls

Automated orchestration tests do not call Groq.

Instead, fake LLM implementations simulate provider responses.

```text
              FAKE
               |
               v
          LLM Call #1
               |
               v
          Tool Request
               |
               v
             REAL
               |
               v
         execute_tool()
               |
               v
         TOOL_REGISTRY
               |
               v
      Pydantic Validation
               |
               v
      get_order_status()
               |
               v
           Tool Result
               |
               v
              FAKE
               |
               v
          LLM Call #2
               |
               v
          Final Answer
```

This provides deterministic tests while avoiding:

- network dependency
- API cost
- model variability
- provider outages
- API credentials in automated tests

---

# Setup

## Prerequisites

- Python 3.13+
- `uv`
- Git
- Groq API key

---

## Clone the Repository

```powershell
git clone <repository-url>
cd llm-tool-calling
```

---

## Install Dependencies

```powershell
uv sync
```

---

## Configure Environment Variables

Create:

```text
.env
```

using:

```text
.env.example
```

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env`.

---

## Run the Application

```powershell
uv run uvicorn llm_tool_calling.main:app --reload
```

The application can then be inspected through FastAPI's local interactive API documentation.

---

## Health Check

The application currently exposes:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Basic Chat Endpoint

The application also provides:

```http
POST /chat
```

Example request:

```json
{
  "message": "What is tool calling?"
}
```

The endpoint demonstrates the basic application → LLM interaction.

The order-assistant tool-calling flow currently exists at the service layer and will be exposed through an API endpoint in the next stage.

---

# Development Stages

## Stage 1 — Project Foundation

Completed:

- Python project setup
- `uv`
- FastAPI
- `/health`
- project package structure
- Git initialization

---

## Stage 2 — LLM Abstraction

Completed:

- `LLMClient`
- `GroqLLMClient`
- dependency injection
- `ChatService`
- `/chat`
- fake LLM testing

---

## Stage 3 — First Tool

Completed:

- `get_order_status`
- mock order data
- unit tests for tool behavior

---

## Stage 4 — Tool Schema and Tool Selection

Completed:

- model-facing tool schema
- tool-enabled Groq request
- automatic tool selection
- inspection of model-generated tool calls

---

## Stage 5 — Tool Argument Validation

Completed:

- Pydantic argument models
- JSON argument parsing
- valid argument handling
- invalid argument rejection

---

## Stage 6 — Tool Registry and Executor

Completed:

- `TOOL_REGISTRY`
- controlled tool lookup
- argument validation before execution
- unknown tool rejection
- centralized `execute_tool()`

---

## Stage 7 — LLM Tool Calling Orchestration

Completed:

- message-history-aware LLM calls
- `OrderAssistantService`
- first LLM call
- tool request detection
- application-controlled tool execution
- tool result serialization
- `tool_call_id` correlation
- second LLM call
- final natural-language answer
- no-tool/direct-answer path
- automated orchestration tests using fake LLM clients

The application now supports the complete:

```text
LLM
 ↓
Tool Request
 ↓
Application Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

lifecycle.

---

## Stage 8 — Order Assistant API

Planned:

Expose the completed `OrderAssistantService` through FastAPI.

Target architecture:

```text
Client
  |
  v
FastAPI
  |
  v
OrderAssistantService
  |
  v
LLM Tool Calling Loop
  |
  v
Final Response
```

---

## Stage 9 — Multiple Tools

Planned:

Introduce additional tools such as:

```text
get_customer_orders(customer_id)
```

and explore:

- multiple tool definitions
- tool selection
- multiple tool calls
- iterative tool execution

---

## Stage 10 — Production Hardening

Planned topics include:

- error handling
- malformed model arguments
- tool execution failures
- structured logging
- tracing
- authentication
- authorization
- tool-level permissions
- read vs write tools
- guardrails
- human approval
- timeouts
- retries
- observability

---

# Current Limitation

The current orchestration handles the first requested tool call:

```python
assistant_message.tool_calls[0]
```

This is intentionally simple for the learning stage.

A more production-oriented implementation would use an iterative tool loop capable of processing:

```text
LLM
 |
 +--> Tool A
 |
 +--> Tool B
 |
 +--> Tool C
 |
 v
Final Answer
```

until the model stops requesting tools or an application-defined stopping condition is reached.

---

# Engineering Principles Demonstrated

This project intentionally applies several production-oriented engineering principles.

### Dependency Inversion

Application services depend on `LLMClient`, not directly on the Groq SDK.

### Separation of Concerns

Tool implementation, tool schemas, validation, execution, orchestration, and provider communication are separated.

### Explicit Tool Allowlisting

Only tools registered by the application can be executed.

### Validate Before Execution

LLM-generated arguments are treated as untrusted input and validated before reaching application functions.

### Application-Controlled Execution

The model can request actions but does not directly execute application code.

### Test External Boundaries

External LLM calls are replaced with deterministic fakes during orchestration testing.

---

# Key Mental Model

The most important concept demonstrated by this project is:

```text
The LLM is not the application.

The LLM proposes.
The application validates.
The application executes.
The application controls.
```

Tool calling connects probabilistic model reasoning with deterministic application capabilities.

A production AI system therefore requires both:

```text
Model Intelligence
       +
Application Engineering
```

The model determines what capability may be useful.

The application determines what is actually permitted to happen.