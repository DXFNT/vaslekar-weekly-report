#!/usr/bin/env python3
"""Deploy the rendered HTML report to Netlify as /index.html on the dexfinity-vaslekar site.

Uses the Netlify file-digest API:
    1. POST /sites/{id}/deploys with {"files": {"/index.html": "<sha1>"}}
    2. PUT /deploys/{id}/files/index.html with the file body
    3. Poll deploy state until "ready"

Required env:
    NETLIFY_TOKEN    — Personal Access Token
    NETLIFY_SITE_ID  — defaults to 0a40a6e4-e854-4438-b3a2-145112f9d99d (dexfinity-vaslekar)

Usage:
    python deploy_netlify.py --html dist/report.html
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import requests

API = "https://api.netlify.com/api/v1"
DEFAULT_SITE = "0a40a6e4-e854-4438-b3a2-145112f9d99d"


def sha1_of(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()


def deploy(html: Path, token: str, site_id: str) -> dict:
    sha = sha1_of(html)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create deploy with file manifest
    r = requests.post(
        f"{API}/sites/{site_id}/deploys",
        headers={**headers, "Content-Type": "application/json"},
        json={"files": {"/index.html": sha}},
        timeout=30,
    )
    r.raise_for_status()
    deploy_obj = r.json()
    deploy_id = deploy_obj["id"]

    # 2. Upload file body
    r = requests.put(
        f"{API}/deploys/{deploy_id}/files/index.html",
        headers={**headers, "Content-Type": "application/octet-stream"},
        data=html.read_bytes(),
        timeout=60,
    )
    r.raise_for_status()

    # 3. Poll for ready state
    for _ in range(20):
        r = requests.get(f"{API}/deploys/{deploy_id}", headers=headers, timeout=10)
        r.raise_for_status()
        d = r.json()
        state = d.get("state")
        if state in ("ready", "error"):
            return d
        time.sleep(2)
    return deploy_obj


def main() -> int:
    p = argparse.ArgumentParser(description="Deploy weekly report HTML to Netlify")
    p.add_argument("--html", required=True, type=Path)
    args = p.parse_args()

    token = os.environ.get("NETLIFY_TOKEN")
    if not token:
        print("ERROR: NETLIFY_TOKEN env var is required", file=sys.stderr)
        return 1

    site_id = os.environ.get("NETLIFY_SITE_ID", DEFAULT_SITE)
    if not args.html.exists():
        print(f"ERROR: {args.html} not found", file=sys.stderr)
        return 1

    result = deploy(args.html, token, site_id)
    print(f"State:    {result.get('state')}")
    print(f"Live URL: {result.get('ssl_url') or result.get('url')}")
    return 0 if result.get("state") == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
