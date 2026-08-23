"""Metadata-only lifecycle adjudication for P9-U-T3's frontier status."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from orion.study.p9.frontier_grid import assess_grid

ROOT = Path(__file__).resolve().parents[4]
STATUS = ROOT / "papers/paper-09-structured-epistemic-learning/evidence/P9_U_T3_FRONTIER_GRID_STATUS_2026-08-21.json"
SCHEMA = "ORION.P9.T3FrontierStatusMetadataAmendment.v1"


def canonical(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def without_environment(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "environment_agreement"}


def build_amendment(repo_root: Path = ROOT) -> dict[str, Any]:
    predecessor = json.loads(STATUS.read_text(encoding="utf-8"))
    replay = assess_grid({}, (), repo_root=repo_root)
    replay["outcomes_file"] = None
    if without_environment(replay) != predecessor:
        raise ValueError("P9 T3 replay changes frozen scientific coordinates, not metadata only")
    shared = sha256(canonical(predecessor)).hexdigest()
    return {
        "schema": SCHEMA,
        "paper_id": "P9",
        "claim_id": "P9_U_T3_FRONTIER_GRID",
        "relation": "AMENDS_METADATA_ONLY",
        "predecessor": str(STATUS.relative_to(ROOT)),
        "predecessor_sha256": sha256(STATUS.read_bytes()).hexdigest(),
        "replay_sha256": sha256(canonical(replay)).hexdigest(),
        "shared_scientific_payload_sha256": shared,
        "added_metadata": {"environment_agreement": replay["environment_agreement"]},
        "scientific_coordinates_unchanged": True,
        "verdict": replay["verdict"],
        "outcome": replay["outcome"],
        "executed_cells": replay["census"]["cells_executed"],
        "declared_cells": replay["census"]["declared_cells"],
        "authority": "PROVENANCE_CORRECTION_ONLY__GRANTS_NO_SCIENTIFIC_PROMOTION",
    }


__all__ = ["SCHEMA", "build_amendment", "without_environment"]
