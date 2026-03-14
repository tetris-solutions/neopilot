"""Environment loading with thread-safe singleton pattern."""

from __future__ import annotations

import os
import threading

_LOADED = False
_LOCK = threading.Lock()


def load_env(dotenv_path: str | None = None, override: bool = False) -> None:
    """Load .env file once (thread-safe).

    Parameters
    ----------
    dotenv_path:
        Path to .env file. If ``None``, searches from cwd upwards.
    override:
        If ``True``, overwrite existing env vars.
    """
    global _LOADED
    if _LOADED and not override:
        return
    with _LOCK:
        if _LOADED and not override:
            return
        try:
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=dotenv_path, override=override)
        except ImportError:
            pass
        _LOADED = True


def get_data_dir() -> str:
    """Return the NeoPilot data directory, creating it if needed."""
    data_dir = os.environ.get("NEOPILOT_DATA_DIR", os.path.expanduser("~/.neopilot"))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def is_debug() -> bool:
    """Return True if debug mode is enabled via NEOPILOT_DEBUG env var."""
    return os.environ.get("NEOPILOT_DEBUG", "").lower() in ("1", "true", "yes")
