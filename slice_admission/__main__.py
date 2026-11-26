import argparse
import csv
import random
import sys
from pathlib import Path

from . import Budget, Request, select_density, select_fifo, select_optimal
from .trace import read_trace


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def synthetic_batches(rounds: int, requests: int, seed: int):
    rng = random.Random(seed)
    for round_number in range(1, rounds + 1):
        batch = tuple(Request(rng.randint(1, 8), rng.randint(1, 8), rng.randint(1, 12)) for _ in range(requests))
        yield round_number, batch


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare admission policies on synthetic requests or a workload trace.")
    parser.add_argument("--rounds", type=positive_int, help="synthetic rounds (default: 10)")
    parser.add_argument("--requests", type=positive_int, help="synthetic requests per round (default: 12)")
    parser.add_argument("--bandwidth", type=positive_int, default=16, help="integer bandwidth budget")
    parser.add_argument("--compute", type=positive_int, default=16, help="integer compute budget")
    parser.add_argument("--seed", type=int, help="synthetic workload seed (default: 42)")
    parser.add_argument("--trace", type=Path, help="CSV with round,bandwidth,compute,reward columns")
    parser.add_argument(
        "--policy",
        choices=("fifo", "density", "optimal"),
        help="run only one admission policy",
    )
    args = parser.parse_args()

    if args.trace is not None:
        if any(value is not None for value in (args.rounds, args.requests, args.seed)):
            parser.error("cannot combine --trace with --rounds, --requests, or --seed")
        try:
            batches = read_trace(args.trace)
        except (OSError, ValueError, csv.Error) as error:
            parser.error(str(error))
    else:
        batches = synthetic_batches(args.rounds or 10, args.requests or 12, 42 if args.seed is None else args.seed)
    budget = Budget(args.bandwidth, args.compute)
    policies = (("fifo", select_fifo), ("density", select_density), ("optimal", select_optimal))
    if args.policy is not None:
        policies = tuple((name, policy) for name, policy in policies if name == args.policy)

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("round", "policy", "requests", "accepted", "reward", "bandwidth_used", "compute_used"))

    for round_number, batch in batches:
        for name, policy in policies:
            selected = policy(batch, budget)
            writer.writerow((
                round_number, name, len(batch), len(selected),
                sum(request.reward for request in selected),
                sum(request.bandwidth for request in selected),
                sum(request.compute for request in selected),
            ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
