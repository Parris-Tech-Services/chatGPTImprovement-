# S02 · Signing keys, attestations and unsafe test execution: security audit

**Date:** 29 October 2026 · **Auditor:** Claude (Claude Code session) · **Backlog task:** S02 (P0)
**Acceptance:** *"Security review with evidence, key leak canary tests and remediation plan; no production key disclosure in report."*

## Scope actually examined

| Component | Examined | How |
|---|---|---|
| This repository's CI (`real-verifier-proof`, `dod-policy`, `public-safety` workflows) | **Yes** | Workflow source review; live CI runs on branch `s02-key-leak-canary` |
| AgentWitness at pinned commit `4d7746d` (Parris-Tech-Services/AgentCheck), as executed in CI | **Behaviour only** | The key-leak canary ran against the keys it creates during the real CI run. Source **not** read: repository access was denied to this session and the archive host is blocked |
| LLMAccountability at `881ef0c` | **Behaviour only** | Exercised by the existing proof script; source not read (same blocker) |
| Windows notary, worker and runner (L01) | **No — BLOCKED** | No access to the approved machine |
| Private reviewer and supervisor (C-track) | **No — BLOCKED** | Private; no access |
| ForgeGrid | **No — BLOCKED** | Repository access denied to this session |

No production key was available to or examined by this audit, and none appears in this report.

## Findings

| ID | Severity | Finding | Evidence | Status |
|---|---|---|---|---|
| **S02-1** | **High** on shared or persistent machines; low on ephemeral CI | **AgentWitness writes its private signing key `private.pem` with mode `0644` (group- and world-readable).** Any local user or process on the same machine can read the key and forge broker-witnessed receipts. | The canary's first CI run on commit `2923417` flagged it (check run `123340165135`, annotation *"key private.pem: permissions 0o644 allow group/other access"*). | **Open, upstream.** Tracked as a CI warning (`--known-permission-finding private.pem`); key leaks still fail CI. |
| S02-2 | Medium | **Target tests run on the same runner, as the same user, as the AgentWitness signing key.** `aw run -- pytest -q` executes repository test code, so a malicious PR's tests can read the run's ephemeral key and sign forged receipts **within that run**. | `.github/workflows/real-verifier-proof.yml` and `scripts/verify_agent_stack_ci.py`: tests and signing share one job and user. | Open |
| S02-3 | Medium | **Third-party actions were pinned by mutable tag** (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`) in all three workflows, so a moved tag changes what runs. | `grep uses: .github/workflows/*.yml` | **Fixed in this PR** for `dod-policy` and `real-verifier-proof`: every `uses:` is pinned to the tag's current commit (checked with `git ls-remote`), with the tag kept as a comment. `public-safety.yml` is pinned the same way in PR #13. |
| S02-4 | Medium | **Verifier dependencies install unpinned at run time** (`pip install -e .external_verifiers/agentcheck pytest`): `pytest` and AgentCheck's transitive dependencies resolve to whatever PyPI serves that day. | `real-verifier-proof.yml` step *Install actual AgentWitness CLI* | Open |
| S02-5 | Info (positive) | No key material in published outputs. The proof artifact, the captured verifier log and every git-tracked file were checked against the real key in raw, hex, base64 and 24-character fragments: **0 leaks**. | Same CI run (only S02-1 was reported) | Holds for this run; checked on every run from now on |
| S02-6 | Info (positive) | External verifier repositories are pinned to full commit SHAs; every checkout uses `persist-credentials: false`; workflow tokens are `contents: read`; no `pull_request_target` trigger. | Workflow source | Holds |
| S02-7 | Info | Receipt history and trust anchors (key rotation, revocation, which public key a receipt should verify against) **could not be reviewed**: they live in AgentWitness and LLMAccountability source, which this session could not read. | — | **BLOCKED** |

## Key-leak canary (delivered)

- [`scripts/key_leak_canary.py`](../scripts/key_leak_canary.py) finds private-key files: PEM private keys, plus `*key*`, `*private*`, `*secret*`, `*.sk` and `*signing*` names. Public keys are excluded.
- It checks that no published output contains the key's material in raw, hex or base64 form, or any 24-character fragment of it. Published outputs are artifacts, logs and every git-tracked file.
- It flags keys that are group or world accessible, or tracked by git, and **refuses to pass if it found no key at all**.
- Findings never echo key values.
- [`tests/test_key_leak_canary.py`](../tests/test_key_leak_canary.py) has 9 seeded-key tests: each encoding of a leak, permissions, git-tracked keys, public keys, the no-keys case, low-entropy false alarms, and a known permission finding that never masks a leak.
- The canary runs on every `real-verifier-proof` CI run, against the keys real AgentWitness generates.

## Remediation plan

| # | Fixes | Change | Owner | Verification |
|---|---|---|---|---|
| 1 | S02-1 | Create the key with `os.open(path, O_WRONLY \| O_CREAT \| O_EXCL, 0o600)` (or `umask(0o077)` around key generation) and refuse to load a private key readable by group or others. | AgentCheck | Drop `--known-permission-finding private.pem` from this workflow; the canary must then pass with no warnings. |
| 2 | S02-2 | Run target tests in a separate job, container or OS user that cannot read the signing key, and pass only the test result into the signing step. Mark receipts from PR runs as untrusted beyond that run. | AgentCheck / this repo's CI | A deliberately malicious test that tries to read the key fails, while honest tests still pass. |
| 3 | S02-3 | Pin every `uses:` to a full commit SHA, with the tag in a comment; let Dependabot propose updates. | This repo | `grep -E 'uses: [^@]+@[0-9a-f]{40}'` matches every `uses:` line. |
| 4 | S02-4 | Install from a hash-pinned requirements file (`pip install --require-hashes -r ci-requirements.txt`). | This repo | CI fails if a dependency hash changes. |
| 5 | S02-7 | Review key rotation, revocation and trust-anchor handling once access to AgentWitness, LLMAccountability and the notary machine is granted (L01, L06). | Programme owner | Key-rotation and compromise simulation (A06). |

## Status

**PARTIALLY COMPLETE.**
- **Done:** the canary, its tests and its CI integration, plus a reviewed pipeline with evidence and the remediation plan.
- **Not done:** the signing-key, receipt and trust-anchor review inside AgentWitness, LLMAccountability, the notary and the reviewer. Those are blocked on access.
- S02-1 to S02-4 remain open until the remediations land.
