"""S01 synthetic negative tests: no consequential action occurs without scoped user approval,
including through automatic retries, uncertain outcomes, overlapping calls and escalation.
Each test counts real side effects."""
import math
import sys
import threading
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
    def __init__(self): self.calls = []; self.lock = threading.Lock()
    def do(self, what, fail_before=False, fail_after=False, wait=None):
        def f():
            if fail_before:
                raise TimeoutError('connection dropped before the request was sent')
            if wait:
                wait()
            with self.lock:
                self.calls.append(what)
            if fail_after:
                raise TimeoutError('lost acknowledgement after the effect happened')
            return 'ok:' + what
        return f


class ApprovalGateTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock(); self.gate = ApprovalGate(clock=self.clock); self.fx = Effects()

    def denied(self, *args, **kw):
        with self.assertRaises(ApprovalDenied):
            self.gate.run(*args, **kw)

    def grant_merge(self, aid='g1', target='acme/app#12'):
        return self.gate.grant(aid, 'merge', target, source='user', wording=f'Yes, merge {target}')

    def test_no_approval_no_action(self):
        for action, target in [('email_send', 'alice@example.com'), ('merge', 'acme/app#12'), ('deploy', 'prod'),
                               ('secret_access', 'VERCEL_TOKEN'), ('system_config', 'firewall')]:
            self.denied('r-' + action, action, target, None, self.fx.do(action))
        self.denied('r-spend', 'spend', 'openai', None, self.fx.do('spend'), amount=1)
        self.assertEqual(self.fx.calls, [])

    def test_broad_or_unstructured_wording_is_not_consent(self):
        cases = [
            ('merge', 'acme/app#12', "Don't stop for approval, go till everything is complete"),
            ('deploy', 'prod', 'Do everything needed for prod'),          # names the target, still broad
            ('deploy', 'prod', 'prod looks fine'),                        # names no action
            ('email_send', 'alice@example.com', ''),                      # empty
            ('email_send', 'alice@example.com', 'send it'),               # names no target
            ('merge', 'acme/app#12', 'whatever is needed for acme/app#12, merge'),
        ]
        for i, (action, target, wording) in enumerate(cases):
            with self.assertRaises(ApprovalDenied, msg=wording):
                self.gate.grant(f'a{i}', action, target, source='user', wording=wording)
        self.assertEqual(self.gate.approvals, {})

    def test_untrusted_sources_cannot_grant(self):
        for src in ['tool_output', 'issue_comment', 'email_body', 'web_page', 'other_agent']:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('a-' + src, 'deploy', 'prod', source=src, wording='Please deploy prod now')
        self.denied('r1', 'deploy', 'prod', 'a-tool_output', self.fx.do('deploy'))
        self.assertEqual(self.fx.calls, [])

    def test_email_verbs_are_separate(self):
        self.gate.grant('m1', 'email_send', 'alice@example.com', source='user', wording='Send the report to alice@example.com')
        self.denied('r1', 'email_forward', 'alice@example.com', 'm1', self.fx.do('fwd'))
        self.denied('r2', 'email_reply', 'alice@example.com', 'm1', self.fx.do('reply'))
        self.denied('r3', 'email_send', 'bob@example.com', 'm1', self.fx.do('send bob'))
        self.assertEqual(self.gate.run('r4', 'email_send', 'alice@example.com', 'm1', self.fx.do('send alice')), 'ok:send alice')
        self.assertEqual(self.fx.calls, ['send alice'])

    def test_target_is_exact(self):
        self.grant_merge()
        self.denied('r1', 'merge', 'acme/app#13', 'g1', self.fx.do('merge 13'))
        self.assertEqual(self.fx.calls, [])
        for t in ['*', 'all', '', 'everything']:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant('g-' + t, 'merge', t, source='user', wording=f'merge {t}')

    def test_effect_then_lost_ack_is_not_repeated(self):
        self.grant_merge()
        with self.assertRaises(TimeoutError):
            self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge', fail_after=True))
        self.assertEqual(self.fx.calls, ['merge'])
        # Blind retries are refused while the outcome is uncertain.
        for _ in range(3):
            self.denied('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))
        self.denied('req-2', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))   # the approval stays reserved
        self.gate.resolve('req-1', happened=True, result='ok:merge')               # read-after-write: it merged
        self.assertEqual(self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge')), 'ok:merge')
        self.assertEqual(self.fx.calls, ['merge'])

    def test_failure_before_effect_can_retry_after_check(self):
        self.grant_merge()
        with self.assertRaises(TimeoutError):
            self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge', fail_before=True))
        self.denied('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))
        self.gate.resolve('req-1', happened=False)                                 # read-after-write: nothing merged
        self.assertEqual(self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge')), 'ok:merge')
        self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))  # deduplicated
        self.denied('req-2', 'merge', 'acme/app#12', 'g1', self.fx.do('merge again'))  # single-use
        self.assertEqual(self.fx.calls, ['merge'])

    def test_overlapping_callers_cannot_share_a_single_use_approval(self):
        self.grant_merge()
        inside, release = threading.Event(), threading.Event()
        outcomes = []
        def first():
            outcomes.append(self.gate.run('req-A', 'merge', 'acme/app#12', 'g1',
                                          self.fx.do('merge A', wait=lambda: (inside.set(), release.wait(5)))))
        t = threading.Thread(target=first); t.start()
        self.assertTrue(inside.wait(5))
        self.denied('req-B', 'merge', 'acme/app#12', 'g1', self.fx.do('merge B'))   # approval reserved by A
        self.denied('req-A', 'merge', 'acme/app#12', 'g1', self.fx.do('merge A2'))  # same request already running
        release.set(); t.join(5)
        self.assertEqual(self.fx.calls, ['merge A'])
        self.assertEqual(outcomes, ['ok:merge A'])

    def test_retry_cannot_escalate(self):
        self.grant_merge()
        self.gate.grant('d1', 'deploy', 'staging', source='user', wording='deploy staging')
        self.gate.run('req-1', 'merge', 'acme/app#12', 'g1', self.fx.do('merge'))
        self.denied('req-1', 'deploy', 'staging', 'd1', self.fx.do('deploy'))
        self.denied('req-1', 'merge', 'acme/app#13', 'g1', self.fx.do('merge 13'))
        self.denied('req-3', 'deploy', 'prod', 'd1', self.fx.do('deploy prod'))
        self.assertEqual(self.fx.calls, ['merge'])
        self.assertIn('denied-escalation', [e['outcome'] for e in self.gate.log])

    def test_expiry(self):
        self.gate.grant('g1', 'deploy', 'staging', source='user', wording='deploy staging', ttl_seconds=60)
        self.clock.t += 61
        self.denied('r1', 'deploy', 'staging', 'g1', self.fx.do('deploy'))
        self.assertEqual(self.fx.calls, [])

    def test_spend_cap_and_invalid_amounts(self):
        for cap in [None, 0, -5, math.nan, math.inf]:
            with self.assertRaises(ApprovalDenied):
                self.gate.grant(f's-{cap}', 'spend', 'openai', source='user', wording='spend up to $5 on openai', max_amount=cap)
        self.gate.grant('s1', 'spend', 'openai', source='user', wording='spend up to $5 on openai', uses=5, max_amount=5)
        for bad in [-5, 0, math.nan, math.inf, True]:
            self.denied(f'bad-{bad}', 'spend', 'openai', 's1', self.fx.do(f'${bad}'), amount=bad)
        self.gate.run('p1', 'spend', 'openai', 's1', self.fx.do('$3'), amount=3)
        self.denied('p2', 'spend', 'openai', 's1', self.fx.do('$3 more'), amount=3)
        self.gate.run('p3', 'spend', 'openai', 's1', self.fx.do('$2'), amount=2)
        self.assertEqual(self.fx.calls, ['$3', '$2'])
        self.assertEqual(self.gate.approvals['s1'].spent, 5)

    def test_every_attempt_is_logged_including_failures(self):
        self.denied('r1', 'deploy', 'prod', None, self.fx.do('deploy'))
        self.grant_merge()
        with self.assertRaises(TimeoutError):
            self.gate.run('r2', 'merge', 'acme/app#12', 'g1', self.fx.do('merge', fail_after=True))
        self.gate.resolve('r2', happened=True)
        outcomes = [(e['request'], e['outcome']) for e in self.gate.log]
        self.assertEqual(outcomes, [('r1', 'denied'), ('r2', 'reserved'), ('r2', 'uncertain'), ('r2', 'resolved')])


if __name__ == '__main__':
    unittest.main()
