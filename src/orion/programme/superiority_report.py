"""Reproducible status report over the P1-P10 superiority ledger.

Run it:

.. code-block:: console

   $ python -m orion.programme.superiority_report \\
       --ledger research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json

Exit codes, following the convention already used by ``make paper01-results``:

``0``
    Every registered terminal is ``EARNED`` and the hostile battery is clean.
``1``
    A real negative: some terminal is ``NOT_EARNED``, or a battery check
    ``FAIL``-ed. Something was checked and did not hold.
``2``
    The ledger could not be bound to the frozen registry. Malformed input, not a
    scientific result.
``3``
    ``CANNOT_CHECK``. Nothing failed and nothing was established. This is the
    expected exit today and it is deliberately distinct from both of the others:
    ten open programmes whose terminals have not been attempted is not a build
    failure and is not a pass.

The report is sealed with :func:`orion.programme.identity.seal`, so a copy
committed to the repository can be re-verified by removing one key.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from orion.programme.checks_superiority import run_superiority_checks
from orion.programme.identity import seal
from orion.programme.records import Outcome
from orion.programme.superiority import (
    SUPERIORITY_REPORT_SCHEMA,
    Actionability,
    PaperTerminalStatus,
)
from orion.programme.superiority_ledger import (
    LedgerBindingError,
    SuperiorityLedger,
    ledger_from_payload,
)
from orion.programme.superiority_terminals import PAPER_GATES

EXIT_EARNED = 0
EXIT_NOT_EARNED = 1
EXIT_MALFORMED = 2
EXIT_CANNOT_CHECK = 3


def build_report(ledger: SuperiorityLedger) -> dict[str, Any]:
    """Adjudicate every paper and run the battery. Returns a sealed payload."""

    battery = run_superiority_checks(ledger)

    papers: list[dict[str, Any]] = []
    for paper in ledger.papers:
        statuses = paper.statuses()
        papers.append(
            {
                "paper_id": paper.paper_id,
                "issue": paper.issue_number,
                "terminal": paper.terminal().value,
                "strongest_grade": paper.strongest_grade.value,
                "declared_claim_scope": (
                    paper.declared_claim_scope.value
                    if paper.declared_claim_scope is not None
                    else None
                ),
                "predecessor_artifacts": [
                    {
                        "artifact_ref": item.artifact_ref,
                        "grade": item.grade.value,
                        "terminal": item.terminal,
                    }
                    for item in paper.predecessor_artifacts
                ],
                "gates": [
                    {
                        "gate_id": status.gate_id,
                        "kind": status.kind.value,
                        "outcome": status.outcome.value,
                        "reason": status.reason,
                        "findings": list(status.findings),
                    }
                    for status in statuses
                ],
                "work_queue": [
                    {
                        "gate_id": item.gate_id,
                        "responsibility": item.responsibility.value,
                        "actionability": item.actionability.value,
                        "statement": item.statement,
                        "unblock": item.unblock,
                        "refs": list(item.refs),
                    }
                    for item in paper.work_queue()
                ],
                "unclassified_blocked_gate_ids": list(paper.unclassified_blocked_gate_ids()),
            }
        )

    terminals = [paper["terminal"] for paper in papers]
    battery_failed = any(
        result.outcome is Outcome.FAIL for result in battery.results
    )

    # The queue across all papers, nearest-to-actionable first. This is the
    # deliverable for a reader asking "what can be done about P1 today?", which a
    # per-paper status cannot answer.
    queue = sorted(
        (
            {**item, "paper_id": paper["paper_id"], "issue": paper["issue"]}
            for paper in papers
            for item in paper["work_queue"]
        ),
        key=lambda item: (
            Actionability(item["actionability"]).queue_rank,
            item["paper_id"],
            item["gate_id"],
        ),
    )
    by_actionability: dict[str, int] = {}
    by_responsibility: dict[str, int] = {}
    for item in queue:
        by_actionability[item["actionability"]] = by_actionability.get(item["actionability"], 0) + 1
        by_responsibility[item["responsibility"]] = (
            by_responsibility.get(item["responsibility"], 0) + 1
        )

    if PaperTerminalStatus.NOT_EARNED.value in terminals or battery_failed:
        overall = PaperTerminalStatus.NOT_EARNED.value
    elif (
        battery.blocked
        or ledger.missing_paper_ids
        or PaperTerminalStatus.CANNOT_CHECK.value in terminals
    ):
        overall = PaperTerminalStatus.CANNOT_CHECK.value
    else:
        overall = PaperTerminalStatus.EARNED.value

    return seal(
        {
            "schema_version": SUPERIORITY_REPORT_SCHEMA,
            "ledger_id": ledger.ledger_id,
            "frozen_at": ledger.frozen_at,
            "overall_terminal": overall,
            # A clean report is a precondition for closing one of these issues,
            # never a grant of it. Closure authority sits with the repository
            # owner, and this key exists so no caller can mistake the two.
            "grants_issue_closure": False,
            "registered_paper_count": len(PAPER_GATES),
            "missing_paper_ids": list(ledger.missing_paper_ids),
            "battery": battery.to_payload(),
            "work_queue": queue,
            "work_queue_by_actionability": by_actionability,
            "work_queue_by_responsibility": by_responsibility,
            "papers": papers,
        }
    )


def exit_code_for(report: dict[str, Any]) -> int:
    overall = report["overall_terminal"]
    if overall == PaperTerminalStatus.NOT_EARNED.value:
        return EXIT_NOT_EARNED
    if overall == PaperTerminalStatus.CANNOT_CHECK.value:
        return EXIT_CANNOT_CHECK
    return EXIT_EARNED


def _render_text(report: dict[str, Any]) -> str:
    lines = [
        f"P1-P10 superiority terminals — ledger {report['ledger_id']} "
        f"frozen {report['frozen_at']}",
        f"overall: {report['overall_terminal']}",
        "",
    ]
    for paper in report["papers"]:
        blocked = [
            gate for gate in paper["gates"] if gate["outcome"] != Outcome.PASS.value
        ]
        lines.append(
            f"{paper['paper_id']:>3} (#{paper['issue']}): {paper['terminal']:<13} "
            f"strongest={paper['strongest_grade']:<22} "
            f"{len(paper['gates']) - len(blocked)}/{len(paper['gates'])} gates pass"
        )
    lines.append("")
    lines.append("battery:")
    for result in report["battery"]["results"]:
        lines.append(f"  {result['outcome']:<12} {result['check_id']}: {result['reason']}")

    queue = report["work_queue"]
    if queue:
        lines.append("")
        lines.append(f"work queue ({len(queue)} blocked terminals, nearest first):")
        current = None
        for item in queue:
            if item["actionability"] != current:
                current = item["actionability"]
                lines.append(f"  [{current}]")
            lines.append(
                f"    {item['paper_id']:>3} {item['gate_id']:<10} "
                f"{item['responsibility']:<29} {item['statement']}"
            )
            lines.append(f"        -> {item['unblock']}")
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    """Entry point. ``argv`` is required rather than defaulting to ``sys.argv``.

    ``tests/unit/programme/test_constitutional_boundary.py`` calls every
    zero-argument callable in this package to prove none of them emits the
    Phase-4 terminal marker. It catches ``Exception``, and argparse raises
    ``SystemExit``, which is not one --- so a defaulted ``argv`` would make that
    boundary test fail on an argument-parsing error rather than on anything it
    is testing. Requiring the parameter keeps this function out of that scan.
    """

    parser = argparse.ArgumentParser(
        prog="orion.programme.superiority_report",
        description="Adjudicate the P1-P10 superiority terminals against a ledger.",
    )
    parser.add_argument("--ledger", required=True, type=Path, help="path to the ledger JSON")
    parser.add_argument("--out", type=Path, help="write the sealed JSON report here")
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the human-readable summary"
    )
    args = parser.parse_args(argv)

    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ledger could not be read: {error}", file=sys.stderr)
        return EXIT_MALFORMED

    try:
        ledger = ledger_from_payload(payload)
    except LedgerBindingError as error:
        print(f"ledger could not be bound to the frozen registry: {error}", file=sys.stderr)
        return EXIT_MALFORMED

    report = build_report(ledger)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if not args.quiet:
        print(_render_text(report))

    code = exit_code_for(report)
    if code == EXIT_CANNOT_CHECK:
        print(
            "\nsuperiority_report -> CANNOT_CHECK (exit 3). No P1-P10 superiority "
            "terminal is currently established, and none has been refuted. This is "
            "the honest state of ten open programmes, not a build failure.",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    raise SystemExit(main(sys.argv[1:]))
