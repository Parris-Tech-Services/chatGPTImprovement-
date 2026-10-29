#!/usr/bin/env python3
"""Scan every issue/PR title, body and comment of a repository with the S03 public-safety scan.

  scan_issue_bodies.py OWNER/REPO [--offline]
Requires the `gh` CLI. Exit 1 when any item has a finding (the item URL is printed, never the value).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_safety_scan as pss


def gh_items(path: str) -> list[dict]:
    out = subprocess.run(["gh", "api", "--paginate", path, "--jq", ".[]|@json"], capture_output=True, text=True, check=True).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def main(argv: list[str]) -> int:
    repo, offline = argv[0], "--offline" in argv
    allow = pss.load_allowlist()
    items = gh_items(f"repos/{repo}/issues?state=all&per_page=100") + gh_items(f"repos/{repo}/issues/comments?per_page=100")
    bad = notes = 0
    for it in items:
        text = (it.get("title") or "") + "\n" + (it.get("body") or "")
        n: list[str] = []
        found = pss.scan_text(text, it.get("html_url", "?"), allow, offline, None if not offline else n)
        notes += len(n)
        for f in found:
            print("FINDING " + f)
        bad += bool(found)
    print(f"issue/comment scan: {len(items)} item(s), {bad} with findings, {notes} unverified link note(s).")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
