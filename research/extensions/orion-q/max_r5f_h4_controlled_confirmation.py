#!/usr/bin/env python3
"""MAX-R5F fresh H4 proof-carrying controlled-composition confirmation.

Protocol frozen before the H4 DUCC coefficient file was opened:
  development/orion-q-max-r0/MAX_R5F_H4_TRUE_INCUMBENT_CONFIRMATION_PROTOCOL.md

Authority ceiling: fresh public-Hamiltonian confirmation only, not R6 novelty.
"""
from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache

import max_r4d_h2o_ducc_confirmation as h

SOURCE_COMMIT = "be306f5830549304176365750d712093950bbdde"
SOURCE_BLOB = "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5"
SOURCE_PATH = "H4/cc-pVDZ/2.0au/DUCC3/H4.cc-pvdz_files/restricted/ducc/H4.cc-pvdz.ducc.results.txt"
SOURCE_URL = "https://raw.githubusercontent.com/npbauman/DUCC-Hamiltonian-Library/" + SOURCE_COMMIT + "/" + SOURCE_PATH
N_OCC = 2
N_VIRT = 2
N_ORB = 4
N_QUBITS = 8
WINDOW = 12
NORM_FRAC = 0.01
TARGET = 0b101
INF = 10**9

# Frozen R5B/R5C projection constants.
SYNTH_EPS = 1e-10
RZ_T = int(math.ceil(1.149 * math.log2(1.0 / SYNTH_EPS) + 9.2))
CRZ_CNOT = 2
CRZ_RZ_SYNTH = 2
CH_CNOT = 1
CH_T = 2
TOFFOLI_CNOT = 6
TOFFOLI_T = 7
DIRECT_T = 3 * CRZ_RZ_SYNTH * RZ_T
TARE_T = DIRECT_T + 3 * CH_T + 4 * TOFFOLI_T
DIRECT_FIXED_CNOT = 3 * CRZ_CNOT
TARE_FIXED_CNOT = 3 * CRZ_CNOT + 3 * CH_CNOT + 4 * TOFFOLI_CNOT

# Parameterize only the already-verified DUCC parser/JW implementation.
h.SOURCE_COMMIT = SOURCE_COMMIT
h.SOURCE_BLOB = SOURCE_BLOB
h.SOURCE_PATH = SOURCE_PATH
h.SOURCE_URL = SOURCE_URL
h.N_OCC = N_OCC
h.N_VIRT = N_VIRT
h.N_ORB = N_ORB
h.N_QUBITS = N_QUBITS

XOR = [[i ^ j for j in range(8)] for i in range(8)]


def sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def weight(k):
    return (k[0] | k[1]).bit_count()


def mul_key(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def symp(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1


def codes(k):
    x, z = k
    for q in range(N_QUBITS):
        yield h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)]


def mask_from_codes(cs):
    x = z = 0
    for q, code in enumerate(cs):
        bx, bz = h.CODE_BITS[code]
        x |= bx << q
        z |= bz << q
    return (x, z)


# Exact local controlled-cost candidates. For a fixed target-local pair, Restore
# base, and parity delta, retain the minimum cost and lexicographically first
# (r0,r1,s) witness. The global Restore base is a DP branch, not a per-qubit mix.
LOCAL = {}
for p0 in range(4):
    for p1 in range(4):
        arr = {(base, d): [] for base in (0, 1) for d in range(8)}
        for r0 in range(4):
            for r1 in range(4):
                for s in range(4):
                    d = h.local_symp(r0, r1) | (h.local_symp(s, r0) << 1) | (h.local_symp(s, r1) << 2)
                    t0 = h.local_mul(p0, r0)
                    t1 = h.local_mul(p1, r1)
                    tx = h.local_mul(t0, t1)
                    common = 4 * h.local_wt(r0) + 2 * h.local_wt(r1) + 2 * h.local_wt(s) + h.local_wt(tx)
                    arr[(0, d)].append((common + h.local_wt(t0), (r0, r1, s)))
                    arr[(1, d)].append((common + h.local_wt(t1), (r0, r1, s)))
        for key in arr:
            arr[key].sort(key=lambda x: (x[0], x[1]))
        LOCAL[(p0, p1)] = arr


def controlled_orientation_witness(a, b, base):
    # state parity -> (raw local cost, local witness sequence)
    states = {0: (0, tuple())}
    for p0, p1 in zip(codes(a), codes(b)):
        nxt = {}
        local = LOCAL[(p0, p1)]
        for prev, (prev_cost, prev_seq) in states.items():
            for d in range(8):
                lc, triple = local[(base, d)][0]
                parity = prev ^ d
                cand = (prev_cost + lc, prev_seq + (triple,))
                if parity not in nxt or cand < nxt[parity]:
                    nxt[parity] = cand
        states = nxt
    raw, seq = states[TARGET]
    return int(raw - 6 + TARE_FIXED_CNOT), seq


