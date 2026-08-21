#!/usr/bin/env python3
"""Independent QG-13 V2 verifier; does not import the V2 checker module."""
from __future__ import annotations
import hashlib,itertools,json,sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; OQ=ROOT/'research/extensions/orion-q';sys.path.insert(0,str(OQ))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
RESULT=ROOT/'artifacts/orion-qg-qg13-v2-support4.json';OUT=ROOT/'artifacts/orion-qg-qg13-v2-generic-verification.json';TOKEN='ORIONQG_QG13_V2_GENERIC_VERIFY='

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def mul(a,b):return int(p10.h.local_mul(a,b))
def sy(a,b):return int(p10.h.local_symp(a,b))
def wt(a):return int(p10.h.local_wt(a))
def desc(a,b,s0,s1):return (int(a!=0),int(b!=0),int(a==b and a!=0),sy(a,b),sy(s0,a),sy(s1,a),sy(s0,b),sy(s1,b))
def avail(a,b,act):return (act=='d0' and a) or (act=='d1' and b) or (act=='db' and a and b)
def aft(a,b,act):return (0,b) if act=='d0' else ((a,0) if act=='d1' else (0,0))
def sig(a,b,s0,s1,act):
    na,nb=aft(a,b,act);old=(sy(a,b),sy(s0,a),sy(s1,a),sy(s0,b),sy(s1,b));new=(sy(na,nb),sy(s0,na),sy(s1,na),sy(s0,nb),sy(s1,nb));return sum((x^y)<<i for i,(x,y) in enumerate(zip(old,new)))
def cost(a,b,p0,p1,p2,c):
    r2=mul(a,b);m=[4,4,4];m[c]=2;return m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(mul(p0,a))+wt(mul(p1,b))+wt(mul(p2,r2))
def delta(a,b,act,p0,p1,p2,c):
    na,nb=aft(a,b,act);return cost(na,nb,p0,p1,p2,c)-cost(a,b,p0,p1,p2,c)
def zs(codes):
    for mask in range(1,1<<len(codes)):
        x=0
        for i,v in enumerate(codes):
            if mask>>i&1:x^=v
        if x==0:return True
    return False
def local():
    reps=defaultdict(list);sigrows=0
    for a,b,s0,s1 in itertools.product(range(4),repeat=4):
        if a==b==0:continue
        d=desc(a,b,s0,s1);reps[d].append((a,b,s0,s1))
        for act in ('d0','d1','db'):
            if avail(a,b,act):sigrows+=1
    prof={}
    for d,rr in reps.items():
        prof[d]={}
        for act in ('d0','d1','db'):
            ar=[r for r in rr if avail(r[0],r[1],act)]
            if not ar:continue
            ss={sig(*r,act) for r in ar};assert len(ss)==1
            # descriptor may contain several letter representatives; take adversarial max per common central.
            by=[]
            for c in range(3):
                vals=[]
                for a,b in sorted({(r[0],r[1]) for r in ar}):
                    vals.extend(delta(a,b,act,*p,c) for p in itertools.product(range(4),repeat=3))
                by.append(max(vals))
            prof[d][act]=(next(iter(ss)),tuple(by))
    cases=sum((int(a!=0)+int(b!=0)+int(a!=0 and b!=0))*3*64 for a,b in itertools.product(range(4),repeat=2) if not(a==b==0))
    return reps,prof,sigrows,cases
def irreducible(combo):
    if not all(d[0] for d in combo):return False
    alpha=b0=b1=0
    for d in combo:alpha^=d[3];b0^=d[4];b1^=d[5]
    if alpha!=1 or ((b0<<1)|b1)==0:return False
    if zs([(d[4]<<1)|d[5] for d in combo if d[2]]):return False
    if zs([(d[3]<<2)|(d[4]<<1)|d[5] for d in combo if d[0] and not d[2]]):return False
    if zs([(d[3]<<2)|(d[6]<<1)|d[7] for d in combo if d[1] and not d[2]]):return False
    return True
def move(combo,prof):
    opts=[]
    for d in combo:
        row=[('none',0,(0,0,0),0)]
        for act,(sg,by) in prof[d].items():row.append((act,sg,by,int(act in ('d0','db') and d[0])))
        opts.append(row)
    for ch in itertools.product(*opts):
        if all(x[0]=='none' for x in ch):continue
        s=0;drop=0
        for x in ch:s^=x[1];drop+=x[3]
        if s or drop<1:continue
        if max(sum(x[2][c] for x in ch) for c in range(3))<=0:return True
    return False
def boundary(w,reps,prof):
    ds=sorted(reps);irr=safe=0
    for inds in itertools.combinations_with_replacement(range(len(ds)),w):
        combo=[ds[i] for i in inds]
        if not irreducible(combo):continue
        irr+=1;safe+=move(combo,prof)
    return irr,safe
def main():
    a=json.loads(RESULT.read_text());u=dict(a);observed=u.pop('result_digest');digest=hashlib.sha256(canon(u).encode()).hexdigest()==observed
    reps,prof,sr,cases=local();w5=boundary(5,reps,prof);w4=boundary(4,reps,prof)
    checks={'schema':a.get('schema')=='ORION.QG.QG13V2.R6ISupport4.v1','digest':digest,'descriptor_count':len(reps)==a.get('descriptor_count')==28,'signature_rows':sr==a.get('signature_domain_rows')==528,'cost_cases':cases==a.get('unique_local_cost_domain_cases')==6336,'support5_irreducible':w5[0]==a['support5']['irreducible_count']==324,'support5_all_safe':w5[1]==a['support5']['certified_move_count']==324,'support4_irreducible':w4[0]==a['support4_boundary']['irreducible_count']==432,'support4_residual':w4[0]-w4[1]==a['support4_boundary']['unresolved_count']==36,'candidate_terminal':a.get('terminal')=='QG13_V2_R6I_SUPPORT4_CANDIDATE_COMPLETE','no_support3_authority':a.get('support3_authority') is False,'no_tightness4_authority':a.get('tightness4_authority') is False,'no_novelty':a.get('novelty_authority') is False}
    out={'schema':'ORION.QG.QG13V2.GenericVerification.v1','decision':'ACCEPT' if all(checks.values()) else 'REJECT','checks':checks,'independent_counts':{'descriptors':len(reps),'signature_rows':sr,'cost_cases':cases,'support5':{'irreducible':w5[0],'safe':w5[1]},'support4':{'irreducible':w4[0],'safe':w4[1],'unresolved':w4[0]-w4[1]}},'novelty_authority':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
