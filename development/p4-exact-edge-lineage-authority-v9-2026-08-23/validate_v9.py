#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
checks=[]
def ok(name,cond):
 checks.append({'check':name,'pass':bool(cond)})
 if not cond: raise AssertionError(name)
def load(n): return json.loads((R/n).read_text())
# Every declared JSON artifact is machine-readable.
json_files=sorted(p for p in R.rglob('*.json') if p.name!='VALIDATION_RECEIPT_V9.json')
for p in json_files: json.loads(p.read_text())
ok('all_json_parse',len(json_files)>=20)
prot=load('PROTOCOL_V9.json');fr=load('PROTOCOL_FREEZE_RECEIPT_V9.json')
ok('protocol_hash',hashlib.sha256((R/'PROTOCOL_V9.json').read_bytes()).hexdigest()==fr['sha256'])
ok('seven_frozen_targets',len(prot['targets'])==7 and [x['frozen_index'] for x in prot['targets']]==[36,91,133,165,185,190,199])
res=load('RESULT_V9.json')
ok('closed_2_of_7',res['v9_closed_count']==2 and res['v9_closed_indices']==[165,190])
ok('remaining_5_of_7',res['v9_remaining_count']==5 and res['v9_remaining_indices']==[36,91,133,185,199])
ok('cumulative_75_of_80',res['cumulative_exact_bridge']=='75/80' and sum(res['cumulative_exact_by_domain'].values())==75)
pay=load('EXACT_EDGE_PAYLOAD_COMPARISON_V9.json');pr={x['frozen_index']:x for x in pay['rows']}
ok('index_165_exact_293',pr[165]['exact_normalized_manifest_equal'] and pr[165]['archive_file_count']==pr[165]['commit_file_count']==293)
e190=load('EDGE_190_CONTENT_COMPARISON_V9.json')['receipts']['compare_archive_pre_joss_main']
ok('index_190_exact_355',e190['equal'] and e190['counts']==[355,355] and e190['different_count']==0)
ok('index_190_rights',load('EDGE_190_COMMIT_RIGHTS_V9.json')['byte_equal'])
e91=load('EDGE_91_EMBEDDED_GIT_AUTHORITY_V9.json')
ok('index_91_adverse_head',e91['head']=='aa021231cdafb6d74ce9ab5f55f824a3032058a4' and not e91['accepted_commit_object_present'])
e199=load('EDGE_199_FULL_COMMIT_PROVIDER_VERIFICATION_V9.json')['rows']
ok('index_199_provider_fail_closed',all(e199[k]['status']==404 for k in ['commit_html','codeload','raw_license']))
ok('index_199_swh_fail_closed',all(x['status']==404 for x in load('EDGE_199_SWH_FULL_REVISION_V9.json')['rows'].values()))
lin=load('LINEAGE_NATURAL_PAIR_AUTHORITY_V9.json')
ok('orcid_counts',lin['counts']=={'publication_authors':30,'crossref_orcid_identified':27,'zenodo_orcid_identified':26,'cross_provider_exact_orcid_matches':26,'crossref_only_orcid':1,'name_only_publication_authors':3})
ok('lineage_fail_closed',lin['adjudication']['author_lineage_independence']=='CANNOT_CHECK' and lin['adjudication']['author_lineage_adjudications_added']==0)
ok('natural_pair_fail_closed',lin['adjudication']['natural_pair_eligibility']=='CANNOT_CHECK' and lin['adjudication']['natural_pairs_added']==0)
probe=load('PRIMARY_AUTHORITY_PROBE_RECEIPT_V9.json')
paths=[R/q['body_path'] for x in probe['rows'] for q in x['requests']]
ok('primary_probe_70_bodies_retained',len(paths)==70 and all(p.is_file() for p in paths))
for name,meta in res['evidence'].items(): ok('evidence_hash_'+name,hashlib.sha256((R/name).read_bytes()).hexdigest()==meta['sha256'])
ok('no_scientific_authority',res['natural_pair_and_scientific_boundary']['scientific_authority_granted'] is False)
receipt={'schema_version':'orion.p4.exact-edge-lineage-authority.v9.validation','validation_basis':'deterministic packet-local structural, hash and scientific-boundary checks','json_file_count_excluding_receipt':len(json_files),'check_count':len(checks),'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'checks':checks,'pytest_run':False,'repository_ci_run':False,'git_operation_run':False}
(R/'VALIDATION_RECEIPT_V9.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'checks':len(checks),'passed':receipt['passed'],'json_files':len(json_files)},sort_keys=True))
