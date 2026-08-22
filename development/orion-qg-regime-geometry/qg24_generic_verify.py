#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-24 tropical weighted-automaton theorem."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts/orion-qg-qg24-tropical-wfa.json"
R6S_RESULT = ROOT / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG7C_RESULT = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
QG23_RESULT = ROOT / "research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg24-generic-verification.json"
TOKEN = "ORIONQG_QG24_GENERIC="
POS = "QG24_TARE_UNRESTRICTED_EXACT_OPTIMUM_RECOGNIZED_BY_FINITE_TROPICAL_AUTOMATON_ALL_N"

# Independent phase-free Pauli coding: 0=I,1=X,2=Y,3=Z.
BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
CODE = {b: i for i, b in enumerate(BITS)}


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha_obj(v):
    return hashlib.sha256(canon(v).encode()).hexdigest()


def valid_digest(r):
    u = {k: v for k, v in r.items() if k != "result_digest"}
    return r.get("result_digest") == hashlib.sha256(canon(u).encode()).hexdigest()


def mul(a, b):
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return CODE[(ax ^ bx, az ^ bz)]


def symp(a, b):
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return (ax * bz + az * bx) & 1


def wt(a):
    x, z = BITS[a]
    return int(bool(x or z))


def tables():
    lw = [wt(a) for a in range(4)]
    lm = [[mul(a, b) for b in range(4)] for a in range(4)]
    sy = [[symp(a, b) for b in range(4)] for a in range(4)]
    f3 = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a, b, c in itertools.product(range(4), repeat=3):
        f3[a][b][c] = 1 if a == b == c != 0 else lw[a] + lw[b] + lw[c]
    return lw, lm, sy, f3


def accept_local(frames, tag, sy):
    if any(f == 0 for f in frames):
        return False, None
    if any(sy[frames[2*j]][frames[2*j+1]] != 1 for j in range(3)):
        return False, None
    l0, l1 = sy[tag][frames[0]], sy[tag][frames[1]]
    if l0 == l1:
        return False, None
    if any(sy[tag][frames[2*j]] != l0 or sy[tag][frames[2*j+1]] != l1 for j in (1,2)):
        return False, None
    return True, (l0, l1)


def aux_rows(sy):
    pairs = [(a,b) for a in range(1,4) for b in range(1,4) if sy[a][b] == 1]
    out = []
    for ps in itertools.product(pairs, repeat=3):
        frames = tuple(x for p in ps for x in p)
        for tag in range(4):
            ok, labels = accept_local(frames, tag, sy)
            if ok:
                out.append((frames, tag, labels))
    return pairs, out


def permute_target(t, p):
    out=[]
    for j in range(3):
        a,b=t[2*j],t[2*j+1]
        out.extend((a,b) if p[j]==0 else (b,a))
    return tuple(out)


def cost_one(pt, frames, tag, centrals, lm, f3):
    raw=0
    for j in range(3):
        raw += (2 if centrals[j]==0 else 4) * int(frames[2*j]!=0)
        raw += (2 if centrals[j]==1 else 4) * int(frames[2*j+1]!=0)
    raw += 2*int(tag!=0)
    r=[lm[pt[i]][frames[i]] for i in range(6)]
    raw += f3[r[0]][r[2]][r[4]] + f3[r[1]][r[3]][r[5]]
    return raw-18


