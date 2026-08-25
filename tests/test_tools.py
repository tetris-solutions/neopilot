"""Tests for MCP tools."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from neopilot.api.errors import FilterNotReadyError
from neopilot.models.instance import InstanceInfo


class TestInstanceTools:
    def test_connect_instance(self, tmp_data_dir, metrics_data, dashboards_data, mock_urlopen):
        with (
            patch("neopilot.tools.instances._store") as mock_store_fn,
            patch("neopilot.tools.instances.verify_connection") as mock_test,
        ):
            from neopilot.tools.instances import connect_instance

            mock_test.return_value = {"ok": True, "slug": "loreal"}
            mock_store = MagicMock()
            mock_store.add_instance.return_value = InstanceInfo(
                slug="loreal", api_token="token", is_active=True,
            )
            mock_store_fn.return_value = mock_store

            result = connect_instance("loreal", "test_token")
            assert "loreal.neodash.ai" in result
            assert "successfully" in result.lower()
            assert "set_language" in result

    def test_list_instances_empty(self, tmp_data_dir):
        with patch("neopilot.tools.instances._store") as mock_store_fn:
            from neopilot.tools.instances import list_instances

            mock_store = MagicMock()
            mock_store.list_instances.return_value = []
            mock_store_fn.return_value = mock_store

            result = list_instances()
            assert "No instances" in result

    def test_list_instances_with_data(self, tmp_data_dir):
        with patch("neopilot.tools.instances._store") as mock_store_fn:
            from neopilot.tools.instances import list_instances

            mock_store = MagicMock()
            mock_store.list_instances.return_value = [
                InstanceInfo(slug="loreal", api_token="tok1", is_active=True),
                InstanceInfo(slug="mdlz", api_token="tok2", is_active=False),
            ]
            mock_store_fn.return_value = mock_store

            result = list_instances()
            assert "loreal" in result
            assert "mdlz" in result
            assert "active" in result.lower()


class TestExplorerTool:
    def test_apply_filter_raises(self):
        from neopilot.tools.explorer import apply_filter

        with pytest.raises(FilterNotReadyError, match="not ready yet"):
            apply_filter()


class TestContextTools:
    def test_setup_user_context_returns_guide(self, tmp_data_dir):
        with patch("neopilot.tools.context_tools.InstanceStore") as mock_cls:
            from neopilot.tools.context_tools import setup_user_context

            mock_store = MagicMock()
            mock_store.get_active.return_value = InstanceInfo(
                slug="loreal", api_token="tok", is_active=True,
            )
            mock_cls.return_value = mock_store

            result = setup_user_context()
            assert "loreal" in result
            assert "list_dashboards" in result
            assert "list_metrics" in result
            assert "add_user_note" in result
