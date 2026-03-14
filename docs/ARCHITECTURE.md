# NeoPilot Architecture

## Overview

NeoPilot is an MCP (Model Context Protocol) server built with FastMCP. It acts as a bridge between LLM tools (Claude, Gemini, OpenAI) and the NeoDash marketing analytics platform.

```
┌─────────────┐     MCP (stdio)     ┌─────────────┐     HTTPS     ┌──────────────┐
│  LLM Client │ ◄────────────────► │  NeoPilot   │ ─────────────► │   NeoDash    │
│  (Claude,   │                     │  MCP Server │               │  {slug}.     │
│   Gemini)   │                     │             │               │  neodash.ai  │
└─────────────┘                     └─────────────┘               └──────────────┘
                                          │
                                          ▼
                                    ~/.neopilot/
                                    (local storage)
```

## Layers

### 1. MCP Layer (`app.py`, `server.py`, `tools/`)

- `app.py` — FastMCP instance (shared across tool modules)
- `server.py` — Entry point; imports tools to register them, runs the server
- `tools/` — One file per domain, each registering tools via `@mcp.tool()`

### 2. API Layer (`api/`)

- `client.py` — `NeoDashClient` using stdlib `urllib.request`
- `endpoints.py` — `NeoDashEndpoints` wrapping each API path into typed methods
- `auth.py` — Connection testing and language detection
- `errors.py` — Error hierarchy (`NeoPilotError` base)

### 3. Model Layer (`models/`)

Pydantic v2 models for all data structures:
- `metrics.py`, `dimensions.py` — with multilingual label resolution
- `dashboards.py` — Dashboard, Component, Dataset models
- `explorer.py` — Explorer query builder and response parser
- `instance.py` — Instance connection info
- `context.py` — Context hierarchy models

### 4. Context Layer (`context/`)

Assembles context from four hierarchical levels:
1. **Global** — metrics, dimensions, dashboards (from API)
2. **Dashboard** — component layout and purpose (from API, on demand)
3. **Component** — specific insights intent (from API, on demand)
4. **User** — personal preferences (from local storage)

### 5. Storage Layer (`storage/`)

JSON file-based storage in `~/.neopilot/`:
- `InstanceStore` — manages slug:token pairs and active instance
- `UserContextStore` — per-instance user preferences

### 6. Infrastructure (`infra/`)

- `env.py` — Thread-safe `.env` loading
- `logging.py` — Standard logging configuration
- `i18n.py` — Multilingual label resolution (pt-BR, en-US)
- `formatting.py` — Metric value formatting (currency, percent, number, duration)

## NeoDash API Endpoints

| Endpoint | Path | Purpose |
|----------|------|---------|
| Metrics | `/ai/metrics` | All available metrics |
| Dimensions | `/ai/dimensions` | All available dimensions |
| All Components | `/ai/allComponents` | Components of a dashboard |
| Component Data | `/ai/component` | Actual data for a component |
| Dashboard List | `/get/resumoDashboard` | List dashboards |
| Explorer | `/get/exploradorResults` | Free-form data query |
| Dataset | `/get/dataset` | Dataset metadata |

All endpoints use `api_token` as a query parameter for authentication.

## Data Flow

1. User asks a question via their LLM
2. LLM selects the appropriate NeoPilot tool
3. Tool calls `NeoDashEndpoints` method
4. `NeoDashClient` makes HTTPS request to `{slug}.neodash.ai`
5. Response is parsed into Pydantic models
6. Tool formats the result as a human-readable string
7. LLM uses the data to answer the user's question

## Key Design Decisions

- **stdlib `urllib`** over requests/httpx — matches sibling repo pattern, zero extra dependencies for HTTP
- **JSON local storage** over SQLite/YAML — stdlib, simple to inspect, adequate for config data
- **Synchronous tools** — simpler than async for stdio transport, can migrate later if needed
- **FastMCP instance in `app.py`** — avoids circular imports between server and tool modules
- **Labels resolved at tool level** — tools always show human-readable labels, never raw IDs
