# Deep Research Brief — Evidence-Based Peak Performance for AI Agents

**Prepared:** 29 October 2026 (Australia/Sydney)
**Research type:** Independent, comparative, evidence-driven architecture and performance review.
**Mission:** Find what successful teams, researchers and open-source communities have *actually demonstrated* improves AI coding agents and multi-step assistants, then determine what our existing software can reuse to reduce failures. This is a research brief, not permission to install tools, spend money, deploy, expose private information, or send communications.

## Role and objective

You are a senior AI systems researcher, principal software engineer, security reviewer and independent evaluator. Act as a sceptical outside investigator, not a promoter of our existing projects or any vendor.

**Central question:** What changes to orchestration, verification, evaluation, tool use, context management and operating discipline produce the largest **measured** improvement in independently verified user outcomes for AI agents working on substantial engineering tasks?

Do not assume that adding more agents, more prompts, more governance documents, more memory or a new model improves results. Distinguish good ideas from code that exists, tests that passed and operational systems actually proven.

A perfect 10/10 every time is not a defensible expectation. Seek the best sustainable reliability frontier and accurate reporting: success as measured by the user, low regression/rework, minimal corrective follow-ups, controlled cost/latency and zero unapproved consequential actions.

## Ground truth: our existing ecosystem (inspect before proposing anything new)

