"""Version management and update checking.

NeoPilot supports two update modes:
- **Optional**: A notice is appended to tool responses when a newer version exists.
- **Forced**: Tools refuse to run if the local version is below the minimum required.

The required minimum version is fetched from a remote JSON file that you control.
Update the remote file to push version requirements to all users.
"""

from __future__ import annotations

import json
import logging
import urllib.error as urlerror
import urllib.request as urlrequest
from functools import lru_cache
from typing import Any

from neopilot import __version__

logger = logging.getLogger(__name__)

# Remote JSON file containing version info.
# Host this on your own infrastructure or a GitHub raw URL.
# Expected format:
# {
#   "latest": "0.2.0",
#   "minimum": "0.1.0",
#   "update_url": "https://github.com/your-org/neopilot",
#   "message": "Optional custom update message"
# }
_VERSION_CHECK_URL = (
    "https://raw.githubusercontent.com/neoperformance/neopilot/main/version.json"
)

_CHECK_TIMEOUT = 5  # seconds — fail fast, never block the user


def current_version() -> str:
    """Return the currently installed NeoPilot version."""
    return __version__


def parse_version(v: str) -> tuple[int, ...]:
    """Parse a semver string like '0.2.1' into a comparable tuple."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


@lru_cache(maxsize=1)
def _fetch_remote_version() -> dict[str, Any]:
    """Fetch the remote version.json (cached for the server's lifetime).

    Returns an empty dict on any failure — version checking should never
    break the tool.
    """
    try:
        req = urlrequest.Request(  # noqa: S310
            _VERSION_CHECK_URL,
            method="GET",
            headers={"Accept": "application/json"},
        )
        with urlrequest.urlopen(req, timeout=_CHECK_TIMEOUT) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except (urlerror.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.debug("Version check failed (non-fatal): %s", exc)
        return {}


def check_update() -> dict[str, Any]:
    """Check if a newer version of NeoPilot is available.

    Returns
    -------
    dict with keys:
        - ``update_available``: bool
        - ``force_update``: bool — True if current version is below minimum
        - ``current``: str — current version
        - ``latest``: str — latest version (or current if unknown)
        - ``minimum``: str — minimum required version (or "0.0.0" if unknown)
        - ``update_url``: str — where to get the update
        - ``message``: str | None — custom message from the server
    """
    remote = _fetch_remote_version()

    latest = remote.get("latest", __version__)
    minimum = remote.get("minimum", "0.0.0")
    update_url = remote.get("update_url", "")
    message = remote.get("message")

    current = parse_version(__version__)
    latest_parsed = parse_version(latest)
    minimum_parsed = parse_version(minimum)

    return {
        "update_available": current < latest_parsed,
        "force_update": current < minimum_parsed,
        "current": __version__,
        "latest": latest,
        "minimum": minimum,
        "update_url": update_url,
        "message": message,
    }


def update_notice() -> str | None:
    """Return a user-facing update notice, or None if up to date.

    - If a forced update is needed, returns a blocking message.
    - If an optional update is available, returns a gentle notice.
    - If up to date or check fails, returns None.
    """
    info = check_update()

    if info["force_update"]:
        url_line = f"\n  Update: {info['update_url']}" if info["update_url"] else ""
        msg = info["message"] or ""
        extra = f"\n  {msg}" if msg else ""
        return (
            f"\n⛔ **NeoPilot update required.** "
            f"Your version ({info['current']}) is below the minimum ({info['minimum']}). "
            f"Please update to continue using NeoPilot.{url_line}{extra}"
        )

    if info["update_available"]:
        url_line = f"\n  Update: {info['update_url']}" if info["update_url"] else ""
        msg = info["message"] or ""
        extra = f"\n  {msg}" if msg else ""
        return (
            f"\n💡 **NeoPilot update available:** "
            f"v{info['current']} → v{info['latest']}{url_line}{extra}"
        )

    return None


def enforce_version() -> str | None:
    """If the current version is below the required minimum, return an error message.

    Tools should call this at the start and return the message immediately
    if it is not None, blocking execution.

    Returns None if the version is acceptable.
    """
    info = check_update()
    if info["force_update"]:
        url_line = f"\nUpdate here: {info['update_url']}" if info["update_url"] else ""
        msg = info["message"] or ""
        extra = f"\n{msg}" if msg else ""
        return (
            f"⛔ **NeoPilot v{info['current']} is no longer supported.**\n"
            f"Minimum required version: v{info['minimum']}\n"
            f"Please update NeoPilot to continue.{url_line}{extra}"
        )
    return None
