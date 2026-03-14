"""MCP tools for dashboard operations."""

from __future__ import annotations

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.app import mcp
from neopilot.infra.debug import debug_block
from neopilot.infra.env import is_debug
from neopilot.storage.local_store import InstanceStore


def _get_endpoints() -> tuple[NeoDashEndpoints, str]:
    """Return endpoints and the active slug."""
    store = InstanceStore()
    active = store.get_active()
    client = NeoDashClient(active.slug, active.api_token)
    return NeoDashEndpoints(client), active.language


@mcp.tool()
def list_dashboards(page: int = 1, search: str = "") -> str:
    """List all dashboards available in the active NeoDash instance.

    Parameters
    ----------
    page:
        Page number (1-indexed). Each page shows up to 20 dashboards.
    search:
        Optional search term to filter dashboards by name.
    """
    endpoints, _lang = _get_endpoints()
    response = endpoints.list_dashboards(page=page, search=search)

    if not response.dashboards:
        if search:
            return f"No dashboards found matching '{search}'."
        return "No dashboards found in this instance."

    lines = [f"**Dashboards** (page {response.current_page}):\n"]
    for db in response.dashboards:
        desc = f" — {db.description}" if db.description else ""
        lines.append(f"- **{db.name}** (id: `{db.id}`){desc}")

    lines.append(
        "\nUse `get_dashboard_components` with a dashboard id to see its components."
    )

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)


@mcp.tool()
def get_dashboard_components(dashboard_id: str) -> str:
    """List all components in a specific dashboard.

    Returns the component IDs, titles, and types. Use these IDs with
    ``get_component_data`` to retrieve the actual data.

    Parameters
    ----------
    dashboard_id:
        The dashboard ID (from ``list_dashboards``).
    """
    endpoints, _lang = _get_endpoints()
    components = endpoints.get_all_components(dashboard_id)

    if not components:
        return f"No components found in dashboard `{dashboard_id}`."

    lines = [f"**Components in dashboard `{dashboard_id}`:**\n"]
    for comp in components:
        subtitle = f" — {comp.subtitle}" if comp.subtitle else ""
        comp_type = f" [{comp.component}]" if comp.component else ""
        lines.append(f"- **{comp.title}**{subtitle}{comp_type} (id: `{comp.id}`)")

    lines.append(
        "\nUse `get_component_data` with a component id, dashboard id, "
        "and date range to get the actual data."
    )

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)
