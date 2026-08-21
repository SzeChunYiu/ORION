"""Audit P9's shipped D1 transfer margins for a comparator that answered the cases.

Scores the three published differences against the arms they name, re-scores the
frozen predictions on re-composed protected splits, measures how many protected
cases each view can still tell apart once its vocabulary is fixed, and asks
whether the ``D1_EVALUATOR_FAILURE`` branch could ever be taken.

Exits ``3`` when anything blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p9.transfer_audit
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from orion.programme.guard_exercise import worst_outcome
from orion.programme.records import Outcome
from orion.study.p9 import transfer_margins as p9


def audit_p9_transfer_margins() -> dict[str, Any]:
    """Measure every published D1 margin, and roll the verdicts up without compensation."""

    result = p9.load_shipped_d1_result()
    margins = p9.d1_contrast_margins(result)
    sensitivity = p9.d1_composition_sensitivity(result)
    collapse = p9.d1_view_collapse()
    oracle = p9.d1_oracle_divergence()

    # The oracle's outcome is not a margin verdict: a terminal branch whose
    # trigger recomputes the gold it grades is the P6 failure, measured with P6's
    # instrument and carried here so the two verdicts stay separable.
    oracle_outcome = Outcome.PASS if oracle.applied else Outcome.FAIL
    outcome = worst_outcome(tuple(item.assessment for item in margins))
    for other in (*(item.outcome for item in margins), oracle_outcome):
        if other.blocks and not outcome.blocks:
            outcome = other

    return {
        "result_digest": result["result_digest"],
        "terminal": result["terminal"],
        "margins": margins,
        "sensitivity": sensitivity,
        "view_collapse": collapse,
        "oracle": oracle,
        "oracle_outcome": oracle_outcome,
        "outcome": outcome,
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_digest": report["result_digest"],
        "terminal": report["terminal"],
        "margins": [item.as_json() for item in report["margins"]],
        "sensitivity": {
            arm: item.as_json() for arm, item in sorted(report["sensitivity"].items())
        },
        "view_collapse": report["view_collapse"],
        "oracle": report["oracle"].as_json(),
        "oracle_outcome": report["oracle_outcome"].value,
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    lines = [
        "P9 D1 transfer margins",
        f"  archive {report['result_digest']} -> {report['terminal']}",
        "",
    ]
    for margin in report["margins"]:
        comparator = margin.comparator
        lines.extend(
            [
                f"  {margin.label}",
                f"    published margin: {margin.published_margin}"
                f"  earned: {margin.earned_margin}"
                f"  prior-supplied: {margin.prior_supplied}",
                f"    informedness margin: {margin.informedness_margin}",
                f"    {comparator.arm_id}: accuracy {comparator.accuracy}, "
                f"{comparator.distinct_predictions} distinct prediction(s), "
                f"informedness {comparator.informedness}",
                f"    departures from its own modal answer: "
                f"{comparator.departures}/{comparator.eval_cases}",
                f"    outcome: {margin.outcome.value} ({margin.reason.value})",
                "",
            ]
        )
    for arm, item in sorted(report["sensitivity"].items()):
        lines.append(
            f"  {arm} over {item.compositions} re-composed splits: "
            f"published margin [{item.published_margin_low}, {item.published_margin_high}], "
            f"informedness margin [{item.informedness_margin_low}, "
            f"{item.informedness_margin_high}]"
        )
    lines.append("")
    for view, counts in sorted(report["view_collapse"].items()):
        lines.append(
            f"  {view}: {counts['test_keys_in_train_vocabulary']}/{counts['test_keys']} "
            f"protected feature keys survive the fitted vocabulary, leaving "
            f"{counts['distinct_in_vocabulary_test_signatures']} distinct protected row(s)"
        )
    oracle = report["oracle"]
    lines.extend(
        [
            "",
            f"  {oracle.theory_id}",
            f"    points {oracle.points}, divergent {oracle.points_changed}",
            f"    outcome: {report['oracle_outcome'].value}",
            "",
            f"  audit outcome: {report['outcome'].value}",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p9_transfer_margins()
    payload = report_as_json(report)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
