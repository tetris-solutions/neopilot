"""MCP tools for instance management."""

from __future__ import annotations

from neopilot.api.auth import detect_language, verify_connection
from neopilot.app import mcp
from neopilot.storage.local_store import InstanceStore


def _store() -> InstanceStore:
    return InstanceStore()


@mcp.tool()
def connect_instance(slug: str, api_token: str) -> str:
    """Connect to a NeoDash instance.

    Tests the connection, detects the user language, and saves the instance
    as the active one. You can connect multiple instances and switch between them.

    Parameters
    ----------
    slug:
        The instance identifier (e.g., ``loreal`` for ``loreal.neodash.ai``).
    api_token:
        Your NeoDash API token for this instance.
    """
    # Test the connection
    result = verify_connection(slug, api_token)
    if not result.get("ok"):
        return f"❌ Connection failed for '{slug}'. Please check your slug and API token."

    # Detect language
    language = detect_language(slug, api_token)

    # Save instance
    store = _store()
    info = store.add_instance(slug, api_token, language=language)

    return (
        f"✅ Connected to **{slug}.neodash.ai** successfully!\n"
        f"- Language: {info.language}\n"
        f"- This is now your active instance.\n\n"
        "You can now use tools like `list_dashboards`, `list_metrics`, "
        "`query_data`, etc."
    )


@mcp.tool()
def disconnect_instance(slug: str) -> str:
    """Remove a saved NeoDash instance.

    Parameters
    ----------
    slug:
        The instance identifier to remove.
    """
    store = _store()
    store.remove_instance(slug)
    return f"Instance '{slug}' has been disconnected and removed."


@mcp.tool()
def list_instances() -> str:
    """List all saved NeoDash instances.

    Shows which instances are connected and which one is currently active.
    """
    store = _store()
    instances = store.list_instances()
    if not instances:
        return (
            "No instances connected.\n"
            "Use `connect_instance` with a slug and API token to get started."
        )

    lines = ["**Connected NeoDash Instances:**\n"]
    for inst in instances:
        active = " ← active" if inst.is_active else ""
        lines.append(
            f"- **{inst.slug}**.neodash.ai "
            f"(lang: {inst.language}){active}"
        )
    return "\n".join(lines)


@mcp.tool()
def switch_instance(slug: str) -> str:
    """Switch the active NeoDash instance.

    All subsequent data queries will use this instance.

    Parameters
    ----------
    slug:
        The instance identifier to switch to.
    """
    store = _store()
    info = store.set_active(slug)
    return (
        f"✅ Switched to **{info.slug}.neodash.ai**.\n"
        f"All queries will now use this instance."
    )


@mcp.tool()
def test_active_connection() -> str:
    """Test if the active NeoDash instance connection is working."""
    store = _store()
    active = store.get_active()
    result = verify_connection(active.slug, active.api_token)
    if result.get("ok"):
        return f"✅ Connection to **{active.slug}.neodash.ai** is working."
    return f"❌ Connection to **{active.slug}.neodash.ai** failed."
