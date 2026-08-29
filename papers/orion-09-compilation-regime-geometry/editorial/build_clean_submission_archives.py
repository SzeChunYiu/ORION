#!/usr/bin/env python3
"""Build deterministic, reviewer-facing archives with plain scientific names.

This is a private packaging utility.  It reads the preserved internal records,
selects their scientific payloads, and writes a separate review artifact that
contains no project identifiers, repository history, paths, or content hashes.
The preserved records themselves are not modified.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-09-compilation-regime-geometry"
MANUSCRIPT = PAPER / "manuscript"
OUT = PAPER / "submission_quantum"
REVIEW = OUT / "review_materials"
SOURCE = OUT / "source"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


DROP_KEY_PARTS = (
    "commit",
    "revision",
    "checkout",
    "issue",
    "pull_request",
    "repository",
    "terminal",
    "schema",
    "programme",
    "protocol",
    "authority",
    "novelty",
    "network_access",
    "protected_subject",
    "chemistry_sources",
    "responsibility",
    "receipt",
    "run_id",
    "execution_head",
    "base_revision",
    "source_result",
    "source_digests",
    "freeze_provenance",
)


def drop_key(key: str) -> bool:
    lowered = key.lower()
    provenance_token = re.search(r"(?:^|_)(?:sha(?:256)?|digest|hash)(?:$|_)", lowered)
    return bool(provenance_token) or any(part in lowered for part in DROP_KEY_PARTS)


def plain_key(key: str) -> str:
    key = re.sub(r"(?i)p0", "pair_gain_condition", key)
    key = re.sub(r"(?i)qg\d*", "", key)
    return re.sub(r"__+", "_", key).strip("_")


def plain_text(value: str) -> str:
    value = re.sub(r"(?i)from committed QG-15/QG-23 receipts;\s*", "", value)
    replacements = {
        "P0": "pair-gain condition",
        "SixLCU": "six-term model",
        "R6I": "rank-two dependent-triple model",
        "R6M_TARE": "shared-tag paired-block model",
        "R6M": "shared-tag paired-block model",
        "R6O": "weight-two local trade",
        "max_r6p_weight2_frame_donor_closure": "support_two_pair_normalization_checker",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def clean(value: Any) -> Any:
    """Remove provenance/workflow fields from an already-selected payload."""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if drop_key(key):
                continue
            renamed = plain_key(key)
            if not renamed:
                continue
            result[renamed] = clean(item)
        return result
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, str):
        return plain_text(value)
    return value


def build_scientific_records() -> None:
    exact = REVIEW / "exact_results"
    exact.mkdir(parents=True, exist_ok=True)

    shared = load("research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    write_json(
        exact / "shared_tag_support_normalization.json",
        {
            "record_type": "shared_tag_support_normalization",
            "model": "shared-tag Pauli block encoding",
            "claim": (
                "For every admitted size and target, an exact optimum exists "
                "with frame support at most two under the stated structural objective."
            ),
            "support_ceiling": 2,
            "local_exchange_check": clean(shared["lemma_e"]),
            "parity_class_check": clean(shared["lemma_b"]),
            "support_two_pair_counts": clean(shared["anticommuting_support2_pair_counts"]),
            "expected_pair_count_check": clean(shared["expected_pair_count_injection"]),
        },
    )

    rank = load("research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json")
    precursor = load("research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json")
    precursor_counts = precursor["support3_full_acceptance"]
    write_json(
        exact / "rank_two_support_normalization.json",
        {
            "record_type": "rank_two_support_normalization",
            "model": "rank-two dependent-triple block encoding",
            "claim": (
                "Every admitted target has an exact optimum with support at most one "
                "under the unit objective; support zero is infeasible."
            ),
            "support_ceiling": rank["support_bound"],
            "intrinsic_support_number": rank["intrinsic_support_number"],
            "support_zero_infeasible": rank["support0_infeasible"],
            "composition": clean(rank["composition"]),
            "finite_obligations": clean(rank["finite_lemmas"]),
            "stress_check": clean(rank["stress"]),
            "support_two_precursor": {
                "action_profile_cases": precursor_counts["v3_action_profile_type_cases"],
                "initially_unsafe_cases": precursor_counts["v3_broad_unsafe_type_cases"],
                "accepted_cases": precursor_counts["full_accepted_type_cases"],
                "accepted_safe_cases": precursor_counts["full_accepted_safe_type_cases"],
                "accepted_unsafe_cases": precursor_counts["full_accepted_unsafe_type_cases"],
            },
        },
    )

    cone = load("research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json")

    def manuscript_vector(theta: list[Any]) -> list[Any]:
        # Stored order is noncentral, central, tag, restoration.  The paper
        # displays central, noncentral, tag, restoration.
        return [theta[1], theta[0], theta[2], theta[3]]

    control_names = {
        "O0": "unit_boundary",
        "O_in": "strict_interior",
        "O_tag_out": "tag_weight_outside",
        "O_restore_out": "restoration_weight_outside",
        "O_nc_out": "noncentral_weight_outside",
    }
    controls = {}
    for source_name, row in cone["controls"].items():
        controls[control_names[source_name]] = {
            "vector": manuscript_vector(row["theta"]),
            **{key: item for key, item in row.items() if key != "theta"},
        }
    write_json(
        exact / "rank_two_objective_region.json",
        {
            "record_type": "rank_two_objective_region",
            "coordinate_order": ["central", "noncentral", "tag", "restoration"],
            "sufficient_inequalities": [
                "2*noncentral >= 5*restoration",
                "central + noncentral >= 5*restoration",
                "2*noncentral >= 2*restoration + 2*tag",
                "central + noncentral >= 2*restoration + 2*tag",
            ],
            "controls": clean(controls),
            "support_ceiling_inside_region": cone["support_bound_inside_cone"],
            "intrinsic_support_inside_region": cone["intrinsic_support_number_inside_cone"],
            "scope_note": (
                "The inequalities certify this proof only. Their complement is not a necessity region."
            ),
        },
    )

    six = load("research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json")
    regression = six["blind_complete_regression"]
    production = six["production_gain_decomposition"]
    write_json(
        exact / "six_term_pair_gain_boundary.json",
        {
            "record_type": "six_term_pair_gain_boundary",
            "model": "six-term linear-combination compilation",
            "claim": (
                "The six-singleton reference is exact exactly when every pair gain is nonpositive, "
                "every two-disjoint-pair gain plus one is nonpositive, and every perfect-matching "
                "gain plus two is nonpositive."
            ),
            "pair_gain_definition": "gain(e) = 4*common_nonidentity_positions(e) - sum_of_weights(e)",
            "packing_clauses": [
                "one pair",
                "two disjoint pairs",
                "three disjoint pairs forming a perfect matching",
            ],
            "interaction_arity": six["certificate_structure"]["interaction_arity"],
            "production_decomposition": clean(
                {
                    "partition_count": production["partition_count"],
                    "shape_count": production["shape_count"],
                    "shapes": production["shapes"],
                    "block_coefficients": production["block_coefficients"],
                    "expected_block_coefficients": production["expected_block_coefficients"],
                    "coefficient_checks": production["coefficient_checks"],
                    "constant_checks": production["constant_checks"],
                    "all_coefficients_exact": production["all_coefficients_exact"],
                    "all_shape_constants_exact": production["all_shape_constants_exact"],
                }
            ),
            "proof_obligations": clean(six["proof_ledger"]),
            "complete_regression": {
                "size_one_instances": regression["n1_count"],
                "size_one_reference_exact": regression["n1_p0_true"],
                "size_two_instances": regression["n2_count"],
                "size_two_reference_exact": regression["n2_p0_true"],
                "mismatches": regression["mismatches"],
                "zero_mismatches": regression["zero_mismatches"],
            },
        },
    )

    coarse = load("research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json")
    rich = load(
        "papers/orion-09-compilation-regime-geometry/evidence/"
        "R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json"
    )
    prospective = load("research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json")
    earlier = prospective["component5_prospective"]
    write_json(
        exact / "state_preparation_exact_summary.json",
        {
            "record_type": "state_preparation_exact_summary",
            "model": "weighted Clifford stabilizer-state preparation",
            "gate_costs": clean(prospective["gate_costs"]),
            "complete_domain": clean(rich["stage1"]),
            "frozen_panel": clean(rich["stage2"]),
            "coarse_feature_negative": {
                "feature_count": 13,
                "states": coarse["stabprep"]["cell_table"]["N_total"]
                + coarse["stabprep"]["cell_table"]["P_total"],
                "positive_labels": coarse["stabprep"]["cell_table"]["P_total"],
                "negative_labels": coarse["stabprep"]["cell_table"]["N_total"],
                "feature_cells": coarse["stabprep"]["cell_table"]["cells"],
                "mixed_cells": coarse["q2"]["mixed_cell_count"],
                "irreducible_error_floor": coarse["q2"]["E_floor"],
            },
            "earlier_prospective_forecast": {
                "panel_states": len(earlier["predictions"]),
                "reference_exact_labels_matched": earlier["regime_correct"],
                "exact_costs_matched": earlier["cost_correct"],
                "interpretation": (
                    "Both exactness criteria failed; later feature work does not revise this forecast."
                ),
            },
        },
    )

    panel = load(
        "papers/orion-09-compilation-regime-geometry/evidence/"
        "STATE_PREPARATION_PANEL_RECORDS_V1.json"
    )
    write_json(
        exact / "state_preparation_panel.json",
        {
            "record_type": "state_preparation_panel",
            "analysis_status": "frozen adverse result exposed for review",
            "panel_generation": clean(panel["panel_generation"]),
            "reference_compiler": clean(panel["reference_compiler"]),
            "feature_schema": clean(panel["feature_schema"]),
            "transfer_rule": clean(panel["transfer_rule"]),
            "panel_partition": clean(panel["panel_partition"]),
            "observed": clean(panel["observed"]),
            "shuffle_null": clean(panel["shuffle_null"]),
            "records": clean(panel["records"]),
        },
    )

    outside = load("research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json")
    objective_names = {
        "O0": "unit_boundary",
        "O_nc_out": "noncentral_weight_outside",
        "O_restore_out": "restoration_weight_outside",
        "O_tag_out": "tag_weight_outside",
    }
    write_json(
        exact / "outside_region_search.json",
        {
            "record_type": "outside_region_search",
            "candidate_count": outside["candidate_count"],
            "corrected_feasibility_rule": (
                "Infeasible shared-tag frame-pair cells are skipped; minima use feasible cells only."
            ),
            "objectives": {
                objective_names[name]: clean(row) for name, row in outside["objectives"].items()
            },
            "objectives_with_strict_witness": [],
            "interpretation": (
                "This is a frozen-domain negative result and does not prove global sharpness."
            ),
        },
    )

    diagnostic = load("research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json")
    rows = {row["family"]: row for row in diagnostic["q1_slack_table"]}
    aligned_rows = {
        row["family"]: row for row in diagnostic["q2_relation"]["rewrite_dependence"]["rows"]
    }
    write_json(
        exact / "rank_support_diagnostic.json",
        {
            "record_type": "rank_support_diagnostic",
            "status": "diagnostic observation, not a theorem or law",
            "certified_rewrite": [
                {
                    "model": "rank-two dependent-triple block encoding",
                    "rank": rows["R6I"]["rank"],
                    "intrinsic_support": rows["R6I"]["kappa"],
                    "exchange_margin": rows["R6I"]["mu"],
                    "rank_minus_support": rows["R6I"]["slack"],
                },
                {
                    "model": "shared-tag paired-block encoding",
                    "rank": rows["R6M_TARE"]["rank"],
                    "intrinsic_support": rows["R6M_TARE"]["kappa"],
                    "exchange_margin": rows["R6M_TARE"]["mu"],
                    "rank_minus_support": rows["R6M_TARE"]["slack"],
                },
            ],
            "aligned_rewrite": [
                {
                    "model": "rank-two dependent-triple block encoding",
                    "rank": aligned_rows["R6I"]["rank_under_margin_aligned_rewrite"],
                    "intrinsic_support": aligned_rows["R6I"]["kappa"],
                    "exchange_margin": aligned_rows["R6I"]["mu"],
                    "relation_holds": aligned_rows["R6I"]["slack_equals_mu"],
                },
                {
                    "model": "shared-tag paired-block encoding",
                    "rank": aligned_rows["R6M_TARE"]["rank_under_margin_aligned_rewrite"],
                    "intrinsic_support": aligned_rows["R6M_TARE"]["kappa"],
                    "exchange_margin": aligned_rows["R6M_TARE"]["mu"],
                    "relation_holds": aligned_rows["R6M_TARE"]["slack_equals_mu"],
                },
            ],
            "interpretation": (
                "The two-point equality is rewrite-dependent and has no residual degrees of freedom."
            ),
        },
    )


VERIFY_SCRIPT = r'''#!/usr/bin/env python3
"""Standard-library checks for the scientific review records."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "exact_results"


