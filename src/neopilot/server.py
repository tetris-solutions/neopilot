"""NeoPilot MCP server entry point."""

from __future__ import annotations

from neopilot.infra.env import load_env
from neopilot.infra.logging import configure_logging

# Load environment and configure logging before anything else
load_env()
configure_logging()

# Import the FastMCP instance
# Import tool modules to trigger @mcp.tool() registration
import neopilot.tools.components  # noqa: E402
import neopilot.tools.context_tools  # noqa: E402
import neopilot.tools.dashboards  # noqa: E402
import neopilot.tools.explorer  # noqa: E402
import neopilot.tools.instances  # noqa: E402
import neopilot.tools.metrics_dimensions  # noqa: E402, F401
from neopilot.app import mcp  # noqa: E402


def main() -> None:
    """Run the NeoPilot MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
