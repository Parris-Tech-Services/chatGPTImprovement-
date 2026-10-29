"""S02 canary tests: seeded signing keys leaked raw, as hex, as base64 or as a fragment into an
output must be detected; loose permissions and git-tracked keys fail; clean outputs pass; and a
run that finds no key at all must not pass silently."""
import base64
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import key_leak_canary as klc

RAW = bytes(range(7, 39))                                  # a fake 32-byte ed25519 seed
PEM = ('-----BEGIN ' + 'PRIVATE KEY-----\n' + base64.b64encode(RAW * 2).decode() + '\n-----END ' + 'PRIVATE KEY-----\n')


class KeyLeakCanaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        self.keys = self.d / 'keys'; self.keys.mkdir()
        self.out = self.d / 'out'; self.out.mkdir()
        (self.keys / 'signing.key').write_bytes(RAW); os.chmod(self.keys / 'signing.key', 0o600)
        (self.keys / 'witness.pem').write_text(PEM); os.chmod(self.keys / 'witness.pem', 0o600)
        (self.keys / 'receipts.jsonl').write_text('{"public": true}\n')

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, git=None):
        return klc.check([self.keys], [self.out], git)

    def test_finds_named_and_pem_keys(self):
        (self.keys / 'blob.bin').write_text(PEM); os.chmod(self.keys / 'blob.bin', 0o600)
        names = {p.name for p in klc.find_keys([self.keys])}
        self.assertEqual(names, {'signing.key', 'witness.pem', 'blob.bin'})

    def test_clean_outputs_pass(self):
        (self.out / 'verification-proof.json').write_text('{"ledger_signature_chain_verified": true, "public_key_fingerprint": "ab12"}')
        self.assertEqual(self.run_check(), ([], 2))

    def test_leaks_in_any_encoding_are_caught(self):
        for name, leak in [('raw.log', PEM), ('hex.json', '{"seed":"' + RAW.hex() + '"}'),
                           ('b64.txt', 'key=' + base64.b64encode(RAW).decode()),
                           ('frag.log', 'debug ' + RAW.hex()[10:40] + ' end')]:
            for f in self.out.iterdir(): f.unlink()
            (self.out / name).write_text(leak)
            findings, _ = self.run_check()
            self.assertTrue(any('appears in output ' + name in f for f in findings), (name, findings))
            self.assertFalse(any(RAW.hex()[10:40] in f for f in findings), 'finding must not echo key material')

    def test_loose_permissions_fail(self):
        os.chmod(self.keys / 'signing.key', 0o644)
        findings, _ = self.run_check()
        self.assertTrue(any('signing.key: permissions' in f for f in findings), findings)

    def test_git_tracked_key_fails(self):
        subprocess.run(['git', 'init', '-q', str(self.d)], check=True)
        subprocess.run(['git', '-C', str(self.d), 'add', 'keys/signing.key'], check=True)
        findings, _ = self.run_check(git=self.d)
        self.assertTrue(any('signing.key: tracked by git' in f for f in findings), findings)

    def test_no_keys_found_does_not_pass(self):
        empty = self.d / 'empty'; empty.mkdir()
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = klc.main(['--key-root', str(empty), '--output', str(self.out)])
        self.assertEqual(code, 2, buf.getvalue())

    def test_low_entropy_material_is_not_a_false_alarm(self):
        (self.keys / 'pad.key').write_bytes(b'A' * 64); os.chmod(self.keys / 'pad.key', 0o600)
        (self.out / 'log.txt').write_text('A' * 200)
        self.assertEqual(self.run_check()[0], [])


if __name__ == '__main__':
    unittest.main()
