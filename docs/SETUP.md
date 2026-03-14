# NeoPilot Setup Guide

## Installation

Open a terminal and run the following commands:

```bash
# 1. Navigate to the NeoPilot project folder
cd /Users/beterraba/Documents/Workgit/neodash-ai/neopilot

# 2. Create a Python virtual environment inside the project
#    (on macOS, use "python3" — "python" alone may not exist)
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows (PowerShell)

# 4. Install NeoPilot and its dependencies into the virtual environment
pip install -e ".[dev]"
```

> **Note:** On macOS, the command is `python3`, not `python`.
> After activating the virtual environment (step 3), both `python` and `python3` will work.

## Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

Restart Claude Desktop. You should see NeoPilot's tools available.

## Claude Code

Add to your project's `.mcp.json`:

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

## Gemini (as a Gem)

Gemini supports MCP through Google's AI Studio. Configure NeoPilot as an MCP tool endpoint following Google's MCP integration documentation.

## Generic MCP Client

NeoPilot uses `stdio` transport. Any MCP-compatible client can connect by running:

```bash
python -m neopilot.server
```

The server communicates via stdin/stdout using the MCP protocol.

## MCP Inspector (Development)

For interactive testing of tools:

```bash
mcp dev src/neopilot/server.py
```

This opens a web UI where you can call tools and see responses.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGLEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `NEOPILOT_DATA_DIR` | `~/.neopilot` | Where to store instances and user context |

## First Connection

Once NeoPilot is running in your LLM tool:

1. Use `connect_instance` with your NeoDash slug and API token
2. Use `list_dashboards` to see what's available
3. Use `list_metrics` and `list_dimensions` to understand the data
4. Use `setup_user_context` for guided preference setup
5. Start querying with `query_data` or `get_component_data`
