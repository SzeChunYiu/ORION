"""Audit P7's two shipped closure checkers for premises they were handed.

Runs both registrations --- the transport theorem behind the paper's C4 and the
composition block behind P7.V3.5 --- and reports, per premise, how many of the
checker's own enumerated cases exclude any value of it and how many deciding
rules the artifact therefore accepts.

The transport check is also measured with
:mod:`orion.programme.refutation_capacity`, and it passes: every declared wrong
theory of the terminal map is refuted. Printing the two verdicts side by side is
the point of this audit --- a check can reject every false theory that can be
written against it and still leave the premise the claim is about entirely free,
because the premise is a parameter and there is no rule to write a false theory
of.

Three things are reported beside the two verdicts, because each of them bounds
what the verdicts mean.

* ``bridge_match`` is now decided, from the donor pair and the registered bridge
  relation, and the report carries the axis sensitivity of that decision. The
  premise is pinned to one rule; the *value* it is pinned to still does not vary
  with the donor pair, because both registries P7 shipped are uniform.
* ``target_ambiguous_if_missing`` is now decided, because the shipped check
  enumerates an admissible target completion class beside each witness and reads
  Definition 14 off it. The report carries both case counts, because they are not
  the same measurement: 64 states of which 1 was decided, against 960 cases every
  one of which decides the premise. It also carries the same premise measured over
  the six coordinates alone, which still comes back ``UNDECIDABLE_IN_MODEL`` ---
  that contrast is what says the repair was a missing axis and not a loosened
  assertion --- and the floor under the verdict when the assertion that the rule
  agrees with ``extension_ambiguous`` is dropped: 945 of the 960 cases still
  exclude a value.
* The donor axis is inert, and the report carries the evidence for which kind of
  inert: no shipped function has a parameter a donor could enter through, so the
  enumeration is a multiplier rather than a rule declining to read a coordinate.

Exits ``3`` when any premise blocks, so it fails a pipeline rather than printing
a table nobody reads. Both premises are now decided, so it exits ``0``::

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
    witness_only_transport = premises.witness_only_transport_constraint(theory_closure)

    capacity: RefutationCapacity = measure_refutation_capacity(
        premises.transport_check(),
        reference=premises.transport_rule(theory_closure),
        reference_id=premises.TRANSPORT_REFERENCE_ID,
        theories=premises.FALSE_TRANSPORT_THEORIES,
        space=premises.transport_theory_space(),
    )

    # Single-case perturbation counts admissible rules exactly only if the
    # artifact's assertions factorise over cases; sampling whole rules tests it.
    # It is reported for the decided premises too, where it is the difference
    # between "one rule survives each case" and "one rule survives the check".
    sampled = sample_assignments_accepted(
        premises.TARGET_AMBIGUITY,
        cases=premises.transport_cases(theory_closure),
        replay=premises.transport_replay(theory_closure),
    )
    sampled_bridge = sample_assignments_accepted(
        premises.BRIDGE_MATCH,
        cases=premises.composition_cases(closure_carrying),
        replay=premises.composition_replay(closure_carrying),
    )
    sampled_witness_only = sample_assignments_accepted(
        premises.TARGET_AMBIGUITY,
        cases=premises.transport_coordinate_states(),
        replay=premises.witness_only_transport_replay(theory_closure),
    )

    space = premises.closure_model_space(closure_carrying)
    donor_axis = axis_sensitivity(
        "donor", reference=premises.closure_reference(closure_carrying), space=space
    )
    accepted, total = premises.compose_rules_accepted(closure_carrying)

    constraints = (transport, composition)
    return {
        "constraints": constraints,
        "witness_only_transport": witness_only_transport,
        "transport_authority": premises.transport_authority(theory_closure),
        "transport_mapping_floor": premises.transport_mapping_only_floor(theory_closure),
        "transport_capacity": capacity,
        "donor_axis": donor_axis,
        "donor_diagnosis": premises.donor_axis_diagnosis(closure_carrying),
        "handoff_axes": premises.composition_handoff_axes(closure_carrying),
        "composition_agreement": premises.composition_agreement(closure_carrying),
        "sampled_ambiguity_rules": sampled,
        "sampled_bridge_rules": sampled_bridge,
        "sampled_witness_only_ambiguity_rules": sampled_witness_only,
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
        "witness_only_transport": report["witness_only_transport"].as_json(),
        "transport_authority": report["transport_authority"],
        "transport_mapping_floor": report["transport_mapping_floor"],
        "transport_capacity": report["transport_capacity"].as_json(),
        "donor_axis": report["donor_axis"].as_json(),
        "donor_diagnosis": report["donor_diagnosis"],
        "handoff_axes": [item.as_json() for item in report["handoff_axes"]],
        "composition_agreement": report["composition_agreement"],
        "sampled_ambiguity_rules": list(report["sampled_ambiguity_rules"]),
        "sampled_bridge_rules": list(report["sampled_bridge_rules"]),
        "sampled_witness_only_ambiguity_rules": list(
            report["sampled_witness_only_ambiguity_rules"]
        ),
        "canonical_rows_sha256": report["canonical_rows_sha256"],
        "canonical_rows_reproduced": report["canonical_rows_reproduced"],
        "composition_argument_triples": [
            list(triple) for triple in report["composition_argument_triples"]
        ],
        "compose_rules_accepted": report["compose_rules_accepted"],
        "compose_rules_total": report["compose_rules_total"],
        "outcome": report["outcome"].value,
    }


def _constraint_lines(constraint: DecisionConstraint, *, note: str = "") -> list[str]:
    head = (
        f"  {constraint.check_id} / {constraint.premise.premise_id} "
        f"[{constraint.premise.claim_ref}] -> {constraint.outcome.value} "
        f"({constraint.reason.value})"
    )
    return [
        head + (f"  {note}" if note else ""),
        f"      free on {len(constraint.free_case_ids)}/{len(constraint.cases)} "
        f"enumerated cases; {constraint.admissible_assignments} deciding "
        f"{'rule is' if constraint.admissible_assignments == 1 else 'rules are'} admissible",
        f"      {constraint.detail}",
    ]


def _render(report: dict[str, Any]) -> str:
    lines = ["P7 closure premises"]
    authority = report["transport_authority"]
    agreement = report["composition_agreement"]
    for constraint in report["constraints"]:
        lines.extend(_constraint_lines(constraint))
        if constraint.check_id == "check_support_transport":
            lines.append(f"      authority: {authority['reading']}")
            lines.append(f"      floor: {report['transport_mapping_floor']['reading']}")
            lines.append(
                f"      the shipped check reports {authority['shipped_terminal']} over "
                f"{authority['shipped_checked']} cases"
            )
        if constraint.check_id == "p7_x2_composition_block":
            lines.append(
                "      the decision agrees with the shipped literal on "
                f"{agreement['rows_where_the_decision_agrees_with_the_shipped_literal']}"
                f"/{agreement['rows']} rows, so composition_successes="
                f"{agreement['composition_successes']} and "
                f"composition_bridge_countermodels="
                f"{agreement['composition_bridge_countermodels']} are unchanged; "
                f"verdicts moved: {agreement['verdicts_moved']}"
            )
    lines.extend(
        _constraint_lines(
            report["witness_only_transport"],
            note="[the model before it carried completion classes; not the shipped space]",
        )
    )
    capacity = report["transport_capacity"]
    lines.append(
        f"  refutation capacity of {capacity.check_id}: {capacity.outcome.value} — "
        f"refuted {len(capacity.refuted)}, accepted {len(capacity.survivors)} of the "
        f"declared false theories of the terminal map"
    )
    for label, key in (
        ("ambiguity rules against the shipped 960 cases", "sampled_ambiguity_rules"),
        ("bridge rules against the decided composition rows", "sampled_bridge_rules"),
        (
            "ambiguity rules against the 64 coordinate states alone",
            "sampled_witness_only_ambiguity_rules",
        ),
    ):
        accepted_rules, trials = report[key]
        lines.append(f"  whole {label} drawn at random and accepted: {accepted_rules}/{trials}")
    axis = report["donor_axis"]
    lines.append(
        f"  axis {axis.axis!r}: {axis.verdict_changing_pairs}/{axis.comparable_pairs} "
        f"sibling pairs change the verdict"
        + (f" -> INERT, every count repeated {axis.multiplier}x" if axis.inert else "")
    )
    diagnosis = report["donor_diagnosis"]
    lines.append(f"      {diagnosis['verdict']}: {diagnosis['reading']}")
    for handoff in report["handoff_axes"]:
        lines.append(
            f"  decided hand-off vs axis {handoff.axis!r}: "
            f"{handoff.verdict_changing_pairs}/{handoff.comparable_pairs} sibling pairs "
            f"change the decided value" + (" -> INERT" if handoff.inert else "")
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
