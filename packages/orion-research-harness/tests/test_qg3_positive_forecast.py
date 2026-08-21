from orion_research_harness.campaign_control import (
    decide_campaign,
    manifest_digest,
    validate_manifest,
)
from orion_research_harness.campaign_protocol import CampaignState, ProtectedReference
from orion_research_harness.domains.orion_qg import (
    QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST,
)


def _state(observations: dict[str, str]) -> CampaignState:
    manifest = QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST
    return CampaignState.create(
        campaign_id=manifest["campaign_id"],
        claim_id=manifest["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=(),
        protected_refs=tuple(
            ProtectedReference.from_dict(row) for row in manifest["protected_refs"]
        ),
        authority_ceiling=manifest["authority_ceiling"],
    )


def test_qg3_manifest_validates() -> None:
    validate_manifest(QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST)


def test_qg3_native_opens_only_fully_admissible_positive() -> None:
    state = _state(
        {
            "QG3_POSITIVE_FOUND": "YES",
            "QG3_NATIVE_CUSTODY_AGGREGATE": "YES",
            "QG3_STAGE1_DIGEST": "a" * 64,
        }
    )
    decision = decide_campaign(state, QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST)
    assert (
        decision.responsibility["identified_hypothesis_id"]
        == "RESP:QG3_POSITIVE_ADMISSIBLE"
    )
    assert decision.selected_id == "REV:OPEN_POSITIVE_REFEREE"
    assert decision.selected_kind == "REVISION"
    assert decision.computation["status"] == "LOCAL_COMPUTATION_STOP"


def test_qg3_native_stops_honestly_when_frozen_scan_has_no_positive() -> None:
    state = _state(
        {
            "QG3_POSITIVE_FOUND": "NO",
            "QG3_NATIVE_CUSTODY_AGGREGATE": "YES",
            "QG3_STAGE1_DIGEST": "b" * 64,
        }
    )
    decision = decide_campaign(state, QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST)
    assert (
        decision.responsibility["identified_hypothesis_id"]
        == "RESP:QG3_NO_POSITIVE"
    )
    assert decision.selected_id == "REV:STOP_NO_POSITIVE"
    assert decision.selected_kind == "REVISION"


def test_qg3_native_rejects_failed_stage1_custody() -> None:
    state = _state(
        {
            "QG3_POSITIVE_FOUND": "YES",
            "QG3_NATIVE_CUSTODY_AGGREGATE": "NO",
            "QG3_STAGE1_DIGEST": "c" * 64,
        }
    )
    decision = decide_campaign(state, QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG3_INVALID"
    assert decision.selected_id == "REV:STOP_INVALID"
    assert decision.selected_kind == "REVISION"


def test_qg3_invalid_custody_dominates_even_when_no_positive() -> None:
    state = _state(
        {
            "QG3_POSITIVE_FOUND": "NO",
            "QG3_NATIVE_CUSTODY_AGGREGATE": "NO",
            "QG3_STAGE1_DIGEST": "d" * 64,
        }
    )
    decision = decide_campaign(state, QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:QG3_INVALID"
    assert decision.selected_id == "REV:STOP_INVALID"
