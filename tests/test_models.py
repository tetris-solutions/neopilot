"""Tests for Pydantic model parsing."""

from __future__ import annotations

from neopilot.models.dashboards import ComponentResult, ComponentSummary, DashboardSummary
from neopilot.models.dimensions import Dimension
from neopilot.models.explorer import ExplorerQuery, ExplorerResult
from neopilot.models.instance import InstanceInfo
from neopilot.models.metrics import Metric


class TestMetricModel:
    def test_parse_with_multilingual_label(self, metrics_data):
        metric = Metric.model_validate(metrics_data[0])
        assert metric.id == "custo_total"
        assert metric.target == "down"
        assert metric.format == "currency"

    def test_resolve_label_pt_br(self, metrics_data):
        metric = Metric.model_validate(metrics_data[0])
        assert metric.resolve_label("pt-BR") == "Custo Total"

    def test_resolve_label_en_us(self, metrics_data):
        metric = Metric.model_validate(metrics_data[0])
        assert metric.resolve_label("en-US") == "Total Cost"

    def test_parse_all_metrics(self, metrics_data):
        metrics = [Metric.model_validate(m) for m in metrics_data]
        assert len(metrics) == 7
        ids = {m.id for m in metrics}
        assert "custo_total" in ids
        assert "ctr" in ids
        assert "roi" in ids

    def test_metric_with_string_label(self):
        data = {"id": "test", "label": "Simple Label", "format": "number"}
        metric = Metric.model_validate(data)
        assert metric.label == "Simple Label"
        assert metric.resolve_label("en-US") == "Simple Label"

    def test_metric_extra_fields_allowed(self):
        data = {"id": "test", "label": "Test", "unknown_field": 42}
        metric = Metric.model_validate(data)
        assert metric.id == "test"


class TestDimensionModel:
    def test_parse_with_multilingual_label(self, dimensions_data):
        dim = Dimension.model_validate(dimensions_data[0])
        assert dim.id == "campanha"
        assert dim.resolve_label("pt-BR") == "Campanha"
        assert dim.resolve_label("en-US") == "Campaign"

    def test_parse_all_dimensions(self, dimensions_data):
        dims = [Dimension.model_validate(d) for d in dimensions_data]
        assert len(dims) == 6
        ids = {d.id for d in dims}
        assert "campanha" in ids
        assert "veiculo" in ids


class TestDashboardModels:
    def test_dashboard_summary(self):
        data = {"id": "3000001", "name": "Overview", "description": "General view"}
        db = DashboardSummary.model_validate(data)
        assert db.id == "3000001"
        assert db.name == "Overview"

    def test_component_summary(self, all_components_data):
        comp = ComponentSummary.model_validate(all_components_data[0])
        assert comp.id == "BigNumbers1751590872194968"
        assert comp.title == "KPIs Gerais"
        assert comp.component == "BigNumbers"

    def test_component_result(self, component_data):
        result = ComponentResult(
            component_data=component_data.get("componentData"),
            results=component_data["componentData"]["results"],
            totals=component_data["componentData"]["totals"],
            metrics_used=component_data["metrics"],
            dimensions_used=component_data["dimensions"],
            raw_response=component_data,
        )
        assert len(result.results) == 3
        assert result.totals["conversoes"] == 465
        assert "veiculo" in result.dimensions_used


class TestExplorerModels:
    def test_query_to_api_params(self):
        query = ExplorerQuery(
            dimensions=["campanha", "veiculo"],
            metrics=["custo_total", "cliques"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert params["dti"] == "2025-01-01"
        assert params["dtf"] == "2025-01-31"
        assert params["showTotals"] == "true"
        assert params["no-cache"] == "false"
        assert "campanha,veiculo" in params["json"]
        assert "custo_total,cliques" in params["json"]

    def test_query_with_comparison(self):
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

    def test_query_no_comparison_omits_keys(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert "dtic" not in params
        assert "dtfc" not in params

    def test_query_caps_limit(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            limit=100_000,
        )
        params = query.to_api_params()
        assert params["limite"] == "50000"

    def test_explorer_result_truncation(self):
        result = ExplorerResult(
            results=[{"x": i} for i in range(500)],
            totals={"custo_total": 1000},
            row_count=500,
            was_truncated=True,
            truncation_message="Results were truncated at 500 rows.",
        )
        assert result.was_truncated is True
        assert result.truncation_message is not None

    def test_explorer_result_not_truncated(self):
        result = ExplorerResult(
            results=[{"x": 1}],
            totals={"custo_total": 100},
            row_count=1,
            was_truncated=False,
        )
        assert result.was_truncated is False
        assert result.truncation_message is None

    def test_query_time_breakdown(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            time_breakdown="mes",
        )
        params = query.to_api_params()
        assert '"segmentarPor": "mes"' in params["json"]


class TestInstanceModel:
    def test_instance_info(self):
        info = InstanceInfo(
            slug="loreal",
            api_token="test_token",
            language="pt-BR",
            is_active=True,
        )
        assert info.base_url() == "https://loreal.neodash.ai/admin/index.php"

    def test_instance_defaults(self):
        info = InstanceInfo(slug="test", api_token="tok")
        assert info.language == "pt-BR"
        assert info.is_active is False
        assert info.last_connected is None
