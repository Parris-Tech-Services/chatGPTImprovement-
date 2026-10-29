#!/usr/bin/env python3
"""S01 approval gate: a consequential action runs only under an explicit, scoped user approval.

Consequential actions are sending/replying/forwarding email, spending money or calling paid
APIs, merging, deploying, changing system configuration, and reading or using secrets.

Rules (all fail closed):
  * The approval must come from the user directly (source "user"). Text found in tool output,
    issues, emails, web pages or another agent's message never grants authority.
  * It names one action and one exact target (e.g. merge of PR owner/repo#12). A broad goal
    ("finish everything", "go till complete") is not an approval for any consequential action,
    and above all not for email.
  * Email approval is per verb: send, reply and forward are separate.
  * It is used at most `uses` times (default 1) and expires.
  * Retries reuse the same request ID and are executed at most once successfully; a retry can
    never change the action or target (no escalation from merge to deploy, PR #12 to #13).
  * Spending is capped by the approved amount.

This module enforces the rule for code paths that route actions through `ApprovalGate.run`.
It cannot stop an agent that bypasses it; record such bypasses as unwitnessed actions.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

CONSEQUENTIAL = {
    "email_send", "email_reply", "email_forward", "spend", "paid_api", "merge", "deploy",
    "system_config", "secret_access", "privilege_change", "delete",
}
TRUSTED_SOURCES = {"user"}
BROAD_PHRASES = ("everything", "all tasks", "whatever", "anything", "go till", "until complete", "don't stop", "do not stop")


class ApprovalDenied(Exception):
    """Raised when no valid approval covers the requested action; the action did not run."""


@dataclass
class Approval:
    id: str
    action: str
    target: str
    source: str
    granted_at: float
    expires_at: float
    uses: int = 1
    max_amount: float | None = None
    wording: str = ""
    used: int = 0
    spent: float = 0.0


@dataclass
class ApprovalGate:
    approvals: dict[str, Approval] = field(default_factory=dict)
    completed: dict[str, Any] = field(default_factory=dict)     # request_id -> result (idempotency)
    request_binding: dict[str, tuple[str, str]] = field(default_factory=dict)
    log: list[dict] = field(default_factory=list)
    clock: Callable[[], float] = time.time

    def grant(self, approval_id: str, action: str, target: str, *, source: str, wording: str,
              ttl_seconds: float = 3600, uses: int = 1, max_amount: float | None = None) -> Approval:
        if action not in CONSEQUENTIAL:
            raise ValueError("not a consequential action: " + action)
        if source not in TRUSTED_SOURCES:
            raise ApprovalDenied(f"approval from {source!r} is not the user's own instruction")
        if not target or target.strip() in {"*", "all", "any"}:
            raise ApprovalDenied("approval must name one exact target")
        if any(p in wording.lower() for p in BROAD_PHRASES) and target.lower() not in wording.lower():
            raise ApprovalDenied("a broad goal is not a scoped approval; it must name the action's target")
        if action in {"spend", "paid_api"} and (max_amount is None or max_amount <= 0):
            raise ApprovalDenied("spending approval needs a positive maximum amount")
        if uses < 1:
            raise ValueError("uses must be at least 1")
        now = self.clock()
        a = Approval(approval_id, action, target, source, now, now + ttl_seconds, uses, max_amount, wording)
        self.approvals[approval_id] = a
        return a

    def _check(self, approval_id: str | None, action: str, target: str, amount: float) -> Approval:
        if action not in CONSEQUENTIAL:
            raise ValueError("not a consequential action: " + action)
        a = self.approvals.get(approval_id or "")
        if a is None:
            raise ApprovalDenied(f"no approval for {action} on {target}")
        if a.action != action:
            raise ApprovalDenied(f"approval {a.id} covers {a.action}, not {action}")
        if a.target != target:
            raise ApprovalDenied(f"approval {a.id} covers {a.target}, not {target}")
        if self.clock() > a.expires_at:
            raise ApprovalDenied(f"approval {a.id} has expired")
        if a.used >= a.uses:
            raise ApprovalDenied(f"approval {a.id} is already used")
        if a.max_amount is not None and a.spent + amount > a.max_amount:
            raise ApprovalDenied(f"approval {a.id} allows {a.max_amount}, requested total {a.spent + amount}")
        return a

    def run(self, request_id: str, action: str, target: str, approval_id: str | None,
            perform: Callable[[], Any], *, amount: float = 0.0) -> Any:
        """Run `perform` once under approval. Retrying the same request returns the first result."""
        bound = self.request_binding.get(request_id)
        if bound and bound != (action, target):
            self.log.append({"request": request_id, "action": action, "target": target, "outcome": "denied-escalation"})
            raise ApprovalDenied(f"request {request_id} was for {bound[0]} on {bound[1]}; a retry cannot change it")
        if request_id in self.completed:
            self.log.append({"request": request_id, "action": action, "target": target, "outcome": "deduplicated"})
            return self.completed[request_id]
        try:
            a = self._check(approval_id, action, target, amount)
        except ApprovalDenied:
            self.log.append({"request": request_id, "action": action, "target": target, "outcome": "denied"})
            raise
        self.request_binding[request_id] = (action, target)
        result = perform()            # an exception leaves the approval unused, so the same request may retry
        a.used += 1
        a.spent += amount
        self.completed[request_id] = result
        self.log.append({"request": request_id, "action": action, "target": target, "approval": a.id, "outcome": "performed"})
        return result
