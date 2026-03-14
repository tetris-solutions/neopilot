"""Context hierarchy manager — assembles context from all four levels."""

from __future__ import annotations

import logging

from neopilot.api.client import NeoDashClient
from neopilot.api.endpoints import NeoDashEndpoints
from neopilot.context.global_context import build_global_context
from neopilot.context.user_context import load_user_context
from neopilot.models.context import FullContext, GlobalContext, UserContext

logger = logging.getLogger(__name__)


class ContextManager:
    """Assembles context from all four hierarchy levels.

    Levels
    ------
    1. **Global** — instance-wide metrics, dimensions, datasets.
    2. **Dashboard** — fetched on demand for a specific dashboard.
    3. **Component** — fetched on demand for a specific component.
    4. **User** — locally stored personal preferences.
    """

    def __init__(
        self,
        client: NeoDashClient,
        data_dir: str | None = None,
    ) -> None:
        self._endpoints = NeoDashEndpoints(client)
        self._slug = client.slug
        self._data_dir = data_dir

    def build_full_context(self) -> FullContext:
        """Build the full context (global + user) for the active instance."""
        global_ctx = build_global_context(self._endpoints, self._slug)
        user_ctx = load_user_context(self._slug, self._data_dir)
        return FullContext(global_context=global_ctx, user_context=user_ctx)

    def build_context_string(self) -> str:
        """Build a human-readable context string for the LLM."""
        ctx = self.build_full_context()
        parts: list[str] = []

        parts.append(f"# NeoDash Instance: {self._slug}")
        parts.append("")

        if ctx.global_context:
            gc = ctx.global_context
            parts.append("## Available Data")
            parts.append(f"- **Metrics**: {gc.metric_count} available")
            for s in gc.metric_summaries:
                parts.append(f"  - {s}")
            parts.append(f"- **Dimensions**: {gc.dimension_count} available")
            for s in gc.dimension_summaries:
                parts.append(f"  - {s}")
            parts.append(f"- **Dashboards**: {gc.dashboard_count} available")
            for s in gc.dashboard_summaries:
                parts.append(f"  - {s}")
            parts.append("")

        if ctx.user_context:
            uc = ctx.user_context
            if uc.dashboards_of_interest:
                parts.append("## User Preferences")
                parts.append(f"- **Dashboards of interest**: {', '.join(uc.dashboards_of_interest)}")
            if uc.metrics_of_interest:
                parts.append(f"- **Key metrics**: {', '.join(uc.metrics_of_interest)}")
            if uc.notes:
                parts.append("- **Notes**:")
                for note in uc.notes:
                    parts.append(f"  - {note}")
            parts.append("")

        return "\n".join(parts)

    def get_global_context(self) -> GlobalContext:
        """Fetch and return the global context."""
        return build_global_context(self._endpoints, self._slug)

    def get_user_context(self) -> UserContext:
        """Load and return the user context."""
        return load_user_context(self._slug, self._data_dir)
