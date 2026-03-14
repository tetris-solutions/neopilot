"""MCP tools for component data retrieval."""

from __future__ import annotations

import json

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
def get_component_data(
    dashboard_id: str,
    component_id: str,
    date_start: str,
    date_end: str,
) -> str:
    """Get actual data for a specific dashboard component.

    This retrieves the real data (results + totals) for a component.
    Use ``get_dashboard_components`` first to find component IDs.

    **Important:** Always ask the user for the date range they want to analyze.

    Parameters
    ----------
    dashboard_id:
        The dashboard ID containing this component.
    component_id:
        The component ID (from ``get_dashboard_components``).
    date_start:
        Start date in ``YYYY-MM-DD`` format.
    date_end:
        End date in ``YYYY-MM-DD`` format.
    """
    endpoints, _language = _get_endpoints()

    result = endpoints.get_component_data(
        dashboard_id=dashboard_id,
        component_id=component_id,
        date_start=date_start,
        date_end=date_end,
    )

    lines: list[str] = []
    lines.append(f"**Component Data** (dashboard: `{dashboard_id}`, component: `{component_id}`)")
    lines.append(f"- Period: {date_start} to {date_end}")

    if result.metrics_used:
        lines.append(f"- Metrics: {', '.join(result.metrics_used)}")
    if result.dimensions_used:
        lines.append(f"- Dimensions: {', '.join(result.dimensions_used)}")
    lines.append("")

    # Totals
    if result.totals:
        lines.append("**Totals:**")
        lines.append(
            f"```json\n{json.dumps(result.totals, indent=2, ensure_ascii=False)}\n```"
        )
        lines.append("")

    # Results
    if result.results:
        lines.append(f"**Data** ({len(result.results)} rows):")
        lines.append(
            f"```json\n{json.dumps(result.results, indent=2, ensure_ascii=False)}\n```"
        )

    if not result.results and not result.totals:
        lines.append("No data returned for this component and date range.")

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)
