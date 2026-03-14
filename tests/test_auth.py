"""Tests for authentication module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from neopilot.api.auth import detect_language, verify_connection
from neopilot.api.errors import NeoDashAuthError


class TestTestConnection:
    def test_success(self, metrics_data, mock_urlopen):
        mock_resp = mock_urlopen(metrics_data)
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp):
            result = verify_connection("testslug", "valid_token")
            assert result["ok"] is True
            assert result["slug"] == "testslug"

    def test_failure_empty_response(self, mock_urlopen):
        mock_resp = mock_urlopen([])
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp):
            with pytest.raises(NeoDashAuthError, match="Empty response"):
                verify_connection("testslug", "bad_token")

    def test_failure_auth_error(self):
        import urllib.error as urlerror
        from unittest.mock import MagicMock

        exc = urlerror.HTTPError(
            url="https://test.neodash.ai/admin/index.php/ai/metrics",
            code=401,
            msg="Unauthorized",
            hdrs=MagicMock(),
            fp=MagicMock(),
        )
        with patch("neopilot.api.client.urlrequest.urlopen", side_effect=exc):
            with pytest.raises(NeoDashAuthError):
                verify_connection("testslug", "bad_token")


class TestDetectLanguage:
    def test_detect_pt_br(self, dashboards_data, mock_urlopen):
        mock_resp = mock_urlopen(dashboards_data)
        with patch("neopilot.api.client.urlrequest.urlopen", return_value=mock_resp):
            lang = detect_language("testslug", "valid_token")
            assert lang == "pt-BR"

    def test_fallback_on_error(self):
        import urllib.error as urlerror

        exc = urlerror.URLError("Network error")
        with patch("neopilot.api.client.urlrequest.urlopen", side_effect=exc):
            lang = detect_language("testslug", "token")
            assert lang == "pt-BR"  # Falls back to default
