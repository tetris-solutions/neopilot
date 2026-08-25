"""Tests for the filter models and their integration with ExplorerQuery."""

from __future__ import annotations

import json

from neopilot.models.explorer import ExplorerQuery
from neopilot.models.filters import (
    FilterExpression,
    FilterGroup,
    Filters,
)

# ---------------------------------------------------------------------------
# FilterExpression
# ---------------------------------------------------------------------------


class TestFilterExpression:
    def test_simple_segment_equals(self):
        expr = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        d = expr.to_api_dict()
        assert d["chave"] == "slug_dimensao"
        assert d["connective"] == "e"
        assert d["estrutura"] == "segmento"
        assert d["operador"] == "="
        assert d["needConvertToString"] is False
        assert d["valor"] == "AOC"
        assert "tipo" not in d

    def test_metric_with_field_comparison(self):
        expr = FilterExpression(
            chave="custo_total",
            operador=">",
            valor="cliques",
            estrutura="metrica",
            tipo="field",
        )
        d = expr.to_api_dict()
        assert d["estrutura"] == "metrica"
        assert d["operador"] == ">"
        assert d["valor"] == "cliques"
        assert d["tipo"] == "field"

    def test_in_operator_with_list_value(self):
        expr = FilterExpression(
            chave="veiculo",
            operador="in",
            valor=["AMAZON DSP", "AMAZON PRODUCTS"],
        )
        d = expr.to_api_dict()
        assert d["valor"] == ["AMAZON DSP", "AMAZON PRODUCTS"]

    def test_contains_operator(self):
        expr = FilterExpression(
            chave="campanha_externa_nome", operador="c", valor="amz"
        )
        d = expr.to_api_dict()
        assert d["operador"] == "c"
        assert d["valor"] == "amz"

    def test_not_contains_operator(self):
        expr = FilterExpression(
            chave="campanha_externa_nome", operador="!c", valor="display"
        )
        d = expr.to_api_dict()
        assert d["operador"] == "!c"


# ---------------------------------------------------------------------------
# FilterGroup
# ---------------------------------------------------------------------------


class TestFilterGroup:
    def test_and_group_single_expression(self):
        expr = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        group = FilterGroup(
            group_type="and_group",
            expressions=[[[expr]]],
        )
        d = group.to_api_dict()
        assert d["groupType"] == "and_group"
        assert len(d["expressions"]) == 1
        assert len(d["expressions"][0]) == 1
        assert d["expressions"][0][0][0]["chave"] == "slug_dimensao"

    def test_or_group_two_branches(self):
        expr_a = FilterExpression(
            chave="campanha_externa_nome", operador="c", valor="conv_sp"
        )
        expr_b = FilterExpression(
            chave="campanha_externa_nome", operador="c", valor="conv_perf"
        )
        group = FilterGroup(
            group_type="or_group",
            expressions=[
                [[expr_a]],  # OR branch 1
                [[expr_b]],  # OR branch 2
            ],
        )
        d = group.to_api_dict()
        assert d["groupType"] == "or_group"
        assert len(d["expressions"]) == 2

    def test_and_group_multiple_conditions(self):
        """Multiple AND conditions in the same branch."""
        expr_a = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        expr_b = FilterExpression(
            chave="veiculo", operador="=", valor="KABUM"
        )
        group = FilterGroup(
            group_type="and_group",
            expressions=[
                [[expr_a], [expr_b]],  # A AND B in same branch
            ],
        )
        d = group.to_api_dict()
        assert len(d["expressions"]) == 1
        assert len(d["expressions"][0]) == 2  # Two AND conditions


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


