# Existing AI Accountability Stack — Reuse and Integration Audit

**Date:** 29 October 2026 (Australia/Sydney)  
**Purpose:** Reconcile the newly created ChatGPT improvement/PIP programme with systems already discussed and developed. **Do not rebuild existing functionality.**  
**Status:** DOCUMENTED SOURCE AND GITHUB AUDIT COMPLETE for the components listed; actual combined end-to-end enforcement is **NOT VERIFIED**.

## Executive findings

**Yes: much of the proposed "senior developer" accountability already exists in code.** Our failure is primarily **adoption, integration, coverage and execution discipline**, not the absence of a PIP checklist or a new verification architecture.

The long-established design principle is:

> The agent may make claims. The agent may not award itself credit. **No evidence → no credit.**

Three requirements that the PIP described as new already exist in AgentWitness: **immutable/anchored Definition of Done contracts, evidence-backed claim verification, and final-answer gates**. LLMAccountability supplies a stronger independent evidence boundary. JoshMemory supplies durable handoffs. A separately maintained review-coordination system is documented, but its integration and security limitations must be respected.

**Critical limitation:** This audit looked at current GitHub metadata, README/architecture/source and tests directories, GitHub Actions listings, and selected previous-chat summaries. **It did not run agents on a machine, independently execute suites, test signed attestations end to end, or read 50–100 complete conversation transcripts.** A README is evidence of intended and documented code behaviour, not a substitute for a fresh demonstration.

## Verification tiers for statements in this document

- **GITHUB-CONFIRMED:** repo exists, canonical location/default branch/source paths were inspected through the connected GitHub API.
- **SOURCE/DOC-CONFIRMED:** main-branch source/test paths and repository documentation describe an implementation; **not** an executed test.
- **HISTORICAL REPORTED:** previous-chat recollection or project narrative from a dated discussion; not independently re-proven here.
- **NOT VERIFIED:** no reliable current end-to-end or live runtime result.
- **PRIVATE / REDACTED:** intentionally avoid identifying or linking private repositories in this public document.

## Verified inventory (as observed 29 October 2026)

