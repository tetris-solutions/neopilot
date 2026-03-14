"""Tests for endpoint wrappers."""

from __future__ import annotations

from unittest.mock import patch

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints


class TestNeoDashEndpoints:
    def setup_method(self):
        self.client = NeoDashClient("testslug", "test_token")
        self.endpoints = NeoDashEndpoints(self.client)

    def test_get_metrics(self, metrics_data):
        with patch.object(self.client, "get", return_value=metrics_data):
            result = self.endpoints.get_metrics()
            assert len(result) == 7
            assert result[0].id == "custo_total"
            assert result[0].format == "currency"

    def test_get_dimensions(self, dimensions_data):
        with patch.object(self.client, "get", return_value=dimensions_data):
            result = self.endpoints.get_dimensions()
            assert len(result) == 6
            assert result[0].id == "campanha"

    def test_get_all_components(self, all_components_data):
        with patch.object(self.client, "get", return_value=all_components_data):
            result = self.endpoints.get_all_components("3000004")
            assert len(result) == 3
            assert result[0].component == "BigNumbers"

    def test_get_component_data(self, component_data):
        with patch.object(self.client, "get", return_value=component_data):
            result = self.endpoints.get_component_data(
                "3000004", "ChartMetricSegmentDate1712768935121613",
                "2025-01-01", "2025-01-31",
            )
            assert len(result.results) == 3
            assert result.totals["conversoes"] == 465
            assert "veiculo" in result.dimensions_used

    def test_list_dashboards(self, dashboards_data):
        with patch.object(self.client, "get", return_value=dashboards_data):
            result = self.endpoints.list_dashboards()
            assert len(result.dashboards) == 4
            assert result.dashboards[0].name == "Overview Geral"
            assert result.user_language == "pt-BR"

    def test_list_dashboards_with_search(self, dashboards_data):
        with patch.object(self.client, "get", return_value=dashboards_data) as mock:
            self.endpoints.list_dashboards(search="Amazon")
            call_args = mock.call_args
            assert call_args[1]["params"]["searchKey"] == "Amazon"

    def test_query_explorer(self, explorer_data):
        from neopilot.models.explorer import ExplorerQuery

        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total", "impressoes", "cliques", "ctr"],
            date_start="2025-01-01",
            date_end="2025-03-31",
        )

        with patch.object(self.client, "get", return_value=explorer_data):
            result = self.endpoints.query_explorer(query)
            assert result.row_count == 3
            assert result.was_truncated is False
            assert result.totals["custo_total"] == 45500.00

    def test_query_explorer_truncated(self, explorer_data):
        from neopilot.models.explorer import ExplorerQuery

        # Make results exactly equal to limit
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            limit=3,  # Same as number of results in fixture
        )

        with patch.object(self.client, "get", return_value=explorer_data):
            result = self.endpoints.query_explorer(query)
            assert result.was_truncated is True
            assert result.truncation_message is not None
            assert "truncated" in result.truncation_message.lower()

    def test_query_explorer_show_totals_enforced(self):
        from neopilot.models.explorer import ExplorerQuery

        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )

        with patch.object(self.client, "get", return_value={"resultsInit": {}}) as mock:
            self.endpoints.query_explorer(query)
            call_params = mock.call_args[1]["params"]
            assert call_params["showTotals"] == "true"

    def test_get_dataset(self):
        mock_data = {"tables": ["campaigns", "ads"], "updated": "2025-01-01"}
        with patch.object(self.client, "get", return_value=mock_data):
            result = self.endpoints.get_dataset()
            assert result.raw["tables"] == ["campaigns", "ads"]
