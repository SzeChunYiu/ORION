from orion.registry import Q3_HARNESS_PUBLICATION_CONTRACT_ID as REGISTRY_CONTRACT_ID
from orion_research_harness.publication_contract import (
    Q3_HARNESS_PUBLICATION_CONTRACT_ID,
    Q3_HARNESS_REQUIRED_PROPERTIES,
    q3_publication_contract,
    validate_q3_publication_contract,
)
from orion_research_harness.campaign_protocol import (
    CAMPAIGN_DECISION_SCHEMA,
    CAMPAIGN_STATE_SCHEMA,
    CAMPAIGN_TRANSITION_SCHEMA,
    authority_false,
)


def test_q3_publication_contract_matches_framework_registry():
    assert Q3_HARNESS_PUBLICATION_CONTRACT_ID == REGISTRY_CONTRACT_ID
    validate_q3_publication_contract()
    contract = q3_publication_contract()
    assert contract["schema"] == REGISTRY_CONTRACT_ID
    assert tuple(contract["required_properties"]) == Q3_HARNESS_REQUIRED_PROPERTIES
    assert contract["sample_request_id_prefix_valid"] is True


def test_q3_publication_contract_is_non_authorizing():
    contract = q3_publication_contract()
    assert contract["grants_scientific_authority"] is False
    assert contract["grants_novelty_authority"] is False
    assert contract["grants_security_certification"] is False


def test_campaign_schema_exports_and_all_authority_fields_are_exact():
    assert (
        CAMPAIGN_STATE_SCHEMA,
        CAMPAIGN_DECISION_SCHEMA,
        CAMPAIGN_TRANSITION_SCHEMA,
    ) == (
        "ORION.ResearchCampaignState.v1",
        "ORION.ResearchCampaignDecision.v1",
        "ORION.ResearchCampaignTransition.v1",
    )
    assert authority_false() == {
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "grants_global_task_stop_authority": False,
    }
