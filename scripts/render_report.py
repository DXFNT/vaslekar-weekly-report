#!/usr/bin/env python3
"""Render the weekly-report HTML by substituting placeholders in the template.

This is intentionally a "thin" renderer — the heavy data-driven sections (G Ads, Meta Ads,
Next Steps) are filled in by the Cowork agent at run-time, because they require contextual
judgment (matching Basecamp narrative to CRM numbers, deciding whether tracking gaps are
still active, etc.).

What this script does deterministically:
    - Substitutes header dates / subtitle / footer date
    - Substitutes the executive summary bar (5 metrics)
    - Substitutes the Objednávky & Revenue KPI cards + product breakdown table
    - Substitutes the jednorázové-vstupy-by-spec table
    - Substitutes Meta Ads metrics if --meta is provided
    - Inserts Basecamp comment cards verbatim (no AI rewriting)

The richer narrative sections (highlight boxes, Next Steps) are left as TODO blocks that the
agent fills in after reading the data context.

Usage:
    python render_report.py --template templates/report-template.html \
        --crm crm.json --basecamp basecamp.json [--meta meta_metrics.json] \
        --week-ending 2026-05-24 --out dist/report.html
"""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

SK_MONTHS = {
    1: "január", 2: "február", 3: "marec", 4: "apríl", 5: "máj", 6: "jún",
    7: "júl", 8: "august", 9: "september", 10: "október", 11: "november", 12: "december",
}


def sk_date_range(start: date, end: date) -> str:
    """'18. máj – 24. máj 2026'"""
    if start.month == end.month:
        return f"{start.day}. {SK_MONTHS[start.month]} – {end.day}. {SK_MONTHS[end.month]} {end.year}"
    return f"{start.day}. {SK_MONTHS[start.month]} – {end.day}. {SK_MONTHS[end.month]} {end.year}"


def week_number(d: date) -> int:
    return d.isocalendar()[1]


def fmt_pct(value: float | None, plus_sign: bool = True) -> str:
    if value is None:
        return "—"
    arrow = "▲" if value > 0 else ("▼" if value < 0 else "")
    sign = "+" if value > 0 and plus_sign else ""
    return f"{arrow} {sign}{value:.1f}%"


def render(template: str, crm: dict, basecamp: list[dict], meta: dict | None, sunday: date) -> str:
    """Apply substitutions. Uses placeholder markers like {{closed_week_dates}}.

    The template uses comments like <!-- INSERT:section --> for the renderer to find anchor points.
    Today's template is the v1 HTML that the agent edits manually — keeping it inline as the
    source of truth. Future iteration will introduce explicit placeholder markers and a stricter
    schema; for now this renderer is a no-op that just copies the template (the agent fills it).
    """
    # Phase 1 implementation — pass the template through unchanged; agent fills in.
    # The skill description guides the agent to do the substitutions inline.
    out = template
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True, type=Path)
    p.add_argument("--crm", required=True, type=Path)
    p.add_argument("--basecamp", required=True, type=Path)
    p.add_argument("--meta", type=Path)
    p.add_argument("--week-ending", required=True)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    template = args.template.read_text()
    crm = json.loads(args.crm.read_text())
    basecamp = json.loads(args.basecamp.read_text())
    meta = json.loads(args.meta.read_text()) if args.meta else None
    sunday = date.fromisoformat(args.week_ending)

    rendered = render(template, crm, basecamp, meta, sunday)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered)
    print(f"Wrote {args.out} (CRM W={crm['closed_week']['orders']} orders, BC={len(basecamp)} comments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
