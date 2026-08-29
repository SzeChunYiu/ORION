from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def _verify_manifest(directory: Path) -> None:
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((directory / relative).read_bytes()).hexdigest() == digest


def test_orion11_primary_falsification_and_replication_fault_remain_distinct() -> None:
    base = "papers/orion-11-recursive-epistemic-reconstruction/experiments/r4-faithful-comparator-v1"
    protocol = _load(f"{base}/ORION11_R4_FAITHFUL_COMPARATOR_PROTOCOL.json")
    primary = _load(f"{base}/result/primary/ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json")
    replication = _load(
        f"{base}/result/replication/ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json"
    )
    disposition = _load(f"{base}/AUTHORITY_DISPOSITION_V1.json")

    assert protocol["arms_executed"] is False
    assert protocol["outcome_accessed"] is False
    assert primary["anchor_reproduction_gate"]["passed"] is True
    assert primary["verdict"] == "H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION"
    assert replication["anchor_reproduction_gate"]["passed"] is False
    assert replication["verdict"] == "INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ"
    assert "WITHDRAW_COMPARATIVE_NECESSITY_READING" in disposition["scientific_authority_delta"]
    _verify_manifest(ROOT / base)


def test_orion15_harvest_preserves_imperfect_result_and_bounded_authority() -> None:
    base = "papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2"
    report = _load(f"{base}/report.json")
    disposition = _load(f"{base}/AUTHORITY_DISPOSITION_V1.json")

    assert report["arms"]["control"]["correct"] == 22
    assert report["arms"]["treatment"]["correct"] == 23
    assert "PERFECT_CEILING_NOT_REPRODUCED" in disposition["terminal"]
    assert disposition["scientific_authority_delta"] == "BOUNDED_DESCRIPTIVE_DIRECTION_ONLY"
    assert "external independence" in disposition["forbidden_promotions"]
    _verify_manifest(ROOT / base)


def test_orion19_custody_probe_grants_no_scientific_result() -> None:
    base = "papers/orion-19-structured-epistemic-learning/experiments/ut3-checkpoint-custody-v1"
    receipt = _load(f"{base}/job-3550343/P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json")
    disposition = _load(f"{base}/AUTHORITY_DISPOSITION_V1.json")

    assert receipt["produces_scientific_result"] is False
    assert receipt["ladder_points_in_custody"] == 4
    assert receipt["ladder_points_declared"] == 6
    assert disposition["scientific_cells_executed"] == 0
    assert disposition["scientific_authority_delta"] == "NONE"
    _verify_manifest(ROOT / base)


def test_orion21_post_outcome_readjudication_is_quarantined() -> None:
    base = "papers/orion-21-state-as-computation/experiments/nr07-width-law-falsification-v1"
    original = _load(
        f"{base}/authoritative-job-3550337/NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json"
    )
    later = _load(
        f"{base}/quarantine-post-outcome-readjudication/NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1_1.json"
    )
    disposition = _load(f"{base}/POST_OUTCOME_PROTOCOL_DEVIATION_DISPOSITION_V1.json")

    assert original["instrument_precondition_p0"]["passed"] is False
    assert original["adjudication"]["verdict"] == "CANNOT_CHECK_INSTRUMENT_DRIFT"
    assert later["instrument_precondition_p0"]["declared_tolerance"] == 0.001
    assert later["adjudication"]["verdict"] == "C1_LAW_CONFIRMED_REGIME_EXTENDED"
    assert disposition["authoritative_terminal"] == "CANNOT_CHECK_INSTRUMENT_DRIFT"
    assert disposition["scientific_authority_delta"] == "NONE"
    _verify_manifest(ROOT / base)
