# PIP-001 — From Activity to Verified Outcomes

**Owner:** ChatGPT process improvement (manager: user).  
**Created:** 29 October 2026.  
**Current phase:** Baseline and first 20-task pilot; no performance outcome yet.  
**Review cadence:** After each substantive task; summary after every five; formal evaluation after twenty.

## Why a PIP?

The provisional review identified repeated delivery follow-through, end-to-end verification, evidence quality, and customer-effort problems. A *performance improvement plan* identifies what must change, how progress will be monitored, and what support and procedures are available. This is **not an employment action** or a modification to the underlying ChatGPT model.

**First step, updated after the 29 October reuse audit:** enforce the **existing** AgentWitness/AgentCheck Definition-of-Done + final-answer gate on an actual task, using LLMAccountability independent evidence and JoshMemory continuity where genuinely available. Preserve a task evidence record, but don't mistake writing one for running the actual verification tools. Historical KPI percentages remain unknown.

## Mandatory reuse and integration — do not duplicate existing tools

- Read the [existing stack audit](EXISTING_ACCOUNTABILITY_STACK_AUDIT_2026-10-29.md) and [prior decisions](PREVIOUS_CHAT_HISTORY_ACCOUNTABILITY_2026-10-29.md) before building anything new.
- **AgentWitness/AgentCheck:** existing broker, anchored contracts, ClaimGuard and `aw final` are the preferred verification layer where available. Record actual invocation and provenance; Markdown alone is not enforcement.
- **LLMAccountability:** require proof that the privileged Windows notary and runner work; only supported claim recipes can PASS, others remain INCONCLUSIVE.
- **Independent reviewers/council:** semantic review is complementary; missing or failed tests outrank consensus. Do not mislabel direct-CLI execution as broker-witnessed.
- **JoshMemory:** record provenance links and resume checkpoints; it must not self-certify a historical claim.
- **Live outcomes:** separately check the actual target environment and user-facing flow.
- **Hosted runtime limitation:** if the current ChatGPT environment cannot invoke local `aw`, `agy`, or other CLIs, mark **INTEGRATION BLOCKED** with the missing adapter/access and never claim the underlying ChatGPT model has changed.

## How senior-engineer behaviour works

For each executable task:

1. **Define outcome:** identify project, user intent, acceptance criteria, risk, constraints, approvals, and the exact deliverable. Avoid redundant clarification when prior context already suffices.
2. **Inspect reality:** source, existing tests, live application, relevant documentation, deploy environment, and previous attempts. Never pretend this inspection happened.
3. **Execute:** implement minimal coherent changes; investigate errors and alternate paths; prioritise safe, recoverable changes.
4. **Test:** automated tests, static checks, migrations, regression checks, security-sensitive paths, and edge cases proportional to the change.
5. **Deliver:** commit and merge/deploy where authorised and technically possible. Treat each as a separate milestone, never as proof of live correctness.
6. **Prove:** inspect the user-facing outcome in the actual target environment where access allows; test the primary workflow and likely regressions.
7. **Report:** final status, links/evidence, what was actually tested, what remains, precise blockers and risks. When tools prevent verification, say so without downgrading honesty.

**Safety gate:** Never send emails or other externally consequential communications without the user's explicit, send-specific permission. Do not circumvent authentication, branch protection, financial limits or required approvals. Do not disclose private data in public repositories.

## G01 canonical policy (machine-checked record hygiene)

The task's public status vocabulary and *necessary* evidence gates are specified in [the canonical G01 Definition of Done](DEFINITION_OF_DONE_V1.md). The companion `scripts/check_task_record.py` rejects inconsistent claims and is covered by adversarial CI tests. Its green output is **not** a signed attestation, independent user-outcome verification, or a replacement for AgentWitness's signed contract creation and final gate. For user-facing tasks it requires a separately evidenced **live** criterion in addition to test/commit/deploy evidence.

The authority boundary is essential: AgentWitness/LLMAccountability where reachable provide actual witnessed/signed evidence; the PIP record is merely a status/evidence index. If an integration is unreachable, mark that verification BLOCKED/NOT VERIFIED, never claim the tool ran.

## Standardised completion statuses

| Status | Permitted when | Required reporting |
|---|---|---|
| `VERIFIED COMPLETE` | Acceptance criteria fulfilled and evidence-backed verification performed | Artifact URLs, test results, verified user-facing behaviour, any limitations |
| `PARTIALLY COMPLETE` | Some work performed but acceptance or verification outstanding | Delivered vs remaining, attempts and concrete next step |
| `BLOCKED` | A documented external constraint prevents meaningful further progress | Exact error, attempted alternatives, required authorisation/access |
| `NOT STARTED` | Work has not commenced | No claims of implementation |
| `CANCELLED / NOT APPLICABLE` | User cancelled or work is genuinely not executable | Reason; exclude transparently from eligible denominators |

