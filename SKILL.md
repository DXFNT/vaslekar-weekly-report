---
name: vaslekar-weekly-report
description: Generate the weekly performance report for client "Váš Lekár" (Dexfinity account). Pulls Meta Ads data via Meta Marketing API MCP, Google Ads commentary + Meta sales view from Basecamp thread, and order/revenue data from client CRM Excel exports. Produces an HTML + PDF report, deploys to Netlify. MANDATORY TRIGGERS - use this skill whenever the user wants to "generate weekly report for Vas Lekar", "vaslekar weekly", "vaslekar report", "týždenný report Váš Lekár", "weekly Vaslekar", or whenever a scheduled task references this report. Designed to run autonomously on Monday mornings for the prior closed week (Mon→Sun).
---

# Váš Lekár — Weekly Performance Report

Automated weekly report for the Dexfinity-managed client Poliklinika Váš Lekár (healthcare).

## Context
- **Client**: Váš Lekár (Bratislava poliklinika)
- **Account Manager**: Jozef Zelenay
- **Primary KPI**: PNO (Podiel Nákladov na Obrate) = total ad spend / total revenue × 100
- **Report cadence**: Every Monday morning for the prior closed week (Mon→Sun)

## Inputs

| Source | What | How (PRIMARY) |
|---|---|---|
| **Meta Marketing API** | Meta Ads raw metrics (W-1 + W-2 account-level) | **Meta MCP** — `ads_get_ad_entities` (level=account) on `1783827691983346` |
| **Google Ads Reporting API** | Google Ads raw metrics (W-1 + W-2, account + per-campaign) | **Supermetrics MCP** (`data_query` on `ds_id=AW`, account `2742476958` for Váš Lekár). Already authenticated via `matej.astary@dexfinity.com`. Fields: `Impressions,Clicks,Cost_eur,Ctr,CPC,Conversions,CostPerConversion,ConversionRate`. **Fallback**: Chrome MCP scrape of `ads.google.com` UI if Supermetrics rate-limited. |
| Basecamp thread | **Optimization context only** (NOT raw numbers): Adrián K. = G Ads narrative + decisions, Peter V. = Meta sales view narrative | `basecamp comments list 9791306636 -p 46381488 --account 5020993` — inserted verbatim into Team Comments section, never as substitute for API/UI data |
| CRM | Orders + revenue | Excel exports from Miroslav T. (`miroslav.tahotny@vaslekar.sk`) — orders sheet + sold-products sheet. Either auto-fetched from Gmail, or attached manually each Monday. |
| Vyťaženosť | Monthly ambulance utilization | Email from Miroslav T. (Thursdays), referenced as last known state |

**Source-of-truth hierarchy:**
1. Meta Ads numbers → Meta Marketing API (MCP). Always.
2. Google Ads numbers → Chrome MCP scrape of Google Ads UI. Always.
3. Basecamp commentary is **never** a substitute for raw numbers — only adds narrative ("Plast. chirurgia CTR vyskočilo, optimalizujeme negatívne KW") and human-judgment Next Steps.
4. If a primary source fails (Chrome not logged in, MCP error), render a clear "data gap" block. Do NOT silently substitute the Basecamp narrative for the missing numbers.

## Workflow

The skill orchestrates 7 steps. Run them in order:

1. **Resolve closed week**. Today = run date. Closed week = previous Mon→Sun. Previous-period comparison = the week before that.
2. **Fetch CRM data**.
   - If user attached two `.xlsx` files (one with orders, one with sold products) → use them.
   - Otherwise call Gmail MCP `search_threads` with `from:miroslav.tahotny@vaslekar.sk has:attachment newer_than:3d` and download the most recent xlsx attachments.
   - Parse with `scripts/parse_crm_excel.py` to compute: orders, revenue, AOV, product breakdown, per-specialization breakdown of jednorázové vstupy.
