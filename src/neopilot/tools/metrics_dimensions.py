"""MCP tools for listing metrics and dimensions."""

from __future__ import annotations

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.app import mcp
from neopilot.infra.debug import debug_block
from neopilot.infra.env import is_debug
from neopilot.storage.local_store import InstanceStore


def _get_endpoints() -> tuple[NeoDashEndpoints, str]:
    """Return endpoints and the active instance language."""
    store = InstanceStore()
    active = store.get_active()
    client = NeoDashClient(active.slug, active.api_token)
    return NeoDashEndpoints(client), active.language


@mcp.tool()
def list_metrics() -> str:
    """List all available metrics in the active NeoDash instance.

    Returns metrics with their human-readable labels, descriptions,
    target direction (up = higher is better, down = lower is better),
    and display format (currency, percent, number, duration).

    Use the metric IDs when calling ``query_data`` or other tools.
    """
    endpoints, language = _get_endpoints()
    metrics = endpoints.get_metrics()

    if not metrics:
        return "No metrics found in this instance."

    lines = ["**Available Metrics:**\n"]
    for m in metrics:
        label = m.resolve_label(language)
        parts = [f"- **{label}** (`{m.id}`)"]

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

    Use the dimension IDs when calling ``query_data``.
    """
    endpoints, language = _get_endpoints()
    dimensions = endpoints.get_dimensions()

    if not dimensions:
        return "No dimensions found in this instance."

    lines = ["**Available Dimensions:**\n"]
    for d in dimensions:
        label = d.resolve_label(language)
        desc = f" — {d.description}" if d.description else ""
        lines.append(f"- **{label}** (`{d.id}`){desc}")

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)
