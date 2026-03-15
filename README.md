# NeoPilot

MCP server that connects LLMs (Claude, Gemini, OpenAI) to **NeoDash** marketing analytics.

NeoPilot lets users conversationally query their advertising data, get insights, list dashboards, explore metrics, and generate visualizations — all through their preferred AI tool.

## Install (1 command)

Run this in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/tetris-solutions/neopilot/main/install.sh | bash
```

This will:
1. Clone NeoPilot to `~/.neopilot/app/`
2. Create a Python virtual environment and install dependencies
3. Automatically configure Claude Desktop

**After running, restart Claude Desktop** (quit and reopen).

### Manual Install

If you prefer to install manually, see [docs/SETUP.md](docs/SETUP.md).

## Getting Started

Once Claude Desktop is restarted with NeoPilot, just say:

```
Connect to my NeoDash instance "yourslug" with API token "your_token_here"
```

Then try:
```
List my dashboards
Show me Spend and CPC for the last 7 days
What metrics are available?
```

## Updating NeoPilot

```bash
cd ~/.neopilot/app && git pull && .venv/bin/pip install -e .
```

Then restart Claude Desktop. NeoPilot will also notify you when updates are available.

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

NeoPilot supports connecting to multiple NeoDash instances simultaneously. Each instance is identified by its slug. The slug is the word before `.neodash.ai` (e.g., `neoperformance.neodash.ai` will have the slug `neoperformance`).

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

## Debug Mode

Set `NEOPILOT_DEBUG=1` in the MCP server config to see the raw API URLs and responses in tool output. Useful for troubleshooting queries that return unexpected results.

## Development

```bash
# Clone the repo
git clone https://github.com/tetris-solutions/neopilot.git
cd neopilot

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests (unit only)
python3 -m pytest tests/ -v --ignore=tests/test_integration.py

# Run integration tests (requires real NeoDash credentials)
# First time: copy .env.test.example → .env.test and fill in your credentials
cp .env.test.example .env.test   # then edit with your slug & token
python3 -m pytest tests/test_integration.py -v

# Lint
ruff check src/ tests/

# Type check
mypy src/neopilot

# MCP Inspector (interactive testing)
mcp dev src/neopilot/server.py
```

## Version Management

NeoPilot checks for updates via a remote `version.json` file:

- **Optional update**: Users see a notice when connecting — "v0.1.0 → v0.2.0 available"
- **Forced update**: If `minimum` version is raised, tools refuse to run until updated

To push a forced update to all users, edit `version.json` in the repo:
```json
{
  "latest": "0.2.0",
  "minimum": "0.2.0",
  "update_url": "https://github.com/tetris-solutions/neopilot#updating-neopilot",
  "message": "Important security fix. Please update."
}
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details.
