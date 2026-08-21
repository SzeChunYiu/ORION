#!/usr/bin/env python3
"""QG-13 V3: three-column combined-edit mining for R6I."""
from __future__ import annotations

import argparse, hashlib, itertools, json, sys
from pathlib import Path
from typing import Any

REPO_ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO_ROOT/'research'/'extensions'/'orion-q'))
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa:E402

BASE='cad8b1b4d3be3668449658d10ef718eb1682d1c9'
ISSUE='SzeChunYiu/ORION#785'
OUT=REPO_ROOT/'artifacts'/'orion-qg-qg13v3-three-column.json'
TOKEN='ORIONQG_QG13V3='
ACTS=('A','B','AB')

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def wt(a):return int(r6i._LW[a])
def mul(a,b):return int(r6i._MUL[a,b])
def sy(a,b):return int(r6i._SYMP[a,b])
def syn(r0,r1,s0,s1):return (sy(r0,r1)<<4)|(sy(s0,r0)<<3)|(sy(s1,r0)<<2)|(sy(s0,r1)<<1)|sy(s1,r1)
def apply(r0,r1,a):return (0,r1) if a=='A' else ((r0,0) if a=='B' else (0,0))
def cost(r0,r1,p0,p1,p2,c):
    rs=(r0,r1,mul(r0,r1));m=[4,4,4];m[c]=2;ps=(p0,p1,p2)
    return sum(m[k]*wt(rs[k])+wt(mul(ps[k],rs[k])) for k in range(3))
def optcode(vals):
    z=0
    for v in vals:z=(z<<2)|int(v)
    return z

def bind_prod():
    bad=[];checked=0
    for r0,r1,s0,s1 in itertools.product(range(4),repeat=4):
        old10=int(r6i._DELTA[optcode((r0,r1,0,0,s0,s1))]);old5=syn(r0,r1,s0,s1)
        for a in ACTS:
            nr0,nr1=apply(r0,r1,a)
            if (nr0,nr1)==(r0,r1):continue
            d10=old10^int(r6i._DELTA[optcode((nr0,nr1,0,0,s0,s1))]);d5=old5^syn(nr0,nr1,s0,s1)
            rec=(((d10>>0)&1)<<4)|(((d10>>6)&1)<<3)|(((d10>>7)&1)<<2)|(((d10>>8)&1)<<1)|((d10>>9)&1)
            dup=((d10>>2)&1)==((d10>>6)&1) and ((d10>>3)&1)==((d10>>7)&1) and ((d10>>4)&1)==((d10>>8)&1) and ((d10>>5)&1)==((d10>>9)&1) and ((d10>>1)&1)==0
            checked+=1
            if rec!=d5 or not dup:bad.append([r0,r1,s0,s1,a,d10,d5,rec])
    return {'checked':checked,'failure_count':len(bad),'failures':bad[:20],'all_exact':not bad}

def resources():
    st={};rows=0
    for r0,r1,s0,s1,p0,p1,p2,c in itertools.product(range(4),range(4),range(4),range(4),range(4),range(4),range(4),range(3)):
        olds=syn(r0,r1,s0,s1);oldc=cost(r0,r1,p0,p1,p2,c)
        for a in ACTS:
            nr0,nr1=apply(r0,r1,a)
            if (nr0,nr1)==(r0,r1):continue
            sig=olds^syn(nr0,nr1,s0,s1);d=cost(nr0,nr1,p0,p1,p2,c)-oldc
            rec=st.setdefault((a,sig),{'action':a,'signature':sig,'count':0,'min_delta':10**9,'max_delta':-10**9,'max_witness':None})
            rec['count']+=1;rec['min_delta']=min(rec['min_delta'],d)
            if d>rec['max_delta']:
                rec['max_delta']=d;rec['max_witness']={'r':[r0,r1],'s':[s0,s1],'p':[p0,p1,p2],'central':c,'delta':d}
            rows+=1
    return st,{'enumerated_action_rows':rows,'action_signature_classes':len(st),'rows':[st[k] for k in sorted(st)]}

