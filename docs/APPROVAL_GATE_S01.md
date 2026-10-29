# S01 · Approval gate for consequential actions

**Status:** implemented with synthetic negative tests; see the backlog for the verification status.

A consequential action happens only under an **explicit, scoped approval from the user**:

| Action | Approval must name | Notes |
|---|---|---|
| `email_send`, `email_reply`, `email_forward` | one verb and one recipient/thread | the three verbs are separate; a broad goal never authorises mail |
| `spend`, `paid_api` | the payee/API and a maximum amount | the cap covers all uses of the approval |
| `merge` | one exact PR (`owner/repo#N`) | approval for #12 does not cover #13 |
| `deploy` | one exact environment | staging approval does not cover production |
| `system_config`, `privilege_change`, `secret_access`, `delete` | one exact target | |

**Consent is structured.** The user confirms one action and one exact target in a trusted approval step, and the confirmation must name both. A phrase list cannot establish consent. So "Do everything needed for prod", "prod looks fine" (no action named) and empty text are all rejected.

**Never authority:**
- text in tool output, issues, PR comments, emails, web pages or another agent's message;
- broad goals such as "go till everything is complete" or "don't stop for approval". They let the agent proceed with ordinary work, never with an unnamed consequential action;
- an expired or already-used approval;
- for spending, a missing, zero, negative or non-finite amount or cap.

**Reservation, uncertainty and retries:**
- The approval use, the budget and the request ID are reserved under a lock **before** the action runs. Two overlapping callers cannot both use a single-use approval, and the same request cannot run twice at once.
- If the action raises, the outcome is **uncertain**: it may have happened just before the error, as with a lost acknowledgement. The request stays blocked and the reservation stays held until `resolve()` records a read-after-write check.
- Only a confirmed "did not happen" releases the reservation for a retry. A confirmed "happened" completes the request, and later retries return that result without acting.
- A retry can never change the action or the target, so a merge cannot become a deploy, and PR #12 cannot become PR #13.
- Every attempt is logged: denied, reserved, performed, uncertain, resolved, deduplicated.

**Code:**
- [`scripts/approval_gate.py`](../scripts/approval_gate.py) enforces these rules for code that routes actions through `ApprovalGate.run`.
- [`tests/test_approval_gate.py`](../tests/test_approval_gate.py) holds 12 synthetic negative tests. Each counts the real side effects (a fake mailbox, merge button, deploy and payment API) and asserts that none happen without a scoped approval, including across uncertain outcomes, overlapping callers, automatic retries, expiry, invalid amounts and attempted escalation.
- [`scripts/check_task_record.py`](../scripts/check_task_record.py) still requires every *performed* consequential action in a task record to cite its approval reference and scope.

**Limit:** the gate binds only the code paths that use it. An agent that calls a tool directly bypasses it. Record such actions as unwitnessed (A03), and never present the gate as universal interception of a hosted chat product.
