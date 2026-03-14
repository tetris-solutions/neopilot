# NeoPilot

MCP server that connects LLMs (Claude, Gemini, OpenAI) to **NeoDash** marketing analytics.

NeoPilot lets users conversationally query their advertising data, get insights, list dashboards, explore metrics, and generate visualizations — all through their preferred AI tool.

## Quick Start

### 1. Install

```bash
# Navigate to the NeoPilot project folder
cd /Users/beterraba/Documents/Workgit/neodash-ai/neopilot

# Create a Python virtual environment (use "python3" on macOS)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install NeoPilot and its dependencies
pip install -e ".[dev]"
```

> **Note:** On macOS, use `python3` — the `python` command may not exist.
> After activating the virtual environment, both `python` and `python3` will work.

### 2. Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "neopilot": {
      "command": "/path/to/neopilot/.venv/bin/python",
      "args": ["-m", "neopilot.server"]
    }
  }
}
```

### 3. Connect a NeoDash Instance

Once NeoPilot is running in your LLM, use the `connect_instance` tool:

```
Connect to my NeoDash instance "loreal" with API token "your_token_here"
```

## Available Tools

### Instance Management
| Tool | Description |
|------|-------------|
| `connect_instance` | Connect to a NeoDash instance (slug + API token) |
| `disconnect_instance` | Remove a saved instance |
| `list_instances` | List all connected instances |
| `switch_instance` | Switch the active instance |
| `test_active_connection` | Test if the connection is working |

### Data Discovery
| Tool | Description |
|------|-------------|
| `list_dashboards` | List all dashboards (with search) |
| `get_dashboard_components` | List components in a dashboard |
| `list_metrics` | List all metrics with labels, targets, formats |
| `list_dimensions` | List all dimensions with labels |

### Data Retrieval
| Tool | Description |
|------|-------------|
| `query_data` | Free-form data query (dimensions, metrics, dates) |
| `get_component_data` | Get data for a specific dashboard component |
| `list_time_breakdowns` | List time breakdown options |

### User Context
| Tool | Description |
|------|-------------|
| `get_context` | Get full instance context (global + user) |
| `setup_user_context` | Guided setup for your preferences |
| `set_dashboards_of_interest` | Save dashboards to monitor |
| `set_metrics_of_interest` | Save priority metrics |
| `add_user_note` | Add a personal context note |
| `get_user_preferences` | View your saved preferences |

## Multi-Instance Support

NeoPilot supports connecting to multiple NeoDash instances simultaneously. Each instance is identified by its slug (e.g., `loreal`, `mdlz`, `tpv`).

```
Connect to "loreal" with token "token_a"
Connect to "mdlz" with token "token_b"
Switch to "loreal"
```

## Data Storage

Instance connections and user preferences are stored locally in `~/.neopilot/`:
- `instances.json` — slug:token pairs
- `user_context_{slug}.json` — per-instance preferences

## Key Behaviors

- **Labels, not IDs**: Metrics and dimensions are always shown with their human-readable labels
- **Totals by NeoDash**: Totals are always calculated by NeoDash, never by NeoPilot
- **Truncation warnings**: When query results hit the row limit, NeoPilot warns you
- **Bilingual**: Supports pt-BR and en-US labels (auto-detected from user settings)
- **Filters**: Custom filters on demand are coming in a future update

## Development

```bash
# Run tests
python3 -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Type check
mypy src/neopilot

# MCP Inspector (interactive testing)
mcp dev src/neopilot/server.py
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details.
