#!/usr/bin/env python3
"""Validate V5 JSON/JSONL, freezes, identity continuity, counts and claim boundaries."""
from __future__ import annotations
import datetime as dt, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
V4=ROOT.parent/'p4-m6-source-provider-successor-v4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_json(p):return json.loads(p.read_text())
def read_jsonl(p):return [json.loads(l) for l in p.open() if l.strip()]
json_files=sorted(ROOT.glob('*.json')); jsonl_files=sorted(ROOT.glob('*.jsonl'))
for p in json_files:read_json(p)
for p in jsonl_files:read_jsonl(p)
protocol=read_json(ROOT/'PROTOCOL_V5.json'); freeze=read_json(ROOT/'PROTOCOL_FREEZE_RECEIPT_V5.json'); manifest=read_json(ROOT/'FROZEN_JOSS_IDENTITIES_V5.json')
checks={}
checks['protocol_freeze_hash']=freeze['protocol_sha256']==sha(ROOT/'PROTOCOL_V5.json')
checks['frozen_manifest_hash']=freeze['identity_manifest_sha256']==sha(ROOT/'FROZEN_JOSS_IDENTITIES_V5.json')
checks['v3_recovery_freeze_hash']=freeze['v3_identity_recovery_sha256']==sha(ROOT/'V3_M6_IDENTITY_RECOVERY_V5.json')
checks['frozen_count_200']=len(manifest['identities'])==manifest['identity_count']==freeze['frozen_identity_count']==200
v4=read_jsonl(V4/'CANDIDATES_V4.jsonl'); v4_dois=[r['publication_doi'] for r in sorted(v4,key=lambda x:x['frozen_index'])]; frozen_dois=[r['publication_doi'] for r in sorted(manifest['identities'],key=lambda x:x['frozen_index'])]
checks['same_v4_200_doi_identities_no_extension']=v4_dois==frozen_dois and len(set(frozen_dois))==200
v3=read_json(ROOT/'V3_M6_IDENTITY_RECOVERY_V5.json')
checks['v3_candidate_source_hash']=v3['source']['candidate_jsonl_sha256_expected_and_observed']==sha(ROOT.parent/'p4-source-universe-successor-v3'/'CANDIDATES_V1.jsonl')
checks['v3_result_source_hash']=v3['source']['result_json_sha256_expected_and_observed']==sha(ROOT.parent/'p4-source-universe-successor-v3'/'RESULT_V1.json')
checks['v3_exact_nine_identity_rows']=v3['counts']['recovered_exact_rows']==len(v3['identities'])==9 and len({(r['object_concept_doi'],r['publication_doi']) for r in v3['identities']})==9
harvest=read_jsonl(ROOT/'HARVEST_RECORDS_V5.jsonl'); github=read_jsonl(ROOT/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl'); bridge=read_jsonl(ROOT/'BRIDGE_ROWS_V5.jsonl')
checks['harvest_exact_frozen_frame']=len(harvest)==200 and [r['publication_doi'] for r in harvest]==frozen_dois
checks['github_resolution_exact_frozen_frame']=len(github)==200 and [r['publication_doi'] for r in github]==frozen_dois
checks['bridge_exact_frozen_frame']=len(bridge)==200 and [r['publication_doi'] for r in bridge]==frozen_dois
result=read_json(ROOT/'RESULT_V5.json'); exact=[r for r in bridge if r['exact_publication_archive_repository_commit_rights_bridge_pass']]
checks['exact_bridge_count_39']=len(exact)==result['counts']['exact_bridge_pass']==39
checks['one_unique_doi_repo_concept_each']=len({(r['publication_doi'],r['joss_repository']) for r in exact})==len(exact)==result['counts']['unique_exact_publication_doi_repository_concepts']
checks['exact_bridge_domain_counts']=result['exact_bridge_by_domain']=={'EARTH_ENVIRONMENT':3,'LIFE_BIOMEDICAL':4,'PHYSICAL_ENGINEERING':2,'SCIENTIFIC_SOFTWARE':30}
checks['dedup_zero_overlap']=all(not any(r['v3_overlap'].values()) for r in bridge) and read_json(ROOT/'V3_V5_CROSS_PROVIDER_DEDUP_AUDIT_V5.json')['overlap']=={'archive_concept_doi_count':0,'archive_version_doi_count':0,'publication_doi_count':0}
cell=read_json(ROOT/'CELL_COUNTS_V5.json')
expected={'EARTH_ENVIRONMENT':5,'LIFE_BIOMEDICAL':4,'SCIENTIFIC_SOFTWARE':36,'PHYSICAL_ENGINEERING':3}
checks['cell_totals']=all(cell['cells'][d]['deduplicated_v3_strict_plus_v5_exact_union']==n for d,n in expected.items()) and cell['all_four_m6_cells_pass'] is False
checks['all_cell_gates_fail']=all(not c['full_source_cell_frame_pass'] for c in cell['cells'].values())
provider=read_json(ROOT/'PROVIDER_FAMILY_AND_LINEAGE_AUDIT_V5.json')
checks['lineage_and_natural_pair_zero']=provider['author_lineage']['externally_adjudicated_independence_count']==0 and provider['natural_pair']['eligible_count']==0 and result['counts']['eligible_natural_pairs']==0
checks['programme_terminal_preserved']='P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK' in result['preserved_terminals'] and result['v5_terminal'].endswith('NATURAL_PAIR_CANNOT_CHECK')
checks['no_outcomes_or_replacements']=result['claim_boundary']['protected_or_system_outcomes_accessed'] is False and result['claim_boundary']['new_doi_identities_added']==0 and result['claim_boundary']['failed_v4_identities_replaced']==0 and result['claim_boundary']['files_versions_tags_commits_or_search_hits_counted_as_n'] is False
checks['all_v4_negative_identities_preserved']=set(result['predecessor_v4_negative_identities_preserved'])=={'CROSS_PROVIDER_CONCEPT_AND_PUBLICATION_DEDUPLICATION','EXACT_PUBLICATION_TO_RELEASE_VERSION_RELATION','EARTH_LIFE_PHYSICAL_CELL_SHORTFALL','SCIENTIFIC_SOFTWARE_SOURCE_DISJOINT_REPLICATION_SHORTFALL','EXACT_RELEASE_RIGHTS','RELEASE_AND_RELATION_ABSENCE','DOMAIN_IDENTIFICATION','AUTHOR_LINEAGE_AND_NATURAL_PAIR_IDENTITY','PREDECESSOR_TRANSPORT'}
checks['result_artifact_hashes']=all(result['artifact_hashes'][k]==sha(p) for k,p in {'bridge_rows':ROOT/'BRIDGE_ROWS_V5.jsonl','cell_counts':ROOT/'CELL_COUNTS_V5.json','cross_provider_dedup':ROOT/'V3_V5_CROSS_PROVIDER_DEDUP_AUDIT_V5.json','provider_lineage':ROOT/'PROVIDER_FAMILY_AND_LINEAGE_AUDIT_V5.json','harvest':ROOT/'HARVEST_RECORDS_V5.jsonl','github_resolution':ROOT/'GITHUB_ARCHIVE_RELATION_RESOLUTION_V5.jsonl','protocol':ROOT/'PROTOCOL_V5.json','frozen_identities':ROOT/'FROZEN_JOSS_IDENTITIES_V5.json'}.items())
if not all(checks.values()):raise AssertionError({k:v for k,v in checks.items() if not v})
receipt={'schema_version':'orion.p4.m6.joss-exact-version-bridge.verify-receipt.v5','created_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'PASS','json_files_validated':len(json_files),'jsonl_files_validated':len(jsonl_files),'checks':checks,'exact_bridge_pass':39,'eligible_natural_pairs':0,'tests_or_ci_run':False,'verification_scope':'JSON_JSONL_HASH_IDENTITY_COUNT_AND_CLAIM_BOUNDARY_ONLY'}
(ROOT/'VERIFY_RECEIPT_V5.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'json':len(json_files),'jsonl':len(jsonl_files)},indent=2))