def pair_safe(st):
    safe=set();tot=unsafe=0
    for (ka,ra),(kb,rb) in itertools.product(st.items(),repeat=2):
        a,sa=ka;b,sb=kb
        if sa!=sb:continue
        tot+=1
        if ra['max_delta']+rb['max_delta']<=0:safe.add((a,sa,b,sb))
        else:unsafe+=1
    return safe,{'classes':tot,'safe':len(safe),'unsafe':unsafe}

def triple_safe(st):
    safe=set();tot=unsafe=0
    items=list(st.items())
    for (ka,ra),(kb,rb),(kc,rc) in itertools.product(items,repeat=3):
        a,sa=ka;b,sb=kb;c,sc=kc
        if sa^sb^sc:continue
        tot+=1
        worst=ra['max_delta']+rb['max_delta']+rc['max_delta']
        if worst<=0:safe.add((a,sa,b,sb,c,sc))
        else:unsafe+=1
    return safe,{'classes':tot,'safe':len(safe),'unsafe':unsafe}

def zs(vals):
    for mask in range(1,1<<len(vals)):
        x=0
        for i,v in enumerate(vals):
            if (mask>>i)&1:x^=v
        if x==0:return True
    return False

def accepting(s):
    a=(s>>4)&1;l0=2*((s>>3)&1)+((s>>2)&1);l1=2*((s>>1)&1)+(s&1)
    return a==1 and l0 in (1,2,3) and l1 in (1,2,3) and l0!=l1

def struct(r0,r1,s0,s1):
    ss=syn(r0,r1,s0,s1);co=r0==r1 and r0!=0;alpha=sy(r0,r1)
    n0=None if r0==0 or co else ((alpha<<2)|(sy(s0,r0)<<1)|sy(s1,r0))
    n1=None if r1==0 or co else ((alpha<<2)|(sy(s0,r1)<<1)|sy(s1,r1))
    cc=None if not co else ((sy(s0,r0)<<1)|sy(s1,r0));acts=[]
    for a in ACTS:
        nr0,nr1=apply(r0,r1,a)
        if (nr0,nr1)==(r0,r1):continue
        acts.append({'action':a,'signature':ss^syn(nr0,nr1,s0,s1),'d0':int(r0!=0 and nr0==0),'d1':int(r1!=0 and nr1==0)})
    return {'syndrome':ss,'support0':int(r0!=0),'support1':int(r1!=0),'n0':n0,'n1':n1,'c':cc,'actions':acts}

def types():
    u={}
    for vals in itertools.product(range(4),repeat=4):
        r=struct(*vals);k=canon(r)
        if k not in u:u[k]={'record':r,'representative':list(vals)}
    return [u[k] for k in sorted(u)]
def irreducible(p,ts):
    n0=[];n1=[];cc=[]
    for i in p:
        r=ts[i]['record']
        if r['n0'] is not None:n0.append(r['n0'])
        if r['n1'] is not None:n1.append(r['n1'])
        if r['c'] is not None:cc.append(r['c'])
    return not zs(n0) and not zs(n1) and not zs(cc)
def move2(p,ts,safe):
    rs=[ts[i]['record'] for i in p];u0=sum(r['support0'] for r in rs);u1=sum(r['support1'] for r in rs);before=(max(u0,u1),u0+u1)
    for i,j in itertools.combinations(range(5),2):
        for a in rs[i]['actions']:
            for b in rs[j]['actions']:
                if a['signature']!=b['signature']:continue
                k=(a['action'],a['signature'],b['action'],b['signature']);rk=(b['action'],b['signature'],a['action'],a['signature'])
                if k not in safe and rk not in safe:continue
                v0=u0-a['d0']-b['d0'];v1=u1-a['d1']-b['d1']
                if (max(v0,v1),v0+v1)<before:return True
    return False
