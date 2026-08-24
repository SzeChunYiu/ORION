#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'p3-public-data-successor-2026-08-23' / 'p3_public_data_adapter.py'
HERE = Path(__file__).resolve().parent
FIX = HERE / 'fixtures_v1_1'
OUT = HERE / 'checks_v1_1'
FIX.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)


def write_jsonl(path: Path, rows):
    path.write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows), encoding='utf-8')


def run(name: str, args: list[str], expect_ok: bool, contains: str | None = None):
    proc = subprocess.run([sys.executable, str(ADAPTER), *args], text=True, capture_output=True)
    passed = proc.returncode == 0 if expect_ok else proc.returncode != 0
    if contains is not None:
        passed = passed and contains in (proc.stdout + proc.stderr)
    record = {'name': name, 'returncode': proc.returncode, 'passed': passed, 'expected_ok': expect_ok, 'expected_text': contains, 'stdout': proc.stdout, 'stderr': proc.stderr}
    if not passed:
        raise SystemExit(json.dumps(record, indent=2))
    return record

base_cases=[]
for i, label in enumerate(['GLUE','OBSTRUCTION','PLURAL','UNRESOLVED'], 1):
    base_cases.append({
      'case_id':f'DIRECT.{i}', 'cluster_id':f'DIRECT.CLUSTER.{i}', 'source_id':'DIRECT_SYNTHETIC', 'panel_id':'DIRECT_MECHANICS_ONLY',
      'left':{'label':f'left-{i}','entity_type':'X','coordinates':{'REFERENT':f'L{i}'},'observedness':{'REFERENT':'OBSERVED'}},
      'right':{'label':f'right-{i}','entity_type':'X','coordinates':{'REFERENT':f'R{i}'},'observedness':{'REFERENT':'OBSERVED'}},
      'required_coordinates':['REFERENT'],
      'provenance':{'source_revision':'SYNTHETIC','builder_id':'DIRECT_REPAIR_CHECK','builder_revision':'1.0.0','left_locator':f'L{i}','right_locator':f'R{i}'}
    })
write_jsonl(FIX/'cases_unsealed.jsonl', base_cases)
records=[]
records.append(run('seal_valid_cases',['seal-cases','--cases',str(FIX/'cases_unsealed.jsonl'),'--out',str(OUT/'cases.jsonl')],True))
cases=[json.loads(x) for x in (OUT/'cases.jsonl').read_text().splitlines()]
truths=['GLUE','OBSTRUCTION','PLURAL','UNRESOLVED']
gold=[]
for case, truth in zip(cases, truths):
    gold.append({'case_id':case['case_id'],'cluster_id':case['cluster_id'],'source_id':case['source_id'],'panel_id':case['panel_id'],'input_digest':case['input_digest'],'true_relation':truth,'identified_relations':[truth],'gold_authority':'OAEI_PUBLIC_REFERENCE','protected_evidence':False,'coordinate_opportunities':{'REFERENT':{'status':'NONZERO','count':1}}})
write_jsonl(FIX/'gold.jsonl',gold)
preds=[]
for case, truth in zip(cases, truths):
    preds.append({'schema_version':'orion.p3.public-prediction.v1.1','case_id':case['case_id'],'system_id':'EXACT_FOUR_STATE_PROBE','relation':truth,'admissible_relations':[truth],'input_digest':case['input_digest'],'details':{},'gold_accessed':False})
    preds.append({'schema_version':'orion.p3.public-prediction.v1.1','case_id':case['case_id'],'system_id':'OBSTRUCTION_PROBE','relation':'OBSTRUCTION','admissible_relations':['OBSTRUCTION'],'input_digest':case['input_digest'],'details':{},'gold_accessed':False})
write_jsonl(FIX/'predictions.jsonl',preds)
score_args=['score-public','--cases',str(OUT/'cases.jsonl'),'--predictions',str(FIX/'predictions.jsonl'),'--gold',str(FIX/'gold.jsonl'),'--out',str(OUT/'score.json'),'--ack-public-gold-not-protected']
records.append(run('valid_four_terminal_score',score_args,True))
score=json.loads((OUT/'score.json').read_text())
exact_rows=score['systems']['EXACT_FOUR_STATE_PROBE']['all_cases_descriptive']['case_results']
obstruction_rows=score['systems']['OBSTRUCTION_PROBE']['all_cases_descriptive']['case_results']
plural_exact=next(row for row in exact_rows if row['truth']=='PLURAL')
plural_obstruction=next(row for row in obstruction_rows if row['truth']=='PLURAL')
semantic_assertions={
 'plural_exact_zero_loss': all(item['loss']==0 and item['excess_harm']==0 for item in plural_exact['floor_adjusted']),
 'obstruction_on_plural_is_plural_collapse': plural_obstruction['plural_collapse'] is True,
 'obstruction_on_plural_positive_loss': all(item['loss']>0 for item in plural_obstruction['floor_adjusted']),
 'coordinate_gate_pass_recorded': score['coordinate_opportunity_gates']['DIRECT_SYNTHETIC']['REFERENT']['status']=='PASS_NONZERO',
 'no_pooled_pass': score['cross_source_terminal']=='NO_POOLED_PASS'
}
if not all(semantic_assertions.values()):
    raise SystemExit(json.dumps(semantic_assertions,indent=2))

