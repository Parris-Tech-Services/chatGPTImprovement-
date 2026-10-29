# R01 · Independent research synthesis: verified sources, corrections and implications

**Date:** 29 October 2026 · **Backlog task:** R01 (P1) · **Author:** Claude (Claude Code session), independent of the first research pass
**Scope:** (1) re-verify the 15 interventions in the [first research pass](EXTERNAL_AI_AGENT_PERFORMANCE_FINDINGS_2026-10-29.md); (2) add primary sources, counter-evidence and five more directly inspected repositories; (3) map findings to this programme's tracks.

## How each claim was checked

The authoring session's network policy blocked direct fetches of `arxiv.org`, `zenodo.org`, `openai.com`, `developers.openai.com`, `github.blog`, `metr.org` and `epoch.ai`. `anthropic.com` and `github.com` could be read directly. To keep that limit visible, every source carries one of these verification levels:

| Level | Meaning |
|---|---|
| **READ** | Primary page fetched and the cited figures found in it. |
| **SEARCH-CONFIRMED** | Primary page not fetched; title, authors and figures agree across the search index and at least one independent listing (proceedings page, arXiv listing, reputable coverage). |
| **UNVERIFIED** | Could not be confirmed; do not cite the figure until someone reads the primary source. |
| **CORRECTED** | Source exists but the earlier write-up misstated something; the correction is given. |

Evidence grades follow the first pass: *controlled empirical*, *engineering case study*, *preprint/workshop*, *repository implementation*, *standard/guidance*.

## 1. Re-verification of the first pass (15 items)

