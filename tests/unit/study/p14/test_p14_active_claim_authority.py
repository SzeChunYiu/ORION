from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers" / "paper-14-orion-rse"
ACTIVE = PAPER / "P14_ACTIVE_CLAIM_AUTHORITY_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_active_p14_authority_is_positive_p14c_and_content_bound() -> None:
    record = json.loads(ACTIVE.read_text(encoding="utf-8"))
    active = record["active_claim"]
    assert active["status"] == "SUPPORTED"
    assert active["scientific_terminal"] == (
        "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"
    )
    result = PAPER / active["result_artifact"]
    replay = PAPER / active["replay_artifact"]
    assert active["result_sha256"] == _sha(result)
    assert active["replay_sha256"] == _sha(replay)
    assert json.loads(result.read_text())["terminal"] == active["scientific_terminal"]
    replay_payload = json.loads(replay.read_text())
    assert replay_payload["authoritative_terminal"] == active["scientific_terminal"]


def test_p14a_is_pinned_immutable_history_without_active_authority() -> None:
    record = json.loads(ACTIVE.read_text(encoding="utf-8"))
    historical = record["historical_adjudicated_record"]
    artifact = PAPER / historical["artifact"]
    assert historical["sha256"] == _sha(artifact)
    assert historical["authority"] == "NONE"
    assert historical["disposition"] == "RETAINED_GATE_ATTAINABILITY_DEFECT"


def test_unchanged_p14a_thresholds_are_met_on_p14c() -> None:
    record = json.loads(ACTIVE.read_text(encoding="utf-8"))
    resolution = record["threshold_resolution"]
    artifact = PAPER / resolution["artifact"]
    assert resolution["sha256"] == _sha(artifact)
    assert resolution["question_answered"] is True
    assert resolution["p14a_thresholds_unchanged"] == [0.05, 0.08]
    assert all(
        realized >= threshold
        for realized, threshold in zip(
            resolution["p14c_realized_statistics"],
            resolution["p14a_thresholds_unchanged"],
            strict=True,
        )
    )
