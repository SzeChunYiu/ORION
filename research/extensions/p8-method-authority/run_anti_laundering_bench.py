#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p8_method_authority import (
    AuthorityCoordinate, AuthorityState, CapabilityKind, CapabilityOutput,
    DefeaterKind, ProvenanceClass, apply_decision, authority_record,
    coerce, provenance, revoke,
)
ROOT=Path(__file__).resolve().parent
PANEL=ROOT/'P9_P10_ANTI_LAUNDERING_CASES_V1.json'
SUMMARY=ROOT/'P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json'
def d(x):return content_digest({'x':x})
def base_record():return authority_record(provenance(method_id='bench-method',provenance_class=ProvenanceClass.INVENTED_METHOD_CANDIDATE,subject_digest=d('subject'),source_ids=('donor',),generator_id='p10',generator_version='v1',evidence_digest=d('provenance')))
def grant_for(record,coordinate):
    source={AuthorityCoordinate.NOVELTY:CapabilityKind.NOVELTY_REVIEW,AuthorityCoordinate.ADOPTION:CapabilityKind.P5_HOST_ADOPTION,AuthorityCoordinate.SEARCH_STOP:CapabilityKind.TASK_CLOSURE}.get(coordinate,CapabilityKind.P4_VERIFICATION)
    return apply_decision(record,coerce(CapabilityOutput(source,record.subject_digest,d('grant:'+coordinate.value)),coordinate))
def evaluate(case):
    coordinate=AuthorityCoordinate(case['coordinate'])
    if case['kind']=='coercion':
        return coerce(CapabilityOutput(CapabilityKind(case['source']),d('subject'),d('case:'+case['id'])),coordinate).state.value
    record=grant_for(base_record(),coordinate)
    return revoke(record,defeater=DefeaterKind(case['defeater']),evidence_digest=d('defeater:'+case['id'])).state(coordinate).value
def run(panel):
    rows=[]
    for case in panel['cases']:
        actual=evaluate(case);rows.append({'id':case['id'],'kind':case['kind'],'expected':case['expected'],'actual':actual,'pass':actual==case['expected']})
    attacks=[r for r in rows if r['kind']=='coercion' and r['expected']=='BLOCKED'];clean=[r for r in rows if r['kind']=='coercion' and r['expected']=='SUPPORTED'];rev=[r for r in rows if r['kind']=='revocation']
    out={'result_version':'P8_P9_P10_ANTI_LAUNDERING_SUMMARY_V1','protocol_id':panel['protocol_id'],'panel_digest':content_digest(panel),'n_cases':len(rows),'contract_accuracy':sum(r['pass'] for r in rows)/len(rows),'illicit_coercion_block_rate':sum(r['pass'] for r in attacks)/len(attacks),'clean_legal_coverage':sum(r['pass'] for r in clean)/len(clean),'revocation_accuracy':sum(r['pass'] for r in rev)/len(rev),'rows':rows,'terminal':'P8_P9_P10_ANTI_LAUNDERING_CLEAR','claim_ceiling':panel['claim_ceiling']}
    out['result_digest']=content_digest(out);return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();out=run(json.loads(PANEL.read_text()));text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.write:SUMMARY.write_text(text)
    if a.check and (not SUMMARY.exists() or SUMMARY.read_text()!=text):raise SystemExit('P8 anti-laundering summary drift')
    if not a.write and not a.check:print(text,end='')
if __name__=='__main__':main()
