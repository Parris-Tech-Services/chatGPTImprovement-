#!/usr/bin/env python3
"""S01 approval gate: a consequential action runs only under an explicit, scoped user approval.

Consequential actions are sending/replying/forwarding email, spending money or calling paid
APIs, merging, deploying, changing system configuration, privilege changes, reading or using
secrets, and deleting.

Rules (all fail closed):
  * Consent is STRUCTURED: the user confirms one action and one exact target in a trusted
    approval step (source "user"), and the confirmation text must name both the action and the
    target. A phrase list cannot establish consent, so broad goals ("do everything needed for
    prod", "go till complete", empty text) are rejected even when they mention the target.
    Text found in tool output, issues, emails, web pages or another agent's message never
    grants authority.
  * Email approval is per verb: send, reply and forward are separate.
  * An approval is used at most `uses` times, expires, and for spend/paid_api carries a finite
    positive cap; every spend request must state a finite positive amount.
  * Each attempt is RESERVED (approval use, budget and request ID) under a lock before any
    external code runs, so overlapping callers cannot share one single-use approval.
  * If the action raises, its outcome is UNCERTAIN (it may have happened before the error).
    The request stays blocked, and the reservation stays held, until `resolve()` records the
    result of a read-after-write check. Only a confirmed "did not happen" releases it for retry.
  * A retry reuses the same request ID, returns the recorded result once completed, and can
    never change the action or target (no escalation from merge to deploy, PR #12 to #13).
  * Every attempt is logged: denied, reserved, performed, uncertain, resolved, deduplicated.

This module enforces the rules for code paths that route actions through `ApprovalGate.run`.
It cannot stop an agent that bypasses it; record such bypasses as unwitnessed actions.
"""
from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

CONSEQUENTIAL = {
    "email_send", "email_reply", "email_forward", "spend", "paid_api", "merge", "deploy",
    "system_config", "secret_access", "privilege_change", "delete",
}
SPENDING = {"spend", "paid_api"}
TRUSTED_SOURCES = {"user"}
# The confirmation must use a word for the specific action; "do everything" names no action.
ACTION_WORDS = {
    "email_send": ("send",), "email_reply": ("reply",), "email_forward": ("forward",),
    "spend": ("spend", "pay", "buy", "purchase"), "paid_api": ("spend", "pay", "paid"),
    "merge": ("merge",), "deploy": ("deploy", "release", "publish"),
    "system_config": ("configure", "change", "set"), "secret_access": ("secret", "token", "key", "credential"),
    "privilege_change": ("grant", "revoke", "privilege", "permission"), "delete": ("delete", "remove"),
}
BROAD_PHRASES = ("everything", "all tasks", "whatever", "anything", "go till", "until complete",
                 "don't stop", "do not stop", "all of it", "as needed", "whatever is needed")


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
    used: int = 0          # reserved or performed uses
    spent: float = 0.0     # reserved or performed amount


def _finite_positive(x: object) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0


