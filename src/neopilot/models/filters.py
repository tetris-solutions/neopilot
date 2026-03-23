"""Filter models for NeoDash Explorer queries.

Filters allow users to narrow down data by dimension values (segment filters)
and metric thresholds (metric filters).  The JSON structure sent to the
``get/exploradorResults`` endpoint follows a nested format:

.. code-block:: text

    filtros: {
        "segment": {              # dimension filters (optional)
            "filters": [ ... ]    # array of FilterGroup objects
        },
        "metric": {               # metric filters (optional)
            "filters": [ ... ]
        }
    }

Filter groups in the ``filters`` array are combined with **AND** logic.
Within each group, ``expressions`` branches are combined according to the
group's ``groupType`` (``and_group`` or ``or_group``).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Operators by estrutura type
# ---------------------------------------------------------------------------

SEGMENT_OPERATORS = {
    "c", "!c",            # contains / does not contain
    "=", "!=",            # equal / not equal
    "in", "!in",          # is one of / is not one of
    "or", "!or",          # contains one of / does not contain any
    "allc", "!allc",      # contains all / does not contain all
    "vazio", "!vazio",    # is empty / is not empty
}

METRIC_OPERATORS = {
    "=", "!=",            # equal / not equal
    ">", ">=",            # greater than (or equal)
    "<", "<=",            # less than (or equal)
    "between", "!between",  # between / not between
}

DATE_OPERATORS = {
    "=", "!=",
    ">", ">=",
    "<", "<=",
    "between", "!between",
    "vazio", "!vazio",
}

# Operators that accept an array as ``valor``
_LIST_OPERATORS = {"in", "!in", "or", "!or", "allc", "!allc"}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class FilterExpression(BaseModel):
    """A single filter condition.

    Parameters
    ----------
    chave:
        Dimension or metric ID (e.g., ``"campanha_externa_nome"``, ``"cpc"``).
    operador:
        Comparison operator (see ``SEGMENT_OPERATORS``, ``METRIC_OPERATORS``).
    valor:
        Value to compare against.  Can be a string, a number (as string),
        an array of strings (for ``in``/``!in``/``or``/``!or``/``allc``/``!allc``),
        or another metric ID when ``tipo="field"``.
    estrutura:
        Filter type — ``"segmento"`` for dimensions, ``"metrica"`` for metrics,
        ``"date"`` for date dimensions.
    tipo:
        Set to ``"field"`` when comparing a metric against another metric
        (e.g., Spend > Clicks).  Omit or ``None`` for normal value comparisons.
    """

    chave: str
    operador: str
    valor: str | list[str] = ""
    estrutura: Literal["segmento", "metrica", "date"] = "segmento"
    tipo: str | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize to the NeoDash API format."""
        d: dict[str, Any] = {
            "chave": self.chave,
            "connective": "e",            # always "e" (legacy)
            "estrutura": self.estrutura,
            "operador": self.operador,
            "needConvertToString": False,  # always false (legacy)
            "valor": self.valor,
        }
        if self.tipo:
            d["tipo"] = self.tipo
        return d


class FilterGroup(BaseModel):
    """A group of filter expressions with AND or OR logic.

    The ``expressions`` field is a 3-level nested array:

    - **Level 1** (outermost): OR branches — items are OR'd together.
    - **Level 2**: AND conditions within a branch — items are AND'd.
    - **Level 3**: Individual ``FilterExpression`` objects.

    Example (A AND B) OR (C)::

        expressions = [
            [[A], [B]],   # branch 1: A AND B
            [[C]],        # branch 2: C
        ]

    Result: ``(A AND B) OR C``
    """

    group_type: Literal["and_group", "or_group"] = "and_group"
    expressions: list[list[list[FilterExpression]]] = Field(default_factory=list)

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize to the NeoDash API format."""
        return {
            "groupType": self.group_type,
            "expressions": [
                [
                    [expr.to_api_dict() for expr in and_block]
                    for and_block in or_branch
                ]
                for or_branch in self.expressions
            ],
        }


class Filters(BaseModel):
    """Top-level filter container for an Explorer query.

    Contains optional ``segment`` (dimension) and ``metric`` filter lists.
    Groups within each list are combined with AND logic.
    """

    segment: list[FilterGroup] = Field(default_factory=list)
    metric: list[FilterGroup] = Field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True if no filters are defined."""
        return not self.segment and not self.metric

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize to the NeoDash API ``filtros`` format.

        Returns an empty dict when no filters are defined, maintaining
        backward compatibility.
        """
        if self.is_empty():
            return {}

        result: dict[str, Any] = {}
        if self.segment:
            result["segment"] = {
                "filters": [g.to_api_dict() for g in self.segment],
            }
        if self.metric:
            result["metric"] = {
                "filters": [g.to_api_dict() for g in self.metric],
            }
        return result

    def to_summary(self, language: str = "en-US") -> str:
        """Return a human-readable summary of the active filters."""
        parts: list[str] = []
        if self.segment:
            n = sum(
                len(expr)
                for g in self.segment
                for branch in g.expressions
                for expr in branch
            )
            label = "filtro(s) de dimensão" if language == "pt-BR" else "dimension filter(s)"
            parts.append(f"{n} {label}")
        if self.metric:
            n = sum(
                len(expr)
                for g in self.metric
                for branch in g.expressions
                for expr in branch
            )
            label = "filtro(s) de métrica" if language == "pt-BR" else "metric filter(s)"
            parts.append(f"{n} {label}")
        if not parts:
            return "No filters" if language != "pt-BR" else "Sem filtros"
        return ", ".join(parts)
