"""S03 canaries: seeded secrets, PII, machine identity, transcripts and private repo links
must fail the public-safety scan, without echoing the full value; clean text must pass."""
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import public_safety_scan as pss

ALLOW = {'public_repos': {'example-org/public-repo'}, 'emails': set(), 'paths': set()}
# Canary values are assembled at runtime so this file itself stays clean.
GH = 'ghp_' + 'A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8'
AWS = 'AKIA' + 'ABCDEFGHIJKLMNOP'
ANT = 'sk-ant-' + 'api03-' + 'x' * 30
KEY = '-----BEGIN ' + 'RSA PRIVATE KEY-----'
GHURL = 'https://' + 'github.com/'   # split so fixture links are not real links in this file


class PublicSafetyScanTests(unittest.TestCase):
    def setUp(self):
        self._vis = pss.repo_visibility
        pss.repo_visibility = lambda r, offline: {'acme/secret-tool': 'not-public', 'acme/unknown': 'unknown'}.get(r, 'public')

    def tearDown(self):
        pss.repo_visibility = self._vis

    def scan(self, text, notes=None):
        return pss.scan_text(text, 'canary.md', ALLOW, offline=False, notes=notes)

    def assertFlags(self, text, rule):
        found = self.scan(text)
        self.assertTrue(any(rule in f for f in found), f'{rule} not flagged in {found}')
        return found

    def test_secret_canaries_fail_without_leaking_value(self):
        for value, rule in [(GH, 'github-token'), (AWS, 'aws-access-key'), (ANT, 'anthropic-key'), (KEY, 'private-key'),
                            ('api_key = "' + 'Zx9' * 5 + '"', 'assigned-secret')]:
            found = self.assertFlags('token here: ' + value, rule)
            self.assertFalse(any(value in f for f in found), 'full secret value echoed in finding')

    def test_personal_data_canaries(self):
        self.assertFlags('contact ' + 'jane.citizen' + '@gmail.com', 'email-address')
        self.assertFlags('call ' + '04' + '12 345 678 today', 'au-phone')
        self.assertFlags('ring +' + '61 2 9876 5432', 'au-phone')

    def test_machine_identity_canaries(self):
        self.assertFlags('see C:\\Users\\' + 'josh\\Documents\\notes.txt', 'windows-user-path')
        self.assertFlags('log at /home/' + 'josh/projects/x', 'unix-home-path')
        self.assertFlags('share \\\\' + 'DESKTOP-7F3\\share', 'unc-host-path')

    def test_transcript_excerpt_canary(self):
        self.assertFlags('You said: please merge my PR', 'transcript-turn')
        self.assertFlags('**ChatGPT said:** done, all tests pass', 'transcript-turn')

    def test_private_repo_link_fails_and_unknown_follows_mode(self):
        self.assertFlags('see ' + GHURL + 'acme/secret-tool/pull/3', 'private-repo-link')
        notes = []
        self.assertEqual(self.scan('see ' + GHURL + 'acme/unknown', notes), [])
        self.assertTrue(any('unverified-repo-link' in n for n in notes))
        self.assertTrue(any('unverified-repo-link' in f for f in self.scan('see ' + GHURL + 'acme/unknown')),
                        'unknown visibility must fail in strict (CI) mode')

    def test_clean_public_text_passes(self):
        clean = ('Use noreply@anthropic.com and git@github.com:example-org/public-repo.git.\n'
                 'Runner path /home/runner/work and placeholder C:\\Users\\<you>\\repo.\n'
                 'Version 0.4.12345678 and ' + GHURL + 'example-org/public-repo/issues/1.\n'
                 'The user said the build was green.')
        self.assertEqual(self.scan(clean), [])

    def test_inline_allow_marker(self):
        self.assertEqual(self.scan('fixture ' + AWS + '  <!-- public-safety: allow -->'), [])

    def test_repository_is_clean_offline(self):
        pss.repo_visibility = self._vis
        out = io.StringIO()
        with redirect_stdout(out):
            code = pss.main(['--offline'])
        self.assertEqual(code, 0, out.getvalue())


if __name__ == '__main__':
    unittest.main()
