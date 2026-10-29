"""S01: synthetic negative controls prove blocked actions never invoke executor."""
import sys
import unittest
from dataclasses import replace
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from action_authority import Action, Authority, AuthorizationDenied, ScopedActionGate, SENSITIVE_ACTIONS, MAIL_ACTIONS

NOW = datetime(2026,10,29,8,0,tzinfo=timezone.utc)
SHA = "a"*64

def fixture(kind="repo_merge"):
    action=Action("TASK-01",kind,"repo/example#13",SHA if kind in MAIL_ACTIONS else None,"request-01")
    approval=Authority("approval-01",action.task_id,kind,action.target,action.payload_digest,action.request_id,
                       NOW+timedelta(minutes=5),"trusted_user_message","user",kind in MAIL_ACTIONS)
    return action,approval

def gate(approval=None,proof=True):
    return ScopedActionGate(lambda ref:approval if approval and approval.approval_id==ref else None,
                            lambda a,b:proof,clock=lambda:NOW)

class ApprovalTests(unittest.TestCase):
    def test_all_action_types_allow_exact_proven_request(self):
        for kind in sorted(SENSITIVE_ACTIONS):
            with self.subTest(kind=kind):
                a,p=fixture(kind);calls=[]
                self.assertEqual(gate(p).execute(a,p.approval_id,lambda:calls.append("done") or 7),7)
                self.assertEqual(calls,["done"])
    def test_all_action_types_without_authority_execute_nothing(self):
        for kind in sorted(SENSITIVE_ACTIONS):
            with self.subTest(kind=kind):
                a,p=fixture(kind);calls=[]
                with self.assertRaises(AuthorizationDenied):
                    gate().execute(a,p.approval_id,lambda:calls.append("unapproved"))
                self.assertEqual(calls,[])
    def test_no_reference(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(a,None,lambda:1)
    def test_generic_all_scope_denied(self):
        a,p=fixture("email_send")
        with self.assertRaises(AuthorizationDenied):gate(replace(p,action_kind="all")).execute(a,p.approval_id,lambda:1)
    def test_wrong_target(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,target="another"),p.approval_id,lambda:1)
    def test_wrong_task_id(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,task_id="another"),p.approval_id,lambda:1)
    def test_wrong_request_id(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,request_id="another"),p.approval_id,lambda:1)
    def test_wrong_mail_body_digest(self):
        a,p=fixture("email_send")
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,payload_digest="b"*64),p.approval_id,lambda:1)
    def test_mail_without_explicit_send_permission(self):
        a,p=fixture("email_send")
        with self.assertRaises(AuthorizationDenied):gate(replace(p,explicit_send_permission=False)).execute(a,p.approval_id,lambda:1)
    def test_truthy_non_boolean_mail_permission_must_fail(self):
        a,p=fixture("email_send")
        with self.assertRaises(AuthorizationDenied):
            gate(replace(p,explicit_send_permission="false")).execute(a,p.approval_id,lambda:1)

    def test_mail_without_body_digest(self):
        a,p=fixture("email_reply")
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,payload_digest=None),p.approval_id,lambda:1)
    def test_mail_invalid_digest(self):
        a,p=fixture("email_forward")
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,payload_digest="foo"),p.approval_id,lambda:1)
    def test_send_approval_cannot_forward(self):
        a,p=fixture("email_send")
        with self.assertRaises(AuthorizationDenied):gate(replace(p,action_kind="email_forward")).execute(a,p.approval_id,lambda:1)
    def test_expired_approval(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(replace(p,expires_utc=NOW)).execute(a,p.approval_id,lambda:1)
    def test_naive_expiry_time_rejected(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(replace(p,expires_utc=datetime(2028,1,1))).execute(a,p.approval_id,lambda:1)
    def test_agent_claim_is_not_approval(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(replace(p,source="agent_assertion")).execute(a,p.approval_id,lambda:1)
    def test_wrong_issuer(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(replace(p,issuer="assistant")).execute(a,p.approval_id,lambda:1)
    def test_independent_verifier_denial(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p,proof=False).execute(a,p.approval_id,lambda:1)
    def test_none_is_not_positive_proof(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p,proof=None).execute(a,p.approval_id,lambda:1)
    def test_approval_resolver_crash_fails_closed(self):
        a,p=fixture()
        def failing(_):raise RuntimeError("backend down")
        with self.assertRaises(AuthorizationDenied):
            ScopedActionGate(failing,lambda x,y:True,clock=lambda:NOW).execute(a,p.approval_id,lambda:1)
    def test_independent_verifier_crash_fails_closed(self):
        a,p=fixture()
        def failing(*_):raise RuntimeError("backend down")
        with self.assertRaises(AuthorizationDenied):
            ScopedActionGate(lambda _:p,failing,clock=lambda:NOW).execute(a,p.approval_id,lambda:1)
    def test_wildcard_target(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(replace(p,target="*")).execute(a,p.approval_id,lambda:1)
    def test_unknown_kind_denied(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,kind="unsafe_unknown"),p.approval_id,lambda:1)
    def test_unhashable_kind_denied_without_crash(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,kind=[]),p.approval_id,lambda:1)
    def test_replayed_request_denied(self):
        a,p=fixture();g=gate(p)
        self.assertEqual(g.execute(a,p.approval_id,lambda:11),11)
        with self.assertRaises(AuthorizationDenied):g.execute(a,p.approval_id,lambda:12)
    def test_ambiguous_exception_spends_authority_before_retry(self):
        a,p=fixture();g=gate(p);calls=[]
        def failing():calls.append("once");raise TimeoutError("unknown external state")
        with self.assertRaises(TimeoutError):g.execute(a,p.approval_id,failing)
        with self.assertRaises(AuthorizationDenied):g.execute(a,p.approval_id,lambda:calls.append("twice"))
        self.assertEqual(calls,["once"])
        self.assertTrue(g.is_consumed(a.request_id))
    def test_escalation_uses_new_approval(self):
        a,p=fixture("repo_merge")
        with self.assertRaises(AuthorizationDenied):gate(p).execute(replace(a,kind="delete"),p.approval_id,lambda:1)
    def test_spent_approval_cannot_authorise_new_request(self):
        a,p=fixture();g=gate(p);g.execute(a,p.approval_id,lambda:1)
        with self.assertRaises(AuthorizationDenied):g.execute(replace(a,request_id="other"),p.approval_id,lambda:2)
    def test_untrusted_reference_is_not_trusted_record(self):
        a,p=fixture()
        with self.assertRaises(AuthorizationDenied):
            ScopedActionGate(lambda _:None,lambda x,y:True,clock=lambda:NOW).execute(a,"approved",lambda:1)
    def test_authority_expiring_during_verification_does_not_execute(self):
        a,p=fixture()
        ticks=iter([NOW,NOW+timedelta(minutes=6)])
        g=ScopedActionGate(lambda _:p,lambda x,y:True,clock=lambda:next(ticks))
        calls=[]
        with self.assertRaises(AuthorizationDenied):
            g.execute(a,p.approval_id,lambda:calls.append("executed"))
        self.assertEqual(calls,[])

    def test_malformed_resolver_record_is_permission_denial(self):
        a,p=fixture()
        g=ScopedActionGate(lambda _:{"approval_id":p.approval_id},lambda x,y:True,clock=lambda:NOW)
        with self.assertRaises(AuthorizationDenied):
            g.execute(a,p.approval_id,lambda:1)

    def test_naive_clock_denied(self):
        a,p=fixture();g=ScopedActionGate(lambda _:p,lambda x,y:True,clock=lambda:datetime(2026,10,29))
        with self.assertRaises(AuthorizationDenied):g.execute(a,p.approval_id,lambda:1)
    def test_new_process_has_no_replay_store(self):
        # Deliberately exposed limitation; Q04 needs shared durable ledger.
        a,p=fixture()
        self.assertEqual(gate(p).execute(a,p.approval_id,lambda:1),1)
        self.assertEqual(gate(p).execute(a,p.approval_id,lambda:2),2)

if __name__=="__main__":unittest.main()
