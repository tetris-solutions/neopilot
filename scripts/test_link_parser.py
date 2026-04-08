#!/usr/bin/env python3
"""Validate the reverse link parser against real NeoDash Explorer URLs.

Tests 5 scenarios:
1. Full explorer link with filtroUsuario (canal=AMAZON)
2. neod.ai short link → resolves to the same
3. Template-only filters (fonte=Mercado Livre Ads)
4. All three filter sources merged (template + filtroUsuario + filtroLocal)
5. Non-explorer link rejection
"""

import json
import sys
import urllib.parse

# Add src to path
sys.path.insert(0, "src")

from neopilot.models.explorer import ExplorerQuery, resolve_neodash_link


EXAMPLES = [
    {
        "number": 1,
        "title": "Full explorer link with filtroUsuario",
        "url": "https://tpv.neodash.ai/explorador/100?dtf=08-04-2026&dti=10-03-2026&filtroUsuario=%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22canal%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22AMAZON%22%7D%5D%5D%5D%7D%5D%7D%2C%22metric%22%3A%7B%22filters%22%3A%5B%5D%7D%7D&filtroUsuarioSelected=%7B%22alterado%22%3Atrue%7D&template=%7B%22id%22%3A100%2C%22criado_por%22%3A4%2C%22nome%22%3A%22CAMPANHA%22%2C%22sistema%22%3A1%2C%22params%22%3A%7B%22segmentarPor%22%3A%22nao%22%2C%22segmentos%22%3A%22veiculo%2Ccampanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Cvalor_conversoes%2Croi%22%2C%22metricasGraph%22%3A%22%22%2C%22segmentoGraph%22%3A%22%22%2C%22segmentoPeriodoGraph%22%3A%22trimestre%22%2C%22openGraphExplorador%22%3A1%2C%22order%22%3A%22desc%22%2C%22filtros%22%3Anull%2C%22importSegmentType%22%3A%22%22%2C%22totalPercent%22%3A0%2C%22unifyY%22%3A0%2C%22showMetricsTotal%22%3A0%2C%22showTrendLine%22%3A0%2C%22filtroLocalSegmentos%22%3A%22%22%2C%22fromOpenOnExplorer%22%3A0%7D%2C%22alterado%22%3Atrue%2C%22tipo_id%22%3A2%7D&urlPrevius=%2Fexplorador%2F100",
        "expect_slug": "tpv",
        "expect_dims": ["veiculo", "campanha_externa_nome"],
        "expect_metrics": ["custo_total", "valor_conversoes", "roi"],
        "expect_dates": ("2026-03-10", "2026-04-08"),
        "expect_has_filters": True,
    },
    {
        "number": 2,
        "title": "neod.ai short link (redirect to example 1)",
        "url": "https://neod.ai/fs1r96jz0e",
        "is_short_link": True,
        "expect_slug": "tpv",
        "expect_has_filters": True,
    },
    {
        "number": 3,
        "title": "Template-only filters (fonte=Mercado Livre Ads)",
        "url": "https://tpv.neodash.ai/explorador/1009?dtf=08-04-2026&dti=10-03-2026&template=%7B%22id%22%3A1009%2C%22criado_por%22%3A4%2C%22nome%22%3A%22CRIATIVOS%20-%20META%22%2C%22sistema%22%3A1%2C%22params%22%3A%7B%22segmentarPor%22%3A%22nao%22%2C%22segmentos%22%3A%22ad_url_thumb_externa%22%2C%22metricas%22%3A%22custo_total%2Cimpressoes%2Ccpm%2Ccliques%2Ccpc%2Cctr%22%2C%22metricasGraph%22%3A%22%22%2C%22segmentoGraph%22%3A%22%22%2C%22segmentoPeriodoGraph%22%3A%22dia%22%2C%22openGraphExplorador%22%3A1%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22fonte%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3A%22false%22%2C%22valor%22%3A%22Mercado%20Livre%20Ads%22%2C%22tipo%22%3A%22%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22importSegmentType%22%3A%22%22%2C%22totalPercent%22%3A0%2C%22unifyY%22%3A0%2C%22showMetricsTotal%22%3A0%2C%22showTrendLine%22%3A0%2C%22filtroLocalSegmentos%22%3A%22%22%7D%2C%22alterado%22%3Afalse%2C%22tipo_id%22%3A2%7D&urlPrevius=%2Fexplorador%2F100",
        "expect_slug": "tpv",
        "expect_dims": ["ad_url_thumb_externa"],
        "expect_metrics": ["custo_total", "impressoes", "cpm", "cliques", "cpc", "ctr"],
        "expect_dates": ("2026-03-10", "2026-04-08"),
        "expect_has_filters": True,
    },
    {
        "number": 4,
        "title": "Three filter sources: template + filtroUsuario + filtroLocal",
        "url": "https://tpv.neodash.ai/explorador/1009?dtf=08-04-2026&dti=10-03-2026&filtroLocal=%7B%22agencia%22%3Anull%2C%22canal%22%3Anull%2C%22veiculo%22%3A%7B%22chave%22%3A%22veiculo%22%2C%22tipo%22%3A%22string%22%2C%22operador%22%3A%22in%22%2C%22valor%22%3A%5B%22MERCADO%20LIVRE%20BRANDS%22%5D%7D%2C%22campanha_externa_nome%22%3Anull%7D&filtroUsuario=%7B%22segment%22%3A%7B%22filters%22%3A%5B%5D%7D%2C%22metric%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22custo_total%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3E%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22100%22%7D%5D%5D%5D%7D%5D%7D%7D&filtroUsuarioSelected=%7B%22alterado%22%3Atrue%7D&template=%7B%22id%22%3A1009%2C%22criado_por%22%3A4%2C%22nome%22%3A%22CRIATIVOS%20-%20META%22%2C%22sistema%22%3A1%2C%22params%22%3A%7B%22segmentarPor%22%3A%22nao%22%2C%22segmentos%22%3A%22ad_url_thumb_externa%22%2C%22metricas%22%3A%22custo_total%2Cimpressoes%2Ccpm%2Ccliques%2Ccpc%2Cctr%22%2C%22metricasGraph%22%3A%22%22%2C%22segmentoGraph%22%3A%22%22%2C%22segmentoPeriodoGraph%22%3A%22dia%22%2C%22openGraphExplorador%22%3A1%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22fonte%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3A%22false%22%2C%22valor%22%3A%22Mercado%20Livre%20Ads%22%2C%22tipo%22%3A%22%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22importSegmentType%22%3A%22%22%2C%22totalPercent%22%3A0%2C%22unifyY%22%3A0%2C%22showMetricsTotal%22%3A0%2C%22showTrendLine%22%3A0%2C%22filtroLocalSegmentos%22%3A%22%22%7D%2C%22alterado%22%3Afalse%2C%22tipo_id%22%3A2%7D&urlPrevius=%2Fexplorador%2F1009",
        "expect_slug": "tpv",
        "expect_dims": ["ad_url_thumb_externa"],
        "expect_dates": ("2026-03-10", "2026-04-08"),
        "expect_has_filters": True,
        "expect_filter_sources": 3,  # template seg + filtroLocal seg + filtroUsuario metric
    },
    {
        "number": 5,
        "title": "Non-explorer link (should be rejected)",
        "url": "https://tpv.neodash.ai/campanha/123",
        "expect_error": True,
    },
]


