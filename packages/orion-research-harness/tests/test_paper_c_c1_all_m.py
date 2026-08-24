from __future__ import annotations

import importlib.util
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_c_c1_all_m import (
    PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST
    observations = {
        "PAPER_C_C1_SOURCE_DIGEST": "YES",
        "PAPER_C_C1_GENERIC_DIGEST": "YES",
        "PAPER_C_C1_POSITIVE": positive,
        "PAPER_C_C1_GATES": "YES",
        "PAPER_C_C1_GENERIC": "YES",
        "PAPER_C_C1_M5_N2": "YES",
        "PAPER_C_C1_M4_SHARP": "YES",
        "PAPER_C_C1_PARENT": "YES",
        "PAPER_C_C1_FOUR_INDEX": "YES",
        "PAPER_C_C1_SCOPE": "YES",
        "PAPER_C_C1_NO_VALUE": "YES",
        "PAPER_C_C1_NO_OPTIMIZER": "YES",
        "PAPER_C_C1_NO_NOVELTY": "YES",
        "PAPER_C_C1_NO_PHYSICAL": "YES",
    }
    return CampaignState.create(
        campaign_id=manifest["campaign_id"],
        claim_id=manifest["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=(),
        protected_refs=(),
        authority_ceiling=manifest["authority_ceiling"],
    )


def _analyzer_module():
    root = Path(__file__).resolve().parents[3]
    path = root / "research" / "extensions" / "orion-qg" / "paper_c_c1_all_m_decision.py"
    spec = importlib.util.spec_from_file_location("paper_c_c1_all_m_decision", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_c_c1_manifest_validates_and_is_bounded() -> None:
    validate_manifest(PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST)
    text = repr(PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST)
    assert PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST["protected_refs"] == []
    assert "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_c_c1_native_accepts_only_complete_bounded_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_c_c1_native_rejects_refutation() -> None:
    decision = decide_campaign(_state("NO"), PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_c_c1_registered_m4_counterexample_is_exact() -> None:
    sharp = _analyzer_module().sharp_m4_counterexample()
    assert sharp["all_checks"] is True
    assert sharp["observed"]["p4"] is True
    assert sharp["observed"]["unary_cost"] == 27
    assert sharp["observed"]["optimum_cost"] == 23


def test_paper_c_c1_symbolic_ledger_closes_only_frozen_scope() -> None:
    ledger = _analyzer_module().proof_ledger()
    assert ledger["all_checks"] is True
    assert "m>=5" in ledger["theorem"]
