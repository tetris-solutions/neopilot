"""Shared fixtures for NeoPilot tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Disable any external tracing during tests
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ.pop("LANGSMITH_API_KEY", None)
os.environ.pop("LANGSMITH_BASE_URL", None)

# Load .env.test for integration test credentials (if it exists).
# This keeps test credentials separate from the MCP runtime .env.
_ENV_TEST = Path(__file__).parent.parent / ".env.test"
if _ENV_TEST.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(_ENV_TEST, override=False)
    except ImportError:
        # python-dotenv is optional; fall back to manual parsing
        with open(_ENV_TEST) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict | list:
    """Load a JSON fixture file."""
    path = FIXTURES_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> str:
    """Return a temporary data directory for instance/context storage."""
    data_dir = str(tmp_path / "neopilot_test")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


@pytest.fixture()
def metrics_data() -> list:
    """Load metrics fixture data."""
    return load_fixture("metrics_response.json")


@pytest.fixture()
def dimensions_data() -> list:
    """Load dimensions fixture data."""
    return load_fixture("dimensions_response.json")


@pytest.fixture()
def dashboards_data() -> dict:
    """Load dashboards fixture data."""
    return load_fixture("dashboards_response.json")


@pytest.fixture()
def explorer_data() -> dict:
    """Load explorer fixture data."""
    return load_fixture("explorer_response.json")


@pytest.fixture()
def component_data() -> dict:
    """Load component fixture data."""
    return load_fixture("component_response.json")


@pytest.fixture()
def all_components_data() -> list:
    """Load all components fixture data."""
    return load_fixture("all_components_response.json")


@pytest.fixture()
def mock_urlopen():
    """Create a mock for urllib.request.urlopen."""

    def _make_mock(response_data: dict | list, status: int = 200):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_response.headers.get_content_charset.return_value = "utf-8"
        mock_response.status = status
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    return _make_mock
