"""Audit P8's shipped authority receipts for a verdict the run could have withheld.

Runs the anti-laundering bench against its register of withholding cases,
injects a claim ceiling the suite has no right to, asks how far the frozen panel
could depart from the tables it grades, and measures the donor axis of the
39,936-state result the superiority ledger names for P8-U-T1.

Exits ``3`` when anything blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p8.terminal_audit
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from orion.programme.guard_exercise import worst_outcome
from orion.programme.records import Outcome
from orion.study.p8 import authority_terminals as p8


def audit_p8_authority_receipts() -> dict[str, Any]:
    """Measure every registered P8 receipt, and roll the verdicts up without compensation."""

    responsiveness = p8.bench_responsiveness()
    ceiling = p8.bench_declared_ceiling()
    divergence = p8.panel_gold_divergence()
    donor = p8.x4_donor_axis()

    # The gold's outcome is not a guard assessment: a panel that cannot disagree
    # with the mechanism it grades is the P4 failure, not a missing denominator.
    gold_outcome = Outcome.PASS if divergence.applied else Outcome.FAIL
    outcome = worst_outcome((responsiveness.assessment,))
    for other in (ceiling.outcome, gold_outcome, Outcome.FAIL if donor.inert else Outcome.PASS):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "responsiveness": responsiveness,
        "ceiling": ceiling,
        "declared_gold": divergence,
        "gold_outcome": gold_outcome,
        "donor_axis": donor,
        "outcome": outcome,
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "responsiveness": report["responsiveness"].as_json(),
        "ceiling": report["ceiling"].as_json(),
        "declared_gold": report["declared_gold"].as_json(),
        "gold_outcome": report["gold_outcome"].value,
        "donor_axis": report["donor_axis"].as_json(),
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    responsiveness = report["responsiveness"]
    ceiling = report["ceiling"]
    divergence = report["declared_gold"]
    donor = report["donor_axis"]
    lines = [
        "P8 authority receipts",
        "",
        f"  {responsiveness.label}",
        f"    baseline verdict: {responsiveness.baseline_verdict}",
        f"    distinct verdicts over the register: {len(responsiveness.verdicts_observed)}",
        f"    withholding cases the verdict ignored: "
        f"{len(responsiveness.unmoved)}/{responsiveness.exercise.opportunities}",
        f"    receipt evidence moved and verdict did not: "
        f"{', '.join(responsiveness.contradicted) or 'none'}",
        f"    outcome: {responsiveness.outcome.value} "
        f"({responsiveness.assessment.reason.value})",
        "",
        f"  {ceiling.label}",
        f"    injected bound repeated verbatim: {ceiling.subject_controlled}",
        f"    outcome: {ceiling.outcome.value}",
        "",
        f"  {divergence.theory_id}",
        f"    cases where the declared gold departs from the graded tables: "
        f"{divergence.points_changed}/{divergence.points}",
        f"    outcome: {report['gold_outcome'].value}",
        "",
        "  P8.X4 donor axis",
        f"    values {donor.values}, comparable sibling pairs {donor.comparable_pairs}, "
        f"verdict-changing {donor.verdict_changing_pairs}",
        f"    inert: {donor.inert} (multiplier x{donor.multiplier})",
        "",
        f"  audit outcome: {report['outcome'].value}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p8_authority_receipts()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
