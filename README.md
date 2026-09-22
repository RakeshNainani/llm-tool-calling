# LLM Tool Calling

A hands-on Python project for learning how **LLM tool/function calling** works inside a production-style application architecture.

The project demonstrates how an LLM can decide that it needs an external capability, request a tool with structured arguments, and allow the application to validate and execute that request safely.

The central architectural principle is:

> **The model proposes an action. The application validates, authorizes, executes, and observes that action.**

The LLM does **not** directly execute Python functions or control external systems.

---

## Learning Objectives

This project is designed to build practical understanding of:

* LLM tool/function calling
* Tool schemas
* Tool selection
* Tool argument validation
* Pydantic validation
* Tool execution
* Tool registries
* LLM abstraction layers
* Provider adapters
* FastAPI service architecture
* LLM → Tool → LLM execution loops
* Error handling
* Guardrails and authorization boundaries
* Enterprise agent architecture

---

## Architecture

The project will evolve toward the following architecture:

                         Client
                           │
                           ▼
                        FastAPI
                           │
                           ▼
                   Application Service
                           │
                           ▼
                       LLM Layer
                           │
                           ▼
                          LLM
                           │
                           ▼
                     Tool Decision
                           │
                           ▼
                     Tool Request
                           │
                           ▼
                  Schema Validation
                           │
                           ▼
                     Tool Registry
                      /         \
                     ▼           ▼
          get_order_status   get_customer_orders
                     │           │
                     └─────┬─────┘
                           ▼
                  Systems / APIs / DB
                           │
                           ▼
                      Tool Result
                           │
                           ▼
                          LLM
                           │
                           ▼
                    Final Response


---

## Tool Calling Mental Model

A common misconception is:

                LLM
                 ↓
            Python Function


The actual architecture is:
           User
            ↓
        Application
            ↓
           LLM
            ↓
        Structured Tool Request
            ↓
        Application Validation
            ↓
        Tool Registry
            ↓
        Python Function
            ↓
        External System
            ↓
        Tool Result
            ↓
           LLM
            ↓
        Final Response

The **application remains the control plane**.

---

## Example

A user asks:   
    Where is order 12345?

The LLM determines that it does not have the current order status and requests:
    get_order_status(order_id="12345")

Conceptually, the model generates structured data similar to:

```json
{
  "name": "get_order_status",
  "arguments": {
    "order_id": "12345"
  }
}
```

The application then:

1. Detects the tool request
2. Validates the arguments
3. Checks whether the tool is allowed
4. Finds the tool implementation
5. Executes the Python function
6. Sends the tool result back to the LLM
7. Returns the final response to the user

---

# Project Setup

## Prerequisites

Make sure the following are installed:

* Python 3.12+
* `uv`
* Git
* VS Code or another Python IDE
* Groq API key

Verify the installations:

```powershell
python --version
uv --version
git --version
```

---

## 1. Create the Project Directory

Open PowerShell and navigate to your development directory:

```powershell
cd C:\Work\code_practise
```

Create the project:

```powershell
mkdir llm-tool-calling
cd llm-tool-calling
```

---

## 2. Initialize the Python Project

Initialize the project using `uv`:

```powershell
uv init
```

This creates the initial Python project configuration including:

```text
pyproject.toml
```

---

## 3. Create the Virtual Environment

Synchronize the project:

```powershell
uv sync
```

This creates:

```text
.venv/
```

Activate the environment in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

The PowerShell prompt should now show the active environment.

Example:

```text
(llm-tool-calling) PS C:\Work\code_practise\llm-tool-calling>
```

> Activating the environment is optional when using `uv run`.

---

## 4. Install Project Dependencies

Install FastAPI, Uvicorn, Groq, Pydantic, and dotenv support:

```powershell
uv add fastapi "uvicorn[standard]" groq python-dotenv pydantic
```

Install development dependencies:

```powershell
uv add --dev pytest
```

The dependencies are recorded automatically in:

