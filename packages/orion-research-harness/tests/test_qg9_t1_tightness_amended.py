from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg9_t1_tightness_amended import QG9T1_TIGHTNESS_AMENDED_CAMPAIGN_MANIFEST as M

def test_amended_manifest_valid(): validate_manifest(M)
def test_amendment_keeps_non_authorizing_negative():
 vals=M['capabilities']['t1.negative']['result_contract']['required_payload_values'];assert {'path':['support3_theorem_authority'],'equals':False} in vals
def test_amendment_has_distinct_campaign_identity(): assert M['campaign_id']=='orion-qg:qg9t1-support4-tightness-amended1'
