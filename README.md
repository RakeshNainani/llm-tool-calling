# LLM Tool Calling Demo

A hands-on Python project for learning how production-style LLM applications use **tool / function calling**.

The project demonstrates how an LLM can determine that an external capability is required, request a tool, and allow the **application** to validate and execute that tool before returning the result to the LLM.

The core principle is:

> The LLM requests an action. The application controls and executes the action.

---

## Learning Objectives

This project demonstrates:

- LLM provider abstraction
- Dependency injection
- FastAPI integration
- Pydantic request and response validation
- Structured tool definitions
- LLM tool / function calling
- Tool argument validation
- Tool registries
- Controlled tool execution
- LLM → Tool → LLM orchestration
- Conversation history during tool calling
- Tool-call correlation
- Separation of model reasoning from application execution
- API-layer testing
- Testing LLM applications without external API calls

---

# Current Architecture

```text
                         Client
                           |
                           v
                        FastAPI
                           |
             +-------------+-------------+
             |                           |
             v                           v
        ChatService             OrderAssistantService
             |                           |
             |                           |
             +------------+--------------+
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
                          |
                          |
                   Tool Request
                          |
                          v
                     ORDER_TOOLS
                          |
                          v
                    TOOL_REGISTRY
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

The `OrderAssistantService` orchestrates the interaction between the LLM and the application tool layer.

---

# Complete Request Flow

A request such as:

```json
{
  "message": "Where is order 12345?"
}
```

travels through:

```text
POST /order-assistant
        |
        v
OrderAssistantRequest
        |
        v
OrderAssistantService
        |
        v
LLM Call #1
        |
        v
Does the model request a tool?
        |
        +----------------------+
        |                      |
       No                     Yes
        |                      |
        v                      v
 Return LLM Answer       Tool Request
                               |
                               v
                       Check Tool Registry
                               |
                               v
                         Parse Arguments
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
                         Final Answer
                               |
                               v
                   OrderAssistantResponse
                               |
                               v
                          HTTP JSON
```

---

# Example Tool-Calling Interaction

User:

```text
Where is order 12345?
```

The LLM determines that it needs order information and requests:

```text
get_order_status(
    order_id="12345"
)
```

The application validates and executes the tool.

Tool result:

```json
{
  "order_id": "12345",
  "status": "shipped",
  "estimated_delivery": "2026-09-25"
}
```

The tool result is returned to the LLM.

The LLM then produces a user-facing response such as:

```text
Order 12345 has been shipped and is expected
to arrive on September 25, 2026.
```

The important distinction is:

```text
LLM
 |
 | requests
 v
Tool

Application
 |
 | validates + executes
 v
Tool
```

The LLM does **not** directly execute Python functions.

---

# Project Structure

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
│       │   ├── order_assistant.py
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
    ├── test_order_assistant.py
    └── test_order_assistant_api.py
```

---

# Core Components

## 1. LLM Abstraction

`LLMClient` defines the interface expected by the application services.

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

This provides:

- provider isolation
- easier testing
- dependency injection
- reduced coupling
- ability to introduce additional providers later

The abstraction currently supports:

```python
generate(...)
```

for normal LLM interaction and:

```python
generate_with_tools(...)
```

for tool-enabled conversations.

---

## 2. Groq LLM Adapter

`GroqLLMClient` implements the `LLMClient` abstraction using the Groq Python SDK.

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

Provider-specific implementation details remain inside the adapter.

The current model is configured through an environment variable:

```env
GROQ_MODEL=openai/gpt-oss-20b
```

---

## 3. Chat Service

`ChatService` demonstrates basic application-to-LLM interaction without tool calling.

```text
FastAPI
   |
   v
ChatService
   |
   v
LLMClient
   |
   v
GroqLLMClient
```

It provides a simpler baseline before introducing tool orchestration.

---

## 4. Tool Implementation

The project currently provides:

```python
get_order_status(order_id)
```

The tool returns mock order information.

Example:

```json
{
  "order_id": "12345",
  "status": "shipped",
  "estimated_delivery": "2026-09-25"
}
```

Another example:

```json
{
  "order_id": "67890",
  "status": "processing",
  "estimated_delivery": "2026-09-28"
}
```

Unknown orders return:

```json
{
  "order_id": "99999",
  "status": "not_found"
}
```