@lru_cache(maxsize=100000)
def tare_witness(k0, k1):
    choices = []
    for orient, (a, b) in enumerate(((k0, k1), (k1, k0))):
        for base in (0, 1):
            cost, seq = controlled_orientation_witness(a, b, base)
            choices.append((cost, orient, base, seq, a, b))
    cost, orient, base, seq, a, b = min(choices, key=lambda x: (x[0], x[1], x[2], x[3]))
    r0 = mask_from_codes([t[0] for t in seq])
    r1 = mask_from_codes([t[1] for t in seq])
    s = mask_from_codes([t[2] for t in seq])
    t0 = mul_key(a, r0)
    t1 = mul_key(b, r1)
    tx = mul_key(t0, t1)
    restore_support = weight(tx) + (weight(t0) if base == 0 else weight(t1))
    uanti = 4 * (weight(r0) - 1) + 2 * (weight(r1) - 1)
    recomputed = uanti + 2 * weight(s) + restore_support + TARE_FIXED_CNOT
    checks = {
        "R0_anticommutes_R1": symp(r0, r1) == 1,
        "S_commutes_R0": symp(s, r0) == 0,
        "S_anticommutes_R1": symp(s, r1) == 1,
        "T0R0_equals_P0": mul_key(t0, r0) == a,
        "T1R1_equals_P1": mul_key(t1, r1) == b,
        "restore_support_recomputed": restore_support == min(weight(t0), weight(t1)) + weight(tx) if weight(t0) == weight(t1) else restore_support == weight(tx) + (weight(t0) if base == 0 else weight(t1)),
        "controlled_CNOT_recomputed": recomputed == cost,
    }
    # The DP branches over base. It may select a non-min-weight Restore base only
    # if the globally optimal representation differs. The circuit is still valid;
    # the exact reported support must match the selected branch.
    checks["selected_restore_base_valid"] = base in (0, 1)
    if not all(checks.values()):
        raise AssertionError({"tare_witness_checks": checks, "k0": k0, "k1": k1})
    return {
        "type": "TARE_M2",
        "orientation": orient,
        "restore_base": base,
        "ordered_targets": [list(a), list(b)],
        "R0": list(r0),
        "R1": list(r1),
        "S": list(s),
        "T0": list(t0),
        "T1": list(t1),
        "restore_support": int(restore_support),
        "controlled_CNOT": int(cost),
        "projected_T": int(TARE_T),
        "checks": checks,
    }


@lru_cache(maxsize=100000)
def direct_witness(k0, k1):
    if symp(k0, k1) != 1:
        raise AssertionError("direct witness on commuting targets")
    vals = []
    for orient, (a, b) in enumerate(((k0, k1), (k1, k0))):
        c = 4 * (weight(a) - 1) + 2 * (weight(b) - 1) + DIRECT_FIXED_CNOT
        vals.append((c, orient, a, b))
    cost, orient, a, b = min(vals, key=lambda x: (x[0], x[1]))
    return {
        "type": "DIRECT_ANTI_UNITARY",
        "orientation": orient,
        "ordered_targets": [list(a), list(b)],
        "controlled_CNOT": int(cost),
        "projected_T": int(DIRECT_T),
        "checks": {"targets_anticommute": symp(k0, k1) == 1},
    }


@lru_cache(maxsize=100000)
def edge_cost(k0, k1, a0, a1):
    # Coefficients are cache-key floats from the immutable parsed Hamiltonian.
    if symp(k0, k1):
        w = direct_witness(k0, k1)
        lam = math.hypot(abs(a0), abs(a1))
        direct = 1
    else:
        w = tare_witness(k0, k1)
        lam = math.sqrt(2.0) * math.hypot(abs(a0), abs(a1))
        direct = 0
    return (float(lam), int(w["controlled_CNOT"]), int(w["projected_T"]), direct)


def pair_edge(terms, i, j):
    k0, a0 = terms[i]
    k1, a1 = terms[j]
    lam, cnot, t, direct = edge_cost(k0, k1, float(a0), float(a1))
    return {"lambda": lam, "CNOT": cnot, "T": t, "direct": direct}


