"""Audit P6's two shipped formal checkers for refutation capacity.

Runs both registrations --- the 320-state certificate-lifting checker behind
P6.V4.6 and the 1,536-state finite-model checker the superiority ledger names as
P6-U-T1's authority --- against their declared false theories, and reports the
per-check verdict, the axes that only multiply case counts, and how far the
shipped "independent" implementation departs from the primary one.

Exits ``3`` when any check blocks, so it fails a pipeline rather than printing a
table nobody reads::

    python -m orion.study.p6.refutation_audit
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from orion.programme.guard_exercise import worst_outcome
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    Rule,
    assess_theory_coverage,
    axis_sensitivity,
    divergence_of,
    measure_refutation_capacity,
)
from orion.study.p6 import finite_model_theories as finite
from orion.study.p6 import lift_theories as lifting


def audit_checker(
    *,
    checker_id: str,
    checks: Sequence[MechanizedCheck],
    reference: Rule,
    reference_id: str,
    theories: Sequence[FalseTheory],
    space: Sequence[ModelPoint],
    axes: Sequence[str],
) -> dict[str, Any]:
    """Measure every check of one shipped checker, plus the inertness of its axes."""

    capacities = tuple(
        measure_refutation_capacity(
            check,
            reference=reference,
            reference_id=reference_id,
            theories=theories,
            space=space,
        )
        for check in checks
    )
    sensitivities = tuple(
        axis_sensitivity(axis, reference=reference, space=space) for axis in axes
    )
    coverage = assess_theory_coverage(capacities, label=checker_id)
    return {
        "checker_id": checker_id,
        "reference_id": reference_id,
        "points": len(space),
        "registered_false_theories": len(theories),
        "outcome": worst_outcome(
            tuple(item.assessment for item in capacities) + (coverage.assessment,)
        ).value,
        "capacities": capacities,
        "coverage": coverage,
        "axes": sensitivities,
    }


def audit_p6_formal_checkers() -> tuple[dict[str, Any], ...]:
    """Audit both shipped checkers.

    The certificate-lifting report additionally carries the divergence of the
    repository's own independent verifier, which is the register's control: a
    second implementation that agrees everywhere cannot refute anything the
    first accepts.
    """

    lifting_report = audit_checker(
        checker_id="check_p6_x2_certificate_lifting",
        checks=lifting.SHIPPED_CHECKS,
        reference=lifting.reference_lift,
        reference_id=lifting.REFERENCE_ID,
        theories=lifting.FALSE_LIFT_THEORIES,
        space=lifting.lifting_model_space(),
        axes=lifting.ENUMERATED_AXES,
    )
    lifting_report["independent_divergence"] = divergence_of(
        lifting.INDEPENDENT_LIFT.rule,
        theory_id=lifting.INDEPENDENT_LIFT.theory_id,
        reference=lifting.reference_lift,
        space=lifting.lifting_model_space(),
    )
    lifting_report["reproduces_shipped_digest"] = (
        lifting.canonical_rows_digest() == lifting.SHIPPED_ROWS_SHA256
    )
    # The inert donor axis is a reporting defect before it is anything else, so the
    # published counts are carried here beside the number of distinct facts behind
    # them rather than left for a reader to divide out.
    lifting_report["multiplicity"] = lifting.published_count_multiplicity()

    finite_report = audit_checker(
        checker_id="check_p6_x_finite_models",
        checks=finite.SHIPPED_CHECKS,
        reference=finite.reference_admissible,
        reference_id=finite.REFERENCE_ID,
        theories=finite.FALSE_ADMISSIBILITY_THEORIES,
        space=finite.finite_model_space(),
        axes=finite.ENUMERATED_AXES,
    )
    return (lifting_report, finite_report)


def report_as_json(reports: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Roll the reports up non-compensatorily: any blocking check blocks the audit."""

    checkers = []
    for report in reports:
        payload = {
            key: value
            for key, value in report.items()
            if key not in {"capacities", "axes", "coverage", "independent_divergence"}
        }
        if "multiplicity" in payload:
            payload["multiplicity"] = [dict(row) for row in payload["multiplicity"]]
        payload["capacities"] = [item.as_json() for item in report["capacities"]]
        payload["axes"] = [item.as_json() for item in report["axes"]]
        payload["coverage"] = report["coverage"].as_json()
        divergence = report.get("independent_divergence")
        if divergence is not None:
            payload["independent_divergence"] = divergence.as_json()
        checkers.append(payload)
    return {
        "schema": "P6.RefutationCapacityAudit.v1",
        "outcome": worst_outcome(
            tuple(
                capacity.assessment
                for report in reports
                for capacity in report["capacities"]
            )
            + tuple(report["coverage"].assessment for report in reports)
        ).value,
        "checkers": checkers,
    }


def _render(reports: Sequence[dict[str, Any]]) -> str:
    lines: list[str] = []
    for report in reports:
        lines.append(
            f"{report['checker_id']}  ({report['points']} enumerated points, "
            f"{report['registered_false_theories']} declared false theories)"
        )
        header = f"  {'check':38} {'refuted':>8} {'survived':>9}  outcome"
        lines.append(header)
        lines.append("  " + "-" * (len(header) - 2))
        for capacity in report["capacities"]:
            lines.append(
                f"  {capacity.check_id:38} {len(capacity.refuted):>8} "
                f"{len(capacity.survivors):>9}  {capacity.outcome.value}"
            )
            if capacity.survivors:
                lines.append(f"      accepted: {', '.join(capacity.survivors)}")
        for axis in report["axes"]:
            state = "INERT" if axis.inert else "read by the rule"
            lines.append(
                f"  axis {axis.axis!r}: {axis.values} values, "
                f"{axis.verdict_changing_pairs}/{axis.comparable_pairs} sibling pairs "
                f"change the verdict -> {state}"
                + (f", every count repeated {axis.multiplier}x" if axis.inert else "")
            )
            if axis.inert and axis.axis == "donor" and report.get("multiplicity"):
                # Which counts, and to what. "Every count repeated 5x" is the fact;
                # a reader needs the table, because 320 that is 64 observed five
                # times is a number they will otherwise read as 320 observations.
                for row in report["multiplicity"]:
                    lines.append(
                        f"      {row['count']}: published {row['published']} = "
                        f"{row['distinct']} distinct x {row['factor']}"
                    )
        coverage = report["coverage"]
        lines.append(
            f"  false theories rejected by no check: "
            f"{len(coverage.unrefuted)}/{len(coverage.live)}"
            + (f" ({', '.join(coverage.unrefuted)})" if coverage.unrefuted else "")
        )
        divergence = report.get("independent_divergence")
        if divergence is not None:
            lines.append(
                f"  independent implementation diverges on "
                f"{divergence.points_changed}/{divergence.points} points"
            )
        lines.append(f"  checker outcome: {report['outcome']}")
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    reports = audit_p6_formal_checkers()
    payload = report_as_json(reports)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(reports))
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
