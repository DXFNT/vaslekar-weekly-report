#!/usr/bin/env python3
"""Fetch Google Ads weekly metrics via Chrome MCP.

This script is a STUB documenting the steps the Cowork agent should take when running the
skill — the actual Chrome MCP tools (`navigate`, `javascript_tool`, `get_page_text`,
`browser_batch`) are invoked by the agent, not by Python. The agent calls this script's
docstring as a runbook.

PRIMARY SOURCE for Google Ads numbers. Adrián's Basecamp commentary is NOT a substitute —
it's optimization narrative layered on top of these raw numbers.

Runbook (agent-side, via Chrome MCP):

    1. Ensure a connected Chrome browser exists:
         mcp__Claude_in_Chrome__list_connected_browsers
       If none, ask the user to install/connect the Chrome extension.

    2. Create a fresh tab in the MCP tab group:
         mcp__Claude_in_Chrome__tabs_create_mcp

    3. Navigate to the Váš Lekár Google Ads account:
         mcp__Claude_in_Chrome__navigate
           url:  https://ads.google.com/aw/campaigns?ocid=${GADS_OCID}

       The OCID is the customer-account identifier; once captured from the URL of a
       logged-in Váš Lekár session, store it in .env as GADS_OCID. Without it, ads.google.com
       redirects to the business.google.com landing page (= "not logged in" signal).

    4. Wait for the campaigns table to render, then set the date picker to the closed week:
         mcp__Claude_in_Chrome__find          (locate "Date range" button)
         mcp__Claude_in_Chrome__left_click    (open picker)
         mcp__Claude_in_Chrome__type          (enter start YYYY-MM-DD)
         mcp__Claude_in_Chrome__key tab       (enter end YYYY-MM-DD)
         mcp__Claude_in_Chrome__find + click  ("Apply")

    5. Extract the campaigns table:
         mcp__Claude_in_Chrome__javascript_tool
           text: |
             new Promise(r => setTimeout(() => {
               const rows = [...document.querySelectorAll('material-row, .campaign-row, tr')]
                 .map(r => r.innerText)
                 .filter(t => t.trim().length);
               r(rows);
             }, 4000))

       Returns a list of row strings; parse client-side to extract:
         spend, clicks, impressions, ctr, cpc, conversions, cpa, conv_rate
       at account total + per campaign.

    6. Repeat steps 4–5 for the previous week.

    7. Compute WoW deltas and write JSON:
         {
           "closed_week": {
             "start": "2026-05-18", "end": "2026-05-24",
             "totals": {"spend_eur": …, "clicks": …, "impressions": …, "ctr_pct": …,
                        "cpc_eur": …, "conversions": …, "cpa_eur": …, "conv_rate_pct": …},
             "by_campaign": [{"name": "SRCH - Neurológia", "spend_eur": …, "clicks": …, …}, …]
           },
           "prev_week": { … same shape … },
           "wow": { "spend_pct": …, "clicks_pct": …, … }
         }

Failure modes:
    - Landing page is business.google.com/google-ads → session not authenticated. Render
      a "data gap" block in the report. Do NOT call Adrián's Basecamp comment a "data source".
    - Landing page is the MCC, not the Váš Lekár sub-account → wrong OCID. Fix .env.
    - Table parse returns 0 rows after 4s → page is still rendering. Retry with longer wait.

This file exists so the SKILL.md can reference it as `scripts/fetch_google_ads.py` for
consistency with the other steps. The actual fetch happens via Chrome MCP, agent-driven.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(__doc__, file=sys.stderr)
    print(
        "\nThis script is an agent runbook, not a standalone fetcher. "
        "The Cowork agent calling this skill performs the Chrome MCP actions described above.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
