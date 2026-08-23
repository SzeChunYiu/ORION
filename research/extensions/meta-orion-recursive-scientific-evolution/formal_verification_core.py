"""Executable closure checks for the ORION-RSE derived mechanics.

This module does not turn protocol definitions into novel theorems.  It verifies
the finite/exact statements that *are* executable and records donor-subsumption
where the stronger parent representation closes the candidate residual.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


rssi = _load("rssi_exact_core_for_formal_closure", "rssi_exact_core.py")
sc = _load("successor_conditioned_core_for_formal_closure", "successor_conditioned_core.py")
sd = _load("successor_debt_core_for_formal_closure", "successor_debt_core.py")
pe = _load("projection_evolution_core_for_formal_closure", "projection_evolution_core.py")
gj = _load("generic_justification_donor_for_formal_closure", "generic_justification_donor.py")


def verify_rssi_migration_mechanics() -> dict[str, Any]:
    pilot = rssi.generate_pilot(seed=20260831, per_family=7)
    interaction = rssi.generate_interaction_pilot(seed=20260837, per_family=7)
    gold = rssi.evaluate(pilot, rssi.rule_policy)
    preserve = rssi.evaluate(pilot, rssi.always_preserve)
    reopen = rssi.evaluate(pilot, rssi.always_reopen)
    answer_only = rssi.evaluate(pilot, rssi.answer_only)
    donor_union = rssi.evaluate(pilot, rssi.donor_union_policy)
    naive_interaction = rssi.evaluate(interaction, rssi.donor_union_policy)
    coordinated = rssi.evaluate(interaction, rssi.interaction_policy)
    passed = (
        gold["all_gates_pass"]
        and not preserve["all_gates_pass"]
        and not reopen["all_gates_pass"]
        and not answer_only["all_gates_pass"]
        and donor_union["all_gates_pass"]
        and not naive_interaction["all_gates_pass"]
        and naive_interaction["task_correct"] == naive_interaction["n"]
        and coordinated["all_gates_pass"]
    )
    return {
        "id": "RSE.T1",
        "statement": "task correctness and scientific-standing migration are separable; naive parent union can be scientifically wrong despite correct answers",
        "status": "EXECUTABLE_COUNTERMODEL_VERIFIED" if passed else "FAILED",
        "passed": passed,
        "claim_boundary": "interaction benchmark only; coordinated composition is not an ORION novelty claim",
    }


def verify_successor_nonidentifiability() -> dict[str, Any]:
    pairs = sc.generate_pairs(seed=20260841, per_family=9)
    report = sc.nonidentifiability_report(pairs)
    lossy = sc.evaluate_current_summary(pairs)
    full = sc.evaluate_full_history(pairs)
    typed = sc.evaluate_typed_state(pairs)
    passed = (
        report["n_pairs"] > 0
        and report["identical_candidate_input_pairs"] == report["n_pairs"]
        and report["same_future_transition_pairs"] == report["n_pairs"]
        and report["different_protected_future_standing_pairs"] == report["n_pairs"]
        and report["deterministic_current_summary_accuracy_ceiling"] == 0.5
        and lossy["accuracy"] == 0.5
        and all(value == 1 for value in lossy["per_pair_exact"])
        and full["accuracy"] == 1.0
        and typed["accuracy"] == 1.0
    )
    return {
        "id": "RSE.T2",
        "statement": "for registered delayed pairs, identical current input plus identical future transition but different protected future standing imposes an exact 1/2 deterministic current-summary ceiling",
        "status": "FINITE_INFORMATION_CEILING_VERIFIED" if passed else "FAILED",
        "passed": passed,
        "claim_boundary": "finite registered families only; generic sufficiency/bisimulation theory is donor-owned",
    }


def verify_delayed_epistemic_debt() -> dict[str, Any]:
    pairs = sd.sc.generate_pairs(seed=20260843, per_family=8)
    lossy = sd.evaluate_d4(pairs, sd.current_summary_predictor)
    full = sd.evaluate_d4(pairs, sd.full_history_predictor)
    typed = sd.evaluate_d4(pairs, sd.typed_state_predictor)
    passed = (
        lossy["d2_current_answer_correct"] == lossy["n_variants"]
        and lossy["d4_accuracy"] == 0.5
        and lossy["d4_invalid_commit_count"] > 0
        and lossy["d4_missed_opportunity_count"] > 0
        and lossy["d4_authority_violation_count"] > 0
        and not lossy["recursive_scientific_integrity_gate"]
        and full["d4_accuracy"] == 1.0
        and full["recursive_scientific_integrity_gate"]
        and typed["d4_accuracy"] == 1.0
        and typed["recursive_scientific_integrity_gate"]
    )
    return {
        "id": "RSE.T3",
        "statement": "a state can be 100% correct on present answers yet carry hidden lineage loss that causes protected D4 successor-action failures",
        "status": "CAUSAL_DELAYED_DEBT_COUNTERMODEL_VERIFIED" if passed else "FAILED",
        "passed": passed,
        "claim_boundary": "exact synthetic DPAIR-1..3 causal extension only; delayed-debt terminology is descriptive",
    }


def verify_projection_refinement() -> dict[str, Any]:
    result = pe.two_generation_experiment(
        f1_train_seed=20260847,
        f1_holdout_seed=20260849,
        f2_refine_seed=20260851,
        f2_holdout_seed=20260853,
        per_family=7,
    )
    passed = (
        result["f0_coordinate_count"] == 0
        and result["f1_coordinate_count"] == 3
        and result["f1_holdout_accuracy"] == 1.0
        and result["f1_new_family_accuracy_before_refinement"] == 0.5
        and result["f2_coordinate_count"] == 4
        and result["f2_new_family_holdout_accuracy"] == 1.0
        and result["f2_all_family_holdout_accuracy"] == 1.0
        and result["full_lineage_holdout_accuracy"] == 1.0
    )
    return {
        "id": "RSE.T4",
        "statement": "CEGAR can refine a task-relative working projection from F0 to F1 to F2 when a new protected standing distinction appears",
        "status": "CEGAR_APPLICATION_VERIFIED" if passed else "FAILED",
        "passed": passed,
        "claim_boundary": "CEGAR and abstraction refinement are prior art; no ORION refinement-algorithm novelty",
    }


def verify_generic_justification_subsumption() -> dict[str, Any]:
    result = gj.subtraction_experiment(
        base_train_seed=20260859,
        new_family_seed=20260861,
        holdout_seed=20260863,
        per_family=8,
    )
    expected_kinds = {
        "ALWAYS_VALID",
        "INVALIDATE_ON_EVENT",
        "INVALIDATE_WHEN_EVENT_TARGET",
        "VALID_ONLY_FOR_EVENT_TARGET",
    }
    passed = (
        result["f1_coordinate_count"] == 3
        and result["f1_unseen_obligation_accuracy"] == 0.5
        and result["donor_all_family_accuracy"] == 1.0
        and set(result["donor_condition_kinds_used"]) == expected_kinds
        and result["terminal_if_verified"] == "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT"
    )
    return {
        "id": "RSE.T5",
        "statement": "a fixed generic proof/justification condition language subsumes the bespoke F1-to-F2 coordinate-expansion effect on the registered four families",
        "status": "DONOR_SUBSUMPTION_VERIFIED" if passed else "FAILED",
        "passed": passed,
        "terminal": result["terminal_if_verified"],
        "claim_boundary": "strike bespoke scientific-state-schema superiority on DPAIR-1..4",
    }


def formal_status_matrix() -> tuple[dict[str, Any], ...]:
    executable = (
        verify_rssi_migration_mechanics(),
        verify_successor_nonidentifiability(),
        verify_delayed_epistemic_debt(),
        verify_projection_refinement(),
        verify_generic_justification_subsumption(),
    )
    non_theorem = (
        {
            "id": "RSE.D1",
            "statement": "JReach_B(F,x,C|kappa)",
            "status": "DEFINITION_ONLY",
            "passed": True,
            "claim_boundary": "organizing metric; not a new universal mathematical theorem",
        },
        {
            "id": "RSE.D2",
            "statement": "mutable framework F separated from protected constitution kappa",
            "status": "DESIGN_AXIOM_PLUS_EXISTING_P4_P8_AUTHORITY",
            "passed": True,
            "claim_boundary": "generic external governance / verifier separation is donor-owned",
        },
        {
            "id": "RSE.D3",
            "statement": "lossless/reconstructive lineage plus task-relative working projection",
            "status": "DONOR_COMPOSITION_PRINCIPLE",
            "passed": True,
            "claim_boundary": "event sourcing, TMS, predictive-state theory and CEGAR own the ingredients",
        },
        {
            "id": "RSE.D4",
            "statement": "F' succeeds only under a non-compensatory scientific-dominance vector",
            "status": "PROTOCOL_RULE_ONLY",
            "passed": True,
            "claim_boundary": "not a theorem of rational agency; an ORION evaluation doctrine",
        },
        {
            "id": "RSE.D5",
            "statement": "one fixed compact scientific projection is sufficient for every future open-ended scientific transformation",
            "status": "STRUCK_UNPROVED_UNIVERSAL",
            "passed": True,
            "claim_boundary": "explicitly not claimed; sufficiency remains task/future-family relative",
        },
    )
    return executable + non_theorem


def build_closure_report() -> dict[str, Any]:
    matrix = formal_status_matrix()
    failed = tuple(row["id"] for row in matrix if not row["passed"])
    executable_rows = tuple(row for row in matrix if row["id"].startswith("RSE.T"))
    terminal = (
        "RSE_FORMAL_MECHANICS_VERIFIED_WITH_DONOR_SUBSUMPTION"
        if not failed
        and all(row["status"] != "FAILED" for row in executable_rows)
        and verify_generic_justification_subsumption()["terminal"]
        == "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT"
        else "CANNOT_CHECK"
    )
    return {
        "schema_version": "ORION.RSE.formal-verification-closure.v1",
        "terminal": terminal,
        "failed_ids": failed,
        "matrix": matrix,
        "authorized_programme_conclusion": (
            "registered exact mechanics are internally verified; bespoke projection-schema "
            "superiority is struck because the generic justification donor closes DPAIR-1..4"
        ),
        "forbidden_conclusions": (
            "universal scientific-state ontology",
            "novel CEGAR theorem",
            "novel belief-revision theorem",
            "real-world recursive scientific superiority",
            "self-authorized framework adoption",
        ),
    }
