from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg13_v3_three_column import QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST

def test_manifest_valid(): validate_manifest(QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST)
def test_terminal_paths_distinct():
 c=QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST['capabilities'];assert c['v3.cand']['next_phase']=='CANDIDATE_RECORDED';assert c['v3.closednew']['next_phase']=='CLOSEDNEW_RECORDED';assert c['v3.obs']['next_phase']=='OBSTRUCTION_RECORDED';assert c['v3.res']['next_phase']=='RESOURCE_RECORDED'
def test_non_authorizing():
 assert QG13V3_THREE_COLUMN_CAMPAIGN_MANIFEST['authority_ceiling']=='NON_AUTHORIZING_THREE_COLUMN_EVIDENCE'
