"""Explorer query and response models."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Literal

from pydantic import BaseModel, Field

from neopilot.models.filters import Filters

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
    filters: Filters = Field(default_factory=Filters)

    def to_api_params(self) -> dict[str, str]:
        """Convert to query parameters for the NeoDash API.

        Notes
        -----
        - ``showTotals`` is always ``true`` — NeoPilot NEVER calculates totals itself.
        - ``no-cache`` is always ``false`` unless the user explicitly requests a cache bypass.
        - ``filtros`` is serialized from the ``filters`` model; empty dict when no filters.
        """
        capped_limit = min(self.limit, MAX_LIMIT)

        json_obj = {
            "segmentos": ",".join(self.dimensions),
            "metricas": ",".join(self.metrics),
            "segmentarPor": self.time_breakdown,
            "filtros": self.filters.to_api_dict(),
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
            "filtros": self.filters.to_api_dict(),
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

    @classmethod
    def from_neodash_link(cls, url: str) -> ExplorerQuery:
        """Parse a NeoDash Explorer URL into an ``ExplorerQuery``.

        Handles the three filter sources found in NeoDash URLs:

        1. ``template.params.filtros`` — saved template filters
        2. ``filtroUsuario`` — user-applied advanced filters
        3. ``filtroLocal`` — combo box quick filters

        All three are merged into a single ``Filters`` object.
        Dates are flipped from DD-MM-YYYY back to YYYY-MM-DD.
        """
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)

        # --- Dates (DD-MM-YYYY → YYYY-MM-DD) ---
        date_start = _flip_date(qs["dti"][0]) if "dti" in qs else ""
        date_end = _flip_date(qs["dtf"][0]) if "dtf" in qs else ""
        compare_start = _flip_date(qs["dtic"][0]) if "dtic" in qs else None
        compare_end = _flip_date(qs["dtfc"][0]) if "dtfc" in qs else None

        # --- Template params ---
        template_raw = json.loads(qs["template"][0]) if "template" in qs else {}
        params = template_raw.get("params", {})

        dimensions = [d for d in params.get("segmentos", "").split(",") if d]
        metrics = [m for m in params.get("metricas", "").split(",") if m]
        time_breakdown = params.get("segmentarPor", "nao")
        order_sort = params.get("order", "desc")
        order_by = params.get("orderBy") or None

        # --- Merge filters from all three sources ---
        merged = Filters()

        # Source 1: template.params.filtros
        template_filtros = params.get("filtros")
        if template_filtros and isinstance(template_filtros, dict):
            merged = merged.merge(Filters.from_api_dict(template_filtros))

        # Source 2: filtroUsuario (user-applied advanced filters)
        if "filtroUsuario" in qs:
            user_filtros = json.loads(qs["filtroUsuario"][0])
            if user_filtros and isinstance(user_filtros, dict):
                merged = merged.merge(Filters.from_api_dict(user_filtros))

        # Source 3: filtroLocal (combo box quick filters)
        if "filtroLocal" in qs:
            local_filtros = json.loads(qs["filtroLocal"][0])
            if local_filtros and isinstance(local_filtros, dict):
                merged = merged.merge(Filters.from_filtro_local(local_filtros))

        return cls(
            dimensions=dimensions,
            metrics=metrics,
            date_start=date_start,
            date_end=date_end,
            time_breakdown=time_breakdown,
            compare_date_start=compare_start,
            compare_date_end=compare_end,
            order_by=order_by,
            order_sort=order_sort,
            filters=merged,
        )


def resolve_neodash_link(url: str) -> tuple[str, str]:
    """Resolve a NeoDash link (full or short) to ``(slug, full_url)``.

    - ``neod.ai`` short links are resolved by following the 301 redirect.
    - Full ``{slug}.neodash.ai/explorador/...`` URLs are returned as-is.
    - Non-explorer links raise ``ValueError``.

    Returns
    -------
    tuple[str, str]
        ``(slug, full_url)`` where slug is the NeoDash instance identifier.
    """
    resolved_url = url

    # Follow redirect for neod.ai short links
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in ("neod.ai", "www.neod.ai"):

        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(
                self, req, fp, code, msg, headers, newurl
            ):
                raise urllib.error.HTTPError(req, code, msg, headers, fp)

        opener = urllib.request.build_opener(_NoRedirect)
        req = urllib.request.Request(url, method="GET")  # noqa: S310
        req.add_header("User-Agent", "NeoPilot/1.0")

        try:
            opener.open(req, timeout=10)
        except urllib.error.HTTPError as e:
            location = e.headers.get("Location", "")
            if location:
                resolved_url = location
            else:
                raise ValueError(
                    f"Short link {url} did not return a redirect."
                ) from e

        parsed = urllib.parse.urlparse(resolved_url)

    # Validate it's an explorer link
    if "/explorador/" not in parsed.path:
        raise ValueError(
            "This link is not an Explorer link. "
            "NeoPilot can only fetch data from Explorer links "
            "(URLs containing /explorador/)."
        )

    # Extract slug from {slug}.neodash.ai
    host = parsed.netloc
    if ".neodash.ai" not in host:
        raise ValueError(
            f"Unrecognized NeoDash host: {host}. "
            "Expected {slug}.neodash.ai format."
        )
    slug = host.split(".neodash.ai")[0]

    return slug, resolved_url


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
