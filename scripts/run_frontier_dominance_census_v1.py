#!/usr/bin/env python3
"""Exact small-scope census for ORION Discovery V3 reference semantics."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from orion.discovery.frontier_dominance import (
    ClosureClass,
    ComparisonContract,
    DonorExplanation,
    NoveltyLayer,
    ResourceVector,
    SemanticAtom,
    SemanticEdge,
    SystemProfile,
    TaskOutcome,
    assess_frontier_dominance,
    donor_expansion_is_residual_monotone,
    fair_dovetail_schedule,
    minimal_residual_families,
)


def rv(pair: tuple[int, int]) -> ResourceVector:
    return ResourceVector.from_mapping({"compute": pair[0], "memory": pair[1]})


def main() -> int:
    resource_rows = ((1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (1, 3), (3, 3))
    profile_cells = 0
    normal_form_violations = 0
    frontier_dominant_cells = 0
    triangulated_cells = 0
    conservativity_negative_cells = 0
    resource_negative_cells = 0
    calibration_negative_cells = 0
    unmatched_negative_cells = 0

    for (
        donor_frontier_success,
        candidate_old_success,
        candidate_frontier_success,
        candidate_old_false_promotion,
        candidate_frontier_false_promotion,
        candidate_old_resource,
        candidate_frontier_resource,
        matched,
    ) in product(
        (False, True),
        (False, True),
        (False, True),
        (False, True),
        (False, True),
        resource_rows,
        resource_rows,
        (False, True),
    ):
        profile_cells += 1
        contract = ComparisonContract(
            contract_id=f"C-{profile_cells}",
            task_ids=("old", "frontier"),
            information_contract_id="I",
            resource_contract_id="R",
            evaluator_id="E",
            same_candidate_visible_information=matched,
            same_tool_access=matched,
            donor_first_refusal=matched,
            frozen_before_outcomes=matched,
        )
        donor = SystemProfile(
            "donor",
            {
                "old": TaskOutcome(
                    "old", ClosureClass.DONOR_CLOSURE, True, True, False, rv((2, 2))
                ),
                "frontier": TaskOutcome(
                    "frontier",
                    ClosureClass.FRONTIER,
                    donor_frontier_success,
                    donor_frontier_success,
                    False,
                    rv((2, 2)),
                    held_out=True,
                    counterfactual=True,
                ),
            },
        )
        candidate = SystemProfile(
            "candidate",
            {
                "old": TaskOutcome(
                    "old",
                    ClosureClass.DONOR_CLOSURE,
                    candidate_old_success,
                    candidate_old_success,
                    candidate_old_false_promotion,
                    rv(candidate_old_resource),
                ),
                "frontier": TaskOutcome(
                    "frontier",
                    ClosureClass.FRONTIER,
                    candidate_frontier_success,
                    candidate_frontier_success,
                    candidate_frontier_false_promotion,
                    rv(candidate_frontier_resource),
                    held_out=True,
                    counterfactual=True,
                ),
            },
        )
        report = assess_frontier_dominance(candidate, (donor,), contract=contract)

        expected_conservative = candidate_old_success and not candidate_old_false_promotion
        expected_resource = rv(candidate_old_resource).weakly_dominates(rv((2, 2)))
        expected_calibration = not (
            candidate_old_false_promotion or candidate_frontier_false_promotion
        )
        expected_frontier = candidate_frontier_success and not candidate_frontier_false_promotion and not donor_frontier_success
        expected = matched and expected_conservative and expected_resource and expected_calibration and expected_frontier
        if report.frontier_dominant != expected:
            normal_form_violations += 1
        frontier_dominant_cells += int(report.frontier_dominant)
        triangulated_cells += int(report.triangulated_frontier_dominant)
        conservativity_negative_cells += int(bool(report.donor_conservativity_violations))
        resource_negative_cells += int(bool(report.resource_violations))
        calibration_negative_cells += int(bool(report.calibration_violations))
        unmatched_negative_cells += int(not report.matched_contract)

    atoms = (
        SemanticAtom("a", NoveltyLayer.METHOD, "A"),
        SemanticAtom("b", NoveltyLayer.REPRESENTATION, "B"),
        SemanticAtom("c", NoveltyLayer.MECHANISM, "C"),
    )
    edges = (
        SemanticEdge("e1", ("a", "b"), "c", "COMPOSES", "E1"),
        SemanticEdge("e2", ("c",), "a", "VALIDATES", "E2"),
    )
    semantic_ids = ("a", "b", "c", "e1", "e2")
    residual_cells = 0
    residual_monotonicity_violations = 0
    interaction_only_cells = 0
    empty_residual_cells = 0
    for old_mask in range(1 << len(semantic_ids)):
        old_covered = {
            semantic_ids[index]
            for index in range(len(semantic_ids))
            if old_mask & (1 << index)
        }
        for new_mask in range(1 << len(semantic_ids)):
            new_covered = {
                semantic_ids[index]
                for index in range(len(semantic_ids))
                if new_mask & (1 << index)
            }
            if not old_covered.issubset(new_covered):
                continue
            residual_cells += 1
            old_explanation = DonorExplanation(
                ("D1",),
                tuple(sorted(old_covered & {"a", "b", "c"})),
                tuple(sorted(old_covered & {"e1", "e2"})),
            )
            new_explanation = DonorExplanation(
                ("D1", "D2"),
                tuple(sorted(new_covered & {"a", "b", "c"})),
                tuple(sorted(new_covered & {"e1", "e2"})),
            )
            old_rows = minimal_residual_families(atoms, edges, (old_explanation,))
            new_rows = minimal_residual_families(
                atoms, edges, (old_explanation, new_explanation)
            )
            if not donor_expansion_is_residual_monotone(old_rows, new_rows):
                residual_monotonicity_violations += 1
            interaction_only_cells += int(any(row.interaction_only for row in new_rows))
            empty_residual_cells += int(any(row.empty for row in new_rows))

    schedule = fair_dovetail_schedule(("g0", "g1", "g2", "g3"), max_stage=10)
    dovetail_expected = {
        (f"g{i}", j)
        for i in range(4)
        for j in range(10 - i)
    }
    dovetail_missing = sorted(dovetail_expected - set(schedule))

    payload = {
        "schema": "orion.discovery.v3.finite-reference-receipt.v1",
        "profile_census": {
            "cells": profile_cells,
            "normal_form_violations": normal_form_violations,
            "frontier_dominant_cells": frontier_dominant_cells,
            "triangulated_cells": triangulated_cells,
            "conservativity_negative_cells": conservativity_negative_cells,
            "resource_negative_cells": resource_negative_cells,
            "calibration_negative_cells": calibration_negative_cells,
            "unmatched_negative_cells": unmatched_negative_cells,
        },
        "residual_census": {
            "cells": residual_cells,
            "monotonicity_violations": residual_monotonicity_violations,
            "interaction_only_cells": interaction_only_cells,
            "empty_residual_cells": empty_residual_cells,
        },
        "dovetail": {
            "scheduled_pairs": len(schedule),
            "expected_pairs": len(dovetail_expected),
            "missing_pairs": dovetail_missing,
        },
        "terminal": (
            "ORION_DISCOVERY_V3_FINITE_REFERENCE_GREEN"
            if normal_form_violations == 0
            and residual_monotonicity_violations == 0
            and not dovetail_missing
            else "ORION_DISCOVERY_V3_FINITE_REFERENCE_FAIL"
        ),
        "authority": {
            "external_novelty": "CANNOT_CHECK",
            "paper_authority_delta": "NONE",
        },
    }
    output = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "orion-discovery-v3"
        / "FINITE_REFERENCE_RECEIPT_V1.json"
    )
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(payload["terminal"], f"profile_cells={profile_cells}", f"residual_cells={residual_cells}")
    return 0 if payload["terminal"].endswith("GREEN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
