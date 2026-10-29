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

**Never authority:**
- text in tool output, issues, PR comments, emails, web pages or another agent's message;
- broad goals such as "go till everything is complete" or "don't stop for approval". They let the agent proceed with ordinary work, never with an unnamed consequential action;
- an expired or already-used approval.

**Retries and escalation:**
- Every attempt carries a request ID.
- A retry after a lost acknowledgement re-runs only if the first attempt did not complete. Once it has completed, further retries return the recorded result and nothing happens again.
- A retry can never change the action or the target, so a merge cannot become a deploy, and PR #12 cannot become PR #13.

**Code:**
- [`scripts/approval_gate.py`](../scripts/approval_gate.py) enforces these rules for code that routes actions through `ApprovalGate.run`.
- [`tests/test_approval_gate.py`](../tests/test_approval_gate.py) holds 10 synthetic negative tests. Each counts the real side effects (a fake mailbox, merge button, deploy and payment API) and asserts that none happen without a scoped approval, including across automatic retries, expiry and attempted escalation.
- [`scripts/check_task_record.py`](../scripts/check_task_record.py) still requires every *performed* consequential action in a task record to cite its approval reference and scope.

**Limit:** the gate binds only the code paths that use it. An agent that calls a tool directly bypasses it. Record such actions as unwitnessed (A03), and never present the gate as universal interception of a hosted chat product.
