#!/usr/bin/env python3
"""Run REAL AgentWitness and LLMAccountability code in an isolated CI runner.

This is a CI integration pilot, NOT a protected Windows SYSTEM-notary proof,
not automatic instrumentation of ChatGPT hosted tool calls, and not a
substitute for real application/browser acceptance. Fail closed on mismatches.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK = "i02-ci-real-verifier-pilot"


def run(argv: list[str], cwd: Path, *, expect: int = 0, label: str = "") -> dict:
    p = subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True, timeout=240)
    # Never emit a full verifier receipt, source tree, signing key or secrets.
    result = {"step": label or " ".join(argv[:2]), "exit_code": p.returncode,
              "expected_exit_code": expect}
    if p.returncode != expect:
        print(f"FAIL {result['step']}: expected {expect}, got {p.returncode}", file=sys.stderr)
        print("STDOUT suffix:", p.stdout[-1400:], file=sys.stderr)
        print("STDERR suffix:", p.stderr[-1400:], file=sys.stderr)
        raise RuntimeError(f"{result['step']} returned unexpected exit code")
    print(f"PASS {result['step']} (exit {p.returncode})")
    return result


def evidence_summary(repo: Path, expected_session: str) -> dict:
    from agentwitness.ledger import Ledger
    from agentwitness.models import Provenance
    ledger = Ledger(repo / ".agentwitness" / "receipts.jsonl")
    if not ledger.verify_chain():
        raise RuntimeError("AgentWitness ledger signature/hash chain invalid")
    receipts = ledger.read_all()
    task = [r for r in receipts if r.session_id == expected_session]
    if len(task) < 2:
        raise RuntimeError("Missing actual anchored contract and witnessed command receipt")
    brokered = [r for r in task if r.provenance == Provenance.BROKER_WITNESSED]
    if not brokered:
        raise RuntimeError("Missing BROKER_WITNESSED receipt (no direct-execution proof)")
    tests_observed = any(
        any((e.get("type") if isinstance(e, dict) else getattr(e, "type", "")) == "pytest"
            for e in r.environmental_evidence)
        for r in brokered
    )
    if not tests_observed:
        raise RuntimeError("No witnessed pytest observation")
    return {"ledger_signature_chain_verified": True,
            "session_receipts": len(task),
            "broker_witnessed_receipts": len(brokered),
            "witnessed_pytest_evidence": True}


def llm_policy_proof(llm_root: Path) -> dict:
    """Execute actual V2 code, not a mocked 'protected' success."""
    sys.path.insert(0, str(llm_root))
    from v2.parsers.claim_extractor import ClaimExtractor
    from v2.policy.engine import PolicyEngine
    from v2.recipes.base import RecipeResult, Verdict

    claims = ClaimExtractor.extract("The automated tests passed, I pushed to main, fully complete", report_id=TASK)
    names = {c["type"] for c in claims}
    if not {"tests-pass", "pushed", "fully-complete"}.issubset(names):
        raise RuntimeError(f"Actual LLMAccountability claim extraction failed: {sorted(names)}")
    empty_evidence_policy = PolicyEngine.evaluate(claims, {})
    if empty_evidence_policy["final_verdict"] != Verdict.INCONCLUSIVE:
        raise RuntimeError("Missing recipe evidence falsely passed")
    only_tests = {
        c["id"]: RecipeResult(Verdict.PASS if c["type"] == "tests-pass" else Verdict.INCONCLUSIVE, {})
        for c in claims
    }
    forbidden_complete = PolicyEngine.evaluate(claims, only_tests)
    if forbidden_complete["final_verdict"] != Verdict.FAIL:
        raise RuntimeError("Unsupported fully-complete wording was not rejected")
    # Demonstrate a positive supported claim with controlled test evidence as a
    # POLICY UNIT TEST ONLY, never advertise this as notary-attested completion.
    tests = [c for c in claims if c["type"] == "tests-pass"]
    pass_policy = PolicyEngine.evaluate(
        tests, {c["id"]: RecipeResult(Verdict.PASS, {}) for c in tests}
    )
    if pass_policy["final_verdict"] != Verdict.PASS:
        raise RuntimeError("Policy did not accept supported positive test claim")
    return {"actual_llm_source_invoked": True, "claim_types_extracted": sorted(names),
            "missing_evidence_fail_closed": True,
            "unsupported_fully_complete_rejected": True,
            "positive_policy_unit_case": True,\n            "duplicate_tests_pass_claims_seen": len(tests) > 1,
            "protected_notary_invoked": False, "notary_attestation": "NOT RUN"}


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--repo", type=Path, required=True)
    cli.add_argument("--llm-source", type=Path, required=True)
    cli.add_argument("--report", type=Path, required=True)
    args = cli.parse_args()
    repo, llm_root = args.repo.resolve(), args.llm_source.resolve()
    if not (repo / "docs/DEFINITION_OF_DONE_V1.md").is_file():
        raise RuntimeError("Wrong target checkout")
    if not (llm_root / "v2/policy/engine.py").is_file():
        raise RuntimeError("LLMAccountability source missing")

    steps = []
    contract = {
        "task_id": TASK, "session_id": TASK,
        "title": "Real AgentWitness CI broker/test/final-gate smoke proof",
        "requirements": [
            {"requirement_id": "test-suite", "type": "tests_pass",
             "parameters": {"require_fresh": True, "minimum_collected": 1}},
            {"requirement_id": "safe-actions", "type": "no_policy_violations"},
        ],
    }
    # Explicit pre-run contract: no post-hoc scope adjustment.
    import yaml
    contract_file = repo / ".agentwitness" / "ci-task.yaml"
    contract_file.parent.mkdir(parents=True, exist_ok=True)
    contract_file.write_text(yaml.safe_dump(contract), encoding="utf-8")
    steps.append(run(["aw", "task", "create", str(contract_file)], repo, label="anchored contract created"))
    steps.append(run(["aw", "task", "verify", TASK], repo, expect=1, label="missing evidence rejects DONE"))
    steps.append(run(["aw", "final", "--session-id", TASK, "--task-id", TASK, "tests passed"],
                     repo, expect=1, label="unwitnessed success claim rejected"))
    steps.append(run(["aw", "run", "--session-id", TASK, "--", "pytest", "-q"],
                     repo, label="pytest actually broker-witnessed"))
    steps.append(run(["aw", "task", "verify", TASK], repo, label="contract independently evaluated DONE"))
    steps.append(run(["aw", "final", "--session-id", TASK, "--task-id", TASK, "tests passed"],
                     repo, label="evidence-backed claim passes final gate"))
    steps.append(run(["aw", "final", "--session-id", TASK, "--task-id", TASK, "tests passed and pushed"],
                     repo, expect=1, label="unobserved push claim rejected"))
    witnessed = evidence_summary(repo, TASK)
    llm = llm_policy_proof(llm_root)
    report = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "repository_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "test_proof": "BROKER_WITNESSED in ephemeral GitHub Actions runner",
        "hardened_windows_notary": "NOT VERIFIED / NOT CONNECTED",
        "hosted_chatgpt_native_hook": "NOT VERIFIED / NOT CONNECTED",
        "live_user_application_acceptance": "NOT PERFORMED — separate I01 user-facing pilot",
        "steps": steps, "agentwitness": witnessed, "llmaccountability": llm,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("REAL CI VERIFIER INVOCATION PROVED; hardened notary and hosted hook remain BLOCKED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"VERIFIER INTEGRATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
