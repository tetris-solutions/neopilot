#!/usr/bin/env python3
"""Execute 10 filter query examples against the tpv NeoDash instance.

This script tests the filter JSON structure for the get/exploradorResults
endpoint, validating that NeoDash correctly processes each filter type.
"""

import json
import urllib.parse
import urllib.request
import ssl
from typing import Any

SLUG = "tpv"
API_TOKEN = "UBsXBR1CBQJAPhMXZkoBDVNeLGtxbld3Bn5WMUJbK1FQd1RMZj9RCAZVdV8yd1pAUzR1XwUCIXdtAGQHXiFBCwILUhUDBElXBhJVVVkMAwIAVRUTEVxAFAVIWg=="
BASE_URL = f"https://{SLUG}.neodash.ai/admin/index.php"
DATE_START = "2026-03-16"
DATE_END = "2026-03-22"


def _flip_date(d: str) -> str:
    """YYYY-MM-DD → DD-MM-YYYY for NeoDash frontend."""
    p = d.split("-")
    return f"{p[2]}-{p[1]}-{p[0]}" if len(p) == 3 else d


def make_filter_expression(
    chave: str,
    operador: str,
    valor: Any,
    estrutura: str = "segmento",
    tipo: str | None = None,
) -> dict:
    """Build a single filter expression."""
    expr = {
        "chave": chave,
        "connective": "e",
        "estrutura": estrutura,
        "operador": operador,
        "needConvertToString": False,
        "valor": valor,
    }
    if tipo:
        expr["tipo"] = tipo
    return expr


def build_query(
    dimensions: list[str],
    metrics: list[str],
    filtros: dict,
    time_breakdown: str = "nao",
    limit: int = 500,
    order_by: str | None = None,
    order_sort: str = "desc",
    compare_start: str | None = None,
    compare_end: str | None = None,
) -> dict[str, str]:
    """Build the full query params for get/exploradorResults."""
    json_obj = {
        "segmentos": ",".join(dimensions),
        "metricas": ",".join(metrics),
        "segmentarPor": time_breakdown,
        "filtros": filtros,
    }
    params = {
        "dti": DATE_START,
        "dtf": DATE_END,
        "json": json.dumps(json_obj, ensure_ascii=False),
        "limite": str(limit),
        "showTotals": "true",
        "no-cache": "false",
        "orderSort": order_sort,
        "api_token": API_TOKEN,
    }
    if order_by:
        params["orderBy"] = order_by
    if compare_start and compare_end:
        params["dtic"] = compare_start
        params["dtfc"] = compare_end
    return params


def build_neodash_link(
    dimensions: list[str],
    metrics: list[str],
    filtros: dict,
    time_breakdown: str = "nao",
    order_by: str | None = None,
    order_sort: str = "desc",
    compare_start: str | None = None,
    compare_end: str | None = None,
) -> str:
    """Build a NeoDash Explorer frontend link."""
    template_params: dict[str, Any] = {
        "segmentos": ",".join(dimensions),
        "metricas": ",".join(metrics),
        "segmentarPor": time_breakdown,
        "order": order_sort,
        "filtros": filtros,
        "openGraphExplorador": 0,
        "totalPercent": 1,
        "showMetricsTotal": 1,
    }
    if order_by:
        template_params["orderBy"] = order_by

    template = {"params": template_params}
    template_json = json.dumps(template, ensure_ascii=False, separators=(",", ":"))

    url = f"https://{SLUG}.neodash.ai/explorador/100"
    url += f"?dti={_flip_date(DATE_START)}"
    url += f"&dtf={_flip_date(DATE_END)}"
    if compare_start and compare_end:
        url += f"&dtic={_flip_date(compare_start)}"
        url += f"&dtfc={_flip_date(compare_end)}"
    url += f"&template={urllib.parse.quote(template_json, safe='')}"
    return url


def execute_query(params: dict[str, str]) -> dict:
    """Execute the query against the NeoDash API."""
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"{BASE_URL}/get/exploradorResults?{qs}"

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# 10 EXAMPLE QUERIES
# ============================================================================

EXAMPLES: list[dict[str, Any]] = []

