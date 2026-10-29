#!/usr/bin/env python3
"""Daily evidence-aware project health: GitHub workflows + public site + G04 record ledger.

No emails, deployments, credential writes, personal chats, private APIs, or claims
that CI proves users' real-world outcomes. On unavailable data, report UNKNOWN.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from kpi_ledger import compute, load_records

ROOT = Path(__file__).resolve().parents[1]
REPOSITORIES = (
    "Parris-Tech-Services/chatGPTImprovement-",
    "Parris-Tech-Services/FaithHub",
    "Parris-Tech-Services/JoshRS",
    "Parris-Tech-Services/AgentCheck",
    "Parris-Tech-Services/LLMAccountability",
    "joshualparris/JoshMemory",
)
SITE_CHECKS = {
    "FaithHub home": "https://parris-tech-services.github.io/FaithHub/",
    "FaithHub Psalms": "https://parris-tech-services.github.io/FaithHub/psalms.html",
}
FAILED = {"failure", "timed_out", "action_required", "startup_failure"}
MAX_HTTP_BODY = 160_000


def request_json(path: str) -> dict:
    # Fixed GitHub HTTPS root; never send a token to an arbitrary host.
    req = urllib.request.Request("https://api.github.com" + path,
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "faithful-quality-audit/1.0"})
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=18) as resp:
        return json.load(resp)


def check_public_page(url: str) -> dict:
    # Caller uses only literal allowlisted public HTTPS URLs above.
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FaithHubHealth/1.0"})
        with urllib.request.urlopen(req, timeout=18) as resp:
            body = resp.read(MAX_HTTP_BODY).decode("utf-8", errors="replace")
            ok = resp.status == 200 and ("FaithHub" in body or "FaithHub" in resp.url)
            return {"url": url, "state": "PASS" if ok else "FAIL",
                    "http_status": resp.status, "body_checked": True,
                    "meaning": "HTTP/HTML marker only; NOT interactive browser acceptance"}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"url": url, "state": "UNKNOWN", "error_type": type(exc).__name__,
                "meaning": "HTTP failed; no browser outcome established"}


def latest_main_workflows(runs: list[dict], branch: str) -> list[dict]:
    """Ignore PR/feature branch results for main health. Keep latest per workflow."""
    main = sorted((x for x in runs if x.get("head_branch") == branch and
                   x.get("event") in {"push", "workflow_dispatch", "schedule"}),
                  key=lambda x: x.get("created_at", ""), reverse=True)
    found = {}
    for x in main:
        key = x.get("workflow_id") or x.get("name")
        if key not in found:
            conclusion = x.get("conclusion")
            state = ("FAIL" if conclusion in FAILED else
                     "PASS" if conclusion == "success" else
                     "UNKNOWN" if x.get("status") != "completed" or not conclusion else "NEUTRAL")
            found[key] = {"workflow": x.get("name") or str(key),
                          "state": state, "conclusion": conclusion or "PENDING",
                          "source_sha": x.get("head_sha"),
                          "run_url": x.get("html_url"),
                          "date": x.get("created_at")}
    return list(found.values())


def read_register(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or len({r.get("id") for r in rows}) != len(rows):
        raise ValueError("Task register missing or contains duplicate task IDs")
    return rows


def local_scorecard(base: Path) -> dict:
    records = load_records(base / "docs" / "evidence")
    register = read_register(base / "docs" / "MASTER_ACTION_BACKLOG_2026-10-29.csv")
    ledger = compute(records, register)
    status = Counter(r["status"] for r in register)
    # A small, self-selected record set is NOT a daily ChatGPT task population.
    return {
        "registered_tasks": len(register),
        "claimed_complete": status["VERIFIED COMPLETE"],
        "open_tasks": status["OPEN"],
        "other_statuses": {k: v for k,v in status.items()
                           if k not in {"VERIFIED COMPLETE", "OPEN"}},
        "recorded_valid_complete": ledger["kpis"]["end_to_end_task_success"]["numerator"],
        "invalid_complete_records": ledger["kpis"]["status_inflation_ids"],
        "unsupported_register_claims": ledger["register_unsupported_verified_claims"],
        "record_loading_errors": ledger["errors"],
        "record_sample_n": ledger["record_count"],
        "sample_eligibility_unknown": ledger["eligibility_unknown_ids"],
        "historical_chat_baseline": "UNKNOWN — 50–100 complete conversations not independently audited",
        "daily_task_completion_rate": "UNKNOWN — no complete daily task cohort",
        "measured_rework": ledger["kpis"]["assistant_caused_rework"],
        "measured_corrective_followups": ledger["kpis"]["corrective_followups_per_task"],
        "measured_claim_verification": ledger["kpis"]["claim_verification"],
        "meaning": "Evidence-record snapshot, NOT a measure of GPT model quality",
    }


def remote_project(repo: str, now: datetime) -> dict:
    try:
        meta = request_json("/repos/" + repo)
        if meta.get("private") is True:
            return {"repo": repo, "state": "SKIPPED_PRIVATE"}
        branch = meta.get("default_branch", "main")
        runs = request_json("/repos/" + repo + "/actions/runs?per_page=100").get("workflow_runs", [])
        prs = request_json("/repos/" + repo + "/pulls?state=open&per_page=100")
        last_day = now - timedelta(days=1)
        recent = [x for x in runs if x.get("head_branch") == branch and
                  x.get("event") in {"push", "workflow_dispatch", "schedule"} and
                  isinstance(x.get("created_at"), str) and
                  parse_timestamp(x["created_at"]) >= last_day]
        latest = latest_main_workflows(runs, branch)
        return {"repo": repo, "state": "OBSERVED",
                "default_branch": branch,
                "open_pr_count": len(prs) if isinstance(prs, list) else "UNKNOWN",
                "latest_main_workflows": latest,
                "last_24h_main_runs": len(recent),
                "last_24h_failed_main_runs": sum(x.get("conclusion") in FAILED for x in recent),
                "warning": "Last 100 API runs only; sparse/path-filtered workflows may not run on every commit"}
    except (urllib.error.URLError, OSError, TimeoutError, ValueError, KeyError) as exc:
        return {"repo": repo, "state": "UNKNOWN", "error_type": type(exc).__name__}


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_report(base: Path, now: datetime, offline: bool) -> dict:
    local = local_scorecard(base)
    projects = [] if offline else [remote_project(r, now) for r in REPOSITORIES]
    pages = {} if offline else {name: check_public_page(url) for name, url in SITE_CHECKS.items()}
    red = [x["repo"] for x in projects
           if x["state"] == "OBSERVED" and any(
               w["state"] == "FAIL" for w in x["latest_main_workflows"])]
    unknown = [x["repo"] for x in projects if x["state"] == "UNKNOWN"]
    return {
        "generated_at_utc": now.isoformat(),
        "generated_at_sydney": now.astimezone(ZoneInfo("Australia/Sydney")).isoformat(),
        "kind": "read-only automatic repository and public HTTP observations",
        "tracked_programme": local,
        "public_projects": projects,
        "live_http_checks": pages,
        "red_latest_main_workflows_repos": red,
        "unknown_api_repos": unknown,
        "source_commit": os.getenv("GITHUB_SHA", "LOCAL/UNSET"),
        "limitations": [
            "CI success does not prove usability, security, deployment content or user satisfaction.",
            "HTTP 200 does not establish a real browser acceptance journey.",
            "Daily report does not cover inaccessible/private projects or full historical ChatGPT conversations.",
            "No alerts sent by email; this report lives in the GitHub Actions summary and artifact.",
        ],
    }


def as_markdown(report: dict) -> str:
    p = report["tracked_programme"]
    lines = ["# Daily ChatGPT Improvement health (read-only)",
             f"Observed: {report['generated_at_sydney']} (Australia/Sydney)",
             "",
             f"- Register: **{p['claimed_complete']}/{p['registered_tasks']} marked complete**; "
             f"**{p['recorded_valid_complete']}** currently backed by structurally accepted records. "
             "This does not independently authenticate their claims.",
             f"- Unsupported register DONE claims: {', '.join(p['unsupported_register_claims']) or 'none'}",
             f"- Historical 50–100 chat baseline: **UNKNOWN**",
             f"- Real daily ChatGPT task success rate: **UNKNOWN**",
             f"- Measured rework from eligible sample: **{p['measured_rework']['value']}**",
             f"- Measured claim verification from eligible sample: **{p['measured_claim_verification']['value']}**",
             "", "## Latest default-branch GitHub workflows (not PR results)"]
    for item in report["public_projects"]:
        if item["state"] != "OBSERVED":
            lines.append(f"- {item['repo']}: **{item['state']}** (not silently counted as PASS)")
            continue
        states = Counter(w["state"] for w in item["latest_main_workflows"])
        lines.append(f"- {item['repo']}: "
                     f"{states.get('PASS',0)} PASS, {states.get('FAIL',0)} FAIL, "
                     f"{states.get('UNKNOWN',0)} UNKNOWN across latest main runs; "
                     f"{item['open_pr_count']} open PR(s)")
    lines.extend(["", "## Public page checks — HTTP only"])
    for name, obs in report["live_http_checks"].items():
        lines.append(f"- {name}: **{obs['state']}** — {obs['url']}")
    lines.extend(["", "## Evidence and boundaries",
                  "- All raw reports are produced from real API/HTTP observations, not simulated claims.",
                  "- No chat transcripts, email, signing keys or private machine data are collected.",
                  "- Dashboard's daily performance percentage remains UNKNOWN until G02/G03 audit task cohorts.",
                  "- For actual end-user acceptance, inspect the app-specific Playwright and AgentWitness workflows.",
                  ""])
    return "\n".join(lines)


def main(argv=None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--offline", action="store_true", help="do not contact GitHub or public sites")
    cli.add_argument("--out", type=Path, default=Path("daily-quality-output"))
    cli.add_argument("--strict", action="store_true", help="return nonzero on confirmed latest main failure or site failure")
    args = cli.parse_args(argv)
    now = datetime.now(timezone.utc)
    report = build_report(ROOT, now, args.offline)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "quality.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    summary = as_markdown(report)
    (args.out / "quality.md").write_text(summary, encoding="utf-8")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fp:
            fp.write(summary)
    print(summary)
    fails = bool(report["red_latest_main_workflows_repos"]) or any(
        x["state"] == "FAIL" for x in report["live_http_checks"].values())
    return 1 if args.strict and fails else 0


if __name__ == "__main__":
    sys.exit(main())
