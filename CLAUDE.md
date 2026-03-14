# CLAUDE.md — Developer Guide for NeoPilot

## What is NeoPilot?

An MCP (Model Context Protocol) server that connects LLMs to NeoDash marketing analytics. Users query advertising data conversationally.

## Tech Stack

- Python 3.11+, pip + venv
- `mcp[cli]` (FastMCP) for the MCP server
- `pydantic` for models and validation
- `urllib.request` (stdlib) for HTTP — no requests/httpx
- `pytest` for testing, `ruff` for linting

## Project Layout

```
src/neopilot/
  app.py              # FastMCP instance (import mcp from here)
  server.py           # Entry point — imports tools, calls mcp.run()
  api/
    client.py         # NeoDashClient — urllib-based HTTP client
    auth.py           # verify_connection(), detect_language()
    endpoints.py      # NeoDashEndpoints — wraps all API paths
    errors.py         # Error hierarchy (NeoPilotError base)
  models/             # Pydantic models for all data types
  context/            # Context hierarchy (global, user, dashboard, component)
  tools/              # MCP tools — one file per domain
  storage/            # JSON file storage (~/.neopilot/)
  infra/              # env, logging, i18n, formatting
tests/
  fixtures/           # JSON mock API responses
  test_*.py           # One test file per module
```

## Key Patterns

- **FastMCP instance** lives in `app.py` to avoid circular imports
- **Tools** import `mcp` from `app.py` and use `@mcp.tool()` decorators
- **HTTP client** uses stdlib `urllib.request` (matching sibling repo pattern)
- **Error classes** extend `RuntimeError`
- **Models** use `extra = "allow"` for defensive API parsing
- **Labels** are multilingual dicts resolved via `infra/i18n.py`

## Critical Rules

1. **Never calculate totals** — always use `showTotals=true` and let NeoDash compute them
2. **Filters on demand are deferred** — raise `FilterNotReadyError` if requested
3. **Show labels, not IDs** — resolve metric/dimension labels for the user's language
4. **Truncation detection** — warn when results count equals the limit
5. **Max 50,000 rows** — hard cap on Explorer queries

## Running

```bash
source .venv/bin/activate
python3 -m pytest tests/ -v      # Tests
ruff check src/ tests/            # Lint
python3 -m neopilot.server        # Run server (stdio)
```

## NeoDash API

- Base URL: `https://{slug}.neodash.ai/admin/index.php`
- Auth: `api_token` query parameter
- AI endpoints: `/ai/metrics`, `/ai/dimensions`, `/ai/allComponents`, `/ai/component`
- Core endpoints: `/get/resumoDashboard`, `/get/exploradorResults`, `/get/dataset`
