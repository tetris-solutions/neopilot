"""Internationalization helpers for label resolution."""

from __future__ import annotations

from typing import Any

SUPPORTED_LANGUAGES = ("pt-BR", "en-US")
DEFAULT_LANGUAGE = "pt-BR"


def resolve_label(label_data: Any, language: str = DEFAULT_LANGUAGE) -> str:
    """Resolve a label that may be a plain string or a dict with language keys.

    Parameters
    ----------
    label_data:
        A string or a dict like ``{"pt-BR": "Custo", "en-US": "Cost"}``.
    language:
        The preferred language code (``pt-BR`` or ``en-US``).

    Returns
    -------
    str
        The resolved label string.
    """
    if isinstance(label_data, str):
        return label_data
    if isinstance(label_data, dict):
        if language in label_data:
            return str(label_data[language])
        if DEFAULT_LANGUAGE in label_data:
            return str(label_data[DEFAULT_LANGUAGE])
        values = list(label_data.values())
        return str(values[0]) if values else ""
    return str(label_data)
