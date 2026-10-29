# What Other Teams Actually Did to Improve AI Agents — External Evidence Review

**Research date:** 29 October 2026 (Australia/Sydney)  
**Purpose:** Address the explicit request to investigate other teams' **real interventions and measured results**, not merely write a prompt about how to research them.  
**Status:** **First substantive external research pass complete**; not a systematic 30–50-source comprehensive review, not a reproduction of external experiments, and not proof that proposed changes improve *our* agent yet.

## Executive findings

The highest-value lessons for our own unfinished work are to:
1. **Make end-to-end outcome tests and persistent acceptance criteria mandatory.** Anthropic publicly described a long-running coding harness using a structured feature list, one-feature-at-a-time progress, git checkpoints and browser acceptance. They identified premature "done", interrupted sessions and unit-tested-but-broken apps as repeat failures.
2. **Use independent state and execution monitoring, not just better instructions.** Researchers injected realistic tool faults and showed that verification-first monitoring reduced confident fabrication. Microsoft researchers identified "lucky passes" in nominally successful software-agent traces.
3. **Build a feedback-to-evaluation improvement loop and test changes against it.** OpenAI, Anthropic and industry practitioners report building reusable evals from production traces and human feedback. Use independent user-facing acceptance alongside code-level tests.
4. **Prefer carefully tested harness improvements over simply buying larger models or adding agents.** GitHub's same-model harness comparisons found on-par success with lower token use in many configurations; a controlled multi-agent study found more agents often failed to help. Skills studies conflict by task category, so measure narrow skills rather than assuming universal benefit.
5. **Avoid false precision and benchmark gaming.** OpenAI's 2026 audit estimated ~30% of SWE-bench Pro tasks have broken evaluation conditions; Anthropic measured a 6 percentage point evaluation swing from resource configuration alone.

### Source grading

- **Published controlled empirical result:** reported numerical comparison with method and tasks; not independently reproduced by this audit.
- **Engineering case study:** credible primary-source project experience; generally lacks matched controls.
- **Research preprint/workshop:** potentially useful but needs replication and peer scrutiny.
- **Repository implementation:** source/docs exist and can be inspected; not confirmation that the software passed a fresh live run.
- **Local recommendation:** our mapping from external findings to existing projects; not an observed improvement.

## External teams: interventions and reported results