```text
pyproject.toml
```

and locked in:

```text
uv.lock
```

---

## 5. Create the Source Structure

The Python package for this project is:

```text
llm_tool_calling
```

Create the required directories:

```powershell
mkdir src\llm_tool_calling\llm
mkdir src\llm_tool_calling\schemas
mkdir src\llm_tool_calling\services
mkdir src\llm_tool_calling\tools
mkdir tests
```

Create package initialization files:

```powershell
New-Item src\llm_tool_calling\llm\__init__.py
New-Item src\llm_tool_calling\schemas\__init__.py
New-Item src\llm_tool_calling\services\__init__.py
New-Item src\llm_tool_calling\tools\__init__.py
```

If it does not already exist, create:

```powershell
New-Item src\llm_tool_calling\main.py
```

---

## 6. Project Structure

At this stage the project should look similar to:

```text
llm-tool-calling/
│
├── .venv/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock
│
├── src/
│   └── llm_tool_calling/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── llm/
│       │   └── __init__.py
│       │
│       ├── schemas/
│       │   └── __init__.py
│       │
│       ├── services/
│       │   └── __init__.py
│       │
│       └── tools/
│           └── __init__.py
│
└── tests/
```

---

## 7. Configure FastAPI

Add the following to:

```text
src/llm_tool_calling/main.py
```

```python
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
```

---

## 8. Configure Environment Variables

Create:

```text
.env
```

Later this file will contain local secrets such as:

```env
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant
```

Never commit `.env` to Git.

Create:

```text
.env.example
```

with:

```env
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
```

`.env.example` documents the required configuration without exposing secrets.

---

## 9. Configure `.gitignore`

Add:

```gitignore
# Virtual environment
.venv/

# Environment variables / secrets
.env

# Python cache
__pycache__/
*.py[cod]

# Testing
.pytest_cache/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

This is particularly important because `.env` will eventually contain the Groq API key.

---

## 10. Start the FastAPI Application

Run:

```powershell
uv run uvicorn llm_tool_calling.main:app --reload
```

Expected output should include:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

## 11. Test the Health Endpoint

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI should display:

```text
GET /health
```

Execute the endpoint.

Expected response:

```json
{
  "status": "ok"
}
```

You can also access:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

## 12. Verify the Project

Run:

```powershell
uv run python --version
```

Then:

```powershell
uv run pytest
```

At this stage there may not yet be tests, but pytest should start successfully.

---

# Development Roadmap

## Stage 1 — Project Foundation

* Initialize Python project with `uv`
* Create package structure
* Configure FastAPI
* Add `/health` endpoint
* Verify application startup

## Stage 2 — LLM Abstraction

Create a provider-independent LLM interface and implement a Groq adapter.

```text
Application
     │
     ▼
 LLM Interface
     │
     ▼
Groq Adapter
     │
     ▼
 Groq SDK
     │
     ▼
    LLM
```

## Stage 3 — First Tool

Implement:

```text
get_order_status(order_id)
```

The tool will initially use mock order data so that tool behavior can be tested independently from the LLM.

## Stage 4 — Tool Schema

Define the model-facing schema describing:

```text
get_order_status
```

This separates:

```text
Tool implementation
        ≠
Tool definition/schema
        ≠
Tool execution
```

## Stage 5 — Argument Validation

Use Pydantic to validate model-generated tool arguments before execution.

```text
LLM Tool Request
       ↓
JSON Arguments
       ↓
Pydantic
       ↓
Validated Arguments
       ↓
Tool Execution
```

## Stage 6 — Tool Registry

Introduce a registry that maps model-selected tool names to application-controlled Python implementations.

## Stage 7 — Tool Execution Loop

Implement:

```text
LLM
 ↓
Tool Request
 ↓
Validation
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
 ↓
