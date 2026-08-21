#!/usr/bin/env python3
"""MAX-R4D fresh H2O DUCC confirmation.

This script intentionally has no OpenFermion/Qiskit dependency. It reproduces the
public DUCC extractor's active-space tensor semantics, applies a fixed
Jordan-Wigner transform, and evaluates the frozen split-TARE pair compiler.

Scientific scope: confirmation harness for #698/#679. It does not self-authorize
novelty or R6.
"""
from __future__ import annotations

import hashlib
import json
import math
import urllib.request
from collections import defaultdict
from functools import lru_cache

import numpy as np

SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
SOURCE_BLOB = "5f157e7bd05aac26b30b10dcea44b7650b7f8648"
SOURCE_PATH = "H2O/Eq/H2O.cc-pvtz_files/restricted/ducc/H2O.cc-pvtz.ducc.results.txt"
SOURCE_URL = (
    "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/"
    f"{SOURCE_COMMIT}/{SOURCE_PATH}"
)
N_OCC = 5
N_VIRT = 5
N_ORB = 10
N_QUBITS = 20
PRINT_THRESH = 5e-11
PAULI_THRESH = 1e-9


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def fetch_source() -> str:
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        raw = r.read()
    got = git_blob_sha(raw)
    if got != SOURCE_BLOB:
        raise RuntimeError(f"external source blob mismatch: {got} != {SOURCE_BLOB}")
    return raw.decode("utf-8")


def parse_ducc(text: str):
    """Faithful sparse port of repository grab_data._extract_integral_data."""
    one = np.zeros((N_ORB, N_ORB), dtype=float)
    two: dict[tuple[int, int, int, int], float] = {}
    mode = ""
    for raw in text.splitlines():
        ln = raw.strip()
        seg = ln.split()
        if not ln or ln.startswith("#"):
            continue
        if mode == "":
            if seg[:3] == ["Begin", "IJ", "Block"]:
                mode = "IJ"
            elif seg[:3] == ["Begin", "IA", "Block"]:
                mode = "IA"
            elif seg[:3] == ["Begin", "AB", "Block"]:
                mode = "AB"
            elif seg[:3] == ["Begin", "IJKL", "Block"]:
                mode = "IJKL"
            elif seg[:3] == ["Begin", "ABCD", "Block"]:
                mode = "ABCD"
            elif seg[:3] == ["Begin", "IJAB", "Block"]:
                mode = "IJAB"
            elif seg[:3] == ["Begin", "AIJB", "Block"]:
                mode = "AIJB"
            elif seg[:3] == ["Begin", "IJKA", "Block"]:
                mode = "IJKA"
            elif seg[:3] == ["Begin", "IABC", "Block"]:
                mode = "IABC"
            continue
        if seg[0] == "End":
            mode = ""
            continue
        if seg[0] == "Begin":
            continue
        if mode == "IJ":
            i, j, v = int(seg[0]) - 1, int(seg[1]) - 1, float(seg[2])
            one[i, j] = one[j, i] = v
        elif mode == "IA":
            i = int(seg[0]) - 1
            a = int(seg[1]) - 1 + N_OCC
            v = float(seg[2])
            one[i, a] = one[a, i] = v
        elif mode == "AB":
            a = int(seg[0]) - 1 + N_OCC
            b = int(seg[1]) - 1 + N_OCC
            v = float(seg[2])
            one[a, b] = one[b, a] = v
        elif mode == "IJKL":
            i = int(seg[0]) - 1
            j = int(seg[1]) - 1 - N_OCC
            k = int(seg[2]) - 1
            l = int(seg[3]) - 1 - N_OCC
            two[i, k, j, l] = float(seg[4])
        elif mode == "ABCD":
            a = int(seg[0]) - 1 + N_OCC
            b = int(seg[1]) - 1 - N_VIRT + N_OCC
            c = int(seg[2]) - 1 + N_OCC
            d = int(seg[3]) - 1 - N_VIRT + N_OCC
            two[a, c, b, d] = float(seg[4])
        elif mode == "IJAB":
            i = int(seg[0]) - 1
            j = int(seg[1]) - 1 - N_OCC
            a = int(seg[2]) - 1 + N_OCC
            b = int(seg[3]) - 1 - N_VIRT + N_OCC
            v = float(seg[4])
            two[i, a, j, b] = v
            two[a, i, b, j] = v
        elif mode == "AIJB":
            if int(seg[2]) > N_OCC:
                a = int(seg[0]) - 1 + N_OCC
                i = int(seg[1]) - 1 - N_OCC
                j = int(seg[2]) - 1 - N_OCC
                b = int(seg[3]) - 1 + N_OCC
                v = -float(seg[4])
                two[a, b, i, j] = v
                two[i, j, a, b] = v
            else:
                a = int(seg[0]) - 1 + N_OCC
                i = int(seg[1]) - 1 - N_OCC
                j = int(seg[2]) - 1
                b = int(seg[3]) - 1 - N_VIRT + N_OCC
                v = float(seg[4])
                two[a, j, i, b] = v
                two[j, a, b, i] = v
        elif mode == "IJKA":
            i = int(seg[0]) - 1
            j = int(seg[1]) - 1 - N_OCC
            k = int(seg[2]) - 1
            a = int(seg[3]) - 1 - N_VIRT + N_OCC
            v = float(seg[4])
            two[i, k, j, a] = v
            two[j, a, i, k] = v
            two[k, i, a, j] = v
            two[a, j, k, i] = v
        elif mode == "IABC":
            i = int(seg[0]) - 1
            a = int(seg[1]) - 1 - N_VIRT + N_OCC
            b = int(seg[2]) - 1 + N_OCC
            c = int(seg[3]) - 1 - N_VIRT + N_OCC
            v = float(seg[4])
            two[i, b, a, c] = v
            two[b, i, c, a] = v
            two[a, c, i, b] = v
            two[c, a, b, i] = v
    if mode:
        raise RuntimeError(f"unterminated DUCC block {mode}")
    return one, two


