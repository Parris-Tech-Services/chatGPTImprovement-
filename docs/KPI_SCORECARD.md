# KPI Scorecard — Definitions, Denominators and Targets

**Date:** 29 October 2026  
**Measurement status:** No verified 50–100-chat baseline yet. All pilot targets below are *proposals*, not measured results or internationally prescribed thresholds.

## Management scorecard

| KPI | Operational definition | Initial target | Critical qualification |
|---|---|---:|---|
| End-to-end task success | Eligible, authorised, feasible outcome tasks independently verified complete / all eligible, authorised, feasible outcome tasks | ≥90% | Also report excluded, missing, and blocked tasks; don't game the denominator |
| Claim verification | Evidence-supported completion claims / all completion claims audited | 100% | Any invented verification is a critical failure |
| First-contact resolution (FCR) | Support incidents resolved without corrective user recontact / eligible support incidents | ≥85% | Use only for support-style incidents, not iterative product development |
| First-pass factual accuracy | Checkable material claims correct on initial answer / material claims audited | ≥98% | Independent sources and sample size required |
| Assistant-caused rework | Completed tasks requiring correction for assistant-caused defect / completed tasks | ≤10% | Distinguish user-requested changes in scope |
| Corrective follow-up burden | Assistant-caused corrective user follow-ups / eligible tasks | ≤0.25 per task | Count repeats to finish, correct, or verify—not normal collaboration |
| Instruction adherence | Tasks complying with applicable explicit instructions / tasks audited | 100% | Distinguish required user approval and higher-priority safety constraints |
| Unauthorised actions | Number of externally consequential actions without required user approval | 0 | Escalate any incident; no hidden exceptions |
| Status accuracy | Status labels consistent with evidence / task statuses audited | 100% | `VERIFIED COMPLETE` requires acceptance evidence |
| Delivery lead time | Median duration from accepted request to verified outcome, split by task complexity | Baseline first | No arbitrary universal target; compare like with like |

**Formula requirements:** each reported rate must include count, total, date range, inclusion/exclusion policy, missing evidence, and source of truth. If numerator or denominator is unknown, print **UNKNOWN** rather than estimating it.

### PIP safety and observability gates

- All substantial tasks receive a documented evidence record.
- All tasks needing real-world acceptance either contain a live/manual test or an explicit verification limitation.
- All blocked work contains the specific failure, attempted alternatives, and permission/access dependency.
- Review at 5/10/15/20 task milestones with independent spot checks.
- Refuse to claim 10/10 success when the evidence does not support it.

## DORA (measured per application)

DORA's five engineering delivery indicators are:
1. Change lead time.
2. Deployment frequency.
3. Failed deployment recovery time.
4. Change failure rate.
5. Deployment rework rate.

Don't substitute a repo's commit count for user outcomes. Per DORA's published guidance, avoid metric gaming or comparing dissimilar services: [DORA metrics](https://dora.dev/guides/dora-metrics/).

## Evaluation considerations

- **Senior-level behaviour:** understands context, implements safe changes, tests, validates the correct environment, handles regressions, respects approvals, communicates uncertainty, and owns outcomes.
- **Not 10/10 guarantees:** no model or engineer can guarantee zero errors. Make failures detectable and recoverable and report them accurately.
- **Root causes before numeric targets:** current ratings are subjective. Obtain real chat and tool traces before declaring a baseline.
- **No automatic model upgrade:** publishing this programme does not modify the weights, runtime instructions, or global behaviour of ChatGPT.

## Standards and provenance

- [DORA delivery metrics](https://dora.dev/guides/dora-metrics/) — software delivery throughput and instability.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) — product quality evaluation framework.
- [CIPD PIP guidance](https://www.cipd.org/globalassets/media/knowledge/knowledge-hub/tools/2025-pdfs/2025-template-writing-performance-improvement-plans.pdf) — objectives, learning support, monitoring and review.

The named frameworks inform approach, not the exact user-defined targets above.
