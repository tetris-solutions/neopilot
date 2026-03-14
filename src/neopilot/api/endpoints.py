"""NeoDash API endpoint wrappers.

Each method wraps a specific NeoDash endpoint and returns
parsed Pydantic models.
"""

from __future__ import annotations

import logging
from typing import Any

from neopilot.api.client import NeoDashClient
from neopilot.models.dashboards import (
    ComponentResult,
    ComponentSummary,
    DashboardListResponse,
    DashboardSummary,
    DatasetInfo,
)
from neopilot.models.dimensions import Dimension
from neopilot.models.explorer import ExplorerQuery, ExplorerResult
from neopilot.models.metrics import Metric

logger = logging.getLogger(__name__)


class NeoDashEndpoints:
    """All NeoDash API endpoint wrappers.

    Parameters
    ----------
    client:
        An authenticated :class:`NeoDashClient` for a specific instance.
    """

    def __init__(self, client: NeoDashClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # AI-Exclusive Endpoints
    # ------------------------------------------------------------------

    def get_metrics(self) -> list[Metric]:
        """Fetch all metrics from ``/ai/metrics``."""
        data = self._client.get("/ai/metrics")
        raw_list = _ensure_list(data)
        return [Metric.model_validate(m) for m in raw_list]

    def get_dimensions(self) -> list[Dimension]:
        """Fetch all dimensions from ``/ai/dimensions``."""
        data = self._client.get("/ai/dimensions")
        raw_list = _ensure_list(data)
        return [Dimension.model_validate(d) for d in raw_list]

    def get_all_components(self, dashboard_id: str) -> list[ComponentSummary]:
        """Fetch all components of a dashboard from ``/ai/allComponents``.

        Parameters
        ----------
        dashboard_id:
            The dashboard ID.
        """
        data = self._client.get(
            "/ai/allComponents",
            params={"id_dashboard": dashboard_id},
        )
        raw_list = _ensure_list(data)
        return [ComponentSummary.model_validate(c) for c in raw_list]

    def get_component_data(
        self,
        dashboard_id: str,
        component_id: str,
        date_start: str,
        date_end: str,
    ) -> ComponentResult:
        """Fetch actual data for a component from ``/ai/component``.

        Parameters
        ----------
        dashboard_id:
            The dashboard ID.
        component_id:
            The component ID.
        date_start:
            Start date (``YYYY-MM-DD``).
        date_end:
            End date (``YYYY-MM-DD``).
        """
        data = self._client.get(
            "/ai/component",
            params={
                "id_dashboard": dashboard_id,
                "id_component": component_id,
                "dti": date_start,
                "dtf": date_end,
            },
        )
        return _parse_component_result(data)

    # ------------------------------------------------------------------
    # Core Endpoints
    # ------------------------------------------------------------------

    def list_dashboards(self, page: int = 1, search: str = "") -> DashboardListResponse:
        """List dashboards from ``/get/resumoDashboard``.

        Parameters
        ----------
        page:
            Page number (1-indexed).
        search:
            Search term for dashboard names.
        """
        data = self._client.get(
            "/get/resumoDashboard",
            params={
                "page": str(page),
                "searchKey": search,
                "sort": "recent",
            },
        )

        if not isinstance(data, dict):
            return DashboardListResponse()

        # Extract dashboards from the "campaigns" node
        campaigns = data.get("campaigns", [])
        dashboards = []
        if isinstance(campaigns, list):
            for camp in campaigns:
                if isinstance(camp, dict):
                    dashboards.append(
                        DashboardSummary(
                            id=str(camp.get("id", "")),
                            name=camp.get("name", camp.get("titulo", "")),
                            description=camp.get("description"),
                        )
                    )

        # Extract user language
        user_language = "pt-BR"
        user = data.get("user", {})
        if isinstance(user, dict):
            user_language = user.get("default_language", "pt-BR")

        return DashboardListResponse(
            dashboards=dashboards,
            user_language=user_language,
            total_pages=data.get("total_pages", 1),
            current_page=page,
        )

    def query_explorer(self, query: ExplorerQuery) -> ExplorerResult:
        """Query data via the Explorer endpoint ``/get/exploradorResults``.

        Parameters
        ----------
        query:
            An :class:`ExplorerQuery` with dimensions, metrics, dates, etc.
        """
        params = query.to_api_params()
        data = self._client.get("/get/exploradorResults", params=params)

        if not isinstance(data, dict):
            return ExplorerResult()

        # Parse main results
        results_init = data.get("resultsInit", {})
        results = []
        totals: dict[str, Any] = {}
        if isinstance(results_init, dict):
            results = results_init.get("results", [])
            totals = results_init.get("total", results_init.get("totals", {}))
            if isinstance(totals, list) and len(totals) == 1:
                totals = totals[0]

        # Parse comparison results
        comparison_results = None
        comparison_totals = None
        results_compare = data.get("resultsCompare")
        if isinstance(results_compare, dict):
            comparison_results = results_compare.get("results", [])
            ct = results_compare.get("total", results_compare.get("totals", {}))
            if isinstance(ct, list) and len(ct) == 1:
                ct = ct[0]
            comparison_totals = ct

        row_count = len(results) if isinstance(results, list) else 0
        was_truncated = row_count >= query.limit

        truncation_message = None
        if was_truncated:
            truncation_message = (
                f"Results were truncated at {query.limit} rows. "
                "You can increase the limit or add more specific dimensions "
                "to see all data."
            )

        return ExplorerResult(
            results=results if isinstance(results, list) else [],
            totals=totals if isinstance(totals, dict) else {},
            comparison_results=comparison_results,
            comparison_totals=comparison_totals if isinstance(comparison_totals, dict) else None,
            row_count=row_count,
            was_truncated=was_truncated,
            truncation_message=truncation_message,
        )

    def get_dataset(self) -> DatasetInfo:
        """Fetch dataset metadata from ``/get/dataset?extended=1``."""
        data = self._client.get("/get/dataset", params={"extended": "1"})
        if isinstance(data, dict):
            return DatasetInfo(raw=data)
        return DatasetInfo()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _ensure_list(data: Any) -> list:
    """Safely coerce API response to a list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Some endpoints wrap the list in a key
        for key in ("data", "results", "items", "metrics", "dimensions", "components"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return []


def _parse_component_result(data: Any) -> ComponentResult:
    """Parse the response from /ai/component into a ComponentResult."""
    if not isinstance(data, dict):
        return ComponentResult(raw_response={"raw": data})

    component_data = data.get("componentData", data.get("component_data"))
    results: list[dict[str, Any]] = []
    totals: dict[str, Any] = {}

    if isinstance(component_data, dict):
        results = component_data.get("results", [])
        totals = component_data.get("totals", component_data.get("total", {}))
        if isinstance(totals, list) and len(totals) == 1:
            totals = totals[0]
    elif isinstance(component_data, list):
        results = component_data

    return ComponentResult(
        component_data=component_data,
        results=results if isinstance(results, list) else [],
        totals=totals if isinstance(totals, dict) else {},
        metrics_used=data.get("metrics", []),
        dimensions_used=data.get("dimensions", data.get("segments", [])),
        raw_response=data,
    )
