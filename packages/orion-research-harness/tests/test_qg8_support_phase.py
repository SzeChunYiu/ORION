from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg import QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST


def _state(positive: str = "YES") -> CampaignState:
    m = QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST
    obs = {
        "QG8_POSITIVE": positive,
        "QG8_DIGEST": "YES", "QG8_GATES": "YES", "QG8_PROOF": "YES",
        "QG8_GENERIC": "YES", "QG8_CONE": "YES", "QG8_O0": "YES",
        "QG8_O1": "YES", "QG8_O2": "YES", "QG8_O1_CONTROL": "YES",
        "QG8_BOUNDARY_OPEN": "YES", "QG8_NOVELTY": "YES",
    }
    return CampaignState.create(
        campaign_id=m["campaign_id"], claim_id=m["claim_id"], phase_id="D0",
        cycle_index=1, manifest_digest=manifest_digest(m), observations=obs,
        active_hard_obligations=(), protected_refs=(), authority_ceiling=m["authority_ceiling"],
    )


def test_qg8_manifest_validates() -> None:
    validate_manifest(QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST)
    assert QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST["protected_refs"] == []


def test_qg8_accepts_bounded_cone_theorem() -> None:
    d = decide_campaign(_state(), QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST)
    assert d.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert d.selected_id == "REV:ACCEPT"
    assert d.selected_kind == "REVISION"


def test_qg8_rejects_refuted_analyzer() -> None:
    d = decide_campaign(_state("NO"), QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST)
    assert d.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert d.selected_id == "REV:REJECT"


def test_qg8_cannot_launder_outside_cone_into_support3_claim() -> None:
    text = repr(QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST)
    assert "NOT_EQUAL_SUPPORT3_REQUIRED" in text
    assert "SUPPORT3_REQUIRED" not in text.replace("NOT_EQUAL_SUPPORT3_REQUIRED", "")
    assert "novelty_authority': True" not in text
    assert "scientific_authority': True" not in text
