from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .driver import SelfDrivingDriver
from .registry import load_registered_checks
from .sources import DirectoryAnswerSource
from .store import LedgerStore


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orion.kernel",
        description="Run bounded self-driving ORION rounds against a durable ledger.",
    )
    parser.add_argument(
        "command", choices=("run", "status", "verify", "report"), help="what to do"
    )
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(".orion-state"),
        help="directory holding the append-only ledger",
    )
    parser.add_argument(
        "--answers",
        type=Path,
        default=Path("research/development/mechanic-answer-loop/answers"),
        help="per-lane JSONL inbox of candidate answers",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="root for resolving 'orion:' evidence references",
    )
    parser.add_argument(
        "--evidence-root",
        action="append",
        default=[],
        metavar="SCHEME=PATH",
        help="register an additional evidence scheme, e.g. rakl=/path/to/RAKL",
    )
    parser.add_argument("--rounds", type=int, default=4, help="maximum rounds this run")
    parser.add_argument(
        "--selection-limit",
        type=int,
        default=16,
        help="how many open questions one round may select",
    )
    parser.add_argument(
        "--no-checks",
        action="store_true",
        help="run without the registered discriminating checks (no verified closures possible)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    store = LedgerStore(args.state)

    if args.command == "report":
        from .report import build_report

        report = build_report(store)
        print(json.dumps(report, indent=2))
        return 0 if report["ledger_intact"] else 1

    if args.command == "verify":
        violations = store.verify()
        print(
            json.dumps(
                {
                    "ledger": str(store.path),
                    "intact": not violations,
                    "violations": list(violations),
                },
                indent=2,
            )
        )
        return 0 if not violations else 1

    evidence_roots = {"orion": args.repo_root}
    for entry in args.evidence_root:
        scheme, separator, path = entry.partition("=")
        if not separator or not scheme.strip() or not path.strip():
            raise SystemExit(f"--evidence-root expects SCHEME=PATH, got {entry!r}")
        evidence_roots[scheme.strip()] = Path(path.strip())

    checks = {} if args.no_checks else dict(load_registered_checks())
    driver = SelfDrivingDriver(
        store=store,
        source=DirectoryAnswerSource(root=args.answers),
        evidence_roots=evidence_roots,
        checks=checks,
        selection_limit=args.selection_limit,
    )

    if args.command == "status":
        cells = driver.cells()
        from orion.mechanics.program import observe_mechanics_program

        metrics = observe_mechanics_program(cells)
        print(
            json.dumps(
                {
                    "completed_rounds": store.completed_round_count(),
                    "mechanics": metrics.mechanic_count,
                    "ready": metrics.ready_mechanic_count,
                    "open_questions": metrics.open_question_count,
                    "ledger_intact": not store.verify(),
                },
                indent=2,
            )
        )
        return 0

    report = driver.run(max_rounds=args.rounds)
    print(
        json.dumps(
            {
                "stop_reason": report.stop_reason,
                "rounds_executed": len(report.rounds),
                "open_at_start": report.open_at_start,
                "open_at_end": report.open_at_end,
                "verified_closures": report.verified_closures,
                "active_guards": [
                    {
                        "guard_id": item.guard_id,
                        "effect": item.effect.value,
                        "argument": item.argument,
                        "authority": item.authority.value,
                    }
                    for item in report.guards
                ],
                "false_progress": [
                    reason
                    for outcome in report.rounds
                    for reason in outcome.false_progress_reasons
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    raise SystemExit(main())
