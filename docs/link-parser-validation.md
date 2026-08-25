# NeoPilot Link Parser — Validation Examples

**Instance:** tpv
**Date:** 2026-04-08

---

## Example 1: Full explorer link with filtroUsuario

**URL:** `https://tpv.neodash.ai/explorador/100?dtf=08-04-2026&dti=10-03-2026&filtroUsuario=...`

**Parsed result:**
- Dimensions: `veiculo, campanha_externa_nome`
- Metrics: `custo_total, valor_conversoes, roi`
- Dates: 2026-03-10 to 2026-04-08
- Filter: canal = "AMAZON" (from filtroUsuario, template.filtros is null)

**Filter JSON produced:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [[[{"chave": "canal", "operador": "=", "valor": "AMAZON", "estrutura": "segmento"}]]]
      }
    ]
  }
}
```

**Status:** PASS

---

## Example 2: neod.ai short link (redirect)

**URL:** `https://neod.ai/fs1r96jz0e`

**Behavior:** HTTP 301 redirect → resolves to the same URL as Example 1

**Parsed result:** Identical to Example 1 (same dimensions, metrics, dates, filters)

**Status:** PASS

---

## Example 3: Template-only filters (no filtroUsuario)

**URL:** `https://tpv.neodash.ai/explorador/1009?...` (user template "CRIATIVOS - META")

**Parsed result:**
- Dimensions: `ad_url_thumb_externa`
- Metrics: `custo_total, impressoes, cpm, cliques, cpc, ctr`
- Dates: 2026-03-10 to 2026-04-08
- Filter: fonte = "Mercado Livre Ads" (from template.params.filtros)

**Status:** PASS

---

## Example 4: Three filter sources merged

**URL:** `https://tpv.neodash.ai/explorador/1009?...&filtroLocal=...&filtroUsuario=...`

**Filter sources:**
1. `template.params.filtros` → segment: fonte = "Mercado Livre Ads"
2. `filtroLocal` → segment: veiculo in ["MERCADO LIVRE BRANDS"]
3. `filtroUsuario` → metric: custo_total > 100

**Merged filter JSON produced:**
```json
{
  "segment": {
    "filters": [
      {"groupType": "and_group", "expressions": [[[{"chave": "fonte", "operador": "=", "valor": "Mercado Livre Ads"}]]]},
      {"groupType": "and_group", "expressions": [[[{"chave": "veiculo", "operador": "in", "valor": ["MERCADO LIVRE BRANDS"]}]]]}
    ]
  },
  "metric": {
    "filters": [
      {"groupType": "and_group", "expressions": [[[{"chave": "custo_total", "operador": ">", "valor": "100"}]]]}
    ]
  }
}
```

**Sanity check:** 2 segment groups + 1 metric group = 3 total, matching the API call structure from the NeoDash frontend.

**Status:** PASS

---

## Example 5: Non-explorer link (rejected)

**URL:** `https://tpv.neodash.ai/campanha/123`

**Result:** Correctly rejected with message: "This link is not an Explorer link. NeoPilot can only fetch data from Explorer links (URLs containing /explorador/)."

**Status:** PASS

---

## Filter Source Priority

| Source | URL param | Format | Used for |
|---|---|---|---|
| Template filters | `template` → `params.filtros` | Standard filter JSON | Saved template filters |
| User filters | `filtroUsuario` | Standard filter JSON | User-applied advanced filters |
| Local filters | `filtroLocal` | Simple `{dim: filter_obj}` dict | Combo box quick filters |

All three are merged with AND logic when present. The final API call receives the combined filter set.