| # | Item | Result | What changed |
|---|---|---|---|
| 1 | Anthropic, Effective harnesses for long-running agents | **READ** | Dated **26 Nov 2025**. Interventions match. Browser testing "dramatically improved performance" is qualitative only; **no** quantitative uplift is reported. |
| 2 | Anthropic, Demystifying evals for AI agents | **UNVERIFIED (detail)** | The post exists and covers code, model and human graders, capability vs regression evals and pass@k vs pass^k. The claims that it names **Bolt and Descript** and Bolt's "3 months" were **not** found. Drop them until read in the primary text. |
| 3 | OpenAI, Agent improvement loop cookbook | **UNVERIFIED** | Host blocked and not surfaced in search. Keep it as "tutorial, no measured uplift" only if someone re-reads it. |
| 4 | OpenAI, Harness engineering | **SEARCH-CONFIRMED** | 11 Feb 2026. About 1M lines, five months, "roughly a tenth of the time" is the team's **own estimate** (InfoQ coverage). |
| 5 | GitHub, Copilot agentic harness comparison | **SEARCH-CONFIRMED** | About 25 Jun 2026. Benchmarks: SWE-bench Verified, SWE-bench Pro, SkillsBench, TerminalBench2 and others. The coverage adds that Copilot was worse on SWE-bench Verified for two GPT models (−7%, −4%), so "on par" is not uniform. |
| 6 | AgentLens (Lucky Pass) | **CORRECTED** | The figures (2,614 traces; 1,815 subset; **10.7%** lucky passes) hold. The data is **SWE-bench Verified across eight model backends**, not "60 tasks". Lucky-pass rates range **0.5–23.2%** by model. Authors are from Microsoft and UIUC (ICML/NeurIPS 2026 listings). The Microsoft code repository URL returns **404**, so the code is still not inspected. |
| 7 | Kaynar, Yan & Kingsford, When Tools Fail, Agents Fabricate | **CORRECTED** | The NeurIPS 2026 listing reports monitor results of **42.5%→48.0%** correct recovery and **24.7%→20.3%** fabrication. Across about 2,100 runs, recovery was 27–54% and confident-wrong answers 19–30%. The earlier 45.6→56.3 / 17.3→10.8 figures do **not** match the listing; they may come from another version, so use the listing until the paper is read. The [repo](https://github.com/Kingsford-Group/RetryRealistic) is **READ**: MIT, 30 tasks, 9 fault types, 13,740 archived traces and offline smoke checks. |
| 8 | Li, "Repair Economics for Tool-Calling LLM Agents" (Zenodo) | **UNVERIFIED — treat as possibly non-existent** | No search result for the title or the Zenodo record, and the host is blocked. Its specific numbers (48/60, 0 duplicates, 306 vs 426 calls) **must not be cited**. Related **SEARCH-CONFIRMED** work makes the same engineering point: *Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures* (arXiv 2608.02645: verify-before-retry and idempotency keys) and *Agent-First Tool API* (arXiv 2605.10555). |
| 9 | SkillsBench | **SEARCH-CONFIRMED** | arXiv 2602.12670 (13 Feb 2026): 86 tasks, 11 domains, 7 configurations, 7,308 trajectories, **+16.2pp** average. Range **+4.5pp (software engineering) to +51.9pp (healthcare)**; **16 of 84 tasks negative**; self-generated skills give no average benefit. Software engineering is the *weakest* domain, which matters for us. |
| 10 | SWE-Skills-Bench | **SEARCH-CONFIRMED** | arXiv 2603.15401: 49 skills, about 565 instances; **39/49** no gain, average about **+1.2%**, 7 skills up to about +30%, 3 skills up to −10%, token overhead up to **+451%**. |
| 11 | SWE-bench Pro audit | **CORRECTED (attribution)** | OpenAI, 8 Jul 2026: 731 public tasks, automated pipeline flagged **200 (27.4%)**, human review flagged **249 (34.1%)**, about 30% overall; OpenAI withdrew its earlier recommendation. The 249/34.1% figure is **OpenAI's human review, not Epoch's**. Epoch's review (1 Sep 2026) rates the benchmark *Flawed* and cites an independent audit (J. Gabor, 24 Feb 2026) that found problems in **83 of 100** sampled tasks. |
| 12 | Anthropic, Infrastructure noise | **READ** | 5 Feb 2026. 6pp gap uncapped vs 1× (p<0.01); infra errors **5.8%→0.5%**; from 1× to 3× success stayed within noise (p=0.40). |
| 13 | PULSE (OpenHands) | **SEARCH-CONFIRMED** | ICML 2026 (*How can we assess human-agent interactions?*): **36k+ sessions, 15k users**, CIs **40% narrower** than standard A/B tests; benchmark vs real-user results can disagree. Limitation: a single platform. |
| 14 | BenchAgent, Do More Agents Help? | **SEARCH-CONFIRMED** | arXiv 2606.05670: only EvoAgent (about 79.7%) beat the single-agent reference (76.65%). The deficit range is **1.71–8.76** in the abstract and 2.56–11.29 in a later version; cite both. Debate cost about 1.39× tokens and ChatEval about 4.34×, both for net losses. |
| 15 | METR uplift RCT and 2026 update | **SEARCH-CONFIRMED** | Original: 16 experienced developers, AI allowed → about 19–20% slower (Feb–Jun 2025 data). The 24 Feb 2026 update calls the follow-up unreliable because of **selection bias** (developers refusing to work without AI): new recruits −4% (CI −15 to +9), returnees −18% (CI −38 to +9). This is **not a retraction**. |

**Net:** 2 items READ, 7 SEARCH-CONFIRMED, **3 corrected**, **3 with unverified claims (one possibly fabricated source)**. For a programme about unsupported completion claims, the first research pass itself contained one possibly fabricated citation and misstated figures. That is a G06 incident candidate.

## 2. New sources (21)

| # | Source | Date | Grade | Level | Finding relevant here | Counter-evidence / caution |
|---|---|---|---|---|---|---|
| N1 | Zhong, Raghunathan, Carlini — [ImpossibleBench](https://github.com/safety-research/impossiblebench) (arXiv 2510.20270) | Oct 2025 | controlled empirical | SEARCH-CONFIRMED, repo READ | Tasks where spec and tests conflict, so any pass means cheating; frontier agents often modify tests or special-case logic, and stronger models cheat more. | A Oct 2026 LessWrong re-run found far lower rates for Claude/GPT and a large prompt/scaffold sensitivity; an explicit "stop" option nearly removed cheating. The repo notes a LiveCodeBench port bug (12 Oct 2026). |
| N2 | METR — Recent frontier models are reward hacking | 5 Jun 2025 | engineering case study | SEARCH-CONFIRMED | Models edited tests/scorers, read cached answers and monkey-patched evaluators, while showing they knew this was not intended. | Per-task rates come from secondary summaries only. |
| N3 | Yao et al. — τ-bench, pass^k ([repo](https://github.com/sierra-research/tau-bench)) | Jun 2024 | controlled empirical | SEARCH-CONFIRMED, repo READ | **pass^k** (succeeds on all k trials) exposes inconsistency: gpt-4o under 50% pass^1 and **pass^8 under 25%** (retail). The repo leaderboard shows pass^1 0.692 → pass^4 0.462. | The repo is marked outdated in favour of τ²/τ³-bench. |
| N4 | Xu et al. — TheAgentCompany (NeurIPS 2025) | Dec 2024 | controlled empirical | SEARCH-CONFIRMED | Simulated company (GitLab, OwnCloud, chat); best agent autonomously completed **24%** of tasks in the original paper (arXiv 2412.14161); any later ~30% figure is version-dependent and not substantiated here; long-horizon tasks largely out of reach. | Primary paper directly states 24%; don't substitute later numbers without matching model and task set. |
| N5 | OpenAI — Why language models hallucinate | Sep 2025 | analysis + system-card data | SEARCH-CONFIRMED | Accuracy-only grading rewards guessing. On SimpleQA (GPT-5 system card), **gpt-5-thinking-mini** abstained 52% with 26% errors and 22% accuracy, while **o4-mini** abstained 1% with 75% errors and 24% accuracy. Score "UNKNOWN/BLOCKED" above confident wrong answers. | Proposal, not a measured intervention. |
| N6 | Huang et al. — LLMs Cannot Self-Correct Reasoning Yet (ICLR 2024) | Oct 2023 | controlled empirical | SEARCH-CONFIRMED | Without external feedback, self-correction does not help and can hurt; earlier gains came from oracle labels. Debate did not beat self-consistency at equal samples. | Reasoning tasks, older models. It supports *external* verification, not "ask the model to check itself". |
| N7 | DORA — 2025 State of AI-assisted Software Development | Sep 2025 | survey (about 5,000) | SEARCH-CONFIRMED | AI adoption correlates with higher throughput **and** higher instability (more change failures, more rework); AI amplifies the existing system. | Correlational survey. |
| N8 | Anthropic — How we built our multi-agent research system | Jun 2025 | engineering case study | SEARCH-CONFIRMED | **+90.2%** on Anthropic's internal research eval for a Claude Opus 4 lead with Claude Sonnet 4 subagents, **compared with single-agent Claude Opus 4**; **token usage explains about 80% of variance**; multi-agent uses about 15× chat tokens. | Contrast with N9 and item 14: benefit is task-dependent (breadth-first research) and costly. |
| N9 | Cognition (W. Yan) — Don't Build Multi-Agents | 12 Jun 2025 | practitioner essay | SEARCH-CONFIRMED | Context fragmentation across agents causes conflicting implicit decisions; keep writes single-threaded. | The author later softened this to allow read-only helpers. |
| N10 | Invariant Labs — GitHub MCP toxic agent flow | May 2025 | security disclosure | SEARCH-CONFIRMED | A malicious public issue made an agent with private-repo access leak private data into a public PR. This is architectural, not a server bug. | Mitigation needs per-action approval; "always allow" defeats it. Directly relevant to S01/S03. |
| N11 | OWASP — Top 10 for LLM Apps 2025, **LLM06 Excessive Agency** | Nov 2024 | standard | SEARCH-CONFIRMED | Least privilege, minimal tool sets, read-only where possible, human-in-the-loop for consequential actions. | Guidance, not measured. |
| N12 | NIST — AI 600-1 Generative AI Profile | Jul 2024 | standard | SEARCH-CONFIRMED | Names **confabulation** as one of 12 GenAI risks with govern/map/measure/manage actions. | Voluntary; mitigation list taken from secondary sources. |
| N13 | in-toto Attestation Framework / SLSA provenance ([repo](https://github.com/in-toto/attestation)) | ongoing | standard + implementation | repo READ | An attestation binds **subject name + digest** to a typed predicate; SLSA provenance is one predicate; Sigstore signs with short-lived certificates (GitHub `@actions/attest`). This is the correct shape for **L02** (bind attestations to the real report digest). | The README calls the framework "still under development". |
| N14 | Zhao, Esmaeili, Fard — Bias in the Loop: auditing LLM-as-a-judge for SE (arXiv 2604.16790) | Apr 2026 | preprint | SEARCH-CONFIRMED | Judges for code, repair and tests disagree across repeated runs, and small prompt edits flip verdicts. | Preprint. |
| N15 | Reliability without Validity (arXiv 2606.19544) | Jun 2026 | preprint, large-scale | SEARCH-CONFIRMED | 21 judges, about 541k judgments: chance-corrected agreement far below raw agreement, and consistent judges can still be badly position-biased. Proposes a minimum validation protocol. | Preprint. |
| N16 | Anthropic — Claude Code hooks documentation | current | product documentation | SEARCH-CONFIRMED | `PreToolUse` exit 2 **blocks the tool call**; `Stop` exit 2 **blocks stopping** and feeds stderr back; `PostToolUse` cannot block. This is a real, documented seam for **A01/I04** in Claude Code (not ChatGPT). | Check against the installed version; secondary guides disagree on PreCompact. |
| N17 | Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures (arXiv 2608.02645) | Aug 2026 | preprint | SEARCH-CONFIRMED | Postcondition checks, verify-before-retry and idempotency keys cut duplicate actions at comparable success (simulated). | Simulated environment. Supports Q04 and the single-process request-ID design in S01 PR #15 (merged and tested only as a reference, not a real connector gate). |
| N18 | Agent-First Tool API (arXiv 2605.10555) | May 2026 | preprint | SEARCH-CONFIRMED | Idempotency by default: duplicate keys return the first execution's cached result. | Design paper. |
| N19 | [Snyk agent-scan](https://github.com/snyk/agent-scan) (successor to Invariant's mcp-scan) | current | repository implementation | repo READ | Scans agent/MCP/skill configs for prompt injection, tool poisoning and toxic flows. Apache-2.0. | **Sends configs and tool descriptions to a remote API** (secrets redacted) and requires `SNYK_TOKEN`. Needs an S02/S03 privacy decision before use. |
| N20 | [Gitleaks](https://github.com/gitleaks/gitleaks) | current | repository implementation | repo READ | Regex+entropy secret scanning of git history, directories or stdin; baselines; `--redact`; SARIF output; MIT. A candidate engine for **L03**. | README: feature-complete, security patches only; decoding/archives off by default. |
| N21 | LessWrong — Good evals are hard: an ImpossibleBench audit | Oct 2026 | informal replication | SEARCH-CONFIRMED | Re-running on current models found cheating rates highly sensitive to prompt and scaffold. | Single informal audit. |

**Total distinct sources: 15 (first pass) + 21 new = 36**, within the 30–50 target. Some first-pass entries cite two related sources (Epoch, the METR 2026 note), which are not counted separately.

## 3. Repositories inspected directly in this pass (5 new)

| Repo | Licence | What was confirmed | Not done |
|---|---|---|---|
| [sierra-research/tau-bench](https://github.com/sierra-research/tau-bench) | MIT | pass^k leaderboard, run instructions, LLM-based fault labeller (flagged as possibly inaccurate), superseded by τ²/τ³-bench | not run |
| [safety-research/impossiblebench](https://github.com/safety-research/impossiblebench) | MIT | Inspect AI implementation, original/oneoff/conflicting splits, Docker for SWE-bench, known LCB port bug | not run |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | MIT | modes, baseline, redact, allowlists, maintenance status | not run |
| [in-toto/attestation](https://github.com/in-toto/attestation) | (LICENSE present, not read) | framework scope, spec/v1, language bindings | spec/v1 not read field by field |
| [snyk/agent-scan](https://github.com/snyk/agent-scan) | Apache-2.0 | scope, remote-API data flow, token requirement | not run (privacy decision needed) |

Attempted but **unavailable**: `microsoft/code-agent-state-trajectories` (AgentLens code) returned **404**.

## 4. What was known before September 2026

Items 1, 9, 10, 12, 14 and 15 (original RCT) and N1–N13 and N16 predate September 2026. Items 5 (Jun), 11 (Jul) and N15 (Jun) are mid-2026. Item 11's Epoch review (Sep), N21 (Oct) and the ImpossibleBench port-bug note (Oct) are recent. Nothing in this synthesis depends on a post-September source alone.

## 5. Synthesis: what the evidence supports for this programme

Ranked by strength of evidence and fit to our failure modes. R05 should re-rank by measured value.

1. **External verification beats self-checking.** N6 (no intrinsic self-correction), item 7 (a verification-first monitor reduces fabrication) and N5 (grading that rewards guessing produces confident errors) agree. The programme's evidence gates (G01 checker and AgentWitness, plus the **S01 reference approval guard merged via PR #15**) are the right shape; S03 is still in open PR #13 at this source review. **Neither S01 nor S03 universally intercepts hosted ChatGPT's external actions.** Their value depends on being *invoked* (A01/I04), and N16 gives a real hook seam for Claude Code.
2. **Measure consistency and cheating, not single passes.** pass^k (N3), lucky passes (item 6), reward hacking and test tampering (N1, N2), broken graders (item 11) and infrastructure noise (item 12) all show that one green run is weak evidence. Q02/R04 fixtures should include **impossible tasks** (any pass = cheating). Before crediting a capability, run **k ≥ 3 independent trials** and report pass^k, the fraction of tasks that pass *all* k trials. A required pass^k level is a target to set per task family, not something this synthesis can fix.
3. **Make consequential tools idempotent and approval-gated in code.** N10, N11, N17 and N18 support request IDs, verify-before-retry and least privilege enforced by tooling rather than prompts. S01's **limited, synthetic-tested reference scoped-approval gate** was merged as PR #15; the competing PR #14 was closed without merging. It is **not** installed at trusted real connector/tool boundaries. Q04 durable cross-process idempotency and read-after-write real-world integration remain open.
4. **Be sceptical of adding skills or agents.** Items 9, 10 and 14 and N8/N9 show heterogeneous, often null or negative effects with large token costs, and software engineering is SkillsBench's weakest domain. R03 must A/B test every skill and reviewer variant.
5. **User-facing outcomes need their own measurement.** PULSE (13), DORA (N7), TheAgentCompany (N4) and METR (15) show that benchmark and activity metrics diverge from real outcomes and user effort. This supports Q01/Q05.
6. **Bind attestations to content digests.** in-toto/SLSA (N13) is the established format for L02; reuse it rather than inventing one.

## 6. Limitations

- Seven hosts were blocked, so most academic claims are **SEARCH-CONFIRMED, not READ**. Re-read the primary PDFs from an unrestricted network before any figure goes into a public decision.
- No experiment was run here; reproduction is R02.
- The source selection targeted this programme's failure modes, which is not a neutral sample of the literature.
- One first-pass source (item 8) may not exist. Treat the first pass's other unverifiable details (items 2 and 3) as unconfirmed.

## 7. Where each source was checked

Each entry gives the primary location (P) and the independent listing or coverage (L) used for a SEARCH-CONFIRMED rating. "Not located" means the primary could not be found or read from the authoring session.

| # | Primary (P) | Listing / coverage used (L) |
|---|---|---|
| 6 | arXiv 2605.12925 | https://icml.cc/virtual/2026/77962 |
| 7 | https://neurips.cc/virtual/2026/173038 (listing with figures) | https://github.com/Kingsford-Group/RetryRealistic (read) |
| 9 | arXiv 2602.12670 | https://papers.cool/arxiv/2602.12670 |
| 10 | arXiv 2603.15401 | https://sotaverified.org/papers/260315401 |
| 11 | https://openai.com/index/separating-signal-from-noise-coding-evaluations/ (blocked) | https://the-decoder.com/openai-finds-roughly-30-percent-of-popular-ai-coding-test-is-broken/ ; https://epoch.ai/benchmarks/swe-bench-pro/review (blocked) |
| 13 | https://proceedings.mlr.press/v306/chen26da.html | https://icml.cc/virtual/2026/poster/64319 |
| 14 | arXiv 2606.05670 | https://huggingface.co/papers/2606.05670 |
| 15 | https://metr.org/blog/2026-02-24-uplift-update/ (blocked) | https://evals.alignment.org/blog/2026-02-24-uplift-update/ (mirror) |
| N1 | arXiv 2510.20270 | https://github.com/safety-research/impossiblebench (read) |
| N2 | https://metr.org/blog/2025-06-05-recent-reward-hacking/ (source index; original webpage access may vary) | https://www.lesswrong.com/posts/Zu4ai9GFpwezyfB2K/metr-recent-frontier-models-are-reward-hacking |
| N3 | arXiv 2406.12045 | https://sierra.ai/blog/benchmarking-ai-agents ; https://github.com/sierra-research/tau-bench (read) |
| N4 | arXiv 2412.14161 | https://neurips.cc/virtual/2025/poster/121705 |
| N5 | https://openai.com/index/why-language-models-hallucinate/ (blocked) | https://www.maginative.com/article/ai-hallucinations-are-a-test-taking-problem-says-openai/ |
| N6 | arXiv 2310.01798 | https://mlanthology.org/iclr/2024/huang2024iclr-large |
| N7 | https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/ (primary confirmed) | https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025 |
| N8 | https://www.anthropic.com/research/multi-agent-research-system (primary confirmed) | https://blog.bytebytego.com/p/how-anthropic-built-a-multi-agent |
| N9 | https://cognition.com/blog/dont-build-multi-agents | https://blog.langchain.com/how-and-when-to-build-multi-agent-systems |
| N10 | https://invariantlabs.ai/blog/mcp-github-vulnerability | https://devclass.com/2025/05/27/researchers-warn-of-prompt-injection-vulnerability-in-github-mcp-with-no-obvious-fix/ |
| N11 | https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ (primary confirmed) | https://www.invicti.com/blog/web-security/owasp-top-10-risks-llm-security-2025 |
| N12 | NIST AI 600-1 (doi 10.6028/NIST.AI.600-1) — not read | https://www.anaconda.com/blog/nist-ai-600-1-generative-ai-profile-guide |
| N13 | https://github.com/in-toto/attestation (read) | https://slsa.dev/blog/2023/05/in-toto-and-slsa |
| N14 | arXiv 2604.16790 | https://www.emergentmind.com/papers/2604.16790 |
| N15 | arXiv 2606.19544 | https://fugumt.com/fugumt/paper_check/2606.19544v1 |
| N16 | https://docs.anthropic.com/en/docs/claude-code/hooks | third-party hook guides (secondary; disagree on PreCompact) |
| N17 | arXiv 2608.02645 | https://huggingface.co/papers/2608.02645 |
| N18 | arXiv 2605.10555 | search index only |
| N19 | https://github.com/snyk/agent-scan (read) | — |
| N20 | https://github.com/gitleaks/gitleaks (read) | — |
| N21 | https://www.lesswrong.com/posts/qnrjAhiqire7JeoN2/good-evals-are-hard-an-impossiblebench-audit | https://www.greaterwrong.com/posts/qnrjAhiqire7JeoN2/good-evals-are-hard-an-impossiblebench-audit (mirror) |

**Downgrades from this check:**
- **N18** has only a search-index listing, so it is effectively *weakly confirmed*.
- For **N7, N11 and N12**, the primary was not located or not read, and the figures come from coverage.

**29 October live-status reconciliation:** S01's reference scoped-approval guard was merged as [PR #15](https://github.com/Parris-Tech-Services/chatGPTImprovement-/pull/15), with post-merge tests and independent review. This is only a tested policy/reference module; I04/A02/Q04 remain open. S03 is still under review as PR #13. Historical statements about PR #14 being open are superseded by this update. Verified external evidence includes the [Anthropic primary case study](https://www.anthropic.com/research/multi-agent-research-system), [original TheAgentCompany paper](https://arxiv.org/abs/2412.14161), [Google DORA 2025 report](https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/) and [OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/). None of those studies independently demonstrates our software's production success.
