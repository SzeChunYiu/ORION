"""Apply the P3 instruments to the frozen public-reference atlas.

:mod:`orion.study.p3.treatment_contrast` and
:mod:`orion.study.p3.identity_opportunity` are scope-general. This module is the
adapter that points them at the artifact whose defect they were written from, so
the check is reachable from P3's real evidence rather than only from a fixture.
An instrument that only ever runs on its own test data repeats the failure it
was built to catch.

It re-derives every arm with ``orion.study.p3_public_reference_analysis``'s own
functions --- ``ablated_relation`` and ``_prediction`` --- so a change to the
ablation definitions cannot leave the audit measuring a stale one. Nothing here
rewrites the frozen analysis; it adds the denominators the analysis does not
carry.

Run it against either frozen atlas::

    python -m orion.study.p3.public_reference_audit --cases <atlas>.jsonl

and it exits non-zero when any arm's treatment was the identity or any guard has
no denominator.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
)
from orion.programme.guard_exercise import GuardAssessment, worst_outcome
from orion.programme.records import Outcome
from orion.study.p3_public_reference import load_jsonl, projection_from_dict
from orion.study.p3_public_reference_analysis import ABLATIONS, _prediction, ablated_relation

from .identity_opportunity import (
    IdentityDecisionLedger,
    assess_identity_guards,
    build_identity_ledger,
)
from .treatment_contrast import (
    NecessityAssessment,
    TreatmentContrast,
    assess_coordinate_necessity,
    contrast_from_runs,
)

SCORED_SYSTEMS = ("orion", "flat_predicate_canonicalization", "exact_coordinate_conservative")

# The arm whose treatment overrides the comparison rule instead of editing the
# projections. Its inputs are the control's by construction, so its contrast is
# built from the cases where the override branch binds rather than from an input
# diff --- which is a different measurement, not an exemption from measuring.
RULE_OVERRIDE_ABLATION = "force_compatibility_without_obstruction"

# What each arm claims to do, in the words the verdict will quote back.
TREATMENT_DEFINITIONS = {
    "remove_referent": "both projections' referent_ids emptied",
    "remove_construct": "both projections' construct_ids emptied",
    "remove_measurement": "both projections' measurement_ids emptied",
    "remove_temporal_context": "both projections' temporal_context_ids emptied",
    "remove_modality_polarity_attribution_discourse": (
        "both projections' modality, polarity, attribution and discourse relation erased"
    ),
    RULE_OVERRIDE_ABLATION: (
        "equal predicates short-circuited to COMPATIBLE, bypassing the obstruction rule"
    ),
}

_COORDINATE_FIELDS = {
    "remove_referent": "referent_ids",
    "remove_construct": "construct_ids",
    "remove_measurement": "measurement_ids",
    "remove_temporal_context": "temporal_context_ids",
}


def ablated_projections(
    case: dict[str, object], ablation: str
) -> tuple[ScientificMeaningProjection, ScientificMeaningProjection]:
    """The inputs one arm actually hands to the comparison rule.

    Mirrors ``ablated_relation``'s transformations. Computing them separately is
    the point: an arm that empties an already-empty field produces inputs equal
    to the control's, and that equality is what the analysis never looks at.
    """

    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    field = _COORDINATE_FIELDS.get(ablation)
    if field is not None:
        return replace(left, **{field: ()}), replace(right, **{field: ()})
    if ablation == "remove_modality_polarity_attribution_discourse":
        blanked: dict[str, object] = {
            "modality": Modality.UNKNOWN,
            "polarity": Polarity.UNKNOWN,
            "attribution_id": "",
            "discourse_relation": "",
        }
        return replace(left, **blanked), replace(right, **blanked)
    if ablation == RULE_OVERRIDE_ABLATION:
        return left, right
    raise ValueError(f"unknown ablation: {ablation}")


def _rule_override_contrast(cases: Sequence[dict[str, object]]) -> TreatmentContrast:
    """Contrast for the arm that overrides the rule rather than the projections.

    The override binds only where the two predicates are equal; elsewhere the arm
    falls through to the untouched comparison and is the full system. So the
    treated set is the equal-predicate cases, and a decision can only move inside
    it.
    """

    treated = 0
    changed = 0
    for case in cases:
        left = projection_from_dict(case["left_projection"])
        right = projection_from_dict(case["right_projection"])
        if left.predicate != right.predicate:
            continue
        treated += 1
        if ablated_relation(case, RULE_OVERRIDE_ABLATION) is not _prediction(case, "orion"):
            changed += 1
    return TreatmentContrast(
        arm_id=RULE_OVERRIDE_ABLATION,
        cases=len(cases),
        cases_treated=treated,
        decisions_changed=changed,
        treatment_definition=TREATMENT_DEFINITIONS[RULE_OVERRIDE_ABLATION],
    )


def contrasts_for_atlas(cases: Sequence[dict[str, object]]) -> tuple[TreatmentContrast, ...]:
    """One :class:`TreatmentContrast` per ablation arm, measured from the cases."""

    if not cases:
        raise ValueError("an empty atlas has no contrast to measure")
    control_inputs = [
        (
            projection_from_dict(case["left_projection"]),
            projection_from_dict(case["right_projection"]),
        )
        for case in cases
    ]
    control_decisions = [_prediction(case, "orion") for case in cases]

    contrasts: list[TreatmentContrast] = []
    for ablation in ABLATIONS:
        if ablation == RULE_OVERRIDE_ABLATION:
            contrasts.append(_rule_override_contrast(cases))
            continue
        contrasts.append(
            contrast_from_runs(
                ablation,
                control_inputs=control_inputs,
                treated_inputs=[ablated_projections(case, ablation) for case in cases],
                control_decisions=control_decisions,
                treated_decisions=[ablated_relation(case, ablation) for case in cases],
                treatment_definition=TREATMENT_DEFINITIONS[ablation],
            )
        )
    return tuple(contrasts)


def ledger_for_atlas(
    atlas_id: str,
    cases: Sequence[dict[str, object]],
    *,
    systems: Sequence[str] = SCORED_SYSTEMS,
) -> IdentityDecisionLedger:
    """The merge/split decision ledger for the scored systems on this atlas."""

    rows: list[tuple[str, str, MeaningRelation, MeaningRelation]] = []
    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, dict)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        for system in systems:
            rows.append((str(case["case_id"]), system, gold, _prediction(case, system)))
    return build_identity_ledger(atlas_id, rows)


def audit_atlas(
    atlas_id: str,
    cases: Sequence[dict[str, object]],
    *,
    candidate: str = "orion",
    false_split_comparator: str = "exact_coordinate_conservative",
) -> dict[str, object]:
    """Full audit: coordinate necessity per arm, merge/split guards, and a roll-up."""

    necessity: tuple[NecessityAssessment, ...] = tuple(
        assess_coordinate_necessity(item) for item in contrasts_for_atlas(cases)
    )
    ledger = ledger_for_atlas(atlas_id, cases)
    guards: tuple[GuardAssessment, ...] = assess_identity_guards(
        ledger, candidate=candidate, comparator=false_split_comparator
    )
    outcomes = {item.outcome for item in necessity} | {worst_outcome(guards)}
    if Outcome.FAIL in outcomes:
        overall = Outcome.FAIL
    elif Outcome.CANNOT_CHECK in outcomes:
        overall = Outcome.CANNOT_CHECK
    else:
        overall = Outcome.PASS
    return {
        "schema_version": "orion.p3.public-reference-audit.v1",
        "atlas_id": atlas_id,
        "n_cases": len(cases),
        "overall_outcome": overall.value,
        "coordinate_necessity": [item.as_json() for item in necessity],
        "identity_guards": [item.as_json() for item in guards],
        "ledger": ledger.as_json(),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a frozen ORION-P3 public-reference atlas for absent measurements"
    )
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--atlas-id", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    cases = load_jsonl(args.cases)
    report = audit_atlas(args.atlas_id or args.cases.parent.name, cases)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["overall_outcome"] == Outcome.PASS.value else 3


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "RULE_OVERRIDE_ABLATION",
    "SCORED_SYSTEMS",
    "TREATMENT_DEFINITIONS",
    "ablated_projections",
    "audit_atlas",
    "contrasts_for_atlas",
    "ledger_for_atlas",
]
