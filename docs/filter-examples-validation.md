# NeoPilot Filter Support — Validation Examples

**Instance:** tpv
**Date range:** 2026-03-16 to 2026-03-22
**Total unfiltered Spend:** R$103,053.82 (43 campaigns, 7 vehicles)

---

## Example 1: Simple equals (`=`)

**User input:**
> Show me Spend and Clicks by External Campaign for the last 7 days, only for the AOC brand.

**Filter logic:**
`Marca TPV = "AOC"`

**Filter JSON:**
```json
{
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
                "needConvertToString": false,
                "valor": "AOC"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 17 rows
**Totals:** Spend R$47,466.73 | Clicks 48,705

**Top 3 rows:**

| External Campaign | Spend | Clicks |
|---|---|---|
| np_monit_aoc-all_aon_conv_sp | 11,682.23 | 12,381 |
| np_amz_monit_aoc-all_pt_aon_roas_display_conv_perf_plus | 9,441.37 | 3,244 |
| ADS_AOC_MONITORES_MAR26_PADS | 5,849.00 | 1,888 |

**Sanity check:** AOC spend (R$47,466) matches the unfiltered brand breakdown (R$47,466.73).

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22slug_dimensao%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22AOC%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 2: Contains (`c`)

**User input:**
> Show me Spend and CPC by External Campaign for the last 7 days, only campaigns containing 'amz'.

**Filter logic:**
`External Campaign contains "amz"`

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "amz"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 20 rows
**Totals:** Spend R$53,206.29 | CPC R$1.30

**Top 3 rows:**

| External Campaign | Spend | CPC |
|---|---|---|
| np_amz_tv_philips-all_pt_aon_roas_display_conv_perf_plus | 14,752.86 | 3.85 |
| np_amz_monit_aoc-all_pt_aon_roas_display_conv_perf_plus | 9,441.37 | 2.91 |
| np_amz_tv_philips-all_pt_aon_roas_conv_sp_bran_roas | 8,081.28 | 2.25 |

**Sanity check:** All campaign names contain "amz". Spend R$53k is the Amazon-related portion.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccpc%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22amz%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 3: Does not contain (`!c`)

**User input:**
> Show me Spend and Clicks by External Campaign, excluding all Amazon campaigns (campaigns containing 'amz').

**Filter logic:**
`External Campaign does not contain "amz"`

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "!c",
                "needConvertToString": false,
                "valor": "amz"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 23 rows
**Totals:** Spend R$49,847.53 | Clicks 32,070

**Top 3 rows:**

| External Campaign | Spend | Clicks |
|---|---|---|
| np_monit_aoc-all_aon_conv_sp | 11,682.23 | 12,381 |
| ADS_AOC_MONITORES_MAR26_PADS | 5,849.00 | 1,888 |
| np_meli_all_philips-all_pt_aon_roas_sca_conv_dads_dca | 3,571.87 | 1,471 |

**Sanity check:** R$53,206 (contains amz) + R$49,847 (not contains amz) = R$103,053.53 ~ R$103,053.82 total.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%21c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22amz%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 4: Metric filter — greater than (`>`)

**User input:**
> Show me all campaigns where CPC is greater than R$3 in the last 7 days.

**Filter logic:**
`CPC > 3`

**Filter JSON:**
```json
{
  "metric": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "cpc",
                "connective": "e",
                "estrutura": "metrica",
                "operador": ">",
                "needConvertToString": false,
                "valor": "3"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 22 rows
**Totals:** Spend R$43,979.71 | Clicks 11,040 | CPC R$3.98

**Top 3 rows:**

| External Campaign | Spend | Clicks | CPC |
|---|---|---|---|
| np_amz_tv_philips-all_pt_aon_roas_display_conv_perf_plus | 14,752.86 | 3,834 | 3.85 |
| ADS_AOC_MONITORES_MAR26_PADS | 5,849.00 | 1,888 | 3.10 |
| np_meli_all_philips-all_pt_aon_roas_sca_conv_dads_dp | 3,188.85 | 724 | 4.40 |

**Sanity check:** All returned rows have CPC > R$3.00.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%2Ccpc%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22metric%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22cpc%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3E%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%223%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22cpc%22%7D%7D)

---

## Example 5: One of these (`in`)

**User input:**
> Show me Spend and Impressions by Vehicle for the last 7 days, only for AMAZON DSP and AMAZON PRODUCTS.