| # | Team / external source | Intervention they actually tried | Published result or evidence | Quality/caution | Reuse here |
|---|---|---|---|---|---|
| 1 | Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | Initialiser creates comprehensive JSON feature list with everything failing; coder makes one feature at a time, records git commits/progress, runs app and browser E2E before marking pass | Reported qualitative improvement in continuity and detecting broken UI; no rigorous uplift percentage published | Engineering experience; no matched intervention group | **JoshMemory + AgentWitness** must require persistent feature states and live acceptance before DONE |
| 2 | Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | Claude Code, Descript, Bolt and others built repeatable evals with human-calibrated graders, static checks and browser-agent runs | Bolt reportedly built a combined static/browser/LLM eval system in **3 months**. Descript kept separate quality and regression suites; no causal percentage attributed | First-party descriptive examples | Convert real task failures into reproducible test cases; keep human judgement and outcome tests |
| 3 | OpenAI, [Build an Agent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop) (12 May 2026) | Capture traces, human and model feedback, turn them into Promptfoo evals, rank harness changes, hand off to Codex | Reproducible **tutorial/demo** with five synthetic traces; **not** measured production uplift | Detailed recipe; synthetic example | Implement a small failure→eval→retest process, **not** another AI accountability application |
| 4 | OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/) (11 Feb 2026) | Agents wrote application and engineering infrastructure while humans designed environment, constraints, tests and feedback loops | Team *estimated* developing internal beta roughly **10× faster** than hand-writing it; real alpha/daily users | Uncontrolled self-estimate, not generalisable causal factor | Improve environment and test harness, not merely model instruction |
| 5 | GitHub, [Copilot agentic harness comparisons](https://github.blog/ai-and-ml/github-copilot/evaluating-performance-and-efficiency-of-the-github-copilot-agentic-harness-across-models-and-tasks/) (25 Jun 2026) | Same models, same tasks, normalised tools/context; **at least five repeats** per model/agent config; compared harness task resolution and token/cost | Copilot harness reported **similar resolution** while using fewer tokens in many settings; differences usually within run-to-run variation | Vendor-conducted but unusually controlled; run-to-run variance explicit | A/B compare our tools with model fixed; route by task size/cost only if measured |
| 6 | Microsoft researchers, [AgentLens](https://www.microsoft.com/en-us/research/publication/agentlens-revealing-the-lucky-pass-problem-in-swe-agent-evaluation/) (May 2026) | Analyse quality of action trajectories even when final patch passes tests; tag exploration, implementation, verification and wasted loops | **2,614** OpenHands traces reviewed over **60** SWE-bench tasks; among passing traces in 1,815-trace subset, **10.7%** showed "lucky pass" behaviour | Research study; benchmark/task-sampling limitations | Extend AgentWitness trace scoring; a green test alone is not a senior-quality execution verdict |
| 7 | Kaynar et al., [When Tools Fail, Agents Fabricate](https://gunkaynar.com/publications/fabricate.html), [RetryRealistic source](https://github.com/Kingsford-Group/RetryRealistic) (2026 workshop manuscript) | Realistic OS/SQLite/HTTP tool-fault injection; monitor checks structured observations and can veto unsupported final claims | Reported **2,100 faulted runs**, correct recovery **45.6%→56.3%**, fabricated answers **17.3%→10.8%** with monitor in one setup; failures still substantial | Research/workshop result, not independently reproduced here | Priority: test partial/truncated tools, stale results and unsupported success claims; use verification-first guard and safe retry |
| 8 | Li, [Repair Economics for Tool-Calling LLM Agents](https://zenodo.org/records/23117824) (3 Oct 2026 preprint) | Tested 6 framework retry policies on injected failures and compared idempotency, naive retry, validation and transactions | Idempotent strategy reached **48/60** successes with **0 duplicate side effects**, using **306 vs 426** calls for heavier transaction strategy; model-in-the-loop examples still omitted idempotency keys | Small single-author preprint; tool-specific | Put **idempotency keys, read-after-write checks and permanent-error classification in tooling**, not only prompts; critical for any approved write |
| 9 | SkillsBench researchers, [original paper](https://arxiv.org/abs/2602.12670), [1.1 release](https://www.skillsbench.ai/blogs/skillsbench-1-1) (Feb/Jun 2026) | Matched agent-model trials with/without curated procedural skill packs | Original: average **+16.2 percentage points** over 7 configurations; later 1.1 reports **33.9%→50.5% (+16.6pp)**; effect highly heterogeneous | Controlled benchmark, but not same as real production | Trial 2–3-module focussed skills (e.g. browser smoke acceptance) only against matched tasks |
| 10 | SWE-Skills-Bench researchers, [study](https://arxiv.org/abs/2603.15401) (Mar 2026 preprint) | Paired real repository tasks against skills on fixed commits and deterministic tests | **39 of 49 skills** yielded no pass-rate increase; average only **+1.2%**, with some negative outcomes and up to **451%** token overhead | Controlled SWE-specific counterevidence; not independently reproduced | **Do not bulk-add skills/prompts**; enforce A/B measurements and remove regressive skills |
| 11 | OpenAI, [SWE-bench Pro task audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) (8 Jul 2026) and [Epoch AI review](https://epoch.ai/benchmarks/swe-bench-pro/review) (Sep 2026) | Audited benchmark against actual task requirements, hidden tests and valid alternative solutions | OpenAI estimated **~30%** of tasks broken; human annotators flagged **249** tasks (**34.1%**) with issues | Strong benchmark-quality warning; results about a particular dataset | Human-audit our scoring rubric and hidden tests; if graders are unfair, fix them rather than punish the agent |
| 12 | Anthropic, [Infrastructure noise in agentic coding evals](https://www.anthropic.com/research/infrastructure-noise) (5 Feb 2026) | Repeated same model/harness/task under six CPU/RAM resource configurations | Terminal-Bench 2 success swung **6 percentage points**; infra errors **5.8%→0.5%** from strict to uncapped resources | Direct experiment; model success not only algorithmic | Control CPU/RAM/time and infra errors in PIP A/B tests before interpreting small score differences |
| 13 | OpenHands researchers, [PULSE in-the-wild agent evaluation](https://proceedings.mlr.press/v306/chen26da.html) (ICML 2026) | Combined user satisfaction with ML-assisted ratings and compared agent design choices in actual user interactions | Study covered **15,000 users** and reported **40% narrower confidence intervals** than ordinary A/B testing in its setting; benchmark rankings could diverge from satisfaction | Peer-reviewed, different domain/task mix | Track actual user acceptance/reopen burden; code benchmark metrics alone are insufficient |
| 14 | BenchAgent researchers, [Do More Agents Help?](https://huggingface.co/papers/2606.05670) (Jun 2026 preprint) | Normalised models, tools, answer protocols and cost across single versus multi-agent workflows | At most **one of six** tested multi-agent variants exceeded matched single-agent anchor, with others **2.56–11.29 points** worse on benchmark-balanced accuracy | Preprint, evaluation-specific | Keep a capable single-agent baseline and use independent second reviewer only when risk/uncertainty justifies it |
| 15 | METR, [2025 developer RCT](https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf) and [2026 replication-method note](https://metr.org/blog/2026-02-24-uplift-update/) | Randomised 246 tasks from 16 experienced open-source developers to AI-allowed vs disallowed; later reported recruitment/selection bias in newer follow-up | In early-2025 tools, AI allowance **increased** task time **19%** despite developers expecting speedup; later study signal was considered unreliable | RCT with limited population/tools/time period; not a claim about current models | Always measure total time and human correction effort instead of assuming AI activity equals speed |

### New public repositories inspected directly through GitHub today

- [Kingsford-Group/RetryRealistic](https://github.com/Kingsford-Group/RetryRealistic): public repo and README directly fetched. It contains fault injector, 30 task families, nine failure types, monitor, grading and offline checks per README; **tests not run here**.
- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench): public repo and README fetched. Native task definitions include oracle solutions and explicit verifiers; **benchmark not run here**.
- [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands): repository metadata confirmed after redirect, but a README fetch on the old path failed. **Do not claim its code was audited**.
- Microsoft's AgentLens source URL advertised in the paper could not be fetched through the connected GitHub source at the queried path. The published study was read, but the code was **not** independently examined today.

This is an actual external-source review, not merely a reading list. Nevertheless, **none of these projects has been installed, tested or integrated into our hosted ChatGPT session**.

## Countermeasures mapped to our recurring failures

| Our failure | Direct external precedent | Existing tool to reuse | Minimum demonstrable change |
|---|---|---|---|
| "Done" while scope remains unfinished | Anthropic structured failing-feature JSON and persistent per-feature progress | AgentWitness DoD + JoshMemory | Freeze complete acceptance list, check each item in real environment, no status promotion on prose |
| Stop after a partial PR/deploy | Anthropic incremental commits; human acceptance gate | JoshMemory handoffs + AgentWitness | Persist exact outstanding deliverables and resume from first unsatisfied acceptance criterion |
| Claim reviewed prior chats without reading them | RetryRealistic verification-first oversight; Anthropic trace inspection | ClaimGuard + external tool trace | Require evidence of actual source access, cite identifiers; mark unavailable data unknown |
| Green tests but broken product | Anthropic browser tool acceptance, Bolt browser-agent evals | AgentWitness contract + app/browser tests | Smoke test deployed primary action, screenshot/render/assets and mobile workflow where relevant |
| Fake/weak evidence and benchmark gaming | AgentLens lucky passes; SWE-bench benchmark audit | AgentWitness + LLMAccountability | Independent check of live state, test scope/freshness and source-of-truth; sample success traces |
| Repeated tool retries causing double changes | Idempotency research | Execution adapters/supervisor | Use idempotency keys for approved writes; read-after-write before retry; stop on 403 |
| Multi-agent overhead | BenchAgent study; GitHub harness matched-model evaluations | Existing reviewer coordinator | Default one implementer; escalate reviewers for significant security, ambiguity or test changes |
| Memory loss/duplicate work | Anthropic progress files and initialiser | JoshMemory leases/handoffs | Always load latest live state, active owner and next unsatisfied feature before work |
| Repeating same mistake next week | OpenAI trace→feedback→eval→change loop | Existing PIP + AgentWitness ledger | Convert every incident into reproducible eval; require re-run after intervention |
| Excessive token use/no real improvement | SkillsBench *vs* SWE-Skills-Bench contradictory results | Existing agent skills/docs | Randomise with-skill vs without-skill; retain only proven task-specific winners |
| Leaderboard looks better but user frustrated | PULSE user satisfaction study | KPI tracker | Track verified acceptance and corrective user effort, not just CI and benchmark pass |
| PIP comparison corrupted by hardware | Anthropic infrastructure noise study | ForgeGrid + evaluation runner | Pin resources and record actual error source; rerun matched trials |

## Prior art vs genuinely new findings

Already present in our system: witness receipts, anti-tampering, immutable Definition of Done, source-commit verification, supported independent test evidence, adversarial review, memory handoffs, work leases, remote job execution, quality gates, historical open-source prior-art research.

**New practical lessons worth explicitly testing:**
1. **Execution-trace quality ("lucky pass" classification)** in addition to binary final test pass.
2. **Tool-fault injection and partial-data fabrication** tests; monitor must inspect outcomes, not just success strings.
3. **Idempotency enforced by the write adapter** instead of leaving it to model text.
4. **Matched-model harness A/B trials**, including repeat-run variance, wall-clock and total user correction.
5. **Contradictory skills research:** software engineering often benefits far less than broad skills benchmarks suggest.
6. **Environment-sensitive success and unfair grader audits** before rating a model poorly.
7. **Independent human satisfaction outcomes** alongside engineering CI, especially for app and game experiences.

These are recommendations/hypotheses about **our** tools; their effectiveness here is currently untested.

## First three experiments to run

### Experiment A — REAL completion gate, not only a policy document
**Task:** One small existing app bug with a user-visible reproduction.  
**Baseline:** current normal agent workflow.  
**Intervention:** AgentWitness anchored DoD + runnable user-facing acceptance test + `aw final` actually executed, with all unsupported steps disclosed.  
**Measures:** independently verified user outcome; false-done claims; tests/rework; cost/latency.  
**No win unless:** source changes, tests, current deployment and final experience match the acceptance criteria.  
**Existing owners:** AgentWitness + JoshMemory.  
**Important:** hosted ChatGPT's access to local `aw` is **not established**.

### Experiment B — Fault injection / fabricated-success regression
**Task:** Make a sandboxed agent fetch partial data, encounter 401/403, stale response, truncated API payload, transient timeout and lost write acknowledgment.  
**Intervention:** verification-first observation checks and idempotent state-changing tool wrapper; stop on permanent errors.  
**Measures:** correct recovery, unsupported claims, duplicative side effects, total calls and honest block rates.  
**No win unless:** independent server state verifies success; no unauthorised external actions.

### Experiment C — Focused skills and independent-review escalation
**Task:** 10+ repeatable coding/QA work items with sufficient task diversity.  
**Comparisons:** base single-agent; base + narrowly scoped 2–3-module skill; base + risk-triggered independent review (same model, resource and time budgets where possible).  
**Measures:** verified completion, rework, latency, human interventions, cost and error bars.  
**No win unless:** improvement survives repeated matched tasks and does not increase customer correction.

### Critical validity considerations

- 20 tasks is a **pilot**, too small to certify near-perfect reliability. No honest 100% long-run guarantee.
- Test suites need independent audit; a green broken test suite creates false confidence.
- Separate **model error**, **tool error**, **environment failure**, **missing permissions**, **unsafe task** and **unclear original requirements**.
- No agent should be granted unsafe privileges or permission to send email simply to improve a KPI.
- All results require dates, task set, source/commit identifiers, repetitions and honest confidence intervals.

## Research follow-ups still needed

The next deeper pass should compare at least five *additional* external codebases at file/test level, reconcile current agent harness releases and new post-September developments, and reproduce fault-injection/acceptance experiments in a safe isolated environment. That is **not completed** by this first external findings document.

**Recommended management decision:** Keep the PIP as a measurement instrument, but make the first real engineering activity **a user-facing, independently verified task using the existing stack**, then test verification-first tool monitoring and selective skills/reviewer changes. Build **no additional general accountability app** without measured evidence that existing components cannot satisfy the requirement.
