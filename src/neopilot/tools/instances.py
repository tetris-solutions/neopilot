"""MCP tools for instance management."""

from __future__ import annotations

from neopilot import __version__
from neopilot.api.auth import verify_connection
from neopilot.app import mcp
from neopilot.infra.env import is_debug, set_debug
from neopilot.infra.i18n import SUPPORTED_LANGUAGES
from neopilot.infra.version import check_update, update_notice
from neopilot.storage.local_store import InstanceStore


def _store() -> InstanceStore:
    return InstanceStore()


@mcp.tool()
def connect_instance(slug: str, api_token: str) -> str:
    """Connect to a NeoDash instance.

    Tests the connection and saves the instance as the active one.
    You can connect multiple instances and switch between them.

    After connecting, the user **must** set their preferred language
    before querying data.

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

    # Save instance (language not yet confirmed)
    store = _store()
    store.add_instance(slug, api_token)

    langs = ", ".join(f"`{lang}`" for lang in SUPPORTED_LANGUAGES)
    msg = (
        f"✅ Connected to **{slug}.neodash.ai** successfully!\n"
        f"- NeoPilot version: v{__version__}\n"
        f"- This is now your active instance.\n\n"
        f"**Next step:** Please ask the user which language they prefer.\n"
        f"Supported languages: {langs}\n"
        "The language determines how metric and dimension labels are displayed.\n"
        "Use `set_language` to set it, then call `list_metrics` and "
        "`list_dimensions` to discover available data."
    )

    # Check for updates (non-blocking)
    notice = update_notice()
    if notice:
        msg += notice

    return msg


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

    Shows which instances are connected, which one is currently active,
    and the current NeoPilot version.
    """
    store = _store()
    instances = store.list_instances()
    if not instances:
        return (
            f"NeoPilot v{__version__}\n\n"
            "No instances connected.\n"
            "Use `connect_instance` with a slug and API token to get started."
        )

    lines = [f"**NeoPilot v{__version__}**\n", "**Connected NeoDash Instances:**\n"]
    for inst in instances:
        active = " ← active" if inst.is_active else ""
        lines.append(
            f"- **{inst.slug}**.neodash.ai "
            f"(lang: {inst.language}){active}"
        )

    notice = update_notice()
    if notice:
        lines.append(notice)

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
        f"All queries will now use this instance.\n\n"
        "**Important:** Call `list_metrics` and `list_dimensions` before querying "
        "data — each instance has different available metrics and dimensions."
    )


@mcp.tool()
def set_language(language: str) -> str:
    """Set the preferred language for the active NeoDash instance.

    This controls how metric and dimension labels are displayed.
    **Must be called before listing metrics/dimensions or querying data.**

    Only two languages are supported: ``pt-BR`` (Portuguese) and ``en-US`` (English).

    Parameters
    ----------
    language:
        Language code: ``pt-BR`` or ``en-US``.
    """
    if language not in SUPPORTED_LANGUAGES:
        langs = ", ".join(f"`{lang}`" for lang in SUPPORTED_LANGUAGES)
        return f"❌ Unsupported language '{language}'. Supported: {langs}"

    store = _store()
    active = store.get_active()
    info = store.set_language(active.slug, language)
    return (
        f"✅ Language set to **{info.language}** for **{info.slug}.neodash.ai**.\n"
        "Metric and dimension labels will be shown in this language.\n\n"
        "**Next:** Call `list_metrics` and `list_dimensions` to discover "
        "available data before using `query_data`."
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


@mcp.tool()
def check_neopilot_version() -> str:
    """Check the current NeoPilot version and whether updates are available.

    Use this when the user asks about the NeoPilot version, wants to know
    if they are up to date, or asks about updates.
    """
    info = check_update()
    lines = [f"**NeoPilot v{info['current']}**\n"]

    if info["check_failed"]:
        lines.append(
            "⚠️ Could not reach the update server to check for new versions.\n"
            "This may be a network issue. Your current version is "
            f"**v{info['current']}**."
        )
        return "\n".join(lines)

    lines.extend([
        f"- Latest available: v{info['latest']}",
        f"- Minimum required: v{info['minimum']}",
    ])

    if info["force_update"]:
        lines.append(
            f"\n⛔ **Update required!** Your version is below the minimum "
            f"(v{info['minimum']}). Please update to continue using NeoPilot."
        )
    elif info["update_available"]:
        lines.append(
            f"\n💡 **Update available:** v{info['current']} → v{info['latest']}"
        )
    else:
        lines.append("\n✅ You are running the latest version.")

    if info.get("message"):
        lines.append(f"\n{info['message']}")

    if info.get("update_url") and (info["force_update"] or info["update_available"]):
        lines.append(f"\nUpdate instructions: {info['update_url']}")

    return "\n".join(lines)


@mcp.tool()
def toggle_debug(enabled: bool) -> str:
    """Enable or disable NeoPilot debug mode.

    When debug mode is on, all tool responses include the actual HTTP
    request URL and raw API response from NeoDash. This is useful for
    troubleshooting empty results or unexpected data.

    Parameters
    ----------
    enabled:
        ``True`` to activate debug mode, ``False`` to deactivate it.
    """
    set_debug(enabled)
    if enabled:
        return (
            "🔧 **Debug mode activated.**\n"
            "All data tools will now show the actual API request URL "
            "and raw response at the end of their output."
        )
    return "🔧 **Debug mode deactivated.** Responses will be clean again."


@mcp.tool()
def debug_status() -> str:
    """Check whether NeoPilot debug mode is currently on or off."""
    status = "**ON**" if is_debug() else "**OFF**"
    return f"🔧 Debug mode is {status}."
