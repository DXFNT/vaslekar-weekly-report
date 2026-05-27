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

| Source | What | How |
|---|---|---|
| Meta Marketing API | W-1 + W-2 account-level metrics | Meta Ads MCP (`ads_get_ad_entities` on account `1783827691983346`) |
| Google Ads | W-1 commentary | Basecamp thread (Adrián Kerekes posts on Monday) |
| Meta sales view | W-1 commentary | Basecamp thread (Peter Volaj posts on Monday) |
| CRM | Orders + revenue | Excel exports from Miroslav T. (`miroslav.tahotny@vaslekar.sk`) — orders sheet + sold-products sheet. Either auto-fetched from Gmail, or attached manually each Monday. |
| Vyťaženosť | Monthly ambulance utilization | Email from Miroslav T. (Thursdays), referenced as last known state |

## Workflow

The skill orchestrates 7 steps. Run them in order:

1. **Resolve closed week**. Today = run date. Closed week = previous Mon→Sun. Previous-period comparison = the week before that.
2. **Fetch CRM data**.
   - If user attached two `.xlsx` files (one with orders, one with sold products) → use them.
   - Otherwise call Gmail MCP `search_threads` with `from:miroslav.tahotny@vaslekar.sk has:attachment newer_than:3d` and download the most recent xlsx attachments.
   - Parse with `scripts/parse_crm_excel.py` to compute: orders, revenue, AOV, product breakdown, per-specialization breakdown of jednorázové vstupy.
3. **Fetch Meta Ads data via MCP**.
   - Call `ads_get_ad_entities` (`level: account`) on Váš Lekár account `1783827691983346` for both weeks.
   - Required fields: `amount_spent, impressions, reach, clicks, cpm, cpc, ctr, frequency, actions:link_click, actions:omni_purchase, actions:page_engagement, cost_per_link_click, cost_per_action_type`.
   - Compute WoW deltas for each metric.
4. **Fetch Google Ads + Meta sales commentary from Basecamp**.
   - Basecamp CLI: `basecamp comments list 9791306636 -p 46381488 --account 5020993 --json --limit 50`.
   - Filter to comments created in the past 7 days from authors Adrián Kerekes (G Ads commentary) and Peter Volaj (Meta sales view).
   - These are the source of Google Ads metrics for the report (Adrián posts CTR/CPC deltas + attributed orders). **Never fabricate G Ads numbers**; if Adrián's comment isn't posted yet, show a "data gap — awaiting weekly commentary" block.
5. **Update HTML report** (`scripts/render_report.py`).
   - Base template: `templates/report-template.html`.
   - Substitutes: dates, all metrics, WoW deltas, product breakdown table, per-spec table, team comment cards (Basecamp comments verbatim, never AI-rewritten), Next Steps recommendations derived from the data.
   - Write output to `dist/vaslekar-weekly-report.html`.
6. **Generate PDF** with WeasyPrint (`scripts/generate_pdf.py`). Output: `dist/vaslekar-weekly-report.pdf`.
7. **Deploy to Netlify** (`scripts/deploy_netlify.py`).
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
| `Reach customers...` landing page | Not signed in to Google Ads in Chrome | Don't try to extract G Ads via Chrome — use Adrián's Basecamp comment instead |
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