def load(name):
    return json.loads((DATA / name).read_text())


checks = []


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


shared = load("shared_tag_support_normalization.json")
rank = load("rank_two_support_normalization.json")
cone = load("rank_two_objective_region.json")
six = load("six_term_pair_gain_boundary.json")
state = load("state_preparation_exact_summary.json")
panel = load("state_preparation_panel.json")
outside = load("outside_region_search.json")
diagnostic = load("rank_support_diagnostic.json")

check("shared support ceiling", shared["support_ceiling"] == 2)
check("shared local exchange", shared["local_exchange_check"]["domain_size"] == 18432)
check("shared local violations", shared["local_exchange_check"]["violations"] == 0)
check("rank support", rank["support_ceiling"] == rank["intrinsic_support_number"] == 1)
check("rank support zero", rank["support_zero_infeasible"] is True)
check("rank finite rows", [
    rank["finite_obligations"]["deletion"]["rows"],
    rank["finite_obligations"]["core_alignment"]["rows"],
    rank["finite_obligations"]["same_qubit_tag_rigidity"]["rows"],
    rank["finite_obligations"]["distinct_qubit_tag"]["rows"],
] == [2880, 6912, 576, 9216])
check("precursor closure", rank["support_two_precursor"]["initially_unsafe_cases"] == 21)
check("precursor accepted unsafe", rank["support_two_precursor"]["accepted_unsafe_cases"] == 0)
check("objective boundary", cone["controls"]["unit_boundary"]["vector"] == [2, 4, 2, 1])
check("objective interior", cone["controls"]["strict_interior"]["vector"] == [3, 5, 2, 1])
check("six shapes", six["production_decomposition"]["shape_count"] == 11)
check("six partitions", six["production_decomposition"]["partition_count"] == 203)
check("six complete size two", six["complete_regression"]["size_two_instances"] == 38760)
check("six zero mismatches", six["complete_regression"]["zero_mismatches"] is True)
check("complete states", state["complete_domain"]["instances"] == 1146)
check("complete feature cells", state["complete_domain"]["unique_feature_cells"] == 1109)
check("complete singleton cells", state["complete_domain"]["singleton_cells"] == 1072)
check("complete mixed cells", state["complete_domain"]["mixed_cell_count"] == 0)
check("coarse floor", state["coarse_feature_negative"]["irreducible_error_floor"] == 43)
check("panel cells", panel["panel_partition"] == {
    "feature_cells": 119,
    "singleton_cells": 118,
    "doubleton_cells": 1,
    "larger_cells": 0,
    "mixed_cells": 0,
    "cell_sizes_sum": 120,
})
check("panel records", len(panel["records"]) == 120)
check("feature names", len(panel["feature_schema"]["ordered_names"]) == 127)
check("panel errors", panel["observed"]["errors"] == 32)
check("panel coverage", panel["observed"]["covered"] == 2)
check("shuffle mean", panel["shuffle_null"]["mean"] == 32.41)
check("shuffle probability", panel["shuffle_null"]["empirical_p_errors_le_observed"] == 0.51)
check("prospective labels", state["earlier_prospective_forecast"]["reference_exact_labels_matched"] == 100)
check("prospective costs", state["earlier_prospective_forecast"]["exact_costs_matched"] == 67)
check("outside search", outside["candidate_count"] == 211248)
check("outside strict witnesses", all(row["strict_count"] == 0 for row in outside["objectives"].values()))
check("diagnostic conditional", diagnostic["aligned_rewrite"][1]["relation_holds"] is False)

