"""Metric value formatting based on type and locale."""

from __future__ import annotations

import math


def format_metric_value(
    value: float | int | None,
    fmt: str = "number",
    language: str = "pt-BR",
) -> str:
    """Format a metric value for display.

    Parameters
    ----------
    value:
        The numeric value to format.
    fmt:
        One of ``"currency"``, ``"percent"``, ``"number"``, ``"duration"``.
    language:
        ``"pt-BR"`` or ``"en-US"``.
    """
    if value is None:
        return "—"

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return "—"

    if fmt == "percent":
        pct = value * 100 if abs(value) <= 1 else value
        if language == "pt-BR":
            return f"{pct:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{pct:,.2f}%"

    if fmt == "currency":
        if language == "pt-BR":
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"${value:,.2f}"

    if fmt in ("duration", "time"):
        return _format_duration(value)

    if fmt == "float":
        formatted = f"{value:,.2f}"
        if language == "pt-BR":
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted

    # Default: number (also covers "default")
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        formatted = f"{int(value):,}"
    else:
        formatted = f"{value:,.2f}"

    if language == "pt-BR":
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    return formatted


def _format_duration(seconds: float | int) -> str:
    """Format seconds into a human-readable duration."""
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    minutes, secs = divmod(total, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {secs}s"
