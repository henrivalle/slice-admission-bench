import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TraceCliTests(unittest.TestCase):
    def run_trace(self, contents, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.csv"
            path.write_text(contents, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-m", "slice_admission", "--trace", str(path), *options],
                text=True,
                capture_output=True,
            )

    def test_replays_batch_order_and_keeps_report_format(self):
        result = self.run_trace(
            "round,bandwidth,compute,reward\n3,3,2,4\n3,1,2,9\n9,1,1,2\n",
            "--bandwidth", "3", "--compute", "2",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {(row["round"], row["policy"]): row for row in csv.DictReader(result.stdout.splitlines())}
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows["3", "fifo"]["reward"], "4")
        self.assertEqual(rows["3", "optimal"]["reward"], "9")
        self.assertEqual(rows["9", "fifo"]["reward"], "2")

    def test_rejects_round_reordering_without_partial_output(self):
        result = self.run_trace("round,bandwidth,compute,reward\n2,1,1,2\n1,2,1,3\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rounds must be in nondecreasing order", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_rejects_incomplete_and_empty_traces(self):
        result = self.run_trace("round,bandwidth,compute,reward\n1,1,2\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected four fields", result.stderr)
        result = self.run_trace("round,bandwidth,compute,reward\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one request", result.stderr)

    def test_refuses_to_ignore_synthetic_options(self):
        result = self.run_trace("round,bandwidth,compute,reward\n1,1,1,2\n", "--requests", "5")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot combine --trace", result.stderr)


if __name__ == "__main__":
    unittest.main()
