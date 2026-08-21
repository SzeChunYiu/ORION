from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.orion_qg.qg13_v4_support4 import QG13V4_SUPPORT4_CAMPAIGN_MANIFEST

def test_manifest_valid(): validate_manifest(QG13V4_SUPPORT4_CAMPAIGN_MANIFEST)
def test_four_theorem_obligations_are_explicit():
 phase=QG13V4_SUPPORT4_CAMPAIGN_MANIFEST['phases']['D0'];scopes={x['scope'] for x in phase['interface_checks']};assert {'LOCAL_LEMMA','SPECTATOR_EXTENSION','PARENT_SUPPORT5','ALL_N_DESCENT'}<=scopes
def test_native_scope_bounded():
 assert QG13V4_SUPPORT4_CAMPAIGN_MANIFEST['authority_ceiling']=='R6I_SUPPORT4_THEOREM_EVIDENCE_ONLY'
