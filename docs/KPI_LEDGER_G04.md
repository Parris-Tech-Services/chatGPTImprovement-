# G04 · KPI ledger

[`scripts/kpi_ledger.py`](../scripts/kpi_ledger.py) computes the [KPI scorecard](KPI_SCORECARD.md) from **task evidence records** in `docs/evidence/*.json`, never from prose or the register's own status column.

**Rules:**
- **Reconciles to task IDs.** Every rate prints its numerator and denominator, and `--json` lists the task IDs on both sides.
- **Missing is not zero.** An unknown rework flag, follow-up count, claim count or timestamp is listed under `missing_ids`, and the rate shows **UNKNOWN** when nothing is measured.
- **Only valid records count as success.** A `VERIFIED COMPLETE` record that fails [`check_task_record`](../scripts/check_task_record.py) is reported as *status inflation*. That covers no independent evidence, scope edited after freezing, and performed actions without approval.
- **No hidden exclusions.** An excluded task needs a reason and is listed. A task with no reason, or unknown eligibility, stays in the denominator.
- **No double counting.** Two records for one task ID are an error, and neither counts.
- **Register cross-check.** A register row marked `VERIFIED COMPLETE` without a valid record is an *unsupported claim*.

**Optional `kpi` object on a record** (all fields nullable): `eligible`, `excluded_reason`, `accepted_at`, `verified_at`, `assistant_rework`, `corrective_followups`, `claims_made`, `claims_supported`.

**Adversarial tests:** [`tests/test_kpi_ledger.py`](../tests/test_kpi_ledger.py) has 16 cases. They cover inflated or self-reported success, tampered scope, reasonless exclusion, unknown eligibility, duplicates, missing data, impossible claim counts, claims from invalid records, mixed-timezone timestamps, wrong-scope or blank approvals, malformed record files, per-task traceability, unapproved actions and unsupported register claims.

## Historical prototype output — superseded, not current

The following is a **historical first-pass example** from before additional evidence records were merged into `main`. It must **not** be presented as today's measured performance, nor extrapolated into 50–100 chats. A scheduled report should execute the ledger against current records and explicitly list unknowns.

```
Records: 2  errors: 0  excluded: 0
End-to-end task success: 1.0 (2/2)
Status accuracy:         1.0 (2/2)  inflated: none
Assistant-caused rework: UNKNOWN (0/0)  missing: ['G01', 'S01']
Corrective follow-ups:   UNKNOWN (0 over 0 tasks)  missing: ['G01', 'S01']
Claim verification:      UNKNOWN (0/0)  missing: ['G01', 'S01']
Unauthorised actions:    0 
Median lead time (h):    UNKNOWN (n=0)  missing: ['G01', 'S01']
Register VERIFIED without valid record: ['I02']
```

**Finding:** the register lists **I02** as `VERIFIED COMPLETE`, but its evidence is a Markdown note ([I02 record](evidence/I02_2026-10-29.md)), not a machine-checkable record. Until a valid `I02_*.json` with independent evidence exists, the ledger reports I02 as an unsupported claim. CI runs the ledger as informational for now, so main isn't blocked.

**Status of G04:** the mechanism and adversarial tests are done. The backlog acceptance also depends on **G03** (a real baseline), so G04 stays **PARTIALLY COMPLETE** until real task records with `kpi` data flow through it.


## Review update — preventing KPI inflation

Following independent review, the script discards **unvalidated records** from corrective-followup averages, instead of letting a fabricated zero improve the result. It also treats invalid UTF-8 evidence files as individual unreadable records, preserving the rest of the report. Both failures have explicit regression tests.

Do not calculate real task-success rates from this sparse, self-selected engineering record sample: `G02/G03` must establish the audited cohort and independent outcome checks first. The primary KPI `end_to_end_task_success` currently measures **only the submitted records with accepted eligibility**, not ChatGPT's actual daily population of user requests.

For operational daily checks, combine this cautious evidence ledger with **live repository CI status** and **real application health**, explicitly reporting deployment and user-interaction verification separately.
