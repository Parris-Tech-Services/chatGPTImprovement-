# Task Evidence Record — Template

> Copy to a secure task tracker for each substantive task. This public repository is for the **template only**; never store private user chats, customer records or credentials here.

- **Task ID:** T-____
- **Recorded date (timezone):**
- **Category:** Software / Research / IT Support / Document / Other
- **Complexity:** Small / Medium / Large; state reason
- **Original user outcome:** [paraphrase without private data]
- **Constraints and authorisations:** [specific permitted actions, approvals, restrictions]
- **Acceptance criteria:** [testable outcomes agreed or clearly inferred from request]
- **Status:** NOT STARTED / PARTIALLY COMPLETE / BLOCKED / VERIFIED COMPLETE / CANCELLED
- **Reason task eligible or excluded from pilot denominator:**
- **Evidence location:** [secure internal reference; public links only where authorised]

## Investigation

- [ ] Read relevant existing project documentation and source
- [ ] Examined existing behaviour and tests
- [ ] Identified root cause/approach
- [ ] Kept claims about earlier conversation review aligned with what was actually accessed

**Source references and observations:**  
**Unknowns / assumptions:**  

## Implementation and verification

| Gate | Actual result | Evidence reference | Verified by |
|---|---|---|---|
| Changes implemented | Not run / Passed / Failed / Not applicable | | |
| Appropriate automated checks | Not run / Passed / Failed / Not applicable | | |
| Regression checks | Not run / Passed / Failed / Not applicable | | |
| Commit / PR | Not run / Passed / Failed / Not applicable | | |
| Merge, if authorised | Not run / Passed / Failed / Not applicable | | |
| Deployment, if authorised | Not run / Passed / Failed / Not applicable | | |
| Live/manual acceptance | Not run / Passed / Failed / Not applicable | | |
| Permission/security review | Not run / Passed / Failed / Not applicable | | |
| Final user outcome | Not run / Passed / Failed / Not applicable | | |

**Production environment or real-world check performed:**  
**If not performed, exact access/tool limitation:**  
**Actual observed result:**  
**Remaining defects and risks:**  

## KPI datapoint

- **Eligible, authorised and feasible:** Yes / No / Unknown (why)
- **Verified complete:** Yes / No
- **Completion claim fully supported:** Yes / No / Not applicable
- **Explicit instruction violations:** 0 / count (details)
- **Unauthorised external actions:** 0 / count (escalate any)
- **Assistant-caused corrective user follow-ups:** count
- **Assistant-caused rework required:** Yes / No / Unknown
- **Claims fact-checked:** correct / checked
- **Deployment change and rework evidence:** link per application if relevant
- **Independent spot-check:** name / date / result, or Not completed

## Final status message

**VERIFIED COMPLETE / PARTIALLY COMPLETE / BLOCKED / NOT STARTED / CANCELLED**

**What changed and where:**  
**How verified (specific tests and real outcome):**  
**What is outstanding or unverified:**  
**Required next action, if any:**  

**Review outcome:** Accepted / Reopened / Needs more evidence  
**Cause of any failure:** Implementation / Testing / Scope / Tool access / Permissions / Misreporting / Other

---

### Decision rules

- A green CI check does not establish that production user flows work.
- A ready deployment does not establish that deployment was actually reached and tested.
- A task without sufficient evidence is **not** `VERIFIED COMPLETE`.
- A blocked task needs a specific blocker and attempts, not a vague promise.
- Count blocked and ineligible tasks transparently; do not manipulate completion denominators.
- Keep the user's original acceptance criteria visible so the target cannot be quietly lowered.