Final Response
```

## Stage 8 — FastAPI Order Assistant

Expose:

```text
POST /orders/assistant
```

Example request:

```json
{
  "message": "Where is order 12345?"
}
```

## Stage 9 — Multiple Tools

Add:

```text
get_customer_orders(customer_id)
```

The model will then select the appropriate tool based on the user's request.

## Stage 10 — Production Hardening

Introduce:

* Unknown tool handling
* Invalid arguments
* Tool execution failures
* Logging
* Authorization
* Tool policies
* Read vs write tools
* Guardrails
* Human approval for high-impact operations

---

# Engineering Principles

## Separate API and Business Logic

FastAPI endpoints should remain thin.

Application and AI orchestration logic belongs in the service layer.

## Separate LLM Provider Integration

```text
Application Service
       ↓
LLM Abstraction
       ↓
Provider Adapter
       ↓
Provider SDK
```

This prevents application logic from becoming tightly coupled to a particular model provider.

## Tools Must Be Independently Testable

For example:

```python
get_order_status("12345")
```

should work and be testable without involving an LLM.

## Never Trust Model-Generated Arguments Directly

Tool arguments generated by an LLM must pass application-side validation.

## The LLM Does Not Own Execution

A production execution path may eventually look like:

```text
LLM
 ↓
Tool Request
 ↓
Schema Validation
 ↓
Authorization
 ↓
Business Policy
 ↓
Guardrails
 ↓
Human Approval
 ↓
Tool Execution
```

---

# Project Status

# Project Status

## Stage 1 — Project Foundation ✅

Completed:

* [x] Project initialized with `uv`
* [x] Virtual environment created
* [x] Dependencies installed
* [x] Python package structure created
* [x] FastAPI application created
* [x] `GET /health` endpoint created
* [x] Development server verified

---

## Stage 2 — LLM Abstraction ✅

Completed:

* [x] Created provider-independent `LLMClient` abstraction
* [x] Implemented `GroqLLMClient`
* [x] Added environment-based API key and model configuration
* [x] Added `ChatService`
* [x] Added Pydantic `ChatRequest` and `ChatResponse` schemas
* [x] Added `POST /chat` endpoint
* [x] Added `FakeLLMClient` for testing
* [x] Verified application logic without making real LLM calls
* [x] Verified Groq integration

Current LLM architecture:

```text
FastAPI
   │
   ▼
ChatService
   │
   ▼
LLMClient
   ▲
   │
GroqLLMClient
   │
   ▼
Groq SDK
   │
   ▼
LLM
```

This keeps the application layer independent of a specific LLM provider.

---

## Stage 3 — First Tool Implementation ✅

Implemented:

```text
get_order_status(order_id)
```

Completed:

* [x] Created `tools/order_tools.py`
* [x] Implemented `get_order_status()`
* [x] Added mock order data
* [x] Added handling for unknown orders
* [x] Tested the tool independently from the LLM
* [x] Added unit tests for shipped orders
* [x] Added unit tests for processing orders
* [x] Added unit tests for unknown orders

Current tool architecture:

```text
Python Application
       │
       ▼
get_order_status()
       │
       ▼
Mock Order Data
       │
       ▼
Order Result
```

At this stage the tool is an ordinary Python application capability.

The LLM does **not yet know that this tool exists**.

This separation is intentional:

```text
Tool Implementation
        ≠
Tool Schema
        ≠
Tool Execution
```

The tool implementation defines what the **application can do**.

The next stage will define what the **model is told it can request**.

---

## Current Test Coverage

The project currently tests:

```text
LLM abstraction
    │
    ├── FakeLLMClient
    │
    └── ChatService
         
Order tools
    │
    ├── shipped order
    ├── processing order
    └── unknown order
