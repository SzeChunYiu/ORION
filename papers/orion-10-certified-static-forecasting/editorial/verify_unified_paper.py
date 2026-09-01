#!/usr/bin/env python3
"""Fail-closed binding check for the unified ORION-09/10 paper.

This standard-library checker replays committed receipt fields and manuscript
bindings. It does not rerun the large scientific enumerations and does not use
the historical concatenated qg7e_generic_verify.py dispatch.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-10-certified-static-forecasting"
OUT = PAPER / "editorial/UNIFIED_PAPER_VERIFICATION.json"
FILES = {
    "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json": "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875",
    "research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json": "f9b505d908bcafec97e7114c04e29fc1f4b8d650d29ecb9ac69842a971ebaf77",
    "research/extensions/orion-qg/QG7E_TWELVE_STATES_RESULTS.json": "b452ac0ae11f610099f0a1813786f6a806847c76752dd065edc559707dcb7fd8",
    "research/extensions/orion-qg/QG7E_V2_PP_SINGLE_PINNER_RESULTS.json": "c5368796d0ccf6267e252ec06614bfeed73af80815859106b64ab7dbd7ab08d8",
    "research/extensions/orion-qg/QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json": "1caf27ed2c5782c3d276cf811bbdf28cf7467c03fcf2f12925829e859ea5fa99",
    "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json": "f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66",
    "research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json": "6b829cf0fa19629522df3c5907fa3c14ac4e49f6c32b4ed1227e486b202a9329",
    "research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json": "e86d16d03e3f2e0bab405c571739e1bd15622a515164d343a866fbae3d53338a",
    "research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json": "e9b744f58a57986973b736ee2d4f30c4759c4437e0a60b17b7ca07b1ee42f50a",
    "papers/orion-09-compilation-regime-geometry/evidence/R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json": "2f52b5dde955d9c156a0b221a1518a66aa966ca7d1c572ed59a198caac217902",
    "papers/orion-09-compilation-regime-geometry/evidence/STATE_PREPARATION_PANEL_RECORDS_V1.json": "34c7449a5d1f2912f8f2de92adead46e54cd5640f548201df165a4a46e52088f",
    "papers/orion-09-compilation-regime-geometry/theory/regime-separator-complexity-v1/RESULT.json": "03fa78697e32110611e5671999d6c6d50b099cdd2efb3c0fbcc66a575a77c1ef",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def main() -> int:
    checks: list[dict] = []

    def check(name: str, value: bool) -> None:
        checks.append({"id": name, "pass": bool(value)})
        if not value:
            raise AssertionError(name)

    for relative, expected in FILES.items():
        check(f"digest:{relative}", sha(ROOT / relative) == expected)

    shared = load("research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    cone = load("research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json")
    envelope = load("research/extensions/orion-qg/QG7E_TWELVE_STATES_RESULTS.json")
    pinner = load("research/extensions/orion-qg/QG7E_V2_PP_SINGLE_PINNER_RESULTS.json")
    chain = load("research/extensions/orion-qg/QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json")
    rank2 = load("research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json")
    six = load("research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json")
    sharp = load("research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json")
    slack = load("research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json")
    rich = load("papers/orion-09-compilation-regime-geometry/evidence/R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json")
    panel = load("papers/orion-09-compilation-regime-geometry/evidence/STATE_PREPARATION_PANEL_RECORDS_V1.json")
    separator = load("papers/orion-09-compilation-regime-geometry/theory/regime-separator-complexity-v1/RESULT.json")

    check("shared_support_two", shared["outcome"] == "THEOREM_MACHINE_CHECKED")
    check("shared_local_domain", shared["lemma_e"]["domain_size"] == 18_432)
    check("objective_cone", cone["support2_cone"]["conditions"] == ["t_c >= 2*t_r", "t_nc >= 2*t_r"])
    check("outside_control_not_converse", cone["proof_audit"]["outside_cone_not_equated_with_support3_required"] is True)
    check("outside_support_three", cone["qg2_binding"]["support3_witnesses"][0]["C_DP"] == 11 and cone["qg2_binding"]["support3_witnesses"][0]["C_Dxx"] == 13)
    check("envelope_terminal", envelope["terminal"] == "QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE")
    check("envelope_proof_chain", envelope["proof_audit"]["theorem_terminal_reached"] is True)
    check("envelope_full_domain", envelope["p1e_domination_lemma"]["geometry_count"] == 378 and envelope["p1e_domination_lemma"]["geometries_closed"] == 378 and all(row["residue"] == 0 for row in envelope["p1e_domination_lemma"]["per_geometry"]))
    check("envelope_state_count", sum(row["state_domain"] for row in envelope["p1e_domination_lemma"]["per_geometry"]) == 6_341_787_648)
    check("pinner_open_fields", pinner["PP_SINGLE_PINNER_ALL_N"] is True and pinner["CHAIN_ALL_N"] is False and pinner["GLOBAL_BDOUBLEPRIME_COMPLETENESS"] is False)
    check("chain_refuted", chain["representation_premise_refuted"] is True and chain["CHAIN_REPRESENTATION_COMPLETE"] is False)
    check("rank2_intrinsic_one", rank2["support_bound"] == rank2["intrinsic_support_number"] == 1 and rank2["support0_infeasible"] is True)
    check("six_term_theorem", six["terminal"] == "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED")
    check("sharpness_negative", sharp["candidate_count"] == 211_248 and all(v["strict_count"] == 0 for v in sharp["objectives"].values()))
    check("rank_slack_not_law", slack["q2_relation"]["rewrite_dependence"]["relation_holds_under_aligned_rewrite"] is False)
    check("small_domain_features", rich["stage1"]["mixed_cell_count"] == 0 and rich["stage1"]["unique_feature_cells"] == 1_109 and rich["stage1"]["singleton_cells"] == 1_072)
    check("four_feature_minimal", separator["separator_complexity"]["k_star"] == 4 and separator["separator_complexity"]["k_star_proved_exact"] is True)
    check("sign_mechanism_unsupported", separator["block_attribution"]["state_block_features_in_witness"] == 0)
    check("transfer_adverse", panel["observed"] == {"covered": 2, "errors": 32, "errors_among_covered": 0, "errors_among_uncovered": 32, "positive_labels": 32} and panel["shuffle_null"]["empirical_p_errors_le_observed"] == 0.51)

    manuscript = "\n".join(
        p.read_text()
        for p in [PAPER / "manuscript/main.tex", PAPER / "manuscript/main-arxiv.tex", PAPER / "manuscript/supplement.tex"]
        + sorted((PAPER / "manuscript/sections").glob("*.tex"))
        + [PAPER / "CLAIM_LEDGER_V4.md", PAPER / "ORION09_TO_ORION10_MERGE_COVERAGE_V1.md"]
    )
    for phrase in (
        "6,341,787,648",
        "CHAIN_ALL_N=false",
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS=false",
        "32 errors on 120 states",
        "MERGE_WITH_SIBLING",
        "objective-independent support-two claim",
    ):
        check(f"manuscript:{phrase}", phrase in manuscript)

    result = {
        "schema": "ORION10.unified-paper-verification.v1",
        "verifier_class": "standard_library_receipt_and_surface_binding_check",
        "large_enumerations_rerun": False,
        "historical_qg7e_generic_dispatch_used": False,
        "same_project_custody": True,
        "external_replication": False,
        "checks": checks,
        "summary": {"passed": len(checks), "failed": 0},
        "terminal": "UNIFIED_PAPER_BINDINGS_PASS__SAME_PROJECT_CUSTODY",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