# Conventional Pauli word P(x,z) = i^(x.z) X^x Z^z, encoded as two bit masks.
def pmul(a: tuple[int, int], b: tuple[int, int]):
    x, z = a
    xp, zp = b
    xo, zo = x ^ xp, z ^ zp
    exponent = (
        (x & z).bit_count()
        + (xp & zp).bit_count()
        - (xo & zo).bit_count()
        + 2 * (z & xp).bit_count()
    ) % 4
    return (xo, zo), (1, 1j, -1, -1j)[exponent]


def jw_ladder(j: int, dagger: bool):
    prefix = (1 << j) - 1
    x = 1 << j
    return [
        ((x, prefix), 0.5 + 0j),
        ((x, prefix | x), (-0.5j if dagger else 0.5j)),
    ]


@lru_cache(maxsize=None)
def jw_monomial(ops: tuple[tuple[int, bool], ...]):
    poly = { (0, 0): 1.0 + 0j }
    for j, dagger in ops:
        nxt: dict[tuple[int, int], complex] = defaultdict(complex)
        for pk, pc in poly.items():
            for qk, qc in jw_ladder(j, dagger):
                rk, phase = pmul(pk, qk)
                nxt[rk] += pc * qc * phase
        poly = dict(nxt)
    return tuple(poly.items())


def add_monomial(acc, coeff: float, ops):
    if abs(coeff) <= PRINT_THRESH:
        return
    for key, c in jw_monomial(tuple(ops)):
        acc[key] += coeff * c


def jordan_wigner_paulis(one, two):
    """Port the repository XACC writer then transform every fermion monomial."""
    acc: dict[tuple[int, int], complex] = defaultdict(complex)
    # same-spin antisymmetrized pieces
    for w in range(N_ORB):
        for x in range(N_ORB):
            for y in range(N_ORB):
                for z in range(N_ORB):
                    g = two.get((w, x, y, z), 0.0)
                    gx = two.get((w, z, y, x), 0.0)
                    v = 0.25 * (g - gx)
                    if abs(v) > PRINT_THRESH:
                        add_monomial(acc, v, ((w, True), (y, True), (z, False), (x, False)))
                        add_monomial(acc, v, ((w+N_ORB, True), (y+N_ORB, True),
                                              (z+N_ORB, False), (x+N_ORB, False)))
    # opposite-spin pieces, exactly as XACC writer
    for w in range(N_ORB):
        for x in range(N_ORB):
            for y in range(N_ORB):
                for z in range(N_ORB):
                    g = two.get((w, x, y, z), 0.0)
                    if abs(g) <= PRINT_THRESH:
                        continue
                    v = 0.25 * g
                    a, b = w, x
                    c, d = y + N_ORB, z + N_ORB
                    add_monomial(acc, v, ((a, True),(c, True),(d, False),(b, False)))
                    add_monomial(acc, v, ((c, True),(a, True),(b, False),(d, False)))
                    add_monomial(acc, -v, ((c, True),(a, True),(d, False),(b, False)))
                    add_monomial(acc, -v, ((a, True),(c, True),(b, False),(d, False)))
    # one-body alpha/beta
    for w in range(N_ORB):
        for x in range(N_ORB):
            v = float(one[w, x])
            if abs(v) > PRINT_THRESH:
                add_monomial(acc, v, ((w, True),(x, False)))
                add_monomial(acc, v, ((w+N_ORB, True),(x+N_ORB, False)))
    # Clean numerical cancellation.
    out = {}
    max_imag = 0.0
    for key, c in acc.items():
        max_imag = max(max_imag, abs(c.imag))
        if abs(c) > PAULI_THRESH:
            if abs(c.imag) > 5e-8:
                raise RuntimeError(f"non-Hermitian JW coefficient {key}: {c}")
            out[key] = float(c.real)
    return out, max_imag


