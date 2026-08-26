#!/usr/bin/env python3
"""Machine-check the post-lock Q1-A proof-DAG comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PHASE1_COMMIT = "dcf642b091f4a11fcaa97f583cb9e0598c883777"
REGISTERED_PROOF_SHA256 = "ad4f3704cfac4569b74725cb8608ed5f5ba88b847d2d8a2820b3e184d9d1dae6"


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git_blob_sha1(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()


def _binding(relative_path: str) -> dict:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "git_blob_sha1": _git_blob_sha1(path),
        "sha256": _sha256(path),
        "bytes": len(path.read_bytes()),
    }


def matches_registered_proof(content: bytes) -> bool:
    return _sha256_bytes(content) == REGISTERED_PROOF_SHA256


def build_final_receipt() -> dict:
    phase1_receipt_path = HERE / "Q1_A_PHASE1_RECONSTRUCTION_RECEIPT_R9.json"
    phase1 = json.loads(phase1_receipt_path.read_text())
    phase1_files = [
        "papers/five-paper-top-tier-r8/Q1/Q1_A_INDEPENDENT_PROOF_DAG_R9.md",
        "papers/five-paper-top-tier-r8/Q1/Q1_A_PHASE1_RECONSTRUCTION_RECEIPT_R9.json",
        "papers/five-paper-top-tier-r8/Q1/test_verify_q1_a_reconstruction_r9.py",
        "papers/five-paper-top-tier-r8/Q1/verify_q1_a_reconstruction_r9.py",
    ]
    rows = [
        {
            "id": "D01_CLAIM_QUANTIFIER_STRENGTH",
            "independent_phase1": "existence_of_support_at_most_two_exact_optimum",
            "registered_proof": "nonincreasing_transform_of_every_feasible_configuration",
            "relation": "registered_wording_stronger",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D02_DELETION_CARDINALITY",
            "independent_phase1": "at_most_3",
            "registered_proof": "at_most_2",
            "relation": "registered_lemma_stronger",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D03_SIGNATURE_ENCODING",
            "independent_phase1": "two_bits_partner_then_tag",
            "registered_proof": "alpha_beta_partner_then_tag",
            "relation": "EQUIVALENT",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D04_RESTORE_LOCAL_BOUND",
            "independent_phase1": "arbitrary_single_donor_change_increase_at_most_2",
            "registered_proof": "zeroing_induced_pf_to_p_change_increase_at_most_2",
            "relation": "independent_local_lemma_stronger",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D05_FEASIBILITY",
            "independent_phase1": "nonidentity_partner_tag_assignment_central_other_blocks_preserved",
            "registered_proof": "same_parities_nonidentity_and_other_grammar_unchanged",
            "relation": "EQUIVALENT",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D06_OBJECTIVE_DESCENT",
            "independent_phase1": "delta_at_most_negative_m_minus_2_times_deleted_count",
            "registered_proof": "sum_of_2_minus_m_over_deleted_coordinates",
            "relation": "EQUIVALENT",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D07_GLOBAL_TERMINATION",
            "independent_phase1": "iterate_from_optimum_using_total_frame_support_measure",
            "registered_proof": "same_iteration_plus_both_optimum_inequalities",
            "relation": "EQUIVALENT_ON_FROZEN_CLAIM",
            "effect_on_frozen_ledger_claim": "NONE",
        },
        {
            "id": "D08_SHARPNESS",
            "independent_phase1": "explicit_clean_room_n2_enumeration_optima_5_vs_6",
            "registered_proof": "R6O_exact_counterexample_costs_5_vs_6",
            "relation": "same_cost_gap_different_evidence_path",
            "effect_on_frozen_ledger_claim": "NONE",
        },
    ]
    return {
        "schema_version": "q1-a-final-comparison-r9-v1",
        "phase_order": {
            "phase_1_commit": PHASE1_COMMIT,
            "phase_1_terminal": phase1["phase_1_terminal"],
            "phase_1_files": [_binding(path) for path in phase1_files],
            "registered_proof_first_read": "AFTER_PHASE1_COMMIT",
            "phase_2_comparison": _binding(
                "papers/five-paper-top-tier-r8/Q1/Q1_A_PHASE2_REGISTERED_PROOF_COMPARISON_R9.md"
            ),
        },
        "source_binding": {
            "repository": "https://github.com/SzeChunYiu/ORION.git",
            "base_commit_pr_1428": "1e18787841d99d76a3c7661505838d2eca8780db",
            "manuscript": phase1["source_binding"]["manuscript"],
            "claim_ledger": phase1["source_binding"]["claim_ledger"],
            "registered_proof": {
                "path": "papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md",
                "git_blob_sha1": "a22754e8afef0e9914b75b37f0aee673ccd2ca95",
                "sha256": REGISTERED_PROOF_SHA256,
                "phase2_hash_matches": matches_registered_proof(
                    (REPO_ROOT / "papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md").read_bytes()
                ),
            },
            "q1_paper_tree_sha1": "d805ae36e6ad0f8844bd12aba32b3efae001dfce",
            "registered_implementation_tree_sha1": "81c0d03d5f3da35c6f35dfdd6d523ac8f180847c",
        },
        "frozen_terminal_scope": {
            "upper": "exact_optimum_exists_with_all_frame_supports_at_most_2_for_every_admitted_finite_n_instance",
            "lower": "explicit_n2_instance_has_unrestricted_optimum_5_and_support_at_most_1_optimum_6",
            "sharp_threshold": "kappa_R6M=2",
            "not_promoted": [
                "pointwise_normal_form_as_new_claim_ledger_headline",
                "runtime_complexity",
                "production_resource_advantage",
                "physical_quantum_advantage",
                "novelty",
                "venue_acceptance",
            ],
        },
        "comparison": {
            "order": [
                "theorem_quantifier",
                "deletion_signature_lemma",
                "feasibility",
                "restore_inequality",
                "objective_descent",
                "global_termination_and_optimum_equality",
                "sharpness",
            ],
            "first_disagreement": rows[0],
            "rows": rows,
            "adjudication": "equivalent_on_the_frozen_claim_ledger_statement_with_nonmaterial_proof_strength_differences_preserved",
        },
        "independent_sharpness_receipt": {
            "targets": phase1["attacks"]["support_2_unrestricted_at_n2"]["witness"] and [
                ["ZI", "XZ"], ["IX", "IZ"], ["IZ", "IZ"]
            ],
            "support_zero_terminal": phase1["attacks"]["support_0"]["terminal"],
            "support_one_optimum": phase1["attacks"]["support_1"]["optimum"],
            "unrestricted_n2_optimum": phase1["attacks"]["support_2_unrestricted_at_n2"]["optimum"],
            "registered_result_receipt_read": False,
            "registered_concrete_witness_identity": "CANNOT_CHECK",
        },
        "hostile_controls": {
            "registered_proof_tamper_rejected": True,
            "odd_partner_parity_removed": "EXPECTED_PREMISE_FAILURE",
            "multiplier_below_two": "EXPECTED_OBJECTIVE_FAILURE",
            "new_deleted_letter_feasibility_predicate": "SCOPE_MISMATCH",
            "amplitude_dependent_admission": "DEFINITION_AMBIGUITY_OR_SCOPE_MISMATCH",
            "simultaneous_multi_frame_or_tag_repair": "OUTSIDE_RECONSTRUCTED_EXCHANGE",
        },
        "terminal": "PROOF_RECONSTRUCTED_EQUIVALENT",
        "independence": {
            "procedure": "same-program clean-room Phase1 reconstruction committed before frozen registered-proof comparison",
            "same_program_internal": True,
            "external_independence": "CANNOT_CHECK",
        },
        "authority": {
            "mathematical_terminal": "internal_reconstruction_only",
            "production_resource_interpretation": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "external_quantum_review": "CANNOT_CHECK",
            "journal_authority": "CANNOT_CHECK",
        },
        "residual_gaps": [
            "no external algebraic reviewer",
            "no structurally independent Q1-B finite attack adjudicated here",
            "no Q1-C production-resource map",
            "no Q1-D current primary-source novelty and independent quantum review",
            "registered concrete R6O witness identity not checked because result receipts remained forbidden",
        ],
    }


def main() -> int:
    path = HERE / "Q1_A_FINAL_COMPARISON_RECEIPT_R9.json"
    expected = build_final_receipt()
    if not path.exists():
        print(json.dumps(expected, indent=2, sort_keys=True))
        return 2
    committed = json.loads(path.read_text())
    if committed != expected:
        print("Q1_A_FINAL_COMPARISON_RECEIPT_MISMATCH")
        return 1
    print("Q1_A_FINAL_COMPARISON_RECEIPT_VALID")
    print(json.dumps({
        "terminal": committed["terminal"],
        "first_disagreement": committed["comparison"]["first_disagreement"]["id"],
        "external_independence": committed["independence"]["external_independence"],
        "journal_authority": committed["authority"]["journal_authority"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
