# Autonomous Ops Agent

An asynchronous task-execution backend built with **FastAPI**, **SQLAlchemy (Async)**, and the **Groq API** that runs a ReAct (Reason + Act) tool-calling loop with sandboxed file operations and **Human-in-the-Loop (HITL)** approval for mutative actions.

## Key Features

- **ReAct Execution Loop (`AgentEngine`)**: Uses LLM function/tool calling to plan steps, invoke tools, observe results (including tool errors), and produce a final response while tracking token usage per task.
- **Sandboxed File Tools**: Separates read-only and mutative tools under `app/tools/`:
  - `read_only` (`FileReader`): Reads files inside the configured `sandbox/` directory.
  - `mutative` (`FileWriter`): Writes files inside `sandbox/` and sets `requires_approval = True`.
- **Human-in-the-Loop (HITL) Governance**: Mutative tool calls pause the task in an `AWAITING_APPROVAL` state with an `Approval` record in the database, resuming via a background task once approved (or feeding rejection context back to the agent if rejected).
- **Persistent Step & Token Tracking**: Stores `Task`, `ExecutionStep`, and `Approval` records in PostgreSQL using async sessions (`AsyncSessionLocal`).

## Project Structure

```text
backend/
├── app/
│   ├── api/            # FastAPI routers for tasks and approval decisions
│   ├── config/         # Environment variables and application settings
│   ├── core/           # AgentEngine (ReAct loop & HITL resume) and prompt templates
│   ├── database/       # Async engine, AsyncSessionLocal, and get_db dependency
│   ├── db/             # SQLAlchemy ORM models and Pydantic schemas
│   └── tools/          # BaseTool, read_only/ (FileReader), and mutative/ (FileWriter)
└── sandbox/            # Isolated directory for agent file read/write operations