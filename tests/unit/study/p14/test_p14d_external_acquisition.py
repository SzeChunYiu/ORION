from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p14.external_acquisition import (
    BLOCKED_TERMINAL,
    INPUT_DIRECTORY,
    REQUIRED_ARTIFACTS,
    build_external_acquisition_preflight,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-14-orion-rse"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_committed_preflight_matches_fail_closed_inventory() -> None:
    committed = json.loads(
        (PAPER / "P14D_EXTERNAL_ACQUISITION_PREFLIGHT_V1.json").read_text(encoding="utf-8")
    )
    assert committed == build_external_acquisition_preflight(ROOT)
    assert committed["terminal"] == BLOCKED_TERMINAL
    assert committed["execution_authorized"] is False
    assert committed["missing_artifacts"] == list(REQUIRED_ARTIFACTS)


def test_locally_authored_complete_looking_packet_cannot_self_certify_custody(
    tmp_path: Path,
) -> None:
    input_root = tmp_path / INPUT_DIRECTORY
    input_root.mkdir(parents=True)
    for artifact in REQUIRED_ARTIFACTS:
        (input_root / artifact).write_text('{"claims_independent": true}\n', encoding="utf-8")

    preflight = build_external_acquisition_preflight(tmp_path)
    assert preflight["missing_artifacts"] == []
    assert preflight["trusted_external_custody_verifier_configured"] is False
    assert preflight["external_custody_verified"] is False
    assert preflight["execution_authorized"] is False
    assert preflight["terminal"] == BLOCKED_TERMINAL


def test_active_authority_binds_acquisition_protocol_preflight_and_validator() -> None:
    authority = json.loads((PAPER / "P14_ACTIVE_CLAIM_AUTHORITY_V1.json").read_text())
    acquisition = authority["prospective_external_validation"]
    assert acquisition["execution_authorized"] is False
    assert acquisition["terminal"] == BLOCKED_TERMINAL
    for prefix in ("protocol", "preflight", "validator"):
        path = (PAPER / acquisition[f"{prefix}_artifact"]).resolve()
        assert acquisition[f"{prefix}_sha256"] == _sha(path)
