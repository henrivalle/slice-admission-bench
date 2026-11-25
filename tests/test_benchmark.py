import csv
from itertools import combinations
from pathlib import Path
import random
import subprocess
import sys
import unittest

from slice_admission import Budget, Request, select_density, select_fifo, select_optimal


class PolicyTests(unittest.TestCase):
    def test_fractional_and_nonpositive_resources_are_rejected(self):
        for constructor, args in ((Budget, (1, 2.5)), (Request, (1, 0, 2)), (Request, (1, 2, True))):
            with self.subTest(constructor=constructor, args=args), self.assertRaises(ValueError):
                constructor(*args)

    def test_two_resources_can_change_the_best_selection(self):
        budget = Budget(bandwidth=5, compute=5)
        early = Request(bandwidth=4, compute=4, reward=10)
        radio_heavy = Request(bandwidth=4, compute=1, reward=6)
        compute_heavy = Request(bandwidth=1, compute=4, reward=6)
        batch = (early, radio_heavy, compute_heavy)

        self.assertEqual(select_fifo(batch, budget), (early,))
        self.assertEqual(select_optimal(batch, budget), (radio_heavy, compute_heavy))

    def test_density_accounts_for_the_scarcer_budget(self):
        radio_heavy = Request(4, 1, 6)
        compute_heavy = Request(1, 4, 6)
        batch = (radio_heavy, compute_heavy)
        self.assertEqual(select_density(batch, Budget(4, 10)), (compute_heavy,))
        self.assertEqual(select_density(batch, Budget(10, 4)), (radio_heavy,))

    def test_every_policy_obeys_both_limits(self):
        budget = Budget(5, 5)
        batch = (Request(6, 1, 80), Request(1, 6, 90), Request(1, 1, 2))
        for select in (select_fifo, select_density, select_optimal):
            with self.subTest(policy=select.__name__):
                self.assertEqual(select(batch, budget), batch[2:])
                self.assertEqual(select((), budget), ())

    def test_optimum_matches_exhaustive_search(self):
        rng = random.Random(7)
        for i in range(20):
            with self.subTest(scenario=i):
                budget = Budget(rng.randint(2, 9), rng.randint(2, 9))
                batch = tuple(Request(rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 15)) for _ in range(7))
                expected = 0
                for count in range(len(batch) + 1):
                    for subset in combinations(batch, count):
                        if sum(x.bandwidth for x in subset) <= budget.bandwidth and sum(x.compute for x in subset) <= budget.compute:
                            expected = max(expected, sum(x.reward for x in subset))
                result = select_optimal(batch, budget)
                self.assertEqual(sum(x.reward for x in result), expected)
                self.assertLessEqual(sum(x.bandwidth for x in result), budget.bandwidth)
                self.assertLessEqual(sum(x.compute for x in result), budget.compute)


class CommandLineTests(unittest.TestCase):
    def run_benchmark(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "slice_admission", *args],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        )

    def test_seed_reproduces_the_csv_and_all_policies(self):
        args = ("--seed", "42", "--rounds", "3", "--requests", "4", "--bandwidth", "8", "--compute", "6")
        first = self.run_benchmark(*args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, self.run_benchmark(*args).stdout)
        records = list(csv.DictReader(first.stdout.splitlines()))
        self.assertEqual(len(records), 9)
        for n in range(1, 4):
            rows = {row["policy"]: row for row in records if int(row["round"]) == n}
            self.assertEqual(set(rows), {"fifo", "density", "optimal"})
            for row in rows.values():
                self.assertLessEqual(int(row["bandwidth_used"]), 8)
                self.assertLessEqual(int(row["compute_used"]), 6)
                self.assertLessEqual(int(row["reward"]), int(rows["optimal"]["reward"]))

    def test_single_policy_limits_output_to_requested_policy(self):
        result = self.run_benchmark("--rounds", "2", "--policy", "fifo")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = list(csv.DictReader(result.stdout.splitlines()))
        self.assertEqual(len(records), 2)
        self.assertEqual([row["policy"] for row in records], ["fifo", "fifo"])

    def test_invalid_policy_reports_usage_error(self):
        bad = self.run_benchmark("--policy", "unknown")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("invalid choice", bad.stderr)

    def test_invalid_budget_reports_usage_error(self):
        bad = self.run_benchmark("--bandwidth", "0")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("positive integer", bad.stderr)


if __name__ == "__main__":
    unittest.main()