def move3(p,ts,st,safe):
    rs=[ts[i]['record'] for i in p];u0=sum(r['support0'] for r in rs);u1=sum(r['support1'] for r in rs);before=(max(u0,u1),u0+u1)
    for i,j,k in itertools.combinations(range(5),3):
        for a in rs[i]['actions']:
            for b in rs[j]['actions']:
                for c in rs[k]['actions']:
                    if a['signature']^b['signature']^c['signature']:continue
                    key=(a['action'],a['signature'],b['action'],b['signature'],c['action'],c['signature'])
                    if key not in safe:continue
                    v0=u0-a['d0']-b['d0']-c['d0'];v1=u1-a['d1']-b['d1']-c['d1']
                    if (max(v0,v1),v0+v1)<before:return True
    return False

def census(st,s2,s3):
    ts=types();accepted=irr=s5=e2=e3=union=0;v2_un=0;v3_closes_v2=0;first3=None;first_v2_survive=None
    for p in itertools.combinations_with_replacement(range(len(ts)),5):
        total=0
        for i in p:total^=ts[i]['record']['syndrome']
        if not accepting(total):continue
        accepted+=1
        if not irreducible(p,ts):continue
        irr+=1
        u0=sum(ts[i]['record']['support0'] for i in p);u1=sum(ts[i]['record']['support1'] for i in p)
        if max(u0,u1)!=5:continue
        s5+=1;m2=move2(p,ts,s2);m3=move3(p,ts,st,s3)
        if m2:e2+=1
        else:
            v2_un+=1
            if m3:v3_closes_v2+=1
            elif first_v2_survive is None:first_v2_survive={'pattern_indices':list(p),'supports':[u0,u1],'representatives':[ts[i]['representative'] for i in p]}
        if m3:e3+=1
        elif first3 is None:first3={'pattern_indices':list(p),'supports':[u0,u1],'representatives':[ts[i]['representative'] for i in p]}
        if m2 or m3:union+=1
    return {'structural_type_count':len(ts),'accepted':accepted,'irreducible':irr,'support5':s5,'e2_covered':e2,'e3_covered':e3,'e3_uncovered':s5-e3,'v2_uncovered_recomputed':v2_un,'v3_closes_v2':v3_closes_v2,'v2_survive_v3':v2_un-v3_closes_v2,'cumulative_e2_e3_covered':union,'cumulative_uncovered':s5-union,'first_e3_uncovered':first3,'first_v2_obstruction_surviving_v3':first_v2_survive}

def run():
    b=bind_prod();st,res=resources();s2,p2=pair_safe(st);s3,p3=triple_safe(st);c=census(st,s2,s3)
    if not b['all_exact']:terminal='QG13V3_SEMANTIC_QUOTIENT_INCOMPLETE'
    elif p3['safe']==0:terminal='QG13V3_RESOURCE_BOUNDARY'
    elif c['e3_uncovered']==0:terminal='QG13V3_SUPPORT4_CANDIDATE'
    elif c['v2_survive_v3']==0 and c['e3_uncovered']>0:terminal='QG13V3_V2_OBSTRUCTIONS_CLOSED_BUT_NEW_OBSTRUCTION_REMAINS'
    elif c['v2_survive_v3']>0:terminal='QG13V3_MINIMAL_THREE_COLUMN_OBSTRUCTION'
    else:terminal='QG13V3_CANNOT_CHECK'
    out={'schema':'ORION.QG.QG13V3.ThreeColumn.v1','issue':ISSUE,'base_revision':BASE,'terminal':terminal,'production_binding':b,'action_resource':res,'pair_reference':p2,'triple_safety':p3,'census':c,'v2_result_file_opened_during_synthesis':False,'new_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False,'network_access':False,'chemistry_sources_read':False,'protected_subject_read':False}
    u=dict(out);out['result_digest']=hashlib.sha256(canon(u).encode()).hexdigest();return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(OUT));args=ap.parse_args();r=run();p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':r['terminal'],'digest':r['result_digest'],'e3_covered':r['census']['e3_covered'],'v3_closes_v2':r['census']['v3_closes_v2'],'cumulative':r['census']['cumulative_e2_e3_covered']}));return 0
if __name__=='__main__':raise SystemExit(main())
