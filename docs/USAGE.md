# NeoPilot Usage Guide

## Connecting to NeoDash

### Connect your first instance

> "Connect to my NeoDash instance with slug 'loreal' and API token 'abc123'"

NeoPilot will test the connection, detect your language, and save it.

### Manage multiple instances

> "List my connected instances"
> "Switch to the 'mdlz' instance"
> "Disconnect 'tpv'"

## Exploring Your Data

### Discover dashboards

> "What dashboards are available?"
> "Search for dashboards with 'Amazon' in the name"
> "Show me the components in dashboard 3000004"

### Understand available metrics and dimensions

> "What metrics can I query?"
> "List all available dimensions"

## Querying Data

### Basic query with the Explorer

> "Show me total cost and clicks by campaign for last week"

NeoPilot will use `query_data` with:
- dimensions: `["campanha"]`
- metrics: `["custo_total", "cliques"]`
- appropriate date range

### Query with time breakdown

> "Show me daily spend by platform for January 2025"

Uses `time_breakdown: "dia"` and `dimensions: ["veiculo"]`.

### Compare periods

> "Compare this month's conversions by brand vs last month"

Uses `compare_date_start` and `compare_date_end` parameters.

### Dashboard component data

> "Get the data from the 'KPIs Gerais' component in dashboard 3000004 for the last 7 days"

Uses `get_component_data` with the component and dashboard IDs.

## Setting Up Your Context

### Guided setup

> "Help me set up my NeoPilot preferences"

### Manual configuration

> "Set my dashboards of interest to '3000001' and '3000002'"
> "My key metrics are cost per click, CTR, and conversions"
> "Add a note: I only manage the Amazon Ads player for Cerave"

### View preferences

> "What are my current NeoPilot preferences?"

## Tips

1. **Always specify dates**: NeoPilot needs a date range for data queries. Be explicit: "last 7 days", "January 2025", "2025-01-01 to 2025-01-31".

2. **Use labels or IDs**: You can refer to metrics/dimensions by either their label ("Cost per Click") or their ID ("cpc"). The LLM will figure it out.

3. **Watch for truncation**: If you get exactly 500 rows, the data might be truncated. Increase the limit or narrow your dimensions.

4. **Totals are computed by NeoDash**: The totals you see are always calculated server-side, not by the LLM.

5. **Filters are coming soon**: If you need filtered data, use the component-based approach (`get_component_data`) which includes pre-configured filters from the dashboard.
