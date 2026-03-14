"""Authentication helpers for NeoDash."""

from __future__ import annotations

import logging

from neopilot.api.client import NeoDashClient
from neopilot.api.errors import NeoDashAuthError

logger = logging.getLogger(__name__)


def verify_connection(slug: str, api_token: str) -> dict:
    """Test a connection to a NeoDash instance.

    Calls ``/ai/metrics`` as a lightweight connectivity + auth check.

    Parameters
    ----------
    slug:
        Instance slug (e.g., ``loreal``).
    api_token:
        API token to validate.

    Returns
    -------
    dict
        A dict with ``{"ok": True, "slug": ..., "language": ...}`` on success.

    Raises
    ------
    NeoDashAuthError
        If the token is invalid or the instance is unreachable.
    """
    client = NeoDashClient(slug, api_token)
    try:
        data = client.get("/ai/metrics")
    except Exception as exc:
        raise NeoDashAuthError(
            f"Connection test failed for '{slug}': {exc}"
        ) from exc

    if not data:
        raise NeoDashAuthError(f"Empty response from '{slug}'. Check your slug and token.")

    logger.info("Connection test OK for '%s'.", slug)
    return {"ok": True, "slug": slug}


def detect_language(slug: str, api_token: str) -> str:
    """Detect the user's language by calling the dashboard list endpoint.

    Falls back to ``pt-BR`` if detection fails.
    """
    client = NeoDashClient(slug, api_token)
    try:
        data = client.get("/get/resumoDashboard", params={"page": "1", "searchKey": "", "sort": "recent"})
        if isinstance(data, dict):
            user = data.get("user", {})
            if isinstance(user, dict):
                lang = user.get("default_language")
                if lang:
                    logger.info("Detected language '%s' for '%s'.", lang, slug)
                    return str(lang)
    except Exception:
        logger.warning("Could not detect language for '%s', defaulting to pt-BR.", slug)
    return "pt-BR"
