"""Explorer query and response models."""

from __future__ import annotations

import json
import urllib.parse
from typing import Any, Literal

from pydantic import BaseModel, Field

# Valid time breakdown slugs
TIME_BREAKDOWNS = {
    "nao": "No time breakdown",
    "dia": "By day",
    "semana": "By week (Sun-Sat)",
    "semanaseg": "By week (Mon-Sun)",
    "diasemana": "By day of the week",
    "mes": "By month",
    "bimestre": "By bimester",
    "trimestre": "By quarter",
    "semestre": "By semester",
    "ano": "By year",
}

MAX_LIMIT = 50_000
DEFAULT_LIMIT = 500


def _flip_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to DD-MM-YYYY for NeoDash frontend links."""
    parts = date_str.split("-")
    if len(parts) == 3:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return date_str


class ExplorerQuery(BaseModel):
    """Parameters for the Explorer data query (/get/exploradorResults).

    This model builds the query parameters expected by the NeoDash API.
    """

    dimensions: list[str]
    metrics: list[str]
    date_start: str  # YYYY-MM-DD
    date_end: str  # YYYY-MM-DD
    time_breakdown: str = "nao"
    compare_date_start: str | None = None  # YYYY-MM-DD
    compare_date_end: str | None = None  # YYYY-MM-DD
    limit: int = DEFAULT_LIMIT
    order_by: str | None = None
    order_sort: Literal["asc", "desc"] = "desc"

    def to_api_params(self) -> dict[str, str]:
        """Convert to query parameters for the NeoDash API.

        Notes
        -----
        - ``showTotals`` is always ``true`` — NeoPilot NEVER calculates totals itself.
        - ``no-cache`` is always ``false`` unless the user explicitly requests a cache bypass.
        - ``filtros`` is always empty — filter on demand is deferred.
        """
        capped_limit = min(self.limit, MAX_LIMIT)

        json_obj = {
            "segmentos": ",".join(self.dimensions),
            "metricas": ",".join(self.metrics),
            "segmentarPor": self.time_breakdown,
            "filtros": {},
        }

        params: dict[str, str] = {
            "dti": self.date_start,
            "dtf": self.date_end,
            "json": json.dumps(json_obj, ensure_ascii=False),
            "limite": str(capped_limit),
            "showTotals": "true",
            "no-cache": "false",
            "orderSort": self.order_sort,
        }

        if self.order_by:
            params["orderBy"] = self.order_by

        if self.compare_date_start and self.compare_date_end:
            params["dtic"] = self.compare_date_start
            params["dtfc"] = self.compare_date_end

        return params

    def to_neodash_link(self, slug: str) -> str:
        """Build a link to the NeoDash Explorer frontend for this query.

        The link opens the same data view in the NeoDash web interface.
        Dates are converted from YYYY-MM-DD to DD-MM-YYYY format.
        """
        # Build template.params — the json payload for the frontend
        template_params: dict[str, Any] = {
            "segmentos": ",".join(self.dimensions),
            "metricas": ",".join(self.metrics),
            "segmentarPor": self.time_breakdown,
            "order": self.order_sort,
            "filtros": {},
            "openGraphExplorador": 0,
            "totalPercent": 1,
            "showMetricsTotal": 1,
        }

        if self.order_by:
            template_params["orderBy"] = self.order_by

        template = {"params": template_params}
        template_json = json.dumps(template, ensure_ascii=False, separators=(",", ":"))

        # Build URL with DD-MM-YYYY dates
        url = f"https://{slug}.neodash.ai/explorador/100"
        url += f"?dti={_flip_date(self.date_start)}"
        url += f"&dtf={_flip_date(self.date_end)}"

        if self.compare_date_start and self.compare_date_end:
            url += f"&dtic={_flip_date(self.compare_date_start)}"
            url += f"&dtfc={_flip_date(self.compare_date_end)}"

        url += f"&template={urllib.parse.quote(template_json, safe='')}"
        return url


class ExplorerResult(BaseModel):
    """Parsed response from the Explorer endpoint."""

    results: list[dict[str, Any]] = Field(default_factory=list)
    totals: dict[str, Any] = Field(default_factory=dict)
    comparison_results: list[dict[str, Any]] | None = None
    comparison_totals: dict[str, Any] | None = None
    row_count: int = 0
    was_truncated: bool = False
    truncation_message: str | None = None

    model_config = {"extra": "allow"}
