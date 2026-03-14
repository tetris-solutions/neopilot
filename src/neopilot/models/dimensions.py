"""Dimension models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, model_validator


class Dimension(BaseModel):
    """A NeoDash dimension definition.

    Attributes
    ----------
    id:
        Internal key used in API calls (e.g., ``campanha``).
    label:
        Display name resolved to the user's language.
    raw_label:
        Original label data (may be a string or multilingual dict).
    description:
        Optional description of the dimension.
    group:
        Optional grouping category.
    """

    id: str
    label: str = ""
    raw_label: Any = None
    description: str | None = None
    group: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def _extract_label(cls, data: Any) -> Any:
        if isinstance(data, dict):
            raw = data.get("label", data.get("raw_label"))
            data["raw_label"] = raw
            if isinstance(raw, dict):
                resolved = raw.get("pt-BR") or raw.get("en-US")
                data["label"] = resolved if resolved else data.get("id", "")
            elif raw is not None:
                data["label"] = str(raw)
            else:
                data["label"] = data.get("id", "")
            # description and group can also be multilingual dicts
            for field in ("description", "group"):
                val = data.get(field)
                if isinstance(val, dict):
                    resolved = val.get("pt-BR") or val.get("en-US")
                    data[field] = resolved if resolved else None
        return data

    def resolve_label(self, language: str = "pt-BR") -> str:
        """Return the label in the requested language."""
        from neopilot.infra.i18n import resolve_label

        return resolve_label(self.raw_label, language) if self.raw_label else self.label