```

Run all tests with:

```powershell
uv run pytest -v
```

Expected result at this milestone:

```text
5 passed
```

---

## Stage 4 — Tool Schema and LLM Tool Selection ✅

The `get_order_status` application capability is now exposed to the LLM through a tool schema.

### What Was Added

* [x] Created `tools/schemas.py`
* [x] Defined the `get_order_status` tool schema
* [x] Added a clear tool name and description
* [x] Defined `order_id` as a required string parameter
* [x] Added `generate_with_tools()` to `GroqLLMClient`
* [x] Passed available tools to the LLM
* [x] Used `tool_choice="auto"` to allow the model to decide when a tool is needed
* [x] Verified that the LLM can select `get_order_status`
* [x] Inspected the tool name and arguments generated by the LLM
* [x] Verified that unrelated questions can be answered without selecting the order tool

### Tool Schema

The LLM does not have direct access to the Python function:

```python
get_order_status(order_id)
```

Instead, the application provides the LLM with a description of the capability:

```text
Tool Schema
    │
    ├── Name
    │     get_order_status
    │
    ├── Description
    │     Get the current fulfillment status and
    │     estimated delivery date for an order
    │
    └── Parameters
          └── order_id
                ├── type: string
                └── required
```

The schema acts as the **model-facing contract** for the tool.

### Current Tool-Calling Flow

When the user asks:

```text
Where is order 12345?
```

the current flow is:

```text
User
 │
 │ "Where is order 12345?"
 ▼
LLM
 │
 │ receives available tool schemas
 ▼
Tool Selection
 │
 ▼
Tool Call Request
 │
 ├── name: get_order_status
 │
 └── arguments:
 │       {"order_id":"12345"}
 │
 ▼
STOP
```

At this stage, the LLM can **request** a tool, but the application does not execute the requested function yet.

### Important Architecture Principle

Tool selection and tool execution are separate responsibilities:

```text
LLM
 │
 │ selects/request capability
 ▼
Tool Call Request
 │
 │
 ▼
Application
 │
 │ validates and controls execution
 ▼
Python Tool
```

The LLM does not directly execute:

```python
get_order_status()
```

Instead, it produces a structured request describing which tool it wants the application to invoke.

This keeps the application as the control plane.

### Tool Implementation vs Tool Schema

The project now contains two separate concepts:

```text
Tool Implementation
-------------------

get_order_status(order_id)
        │
        ▼
Executable Python capability


Tool Schema
-----------

ORDER_TOOLS
        │
        ▼
Model-facing description
of the capability
```

The tool implementation defines:

> What can the application do?

The tool schema defines:

> What can the LLM request?

The matching name `get_order_status` does not automatically connect the schema to the Python function. Controlled mapping and execution will be added in later stages.

---
## Stage 5 — Tool Argument Validation ✅

LLM-generated tool arguments are now parsed and validated before they can be used by the application.

### What Was Added

* [x] Created `schemas/tools.py`
* [x] Added the `GetOrderStatusArgs` Pydantic model
* [x] Defined `order_id` as a required string
* [x] Added minimum-length validation for `order_id`
* [x] Inspected raw arguments returned by the LLM
* [x] Parsed the LLM-generated JSON string using `json.loads()`
* [x] Validated parsed arguments using Pydantic
* [x] Verified that missing `order_id` is rejected
* [x] Verified that an empty `order_id` is rejected
* [x] Added automated tests for tool argument validation

### Current Validation Flow

The LLM returns tool arguments as a JSON string:

```text id="f3l5ge"
'{"order_id":"12345"}'
```

The application does not pass this directly to the tool.

Instead:

```text id="ftdk06"
LLM
 │
 ▼
Tool Call Request
 │
 └── arguments:
     '{"order_id":"12345"}'
 │
 │
 ▼
json.loads()
 │
 ▼
Python Dictionary
 │
 └── {"order_id": "12345"}
 │
 │
 ▼
Pydantic
 │
 ▼
GetOrderStatusArgs
 │
 └── order_id = "12345"
 │
 ▼
Validated Arguments
```

### Parsing vs Validation

JSON parsing and application validation solve different problems.

```text id="8acbxm"
json.loads()
     │
     └── "Is this valid JSON?"
              │
              ▼
         Python object


