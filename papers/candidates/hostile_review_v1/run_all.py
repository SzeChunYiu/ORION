"""Run the additive hostile review and emit canonical JSON."""

from __future__ import annotations

import argparse
from pathlib import Path
import platform
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from papers.candidates.hostile_review_v1.common import Status, write_report
    from papers.candidates.hostile_review_v1 import p6_reopening, p7_refinement, p8_authority
else:
    from .common import Status, write_report
    from . import p6_reopening, p7_refinement, p8_authority


REVIEWED_SNAPSHOT = "999abd4899f3fed906ba024ae8ecd775a69b6560"


def collect_results():
    return [
        *p6_reopening.run_checks(),
        *p7_refinement.run_checks(),
        *p8_authority.run_checks(),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("artifacts") / "HOSTILE_REVIEW_RESULTS.json",
    )
    args = parser.parse_args()
    results = collect_results()
    digest = write_report(
        args.output,
        results,
        {
            "programme": "ORION candidate papers P6-P8",
            "reviewed_snapshot": REVIEWED_SNAPSHOT,
            "review_date": "2026-08-17",
            "python": platform.python_version(),
            "implementation": "standard-library additive hostile review",
            "claim_boundary": "Counterexamples target the reviewed formalization/checker scope; they do not establish paper novelty or empirical value.",
        },
    )
    for result in results:
        print(f"{result.paper} {result.finding}: {result.status.value} ({result.cases} cases)")
    print(f"report={args.output}")
    print(f"report_file_sha256={digest}")
    return 1 if any(result.status == Status.FAIL for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
