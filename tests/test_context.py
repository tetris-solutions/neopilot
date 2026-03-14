"""Tests for the context system."""

from __future__ import annotations

from unittest.mock import MagicMock

from neopilot.context.manager import ContextManager
from neopilot.models.dashboards import DashboardListResponse, DashboardSummary
from neopilot.models.dimensions import Dimension
from neopilot.models.metrics import Metric


class TestContextManager:
    def _make_manager(self, tmp_data_dir):
        client = MagicMock()
        client.slug = "testslug"
        return ContextManager(client, data_dir=tmp_data_dir)

    def test_build_full_context(self, tmp_data_dir, metrics_data, dimensions_data, dashboards_data):
        manager = self._make_manager(tmp_data_dir)

        # Mock the endpoints
        mock_endpoints = MagicMock()
        mock_endpoints.get_metrics.return_value = [
            Metric.model_validate(m) for m in metrics_data
        ]
        mock_endpoints.get_dimensions.return_value = [
            Dimension.model_validate(d) for d in dimensions_data
        ]
        mock_endpoints.list_dashboards.return_value = DashboardListResponse(
            dashboards=[
                DashboardSummary(id="1", name="Test Dashboard"),
            ],
            user_language="pt-BR",
        )
        manager._endpoints = mock_endpoints

        ctx = manager.build_full_context()
        assert ctx.global_context is not None
        assert ctx.global_context.metric_count == 7
        assert ctx.global_context.dimension_count == 6
        assert ctx.global_context.dashboard_count == 1
        assert ctx.user_context is not None

    def test_build_context_string(self, tmp_data_dir, metrics_data, dimensions_data):
        manager = self._make_manager(tmp_data_dir)

        mock_endpoints = MagicMock()
        mock_endpoints.get_metrics.return_value = [
            Metric.model_validate(m) for m in metrics_data[:2]
        ]
        mock_endpoints.get_dimensions.return_value = [
            Dimension.model_validate(d) for d in dimensions_data[:2]
        ]
        mock_endpoints.list_dashboards.return_value = DashboardListResponse(
            dashboards=[DashboardSummary(id="1", name="Overview")],
        )
        manager._endpoints = mock_endpoints

        text = manager.build_context_string()
        assert "testslug" in text
        assert "Metrics" in text
        assert "Dimensions" in text

    def test_context_includes_user_preferences(self, tmp_data_dir, metrics_data, dimensions_data):
        from neopilot.storage.local_store import UserContextStore

        # Save some user preferences
        ctx_store = UserContextStore(data_dir=tmp_data_dir)
        ctx_store.update_dashboards("testslug", ["db1"])
        ctx_store.update_metrics("testslug", ["roi"])
        ctx_store.add_note("testslug", "Focus on Amazon")

        manager = self._make_manager(tmp_data_dir)

        mock_endpoints = MagicMock()
        mock_endpoints.get_metrics.return_value = []
        mock_endpoints.get_dimensions.return_value = []
        mock_endpoints.list_dashboards.return_value = DashboardListResponse()
        manager._endpoints = mock_endpoints

        text = manager.build_context_string()
        assert "db1" in text
        assert "roi" in text
        assert "Focus on Amazon" in text
