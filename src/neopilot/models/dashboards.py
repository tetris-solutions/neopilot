"""Dashboard and component models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    """A dashboard entry from the list endpoint."""

    id: str
    name: str
    description: str | None = None

    model_config = {"extra": "allow"}


class DashboardListResponse(BaseModel):
    """Response from /get/resumoDashboard."""

    dashboards: list[DashboardSummary] = Field(default_factory=list)
    user_language: str = "pt-BR"
    total_pages: int = 1
    current_page: int = 1

    model_config = {"extra": "allow"}


class ComponentSummary(BaseModel):
    """A component entry from /ai/allComponents."""

    id: str
    title: str = ""
    subtitle: str | None = None
    component: str = ""  # Type: BigNumbers, Chart, ExplorerTable, etc.

    model_config = {"extra": "allow"}


class ComponentResult(BaseModel):
    """Response from /ai/component — actual data for a component."""

    component_data: Any = None
    results: list[dict[str, Any]] = Field(default_factory=list)
    totals: dict[str, Any] = Field(default_factory=dict)
    metrics_used: list[str] = Field(default_factory=list)
    dimensions_used: list[str] = Field(default_factory=list)
    raw_response: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class DatasetInfo(BaseModel):
    """Response from /get/dataset?extended=1."""

    raw: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}
