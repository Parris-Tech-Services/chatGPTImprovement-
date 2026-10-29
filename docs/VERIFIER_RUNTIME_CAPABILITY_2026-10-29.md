# I02 — Actual Verifier Runtime Capability and Honest Integration Boundaries

**Investigated:** 29 October 2026 (Australia/Sydney)  
**Tracked work:** I01 / I02, [PR #12](https://github.com/Parris-Tech-Services/chatGPTImprovement-/pull/12), [master backlog](MASTER_ACTION_BACKLOG_2026-10-29.md).  
**Design goal:** Use existing verification tools for a real task; no more verification theatre.

## Proven vs inaccessible

| Runtime / component | How checked | Actual result | What it does NOT prove |
|---|---|---|---|
| Hosted ChatGPT container session | Checked executable availability and Python imports (`aw`, `agy`, `agentwitness`, `v2`); no internet DNS in local container | No locally installed verifiers; cannot directly reach user's private Windows SYSTEM/worker/runner from hosted environment | This does **not** say verifiers are uninstalled on the user's personal machines |
| GitHub-hosted ephemeral Ubuntu Actions | Read-only checkout of the improvement repo and exact pinned public verifier commits; install actual CLI from AgentCheck | **Working indirect execution route**: `aw task create`, `aw run`, `aw task verify`, `aw final`, signed receipt validation, missing-evidence and fake-push negative cases | Not native ChatGPT lifecycle interception, nor an OS-wide monitor |
| LLMAccountability pure V2 code on Actions runner | Import and exercise actual `ClaimExtractor`, `PolicyEngine`, `Verdict`, `RecipeResult` from pinned checkout | Real policy code evaluated for missing evidence, inappropriate fully-complete wording, and positive supported claim | In-memory recipe results are **unit-control fixtures**, not notary-produced evidence or signed attestation |
| LLMAccountability V2 `agy.py audit-report --enforce` on Ubuntu Actions | Actual CLI invoked in a runner without a protected notary on loopback 8123 | **Must reject** completion because no notary is available, and fail pipeline if it unexpectedly succeeds | Does not certify test/Git results; proves only fail-closed missing-service behaviour |
| AgentWitness `aw task verify --hardened` on Ubuntu Actions | Invoke real hardened evaluation with no Windows service or trusted notary key | **Must reject**; previous non-hardened receipts cannot be upgraded to hardened evidence | No proof of a functioning SYSTEM notary/attestation |
| User's Windows protected notary/worker/runner | No authorised network access to that workstation or Windows service from current tools | **NOT CHECKED / NOT CONNECTED** | Cannot claim the installed security identities, service, keys, ACLs or attestation validity |
| Live browser/mobile/gameplay | No target app selected or live acceptance criteria executed by this CI harness | **NOT PERFORMED; I01 remains open** | CI output cannot verify all end-user behaviour |
| Independent review | Greptile requested on PR #12; Github Actions provides independent execution environment | Review is distinct from proof of protected signing; track any findings and verify repairs | Reviewer consensus is not evidence by itself |

## Real integration workflow

[`real-verifier-proof.yml`](../.github/workflows/real-verifier-proof.yml) provides **read-only** CI integration using:

- AgentWitness pinned to `4d7746d664e4c2d75e64a8436df0bc9b7c9dfc9e`.
- LLMAccountability pinned to `881ef0cdd8da3a3bd025bdc78ed8e00cef602ad8`.
- The improvement repository's own pytest acceptance suite as the sample *real codebase*; no fake zero-test fixtures.
- A real task/session contract with `tests_pass` and `no_policy_violations`.
- Genuine `aw` CLI invocations with a test evidence receipt and independently verified local Ed25519 ledger hash chain.
- Negative controls for no tests, no observed push, missing protected notary.
- Real LLM V2 source evaluation; no spoofed privilege or signed success.
- A short `verification-proof.json` artifact (retention 7 days); **never upload .agentwitness/, protected keys, raw agent logs or private conversations**.

### How to apply to other work

1. Define actual task-specific criteria including user-facing acceptance before editing code.
2. Use GitHub-hosted CI as a reachable **verification executor**, not as automatic omniscient observation of all actions that happened earlier in ChatGPT.
3. If scope is a new application, replace the demo test contract with that app's actual suite and an independent browser/live test; don't claim cross-repository coverage from this smoke demo.
4. A local Windows notary must be provisioned and operated **separately and with explicit machine-owner approval**. Existing `install_service.ps1` changes machine accounts, tasks, ACLs and logon rights and is therefore **not executed** by this workflow.
5. Do not expose a privileged notary to the public internet or store any signing key in Actions artifacts, repository commits or unprotected secrets.
6. For a future private, trusted runner connection, prefer a strictly allowlisted, short-lived request path using user-approved jobs and attestation verification; keep untrusted PR execution **away** from the SYSTEM host.

## Why this does not automatically change ChatGPT

GitHub Actions runs when a repository event occurs. ChatGPT can **start this indirect route** by committing a scoped workflow/input branch where authorised, and can then inspect the resulting run through GitHub tools. That does **not** inject `aw final` into all ChatGPT conversations or give the model access to a local Windows machine.

A fully integrated hosted workflow would need an authorised host-level connector/MCP or other execution bridge (remaining `A02/I04`) with policies, independent evidence and no secrets exposure.

## Next definitive acceptance

**I01** requires using the newly proven broker path for an actual app issue: freeze acceptance in AgentWitness, execute real tests, independently inspect PR/CI and verify the user-facing result before reporting verified completion. **I02** is an execution/access inventory and smoke proof, not a replacement for I01 or L01.

## Measured status

Review the run/commit links in [PR #12](https://github.com/Parris-Tech-Services/chatGPTImprovement-/pull/12) and GitHub Actions before updating this summary. A linked run is proof only for its exact SHA and executed checks, not for unrun conditions.

**Privacy:** this document is intentionally public-safe; do not commit any workstation address, credentials, private signing keys or personal conversation text.
