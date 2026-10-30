#!/usr/bin/env python3
"""S02 key-leak canary: prove signing-key material never reaches published outputs.

Finds key-like files under the given roots (names such as *key*, *.pem, *private*, *secret*,
*.sk, or PEM private-key content), then checks that no published output (CI artifacts, captured
logs, git-tracked files) contains any of that material, whether raw, hex or base64 encoded,
including 24-character fragments. It also reports key files that are group/world readable or
tracked by git. Key values and paths inside outputs are never printed; findings name the key
file and the output only.

  key_leak_canary.py --key-root DIR [--key-root DIR ...] --output FILE_OR_DIR [...] [--git-repo DIR]

Exit 1 on any leak, unsafe permission or tracked key; exit 2 if no key file was found at all
(a canary that inspected nothing must not pass silently) unless --allow-no-keys is given.
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

NAME = re.compile(r"(?i)(key|private|secret|\.pem$|\.sk$|signing)")
PEM_PRIVATE = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")
FRAGMENT = 24            # shortest secret fragment we look for, in characters
MAX_KEY_BYTES = 64 * 1024


PUBLIC = re.compile(r"(?i)(public|\.pub$)")


def is_key_file(p: Path) -> bool:
    """Private key material only: public keys are meant to be shared."""
    if not p.is_file() or p.stat().st_size == 0 or p.stat().st_size > MAX_KEY_BYTES:
        return False
    try:
        data = p.read_bytes()
    except OSError:
        return False
    if PEM_PRIVATE.search(data):
        return True
    if PUBLIC.search(p.name) or b"PUBLIC KEY-----" in data:
        return False
    if NAME.search(p.name):
        return True
    return False


def find_keys(roots: list[Path]) -> list[Path]:
    keys = []
    for root in roots:
        if root.is_file():
            if is_key_file(root):
                keys.append(root)
            continue
        for p in root.rglob("*") if root.is_dir() else []:
            if is_key_file(p):
                keys.append(p)
    return sorted(set(keys))


def needles(material: bytes) -> list[str]:
    """Distinctive strings that would reveal the key: the text itself (minus PEM armour), plus hex
    and base64 of the raw bytes, cut into overlapping fragments."""
    forms: list[str] = []
    text = material.decode("utf-8", "ignore")
    body = "".join(l.strip() for l in text.splitlines() if l.strip() and not l.startswith("-----"))
    for f in (body, material.hex(), base64.b64encode(material).decode(), base64.urlsafe_b64encode(material).decode().rstrip("=")):
        f = re.sub(r"\s+", "", f)
        if len(f) >= FRAGMENT:
            step = max(1, FRAGMENT // 2)
            forms += [f[i:i + FRAGMENT] for i in range(0, len(f) - FRAGMENT + 1, step)]
    # Low-entropy fragments (e.g. runs of the same character) would match innocently.
    return sorted({n for n in forms if len(set(n)) >= 8})


def output_files(outputs: list[Path]) -> list[Path]:
    files = []
    for o in outputs:
        if o.is_file():
            files.append(o)
        elif o.is_dir():
            files += [p for p in o.rglob("*") if p.is_file() and ".git" not in p.parts]
    return files


def tracked(repo: Path) -> set[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=True).stdout
    return {(repo / p).resolve() for p in out.decode().split("\0") if p}


def check(key_roots: list[Path], outputs: list[Path], git_repo: Path | None) -> tuple[list[str], int]:
    findings: list[str] = []
    keys = find_keys(key_roots)
    tracked_files = tracked(git_repo) if git_repo else set()
    outs = output_files(outputs) + sorted(tracked_files)      # every git-tracked file is a published output
    print("key files inspected: " + (", ".join(sorted(k.name for k in keys)) or "none"))
    out_text = {}
    for o in outs:
        try:
            out_text[o] = o.read_bytes().decode("utf-8", "ignore")
        except OSError:
            findings.append(f"output {o.name}: unreadable, cannot be cleared")
    for k in keys:
        mode = stat.S_IMODE(k.stat().st_mode)
        if mode & (stat.S_IRGRP | stat.S_IROTH | stat.S_IWGRP | stat.S_IWOTH):
            findings.append(f"key {k.name}: permissions {oct(mode)} allow group/other access")
        if k.resolve() in tracked_files:
            findings.append(f"key {k.name}: tracked by git")
        ns = needles(k.read_bytes())
        for o, text in out_text.items():
            if o.resolve() == k.resolve():
                continue
            if any(n in text for n in ns):
                findings.append(f"key {k.name}: material appears in output {o.name}")
    return findings, len(keys)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key-root", type=Path, action="append", required=True)
    ap.add_argument("--output", type=Path, action="append", required=True)
    ap.add_argument("--git-repo", type=Path)
    ap.add_argument("--allow-no-keys", action="store_true")
    ap.add_argument("--known-permission-finding", action="append", default=[], metavar="KEYNAME",
                    help="a documented upstream permission bug for this key name: warn instead of fail (leaks still fail)")
    a = ap.parse_args(argv)
    findings, n = check(a.key_root, a.output, a.git_repo)
    known = [f for f in findings if ": permissions " in f and f.split(":")[0].removeprefix("key ") in a.known_permission_finding]
    findings = [f for f in findings if f not in known]
    for f in known:
        print("KNOWN UPSTREAM FINDING " + f)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("::warning title=key-leak-canary (tracked upstream)::" + f)
    for f in findings:
        print("FINDING " + f)
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("::error title=key-leak-canary::" + f)
    print(f"key-leak canary: {n} key file(s) checked against {len(output_files(a.output))} output file(s); {len(findings)} finding(s).")
    if findings:
        return 1
    if n == 0 and not a.allow_no_keys:
        print("NO KEY FILES FOUND: the canary inspected nothing; refusing to report a pass.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
