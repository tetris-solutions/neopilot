"""NeoDash API client layer."""

from neopilot.api.auth import detect_language, verify_connection
from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.api.errors import (
    FilterNotReadyError,
    InstanceNotFoundError,
    NeoDashAPIError,
    NeoDashAuthError,
    NeoPilotError,
)

__all__ = [
    "FilterNotReadyError",
    "InstanceNotFoundError",
    "NeoDashAPIError",
    "NeoDashAuthError",
    "NeoDashClient",
    "NeoDashEndpoints",
    "NeoPilotError",
    "detect_language",
    "verify_connection",
]
