#!/usr/bin/env python3
"""QG-13 V1: infer theorem packets from production ORION-Q transition semantics."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

BASE = "beac25450b5d95dd766345dcee872fed840f833b"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG13_THEOREM_MINER_PROTOCOL_V1.md"
NOVELTY = ROOT / "development/orion-qg-regime-geometry/QG13_NOVELTY_THREAT_FREEZE_2026-08-21.md"
R6S = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
QG1 = ROOT / "research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json"
QG2 = ROOT / "research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json"
DEFAULT = ROOT / "artifacts/orion-qg-qg13-theorem-miner.json"
TOKEN = "ORIONQG_QG13_THEOREM_MINER="


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code4(values: tuple[int, ...]) -> int:
    out = 0
    for v in values:
        out = (out << 2) | int(v)
    return out


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
    return [basis[p] for p in sorted(basis, reverse=True)]


def span_report(changes: set[int], width: int) -> dict[str, Any]:
    basis = gf2_basis(changes)
    return {
        "rank": len(basis),
        "basis": basis,
        "unique_change_count": len(changes),
        "change_vectors": sorted(changes),
        "changed_bit_union": [b for b in range(width) if any((x >> b) & 1 for x in changes)],
    }


def infer_r6m_quotient() -> dict[str, Any]:
    names = ("A0", "A1", "B0", "B1", "C0", "C1")
    changes = {name: set() for name in names}
    rows = 0
    for vals in itertools.product(range(4), repeat=7):
        rows += 1
        old = int(r6m._DELTA[code4(vals)])
        for slot, name in enumerate(names):
            newvals = list(vals)
            newvals[slot] = 0
            new = int(r6m._DELTA[code4(tuple(newvals))])
            changes[name].add(old ^ new)
    reports = {name: span_report(changes[name], 9) for name in names}
    ranks = sorted({r["rank"] for r in reports.values()})
    return {"domain_rows": rows, "expected_rows": 4**7, "slots": reports, "uniform_rank": ranks[0] if len(ranks) == 1 else None}


def infer_r6i_quotient() -> dict[str, Any]:
    changes = {"A": set(), "B": set()}
    rows = 0
    for vals in itertools.product(range(4), repeat=6):
        rows += 1
        old = int(r6i._DELTA[code4(vals)])
        av = (0, 0, vals[2], vals[3], vals[4], vals[5])
        bv = (vals[0], vals[1], 0, 0, vals[4], vals[5])
        changes["A"].add(old ^ int(r6i._DELTA[code4(av)]))
        changes["B"].add(old ^ int(r6i._DELTA[code4(bv)]))
    reports = {name: span_report(changes[name], 10) for name in ("A", "B")}
    ranks = sorted({r["rank"] for r in reports.values()})
    return {"domain_rows": rows, "expected_rows": 4**6, "blocks": reports, "uniform_rank": ranks[0] if len(ranks) == 1 else None}


def infer_r6m_resource_cone() -> dict[str, Any]:
    maxima = {"central": -10**9, "noncentral": -10**9}
    extrema: dict[str, list[dict[str, int]]] = {"central": [], "noncentral": []}
    rows = 0
    for kind in ("central", "noncentral"):
        for slot in range(3):
            for f in (1, 2, 3):
                for partner, tag, target, u, v in itertools.product(range(4), repeat=5):
                    rows += 1
                    old_letter = int(r6m._LM[target, f])
                    if slot == 0:
                        old = int(r6m._F3[old_letter, u, v]); new = int(r6m._F3[target, u, v])
                    elif slot == 1:
                        old = int(r6m._F3[u, old_letter, v]); new = int(r6m._F3[u, target, v])
                    else:
                        old = int(r6m._F3[u, v, old_letter]); new = int(r6m._F3[u, v, target])
                    df3 = new - old
                    if df3 > maxima[kind]:
                        maxima[kind] = df3
                        extrema[kind] = [{"slot": slot, "f": f, "partner": partner, "tag": tag, "target": target, "u": u, "v": v, "delta_f3": df3}]
                    elif df3 == maxima[kind] and len(extrema[kind]) < 8:
                        extrema[kind].append({"slot": slot, "f": f, "partner": partner, "tag": tag, "target": target, "u": u, "v": v, "delta_f3": df3})
    return {
        "domain_rows": rows,
        "expected_rows": 18432,
        "max_delta_f3": maxima,
        "extreme_witnesses": extrema,
        "objective_cone": [f"t_c >= {maxima['central']}*t_r", f"t_nc >= {maxima['noncentral']}*t_r"],
        "tag_delta": 0,
        "rotation_delta": 0,
    }


def infer_r6i_unit_resource() -> dict[str, Any]:
    count = 0
    maximum = -10**9
    minimum = 10**9
    violations: list[dict[str, Any]] = []
    witnesses: list[dict[str, Any]] = []
    for central in range(3):
        mult = [4, 4, 4]
        mult[central] = 2
        for a, b in itertools.product(range(4), repeat=2):
            if a == 0 and b == 0:
                continue
            r2 = int(r6i._MUL[a, b])
            for p0, p1, p2, s0, s1 in itertools.product(range(4), repeat=5):
                count += 1
                old = (
                    mult[0] * int(r6i._LW[a]) + mult[1] * int(r6i._LW[b]) + mult[2] * int(r6i._LW[r2])
                    + int(r6i._LW[int(r6i._MUL[p0, a])]) + int(r6i._LW[int(r6i._MUL[p1, b])]) + int(r6i._LW[int(r6i._MUL[p2, r2])])
                )
                new = int(r6i._LW[p0]) + int(r6i._LW[p1]) + int(r6i._LW[p2])
                delta = new - old
                maximum = max(maximum, delta); minimum = min(minimum, delta)
                if delta > 0 and len(violations) < 20:
                    violations.append({"central": central, "a": a, "b": b, "p": [p0, p1, p2], "s": [s0, s1], "delta": delta})
                if delta == maximum and len(witnesses) < 12:
                    witnesses.append({"central": central, "a": a, "b": b, "p": [p0, p1, p2], "delta": delta})
    return {"domain_rows": count, "expected_rows": 46080, "max_delta_c": maximum, "min_delta_c": minimum, "positive_violations": violations, "max_witnesses": witnesses}


def parent_score(r6m_packet: dict[str, Any], r6i_packet: dict[str, Any]) -> dict[str, Any]:
    r6s = json.loads(R6S.read_text())
    qg1 = json.loads(QG1.read_text())
    qg2 = json.loads(QG2.read_text())
    o0 = qg2["baseline_control_O0"]["weights"]
    o1 = qg2["objectives"]["O1"]["weights"]
    def inside(w: dict[str, Any]) -> bool:
        return w["t_c"] >= r6m_packet["resource_cone"]["max_delta_f3"]["central"] * w["t_r"] and w["t_nc"] >= r6m_packet["resource_cone"]["max_delta_f3"]["noncentral"] * w["t_r"]
    return {
        "r6s_authority": str(r6s.get("authority", "")),
        "qg1_authority": str(qg1.get("authority", "")),
        "r6m_support_matches_parent": r6m_packet["support_bound"] == 2 and str(r6s.get("outcome", "")).startswith("THEOREM"),
        "r6i_support_matches_parent": r6i_packet["support_bound"] == 5 and "SUPPORT5" in str(qg1.get("authority", "")),
        "qg2_o0_inside_inferred_cone": inside(o0),
        "qg2_o1_outside_inferred_cone": not inside(o1),
        "qg2_o1_support3_control_present": "NEW_SUPPORT3" in qg2["objectives"]["O1"].get("new_trade_classes", []),
        "parent_hashes": {"R6S": sha(R6S), "QG1": sha(QG1), "QG2": sha(QG2)},
    }


def main() -> int:
    q6m = infer_r6m_quotient(); q6i = infer_r6i_quotient()
    cone = infer_r6m_resource_cone(); r6icost = infer_r6i_unit_resource()
    r6m_packet = {
        "edit": "E_R6M_ZERO_FRAME_LETTER",
        "quotient_dimension": q6m["uniform_rank"],
        "support_bound": q6m["uniform_rank"],
        "resource_cone": cone,
        "composition_conditions": ["NONZERO_GLOBAL_ANTICOMMUTATION_SYNDROME", "ZERO_SUM_SUBSET_PROPER", "EDIT_REMOVES_SUPPORT", "TIES_REDUCE_SUPPORT"],
    }
    r6i_packet = {
        "edit": "E_R6I_ZERO_BLOCK_GENERATORS",
        "quotient_dimension": q6i["uniform_rank"],
        "support_bound": q6i["uniform_rank"],
        "unit_objective_resource": r6icost,
        "composition_conditions": ["NONZERO_GLOBAL_ANTICOMMUTATION_SYNDROME", "ZERO_SUM_SUBSET_PROPER", "EDIT_REMOVES_SUPPORT", "DEPENDENT_THIRD_RECOMPUTED"],
    }
    parents = parent_score(r6m_packet, r6i_packet)
    gates = {
        "protocol_present": PROTOCOL.is_file(), "novelty_freeze_present": NOVELTY.is_file(),
        "r6m_domain_exact": q6m["domain_rows"] == q6m["expected_rows"],
        "r6i_domain_exact": q6i["domain_rows"] == q6i["expected_rows"],
        "r6m_uniform_quotient": q6m["uniform_rank"] is not None,
        "r6i_uniform_quotient": q6i["uniform_rank"] is not None,
        "r6m_resource_domain_exact": cone["domain_rows"] == cone["expected_rows"],
        "r6i_resource_domain_exact": r6icost["domain_rows"] == r6icost["expected_rows"],
        "r6i_unit_edit_nonincreasing": r6icost["max_delta_c"] <= 0 and not r6icost["positive_violations"],
        "r6m_parent_recovered": parents["r6m_support_matches_parent"],
        "r6i_parent_recovered": parents["r6i_support_matches_parent"],
        "qg2_controls_consistent": parents["qg2_o0_inside_inferred_cone"] and parents["qg2_o1_outside_inferred_cone"] and parents["qg2_o1_support3_control_present"],
    }
    positive = all(gates.values())
    terminal = "QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS" if positive else "QG13_QUOTIENT_OR_RESOURCE_INFERENCE_REFUTED"
    result = {
        "schema": "ORION.QG.QG13.TheoremMinerRecovery.v1", "issue": "SzeChunYiu/ORION#767", "base_revision": BASE,
        "protocol_sha256": sha(PROTOCOL), "novelty_sha256": sha(NOVELTY),
        "r6m_transition_inference": q6m, "r6i_transition_inference": q6i,
        "r6m_theorem_candidate": r6m_packet, "r6i_theorem_candidate": r6i_packet,
        "parent_scoring_after_synthesis": parents, "gates": gates, "terminal": terminal,
        "new_theorem_authority": False, "novelty_authority": False, "physical_quantum_advantage_claim": False,
    }
    digest_source = canonical(result)
    result["result_digest"] = hashlib.sha256(digest_source.encode()).hexdigest()
    args = argparse.ArgumentParser(); args.add_argument("--output", default=str(DEFAULT)); ns = args.parse_args()
    path = Path(ns.output); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
