#!/usr/bin/env python3
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
