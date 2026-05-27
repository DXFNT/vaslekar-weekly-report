#!/usr/bin/env python3
"""Orchestrator — runs the full weekly-report pipeline end-to-end.

Pipeline:
    1. Resolve closed week dates (Mon→Sun ending on --week-ending; defaults to last Sunday).
    2. Parse CRM xlsx files → JSON aggregates.
    3. Fetch Basecamp comments (since the Monday of the closed week).
    4. (Meta Marketing API fetch is performed by the Cowork host calling this skill — see SKILL.md.
        The host should drop a `meta_metrics.json` into the working dir before invoking this script,
        with keys 'closed_week' and 'prev_week', each having amount_spent/impressions/reach/clicks/
        cpm/cpc/ctr/frequency/link_clicks/page_engagement/omni_purchases.)
    5. Render HTML.
    6. Generate PDF.
    7. Deploy to Netlify.

Usage:
    python run_report.py \
        --orders orders.xlsx \
        --products products.xlsx \
        --meta meta_metrics.json \
        --week-ending 2026-05-24
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATES = ROOT / "templates"


def last_sunday(today: date | None = None) -> date:
    today = today or date.today()
    # Monday=0 … Sunday=6
    return today - timedelta(days=(today.weekday() + 1) % 7 or 7)


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, check=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Run the Váš Lekár weekly report end-to-end")
    p.add_argument("--orders", required=True, type=Path, help="zoznam_objednavok_klientov.xlsx")
    p.add_argument("--products", type=Path, help="export_predanych_produktov.xlsx (optional)")
    p.add_argument("--meta", type=Path, help="meta_metrics.json from Meta MCP (optional; data-gap block if missing)")
    p.add_argument(
        "--week-ending",
        help="Sunday of the closed week (YYYY-MM-DD). Defaults to last Sunday.",
    )
    p.add_argument("--dist", type=Path, default=ROOT / "dist")
    p.add_argument("--skip-deploy", action="store_true", help="Render HTML+PDF but skip Netlify deploy")
    args = p.parse_args()

    sunday = date.fromisoformat(args.week_ending) if args.week_ending else last_sunday()
    monday = sunday - timedelta(days=6)
    args.dist.mkdir(parents=True, exist_ok=True)

    crm_json = args.dist / "crm.json"
    basecamp_json = args.dist / "basecamp.json"
    html_out = args.dist / "vaslekar-weekly-report.html"
    pdf_out = args.dist / "vaslekar-weekly-report.pdf"

    # Step 2: CRM
    cmd = [
        sys.executable,
        str(SCRIPTS / "parse_crm_excel.py"),
        "--orders",
        str(args.orders),
        "--week-ending",
        sunday.isoformat(),
        "--out",
        str(crm_json),
    ]
    if args.products:
        cmd += ["--products", str(args.products)]
    run(cmd)

    # Step 3: Basecamp
    run(
        [
            sys.executable,
            str(SCRIPTS / "fetch_basecamp.py"),
            "--since",
            monday.isoformat(),
            "--out",
            str(basecamp_json),
        ]
    )

    # Step 5: Render
    render_cmd = [
        sys.executable,
        str(SCRIPTS / "render_report.py"),
        "--template",
        str(TEMPLATES / "report-template.html"),
        "--crm",
        str(crm_json),
        "--basecamp",
        str(basecamp_json),
        "--week-ending",
        sunday.isoformat(),
        "--out",
        str(html_out),
    ]
    if args.meta:
        render_cmd += ["--meta", str(args.meta)]
    run(render_cmd)

    # Step 6: PDF
    run(
        [
            sys.executable,
            str(SCRIPTS / "generate_pdf.py"),
            "--html",
            str(html_out),
            "--pdf",
            str(pdf_out),
        ]
    )

    # Step 7: Deploy
    if not args.skip_deploy:
        if not os.environ.get("NETLIFY_TOKEN"):
            print("WARN: NETLIFY_TOKEN not set; skipping deploy", file=sys.stderr)
        else:
            run([sys.executable, str(SCRIPTS / "deploy_netlify.py"), "--html", str(html_out)])

    print(f"\nDone. HTML: {html_out}\n     PDF:  {pdf_out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
