from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_rg.nonquantum_m1_tail_corridor import (
    NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST
    names = (
        "SOURCE_DIGEST",
        "GENERIC_DIGEST",
        "POSITIVE",
        "GATES",
        "GENERIC",
        "PARENTS",
        "RECURRENCE",
        "D4_OPEN",
        "SUPPORT_NONAGGREGABLE",
        "NO_D4_31_TAIL",
        "SCOPE",
        "NO_NOVELTY",
        "NO_QUANTUM",
    )
    observations = {f"NONQUANTUM_M1_{name}": "YES" for name in names}
    observations["NONQUANTUM_M1_POSITIVE"] = positive
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
    path = root / "research/orion-rg/nonquantum_m1_dk_tail_corridor.py"
    spec = importlib.util.spec_from_file_location("nonquantum_m1_dk_tail_corridor", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nonquantum_m1_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST)
    text = repr(NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST)
    assert "DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY" in text
    assert "exact_d4_authority': True" not in text
    assert "support_23_theorem_authority': True" not in text
    assert "novelty_authority': True" not in text


def test_nonquantum_m1_native_accepts_complete_evidence() -> None:
    decision = decide_campaign(_state(), NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_nonquantum_m1_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_nonquantum_m1_recurrence_is_exact_on_small_instances() -> None:
    analyzer = _analyzer()
    assert analyzer.upper_tail(8, 31) == {4: 31, 5: 36, 6: 41, 7: 46, 8: 51}
    assert analyzer.upper_tail(8, 30) == {4: 30, 5: 35, 6: 40, 7: 45, 8: 50}
    assert analyzer.lower(8) == 50


def test_nonquantum_m1_saved_result_preserves_open_boundary() -> None:
    root = Path(__file__).resolve().parents[3]
    result = json.loads(
        (root / "research/orion-rg/NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json").read_text()
    )
    assert result["theorem"]["current_exact_gate"] == "D_4 in {30,31}"
    assert result["theorem"]["d4_31_tail_consequence"] == "NOT_DETERMINED"
    assert result["exact_d4_authority"] is False
    assert result["support_frontier"]["used_in_tail_proof"] is False
    assert result["support_frontier"]["aggregable_as_theorem"] is False
    assert result["support_23_theorem_authority"] is False
    assert result["novelty_authority"] is False
