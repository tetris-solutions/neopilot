"""MCP tools for listing metrics and dimensions."""

from __future__ import annotations

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.app import mcp
from neopilot.infra.debug import debug_block
from neopilot.infra.env import is_debug
from neopilot.infra.i18n import SUPPORTED_LANGUAGES
from neopilot.models.instance import InstanceInfo
from neopilot.storage.local_store import InstanceStore


def _get_active() -> InstanceInfo:
    """Return the active instance."""
    store = InstanceStore()
    return store.get_active()


def _get_endpoints(active: InstanceInfo) -> NeoDashEndpoints:
    """Return endpoints for the active instance."""
    client = NeoDashClient(active.slug, active.api_token)
    return NeoDashEndpoints(client)


def _language_guard(active: InstanceInfo) -> str | None:
    """Return an error message if language has not been confirmed, else None."""
    if not active.language_confirmed:
        langs = ", ".join(f"`{lang}`" for lang in SUPPORTED_LANGUAGES)
        return (
            "⚠️ **Language not set.** Please ask the user which language they "
            "prefer for metric and dimension labels.\n"
            f"Supported: {langs}\n"
            "Use `set_language` to set it before listing metrics or dimensions."
        )
    return None


@mcp.tool()
def list_metrics() -> str:
    """List all available metrics in the active NeoDash instance.

    Returns metrics with their human-readable labels, descriptions,
    target direction (up = higher is better, down = lower is better),
    and display format (currency, percent, number, duration).

    Match the user's request against the **label names** below, then
    use the corresponding **ID** when calling ``query_data``.
    """
    active = _get_active()
    blocked = _language_guard(active)
    if blocked:
        return blocked

    endpoints = _get_endpoints(active)
    metrics = endpoints.get_metrics()

    if not metrics:
        return "No metrics found in this instance."

    lines = [
        "**Available Metrics:**\n"
        "Match user requests against the **labels** below. "
        "Use the **ID** (after the arrow) in `query_data`.\n"
    ]
    for m in metrics:
        label = m.resolve_label(active.language)
        parts = [f"- **{label}** → ID: `{m.id}`"]

        annotations: list[str] = []
        if m.format and m.format != "number":
            annotations.append(m.format)
        if m.target and m.target != "neutral":
            direction = "↑ higher is better" if m.target == "up" else "↓ lower is better"
            annotations.append(direction)
        elif m.target == "neutral":
            annotations.append("neutral")
        if annotations:
            parts.append(f" [{', '.join(annotations)}]")

        if m.description:
            parts.append(f"\n  {m.description}")

        lines.append("".join(parts))

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)


@mcp.tool()
def list_dimensions() -> str:
    """List all available dimensions in the active NeoDash instance.

    Dimensions are used to break down and segment your data
    (e.g., Campaign, Ad Group, Ad, Brand, etc.).

    Match the user's request against the **label names** below, then
    use the corresponding **ID** when calling ``query_data``.
    """
    active = _get_active()
    blocked = _language_guard(active)
    if blocked:
        return blocked

    endpoints = _get_endpoints(active)
    dimensions = endpoints.get_dimensions()

    if not dimensions:
        return "No dimensions found in this instance."

    lines = [
        "**Available Dimensions:**\n"
        "Match user requests against the **labels** below. "
        "Use the **ID** (after the arrow) in `query_data`.\n"
    ]
    for d in dimensions:
        label = d.resolve_label(active.language)
        desc = f" — {d.description}" if d.description else ""
        lines.append(f"- **{label}** → ID: `{d.id}`{desc}")

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)
