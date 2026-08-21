from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg import QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST


def _observations(*, analyzer_positive: str = "YES") -> dict[str, str]:
    return {
        "QG6_ANALYZER_POSITIVE": analyzer_positive,
        "QG6_ANALYZER_DIGEST_VALID": "YES",
        "QG6_ANALYZER_GATES": "YES",
        "QG6_GENERIC_ACCEPT": "YES",
        "QG6_R6M_D2": "YES",
        "QG6_R6M_SUPPORT2_RECOVERED": "YES",
        "QG6_R6I_D5": "YES",
        "QG6_R6I_PENDING": "YES",
        "QG6_NO_CHEMISTRY": "YES",
        "QG6_NO_PROTECTED": "YES",
    }


def _state(observations: dict[str, str]) -> CampaignState:
    manifest = QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST
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


def test_qg6_manifest_validates_and_has_no_protected_refs() -> None:
    validate_manifest(QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST)
    assert QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST["protected_refs"] == []


def test_qg6_native_accepts_only_bounded_rank_findings() -> None:
    decision = decide_campaign(
        _state(_observations()), QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST
    )
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG6_ACCEPT"
    assert decision.selected_id == "REV:QG6_ACCEPT_RANK_FINDINGS"
    assert decision.selected_kind == "REVISION"


def test_qg6_native_rejects_failed_analyzer_binding() -> None:
    decision = decide_campaign(
        _state(_observations(analyzer_positive="NO")),
        QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST,
    )
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG6_REJECT"
    assert decision.selected_id == "REV:QG6_REJECT"


def test_qg6_capabilities_cannot_promote_qg1() -> None:
    text = repr(QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST)
    assert "PENDING_QG1" in text
    assert "QG1_THEOREM_ACCEPTED" not in text
    assert "novelty_authority': True" not in text
    assert "scientific_authority': True" not in text
