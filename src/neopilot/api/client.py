"""HTTP client for the NeoDash API using stdlib urllib."""

from __future__ import annotations

import json
import logging
import urllib.error as urlerror
import urllib.parse as urlparse
import urllib.request as urlrequest
from typing import Any

from neopilot.api.errors import NeoDashAPIError, NeoDashAuthError

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds

_HEADERS = {
    "Accept": "application/json; charset=UTF-8",
    "Accept-Language": "pt-BR,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
}


class NeoDashClient:
    """HTTP client for a single NeoDash instance.

    Parameters
    ----------
    slug:
        Instance identifier (e.g., ``loreal``).
    api_token:
        Authentication token for the instance.
    timeout:
        Request timeout in seconds.
    """

    def __init__(self, slug: str, api_token: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        self.slug = slug
        self.api_token = api_token
        self.base_url = f"https://{slug}.neodash.ai/admin/index.php"
        self.timeout = timeout
        self.last_url: str | None = None
        self.last_raw_response: str | None = None

    def get(self, path: str, params: dict[str, str] | None = None) -> Any:
        """Make an authenticated GET request.

        Parameters
        ----------
        path:
            API path appended to base_url (e.g., ``/ai/metrics``).
        params:
            Extra query parameters (``api_token`` is added automatically).

        Returns
        -------
        Any
            Parsed JSON response.
        """
        all_params = {"api_token": self.api_token}
        if params:
            all_params.update(params)

        url = f"{self.base_url}{path}"
        if all_params:
            url = f"{url}?{urlparse.urlencode(all_params, quote_via=urlparse.quote)}"

        self.last_url = url.replace(self.api_token, "***")
        logger.debug("GET %s", self.last_url)

        req = urlrequest.Request(url, method="GET", headers=_HEADERS)  # noqa: S310
        return self._execute(req)

    def _execute(self, req: urlrequest.Request) -> Any:
        """Execute a request and return parsed JSON."""
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                charset = resp.headers.get_content_charset() or "utf-8"
                body = resp.read().decode(charset)
                self.last_raw_response = body
        except urlerror.HTTPError as exc:
            if exc.code in (401, 403):
                raise NeoDashAuthError(
                    f"Authentication failed for instance '{self.slug}' "
                    f"(HTTP {exc.code}). Check your API token."
                ) from exc
            raise NeoDashAPIError(
                f"NeoDash API error: HTTP {exc.code} on {req.full_url}",
                status_code=exc.code,
            ) from exc
        except urlerror.URLError as exc:
            raise NeoDashAPIError(
                f"Cannot reach NeoDash instance '{self.slug}': {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise NeoDashAPIError(
                f"Request to '{self.slug}' timed out after {self.timeout}s."
            ) from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise NeoDashAPIError(
                f"Invalid JSON response from '{self.slug}': {exc}"
            ) from exc
