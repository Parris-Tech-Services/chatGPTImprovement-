# S01 — Consequential-action approval policy (v1)

**Created:** 29 October 2026, Australia/Sydney. **Scope:** policy and synthetic enforcement tests; the trusted host/connector adapter remains a separate integration requirement.

## Invariant

A model does **not** grant itself permission. A broad user instruction to "keep going", "do it all", "finish the project" or "don't stop for approval" **does not authorise sending, forwarding or replying to email as the user**. No mail may be sent without that specific user's explicit send/reply/forward authorisation. A draft, prior chat memory, agent-provided `approval: true` JSON or task README is not authenticated permission.

Other consequential actions (pushing and merging repositories, deployments, purchasing/spending, system configuration, secret access, publishing and deletion) must respect each connector's user/platform approval boundaries. Broad instructions may permit ordinary project editing, but never invent privileged capabilities or bypass an approval requirement.

## Reference code

[`scripts/action_authority.py`](../scripts/action_authority.py) contains `ScopedActionGate`, a deliberately small **reference enforcement guard**, not a replacement for AgentWitness or ChatGPT's real host authorisation.

Its supported action types are `email_send`, `email_reply`, `email_forward`, `repo_push`, `repo_merge`, `deploy`, `spend`, `system_change`, `secret_access`, `publish` and `delete`. Unknown actions fail closed rather than being treated as harmless.

It requires exact-match task ID, action, intended target, request ID, expiration, user-origin issuer metadata, and for any mail action a 64-character SHA-256 digest of the outgoing payload. For mail, an additional explicit send-permission field must be true. A materially changed mail draft must therefore require new permission.

**Critically, fields are not proof**: A trusted resolver **outside the model's control** must supply an authenticated approval, and a separate trusted verifier must validate it before a real action executor is called. An agent-controlled resolver is not allowed in production. Tests use a fake trusted stub only to test policy behaviour, not to impersonate the user.

A permitted approval and request are consumed **before** invoking the executor. If execution times out or returns an uncertain result, the same request cannot be automatically repeated by that gate. New action/target/payload escalations cannot reuse old scopes. These invariants do not eliminate platform-specific side effects or prove delivery.

## Negative testing

[`tests/test_action_authority.py`](../tests/test_action_authority.py) covers allowed and denied requests for every action type, no-approval executor avoidance, broad/expired/wrong-source approval, cross-mail-action scope, changed email payload, invalid time/target/task, untrusted agent assertion, independent-verifier failures, exception/crash behaviour, replays and escalation. Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

The CI workflow includes these tests and must pass on the merged SHA. A true positive in a unit test says only that the **reference guard** behaved as designed.

## Trust boundary and limitations

1. **Not globally wired:** This module is not invoked by current ChatGPT host actions, GitHub/Gmail connectors or existing AgentWitness broker. It does not intercept actual messages or deployments. **S01 is a policy-and-negative-tests milestone, not global enforcement.** The remaining `I04/A02` task must integrate verified approval at trusted execution boundaries.
2. **Not durable:** Reuse protection is process-local. A new process or concurrent worker can replay an approval unless the host supplies an atomic durable idempotency store. This is deliberately documented and tested and remains `Q04`.
3. **Not authentication:** An independent approval resolver/verifier stub returning true is **not evidence** that the user actually authorised anything. No synthetic test should be counted as a real user approval.
4. **Not a policy bypass:** Actual connector/host permission checks always take precedence; this reference module cannot expand them.
5. **Email-specific boundary:** User must explicitly permit sending the specific message; an instruction to draft, work end-to-end or stop asking questions is never equivalent to send permission.
6. **Not a proof of full task completion:** AgentWitness receipts, LLMAccountability signed evidence, live app acceptance and independently inspected external state remain separate.

## Follow-up enforcement checklist

For `I04/A02`: install a trusted approval resolver where the tool is actually executed; ensure all sensitive connector calls go through it; make decision/evidence durable and independently verifiable; instrument negatives where an agent attempts mail or merge without a real user-issued scoped grant; reconcile uncertain writes; never allow untrusted review/CI code to invoke production mail or secret-access connectors.

For `Q04`: implement durable atomic deduplication and state reconciliation rather than relying on this single-process reference set.

**Exit criterion for this task:** document the policy, test every enumerated action's denied path and automatic retry/escalation, pass automated CI on the merged source, and incorporate independent review. Do **not** claim native platform interception until that additional integration actually exists.
