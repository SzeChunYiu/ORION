#!/usr/bin/env python3
from __future__ import annotations
import collections,datetime as dt,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];V5=REPO/'development/p4-m6-joss-exact-version-bridge-v5-2026-08-23'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jl(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
checks={};details={}
rows=jl(HERE/'BRIDGE_REPAIR_ROWS_V6.jsonl');old=jl(V5/'BRIDGE_ROWS_V5.jsonl');res=json.loads((HERE/'RESULT_V6.json').read_text());neg=json.loads((HERE/'NEGATIVE_RESULT_LEDGER_V6.json').read_text());cells=json.loads((HERE/'CELL_COUNTS_V6.json').read_text());freeze=json.loads((HERE/'PROTOCOL_FREEZE_RECEIPT_V6.json').read_text());waves=json.loads((HERE/'EXECUTION_WAVES_V6.json').read_text())
old41=[r for r in old if r['gates']['v4_provider_qualified_predecessor_preserved'] and not r['exact_publication_archive_repository_commit_rights_bridge_pass']]
checks['same_exact_41_v5_failed_frozen_indices']={r['frozen_index'] for r in rows}=={r['frozen_index'] for r in old41} and len(rows)==41
checks['same_exact_41_publication_dois']={r['publication_doi'] for r in rows}=={r['publication_doi'] for r in old41} and len({r['publication_doi'] for r in rows})==41
checks['one_unit_per_publication_repository']=len({(r['publication_doi'],r['repository']) for r in rows})==41 and all(r['counts_as_unit']==1 for r in rows)
checks['exact_17_repaired_24_unresolved']=sum(r['v6_exact_bridge_repaired'] for r in rows)==17 and sum(not r['v6_exact_bridge_repaired'] for r in rows)==24
checks['repaired_have_all_exact_gates']=all(all(r['repaired_gates'].values()) for r in rows if r['v6_exact_bridge_repaired'])
checks['unresolved_have_a_failed_gate']=all(not all(r['repaired_gates'].values()) for r in rows if not r['v6_exact_bridge_repaired'])
allowed={'SOURCE_NATIVE_ARCHIVE_MANIFEST_EQUALS_GITHUB_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST','QUALIFIED_SWHID_PATH_DIRECTORY_EQUALS_GIT_COMMIT_ROOT_TREE'}
checks['positive_content_methods_closed']=all((r['accepted_content_identity'] or {}).get('content_identity_method') in allowed for r in rows if r['v6_exact_bridge_repaired'])
checks['manifest_equalities_exact']=all(sum(x.get('exact_manifest_match',False) for x in r['accepted_content_identity'].get('source_manifest_comparisons',[]))==1 for r in rows if r['v6_exact_bridge_repaired'] and r['accepted_content_identity']['content_identity_method'].startswith('SOURCE_NATIVE_ARCHIVE'))
checks['swh_git_tree_equalities_exact']=all(r['accepted_content_identity']['source_manifest']['manifest_sha1']==r['accepted_content_identity']['github_manifest']['manifest_sha1']==r['accepted_content_identity']['tree_sha']==r['swh_identity']['resolved_directory_id'] for r in rows if r['v6_exact_bridge_repaired'] and r['accepted_content_identity']['content_identity_method'].startswith('QUALIFIED_SWHID'))
checks['positive_commits_immutable_40hex']=all(re.fullmatch(r'[0-9a-f]{40}',r['exact_commit_sha'] or '') for r in rows if r['v6_exact_bridge_repaired'])
checks['positive_archive_and_commit_rights']=all(r['source_native_archive_spdx'] and r['commit_spdx'] for r in rows if r['v6_exact_bridge_repaired'])
checks['no_natural_pair_or_lineage_promotion']=all(r['author_lineage_independence'].startswith('CANNOT_CHECK') and r['natural_pair_eligibility'].startswith('CANNOT_CHECK') for r in rows) and res['counts']['eligible_natural_pairs']==0 and res['counts']['author_lineage_independence_adjudicated']==0
checks['result_exact_counts']=res['counts']['same_frozen_publication_dois']==200 and res['counts']['v4_provider_qualified_frozen']==80 and res['counts']['v5_exact_pass']==39 and res['counts']['v6_same_identity_repairs']==17 and res['counts']['v6_remaining_unresolved']==24 and res['counts']['final_exact_bridge']==56 and res['counts']['new_or_replacement_publication_dois']==0
checks['domain_repairs_exact']=res['repairs_by_domain']=={'EARTH_ENVIRONMENT':1,'PHYSICAL_ENGINEERING':1,'SCIENTIFIC_SOFTWARE':15}
checks['final_domains_exact']=res['final_exact_bridge_by_domain']=={'EARTH_ENVIRONMENT':4,'LIFE_BIOMEDICAL':4,'PHYSICAL_ENGINEERING':3,'SCIENTIFIC_SOFTWARE':45}
checks['primary_causes_sum_24']=sum(res['primary_mutually_exclusive_unresolved_cause_counts'].values())==24 and res['primary_mutually_exclusive_unresolved_cause_counts']==neg['primary_mutually_exclusive_counts']
checks['all_full_cells_fail']=all(not c['full_cell_frame_pass'] for c in cells.values())
checks['software_total_pass_replication_fail']=cells['SCIENTIFIC_SOFTWARE']['deduplicated_v3_plus_final_exact']==51 and cells['SCIENTIFIC_SOFTWARE']['total_quota_48_pass'] and cells['SCIENTIFIC_SOFTWARE']['joss_primary_quota_24_pass'] and not cells['SCIENTIFIC_SOFTWARE']['figshare_source_disjoint_replication_quota_8_pass'] and not cells['SCIENTIFIC_SOFTWARE']['full_cell_frame_pass']
checks['cell_unions_exact']={d:c['deduplicated_v3_plus_final_exact'] for d,c in cells.items()}=={'EARTH_ENVIRONMENT':6,'LIFE_BIOMEDICAL':4,'PHYSICAL_ENGINEERING':4,'SCIENTIFIC_SOFTWARE':51}
checks['protocol_freeze_hash_valid']=freeze['protocol_sha256']==sha(HERE/'PROTOCOL_V6.json') and freeze['repair_identity_count']==41
checks['result_input_hashes_valid']=all(res['artifact_hashes'][k]==sha(p) for k,p in {'protocol':HERE/'PROTOCOL_V6.json','protocol_freeze':HERE/'PROTOCOL_FREEZE_RECEIPT_V6.json','rows':HERE/'BRIDGE_REPAIR_ROWS_V6.jsonl','harvest_receipt':HERE/'HARVEST_RECEIPT_V6.json','runner':HERE/'run_bridge_repair_v6.py','v5_result':V5/'RESULT_V5.json','v5_rows':V5/'BRIDGE_ROWS_V5.jsonl'}.items())
checks['execution_accounting_final']=waves['final_counts']=={'frozen_units':41,'repaired':17,'unresolved':24,'new_or_replacement_units':0} and waves['pytest_run'] is False and waves['tests_and_ci_run'] is False and waves['commit_push_merge_rebase_run'] is False
checks['no_download_payload_cache_retained']=not (HERE/'cache_v6').exists()
checks['overclaim_boundary_closed']=res['claim_boundary']=={'global_transport_claim':False,'natural_pair_readiness_claim':False,'author_lineage_independence_claim':False,'model_performance_or_superiority_claim':False,'protected_or_system_outcomes_accessed':False,'confirmatory_claim':False,'pilot_disclosure_preserved':True,'scientific_software_total_quota_pass_does_not_override_replication_failure':True}
# Parse every authoritative JSON/JSONL.
json_paths=sorted(HERE.glob('*.json'))
try:
 for p in json_paths:json.loads(p.read_text())
 for p in HERE.glob('*.jsonl'):jl(p)
 checks['all_json_and_jsonl_parse']=True
except Exception as e:checks['all_json_and_jsonl_parse']=False;details['parse_error']=type(e).__name__
checks['all_checks_pass']=all(checks.values())
# The receipt is manifest-bound, so its timestamp must be replay-stable.  Use
# the already frozen result timestamp rather than mutating the receipt on each
# verification run.
receipt={'schema_version':'orion.p4.m6.joss-bridge-repair.verify-receipt.v6','created_at':res['created_at'],'validator':str(Path(__file__).resolve()),'validator_sha256':sha(Path(__file__).resolve()),'command':'rtk python development/p4-m6-joss-bridge-repair-v6-2026-08-23/verify_v6.py','pytest_or_repository_ci_run':False,'checks':checks,'details':details,'terminal':res['terminal'],'artifact_hashes':{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in ('VERIFY_RECEIPT_V6.json','SHA256SUMS')}}
(HERE/'VERIFY_RECEIPT_V6.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'all_checks_pass':checks['all_checks_pass'],'checks':sum(checks.values()),'total':len(checks),'terminal':res['terminal']},sort_keys=True))
raise SystemExit(0 if checks['all_checks_pass'] else 1)