# Local Pauli code: I=0, X=1, Y=2, Z=3. Table via symplectic bits.
CODE_BITS = ((0,0),(1,0),(1,1),(0,1))
BITS_CODE = {b:i for i,b in enumerate(CODE_BITS)}

def local_mul(a: int, b: int) -> int:
    xa,za = CODE_BITS[a]; xb,zb = CODE_BITS[b]
    return BITS_CODE[(xa^xb, za^zb)]

def local_symp(a: int, b: int) -> int:
    xa,za = CODE_BITS[a]; xb,zb = CODE_BITS[b]
    return (xa*zb ^ za*xb) & 1

def local_wt(a: int) -> int:
    return int(a != 0)

# For each target local pair and local parity delta, exact minimum local Tag/Restore factor.
LOCAL_C = np.full((4,4,8), 99, dtype=np.int16)
LOCAL_E = np.full((4,4,8), 99, dtype=np.int16)
for p0 in range(4):
    for p1 in range(4):
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    d0 = local_symp(r0,r1)
                    d1 = local_symp(s,r0)
                    d2 = local_symp(s,r1)
                    d = d0 | (d1<<1) | (d2<<2)
                    c = local_wt(s) + local_wt(local_mul(p0,r0)) + local_wt(local_mul(p1,r1))
                    # Additive support model for the three m=2 Uanti axes R0, R1, R0R1.
                    e = local_wt(r0) + local_wt(r1) + local_wt(local_mul(r0,r1))
                    if c < LOCAL_C[p0,p1,d]: LOCAL_C[p0,p1,d] = c
                    if e < LOCAL_E[p0,p1,d]: LOCAL_E[p0,p1,d] = e

XOR = np.bitwise_xor(np.arange(8)[:,None], np.arange(8)[None,:])


def local_codes(key: tuple[int,int]):
    x,z = key
    for q in range(N_QUBITS):
        yield BITS_CODE[((x>>q)&1, (z>>q)&1)]


def anticommutes(a, b) -> bool:
    x,z = a; xp,zp = b
    return (((x & zp).bit_count() + (z & xp).bit_count()) & 1) == 1


@lru_cache(maxsize=200000)
def corrected_pair_cost(a: tuple[int,int], b: tuple[int,int]):
    """Exact m=2 TARE local objective via 8-state symplectic parity DP."""
    if anticommutes(a,b):
        return 0, 0, True
    ca = tuple(local_codes(a)); cb = tuple(local_codes(b))
    dp_c = np.full(8, 10**6, dtype=np.int32); dp_c[0] = 0
    dp_e = np.full(8, 10**6, dtype=np.int32); dp_e[0] = 0
    for p0,p1 in zip(ca,cb):
        lc = LOCAL_C[p0,p1]
        le = LOCAL_E[p0,p1]
        dp_c = np.min(dp_c[:,None] + lc[XOR], axis=0)
        dp_e = np.min(dp_e[:,None] + le[XOR], axis=0)
    # target parities: <R0,R1>=1, <S,R0>=0, <S,R1>=1 -> 0b101
    return int(dp_c[5]), int(dp_e[5]), False


def pair_lambda(a: float, b: float) -> float:
    return math.sqrt(2.0) * math.hypot(abs(a), abs(b))


def pair_metrics(t0, t1):
    (k0,a0),(k1,a1) = t0,t1
    c,e,direct = corrected_pair_cost(k0,k1)
    return {"lambda":pair_lambda(a0,a1), "C":c, "E_support":e, "direct":direct}


def matching_metrics(terms, pairs, singleton=None):
    lam=C=E=direct=0.0
    for i,j in pairs:
        m=pair_metrics(terms[i],terms[j])
        lam += m["lambda"]; C += m["C"]; E += m["E_support"]; direct += int(m["direct"])
    if singleton is not None:
        lam += abs(terms[singleton][1])
    return {"Lambda":float(lam),"C":int(C),"E_support":int(E),"direct_pairs":int(direct)}