Pydantic
     │
     └── "Does this data satisfy
          my application's contract?"
              │
              ▼
        Validated model
```

For example, this is valid JSON:

```json id="49t5y5"
{}
```

but it is not valid input for `get_order_status` because `order_id` is required.

Similarly:

```json id="k23axr"
{
  "order_id": ""
}
```

is valid JSON but fails application validation because `order_id` must contain at least one character.

### Pydantic Argument Model

The application now defines the contract:

```python id="2s7shb"
class GetOrderStatusArgs(BaseModel):
    """Arguments accepted by the get_order_status tool."""

    order_id: str = Field(
        min_length=1,
        description="Unique order identifier.",
    )
```

This provides an explicit validation boundary between model-generated data and application execution.

### Tool Schema vs Validation Schema

The project now contains two related but distinct schemas:

```text id="9hs6hn"
tools/schemas.py
      │
      │ Tool definition
      ▼
     LLM
      │
      │ Generates tool request
      ▼
Raw Arguments
      │
      ▼
schemas/tools.py
      │
      │ Pydantic validation
      ▼
 Application
```

`tools/schemas.py` answers:

> What arguments should the LLM generate?

`schemas/tools.py` answers:

> What arguments will the application accept?

These are separate responsibilities.

### Current Architecture

The project has now progressed to:

```text id="ayk9tt"
User
 │
 ▼
LLM
 │
 │ sees tool schema
 ▼
Tool Selection
 │
 ▼
Tool Call Request
 │
 ├── name: get_order_status
 │
 └── arguments: '{"order_id":"12345"}'
 │
 ▼
JSON Parsing
 │
 ▼
Pydantic Validation
 │
 ▼
Validated Arguments
 │
 ▼
STOP
```

The application still does **not automatically execute** `get_order_status()`.

That separation is intentional.

---

## Next Stage — Tool Registry

The next problem is connecting:

```text id="n4fmra"
"get_order_status"
```

returned by the LLM to:

```python id="1bt9hy"
get_order_status()
```

the actual Python function.

Instead of scattering logic such as:

```python id="db75qf"
if tool_name == "get_order_status":
    ...
elif tool_name == "get_customer_orders":
    ...
elif tool_name == "another_tool":
    ...
```

throughout the application, Stage 6 will introduce a **Tool Registry**.

Target architecture:

```text id="ovc4fe"
LLM Tool Request
       │
       ├── name
       └── arguments
       │
       ▼
   Tool Registry
       │
       ├── Tool Schema
       ├── Validation Model
       └── Python Function
       │
       ▼
Controlled Tool Execution
```

Conceptually:

```text id="31s7tg"
get_order_status
       │
       ▼
┌──────────────────────────────┐
│ Tool Registry                │
│                              │
│ name                         │
│   get_order_status           │
│                              │
│ validator                    │
│   GetOrderStatusArgs         │
│                              │
│ function                     │
│   get_order_status()         │
└──────────────────────────────┘
```

This will give the application a controlled mapping between model-visible tool names and executable Python capabilities.

### Remaining Roadmap

```text id="l03wyi"
Stage 6
Tool Registry
      ↓
Stage 7
LLM → Tool → LLM Execution Loop
      ↓
Stage 8
Order Assistant API
      ↓
Stage 9
Multiple Tools
      ↓
Stage 10
Production Hardening
```

---

# Future Enhancements

Potential extensions include:

* OpenAI adapter
* Azure OpenAI adapter
* Amazon Bedrock adapter
* Tool authorization policies
* Async tool execution
* Observability and tracing
* Tool execution metrics
* LLM evaluation
* Guardrails
* Persistent conversation state
* RAG tools
* MCP integration
* Multi-step agent workflows

---

# Purpose

This repository is primarily a learning project for understanding the engineering foundations behind **LLM applications, tool calling, and agentic AI systems**.

Rather than hiding orchestration behind an agent framework, the initial implementation builds the tool-calling loop explicitly so that each architectural responsibility can be understood and tested.