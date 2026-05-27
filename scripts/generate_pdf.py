#!/usr/bin/env python3
"""Convert the rendered weekly-report HTML to PDF via WeasyPrint.

Run inside a Linux environment with pango/glib system libs installed.
(On macOS, install with `brew install pango cairo glib`.)

Usage:
    python generate_pdf.py --html dist/report.html --pdf dist/report.pdf
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="HTML → PDF via WeasyPrint")
    p.add_argument("--html", required=True, type=Path)
    p.add_argument("--pdf", required=True, type=Path)
    args = p.parse_args()

    # Import lazily so help text still works on systems without WeasyPrint installed
    from weasyprint import HTML

    args.pdf.parent.mkdir(parents=True, exist_ok=True)
    HTML(str(args.html)).write_pdf(str(args.pdf))
    print(f"Wrote {args.pdf} ({args.pdf.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
