#!/usr/bin/env python3
"""QG-7d N2_DIRECT: remove QG-7c's common spectator and referee pinned residuals exactly."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(ORION_Q)); sys.path.insert(0, str(ORION_QG))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import qg5b_exact_forecaster as qg5b  # noqa: E402
import qg7b_hybrid_family as qg7b  # noqa: E402
import qg7c_classification as qg7c  # noqa: E402

ISSUE = "SzeChunYiu/ORION#836"
BASE = "c5ba39fef4f25c46de5fb69bf07f50530f4693ca"
PARENT = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PROTO = ROOT / "development/orion-qg-regime-geometry/QG7D_PINNED_COMM_S2_PROTOCOL_V1.md"
AMEND = ROOT / "development/orion-qg-regime-geometry/QG7D_N2_DIRECT_PROTOCOL_AMENDMENT_V1.md"
DEFAULT = ROOT / "artifacts/orion-qg-qg7d-n2-direct.json"
TOKEN = "ORIONQG_QG7D_N2="
INF = 10**9
MATCHING = r6m._SYNTHETIC_MATCHING
EXPECTED_PARENT_DIGEST = "0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
EXPECTED_CENSUS = {
    "PA_ja0_delta1": 97072, "PA_ja0_delta2": 2376, "PA_ja1_delta1": 3600,
    "PP_ja0_delta1": 30500, "PP_ja0_delta2": 440, "PP_ja1_delta1": 1616,
}


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def key(letters):
    out = (0, 0)
    for q, le in enumerate(letters):
        if le:
            out = p10.mul(out, r6o._letter_key(int(le), q))
    return out


def direct_row(row):
    if row["case"] != "PA":
        raise ValueError("N2_DIRECT only admits PA rows; PP has a third phantom home")
    ja = int(row["ja"]); R_b = int(row["R_b"]); R_a = int(row["R_a"]); p = int(row["p"])
    t0b, t1b, t21b = qg7c._decode_core(int(row["coreB"]))
    t0a, t1a, t21a = qg7c._decode_core(int(row["coreA"]))
    e0b, e1b = divmod(int(row["envB"]), 4); u0b, v0b = divmod(e0b, 4)
    e0a, e1a = divmod(int(row["envA"]), 4); u0a, v0a = divmod(e0a, 4)
    t2_0b = qg7c.lmul(u0b, qg7c.Z)
    t2_0a = u0a
    t3_0b = v0b
    if ja == 0:
        t3_0a = qg7c.lmul(v0a, qg7c.Z); t3_1b = e1b; t3_1a = qg7c.lmul(e1a, qg7c.X)
    else:
        t3_0a = v0a; t3_1b = qg7c.lmul(e1b, qg7c.X); t3_1a = e1a
    tp = (
        (key([t0b, t0a]), key([t1b, t1a])),
        (key([t2_0b, t2_0a]), key([t21b, t21a])),
        (key([t3_0b, t3_0a]), key([t3_1b, t3_1a])),
    )
    s = p10.mul(r6o._letter_key(qg7c.Z, 0), r6o._letter_key(qg7c.Z, 1))
    w = qg7c.lmul(R_a, qg7c.Z)
    ours = (p10.mul(r6o._letter_key(R_b, 0), r6o._letter_key(R_a, 1)), r6o._letter_key(w, 1))
    pin = (r6o._letter_key(qg7c.Z, 0), r6o._letter_key(p, 0))
    third = ((r6o._letter_key(qg7c.Z, 1), r6o._letter_key(qg7c.X, 1)) if ja == 0
             else (r6o._letter_key(qg7c.Z, 0), r6o._letter_key(qg7c.X, 0)))
    frames6 = ours + pin + third
    t6 = (tp[0][0], tp[0][1], tp[1][0], tp[1][1], tp[2][0], tp[2][1])
    ok, labs = r6s.config_labels(frames6, s)
    ref = int(r6s.config_cost(t6, frames6, s, (0, 1, 1), 2)) if ok else None
    return tp, {"accepted": bool(ok), "labels": list(labs) if ok else None, "reference_cost": ref,
                "has_identity_target": any(x == (0, 0) for pair in tp for x in pair)}


def clear_caches():
    r6m._local_table.cache_clear(); r6o._block_cache.clear(); qg5b._bprime_block_cache.clear(); qg7b._bsecond_block_cache.clear()


def evaluate(tp):
    clear_caches()
    dxx = r6p.dxx_search(tp, 2, want_witness=True)
    dplus = r6p.dxx_search(tp, 2, max_weight=1, want_witness=True)
    bp, bpw = qg5b.bprime_family_min(tp, 2, want_witness=True)
    bpp, bppw = qg7b.bsecond_family_min(tp, 2, want_witness=True)
    cxx = int(dxx["C_Dxx"]); cd = int(dplus["C_Dxx"])
    cbp = INF if bp is None else int(bp); cbpp = INF if bpp is None else int(bpp)
    checks = {
        "dxx_witness": bool(r6p.verify_dxx_witness(tp, 2, dxx["witness"])),
        "dplus_witness": bool(r6p.verify_dxx_witness(tp, 2, dplus["witness"])),
        "bprime_witness": bp is None or bool(qg5b.verify_bprime_witness(tp, 2, bpw)),
        "bsecond_witness": bpp is None or bool(qg7b.verify_bsecond_witness(tp, 2, bppw)),
        "bsecond_infeasible_n2": bpp is None,
    }
    incumbent = min(cd, cbp, cbpp)
    strict = cxx < incumbent
    dp = None; replay = None
    if strict:
        terms = r6m._synthetic_terms(tp)
        dp = int(r6o.dp_cost_frozen_configs(terms, 2))
        rw = r6m.exact_r6m_matching(terms, MATCHING, 2, list(range(6)))
        replay = {"C_DP": dp, "C_R6M": int(rw["C_R6M"]), "checks": rw["checks"], "witness": rw,
                  "pass": dp == cxx == int(rw["C_R6M"]) and all(rw["checks"].values())}
    return {
        "C_Dxx": cxx, "C_Dplus": cd, "f_Bprime": None if bp is None else int(bp),
        "f_Bsecond": None if bpp is None else int(bpp), "incumbent": int(incumbent),
        "gap_Dxx_minus_incumbent": int(cxx - incumbent), "strict": bool(strict),
        "checks": checks, "dxx_witness": dxx["witness"], "dplus_witness": dplus["witness"],
        "bprime_witness": bpw, "bsecond_witness": bppw, "dp_replay": replay,
    }


def identity_control():
    tp = (((0, 0), (1, 0)), ((0, 1), (1, 1)), ((3, 0), (0, 3)))
    terms = r6m._synthetic_terms(tp)
    perm_b = perm_c = 0; centrals = (0, 1, 1)
    dp = r6m._dp_config_cost(terms, MATCHING, perm_b, perm_c, centrals, 2)
    brute = r6m._brute_config_n2(tp, perm_b, perm_c, centrals)
    return {"target_pairs": [[list(a), list(b)] for a, b in tp], "dp": dp, "brute": brute,
            "has_identity": True, "pass": dp is not None and brute is not None and int(dp) == int(brute)}


def main() -> int:
    parent = json.loads(PARENT.read_text())
    t4 = parent["t4b_pinned"]
    rows = t4["failing_verbatim_capped"]
    pbind = {
        "digest": parent.get("result_digest") == EXPECTED_PARENT_DIGEST,
        "terminal": parent.get("terminal") == "QG7C_PARTIAL__L4B_OPEN",
        "domain": int(t4["domain_size"]) == 536870912,
        "failures": int(t4["failures_total"]) == 135604,
        "worst": int(t4["worst_delta"]) == 2,
        "census": t4["failing_census"] == EXPECTED_CENSUS,
        "capped_rows_40": len(rows) == 40,
        "all_capped_rows_PA": all(r["case"] == "PA" for r in rows),
    }
    control = identity_control()
    outrows=[]; selected=None; strict_count=0; identities=0
    for i,row in enumerate(rows):
        tp, ref = direct_row(row); identities += int(ref["has_identity_target"])
        ev = evaluate(tp)
        rec = {"index": i, "parent_row": row, "target_pairs": [[list(a),list(b)] for a,b in tp],
               "reference": ref, "evaluation": ev}
        outrows.append(rec)
        if ev["strict"] and ev["dp_replay"] and ev["dp_replay"]["pass"]:
            strict_count += 1
            if selected is None: selected = rec
    all_member_checks = all(all(r["evaluation"]["checks"].values()) for r in outrows)
    gates = {
        "protocol_present": PROTO.is_file() and AMEND.is_file(), "parent_all": all(pbind.values()),
        "identity_admissibility": bool(control["pass"]), "rows_all_evaluated": len(outrows)==40,
        "member_witnesses": all_member_checks, "bsecond_infeasible_all": all(r["evaluation"]["f_Bsecond"] is None for r in outrows),
        "strict_rows_replayed": all((not r["evaluation"]["strict"]) or (r["evaluation"]["dp_replay"] and r["evaluation"]["dp_replay"]["pass"]) for r in outrows),
    }
    positive = selected is not None and all(gates.values())
    terminal = ("QG7D_BTRIPLEPRIME_REGIME_FOUND__PINNED_COMM_S2_EXACT_WITNESS" if positive
                else "QG7D_N2_DIRECT_NO_GAP_IN_COMMITTED_T4B_ROWS")
    result = {
        "schema":"ORIONQG.QG7D.N2Direct.v1","issue":ISSUE,"base_revision":BASE,
        "protocol_sha256":sha(PROTO),"amendment_sha256":sha(AMEND),"parent_binding":pbind,
        "identity_target_control":control,"rows_evaluated":len(outrows),"identity_target_rows":identities,
        "strict_witness_count":strict_count,"selected":selected,"rows":outrows,"gates":gates,"terminal":terminal,
        "global_all_n_closure_authority":False,"btripleprime_authority":bool(positive),"novelty_authority":False,
        "r6_authority":False,"physical_quantum_advantage_claim":False,"chemistry_data_read":False,
        "reserved_stretched_n2_accessed":False,
    }
    u=dict(result); result["result_digest"] = hashlib.sha256(canonical(u).encode()).hexdigest()
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default=str(DEFAULT)); ns=ap.parse_args()
    p=Path(ns.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canonical(result)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