def run_all():
    results = []

    for ex in EXAMPLES:
        num = ex["number"]
        print(f"\n{'='*80}")
        print(f"EXAMPLE {num}: {ex['title']}")
        print(f"{'='*80}")
        print(f"URL: {ex['url'][:100]}...")

        if ex.get("expect_error"):
            try:
                resolve_neodash_link(ex["url"])
                print("ERROR: Should have raised ValueError!")
                results.append({"number": num, "status": "FAIL"})
            except ValueError as e:
                print(f"Correctly rejected: {e}")
                results.append({"number": num, "status": "PASS", "error": str(e)})
            continue

        # Resolve link
        try:
            slug, full_url = resolve_neodash_link(ex["url"])
            print(f"Resolved slug: {slug}")
            if ex.get("is_short_link"):
                print(f"Redirected to: {full_url[:100]}...")
        except Exception as e:
            print(f"ERROR resolving: {e}")
            results.append({"number": num, "status": "FAIL", "error": str(e)})
            continue

        if "expect_slug" in ex:
            assert slug == ex["expect_slug"], f"Expected slug {ex['expect_slug']}, got {slug}"

        # Parse link
        query = ExplorerQuery.from_neodash_link(full_url)
        print(f"Dimensions: {query.dimensions}")
        print(f"Metrics: {query.metrics}")
        print(f"Dates: {query.date_start} to {query.date_end}")
        print(f"Time breakdown: {query.time_breakdown}")
        print(f"Order: {query.order_sort} (by {query.order_by})")
        print(f"Filters empty: {query.filters.is_empty()}")

        if not query.filters.is_empty():
            api_dict = query.filters.to_api_dict()
            print(f"Filter summary: {query.filters.to_summary()}")
            print(f"Filter API dict:")
            print(json.dumps(api_dict, indent=2, ensure_ascii=False))

        # Validate expectations
        if "expect_dims" in ex:
            assert query.dimensions == ex["expect_dims"], f"Dims mismatch: {query.dimensions}"
        if "expect_metrics" in ex:
            assert query.metrics == ex["expect_metrics"], f"Metrics mismatch: {query.metrics}"
        if "expect_dates" in ex:
            assert (query.date_start, query.date_end) == ex["expect_dates"]
        if "expect_has_filters" in ex:
            assert query.filters.is_empty() != ex["expect_has_filters"]

        if "expect_filter_sources" in ex:
            api_dict = query.filters.to_api_dict()
            seg_count = len(api_dict.get("segment", {}).get("filters", []))
            met_count = len(api_dict.get("metric", {}).get("filters", []))
            total = seg_count + met_count
            print(f"Filter groups: {seg_count} segment + {met_count} metric = {total} total")
            assert total >= ex["expect_filter_sources"], f"Expected >= {ex['expect_filter_sources']} filter groups, got {total}"

        # Show the API params that would be sent
        params = query.to_api_params()
        json_payload = json.loads(params["json"])
        print(f"\nAPI params json.filtros:")
        print(json.dumps(json_payload["filtros"], indent=2, ensure_ascii=False))

        results.append({"number": num, "status": "PASS"})

    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for r in results:
        print(f"  Example {r['number']}: {r['status']}")


if __name__ == "__main__":
    run_all()
