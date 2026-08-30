#!/usr/bin/env python3
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