1. [AgentCheck / AgentWitness](https://github.com/Parris-Tech-Services/AgentCheck): witness broker, signed evidence, ClaimGuard, anchored Definition-of-Done contracts, freshness/scope protection, `aw final`, hardened verifier backend.
2. [LLMAccountability](https://github.com/Parris-Tech-Services/LLMAccountability): isolated Windows notary/worker/runner, supported independently executed test/push verification recipes, fail-closed policy, signed attestations. Do not treat unimplemented recipes or dummy report-digest bindings as complete.
3. [JoshMemory](https://github.com/joshualparris/JoshMemory): indexed history, provenance, durable handoffs, trust overlays, project leases and journal; memory is not authoritative proof of current code state.
4. [ForgeGrid](https://github.com/Parris-Tech-Services/ForgeGrid): distributed job execution/coordinator/worker capabilities, not an independent semantic verifier.
5. Existing private multi-agent review/coordinator and mission-supervision work: inspect only if access is explicitly available; never publish private repository addresses, source, secrets or records.
6. [Current improvement repository](https://github.com/Parris-Tech-Services/chatGPTImprovement-), especially:
   - docs/PERFORMANCE_REVIEW_2026-10-29.md
   - docs/PIP_001_SENIOR_EXECUTION.md
   - docs/KPI_SCORECARD.md
   - docs/EXISTING_ACCOUNTABILITY_STACK_AUDIT_2026-10-29.md
   - docs/PREVIOUS_CHAT_HISTORY_ACCOUNTABILITY_2026-10-29.md
   - templates/TASK_EVIDENCE.md
7. Existing prior-art documents:
   - AgentCheck: docs/PRIOR_ART.md
   - LLMAccountability: docs/OPEN_SOURCE_FEATURE_HARVEST.md
   - JoshMemory: docs/OPEN_SOURCE_MEMORY_BORROWING_PLAN.md
   - JoshMemory: docs/CODING_2026_MASTER_HANDOFF.md

Prior dives in August–September 2026 already investigated agent-verify, backcheck, truth, agent-execution-harness, proof-agent, Hermes Agent, Sigstore/in-toto/SLSA, OPA concepts, memory/lease systems and multi-agent orchestration. **Do not simply rediscover them or rebuild existing capabilities**. Recheck upstream development, measure adoption and identify what has changed since those dives.

These links are starting evidence only; source code, live state and demonstrable results outrank README claims or old conversation summaries. The provisional 1.75/5 performance review is a subjective managerial rubric, **not** measured task success. A 50–100-chat complete-transcript retrospective has **not** been established. Do not invent its results.

## Failure modes the research must address

Construct a testable failure taxonomy and root-cause hypotheses for ALL of:

1. Promising full completion but stopping at a plan, PR, unmerged branch, green CI, successful deployment start or partial implementation.
2. Claiming to have reviewed chats, files, source, tests, applications or deployments without actually accessing or examining them.
3. Self-grading or verification theatre: claiming AgentWitness/LLMAccountability was used when it was merely mentioned; forged, stale, scoped, imported or self-reported evidence promoted to authoritative proof.
4. Feature implemented but user-facing behaviour broken: browser UI, mobile, game interactions, persistence, authentication, hardware integrations or regressions not actually tested.
5. Context loss across long tasks/chats, duplicate work, wrong repository/branch/commit/environment, forgotten acceptance criteria or unfinished checkpoints.
6. Failing to independently diagnose a blocker, retry bounded alternatives, continue work and accurately preserve unresolved tasks.
7. Excessive corrective user follow-ups, repetitive clarification, verbose progress messages replacing delivery and high customer effort.
8. Security and permission failures: secrets exposed in logs, risky local execution, unsafe verifier keys, prompt injection, excessive permissions, unauthorised emails, merges, deployments or spending.
9. Reviewer consensus hiding inadequate tests, test contamination, benchmark gaming, test changes that weaken acceptance, missing human review for risky decisions.
10. Optimising model IQ, pass rates, commits or dashboards rather than independently verified end-to-end outcomes; high cost, latency and flaky result variance.
11. Local CLI vs cloud-hosted agent mismatch: inaccessible binaries, unavailable privileged Windows services, incomplete hooks/MCP adapters and missing observability, causing enforcement to be optional.
12. Blind faith in past work and inaccurate memories or stale documentation. Always re-check current evidence.

For each failure: identify detection, prevention, containment, recovery, observable evidence, which **existing** component owns it, and what is missing.

## External research: investigate what genuinely works

Search research papers, independent replications, incident/postmortem reports, strong open-source repos and code, engineering blogs by teams running agents in production, public benchmarks and community experiences.

Include, but do not limit research to:

- Evaluation-driven development, production trace grading, human calibration, task-specific eval suites, automatic regression replay and continuous improvement flywheels.
- Agent harness comparisons with a controlled model: tool design, context curation, risk-based routing, test-and-repair loops, prompts/skills, structured handoffs, and stop criteria.
- Existing independent verification, action receipts, trusted execution, taint/provenance classifications, sandboxed test runners, policy engines, signed attestations, anti-reward-hacking and real-world acceptance testing.
- Planning/decomposition vs just-in-time plans; persistence across sessions; checkpointing, memory retrieval metrics, source-of-truth hierarchy, multi-agent work ownership, lease expiry and crash recovery.
- Single-agent versus multi-agent, independent adversarial reviewers, reviewer agreement, escalation only when warranted, bounded retries, token/latency budgets and diminishing returns.
- Browser/computer-use agents, end-to-end release QA, screenshots/render checks, instrumented web/mobile/game interactions, API/CI/deployment evidence correlated to exact source SHA.
- Safe and practical human approval gates: consequential actions, secrets, access controls, prompt injection and least privilege.
- Cost-effective use of subscriptions and local inference where appropriate, without new paid API charges by default.
- Reliability engineering: operational playbooks, SLOs/error budgets, incident analysis, recovery, graceful degradation and hard stop on unsupported success claims.
- Evaluation validity: contamination, infrastructure variation, benchmark leakage, brittle tests, grader bias, single-run stochasticity and reporting uncertainty.

**Leads to examine and independently verify (do not assume endorsement):**
- OpenAI: agent evals, traces, graders, and the May 2026 agents/Codex improvement-loop cookbook.
- Anthropic: Demystifying evals for AI agents; infrastructure noise in agentic coding evaluations; Claude Code operational lessons.
- GitHub: Copilot agent harness controlled comparisons across models/tasks.
- Open-source: OpenHands, SWE-agent, Aider, Roo Code, Cline, Codex CLI, Claude Code, AgentWitness's recorded prior art, existing agent-memory/coordination systems, Promptfoo, Inspect AI, LangSmith, Braintrust, and observability suites. Verify project activity, license, quality, security and applicability before recommending.
- Research benchmarks: SWE-bench Verified/Pro and improved anti-hacking variants, Terminal-Bench, OSWorld, WebArena, GAIA/BrowseComp, SkillsBench, tau-bench, METR task horizon, and independent task/trace evaluation methods. Confirm current versions, reliability/contamination caveats and precise dates.
- Recent research on independent environment-state plus trace verification and adversarial/fault-injection evaluators; assess paper methods and reproduction rather than trusting abstract metrics.

## Contemporary source leads (verify carefully; not endorsements)

- [OpenAI: Build an Agent Improvement Loop with Traces, Evals, and Codex (12 May 2026)](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop) — explicit harness/trace/feedback/evaluation improvement cycle.
- [OpenAI: Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals) — trace grading and datasets/eval runs.
- [Anthropic: Demystifying evals for AI agents (January 2026)](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) — eval development and human feedback.
- [Anthropic: Quantifying infrastructure noise in agentic coding evals (February 2026)](https://www.anthropic.com/research/infrastructure-noise) — environment confounders.
- [GitHub: Comparing the Copilot agentic harness across models/tasks (2026)](https://github.blog/ai-and-ml/github-copilot/evaluating-performance-and-efficiency-of-the-github-copilot-agentic-harness-across-models-and-tasks/) — matched model/task harness comparison, repeated runs and cost/task.
- [SWE-Bench Pro Verified (September 2026, preprint)](https://arxiv.org/abs/2609.08149) — benchmark contamination, reward hacking, task validity.
- [Evidence-First Agentic Verification (October 2026, preprint)](https://arxiv.org/abs/2610.17724) — trace + state verification and fault-injection evaluation; independently reproduce claims.
- [Artificial Analysis Coding Agent Index](https://artificialanalysis.ai/agents/coding-agents) — model/harness/time/cost benchmarks; check live methodology.

These are **starting leads**, not a substitute for finding fresher independent results or checking publication dates, conflicts, data quality and replication.

## Source and evidence quality requirements

1. Search to the **actual research date**; record source publication/update dates.
2. Aim for **30–50 high-relevance sources**, including **at least 15 primary sources** and **10 genuine open-source implementations** where available. Never pad the list with low-quality entries to meet quotas.
3. Inspect actual source code, tests, changelogs, issues and activity for at least five high-value open-source candidates where accessible. Differentiate documented features from independently demonstrated features.
4. For a claimed improvement, capture: baseline, intervention, model/harness, task set, N/repetitions, metric, point estimate, uncertainty, setup, cost, latency, known confounders and replication status.
5. Treat sales claims, synthetic demos, cherry-picked anecdotes, Reddit discussions and unreviewed preprints as leads rather than conclusive results. Include negative and null findings.
6. Prefer matched-model/matched-task A/B studies; account for model and infrastructure changes, test leakage and run-to-run variance.
7. Cite original URLs for material claims. Explicitly identify sources already considered in August–September 2026 and state **what is genuinely new since then**.
8. Do not assert a universal 100% success rate or that an engineering framework guarantees any particular KPI.

## Deliverables (required)

### A. Executive assessment
- Direct answer: **What are the three biggest changes likely to improve our actual success rate?**
- State what already works in our stack, what is only documented, what was historically reported and what is not independently verified.
- Distinguish model limitations from harness/process/tool-access limitations.

### B. Previous-research reconciliation
- Dated inventory of prior deep dives and their primary sources.
- For each explored idea: ALREADY IMPLEMENTED / PARTIALLY INTEGRATED / PLANNED / SUPERSEDED / NOT VERIFIED, with source and confidence.
- An explicit **DO NOT REBUILD** list and outstanding evidence needed.

### C. Comparative landscape
- 15–25 top candidate methods/products/projects ranked for measurable end-to-end reliability benefit, maturity, compatibility, security, maintenance, integration effort, latency and ongoing cost.
- Detailed comparison of the top five. Explain why attractive alternatives should **not** be adopted when evidence is weaker or an existing component suffices.
- Separate product marketing from measured results; note ecosystem freshness.

### D. Failure-mode / countermeasure matrix
For every failure above: root cause, current protection, gap, proven external technique, owner, specific change, cost/risk, verification test and whether it requires permissions/access not currently available.

### E. Target architecture
- One minimal, modular improvement design reusing AgentWitness, LLMAccountability, JoshMemory, supervisor, independent reviewer and ForgeGrid only for their appropriate roles.
- Precise flow from user request → frozen acceptance criteria → existing context/live state → authorised implementation → witnessed tests → independent review → deployment → real UX acceptance → final claim gate → durable evidence/handoff.
- Trust/provenance levels and an honest fallback when hosted ChatGPT cannot reach local CLI services.
- A diagram plus interface/event schema (not a speculative total rewrite).

### F. Measurable evaluation plan
- How to obtain an authorised, representative **50–100-full-chat historical baseline** without pretending snippets are full transcripts.
- Task taxonomy, complexity strata, sampling, exclusions, success/failure criteria, independent second reviewer and evidence provenance.
- An initial 20-substantial-task pilot with a paired before/after or controlled comparison where feasible, repeated trials for stochastic workflows, confidence intervals and a fixed regression suite.
- Metrics with NUMERATOR, DENOMINATOR, window, missingness and gaming countermeasures: verified completion, unsupported claim rate, instruction adherence, unauthorised actions, assistant-caused rework, corrective follow-up burden, test/deploy quality, lead time, cost/latency, and DORA metrics per application.
- Human assessment: what a real user actually wanted, not just what CI certified.
- Negative controls/adversarial cases: fabricated test results, narrowed tests, 0 collected tests, stale SHA, wrong checkout, falsified transcript, edited acceptance criteria, reviewer crash, permission bypass, fake deployment success and broken live UI.

### G. Prioritised implementation roadmap
Deliver an **impact × confidence × effort × risk** ranked backlog:
- QUICK WINS: small changes that can be proven on the next real task.
- 30-DAY ENGINEERING IMPROVEMENTS: integrations, tests, automatic gates and dashboards justified by evidence.
- LONGER-TERM RESEARCH: only genuinely novel, unproven opportunities worth pilot testing.
For the top five, provide exact repository/component, files/interfaces likely involved (verified against code, not guessed), non-goals, acceptance tests, rollback, cost and dependency on user permission.

### H. Adversarial management review
Challenge your own top recommendation. Give the strongest argument it may fail, what evidence would falsify it, what would be required to switch to another approach, and how to prevent a new accountability system from merely generating more reports.

### I. Actionable output
Conclude with:
1. **Top three changes to do first**, each with an independently verifiable test.
2. **Top ten experiments**, ordered by expected value.
3. **What we should stop doing immediately.**
4. **What we should not build because it already exists.**
5. **Questions genuinely blocked on permissions or missing evidence** — don't ask for details available in prior context.
6. A reusable task-level scorecard and a clear distinction between VERIFIED COMPLETE, PARTIALLY COMPLETE, BLOCKED and NOT STARTED.

## Research-only security and execution rules

- Do **not** send emails, notifications, or messages as the user; do not publish raw conversation history or private repo content.
- Do not spend money, purchase products, modify production, install privileged software, merge or deploy without separate task-specific authority.
- Do not reveal secrets, exact private repo locations, credentials, personal data or confidential source in a public report.
- Do not invent sources, tests, measured improvements, or successful tool use. If a source or artifact is inaccessible, mark it inaccessible and continue with clearly qualified findings.
- A research recommendation is **not** a verified implementation. No new process document modifies ChatGPT's underlying model or its hosted tool permissions.
- Prioritise improvements to **actual user outcomes**, not verbosity, number of agents, audit activity or metrics that can be gamed.

**Final standard:** I should be able to hand the resulting research to an engineering agent and know **what already exists, what to reuse, what to build, why it should work, what could go wrong, how to test it and how success will be measured**.