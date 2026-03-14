"""Context hierarchy models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """User-level context preferences, stored locally per instance."""

    slug: str
    dashboards_of_interest: list[str] = Field(default_factory=list)
    metrics_of_interest: list[str] = Field(default_factory=list)
    preferred_language: str = "pt-BR"
    notes: list[str] = Field(default_factory=list)
    last_updated: str | None = None


class GlobalContext(BaseModel):
    """Instance-level context assembled from API data."""

    slug: str
    metric_count: int = 0
    dimension_count: int = 0
    dashboard_count: int = 0
    metric_summaries: list[str] = Field(default_factory=list)
    dimension_summaries: list[str] = Field(default_factory=list)
    dashboard_summaries: list[str] = Field(default_factory=list)
    language: str = "pt-BR"


class FullContext(BaseModel):
    """Combined context from all levels for a session."""

    global_context: GlobalContext | None = None
    user_context: UserContext | None = None
    dashboard_context: str | None = None
    component_context: str | None = None
