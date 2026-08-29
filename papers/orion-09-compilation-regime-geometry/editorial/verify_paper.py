#!/usr/bin/env python3
"""Independent, standard-library verification of ORION-09 paper bindings.

The verifier does not import any scientific generator.  It checks immutable
input digests, selected theorem and finite-domain fields, arithmetic, generated
tables, and exact manuscript wording for the most error-prone claims.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-09-compilation-regime-geometry"
OUT = PAPER / "editorial" / "INDEPENDENT_PAPER_VERIFICATION.json"

EXPECTED_SHA256 = {
    "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json": "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875",
    "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json": "f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66",
    "research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json": "6020dfe340b224a6fae22ef9d74be3bb381d091ee819bb39f44e416ba8a8bf44",
    "research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json": "6b829cf0fa19629522df3c5907fa3c14ac4e49f6c32b4ed1227e486b202a9329",
    "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json": "99526e0c133a7e58ef203f83ee817185d4349f17bca652d54cc0a6700c7ecdc1",
    "research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json": "30011c45adc85918ce535f71c87ba7a1dbbea7ee87dc209810d65a1f22066e51",
    "research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json": "d3353ce926b1f2ff2ecab3da68c4fbd545ec820a9e372d6f288ec9daed1b6e82",
    "papers/orion-09-compilation-regime-geometry/evidence/R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json": "2f52b5dde955d9c156a0b221a1518a66aa966ca7d1c572ed59a198caac217902",
    "papers/orion-09-compilation-regime-geometry/evidence/STATE_PREPARATION_PANEL_RECORDS_V1.json": "34c7449a5d1f2912f8f2de92adead46e54cd5640f548201df165a4a46e52088f",
    "research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json": "e86d16d03e3f2e0bab405c571739e1bd15622a515164d343a866fbae3d53338a",
    "research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json": "e9b744f58a57986973b736ee2d4f30c4759c4437e0a60b17b7ca07b1ee42f50a",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def require(text: str, needle: str, label: str, checks: list[dict]) -> None:
    ok = needle in text
    checks.append({"id": label, "pass": ok})
    if not ok:
        raise AssertionError(f"missing manuscript binding: {needle}")


def main() -> None:
    checks: list[dict] = []
    for relative, expected in EXPECTED_SHA256.items():
        observed = digest(ROOT / relative)
        ok = observed == expected
        checks.append(
            {
                "id": f"digest:{relative}",
                "pass": ok,
                "expected": expected,
                "observed": observed,
            }
        )
        if not ok:
            raise AssertionError(f"digest mismatch: {relative}")

    shared = load("research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    rank2 = load("research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json")
    rank2_parent = load("research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json")
    six = load("research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json")
    cone = load("research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json")
    stab = load("research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json")
    rich = load(
        "papers/orion-09-compilation-regime-geometry/evidence/"
        "R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json"
    )
    panel = load(
        "papers/orion-09-compilation-regime-geometry/evidence/"
        "STATE_PREPARATION_PANEL_RECORDS_V1.json"
    )
    phase = load("research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json")
    slack = load("research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json")

    facts = {
        "shared_support_ceiling": shared["outcome"] == "THEOREM_MACHINE_CHECKED",
        "shared_exchange_domain": shared["lemma_e"]["domain_size"] == 18_432,
        "rank2_exact_support": rank2["support_bound"] == rank2["intrinsic_support_number"] == 1,
        "rank2_tightness": rank2["support0_infeasible"] is True,
        "rank2_precursor_closed": rank2_parent["support3_full_acceptance"]["v3_broad_unsafe_type_cases"] == 21
        and rank2_parent["support3_full_acceptance"]["full_accepted_unsafe_type_cases"] == 0,
        "rank2_finite_counts": [
            rank2["finite_lemmas"]["deletion"]["rows"],
            rank2["finite_lemmas"]["core_alignment"]["rows"],
            rank2["finite_lemmas"]["same_qubit_tag_rigidity"]["rows"],
            rank2["finite_lemmas"]["distinct_qubit_tag"]["rows"],
        ]
        == [2_880, 6_912, 576, 9_216],
        "six_term_theorem": six["terminal"] == "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED",
        "six_term_complete_n2": six["blind_complete_regression"]["n2_count"] == 38_760,
        "six_term_condition_complete": six["certificate_structure"]["packing_clauses"]
        == ["ONE_PAIR", "TWO_DISJOINT_PAIRS", "THREE_DISJOINT_PAIRS"]
        and six["production_gain_decomposition"]["shape_count"] == 11,
        "unit_objective": cone["controls"]["O0"]["theta"] == [4, 2, 2, 1]
        and cone["controls"]["O0"]["inside"] is True
        and cone["controls"]["O0"]["on_boundary"] is True,
        "interior_objective": cone["controls"]["O_in"]["theta"] == [5, 3, 2, 1]
        and cone["controls"]["O_in"]["strict_interior"] is True,
        "cone_outside_semantics": cone["outside_cone_semantics"] == "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED",
        "state_complete_domain": sum(v["instances"] for v in rich["stage1"]["domain"].values()) == 1_146,
        "rich_near_injective": rich["stage1"]["unique_feature_cells"] == 1_109
        and rich["stage1"]["singleton_cells"] == 1_072,
        "rich_in_domain_zero_floor": rich["stage1"]["mixed_cell_count"] == 0
        and rich["stage1"]["irreducible_error_floor"] == 0,
        "rich_failed_transfer": rich["stage2"]["cv_parity_split_lookup"]["errors"] == 32
        and rich["stage2"]["cv_parity_split_lookup"]["covered"] == 2
        and rich["stage2"]["shuffle_null_200"]["empirical_p_errors_le_observed"] == 0.51,
        "panel_partition_invariant": panel["panel_partition"]
        == {
            "feature_cells": 119,
            "singleton_cells": 118,
            "doubleton_cells": 1,
            "larger_cells": 0,
            "mixed_cells": 0,
            "cell_sizes_sum": 120,
        },
        "panel_record_count": len(panel["records"]) == 120
        and len(panel["feature_schema"]["ordered_names"]) == 127,
        "shuffle_protocol_bound": panel["shuffle_null"]["permutations"] == 200
        and panel["shuffle_null"]["python_seed"] == 20260828
        and panel["shuffle_null"]["mean"] == 32.41
        and panel["shuffle_null"]["empirical_p_errors_le_observed"] == 0.51,
        "prospective_adverse": stab["component5_prospective"]["regime_correct"] == 100
        and stab["component5_prospective"]["cost_correct"] == 67,
        "corrected_search_negative": phase["candidate_count"] == 211_248
        and all(value["strict_count"] == 0 for value in phase["objectives"].values()),
        "slack_conditional": slack["q2_relation"]["relation_holds_on_measured_families"] is True
        and slack["q2_relation"]["rewrite_dependence"]["relation_holds_under_aligned_rewrite"] is False,
    }
    for label, ok in facts.items():
        checks.append({"id": f"fact:{label}", "pass": bool(ok)})
        if not ok:
            raise AssertionError(label)

    manuscript = "\n".join(
        path.read_text()
        for path in [PAPER / "manuscript" / "main.tex"]
        + sorted((PAPER / "manuscript" / "sections").glob("*.tex"))
        + [
            PAPER / "manuscript" / "generated_results_tables.tex",
            PAPER / "manuscript" / "supplement.tex",
            PAPER / "manuscript" / "generated_support_tables.tex",
        ]
    )
    require(manuscript, "1,109 distinct cells", "manuscript-rich-cells", checks)
    require(manuscript, "32 of 120 errors", "manuscript-transfer-errors", checks)
    require(manuscript, "100 of 120 regime labels", "manuscript-prospective-regime", checks)
    require(manuscript, "67 of 120 exact costs", "manuscript-prospective-cost", checks)
    require(manuscript, "certificate is silent", "manuscript-outside-cone", checks)
    require(manuscript, "not a compact law", "manuscript-near-injective-boundary", checks)
    require(manuscript, "(2,4,2,1)", "manuscript-unit-objective-vector", checks)
    require(manuscript, "(3,5,2,1)", "manuscript-interior-objective-vector", checks)
    require(manuscript, "for every perfect matching", "manuscript-six-term-condition", checks)
    require(manuscript, "119 cells", "manuscript-panel-cells", checks)
    require(manuscript, "no improvement under this null on this panel", "manuscript-null-calibration", checks)
    require(manuscript, "unknown", "manuscript-typed-unknown", checks)
    require(manuscript, "not applicable", "manuscript-typed-not-applicable", checks)

    table_text = (PAPER / "manuscript" / "generated_results_tables.tex").read_text()
    require(table_text, "Feature cells & 1,109 & 119", "table-panel-cells", checks)
    require(table_text, "Singleton cells & 1,072 & 118", "table-panel-singletons", checks)

    result = {
        "schema": "ORION09.paper_verification.v1",
        "verifier_class": "standard_library_only_no_scientific_generator_imports",
        "same_project_custody": True,
        "external_replication": False,
        "checks": checks,
        "summary": {"passed": sum(c["pass"] for c in checks), "failed": 0},
        "terminal": "PAPER_BINDINGS_VERIFIED_WITHIN_SAME_PROJECT_CUSTODY",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
