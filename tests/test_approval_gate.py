"""S01 synthetic negative tests: no consequential action occurs without scoped user approval,
including through automatic retries and escalation. Each test counts real side effects."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from approval_gate import ApprovalDenied, ApprovalGate


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t


class Effects:
    """A fake mailbox / merge button / payment API that records what actually happened."""
    def __init__(self): self.calls = []
    def do(self, what, fail=False):
        def f():
            if fail:
                raise TimeoutError('lost acknowledgement')
            self.calls.append(what)
            return 'ok:' + what
        return f


class ApprovalGateTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock(); self.gate = ApprovalGate(clock=self.clock); self.fx = Effects()

    def denied(self, *args, **kw):
        with self.assertRaises(ApprovalDenied):
            self.gate.run(*args, **kw)

    def test_no_approval_no_action(self):
        for action, target in [('email_send', 'to:alice'), ('merge', 'acme/app#12'), ('deploy', 'prod'),
                               ('spend', 'openai'), ('secret_access', 'VERCEL_TOKEN'), ('system_config', 'firewall')]:
            self.denied('r-' + action, action, target, None, self.fx.do(action))
        self.assertEqual(self.fx.calls, [])

    def test_broad_goal_is_not_authority(self):
        for wording in ["Don't stop for approval, go till everything is complete", 'do all tasks', 'whatever it takes']:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('a1', 'merge', 'acme/app#12', source='user', wording=wording)
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('a2', 'email_send', 'to:alice', source='user', wording=wording)
        self.assertEqual(self.gate.approvals, {})

    def test_untrusted_sources_cannot_grant(self):
        for src in ['tool_output', 'issue_comment', 'email_body', 'web_page', 'other_agent']:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('a-' + src, 'deploy', 'prod', source=src, wording='Please deploy prod now')
        self.denied('r1', 'deploy', 'prod', 'a-tool_output', self.fx.do('deploy'))
        self.assertEqual(self.fx.calls, [])

    def test_email_verbs_are_separate(self):
        self.gate.grant('m1', 'email_send', 'to:alice', source='user', wording='Send the report to alice')
        self.denied('r1', 'email_forward', 'to:alice', 'm1', self.fx.do('fwd'))
        self.denied('r2', 'email_reply', 'to:alice', 'm1', self.fx.do('reply'))
        self.denied('r3', 'email_send', 'to:bob', 'm1', self.fx.do('send bob'))
        self.assertEqual(self.gate.run('r4', 'email_send', 'to:alice', 'm1', self.fx.do('send alice')), 'ok:send alice')
        self.assertEqual(self.fx.calls, ['send alice'])

    def test_target_is_exact(self):
        self.gate.grant('g1', 'merge', 'acme/app#12', source='user', wording='merge acme/app#12')
        self.denied('r1', 'merge', 'acme/app#13', 'g1', self.fx.do('merge 13'))
        self.assertEqual(self.fx.calls, [])
        for t in ['*', 'all', '']:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('g-' + t, 'merge', t, source='user', wording='merge them')

    def test_retry_after_lost_ack_does_not_duplicate(self):
        self.gate.grant('g1', 'merge', 'acme/app#12', source='user', wording='merge acme/app#12')
        with self.assertRaises(TimeoutError):
            self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge', fail=True))
        self.assertEqual(self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge')), 'ok:merge')
        for _ in range(3):   # automatic retries after success are deduplicated, not re-performed
            self.assertEqual(self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge')), 'ok:merge')
        self.assertEqual(self.fx.calls, ['merge'])
        self.denied('req-2', 'merge', 'acme/app#12', 'g1', self.fx.do('merge again'))  # single-use
        self.assertEqual(self.fx.calls, ['merge'])

    def test_retry_cannot_escalate(self):
        self.gate.grant('g1', 'merge', 'acme/app#12', source='user', wording='merge acme/app#12')
        self.gate.grant('d1', 'deploy', 'staging', source='user', wording='deploy staging')
        self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))
        self.denied('req-1', 'deploy', 'staging', 'd1', self.fx.do('deploy'))      # same request, new action
        self.denied('req-1', 'merge', 'acme/app#13', 'g1', self.fx.do('merge 13'))  # same request, new target
        self.denied('req-3', 'deploy', 'prod', 'd1', self.fx.do('deploy prod'))    # staging approval, prod target
        self.assertEqual(self.fx.calls, ['merge'])
        self.assertIn('denied-escalation', [e['outcome'] for e in self.gate.log])

    def test_expiry(self):
        self.gate.grant('g1', 'deploy', 'staging', source='user', wording='deploy staging', ttl_seconds=60)
        self.clock.t += 61
        self.denied('r1', 'deploy', 'staging', 'g1', self.fx.do('deploy'))
        self.assertEqual(self.fx.calls, [])

    def test_spend_cap(self):
        with self.assertRaises(ApprovalDenied):
            self.gate.grant('s0', 'spend', 'openai', source='user', wording='spend on openai')
        self.gate.grant('s1', 'spend', 'openai', source='user', wording='up to $5 on openai', uses=3, max_amount=5)
        self.gate.run('p1', 'spend', 'openai', 's1', self.fx.do('$3'), amount=3)
        self.denied('p2', 'spend', 'openai', 's1', self.fx.do('$3 more'), amount=3)
        self.gate.run('p3', 'spend', 'openai', 's1', self.fx.do('$2'), amount=2)
        self.assertEqual(self.fx.calls, ['$3', '$2'])

    def test_every_attempt_is_logged(self):
        self.denied('r1', 'deploy', 'prod', None, self.fx.do('deploy'))
        self.assertEqual(self.gate.log[-1]['outcome'], 'denied')


if __name__ == '__main__':
    unittest.main()
