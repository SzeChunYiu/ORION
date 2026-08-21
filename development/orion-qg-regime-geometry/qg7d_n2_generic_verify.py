#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-7d N2_DIRECT."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'artifacts/orion-qg-qg7d-n2-direct.json'
PARENT=ROOT/'research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json'
PROTO=ROOT/'development/orion-qg-regime-geometry/QG7D_PINNED_COMM_S2_PROTOCOL_V1.md'
AMEND=ROOT/'development/orion-qg-regime-geometry/QG7D_N2_DIRECT_PROTOCOL_AMENDMENT_V1.md'
OUT=ROOT/'artifacts/orion-qg-qg7d-n2-generic-verification.json'
TOKEN='ORIONQG_QG7D_N2_GENERIC='
INF=10**9


def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def pc(v): return int(v).bit_count()
def wt(k): return pc(k[0]|k[1])
def mul(a,b): return (a[0]^b[0],a[1]^b[1])
def symp(a,b): return (pc(a[0]&b[1])+pc(a[1]&b[0]))&1
def lmul(a,b):
    if a==0:return b
    if b==0:return a
    if a==b:return 0
    return 6-a-b
def lsy(a,b): return int(a!=0 and b!=0 and a!=b)
def letter(k,q): return {(0,0):0,(1,0):1,(1,1):2,(0,1):3}[((k[0]>>q)&1,(k[1]>>q)&1)]
def letter_key(v,q):
    x,z={0:(0,0),1:(1,0),2:(1,1),3:(0,1)}[v]; return (x<<q,z<<q)
def key(letters):
    o=(0,0)
    for q,v in enumerate(letters): o=mul(o,letter_key(int(v),q)) if v else o
    return o

def f3(a,b,c): return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
F3=np.array([[[f3(a,b,c) for c in range(4)] for b in range(4)] for a in range(4)],dtype=np.int16)
KEYS=tuple((x,z) for x in range(4) for z in range(4))
PERMS=((0,1),(1,0))


def decode_core(idx): return idx//16,(idx//4)%4,idx%4

def direct_target(row):
    if row['case']!='PA': raise AssertionError('non-PA committed row')
    ja=int(row['ja']); Rb=int(row['R_b']); Ra=int(row['R_a']); p=int(row['p'])
    t0b,t1b,t21b=decode_core(int(row['coreB']));t0a,t1a,t21a=decode_core(int(row['coreA']))
    e0b,e1b=divmod(int(row['envB']),4);u0b,v0b=divmod(e0b,4)
    e0a,e1a=divmod(int(row['envA']),4);u0a,v0a=divmod(e0a,4)
    t20b=lmul(u0b,3);t20a=u0a;t30b=v0b
    if ja==0:t30a=lmul(v0a,3);t31b=e1b;t31a=lmul(e1a,1)
    else:t30a=v0a;t31b=lmul(e1b,1);t31a=e1a
    return ((key([t0b,t0a]),key([t1b,t1a])),(key([t20b,t20a]),key([t21b,t21a])),(key([t30b,t30a]),key([t31b,t31a])))


def pair_space(cap):
    return tuple((a,b) for a in KEYS for b in KEYS if symp(a,b)==1 and wt(a)<=cap and wt(b)<=cap)


def exact_family(tp,cap):
    pairs=pair_space(cap); best=INF
    for pbperm,pcperm in itertools.product(PERMS,repeat=2):
        ordered=(tp[0],(tp[1][pbperm[0]],tp[1][pbperm[1]]),(tp[2][pcperm[0]],tp[2][pcperm[1]]))
        for centrals in itertools.product((0,1),repeat=3):
            for s in KEYS[1:]:
                for orient in ((0,1),(1,0)):
                    aps=[p for p in pairs if symp(s,p[0])==orient[0] and symp(s,p[1])==orient[1]]
                    if not aps: continue
                    block=[]
                    for j in range(3):
                        base=[]; letters=[]
                        for r0,r1 in aps:
                            c=centrals[j]
                            u=4*(wt((r0,r1)[1-c])-1)+2*(wt((r0,r1)[c])-1)
                            ts=(mul(ordered[j][0],r0),mul(ordered[j][1],r1))
                            base.append(u)
                            letters.append([[letter(ts[k],q) for q in range(2)] for k in range(2)])
                        block.append((np.array(base,dtype=np.int16),np.array(letters,dtype=np.int8)))
                    (ba,la),(bb,lb),(bc,lc)=block
                    total=ba[:,None,None].astype(np.int16)+bb[None,:,None]+bc[None,None,:]+np.int16(2*wt(s))
                    for k in range(2):
                        for q in range(2):
                            total=total+F3[la[:,k,q][:,None,None],lb[:,k,q][None,:,None],lc[:,k,q][None,None,:]]
                    v=int(total.min())
                    if v<best: best=v
    return best


def union_qubits(tp):
    mask=0
    for a,b in tp: mask|=a[0]|a[1]|b[0]|b[1]
    return [q for q in range(2) if (mask>>q)&1]

