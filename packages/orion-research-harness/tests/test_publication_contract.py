from orion.registry import Q3_HARNESS_PUBLICATION_CONTRACT_ID as REGISTRY_CONTRACT_ID
from orion_research_harness.publication_contract import (
    Q3_HARNESS_PUBLICATION_CONTRACT_ID,
    Q3_HARNESS_REQUIRED_PROPERTIES,
    q3_publication_contract,
    validate_q3_publication_contract,
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