print(json.dumps({"checks_passed": len(checks), "checks_failed": 0}, sort_keys=True))
'''


TABLE_SCRIPT = r'''#!/usr/bin/env python3
"""Regenerate concise review tables from the scientific records."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "exact_results"


def load(name):
    return json.loads((DATA / name).read_text())


shared = load("shared_tag_support_normalization.json")
rank = load("rank_two_support_normalization.json")
six = load("six_term_pair_gain_boundary.json")
state = load("state_preparation_exact_summary.json")
panel = load("state_preparation_panel.json")

lines = [
    "# Regenerated headline tables",
    "",
    "| Model | Exact authority | Headline result |",
    "|---|---:|---|",
    f"| Shared-tag Pauli block encoding | all admitted sizes | support at most {shared['support_ceiling']} |",
    f"| Rank-two dependent-triple block encoding | all admitted sizes | intrinsic support {rank['intrinsic_support_number']} |",
    f"| Six-term linear-combination compilation | {six['production_decomposition']['shape_count']} partition shapes | exact pair-gain boundary |",
    f"| Weighted Clifford state preparation | {state['complete_domain']['instances']} complete states and 120 frozen panel states | adverse transfer retained |",
    "",
    "| Quantity | Complete domain | Frozen panel |",
    "|---|---:|---:|",
    f"| States | {state['complete_domain']['instances']} | 120 |",
    f"| Feature cells | {state['complete_domain']['unique_feature_cells']} | {panel['panel_partition']['feature_cells']} |",
    f"| Singleton cells | {state['complete_domain']['singleton_cells']} | {panel['panel_partition']['singleton_cells']} |",
    f"| Mixed cells | {state['complete_domain']['mixed_cell_count']} | {panel['panel_partition']['mixed_cells']} |",
    f"| Lookup errors | not applicable | {panel['observed']['errors']} |",
    f"| Covered states | not applicable | {panel['observed']['covered']} |",
    f"| Shuffle-null mean errors | not applicable | {panel['shuffle_null']['mean']:.2f} |",
    f"| Empirical probability | not applicable | {panel['shuffle_null']['empirical_p_errors_le_observed']:.2f} |",
    "",
]
(ROOT / "generated_tables.md").write_text("\n".join(lines))
print(ROOT / "generated_tables.md")
'''


def build_review_materials() -> None:
    REVIEW.mkdir(parents=True, exist_ok=True)
    build_scientific_records()
    (REVIEW / "code").mkdir(exist_ok=True)
    (REVIEW / "code" / "verify_review_results.py").write_text(VERIFY_SCRIPT)
    (REVIEW / "code" / "generate_review_tables.py").write_text(TABLE_SCRIPT)
    (REVIEW / "README.md").write_text(
        "# Review materials\n\n"
        "These materials accompany *Regime maps for exact quantum compilation separate "
        "expressivity, certificates and feature transfer*.\n\n"
        "The `exact_results` directory exposes the scientific values needed to inspect the "
        "three exact model-specific results, the finite state-preparation study, the frozen "
        "transfer panel, and the retained adverse and conditional results.  The per-state panel "
        "record includes all 120 canonical states, 127 ordered features, labels, folds, predictions, "
        "errors, earlier prospective predictions and the full 200-permutation null distribution.\n\n"
        "The records deliberately exclude project-management provenance.  They do not change any "
        "scientific value used in the manuscript.  The checks are same-team consistency checks, not "
        "external replication or independent proof review.\n"
    )
    (REVIEW / "REPRODUCE.md").write_text(
        "# Reproduction order\n\n"
        "Requirements: Python 3.10 or later; the included checks use only the standard library.\n\n"
        "1. Run `python3 code/verify_review_results.py`.\n"
        "2. Run `python3 code/generate_review_tables.py`.\n"
        "3. Compare `generated_tables.md` with the corresponding manuscript tables.\n"
        "4. Inspect `exact_results/state_preparation_panel.json` for the complete per-state panel and null distribution.\n\n"
        "The Supplementary Information gives the formal models, proof compositions and exact null algorithm.\n"
    )
    subprocess.run([sys.executable, "code/verify_review_results.py"], cwd=REVIEW, check=True)
    subprocess.run([sys.executable, "code/generate_review_tables.py"], cwd=REVIEW, check=True)


SECTION_MAP = {
    "01-introduction.tex": "introduction.tex",
    "02-methods.tex": "methods.tex",
    "03-results.tex": "results.tex",
    "04-discussion.tex": "discussion.tex",
    "05-related-work-boundary.tex": "related_work.tex",
    "06-limitations.tex": "limitations.tex",
    "07-conclusion.tex": "conclusion.tex",
    "08-reproducibility.tex": "data_and_code_availability.tex",
    "09-ethics-safety-resources.tex": "ethics_and_author_statement.tex",
}


def build_source_tree() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    (SOURCE / "sections").mkdir(exist_ok=True)
    main = (MANUSCRIPT / "main.tex").read_text()
    for old, new in SECTION_MAP.items():
        main = main.replace(f"sections/{old[:-4]}", f"sections/{new[:-4]}")
        shutil.copy2(MANUSCRIPT / "sections" / old, SOURCE / "sections" / new)
    (SOURCE / "main.tex").write_text(main)
    for name in (
        "supplement.tex",
        "bibliography.bib",
        "main.bbl",
        "supplement.bbl",
        "generated_results_tables.tex",
        "generated_support_tables.tex",
        "quantumarticle.cls",
    ):
        shutil.copy2(MANUSCRIPT / name, SOURCE / name)
    (SOURCE / "README.md").write_text(
        "# Source package\n\n"
        "Source for *Regime maps for exact quantum compilation separate expressivity, "
        "certificates and feature transfer*.\n\n"
        "Build the article with `tectonic main.tex` and the Supplementary Information with "
        "`tectonic supplement.tex`.  The bibliography outputs are included.\n"
    )


def build_submission_documents() -> None:
    shutil.copy2(MANUSCRIPT / "main.pdf", OUT / "main.pdf")
    shutil.copy2(MANUSCRIPT / "supplement.pdf", OUT / "supplement.pdf")
    (OUT / "cover_letter.md").write_text(
        "# Cover letter\n\n"
        "Dear Editors,\n\n"
        "Please consider the manuscript *Regime maps for exact quantum compilation separate "
        "expressivity, certificates and feature transfer* as an Original Research Article in "
        "*Quantum*.\n\n"
        "The manuscript presents three exact, model-specific results and one retained adverse "
        "transfer study.  It proves an all-size support-two normalization for a shared-tag Pauli "
        "block model, establishes intrinsic support one together with an explicit objective-validity "
        "region for a rank-two dependent-triple model, and gives an exact three-clause pair-gain "
        "boundary for a six-term linear-combination model.  A complete finite stabilizer-state study "
        "then shows that a nearly injective in-domain feature representation does not improve on the "
        "specified shuffle null when transferred to the frozen next-size panel.\n\n"
        "The organizing contribution is a typed comparison record that prevents proof ceilings, "
        "intrinsic support, certificate regions, finite feature determination and prospective transfer "
        "from borrowing authority from one another.  The manuscript does not claim a universal "
        "compiler law, hardware advantage, external replication or feature generalization.  The "
        "adverse outcomes, low panel coverage and null result remain explicit.\n\n"
        "The accompanying Supplementary Information states the formal models and proof obligations.  "
        "Separate review materials expose the exact scientific values, the complete per-state panel, "
        "a standard-library verifier and table regeneration code.\n\n"
        "Sincerely,\n\n"
        "Sze Chun Yiu\n"
        "sze-chun.yiu@fysik.su.se\n"
    )
    (OUT / "availability_statement.md").write_text(
        "# Data and code availability statement\n\n"
        "The review materials accompanying *Regime maps for exact quantum compilation separate "
        "expressivity, certificates and feature transfer* contain the exact scientific records, "
        "analysis descriptions, complete per-state panel, table-generation code and a separate "
        "standard-library verifier needed to check every headline number.  The Supplementary "
        "Information gives the formal models, proof obligations and deterministic reproduction order.  "
        "No permanent public archive identifier or reuse licence is currently asserted.\n"
    )
    author_only = OUT / "author_only"
    author_only.mkdir(exist_ok=True)
    (author_only / "HUMAN_INPUT_CHECKLIST.md").write_text(
        "# Author confirmation checklist\n\n"
        "This file is for the author and submission operator; it is not a reviewer-facing attachment.\n\n"
        "- [ ] Confirm the complete institutional affiliation.\n"
        "- [ ] Confirm whether an ORCID identifier will be supplied.\n"
        "- [ ] Supply the funding statement.\n"
        "- [ ] Supply the competing-interest statement.\n"
        "- [ ] Supply acknowledgements, or confirm that none are required.\n"
        "- [ ] Approve the sole-author contribution statement.\n"
        "- [ ] Approve the generative-artificial-intelligence disclosure.\n"
        "- [ ] Supply the public preprint identifier and licence.\n"
        "- [ ] Supply the permanent review-materials archive URL and reuse licence.\n"
        "- [ ] Inspect the exact final PDFs and approve the scientific claims and wording.\n"
        "- [ ] Confirm the primary venue choice and authorize filing.\n"
    )


FORBIDDEN = {
    "internal paper identifier": re.compile(r"(?i)\b(?:orion(?:[-_ ]?\d+)?|qg[-_ ]?\d+[a-z]*|p\d+[-_][a-z0-9_-]+|r\d+[a-z])\b"),
    "internal terminal": re.compile(r"(?i)(?:blocked_on_author_evidence|cannot_check|submission[_ -]?ready|machine[_ -]?checked|same[_ -]?project[_ -]?custody)"),
    "internal path": re.compile(r"(?i)(?:/Users/|research/extensions/|papers/orion|editorial/|\.git(?:/|\\b))"),
    "workflow history": re.compile(r"(?i)(?:pull request|\bpr\s*#\s*\d+|issue\s*#\s*\d+|git commit|github\.com/SzeChunYiu/ORION)"),
    "content hash": re.compile(r"(?i)(?:sha[-_ ]?256|checksum|\bdigest\b|\b[0-9a-f]{40,64}\b)"),
    "placeholder": re.compile(r"(?i)(?:\?\?|\bTODO\b|\bTBD\b|\ufffd)"),
}


def audit_tree(root: Path) -> None:
    failures: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        for label, pattern in FORBIDDEN.items():
            if pattern.search(relative):
                failures.append(f"{relative}: entry name contains {label}")
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for label, pattern in FORBIDDEN.items():
            match = pattern.search(text)
            if match:
                failures.append(f"{relative}: {label}: {match.group(0)!r}")
    if failures:
        raise AssertionError("review-surface audit failed:\n" + "\n".join(failures))


def deterministic_zip(tree: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in tree.rglob("*") if item.is_file()):
            relative = path.relative_to(tree).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def audit_zip(path: Path) -> None:
    failures: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names != sorted(names):
            failures.append("entries are not sorted")
        for name in names:
            for label, pattern in FORBIDDEN.items():
                if pattern.search(name):
                    failures.append(f"{name}: entry name contains {label}")
            data = archive.read(name)
            try:
                text = data.decode()
            except UnicodeDecodeError:
                continue
            for label, pattern in FORBIDDEN.items():
                match = pattern.search(text)
                if match:
                    failures.append(f"{name}: {label}: {match.group(0)!r}")
    if failures:
        raise AssertionError(f"{path.name} audit failed:\n" + "\n".join(failures))


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    build_review_materials()
    build_source_tree()
    build_submission_documents()
    audit_tree(REVIEW)
    audit_tree(SOURCE)
    deterministic_zip(REVIEW, OUT / "review_materials.zip")
    deterministic_zip(SOURCE, OUT / "source.zip")
    audit_zip(OUT / "review_materials.zip")
    audit_zip(OUT / "source.zip")
    audit_tree(OUT)
    print(
        json.dumps(
            {
                "review_files": sum(item.is_file() for item in REVIEW.rglob("*")),
                "source_files": sum(item.is_file() for item in SOURCE.rglob("*")),
                "archives": ["review_materials.zip", "source.zip"],
                "forbidden_matches": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
