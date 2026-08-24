from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_rg.nonquantum_m3_support10 import (
    NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST
    names = (
        "SOURCE_DIGEST", "GENERIC_DIGEST", "POSITIVE", "GATES", "GENERIC", "PATTERNS",
        "DUAL", "SCOPE", "BOUNDED", "NO_SUPPORT11", "NO_SUPPORT23", "NO_EXTERNAL",
        "NO_PROSPECTIVE", "NO_C0", "NO_D4", "NO_NOVELTY", "NO_QUANTUM",
    )
    observations = {f"NONQUANTUM_M3_{name}": "YES" for name in names}
    observations["NONQUANTUM_M3_POSITIVE"] = positive
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


def _analyzer():
    root = Path(__file__).resolve().parents[3]
    path = root / "research/orion-rg/nonquantum_m3_support10_replay.py"
    spec = importlib.util.spec_from_file_location("nonquantum_m3_support10_replay", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nonquantum_m3_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST)
    text = repr(NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST)
    assert "BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY" in text
    assert "support_11_plus_theorem_authority': True" not in text
    assert "support_23_theorem_authority': True" not in text
    assert "exact_d4_authority': True" not in text


def test_nonquantum_m3_native_accepts_complete_evidence() -> None:
    decision = decide_campaign(_state(), NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_nonquantum_m3_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_nonquantum_m3_pattern_equations_are_complete() -> None:
    analyzer = _analyzer()
    ledger = analyzer.pattern_ledger()
    assert ledger["all_checks"] is True
    assert ledger["patterns"] == [[1, 3, 6], [3, 0, 7]]


def test_nonquantum_m3_saved_result_preserves_authority_boundary() -> None:
    root = Path(__file__).resolve().parents[3]
    result = json.loads(
        (root / "research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json").read_text()
    )
    assert result["bounded_support_le10_theorem_authority"] is True
    assert result["support_11_plus_theorem_authority"] is False
    assert result["support_23_theorem_authority"] is False
    assert result["independent_external_replay_complete"] is False
    assert result["prospective_validation_authority"] is False
    assert result["c0_31_authority"] is False
    assert result["exact_d4_authority"] is False
    assert result["novelty_authority"] is False
