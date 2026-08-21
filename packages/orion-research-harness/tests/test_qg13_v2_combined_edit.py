from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg13_v2_combined_edit import QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST


def test_manifest_valid():
    validate_manifest(QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST)


def test_three_scientific_acceptance_paths_are_distinct():
    m = QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST
    caps = m["capabilities"]
    assert caps["qg13v2.candidate"]["next_phase"] == "CANDIDATE_RECORDED"
    assert caps["qg13v2.obstruction"]["next_phase"] == "OBSTRUCTION_RECORDED"
    assert caps["qg13v2.resource"]["next_phase"] == "RESOURCE_RECORDED"


def test_authority_ceiling_is_non_authorizing():
    m = QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST
    assert m["authority_ceiling"] == "NON_AUTHORIZING_COMBINED_EDIT_EVIDENCE"
    for name in ("qg13v2.candidate", "qg13v2.obstruction", "qg13v2.resource"):
        vals = m["capabilities"][name]["result_contract"]["required_payload_values"]
        assert {"path": ["new_theorem_authority"], "equals": False} in vals
        assert {"path": ["novelty_authority"], "equals": False} in vals
        assert {"path": ["support4_theorem_authority"], "equals": False} in vals