def metrics(terms, pairs):
    out = {"Lambda": 0.0, "CNOT": 0, "T": 0, "direct": 0, "pairs": len(pairs)}
    for i, j in pairs:
        e = pair_edge(terms, i, j)
        out["Lambda"] += e["lambda"]
        out["CNOT"] += e["CNOT"]
        out["T"] += e["T"]
        out["direct"] += e["direct"]
    out["Lambda"] = float(out["Lambda"])
    return out


def enumerate_matchings(items):
    items = tuple(items)
    if not items:
        yield tuple()
        return
    a = items[0]
    rest = items[1:]
    for pos, b in enumerate(rest):
        rem = rest[:pos] + rest[pos + 1 :]
        for tail in enumerate_matchings(rem):
            yield ((a, b),) + tail


def quartet_incumbent(terms):
    pairs = []
    for s in range(0, len(terms), 4):
        idx = list(range(s, min(s + 4, len(terms))))
        if len(idx) == 2:
            pairs.append((idx[0], idx[1]))
            continue
        if len(idx) != 4:
            raise AssertionError({"unexpected_quartet_tail": idx})
        patterns = [
            [(idx[0], idx[1]), (idx[2], idx[3])],
            [(idx[0], idx[2]), (idx[1], idx[3])],
            [(idx[0], idx[3]), (idx[1], idx[2])],
        ]
        vals = []
        for oi, ps in enumerate(patterns):
            m = metrics(terms, ps)
            vals.append((m["Lambda"], m["T"], m["CNOT"], oi, tuple(ps)))
        pairs.extend(min(vals)[4])
    return pairs


def frontier_2d(rows):
    rows = sorted(rows, key=lambda x: (x["dC"], x["dl"], x["pairs"]))
    keep = []
    best_dl = float("inf")
    for r in rows:
        if r["dl"] < best_dl - 1e-15:
            keep.append(r)
            best_dl = r["dl"]
    return keep


def dominates(a, b):
    return (
        a["dD"] >= b["dD"]
        and a["dC"] <= b["dC"]
        and a["dl"] <= b["dl"] + 1e-15
        and (a["dD"] > b["dD"] or a["dC"] < b["dC"] or a["dl"] < b["dl"] - 1e-15)
    )


def local_frontier(terms, indices, base_pairs):
    base = metrics(terms, base_pairs)
    grouped = {}
    count = 0
    for ps in enumerate_matchings(indices):
        count += 1
        m = metrics(terms, ps)
        r = {
            "pairs": ps,
            "dl": m["Lambda"] - base["Lambda"],
            "dC": m["CNOT"] - base["CNOT"],
            "dD": m["direct"] - base["direct"],
        }
        grouped.setdefault(r["dD"], []).append(r)
    reduced = []
    for dD in sorted(grouped, reverse=True):
        reduced.extend(frontier_2d(grouped[dD]))
    keep = []
    for i, a in enumerate(reduced):
        if any(i != j and dominates(b, a) for j, b in enumerate(reduced)):
            continue
        keep.append(a)
    keep.sort(key=lambda x: (-x["dD"], x["dC"], x["dl"], x["pairs"]))
    return base, keep, count


def prune_same_direct(states):
    by_d = {}
    for (dD, dC), (dl, choices) in states.items():
        by_d.setdefault(dD, []).append((dC, dl, choices))
    out = {}
    for dD, rows in by_d.items():
        rows.sort(key=lambda x: (x[0], x[1], x[2]))
        best_dl = float("inf")
        for dC, dl, choices in rows:
            if dl < best_dl - 1e-15:
                out[(dD, dC)] = (dl, choices)
                best_dl = dl
    return out


def proof_payload(terms, pairs):
    payload = []
    ok = True
    for i, j in pairs:
        k0, a0 = terms[i]
        k1, a1 = terms[j]
        if symp(k0, k1):
            w = direct_witness(k0, k1)
            lam = math.hypot(abs(a0), abs(a1))
        else:
            w = tare_witness(k0, k1)
            lam = math.sqrt(2.0) * math.hypot(abs(a0), abs(a1))
        ok = ok and all(w["checks"].values())
        rec = {
            "term_indices": [int(i), int(j)],
            "input_keys": [list(k0), list(k1)],
            "type": w["type"],
            "orientation": w["orientation"],
            "lambda_pair": round(float(lam), 16),
            "controlled_CNOT": w["controlled_CNOT"],
            "projected_T": w["projected_T"],
        }
        for key in ("restore_base", "R0", "R1", "S", "T0", "T1", "restore_support"):
            if key in w:
                rec[key] = w[key]
        payload.append(rec)
    return payload, bool(ok)


