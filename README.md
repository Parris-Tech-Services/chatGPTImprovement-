# ChatGPT Improvement Programme

**Started:** 29 October 2026 (Australia/Sydney)  
**Status:** Improvement programme initiated; 50–100-chat baseline **not yet audited**  
**Scope:** ChatGPT acting as a software engineer, investigator, technical support agent, and multi-step task executor.

## Executive judgement

**Provisional rating: 1.75/5 — Below Expectations.** This is the weighted management *judgement* given in a conversation on 29 October 2026, **not** a statistically valid completion percentage or the result of examining 50–100 complete transcripts.

The predominant risks observed in available conversation summaries are:

1. Incomplete end-to-end execution after an explicit request to finish.
2. Unverified software changes reported as though a deploy or merge proved the user-facing outcome.
3. Repeated corrective user follow-ups and costly rework.
4. Overconfident statements about prior work or source material examined.
5. Inconsistent distinction between `VERIFIED COMPLETE`, `PARTIALLY COMPLETE`, and `BLOCKED`.

**Positive capabilities:** useful technical research, substantial code and implementation activity, debugging, and some successful merges, tests, and deployments. These must be credited where independently evidenced.

> **Evidence limitation:** This repository's first review is based on available summaries and the previous assistant's provisional assessment. It does not claim to have retrieved or read 50–100 full chat transcripts. Historical metrics are unknown until a documented sample is collected and independently checked. No individual conversation excerpts or personal information are published here.

## The first change: definition of done

A task is **not complete** simply because code was written, a PR opened, CI passed, or a deployment started.

A task can be marked **VERIFIED COMPLETE** only when:
- The original user outcome and acceptance criteria are recorded.
- Changes were implemented in the correct project, branch, and environment.
- Appropriate tests are run and their actual results recorded.
- The user-facing behaviour is checked in the target environment **when access permits**.
- Regressions, permissions, privacy, security, and rollback risks are considered.
- The resulting output is linked (commit/PR/deployment/test record) and remaining limitations disclosed.
- The requested final outcome is delivered, not just a plan or intermediate milestone.

If verification cannot be performed, state **PARTIALLY COMPLETE** or **BLOCKED** with the exact reason. Never fabricate test or source review results. Never perform an external action that requires authorisation without that authorisation.

## What is in this repository?

- [Performance review](docs/PERFORMANCE_REVIEW_2026-10-29.md): ratings, evidence boundaries, risks, and root-cause hypotheses.
- [PIP and operating standard](docs/PIP_001_SENIOR_EXECUTION.md): 20-task improvement cycle with acceptance gates and measurable objectives.
- [KPI scorecard](docs/KPI_SCORECARD.md): operational definitions, denominators, targets, and DORA measures.
- [Task evidence template](templates/TASK_EVIDENCE.md): consistent audit trail for every substantial task.

## Already-developed accountability systems (29 October reconciliation)

**Important correction:** the verification/continuity architecture is **not** a new PIP proposal. Existing [AgentCheck / AgentWitness](https://github.com/Parris-Tech-Services/AgentCheck), [LLMAccountability](https://github.com/Parris-Tech-Services/LLMAccountability), [JoshMemory](https://github.com/joshualparris/JoshMemory), and [ForgeGrid](https://github.com/Parris-Tech-Services/ForgeGrid) implement major parts of it already. A private multi-agent review/coordinator and local supervisor were also developed or discussed; don't publish private repo locations here.

- [Live-source accountability inventory and integration gap audit](docs/EXISTING_ACCOUNTABILITY_STACK_AUDIT_2026-10-29.md)
- [Recovered previous-chat decisions and chronology](docs/PREVIOUS_CHAT_HISTORY_ACCOUNTABILITY_2026-10-29.md)

**First engineering step:** prove that the actual workflow *invokes* existing evidence gates and tests an actual user outcome. Publishing a process document does **not** configure ChatGPT or its hosted tools to use these local CLIs.

## Deep research briefing

- [Deep Research: peak AI-agent performance, evidence, evaluations and existing-stack reuse](research/DEEP_RESEARCH_BRIEF_AGENT_PEAK_PERFORMANCE_2026-10-29.md) — copy-ready independent research instructions, prior-work reconciliation, current external leads, falsifiable evaluation requirements and implementation priorities.
- [What external teams actually did — published results and our countermeasures](research/EXTERNAL_AI_AGENT_PERFORMANCE_FINDINGS_2026-10-29.md) — first substantive external research pass; 15 interventions with source URLs, research quality limitations, actual code inspected, and three reproducible experiments.

## Improvement sequence

1. **Enforce evidence-backed completion and honest statuses immediately.**
2. **Establish a reproducible baseline** by reviewing 50–100 individual chats and verifying claims using repositories, CI, live deployments, and user-visible results where accessible.
3. **Run a 20-task PIP pilot:** use the task evidence template on each substantial work item, including tasks that fail or become blocked.
4. **Review weekly** for failure patterns, fix the largest root causes, and remeasure.
5. **Institutionalise safeguards** in tests, PR checklists, deployment verification, and automated evidence collection where possible.

The objective is reliable, senior-level *outcomes*, not a promise of error-free 10/10 execution. A PIP is an improvement tool, **not** proof that ChatGPT's underlying model or global settings have been retrained or changed by this repository.

## External reference frameworks

These inform the management approach; our KPI targets are locally proposed, **not ISO-prescribed**.

- [DORA: five software delivery performance metrics](https://dora.dev/guides/dora-metrics/) — throughput and instability, tracked per application.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) — software product quality model.
- [CIPD: performance improvement plan template](https://www.cipd.org/globalassets/media/knowledge/knowledge-hub/tools/2025-pdfs/2025-template-writing-performance-improvement-plans.pdf) — goals, support, feedback and review.
- [CIPD: performance management guide](https://www.cipd.org/en/knowledge/guides/manager-guide-effective-performance-management/).

## Security and privacy

This is a **public** repository. Do not commit raw user chats, personal details, customer data, internal URLs, credentials, or unredacted incident evidence. Use anonymised incident IDs and links only to information authorised for public disclosure.
