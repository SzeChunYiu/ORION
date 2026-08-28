from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / (
    "papers/orion-21-state-as-computation/experiments/"
    "nr07-width-law-falsification-v1"
)


def _load(relative: str) -> dict:
    return json.loads((BASE / relative).read_text())


def test_nr07_exact_replay_failure_remains_the_controlling_outcome() -> None:
    original = _load(
        "authoritative-job-3550337/NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json"
    )
    later = _load(
        "quarantine-post-outcome-readjudication/"
        "NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1_1.json"
    )
    disposition = _load("POST_OUTCOME_PROTOCOL_DEVIATION_DISPOSITION_V1.json")

    mismatch = original["instrument_precondition_p0"]["rows"][1]
    assert original["environment"]["slurm_job_id"] == "3550337"
    assert original["instrument_precondition_p0"]["passed"] is False
    assert mismatch["cell"] == [14, 3, 3]
    assert mismatch["expected"]["64"] == 0.94912109375
    assert mismatch["observed"]["64"] == 0.949169921875
    assert original["adjudication"]["verdict"] == "CANNOT_CHECK_INSTRUMENT_DRIFT"

    assert later["instrument_precondition_p0"]["declared_tolerance"] == 0.001
    assert later["adjudication"]["verdict"] == "C1_LAW_CONFIRMED_REGIME_EXTENDED"
    assert disposition["authoritative_terminal"] == "CANNOT_CHECK_INSTRUMENT_DRIFT"
    assert disposition["quarantined_terminal"] == "C1_LAW_CONFIRMED_REGIME_EXTENDED"
    assert disposition["scientific_authority_delta"] == "NONE"
    assert all(
        "quarantine-post-outcome-readjudication" not in item["path"]
        for item in disposition["authoritative_artifacts"]
    )


def test_nr07_custody_manifest_binds_every_preserved_artifact() -> None:
    lines = (BASE / "SHA256SUMS").read_text().splitlines()
    assert len(lines) == 8

    for line in lines:
        digest, relative = line.split("  ", 1)
        artifact = BASE / relative
        assert artifact.is_file(), relative
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == digest
