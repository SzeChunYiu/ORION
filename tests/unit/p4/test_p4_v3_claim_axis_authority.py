from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from orion.study.p4 import assess_claim_axis

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
REGISTER = P4 / "evidence" / "protected_v3" / "IDENTIFIABILITY_V3.json"
ADJUDICATION = P4 / "evidence" / "audit" / "P4_H3_V3_CLAIM_AXIS_ADJUDICATION_2026-08-22.json"


def _register() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def test_committed_h3_axis_is_authorized_without_claiming_whole_register_pass() -> None:
    assessment = assess_claim_axis(_register(), construction="v3", terminal="CANNOT_CHECK")
    assert assessment.authorized
    assert assessment.authority == "AUTHORIZED_FOR_CLAIM_SCOPE"
    assert assessment.seed_count == 13
    assert assessment.off_axis_residual_count == 4
    assert not assessment.blockers


def test_one_failed_claim_axis_seed_withholds_authority() -> None:
    register = copy.deepcopy(_register())
    entry = register["seed_invariance"]["v3-invariance-00"]["CANNOT_CHECK"]
    entry.update(outcome="FAIL", worst_recovery=0.01)
    assessment = assess_claim_axis(register, construction="v3", terminal="CANNOT_CHECK")
    assert not assessment.authorized
    assert any("v3-invariance-00" in blocker for blocker in assessment.blockers)


def test_unscored_probe_withholds_authority() -> None:
    register = copy.deepcopy(_register())
    register["constructions"]["v3"]["terminals"]["CANNOT_CHECK"]["results"][0][
        "unscored"
    ] = 1
    assessment = assess_claim_axis(register, construction="v3", terminal="CANNOT_CHECK")
    assert not assessment.authorized
    assert "REGISTERED_PROBE_UNSCORED" in assessment.blockers


def test_off_axis_failure_is_disclosed_but_cannot_change_h3_authority() -> None:
    register = copy.deepcopy(_register())
    entry = register["seed_invariance"]["v3-invariance-00"]["BLOCK"]
    entry.update(outcome="FAIL", worst_recovery=0.2)
    assessment = assess_claim_axis(register, construction="v3", terminal="CANNOT_CHECK")
    assert assessment.authorized
    assert assessment.off_axis_residual_count == 5


def test_adjudication_is_bound_to_the_immutable_register() -> None:
    artifact = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    assessment = assess_claim_axis(_register(), construction="v3", terminal="CANNOT_CHECK")
    assert artifact["register_sha256"] == hashlib.sha256(REGISTER.read_bytes()).hexdigest()
    assert artifact["authority"] == assessment.authority
    assert artifact["off_axis_residual_count"] == assessment.off_axis_residual_count
    assert artifact["blockers"] == list(assessment.blockers)
