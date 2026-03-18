# NeoPilot Setup Guide

## Quick Install (recommended)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.ps1 | iex
```

This will:
1. Clone NeoPilot to `~/.neopilot/app/`
2. Create a Python virtual environment and install dependencies
3. Automatically configure Claude Desktop

**After running, restart Claude Desktop** (quit and reopen).

> **Requirements:** Python 3.11+ and git.

---

## Manual Install

### 1. Clone the repo

```bash
git clone https://github.com/tetris-solutions/neopilot.git
cd neopilot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows (PowerShell)
pip install -e ".[dev]"
```

> **Note:** On macOS, use `python3` — `python` alone may not exist.
> After activating the venv, both `python` and `python3` will work.

### 3. Configure your LLM client

See the sections below for your specific tool.

---

## Claude Desktop

Config file location:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS / Linux:**
```json
{
  "mcpServers": {
    "neopilot": {
      "command": "/absolute/path/to/neopilot/.venv/bin/python",
      "args": ["-m", "neopilot.server"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "neopilot": {
      "command": "C:\\Users\\<you>\\.neopilot\\app\\.venv\\Scripts\\python.exe",
      "args": ["-m", "neopilot.server"]
    }
  }
}
```

Replace the path with the actual path where you cloned the repo.

To enable **debug mode** (shows raw API URLs and responses in tool output), add an `env` key:

```json
{
  "mcpServers": {
    "neopilot": {
      "command": "...python path...",
      "args": ["-m", "neopilot.server"],
      "env": {
        "NEOPILOT_DEBUG": "1"
      }
    }
  }
}
```

Restart Claude Desktop after any config change.

## Claude Code

Add to your project's `.mcp.json`:

**macOS / Linux:**
```json
{
  "mcpServers": {
    "neopilot": {
      "command": "/absolute/path/to/neopilot/.venv/bin/python",
      "args": ["-m", "neopilot.server"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "neopilot": {
      "command": "C:\\Users\\<you>\\.neopilot\\app\\.venv\\Scripts\\python.exe",
      "args": ["-m", "neopilot.server"]
    }
  }
}
```

## Gemini (as a Gem)

Gemini supports MCP through Google's AI Studio. Configure NeoPilot as an MCP tool endpoint following Google's MCP integration documentation.

## Generic MCP Client

NeoPilot uses `stdio` transport. Any MCP-compatible client can connect by running:

```bash
python3 -m neopilot.server
```

The server communicates via stdin/stdout using the MCP protocol.

---

## First Connection

Once NeoPilot is running in your LLM tool:

1. Use `connect_instance` with your NeoDash slug and API token
2. Use `list_dashboards` to see what's available
3. Use `list_metrics` and `list_dimensions` to understand the data
4. Use `setup_user_context` for guided preference setup
5. Start querying with `query_data` or `get_component_data`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGLEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `NEOPILOT_DATA_DIR` | `~/.neopilot` | Where to store instances and user context |
| `NEOPILOT_DEBUG` | _(off)_ | Set to `1` to show raw API URLs and responses in tool output |

---

## Development Setup

### Running tests

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Then:
```bash
# Unit tests (no credentials needed)
python3 -m pytest tests/ -v --ignore=tests/test_integration.py

# Lint
ruff check src/ tests/
```

### Integration tests

Integration tests hit the real NeoDash API to verify that our Pydantic models can parse actual responses. They require credentials for a NeoDash instance.

**Setup:**

```bash
# 1. Copy the example file
cp .env.test.example .env.test

# 2. Edit .env.test with your real credentials
#    NEODASH_TEST_SLUG=yourslug
#    NEODASH_TEST_TOKEN=your_api_token_here
```

`.env.test` is in `.gitignore` — it will **never** be committed.

Ask your team lead for a test slug and API token if you don't have one.

**Run:**

```bash
python3 -m pytest tests/test_integration.py -v
```

Without `.env.test`, integration tests are automatically skipped.

### MCP Inspector

For interactive testing of tools in a web UI:

```bash
mcp dev src/neopilot/server.py
```
