"""P11I replay adjudication with the corrected independent-unit hierarchy."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

SUPPORTED = "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL"
NOT_REPLICATED = "P11I_HIGH_WIDTH_ADVANTAGE_NOT_REPLICATED"
PRECONDITION_FAILED = "P11I_INSTRUMENT_PRECONDITION_NOT_MET"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-11-state-as-computation"
ORIGINAL_RESULT = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json"
AMENDMENT = PAPER / "P11I_REPLICATION_UNIT_AMENDMENT_V1_1.md"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def adjudicate_scientific_payload(
    scientific_payload: Mapping[str, Any], *, byte_identical_replay: bool
) -> dict[str, Any]:
    payload = deepcopy(scientific_payload)
    seeds = tuple(payload.get("seeds", ()))
    geometries = tuple(tuple(item) for item in payload.get("bank_geometries", ()))
    high = payload.get("high_width_units", [])
    low = payload.get("low_width_controls", [])
    target = payload.get("target_accuracy")
    delta_threshold = payload.get("delta64_threshold")

    panel_complete = (
        len(seeds) == len(set(seeds)) == 3
        and len(geometries) == len(set(geometries)) == 3
        and len(high) == len(low) == 9
        and {(row.get("seed"), tuple(row.get("bank_geometry", ()))) for row in high}
        == {(seed, geometry) for seed in seeds for geometry in geometries}
        and {(row.get("seed"), tuple(row.get("bank_geometry", ()))) for row in low}
        == {(seed, geometry) for seed in seeds for geometry in geometries}
    )
    high_pass = panel_complete and all(
        row.get("compiled_at_64", float("-inf")) >= target
        and row.get("pooled_best_below_256", float("inf")) < target
        and row.get("delta64_vs_pool", float("-inf")) >= delta_threshold
        for row in high
    )
    attack_live = panel_complete and all(
        row.get("pooled_best_below_256", float("-inf")) >= target for row in low
    )
    no_laundering = payload.get("instrument_gates", {}).get("no_answer_laundering") is True
    instrument_pass = panel_complete and attack_live and no_laundering and byte_identical_replay
    terminal = PRECONDITION_FAILED if not instrument_pass else SUPPORTED if high_pass else NOT_REPLICATED
    cells_by_seed = {
        str(seed): sum(row.get("seed") == seed for row in high) for seed in seeds
    }
    return {
        "schema": "ORION.P11I.WidePanelRevalidation.v1.1",
        "independent_unit": "execution_seed",
        "n_independent_rng_replicates": len(seeds),
        "fixed_geometry_strata_per_replicate": len(geometries),
        "n_prespecified_seed_x_geometry_cells": len(high),
        "cells_by_seed": cells_by_seed,
        "gates": {
            "complete_three_seed_x_three_geometry_panel": panel_complete,
            "all_nine_high_width_cells_pass": high_pass,
            "matched_low_width_attack_live_in_all_nine_cells": attack_live,
            "no_answer_laundering": no_laundering,
            "byte_identical_replay": byte_identical_replay,
        },
        "terminal": terminal,
    }


def build_revalidation_receipt(
    scientific_payload: Mapping[str, Any], *, replay_sha256: str, byte_identical: bool
) -> dict[str, Any]:
    adjudication = adjudicate_scientific_payload(
        scientific_payload, byte_identical_replay=byte_identical
    )
    return {
        "schema": "ORION.P11I.RevalidationReceipt.v1.1",
        "paper_id": "P11",
        "original_result": str(ORIGINAL_RESULT.relative_to(REPO_ROOT)),
        "original_result_sha256": file_sha256(ORIGINAL_RESULT),
        "replication_unit_amendment": str(AMENDMENT.relative_to(REPO_ROOT)),
        "replication_unit_amendment_sha256": file_sha256(AMENDMENT),
        "fresh_scientific_payload_sha256": replay_sha256,
        "adjudication": adjudication,
        "active_terminal_unchanged": adjudication["terminal"] == SUPPORTED,
        "authority_boundary": "three_independent_rng_replicates_nine_prespecified_cells",
    }


__all__ = [
    "NOT_REPLICATED",
    "PRECONDITION_FAILED",
    "SUPPORTED",
    "adjudicate_scientific_payload",
    "build_revalidation_receipt",
    "canonical_text",
]
