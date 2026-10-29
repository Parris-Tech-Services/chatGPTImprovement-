"""S01 trusted-source action authorization gate.

NOT a ChatGPT host hook or an approval verifier. The caller MUST supply a
trusted approval resolver implemented outside the agent's influence. Never
accept approval claims merely because an LLM formatted JSON says 'approved'.

This module is deliberately dependency-free and never performs any network,
mail, deployment or repository operation itself.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
SENSITIVE_ACTIONS = frozenset({
    "email_send", "email_reply", "email_forward", "repo_push", "repo_merge",
    "deploy", "spend", "system_change", "secret_access", "publish", "delete",
})
MAIL_ACTIONS = frozenset({"email_send", "email_reply", "email_forward"})

class AuthorizationDenied(PermissionError):
    """The requested external action was not permitted or not independently proven."""

@dataclass(frozen=True)
class Action:
    task_id: str
    kind: str
    target: str
    payload_digest: str | None
    request_id: str

@dataclass(frozen=True)
class Authority:
    """Untrusted descriptive metadata until an independent resolver validates it."""
    approval_id: str
    task_id: str
    action_kind: str
    target: str
    payload_digest: str | None
    request_id: str
    expires_utc: datetime
    source: str
    issuer: str
    explicit_send_permission: bool = False

def _nonblank(x: object) -> bool:
    return isinstance(x, str) and bool(x.strip())

def _is_sha256_hex(s: object) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)

def _valid_action(action: Action) -> bool:
    return (
        isinstance(action, Action)
        and isinstance(action.kind, str) and action.kind in SENSITIVE_ACTIONS
        and all(_nonblank(x) for x in (action.task_id, action.target, action.request_id))
        and (
            (action.kind in MAIL_ACTIONS and _is_sha256_hex(action.payload_digest))
            or (action.kind not in MAIL_ACTIONS and (
                action.payload_digest is None or _is_sha256_hex(action.payload_digest)
            ))
        )
    )

def _matches(action: Action, authority: Authority, now: datetime) -> bool:
    if not isinstance(authority, Authority):
        return False
    if not (all(_nonblank(x) for x in (authority.approval_id, authority.source, authority.issuer))
            and authority.issuer == "user"
            and authority.source != "agent_assertion"):
        return False
    if (authority.task_id, authority.action_kind, authority.target, authority.payload_digest,
        authority.request_id) != (action.task_id, action.kind, action.target,
                                  action.payload_digest, action.request_id):
        return False
    if action.kind in MAIL_ACTIONS and not authority.explicit_send_permission:
        return False
    expiry = authority.expires_utc
    if not isinstance(expiry, datetime) or expiry.tzinfo is None or expiry.utcoffset() is None:
        return False
    return now < expiry

class ScopedActionGate(Generic[T]):
    """Single-process guarded execution, with consumptive deny-on-retry semantics.

    Resolver and verifier MUST be host-injected functions outside agent control.
    A token is consumed before invoking executor to avoid automatically replaying
    an uncertain outcome. Persistent/shared deduplication is NOT supplied.
    """
    def __init__(self, resolver: Callable[[str], Authority | None],
                 verifier: Callable[[Authority, Action], bool],
                 clock: Callable[[], datetime] | None = None):
        if not callable(resolver) or not callable(verifier):
            raise TypeError("trusted resolver and verifier callbacks are required")
        self._resolve = resolver
        self._verify = verifier
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._spent_request_ids: set[str] = set()
        self._spent_approvals: set[str] = set()

    def execute(self, action: Action, approval_id: str | None,
                executor: Callable[[], T]) -> T:
        if not _valid_action(action) or not _nonblank(approval_id) or not callable(executor):
            raise AuthorizationDenied("Invalid action or no explicit approval reference")
        if action.request_id in self._spent_request_ids or approval_id in self._spent_approvals:
            raise AuthorizationDenied("Repeated or ambiguous request; reconcile state before any retry")
        try:
            authority = self._resolve(approval_id)
        except Exception as exc:
            raise AuthorizationDenied("Cannot read trusted approval source") from exc
        now = self._clock()
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise AuthorizationDenied("No trusted time source")
        if authority is None or authority.approval_id != approval_id or not _matches(action, authority, now):
            raise AuthorizationDenied("Approval missing, expired, generic or outside action scope")
        try:
            independently_verified = self._verify(authority, action)
        except Exception as exc:
            raise AuthorizationDenied("Independent approval verification unavailable") from exc
        if independently_verified is not True:
            raise AuthorizationDenied("No independently verified approval")
        self._spent_request_ids.add(action.request_id)
        self._spent_approvals.add(approval_id)
        return executor()

    def is_consumed(self, request_id: str) -> bool:
        return request_id in self._spent_request_ids
