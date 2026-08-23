from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg9_t1_tightness import QG9T1_TIGHTNESS_CAMPAIGN_MANIFEST

def test_manifest_valid(): validate_manifest(QG9T1_TIGHTNESS_CAMPAIGN_MANIFEST)
def test_negative_does_not_grant_support3_theorem():
 c=QG9T1_TIGHTNESS_CAMPAIGN_MANIFEST['capabilities']['t1.negative']['result_contract']['required_payload_values'];assert {'path':['support3_theorem_authority'],'equals':False} in c
def test_tight_and_negative_paths_distinct():
 c=QG9T1_TIGHTNESS_CAMPAIGN_MANIFEST['capabilities'];assert c['t1.tight']['next_phase']=='TIGHT_RECORDED';assert c['t1.negative']['next_phase']=='NEGATIVE_RECORDED'
