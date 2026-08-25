"""Tests specifically for the Explorer query and response logic."""

from __future__ import annotations

import json
import urllib.parse

from neopilot.models.explorer import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    ExplorerQuery,
    ExplorerResult,
    _flip_date,
)


class TestExplorerQueryConstruction:
    def test_basic_query(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total", "cliques"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()

        # Verify mandatory fields
        assert params["dti"] == "2025-01-01"
        assert params["dtf"] == "2025-01-31"
        assert params["showTotals"] == "true"
        assert params["no-cache"] == "false"
        assert params["orderSort"] == "desc"
        assert params["limite"] == str(DEFAULT_LIMIT)

        # Verify JSON payload
        json_payload = json.loads(params["json"])
        assert json_payload["segmentos"] == "campanha"
        assert json_payload["metricas"] == "custo_total,cliques"
        assert json_payload["segmentarPor"] == "nao"
        assert json_payload["filtros"] == {}

    def test_multiple_dimensions(self):
        query = ExplorerQuery(
            dimensions=["campanha", "veiculo", "marca"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        assert json_payload["segmentos"] == "campanha,veiculo,marca"

    def test_time_breakdown(self):
        for breakdown in ["dia", "semana", "mes", "trimestre", "ano"]:
            query = ExplorerQuery(
                dimensions=["campanha"],
                metrics=["custo_total"],
                date_start="2025-01-01",
                date_end="2025-12-31",
                time_breakdown=breakdown,
            )
            params = query.to_api_params()
            json_payload = json.loads(params["json"])
            assert json_payload["segmentarPor"] == breakdown

    def test_order_by(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total", "roi"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            order_by="roi",
            order_sort="asc",
        )
        params = query.to_api_params()
        assert params["orderBy"] == "roi"
        assert params["orderSort"] == "asc"

    def test_limit_capping(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
            limit=100_000,
        )
        params = query.to_api_params()
        assert params["limite"] == str(MAX_LIMIT)

    def test_show_totals_always_true(self):
        """showTotals must ALWAYS be true — NeoPilot never calculates totals."""
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert params["showTotals"] == "true"

    def test_filters_empty_by_default(self):
        """Without filters, filtros is an empty dict."""
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-01-01",
            date_end="2025-01-31",
        )
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        assert json_payload["filtros"] == {}

    def test_comparison_dates(self):
        query = ExplorerQuery(
            dimensions=["campanha"],
            metrics=["custo_total"],
            date_start="2025-02-01",
            date_end="2025-02-28",
            compare_date_start="2025-01-01",
            compare_date_end="2025-01-31",
        )
        params = query.to_api_params()
        assert params["dtic"] == "2025-01-01"
        assert params["dtfc"] == "2025-01-31"


class TestExplorerTruncation:
    def test_truncated_when_equal_to_limit(self):
        result = ExplorerResult(
            results=[{"x": i} for i in range(500)],
            totals={"custo_total": 1000},
            row_count=500,
            was_truncated=True,
            truncation_message="Results were truncated at 500 rows.",
        )
        assert result.was_truncated is True
        assert "truncated" in result.truncation_message.lower()

    def test_not_truncated_when_less_than_limit(self):
        result = ExplorerResult(
            results=[{"x": i} for i in range(10)],
            totals={"custo_total": 100},
            row_count=10,
            was_truncated=False,
        )
        assert result.was_truncated is False
        assert result.truncation_message is None

    def test_comparison_results(self):
        result = ExplorerResult(
            results=[{"x": 1}],
            totals={"custo_total": 100},
            comparison_results=[{"x": 2}],
            comparison_totals={"custo_total": 90},
            row_count=1,
            was_truncated=False,
        )
        assert result.comparison_results is not None
        assert len(result.comparison_results) == 1
        assert result.comparison_totals["custo_total"] == 90


class TestFlipDate:
    def test_basic(self):
        assert _flip_date("2026-03-17") == "17-03-2026"

    def test_single_digit(self):
        assert _flip_date("2026-01-05") == "05-01-2026"

    def test_passthrough_on_bad_format(self):
        # Non-3-part strings pass through unchanged
        assert _flip_date("invalid") == "invalid"
        assert _flip_date("2026-03") == "2026-03"


class TestNeoDashLinkBuilder:
    def test_simple_link(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total", "cpa"],
            date_start="2026-03-11",
            date_end="2026-03-17",
        )
        link = query.to_neodash_link("tpv")

        assert link.startswith("https://tpv.neodash.ai/explorador/100?")
        assert "dti=11-03-2026" in link
        assert "dtf=17-03-2026" in link
        assert "template=" in link

        # Parse the template param (URL-encoded)
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        template = json.loads(template_str)
        params = template["params"]

        assert params["segmentos"] == "canal"
        assert params["metricas"] == "custo_total,cpa"
        assert params["segmentarPor"] == "nao"
        assert params["order"] == "desc"
        assert params["filtros"] == {}  # always empty in template
        assert "filtroUsuario" not in link  # no filters = no filtroUsuario param
        assert params["openGraphExplorador"] == 0
        assert params["totalPercent"] == 1
        assert params["showMetricsTotal"] == 1

    def test_link_with_time_breakdown(self):
        query = ExplorerQuery(
            dimensions=["veiculo"],
            metrics=["custo_total"],
            date_start="2026-03-01",
            date_end="2026-03-17",
            time_breakdown="dia",
            order_sort="asc",
        )
        link = query.to_neodash_link("tpv")
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        params = json.loads(template_str)["params"]

        assert params["segmentarPor"] == "dia"
        assert params["order"] == "asc"

    def test_link_with_comparison_dates(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total"],
            date_start="2026-03-11",
            date_end="2026-03-17",
            compare_date_start="2026-03-04",
            compare_date_end="2026-03-10",
        )
        link = query.to_neodash_link("tpv")

        assert "dtic=04-03-2026" in link
        assert "dtfc=10-03-2026" in link

    def test_filters_go_in_filtro_usuario(self):
        """Filters must be in the filtroUsuario param, not inside template."""
        from neopilot.models.filters import FilterExpression, FilterGroup, Filters

        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total"],
            date_start="2026-03-11",
            date_end="2026-03-17",
            filters=Filters(
                segment=[FilterGroup(
                    group_type="and_group",
                    expressions=[[[FilterExpression(chave="marca", operador="in", valor=["Vichy | vic"])]]]
                )]
            ),
        )
        link = query.to_neodash_link("tpv")

        parsed = urllib.parse.urlparse(link)
        qs = urllib.parse.parse_qs(parsed.query)

        # filtroUsuario should contain the filters
        assert "filtroUsuario" in qs
        filtro = json.loads(qs["filtroUsuario"][0])
        assert "segment" in filtro
        assert filtro["segment"]["filters"][0]["expressions"][0][0][0]["valor"] == ["Vichy | vic"]

        # template.params.filtros should be empty
        template = json.loads(qs["template"][0])
        assert template["params"]["filtros"] == {}

    def test_link_with_order_by(self):
        query = ExplorerQuery(
            dimensions=["canal"],
            metrics=["custo_total", "cpa"],
            date_start="2026-03-11",
            date_end="2026-03-17",
            order_by="custo_total",
        )
        link = query.to_neodash_link("tpv")
        template_str = urllib.parse.unquote(link.split("template=", 1)[1])
        params = json.loads(template_str)["params"]

        assert params["orderBy"] == "custo_total"


class TestFromNeoDashLink:
    """Tests for ExplorerQuery.from_neodash_link() — reverse link parsing."""

    def test_simple_link_no_filters(self):
        """Parse a basic explorer link without filters."""
        url = (
            "https://tpv.neodash.ai/explorador/100"
            "?dti=16-03-2026&dtf=22-03-2026"
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22"
            "%2C%22metricas%22%3A%22custo_total%2Ccliques%22"
            "%2C%22segmentarPor%22%3A%22nao%22"
            "%2C%22order%22%3A%22desc%22"
            "%2C%22filtros%22%3A%7B%7D%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)
        assert query.dimensions == ["campanha_externa_nome"]
        assert query.metrics == ["custo_total", "cliques"]
        assert query.date_start == "2026-03-16"
        assert query.date_end == "2026-03-22"
        assert query.time_breakdown == "nao"
        assert query.order_sort == "desc"
        assert query.filters.is_empty()

    def test_link_with_filtro_usuario(self):
        """Parse a link with user-applied filters (filtroUsuario)."""
        url = (
            "https://tpv.neodash.ai/explorador/100"
            "?dti=10-03-2026&dtf=08-04-2026"
            "&filtroUsuario=%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B"
            "%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B"
            "%22chave%22%3A%22canal%22%2C%22connective%22%3A%22e%22%2C"
            "%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C"
            "%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22AMAZON%22"
            "%7D%5D%5D%5D%7D%5D%7D%7D"
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22veiculo%2C"
            "campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2C"
            "valor_conversoes%2Croi%22%2C%22segmentarPor%22%3A%22nao%22%2C"
            "%22order%22%3A%22desc%22%2C%22filtros%22%3Anull%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)
        assert query.dimensions == ["veiculo", "campanha_externa_nome"]
        assert query.metrics == ["custo_total", "valor_conversoes", "roi"]
        assert query.date_start == "2026-03-10"
        assert query.date_end == "2026-04-08"
        # Should have the canal=AMAZON filter from filtroUsuario
        assert not query.filters.is_empty()
        api_dict = query.filters.to_api_dict()
        assert "segment" in api_dict

    def test_link_with_template_filters(self):
        """Parse a link with template-level filters (no filtroUsuario)."""
        url = (
            "https://tpv.neodash.ai/explorador/1009"
            "?dti=10-03-2026&dtf=08-04-2026"
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22ad_url_thumb_externa%22"
            "%2C%22metricas%22%3A%22custo_total%2Cimpressoes%22"
            "%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22"
            "%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B"
            "%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B"
            "%22chave%22%3A%22fonte%22%2C%22operador%22%3A%22%3D%22%2C"
            "%22valor%22%3A%22Mercado%20Livre%20Ads%22%2C%22estrutura%22%3A%22segmento%22"
            "%7D%5D%5D%5D%7D%5D%7D%7D%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)
        assert query.dimensions == ["ad_url_thumb_externa"]
        assert not query.filters.is_empty()
        api_dict = query.filters.to_api_dict()
        seg_filters = api_dict["segment"]["filters"]
        assert seg_filters[0]["expressions"][0][0][0]["chave"] == "fonte"

    def test_link_with_all_three_filter_sources(self):
        """Parse a link with template filters + filtroUsuario + filtroLocal."""
        url = (
            "https://tpv.neodash.ai/explorador/1009"
            "?dti=10-03-2026&dtf=08-04-2026"
            # filtroLocal: veiculo in [MERCADO LIVRE BRANDS]
            "&filtroLocal=%7B%22veiculo%22%3A%7B%22chave%22%3A%22veiculo%22%2C"
            "%22tipo%22%3A%22string%22%2C%22operador%22%3A%22in%22%2C"
            "%22valor%22%3A%5B%22MERCADO%20LIVRE%20BRANDS%22%5D%7D%7D"
            # filtroUsuario: custo_total > 100
            "&filtroUsuario=%7B%22segment%22%3A%7B%22filters%22%3A%5B%5D%7D%2C"
            "%22metric%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C"
            "%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22custo_total%22%2C"
            "%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3E%22%2C"
            "%22valor%22%3A%22100%22%7D%5D%5D%5D%7D%5D%7D%7D"
            # template.params.filtros: fonte = Mercado Livre Ads
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22ad_url_thumb_externa%22"
            "%2C%22metricas%22%3A%22custo_total%2Cimpressoes%22"
            "%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22"
            "%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B"
            "%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B"
            "%22chave%22%3A%22fonte%22%2C%22operador%22%3A%22%3D%22%2C"
            "%22valor%22%3A%22Mercado%20Livre%20Ads%22%2C%22estrutura%22%3A%22segmento%22"
            "%7D%5D%5D%5D%7D%5D%7D%7D%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)
        api_dict = query.filters.to_api_dict()
        # Should have segment filters from template + filtroLocal
        assert "segment" in api_dict
        seg_groups = api_dict["segment"]["filters"]
        assert len(seg_groups) >= 2  # template fonte + filtroLocal veiculo
        # Should have metric filters from filtroUsuario
        assert "metric" in api_dict

    def test_date_flipping(self):
        """Dates should be flipped from DD-MM-YYYY to YYYY-MM-DD."""
        url = (
            "https://tpv.neodash.ai/explorador/100"
            "?dti=01-01-2026&dtf=31-01-2026"
            "&dtic=01-12-2025&dtfc=31-12-2025"
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha%22"
            "%2C%22metricas%22%3A%22custo_total%22"
            "%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22"
            "%2C%22filtros%22%3A%7B%7D%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)
        assert query.date_start == "2026-01-01"
        assert query.date_end == "2026-01-31"
        assert query.compare_date_start == "2025-12-01"
        assert query.compare_date_end == "2025-12-31"

    def test_round_trip(self):
        """from_neodash_link(to_neodash_link(query)) should preserve key fields."""
        from neopilot.models.filters import FilterExpression, FilterGroup, Filters

        original = ExplorerQuery(
            dimensions=["veiculo", "campanha_externa_nome"],
            metrics=["custo_total", "roi"],
            date_start="2026-03-10",
            date_end="2026-04-08",
            time_breakdown="dia",
            order_by="custo_total",
            order_sort="desc",
            filters=Filters(
                segment=[FilterGroup(
                    group_type="and_group",
                    expressions=[[[FilterExpression(chave="canal", operador="=", valor="AMAZON")]]]
                )]
            ),
        )
        link = original.to_neodash_link("tpv")
        parsed = ExplorerQuery.from_neodash_link(link)

        assert parsed.dimensions == original.dimensions
        assert parsed.metrics == original.metrics
        assert parsed.date_start == original.date_start
        assert parsed.date_end == original.date_end
        assert parsed.time_breakdown == original.time_breakdown
        assert parsed.order_sort == original.order_sort

    def test_real_url_with_pipe_chars_and_null_valor(self):
        """Real-world URL: filtroLocal with null valor + pipe chars in values."""
        url = (
            "https://loreal.neodash.ai/explorador/1379"
            "?dtf=08-04-2026&dti=06-04-2026"
            # filtroLocal: cliente=["LBD | LDB"], marca has valor:null
            "&filtroLocal=%7B%22agencia%22%3Anull%2C%22cliente%22%3A%7B%22chave%22"
            "%3A%22cliente%22%2C%22tipo%22%3A%22string%22%2C%22operador%22%3A%22in%22"
            "%2C%22valor%22%3A%5B%22LBD+%7C+LDB%22%5D%7D%2C%22marca%22%3A%7B%22chave"
            "%22%3A%22marca%22%2C%22tipo%22%3A%22string%22%2C%22operador%22%3A%22in%22"
            "%2C%22valor%22%3Anull%7D%2C%22fase_campanha%22%3Anull%7D"
            # filtroUsuario: marca in ["Vichy | vic", "La Roche-Posay | lrp"]
            "&filtroUsuario=%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType"
            "%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A"
            "%22marca%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento"
            "%22%2C%22operador%22%3A%22in%22%2C%22needConvertToString%22%3Afalse%2C"
            "%22valor%22%3A%5B%22Vichy+%7C+vic%22%2C%22La+Roche-Posay+%7C+lrp%22%5D"
            "%7D%5D%5D%5D%7D%5D%7D%7D"
            # template with basic params
            "&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22veiculo%2Cmarca%22"
            "%2C%22metricas%22%3A%22custo_total%2Cimpressoes%22"
            "%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22"
            "%2C%22filtros%22%3A%7B%7D%7D%7D"
        )
        query = ExplorerQuery.from_neodash_link(url)

        assert query.dimensions == ["veiculo", "marca"]
        assert query.metrics == ["custo_total", "impressoes"]
        assert query.date_start == "2026-04-06"
        assert query.date_end == "2026-04-08"
        assert not query.filters.is_empty()

        api = query.filters.to_api_dict()
        # Should have segment filters from filtroUsuario + filtroLocal
        seg_filters = api["segment"]["filters"]

        # Verify pipe chars survived parsing
        all_valores = []
        for group in seg_filters:
            for branch in group["expressions"]:
                for block in branch:
                    for expr in block:
                        v = expr["valor"]
                        all_valores.extend(v if isinstance(v, list) else [v])

        assert "LBD | LDB" in all_valores
        assert "Vichy | vic" in all_valores
        assert "La Roche-Posay | lrp" in all_valores

        # Round-trip: build link and parse back
        link = query.to_neodash_link("loreal")
        reparsed = ExplorerQuery.from_neodash_link(link)
        assert json.dumps(query.filters.to_api_dict()) == json.dumps(reparsed.filters.to_api_dict())


class TestResolveNeoDashLink:
    """Tests for resolve_neodash_link() — URL validation."""

    def test_full_explorer_url(self):
        from neopilot.models.explorer import resolve_neodash_link

        slug, resolved = resolve_neodash_link(
            "https://tpv.neodash.ai/explorador/100?dti=01-01-2026&dtf=31-01-2026"
        )
        assert slug == "tpv"
        assert resolved == "https://tpv.neodash.ai/explorador/100?dti=01-01-2026&dtf=31-01-2026"

    def test_non_explorer_link_rejected(self):
        import pytest

        from neopilot.models.explorer import resolve_neodash_link

        with pytest.raises(ValueError, match="not an Explorer link"):
            resolve_neodash_link("https://tpv.neodash.ai/campanha/123")

    def test_non_neodash_host_rejected(self):
        import pytest

        from neopilot.models.explorer import resolve_neodash_link

        with pytest.raises(ValueError, match="Unrecognized NeoDash host"):
            resolve_neodash_link("https://example.com/explorador/100")
