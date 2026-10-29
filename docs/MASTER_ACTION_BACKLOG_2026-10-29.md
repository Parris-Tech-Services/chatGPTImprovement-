# Master Outstanding Work Backlog — ChatGPT Agent Improvement

**Compiled:** 29 October 2026 (Australia/Sydney)  
**Scope:** All outstanding action items surfaced in this ChatGPT improvement conversation, current research/PIP documents and directly inspected relevant repositories. This does **not** claim a comprehensive audit of every previous chat, all open projects or private machine state.

**Status:** 52 specific items identified; **1 VERIFIED COMPLETE (G01), 51 OPEN**. The G01 evidence is linked below; remaining underlying capabilities may exist, but their specific acceptance requirements are still unverified in this programme. Some underlying capabilities already exist; OPEN means the **specific acceptance evidence requested here has not been produced in this programme**. Existing features should be verified before new engineering work is started.

**Owner assignment:** Functional system/repository is assigned below, **not a GitHub user or an autonomous agent invocation**. No people were assigned or notified. Private review/supervisor work is role-named without exposing private repository URLs.

## What to do first

1. **Safety and truthfulness first:** G01, G02, G03, G05, I01, I02, A01, A03, L01, L02, C01, C02, M01, M03, F01, Q01, S01, S02, S03. P0 means high-priority *validation and planning*; do not launch privileged or production actions merely because they are P0.
2. **First proof task:** [#2](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/2) / `I01`, with the existing anchored AgentWitness DoD, real tests, independent evidence and live target behaviour. `I02` must surface local-tool access limitations rather than pretend integration is live.
3. **Historical baseline:** `G02–G03`; full prior chats must be available and enumerated. No guessed 50–100-chat coverage.
4. **Pilot:** `G05` records 20 verified tasks with 5/10/15/20 milestones; review outcomes, not commits.
5. **External evaluation:** `R01–R05` turn first-pass research into controlled demonstrations. Existing [external review](../research/EXTERNAL_AI_AGENT_PERFORMANCE_FINDINGS_2026-10-29.md) is an initial scan, not a complete study.

## Project ownership / tracking epics

| Track | Scope | Functional owner | Action count | Issue |
|---|---|---|---:|---|
| G | Governance, baseline and PIP | chatGPTImprovement- | 7 | [Existing issue #1](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/1) |
| I | Cross-project adoption and integration | chatGPTImprovement- / existing components | 5 | [Existing issue #2](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/2) |
| A | AgentCheck / AgentWitness | Parris-Tech-Services/AgentCheck | 6 | [Issue #3](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/3) |
| L | LLMAccountability hardened evidence | Parris-Tech-Services/LLMAccountability | 6 | [Issue #4](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/4) |
| C | Independent review and supervisor (private components) | Existing private reviewer/coordinator and mission supervisor | 5 | [Issue #5](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/5) |
| M | JoshMemory continuity and evidence references | joshualparris/JoshMemory | 5 | [Issue #6](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/6) |
| F | ForgeGrid execution and fleet | Parris-Tech-Services/ForgeGrid | 4 | [Issue #7](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/7) |
| Q | Real-world QA, evals, tool-failure resilience | Cross-project test harness / target application repo | 6 | [Issue #8](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/8) |
| R | External deep research and controlled experiments | chatGPTImprovement- research / existing evaluation runners | 5 | [Issue #9](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/9) |
| S | Permissions, privacy and supply-chain trust | All components (security gate) | 3 | [Issue #10](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/10) |

## Exact tasks and acceptance conditions

### G — Governance, baseline and PIP

**Functional owner:** chatGPTImprovement- · Existing [#1](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/1)

- [x] **G01 · P0 · Freeze task-level Defi
  **Verified evidence:** [G01 record](evidence/G01_2026-10-29.json), [PR #11](https://github.com/Parris-Tech-Services/chatGPTImprovement-/pull/11), [main CI run](https://github.com/Parris-Tech-Services/chatGPTImprovement-/actions/runs/40836061002). Independent Greptile review produced 3 valid findings, all fixed before merge; Codex quota-blocked and did not review.nition of Done and status rules.** Action: Document and review canonical VERIFIED COMPLETE/PARTIALLY COMPLETE/BLOCKED/NOT STARTED definitions; log evidence, user permissions and exact acceptance criteria for first pilot task. **Done only when:** A test task with no live acceptance cannot be marked VERIFIED COMPLETE; status and evidence template agree. **Depends on:** —.
- [ ] **G02 · P0 · Audit 50–100 full prior chats with defensible sampling.** Action: Acquire authorised complete transcripts, enumerate chat identifiers/date span, avoid cherry-picking, classify tasks and missing records; keep raw evidence private. **Done only when:** Auditor records exact reviewed counts, time window, sample method, completeness and source pointers; no unsupported 'all chats reviewed' statements. **Depends on:** G01.
- [ ] **G03 · P0 · Create independently checked task-level baseline.** Action: For eligible sampled tasks, compare completion claims with Git/CI/deploy and user evidence; record exclusions, unknowns and denominator; obtain second-review sample. **Done only when:** Publish anonymised aggregate success, false-DONE, rework and corrective-follow-up counts with evidence quality; disputed cases adjudicated. **Depends on:** G02.
- [ ] **G04 · P1 · Create auditable KPI collection and anti-gaming rules.** Action: Implement a task ledger feeding the established KPI scorecard (verified outcome, evidence claims, permissions, rework, completion latency, cost); never infer missing data. **Done only when:** Machine-checkable aggregates reconcile to task IDs, show numerator/denominator and missingness; adversarial tests reject inflated successes. **Depends on:** G01,G03.
- [ ] **G05 · P0 · Run 20-task prospective PIP without moving goalposts.** Action: Maintain twenty distinct eligible substantive task records, frozen criteria and independent spot-check; report blocked and excluded tasks separately. **Done only when:** Review at tasks 5/10/15/20; measured outcomes and variance published; no '10/10 guarantee' claim. **Depends on:** G01,G04,I01.
- [ ] **G06 · P1 · Establish incident-to-regression evaluation loop.** Action: Turn verified failures (false source review, unfinished PR, wrong deploy, repeated user correction) into minimal reproducible fixtures and regression checks. **Done only when:** At least five incident-derived eval fixtures with known failing baseline and reproducible passing/negative checks, or exact blockers. **Depends on:** G03,Q02.
- [ ] **G07 · P1 · Review outcomes and recalibrate targets.** Action: After pilot independently audit findings, compare task complexity and variance, assign failure causes and update PIP without altering historical acceptance. **Done only when:** Document decision KEEP/CHANGE/ROLLBACK with numeric evidence and outstanding risks. **Depends on:** G05.

### I — Cross-project adoption and integration

**Functional owner:** chatGPTImprovement- / existing components · Existing [#2](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/2)

- [ ] **I01 · P0 · Prove one real witnessed task end to end.** Action: Select small authorised app issue; use existing AgentWitness frozen contract, source-state review, actual tests, reviewer where available, live acceptance and final claim gate. **Done only when:** Reproducible task trace shows source SHA, actual command receipts, independent verdict and actual user flow; or named missing integration blocks. **Depends on:** G01.
- [ ] **I02 · P0 · Check hosted ChatGPT-to-local verifier access honestly.** Action: Inventory available connector/MCP/CI/runner paths to aw, notary and reviewer; validate with harmless dry-run, not descriptions of theoretical hooks. **Done only when:** Published capability matrix per runtime: executable, authorised, observed evidence, missing adapter; impossible paths marked BLOCKED. **Depends on:** I01.
- [ ] **I03 · P1 · Define minimum typed handoff between existing tools.** Action: Specify DoD/receipt/notary/reviewer/live-acceptance/JoshMemory reference event schema including SHA, provenance, expiry, task ID, approval and status. **Done only when:** Schema examples validate; unsupported attestations never become VERIFIED and no secrets enter public events. **Depends on:** I02,A02,M03.
- [ ] **I04 · P1 · Enforce final-report gate on connected workflow.** Action: Add lifecycle adapter or external CI/MCP check for genuinely reachable agent run; avoid claiming universal ChatGPT interception. **Done only when:** Negative test with fake 'tests passed' is blocked; positive real proof passes; unreachable hosted channels disclosed. **Depends on:** I02,A01.
- [ ] **I05 · P1 · Publish an integration threat model and ownership boundary.** Action: Clarify broker-witnessed vs imported vs independently tested, trust roots, reviewer provenance, policy ownership, human merge and email approval. **Done only when:** Table of trust levels and bypass tests reviewed; no private source/credentials or unverifiable claims. **Depends on:** I03,S01.

### A — AgentCheck / AgentWitness

**Functional owner:** Parris-Tech-Services/AgentCheck

- [ ] **A01 · P0 · Add practical native final/Stop hook integration.** Action: Evaluate CLI hook integration for Claude Code, Codex and Antigravity; implement minimally supported adapters without inventing SDK hooks. **Done only when:** Supported runtime invokes real `aw final`; fail-closed missing/failed evidence and bypass documented; integration test proves call occurs. **Depends on:** I02.
- [ ] **A02 · P1 · Offer authenticated structured verifier interface (MCP or equivalent).** Action: Extend existing run/audit/task verify/final capabilities to tool-capable clients; restrict dangerous commands, avoid separate verifier engine. **Done only when:** Contract tests for valid/invalid tool calls, auth, approvals and returned provenance; unsupported hosted clients clearly marked. **Depends on:** I02,S01.
- [ ] **A03 · P0 · Harden unwitnessed-actions detection and provenance claims.** Action: Enumerate direct agent edits/commands escaping broker; make resulting verification provenance visibly weaker, test action imports cannot masquerade as BROKER_WITNESSED. **Done only when:** Malicious transcript, forged command and native edit tests never produce authoritative broker receipt; remaining blind spots listed. **Depends on:** I01.
- [ ] **A04 · P1 · Add deployed-application acceptance evidence adapters.** Action: Design plugin/receipt for current commit + real browser smoke/CLI scenario/target URL, distinct from pytest and Git SHA gates. **Done only when:** A broken UI fails despite passing tests; positive screenshot/interaction trace binds to exact release and environment. **Depends on:** Q01,I03.
- [ ] **A05 · P1 · Extend runtime evidence to non-Python suites safely.** Action: Implement precise Node/Vitest/Go/test-profile adapters with collected counts, scope/freshness and zero-test rejection; retain existing Python logic. **Done only when:** Fixture suites covering zero tests, narrowed scope, stale changes, changed lockfile, invalid JSON and failing test reject fake passes. **Depends on:** A03.
- [ ] **A06 · P2 · Assess external anchoring and telemetry without leaking evidence.** Action: Threat-model signing-key compromise and ledger rewrite; prototype privacy-safe optional transparency/OTel or cross-agent reliability observation. **Done only when:** Key-rotation/compromise simulation and redaction audit; opt-in external transmission only; no plaintext secrets in receipts. **Depends on:** S02,I05.

### L — LLMAccountability hardened evidence

**Functional owner:** Parris-Tech-Services/LLMAccountability

- [ ] **L01 · P0 · Verify real Windows notary/worker/runner deployment.** Action: Inspect service state, identities, endpoint reachability and key placement on approved test machine; execute safe signed test/push recipe. **Done only when:** Actual notary-signed result validated independently with live SHA and test metrics; unavailable privileges recorded as blocked. **Depends on:** I02.
- [ ] **L02 · P0 · Bind signed attestation to real report digest.** Action: Replace documented dummy subject digest with independently computed report content hash and correct notary-side validation. **Done only when:** Changing one report byte invalidates attestation; forged subject digest rejected; tests cover encoding and content changes. **Depends on:** L01.
- [ ] **L03 · P1 · Implement bounded no-secrets verification recipe.** Action: Upgrade recognised but unsupported no-secrets claim into independently executed scoped scan using existing scanners/evidence format. **Done only when:** Seeded secret fixtures fail without leaking values; unknown/unscannable paths stay INCONCLUSIVE; false-negative limitations documented. **Depends on:** L01,S02.
- [ ] **L04 · P1 · Evidence-based security-reviewed claim.** Action: Define exact verifiable coverage (SAST, dependency, policy, human review ID) rather than blanket 'security reviewed'; implement only measurable subclaims. **Done only when:** Unsupported/general security assertions remain INCONCLUSIVE; checks bound to commit and CI evidence. **Depends on:** L01,I03.
- [ ] **L05 · P1 · Composite fully-complete attestation policy.** Action: Require verified test, push, acceptance, permissions and actual runtime state; do not substitute recipe aggregate for semantic verification. **Done only when:** A missing browser outcome or policy check cannot produce fully-complete PASS; tests include partial evidence. **Depends on:** L02,Q01.
- [ ] **L06 · P1 · Hardening, isolation and platform-profile adversarial audit.** Action: Review OS identity separation, HMAC, signing key, runner limits, Python vs npm profiles and replay/nonce handling in real approved Windows sandbox. **Done only when:** Privileged/integration adversarial suite runs with redacted logs, reports actual isolation vs aspirational claims, follows no-secret/no-escalation policy. **Depends on:** L01,S02.

### C — Independent review and supervisor (private components)

**Functional owner:** Existing private reviewer/coordinator and mission supervisor

- [ ] **C01 · P0 · Inventory current supervisor/reviewer operational status.** Action: Locate existing authorised code and machine runtime, compare historical docs with actual installed CLIs, tickets, session tests and supported adapters. **Done only when:** Private evidence register identifies canonical source, active environment, recent checks, known broken paths and ownership; no private repo location published. **Depends on:** I02.
- [ ] **C02 · P0 · Isolate ground-truth tests from host credentials.** Action: Replace unsandboxed orchestrator test invocation with container/restricted runner appropriate to target OS, retaining reviewer worktrees. **Done only when:** Host-file/network escape negative cases denied; normal tests pass; security and portability tradeoffs documented. **Depends on:** C01,S01.
- [ ] **C03 · P1 · Bridge reviewer run evidence to AgentWitness without false provenance.** Action: Keep orchestrator-owned test result, import provenance honestly or route compatible checks through broker; do not audit an empty ledger. **Done only when:** Reviewer's own claims cannot pass ClaimGuard without trace; broker receipts and imported events clearly differentiated. **Depends on:** C01,A03,I03.
- [ ] **C04 · P1 · Make reviewer crash, test editing and disagreement fail closed.** Action: Extend existing tests for crashed reviewer, test-file edits, unresolved objections and fake reviewer consensus; no auto-merge. **Done only when:** Injected review crash or modified acceptance tests cannot produce full APPROVED; actual orchestrator test failure dominates. **Depends on:** C01,C02.
- [ ] **C05 · P2 · Experiment with single-agent baseline vs risk-triggered review.** Action: Run matched models/tasks/tools with no reviewer, one reviewer and escalated reviewer; measure independent acceptance and total cost. **Done only when:** Repeat-trial results show intervals, disagreement and marginal benefit; retain least costly verified configuration. **Depends on:** C04,R03.

### M — JoshMemory continuity and evidence references

**Functional owner:** joshualparris/JoshMemory

- [ ] **M01 · P0 · Prove two-machine authoritative resume.** Action: Run approved two-client session handoff, pause/resume and changed live HEAD detection; include missing/stale memory cases. **Done only when:** Second client resumes correct unsatisfied work with live Git winning; redacted source IDs and stale-detection traces retained privately. **Depends on:** I01.
- [ ] **M02 · P1 · Prove work lease collision, expiry and reclaim under concurrency.** Action: Exercise live GitHub append-only race semantics with two agents and expired lease, ensuring no false distributed-lock guarantee. **Done only when:** Two contenders get accurate collision warnings; stale lease reclaims; no duplicate task success or lost ownership claimed. **Depends on:** M01.
- [ ] **M03 · P0 · Persist accountability proof references across handoffs.** Action: Carry task ID, exact SHA, verification-system evidence ID, signature/provenance grade, verdict, age, human approval and final acceptance. **Done only when:** A resumed agent cannot promote UNTRUSTED transcript or stale receipt to VERIFIED; original evidence link reconstructs. **Depends on:** I03,M01.
- [ ] **M04 · P1 · Measure historical chat-search completeness and confidence.** Action: Test distinct requested conversation queries against actual ChatGPT exports (when authorised), record total documents retrieved and coverage limits. **Done only when:** Audits never infer complete review from snippets; query report includes exact hits, unavailable data, date range, and duplicates. **Depends on:** G02.
- [ ] **M05 · P1 · Protect private records while feeding public programme metrics.** Action: Publish only aggregate/anonymised task outcomes and references approved for public release; verify redaction of chats, paths, keys and user identifiers. **Done only when:** Secret/PII canaries cannot appear in public exports, PRs, metrics or repo; explicit reviewer test. **Depends on:** S03,M03.

### F — ForgeGrid execution and fleet

**Functional owner:** Parris-Tech-Services/ForgeGrid

- [ ] **F01 · P0 · Reconcile existing open ForgeGrid PRs/issues before changes.** Action: Inspect active issue #1 and existing PRs for duplicate work, CI, merge conflicts and archived docs; select relevant base without rewriting. **Done only when:** Decision table for each relevant branch: keep/rebase/merge/close; verified run of affected tests; no unreviewed merge. **Depends on:** —.
- [ ] **F02 · P1 · Ensure worker completion acknowledgements and idempotent retry.** Action: Audit coordinator/worker job result delivery, ACK/retry and deduplication, including partial response, disconnect and restart. **Done only when:** Fault injection yields one authoritative completion per job, no duplicate side effects and correct failure/pending state. **Depends on:** F01,S01.
- [ ] **F03 · P1 · Verify distributed job cancellation, loss and evidence binding.** Action: Exercise documented ForgeGrid acceptance tests for cancel/retry, offline worker, resource limits, TLS pairing and artifact digests. **Done only when:** Run actual Go and LAN/sandbox integration tests; job evidence binds to correct source commit; record unreachable equipment. **Depends on:** F01.
- [ ] **F04 · P2 · Establish safe remote verifier/acceptance runner integration.** Action: Assess existing AgentBridge/ForgeGrid worker interface to execute approved tests and return signed/verifiable results without host-wide control. **Done only when:** One approved remote task returns artifacts, exact SHA, exit + test metrics, timeout and redacted trace, or a documented integration blocker. **Depends on:** F02,I03,L01.

### Q — Real-world QA, evals, tool-failure resilience

**Functional owner:** Cross-project test harness / target application repo

- [ ] **Q01 · P0 · Define application-specific live acceptance receipts.** Action: For web/mobile/game tasks prove realistic primary interaction, loading, safe areas, persistence and relevant failure/regression cases—not HTTP 200. **Done only when:** Seeded broken feature fails acceptance even with green CI; release SHA/URL and browser/test observation persisted. **Depends on:** I01.
- [ ] **Q02 · P1 · Create representative task and adversarial evaluation suite.** Action: Convert existing incidents into safe fixtures: false chat review, fake CI success, stale SHA, wrong branch, broken UI, reviewer crash and zero-test green. **Done only when:** Independent grader detects fabricated completions and reports FPR/FNR, unknowns and evaluator disagreements. **Depends on:** G03,A03,Q01.
- [ ] **Q03 · P1 · Run realistic fault-injection suite for agent tool calls.** Action: Adapt ideas from RetryRealistic: timeout, truncated results, 401, 403, partial write, malformed JSON, stale output, nonzero exit. **Done only when:** Measured correct recovery, honest failure, fabrication and tool calls across repeated seeded tests; no real customer mutations. **Depends on:** Q02,S01.
- [ ] **Q04 · P1 · Implement read-after-write/idempotency at consequential tool boundaries.** Action: For permitted state-changing actions design request IDs, retry classifier and post-write check to avoid duplicate merges/deploys/external actions. **Done only when:** Simulated lost ACK does not duplicate effects; permanent errors are not blindly retried; user approval remains mandatory. **Depends on:** Q03,S01.
- [ ] **Q05 · P1 · Measure actual user effort and real UX satisfaction.** Action: Record reopen/corrective follow-up, tested scenarios and user-confirmed acceptance separately from CI and PR counts. **Done only when:** Pilot report shows corrective user turns per task, bugs after deploy and verified product behaviour; normal scope change excluded from rework. **Depends on:** G04,Q01.

- [ ] **Q06 · P1 · Reuse existing code-quality gates and test-adequacy signals.** Action: Audit existing private code-quality tooling before proposing a new scanner; integrate available complexity, per-function coverage, mutation, lint and security findings into the task evidence model without equating a good score to functioning UX. **Done only when:** At least one approved sample repository reports actual coverage and mutation/complexity results, generated code exclusions and no fabricated green on missing data; independently verify relevant user flow. **Depends on:** Q01,G04.

### R — External deep research and controlled experiments

**Functional owner:** chatGPTImprovement- research / existing evaluation runners

- [ ] **R01 · P1 · Complete independent 30–50-source research synthesis.** Action: Expand initial 15 intervention findings with fresh primary papers, dates, counter-evidence, license/security and five additional inspected repos. **Done only when:** Sources, evidence grades, model/task/control descriptions and what was known before Sep 2026 documented; no invented tests. **Depends on:** —.
- [ ] **R02 · P1 · Independently reproduce at least one external countermeasure.** Action: In safe sandbox reproduce RetryRealistic monitor or analogous fault-injection result with pinned code and model/tool costs. **Done only when:** Release scripts, seeds, actual counts, limitations and delta vs own baseline; if access unavailable, report specific blocker. **Depends on:** R01,Q03.
- [ ] **R03 · P1 · A/B test skill and reviewer strategies instead of bulk adding prompts.** Action: Same model/tasks/time budgets: no skill vs narrow skills; single vs independent review; document failures and token/latency impact. **Done only when:** Repeated-task outcome, confidence intervals, rework and total cost presented; remove regressive variants. **Depends on:** G04,Q02.
- [ ] **R04 · P1 · Audit grader validity and infrastructure variance.** Action: Audit test oracle, CPU/RAM/time budgets, flaky tests, reproducibility, model seeds, benchmark leakage and lucky-pass trajectories. **Done only when:** Report infrastructure failure separately; independently spot-check 'successes'; no credit for contaminated or broken graders. **Depends on:** Q02.
- [ ] **R05 · P2 · Prioritise external opportunities by measured expected value.** Action: Rank latest findings by impact/confidence/effort/risk against real stack and avoid redundant architecture proposals. **Done only when:** Top five include owning existing component, exact plausible edit seam, acceptance experiment and rollback; reject unproven duplicate apps. **Depends on:** R01,R02,R03.

### S — Permissions, privacy and supply-chain trust

**Functional owner:** All components (security gate)

- [ ] **S01 · P0 · Codify approval gate for every consequential action.** Action: Explicit task-specific authority for email/send/forward/reply, paid API/spend, merge, deploy, system config or secret access; never treat broad goals as mail authorisation. **Done only when:** Synthetic negative tests prove no action occurs without scoped approval, including automatic retries/escalation. **Depends on:** —.
- [ ] **S02 · P0 · Audit signing keys, attestations and unsafe test execution.** Action: Check generated keys, receipt history, public exposure, non-root runners, digest binding, injection, trust anchors and secret redaction. **Done only when:** Security review with evidence, key leak canary tests and remediation plan; no production key disclosure in report. **Depends on:** S01.
- [ ] **S03 · P0 · Keep private-repo/chat evidence out of public improvement project.** Action: Restrict improvement repo to public-safe architecture, anonymised work IDs and aggregate metrics; keep raw chat logs and private evidence in authorised store. **Done only when:** Diff and secret/PII scan on every new public doc/issue; no private repo URLs, machine identity or conversation excerpts leak. **Depends on:** S01.

## Definition of Done and sequencing

- Do **not** mark any backlog task COMPLETE from a README, green historical CI badge, pull request, signed transcript import or stated intention alone. Record live evidence and exact SHA/test/deployment/behaviour where applicable.
- Consult existing source and open PRs before writing code. Do not rebuild AgentWitness, LLMAccountability, JoshMemory, reviewer or ForgeGrid capabilities already implemented.
- Keep source/project status **SOURCE/DOC-CONFIRMED**, **HISTORICALLY REPORTED**, **LIVE VERIFIED**, **PARTIAL** and **BLOCKED** separate. Inaccessible machines/hosted clients are legitimate blocks.
- Safety gates are absolute: no emails as the user without explicit send-specific authorisation, no unapproved merges/spending/deployments or privilege elevation, no secrets/private chats in public source.
- Dependencies indicate prerequisite evidence or decisions, not automatic authority to run other actions.
- Commit evidence records only in authorised locations; the public improvement repo should use aggregate task status/approved links.

## Pre-existing trackers to avoid duplicating

- [#1 — twenty-task PIP](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/1) (`G05` and governance track).
- [#2 — existing-stack integration proof](https://github.com/Parris-Tech-Services/chatGPTImprovement-/issues/2) (`I01` and integration track).
- [ForgeGrid issue #1](https://github.com/Parris-Tech-Services/ForgeGrid/issues/1) and [existing ForgeGrid PRs](https://github.com/Parris-Tech-Services/ForgeGrid/pulls) (read before `F01`).
- [JoshMemory issue #26](https://github.com/joshualparris/JoshMemory/issues/26) is about Repository Town branch/playtesting and **not** a replacement for JoshMemory continuity tasks.

## Audit coverage and non-claims

Reviewed current improvement repo issues, relevant public source/docs/test paths, private coordinator design at a high level, open ForgeGrid PR/issue inventory, and prior research documents. **No code change or test execution in other repositories** was performed by constructing this backlog. Previously written research documents remain evidence-limited as labelled. This is a **consolidation of identified outstanding work**, not a guarantee that no undiscovered work remains.
