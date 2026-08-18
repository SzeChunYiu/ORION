#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p7_method_space import (
    EdgeKind, MethodChartEdge, RevisitLedger, StopScope,
    build_chart, propose_invention, record_event, reopen_chart, stop,
)
ROOT=Path(__file__).resolve().parent
PANEL=ROOT/'METHOD_SPACE_BENCH_V1.json'
SUMMARY=ROOT/'METHOD_SPACE_BENCH_SUMMARY_V1.json'
def d(x): return content_digest({'x':x})
def base_chart(edges=()):
    return build_chart(chart_id='bench-chart',subject_digest=d('subject'),construction_rule='frozen-bounded-v1',signature_digests=(d('sig'),),edges=edges,route_ids=('r1','r2'),source_families=('f1',),unknown_boundary=('outside-chart',),noncoverage=('future-methods',),reopen_triggers=('new-route','new-fibre'))
def evaluate(case):
    k=case['kind']; c=base_chart()
    if k=='stop': return stop(c,scope=StopScope(case['scope']),reason='bounded local stop').task_terminal
    if k=='task_stop': return stop(c,scope=StopScope.TASK,reason='external closure',task_closable=True,external_authority_digest=d('task-authority')).task_terminal
    if k=='representation':
        e=MethodChartEdge(d('sig'),d(case['id']),EdgeKind.REPRESENTATION_CHANGE,d('prov:'+case['id']),'reframe',True,case['reconstruction_valid']);return record_event(base_chart((e,)),e,event_id=case['id'],evidence_digest=d('ev:'+case['id'])).state.value
    if k=='invention': return propose_invention(c,attempted_route_ids=case['attempted'],required_route_ids=case['required']).eligible
    if k=='reopen': return reopen_chart(c,new_signature_digest=d('new-fibre')).epoch
    if k=='revisit':
        e=MethodChartEdge(d('sig'),d('target'),EdgeKind.METHOD_NEIGHBOR,d('prov'),'try');evt=record_event(base_chart((e,)),e,event_id='visit',evidence_digest=d('same-evidence'));ledger=RevisitLedger();ledger.allow(evt);return ledger.allow(evt)
    raise ValueError(k)
def run(panel):
    rows=[]
    for c in panel['cases']:
        expected=c.get('expected',c.get('expected_epoch',c.get('expected_second')));actual=evaluate(c);rows.append({'id':c['id'],'expected':expected,'actual':actual,'pass':actual==expected})
    out={'result_version':'P7_METHOD_SPACE_BENCH_SUMMARY_V1','protocol_id':panel['protocol_id'],'panel_digest':content_digest(panel),'n_cases':len(rows),'contract_accuracy':sum(r['pass'] for r in rows)/len(rows),'rows':rows,'terminal':'P7_METHOD_SPACE_NAVIGATION_NARROWED','claim_ceiling':panel['claim_ceiling']};out['result_digest']=content_digest(out);return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();out=run(json.loads(PANEL.read_text()));text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.write:SUMMARY.write_text(text)
    if a.check and (not SUMMARY.exists() or SUMMARY.read_text()!=text):raise SystemExit('P7 method-space benchmark summary drift')
    if not a.write and not a.check:print(text,end='')
if __name__=='__main__':main()