The current implementation uses in-memory data for learning purposes.

In a production system, the same tool could call:

- a database
- REST API
- ERP
- CRM
- order-management service
- enterprise microservice
- external API

without fundamentally changing the LLM tool-calling architecture.

---

## 5. Tool Schema

The LLM does not inspect the Python function directly.

Instead, the application exposes a structured tool definition describing:

- tool name
- description
- parameters
- parameter types
- required parameters

Conceptually:

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

The distinction is important:

```text
Tool Schema
    |
    +--> Model-facing contract

Python Function
    |
    +--> Application implementation
```

The schema tells the LLM what capability exists.

The Python function performs the actual operation.

---

## 6. Tool Argument Validation

LLM-generated arguments are treated as untrusted input.

The current validation flow is:

```text
LLM-generated arguments
        |
        v
JSON String
        |
        v
json.loads()
        |
        v
Python Dictionary
        |
        v
GetOrderStatusArgs
        |
        v
Pydantic Validation
        |
        v
Validated Arguments
        |
        v
Tool Execution
```

For example:

```json
{
  "order_id": "12345"
}
```

is validated before reaching:

```python
get_order_status(...)
```

Invalid or missing arguments are rejected before execution.

---

## 7. Tool Registry

The application maintains an explicit registry of executable tools.

Conceptually:

```text
Tool Name
    |
    v
TOOL_REGISTRY
    |
    +------> Function
    |
    +------> Validator
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

The registry acts as an application-controlled allowlist.

The LLM cannot execute an arbitrary Python function simply by generating its name.

For example, if the model requested:

```text
delete_everything
```

and that function was not registered, the application would reject the request.

---

## 8. Tool Executor

`execute_tool()` provides centralized controlled tool execution.

Its responsibilities are:

```text
Tool Request
    |
    v
Check Registry
    |
    v
Reject Unknown Tool
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

This creates an important security boundary between:

```text
Probabilistic LLM output
```

and:

```text
Deterministic application execution
```

---

# Order Assistant Service

`OrderAssistantService` implements the complete LLM tool-calling lifecycle.

It coordinates:

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

There are currently two execution paths.

---

## Path A — No Tool Required

For a question such as:

```text
What does shipped mean?
```

the model may answer directly.

```text
User
 |
 v
LLM Call #1
 |
 v
No Tool Requested
 |
 v
Return Answer
```

Only one LLM call is required.

---

## Path B — Tool Required

For:

```text
Where is order 12345?
```

the flow becomes:

```text
User
 |
 v
LLM Call #1
 |
 v
Tool Requested
 |
 v
get_order_status
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
Final Natural-Language Answer
```

---

# Message History

Tool calling requires conversation state to be maintained between LLM calls.

A simplified history looks like:

```text
[
    User Message,

    Assistant Tool Request,

    Tool Result
]
```

The second LLM call receives this history so the model knows:

1. what the user originally requested
2. which tool it requested
3. which arguments it generated
4. what result the application returned

---

## Tool Call Correlation

A `tool_call_id` connects the assistant's tool request with the application's result.

```text
Assistant Tool Request
        |
        | id = call_123
        |
        v
Application Executes Tool
        |
        v
Tool Result
        |
        | tool_call_id = call_123
        |
        v
LLM Call #2
```

This becomes particularly important when multiple tools or multiple calls are involved.

---

# FastAPI Layer

The project exposes the application through FastAPI.

Current endpoints:

```text
GET   /health
POST  /chat
POST  /order-assistant
```

---

## Health Endpoint

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

```http
POST /chat
```

Example request:

```json
{
  "message": "What is tool calling?"
}
```

This endpoint demonstrates basic:

```text
HTTP
 ↓
ChatService
 ↓
LLM
 ↓
HTTP
```

interaction without application tools.

---

# Order Assistant API

The complete tool-calling workflow is exposed through:

```http
POST /order-assistant
```

Example request:

```json
{
  "message": "Where is order 12345?"
}
```

Example response:

```json
{
  "answer": "Order 12345 has been shipped and is expected to be delivered on September 25, 2026."
}
```

The exact natural-language wording can vary because the final answer is generated by the LLM.

---

## API Architecture

```text
Client
  |
  | POST /order-assistant
  v
FastAPI
  |
  v
OrderAssistantRequest
  |
  v
OrderAssistantService
  |
  v
LLM Tool Calling Loop
  |
  v
OrderAssistantResponse
  |
  v
HTTP JSON
```

