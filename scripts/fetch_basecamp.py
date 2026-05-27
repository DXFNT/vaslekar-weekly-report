#!/usr/bin/env python3
"""Fetch comments from the Basecamp 'Weekly reports comments' thread (Dexfinity & Váš Lekár project).

Returns the comments posted in the last 7 days as JSON, with HTML stripped to plain text.

Usage:
    python fetch_basecamp.py --since 2026-05-18 --out basecamp_comments.json

Requires: `basecamp` CLI installed and authenticated (`brew install basecamp-cli`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from html import unescape
from pathlib import Path

BASECAMP_BIN = os.environ.get("BASECAMP_BIN", "/opt/homebrew/bin/basecamp")
ACCOUNT = os.environ.get("BASECAMP_ACCOUNT_ID", "5020993")
PROJECT = os.environ.get("BASECAMP_PROJECT_ID", "46381488")
MESSAGE = os.environ.get("BASECAMP_MESSAGE_ID", "9791306636")


def strip_html(html: str) -> str:
    if not html:
        return ""
    # Remove bc-attachment blocks (file attachments, mentions, etc.)
    html = re.sub(r"<bc-attachment[^>]*>.*?</bc-attachment>", "", html, flags=re.S)
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</p>", "\n", html)
    html = re.sub(r"</li>", "\n", html)
    html = re.sub(r"<[^>]+>", "", html)
    return unescape(html).strip()


def fetch_comments(limit: int = 50) -> list[dict]:
    cmd = [
        BASECAMP_BIN,
        "comments",
        "list",
        MESSAGE,
        "-p",
        PROJECT,
        "--account",
        ACCOUNT,
        "--json",
        "--limit",
        str(limit),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    if not payload.get("ok"):
        raise RuntimeError(f"Basecamp CLI returned ok=false: {payload}")
    return payload["data"]


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch weekly Basecamp comments → JSON")
    p.add_argument(
        "--since",
        required=True,
        help="ISO date — return comments created on or after this date (typically the Monday of the closed week)",
    )
    p.add_argument("--out", type=Path, default=Path("basecamp_comments.json"))
    args = p.parse_args()

    raw = fetch_comments()
    since = args.since  # ISO compare on the prefix is fine
    filtered = []
    for c in raw:
        if c.get("created_at", "")[:10] < since:
            continue
        filtered.append(
            {
                "author": c["creator"]["name"],
                "email": c["creator"]["email_address"],
                "created_at": c["created_at"],
                "body": strip_html(c["content"]),
                "app_url": c.get("app_url"),
            }
        )

    args.out.write_text(json.dumps(filtered, ensure_ascii=False, indent=2))
    print(f"Wrote {len(filtered)} comments since {since} to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
