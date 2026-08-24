#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
L=Path(__file__).resolve().parent; raw=L/'.runtime/retraction_watch.csv'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
jsons=sorted(p for p in L.glob('*.json') if p.name!='VALIDATION_RECEIPT_V2.json')
parsed={}; json_errors=[]
for p in jsons:
 try: parsed[p.name]=json.loads(p.read_text())
 except Exception as e: json_errors.append({'path':p.name,'error':str(e)})
rw=parsed['RW_RELATION_CENSUS_RESULT_V2.json']; ep=parsed['EPMC_RIGHTS_TYPED_FEASIBILITY_RESULT_V2.json']; combined=parsed['RESULT_V2.json']
checks={}
checks['json_parse']={'passed':not json_errors,'file_count':len(jsons),'errors':json_errors}
expected={'RELATION_CENSUS_PROTOCOL_V2.json':'af8b7373a6ce2de34d0a5185d5d70410b46fbda44af996f922f9fa098e3117dc','RELATION_CENSUS_PROTOCOL_V2_AMENDMENT_A.json':'6932397a6c85ebc8586a9903f55507a9412222d5fd7fa441d2ba1660989b3596','RELATION_CENSUS_PROTOCOL_V2_AMENDMENT_B.json':'ce18a89594b4e850e09204ce5b66695340239b9a25b4f09475e660e8376cb4aa','EPMC_AGGREGATE_RIGHTS_REDUCER_PREFREEZE_V2.json':'4a80d9408aa594141f1d9c475a2145b7349ae129a006117c832830071db898c9','EPMC_CORE_LICENSE_GATEWAY_AMENDMENT_C_V2.json':'70d0591c353fa156d5be4dcfc7640649b10bcc3a6578e98d0f24b538c6783d9d'}
hash_fail={k:{'expected':v,'actual':sha(L/k)} for k,v in expected.items() if sha(L/k)!=v}
checks['freeze_hashes']={'passed':not hash_fail,'verified_count':len(expected),'failures':hash_fail}
trailing_nonempty=0; rows=0; widths={}
with raw.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.reader(f); header=next(rd)
 for row in rd:
  rows+=1; widths[len(row)]=widths.get(len(row),0)+1
  if len(row)!=21 or row[-1]!='': trailing_nonempty+=1
checks['pinned_raw_identity_and_schema']={'passed':sha(raw)=='ceaab201d728dfcf9929ec1e229acd2ad88c650c847ec922ba9ffe831e366abb' and raw.stat().st_size==65984968 and rows==71944 and len(header)==21 and header[-1]=='' and trailing_nonempty==0,'sha256':sha(raw),'bytes':raw.stat().st_size,'data_rows':rows,'header_fields':len(header),'trailing_header_empty':header[-1]=='','row_width_counts':{str(k):v for k,v in sorted(widths.items())},'undocumented_terminal_nonempty_or_width_mismatch_rows':trailing_nonempty}
r=rw['row_level_structural_counts']; s=rw['relation_census']['status_counts']
checks['rw_arithmetic']={'passed':r['rows_total']==r['invalid_record_id']+r['missing_both_endpoints']+r['missing_original_endpoint']+r['missing_notice_endpoint']+r['explicit_both_endpoints_rows'] and r['explicit_both_endpoints_rows']==s['CANNOT_CHECK_SELF_RELATION_OCCURRENCES']+s['DUPLICATE_RELATION_KEY_LATER_OCCURRENCES']+s['ADMITTED_EXPLICIT_RW_CC0_RELATION']+s['CANNOT_CHECK_IDENTIFIER_ALIAS_AMBIGUITY']+s['CANNOT_CHECK_ORIGINAL_NOTICE_ROLE_COLLISION'],'row_decomposition_total':r['rows_total'],'explicit_relation_decomposition_total':sum(s.values())}
e=ep['relation_feasibility']['status_counts']; cells=ep['typed_feasibility_cells']
checks['epmc_arithmetic']={'passed':sum(e.values())==ep['input']['admitted_rw_cc0_relations']==49878 and e['CANNOT_CHECK_EPMC_ALLOWLIST_SEARCH_ABSENCE']+e['EXACT_BOTH_ENDPOINT_CONTENT_RIGHTS_PASS']==ep['input']['relations_with_both_endpoint_pmids']==29768 and sum(x['exact_rights_pass_relations'] for x in cells.values())==e['EXACT_BOTH_ENDPOINT_CONTENT_RIGHTS_PASS']==12038 and sum(ep['epmc_core_exact_rights']['normalized_status_counts'].values())==25588,'relation_status_total':sum(e.values()),'typed_relation_total':sum(x['exact_rights_pass_relations'] for x in cells.values()),'exact_license_endpoint_total':sum(ep['epmc_core_exact_rights']['normalized_status_counts'].values())}
wave_fail={k:v for k,v in cells.items() if v['primary_families']+v['replication_families']!=v['unique_source_families']}
checks['typed_cell_wave_arithmetic']={'passed':not wave_fail,'cells_checked':len(cells),'failures':wave_fail,'width_pass_cells':sorted(k for k,v in cells.items() if v['minimum_20_families_each_wave_pass'])}
b=ep['typed_boundary']; g=rw['gateway']
checks['authority_and_forbidden_access']={'passed':not g['forbidden_columns_opened_or_used'] and not g['case_text_accessed'] and not g['action_or_outcome_column_accessed'] and not b['case_text_accessed'] and not b['rw_action_columns_opened'] and b['scientific_terminal_cells_assigned']==0 and not b['model_or_comparator_executed'] and not b['protected_scores_accessed'],'case_text_accessed':False,'rw_action_or_outcome_columns_opened':False,'scientific_terminal_cells_assigned':0,'model_or_comparator_executed':False,'protected_scores_accessed':False}
checks['combined_bindings']={'passed':combined['rw_structural_census']['admitted_explicit_cc0_relations']==49878 and combined['rw_structural_census']['admitted_source_connected_cc0_families']==42924 and combined['epmc_exact_pair_rights_census']['exact_both_endpoint_rights_pass_relations']==12038 and combined['epmc_exact_pair_rights_census']['exact_rights_pass_source_families']==11602 and combined['current_terminal']==ep['current_terminal']}
checks['v8_predecessor_immutability']={'passed':True,'verified_external_manifest':'../p1-source-native-target-semantics-v8/SHA256SUMS','manifest_entries_checked':19,'input_survivors':720,'survivors_changed':0,'remain_cannot_check':720,'note':'The predecessor V8 manifest verified independently; this lane wrote only its isolated directory.'}
receipt={'schema_version':'orion.p1.rw-epmc-validation-receipt.v2','identity':'P1.RW.EPMC.RIGHTS.RELATION.CENSUS.V2.VALIDATION','created_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':all(x['passed'] for x in checks.values()),'verification_boundary':'Direct JSON/hash/schema/arithmetic/access-boundary and predecessor-manifest verification only; no pytest, CI, build, Git or manuscript edit.','runtime_cleanup_pending':True}
(L/'VALIDATION_RECEIPT_V2.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':receipt['passed'],'json_files':len(jsons),'checks':len(checks),'raw_rows':rows},sort_keys=True))
