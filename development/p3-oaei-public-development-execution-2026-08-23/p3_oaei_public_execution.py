#!/usr/bin/env python3
"""Public-only OAEI development execution for P3.

The script deliberately separates input/candidate construction, prediction
freeze, public-reference joining, and compact scoring. It imports the repaired
V1.1 contract validators but has a new empirical identity.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urldefrag
from xml.etree import ElementTree

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
ADAPTER_PATH=REPO/'development/p3-public-data-successor-2026-08-23/p3_public_data_adapter.py'
PROTOCOL_ID='P3.PUBLIC.OAEI.CONFLICT_PRESERVING.DEV.V1'
TARGETS=['102','103','104','105','201','202','204','205','206','221','222','223','224','225','228','230','301','302','303','304']
SYSTEMS=['AML_V3_2_AUTO_SOURCE_NATIVE','FLAT_LABEL_EQUALITY_V1','TOKEN_JACCARD_FORCED_V1','AML_OR_LABEL_FORCED_V1','AML_AND_LABEL_FORCED_V1','P3_CONFLICT_PRESERVING_WRAPPER_V1','P3_INFORMATION_EQUIVALENT_IDEAL_V1']

spec=importlib.util.spec_from_file_location('p3_v11_adapter',ADAPTER_PATH)
if spec is None or spec.loader is None: raise RuntimeError('cannot load repaired V1.1 adapter')
adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def read_jsonl(path:Path)->Iterable[dict[str,Any]]:
    with path.open(encoding='utf-8') as f:
        for n,line in enumerate(f,1):
            if not line.strip(): continue
            try: yield json.loads(line)
            except json.JSONDecodeError as e: raise ValueError(f'{path}:{n}: invalid JSON') from e

def write_json(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')

def normalize_label(value:Any)->str:
    text=unicodedata.normalize('NFKC','' if value is None else str(value)).casefold()
    return ' '.join(x for x in re.split(r'[^\w]+',text) if x)

def jaccard(a:str,b:str)->float:
    x,y=set(a.split()),set(b.split())
    return len(x&y)/len(x|y) if x or y else 0.0

def local_id(uri:str)->str:
    base,frag=urldefrag(uri)
    return frag or base.rstrip('/').rsplit('/',1)[-1]

def target_of_case(case:dict[str,Any])->str:
    return Path(case['provenance']['right_member']).parent.name

def alignment_cells(raw:bytes)->list[dict[str,Any]]:
    root=ElementTree.fromstring(raw)
    rdf_resource='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
    cells=[]
    for cell in root.iter():
        if adapter.xml_local_name(cell.tag)!='Cell': continue
        row={'entity1':None,'entity2':None,'relation':None,'measure':None}
        for child in cell:
            name=adapter.xml_local_name(child.tag)
            if name in {'entity1','entity2'}: row[name]=child.attrib.get(rdf_resource)
            elif name=='relation': row[name]=(child.text or '').strip()
            elif name=='measure':
                try: row[name]=float((child.text or '').strip())
                except ValueError: row[name]=None
        if row['entity1'] and row['entity2']: cells.append(row)
    return cells

def cmd_build_cases(args:argparse.Namespace)->None:
    output=Path(args.out); receipt=Path(args.receipt)
    with tempfile.TemporaryDirectory(prefix='p3-oaei-v11-build-') as td:
        raw_cases=Path(td)/'v11_cases.jsonl'; raw_receipt=Path(td)/'v11_receipt.json'
        adapter.cmd_build_oaei_cases(argparse.Namespace(data_dir=args.data_dir,source_test='101',out=str(raw_cases),receipt=str(raw_receipt)))
        seen=set(); n=0
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('w',encoding='utf-8') as out:
            for case in read_jsonl(raw_cases):
                identity=f"{PROTOCOL_ID}\0{case['provenance']['left_locator']}\0{case['provenance']['right_locator']}"
                case['case_id']='P3.OAEI.DEV.'+hashlib.sha256(identity.encode()).hexdigest()[:24]
                case['required_coordinates']=['REFERENT']
                case['provenance']['builder_id']='P3_OAEI_PUBLIC_DEV_EXHAUSTIVE_V1'
                case['provenance']['builder_revision']='1.0.0'
                case.pop('input_digest',None); case['input_digest']=adapter.canonical_case_digest(case)
                adapter.validate_case(case,f'built[{n+1}]',True)
                if case['case_id'] in seen: raise ValueError('duplicate case id')
                seen.add(case['case_id']); out.write(json.dumps(case,sort_keys=True,ensure_ascii=False)+'\n'); n+=1
    write_json(receipt,{'schema_version':'orion.p3.oaei-public-case-universe.v1','protocol_id':PROTOCOL_ID,'authority':'INPUT_ONLY_CASE_UNIVERSE__NO_PUBLIC_REFERENCE_CONTENT','public_reference_content_opened':False,'construction':'EXHAUSTIVE_CROSS_PRODUCT_WITHIN_SOURCE_NATIVE_ENTITY_TYPE','claimed_coordinates':['REFERENT'],'controlled_not_claimed_coordinates':['CONSTRUCT'],'n_cases':n,'n_clusters':1,'targets':TARGETS,'case_file':str(output),'case_file_size':output.stat().st_size,'case_file_sha256':sha(output),'adapter_sha256':sha(ADAPTER_PATH),'current_terminal':'INPUT_CASE_UNIVERSE_FROZEN__NO_GOLD_OR_RESULT'})

def aml_matches(output_dir:Path, manifest:dict[str,Any])->tuple[set[tuple[str,str,str]],dict[str,str]]:
    selected=set(); statuses={row['target_test']:row['status'] for row in manifest['targets']}
    for target,status in statuses.items():
        if status!='EXECUTED': continue
        for cell in alignment_cells((output_dir/f'{target}.rdf').read_bytes()):
            if cell['relation'] not in {'=','%3D'}: continue
            selected.add((target,local_id(cell['entity1']),local_id(cell['entity2'])))
    return selected,statuses

def prediction(case:dict[str,Any],system_id:str,aml_selected:bool,aml_available:bool)->dict[str,Any]:
    left=normalize_label(case['left']['label']); right=normalize_label(case['right']['label'])
    lexical=bool(left and left==right); token_score=jaccard(left,right); token=token_score>=0.5
    if system_id=='AML_V3_2_AUTO_SOURCE_NATIVE':
        if not aml_available: relation,admissible='UNRESOLVED',['GLUE','OBSTRUCTION']
        else: relation='GLUE' if aml_selected else 'OBSTRUCTION'; admissible=[relation]
    elif system_id=='FLAT_LABEL_EQUALITY_V1': relation='GLUE' if lexical else 'OBSTRUCTION'; admissible=[relation]
    elif system_id=='TOKEN_JACCARD_FORCED_V1': relation='GLUE' if token else 'OBSTRUCTION'; admissible=[relation]
    elif system_id in {'AML_OR_LABEL_FORCED_V1','AML_AND_LABEL_FORCED_V1'}:
        if not aml_available: relation,admissible='UNRESOLVED',['GLUE','OBSTRUCTION']
        else:
            flag=(aml_selected or lexical) if system_id=='AML_OR_LABEL_FORCED_V1' else (aml_selected and lexical)
            relation='GLUE' if flag else 'OBSTRUCTION'; admissible=[relation]
    elif system_id in {'P3_CONFLICT_PRESERVING_WRAPPER_V1','P3_INFORMATION_EQUIVALENT_IDEAL_V1'}:
        if not aml_available or aml_selected!=lexical: relation,admissible='UNRESOLVED',['GLUE','OBSTRUCTION']
        else: relation='GLUE' if aml_selected else 'OBSTRUCTION'; admissible=[relation]
    else: raise ValueError(system_id)
    row={'schema_version':'orion.p3.public-prediction.v1.1','case_id':case['case_id'],'system_id':system_id,'relation':relation,'admissible_relations':admissible,'input_digest':case['input_digest'],'details':{'aml_available':aml_available,'aml_selected':aml_selected,'normalized_label_equal':lexical,'token_jaccard':token_score},'gold_accessed':False}
    adapter.validate_prediction(row,f'prediction[{case["case_id"]}/{system_id}]')
    return row

def cmd_run_systems(args:argparse.Namespace)->None:
    cases_path=Path(args.cases); out=Path(args.out); receipt=Path(args.receipt)
    manifest=json.loads(Path(args.aml_manifest).read_text()); selected,statuses=aml_matches(Path(args.aml_output_dir),manifest)
    key_counts=defaultdict(int); system_counts={s:defaultdict(int) for s in SYSTEMS}; n=0
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as f:
        for case in read_jsonl(cases_path):
            adapter.validate_case(case,f'case[{n+1}]',True)
            if case['input_digest']!=adapter.canonical_case_digest(case): raise ValueError('case digest mismatch')
            target=target_of_case(case); key=(target,local_id(case['left']['coordinates']['REFERENT']),local_id(case['right']['coordinates']['REFERENT'])); key_counts[key]+=1
            is_selected=key in selected; available=statuses[target]=='EXECUTED'
            for system_id in SYSTEMS:
                row=prediction(case,system_id,is_selected,available); f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+'\n'); system_counts[system_id][row['relation']]+=1
            n+=1
    ambiguous=sum(count>1 for count in key_counts.values()); unmatched_aml=sum(key not in key_counts for key in selected)
    if ambiguous or unmatched_aml: raise ValueError(f'AML/case terminal map invalid: ambiguous={ambiguous}, unmatched={unmatched_aml}')
    write_json(receipt,{'schema_version':'orion.p3.oaei-public-prediction-freeze.v1','protocol_id':PROTOCOL_ID,'authority':'PRE_PUBLIC_GOLD_PREDICTION_FREEZE','public_reference_content_opened':False,'case_file_sha256':sha(cases_path),'prediction_file':str(out),'prediction_file_size':out.stat().st_size,'prediction_file_sha256':sha(out),'n_cases':n,'systems':SYSTEMS,'n_prediction_rows':n*len(SYSTEMS),'system_action_counts':{s:dict(c) for s,c in system_counts.items()},'aml_selected_pairs':len(selected),'aml_case_key_ambiguities':ambiguous,'aml_pairs_outside_case_universe':unmatched_aml,'current_terminal':'PREDICTIONS_FROZEN__PUBLIC_REFERENCE_NOT_OPENED'})

def cmd_freeze(args:argparse.Namespace)->None:
    files=[Path(args.protocol),Path(args.rights),Path(args.aml_binding),Path(args.aml_manifest),Path(args.script),Path(args.case_receipt),Path(args.prediction_receipt),Path(args.cases),Path(args.predictions)]
    if Path(args.gold).exists(): raise ValueError('gold output already exists; pre-gold freeze refused')
    rows=[{'path':str(p),'sha256':sha(p),'size':p.stat().st_size} for p in files]
    write_json(Path(args.out),{'schema_version':'orion.p3.oaei-public-pre-gold-freeze.v1','protocol_id':PROTOCOL_ID,'authority':'PRE_PUBLIC_GOLD_FREEZE','public_reference_content_opened':False,'protected_evidence':False,'frozen_files':rows,'gold_output_absent':True,'current_terminal':'PRE_GOLD_FREEZE_COMPLETE__PUBLIC_EVALUATION_MAY_OPEN'})

def cmd_join_gold(args:argparse.Namespace)->None:
    cases_path=Path(args.cases); archive_path=Path(args.archive); output=Path(args.out); receipt_path=Path(args.receipt)
    cases={}; keys={}
    for n,case in enumerate(read_jsonl(cases_path),1):
        adapter.validate_case(case,f'case[{n}]',True); cases[case['case_id']]=case
        key=(target_of_case(case),local_id(case['left']['coordinates']['REFERENT']),local_id(case['right']['coordinates']['REFERENT']))
        if key in keys: raise ValueError(f'ambiguous case key {key}')
        keys[key]=case['case_id']
    positives=set(); member_receipts=[]; total_reference=0; missing=[]; non_equivalence=[]
    with zipfile.ZipFile(archive_path) as z:
        refs={Path(name).parent.name:name for name in z.namelist() if Path(name).name.lower()=='refalign.rdf'}
        for target in TARGETS:
            if target not in refs: missing.append(target); continue
            raw=z.read(refs[target]); cells=alignment_cells(raw); member_receipts.append({'target_test':target,'member':refs[target],'sha256':hashlib.sha256(raw).hexdigest(),'n_cells':len(cells)})
            for cell in cells:
                total_reference+=1
                if cell['relation'] not in {'=','%3D'}: non_equivalence.append({'target':target,'relation':cell['relation']}); continue
                a,b=local_id(cell['entity1']),local_id(cell['entity2']); direct=(target,a,b); reverse=(target,b,a)
                if direct in keys: positives.add(keys[direct])
                elif reverse in keys: positives.add(keys[reverse])
                else: missing.append({'target':target,'left':a,'right':b})
    recall=len(positives)/total_reference if total_reference else 0.0
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8') as f:
        for case_id,case in cases.items():
            truth='GLUE' if case_id in positives else 'OBSTRUCTION'
            gold={'case_id':case_id,'cluster_id':case['cluster_id'],'source_id':case['source_id'],'panel_id':case['panel_id'],'input_digest':case['input_digest'],'true_relation':truth,'identified_relations':[truth],'gold_authority':'OAEI_PUBLIC_REFERENCE','protected_evidence':False,'coordinate_opportunities':{'REFERENT':{'status':'NONZERO','count':1}},'provenance':{'contract':'OAEI_2004_CLOSED_WORLD_PUBLIC_REFERENCE','adaptation':'REFERENCE_EQUIVALENCE_IS_GLUE__ABSENCE_IS_OBSTRUCTION'}}
            adapter.validate_gold_row(gold,case,f'gold[{case_id}]'); f.write(json.dumps(gold,sort_keys=True,ensure_ascii=False)+'\n')
    write_json(receipt_path,{'schema_version':'orion.p3.oaei-public-gold-join.v1','protocol_id':PROTOCOL_ID,'authority':'PUBLIC_REFERENCE_ONLY__NOT_PROTECTED','archive_sha256':sha(archive_path),'case_file_sha256':sha(cases_path),'gold_file':str(output),'gold_file_sha256':sha(output),'gold_file_size':output.stat().st_size,'n_cases':len(cases),'n_glue':len(positives),'n_obstruction':len(cases)-len(positives),'reference_cells_total':total_reference,'reference_pairs_in_candidate_universe':len(positives),'candidate_universe_recall':recall,'missing_or_unmapped_reference':missing,'non_equivalence_reference_cells':non_equivalence,'reference_members':member_receipts,'plural_truth_opportunities':0,'temporal_context_opportunities':0,'protected_evidence':False,'gate_status':'PASS' if recall==1.0 and not missing and not non_equivalence else 'FAIL_INVALID_CANDIDATE_UNIVERSE','current_terminal':'PUBLIC_GOLD_JOIN_COMPLETE__SCORING_NOT_YET_INTERPRETED'})

def empty_counter()->dict[str,Any]:
    return {'n':0,'tp':0,'fp':0,'fn':0,'tn':0,'exact':0,'unresolved':0,'covered':0,'loss_sums':[0.0,0.0,0.0]}
def update_counter(c:dict[str,Any],truth:str,pred:str,covered:bool,losses:list[float])->None:
    c['n']+=1; c['exact']+=pred==truth; c['unresolved']+=pred=='UNRESOLVED'; c['covered']+=covered
    c['tp']+=truth=='GLUE' and pred=='GLUE'; c['fp']+=truth=='OBSTRUCTION' and pred=='GLUE'; c['fn']+=truth=='GLUE' and pred!='GLUE'; c['tn']+=truth=='OBSTRUCTION' and pred=='OBSTRUCTION'
    for i,x in enumerate(losses): c['loss_sums'][i]+=x
def finalize(c:dict[str,Any])->dict[str,Any]:
    precision=c['tp']/(c['tp']+c['fp']) if c['tp']+c['fp'] else None; recall=c['tp']/(c['tp']+c['fn']) if c['tp']+c['fn'] else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else None
    return {**{k:c[k] for k in ['n','tp','fp','fn','tn']},'precision':precision,'recall':recall,'f1':f1,'exact_rate':c['exact']/c['n'],'unresolved_rate':c['unresolved']/c['n'],'gold_in_envelope_coverage':c['covered']/c['n'],'mean_floor_adjusted_harm':[x/c['n'] for x in c['loss_sums']]}

def cmd_score(args:argparse.Namespace)->None:
    cases={}; case_target={}
    for n,case in enumerate(read_jsonl(Path(args.cases)),1):
        adapter.validate_case(case,f'case[{n}]',True)
        if case['input_digest']!=adapter.canonical_case_digest(case): raise ValueError('case digest mismatch')
        if case['case_id'] in cases: raise ValueError('duplicate case')
        cases[case['case_id']]=case; case_target[case['case_id']]=target_of_case(case)
    gold={}
    for n,row in enumerate(read_jsonl(Path(args.gold)),1):
        if row['case_id'] not in cases: raise ValueError('unknown gold case')
        if row['case_id'] in gold: raise ValueError('duplicate gold')
        adapter.validate_gold_row(row,cases[row['case_id']],f'gold[{n}]'); gold[row['case_id']]=row
    if set(gold)!=set(cases): raise ValueError('gold exact coverage failure')
    opportunity=adapter.enforce_coordinate_opportunity_gates(cases,gold)
    loss_grid=json.loads((REPO/'development/p3-public-data-successor-2026-08-23/P3_PUBLIC_DATA_SUCCESSOR_PROTOCOL_V1_1.json').read_text())['endpoints']['loss_grid']
    counters={s:empty_counter() for s in SYSTEMS}; per_test={s:{t:empty_counter() for t in TARGETS} for s in SYSTEMS}; seen={s:set() for s in SYSTEMS}; paired={}
    for n,pred in enumerate(read_jsonl(Path(args.predictions)),1):
        adapter.validate_prediction(pred,f'prediction[{n}]'); cid=pred['case_id']; sid=pred['system_id']
        if sid not in counters or cid not in cases: raise ValueError('unknown system/case')
        if cid in seen[sid]: raise ValueError('duplicate prediction')
        if pred['input_digest']!=cases[cid]['input_digest']: raise ValueError('prediction digest mismatch')
        seen[sid].add(cid); truth=gold[cid]['true_relation']; covered=truth in pred['admissible_relations']; losses=[adapter.point_loss(pred['relation'],truth,costs) for costs in loss_grid]
        update_counter(counters[sid],truth,pred['relation'],covered,losses); update_counter(per_test[sid][case_target[cid]],truth,pred['relation'],covered,losses)
        if sid in {'AML_V3_2_AUTO_SOURCE_NATIVE','P3_CONFLICT_PRESERVING_WRAPPER_V1','P3_INFORMATION_EQUIVALENT_IDEAL_V1'}: paired.setdefault(cid,{})[sid]={'relation':pred['relation'],'admissible':pred['admissible_relations'],'exact':pred['relation']==truth,'losses':losses}
    for sid in SYSTEMS:
        if seen[sid]!=set(cases): raise ValueError(f'prediction exact coverage failure {sid}')
    systems={s:{'full_census':finalize(counters[s]),'per_target':{t:finalize(per_test[s][t]) for t in TARGETS}} for s in SYSTEMS}
    cand='P3_CONFLICT_PRESERVING_WRAPPER_V1'; aml='AML_V3_2_AUTO_SOURCE_NATIVE'; ideal='P3_INFORMATION_EQUIVALENT_IDEAL_V1'
    candidate_minus_aml_harm=[systems[cand]['full_census']['mean_floor_adjusted_harm'][i]-systems[aml]['full_census']['mean_floor_adjusted_harm'][i] for i in range(3)]
    ideal_tie=all(p[cand]['relation']==p[ideal]['relation'] and p[cand]['admissible']==p[ideal]['admissible'] and p[cand]['losses']==p[ideal]['losses'] for p in paired.values())
    cand_coverage=systems[cand]['full_census']['gold_in_envelope_coverage']; gold_receipt=json.loads(Path(args.gold_receipt).read_text())
    gates={'candidate_universe_recall_1_0':gold_receipt['candidate_universe_recall']==1.0,'referent_opportunity_nonzero':opportunity['OAEI_2004_ZENODO_15827226']['REFERENT']['status']=='PASS_NONZERO','p3_gold_in_envelope_coverage_1_0':cand_coverage==1.0,'p3_ideal_product_exact_tie':ideal_tie,'one_independent_cluster_only':True,'protected_authority':False}
    if not gates['candidate_universe_recall_1_0']: terminal='PUBLIC_CANDIDATE_UNIVERSE_INVALID'
    elif not gates['p3_gold_in_envelope_coverage_1_0']: terminal='PUBLIC_P3_INVALID_ENVELOPE_COVERAGE'
    elif not ideal_tie: terminal='PUBLIC_P3_INFORMATION_EQUIVALENT_BOUNDARY_FAILED'
    elif all(x<0 for x in candidate_minus_aml_harm): terminal='PUBLIC_ONE_SEED_FAMILY_DESCRIPTIVE_HARM_SIGNAL'
    elif any(x>0 for x in candidate_minus_aml_harm): terminal='PUBLIC_P3_HARMFUL'
    else: terminal='PUBLIC_P3_NO_HARM_REDUCTION'
    result={'schema_version':'orion.p3.oaei-public-development-result.v1','protocol_id':PROTOCOL_ID,'authority':'PUBLIC_ONE_SEED_FAMILY_DESCRIPTIVE_DEVELOPMENT_ONLY','protected_evidence':False,'n_cases':len(cases),'n_clusters':1,'systems':systems,'candidate_vs_source_native':{'candidate':cand,'comparator':aml,'candidate_minus_aml_exact_rate':systems[cand]['full_census']['exact_rate']-systems[aml]['full_census']['exact_rate'],'candidate_minus_aml_mean_floor_adjusted_harm':candidate_minus_aml_harm,'candidate_minus_aml_unresolved_rate':systems[cand]['full_census']['unresolved_rate']-systems[aml]['full_census']['unresolved_rate']},'gates':gates,'opportunity_receipt':opportunity,'primary_terminal':terminal,'adverse_terminals':['AML_TEST_206_UNPARSABLE_SOURCE_NATIVE_RUNTIME_FAILURE','PLURAL_TRUTH_OPPORTUNITY_ZERO','TEMPORAL_CONTEXT_CANNOT_CHECK','NO_INFERENTIAL_AUTHORITY_ONE_CLUSTER'],'protected_and_768_terminal':'CANNOT_CHECK','current_terminal':terminal+'__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY'}
    write_json(Path(args.out),result)

def parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
    x=s.add_parser('build-cases'); x.add_argument('--data-dir',required=True); x.add_argument('--out',required=True); x.add_argument('--receipt',required=True); x.set_defaults(func=cmd_build_cases)
    x=s.add_parser('run-systems'); x.add_argument('--cases',required=True); x.add_argument('--aml-manifest',required=True); x.add_argument('--aml-output-dir',required=True); x.add_argument('--out',required=True); x.add_argument('--receipt',required=True); x.set_defaults(func=cmd_run_systems)
    x=s.add_parser('freeze');
    for name in ['protocol','rights','aml-binding','aml-manifest','script','case-receipt','prediction-receipt','cases','predictions','gold','out']: x.add_argument('--'+name,required=True)
    x.set_defaults(func=cmd_freeze)
    x=s.add_parser('join-gold'); x.add_argument('--cases',required=True); x.add_argument('--archive',required=True); x.add_argument('--out',required=True); x.add_argument('--receipt',required=True); x.set_defaults(func=cmd_join_gold)
    x=s.add_parser('score'); x.add_argument('--cases',required=True); x.add_argument('--predictions',required=True); x.add_argument('--gold',required=True); x.add_argument('--gold-receipt',required=True); x.add_argument('--out',required=True); x.set_defaults(func=cmd_score)
    return p

def main()->None:
    a=parser().parse_args(); a.func(a)
if __name__=='__main__': main()
