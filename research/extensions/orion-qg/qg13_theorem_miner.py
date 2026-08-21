#!/usr/bin/env python3
"""QG-13 V1: infer normal-form theorem packets from production compiler semantics."""
from __future__ import annotations

import argparse, hashlib, itertools, json, sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG13_THEOREM_MINER_PROTOCOL_V1.md"
R6S = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG1 = REPO_ROOT / "research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json"
QG8 = REPO_ROOT / "research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/orion-qg-qg13-theorem-miner.json"
TOKEN = "ORIONQG_QG13_THEOREM_MINER="


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code4(values: tuple[int, ...]) -> int:
    x = 0
    for v in values:
        x = (x << 2) | int(v)
    return x


def gf2_basis(values: Iterable[int]) -> list[int]:
    basis: dict[int, int] = {}
    for raw in sorted(set(int(v) for v in values)):
        x = raw
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return [basis[k] for k in sorted(basis, reverse=True)]


def span_report(changes: set[int], width: int) -> dict[str, Any]:
    b = gf2_basis(changes)
    return {
        "rank": len(b), "basis": b, "unique_change_count": len(changes),
        "change_vectors": sorted(changes),
        "changed_bit_union": [i for i in range(width) if any((x >> i) & 1 for x in changes)],
    }


def infer_r6m_quotient() -> dict[str, Any]:
    names = ("A0", "A1", "B0", "B1", "C0", "C1")
    changes = {n: set() for n in names}
    rows = 0
    for values in itertools.product(range(4), repeat=7):
        rows += 1
        old = int(r6m._DELTA[code4(values)])
        for i, name in enumerate(names):
            newv = list(values); newv[i] = 0
            new = int(r6m._DELTA[code4(tuple(newv))])
            changes[name].add(old ^ new)
    reports = {n: span_report(changes[n], 9) for n in names}
    ranks = sorted({r["rank"] for r in reports.values()})
    return {"rows": rows, "production_state_bits": 9, "slots": reports,
            "uniform_rank": ranks[0] if len(ranks) == 1 else None, "rank_set": ranks}


def infer_r6i_quotient() -> dict[str, Any]:
    changes = {"A": set(), "B": set()}; rows = 0
    for values in itertools.product(range(4), repeat=6):
        rows += 1
        old = int(r6i._DELTA[code4(values)])
        a = (0, 0, values[2], values[3], values[4], values[5])
        b = (values[0], values[1], 0, 0, values[4], values[5])
        changes["A"].add(old ^ int(r6i._DELTA[code4(a)]))
        changes["B"].add(old ^ int(r6i._DELTA[code4(b)]))
    reports = {n: span_report(changes[n], 10) for n in ("A", "B")}
    ranks = sorted({r["rank"] for r in reports.values()})
    return {"rows": rows, "production_state_bits": 10, "blocks": reports,
            "uniform_rank": ranks[0] if len(ranks) == 1 else None, "rank_set": ranks}


def infer_r6m_resource_cone() -> dict[str, Any]:
    hist = {"central": Counter(), "noncentral": Counter()}
    vectors = {"central": set(), "noncentral": set()}
    count = 0
    for kind in ("central", "noncentral"):
        for pos in range(3):
            for f in (1, 2, 3):
                for partner, tag, p, u, v in itertools.product(range(4), repeat=5):
                    del partner, tag
                    old_letter = int(r6m._LM[p, f])
                    if pos == 0:
                        old_f = int(r6m._F3[old_letter, u, v]); new_f = int(r6m._F3[p, u, v])
                    elif pos == 1:
                        old_f = int(r6m._F3[u, old_letter, v]); new_f = int(r6m._F3[u, p, v])
                    else:
                        old_f = int(r6m._F3[u, v, old_letter]); new_f = int(r6m._F3[u, v, p])
                    df = new_f - old_f; count += 1; hist[kind][df] += 1
                    vec = (-1, 0, df, 0, 0) if kind == "central" else (0, -1, df, 0, 0)
                    vectors[kind].add(vec)
    mx = {k: max(v[2] for v in vs) for k, vs in vectors.items()}
    facets = [f"t_c >= {mx['central']}*t_r", f"t_nc >= {mx['noncentral']}*t_r"]
    return {
        "domain_size": count, "resource_coordinates": ["U_c", "U_nc", "F3", "Tag", "Rot"],
        "unique_vectors": {k: [list(x) for x in sorted(v)] for k, v in vectors.items()},
        "delta_f3_histogram": {k: {str(a): b for a, b in sorted(h.items())} for k, h in hist.items()},
        "max_delta_f3": mx, "derived_facets": facets,
    }


