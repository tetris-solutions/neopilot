"""User-level context — stored locally per instance."""

from __future__ import annotations

from neopilot.models.context import UserContext
from neopilot.storage.local_store import UserContextStore


def load_user_context(slug: str, data_dir: str | None = None) -> UserContext:
    """Load user context for a slug, returning defaults if absent."""
    store = UserContextStore(data_dir=data_dir)
    return store.load(slug)


def save_user_context(ctx: UserContext, data_dir: str | None = None) -> None:
    """Save user context to disk."""
    store = UserContextStore(data_dir=data_dir)
    store.save(ctx)
