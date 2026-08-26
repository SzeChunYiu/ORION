from __future__ import annotations

import json
from pathlib import Path

from orion.study.p9.frontier_status_lifecycle import build_amendment

ROOT = Path(__file__).resolve().parents[4]
ARTIFACT = ROOT / "papers/orion-19-structured-epistemic-learning/evidence/P9_U_T3_FRONTIER_GRID_METADATA_AMENDMENT_2026-08-22.json"


def test_metadata_amendment_replays_exactly() -> None:
    actual = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert actual == build_amendment(ROOT)
    assert actual["relation"] == "AMENDS_METADATA_ONLY"
    assert actual["scientific_coordinates_unchanged"] is True
    assert actual["executed_cells"] == 0
    assert actual["declared_cells"] == 1344
    assert actual["outcome"] == "CANNOT_CHECK"


def test_environment_metadata_cannot_promote_the_grid() -> None:
    actual = build_amendment(ROOT)
    assert actual["authority"] == "PROVENANCE_CORRECTION_ONLY__GRANTS_NO_SCIENTIFIC_PROMOTION"
    assert actual["added_metadata"]["environment_agreement"]["measured"]["measured_on_this_machine"] is True
