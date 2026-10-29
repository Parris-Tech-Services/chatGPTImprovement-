#!/usr/bin/env python3
"""S03 public-safety scan for this PUBLIC repository and its issues.

Fails closed on content that must stay in a private, authorised store:
credentials and private keys, personal email addresses and phone numbers,
machine identity (user home paths, hostnames in UNC paths), raw conversation
transcripts, and links to GitHub repositories that are not publicly visible.

This is a bounded pattern scan, NOT proof that nothing sensitive exists:
paraphrased private facts, screenshots and novel secret formats are not
detected. Matched values are never printed in full.

Usage:
  public_safety_scan.py [PATH ...]           scan files (default: git-tracked files)
  public_safety_scan.py --text-file F        scan one text blob (issue/comment body)
  public_safety_scan.py --offline            do not query GitHub for repo visibility
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "scripts" / "public_safety_allowlist.json"

# (rule id, pattern). Patterns are deliberately specific to keep false positives reviewable.
SECRET_RULES = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("assigned-secret", re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
]
PII_RULES = [
    ("email-address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("au-phone", re.compile(r"(?<![\w/.-])(?:\+61\s?[2-478]|0[2-478])(?:[\s-]?\d){8}(?![\w/-])")),
]
IDENTITY_RULES = [
    ("windows-user-path", re.compile(r"(?i)\b[A-Z]:\\Users\\(?!Public\\|Default\\|<|\{|%|USERNAME)[^\\\s]+")),
    ("unix-home-path", re.compile(r"(?<![\w.])/(?:home|Users)/(?!user/|runner/|<|\{|\$|USER\b|you/|example/)[A-Za-z0-9._-]+/")),
    ("unc-host-path", re.compile(r"\\\\[A-Za-z0-9-]{2,}\\[A-Za-z0-9$_-]+")),
]
TRANSCRIPT_RULES = [
    ("transcript-turn", re.compile(r"(?im)^\s*(?:\*\*)?(?:You said|ChatGPT said|User|Assistant|Human)(?:\*\*)?\s*:\s*\S")),
]
GITHUB_REPO = re.compile(r"(?:https?://(?:www\.)?github\.com/|git@github\.com:|ssh://git@github\.com/)([A-Za-z0-9-]+)/([A-Za-z0-9._-]+?)(?:\.git)?(?=[/#?)\]\s\"'`>,:;!]|$)", re.IGNORECASE)
EMAIL_OK = re.compile(r"(?i)@(?:users\.noreply\.github\.com|noreply\.[a-z.]+|example\.(?:com|org|net|test)|anthropic\.com)$|^noreply@|^git@")


def redact(value: str) -> str:
    value = value.strip()
    return value[:4] + "…" + f"({len(value)} chars)" if len(value) > 6 else "…"


def load_allowlist() -> dict:
    try:
        data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return {
        "public_repos": {r.lower() for r in data.get("public_repos", [])},
        "emails": {e.lower() for e in data.get("emails", [])},
        "paths": set(data.get("paths", [])),
        "binary_paths": set(data.get("binary_paths", [])),
    }


_visibility_cache: dict[str, str] = {}


def repo_visibility(owner_repo: str, offline: bool) -> str:
    """'public', 'not-public' (404 to an anonymous request) or 'unknown'."""
    key = owner_repo.lower()
    if key in _visibility_cache:
        return _visibility_cache[key]
    if offline:
        return "unknown"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "public-safety-scan"}
    # In Actions the job token is scoped to this repository, so another repository
    # answers 200 only when it is public and 404 when it is private.
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request("https://api.github.com/repos/" + owner_repo, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = "not-public" if json.load(r).get("private") else "public"
    except urllib.error.HTTPError as e:
        result = "not-public" if e.code == 404 else "unknown"
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        result = "unknown"
    _visibility_cache[key] = result
    return result


def scan_text(text: str, where: str, allow: dict, offline: bool, notes: list[str] | None = None, allow_inline: bool = False) -> list[str]:
    """allow_inline honours `public-safety: allow` markers; only for reviewed repository files,
    never for issue, PR or review text that anyone can write."""
    findings: list[str] = []
    notes = notes if notes is not None else findings
    for lineno, line in enumerate(text.splitlines(), 1):
        if allow_inline and "public-safety: allow" in line:
            continue
        loc = f"{where}:{lineno}"
        for rule, pat in SECRET_RULES:
            for m in pat.finditer(line):
                findings.append(f"{loc}: {rule} {redact(m.group(0))}")
        for rule, pat in PII_RULES:
            for m in pat.finditer(line):
                v = m.group(0)
                if rule == "email-address" and (EMAIL_OK.search(v) or v.lower() in allow["emails"]):
                    continue
                findings.append(f"{loc}: {rule} {redact(v)}")
        for rule, pat in IDENTITY_RULES:
            for m in pat.finditer(line):
                if m.group(0) in allow["paths"]:
                    continue
                findings.append(f"{loc}: {rule} {redact(m.group(0))}")
        for rule, pat in TRANSCRIPT_RULES:
            if pat.search(line):
                findings.append(f"{loc}: {rule} (raw chat turns belong in the private store)")
        for m in GITHUB_REPO.finditer(line):
            owner, repo = m.group(1), m.group(2)
            if owner.lower() in {"orgs", "settings", "features", "apps", "marketplace", "topics", "sponsors"}:
                continue
            # Conventional example URL used in reviewer documentation; not a real
            # GitHub repository locator. Keep the exception EXACT, and do not
            # exempt any actual private owner or any other repository.
            if owner.casefold() == "owner" and repo.casefold() == "repo":
                continue
            full = f"{owner}/{repo}"
            if full.lower() in allow["public_repos"]:
                continue
            vis = repo_visibility(full, offline)
            if vis == "not-public":
                findings.append(f"{loc}: private-repo-link {owner}/… is not publicly visible")
            elif vis == "unknown":
                notes.append(f"{loc}: unverified-repo-link {owner}/… (visibility could not be checked)")
    return findings


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.splitlines()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--text-file", type=Path, help="scan a single text blob, e.g. an issue body")
    ap.add_argument("--offline", action="store_true", help="skip GitHub visibility checks")
    ap.add_argument("--require-visibility", action="store_true", help="fail when a linked repo's visibility cannot be confirmed (CI)")
    args = ap.parse_args(argv)
    allow = load_allowlist()
    findings: list[str] = []
    notes: list[str] = []
    sink = findings if args.require_visibility else notes
    scanned = 0
    if args.text_file:
        findings += scan_text(args.text_file.read_text(encoding="utf-8", errors="replace"), "text", allow, args.offline, sink)
        scanned = 1
    else:
        for p in args.paths or tracked_files():
            if p.resolve() == ALLOWLIST.resolve() or not p.is_file():
                continue
            rel = p.resolve().relative_to(ROOT) if p.resolve().is_relative_to(ROOT) else p
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                if str(rel) not in allow["binary_paths"]:
                    findings.append(f"{rel}: binary or non-UTF-8 file; review it and list it under binary_paths in the allowlist")
                continue
            findings += scan_text(text, str(rel), allow, args.offline, sink, allow_inline=True)
            scanned += 1
    for f in findings:
        print("FINDING " + f)
        if os.environ.get("GITHUB_ACTIONS") == "true":    # surface (already redacted) findings as annotations
            print("::error title=public-safety::" + f.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"))
    for n in sorted(set(notes)):
        print("NOTE " + n)
    print(f"public-safety scan: {scanned} item(s), {len(findings)} finding(s). Pattern scan only; not proof of absence.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
