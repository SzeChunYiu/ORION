from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "CONTROLLED_NOVELTY_RESULTS_RECEIPT_V1.json"
LEDGER = HERE / "CONTROLLED_NOVELTY_RESULTS_LEDGER_V1.md"

REQUIRED = [
    "STRUCTURAL_SCALING_RESEARCH_PROGRAM_V1.md",
    "P9_LLM_STRUCTURE_SCALING_PROTOCOL_V1.md",
    "P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md",
    "P10_INVARIANT_STATE_AND_SEARCH_PROTOCOL_V1.md",
    "HOSTILE_NOVELTY_REVIEW_MATRIX_V1.md",
    "NOVELTY_EXPANSION_PROTOCOL_V3.md",
    "RELATIONAL_COMPLEXITY_THEOREM_V1.md",
    "INVERTIBLE_OBFUSCATION_THEOREM_V1.md",
    "STRUCTURAL_ACCESSIBILITY_THEORY_V2.md",
    "verify_structural_accessibility_theory_v2.py",
    "RELATIONAL_ACCESSIBILITY_V1_1_OUTCOME_DISPOSITION.md",
    "RELATIONAL_ACCESSIBILITY_REPLICATION_PROTOCOL_V2.md",
    "SEMANTIC_ORBIT_CONTROLLED_PROTOCOL_V1.md",
    "ACCESS_DEGREE_RECOVERY_PROTOCOL_V1.md",
    "PREDICTIVE_STATE_COMPRESSION_PROTOCOL_V1.md",
    "RUNTIME_GATED_ANALYSIS_CONTRACT_V1.md",
    "analyze_runtime_gated_novelty_v1.py",
    "analyze_runtime_gated_extensions_v1.py",
]


