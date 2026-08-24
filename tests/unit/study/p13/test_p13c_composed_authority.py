"""P13C composed authority (V3) binds the composed result without promotion."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from orion.study.p13.composed_authority import (
    ACTIVE_TERMINAL,
    COMPOSED_TERMINAL,
    build_composed_claim_authority,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-13-responsibility-carrying-state"
V3_AUTHORITY = PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V3.json"
REPLAY_SHA = "645961cf01afe15f1b5976244b76b846c31d3c6119af4fbbc031e4b2a3611e57"


def test_v3_authority_rebuilds_and_binds_the_composed_result() -> None:
    committed = json.loads(V3_AUTHORITY.read_text(encoding="utf-8"))
    assert committed == build_composed_claim_authority()
    assert committed["active_terminal"] == ACTIVE_TERMINAL
    assert committed["promotion_allowed"] is True

    leaves = {leaf["claim_id"]: leaf for leaf in committed["active_claim_leaves"]}
    composed = leaves["P13C.COMPOSED.SAFETY_EFFICACY"]
    assert composed["terminal"] == COMPOSED_TERMINAL
    result = composed["result"]
    assert result["authenticated_unsafe_reuse"] == 0
    assert result["scheduled_corruptions_rejected"] == "2457/2457"
    assert result["unverified_rcs_unsafe_reuse"] == 330
    assert result["unverified_rcs_unsafe_by_world"] == {
        "FORGED_SUPPORT": 66,
        "OMITTED_SUPPORT": 0,
        "OVERBROAD_SUPPORT": 87,
        "STALE_EPOCH": 177,
    }
    assert result["authenticated_cannot_check_cases"] == 254
    assert result["byte_identical_replay_core_sha256"] == REPLAY_SHA
    assert composed["scope"]["external_validation"] is False


def test_v3_preserves_v2_leaves_and_forbids_external_promotion() -> None:
    authority = build_composed_claim_authority()
    v2 = json.loads((PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V2.json").read_text(encoding="utf-8"))
    assert authority["active_claim_leaves"][:2] == v2["active_claim_leaves"]
    assert authority["historical_boundary_leaf"] == v2["historical_boundary_leaf"]
    for forbidden in v2["forbidden_promotions"]:
        assert forbidden in authority["forbidden_promotions"]
    assert "P13C_COMPOSED_RESULT_AS_EXTERNAL_VALIDATION" in authority["forbidden_promotions"]
    assert "P13C_COMPOSED_RESULT_AS_POPULATION_EVIDENCE" in authority["forbidden_promotions"]
    for key, binding in authority["evidence_bindings"].items():
        assert (ROOT / binding["artifact"]).is_file(), key


def test_manuscript_and_ledger_integrate_p13c_and_the_d7_scope() -> None:
    manuscript = (PAPER / "MANUSCRIPT.md").read_text(encoding="utf-8")
    assert "### 7.5 Composed safety–efficacy (P13C)" in manuscript
    assert COMPOSED_TERMINAL in manuscript
    assert REPLAY_SHA in manuscript
    assert "P13_ACTIVE_CLAIM_AUTHORITY_V3.json" in manuscript
    assert "### 8.1 Scope binding" in manuscript
    assert "two independent experts plus" in manuscript
    assert "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md" in manuscript
    assert "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json" in manuscript

    ledger = (PAPER / "CLAIM_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
    assert COMPOSED_TERMINAL in ledger
    assert "P13_ACTIVE_CLAIM_AUTHORITY_V3.json" in ledger
    assert "SUPPORTED / CONTROLLED P13C" in ledger
    assert "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md" in ledger


def _checker():
    checker_path = PAPER / "check_lifecycle_consolidation_binding_v1.py"
    spec = importlib.util.spec_from_file_location("lifecycle_consolidation_binding", checker_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lifecycle_consolidation_checker_passes_fail_closed() -> None:
    report = _checker().audit(ROOT)
    assert report["status"] == "PASS", report["errors"]
    assert report["p13c_terminal"] == COMPOSED_TERMINAL
    assert report["p14d_terminal"] == "P14D_EXTERNAL_ACQUISITION_BLOCKED"
    assert report["p15_status"] == "SUPPORTED_INTERNAL_PANEL"
    assert report["population_inference"] is False