3. **Fetch Meta Ads data via Meta MCP**.
   - **Account-level totals**: `ads_get_ad_entities` (`level: account`) on `1783827691983346` for both weeks. Fields: `amount_spent, impressions, reach, clicks, cpm, cpc, ctr, frequency, actions:link_click, actions:omni_purchase, actions:page_engagement, cost_per_link_click, cost_per_action_type`.
   - **Campaign-level breakdown for performance vs boosting split**: `ads_get_ad_entities` (`level: campaign`) with filtering `[{field: "campaign.amount_spent", operator: "GREATER_THAN", value: ["0"]}]`, sort `amount_spent_descending`, limit 30. Fields: `name, objective, amount_spent, impressions, actions:omni_purchase`.
   - **Categorize each campaign by objective**:
     - `OUTCOME_SALES` → **Performance** bucket (e.g. `dex-sales-*`)
     - `OUTCOME_ENGAGEMENT`, `OUTCOME_AWARENESS` → **Boosting** bucket (e.g. `5/26 Poliklinika boost - engagement / ThruPlay`)
     - `LINK_CLICKS` with awareness intent (e.g. `dex-klinicka_studia-traffic`) → **Other** bucket; flag separately, never lump with performance
   - Compute the split tables: `(performance / boosting / other) × (W21 / W20 / WoW%)`. Surface in report.
   - Compute WoW deltas for each metric.
4. **Fetch Google Ads data via Supermetrics MCP** (PRIMARY).
   - Tool: `mcp__<supermetrics>__data_query`
   - `ds_id`: `AW` (Google Ads)
   - `ds_accounts`: `2742476958` (Váš Lekár, in Dexfinity MCC)
   - `fields`: `Impressions,Clicks,Cost_eur,Ctr,CPC,Conversions,CostPerConversion,ConversionRate`
   - `date_range_type`: `custom` with `start_date` + `end_date` for the closed week (Mon→Sun), then same query for the previous week.
   - Returns `schedule_id` → poll with `get_async_query_results` until status=`completed`.
   - For per-campaign breakdown, add `Campaign` as a dimension and increase `max_rows`.
   - Compute WoW deltas: cost, clicks, impressions, CTR, CPC, conversions, CPA, conv. rate — account-level and per-campaign.
   - **Cross-validate** with Adrián's Basecamp comment (CTR / CPC numbers should match within rounding).
   - **Fallback if Supermetrics is rate-limited or auth-expired**: Chrome MCP scrape of `ads.google.com` (see `scripts/fetch_google_ads.py`). If both fail, render "data gap" — do NOT substitute Basecamp narrative for raw numbers.
5. **Fetch optimization commentary from Basecamp**.
   - Basecamp CLI: `basecamp comments list 9791306636 -p 46381488 --account 5020993 --json --limit 50`.
   - Filter to comments created in the past 7 days from Adrián Kerekes (G Ads optimization narrative) and Peter Volaj (Meta sales view narrative).
   - These go **verbatim** into the Team Comments section as context layered on top of the API/UI numbers. They are not the source of truth for spend/clicks/impressions.
6. **Update HTML report** (`scripts/render_report.py`).
   - Base template: `templates/report-template.html`.
   - Substitutes: dates, all metrics, WoW deltas, product breakdown table, per-spec table, team comment cards (Basecamp comments verbatim, never AI-rewritten), Next Steps recommendations derived from the data.
   - Write output to `dist/vaslekar-weekly-report.html`.
7. **Generate PDF** with WeasyPrint (`scripts/generate_pdf.py`). Output: `dist/vaslekar-weekly-report.pdf`.
8. **Deploy to Netlify** (`scripts/deploy_netlify.py`).
   - Site ID: `0a40a6e4-e854-4438-b3a2-145112f9d99d`
   - Uploads as `/index.html` via file digest API.
   - Verifies `https://dexfinity-vaslekar.netlify.app` returns 200 with the new content.

## Hard rules

