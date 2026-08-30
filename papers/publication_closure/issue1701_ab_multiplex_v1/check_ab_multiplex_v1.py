#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CANONICAL={
'ORION-01':'Certificate Realization','ORION-02':'Finite-Fibre Certifiability','ORION-03':'Typed Merge Falsification','ORION-04':'Rooted Completion Certificates','ORION-05':'TARE Expressivity','ORION-06':'Recursive Recovery','ORION-07':'Dual Instrument','ORION-08':'Typed State','ORION-09':'Compilation Regime Geometry','ORION-10':'Certified Static Forecasting','ORION-11':'Recursive Epistemic Reconstruction','ORION-12':'Open-World Scientific Discovery','ORION-13':'Global Knowledge Portrait','ORION-14':'Verified Scientific Discovery','ORION-15':'Self-ORION','ORION-16':'Formal Epistemic Structures and Mechanics','ORION-17':'Epistemic Navigation in Open Worlds','ORION-18':'Epistemic Authority for Autonomous Science','ORION-19':'Structured Epistemic Learning','ORION-20':'Structured Problem Solving','ORION-21':'State as Computation','ORION-22':'Adaptive-State Reasoning','ORION-23':'Responsibility-Carrying State','ORION-24':'ORION Recursive Scientific Evaluation','ORION-25':'ORION Research Harness'}

def binom(n,k,p): return math.comb(n,k)*p**k*(1-p)**(n-k)
def upper(n,k,p=.5): return sum(binom(n,j,p) for j in range(k,n+1))
def joint(n_each,min_each,total_min,p):
    return sum(binom(n_each,a,p)*binom(n_each,b,p) for a in range(min_each,n_each+1) for b in range(min_each,n_each+1) if a+b>=total_min)

def load(name): return json.loads((ROOT/name).read_text())
def req(cond,msg):
    if not cond: raise AssertionError(msg)

def main():
    plan=load('AB_MULTIPLEX_PLAN_V1.json')
    rows=plan['papers']
    req(len(rows)==25,'must enumerate all 25 canonical papers')
    req({r['paper_id'] for r in rows}==set(CANONICAL),'paper id set mismatch')
    for r in rows:
        req(r['canonical_title']==CANONICAL[r['paper_id']],f"canonical title mismatch {r['paper_id']}")
        req(r['action_grade'] in {'A','B','X'},'unknown action grade')
    # The rejected audit must never be used as paper-local grading authority.
    rejected=[a for a in plan['uploaded_audits'] if 'rejected' in a['role'] or 'generic review rubric' in a['role']]
    req(len(rejected)==1,'exactly one mismapped audit must be quarantined')

    p05=load('ORION05_SAME_DOMAIN_PROTOCOL_V2.json')
    req(p05['status'].startswith('DESIGN_ONLY'),'ORION05 protocol must not claim outcomes')
    req(p05['stage_1_positive_control_discovery']['domain_size']==33755,'O05 multiset-domain cardinality drift')
    expected={'r6o-16':[4,4],'r6o-17':[5,5],'r6o-19':[6,6]}
    got={x['id']:x['expected_all_matchings'] for x in p05['stage_0_domain_sensitivity_controls']}
    req(got==expected,'O05 same-domain control correction drift')

    p17=load('ORION17_RULE_DISAGREEMENT_PROTOCOL_V1.json')
    req(p17['status'].startswith('DESIGN_ONLY'),'ORION17 protocol must not claim outcomes')
    alpha=joint(10,7,15,.5); power=joint(10,7,15,.8)
    req(math.isclose(alpha,p17['primary_gate']['null_joint_probability'],rel_tol=0,abs_tol=1e-15),'O17 alpha drift')
    req(math.isclose(power,p17['primary_gate']['power_if_independent_density_win_probability_0_8'],rel_tol=0,abs_tol=1e-15),'O17 power drift')
    req(alpha<0.025,'O17 gate not strict enough')

    for name in ['ORION19_FAMILY_REPLICATION_PROTOCOL_V1.json','ORION24_STRATIFIED_REPLICATION_PROTOCOL_V1.json']:
        p=load(name)
        req(p['status'].startswith('DESIGN_ONLY'),f'{name} must not claim outcomes')
        cur=p['current_bounded_result']
        req(cur['favourable_discordances']==4 and cur['adverse_discordances']==0,'paired counts drift')
        req(math.isclose(cur['one_sided_exact_p'],upper(4,4,.5)),'one-sided paired p drift')
        req(math.isclose(cur['two_sided_exact_p'],min(1,2*upper(4,4,.5))),'two-sided paired p drift')
    p24=load('ORION24_STRATIFIED_REPLICATION_PROTOCOL_V1.json')
    req(math.isclose(p24['primary_gate']['null_joint_probability'],alpha,abs_tol=1e-15),'O24 gate alpha drift')

    # Candidate integrity: no outcome language and every candidate has a falsifier/unit.
    ids=[]
    for pid,cs in plan['candidate_registry'].items():
        req(pid in CANONICAL,'candidate attached to noncanonical paper')
        for c in cs:
            ids.append(c['id']); req(c.get('falsifier'),'candidate lacks falsifier'); req(c.get('unit'),'candidate lacks inference unit')
    req(len(ids)==len(set(ids)),'duplicate candidate id')

    print(json.dumps({'status':'PASS_PLAN_COHERENT__NO_SCIENTIFIC_PROMOTION','papers':25,'candidates':len(ids),'o05_control_discovery_domain':33755,'o17_o24_joint_alpha':alpha,'o17_o24_power_at_0_8':power,'paired_4_0_two_sided_p':0.125},indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
