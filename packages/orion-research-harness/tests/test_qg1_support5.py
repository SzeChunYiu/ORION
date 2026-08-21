from orion_research_harness.campaign_control import (
    decide_campaign,
    manifest_digest,
    validate_manifest,
)
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg import QG1_SUPPORT5_CAMPAIGN_MANIFEST


def _state(observations: dict[str, str]) -> CampaignState:
    manifest = QG1_SUPPORT5_CAMPAIGN_MANIFEST
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


def test_qg1_manifest_validates() -> None:
    validate_manifest(QG1_SUPPORT5_CAMPAIGN_MANIFEST)


def test_qg1_native_accepts_only_bound_positive_theorem() -> None:
    state = _state(
        {
            "QG1_ACCEPT": "YES",
            "QG1_CUSTODY": "YES",
            "QG1_POSITIVE": "YES",
            "QG1_GENERIC_PASS": "YES",
            "QG1_RESULT_DIGEST": "a" * 64,
        }
    )
    decision = decide_campaign(state, QG1_SUPPORT5_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG1_ACCEPT"
    assert decision.selected_kind == "REVISION"
    assert decision.selected_id == "REV:QG1_ACCEPT"
    assert decision.computation["status"] == "LOCAL_COMPUTATION_STOP"


def test_qg1_native_rejects_scientific_negative_without_host_failure() -> None:
    state = _state(
        {
            "QG1_ACCEPT": "NO",
            "QG1_CUSTODY": "YES",
            "QG1_POSITIVE": "NO",
            "QG1_GENERIC_PASS": "NO",
            "QG1_RESULT_DIGEST": "b" * 64,
        }
    )
    decision = decide_campaign(state, QG1_SUPPORT5_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG1_REJECT"
    assert decision.selected_kind == "REVISION"
    assert decision.selected_id == "REV:QG1_REJECT"


def test_qg1_native_cannot_check_dominates_custody_failure() -> None:
    state = _state(
        {
            "QG1_ACCEPT": "NO",
            "QG1_CUSTODY": "NO",
            "QG1_POSITIVE": "YES",
            "QG1_GENERIC_PASS": "YES",
            "QG1_RESULT_DIGEST": "c" * 64,
        }
    )
    decision = decide_campaign(state, QG1_SUPPORT5_CAMPAIGN_MANIFEST)
    assert (
        decision.responsibility["identified_hypothesis_id"]
        == "RESP:QG1_CANNOT_CHECK"
    )
    assert decision.selected_kind == "REVISION"
    assert decision.selected_id == "REV:QG1_CANNOT"


def test_qg1_native_never_grants_scientific_or_novelty_authority() -> None:
    state = _state(
        {
            "QG1_ACCEPT": "YES",
            "QG1_CUSTODY": "YES",
            "QG1_POSITIVE": "YES",
            "QG1_GENERIC_PASS": "YES",
            "QG1_RESULT_DIGEST": "d" * 64,
        }
    )
    decision = decide_campaign(state, QG1_SUPPORT5_CAMPAIGN_MANIFEST)
    assert decision.unsigned()["grants_scientific_authority"] is False
    assert decision.unsigned()["grants_novelty_authority"] is False
    assert decision.unsigned()["grants_adoption_authority"] is False
