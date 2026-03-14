"""Integration tests that hit the real NeoDash API.

These tests validate that our Pydantic models can parse actual API responses
without validation errors. They catch field-type mismatches (like multilingual
dicts, unexpected enum values) that mock fixtures miss.

Run with:
    NEODASH_TEST_SLUG=yourslug NEODASH_TEST_TOKEN=yourtoken python3 -m pytest tests/test_integration.py -v

Set these env vars to enable:
    NEODASH_TEST_SLUG   — instance slug (e.g., "loreal")
    NEODASH_TEST_TOKEN  — API token for that instance
"""

from __future__ import annotations

import os

import pytest

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.models.explorer import ExplorerQuery

_SLUG = os.environ.get("NEODASH_TEST_SLUG", "")
_TOKEN = os.environ.get("NEODASH_TEST_TOKEN", "")

skip_no_creds = pytest.mark.skipif(
    not _SLUG or not _TOKEN,
    reason="NEODASH_TEST_SLUG and NEODASH_TEST_TOKEN env vars required",
)


@pytest.fixture()
def endpoints() -> NeoDashEndpoints:
    client = NeoDashClient(_SLUG, _TOKEN)
    return NeoDashEndpoints(client)


@skip_no_creds
class TestMetricsParsing:
    """Validate that /ai/metrics responses parse without errors."""

    def test_all_metrics_parse(self, endpoints: NeoDashEndpoints) -> None:
        metrics = endpoints.get_metrics()
        assert len(metrics) > 0, "Expected at least one metric"

        for m in metrics:
            # Every metric must have an id and a resolved label
            assert m.id, f"Metric missing id: {m}"
            assert m.label, f"Metric {m.id} has no label"

            # format should be a known value (log unexpected ones)
            assert isinstance(m.format, str), f"Metric {m.id} format is not a string"

            # target should be a known value if present
            if m.target is not None:
                assert isinstance(m.target, str), f"Metric {m.id} target is not a string"

            # description and group must be strings (not dicts) after parsing
            if m.description is not None:
                assert isinstance(m.description, str), (
                    f"Metric {m.id} description is {type(m.description)}, expected str"
                )
            if m.group is not None:
                assert isinstance(m.group, str), (
                    f"Metric {m.id} group is {type(m.group)}, expected str"
                )

    def test_resolve_labels(self, endpoints: NeoDashEndpoints) -> None:
        metrics = endpoints.get_metrics()
        for m in metrics:
            label_pt = m.resolve_label("pt-BR")
            label_en = m.resolve_label("en-US")
            assert isinstance(label_pt, str) and label_pt
            assert isinstance(label_en, str) and label_en


@skip_no_creds
class TestDimensionsParsing:
    """Validate that /ai/dimensions responses parse without errors."""

    def test_all_dimensions_parse(self, endpoints: NeoDashEndpoints) -> None:
        dimensions = endpoints.get_dimensions()
        assert len(dimensions) > 0, "Expected at least one dimension"

        for d in dimensions:
            assert d.id, f"Dimension missing id: {d}"
            assert d.label, f"Dimension {d.id} has no label"

            if d.description is not None:
                assert isinstance(d.description, str), (
                    f"Dimension {d.id} description is {type(d.description)}, expected str"
                )
            if d.group is not None:
                assert isinstance(d.group, str), (
                    f"Dimension {d.id} group is {type(d.group)}, expected str"
                )

    def test_resolve_labels(self, endpoints: NeoDashEndpoints) -> None:
        dimensions = endpoints.get_dimensions()
        for d in dimensions:
            label_pt = d.resolve_label("pt-BR")
            label_en = d.resolve_label("en-US")
            assert isinstance(label_pt, str), f"Dimension {d.id} pt-BR label is not a string"
            assert isinstance(label_en, str), f"Dimension {d.id} en-US label is not a string"