The FastAPI endpoint itself remains thin.

Its responsibilities are:

```text
Validate HTTP Request
        |
        v
Call Application Service
        |
        v
Construct HTTP Response
```

Tool selection, argument parsing, tool execution and LLM orchestration remain outside the API layer.

---

# Validation Boundaries

The project currently demonstrates two distinct validation boundaries.

## Boundary 1 — Client Input

```text
Untrusted HTTP Input
        |
        v
OrderAssistantRequest
        |
        v
Pydantic Validation
        |
        +---- Invalid ----> HTTP 422
        |
       Valid
        |
        v
Application
```

For example:

```json
{
  "message": ""
}
```

is rejected because `message` requires a minimum length.

Likewise:

```json
{}
```

is rejected because `message` is required.

---

## Boundary 2 — LLM Tool Arguments

After the HTTP request has passed validation, the LLM may generate another set of untrusted data:

```text
Client
  |
  v
HTTP Validation
  |
  v
Application
  |
  v
LLM
  |
  v
Generated Tool Arguments
  |
  v
GetOrderStatusArgs
  |
  v
Pydantic Validation
  |
  v
Tool
```

Therefore:

```text
Client-generated input
```

and:

```text
LLM-generated input
```

are validated independently.

---

# Security Boundary

A central principle of this project is:

```text
LLM = reasoning / request layer

Application = control / execution layer
```

The model may request:

```text
get_order_status
```

but the application determines:

- whether the tool exists
- whether the tool is registered
- whether it is permitted
- whether arguments are valid
- whether execution should proceed
- what result is returned

This separation becomes especially important when tools can:

- modify data
- send emails
- create orders
- issue refunds
- access private information
- interact with enterprise systems
- perform financial operations

---

# Testing Strategy

The project uses `pytest`.

Run the complete test suite with:

```powershell
uv run pytest -v
```

The current suite contains tests across several architectural layers.

```text
API Tests
    |
    v
HTTP + Pydantic + Endpoint
    |
    v
Service Tests
    |
    v
LLM → Tool → LLM Orchestration
    |
    v
Executor Tests
    |
    v
Registry + Validation + Execution
    |
    v
Tool Tests
    |
    v
Business Function
```

---

## Tool Tests

Tests verify:

- known orders
- different order statuses
- unknown orders

These tests exercise the business function directly.

---

## Tool Validation Tests

Tests verify:

- valid arguments
- empty order IDs
- missing order IDs

These verify the Pydantic tool argument boundary.

---

## Tool Executor Tests

Tests verify:

- registered tool execution
- unknown order behavior
- unknown tool rejection
- invalid tool argument rejection

These exercise:

```text
Registry
   +
Validation
   +
Execution
```

---

## Order Assistant Service Tests

The complete orchestration is tested without making real Groq requests.

A fake LLM simulates:

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

The tool executor and business tool remain real.

Only the external LLM dependency is replaced.

Tests cover both:

```text
LLM → Tool → LLM
```

and:

```text
LLM → Direct Answer
```

paths.

---

# API Testing

FastAPI endpoints are tested using:

```python
TestClient
```

The API tests cover:

- successful request handling
- HTTP response structure
- empty message rejection
- missing message rejection
- Pydantic validation
- application service delegation

For successful API tests, the real order assistant service is replaced using pytest `monkeypatch`.

```text
pytest
   |
   v
TestClient
   |
   v
FastAPI
   |
   v
FakeOrderAssistantService
   |
   v
HTTP Response
```

This allows the API layer to be tested without:

- Groq API calls
- network dependency
- API cost
- provider variability
- external credentials

---

# Why Fake the LLM?

Calling a real LLM from every automated test would introduce:

```text
Network dependency
API cost
Provider outages
Model variability
Rate limits
Authentication requirements
Non-deterministic answers
```

Instead:

```text
Unit / Integration Tests
        |
        v
Fake External LLM
        |
        +
        |
Real Application Logic
```

This keeps tests fast and deterministic.

Real provider integration can be tested separately.

---

# Setup

## Prerequisites

Install:

- Python 3.13+
- `uv`
- Git
- VS Code or another Python IDE
- Groq API key

---

## Clone Repository

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