1. **Closed weeks only.** Mon 00:00 → Sun 23:59. Never use arbitrary 7-day rolling windows.
2. **Never fabricate numbers.** If a data source is unavailable, render a "data gap" block. Do not estimate Google Ads spend from CTR/CPC alone.
3. **Only real Basecamp comments.** Comment cards must reflect actual posts from Adrián K. / Peter V. — never AI-rewritten or invented. Cite date and full author name.
4. **Meta end-date in URL params is exclusive.** When constructing manual Meta Ads URLs (fallback), add +1 day to the end date.
5. **Pixel disclaimer.** Until W21 (25.5.2026), the report carried a "40+ days without purchase event" warning. W21 broke this — 2 omni_purchase events fired. Keep tracking-gap language up to date with reality (don't carry stale warnings).
6. **Keep Dexfinity / Váš Lekár branding intact.** Logos: `https://vaslekar.sk/wp-content/uploads/2022/06/vaslekar_logo_light.svg` (header) and `https://www.dexfinity.com/wp-content/uploads/2021/02/Logo-Small-Light-Landscape.svg` (footer, on navy background).
7. **Always split Meta spend by objective** — Performance (OUTCOME_SALES) vs Boosting (OUTCOME_ENGAGEMENT / OUTCOME_AWARENESS) vs Other (LINK_CLICKS / traffic / clinical / one-off). Render two PNOs: **Performance PNO** (G Ads + Meta performance / revenue) for sales attribution, and **Total PNO** (all paid spend / revenue) for full nákladová rovnica. AM-ovia chcú vidieť oboje, a klient si zaslúži vedieť, koľko ide do brand-buildingu vs okamžitej predajnej výkonnosti.

## Environment variables

Required in `.env`:
- `NETLIFY_TOKEN` — Netlify Personal Access Token for the Dexfinity-Váš Lekár site
- `NETLIFY_SITE_ID` — `0a40a6e4-e854-4438-b3a2-145112f9d99d`
- `BASECAMP_ACCOUNT_ID` — `5020993`
- `BASECAMP_PROJECT_ID` — `46381488`
- `BASECAMP_MESSAGE_ID` — `9791306636` ("Weekly reports comments" thread)
- `META_AD_ACCOUNT_ID` — `1783827691983346`

Gmail and Meta MCP authentication is handled through Cowork connectors (no static credentials needed).

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Meta MCP error "Unsupported field" | Field name changed | Run `ads_get_field_context` to refresh schema, use `amount_spent` not `spend`, `actions:omni_purchase` not `purchase`, etc. |
| Basecamp 404 on message ID | Wrong message ID type | Use `basecamp messages show <id>` not `basecamp show <id>` — the latter hits `/recordings/` endpoint |
| WeasyPrint dlopen libgobject | Mac is missing pango/glib | Run PDF generation in the Linux sandbox, not on the Mac shell |
| `Reach customers...` landing page when navigating to ads.google.com | Chrome MCP session not authenticated to Google Ads | Ask the user to sign in to Google Ads in the connected Chrome before re-running. Render a "data gap — Chrome session not authenticated" block in the meantime — **do NOT** substitute Adrián's Basecamp commentary for the raw numbers. |
| Chrome MCP can reach Google Ads but landing on MCC, not the Váš Lekár sub-account | Wrong OCID or not navigated into the client account | Capture the correct `ocid=` query param from the Váš Lekár account URL once, store it in `.env` as `GADS_OCID` |
| Empty Basecamp comment list for W21 | Adrián K. hasn't posted yet (Monday morning) | Render placeholder card; the scheduled task will refresh on next run |

## Scheduling

Set up via Cowork's `/schedule`:
```
/schedule weekly Monday 08:00 — run vaslekar-weekly-report skill
```

Run is autonomous (user not present). Make reasonable defaults, note assumptions in the report, never block on missing data.

## See also

- `templates/report-template.html` — full HTML structure with placeholder markers
- `scripts/parse_crm_excel.py` — CRM Excel → JSON aggregates
- `scripts/render_report.py` — JSON aggregates → HTML
- `scripts/generate_pdf.py` — HTML → PDF via WeasyPrint
- `scripts/deploy_netlify.py` — HTML → Netlify deploy
- `README.md` — human-facing setup instructions
