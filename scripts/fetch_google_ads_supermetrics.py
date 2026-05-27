#!/usr/bin/env python3
"""Fetch Google Ads weekly metrics via Supermetrics MCP (Reporting API wrapper).

PRIMARY source for Google Ads numbers. Chrome MCP scrape (fetch_google_ads.py) is a fallback.

Agent-side runbook (the Cowork agent calling this skill performs these tool calls — this
script is the documented contract):

    1. Discover data sources to confirm AW (Google Ads) is AUTHENTICATED:
         mcp__<supermetrics>__data_source_discovery(filter="google ads", compress=true)

    2. Confirm account access:
         mcp__<supermetrics>__accounts_discovery(ds_id="AW", filter="vaslekar")
       Expect: account_id "2742476958", account_name "Vas lekar", group "Dexfinity MCC"

    3. Query the closed week:
         mcp__<supermetrics>__data_query(
             ds_id="AW",
             ds_accounts="2742476958",
             fields="Impressions,Clicks,Cost_eur,Ctr,CPC,Conversions,CostPerConversion,ConversionRate",
             date_range_type="custom",
             start_date="<MONDAY of closed week>",
             end_date="<SUNDAY of closed week>",
             compress=true,
         )
       Returns a schedule_id. Immediately poll:
         mcp__<supermetrics>__get_async_query_results(schedule_id=<id>, compress=true)
       Repeat until status="completed".

    4. Repeat step 3 for the previous week.

    5. For per-campaign breakdown, add `Campaign` as a dimension and set max_rows ~100.

    6. Cross-validate vs Adrián's Basecamp commentary (CTR/CPC should match within rounding).
       If they diverge substantially, surface the conflict — don't silently pick one.

    7. Compute WoW deltas and emit JSON in this shape:

        {
          "closed_week": {
            "start": "2026-05-18", "end": "2026-05-24",
            "totals": {
              "cost_eur": 311.71, "impressions": 9529, "clicks": 1406,
              "ctr": 0.1475, "cpc": 0.2217,
              "conversions": 490.1, "cost_per_conversion": 0.636,
              "conversion_rate": 0.3486
            },
            "by_campaign": [...]
          },
          "prev_week": { ... same shape ... },
          "wow": { "cost_pct": +2.0, "clicks_pct": +0.07, ... }
        }

Failure modes:
    - Supermetrics returns "authentication required" → relink the Supermetrics connector
      in Cowork; auth is via matej.astary@dexfinity.com.
    - Returns empty/zero data for a known-active campaign week → check that the date range
      uses the correct timezone (default UTC; Slovak ad accounts report in CET).
    - 429 rate limit → fall back to Chrome MCP scrape (scripts/fetch_google_ads.py).

This script is a runbook for the agent. The actual MCP calls happen in the host agent
session, not by running this file. Run with `--help` for this docstring.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(__doc__, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
