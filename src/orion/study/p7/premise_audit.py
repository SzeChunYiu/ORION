"""Audit P7's two shipped closure checkers for premises they were handed.

Runs both registrations --- the 64-state transport theorem behind the paper's C4
and the 25-pair composition block behind P7.V3.5 --- and reports, per premise,
how many of the checker's own enumerated cases exclude any value of it and how
many deciding rules the artifact therefore accepts.

The transport check is also measured with
:mod:`orion.programme.refutation_capacity`, and it passes: every declared wrong
theory of the terminal map is refuted. Printing the two verdicts side by side is
the point of this audit --- a check can reject every false theory that can be
written against it and still leave the premise the claim is about entirely free,
because the premise is a parameter and there is no rule to write a false theory
of.

Exits ``3`` when any premise blocks, so it fails a pipeline rather than printing
a table nobody reads::

    python -m orion.study.p7.premise_audit
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from orion.programme.decided_premises import (
    DecisionConstraint,
    decision_outcome,
    sample_assignments_accepted,
)
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    RefutationCapacity,
    axis_sensitivity,
    measure_refutation_capacity,
)
from orion.study.p7 import closure_premises as premises


def audit_p7_closure_checkers() -> dict[str, Any]:
    """Measure both shipped artifacts, against the files on disk."""

    theory_closure = premises.theory_closure_module()
    closure_carrying = premises.closure_carrying_module()

    transport = premises.transport_constraint(theory_closure)
    composition = premises.composition_constraint(closure_carrying)

    capacity: RefutationCapacity = measure_refutation_capacity(
        premises.transport_check(),
        reference=premises.transport_rule(theory_closure),
        reference_id=premises.TRANSPORT_REFERENCE_ID,
        theories=premises.FALSE_TRANSPORT_THEORIES,
        space=premises.transport_theory_space(),
    )

    # Single-case perturbation counts admissible rules exactly only if the
    # artifact's assertions factorise over cases; sampling whole rules tests it.
    sampled = sample_assignments_accepted(
        premises.TARGET_AMBIGUITY,
        cases=premises.transport_cases(),
        replay=premises.transport_replay(theory_closure),
    )

    space = premises.closure_model_space(closure_carrying)
    donor_axis = axis_sensitivity(
        "donor", reference=premises.closure_reference(closure_carrying), space=space
    )
    accepted, total = premises.compose_rules_accepted(closure_carrying)

    constraints = (transport, composition)
    return {
        "constraints": constraints,
        "transport_capacity": capacity,
        "donor_axis": donor_axis,
        "sampled_ambiguity_rules": sampled,
        "canonical_rows_sha256": premises.canonical_rows_digest(closure_carrying),
        "canonical_rows_reproduced": (
            premises.canonical_rows_digest(closure_carrying) == premises.SHIPPED_ROWS_SHA256
        ),
        "composition_argument_triples": premises.composition_argument_triples(closure_carrying),
        "compose_rules_accepted": accepted,
        "compose_rules_total": total,
        "outcome": decision_outcome(constraints),
    }


def report_as_json(report: dict[str, Any]) -> dict[str, Any]:
    constraints: Sequence[DecisionConstraint] = report["constraints"]
    return {
        "constraints": [item.as_json() for item in constraints],
        "transport_capacity": report["transport_capacity"].as_json(),
        "donor_axis": report["donor_axis"].as_json(),
        "sampled_ambiguity_rules": list(report["sampled_ambiguity_rules"]),
        "canonical_rows_sha256": report["canonical_rows_sha256"],
        "canonical_rows_reproduced": report["canonical_rows_reproduced"],
        "composition_argument_triples": [
            list(triple) for triple in report["composition_argument_triples"]
        ],
        "compose_rules_accepted": report["compose_rules_accepted"],
        "compose_rules_total": report["compose_rules_total"],
        "outcome": report["outcome"].value,
    }


def _render(report: dict[str, Any]) -> str:
    lines = ["P7 closure premises"]
    for constraint in report["constraints"]:
        lines.append(
            f"  {constraint.check_id} / {constraint.premise.premise_id} "
            f"[{constraint.premise.claim_ref}] -> {constraint.outcome.value} "
            f"({constraint.reason.value})"
        )
        lines.append(
            f"      free on {len(constraint.free_case_ids)}/{len(constraint.cases)} "
            f"enumerated cases; {constraint.admissible_assignments} deciding rules admissible"
        )
        lines.append(f"      {constraint.detail}")
    capacity = report["transport_capacity"]
    lines.append(
        f"  refutation capacity of {capacity.check_id}: {capacity.outcome.value} — "
        f"refuted {len(capacity.refuted)}, accepted {len(capacity.survivors)} of the "
        f"declared false theories of the terminal map"
    )
    accepted_rules, trials = report["sampled_ambiguity_rules"]
    lines.append(
        f"  whole ambiguity rules drawn at random and accepted: {accepted_rules}/{trials}"
    )
    axis = report["donor_axis"]
    lines.append(
        f"  axis {axis.axis!r}: {axis.verdict_changing_pairs}/{axis.comparable_pairs} "
        f"sibling pairs change the verdict"
        + (f" -> INERT, every count repeated {axis.multiplier}x" if axis.inert else "")
    )
    lines.append(
        f"  composition block evaluates {len(report['composition_argument_triples'])} of 8 "
        f"argument triples and accepts {report['compose_rules_accepted']}/"
        f"{report['compose_rules_total']} Boolean composition rules"
    )
    lines.append(
        f"  canonical_rows_sha256 reproduced: {report['canonical_rows_reproduced']} "
        f"({report['canonical_rows_sha256'][:8]})"
    )
    lines.append(f"  outcome: {report['outcome'].value}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p7_closure_checkers()
    print(json.dumps(report_as_json(report), indent=2, sort_keys=True) if args.json else _render(report))
    return 3 if Outcome(report["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
