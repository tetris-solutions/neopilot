"""Logging configuration."""

from __future__ import annotations

import logging
import os


def configure_logging(default_level: int = logging.INFO) -> None:
    """Configure root logger.

    Respects the ``LOGLEVEL`` environment variable
    (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    level_name = os.environ.get("LOGLEVEL", "").upper()
    level = getattr(logging, level_name, None) if level_name else None
    if not isinstance(level, int):
        level = default_level

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