class TestFilters:
    def test_empty_filters(self):
        f = Filters()
        assert f.is_empty()
        assert f.to_api_dict() == {}

    def test_segment_only(self):
        expr = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        group = FilterGroup(
            group_type="and_group", expressions=[[[expr]]]
        )
        f = Filters(segment=[group])
        assert not f.is_empty()
        d = f.to_api_dict()
        assert "segment" in d
        assert "metric" not in d
        assert len(d["segment"]["filters"]) == 1

    def test_metric_only(self):
        expr = FilterExpression(
            chave="cpc", operador=">", valor="3", estrutura="metrica"
        )
        group = FilterGroup(
            group_type="and_group", expressions=[[[expr]]]
        )
        f = Filters(metric=[group])
        d = f.to_api_dict()
        assert "metric" in d
        assert "segment" not in d

    def test_segment_and_metric_combined(self):
        seg_expr = FilterExpression(
            chave="campanha_externa_nome", operador="c", valor="philips"
        )
        met_expr = FilterExpression(
            chave="cpc", operador="<", valor="2", estrutura="metrica"
        )
        f = Filters(
            segment=[FilterGroup(group_type="and_group", expressions=[[[seg_expr]]])],
            metric=[FilterGroup(group_type="and_group", expressions=[[[met_expr]]])],
        )
        d = f.to_api_dict()
        assert "segment" in d
        assert "metric" in d

    def test_multiple_groups_and_between(self):
        """Two segment groups are AND'd together."""
        g1 = FilterGroup(
            group_type="and_group",
            expressions=[[[
                FilterExpression(chave="slug_dimensao", operador="=", valor="Philips")
            ]]],
        )
        g2 = FilterGroup(
            group_type="and_group",
            expressions=[[[
                FilterExpression(
                    chave="veiculo",
                    operador="in",
                    valor=["AMAZON DSP", "AMAZON PRODUCTS"],
                )
            ]]],
        )
        f = Filters(segment=[g1, g2])
        d = f.to_api_dict()
        assert len(d["segment"]["filters"]) == 2

    def test_summary_en(self):
        expr = FilterExpression(chave="slug_dimensao", operador="=", valor="AOC")
        f = Filters(
            segment=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        summary = f.to_summary("en-US")
        assert "1 dimension filter(s)" in summary

    def test_summary_pt(self):
        expr = FilterExpression(chave="cpc", operador=">", valor="3", estrutura="metrica")
        f = Filters(
            metric=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        summary = f.to_summary("pt-BR")
        assert "filtro(s) de métrica" in summary

    def test_summary_empty(self):
        f = Filters()
        assert f.to_summary("en-US") == "No filters"
        assert f.to_summary("pt-BR") == "Sem filtros"


# ---------------------------------------------------------------------------
# ExplorerQuery integration with filters
# ---------------------------------------------------------------------------


class TestExplorerQueryWithFilters:
    def test_default_filters_empty(self):
        """Without filters, filtros is still an empty dict (backward compat)."""
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        assert json_payload["filtros"] == {}

    def test_segment_filter_in_api_params(self):
        expr = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        filters = Filters(
            segment=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        query = ExplorerQuery(
            dimensions=["campanha_externa_nome"],
            metrics=["custo_total"],
            date_start="2026-03-16",
            date_end="2026-03-22",
            filters=filters,
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        filtros = json_payload["filtros"]
        assert "segment" in filtros
        assert filtros["segment"]["filters"][0]["groupType"] == "and_group"
        assert filtros["segment"]["filters"][0]["expressions"][0][0][0]["chave"] == "slug_dimensao"
        assert filtros["segment"]["filters"][0]["expressions"][0][0][0]["valor"] == "AOC"

    def test_metric_filter_in_api_params(self):
        expr = FilterExpression(
            chave="cpc", operador=">", valor="3", estrutura="metrica"
        )
        filters = Filters(
            metric=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        query = ExplorerQuery(
            dimensions=["campanha_externa_nome"],
            metrics=["custo_total", "cpc"],
            date_start="2026-03-16",
            date_end="2026-03-22",
            filters=filters,
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        filtros = json_payload["filtros"]
        assert "metric" in filtros
        assert filtros["metric"]["filters"][0]["expressions"][0][0][0]["chave"] == "cpc"
        assert filtros["metric"]["filters"][0]["expressions"][0][0][0]["operador"] == ">"

    def test_filters_in_neodash_link(self):
        expr = FilterExpression(
            chave="slug_dimensao", operador="=", valor="AOC"
        )
        filters = Filters(
            segment=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        query = ExplorerQuery(
            dimensions=["campanha_externa_nome"],
            metrics=["custo_total"],
            date_start="2026-03-16",
            date_end="2026-03-22",
            filters=filters,
        )
        link = query.to_neodash_link("tpv")
        assert "slug_dimensao" in link
        assert "AOC" in link

    def test_complex_or_segment_plus_metric(self):
        """Example 10-style: OR segment + metric with field comparison."""
        seg_group = FilterGroup(
            group_type="or_group",
            expressions=[
                [[FilterExpression(chave="campanha_externa_nome", operador="c", valor="meli")]],
                [[FilterExpression(chave="campanha_externa_nome", operador="c", valor="amz")]],
            ],
        )
        met_group = FilterGroup(
            group_type="and_group",
            expressions=[
                [[FilterExpression(
                    chave="custo_total", operador=">", valor="cliques",
                    estrutura="metrica", tipo="field",
                )]],
                [[FilterExpression(
                    chave="cpc", operador="<", valor="5",
                    estrutura="metrica",
                )]],
            ],
        )
        filters = Filters(segment=[seg_group], metric=[met_group])
        query = ExplorerQuery(
            dimensions=["campanha_externa_nome"],
            metrics=["custo_total", "cliques", "cpc"],
            date_start="2026-03-16",
            date_end="2026-03-22",
            time_breakdown="dia",
            filters=filters,
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        filtros = json_payload["filtros"]

        # Segment: OR group with 2 branches
        seg = filtros["segment"]["filters"][0]
        assert seg["groupType"] == "or_group"
        assert len(seg["expressions"]) == 2

        # Metric: AND group with 2 branches
        met = filtros["metric"]["filters"][0]
        assert met["groupType"] == "and_group"
        assert len(met["expressions"]) == 2
        # First metric expression has tipo=field
        assert met["expressions"][0][0][0]["tipo"] == "field"
        assert met["expressions"][0][0][0]["valor"] == "cliques"


# ---------------------------------------------------------------------------
# _parse_filters helper (imported from explorer tool)
# ---------------------------------------------------------------------------


class TestParseFilters:
    def test_parse_single_segment(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(
            segment_filters=[
                {"dimension": "slug_dimensao", "operator": "=", "value": "AOC"}
            ],
            metric_filters=None,
        )
        assert not result.is_empty()
        assert len(result.segment) == 1
        d = result.to_api_dict()
        assert d["segment"]["filters"][0]["expressions"][0][0][0]["chave"] == "slug_dimensao"

    def test_parse_metric_filter(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(
            segment_filters=None,
            metric_filters=[
                {"metric": "cpc", "operator": ">", "value": "3"}
            ],
        )
        assert len(result.metric) == 1
        d = result.to_api_dict()
        assert d["metric"]["filters"][0]["expressions"][0][0][0]["estrutura"] == "metrica"

    def test_parse_field_comparison(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(
            segment_filters=None,
            metric_filters=[
                {"metric": "custo_total", "operator": ">", "value": "cliques", "field_comparison": True}
            ],
        )
        d = result.to_api_dict()
        assert d["metric"]["filters"][0]["expressions"][0][0][0]["tipo"] == "field"

    def test_parse_or_segment_filters(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(
            segment_filters=[
                {"dimension": "campanha_externa_nome", "operator": "c", "value": "meli", "group": "or"},
                {"dimension": "campanha_externa_nome", "operator": "c", "value": "amz", "group": "or"},
            ],
            metric_filters=None,
        )
        assert len(result.segment) == 1
        assert result.segment[0].group_type == "or_group"
        assert len(result.segment[0].expressions) == 2

    def test_parse_combined(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(
            segment_filters=[
                {"dimension": "campanha_externa_nome", "operator": "c", "value": "philips"}
            ],
            metric_filters=[
                {"metric": "cpc", "operator": "<", "value": "2"}
            ],
        )
        assert len(result.segment) == 1
        assert len(result.metric) == 1

    def test_parse_none_returns_empty(self):
        from neopilot.tools.explorer import _parse_filters

        result = _parse_filters(None, None)
        assert result.is_empty()
        assert result.to_api_dict() == {}


# ---------------------------------------------------------------------------
# Filters.from_api_dict() — reverse parsing
# ---------------------------------------------------------------------------


class TestFiltersFromApiDict:
    def test_empty_dict(self):
        f = Filters.from_api_dict({})
        assert f.is_empty()

    def test_none_input(self):
        f = Filters.from_api_dict(None)
        assert f.is_empty()

    def test_segment_only(self):
        raw = {
            "segment": {
                "filters": [
                    {
                        "groupType": "and_group",
                        "expressions": [
                            [
                                [
                                    {
                                        "chave": "slug_dimensao",
                                        "connective": "e",
                                        "estrutura": "segmento",
                                        "operador": "=",
                                        "needConvertToString": False,
                                        "valor": "AOC",
                                    }
                                ]
                            ]
                        ],
                    }
                ]
            }
        }
        f = Filters.from_api_dict(raw)
        assert len(f.segment) == 1
        assert f.segment[0].group_type == "and_group"
        assert f.segment[0].expressions[0][0][0].chave == "slug_dimensao"
        assert f.segment[0].expressions[0][0][0].valor == "AOC"

    def test_metric_with_field_type(self):
        raw = {
            "metric": {
                "filters": [
                    {
                        "groupType": "and_group",
                        "expressions": [
                            [
                                [
                                    {
                                        "chave": "custo_total",
                                        "connective": "e",
                                        "estrutura": "metrica",
                                        "operador": ">",
                                        "valor": "cliques",
                                        "tipo": "field",
                                    }
                                ]
                            ]
                        ],
                    }
                ]
            }
        }
        f = Filters.from_api_dict(raw)
        assert len(f.metric) == 1
        assert f.metric[0].expressions[0][0][0].tipo == "field"

    def test_empty_tipo_normalized_to_none(self):
        """NeoDash sometimes sends tipo="" — should be normalized to None."""
        raw = {
            "segment": {
                "filters": [
                    {
                        "groupType": "and_group",
                        "expressions": [
                            [[{"chave": "fonte", "operador": "=", "valor": "X", "tipo": ""}]]
                        ],
                    }
                ]
            }
        }
        f = Filters.from_api_dict(raw)
        assert f.segment[0].expressions[0][0][0].tipo is None

    def test_round_trip(self):
        """from_api_dict(to_api_dict(filters)) should produce equivalent filters."""
        expr = FilterExpression(chave="cpc", operador=">", valor="3", estrutura="metrica")
        original = Filters(
            metric=[FilterGroup(group_type="and_group", expressions=[[[expr]]])]
        )
        round_tripped = Filters.from_api_dict(original.to_api_dict())
        assert round_tripped.to_api_dict() == original.to_api_dict()

    def test_empty_filters_array(self):
        """filtroUsuario sometimes has segment.filters=[] — should be handled."""
        raw = {
            "segment": {"filters": []},
            "metric": {
                "filters": [
                    {
                        "groupType": "and_group",
                        "expressions": [
                            [[{"chave": "custo_total", "estrutura": "metrica", "operador": ">", "valor": "100"}]]
                        ],
                    }
                ]
            },
        }
        f = Filters.from_api_dict(raw)
        assert len(f.segment) == 0
        assert len(f.metric) == 1


class TestFiltersFromFiltroLocal:
    def test_all_null(self):
        raw = {"agencia": None, "canal": None, "veiculo": None}
        f = Filters.from_filtro_local(raw)
        assert f.is_empty()

    def test_one_active_filter(self):
        raw = {
            "agencia": None,
            "veiculo": {
                "chave": "veiculo",
                "tipo": "string",
                "operador": "in",
                "valor": ["MERCADO LIVRE BRANDS"],
            },
        }
        f = Filters.from_filtro_local(raw)
        assert len(f.segment) == 1
        assert f.segment[0].expressions[0][0][0].chave == "veiculo"
        assert f.segment[0].expressions[0][0][0].operador == "in"

    def test_empty_dict(self):
        f = Filters.from_filtro_local({})
        assert f.is_empty()


class TestFiltroLocalNullValor:
    """filtroLocal entries can have a dict with valor: null (unset combo box)."""

    def test_skip_entry_with_null_valor(self):
        raw = {
            "agencia": None,
            "cliente": {
                "chave": "cliente",
                "tipo": "string",
                "operador": "in",
                "valor": ["LBD | LDB"],
            },
            "marca": {
                "chave": "marca",
                "tipo": "string",
                "operador": "in",
                "valor": None,  # unset combo box
            },
        }
        f = Filters.from_filtro_local(raw)
        assert len(f.segment) == 1
        assert f.segment[0].expressions[0][0][0].chave == "cliente"
        assert f.segment[0].expressions[0][0][0].valor == ["LBD | LDB"]

    def test_all_entries_null_valor(self):
        raw = {
            "marca": {
                "chave": "marca",
                "tipo": "string",
                "operador": "in",
                "valor": None,
            },
            "veiculo": None,
        }
        f = Filters.from_filtro_local(raw)
        assert f.is_empty()


class TestSpecialCharactersInFilters:
    """Filter values with special characters (|, &, =, accents) must survive
    serialization, URL encoding, and round-trip parsing."""

    def test_pipe_in_filter_value(self):
        expr = FilterExpression(
            chave="marca", operador="in", valor=["Vichy | vic", "La Roche-Posay | lrp"]
        )
        d = expr.to_api_dict()
        assert d["valor"] == ["Vichy | vic", "La Roche-Posay | lrp"]

    def test_pipe_in_filtro_local(self):
        raw = {
            "cliente": {
                "chave": "cliente",
                "tipo": "string",
                "operador": "in",
                "valor": ["LBD | LDB"],
            },
        }
        f = Filters.from_filtro_local(raw)
        assert f.segment[0].expressions[0][0][0].valor == ["LBD | LDB"]

    def test_pipe_in_from_api_dict(self):
        raw = {
            "segment": {
                "filters": [{
                    "groupType": "and_group",
                    "expressions": [[[{
                        "chave": "marca",
                        "operador": "in",
                        "valor": ["Vichy | vic"],
                        "estrutura": "segmento",
                    }]]],
                }],
            },
        }
        f = Filters.from_api_dict(raw)
        assert f.segment[0].expressions[0][0][0].valor == ["Vichy | vic"]

    def test_special_chars_round_trip_via_link(self):
        """Build a NeoDash link with special chars in filter values, parse it back."""
        filters = Filters(
            segment=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(
                    chave="marca",
                    operador="in",
                    valor=["Vichy | vic", "La Roche-Posay | lrp"],
                )]]]
            )]
        )
        query = ExplorerQuery(
            dimensions=["veiculo", "marca"],
            metrics=["custo_total"],
            date_start="2026-03-01",
            date_end="2026-03-31",
            filters=filters,
        )
        link = query.to_neodash_link("test")
        parsed = ExplorerQuery.from_neodash_link(link)

        api_orig = query.filters.to_api_dict()
        api_parsed = parsed.filters.to_api_dict()
        assert json.dumps(api_orig) == json.dumps(api_parsed)

    def test_ampersand_in_filter_value_round_trip(self):
        """Values with & must not break URL parsing."""
        filters = Filters(
            segment=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(
                    chave="campanha",
                    operador="c",
                    valor="Brand & Performance",
                )]]]
            )]
        )
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2026-01-01",
            date_end="2026-01-31",
            filters=filters,
        )
        link = query.to_neodash_link("test")
        parsed = ExplorerQuery.from_neodash_link(link)
        assert parsed.filters.segment[0].expressions[0][0][0].valor == "Brand & Performance"

    def test_accented_chars_round_trip(self):
        """Portuguese accented characters must survive round-trip."""
        filters = Filters(
            segment=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(
                    chave="produto",
                    operador="c",
                    valor="Proteção Solar",
                )]]]
            )]
        )
        query = ExplorerQuery(
            dimensions=["produto"],
            metrics=["custo_total"],
            date_start="2026-01-01",
            date_end="2026-01-31",
            filters=filters,
        )
        link = query.to_neodash_link("test")
        parsed = ExplorerQuery.from_neodash_link(link)
        assert parsed.filters.segment[0].expressions[0][0][0].valor == "Proteção Solar"

    def test_equals_in_filter_value_round_trip(self):
        """Values with = must not break URL query string parsing."""
        filters = Filters(
            segment=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(
                    chave="tag",
                    operador="c",
                    valor="key=value",
                )]]]
            )]
        )
        query = ExplorerQuery(
            dimensions=["tag"],
            metrics=["custo_total"],
            date_start="2026-01-01",
            date_end="2026-01-31",
            filters=filters,
        )
        link = query.to_neodash_link("test")
        parsed = ExplorerQuery.from_neodash_link(link)
        assert parsed.filters.segment[0].expressions[0][0][0].valor == "key=value"


class TestFiltersMerge:
    def test_merge_two_filters(self):
        f1 = Filters(
            segment=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(chave="a", operador="=", valor="1")]]]
            )]
        )
        f2 = Filters(
            metric=[FilterGroup(
                group_type="and_group",
                expressions=[[[FilterExpression(chave="b", operador=">", valor="2", estrutura="metrica")]]]
            )]
        )
        merged = f1.merge(f2)
        assert len(merged.segment) == 1
        assert len(merged.metric) == 1
