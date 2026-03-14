"""Metric models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class Metric(BaseModel):
    """A NeoDash metric definition.

    Attributes
    ----------
    id:
        Internal key used in API calls (e.g., ``custo_total``).
    label:
        Display name resolved to the user's language.
    raw_label:
        Original label data (may be a string or multilingual dict).
    description:
        Optional description of the metric.
    target:
        ``"up"`` if higher is better, ``"down"`` if lower is better.
    format:
        Display format: ``"currency"``, ``"percent"``, ``"number"``, or ``"duration"``.
    group:
        Optional grouping category.
    formula:
        Optional formula string describing how the metric is calculated.
    related_conversion:
        Optional related conversion metric key.
    """

    id: str
    label: str = ""
    raw_label: Any = None
    description: str | None = None
    target: str | None = None
    format: str = "number"
    group: str | None = None
    formula: str | None = None
    related_conversion: str | None = Field(default=None, alias="relatedConversion")

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
            # Normalize empty format to "number"
            if not data.get("format"):
                data["format"] = "number"
        return data

    def resolve_label(self, language: str = "pt-BR") -> str:
        """Return the label in the requested language."""
        from neopilot.infra.i18n import resolve_label

        return resolve_label(self.raw_label, language) if self.raw_label else self.label
