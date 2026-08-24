from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_d_d1_authority import (
    PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST
    names = (
        "SOURCE_DIGEST",
        "GENERIC_DIGEST",
        "POSITIVE",
        "GATES",
        "GENERIC",
        "FORMAL",
        "QG5",
        "PAPER_C",
        "DENOMINATOR",
        "NO_PROSPECTIVE",
        "NO_SECOND",
        "NO_FRAMEWORK",
        "SCOPE",
        "NO_NOVELTY",
        "NO_PHYSICAL",
    )
    observations = {f"PAPER_D_D1_{name}": "YES" for name in names}
    observations["PAPER_D_D1_POSITIVE"] = positive
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
    path = root / "research/extensions/orion-qg/paper_d_d1_authority_calculus.py"
    spec = importlib.util.spec_from_file_location("paper_d_d1_authority_calculus", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_d_d1_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST)
    text = repr(PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST)
    assert "FORMAL_STRATIFIED_CERTIFICATE_CALCULUS" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_d_d1_native_accepts_complete_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_d_d1_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_d_d1_alternative_derivation_is_exact() -> None:
    analyzer = _analyzer()
    rules = (((0,), 2), ((1,), 2), ((2,), 3))
    assert analyzer.closure(4, frozenset({0, 1}), frozenset({0}), rules) == frozenset(
        {1, 2, 3}
    )
    assert analyzer.closure(
        4, frozenset({0, 1}), frozenset({0, 1}), rules
    ) == frozenset()


def test_paper_d_d1_saved_result_preserves_adverse_denominator() -> None:
    root = Path(__file__).resolve().parents[3]
    result = json.loads(
        (root / "research/extensions/orion-qg/PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json").read_text()
    )
    qg5 = result["qg5_instantiation"]
    assert qg5["original_benchmark"] == {
        "exact": 9545,
        "total": 9546,
        "errors": 1,
        "universal_exactness": False,
    }
    assert qg5["exact_retraction"] == [
        "ORIGINAL_CLOSED_FORM_EXACTNESS",
        "ORIGINAL_REGIME_LABEL",
    ]
    assert qg5["qg5b_is_prospective_confirmation"] is False
