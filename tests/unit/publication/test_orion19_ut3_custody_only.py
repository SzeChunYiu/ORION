from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / (
    "papers/orion-19-structured-epistemic-learning/experiments/"
    "ut3-checkpoint-custody-v1"
)


def _load(relative: str) -> dict:
    return json.loads((BASE / relative).read_text())


def test_ut3_probe_is_custody_only_and_has_zero_scientific_cells() -> None:
    receipt = _load("job-3550343/P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json")
    disposition = _load("AUTHORITY_DISPOSITION_V1.json")

    assert receipt["produces_scientific_result"] is False
    assert receipt["ladder_points_in_custody"] == 4
    assert receipt["ladder_points_declared"] == 6
    assert disposition["scientific_cells_executed"] == 0
    assert disposition["scientific_authority_delta"] == "NONE"
    assert "ZERO_GRID_CELLS_EXECUTED" in disposition["terminal"]


def test_ut3_custody_manifest_binds_every_preserved_artifact() -> None:
    lines = (BASE / "SHA256SUMS").read_text().splitlines()
    assert len(lines) == 8

    for line in lines:
        digest, relative = line.split("  ", 1)
        artifact = BASE / relative
        assert artifact.is_file(), relative
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == digest
