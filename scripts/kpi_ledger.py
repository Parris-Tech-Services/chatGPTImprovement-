#!/usr/bin/env python3
"""G04 KPI ledger: compute the KPI scorecard from task evidence records, never from claims.

Every rate is reported as numerator/denominator with the task IDs behind it, plus the IDs
whose data is missing. If a denominator is zero or the data is missing, the value is UNKNOWN;
missing data is never treated as zero or success.

Anti-gaming rules:
  * Only records that pass check_task_record.validate() can count as VERIFIED COMPLETE
    successes; an invalid "VERIFIED COMPLETE" counts as a status error, not a success.
  * Ineligible/excluded tasks must give a reason and are listed, not silently dropped.
  * Duplicate task IDs are an error (no double counting).
  * A register (CSV) status of VERIFIED COMPLETE without a valid record is an unsupported claim.
  * Performed consequential actions without approval reference/scope are unauthorised.

Optional per-record "kpi" object (all fields nullable; null means unknown):
  eligible (bool), excluded_reason (str), accepted_at / verified_at (ISO 8601),
  assistant_rework (bool), corrective_followups (int), claims_made (int), claims_supported (int)

  kpi_ledger.py [--records DIR] [--register CSV] [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_task_record import validate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UNKNOWN = "UNKNOWN"


def rate(num_ids: list[str], den_ids: list[str], missing: list[str]) -> dict:
    n, d = len(num_ids), len(den_ids)
    return {"value": round(n / d, 4) if d else UNKNOWN, "numerator": n, "denominator": d,
            "numerator_ids": sorted(num_ids), "denominator_ids": sorted(den_ids), "missing_ids": sorted(missing)}


def _when(v):
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def load_records(directory: Path) -> list[tuple[str, dict]]:
    out = []
    for p in sorted(directory.glob("*.json")):
        try:
            out.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as e:
            out.append((p.name, {"__load_error__": str(e)}))
    return out


def compute(records: list[tuple[str, dict]], register: list[dict] | None = None) -> dict:
    errors: list[str] = []
    seen: dict[str, str] = {}
    tasks: dict[str, dict] = {}
    for name, rec in records:
        if "__load_error__" in rec or not isinstance(rec, dict):
            errors.append(f"{name}: unreadable record")
            continue
        tid = rec.get("task_id")
        if not isinstance(tid, str) or not tid:
            errors.append(f"{name}: record without task_id")
            continue
        if tid in seen:
            errors.append(f"{name}: duplicate task_id {tid} (also in {seen[tid]}); neither counted")
            tasks.pop(tid, None)
            continue
        seen[tid] = name
        tasks[tid] = rec

    valid = {t: not validate(r) for t, r in tasks.items()}
    kpi = {t: (r.get("kpi") if isinstance(r.get("kpi"), dict) else {}) for t, r in tasks.items()}

    eligible, excluded, unknown_elig = [], [], []
    for t in tasks:
        e = kpi[t].get("eligible")
        if e is True:
            eligible.append(t)
        elif e is False:
            reason = kpi[t].get("excluded_reason")
            if isinstance(reason, str) and reason.strip():
                excluded.append({"task_id": t, "reason": reason.strip()})
            else:
                errors.append(f"{t}: excluded without a reason; treated as eligible")
                eligible.append(t)
        else:
            unknown_elig.append(t)
            eligible.append(t)        # unknown eligibility stays in the denominator

    success = [t for t in eligible if tasks[t].get("status") == "VERIFIED COMPLETE" and valid[t]]
    inflated = [t for t in tasks if tasks[t].get("status") == "VERIFIED COMPLETE" and not valid[t]]

    completed = [t for t in eligible if t in success]
    rework_known = [t for t in completed if isinstance(kpi[t].get("assistant_rework"), bool)]
    rework_yes = [t for t in rework_known if kpi[t]["assistant_rework"]]

    fu_known = [t for t in eligible if type(kpi[t].get("corrective_followups")) is int and kpi[t]["corrective_followups"] >= 0]
    fu_total = sum(kpi[t]["corrective_followups"] for t in fu_known)

    claim_known = [t for t in tasks if type(kpi[t].get("claims_made")) is int and type(kpi[t].get("claims_supported")) is int
                   and 0 <= kpi[t]["claims_supported"] <= kpi[t]["claims_made"]]
    claims_made = sum(kpi[t]["claims_made"] for t in claim_known)
    claims_ok = sum(kpi[t]["claims_supported"] for t in claim_known)

    unauthorised = []
    for t, r in tasks.items():
        for a in r.get("external_actions") or []:
            if isinstance(a, dict) and a.get("performed") is True and not (a.get("approval_reference") and a.get("approval_scope")):
                unauthorised.append({"task_id": t, "action": a.get("action")})

    leads, lead_missing = [], []
    for t in success:
        a, v = _when(kpi[t].get("accepted_at")), _when(kpi[t].get("verified_at"))
        if a and v and v >= a:
            leads.append((v - a).total_seconds() / 3600)
        else:
            lead_missing.append(t)

    unsupported_register = []
    if register is not None:
        for row in register:
            rid, rst = row.get("id"), row.get("status")
            if rst == "VERIFIED COMPLETE" and not (rid in tasks and valid.get(rid) and tasks[rid].get("status") == "VERIFIED COMPLETE"):
                unsupported_register.append(rid)

    return {
        "source_of_truth": "task evidence records validated by scripts/check_task_record.py",
        "record_count": len(tasks),
        "errors": errors,
        "excluded": excluded,
        "eligibility_unknown_ids": sorted(unknown_elig),
        "kpis": {
            "end_to_end_task_success": rate(success, eligible, []),
            "status_accuracy": rate([t for t in tasks if valid[t]], list(tasks), []),
            "status_inflation_ids": sorted(inflated),
            "assistant_caused_rework": rate(rework_yes, rework_known, [t for t in completed if t not in rework_known]),
            "corrective_followups_per_task": {
                "value": round(fu_total / len(fu_known), 4) if fu_known else UNKNOWN, "followups": fu_total,
                "tasks": len(fu_known), "missing_ids": sorted(t for t in eligible if t not in fu_known)},
            "claim_verification": {
                "value": round(claims_ok / claims_made, 4) if claims_made else UNKNOWN, "supported": claims_ok,
                "made": claims_made, "missing_ids": sorted(t for t in tasks if t not in claim_known)},
            "unauthorised_actions": {"count": len(unauthorised), "items": unauthorised},
            "delivery_lead_time_hours_median": {
                "value": round(statistics.median(leads), 2) if leads else UNKNOWN, "n": len(leads), "missing_ids": sorted(lead_missing)},
        },
        "register_unsupported_verified_claims": sorted(unsupported_register) if register is not None else UNKNOWN,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", type=Path, default=ROOT / "docs" / "evidence")
    ap.add_argument("--register", type=Path, default=ROOT / "docs" / "MASTER_ACTION_BACKLOG_2026-10-29.csv")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    register = None
    if args.register and args.register.is_file():
        with args.register.open(encoding="utf-8", newline="") as f:
            register = list(csv.DictReader(f))
    report = compute(load_records(args.records), register)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        k = report["kpis"]
        fmt = lambda r: f"{r['value']} ({r['numerator']}/{r['denominator']})"
        print(f"Records: {report['record_count']}  errors: {len(report['errors'])}  excluded: {len(report['excluded'])}")
        print("End-to-end task success:", fmt(k["end_to_end_task_success"]))
        print("Status accuracy:        ", fmt(k["status_accuracy"]), " inflated:", k["status_inflation_ids"] or "none")
        print("Assistant-caused rework:", fmt(k["assistant_caused_rework"]), " missing:", k["assistant_caused_rework"]["missing_ids"] or "none")
        print("Corrective follow-ups:  ", k["corrective_followups_per_task"]["value"], " missing:", k["corrective_followups_per_task"]["missing_ids"] or "none")
        print("Claim verification:     ", k["claim_verification"]["value"])
        print("Unauthorised actions:   ", k["unauthorised_actions"]["count"])
        print("Median lead time (h):   ", k["delivery_lead_time_hours_median"]["value"])
        print("Register VERIFIED without valid record:", report["register_unsupported_verified_claims"] or "none")
        for e in report["errors"]:
            print("ERROR " + e)
    bad = report["errors"] or report["kpis"]["status_inflation_ids"] or report["kpis"]["unauthorised_actions"]["count"] \
        or (isinstance(report["register_unsupported_verified_claims"], list) and report["register_unsupported_verified_claims"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