# Recursive/closed-field leakage rejection.
leaky_inventory=FIX/'leaky_inventory.jsonl'
write_jsonl(leaky_inventory,[{'source_id':'OAEI_2004_ZENODO_15827226','donor_family':'OAEI','unit_id':'L','cluster_id':'C','provider_split':'descriptive_stress','selection_fields_only':True,'provenance':{'evaluator_gold':{'true_relation':'GLUE'}}}])
records.append(run('recursive_inventory_leak_rejected',['sample','--inventory',str(leaky_inventory),'--out',str(OUT/'never_sample.json')],False,'unknown fields rejected'))
leaky_case=dict(base_cases[0]); leaky_case['provenance']=dict(leaky_case['provenance']); leaky_case['provenance']['evaluator_gold']={'true_relation':'GLUE'}
write_jsonl(FIX/'leaky_case.jsonl',[leaky_case])
records.append(run('recursive_case_leak_rejected',['seal-cases','--cases',str(FIX/'leaky_case.jsonl'),'--out',str(OUT/'never_case.jsonl')],False,'forbidden outcome fields'))

# Coordinate opportunity gate rejection.
zero_gold=json.loads(json.dumps(gold))
for row in zero_gold: row['coordinate_opportunities']['REFERENT']={'status':'ZERO','count':0}
write_jsonl(FIX/'zero_gold.jsonl',zero_gold)
records.append(run('zero_coordinate_gate_rejected',['score-public','--cases',str(OUT/'cases.jsonl'),'--predictions',str(FIX/'predictions.jsonl'),'--gold',str(FIX/'zero_gold.jsonl'),'--out',str(OUT/'never_zero_score.json'),'--ack-public-gold-not-protected'],False,'ZERO_OR_UNKNOWN_OPPORTUNITY'))

# Prediction uniqueness, relation, digest, and forbidden statistical identity fields.
def variant(name, mutate, expected):
    rows=json.loads(json.dumps(preds)); mutate(rows); path=FIX/f'{name}.jsonl'; write_jsonl(path,rows)
    records.append(run(name,['score-public','--cases',str(OUT/'cases.jsonl'),'--predictions',str(path),'--gold',str(FIX/'gold.jsonl'),'--out',str(OUT/f'never_{name}.json'),'--ack-public-gold-not-protected'],False,expected))
variant('duplicate_prediction_rejected',lambda rows: rows.append(dict(rows[0])),'duplicate (system_id, case_id)')
variant('invalid_relation_rejected',lambda rows: rows[0].update(relation='BANANA'),'invalid relation')
variant('digest_mismatch_rejected',lambda rows: rows[0].update(input_digest='f'*64),'input_digest mismatch')
variant('prediction_cluster_injection_rejected',lambda rows: rows[0].update(cluster_id='INJECTED'),'unknown fields rejected')

# A human rights receipt with CANNOT_CHECK must block the body without network access.
rights_decision={
 'schema_version':'orion.p3.public-rights-decision.v1.1','decision_id':'DIRECT.CRAFT.CANNOT_CHECK','source_id':'CRAFT_SHARED_TASK_2019_ZENODO_3460908','decided_by':'DIRECT_SYNTHETIC_CHECK','decided_at_utc':'2026-08-23T00:00:00Z',
 'permitted_operations':['METADATA_ONLY'],'content_classes':['BIOMEDICAL_ARTICLE_TEXT'],'license_evidence':['SYNTHETIC_MECHANICS_FIXTURE_ONLY'],'required_conditions_acknowledged':[],'redistribution_plan':'NO_BODY_ACQUIRED','terminal':'CANNOT_CHECK','non_legal_advice_acknowledged':True
}
(FIX/'craft_rights_cannot_check.json').write_text(json.dumps(rights_decision,indent=2,sort_keys=True)+'\n')
records.append(run('rights_cannot_check_blocks_body',['fetch','--source','CRAFT_SHARED_TASK_2019_ZENODO_3460908','--data-dir',str(OUT/'rights_no_download'),'--receipt',str(OUT/'rights_receipt.json'),'--rights-decision',str(FIX/'craft_rights_cannot_check.json')],True))
rights_receipt=json.loads((OUT/'rights_receipt.json').read_text())
semantic_assertions['rights_cannot_check_blocks_body']=rights_receipt['receipts'][0]['status']=='SKIPPED_DATA_BODY__HUMAN_RIGHTS_DECISION_ABSENT_OR_NOT_AUTHORIZED' and rights_receipt['downloaded_containers_with_public_gold_bytes']==0
if not semantic_assertions['rights_cannot_check_blocks_body']:
    raise SystemExit(json.dumps(rights_receipt,indent=2))

receipt={'schema_version':'orion.p3.public-adapter-direct-repair-checks.v1.1','authority':'DIRECT_SYNTHETIC_AND_INPUT_ONLY_MECHANICS__NO_PUBLIC_GOLD__NO_EMPIRICAL_RESULT','pytest_or_ci_run':False,'public_gold_opened':False,'semantic_assertions':semantic_assertions,'checks':records,'passed':all(r['passed'] for r in records) and all(semantic_assertions.values())}
(HERE/'DIRECT_REPAIR_CHECK_RECEIPT_V1_1.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':receipt['passed'],'n_checks':len(records),'semantic_assertions':semantic_assertions},indent=2,sort_keys=True))