**Filter logic:**
`Vehicle is one of ["AMAZON DSP", "AMAZON PRODUCTS"]`

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "veiculo",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "in",
                "needConvertToString": false,
                "valor": ["AMAZON DSP", "AMAZON PRODUCTS"]
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 2 rows
**Totals:** Spend R$47,611.07 | Impressions 13,104,914

**All rows:**

| Vehicle | Spend | Impressions |
|---|---|---|
| AMAZON DSP | 28,102.82 | 11,708,312 |
| AMAZON PRODUCTS | 19,508.25 | 1,396,602 |

**Sanity check:** Exactly 2 rows returned matching the filter values. Values match unfiltered vehicle breakdown.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22veiculo%22%2C%22metricas%22%3A%22custo_total%2Cimpressoes%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22veiculo%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22in%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%5B%22AMAZON%20DSP%22%2C%22AMAZON%20PRODUCTS%22%5D%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 6: Segment + Metric filters combined

**User input:**
> Show me Philips campaigns where CPC is less than R$2 in the last 7 days.

**Filter logic:**
`External Campaign contains "philips" AND CPC < 2`

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "philips"
              }
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
              {
                "chave": "cpc",
                "connective": "e",
                "estrutura": "metrica",
                "operador": "<",
                "needConvertToString": false,
                "valor": "2"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Result:** 7 rows
**Totals:** Spend R$12,126.52 | Clicks 10,901 | CPC R$1.11

**Top 3 rows:**

| External Campaign | Spend | Clicks | CPC |
|---|---|---|---|
| np_tv_philips-all_aon_conv_sp | 3,355.57 | 3,495 | 0.96 |
| np_amz_ava_philips-mix_pt_aon_roas_display_conv_perf_plus | 3,145.94 | 1,665 | 1.89 |
| np_tv_philips-all_aon_conv_sp_ | 2,434.00 | 1,751 | 1.39 |

**Sanity check:** All rows contain "philips" in campaign name AND have CPC < R$2.00.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%2Ccpc%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22philips%22%7D%5D%5D%5D%7D%5D%7D%2C%22metric%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22cpc%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3C%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%222%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 7: AND group with multiple dimension conditions

**User input:**
> Show me Spend and CPC by External Campaign for AOC brand campaigns on KABUM vehicle.

**Filter logic:**
`Marca TPV = "AOC" AND Vehicle = "KABUM"`

**Filter JSON:**
```json
{
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
                "needConvertToString": false,
                "valor": "AOC"
              }
            ],
            [
              {
                "chave": "veiculo",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "=",
                "needConvertToString": false,
                "valor": "KABUM"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Note:** Multiple AND conditions within the same group use separate inner arrays within the same expression branch. Each `[{...}]` block is a condition, and they are AND'd together within the enclosing array.

**Result:** 4 rows
**Totals:** Spend R$7,103.56 | CPC R$3.66

**All rows:**

| External Campaign | Spend | CPC |
|---|---|---|
| ADS_AOC_MONITORES_MAR26_PADS | 5,849.00 | 3.10 |
| ADS_AOC_MONITORES_MAR26_DISPLAY_TESTEA | 791.50 | 25.53 |
| ADS_AOC_MONITORES_MAR26_DISPLAY_TESTEB | 366.70 | 18.33 |
| ADS_AOC_MONITORES_MAR26_AWARENESS | 96.36 | 48.18 |

**Sanity check:** Total R$7,103.56 matches KABUM vehicle spend from the unfiltered breakdown. All campaigns are KABUM/AOC campaigns.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccpc%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22slug_dimensao%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22AOC%22%7D%5D%2C%5B%7B%22chave%22%3A%22veiculo%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22KABUM%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 8: OR group

**User input:**
> Show me campaigns that contain 'conv_sp' OR 'conv_perf' in the name, with Spend and ROAS.

**Filter logic:**
`External Campaign contains "conv_sp" OR External Campaign contains "conv_perf"`

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "or_group",
        "expressions": [
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "conv_sp"
              }
            ]
          ],
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "conv_perf"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Note:** OR groups use `"groupType": "or_group"`. Each OR branch is a separate array within `expressions`. The first branch matches "conv_sp", the second matches "conv_perf".

**Result:** 18 rows
**Totals:** Spend R$66,873.60 | ROAS 39.78

**Top 3 rows:**

| External Campaign | Spend | ROAS |
|---|---|---|
| np_amz_tv_philips-all_pt_aon_roas_display_conv_perf_plus | 14,752.86 | 49.43 |
| np_monit_aoc-all_aon_conv_sp | 11,682.23 | 45.13 |
| np_amz_monit_aoc-all_pt_aon_roas_display_conv_perf_plus | 9,441.37 | 69.39 |

**Sanity check:** All rows contain either "conv_sp" or "conv_perf" in the campaign name.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Croi%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22or_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22conv_sp%22%7D%5D%5D%2C%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22conv_perf%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 9: Multiple filter groups (AND between groups)

**User input:**
> Show me Spend by External Campaign for Philips brand AND only on Amazon vehicles (AMAZON DSP, AMAZON PRODUCTS, AMAZON BRANDS).

**Filter logic:**
`Group 1: Marca TPV = "Philips"` AND `Group 2: Vehicle is one of ["AMAZON DSP", "AMAZON PRODUCTS", "AMAZON BRANDS"]`

**Filter JSON:**
```json
{
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
                "needConvertToString": false,
                "valor": "Philips"
              }
            ]
          ]
        ]
      },
      {
        "groupType": "and_group",
        "expressions": [
          [
            [
              {
                "chave": "veiculo",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "in",
                "needConvertToString": false,
                "valor": ["AMAZON DSP", "AMAZON PRODUCTS", "AMAZON BRANDS"]
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Note:** Multiple objects in the `filters` array are combined with AND logic. Each group can independently use AND or OR logic within its own expressions.

**Result:** 15 rows
**Totals:** Spend R$34,167.06 | Clicks 11,196 | CPC R$3.05 | Impressions 2,374,255

**Top 3 rows:**

| External Campaign | Spend | Clicks | CPC | Impressions |
|---|---|---|---|---|
| np_amz_tv_philips-all_pt_aon_roas_display_conv_perf_plus | 14,752.86 | 3,834 | 3.85 | 983,413 |
| np_amz_tv_philips-all_pt_aon_roas_conv_sp_bran_roas | 8,081.28 | 3,589 | 2.25 | 575,339 |
| np_amz_ava_philips-mix_pt_aon_roas_display_conv_perf_plus | 3,145.94 | 1,665 | 1.89 | 394,905 |

**Sanity check:** All campaigns are Philips brand on Amazon vehicles only (DSP, Products, or Brands).

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%2Ccpc%2Cimpressoes%22%2C%22segmentarPor%22%3A%22nao%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22slug_dimensao%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22%3D%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22Philips%22%7D%5D%5D%5D%7D%2C%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22veiculo%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22in%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%5B%22AMAZON%20DSP%22%2C%22AMAZON%20PRODUCTS%22%2C%22AMAZON%20BRANDS%22%5D%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Example 10: Complex — OR segment + metric filter + field comparison + daily breakdown

**User input:**
> Show me daily Spend, Clicks, and CPC for campaigns containing 'meli' OR 'amz', but only where Spend is greater than Clicks (comparing metric to metric field), and CPC is less than R$5.

**Filter logic:**
- Segment OR: `External Campaign contains "meli" OR External Campaign contains "amz"`
- Metric AND: `Spend > Clicks (field comparison)` AND `CPC < 5`
- Time breakdown: daily

**Filter JSON:**
```json
{
  "segment": {
    "filters": [
      {
        "groupType": "or_group",
        "expressions": [
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "meli"
              }
            ]
          ],
          [
            [
              {
                "chave": "campanha_externa_nome",
                "connective": "e",
                "estrutura": "segmento",
                "operador": "c",
                "needConvertToString": false,
                "valor": "amz"
              }
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
              {
                "chave": "custo_total",
                "connective": "e",
                "estrutura": "metrica",
                "operador": ">",
                "needConvertToString": false,
                "valor": "cliques",
                "tipo": "field"
              }
            ]
          ],
          [
            [
              {
                "chave": "cpc",
                "connective": "e",
                "estrutura": "metrica",
                "operador": "<",
                "needConvertToString": false,
                "valor": "5"
              }
            ]
          ]
        ]
      }
    ]
  }
}
```

**Note:** The `"tipo": "field"` property makes the filter compare a metric against another metric field (Spend > Clicks) instead of a static value. The metric `expressions` use two AND branches — one for the field comparison and one for the CPC threshold.

**Result:** 130 rows (daily breakdown)
**Totals:** Spend R$62,308.09 | Clicks 23,264 | CPC R$2.68

**Sample rows (2026-03-22):**

| Date | External Campaign | Spend | Clicks | CPC |
|---|---|---|---|---|
| 2026-03-22 | np_amz_tv_philips-all_pt_aon_roas_display_conv_perf_plus | 2,033.49 | 445 | 4.57 |
| 2026-03-22 | np_meli_monit_aoc-all_pt_aon_roas_sca_conv_dads_dc | 439.99 | 364 | 1.21 |
| 2026-03-22 | np_amz_tv_philips-all_pt_aon_roas_conv_sp_bran_roas | 1,086.93 | 528 | 2.06 |

**Sanity check:** All rows have campaign names containing "meli" or "amz", Spend > Clicks (numerically), and CPC < R$5. Daily breakdown adds `data` field to each row.

**NeoDash link:** [View on NeoDash](https://tpv.neodash.ai/explorador/100?dti=16-03-2026&dtf=22-03-2026&template=%7B%22params%22%3A%7B%22segmentos%22%3A%22campanha_externa_nome%22%2C%22metricas%22%3A%22custo_total%2Ccliques%2Ccpc%22%2C%22segmentarPor%22%3A%22dia%22%2C%22order%22%3A%22desc%22%2C%22filtros%22%3A%7B%22segment%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22or_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22meli%22%7D%5D%5D%2C%5B%5B%7B%22chave%22%3A%22campanha_externa_nome%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22segmento%22%2C%22operador%22%3A%22c%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22amz%22%7D%5D%5D%5D%7D%5D%7D%2C%22metric%22%3A%7B%22filters%22%3A%5B%7B%22groupType%22%3A%22and_group%22%2C%22expressions%22%3A%5B%5B%5B%7B%22chave%22%3A%22custo_total%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3E%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%22cliques%22%2C%22tipo%22%3A%22field%22%7D%5D%5D%2C%5B%5B%7B%22chave%22%3A%22cpc%22%2C%22connective%22%3A%22e%22%2C%22estrutura%22%3A%22metrica%22%2C%22operador%22%3A%22%3C%22%2C%22needConvertToString%22%3Afalse%2C%22valor%22%3A%225%22%7D%5D%5D%5D%7D%5D%7D%7D%2C%22openGraphExplorador%22%3A0%2C%22totalPercent%22%3A1%2C%22showMetricsTotal%22%3A1%2C%22orderBy%22%3A%22custo_total%22%7D%7D)

---

## Filter JSON Structure Reference

```
filtros: {
  "segment": {                          // Dimension filters (optional)
    "filters": [                         // Array of groups — groups are AND'd together
      {
        "groupType": "and_group|or_group",
        "expressions": [                 // Array of OR branches
          [                              // OR branch 1
            [                            // AND conditions within branch
              { filter_expression },      // Condition A
              { filter_expression }       // Condition B (AND'd with A)
            ],
            [                            // Another AND block (AND'd with above)
              { filter_expression }
            ]
          ],
          [                              // OR branch 2 (OR'd with branch 1)
            [
              { filter_expression }
            ]
          ]
        ]
      }
    ]
  },
  "metric": {                           // Metric filters (optional)
    "filters": [ ... same structure ... ]
  }
}
```

### Filter expression fields:
| Field | Value | Description |
|---|---|---|
| `chave` | dimension/metric ID | The field to filter on |
| `connective` | `"e"` | Always "e" (legacy) |
| `estrutura` | `"segmento"` or `"metrica"` | Filter type |
| `operador` | see operators table | Comparison operator |
| `needConvertToString` | `false` | Always false (legacy) |
| `valor` | string, number, or array | Value(s) to compare against |
| `tipo` | `"field"` (optional) | Set when comparing metric vs metric |

### Operators:
| Operator | Type | Description |
|---|---|---|
| `=` | segment/metric/date | Equal to |
| `!=` | segment/metric/date | Not equal to |
| `c` | segment | Contains |
| `!c` | segment | Does not contain |
| `in` | segment | Is one of (array) |
| `!in` | segment | Is not one of (array) |
| `or` | segment | Contains one of (array) |
| `!or` | segment | Does not contain any of (array) |
| `allc` | segment | Contains all of (array) |
| `!allc` | segment | Does not contain all of (array) |
| `vazio` | segment/date | Is empty |
| `!vazio` | segment/date | Is not empty |
| `>` | metric/date | Greater than |
| `>=` | metric/date | Greater than or equal |
| `<` | metric/date | Less than |
| `<=` | metric/date | Less than or equal |
| `between` | metric/date | Is between |
| `!between` | metric/date | Is not between |
