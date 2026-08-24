from __future__ import annotations

import importlib.util
from pathlib import Path

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_b_b1_proof_gap import (
    PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST
    names = (
        "SOURCE_DIGEST",
        "GENERIC_DIGEST",
        "POSITIVE",
        "GATES",
        "GENERIC",
        "PRODUCTION",
        "PRODUCT",
        "PARENTS",
        "NOBROAD",
        "SCOPE",
        "NO_NOVELTY",
        "NO_PHYSICAL",
    )
    observations = {f"PAPER_B_B1_{name}": "YES" for name in names}
    observations["PAPER_B_B1_POSITIVE"] = positive
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
    path = root / "research/extensions/orion-qg/paper_b_b1_rank_only_proof_gap.py"
    spec = importlib.util.spec_from_file_location("paper_b_b1_rank_only_proof_gap", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_b_b1_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST)
    text = repr(PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST)
    assert "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_b_b1_native_accepts_complete_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_b_b1_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_b_b1_basis_words_are_rank_sharp() -> None:
    analyzer = _analyzer()
    qg6 = __import__("json").loads(analyzer.QG6_RESULT.read_text())
    observed = analyzer.production_rank_sharpness(qg6)
    assert observed["all_checks"] is True
    assert observed["certificate_complexity"] == 5
    assert observed["intrinsic_support"] == 1


def test_paper_b_b1_product_gap_is_4t() -> None:
    product = _analyzer().product_ledger()
    assert product["all_checks"] is True
    assert [(row["copies"], row["additive_gap"]) for row in product["rows"]] == [
        (1, 4),
        (2, 8),
        (3, 12),
        (10, 40),
        (100, 400),
    ]