| Project / role | Existing capability | What was checked today | Integration status / remaining issue |
|---|---|---|---|
| [AgentCheck / AgentWitness](https://github.com/Parris-Tech-Services/AgentCheck) | Broker-witnessed command receipts; signed hash-chain; `ClaimGuard`; DoD contracts, anchor/freshness/scope protection; remote SHA / CI adapters; final-answer gate `aw final`; optional hardened backend | GITHUB-CONFIRMED: canonical repo, `src/agentwitness/` modules (`broker.py`, `claimguard.py`, `ledger.py`, `backends.py`), `tests/` including hardened and trust-boundary suites. [README](https://github.com/Parris-Tech-Services/AgentCheck/blob/main/README.md) and [JoshMemory boundary](https://github.com/Parris-Tech-Services/AgentCheck/blob/main/docs/JOSHMEMORY_INTEGRATION.md). | Tool is **not** a universal machine monitor. It witnesses broker-routed commands plus provenance-labelled imports and explicit live observations. A ChatGPT workflow is NOT automatically gated simply because this repo exists. |
| [LLMAccountability](https://github.com/Parris-Tech-Services/LLMAccountability) | Protected Windows `SYSTEM` notary + restricted worker/runner; Ed25519/DSSE/in-toto attestations; claim extraction; test/Git recipes and fail-closed policy | GITHUB-CONFIRMED: `agy_service.py`, `agy_worker.py`, `v2/recipes/{tests,git}.py`, `v2/policy/engine.py`, adversarial tests; [README](https://github.com/Parris-Tech-Services/LLMAccountability/blob/main/README.md), [architecture](https://github.com/Parris-Tech-Services/LLMAccountability/blob/main/docs/ARCHITECTURE.md). | Test-pass and pushed are the two dedicated V2 recipes; no-secrets, security-reviewed and fully-complete are recognised but **INCONCLUSIVE** without dedicated recipes. Requires a working privileged Windows installation to prove its security boundary. |
| [JoshMemory](https://github.com/joshualparris/JoshMemory) | Cross-agent provenance, recorded handoffs, accountable evidence references, shared append-only cloud continuity, work leases, journals, resume briefs, trust overlay | GITHUB-CONFIRMED: `joshmemory/continuity.py`, `continuity_cli.py`, `continuity_mcp.py`, `github_store.py`; [README](https://github.com/joshualparris/JoshMemory/blob/main/README.md), [2026 master handoff](https://github.com/joshualparris/JoshMemory/blob/main/docs/CODING_2026_MASTER_HANDOFF.md). | Memories are historical context, not independent verification. Live Git/machine evidence overrides stored state. This improvement repo should link to evidence, not duplicate private memory. |
| [ForgeGrid](https://github.com/Parris-Tech-Services/ForgeGrid) / AgentBridge work | Distributed coordinator/worker execution and evidence transport; capability-aware jobs, TLS pairing, log/artifact collection | GITHUB-CONFIRMED: [README](https://github.com/Parris-Tech-Services/ForgeGrid/blob/main/README.md), [architecture](https://github.com/Parris-Tech-Services/ForgeGrid/blob/main/ARCHITECTURE.md), Go source/tests. | Transport/execution is not an independent verifier by itself. A local supervisor should choose jobs; verification stays elsewhere. Live fleet health was not tested today. |
| AgentCouncil (PRIVATE / redacted) | Independent code reviewers using Claude/Codex/Antigravity CLIs, worktree isolation, runner-owned tests, reviewed/council/critical tiers and evidence ledger | Source/docs/test paths were inspected privately today. Repository name/path and private links intentionally withheld from the public audit. | Explicitly **does not auto-merge or push**; it does not route the CLIs through `aw run` and therefore cannot pretend that ClaimGuard verified that activity. Local host test sandbox and some agent permission boundaries remain limited. |
| JoshSupervisor / DadLAN Mission Supervisor | Durable observe → implement → test → independent review → revise/resume mission loop | HISTORICAL REPORTED in discussions and [JoshMemory handoff](https://github.com/joshualparris/JoshMemory/blob/main/docs/CODING_2026_MASTER_HANDOFF.md). | No current source/runtime directly checked for the supervisor in this audit. Investigate existing deployed implementation before changing/rewriting anything. |
| `josh_reviewer` / Codex reviewer | Adversarial second opinion, objection/repair cycles | HISTORICAL REPORTED; existing reviewer pattern also described in inspected private coordination docs. | Review is not equivalent to fresh test evidence; avoid treating reviewer consensus as the final authority. |
| CRAP4All and portfolio code-quality gates | Complexity, coverage, mutation, security/lint/CI metrics and quality ratchets | [2026 master handoff](https://github.com/joshualparris/JoshMemory/blob/main/docs/CODING_2026_MASTER_HANDOFF.md) describes past implementation; codebase not independently audited today. | Engineering-quality signals complement, but do not replace, functional completion and verification. |

### Canonical location correction

The previously cited `joshualparris/AgentCheck`, `joshualparris/LLMAccountability` and `joshualparris/ForgeGrid` URLs resolve through moved-repository redirects. GitHub metadata returned the canonical **Parris-Tech-Services** locations linked above. **AgentWitness is the package/product within AgentCheck**, although there were historically distinct working clones/branches with similar names. Do not collapse those historical local checkouts into one location or delete them without validating live state.

### Actual GitHub CI evidence (not runtime validation)

At the time of this audit:

- **AgentCheck:** GitHub Actions reported 40 historical workflow runs. Recent observed successful run included [main at 17 September](https://github.com/Parris-Tech-Services/AgentCheck/actions/runs/35222178155); a later PR workflow also succeeded [29 September](https://github.com/Parris-Tech-Services/AgentCheck/actions/runs/36644038927). The **current main SHA** was `4d7746d664e4c2d75e64a8436df0bc9b7c9dfc9e`; we did **not** establish a passing workflow at that exact head.
- **LLMAccountability:** no GitHub Actions runs returned. This is **absence of GitHub Actions evidence**, not proof that local tests or runtime fail.
- **AgentCouncil:** no GitHub Actions runs returned. Its own docs report historical local tests and real reviewed sessions; these were **not rerun** today.
- **ForgeGrid:** 78 historical GitHub Actions runs returned; a successful 25 September PR run was observed, but no live fleet test occurred.
- **JoshMemory:** implementation and docs inspected; CI not assessed in this audit.

## Existing ownership boundaries — preserve these

```text
USER REQUIREMENT / IMMUTABLE ACCEPTANCE CONTRACT
                |
                v
DURABLE SUPERVISOR / PROJECT QUEUE -- JoshMemory context and work lease
                |
                v
BUILDER / IMPLEMENTER -- local or hosted agent and repo worktree
                |
                v
REPRODUCIBLE TESTS + LIVE STATE -- external evidence producers
                |
                +-- AgentWitness/AgentCheck: provenance, ClaimGuard, DoD, final gate
                |
                +-- LLMAccountability: hardened protected test/Git notary (where available)
                |
                +-- independent semantic reviewer / council: objections and repair
                |
                v
GATE: contract satisfied?  NO -> REWORK / BLOCKED / HUMAN_REQUIRED
                |
               YES
                v
AUTHORISATION-AWARE MERGE / DEPLOY / LIVE SMOKE VERIFICATION
                |
                v
EVIDENCE-BACKED FINAL CLAIM + JoshMemory provenance reference
```

**Warning:** This is the **target integration architecture assembled from existing parts**, **not** a claim that one fully functioning, unattended integration is already deployed. Implementation and independent review alone do not establish production acceptance.

## What already solves the newly proposed PIP

| New PIP demand | Existing reusable mechanism | Remaining step |
|---|---|---|
| Written acceptance criteria / DoD | AgentWitness v3 anchored task contracts | Translate the user's accepted requirements into a verified contract at the start of real work |
| Don't self-grade / no fake DONE | ClaimGuard, `aw final`, signed receipt ledger | Actually route supported commands and final reports through the gate; disclose bypasses |
| Proof that tests genuinely ran | Broker-witnessed pytest/Vitest evidence, fresh workspace and scope controls; hardened `python-full` recipe | Match verifier to language/environment; add real live browser acceptance where required |
| Verify correct commit, push, CI | Git/remote SHA and CI adapters; V2 pushed recipe | Verify exact SHA, target branch, job conclusion, production build/URL (separate) |
| Independent semantic review | Existing multi-agent reviewer/council and Codex supervisor patterns | Preserve reviewer isolation; feed objections into bounded repair, do not self-award PASS |
| Persist tasks/checkpoints | JoshMemory handoffs, journals, leases, source evidence references | Integrate per-task reporting with durable shared store; don't copy private transcripts into this public repo |
| Autonomous retry/resume | Existing local Mission Supervisor ideas/implementation | Check actual running state and close the gap to ChatGPT's hosted tool workflow |
| KPI dashboard | PIP scorecard + historical quality metrics | Collect real denominators across complete tasks; don't mistake logs or commits for completed outcomes |
| Privileged adversarial proof | LLMAccountability protected notary | Verify real installation and runner identities; unsupported claims remain INCONCLUSIVE |
| Cross-machine execution | ForgeGrid/AgentBridge | Restore/check any required machines; remote execution is never evidence of correct results by itself |

## Gaps and risks that remain

1. **MANDATORY ADOPTION — highest priority.** Nothing establishes that ChatGPT in this hosted conversation actually invoked `aw final` or the hardened notary on its work. Repository availability does not install enforcement into ChatGPT. User feedback on recent tasks indicates this gap is operationally important.
2. **Integration trust mismatch.** The reviewed multi-agent coordinator currently runs CLIs independently; its own doc explicitly explains why ClaimGuard cannot meaningfully audit an empty broker ledger. Use orchestrator-run tests and carefully labelled provenance today; don't mislabel direct-CLI runs `BROKER_WITNESSED`.
3. **Live acceptance gap.** Passing unit tests, GitHub CI, and a deployment starting do not prove game interactions, browser UI, mobile navigation, login, data persistence, security requirements, or other end-user acceptance. Add environment-specific smoke and regression checks to contracts and report unsupported checks as NOT VERIFIED.
4. **Uncovered claim families.** LLMAccountability V2 currently supports dedicated test-pass and push recipes, not universal proof of secret-free, security-reviewed or fully-complete status.
5. **Execution isolation gap.** Coordination project docs describe risks from unsandboxed test execution and some model adapters. Do not turn higher permissions on or run arbitrary tests with secrets to chase KPI targets.
6. **Local privileged runtime availability.** The Windows notary requires an installed/reachable privileged runner; historical machine-level blockers were reported. We did not check its present service state.
7. **Evidence provenance/security.** A signing receipt can prove receipt integrity without proving the original execution was independently observed. Historical conversations also highlighted handling signing secrets safely; do not commit private keys/evidence stores, assume external transparency anchoring, or treat a locally held signing key as tamper-proof.
8. **Human approval boundary.** Existing coordination tooling deliberately does not auto-merge. Any autonomous continuation must respect user permissions, repo rules and explicitly authorised external actions, especially emails.
9. **Chat-history audit remains incomplete.** Selected prior conversations and master handoff are not all 50–100 full chat transcripts. Only a systematic, complete evidence extraction can support historical rates.

## Recommended first engineering action — PIP-001 integration proof

**Do not build a new accountability app.** Choose a small, real, already authorised engineering task in an existing repository and implement the smallest **demonstrable** end-to-end accountability path:

1. Inspect current repo, branch, tests, runner availability and the relevant live app.
2. Freeze its Definition-of-Done contract before modifying code.
3. Implement via the existing workflow; route supported commands through AgentWitness where actually possible.
4. Independently test; use the hardened verifier if the protected runtime is installed; otherwise explicitly record its absence.
5. Request independent semantic review if appropriate; repair any objections.
6. Verify exact commit/PR, merge/deploy status (where authorised), then the actual user-visible behaviour.
7. Invoke an actual final claim gate (not merely cite its existence).
8. Record evidence references and disposition in JoshMemory; update PIP measures with only the verified result.

**Exit condition:** exact evidence links, verdicts, final user-facing outcome, and a written explanation of any unobserved actions. If the workflow can't reach the gate from hosted ChatGPT tools, call that **INTEGRATION BLOCKED** and document the adapter requirement without pretending a PIP markdown file changed the model runtime.

## Privacy and audit discipline

This is a **public** improvement repository. Private repository URLs/metadata, machine details, personal conversations, API credentials, keys, private memory payloads and raw transcripts are intentionally omitted. Links above point to public sources only. A private source can inform a public-safe role/capability summary but must not be cited with a revealing locator.

**Conclusion:** New PIP = **governance/measurement layer** over the existing stack. The first real engineering task = **enforce and prove adoption**. **No evidence → no credit.**
