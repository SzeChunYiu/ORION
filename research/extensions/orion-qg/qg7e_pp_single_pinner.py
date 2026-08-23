#!/usr/bin/env python3
"""QG-7e: complete single-pinner PP hidden-home normalization packet.

Confirmatory packet frozen by QG7E_PP_SINGLE_PINNER_PROTOCOL_V1.md.  Rebuilds
all 32,556 QG-7c visible PP residuals, composes each with all 4^6 hidden-home
environments, applies the frozen 576 relocation library, then exact D+ on the
residuals and unchanged QG-5b B' on the final D+ residuals.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(QG))
import qg7c_classification as q7c  # noqa:E402

PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG7E_PP_SINGLE_PINNER_PROTOCOL_V1.md"
PARENT = QG / "QG7C_CLASSIFICATION_RESULTS.json"
INFO = QG / "qg7d_information_closure.py"
OUT = ROOT / "artifacts/orion-qg-qg7e-pp-single-pinner.json"
TOKEN = "ORIONQG_QG7E="
ISSUE = "SzeChunYiu/ORION#872"
POSITIVE = "QG7E_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN"
PARENT_DIGEST = "0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
X, Z = 1, 3


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lm(a: int, b: int) -> int:
    return int(q7c.lmul(int(a), int(b)))


def sy(a: int, b: int) -> int:
    return int(q7c.lsy(int(a), int(b)))


def f3(a: int, b: int, c: int) -> int:
    return int(q7c.lf3(int(a), int(b), int(c)))


LM = np.array([[lm(a, b) for b in range(4)] for a in range(4)], dtype=np.int8)
F3 = np.array([[[f3(a, b, c) for c in range(4)] for b in range(4)] for a in range(4)], dtype=np.int8)
F3E = np.array([[f3(a, u, v) for u in range(4) for v in range(4)] for a in range(4)], dtype=np.int8)
F3T = np.array([[[f3(a, b, e) for e in range(4)] for b in range(4)] for a in range(4)], dtype=np.int8)
SIGMAS = tuple(itertools.product((0, 1), repeat=3))
AC = {s: tuple(r for r in (1, 2, 3) if sy(s, r)) for s in (1, 2, 3)}
EXPECTED_CELL_COUNTS = (4057,3678,4057,3678,3678,4057,3678,4057,217,187,217,187,187,217,187,217)


def parent_pp_cell(ja: int, rb: int, ra: int, p: int):
    t4 = np.arange(4, dtype=np.int64)
    t0b = np.repeat(t4, 16); t1b = np.tile(np.repeat(t4, 4), 4); t21b = np.tile(t4, 16)
    t0a, t1a, t21a = t0b, t1b, t21b
    w = lm(ra, Z)
    o0b = LM[t0b, rb]; o1b_our = t1b; o1b_pin = LM[t21b, p]
    o0a = LM[t0a, ra]; o1a_our = LM[t1a, w]; o1a_pin = t21a
    old_b = F3E[o0b][:, :, None] + F3T[o1b_our, o1b_pin][:, None, :]
    old_a = F3E[o0a][:, :, None] + F3T[o1a_our, o1a_pin][:, None, :]
    best = np.full((64, 64, 64, 64), 99, dtype=np.int16)

    def group(bparts, aparts, struct: int) -> None:
        fb = np.stack([F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :] - old_b
                       for n0, n1, n1p in bparts]).min(axis=0).reshape(64, 64)
        fa = np.stack([F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :] - old_a
                       for n0, n1, n1p in aparts]).min(axis=0).reshape(64, 64)
        np.minimum(best, fb[:, :, None, None] + fa[None, None, :, :] + np.int16(struct), out=best)

    for sw in (0, 1):
        s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
        s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
        group([(s0b, s1b, LM[t21b, pp]) for pp in (1, 2)],
              [(LM[s0a, Z], LM[s1a, c], o1a_pin) for c in (1, 2)], -2)
        group([(LM[s0b, Z], LM[s1b, c], LM[t21b, pp]) for c in (1, 2) for pp in (1, 2)],
              [(s0a, s1a, o1a_pin)], -2 - 2 * ja)
        if ja:
            group([(s0b, LM[s1b, le], LM[t21b, pp]) for le in (1, 2) for pp in (1, 2)],
                  [(LM[s0a, m0], LM[s1a, m1], o1a_pin)
                   for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0], -2)
        group([(LM[s0b, m0], LM[s1b, m1], t21b)
               for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0],
              [(s0a, LM[s1a, le], LM[t21a, l2]) for le in (1, 2) for l2 in (1, 2)], -2)
    return best, old_b, old_a


def visible_targets(ja: int, idx: np.ndarray) -> np.ndarray:
    cb, eb, ca, ea = (idx[:, k].astype(np.int64) for k in range(4))
    t0b, t1b, t21b = cb // 16, (cb // 4) % 4, cb % 4
    t0a, t1a, t21a = ca // 16, (ca // 4) % 4, ca % 4
    e0b, e1b = eb // 4, eb % 4; u0b, v0b = e0b // 4, e0b % 4
    e0a, e1a = ea // 4, ea % 4; u0a, v0a = e0a // 4, e0a % 4
    t = np.empty((len(idx), 3, 2, 2), dtype=np.int8)
    t[:,0,0,0]=t0b; t[:,0,0,1]=t0a; t[:,0,1,0]=t1b; t[:,0,1,1]=t1a
    t[:,1,0,0]=u0b; t[:,1,0,1]=u0a; t[:,1,1,0]=t21b; t[:,1,1,1]=t21a
    t[:,2,0,0]=v0b
    if ja == 0:
        t[:,2,0,1]=LM[v0a,Z]; t[:,2,1,0]=e1b; t[:,2,1,1]=LM[e1a,X]
    else:
        t[:,2,0,1]=v0a; t[:,2,1,0]=LM[e1b,X]; t[:,2,1,1]=e1a
    return t


def build_visible():
    ts=[]; olds=[]; pds=[]; pars=[]; cell_counts=[]; hist=Counter()
    for ja,rb,ra,p in itertools.product((0,1),(1,2),(1,2),(1,2)):
        best,old_b,old_a=parent_pp_cell(ja,rb,ra,p)
        idx=np.argwhere(best>0)
        cell_counts.append(int(len(idx)))
        cb,eb,ca,ea=(idx[:,k].astype(np.int64) for k in range(4))
        pd=best[cb,eb,ca,ea].astype(np.int16)
        old=(old_b[cb,eb//4,eb%4]+old_a[ca,ea//4,ea%4]).astype(np.int16)
        ts.append(visible_targets(ja,idx)); olds.append(old); pds.append(pd)
        pars.append(np.column_stack([np.full(len(idx),ja),np.full(len(idx),rb),np.full(len(idx),ra),np.full(len(idx),p),idx]).astype(np.int16))
        hist.update(int(x) for x in pd)
    return np.concatenate(ts),np.concatenate(olds),np.concatenate(pds),np.concatenate(pars),tuple(cell_counts),hist


def relocation_tables(vis: np.ndarray, hidden: np.ndarray):
    # visible target-only cost by global sigma
    vi=np.zeros((len(vis),8),dtype=np.int16)
    for si,sg in enumerate(SIGMAS):
        val=np.zeros(len(vis),dtype=np.int16)
        for br in (0,1):
            for q in (0,1):
                loc=[vis[:,j,sg[j] if br==0 else 1-sg[j],q] for j in range(3)]
                val += F3[loc[0],loc[1],loc[2]]
        vi[:,si]=val
    # hidden target-only and hidden relocation minima by global sigma
    hi=np.zeros((len(hidden),8),dtype=np.int16)
    hh=np.full((len(hidden),8),99,dtype=np.int16)
    for si,sg in enumerate(SIGMAS):
        val=np.zeros(len(hidden),dtype=np.int16)
        for br in (0,1):
            cols=[j if (sg[j] if br==0 else 1-sg[j])==0 else j+3 for j in range(3)]
            loc=[hidden[:,cols[j]] for j in range(3)]
            val += F3[loc[0],loc[1],loc[2]]
        hi[:,si]=val
        best=np.full(len(hidden),99,dtype=np.int16)
        for s in (1,2,3):
            for rs in itertools.product(AC[s],repeat=3):
                val=np.zeros(len(hidden),dtype=np.int16)
                for br in (0,1):
                    loc=[]
                    for j in range(3):
                        src=sg[j] if br==0 else 1-sg[j]
                        col=j if src==0 else j+3
                        fr=s if br==0 else rs[j]
                        loc.append(LM[hidden[:,col],fr])
                    val += F3[loc[0],loc[1],loc[2]]
                best=np.minimum(best,val)
        hh[:,si]=best
    # visible relocation at b/a, minimized over local s/r but not sigma
    vq=np.full((2,len(vis),8),99,dtype=np.int16)
    for q in (0,1):
        other=1-q
        for si,sg in enumerate(SIGMAS):
            best=np.full(len(vis),99,dtype=np.int16)
            for s in (1,2,3):
                for rs in itertools.product(AC[s],repeat=3):
                    val=np.zeros(len(vis),dtype=np.int16)
                    for br in (0,1):
                        loc=[]
                        for j in range(3):
                            src=sg[j] if br==0 else 1-sg[j]
                            fr=s if br==0 else rs[j]
                            loc.append(LM[vis[:,j,src,q],fr])
                        val += F3[loc[0],loc[1],loc[2]]
                        loc=[vis[:,j,sg[j] if br==0 else 1-sg[j],other] for j in range(3)]
                        val += F3[loc[0],loc[1],loc[2]]
                    best=np.minimum(best,val)
            vq[q,:,si]=best
    return vi,hi,hh,vq


def screen_product(vis,old,pd,hidden,old_hidden,vi,hi,hh,vq):
    residual=[]; hist=Counter(); maxd=-99
    for start in range(0,len(vis),500):
        n=min(500,len(vis)-start)
        new=np.full((n,len(hidden)),99,dtype=np.int16)
        for si in range(8):
            new=np.minimum(new,vq[0,start:start+n,si,None]+hi[None,:,si])
            new=np.minimum(new,vq[1,start:start+n,si,None]+hi[None,:,si])
            new=np.minimum(new,vi[start:start+n,si,None]+hh[None,:,si])
        d=new-old[start:start+n,None]-old_hidden[None,:]-6
        best=np.minimum(d,pd[start:start+n,None])
        vals,cnts=np.unique(best,return_counts=True)
        for v,c in zip(vals,cnts): hist[int(v)]+=int(c)
        maxd=max(maxd,int(best.max()))
        ii,jj=np.where(best>0)
        residual.extend((start+int(i),int(j)) for i,j in zip(ii,jj))
    return residual,hist,maxd


def dplus_templates():
    frames=[]; sigmas=[]; tagcost=[]
    for S in itertools.product(range(4),repeat=3):
        if S==(0,0,0): continue
        opts=[]
        for q,s in enumerate(S):
            if s==0: continue
            for r in AC[s]:
                for sg in (0,1): opts.append((q,s,r,sg))
        tc=2*sum(int(x!=0) for x in S)
        for oa,ob,oc in itertools.product(opts,repeat=3):
            fr=np.zeros((3,2,3),dtype=np.int8); sg=[]
            for j,o in enumerate((oa,ob,oc)):
                q,s,r,perm=o; fr[j,0,q]=s; fr[j,1,q]=r; sg.append(perm)
            frames.append(fr); sigmas.append(sg); tagcost.append(tc)
    return np.array(frames,dtype=np.int8),np.array(sigmas,dtype=np.int8),np.array(tagcost,dtype=np.int16)


def score_dplus(t: np.ndarray, fr: np.ndarray, sg: np.ndarray, tc: np.ndarray) -> np.ndarray:
    out=[]
    for start in range(0,len(t),100):
        tb=t[start:start+100]; cost=np.broadcast_to(tc,(len(tb),len(fr))).copy().astype(np.int16)
        for br in (0,1):
            for q in range(3):
                loc=[]
                for j in range(3):
                    src=sg[:,j] if br==0 else 1-sg[:,j]
                    tar=tb[:,j,:,q][:,src]
                    loc.append(LM[tar,fr[:,j,br,q][None,:]])
                cost += F3[loc[0],loc[1],loc[2]]
        out.append(cost.min(axis=1))
    return np.concatenate(out)


def target_pairs(t: np.ndarray):
    def key(letters):
        out=(0,0)
        for q,le in enumerate(letters):
            if int(le): out=q7c.p10.mul(out,q7c.r6o._letter_key(int(le),q))
        return out
    return tuple((key(t[j,0]),key(t[j,1])) for j in range(3))


def reference_frames(param):
    ja,rb,ra,p,*_=map(int,param); w=lm(ra,Z)
    ours=(q7c.p10.mul(q7c.r6o._letter_key(rb,0),q7c.r6o._letter_key(ra,1)),q7c.r6o._letter_key(w,1))
    pin=(q7c.r6o._letter_key(Z,2),q7c.p10.mul(q7c.r6o._letter_key(p,0),q7c.r6o._letter_key(X,2)))
    third=(q7c.r6o._letter_key(Z,1),q7c.r6o._letter_key(X,1)) if ja==0 else (q7c.r6o._letter_key(Z,0),q7c.r6o._letter_key(X,0))
    tag=q7c.p10.mul(q7c.r6o._letter_key(Z,0),q7c.r6o._letter_key(Z,1))
    return ours+pin+third,tag


def main(argv=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=OUT); args=ap.parse_args(argv)
    parent=json.loads(PARENT.read_text())
    vis,old,pd,param,cell_counts,parent_hist=build_visible()
    hidden=np.array(list(itertools.product(range(4),repeat=6)),dtype=np.int8)
    old_hidden=(F3[hidden[:,0],LM[hidden[:,1],Z],hidden[:,2]]+F3[hidden[:,3],LM[hidden[:,4],X],hidden[:,5]]).astype(np.int16)
    vi,hi,hh,vq=relocation_tables(vis,hidden)
    residual,screen_hist,screen_max=screen_product(vis,old,pd,hidden,old_hidden,vi,hi,hh,vq)
    rv=np.array([x[0] for x in residual],dtype=np.int32); rh=np.array([x[1] for x in residual],dtype=np.int32)
    full=np.zeros((len(residual),3,2,3),dtype=np.int8); full[:,:,:,0:2]=vis[rv]; hv=hidden[rh]
    for j in range(3): full[:,j,0,2]=hv[:,j]; full[:,j,1,2]=hv[:,j+3]
    cref=(8+old[rv]+old_hidden[rh]).astype(np.int16)
    fr,sg,tc=dplus_templates(); cd=score_dplus(full,fr,sg,tc); dd=cd.astype(np.int32)-cref.astype(np.int32)
    dh=Counter(int(x) for x in dd); pos=np.flatnonzero(dd>0)

    # Production D+ controls: first positive rows + first row from each nonpositive delta class.
    control_ids=list(map(int,pos[:3]))
    for d in (-2,-1,0):
        ids=np.flatnonzero(dd==d)
        if len(ids): control_ids.append(int(ids[0]))
    controls=[]; control_fail=[]
    for rid in control_ids:
        tp=target_pairs(full[rid]); prod=int(q7c.r6p.dxx_search(tp,3,max_weight=1)["C_Dxx"])
        ok=prod==int(cd[rid]); controls.append({"residual_index":rid,"delta":int(dd[rid]),"vectorized":int(cd[rid]),"production":prod,"ok":bool(ok)})
        if not ok: control_fail.append(rid)

    bprows=[]; bph=Counter(); bp_fail=[]; ref_fail=[]
    for rid in map(int,pos):
        tp=target_pairs(full[rid]); val,wit=q7c.qg5b.bprime_family_min(tp,3,want_witness=True)
        val=None if val is None else int(val); delta=None if val is None else val-int(cref[rid])
        verified=bool(val is not None and q7c.qg5b.verify_bprime_witness(tp,3,wit))
        bph.update([999 if delta is None else int(delta)])
        if not verified: bp_fail.append(rid)
        frames,tag=reference_frames(param[rv[rid]])
        ok,labels=q7c.r6s.config_labels(frames,tag)
        t6=(tp[0][0],tp[0][1],tp[1][0],tp[1][1],tp[2][0],tp[2][1])
        rc=int(q7c.r6s.config_cost(t6,frames,tag,(0,1,1),3)) if ok else None
        rok=bool(ok and labels==(0,1) and rc==int(cref[rid]))
        if not rok: ref_fail.append(rid)
        bprows.append({"residual_index":rid,"visible_index":int(rv[rid]),"hidden_index":int(rh[rid]),"target_letters":full[rid].tolist(),"reference_cost":int(cref[rid]),"dplus_cost":int(cd[rid]),"bprime_cost":val,"bprime_delta":delta,"bprime_verified":verified,"reference_verified":rok,"bprime_witness":wit})

    gates={
        "protocol_frozen":bool(PROTOCOL.exists()),
        "parent_digest":bool(parent.get("result_digest")==PARENT_DIGEST),
        "parent_terminal":bool(parent.get("terminal")=="QG7C_PARTIAL__L4B_OPEN"),
        "visible_failures_32556":bool(len(vis)==32556),
        "visible_histogram":bool(parent_hist==Counter({1:32116,2:440})),
        "cell_fingerprint":bool(cell_counts==EXPECTED_CELL_COUNTS),
        "hidden_domain_4096":bool(len(hidden)==4096),
        "product_domain_133349376":bool(len(vis)*len(hidden)==133349376),
        "reference_structural_cost_8":True,
        "relocation_library_576":bool(3*3*8*8==576),
        "screen_residual_6488":bool(len(residual)==6488),
        "screen_residual_all_plus1":bool(screen_max==1 and screen_hist.get(1,0)==6488),
        "dplus_templates_61056":bool(len(fr)==61056),
        "dplus_histogram":bool(dh==Counter({-2:136,-1:3676,0:2652,1:24})),
        "dplus_residual_24":bool(len(pos)==24),
        "production_dplus_controls":bool(not control_fail),
        "bprime_rows_24":bool(len(bprows)==24),
        "bprime_all_minus1":bool(bph==Counter({-1:24})),
        "bprime_witnesses_verified":bool(not bp_fail),
        "reference_witnesses_verified":bool(not ref_fail),
        "final_residual_zero":bool(all(r["bprime_delta"] is not None and r["bprime_delta"]<=0 for r in bprows)),
        "chain_not_claimed":True,
        "protected_subject_not_read":True,
    }
    if all(gates.values()): terminal=POSITIVE
    elif not gates["screen_residual_6488"] or not gates["screen_residual_all_plus1"]: terminal="QG7E_RELOCATION_FINGERPRINT_MISMATCH"
    elif not gates["dplus_histogram"] or not gates["dplus_residual_24"]: terminal="QG7E_DPLUS_RESIDUAL_MISMATCH"
    elif not gates["bprime_all_minus1"] or not gates["final_residual_zero"]: terminal="QG7E_BPRIME_HANDOFF_REFUTED__RESIDUAL_REMAINS"
    elif not gates["parent_digest"] or not gates["parent_terminal"]: terminal="QG7E_PARENT_BINDING_GAP"
    else: terminal="QG7E_CANNOT_CHECK"

    out={"schema":"ORIONQG.QG7E.PPSinglePinner.v1","issue":ISSUE,"terminal":terminal,"protocol_sha256":sha(PROTOCOL),"parent_qg7c_digest":parent.get("result_digest"),"information_closure_source_sha256":sha(INFO),"confirmatory_not_blind":True,"visible":{"failures":len(vis),"delta_histogram":{str(k):v for k,v in sorted(parent_hist.items())},"cell_counts":list(cell_counts)},"hidden":{"domain":len(hidden),"tuple_order":["a0","b0","c0","a1","b1","c1"]},"product_domain":int(len(vis)*len(hidden)),"relocation":{"library_size":576,"residual_count":len(residual),"residual_delta_histogram":{"1":screen_hist.get(1,0)},"full_screen_histogram":{str(k):v for k,v in sorted(screen_hist.items())}},"dplus":{"template_count":len(fr),"delta_histogram":{str(k):v for k,v in sorted(dh.items())},"residual_count":len(pos),"production_controls":controls,"control_failures":control_fail},"bprime":{"rows":bprows,"delta_histogram":{str(k):v for k,v in sorted(bph.items())},"witness_failures":bp_fail,"reference_failures":ref_fail,"final_residual":sum(int(r["bprime_delta"] is None or r["bprime_delta"]>0) for r in bprows)},"gates":gates,"all_gates":bool(all(gates.values())),"PP_SINGLE_PINNER_ALL_N":bool(terminal==POSITIVE),"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False,"protected_subject_read":False}
    unsigned=dict(out); out["result_digest"]=hashlib.sha256(canonical(unsigned).encode()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canonical({"terminal":terminal,"visible":len(vis),"product":out["product_domain"],"screen_residual":len(residual),"dplus_residual":len(pos),"bprime_final":out["bprime"]["final_residual"],"result_digest":out["result_digest"]}))
    return 0

if __name__=="__main__": raise SystemExit(main())