def compile_quartets(terms):
    # Terms arrive magnitude-descending and even in count after optional singleton removal.
    n=len(terms)
    base_pairs=[]
    for i in range(0,n,2): base_pairs.append((i,i+1))
    base=matching_metrics(terms,base_pairs)

    quartet_options=[]
    for s in range(0,n,4):
        idx=list(range(s,min(s+4,n)))
        if len(idx)<4:
            # deterministic tail: adjacent only
            quartet_options.append([([(idx[0],idx[1])], matching_metrics(terms,[(idx[0],idx[1])]))])
            continue
        patterns=[((0,1),(2,3)),((0,2),(1,3)),((0,3),(1,2))]
        opts=[]
        for pat in patterns:
            ps=[(idx[a],idx[b]) for a,b in pat]
            opts.append((ps,matching_metrics(terms,ps)))
        quartet_options.append(opts)

    def greedy(frac):
        # Start coefficient-optimal option 0 in every quartet. Each quartet may switch once
        # to its best C-reducing alternative. Rank by C benefit per Lambda penalty.
        selected=[0]*len(quartet_options)
        lam=base["Lambda"]; C=base["C"]
        budget=base["Lambda"]*frac
        moves=[]
        for qi,opts in enumerate(quartet_options):
            b=opts[0][1]
            for oi in range(1,len(opts)):
                m=opts[oi][1]
                dl=m["Lambda"]-b["Lambda"]
                dc=b["C"]-m["C"]
                if dc>0 and dl>=-1e-12:
                    score=(float("inf") if dl<=1e-15 else dc/dl)
                    moves.append((score,dc,dl,qi,oi))
        moves.sort(reverse=True)
        used=0.0
        for score,dc,dl,qi,oi in moves:
            if selected[qi]!=0: continue
            if used+dl <= budget+1e-12:
                selected[qi]=oi; used+=max(0.0,dl)
        pairs=[]
        for qi,oi in enumerate(selected): pairs.extend(quartet_options[qi][oi][0])
        return matching_metrics(terms,pairs)

    return base, greedy(0.01), greedy(0.05)


def main():
    text=fetch_source()
    one,two=parse_ducc(text)
    paulis,max_imag=jordan_wigner_paulis(one,two)
    identity=(0,0)
    identity_coeff=paulis.pop(identity,0.0)
    terms=sorted(paulis.items(), key=lambda kv: abs(kv[1]), reverse=True)
    singleton=None
    singleton_term=None
    if len(terms)%2:
        singleton=len(terms)-1
        singleton_term={"coefficient":terms[-1][1],"abs":abs(terms[-1][1])}
        paired_terms=terms[:-1]
    else:
        paired_terms=terms
    base,g1,g5=compile_quartets(paired_terms)
    if singleton_term is not None:
        for m in (base,g1,g5): m["Lambda"] += singleton_term["abs"]
    def reduction(m,key):
        return 0.0 if base[key]==0 else (base[key]-m[key])/base[key]
    g1_over=(g1["Lambda"]/base["Lambda"]-1.0)
    g5_over=(g5["Lambda"]/base["Lambda"]-1.0)
    gate1=(g1_over<=0.0100000001 and (reduction(g1,"C")>=0.05 or reduction(g1,"E_support")>=0.05))
    gate5=(g5_over<=0.0500000001 and (g5["C"]<base["C"] or g5["E_support"]<base["E_support"]))
    result={
        "schema":"ORIONQ.MAXR4D.H2ODUCCConfirmation.v1",
        "source":{"repo":"npbauman/DUCC-Hamiltonian-Library","commit":SOURCE_COMMIT,"blob":SOURCE_BLOB,"path":SOURCE_PATH},
        "mapping":"repository_extractor_semantics_then_Jordan_Wigner_no_tapering",
        "n_spatial_orbitals":N_ORB,
        "n_qubits":N_QUBITS,
        "two_body_sparse_entries":len(two),
        "pauli_terms_including_identity":len(paulis)+1,
        "nonidentity_pauli_terms":len(terms),
        "identity_coefficient_without_nuclear_shift":identity_coeff,
        "max_pauli_imaginary_residual":max_imag,
        "odd_singleton":singleton_term,
        "coefficient_optimum":base,
        "greedy_1pct":g1,
        "greedy_5pct":g5,
        "greedy_1pct_normalization_overhead":g1_over,
        "greedy_5pct_normalization_overhead":g5_over,
        "greedy_1pct_C_reduction":reduction(g1,"C"),
        "greedy_1pct_E_reduction":reduction(g1,"E_support"),
        "greedy_5pct_C_reduction":reduction(g5,"C"),
        "greedy_5pct_E_reduction":reduction(g5,"E_support"),
        "gate_1pct_5pct_resource_reduction":bool(gate1),
        "gate_5pct_strict_pareto":bool(gate5),
        "r4d_protocol_pass":bool(gate1 and gate5),
        "authority":"fresh_public_hamiltonian_confirmation_only__not_novelty_authority",
    }
    print("ORIONQ_MAX_R4D_RESULT="+json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    main()
