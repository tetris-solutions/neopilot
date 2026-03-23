"""MCP tool for free-form data queries via the NeoDash Explorer."""

from __future__ import annotations

import json
from typing import Any

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.api.errors import FilterNotReadyError
from neopilot.app import mcp
from neopilot.infra.debug import debug_block
from neopilot.infra.env import is_debug
from neopilot.infra.version import enforce_version
from neopilot.models.explorer import MAX_LIMIT, TIME_BREAKDOWNS, ExplorerQuery
from neopilot.models.filters import FilterExpression, FilterGroup, Filters
from neopilot.models.instance import InstanceInfo
from neopilot.storage.local_store import InstanceStore

# Localized label for the "See data on NeoDash" link
_NEODASH_LINK_LABEL = {
    "pt-BR": "Ver dados no NeoDash",
    "en-US": "See data on NeoDash",
}


def _get_active_and_endpoints() -> tuple[InstanceInfo, NeoDashEndpoints]:
    """Return the active instance and its endpoints."""
    store = InstanceStore()
    active = store.get_active()
    client = NeoDashClient(active.slug, active.api_token)
    return active, NeoDashEndpoints(client)


def _parse_filters(
    segment_filters: list[dict[str, Any]] | None,
    metric_filters: list[dict[str, Any]] | None,
) -> Filters:
    """Parse user-provided filter dicts into a ``Filters`` model.

    Each filter dict has:
    - ``dimension`` or ``metric``: the field ID (e.g., ``"campanha_externa_nome"``)
    - ``operator``: comparison operator (e.g., ``"c"``, ``"="``, ``">"``)
    - ``value``: comparison value (string, number-as-string, or list of strings)
    - ``field_comparison`` (optional): ``true`` when comparing metric vs metric
    - ``group`` (optional): ``"or"`` to OR with next filter in same group,
      default ``"and"``

    Returns a ``Filters`` object ready for ``ExplorerQuery``.
    """
    filters = Filters()

    if segment_filters:
        # Group consecutive filters by their group_type
        and_exprs: list[list[list[FilterExpression]]] = []
        or_exprs: list[list[list[FilterExpression]]] = []
        current_is_or = False

        for i, f in enumerate(segment_filters):
            expr = FilterExpression(
                chave=f["dimension"],
                operador=f["operator"],
                valor=f["value"],
                estrutura="segmento",
            )
            is_or = f.get("group", "and").lower() == "or"

            if i == 0:
                current_is_or = is_or

            if is_or == current_is_or:
                # Same group logic — add as another branch
                if current_is_or:
                    or_exprs.append([[expr]])
                else:
                    and_exprs.append([[expr]])
            else:
                # Logic changed — flush current group, start new
                if current_is_or and or_exprs:
                    filters.segment.append(
                        FilterGroup(group_type="or_group", expressions=or_exprs)
                    )
                    or_exprs = []
                elif not current_is_or and and_exprs:
                    filters.segment.append(
                        FilterGroup(group_type="and_group", expressions=and_exprs)
                    )
                    and_exprs = []
                current_is_or = is_or
                if is_or:
                    or_exprs.append([[expr]])
                else:
                    and_exprs.append([[expr]])

        # Flush remaining
        if or_exprs:
            filters.segment.append(
                FilterGroup(group_type="or_group", expressions=or_exprs)
            )
        if and_exprs:
            filters.segment.append(
                FilterGroup(group_type="and_group", expressions=and_exprs)
            )

    if metric_filters:
        and_exprs_m: list[list[list[FilterExpression]]] = []
        or_exprs_m: list[list[list[FilterExpression]]] = []
        current_is_or_m = False

        for i, f in enumerate(metric_filters):
            expr = FilterExpression(
                chave=f["metric"],
                operador=f["operator"],
                valor=f["value"],
                estrutura="metrica",
                tipo="field" if f.get("field_comparison") else None,
            )
            is_or = f.get("group", "and").lower() == "or"

            if i == 0:
                current_is_or_m = is_or

            if is_or == current_is_or_m:
                if current_is_or_m:
                    or_exprs_m.append([[expr]])
                else:
                    and_exprs_m.append([[expr]])
            else:
                if current_is_or_m and or_exprs_m:
                    filters.metric.append(
                        FilterGroup(group_type="or_group", expressions=or_exprs_m)
                    )
                    or_exprs_m = []
                elif not current_is_or_m and and_exprs_m:
                    filters.metric.append(
                        FilterGroup(group_type="and_group", expressions=and_exprs_m)
                    )
                    and_exprs_m = []
                current_is_or_m = is_or
                if is_or:
                    or_exprs_m.append([[expr]])
                else:
                    and_exprs_m.append([[expr]])

        if or_exprs_m:
            filters.metric.append(
                FilterGroup(group_type="or_group", expressions=or_exprs_m)
            )
        if and_exprs_m:
            filters.metric.append(
                FilterGroup(group_type="and_group", expressions=and_exprs_m)
            )

    return filters


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
    segment_filters: list[dict[str, Any]] | None = None,
    metric_filters: list[dict[str, Any]] | None = None,
    confirmed: bool = False,
) -> str:
    """Query advertising data from NeoDash using the Explorer.

    **This is a two-step tool:**
    1. First call with ``confirmed=false`` (default) to preview the query.
       Show the preview to the user and ask them to confirm.
    2. Then call again with ``confirmed=true`` to execute the query.

    **CRITICAL: Before calling this tool, you MUST first call ``list_metrics``
    and ``list_dimensions`` to get the exact IDs available in this instance.**
    Do NOT guess metric or dimension IDs — they vary between instances.

    **Important rules:**
    - Date format: ``YYYY-MM-DD``
    - Always ask the user for the date range they want to analyze
    - Totals are calculated by NeoDash — never calculate them yourself
    - If results are truncated, inform the user

    Parameters
    ----------
    dimensions:
        List of dimension IDs to break down by (e.g., ``["campanha", "grupo_anuncio"]``).
        **You MUST call ``list_dimensions`` first** to get the valid IDs.
    metrics:
        List of metric IDs to retrieve (e.g., ``["custo_total", "cliques", "ctr"]``).
        **You MUST call ``list_metrics`` first** to get the valid IDs.
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
    segment_filters:
        Optional list of dimension filters. Each filter is a dict with:

        - ``dimension``: dimension ID (e.g., ``"campanha_externa_nome"``)
        - ``operator``: one of ``"c"`` (contains), ``"!c"`` (not contains),
          ``"="`` (equals), ``"!="`` (not equals), ``"in"`` (one of),
          ``"!in"`` (not one of), ``"or"`` (contains one of),
          ``"!or"`` (not contains any), ``"allc"`` (contains all),
          ``"!allc"`` (not contains all), ``"vazio"`` (empty),
          ``"!vazio"`` (not empty)
        - ``value``: string or list of strings to compare against
        - ``group`` (optional): ``"or"`` to OR with other filters,
          default ``"and"``

        Example: ``[{"dimension": "campanha_externa_nome", "operator": "c", "value": "amz"}]``
    metric_filters:
        Optional list of metric filters. Each filter is a dict with:

        - ``metric``: metric ID (e.g., ``"cpc"``, ``"custo_total"``)
        - ``operator``: one of ``"="``, ``"!="``, ``">"``, ``">="``,
          ``"<"``, ``"<="``, ``"between"``, ``"!between"``
        - ``value``: number as string, or another metric ID when
          ``field_comparison=true``
        - ``field_comparison`` (optional): set ``true`` to compare
          metric vs metric (e.g., Spend > Clicks)
        - ``group`` (optional): ``"or"`` to OR with other filters,
          default ``"and"``

        Example: ``[{"metric": "cpc", "operator": ">", "value": "3"}]``
    confirmed:
        Set to ``true`` to execute the query. Default ``false`` returns
        a preview for user confirmation.
    """
    # Block usage if version is below minimum
    blocked = enforce_version()
    if blocked:
        return blocked

    if time_breakdown not in TIME_BREAKDOWNS:
        return (
            f"Invalid time_breakdown '{time_breakdown}'. "
            f"Valid options: {', '.join(TIME_BREAKDOWNS.keys())}"
        )

    if limit > MAX_LIMIT:
        return f"Limit cannot exceed {MAX_LIMIT:,}. Please use a smaller value."

    # --- Parse filters ---
    filters = _parse_filters(segment_filters, metric_filters)

    # --- Confirmation step ---
    if not confirmed:
        lines = ["**Query Preview — please confirm before executing:**\n"]
        lines.append(f"- **Dimensions:** {', '.join(dimensions)}")
        lines.append(f"- **Metrics:** {', '.join(metrics)}")
        lines.append(f"- **Date range:** {date_start} to {date_end}")
        if time_breakdown != "nao":
            lines.append(f"- **Time breakdown:** {TIME_BREAKDOWNS[time_breakdown]}")
        if order_by:
            lines.append(f"- **Order by:** {order_by} ({order_sort})")
        if compare_date_start and compare_date_end:
            lines.append(
                f"- **Comparison period:** {compare_date_start} to {compare_date_end}"
            )
        if not filters.is_empty():
            lines.append(f"- **Filters:** {filters.to_summary()}")
        lines.append(f"- **Row limit:** {limit:,}")
        lines.append(
            "\nShow this to the user and ask them to confirm. "
            "If confirmed, call `query_data` again with the same parameters "
            "and `confirmed=true`."
        )
        return "\n".join(lines)

    # --- Execute query ---
    active, endpoints = _get_active_and_endpoints()

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
        filters=filters,
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
    if not filters.is_empty():
        lines.append(f"- Filters: {filters.to_summary()}")
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

    # NeoDash link — with explicit instruction for the LLM to always show it
    neodash_link = query.to_neodash_link(active.slug)
    link_label = _NEODASH_LINK_LABEL.get(active.language, _NEODASH_LINK_LABEL["en-US"])
    lines.append("")
    lines.append(f"[{link_label}]({neodash_link})")
    lines.append("")
    lines.append(
        "IMPORTANT: You MUST always include the NeoDash link above in your "
        "response to the user, even when summarizing or formatting the data "
        "as a report. The link lets the user see this exact query on NeoDash."
    )

    if is_debug():
        lines.append(debug_block(endpoints._client))

    return "\n".join(lines)


@mcp.tool()
def create_short_link(url: str) -> str:
    """Create a compressed/short link from a NeoDash URL for easy sharing.

    Use this tool when the user asks for a "compressed link", "short link",
    "link to share", "link encurtado", "link curto", or "link para compartilhar".

    Parameters
    ----------
    url:
        The full NeoDash URL to shorten (e.g., an Explorer link).
    """
    blocked = enforce_version()
    if blocked:
        return blocked

    active, endpoints = _get_active_and_endpoints()

    short_url = endpoints.create_short_link(url)

    label = {
        "pt-BR": "Link encurtado",
        "en-US": "Short link",
    }
    link_label = label.get(active.language, label["en-US"])

    return f"**{link_label}:** {short_url}"


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
