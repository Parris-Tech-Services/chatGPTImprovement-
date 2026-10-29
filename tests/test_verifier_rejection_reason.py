"""Regression coverage: an unrelated crash is not a successful negative proof."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_agent_stack_ci import run


class RejectionReasonTests(unittest.TestCase):
    def test_expected_reason_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            result = run([sys.executable, "-c",
                          "import sys; print('FINAL GATE: NOT VERIFIED');sys.exit(1)"],
                         Path(folder), expect=1, expected_text="NOT VERIFIED",
                         label="deliberate rejection")
            self.assertEqual(result["exit_code"], 1)

    def test_generic_failure_does_not_count_as_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError, "wrong reason"):
                run([sys.executable, "-c",
                     "import sys; print('traceback unrelated');sys.exit(1)"],
                    Path(folder), expect=1, expected_text="NOT VERIFIED")

    def test_wrong_exit_code_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError, "unexpected exit code"):
                run([sys.executable, "-c", "print('NOT VERIFIED')"],
                    Path(folder), expect=1, expected_text="NOT VERIFIED")

    def test_positive_process_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(run([sys.executable, "-c", "print('good')"],
                                 Path(folder), expect=0)["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
