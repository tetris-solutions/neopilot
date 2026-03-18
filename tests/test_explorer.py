"""Tests specifically for the Explorer query and response logic."""

from __future__ import annotations

import json
import urllib.parse

from neopilot.models.explorer import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    ExplorerQuery,
    ExplorerResult,
    _flip_date,
)


class TestExplorerQueryConstruction:
    def test_basic_query(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total", "cliques"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()

        # Verify mandatory fields
        assert params["dti"] == "2025-01-01"
        assert params["dtf"] == "2025-01-31"
        assert params["showTotals"] == "true"
        assert params["no-cache"] == "false"
        assert params["orderSort"] == "desc"
        assert params["limite"] == str(DEFAULT_LIMIT)

        # Verify JSON payload
        json_payload = json.loads(params["json"])
        assert json_payload["segmentos"] == "campanha"
        assert json_payload["metricas"] == "custo_total,cliques"
        assert json_payload["segmentarPor"] == "nao"
        assert json_payload["filtros"] == {}

    def test_multiple_dimensions(self):
        query = ExplorerQuery(
            dimensions=["campanha", "veiculo", "marca"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        assert json_payload["segmentos"] == "campanha,veiculo,marca"

    def test_time_breakdown(self):
        for breakdown in ["dia", "semana", "mes", "trimestre", "ano"]:
            query = ExplorerQuery(
                dimensions=["campanha"],
                metrics=["custo_total"],
                date_start="2025-01-01",
                date_end="2025-12-31",
                time_breakdown=breakdown,
            )
            params = query.to_api_params()
            json_payload = json.loads(params["json"])
            assert json_payload["segmentarPor"] == breakdown

    def test_order_by(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total", "roi"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            order_by="roi",
            order_sort="asc",
        )
        params = query.to_api_params()
        assert params["orderBy"] == "roi"
        assert params["orderSort"] == "asc"

    def test_limit_capping(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            limit=100_000,
        )
        params = query.to_api_params()
        assert params["limite"] == str(MAX_LIMIT)

    def test_show_totals_always_true(self):
        """showTotals must ALWAYS be true — NeoPilot never calculates totals."""
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert params["showTotals"] == "true"

    def test_filters_always_empty(self):
        """Filters are deferred — always empty dict."""
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        assert json_payload["filtros"] == {}

    def test_comparison_dates(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-02-01",
            date_end="2025-02-28",
            compare_date_start="2025-01-01",
            compare_date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert params["dtic"] == "2025-01-01"
        assert params["dtfc"] == "2025-01-31"


class TestExplorerTruncation:
    def test_truncated_when_equal_to_limit(self):
        result = ExplorerResult(
            results=[{"x": i} for i in range(500)],
            totals={"custo_total": 1000},
            row_count=500,
            was_truncated=True,
            truncation_message="Results were truncated at 500 rows.",
        )
        assert result.was_truncated is True
        assert "truncated" in result.truncation_message.lower()

    def test_not_truncated_when_less_than_limit(self):
        result = ExplorerResult(
            results=[{"x": i} for i in range(10)],
            totals={"custo_total": 100},
            row_count=10,
            was_truncated=False,
        )
        assert result.was_truncated is False
        assert result.truncation_message is None

    def test_comparison_results(self):
        result = ExplorerResult(
            results=[{"x": 1}],
            totals={"custo_total": 100},
            comparison_results=[{"x": 2}],
            comparison_totals={"custo_total": 90},
            row_count=1,
            was_truncated=False,
        )
        assert result.comparison_results is not None
        assert len(result.comparison_results) == 1
        assert result.comparison_totals["custo_total"] == 90


class TestFlipDate:
    def test_basic(self):
        assert _flip_date("2026-03-17") == "17-03-2026"

    def test_single_digit(self):
        assert _flip_date("2026-01-05") == "05-01-2026"

    def test_passthrough_on_bad_format(self):
        # Non-3-part strings pass through unchanged
        assert _flip_date("invalid") == "invalid"
        assert _flip_date("2026-03") == "2026-03"


class TestNeoDashLinkBuilder:
    def test_simple_link(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total", "cpa"],
            date_start="2026-03-11",
            date_end="2026-03-17",
        )
        link = query.to_neodash_link("tpv")

        assert link.startswith("https://tpv.neodash.ai/explorador/100?")
        assert "dti=11-03-2026" in link
        assert "dtf=17-03-2026" in link
        assert "template=" in link

        # Parse the template param (URL-encoded)
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        template = json.loads(template_str)
        params = template["params"]

        assert params["segmentos"] == "canal"
        assert params["metricas"] == "custo_total,cpa"
        assert params["segmentarPor"] == "nao"
        assert params["order"] == "desc"
        assert params["filtros"] == {}
        assert params["openGraphExplorador"] == 0
        assert params["totalPercent"] == 1
        assert params["showMetricsTotal"] == 1

    def test_link_with_time_breakdown(self):
        query = ExplorerQuery(
            dimensions=["veiculo"],
            metrics=["custo_total"],
            date_start="2026-03-01",
            date_end="2026-03-17",
            time_breakdown="dia",
            order_sort="asc",
        )
        link = query.to_neodash_link("tpv")
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        params = json.loads(template_str)["params"]

        assert params["segmentarPor"] == "dia"
        assert params["order"] == "asc"

    def test_link_with_comparison_dates(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total"],
            date_start="2026-03-11",
            date_end="2026-03-17",
            compare_date_start="2026-03-04",
            compare_date_end="2026-03-10",
        )
        link = query.to_neodash_link("tpv")

        assert "dtic=04-03-2026" in link
        assert "dtfc=10-03-2026" in link

    def test_link_with_order_by(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total", "cpa"],
            date_start="2026-03-11",
            date_end="2026-03-17",
            order_by="custo_total",
        )
        link = query.to_neodash_link("tpv")
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        params = json.loads(template_str)["params"]

        assert params["orderBy"] == "custo_total"
