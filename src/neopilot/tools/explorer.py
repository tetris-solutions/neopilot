"""MCP tool for free-form data queries via the NeoDash Explorer."""

from __future__ import annotations

import json

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.api.errors import FilterNotReadyError
from neopilot.app import mcp
from neopilot.infra.debug import debug_block
from neopilot.infra.env import is_debug
from neopilot.models.explorer import MAX_LIMIT, TIME_BREAKDOWNS, ExplorerQuery
from neopilot.storage.local_store import InstanceStore


def _get_endpoints() -> tuple[NeoDashEndpoints, str]:
    """Return endpoints and the active instance language."""
    store = InstanceStore()
    active = store.get_active()
    client = NeoDashClient(active.slug, active.api_token)
    return NeoDashEndpoints(client), active.language


@mcp.tool()
def query_data(
    dimensions: list[str],
    metrics: list[str],
    date_start: str,
    date_end: str,
    time_breakdown: str = "nao",
    limit: int = 500,
    order_by: str | None = None,
    order_sort: str = "desc",
    compare_date_start: str | None = None,
    compare_date_end: str | None = None,
) -> str:
    """Query advertising data from NeoDash using the Explorer.

    This is the most flexible way to retrieve data. You specify which
    dimensions to break down by, which metrics to retrieve, and the
    date range.

    **Important rules:**
    - Date format: ``YYYY-MM-DD``
    - Always ask the user for the date range they want to analyze
    - Totals are calculated by NeoDash — never calculate them yourself
    - If results are truncated, inform the user

    **Filters on demand are not ready yet.** If the user needs to filter,
    let them know this feature is coming in a future update.

    Parameters
    ----------
    dimensions:
        List of dimension IDs to break down by (e.g., ``["campanha", "grupo_anuncio"]``).
        Use ``list_dimensions`` to see available dimensions.
    metrics:
        List of metric IDs to retrieve (e.g., ``["custo_total", "cliques", "ctr"]``).
        Use ``list_metrics`` to see available metrics.
    date_start:
        Start date in ``YYYY-MM-DD`` format.
    date_end:
        End date in ``YYYY-MM-DD`` format.
    time_breakdown:
        How to segment data over time. Options:
        ``nao`` (none), ``dia`` (daily), ``semana`` (weekly Sun-Sat),
        ``semanaseg`` (weekly Mon-Sun), ``diasemana`` (day of week),
        ``mes`` (monthly), ``bimestre``, ``trimestre`` (quarterly),
        ``semestre``, ``ano`` (yearly).
    limit:
        Maximum rows to return (default: 500, max: 50000).
    order_by:
        Metric ID to sort by (e.g., ``custo_total``).
    order_sort:
        Sort direction: ``asc`` or ``desc`` (default: ``desc``).
    compare_date_start:
        Optional comparison period start date (``YYYY-MM-DD``).
    compare_date_end:
        Optional comparison period end date (``YYYY-MM-DD``).
    """
    if time_breakdown not in TIME_BREAKDOWNS:
        return (
            f"Invalid time_breakdown '{time_breakdown}'. "
            f"Valid options: {', '.join(TIME_BREAKDOWNS.keys())}"
        )

    if limit > MAX_LIMIT:
        return f"Limit cannot exceed {MAX_LIMIT:,}. Please use a smaller value."

    endpoints, _language = _get_endpoints()

    query = ExplorerQuery(
        dimensions=dimensions,
        metrics=metrics,
        date_start=date_start,
        date_end=date_end,
        time_breakdown=time_breakdown,
        limit=limit,
        order_by=order_by,
        order_sort=order_sort,
        compare_date_start=compare_date_start,
        compare_date_end=compare_date_end,
    )

    result = endpoints.query_explorer(query)

    # Build response
    lines: list[str] = []

    # Metadata
    lines.append(f"**Query Results** ({result.row_count} rows)")
    lines.append(f"- Period: {date_start} to {date_end}")
    if compare_date_start and compare_date_end:
        lines.append(f"- Comparison: {compare_date_start} to {compare_date_end}")
    lines.append(f"- Dimensions: {', '.join(dimensions)}")
    lines.append(f"- Metrics: {', '.join(metrics)}")
    if time_breakdown != "nao":
        lines.append(f"- Time breakdown: {TIME_BREAKDOWNS[time_breakdown]}")
    lines.append("")

    # Truncation warning
    if result.was_truncated and result.truncation_message:
        lines.append(f"⚠️ {result.truncation_message}")
        lines.append("")

    # Totals
    if result.totals:
        lines.append("**Totals:**")
        lines.append(f"```json\n{json.dumps(result.totals, indent=2, ensure_ascii=False)}\n```")
        lines.append("")

    # Results
    if result.results:
        lines.append("**Data:**")
        lines.append(
            f"```json\n{json.dumps(result.results, indent=2, ensure_ascii=False)}\n```"
        )

    # Comparison results
    if result.comparison_results:
        lines.append("")
        lines.append("**Comparison Data:**")
        if result.comparison_totals:
            lines.append("Comparison Totals:")
            lines.append(
                f"```json\n{json.dumps(result.comparison_totals, indent=2, ensure_ascii=False)}\n```"
            )
        lines.append(
            f"```json\n{json.dumps(result.comparison_results, indent=2, ensure_ascii=False)}\n```"
        )

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)


@mcp.tool()
def list_time_breakdowns() -> str:
    """List all available time breakdown options for the Explorer.

    These are used with the ``time_breakdown`` parameter of ``query_data``.
    """
    lines = ["**Time Breakdown Options:**\n"]
    for slug, desc in TIME_BREAKDOWNS.items():
        lines.append(f"- `{slug}` — {desc}")
    return "\n".join(lines)


@mcp.tool()
def apply_filter() -> str:
    """Apply filters to data queries.

    **This feature is not ready yet.** Custom filters on demand are coming
    in a future update. For now, you can use the component-based approach
    (``get_component_data``) which includes pre-configured filters.
    """
    raise FilterNotReadyError
