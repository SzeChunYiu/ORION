"""Command line entry point: evaluate SCHEMA_V1 instances.

    python -m typed_merge_evaluator INSTANCE.json [INSTANCE.json ...]

Exit codes are distinct so that "could not check" is never reported as "checked
and fine":

    0  every instance evaluated and every declared expectation held
    1  an instance evaluated but a declared expectation did not hold
    2  an instance could not be read, parsed or validated
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Sequence

from .analysis import Report, check_expectations
from .model import Problem, SchemaError

EXIT_OK = 0
EXIT_EXPECTATION_FAILED = 1
EXIT_CANNOT_CHECK = 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="typed_merge_evaluator")
    parser.add_argument("instances", nargs="+", help="SCHEMA_V1 JSON documents")
    parser.add_argument("--json", action="store_true", help="emit full JSON reports")
    args = parser.parse_args(argv)

    failures: List[str] = []
    reports = []
    for path in args.instances:
        try:
            problem = Problem.load(path)
        except (OSError, ValueError, SchemaError) as exc:
            print(f"CANNOT_CHECK {path}: {exc}", file=sys.stderr)
            return EXIT_CANNOT_CHECK
        report = Report(problem)
        reports.append(report.as_dict())
        mismatches = check_expectations(problem, report)
        status = "PASS" if not mismatches else "FAIL"
        flagged = sorted(t for t in (problem.targets or ()) if report.first_mixing(t))
        print(f"{status} {problem.id}: first_mixing={flagged or 'none'}")
        for line in mismatches:
            print(f"     {line}")
            failures.append(f"{problem.id}: {line}")

    if args.json:
        print(json.dumps(reports, indent=2, sort_keys=True))
    return EXIT_EXPECTATION_FAILED if failures else EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