as the template.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env`.

---

# Run the Application

Start FastAPI with:

```powershell
uv run uvicorn llm_tool_calling.main:app --reload
```

The server should start locally.

Open the FastAPI interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Available endpoints should include:

```text
GET   /health
POST  /chat
POST  /order-assistant
```

---

# Run Tests

Run all tests:

```powershell
uv run pytest -v
```

At the completion of Stage 8, the project contains:

```text
17 passing tests
```

The current environment may also report dependency deprecation warnings originating from the FastAPI/Starlette testing dependency stack.

These warnings do not currently indicate failures in the application tests and will be reviewed during dependency/production hardening.

---

# Development Stages

## Stage 1 — Project Foundation

Completed:

- Python project setup
- `uv`
- FastAPI
- `/health`
- package structure
- Git initialization
- initial README

---

## Stage 2 — LLM Abstraction

Completed:

- `LLMClient`
- `GroqLLMClient`
- dependency injection
- `ChatService`
- `/chat`
- fake LLM testing

Architecture:

```text
ChatService
     |
     v
LLMClient
     ^
     |
GroqLLMClient
```

---

## Stage 3 — First Tool

Completed:

- `get_order_status`
- mock order data
- tool unit tests

Key principle:

```text
Tool implementation
        !=
LLM integration
```

The tool was implemented and tested independently before connecting it to the model.

---

## Stage 4 — Tool Schema and Tool Selection

Completed:

- model-facing tool schema
- Groq tool-enabled request
- automatic tool selection
- inspection of generated tool calls
- inspection of tool arguments

Key principle:

```text
Tool Schema
    =
Model-facing description

Tool Function
    =
Application implementation
```

---

## Stage 5 — Tool Argument Validation

Completed:

- Pydantic tool argument model
- JSON argument parsing
- valid argument handling
- missing argument rejection
- invalid argument rejection

Key principle:

```text
Never directly trust LLM-generated arguments.
```

---

## Stage 6 — Tool Registry and Executor

Completed:

- `TOOL_REGISTRY`
- controlled tool lookup
- argument validation
- unknown tool rejection
- centralized `execute_tool()`

Architecture:

```text
LLM Tool Request
      |
      v
execute_tool()
      |
      v
TOOL_REGISTRY
      |
      v
Validator
      |
      v
Function
```

---

## Stage 7 — LLM Tool Calling Orchestration

Completed:

- message-history-aware LLM calls
- `OrderAssistantService`
- first LLM call
- tool request detection
- controlled tool execution
- tool result serialization
- `tool_call_id` correlation
- second LLM call
- final natural-language response
- direct-answer path
- fake LLM orchestration tests

The application now supports:

```text
LLM
 ↓
Tool Request
 ↓
Application Validation
 ↓
Application Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

---

## Stage 8 — Order Assistant API

Completed:

- `OrderAssistantRequest`
- `OrderAssistantResponse`
- `POST /order-assistant`
- HTTP request validation
- FastAPI integration with `OrderAssistantService`
- real end-to-end manual testing
- successful order lookup
- unknown order handling
- direct-answer path
- FastAPI `TestClient`
- fake service substitution
- pytest `monkeypatch`
- empty request validation
- missing field validation

Architecture:

```text
HTTP
 |
 v
FastAPI
 |
 v
Pydantic Request
 |
 v
Application Service
 |
 v
LLM Orchestration
 |
 v
Tool Execution
 |
 v
LLM
 |
 v
Pydantic Response
 |
 v
HTTP
```

---

## Stage 9 — Multiple Tools and Iterative Tool Calling

Completed:

- Added `get_customer_orders(customer_id)`
- Added `GetCustomerOrdersArgs`
- Added the `get_customer_orders` LLM tool schema
- Registered the second tool in `TOOL_REGISTRY`
- Added validation and executor tests for the second tool
- Enabled semantic tool selection between multiple tools
- Replaced single `tool_calls[0]` handling with iteration over all requested tool calls
- Replaced the fixed two-LLM-call workflow with an iterative tool-calling loop
- Added support for multiple tool calls in a single LLM response
- Added support for sequential tool calls across multiple LLM turns
- Added a maximum tool-calling iteration limit
- Added automated multi-tool orchestration tests

### Available Tools

The model currently has access to two application capabilities:

```text
LLM
 |
 +--> get_order_status(order_id)
 |
 +--> get_customer_orders(customer_id)
```