def infer_r6i_unit_resource() -> dict[str, Any]:
    hist: Counter[int] = Counter(); violations = []; count = 0; max_delta = -10**9
    for central in range(3):
        m = [4, 4, 4]; m[central] = 2
        for a, b in itertools.product(range(4), repeat=2):
            if a == 0 and b == 0: continue
            r2 = int(r6i._MUL[a, b])
            for p0, p1, p2, s0, s1 in itertools.product(range(4), repeat=5):
                del s0, s1
                old = (m[0]*int(r6i._LW[a]) + m[1]*int(r6i._LW[b]) + m[2]*int(r6i._LW[r2])
                       + int(r6i._LW[int(r6i._MUL[p0,a])])
                       + int(r6i._LW[int(r6i._MUL[p1,b])])
                       + int(r6i._LW[int(r6i._MUL[p2,r2])]))
                new = int(r6i._LW[p0]) + int(r6i._LW[p1]) + int(r6i._LW[p2])
                d = new - old; count += 1; hist[d] += 1; max_delta = max(max_delta, d)
                if d > 0 and len(violations) < 20:
                    violations.append({"central": central, "a": a, "b": b, "p": [p0,p1,p2], "delta": d})
    return {"domain_size": count, "max_delta": max_delta,
            "histogram": {str(k): v for k,v in sorted(hist.items())}, "positive_violations": violations}


def bind_tables() -> dict[str, bool]:
    return {
        "r6m_mul": all(int(r6m._LM[a,b]) == int(p10.h.local_mul(a,b)) for a in range(4) for b in range(4)),
        "r6m_symp": all(int(r6m._SY[a,b]) == int(p10.h.local_symp(a,b)) for a in range(4) for b in range(4)),
        "r6i_mul": all(int(r6i._MUL[a,b]) == int(p10.h.local_mul(a,b)) for a in range(4) for b in range(4)),
        "r6i_symp": all(int(r6i._SYMP[a,b]) == int(p10.h.local_symp(a,b)) for a in range(4) for b in range(4)),
    }


def parent_recovery(r6m_packet: dict, r6i_packet: dict) -> dict[str, Any]:
    r6s = json.loads(R6S.read_text()); qg1 = json.loads(QG1.read_text()); qg8 = json.loads(QG8.read_text())
    qg8_conditions = qg8.get("support2_cone", {}).get("conditions")
    return {
        "opened_after_synthesis": True,
        "r6s_sha256": sha(R6S), "qg1_sha256": sha(QG1), "qg8_sha256": sha(QG8),
        "r6m": {
            "parent_authority": r6s.get("authority"),
            "parent_machine_checked": str(r6s.get("authority","")).startswith("MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"),
            "synthesized_support_bound": r6m_packet["support_bound"],
            "parent_support2_phrase": "support <= 2" in str(r6s.get("claim_boundary",{}).get("covers","")),
            "synthesized_cone": r6m_packet["objective_cone"],
            "qg8_conditions": qg8_conditions,
            "qg8_terminal": qg8.get("terminal"),
        },
        "r6i": {
            "parent_authority": qg1.get("authority"),
            "parent_machine_checked": str(qg1.get("authority","")).startswith("ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED"),
            "synthesized_support_bound": r6i_packet["support_bound"],
            "parent_support5_phrase": "support <= 5" in str(qg1.get("claim_boundary",{}).get("covers","")),
        },
    }


