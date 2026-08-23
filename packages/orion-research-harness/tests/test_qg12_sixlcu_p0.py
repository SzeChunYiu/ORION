from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg import QG12_SIXLCU_P0_CAMPAIGN_MANIFEST


def _state(positive: str = "YES") -> CampaignState:
    m = QG12_SIXLCU_P0_CAMPAIGN_MANIFEST
    obs = {
        "QG12_POSITIVE": positive,
        "QG12_DIGEST": "YES",
        "QG12_GATES": "YES",
        "QG12_GENERIC": "YES",
        "QG12_PARTITIONS": "YES",
        "QG12_SHAPES": "YES",
        "QG12_ALL_SHAPES": "YES",
        "QG12_CONVERSE": "YES",
        "QG12_N1": "YES",
        "QG12_N2": "YES",
        "QG12_ZERO_MISMATCH": "YES",
        "QG12_QG4_BOUND": "YES",
        "QG12_NO_EXTERNAL": "YES",
        "QG12_NOVELTY_FALSE": "YES",
    }
    return CampaignState.create(
        campaign_id=m["campaign_id"],
        claim_id=m["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(m),
        observations=obs,
        active_hard_obligations=(),
        protected_refs=(),
        authority_ceiling=m["authority_ceiling"],
    )


def test_qg12_manifest_validates() -> None:
    validate_manifest(QG12_SIXLCU_P0_CAMPAIGN_MANIFEST)
    assert QG12_SIXLCU_P0_CAMPAIGN_MANIFEST["protected_refs"] == []


def test_qg12_accepts_only_the_bounded_sixlcu_theorem() -> None:
    d = decide_campaign(_state(), QG12_SIXLCU_P0_CAMPAIGN_MANIFEST)
    assert d.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert d.selected_kind == "REVISION"
    assert d.selected_id == "REV:ACCEPT"


def test_qg12_rejects_refuted_analyzer() -> None:
    d = decide_campaign(_state("NO"), QG12_SIXLCU_P0_CAMPAIGN_MANIFEST)
    assert d.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert d.selected_id == "REV:REJECT"


def test_qg12_cannot_transfer_pairwise_claim_across_families() -> None:
    text = repr(QG12_SIXLCU_P0_CAMPAIGN_MANIFEST)
    assert "SIXLCU_ONLY" in text
    assert "cross_family_transfer': False" in text
    assert "novelty_authority': True" not in text
    assert "scientific_authority': True" not in text
