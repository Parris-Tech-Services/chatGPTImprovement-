# G01 — Canonical Definition of Done and Status Contract (v1)

**Scope:** ChatGPT Improvement PIP governance. This document defines the **public outcome vocabulary**, not an alternative execution witness or attestation authority. [AgentWitness / AgentCheck](https://github.com/Parris-Tech-Services/AgentCheck) owns signed contract anchors, broker receipts, source/test freshness and actual final-gate evidence. [LLMAccountability](https://github.com/Parris-Tech-Services/LLMAccountability) provides stronger independent test/Git verification when its protected Windows runtime is available.

## The first engineering rule

A task is **VERIFIED COMPLETE only when all frozen user acceptance criteria have independently checked PASS evidence and no work or blocker remains.** For a user-facing application task, at least one explicit `live` criterion must be exercised in the actual target environment. A passing test suite, green CI, PR merge, GitHub push, deploy starting, HTTP 200 or unverified model statement is **not** that proof.

## Before implementation

1. Capture the exact original user outcome, project/environment, date, constraints and permission boundaries.
2. Freeze a numbered set of testable acceptance criteria including meaningful end-user behaviour where applicable; do not silently weaken criteria after implementation.
3. Identify consequential external actions (emails, spending, merge, deploy, privilege changes) and obtain **specific** approval. A broad end-to-end request never permits sending email without an explicit, send-specific instruction.
4. Use AgentWitness `aw task create` and its signed contract-creation receipt when the runner is actually available. This repo's record `digest_sha256` detects **accidental drift only**: it can be recomputed by whoever edits the file and is not signed proof or user authorisation.
5. Record current state, owner, precise outstanding work and references. JoshMemory may retain the history, but cannot turn an assistant's assertion into independent proof.

## Canonical statuses

| Status | Strict condition | No-go |
|---|---|---|
| `NOT STARTED` | Outcome and criteria may be prepared, but no task execution/evidence exists | Must not report code implemented |
| `PARTIALLY COMPLETE` | Concrete work is recorded and **remaining_work** describes unfinished acceptance | Can't silently equate a PR, green CI or partial build with user success |
| `BLOCKED` | Exact **reason**, **attempted_alternatives** and **next_action** recorded | No vague 'couldn't do it', no invented alternate attempts |
| `VERIFIED COMPLETE` | Every accepted criterion PASS with correct independent observation and **no** remaining work/blocker | No self-report/transcript import alone, no untested live user flows |
| `CANCELLED` | Genuine user cancellation/not-applicable with recorded reason | Must be excluded transparently from completion denominator |

AgentWitness task states (DONE, FAILED, READY_FOR_VERIFICATION, BLOCKED) and our public PIP statuses are **not interchangeable**. An AgentWitness `DONE` only proves the specific contract it actually evaluated; missing human/UX requirements cannot be assumed satisfied.

## Evidence record and offline checker

The offline `scripts/check_task_record.py` enforces **shape and internal consistency of untrusted metadata**. It does not execute verification, authenticate external signatures, validate approval references or determine whether an evidence URL is true.

Record format (public-safe illustration):
```json
{
  "schema_version": 1,
  "task_id": "DEMO-01",
  "task_type": "software",
  "user_facing": true,
  "actor": "implementer",
  "status": "PARTIALLY COMPLETE",
  "contract": {
    "user_outcome": "Working user-facing feature",
    "criteria": [
      {"id": "AC-1", "kind": "test", "description": "Run required test suite"},
      {"id": "AC-2", "kind": "live", "description": "Observe actual deployed user interaction"}
    ],
    "digest_sha256": "CALCULATE_WITH_CLI"
  },
  "results": [
    {"criterion_id": "AC-1", "outcome": "PASS", "evidence_ids": ["TEST-1"]},
    {"criterion_id": "AC-2", "outcome": "NOT_RUN", "evidence_ids": []}
  ],
  "evidence": [
    {"id": "TEST-1", "reference": "public-safe-evidence-id",
     "kind": "test", "provenance": "broker_witnessed",
     "observed_by": "independent-runner"}
  ],
  "external_actions": [],
  "remaining_work": ["Live user interaction not yet tested"],
  "blocker": null
}
```

`task_type`: software/documentation/research/support/other. Criterion `kind`: artifact/test/live/security/review/deployment. Outcome: PASS/FAIL/NOT_RUN/BLOCKED. Provenance: self_reported/transcript_imported/external_observed/broker_witnessed/hardened_observed. These are **untrusted strings** in this JSON, not independently verified signatures. Actual independent receipt IDs and exact SHA should remain in authoritative evidence sources; don't put private conversations in this public repository.

To prepare and check an authorised task record:
```bash
python scripts/check_task_record.py /path/to/private-record.json --stamp-contract
python scripts/check_task_record.py /path/to/private-record.json
python -m unittest discover -s tests -v
```

Set `digest_sha256` to the computed digest at contract creation. It must not be changed after work starts without an approved supersession and a stronger signed AgentWitness contract anchor.

Exit `0` = internally consistent **ONLY**; `1` = inconsistent; `2` = unreadable/invalid JSON/contract. Zero exit does **not** certify independent success.

## G01 negative acceptance, required in CI

- User-facing task with no `live` criterion is rejected even if automated tests pass.
- User-facing task with a `live` criterion that is NOT_RUN, has no evidence, has mismatched evidence kind, or only self-reported/transcript-imported evidence is rejected if it claims VERIFIED COMPLETE.
- Missing/failed criteria, stale/drifted contract hash, duplicate IDs, remaining work, blockers or missing action approval metadata also reject VERIFIED COMPLETE.
- For a performed mail action, the recorded approval_scope must be that **exact** action, not `general_assistance`. This is metadata hygiene, **not authentication of an approval**.
- An actor cannot claim their own observation as independent. Record actual provenance at source rather than changing a text field to get a green check.

## Ownership and limitations

- AgentWitness verifies actual observed commands, anchored contracts, Git/CI/test evidence and final claims, **when genuinely invoked**.
- LLMAccountability checks only supported recipes with a working local notary and signed attestations. Unsupported security/semantic claims remain INCONCLUSIVE.
- Independent reviewer assesses real artifacts and user outcomes, not just the implementer's assertions.
- JoshMemory preserves external provenance and handoffs; live Git/API/machine evidence wins over memory.
- This policy linter is an **offline quality check only**. Its test fixtures demonstrate consistency; they do not prove that a real task, application or tool was tested or that the underlying ChatGPT model has changed.
- Privacy: never publish raw conversations, credentials, signing keys, private repository paths or customer data in this public repo.

## Next, separate task

`I01/I02` must actually connect and exercise AgentWitness, the supported LLMAccountability backend, independent review and a real application workflow. Until a reachable, authorised runtime is verified, status is **INTEGRATION BLOCKED**, not an invented COMPLETE.
