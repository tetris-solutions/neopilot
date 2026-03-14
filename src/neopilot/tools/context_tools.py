"""MCP tools for user context management."""

from __future__ import annotations

from neopilot.api.client import NeoDashClient
from neopilot.app import mcp
from neopilot.context.manager import ContextManager
from neopilot.storage.local_store import InstanceStore, UserContextStore


def _get_context_manager() -> ContextManager:
    """Return a ContextManager for the active instance."""
    store = InstanceStore()
    active = store.get_active()
    client = NeoDashClient(active.slug, active.api_token)
    return ContextManager(client)


@mcp.tool()
def get_context() -> str:
    """Get the full context for the active NeoDash instance.

    Returns a summary of available metrics, dimensions, dashboards,
    and your personal preferences. This helps you understand what data
    is available for analysis.
    """
    cm = _get_context_manager()
    return cm.build_context_string()


@mcp.tool()
def set_dashboards_of_interest(dashboard_ids: list[str]) -> str:
    """Save which dashboards you want to monitor regularly.

    This helps NeoPilot provide more relevant suggestions and insights.

    Parameters
    ----------
    dashboard_ids:
        List of dashboard IDs to monitor (from ``list_dashboards``).
    """
    store = InstanceStore()
    active = store.get_active()
    ctx_store = UserContextStore()
    ctx = ctx_store.update_dashboards(active.slug, dashboard_ids)
    return (
        f"✅ Updated dashboards of interest for **{active.slug}**:\n"
        f"{', '.join(ctx.dashboards_of_interest)}"
    )


@mcp.tool()
def set_metrics_of_interest(metric_ids: list[str]) -> str:
    """Save which metrics are most important to you.

    This helps NeoPilot prioritize insights around metrics you care about.

    Parameters
    ----------
    metric_ids:
        List of metric IDs (from ``list_metrics``).
    """
    store = InstanceStore()
    active = store.get_active()
    ctx_store = UserContextStore()
    ctx = ctx_store.update_metrics(active.slug, metric_ids)
    return (
        f"✅ Updated key metrics for **{active.slug}**:\n"
        f"{', '.join(ctx.metrics_of_interest)}"
    )


@mcp.tool()
def add_user_note(note: str) -> str:
    """Add a personal context note for the active instance.

    Notes help NeoPilot understand your specific context. For example:
    - "I'm only responsible for the Amazon Ads player"
    - "Focus on CPA optimization this quarter"
    - "The Cerave brand is my main priority"

    Parameters
    ----------
    note:
        The context note to save.
    """
    store = InstanceStore()
    active = store.get_active()
    ctx_store = UserContextStore()
    ctx = ctx_store.add_note(active.slug, note)
    return (
        f"✅ Note added for **{active.slug}**.\n"
        f"You now have {len(ctx.notes)} note(s) saved."
    )


@mcp.tool()
def get_user_preferences() -> str:
    """Get your current NeoPilot preferences for the active instance.

    Shows your dashboards of interest, key metrics, and personal notes.
    """
    store = InstanceStore()
    active = store.get_active()
    ctx_store = UserContextStore()
    ctx = ctx_store.load(active.slug)

    lines = [f"**Your Preferences for {active.slug}:**\n"]

    if ctx.dashboards_of_interest:
        lines.append(f"**Dashboards of interest:** {', '.join(ctx.dashboards_of_interest)}")
    else:
        lines.append("**Dashboards of interest:** Not set. Use `set_dashboards_of_interest`.")

    if ctx.metrics_of_interest:
        lines.append(f"**Key metrics:** {', '.join(ctx.metrics_of_interest)}")
    else:
        lines.append("**Key metrics:** Not set. Use `set_metrics_of_interest`.")

    if ctx.notes:
        lines.append("\n**Notes:**")
        for i, note in enumerate(ctx.notes, 1):
            lines.append(f"  {i}. {note}")
    else:
        lines.append("\n**Notes:** None. Use `add_user_note` to add context.")

    lines.append(f"\n**Language:** {ctx.preferred_language}")

    if ctx.last_updated:
        lines.append(f"**Last updated:** {ctx.last_updated}")

    return "\n".join(lines)


@mcp.tool()
def setup_user_context() -> str:
    """Get a guided setup to build your NeoPilot user context.

    Returns questions to help configure your preferences step by step.
    Answer these questions to help NeoPilot provide better insights.
    """
    store = InstanceStore()
    active = store.get_active()

    return (
        f"Let's set up your NeoPilot preferences for **{active.slug}**! "
        "Please answer the following questions:\n\n"
        "1. **Which dashboards do you want to monitor?**\n"
        "   Use `list_dashboards` to see available options, then use "
        "`set_dashboards_of_interest` with the dashboard IDs.\n\n"
        "2. **Which metrics are most important to you?**\n"
        "   Use `list_metrics` to see all metrics, then use "
        "`set_metrics_of_interest` with the metric IDs.\n\n"
        "3. **Any specific context about your role or focus?**\n"
        "   Use `add_user_note` to add notes like:\n"
        '   - "I manage the Amazon Ads player"\n'
        '   - "My priority is CPA optimization"\n'
        '   - "I only work with the Cerave brand"\n\n'
        "Take your time — you can always update these later!"
    )