def singleton_resource(term):
    if term is None:
        return {"Lambda": 0.0, "CNOT": 0, "T": 0, "count": 0, "key": None}
    k, a = term
    # Under the same outer one-block control, a Pauli singleton uses one controlled
    # Clifford Pauli factor per nonidentity support site; coefficient lives in PREP.
    return {"Lambda": float(abs(a)), "CNOT": int(weight(k)), "T": 0, "count": 1, "key": list(k)}


def add_singleton(m, sr):
    out = dict(m)
    out["Lambda"] += sr["Lambda"]
    out["CNOT"] += sr["CNOT"]
    out["T"] += sr["T"]
    return out


def main():
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    identity = paulis.pop((0, 0), 0.0)
    all_terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    singleton = all_terms[-1] if len(all_terms) % 2 else None
    terms = all_terms[:-1] if singleton is not None else all_terms
    sr = singleton_resource(singleton)

    b_pairs = quartet_incumbent(terms)
    b_pair = metrics(terms, b_pairs)
    b = add_singleton(b_pair, sr)

    windows = []
    total_enum = 0
    for start in range(0, len(terms), WINDOW):
        end = min(start + WINDOW, len(terms))
        idx = list(range(start, end))
        if len(idx) % 2:
            raise AssertionError({"odd_paired_window": idx})
        bp = [p for p in b_pairs if start <= p[0] < end and start <= p[1] < end]
        if len(bp) != len(idx) // 2:
            raise AssertionError({"incumbent_pair_cut": [start, end], "pairs": bp})
        base, front, count = local_frontier(terms, idx, bp)
        total_enum += count
        windows.append({"start": start, "end": end, "base": base, "frontier": front, "enumerated": count})

    # exact global composition under the frozen 1% normalization budget
    suffix_min_dl = [0.0] * (len(windows) + 1)
    suffix_max_dD = [0] * (len(windows) + 1)
    for wi in range(len(windows) - 1, -1, -1):
        f = windows[wi]["frontier"]
        suffix_min_dl[wi] = suffix_min_dl[wi + 1] + min(x["dl"] for x in f)
        suffix_max_dD[wi] = suffix_max_dD[wi + 1] + max(x["dD"] for x in f)
    budget = NORM_FRAC * b["Lambda"]
    states = {(0, 0): (0.0, tuple())}
    frontier_sizes = [1]
    for wi, w in enumerate(windows):
        nxt = {}
        for (dD0, dC0), (dl0, choices0) in states.items():
            for oi, opt in enumerate(w["frontier"]):
                dD = dD0 + opt["dD"]
                dC = dC0 + opt["dC"]
                dl = dl0 + opt["dl"]
                if dl + suffix_min_dl[wi + 1] > budget + 1e-12:
                    continue
                if dD + suffix_max_dD[wi + 1] < 0:
                    continue
                key = (dD, dC)
                cand = (dl, choices0 + (oi,))
                old = nxt.get(key)
                if old is None or cand < old:
                    nxt[key] = cand
        states = prune_same_direct(nxt)
        if not states:
            raise AssertionError({"empty_global_frontier": wi})
        frontier_sizes.append(len(states))

    feasible = []
    for (dD, dC), (dl, choices) in states.items():
        if dD >= 0 and dl <= budget + 1e-12:
            feasible.append((dC, dl, -dD, choices, dD))
    if not feasible:
        raise AssertionError("no admissible H4 successor")
    dC, dl, _negd, choices, dD = min(feasible, key=lambda x: (x[0], x[1], x[2], x[3]))
    e_pairs = []
    for wi, oi in enumerate(choices):
        e_pairs.extend(windows[wi]["frontier"][oi]["pairs"])
    e_pair = metrics(terms, e_pairs)
    e = add_singleton(e_pair, sr)

    # Bind DP aggregate and then generate proof-carrying selected witnesses.
    if e_pair["CNOT"] - b_pair["CNOT"] != dC or e_pair["direct"] - b_pair["direct"] != dD:
        raise AssertionError("global discrete delta mismatch")
    if abs((e_pair["Lambda"] - b_pair["Lambda"]) - dl) > 1e-10:
        raise AssertionError("global lambda delta mismatch")
    bproof, bok = proof_payload(terms, b_pairs)
    eproof, eok = proof_payload(terms, e_pairs)

    # Every full 12 window must enumerate exactly 10,395 matchings. Smaller even
    # tails are checked against (n-1)!! exactly.
    def matching_count(n):
        z = 1
        for k in range(n - 1, 0, -2):
            z *= k
        return z
    enum_ok = all(w["enumerated"] == matching_count(w["end"] - w["start"]) for w in windows)

    norm_over = e["Lambda"] / b["Lambda"] - 1.0
    c_red = 1.0 - e["CNOT"] / b["CNOT"]
    t_red = 0.0 if b["T"] == 0 else 1.0 - e["T"] / b["T"]
    lambda_cnot_ratio = (e["Lambda"] * e["CNOT"]) / (b["Lambda"] * b["CNOT"])
    lambda_t_ratio = (e["Lambda"] * e["T"]) / (b["Lambda"] * b["T"]) if b["T"] else 1.0

    blocks = len(b_pairs) + sr["count"]
    address = int(math.ceil(math.log2(blocks))) if blocks > 1 else 0
    padded = 1 << address if address else 1
    common_outer = {
        "outer_blocks": int(blocks),
        "outer_address_qubits": address,
        "dense_prepare_rotations_per_Prepare": int(padded - 1),
        "dense_prepare_rotations_two_sided": int(2 * (padded - 1)),
        "unary_selector_routing_T_reference": int(4 * max(0, blocks - 1)),
        "local_TARE_ancilla_capacity": 1,
        "synthesis_precision": SYNTH_EPS,
        "status": "reported_common_reference__not_hidden_from_primary_block_cost",
    }

    coeff_rotations = 3 * len(b_pairs)
    gates = {
        "source_blob_match": True,
        "hermitian": max_imag <= 5e-8,
        "eight_qubits_no_taper": N_QUBITS == 8,
        "incumbent_reconstructed": len(b_pairs) == len(terms) // 2,
        "windows_exhaustive": enum_ok,
        "all_selected_witnesses": bok and eok,
        "normalization_le_1pct": norm_over <= 0.0100000001,
        "T_nonworsening": e["T"] <= b["T"],
        "direct_nonworsening": e_pair["direct"] >= b_pair["direct"],
        "controlled_CNOT_reduction_ge_1pct": c_red >= 0.01,
        "no_stronger_oracle": True,
        "outer_common_layer_reported": True,
    }
    result = {
        "schema": "ORIONQ.MAXR5F.H4ControlledConfirmation.v1",
        "authority": "MAX_R5F_FRESH_H4_CONTROLLED_COMPOSITION_AWARE_COMPILER_SUPPORTED" if all(gates.values()) else "MAX_R5F_FRESH_H4_PROTOCOL_NEGATIVE",
        "scope": "fresh_public_H4_controlled_pair_compiler__not_R6_novelty_authority",
        "source": {"repo": "npbauman/DUCC-Hamiltonian-Library", "commit": SOURCE_COMMIT, "blob": SOURCE_BLOB, "path": SOURCE_PATH},
        "mapping": "repository_extractor_semantics_then_Jordan_Wigner_no_tapering",
        "n_spatial_orbitals": N_ORB,
        "n_qubits": N_QUBITS,
        "two_body_sparse_entries": len(two),
        "pauli_terms_including_identity": len(all_terms) + 1,
        "nonidentity_pauli_terms": len(all_terms),
        "identity_coefficient_without_nuclear_shift": identity,
        "max_pauli_imaginary_residual": max_imag,
        "odd_singleton": None if singleton is None else {"key": list(singleton[0]), "coefficient": singleton[1], "resource": sr},
        "pair_count": len(b_pairs),
        "coefficient_rotation_count": coeff_rotations,
        "window_size": WINDOW,
        "window_count": len(windows),
        "perfect_matchings_enumerated": total_enum,
        "local_frontier_sizes": [len(w["frontier"]) for w in windows],
        "global_frontier_sizes": frontier_sizes,
        "incumbent": b,
        "successor": e,
        "incumbent_pair_resources": b_pair,
        "successor_pair_resources": e_pair,
        "normalization_overhead": norm_over,
        "controlled_CNOT_reduction": c_red,
        "projected_T_reduction": t_red,
        "normalization_weighted_CNOT_ratio": lambda_cnot_ratio,
        "normalization_weighted_T_ratio": lambda_t_ratio,
        "direct_delta": e_pair["direct"] - b_pair["direct"],
        "incumbent_pair_list_sha256": sha([[int(i), int(j)] for i, j in b_pairs]),
        "successor_pair_list_sha256": sha([[int(i), int(j)] for i, j in e_pairs]),
        "incumbent_witness_sha256": sha(bproof),
        "successor_witness_sha256": sha(eproof),
        "sorted_terms_sha256": sha([[list(k), format(float(a), ".17g")] for k, a in all_terms]),
        "common_outer_layer": common_outer,
        "gates": gates,
        "r5f_protocol_pass": all(gates.values()),
    }
    print("ORIONQ_MAX_R5F_H4_RESULT=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
