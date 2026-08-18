#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p6_method_fibres import (
    CompositionContract, CompositionKind, StructuralRelation,
    MethodRealizationView, build_reduction, build_signature,
    membership_evidence, assess_membership, check_composition,
    relation, representation_lift,
)
ROOT=Path(__file__).resolve().parents[1]
PANEL=ROOT/'method_fibre_extension'/'METHOD_FIBRE_BENCH_V1.json'
SUMMARY=ROOT/'method_fibre_extension'/'METHOD_FIBRE_BENCH_SUMMARY_V1.json'

def d(x): return content_digest({'x':x})
def realization(name):
    return MethodRealizationView(name,d(name),('finite',),('transform','solve'),(('transform','solve'),),('safe',),('reduce',),'rank','lift',('stuck',),(name,))
def signature():
    r=realization('base'); red=build_reduction(r,reduction_id='bench-red',claim_id='bench-claim',preserved=('preconditions','invariants','effects','reconstruction'),erased=('actions','dependencies','termination','failures','lineage'),load_bearing=('preconditions','invariants','effects','reconstruction'),justifications={'actions':'surface','dependencies':'internal','termination':'effect-local','failures':'out of claim','lineage':'retained externally'}); return r,build_signature(r,red)
def evaluate(case,s):
    kind=case['kind']
    if kind=='membership':
        r=realization(case['id']); e=membership_evidence(s,r,**case['settings']); return assess_membership(s,r,e).status.value
    if kind=='parallel_collision': return check_composition(CompositionContract(CompositionKind.PARALLEL,left_write=('x',),right_read=('x',)))[0].value
    if kind=='precondition': return check_composition(CompositionContract(CompositionKind.SEQUENTIAL,right_preconditions=('ready','stable'),left_guarantees=('ready',)))[0].value
    if kind=='authority': return check_composition(CompositionContract(CompositionKind.SEQUENTIAL,emitted_authorities=('adopt:self',),permitted_authorities=()))[0].value
    if kind=='recursive': return check_composition(CompositionContract(CompositionKind.RECURSIVE,rank_decreases=False))[0].value
    if kind=='clean': return check_composition(CompositionContract(CompositionKind.SEQUENTIAL,right_preconditions=('ready',),left_guarantees=('ready',),required_dependencies=('m',),declared_dependencies=('m',),emitted_authorities=('local',),permitted_authorities=('local',)))[0].value
    if kind=='specialization': return relation(base_preconditions=('finite',),candidate_preconditions=('finite','acyclic'),base_effects=('solve',),candidate_effects=('solve',),requested=StructuralRelation.SPECIALIZES,obligations_satisfied=True).value
    if kind=='lift': return representation_lift(False).value
    raise ValueError(kind)
def run(panel):
    _,s=signature(); rows=[]
    for c in panel['cases']:
        actual=evaluate(c,s); rows.append({'id':c['id'],'family':c['family'],'expected':c['expected'],'actual':actual,'pass':actual==c['expected']})
    false_fibres=[r for r in rows if r['family']=='FALSE_FIBRE']; clean=[r for r in rows if r['family'] in {'FAITHFUL_SUBSTITUTION','CLEAN_COMPOSITION'}]
    out={'result_version':'P6_METHOD_FIBRE_BENCH_SUMMARY_V1','protocol_id':panel['protocol_id'],'panel_digest':content_digest(panel),'n_cases':len(rows),'typed_calculus_accuracy':sum(r['pass'] for r in rows)/len(rows),'false_fibre_control':sum(r['pass'] for r in false_fibres)/len(false_fibres),'clean_acceptance':sum(r['pass'] for r in clean)/len(clean),'rows':rows,'terminal':'P6_METHOD_FIBRE_FORMALISM_NARROWED','claim_ceiling':panel['claim_ceiling']}
    out['result_digest']=content_digest(out); return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args(); panel=json.loads(PANEL.read_text()); out=run(panel); text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.write: SUMMARY.write_text(text)
    if a.check:
        if not SUMMARY.exists() or SUMMARY.read_text()!=text: raise SystemExit('P6 fibre benchmark summary drift')
    if not a.write and not a.check: print(text,end='')
if __name__=='__main__': main()
