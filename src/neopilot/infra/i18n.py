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
        # Try requested language, then default, then any non-None value
        val = label_data.get(language) or label_data.get(DEFAULT_LANGUAGE)
        if val:
            return str(val)
        for v in label_data.values():
            if v:
                return str(v)
        return ""
    if label_data is None:
        return ""
    return str(label_data)