# --- Example 1: Simple equals ---
EXAMPLES.append({
    "number": 1,
    "title": "Simple equals (dimension = value)",
    "user_input": "Show me Spend and Clicks by External Campaign for the last 7 days, only for the AOC brand.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("slug_dimensao", "=", "AOC")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 2: Contains ---
EXAMPLES.append({
    "number": 2,
    "title": "Contains (dimension contains value)",
    "user_input": "Show me Spend and CPC by External Campaign for the last 7 days, only campaigns containing 'amz'.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cpc"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "amz")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 3: Does not contain ---
EXAMPLES.append({
    "number": 3,
    "title": "Does not contain (dimension !c value)",
    "user_input": "Show me Spend and Clicks by External Campaign, excluding all Amazon campaigns (campaigns containing 'amz').",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "!c", "amz")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 4: Metric filter (greater than) ---
EXAMPLES.append({
    "number": 4,
    "title": "Metric filter (metric > value)",
    "user_input": "Show me all campaigns where CPC is greater than R$3 in the last 7 days.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques", "cpc"],
    "order_by": "cpc",
    "filtros": {
        "metric": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("cpc", ">", "3", estrutura="metrica")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 5: One of these (in) ---
EXAMPLES.append({
    "number": 5,
    "title": "One of these (dimension in [values])",
    "user_input": "Show me Spend and Impressions by Vehicle for last 7 days, only for AMAZON DSP and AMAZON PRODUCTS.",
    "dimensions": ["veiculo"],
    "metrics": ["custo_total", "impressoes"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("veiculo", "in", ["AMAZON DSP", "AMAZON PRODUCTS"])
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 6: Segment + Metric combined ---
EXAMPLES.append({
    "number": 6,
    "title": "Segment + Metric filters combined",
    "user_input": "Show me Philips campaigns where CPC is less than R$2 in the last 7 days.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques", "cpc"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "philips")
                            ]
                        ]
                    ]
                }
            ]
        },
        "metric": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("cpc", "<", "2", estrutura="metrica")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 7: AND group with multiple conditions ---
EXAMPLES.append({
    "number": 7,
    "title": "AND group with multiple dimension conditions",
    "user_input": "Show me Spend and CPC by External Campaign for AOC brand campaigns on KABUM vehicle.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cpc"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("slug_dimensao", "=", "AOC")
                            ],
                            [
                                make_filter_expression("veiculo", "=", "KABUM")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 8: OR group ---
EXAMPLES.append({
    "number": 8,
    "title": "OR group (dimension contains A OR contains B)",
    "user_input": "Show me campaigns that contain 'conv_sp' OR 'conv_perf' in the name, with Spend and ROAS.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "roi"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "or_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "conv_sp")
                            ]
                        ],
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "conv_perf")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 9: Multiple filter groups (AND between groups) ---
EXAMPLES.append({
    "number": 9,
    "title": "Multiple filter groups (group1 AND group2)",
    "user_input": "Show me Spend by External Campaign for Philips brand AND only on Amazon vehicles (AMAZON DSP, AMAZON PRODUCTS, AMAZON BRANDS).",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques", "cpc", "impressoes"],
    "order_by": "custo_total",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("slug_dimensao", "=", "Philips")
                            ]
                        ]
                    ]
                },
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("veiculo", "in", ["AMAZON DSP", "AMAZON PRODUCTS", "AMAZON BRANDS"])
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})

# --- Example 10: Complex — segment OR + metric + field comparison + daily breakdown ---
EXAMPLES.append({
    "number": 10,
    "title": "Complex: OR segment + metric filter + field comparison + time breakdown",
    "user_input": "Show me daily Spend, Clicks, and CPC for campaigns containing 'meli' OR 'amz', but only where Spend is greater than Clicks (comparing metric to metric field), and CPC is less than R$5.",
    "dimensions": ["campanha_externa_nome"],
    "metrics": ["custo_total", "cliques", "cpc"],
    "order_by": "custo_total",
    "time_breakdown": "dia",
    "filtros": {
        "segment": {
            "filters": [
                {
                    "groupType": "or_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "meli")
                            ]
                        ],
                        [
                            [
                                make_filter_expression("campanha_externa_nome", "c", "amz")
                            ]
                        ]
                    ]
                }
            ]
        },
        "metric": {
            "filters": [
                {
                    "groupType": "and_group",
                    "expressions": [
                        [
                            [
                                make_filter_expression(
                                    "custo_total", ">", "cliques",
                                    estrutura="metrica", tipo="field"
                                )
                            ]
                        ],
                        [
                            [
                                make_filter_expression("cpc", "<", "5", estrutura="metrica")
                            ]
                        ]
                    ]
                }
            ]
        }
    },
})


def run_all():
    """Execute all examples and print results."""
    results = []

    for ex in EXAMPLES:
        num = ex["number"]
        dims = ex["dimensions"]
        mets = ex["metrics"]
        filtros = ex["filtros"]
        tb = ex.get("time_breakdown", "nao")
        ob = ex.get("order_by")
        cs = ex.get("compare_start")
        ce = ex.get("compare_end")

        print(f"\n{'='*80}")
        print(f"EXAMPLE {num}: {ex['title']}")
        print(f"{'='*80}")
        print(f"User: {ex['user_input']}")
        print(f"\nFilter JSON:")
        print(json.dumps(filtros, indent=2, ensure_ascii=False))

        params = build_query(dims, mets, filtros, tb, 500, ob, "desc", cs, ce)
        link = build_neodash_link(dims, mets, filtros, tb, ob, "desc", cs, ce)

        print(f"\nNeoDash Link:\n{link}")
        print(f"\nExecuting query...")

        response = execute_query(params)

        if "error" in response:
            print(f"ERROR: {response['error']}")
            result_data = {"error": response["error"]}
        else:
            retorno = response.get("retorno", {})
            results_init = retorno.get("resultsInit", {})
            rows = results_init.get("results", [])
            totals = results_init.get("total", {})

            print(f"Rows returned: {len(rows)}")
            print(f"\nTotals: {json.dumps(totals, indent=2, ensure_ascii=False)}")
            print(f"\nFirst 5 rows:")
            for row in rows[:5]:
                print(f"  {json.dumps(row, ensure_ascii=False)}")
            if len(rows) > 5:
                print(f"  ... and {len(rows) - 5} more rows")

            result_data = {
                "row_count": len(rows),
                "totals": totals,
                "first_5_rows": rows[:5],
                "all_rows": rows,
            }

        results.append({
            "number": num,
            "title": ex["title"],
            "user_input": ex["user_input"],
            "filtros": filtros,
            "neodash_link": link,
            "result": result_data,
            "dimensions": dims,
            "metrics": mets,
            "time_breakdown": tb,
            "order_by": ob,
        })

    # Save full results to JSON
    output_path = "/Users/beterraba/Documents/Workgit/neodash-ai/neopilot/scripts/filter_examples_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n\nFull results saved to: {output_path}")


if __name__ == "__main__":
    run_all()