def block_bprime_options(pair,qt,v,homes):
    rows=[]; vk=letter_key(v,qt)
    for c in (1,2,3):
        if c==v:continue
        ck=letter_key(c,qt)
        for sigma in (0,1): rows.append((0,mul(pair[sigma],vk),mul(pair[1-sigma],ck)))
    for qh in homes:
        for ell in (1,2,3):
            if ell==v:continue
            ek=letter_key(ell,qt)
            for m0 in (1,2,3):
                m0k=letter_key(m0,qh)
                for m1 in (1,2,3):
                    if m1==m0:continue
                    anti=mul(ek,letter_key(m1,qh))
                    for sigma in (0,1): rows.append((2,mul(pair[sigma],m0k),mul(pair[1-sigma],anti)))
    return rows

def exact_bprime(tp):
    uq=union_qubits(tp); pool=list(uq)
    for q in range(2):
        if q not in uq: pool.append(q); break
    pool=sorted(pool); qtags=list(uq)+[q for q in pool if q not in uq]
    best=INF
    for qt in qtags:
        homes=tuple(q for q in pool if q!=qt)
        if not homes:continue
        for v in (1,2,3):
            opts=[block_bprime_options(tp[j],qt,v,homes) for j in range(3)]
            for oa in opts[0]:
                for ob in opts[1]:
                    for oc in opts[2]:
                        if oa[0]==ob[0]==oc[0]==0:continue
                        val=2+oa[0]+ob[0]+oc[0]
                        for k in (0,1):
                            for q in range(2): val+=f3(letter(oa[1+k],q),letter(ob[1+k],q),letter(oc[1+k],q))
                        if val<best:best=val
    return None if best>=INF else best


def bsecond_impossible_n2(tp):
    # B'' requires two distinct tag qubits and >=1 off-tag phantom home. At n=2 no such home exists.
    return True


def verify_selected(rec):
    tp=tuple((tuple(a),tuple(b)) for a,b in rec['target_pairs'])
    cxx=exact_family(tp,2); cd=exact_family(tp,1); bp=exact_bprime(tp)
    ev=rec['evaluation']; inc=min(cd, INF if bp is None else bp)
    return {
        'target_reconstructed': [[list(a),list(b)] for a,b in direct_target(rec['parent_row'])]==rec['target_pairs'],
        'C_Dxx_independent': cxx==int(ev['C_Dxx']),
        'C_Dplus_independent': cd==int(ev['C_Dplus']),
        'Bprime_independent': bp==ev['f_Bprime'],
        'Bsecond_impossible': ev['f_Bsecond'] is None and bsecond_impossible_n2(tp),
        'strict_independent': cxx<inc,
        'dp_replay_bound': ev['dp_replay'] is not None and ev['dp_replay']['pass'] is True and int(ev['dp_replay']['C_DP'])==cxx,
    }


def main():
    a=json.loads(RESULT.read_text());p=json.loads(PARENT.read_text());u=dict(a);obs=u.pop('result_digest',None)
    positive=a.get('terminal')=='QG7D_BTRIPLEPRIME_REGIME_FOUND__PINNED_COMM_S2_EXACT_WITNESS'
    selected_checks={} if not positive else verify_selected(a['selected'])
    # Negative authority is bounded only: independently spot-check four deterministic rows.
    spot=[]
    if not positive:
        for idx in (0,13,26,39):
            rec=a['rows'][idx];tp=tuple((tuple(x),tuple(y)) for x,y in rec['target_pairs'])
            cd=exact_family(tp,1);bp=exact_bprime(tp);inc=min(cd,INF if bp is None else bp)
            spot.append({'index':idx,'target_reconstructed':[[list(x),list(y)] for x,y in direct_target(rec['parent_row'])]==rec['target_pairs'],
                         'Dplus':cd==rec['evaluation']['C_Dplus'],'Bprime':bp==rec['evaluation']['f_Bprime'],
                         'no_false_gap':int(rec['evaluation']['C_Dxx'])>=inc})
    checks={
        'schema':a.get('schema')=='ORIONQG.QG7D.N2Direct.v1',
        'digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),
        'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTO.read_bytes()).hexdigest(),
        'amendment':a.get('amendment_sha256')==hashlib.sha256(AMEND.read_bytes()).hexdigest(),
        'parent_digest':p.get('result_digest')=='0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6',
        'rows':a.get('rows_evaluated')==40,
        'positive_selected_independent':(not positive) or (selected_checks and all(selected_checks.values())),
        'negative_spotchecks':positive or (len(spot)==4 and all(all(v for k,v in r.items() if k!='index') for r in spot)),
        'no_alln_authority':a.get('global_all_n_closure_authority') is False,
        'authority':a.get('novelty_authority') is False and a.get('r6_authority') is False and a.get('physical_quantum_advantage_claim') is False,
    }
    decision='ACCEPT_BTRIPLEPRIME_WITNESS' if positive and all(checks.values()) else ('ACCEPT_BOUNDED_NEGATIVE' if (not positive) and all(checks.values()) else 'REJECT')
    out={'schema':'ORIONQG.QG7D.N2GenericVerification.v1','issue':'SzeChunYiu/ORION#836','decision':decision,'checks':checks,'all_checks':all(checks.values()),'selected_checks':selected_checks,'negative_spotchecks':spot,'terminal':a.get('terminal'),'novelty_authority':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(out));return 0
if __name__=='__main__':raise SystemExit(main())