def run() -> dict[str, Any]:
    if not PROTOCOL.is_file(): raise FileNotFoundError(PROTOCOL)
    bindings = bind_tables()
    m_q = infer_r6m_quotient(); i_q = infer_r6i_quotient()
    m_r = infer_r6m_resource_cone(); i_r = infer_r6i_unit_resource()

    m_packet = {
        "family": "R6M", "edit": "E_R6M_ZERO_FRAME_LETTER", "group": "F_2",
        "quotient_dimension": m_q["uniform_rank"], "support_bound": m_q["uniform_rank"],
        "quotient_basis_by_slot": {k:v["basis"] for k,v in m_q["slots"].items()},
        "global_proper_subset_condition": "FRAME_ANTICOMMUTATION_PARITY_IS_NONZERO",
        "objective_cone": m_r["derived_facets"],
        "proof_schema": "ZERO_SUM_DEPENDENCE_PLUS_NONINCREASING_SUPPORT_DELETION",
    }
    i_packet = {
        "family": "R6I", "edit": "E_R6I_ZERO_BLOCK_GENERATORS", "group": "F_2",
        "quotient_dimension": i_q["uniform_rank"], "support_bound": i_q["uniform_rank"],
        "quotient_basis_by_block": {k:v["basis"] for k,v in i_q["blocks"].items()},
        "global_proper_subset_condition": "BLOCK_ANTICOMMUTATION_PARITY_IS_NONZERO",
        "objective_scope": "FROZEN_R6I_UNIT_OBJECTIVE", "max_local_cost_delta": i_r["max_delta"],
        "proof_schema": "ZERO_SUM_DEPENDENCE_PLUS_STRICTLY_DECREASING_BLOCK_DELETION",
    }

    parents = parent_recovery(m_packet, i_packet)
    gates = {
        "production_tables_bound": all(bindings.values()),
        "r6m_domain_16384": m_q["rows"] == 4**7,
        "r6m_uniform_quotient": m_q["uniform_rank"] is not None,
        "r6m_resource_domain_18432": m_r["domain_size"] == 18432,
        "r6m_resource_nonnegative_facet_coefficients": all(x >= 0 for x in m_r["max_delta_f3"].values()),
        "r6i_domain_4096": i_q["rows"] == 4**6,
        "r6i_uniform_quotient": i_q["uniform_rank"] is not None,
        "r6i_resource_domain_46080": i_r["domain_size"] == 46080,
        "r6i_no_positive_local_delta": not i_r["positive_violations"] and i_r["max_delta"] <= 0,
        "parent_r6m_recovered": parents["r6m"]["parent_machine_checked"] and parents["r6m"]["parent_support2_phrase"] and m_packet["support_bound"] == 2,
        "parent_qg8_cone_recovered": parents["r6m"]["qg8_terminal"] == "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED" and m_packet["objective_cone"] == parents["r6m"]["qg8_conditions"],
        "parent_r6i_recovered": parents["r6i"]["parent_machine_checked"] and parents["r6i"]["parent_support5_phrase"] and i_packet["support_bound"] == 5,
    }
    positive = all(gates.values())
    terminal = "QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS" if positive else "QG13_QUOTIENT_OR_RESOURCE_INFERENCE_REFUTED"
    result = {
        "schema": "ORION.QG.QG13.TheoremMiner.v1", "issue": "SzeChunYiu/ORION#767",
        "protocol_sha256": sha(PROTOCOL), "terminal": terminal, "bindings": bindings,
        "r6m_transition": m_q, "r6m_resource": m_r, "r6m_theorem_candidate": m_packet,
        "r6i_transition": i_q, "r6i_resource": i_r, "r6i_theorem_candidate": i_packet,
        "parent_recovery": parents, "gates": gates,
        "new_theorem_authority": False, "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "v2_permission": "OPEN_NEW_EDIT_TEMPLATE_ONLY_IF_PROTECTED_DUAL_HARNESS_ACCEPTS_V1",
    }
    d = dict(result); result["result_digest"] = hashlib.sha256(canonical(d).encode()).hexdigest()
    return result


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output", default=str(DEFAULT_OUTPUT)); a=ap.parse_args()
    r=run(); p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canonical(r)); return 0

if __name__ == "__main__": raise SystemExit(main())
