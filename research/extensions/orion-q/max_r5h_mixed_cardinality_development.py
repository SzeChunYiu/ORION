#!/usr/bin/env python3
"""MAX-R5H donor-composed mixed-cardinality development on open H4 and N2.

Frozen by MAX_R5H_MIXED_CARDINALITY_DONOR_COMPOSED_PROTOCOL.md.
This is development-only: arbitrary anticommuting cliques are absorbed donor
capability. ORION receives value only from a mixed-alphabet Pareto point that
survives the donor-only direct-clique baseline.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

import max_r4d_h2o_ducc_confirmation as h

RZ_T = 48
TARE_T = 322
TARE_FIXED_CNOT = 33
WINDOW = 12
TARGET = 0b101
INF = 10**9

SUBJECTS = {
    "H4": {
        "commit": "be306f5830549304176365750d712093950bbdde",
        "blob": "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5",
        "path": "H4/cc-pVDZ/2.0au/DUCC3/H4.cc-pvdz_files/restricted/ducc/H4.cc-pvdz.ducc.results.txt",
        "n_occ": 2, "n_virt": 2, "n_orb": 4, "n_qubits": 8,
        "pair_reference": {"Lambda": 4.862865511405695, "CNOT": 4198, "T": 40224, "blocks": 134, "ancilla": 1},
    },
    "N2": {
        "commit": "be306f5830549304176365750d712093950bbdde",
        "blob": "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba",
        "path": "N2/cc-pVTZ/6Elec_6Orbs/1.0_Eq-2.0680au/DUCC2/N2.cc-pvtz.ducc.results.txt",
        "n_occ": 3, "n_virt": 3, "n_orb": 6, "n_qubits": 12,
        "pair_reference": {"Lambda": 11.221925428903152, "CNOT": 11177, "T": 94094, "blocks": 307, "ancilla": 1},
    },
}


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def wt(k): return (k[0] | k[1]).bit_count()
def symp(a,b): return ((a[0]&b[1]).bit_count() + (a[1]&b[0]).bit_count()) & 1


def reference_outer(blocks: int, block_t: int):
    if blocks <= 0:
        raise ValueError(blocks)
    q = 0 if blocks <= 1 else int(math.ceil(math.log2(blocks)))
    padded = 1 << q if q else 1
    prep_rot = 2 * (padded - 1)
    prep_t = prep_rot * RZ_T
    selector_t = 4 * max(0, blocks - 1)
    return {
        "outer_address_qubits": q,
        "padded_blocks": padded,
        "two_sided_dense_prepare_rotations": prep_rot,
        "reference_PREP_T": prep_t,
        "reference_selector_routing_T": selector_t,
        "reference_total_T": int(block_t + prep_t + selector_t),
    }


# Local exact controlled-TARE cost table, independent of subject qubit count.
LOCAL = {}
for p0 in range(4):
    for p1 in range(4):
        for base in (0,1):
            for d in range(8):
                best = INF
                for r0 in range(4):
                    for r1 in range(4):
                        for s in range(4):
                            dd = h.local_symp(r0,r1) | (h.local_symp(s,r0)<<1) | (h.local_symp(s,r1)<<2)
                            if dd != d: continue
                            t0=h.local_mul(p0,r0);t1=h.local_mul(p1,r1);tx=h.local_mul(t0,t1)
                            tb=t0 if base==0 else t1
                            c=4*h.local_wt(r0)+2*h.local_wt(r1)+2*h.local_wt(s)+h.local_wt(tx)+h.local_wt(tb)
                            best=min(best,c)
                LOCAL[(p0,p1,base,d)] = best


def local_codes(key, n):
    x,z=key
    for q in range(n): yield h.BITS_CODE[((x>>q)&1,(z>>q)&1)]


@lru_cache(maxsize=500000)
def tare_ctrl_cnot(k0, k1, n):
    best=INF
    for a,b in ((k0,k1),(k1,k0)):
        ca=tuple(local_codes(a,n));cb=tuple(local_codes(b,n))
        for base in (0,1):
            dp={0:0}
            for p0,p1 in zip(ca,cb):
                nxt={}
                for old,oc in dp.items():
                    for d in range(8):
                        nc=oc+LOCAL[(p0,p1,base,d)];key=old^d
                        if key not in nxt or nc<nxt[key]:nxt[key]=nc
                dp=nxt
            best=min(best,dp[TARGET]-6+TARE_FIXED_CNOT)
    return int(best)


@dataclass(frozen=True)
class Block:
    mask: int
    indices: tuple[int,...]
    kind: str
    lam: float
    cnot: int
    t: int
    ancilla: int


@dataclass(frozen=True)
class State:
    lam: float
    cnot: int
    t: int
    blocks: int
    ancilla: int
    partition: tuple[tuple[str,tuple[int,...]],...]

    def outer(self):
        return reference_outer(self.blocks,self.t)


def state_key(s: State):
    return (round(s.lam,15),s.cnot,s.t,s.blocks,s.ancilla,s.partition)


def dominates(a: State, b: State):
    oa,ob=a.outer(),b.outer()
    le=(a.lam<=b.lam+1e-13 and a.cnot<=b.cnot and a.t<=b.t and a.blocks<=b.blocks and a.ancilla<=b.ancilla and oa["reference_total_T"]<=ob["reference_total_T"])
    strict=(a.lam<b.lam-1e-13 or a.cnot<b.cnot or a.t<b.t or a.blocks<b.blocks or a.ancilla<b.ancilla or oa["reference_total_T"]<ob["reference_total_T"])
    return le and strict


def prune(states: Iterable[State]):
    # First collapse exact discrete coordinates to minimum lambda / deterministic partition.
    d={}
    for s in states:
        k=(s.cnot,s.t,s.blocks,s.ancilla)
        old=d.get(k)
        if old is None or (s.lam,s.partition)<(old.lam,old.partition):d[k]=s
    rows=sorted(d.values(),key=state_key)
    keep=[]
    for i,s in enumerate(rows):
        if any(i!=j and dominates(o,s) for j,o in enumerate(rows)):continue
        keep.append(s)
    return tuple(sorted(keep,key=state_key))


def configure_subject(cfg):
    h.SOURCE_COMMIT=cfg["commit"];h.SOURCE_BLOB=cfg["blob"];h.SOURCE_PATH=cfg["path"]
    h.SOURCE_URL="https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/"+cfg["commit"]+"/"+cfg["path"]
    h.N_OCC=cfg["n_occ"];h.N_VIRT=cfg["n_virt"];h.N_ORB=cfg["n_orb"];h.N_QUBITS=cfg["n_qubits"]


def direct_block(indices, terms, offset=0):
    m=len(indices)
    coeff=[abs(terms[i][1]) for i in indices]
    weights=[wt(terms[i][0]) for i in indices]
    lam=math.sqrt(sum(x*x for x in coeff))
    # 2m-1 donor circuit: all but central axis twice, max-weight axis central once.
    central=max(range(m),key=lambda j:(weights[j],-indices[j]))
    parity=4*sum(w-1 for w in weights)-2*(weights[central]-1)
    cnot=parity+2*(2*m-1)
    t=2*(2*m-1)*RZ_T
    global_idx=tuple(offset+i for i in indices)
    return Block(sum(1<<i for i in indices),global_idx,f"DIRECT_CLIQUE_{m}",float(lam),int(cnot),int(t),0)


def singleton_block(i,terms,offset=0):
    k,a=terms[i]
    return Block(1<<i,(offset+i,),"PAULI_SINGLETON",float(abs(a)),int(wt(k)),0,0)


def pair_block(i,j,terms,n,offset=0):
    k0,a0=terms[i];k1,a1=terms[j]
    if symp(k0,k1):
        return direct_block((i,j),terms,offset)
    lam=math.sqrt(2.0)*math.hypot(abs(a0),abs(a1))
    return Block((1<<i)|(1<<j),(offset+i,offset+j),"TARE_M2",float(lam),tare_ctrl_cnot(k0,k1,n),TARE_T,1)


def admissible_direct(indices,terms):
    for x in range(len(indices)):
        for y in range(x+1,len(indices)):
            if not symp(terms[indices[x]][0],terms[indices[y]][0]):return False
    return True


def candidate_blocks(terms,n,offset,alphabet):
    w=len(terms);out=[]
    for i in range(w):out.append(singleton_block(i,terms,offset))
    # All pairs: donor-only permits direct anti pairs, mixed permits TARE fallback.
    for i in range(w):
        for j in range(i+1,w):
            if symp(terms[i][0],terms[j][0]):out.append(direct_block((i,j),terms,offset))
            elif alphabet=="mixed":out.append(pair_block(i,j,terms,n,offset))
    # Every larger anticommuting subset is a donor-direct candidate.
    for mask in range(1,1<<w):
        if mask.bit_count()<3:continue
        idx=tuple(i for i in range(w) if (mask>>i)&1)
        if admissible_direct(idx,terms):out.append(direct_block(idx,terms,offset))
    # deterministic unique resource/circuit candidates per mask/kind
    uniq={}
    for b in out:
        key=(b.mask,b.kind)
        old=uniq.get(key)
        if old is None or (b.lam,b.cnot,b.t,b.indices)<(old.lam,old.cnot,old.t,old.indices):uniq[key]=b
    return tuple(sorted(uniq.values(),key=lambda b:(b.mask,b.kind,b.indices)))


def exact_window_frontier(terms,n,offset,alphabet):
    w=len(terms);full=(1<<w)-1
    blocks=candidate_blocks(terms,n,offset,alphabet)
    by_first={i:[] for i in range(w)}
    for b in blocks:
        for i in range(w):
            if (b.mask>>i)&1:by_first[i].append(b)
    calls=0
    @lru_cache(maxsize=None)
    def solve(mask):
        nonlocal calls
        calls+=1
        if mask==0:return (State(0.0,0,0,0,0,tuple()),)
        first=(mask & -mask).bit_length()-1
        cand=[]
        for b in by_first[first]:
            if b.mask & mask != b.mask:continue
            for tail in solve(mask^b.mask):
                part=((b.kind,b.indices),)+tail.partition
                cand.append(State(b.lam+tail.lam,b.cnot+tail.cnot,b.t+tail.t,1+tail.blocks,max(b.ancilla,tail.ancilla),part))
        return prune(cand)
    front=solve(full)
    return front,{"candidate_blocks":len(blocks),"subset_states_solved":calls,"frontier":len(front)}


def combine_frontiers(a,b):
    cand=[]
    for x in a:
        for y in b:
            cand.append(State(x.lam+y.lam,x.cnot+y.cnot,x.t+y.t,x.blocks+y.blocks,max(x.ancilla,y.ancilla),x.partition+y.partition))
    return prune(cand)


def global_frontier(terms,n,alphabet):
    front=(State(0.0,0,0,0,0,tuple()),);meta=[]
    for start in range(0,len(terms),WINDOW):
        sub=terms[start:min(start+WINDOW,len(terms))]
        lf,m=exact_window_frontier(sub,n,start,alphabet);meta.append({"start":start,"size":len(sub),**m})
        front=combine_frontiers(front,lf)
        meta[-1]["global_frontier_after"]=len(front)
        if len(front)>200000:raise RuntimeError({"pareto_saturation":len(front),"alphabet":alphabet,"window":start})
    return front,meta


def pauli_lcu(terms):
    lam=sum(abs(a) for _k,a in terms);c=sum(wt(k) for k,_a in terms);b=len(terms)
    return State(float(lam),int(c),0,b,0,tuple(("PAULI_SINGLETON",(i,)) for i in range(b)))


def serialize(s: State):
    o=s.outer();hist={}
    for kind,idx in s.partition:
        hist[kind]=hist.get(kind,0)+1
    return {"Lambda":s.lam,"CNOT":s.cnot,"block_internal_T":s.t,"blocks":s.blocks,"ancilla":s.ancilla,"reference_outer":o,"histogram":hist,"partition_sha256":sha([[k,list(i)] for k,i in s.partition])}


def pair_reference_state(cfg):
    r=cfg["pair_reference"]
    # No partition payload is needed; this is a frozen independently replayed reference point.
    s=State(r["Lambda"],r["CNOT"],r["T"],r["blocks"],r["ancilla"],tuple())
    return s


def pick_named(front,pair_ref):
    # Full frontier is exact. Deterministic named selections only filter/lexicographically choose.
    p_lambda=min(front,key=lambda s:(s.lam,s.cnot,s.outer()["reference_total_T"],s.blocks,s.partition))
    ft=[s for s in front if s.lam<=pair_ref.lam+1e-12 and s.cnot<=pair_ref.cnot]
    p_ft=min(ft,key=lambda s:(s.outer()["reference_total_T"],s.lam,s.cnot,s.blocks,s.partition)) if ft else None
    cr=[s for s in front if s.lam<=pair_ref.lam+1e-12 and s.outer()["reference_total_T"]<=pair_ref.outer()["reference_total_T"] and s.ancilla<=pair_ref.ancilla]
    p_cnot=min(cr,key=lambda s:(s.cnot,s.lam,s.outer()["reference_total_T"],s.blocks,s.partition)) if cr else None
    bal=[]
    for s in front:
        if not (s.lam<=pair_ref.lam+1e-12 and s.cnot<=pair_ref.cnot and s.t<=pair_ref.t and s.outer()["reference_total_T"]<=pair_ref.outer()["reference_total_T"] and s.ancilla<=pair_ref.ancilla):continue
        improvements=[]
        for new,old in ((s.lam,pair_ref.lam),(s.cnot,pair_ref.cnot),(s.t,pair_ref.t),(s.outer()["reference_total_T"],pair_ref.outer()["reference_total_T"])):
            if old>0:improvements.append(1-new/old)
        if max(improvements,default=0)>=0.01:bal.append(s)
    p_bal=min(bal,key=lambda s:(s.cnot,s.outer()["reference_total_T"],s.lam,s.blocks,s.partition)) if bal else None
    return {"P_LAMBDA":p_lambda,"P_FT":p_ft,"P_CNOT":p_cnot,"P_BALANCED":p_bal}


def uses_tare(s):
    return s is not None and any(k=="TARE_M2" for k,_ in s.partition)


def same_resource(a,b):
    if a is None or b is None:return False
    return abs(a.lam-b.lam)<=1e-12 and a.cnot==b.cnot and a.t==b.t and a.blocks==b.blocks and a.ancilla==b.ancilla


def run_subject(name,cfg):
    configure_subject(cfg)
    text=h.fetch_source();one,two=h.parse_ducc(text);paulis,max_imag=h.jordan_wigner_paulis(one,two);paulis.pop((0,0),None)
    terms=sorted(paulis.items(),key=lambda kv:(-abs(kv[1]),kv[0][0],kv[0][1]))
    b0=pauli_lcu(terms);b1=pair_reference_state(cfg)
    donor_front,donor_meta=global_frontier(terms,cfg["n_qubits"],"donor")
    mixed_front,mixed_meta=global_frontier(terms,cfg["n_qubits"],"mixed")
    b2=pick_named(donor_front,b1);b3=pick_named(mixed_front,b1)
    bal=b3["P_BALANCED"];donor_bal=b2["P_BALANCED"]
    # Donor absorption gate: ORION point must use TARE and not collapse to the donor-only resource vector.
    mixed_value=bal is not None and uses_tare(bal) and not any(same_resource(bal,d) for d in donor_front)
    result={
        "subject":name,"source_blob":cfg["blob"],"n_qubits":cfg["n_qubits"],"terms":len(terms),"max_imag":max_imag,
        "B0_Pauli_LCU":serialize(b0),"B1_R5G_pair_reference":serialize(b1),
        "donor_direct_frontier_size":len(donor_front),"mixed_frontier_size":len(mixed_front),
        "donor_window_meta":donor_meta,"mixed_window_meta":mixed_meta,
        "B2_donor_named":{k:(None if v is None else serialize(v)) for k,v in b2.items()},
        "B3_mixed_named":{k:(None if v is None else serialize(v)) for k,v in b3.items()},
        "mixed_balanced_uses_TARE":uses_tare(bal),"mixed_balanced_distinct_from_all_donor_resources":bool(mixed_value),
        "r5h_subject_development_pass":bool(mixed_value),
    }
    return result


def main():
    results={name:run_subject(name,cfg) for name,cfg in SUBJECTS.items()}
    out={"schema":"ORIONQ.MAXR5H.MixedCardinalityDevelopment.v1","authority":"DEVELOPMENT_ONLY__DONOR_ABSORPTION",
         "subjects":results,"r5h_development_pass":all(r["r5h_subject_development_pass"] for r in results.values()),
         "interpretation":"positive_only_if_mixed_TARE_plus_direct_clique_point_survives_donor_only_direct_frontier_on_both_open_subjects"}
    print("ORIONQ_MAX_R5H_DEV="+json.dumps(out,sort_keys=True));return out

if __name__=="__main__":main()
