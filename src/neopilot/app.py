"""FastMCP application instance.

This module holds the ``mcp`` instance so that tool modules can import it
without circular dependencies. The ``server`` module imports tool modules
(which register themselves) and then calls ``mcp.run()``.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="NeoPilot",
    instructions=(
        "NeoPilot connects your LLM to NeoDash marketing analytics. "
        "Query advertising data, get insights, and generate visualizations "
        "from your NeoDash dashboards."
    ),
)