def main() -> None:
    missing = [name for name in REQUIRED if not (HERE / name).is_file()]
    if missing:
        raise SystemExit(f"missing controlled novelty artifacts: {missing}")
    if not RECEIPT.is_file() or not LEDGER.is_file():
        raise SystemExit("missing controlled result receipt/ledger")

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "P9P10.ControlledNoveltyResultsReceipt.v1"
    assert receipt["claim_authority"] == "CONTROLLED_GENERATED_WORLDS_ONLY_NO_LLM_OR_LEAN_PROMOTION"
    r = receipt["results"]

    # Historical negative must remain negative.
    assert r["N1_v1_1_failed_terminal"]["terminal"] == "RELATIONAL_ACCESSIBILITY_PRIMARY_GATE_NOT_MET"
    assert r["N1_v1_1_failed_terminal"]["disposition"] == "FAILED_FROZEN_HOSTILE_GATE_RETAINED"

    # Fresh same-information replication.
    n2 = r["N2_relational_accessibility_v2"]
    assert n2["terminal"] == "RELATIONAL_ACCESSIBILITY_REPLICATED_CONTROLLED_CLASS"
    assert n2["passed_cell_count"] == n2["cell_count"] == 18
    assert n2["mean_relational_accuracy"] > 0.999
    assert n2["mean_flat_accuracy"] < 0.51
    assert n2["minimum_delta"] > 0.45

    # Capacity frontier and theorem-aligned interaction order.
    n3 = r["N3_relational_complexity_frontier"]
    assert n3["terminal"] == "RELATIONAL_CAPACITY_FRONTIER_SUPPORTED_CONTROLLED_CLASS"
    assert n3["k17_threshold_ratio"] == 32.0
    assert n3["relational_linear_sample_threshold_0_90"] == [64, 64, 128, 128, 512]
    assert n3["flat_quadratic_sample_threshold_0_90"] == [64, 128, 512, 4096, None]
    assert all(v is None for v in n3["flat_linear_sample_threshold_0_90"])

    # Bijective obfuscation difficulty.
    n4 = r["N4_invertible_obfuscation_ladder"]
    assert n4["terminal"] == "INVERTIBLE_OBFUSCATION_ACCESSIBILITY_TAX_SUPPORTED"
    assert n4["decode_failure_count"] == 0
    assert n4["all_adjacent_nonincreasing"] is True
    assert n4["mean_linear_accuracy"][0] == 1.0
    assert n4["mean_linear_accuracy"][-1] < 0.54

    # Exact semantic symmetries.
    n5 = r["N5_semantic_orbit"]
    assert n5["terminal"] == "RELATIONAL_SEMANTIC_ORBIT_STABILITY_SUPPORTED_CONTROLLED_CLASS"
    assert n5["target_preservation_failures"] == 0
    assert n5["relational_mean_oir"][0] == 0.0
    assert n5["relational_mean_oir"][1] == 0.0
    assert n5["flat_mean_oir"][2] > 0.31
    assert n5["relational_mean_oir"][2] < 0.012

    # Capacity buys back access only to tested degree.
    n6 = r["N6_access_degree_recovery"]
    assert n6["terminal"] == "ACCESS_DEGREE_RECOVERY_SUPPORTED_CONTROLLED_CLASS"
    assert n6["decode_failure_count"] == 0
    assert n6["minimum_tested_degree_reaching_0_90"] == {
        "block_1": 1,
        "block_2": 2,
        "block_4": 4,
        "block_8": None,
        "block_13": None,
    }
    assert n6["mean_accuracy"]["block_4"][3] > 0.93
    assert n6["mean_accuracy"]["block_8"][3] < 0.78

    # Predictive sufficiency is deliberately not a same-information claim.
    n7 = r["N7_predictive_state_compression"]
    assert n7["terminal"] == "PREDICTIVE_STATE_COMPRESSION_ADVANTAGE_SUPPORTED"
    assert n7["same_information_claim"] is False
    assert n7["sample_threshold_0_90"]["minimal"] == [64, 128, 512]
    assert n7["sample_threshold_0_90"]["full"] == [128, 256, 1024]
    assert n7["sample_threshold_0_90"]["padded"] == [512, 1024, 2048]
    assert n7["median_full_to_minimal_threshold_ratio"] == 2.0
    assert n7["median_padded_to_minimal_threshold_ratio"] == 8.0
    assert n7["maximum_abs_nuisance_label_correlation"] < n7["frozen_nuisance_correlation_sentinel"]

    blocked = receipt["runtime_gated_claims"]
    assert blocked["P9_LLM_structure_scale_compute"].startswith("CANNOT_CHECK_")
    assert blocked["P10_native_state_incremental_value"].startswith("CANNOT_CHECK_")
    assert blocked["P10_action_abstraction"].startswith("CANNOT_CHECK_")
    assert blocked["P10_same_information_Lean_feedback"].startswith("CANNOT_CHECK_")
    assert blocked["P10_cross_revision"].startswith("CANNOT_CHECK_")
    assert blocked["cross_domain_structural_accessibility_law"].startswith("BLOCKED_")

    theory = (HERE / "STRUCTURAL_ACCESSIBILITY_THEORY_V2.md").read_text(encoding="utf-8")
    for token in (
        "I(Y;F)=I(Y;R)=H(Y)=1 bit",
        "E[Z x_i]=0",
        "E[Z c_i]=0",
        "E[Z r_i] = E[|S_k|]/k",
        "sqrt(B/k)",
        "I(Y;W|r)=0",
    ):
        if token not in theory:
            raise SystemExit(f"theory V2 missing exact identity: {token}")

    ledger = LEDGER.read_text(encoding="utf-8")
    for token in (
        "FAILED_TERMINAL_RETAINED",
        "SUPPORTED_CONTROLLED_CAPACITY_FRONTIER",
        "SUPPORTED_CONTROLLED_ACCESSIBILITY_TAX",
        "SUPPORTED_CONTROLLED_SEMANTIC_STABILITY",
        "SUPPORTED_CONTROLLED_CAPACITY_RECOVERY",
        "SUPPORTED_PREDICTIVE_SUFFICIENCY_RESULT",
        "CANNOT_CHECK_LLM_RUNTIME",
        "CANNOT_CHECK_NATIVE_STATE_EXECUTION",
        "BLOCKED_PENDING_SECOND_DOMAIN",
        "not same-information",
    ):
        if token not in ledger:
            raise SystemExit(f"ledger missing required claim-boundary token: {token}")

    print("P9/P10 controlled novelty review package: PASS")


if __name__ == "__main__":
    main()
