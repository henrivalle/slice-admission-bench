"""Read ordered batches from a CSV workload trace."""

import csv
from itertools import groupby
from operator import itemgetter
from pathlib import Path

from . import Request


_COLUMNS = ("round", "bandwidth", "compute", "reward")


def read_trace(path: Path) -> list[tuple[int, tuple[Request, ...]]]:
    """Validate the trace before emitting output, preserving arrival order."""
    requests = []
    last_round = 0
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if sorted(reader.fieldnames or []) != sorted(_COLUMNS):
            raise ValueError(f"{path.name}: expected columns {','.join(_COLUMNS)}")
        for row in reader:
            location = f"{path.name}:{reader.line_num}"
            if None in row or None in row.values():
                raise ValueError(f"{location}: expected four fields")
            try:
                round_number, bandwidth, compute, reward = (int(row[key]) for key in _COLUMNS)
                request = Request(bandwidth, compute, reward)
            except ValueError as error:
                raise ValueError(f"{location}: round, bandwidth, compute, and reward must be positive integers") from error
            if round_number <= 0:
                raise ValueError(f"{location}: round must be a positive integer")
            if round_number < last_round:
                raise ValueError(f"{location}: rounds must be in nondecreasing order")
            requests.append((round_number, request))
            last_round = round_number
    if not requests:
        raise ValueError(f"{path.name}: expected at least one request")
    return [
        (round_number, tuple(request for _, request in rows))
        for round_number, rows in groupby(requests, key=itemgetter(0))
    ]
