"""Tests for the HTTP client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from neopilot.api.client import NeoDashClient
from neopilot.api.errors import NeoDashAPIError, NeoDashAuthError


class TestNeoDashClient:
    def setup_method(self):
        self.client = NeoDashClient("testslug", "test_token_123")

    def test_base_url(self):
        assert self.client.base_url == "https://testslug.neodash.ai/admin/index.php"

    def test_get_builds_url_with_token(self, mock_urlopen):
        mock_resp = mock_urlopen({"status": "ok"})
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp) as mock:
            self.client.get("/ai/metrics")
            call_args = mock.call_args
            request = call_args[0][0]
            assert "api_token=test_token_123" in request.full_url
            assert "/ai/metrics" in request.full_url

    def test_get_includes_extra_params(self, mock_urlopen):
        mock_resp = mock_urlopen({"data": []})
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp) as mock:
            self.client.get("/get/resumoDashboard", params={"page": "1", "searchKey": "test"})
            request = mock.call_args[0][0]
            assert "page=1" in request.full_url
            assert "searchKey=test" in request.full_url

    def test_get_returns_parsed_json(self, mock_urlopen):
        expected = [{"id": "custo_total", "label": "Cost"}]
        mock_resp = mock_urlopen(expected)
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp):
            result = self.client.get("/ai/metrics")
            assert result == expected

    def test_auth_error_on_401(self):
        import urllib.error as urlerror

        exc = urlerror.HTTPError(
            url="https://test.neodash.ai/admin/index.php/ai/metrics",
            code=401,
            msg="Unauthorized",
            hdrs=MagicMock(),
            fp=MagicMock(),
        )
        with patch("neopilot.api.client.urlrequest.urlopen", side_effect=exc):
            with pytest.raises(NeoDashAuthError, match="Authentication failed"):
                self.client.get("/ai/metrics")

    def test_api_error_on_500(self):
        import urllib.error as urlerror

        exc = urlerror.HTTPError(
            url="https://test.neodash.ai/admin/index.php/ai/metrics",
            code=500,
            msg="Server Error",
            hdrs=MagicMock(),
            fp=MagicMock(),
        )
        with patch("neopilot.api.client.urlrequest.urlopen", side_effect=exc):
            with pytest.raises(NeoDashAPIError, match="HTTP 500"):
                self.client.get("/ai/metrics")

    def test_api_error_on_network_failure(self):
        import urllib.error as urlerror

        exc = urlerror.URLError("Connection refused")
        with patch("neopilot.api.client.urlrequest.urlopen", side_effect=exc):
            with pytest.raises(NeoDashAPIError, match="Cannot reach"):
                self.client.get("/ai/metrics")

    def test_api_error_on_invalid_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json"
        mock_resp.headers.get_content_charset.return_value = "utf-8"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp):
            with pytest.raises(NeoDashAPIError, match="Invalid JSON"):
                self.client.get("/ai/metrics")