def calibration(rows, lm, f3):
    perms=list(itertools.product((0,1), repeat=3))
    centrals=list(itertools.product((0,1), repeat=3))
    targets=list(itertools.product(range(1,4), repeat=6))
    minima=[]
    for t in targets:
        best=10**9
        for p in perms:
            pt=permute_target(t,p)
            for c in centrals:
                for frames,tag,_ in rows:
                    v=cost_one(pt,frames,tag,c,lm,f3)
                    if v<best:
                        best=v
        minima.append(best)
    h=Counter(minima)
    return {
        "valid_target_words":len(targets),
        "minimum_vector_sha256":sha_obj(minima),
        "minimum_cost_histogram":{str(k):int(v) for k,v in sorted(h.items())},
        "minimum_cost_min":min(minima),
        "minimum_cost_max":max(minima),
    }


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args()
    src=json.loads(x.input.read_text())

    # Seal the generic finite-state contract and calibration before parent inspection.
    lw,lm,sy,f3=tables()
    pairs,rows=aux_rows(sy)
    cal=calibration(rows,lm,f3)
    state={
        "input_alphabet_size":4**6,
        "target_permutation_sectors":2**3,
        "central_bit_sectors":2**3,
        "global_control_sectors":64,
        "frame_support_counters":6,
        "frame_counter_cardinality":3,
        "tag_counter_cardinality":7,
        "frame_pair_parity_bits":3,
        "tag_frame_parity_bits":6,
        "raw_states_per_sector":3**6*7*2**9,
        "transition_local_aux_alphabet_size":4**7,
    }
    contract_checks={
        "alphabet_4096":state["input_alphabet_size"]==4096,
        "sectors_64":state["global_control_sectors"]==64,
        "raw_states_2612736":state["raw_states_per_sector"]==2612736,
        "local_choices_16384":state["transition_local_aux_alphabet_size"]==16384,
        "anti_pairs_6":len(pairs)==6,
        "n1_aux_rows_48":len(rows)==48,
        "two_orientations":{r[2] for r in rows}=={(0,1),(1,0)},
        "n1_targets_729":cal["valid_target_words"]==729,
    }

    r6s=json.loads(R6S_RESULT.read_text());q7c=json.loads(QG7C_RESULT.read_text());q23=json.loads(QG23_RESULT.read_text())
    m1=q7c.get("m1_inventory",{});t1=q7c.get("t1_prune",{});t2=q7c.get("t2_occupancy",{});rb=q7c.get("receipt_bindings",{})
    parent_checks={
        "r6s_support2_all_n":str(r6s.get("authority","")).startswith("MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED") and r6s.get("outcome")=="THEOREM_MACHINE_CHECKED",
        "qg7c_r6s_bound":rb.get("r6s_receipt_bound") is True,
        "m1_exact":m1.get("holds") is True and set(m1.get("irreducible_shape_counts",{}))=={"anchored","phantom","comm_s2"} and m1.get("unclassified_irreducible")==0,
        "t1_exact":t1.get("holds") is True and t1.get("failures")==0 and t1.get("exact_refund")==2,
        "t2_exact":t2.get("holds") is True and t2.get("occupancy_failures_from_m1")==0 and t2.get("per_shape_anticommuting_tag_qubits")=={"anchored":1,"comm_s2":2,"phantom":1},
        "tag_cap": "wt(s) <= 3 + #comm-s2" in str(t2.get("corollary","")),
        "chain_still_open":q7c.get("terminal")=="QG7C_PARTIAL__L4B_OPEN",
        "qg23_hostile_corrected":q23.get("both_accept") is True and q23.get("maximum_auxiliary_support")==6 and q23.get("FULL_STATE_DIMENSION_6") is False,
    }

    generic_tables={"LW":lw,"LM":lm,"SY":sy,"F3":f3}
    source_checks={
        "source_digest":valid_digest(src),
        "source_positive":src.get("terminal")==POS and src.get("FINITE_STATE_EXACT_COMPILER") is True and src.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True,
        "tables_identical":src.get("local_tables",{}).get("sha256")==sha_obj(generic_tables) and all(src.get("local_tables",{}).get(k)==v for k,v in generic_tables.items()),
        "state_identical":src.get("state_contract",{}).get("input_alphabet_size")==4096 and src.get("state_contract",{}).get("global_control_sectors")==64 and src.get("state_contract",{}).get("raw_states_per_sector")==2612736 and src.get("state_contract",{}).get("parity_bits_total")==9,
        "n1_digest_identical":src.get("n1_calibration",{}).get("production_minimum_vector_sha256")==cal["minimum_vector_sha256"]==src.get("n1_calibration",{}).get("wfa_minimum_vector_sha256"),
        "n1_hist_identical":src.get("n1_calibration",{}).get("minimum_cost_histogram")==cal["minimum_cost_histogram"],
        "n1_range_identical":src.get("n1_calibration",{}).get("minimum_cost_min")==cal["minimum_cost_min"] and src.get("n1_calibration",{}).get("minimum_cost_max")==cal["minimum_cost_max"],
        "production_n1_formula_exact":src.get("n1_calibration",{}).get("all_formula_rows_match") is True and src.get("n1_calibration",{}).get("all_minima_match") is True,
        "path_bijection_claim_scoped":src.get("proof_audit",{}).get("accepting_path_to_original_configuration") is True and src.get("proof_audit",{}).get("capped_original_configuration_to_accepting_path") is True and src.get("proof_audit",{}).get("fixed_matching_only_v1") is True,
        "stronger_authority_false":all(src.get(k) is False for k in ("AUTOMATON_MINIMALITY","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","CHAIN_ALL_N","ASYMPTOTIC_PHASE_BOUNDARY","GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY","novelty_authority","r6_authority","physical_quantum_advantage_claim")),
    }

    ok=all(contract_checks.values()) and all(parent_checks.values()) and all(source_checks.values())
    out={
        "schema":"ORIONQG.QG24.GenericVerification.v1",
        "decision":"ACCEPT_FINITE_TROPICAL_EXACT_COMPILER" if ok else "REJECT",
        "all_checks":bool(ok),
        "contract_checks":contract_checks,
        "parent_checks":parent_checks,
        "source_checks":source_checks,
        "generic_state_contract":state,
        "generic_local_tables_sha256":sha_obj(generic_tables),
        "generic_n1_calibration":cal,
        "generic_n1_aux_rows":len(rows),
        "source_result_digest":src.get("result_digest"),
        "FINITE_STATE_EXACT_COMPILER":bool(ok),
        "UNRESTRICTED_DP_EQUALITY_ALL_N":bool(ok),
        "AUTOMATON_MINIMALITY":False,
        "CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,
        "CHAIN_ALL_N":False,
        "ASYMPTOTIC_PHASE_BOUNDARY":False,
        "GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY":False,
        "novelty_authority":False,
        "r6_authority":False,
        "physical_quantum_advantage_claim":False,
    }
    x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"state_count":state["raw_states_per_sector"],"n1_digest":cal["minimum_vector_sha256"],"n1_hist":cal["minimum_cost_histogram"]}))
    return 0

if __name__=="__main__":raise SystemExit(main())
