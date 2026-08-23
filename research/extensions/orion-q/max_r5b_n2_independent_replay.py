#!/usr/bin/env python3
"""Independent MAX-R5B N2 replay.

This implementation intentionally does not import either R5 N2 compiler or R5B
proof-replay code. It reuses only the already-verified R4D DUCC->JW semantic
layer, then independently rebuilds block classification, canonical witness DP,
bounded quartet incumbent, and frozen 1% successor.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache

import max_r4d_h2o_ducc_confirmation as h

h.SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
h.SOURCE_BLOB = "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba"
h.SOURCE_PATH = "N2/cc-pVTZ/6Elec_6Orbs/1.0_Eq-2.0680au/DUCC2/N2.cc-pvtz.ducc.results.txt"
h.SOURCE_URL = (
    "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/"
    f"{h.SOURCE_COMMIT}/{h.SOURCE_PATH}"
)
h.N_OCC = 3
h.N_VIRT = 3
h.N_ORB = 6
h.N_QUBITS = 12

N = 12
TARGET = 0b101
INF = 10**9
EXPECTED = {
    "sorted_terms": "56e3b79b43407f2dbe7360e98b1d74bfbd1ae4bee4cd52af47455746a2447443",
    "inc_pair_list": "5bc7120abe130d2cf9f570406a75cf7d73c9e8f90d72f95e5352985de804c7c4",
    "suc_pair_list": "211290d7dead4de5b94ae5990ead659b2223e532a7223f53bb7efcf4028fcc94",
    "inc_witness": "83f1952d25b6cb774ef62172b9dc015263f616acbc31e0909919c8b625fba01d",
    "suc_witness": "fcc4b665d89c9377fb818f6257685fc9dd20ea09e516370a63cd4281a613091c",
}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def weight(k):
    return (k[0] | k[1]).bit_count()


def mul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def symp(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1


def codes(k):
    x, z = k
    for q in range(N):
        yield h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)]


def pack(seq, slot):
    x = z = 0
    for q, triple in enumerate(seq):
        bx, bz = h.CODE_BITS[triple[slot]]
        x |= bx << q
        z |= bz << q
    return (x, z)


def local_delta(r0, r1, s):
    return h.local_symp(r0, r1) | (h.local_symp(s, r0) << 1) | (h.local_symp(s, r1) << 2)


def local_cost(p0, p1, r0, r1, s):
    return (
        4 * h.local_wt(r0) + 2 * h.local_wt(r1) + 2 * h.local_wt(s)
        + h.local_wt(h.local_mul(p0, r0)) + h.local_wt(h.local_mul(p1, r1))
    )


def orientation(k0, k1):
    # Structurally independent replay: enumerate every one of the 64 triples at
    # every qubit and let a dictionary DP choose the exact minimum/tie sequence.
    states = {0: (0, tuple())}
    for p0, p1 in zip(codes(k0), codes(k1)):
        nxt = {}
        for old_parity, (old_cost, old_seq) in states.items():
            for r0 in range(4):
                for r1 in range(4):
                    for s in range(4):
                        d = local_delta(r0, r1, s)
                        new_parity = old_parity ^ d
                        candidate = (old_cost + local_cost(p0, p1, r0, r1, s), old_seq + ((r0, r1, s),))
                        if new_parity not in nxt or candidate < nxt[new_parity]:
                            nxt[new_parity] = candidate
        states = nxt
    raw, seq = states[TARGET]
    return raw - 6, seq


@lru_cache(maxsize=400000)
def witness(k0, k1):
    if symp(k0, k1):
        choices = []
        for orient, (a, b) in enumerate(((k0, k1), (k1, k0))):
            g = 4 * (weight(a) - 1) + 2 * (weight(b) - 1)
            choices.append((g, orient, a, b))
        g, orient_id, a, b = min(choices, key=lambda x: (x[0], x[1]))
        return {"type": "DIRECT_ANTI_UNITARY", "orientation": orient_id, "ordered_targets": [list(a), list(b)], "G_internal_2q": int(g)}

    choices = []
    for orient_id, (a, b) in enumerate(((k0, k1), (k1, k0))):
        g, seq = orientation(a, b)
        choices.append((g, orient_id, seq, a, b))
    g, orient_id, seq, a, b = min(choices, key=lambda x: (x[0], x[1], x[2]))
    r0, r1, s = pack(seq, 0), pack(seq, 1), pack(seq, 2)
    t0, t1 = mul(a, r0), mul(b, r1)
    assert symp(r0, r1) == 1 and symp(s, r0) == 0 and symp(s, r1) == 1
    assert mul(t0, r0) == a and mul(t1, r1) == b
    recomputed = 4 * (weight(r0)-1) + 2 * (weight(r1)-1) + 2*weight(s) + weight(t0) + weight(t1)
    assert recomputed == g
    return {
        "type": "TARE_M2", "orientation": orient_id, "ordered_targets": [list(a), list(b)],
        "R0": list(r0), "R1": list(r1), "S": list(s), "T0": list(t0), "T1": list(t1),
        "G_internal_2q": int(g),
    }


def edge(terms, i, j):
    k0, a0 = terms[i]; k1, a1 = terms[j]
    w = witness(k0, k1)
    lam = math.hypot(abs(a0), abs(a1)) if w["type"] == "DIRECT_ANTI_UNITARY" else math.sqrt(2.0)*math.hypot(abs(a0), abs(a1))
    return lam, w["G_internal_2q"], w


def metrics(terms, pairs):
    lam = 0.0; g = 0; direct = 0
    for i, j in pairs:
        l, c, w = edge(terms, i, j)
        lam += l; g += c; direct += (w["type"] == "DIRECT_ANTI_UNITARY")
    return {"Lambda_joint": float(lam), "G_internal_2q": int(g), "direct": int(direct)}


def patterns(idx):
    if len(idx) == 2:
        return [[(idx[0], idx[1])]]
    return [
        [(idx[0], idx[1]), (idx[2], idx[3])],
        [(idx[0], idx[2]), (idx[1], idx[3])],
        [(idx[0], idx[3]), (idx[1], idx[2])],
    ]


def compile_frozen(terms, frac=0.01):
    qopts = []
    for s in range(0, len(terms), 4):
        opts = []
        for oi, ps in enumerate(patterns(list(range(s, min(s+4, len(terms)))))):
            opts.append((oi, ps, metrics(terms, ps)))
        opts.sort(key=lambda x: (x[2]["Lambda_joint"], x[2]["G_internal_2q"], x[0]))
        qopts.append(opts)
    base_choice = {qi: opts[0][0] for qi, opts in enumerate(qopts)}
    def assemble(choice):
        ps = []
        for qi, opts in enumerate(qopts):
            byid = {oi: p for oi, p, _ in opts}
            ps.extend(byid[choice[qi]])
        return ps
    base_pairs = assemble(base_choice)
    base = metrics(terms, base_pairs)
    moves = []
    for qi, opts in enumerate(qopts):
        bid = base_choice[qi]
        bm = next(m for oi, _p, m in opts if oi == bid)
        local = []
        for oi, _p, m in opts:
            if oi == bid:
                continue
            dl = m["Lambda_joint"] - bm["Lambda_joint"]
            dg = bm["G_internal_2q"] - m["G_internal_2q"]
            if dg > 0 and dl >= -1e-12:
                local.append((float("inf") if dl <= 1e-15 else dg/dl, dg, max(0.0, dl), oi))
        if local:
            local.sort(key=lambda x: (-x[0], -x[1], x[2], x[3]))
            score, dg, dl, oi = local[0]
            moves.append((score, dg, dl, qi, oi))
    moves.sort(key=lambda x: (-x[0], -x[1], x[2], x[3], x[4]))
    choice = dict(base_choice); used = 0.0; budget = frac*base["Lambda_joint"]
    for _score, _dg, dl, qi, oi in moves:
        if used + dl <= budget + 1e-12:
            choice[qi] = oi; used += dl
    return base_pairs, assemble(choice)


def proof_payload(terms, pairs):
    payload = []
    for i, j in pairs:
        k0, a0 = terms[i]; k1, a1 = terms[j]
        lam, _g, w0 = edge(terms, i, j)
        w = {
            "term_indices": [int(i), int(j)], "type": w0["type"], "orientation": w0["orientation"],
            "input_keys": [list(k0), list(k1)], "ordered_targets": w0["ordered_targets"],
            "coefficient_sign_bits": [int(a0 < 0), int(a1 < 0)], "lambda_pair": round(lam, 16),
            "G_internal_2q": w0["G_internal_2q"],
        }
        for key in ("R0", "R1", "S", "T0", "T1"):
            if key in w0: w[key] = w0[key]
        payload.append(w)
    return payload


def main():
    text = h.fetch_source(); one, two = h.parse_ducc(text); paulis, max_imag = h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms_all = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    assert len(terms_all) % 2 == 0
    term_hash = sha([[list(k), format(float(a), ".17g")] for k, a in terms_all])
    inc_pairs, suc_pairs = compile_frozen(terms_all, 0.01)
    inc = metrics(terms_all, inc_pairs); suc = metrics(terms_all, suc_pairs)
    got = {
        "sorted_terms": term_hash,
        "inc_pair_list": sha([[int(i), int(j)] for i, j in inc_pairs]),
        "suc_pair_list": sha([[int(i), int(j)] for i, j in suc_pairs]),
        "inc_witness": sha(proof_payload(terms_all, inc_pairs)),
        "suc_witness": sha(proof_payload(terms_all, suc_pairs)),
    }
    hash_match = {k: got[k] == EXPECTED[k] for k in EXPECTED}
    aggregate_match = {
        "inc_Lambda": abs(inc["Lambda_joint"] - 11.154919014188893) <= 1e-12,
        "inc_G": inc["G_internal_2q"] == 5467,
        "inc_direct": inc["direct"] == 104,
        "suc_Lambda": abs(suc["Lambda_joint"] - 11.264669617948641) <= 1e-12,
        "suc_G": suc["G_internal_2q"] == 3646,
        "suc_direct": suc["direct"] == 3,
    }
    if not all(hash_match.values()) or not all(aggregate_match.values()):
        raise AssertionError({"hash_match": hash_match, "aggregate_match": aggregate_match, "got": got, "inc": inc, "suc": suc})
    out = {
        "schema": "ORIONQ.MAXR5B.N2IndependentReplay.v1",
        "source_blob": h.SOURCE_BLOB,
        "max_pauli_imaginary_residual": max_imag,
        "hashes": got,
        "hash_match": hash_match,
        "aggregate_match": aggregate_match,
        "incumbent": inc,
        "successor": suc,
        "independent_replay_pass": True,
        "authority": "R5B_INDEPENDENT_REPLAY_GREEN__OUTER_NEGATIVE_UNCHANGED",
    }
    print("ORIONQ_MAX_R5B_INDEPENDENT=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
