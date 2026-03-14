"""Custom error hierarchy for NeoPilot."""

from __future__ import annotations


class NeoPilotError(RuntimeError):
    """Base error for all NeoPilot operations."""


class NeoDashAPIError(NeoPilotError):
    """Error communicating with the NeoDash API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class NeoDashAuthError(NeoPilotError):
    """Authentication or authorization failure."""


class InstanceNotFoundError(NeoPilotError):
    """No active instance configured."""


class FilterNotReadyError(NeoPilotError):
    """Filters on demand are not implemented yet."""

    def __init__(self) -> None:
        super().__init__(
            "Custom filters on demand are not ready yet. "
            "This feature is coming in a future update."
        )