The LLM selects a tool based on the user's intent.

For example:

```text
"Where is order 12345?"
        |
        v
get_order_status(
    order_id="12345"
)
```

while:

```text
"What orders does customer C001 have?"
        |
        v
get_customer_orders(
    customer_id="C001"
)
```

No application-level keyword routing is required.

The model performs semantic tool selection using the tool names, descriptions and parameter schemas.

### Multi-Step Tool Composition

The application can now support requests that require multiple capabilities.

For example:

```text
"What orders does customer C001 have,
and tell me the status of those orders?"
```

can result in:

```text
User
 |
 v
LLM Turn 1
 |
 v
get_customer_orders("C001")
 |
 v
["12345", "67890"]
 |
 v
LLM Turn 2
 |
 +--> get_order_status("12345")
 |
 +--> get_order_status("67890")
 |
 v
Tool Results
 |
 v
LLM Turn 3
 |
 v
Final Combined Answer
```

This demonstrates two forms of tool composition.

#### Sequential Tool Calling

One tool result can lead the model to request another capability:

```text
LLM
 |
 v
get_customer_orders
 |
 v
Tool Result
 |
 v
LLM
 |
 v
get_order_status
```

#### Multiple Tool Calls in One Turn

The model can also request multiple independent tool calls in the same response:

```text
LLM
 |
 +--> get_order_status("12345")
 |
 +--> get_order_status("67890")
```

The application executes every requested tool call and adds each result to the conversation history.

### Iterative Tool Loop

The original implementation assumed:

```text
LLM
 |
 v
One Tool
 |
 v
LLM
 |
 v
Final Answer
```

Stage 9 replaces this with:

```text
             +-----------------------+
             |                       |
             v                       |
            LLM                      |
             |                       |
             v                       |
        Tool calls?                  |
          /     \                    |
        No       Yes                 |
        |         |                  |
        v         v                  |
      Return    Execute              |
      Answer    Tool(s)              |
                  |                  |
                  v                  |
             Add Results             |
                  |                  |
                  +------------------+
```

Conceptually:

```python
for _ in range(MAX_TOOL_ITERATIONS):
    response = llm.generate_with_tools(...)

    if not response.tool_calls:
        return response.content

    for tool_call in response.tool_calls:
        result = execute_tool(...)

        # add result to conversation history
```

The orchestration therefore continues until either:

1. the model produces a final response, or
2. the application's maximum iteration limit is reached.

### Application-Controlled Stopping Condition

Tool-calling loops must not be allowed to execute indefinitely.

The application therefore defines:

```python
MAX_TOOL_ITERATIONS = 5
```

Conceptually:

```text
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
...
 ↓
Maximum iterations reached
 ↓
STOP
```

If the model continues requesting tools beyond the configured limit, the application raises an error rather than continuing indefinitely.

This protects against:

- runaway tool loops
- unnecessary LLM calls
- excessive token consumption
- increased latency
- unnecessary API cost
- provider rate-limit pressure

The stopping condition belongs to the application rather than the model.

### Stage 9 Architecture

```text
                         User
                          |
                          v
                       FastAPI
                          |
                          v
                OrderAssistantService
                          |
                          v
                         LLM
                          |
                    Tool Request(s)
                          |
                          v
                    TOOL_REGISTRY
                          |
              +-----------+-----------+
              |                       |
              v                       v
   GetOrderStatusArgs       GetCustomerOrdersArgs
              |                       |
              v                       v
    get_order_status()      get_customer_orders()
              |                       |
              +-----------+-----------+
                          |
                          v
                     Tool Results
                          |
                          v
                    Message History
                          |
                          v
                         LLM
                          |
                  More tools needed?
                     /         \
                   Yes          No
                    |            |
                    +-----+      v
                          |   Final Answer
                          |
                          +----> repeat
```

The LLM controls tool selection and reasoning.

The application controls:

- available tools
- argument validation
- tool execution
- iteration limits
- conversation state
- stopping conditions

### Multi-Tool Testing

Stage 9 includes deterministic tests that simulate:

```text
LLM Call #1
    |
    v
get_customer_orders("C001")
    |
    v
Application executes tool
    |
    v
LLM Call #2
    |
    +--> get_order_status("12345")
    |
    +--> get_order_status("67890")
    |
    v
Application executes both tools
    |
    v
LLM Call #3
    |
    v
Final Answer
```

