#!/usr/bin/env python3
"""Export the exact frozen state-preparation panel and transfer calculation.

This exporter is intentionally separate from the scientific result generator.
It exposes the already-frozen feature vectors, folds, labels, predictions and
shuffle controls in one reader-auditable record without changing the analysis.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research" / "extensions" / "orion-qg"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(QG))
sys.path.insert(0, str(SCRIPTS))

import qg15_third_family as q15  # noqa: E402
import qg15c_vocabulary as v15c  # noqa: E402
from qg15c_enlarged_vocab import donor_path_features  # noqa: E402
from r2_revive_stabprep_l3_vocabulary import l3_vector  # noqa: E402


PAPER = ROOT / "papers" / "orion-09-compilation-regime-geometry"
OUT = PAPER / "evidence" / "STATE_PREPARATION_PANEL_RECORDS_V1.json"
RICH_RESULT = PAPER / "evidence" / "R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json"
EARLY_RESULT = QG / "QG15_THIRD_FAMILY_RESULTS.json"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats_names(prefix: str) -> list[str]:
    return [f"{prefix}_min", f"{prefix}_max", f"{prefix}_sum_squares", f"{prefix}_zero_count"]


def feature_names() -> list[str]:
    path = [f"gate_total_{kind}" for kind in ("H", "S", "SDG", "CX")]
    for channel in ("H", "S", "SDG", "CX_IN", "CX_OUT"):
        path.extend(stats_names(f"per_qubit_{channel}"))
    path.extend(
        [
            "directed_CX_edges_used",
            "directed_CX_edge_max_multiplicity",
            "directed_CX_edge_sum_squares",
            "reciprocal_CX_pairs",
            "CX_indegree_max",
            "CX_outdegree_max",
            "CX_indegree_sum_squares",
            "CX_outdegree_sum_squares",
        ]
    )
    for left in ("H", "S", "SDG", "CX"):
        for right in ("H", "S", "SDG", "CX"):
            path.append(f"adjacent_transition_{left}_to_{right}")
    path.extend(["first_gate_kind", "last_gate_kind", "gate_kind_runs", "max_gate_kind_run", "distinct_gate_kinds"])
    assert len(path) == 53

    state = ["negative_sign_count"]
    for prefix in ("positive_weight", "negative_weight", "positive_Y_count", "negative_Y_count"):
        state.extend(f"{prefix}_{value}" for value in range(5))
    for prefix in ("positive_binary_parity_class", "negative_binary_parity_class"):
        state.extend(f"{prefix}_{value}" for value in range(4))
    for letter in ("X", "Y", "Z"):
        state.extend(stats_names(f"per_qubit_{letter}_column_marginal"))
    assert len(state) == 41

    names = list(v15c.V2_FEATURES) + path + state
    assert len(names) == 127 and len(set(names)) == 127
    return names


def lookup_rows(vectors: list[tuple[int, ...]], labels: list[bool]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict() for _ in vectors]
    for heldout_parity in (0, 1):
        train: dict[tuple[int, ...], list[int]] = {}
        for index, (vector, label) in enumerate(zip(vectors, labels)):
            if index % 2 == heldout_parity:
                continue
            cell = train.setdefault(vector, [0, 0])
            cell[0 if label else 1] += 1
        for index, (vector, label) in enumerate(zip(vectors, labels)):
            if index % 2 != heldout_parity:
                continue
            seen = vector in train
            counts = train.get(vector, [0, 0])
            prediction = counts[0] > counts[1] if seen else False
            rows[index] = {
                "fold": heldout_parity,
                "covered": seen,
                "training_cell_positive": counts[0],
                "training_cell_negative": counts[1],
                "prediction": prediction,
                "error": prediction != label,
            }
    return rows


def cv_errors(vectors: list[tuple[int, ...]], labels: list[bool]) -> tuple[int, int, int]:
    rows = lookup_rows(vectors, labels)
    errors = sum(bool(row["error"]) for row in rows)
    covered = sum(bool(row["covered"]) for row in rows)
    covered_errors = sum(bool(row["covered"]) and bool(row["error"]) for row in rows)
    return errors, covered, covered_errors


def main() -> int:
    names = feature_names()
    rich = json.loads(RICH_RESULT.read_text())
    early = json.loads(EARLY_RESULT.read_text())
    early_by_index = {row["index"]: row for row in early["component5_prospective"]["predictions"]}

    panel = q15.build_panel()
    dist4 = q15.referee(4)
    vectors: list[tuple[int, ...]] = []
    labels: list[bool] = []
    donor_costs: list[int] = []
    for state in panel:
        vector, donor_cost = l3_vector(state, 4)
        vectors.append(vector)
        donor_costs.append(donor_cost)
        labels.append(dist4[state] == donor_cost)

    lookup = lookup_rows(vectors, labels)
    panel_cells = Counter(vectors)
    cell_sizes = sorted(panel_cells.values())
    mixed = 0
    for vector in panel_cells:
        labs = {label for item, label in zip(vectors, labels) if item == vector}
        mixed += int(len(labs) > 1)

    rng = random.Random(20260828)
    null_distribution = [cv_errors(vectors, rng.sample(labels, len(labels)))[0] for _ in range(200)]
    errors, covered, covered_errors = cv_errors(vectors, labels)

    records = []
    for index, (state, vector, label, donor_cost, lookup_row) in enumerate(
        zip(panel, vectors, labels, donor_costs, lookup)
    ):
        previous = early_by_index[index]
        assert previous["canonical_key"] == list(state)
        records.append(
            {
                "index": index,
                "canonical_state_key": list(state),
                "feature_vector": list(vector),
                "panel_feature_cell_size": panel_cells[vector],
                "donor_cost": donor_cost,
                "exact_cost": dist4[state],
                "donor_exact_label": label,
                **lookup_row,
                "earlier_forecast": {
                    "predicted_donor_exact": previous["predicted_donor_exact"],
                    "predicted_exact_cost": previous["predicted_C_opt"],
                },
            }
        )

    result = {
        "schema": "ORION09.state_preparation_panel.v1",
        "analysis_status": "frozen_adverse_result_exposed_for_review",
        "panel_generation": {
            "n": 4,
            "states": 120,
            "seed": 20260821,
            "gates_per_candidate": 24,
            "duplicates_discarded": True,
            "gate_draw": "uniform over H,S,SDG,CX; uniform qubit or ordered distinct control-target as applicable",
            "canonical_keys_sha256": hashlib.sha256(canonical([list(state) for state in panel]).encode()).hexdigest(),
        },
        "reference_compiler": {
            "algorithm": "ascending-qubit deterministic stabilizer Gaussian elimination; minimum-key X pivot; forced signed-Z fallback",
            "gate_costs": q15.COST,
            "exact_referee": "Dijkstra over all 36,720 four-qubit stabilizer states",
        },
        "feature_schema": {
            "count": len(names),
            "ordered_names": names,
            "groups": [
                {"name": "schedule_and_tensor", "start": 0, "stop": 33},
                {"name": "reference_synthesis_path", "start": 33, "stop": 86},
                {"name": "sign_aware_state", "start": 86, "stop": 127},
            ],
        },
        "transfer_rule": {
            "fold": "panel index parity",
            "match": "exact equality of the 127-coordinate vector",
            "seen_cell_prediction": "strict positive majority; tie predicts negative",
            "unseen_cell_prediction": "negative",
            "coverage": "test vector occurs in the opposite-parity training fold",
        },
        "panel_partition": {
            "feature_cells": len(panel_cells),
            "singleton_cells": sum(size == 1 for size in cell_sizes),
            "doubleton_cells": sum(size == 2 for size in cell_sizes),
            "larger_cells": sum(size > 2 for size in cell_sizes),
            "mixed_cells": mixed,
            "cell_sizes_sum": sum(cell_sizes),
        },
        "observed": {
            "positive_labels": sum(labels),
            "errors": errors,
            "covered": covered,
            "errors_among_covered": covered_errors,
            "errors_among_uncovered": errors - covered_errors,
        },
        "shuffle_null": {
            "shuffled_unit": "the 120 observed labels",
            "preserved": "feature vectors, state order, parity folds, lookup rule and negative default",
            "permutations": 200,
            "python_seed": 20260828,
            "tail": "fraction with errors no larger than observed",
            "error_counts": null_distribution,
            "mean": sum(null_distribution) / len(null_distribution),
            "minimum": min(null_distribution),
            "maximum": max(null_distribution),
            "empirical_p_errors_le_observed": sum(value <= errors for value in null_distribution) / len(null_distribution),
        },
        "freeze_provenance": {
            "feature_stage_digest_before_four_qubit_referee": rich["stage1_digest"],
            "earlier_forecast_predictions_sha256": early["component5_prospective"]["predictions_sha256"],
            "earlier_forecast_stamped_before_referee": early["component5_prospective"]["predictions_stamped_before_referee"],
        },
        "source_digests": {
            str(RICH_RESULT.relative_to(ROOT)): sha256(RICH_RESULT),
            str(EARLY_RESULT.relative_to(ROOT)): sha256(EARLY_RESULT),
            "scripts/r2_revive_stabprep_l3_vocabulary.py": sha256(SCRIPTS / "r2_revive_stabprep_l3_vocabulary.py"),
        },
        "records": records,
    }

    assert result["panel_partition"] == {
        "feature_cells": 119,
        "singleton_cells": 118,
        "doubleton_cells": 1,
        "larger_cells": 0,
        "mixed_cells": 0,
        "cell_sizes_sum": 120,
    }
    assert result["observed"] == {
        "positive_labels": 32,
        "errors": 32,
        "covered": 2,
        "errors_among_covered": 0,
        "errors_among_uncovered": 32,
    }
    assert result["shuffle_null"]["mean"] == 32.41
    assert result["shuffle_null"]["empirical_p_errors_le_observed"] == 0.51
    assert result["panel_generation"]["canonical_keys_sha256"] == rich["stage2"]["panel_keys_sha256"]

    unsigned = canonical(result)
    result["result_digest"] = hashlib.sha256(unsigned.encode()).hexdigest()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(canonical({"output": str(OUT), "cells": 119, "errors": errors, "shuffle_p": 0.51}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
