"""NeoPilot MCP server entry point."""

from __future__ import annotations

import logging

from neopilot.infra.env import load_env
from neopilot.infra.logging import configure_logging

# Load environment and configure logging before anything else
load_env()
configure_logging()

logger = logging.getLogger(__name__)

# Import the FastMCP instance
# Import tool modules to trigger @mcp.tool() registration
import neopilot.tools.components  # noqa: E402
import neopilot.tools.context_tools  # noqa: E402
import neopilot.tools.dashboards  # noqa: E402
import neopilot.tools.explorer  # noqa: E402
import neopilot.tools.instances  # noqa: E402
import neopilot.tools.metrics_dimensions  # noqa: E402, F401

# Log version on startup
from neopilot import __version__  # noqa: E402
from neopilot.app import mcp  # noqa: E402

logger.info("NeoPilot v%s starting.", __version__)


def main() -> None:
    """Run the NeoPilot MCP server."""
    import os

    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport in ("sse", "streamable-http"):
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("MCP_PORT", "8000"))
        logger.info("Starting HTTP transport on %s:%s", host, port)
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport=transport)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