@skip_no_creds
class TestDashboardsParsing:
    """Validate that /get/resumoDashboard responses parse without errors."""

    def test_list_dashboards(self, endpoints: NeoDashEndpoints) -> None:
        response = endpoints.list_dashboards()
        assert len(response.dashboards) > 0, "Expected at least one dashboard"
        assert response.user_language in ("pt-BR", "en-US", "es-ES")

        for db in response.dashboards:
            assert db.id, f"Dashboard missing id: {db}"
            assert db.name, f"Dashboard {db.id} has no name"

    def test_dashboard_search(self, endpoints: NeoDashEndpoints) -> None:
        response = endpoints.list_dashboards(search="___nonexistent___")
        # Should return empty, not crash
        assert isinstance(response.dashboards, list)


@skip_no_creds
class TestExplorerParsing:
    """Validate that /get/exploradorResults responses parse without errors."""

    def test_basic_query(self, endpoints: NeoDashEndpoints) -> None:
        # Get real metric and dimension IDs first
        metrics = endpoints.get_metrics()
        dimensions = endpoints.get_dimensions()
        assert metrics and dimensions, "Need metrics and dimensions to test explorer"

        # Use first metric and dimension
        query = ExplorerQuery(
            dimensions=[dimensions[0].id],
            metrics=[metrics[0].id],
            date_start="2025-01-01",
            date_end="2025-01-07",
            limit=10,
        )
        result = endpoints.query_explorer(query)

        # Should parse without errors
        assert isinstance(result.results, list)
        assert isinstance(result.totals, dict)
        assert isinstance(result.row_count, int)
        assert isinstance(result.was_truncated, bool)

    def test_query_with_time_breakdown(self, endpoints: NeoDashEndpoints) -> None:
        metrics = endpoints.get_metrics()
        dimensions = endpoints.get_dimensions()

        query = ExplorerQuery(
            dimensions=[dimensions[0].id],
            metrics=[metrics[0].id],
            date_start="2025-01-01",
            date_end="2025-01-07",
            time_breakdown="dia",
            limit=10,
        )
        result = endpoints.query_explorer(query)
        assert isinstance(result.results, list)

    def test_query_multiple_metrics(self, endpoints: NeoDashEndpoints) -> None:
        metrics = endpoints.get_metrics()
        dimensions = endpoints.get_dimensions()

        # Use up to 3 metrics
        metric_ids = [m.id for m in metrics[:3]]
        query = ExplorerQuery(
            dimensions=[dimensions[0].id],
            metrics=metric_ids,
            date_start="2025-01-01",
            date_end="2025-01-07",
            limit=10,
        )
        result = endpoints.query_explorer(query)
        assert isinstance(result.results, list)


@skip_no_creds
class TestComponentsParsing:
    """Validate that /ai/allComponents and /ai/component responses parse."""

    def test_all_components(self, endpoints: NeoDashEndpoints) -> None:
        dashboards = endpoints.list_dashboards()
        assert dashboards.dashboards, "Need at least one dashboard"

        dashboard_id = dashboards.dashboards[0].id
        components = endpoints.get_all_components(dashboard_id)

        # Should parse without errors (may be empty for some dashboards)
        assert isinstance(components, list)
        for c in components:
            assert c.id, f"Component missing id: {c}"

    def test_component_data(self, endpoints: NeoDashEndpoints) -> None:
        dashboards = endpoints.list_dashboards()
        assert dashboards.dashboards, "Need at least one dashboard"

        dashboard_id = dashboards.dashboards[0].id
        components = endpoints.get_all_components(dashboard_id)
        if not components:
            pytest.skip("No components in first dashboard")

        component_id = components[0].id
        result = endpoints.get_component_data(
            dashboard_id=dashboard_id,
            component_id=component_id,
            date_start="2025-01-01",
            date_end="2025-01-07",
        )

        # Should parse without errors
        assert isinstance(result.results, list)
        assert isinstance(result.totals, dict)


@skip_no_creds
class TestAuthParsing:
    """Validate auth-related endpoints."""

    def test_verify_connection(self) -> None:
        from neopilot.api.auth import verify_connection

        result = verify_connection(_SLUG, _TOKEN)
        assert isinstance(result, dict)
        assert result["ok"] is True
        assert result["slug"] == _SLUG

    def test_detect_language(self) -> None:
        from neopilot.api.auth import detect_language

        lang = detect_language(_SLUG, _TOKEN)
        assert lang in ("pt-BR", "en-US", "es-ES")
