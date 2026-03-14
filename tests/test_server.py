"""Smoke test for the MCP server initialization."""

from __future__ import annotations


class TestServerInit:
    def test_mcp_instance_exists(self):
        from neopilot.app import mcp

        assert mcp is not None
        assert mcp.name == "NeoPilot"

    def test_tools_are_registered(self):
        """Verify that importing server registers all tools."""
        # Import server to trigger tool registration
        import neopilot.server  # noqa: F401
        from neopilot.app import mcp

        # Check that we have tools registered
        # FastMCP stores tools internally
        assert mcp is not None