The external LLM is replaced with a fake while the real application orchestration, registry, validation and tool execution remain active.

This verifies multi-tool behavior without depending on:

- network connectivity
- Groq availability
- API credentials
- model variability
- token cost

---
# Next Stage

---

## Stage 10 — Production Hardening

Future topics include:

- malformed model arguments
- unknown tool handling
- tool execution failures
- provider failures
- timeouts
- retries
- structured logging
- tracing
- observability
- authentication
- authorization
- tool-level permissions
- read vs write tools
- audit trails
- guardrails
- human approval
- rate limiting
- cost monitoring
- evaluation
- dependency management

---

# Current Limitations

The current implementation intentionally remains simple while the core concepts are being learned.

## Single Tool Call

The orchestration currently processes:

```python
assistant_message.tool_calls[0]
```

Therefore only the first requested tool call is executed.

A more production-oriented implementation would support:

```text
LLM
 |
 v
Tool Call(s)
 |
 v
Execute
 |
 v
Return Results
 |
 v
LLM
 |
 v
More Tool Call(s)?
 |
 +---- Yes ---> Execute Again
 |
 +---- No ----> Final Answer
```

---

## Provider Response Coupling

Although application services depend on `LLMClient`, the current tool-calling orchestration still understands response structures such as:

```python
response.choices[0].message
```

and:

```python
assistant_message.model_dump()
```

This means the abstraction is not yet completely provider-neutral.

A future improvement can introduce application-level response models such as:

```text
LLMResponse
ToolCall
ToolResult
Message
```

and let provider adapters translate provider-specific responses into those models.

That would produce a stronger boundary:

```text
OrderAssistantService
        |
        v
Provider-Neutral LLM Models
        |
        v
LLMClient
        |
        +------------------+
        |                  |
        v                  v
Groq Adapter        Other Provider Adapter
```

---

## Mock Business Data

`get_order_status()` currently uses in-memory order data.

A production implementation would typically call a real order-management system.

---

## Final-Answer Grounding

The final answer is generated by the LLM after receiving the tool result.

The model may occasionally add conversational suggestions or statements that were not explicitly contained in the tool response.

Future stages can introduce stronger system instructions, grounding rules, guardrails and evaluations to ensure the final answer remains faithful to tool results.

---

# Engineering Principles Demonstrated

## 1. Dependency Inversion

Application services depend on:

```text
LLMClient
```

rather than directly depending on:

```text
Groq SDK
```

---

## 2. Separation of Concerns

Different components have distinct responsibilities:

```text
FastAPI
    -> HTTP boundary

Application Service
    -> orchestration

LLM Adapter
    -> provider communication

Tool Schema
    -> model-facing capability definition

Pydantic Model
    -> argument validation

Tool Registry
    -> allowed tool mapping

Tool Executor
    -> controlled execution

Tool Function
    -> business capability
```

---

## 3. Explicit Tool Allowlisting

Only registered tools can be executed.

```text
LLM Request
    |
    v
TOOL_REGISTRY
    |
    +---- Known ----> Execute
    |
    +---- Unknown --> Reject
```

---

## 4. Validate Before Execution

LLM-generated arguments are validated before reaching application functions.

```text
LLM Output
   |
   v
Parse
   |
   v
Validate
   |
   v
Execute
```

---

## 5. Application-Controlled Execution

The model can request actions.

It does not directly control application execution.

```text
LLM
 |
 | proposes
 v
Application
 |
 | validates
 | authorizes
 | executes
 v
Tool
```

---

## 6. External Dependencies Are Replaceable in Tests

Automated tests replace external AI dependencies with deterministic fakes.

```text
Production
Application → Groq

Testing
Application → Fake LLM
```

This improves:

- speed
- reliability
- determinism
- test isolation

---

# Key Mental Model

The most important concept demonstrated by this project is:

```text
The LLM is not the application.

The LLM proposes.
The application validates.
The application authorizes.
The application executes.
The application controls.
```

Tool calling connects:

```text
Probabilistic Model Reasoning
             +
Deterministic Application Capabilities
```

A production AI system therefore requires both:

```text
Model Intelligence
        +
Application Engineering
```

The model determines what capability may be useful.

The application determines what is actually allowed to happen.