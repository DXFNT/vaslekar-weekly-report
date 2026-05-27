# Váš Lekár — Weekly Report Skill

A Cowork skill that generates the weekly performance report for client **Poliklinika Váš Lekár** (Dexfinity-managed account). Pulls data from Meta Marketing API, Basecamp commentary, and client CRM Excel exports — renders an HTML + PDF report and deploys to Netlify.

## What it produces

- `dist/vaslekar-weekly-report.html` — interactive HTML report
- `dist/vaslekar-weekly-report.pdf` — print-ready PDF
- Deploy on `https://dexfinity-vaslekar.netlify.app` (shared with client)

## Quick start

### Prerequisites

- **Cowork** (or Claude Agent SDK) with:
  - Gmail connector (for fetching CRM emails)
  - Meta Marketing API MCP (for ad account data)
- **Basecamp CLI** installed locally (`brew install basecamp-cli`) and authenticated to the Dexfinity workspace
- **Python 3.10+** with `openpyxl`, `weasyprint`, `requests`
- **Netlify** PAT scoped to the dexfinity-vaslekar site
- **System libs** for WeasyPrint: `pango`, `glib`, `cairo` (Linux: `apt install libpango-1.0-0 libpangoft2-1.0-0`; Mac: `brew install pango`)

### Installation

```bash
git clone https://github.com/DXFNT/vaslekar-weekly-report.git
cd vaslekar-weekly-report
pip install -r requirements.txt
cp .env.example .env  # fill in NETLIFY_TOKEN
```

### Run manually

```bash
python scripts/run_report.py \
  --week-ending 2026-05-24 \
  --orders-xlsx /path/to/orders.xlsx \
  --products-xlsx /path/to/products.xlsx
```

Outputs `dist/vaslekar-weekly-report.{html,pdf}` and deploys to Netlify.

### Run on schedule (Cowork)

In Cowork mode:

```
/schedule every Monday at 08:00 — generate vaslekar weekly report
```

The skill auto-resolves the closed week, pulls Gmail attachments, fetches MCP data, polls Basecamp, builds the report, and deploys — without user input.

## Architecture

```
┌─────────────────┐
│ Scheduled task  │  (Monday 08:00)
└────────┬────────┘
         ▼
┌─────────────────────────────────────────────┐
│ run_report.py                               │
│ ├── Step 1: resolve closed week dates       │
│ ├── Step 2: fetch CRM xlsx (Gmail or local) │──▶ parse_crm_excel.py
│ ├── Step 3: fetch Meta data (MCP)           │──▶ Meta Marketing API
│ ├── Step 4: fetch Basecamp commentary       │──▶ basecamp CLI
│ ├── Step 5: render HTML                     │──▶ render_report.py
│ ├── Step 6: generate PDF                    │──▶ generate_pdf.py (WeasyPrint)
│ └── Step 7: deploy to Netlify               │──▶ deploy_netlify.py
└─────────────────────────────────────────────┘
```

## Data sources

| Source | What | Cadence | Owner |
|---|---|---|---|
| **Meta Marketing API** (Cowork Meta MCP) | Meta Ads raw metrics | On demand | Dexfinity (MCP token) |
| **Google Ads Reporting API** (Supermetrics MCP) | Google Ads raw metrics, account + per-campaign | On demand | Dexfinity (Supermetrics token via `matej.astary@dexfinity.com`) — fallback to Chrome MCP scrape if rate-limited |
| Basecamp "Weekly reports comments" thread (msg `9791306636`) | Optimization narrative — **NOT raw numbers** | Mondays | Adrián K. (G Ads context), Peter V. (Meta sales context) |
| CRM orders + products xlsx | Orders, revenue, AOV, product mix | Mondays | Miroslav Tahotný (`miroslav.tahotny@vaslekar.sk`) |
| Vyťaženosť ambulancií | Per-spec utilization % | Thursdays | Miroslav Tahotný |

**Source-of-truth rule**: raw spend/clicks/impressions/conversions for both ad platforms come from the API / UI scrape. Basecamp commentary is layered on top as narrative and never substitutes for missing numbers — if Chrome can't reach Google Ads (no session), the report renders a "data gap" block, not Adrián's commentary in its place.

## Hard rules baked into the skill

1. **Closed weeks only** — Mon 00:00 → Sun 23:59. Never arbitrary 7-day windows.
2. **Never fabricate numbers.** Missing source = "data gap" block. No estimates.
3. **Only real Basecamp comments** in the team-comments section. Never AI-paraphrased.
4. **Pixel state must reflect reality.** Stale "no purchases" warnings must be removed when events fire.

## Repo layout

```
vaslekar-weekly-report/
├── SKILL.md                      # Cowork skill definition (frontmatter + instructions)
├── README.md                     # this file
├── requirements.txt              # python deps
├── .env.example                  # env var template
├── templates/
│   └── report-template.html      # full HTML structure (1300+ lines)
├── scripts/
│   ├── run_report.py             # orchestrator
│   ├── parse_crm_excel.py        # orders.xlsx + products.xlsx → JSON aggregates
│   ├── fetch_google_ads.py       # Chrome MCP runbook — agent-driven scrape of Google Ads UI
│   ├── fetch_basecamp.py         # basecamp CLI wrapper — optimization narrative
│   ├── render_report.py          # JSON + template → HTML
│   ├── generate_pdf.py           # HTML → PDF
│   └── deploy_netlify.py         # HTML → Netlify file-digest deploy
└── dist/                         # outputs (gitignored)
```

## Troubleshooting

See **Common failure modes** table in `SKILL.md`.

## License

Internal — Dexfinity s.r.o. Not for public redistribution.

## Maintainers

- Matej Aštary — Partner, CreAI (`matej.astary@dexfinity.com`)
- Jozef Zelenay — Account Manager (`jozef.zelenay@dexfinity.com`)