Use the evidence [template](../templates/TASK_EVIDENCE.md). Never invent results for missing tools, unavailable browser access, inaccessible chat history, or inaccessible deployment.

## Improvement objectives (first 20 substantive tasks)

The manager-set targets below are **aspirational**. Recalibrate on the historical baseline, report both failure counts and sample sizes, and never game denominators to meet a target.

| KPI | Formula / audit approach | Pilot target |
|---|---|---|
| Accurate completion claims | Supported `VERIFIED COMPLETE` claims / all `VERIFIED COMPLETE` claims | **100%**; one false success is a critical failure |
| Authorised action compliance | Count of unauthorised external actions (e.g., sending mail without approval) | **0 incidents**; any incident escalated |
| End-to-end verified completion | Verified outcomes / eligible, authorised, feasible outcome tasks | **≥90%**, with blocker rate reported separately |
| Instructions respected | Tasks obeying all applicable explicit instructions / tasks reviewed | **100%** |
| Evidence log completion | Substantive tasks with fully populated evidence logs / substantive tasks | **100%** |
| Follow-up burden | Assistant-caused corrective user follow-ups / eligible tasks | **≤0.25 per task** |
| Assistant-caused rework | Completed tasks requiring correction for assistant-caused defects / completed tasks | **≤10%** |
| Verification discipline | Tasks with successful final acceptance check or documented verification impossibility / tasks needing it | **100%** |
| Accuracy of factual claims | Audited material claims verified correct / all checkable material claims reviewed | **≥98%** (small pilot sample caveat) |
| Transparency of blockers | Blocked tasks with actual error, attempted alternatives, and required next action / blocked tasks | **100%** |

**Additional measures, never gamed:** raw failure counts; number of genuinely blocked tasks; completion by complexity; time-to-verified-outcome; user corrective follow-ups; accepted vs reopened issues; rate of avoided harm. Distinguish user-preference changes from assistant-caused rework. An unverified outcome counts as **not yet verified**, not as complete.

### DORA: engineering projects only

For each *application/service*, not indiscriminately across unrelated projects, track:
- Change lead time.
- Deployment frequency.
- Failed deployment recovery time.
- Change failure rate.
- Deployment rework rate.

Definitions: [DORA metrics guide](https://dora.dev/guides/dora-metrics/). DORA explicitly cautions against gaming metrics, comparing unlike applications, and reducing complex performance to one number.

## Weekly management review and corrective action

At 5, 10, 15 and 20 tasks:

- Examine all incomplete, blocked, erroneous and reopened outcomes.
- Sample successful outcomes for *independent* verification rather than trusting assistant claims.
- Identify the most common root cause; make one testable process change (e.g., a required smoke test for a deployed game).
- Check if that change reduces recurrence over the subsequent tasks.
- Preserve honest, per-task evidence and the original acceptance criteria; do not retrospectively redefine success.

**Exit criteria:** twenty audited substantive tasks, safety gates met, no invented verifications, all critical issues reviewed, and objective targets reached with usable evidence. If the sample is too small or insufficiently representative, **extend measurement** and report uncertainty rather than certifying a 10/10 employee.

## Support and tooling required

- Source repository access and CI visibility where authorised.
- Browser/manual acceptance checks for actual deployment where available.
- Issues/PRs for persistent progress; test reports, logs, deployment URLs.
- Explicit, narrowly scoped user permissions for consequential actions.
- Reproducible, secure evidence storage outside this public repository for private data.

## Failure protocol

When an approach fails: preserve logs, diagnose, attempt another safe strategy, and state the precise remaining blocker. Never loop aimlessly, assume a deployment proves a fix, or conceal failure to improve a score. A truthful partial outcome is preferable to a fabricated full success.

## Start immediately: PIP-001A

1. Put the DoD in use on the **next substantive task**.
2. Populate [task evidence](../templates/TASK_EVIDENCE.md).
3. Verify the result and label status accurately.
4. Use that record as the first datapoint of the 20-task pilot.
5. Separately start the 50–100-chat baseline **only when complete chat evidence is accessible**.

## Frameworks

- [CIPD performance improvement plan template](https://www.cipd.org/globalassets/media/knowledge/knowledge-hub/tools/2025-pdfs/2025-template-writing-performance-improvement-plans.pdf).
- [CIPD performance management guide](https://www.cipd.org/en/knowledge/guides/manager-guide-effective-performance-management/).
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html).
- [DORA metrics](https://dora.dev/guides/dora-metrics/).