@dataclass
class ApprovalGate:
    approvals: dict[str, Approval] = field(default_factory=dict)
    completed: dict[str, Any] = field(default_factory=dict)          # request_id -> result
    in_flight: dict[str, tuple[str, float]] = field(default_factory=dict)   # request_id -> (approval id, amount)
    uncertain: dict[str, tuple[str, float]] = field(default_factory=dict)
    request_binding: dict[str, tuple[str, str]] = field(default_factory=dict)
    log: list[dict] = field(default_factory=list)
    clock: Callable[[], float] = time.time
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def _record(self, request_id, action, target, outcome, **extra):
        self.log.append({"request": request_id, "action": action, "target": target, "outcome": outcome, **extra})

    def grant(self, approval_id: str, action: str, target: str, *, source: str, wording: str,
              ttl_seconds: float = 3600, uses: int = 1, max_amount: float | None = None) -> Approval:
        if action not in CONSEQUENTIAL:
            raise ValueError("not a consequential action: " + action)
        if source not in TRUSTED_SOURCES:
            raise ApprovalDenied(f"approval from {source!r} is not the user's own instruction")
        if not isinstance(target, str) or not target.strip() or target.strip().lower() in {"*", "all", "any", "everything"}:
            raise ApprovalDenied("approval must name one exact target")
        text = (wording or "").strip().lower()
        if not text:
            raise ApprovalDenied("approval needs the user's explicit confirmation text")
        if any(p in text for p in BROAD_PHRASES):
            raise ApprovalDenied("a broad goal is not a scoped approval")
        if target.lower() not in text:
            raise ApprovalDenied("the confirmation must name the exact target")
        if not any(w in text for w in ACTION_WORDS[action]):
            raise ApprovalDenied(f"the confirmation must name the action ({action})")
        if action in SPENDING and not _finite_positive(max_amount):
            raise ApprovalDenied("spending approval needs a finite, positive maximum amount")
        if not isinstance(uses, int) or uses < 1:
            raise ValueError("uses must be a positive integer")
        if not _finite_positive(ttl_seconds):
            raise ValueError("ttl_seconds must be finite and positive")
        with self._lock:
            if approval_id in self.approvals:
                raise ApprovalDenied(f"approval id {approval_id} already exists")
            now = self.clock()
            a = Approval(approval_id, action, target, source, now, now + ttl_seconds, uses, max_amount, wording)
            self.approvals[approval_id] = a
            return a

    def _reserve(self, request_id: str, approval_id: str | None, action: str, target: str, amount: float) -> Approval:
        if action in SPENDING and not _finite_positive(amount):
            raise ApprovalDenied("a spend request must state a finite, positive amount")
        if action not in SPENDING and amount != 0:
            raise ApprovalDenied("only spending actions carry an amount")
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
        a.used += 1
        a.spent += amount
        self.in_flight[request_id] = (a.id, amount)
        return a

    def run(self, request_id: str, action: str, target: str, approval_id: str | None,
            perform: Callable[[], Any], *, amount: float = 0.0) -> Any:
        """Run `perform` once under approval. Retrying a completed request returns its first result."""
        if action not in CONSEQUENTIAL:
            raise ValueError("not a consequential action: " + action)
        with self._lock:
            bound = self.request_binding.get(request_id)
            if bound and bound != (action, target):
                self._record(request_id, action, target, "denied-escalation")
                raise ApprovalDenied(f"request {request_id} was for {bound[0]} on {bound[1]}; a retry cannot change it")
            if request_id in self.completed:
                self._record(request_id, action, target, "deduplicated")
                return self.completed[request_id]
            if request_id in self.in_flight:
                self._record(request_id, action, target, "denied-in-flight")
                raise ApprovalDenied(f"request {request_id} is already running")
            if request_id in self.uncertain:
                self._record(request_id, action, target, "denied-uncertain")
                raise ApprovalDenied(f"request {request_id} has an uncertain outcome; resolve it with a read-after-write check first")
            try:
                a = self._reserve(request_id, approval_id, action, target, amount)
            except ApprovalDenied as e:
                self._record(request_id, action, target, "denied", reason=str(e))
                raise
            self.request_binding[request_id] = (action, target)
            self._record(request_id, action, target, "reserved", approval=a.id, amount=amount)
        try:
            result = perform()
        except BaseException as e:
            with self._lock:
                self.uncertain[request_id] = self.in_flight.pop(request_id)
                self._record(request_id, action, target, "uncertain", error=type(e).__name__)
            raise
        with self._lock:
            self.in_flight.pop(request_id, None)
            self.completed[request_id] = result
            self._record(request_id, action, target, "performed", approval=a.id)
        return result

    def resolve(self, request_id: str, happened: bool, result: Any = None) -> None:
        """Record a read-after-write check of an uncertain request.

        happened=True: the effect is there; the request is completed and its reservation kept.
        happened=False: the effect is absent; the reservation is released so the same request may retry.
        """
        with self._lock:
            if request_id not in self.uncertain:
                raise KeyError(f"request {request_id} is not uncertain")
            approval_id, amount = self.uncertain.pop(request_id)
            action, target = self.request_binding[request_id]
            if happened:
                self.completed[request_id] = result
            else:
                a = self.approvals[approval_id]
                a.used -= 1
                a.spent -= amount
            self._record(request_id, action, target, "resolved", happened=happened)
