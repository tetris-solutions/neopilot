"""Global-level context — fetched dynamically from the NeoDash API."""

from __future__ import annotations

import logging

from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.models.context import GlobalContext

logger = logging.getLogger(__name__)


def build_global_context(
    endpoints: NeoDashEndpoints,
    slug: str,
    language: str = "pt-BR",
) -> GlobalContext:
    """Build global context by fetching metrics, dimensions, and dashboards.

    Parameters
    ----------
    endpoints:
        Authenticated endpoint wrapper.
    slug:
        Instance slug.
    language:
        Language for label resolution.
    """
    metric_summaries: list[str] = []
    dimension_summaries: list[str] = []
    dashboard_summaries: list[str] = []

    # Fetch metrics
    metric_count = 0
    try:
        metrics = endpoints.get_metrics()
        metric_count = len(metrics)
        for m in metrics:
            label = m.resolve_label(language)
            target_info = f" (better when {m.target})" if m.target else ""
            fmt_info = f" [{m.format}]" if m.format != "number" else ""
            metric_summaries.append(f"{label} (`{m.id}`){fmt_info}{target_info}")
    except Exception:
        logger.warning("Could not fetch metrics for global context.")

    # Fetch dimensions
    dimension_count = 0
    try:
        dimensions = endpoints.get_dimensions()
        dimension_count = len(dimensions)
        for d in dimensions:
            label = d.resolve_label(language)
            dimension_summaries.append(f"{label} (`{d.id}`)")
    except Exception:
        logger.warning("Could not fetch dimensions for global context.")

    # Fetch dashboards (first page)
    dashboard_count = 0
    try:
        dash_response = endpoints.list_dashboards(page=1)
        dashboard_count = len(dash_response.dashboards)
        for db in dash_response.dashboards:
            desc = f": {db.description}" if db.description else ""
            dashboard_summaries.append(f"{db.name} (id: {db.id}){desc}")
    except Exception:
        logger.warning("Could not fetch dashboards for global context.")

    return GlobalContext(
        slug=slug,
        metric_count=metric_count,
        dimension_count=dimension_count,
        dashboard_count=dashboard_count,
        metric_summaries=metric_summaries,
        dimension_summaries=dimension_summaries,
        dashboard_summaries=dashboard_summaries,
        language=language,
    )
