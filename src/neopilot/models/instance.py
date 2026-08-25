"""Instance connection models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InstanceInfo(BaseModel):
    """A saved NeoDash instance connection."""

    slug: str
    api_token: str
    language: str = "pt-BR"
    language_confirmed: bool = False
    last_connected: str | None = None
    is_active: bool = False

    def base_url(self) -> str:
        """Return the base API URL for this instance."""
        return f"https://{self.slug}.neodash.ai/admin/index.php"


class InstancesFile(BaseModel):
    """Root structure for ~/.neopilot/instances.json."""

    instances: list[InstanceInfo] = Field(default_factory=list)
