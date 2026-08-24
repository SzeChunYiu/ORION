from __future__ import annotations

import importlib.util
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_a_a1_multitag import (
    PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST
    names = (
        "SOURCE_DIGEST",
        "GENERIC_DIGEST",
        "POSITIVE",
        "GATES",
        "GENERIC",
        "RESTORE",
        "SIGNATURES",
        "DESCENT",
        "PARENT",
        "SCOPE",
        "NO_SHARP",
        "NO_OUTSIDE",
        "NO_TRANSFER",
        "NO_NOVELTY",
        "NO_PHYSICAL",
    )
    observations = {f"PAPER_A_A1_{name}": "YES" for name in names}
    observations["PAPER_A_A1_POSITIVE"] = positive
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
    path = root / "research/extensions/orion-qg/paper_a_a1_multitag_tare.py"
    spec = importlib.util.spec_from_file_location("paper_a_a1_multitag_tare", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_a_a1_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST)
    text = repr(PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST)
    assert "DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_a_a1_native_accepts_complete_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_a_a1_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_a_a1_restore_bound_is_exact() -> None:
    observed = _analyzer().restore_ledger()
    assert observed["all_checks"] is True
    assert observed["row_count"] == 768
    assert observed["histogram"] == {"-2": 18, "-1": 144, "0": 444, "1": 144, "2": 18}


def test_paper_a_a1_signatures_and_descent_are_machine_correlated() -> None:
    analyzer = _analyzer()
    signatures = analyzer.signature_ledger()
    descent = analyzer.descent_ledger()
    assert signatures["all_checks"] is True
    assert [(row["tag_count"], row["distinct_observed"]) for row in signatures["rows"]] == [
        (s, 1 << (s + 1)) for s in range(9)
    ]
    assert descent["all_checks"] is True
    assert [(row["dimension"], row["failures"]) for row in descent["exhaustive_small_dimensions"]] == [
        (1, 0), (2, 0), (3, 0)
    ]
