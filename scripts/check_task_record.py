#!/usr/bin/env python3
"""Offline G01 status/evidence consistency linter; NOT a trusted attestor.

Only AgentWitness / external proof can authenticate observations. This file
checks internal consistency in an untrusted JSON record and fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

STATUSES = {"NOT STARTED", "PARTIALLY COMPLETE", "BLOCKED", "VERIFIED COMPLETE", "CANCELLED"}
KINDS = {"artifact", "test", "live", "security", "review", "deployment"}
PROVENANCE = {"self_reported", "transcript_imported", "external_observed", "broker_witnessed", "hardened_observed"}
ACCEPTED_PROOF = {"external_observed", "broker_witnessed", "hardened_observed"}
SENSITIVE_ACTIONS = {"email_send", "email_reply", "email_forward", "merge", "deploy", "spend", "privilege_change"}
MAIL_ACTIONS = {"email_send", "email_reply", "email_forward"}


def digest_contract(record: dict) -> str:
    """Detect accidental drift; NOT cryptographic protection against author edits.

    This hash is not signed, externally anchored, or proof of user consent.
    For immutable contracts use AgentWitness signed creation anchors.
    """
    contract = record["contract"]
    data = {
        "task_id": record["task_id"],
        "task_type": record["task_type"],
        "user_facing": record["user_facing"],
        "user_outcome": contract["user_outcome"],
        "criteria": contract["criteria"],
    }
    blob = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _text(x: object) -> bool:
    return isinstance(x, str) and bool(x.strip())


def _in(x: object, allowed: set[str]) -> bool:
    return isinstance(x, str) and x in allowed


def validate(record: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    required = {"schema_version", "task_id", "task_type", "user_facing", "actor", "status", "contract", "results", "evidence", "external_actions", "remaining_work", "blocker"}
    missing = required - record.keys()
    if missing:
        return ["missing required keys: " + ", ".join(sorted(missing))]
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        errors.append("schema_version must be integer 1")
    if not _text(record["task_id"]) or not _text(record["actor"]):
        errors.append("task_id and actor must be non-empty strings")
    if not _in(record["task_type"], {"software", "documentation", "research", "support", "other"}):
        errors.append("invalid task_type")
    if not isinstance(record["user_facing"], bool):
        errors.append("user_facing must be boolean")
    status = record["status"]
    if not _in(status, STATUSES):
        errors.append("invalid status")
    contract = record["contract"]
    if not isinstance(contract, dict) or not all(k in contract for k in ("user_outcome", "criteria", "digest_sha256")):
        return errors + ["contract requires user_outcome, criteria and digest_sha256"]
    criteria = contract["criteria"]
    if not _text(contract["user_outcome"]) or not isinstance(criteria, list) or not criteria:
        return errors + ["contract must have outcome and at least one acceptance criterion"]
    if not all(isinstance(c, dict) and _text(c.get("id")) and _text(c.get("description")) and _in(c.get("kind"), KINDS) for c in criteria):
        return errors + ["every criterion requires id, description and valid kind"]
    ids = [c["id"] for c in criteria]
    if len(set(ids)) != len(ids):
        errors.append("duplicate criterion IDs")
    if record["user_facing"] and not any(c["kind"] == "live" for c in criteria):
        errors.append("user-facing task must include live acceptance criterion")
    if not isinstance(contract["digest_sha256"], str) or len(contract["digest_sha256"]) != 64:
        errors.append("contract digest_sha256 must be 64 hexadecimal characters")
    else:
        try:
            if contract["digest_sha256"] != digest_contract(record):
                errors.append("contract digest mismatch; original scope cannot be assumed unchanged")
        except (ValueError, TypeError, KeyError):
            errors.append("could not calculate contract digest")
    results = record["results"]
    evidence = record["evidence"]
    actions = record["external_actions"]
    remaining = record["remaining_work"]
    blocker = record["blocker"]
    if not isinstance(results, list) or not isinstance(evidence, list) or not isinstance(actions, list) or not isinstance(remaining, list):
        return errors + ["results, evidence, external_actions and remaining_work must be arrays"]
    if not all(_text(v) for v in remaining):
        errors.append("remaining_work values must be non-empty strings")
    if not all(isinstance(e, dict) and _text(e.get("id")) and _text(e.get("reference")) and _in(e.get("kind"), KINDS) and _in(e.get("provenance"), PROVENANCE) and _text(e.get("observed_by")) for e in evidence):
        errors.append("evidence must have id, reference, kind, provenance and observed_by")
    good_ev = [e for e in evidence if isinstance(e, dict) and _text(e.get("id"))]
    evid_ids = [e["id"] for e in good_ev]
    if len(set(evid_ids)) != len(evid_ids):
        errors.append("duplicate evidence IDs")
    ev_map = {e["id"]: e for e in good_ev}
    if not all(isinstance(r, dict) and r.get("criterion_id") in ids and _in(r.get("outcome"), {"PASS", "FAIL", "NOT_RUN", "BLOCKED"}) and isinstance(r.get("evidence_ids"), list) for r in results):
        errors.append("each result requires known criterion_id, valid outcome and evidence_ids array")
    good_results = [r for r in results if isinstance(r, dict) and r.get("criterion_id") in ids and isinstance(r.get("evidence_ids"), list)]
    if len({r["criterion_id"] for r in good_results}) != len(good_results):
        errors.append("duplicate criterion results")
    r_map = {r["criterion_id"]: r for r in good_results}
    for r in good_results:
        for ref in r["evidence_ids"]:
            if not isinstance(ref, str) or ref not in ev_map:
                errors.append("criterion " + str(r["criterion_id"]) + " references unknown evidence")
    for action in actions:
        if not isinstance(action, dict) or not _in(action.get("action"), SENSITIVE_ACTIONS) or not isinstance(action.get("performed"), bool):
            errors.append("external action requires recognised action and boolean performed")
            continue
        if action["performed"]:
            if not _text(action.get("approval_reference")) or not _text(action.get("approval_scope")):
                errors.append("performed consequential action missing approval reference/scope")
            if action["action"] in MAIL_ACTIONS and action.get("approval_scope") != action["action"]:
                errors.append("email action requires exactly send-specific approval scope")
    if status == "VERIFIED COMPLETE":
        if remaining or blocker is not None:
            errors.append("VERIFIED COMPLETE cannot have remaining work or blocker")
        if set(r_map) != set(ids):
            errors.append("VERIFIED COMPLETE requires one result per criterion")
        for c in criteria:
            r = r_map.get(c["id"])
            if not r or r.get("outcome") != "PASS":
                errors.append("VERIFIED COMPLETE requires PASS for " + c["id"])
                continue
            proof = [ev_map[v] for v in r["evidence_ids"] if isinstance(v, str) and v in ev_map]
            if not any(e.get("kind") == c["kind"] and _in(e.get("provenance"), ACCEPTED_PROOF) and e.get("observed_by") != record["actor"] for e in proof):
                errors.append("VERIFIED COMPLETE requires independent evidence of matching kind for " + c["id"])
    elif status == "NOT STARTED":
        if results or evidence or any(isinstance(a, dict) and a.get("performed") for a in actions) or blocker is not None:
            errors.append("NOT STARTED cannot claim actions, observations, or a blocker")
    elif status == "PARTIALLY COMPLETE":
        if not remaining:
            errors.append("PARTIALLY COMPLETE must name remaining work")
        if not evidence and not any(r.get("outcome") == "PASS" for r in good_results):
            errors.append("PARTIALLY COMPLETE needs some recorded work/evidence")
    elif status == "BLOCKED":
        if not isinstance(blocker, dict) or not all(_text(blocker.get(k)) for k in ("reason", "attempted_alternatives", "next_action")):
            errors.append("BLOCKED requires reason, attempted_alternatives and next_action")
    elif status == "CANCELLED":
        if not isinstance(blocker, dict) or not _text(blocker.get("reason")):
            errors.append("CANCELLED requires reason")
    return sorted(set(errors))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("record", type=Path, help="task evidence JSON file")
    p.add_argument("--stamp-contract", action="store_true", help="print calculated digest; does not sign or freeze")
    args = p.parse_args()
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        print(f"INVALID RECORD: {e}", file=sys.stderr)
        return 2
    if args.stamp_contract:
        try:
            print(digest_contract(data))
            return 0
        except (KeyError, TypeError, ValueError) as e:
            print(f"INVALID CONTRACT: {e}", file=sys.stderr)
            return 2
    errors = validate(data)
    if errors:
        for e in errors:
            print("INVALID: " + e, file=sys.stderr)
        return 1
    print(f"STRUCTURALLY CONSISTENT: {data['task_id']} ({data['status']}); NOT AN INDEPENDENT ATTESTATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
