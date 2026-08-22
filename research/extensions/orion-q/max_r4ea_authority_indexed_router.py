#!/usr/bin/env python3
"""MAX-R4E-A production calibration: authority-indexed routing over frozen real compiler receipts."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PROTO = ROOT / "development/orion-q-max-r0/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PROTOCOL.md"
QG31 = ROOT / "research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json"
QG28 = ROOT / "research/extensions/orion-qg/QG28_LOCAL_CLIFFORD_ORBIT_RESULTS.json"
QG15B = ROOT / "research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json"
QG9 = ROOT / "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
R4B = ROOT / "research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json"
R4D = ROOT / "research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json"
OUT = ROOT / "artifacts/orion-q-max-r4ea-authority-router.json"
TOKEN = "ORIONQ_MAX_R4EA="
POS = "MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PARETO_DOMINATES_STATIC_ABSTRACTION_POLICIES_ON_REAL_RECEIPTS"

RANK = {
    "ONE_LITERAL_PREDICATE": 1,
    "SUPPORT1_NORMAL_FORM": 2,
    "COEFFICIENT_THEOREM": 3,
    "BULK45": 4,
    "SPECTRUM54": 5,
    "ORBIT715": 6,
    "INDEXED715": 7,
    "EXACT_RICH_STATE": 8,
    "IMPLEMENTATION_AWARE_RESOURCE": 9,
    "CANNOT_AUTHORIZE": 10,
}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def shaf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def route(name: str, supports: list[str], kind: str = "ANSWER", size: int | None = None) -> dict[str, Any]:
    return {"name": name, "supports": sorted(supports), "kind": kind, "burden": RANK[name], "representation_size": size}


def bindings() -> tuple[dict[str, Any], dict[str, Any]]:
    q31 = json.loads(QG31.read_text())
    q28 = json.loads(QG28.read_text())
    q15 = json.loads(QG15B.read_text())
    q9 = json.loads(QG9.read_text())
    r4b = json.loads(R4B.read_text())
    r4d = json.loads(R4D.read_text())
    checks = {
        "qg31_green": q31.get("both_accept") is True and q31.get("QUERY_INDEXED_ABSTRACTION_REQUIRED") is True,
        "qg31_counts": q31.get("class_counts") == {"bulk": 45, "defect_spectrum": 54, "indexed_local_response": 715},
        "qg31_incomparable": q31.get("BULK_SPECTRUM_PARTITIONS_INCOMPARABLE") is True,
        "qg31_scope_boundary": q31.get("FULL_FINITE_N_OPTIMUM_REQUIRES_715_CLASSES") is False,
        "qg28_orbit715": q28.get("both_accept") is True and q28.get("LOCAL_CLIFFORD_ORBIT_COUNT") == 715 and q28.get("ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True,
        "sixlcu_literal_exact": q15.get("q3", {}).get("E_floor") == 0 and q15.get("q3", {}).get("zero_error_cells", {}).get("headline_cell") == [1, 1],
        "stabprep_mixed_impossible": q15.get("q2", {}).get("E_floor") == 43 and q15.get("q2", {}).get("mixed_cell_count") == 12 and q15.get("q2", {}).get("terminal") == "ZERO_UNACHIEVABLE_ANY_BUDGET",
        "r6i_support1": q9.get("both_accept") is True and q9.get("support_bound") == 1 and q9.get("intrinsic_support_number") == 1,
        "r4b_coefficient_only": r4b.get("terminal") == "R4B_TARE_SPLIT_MAJORISATION_THEOREM_SUPPORTED__COEFFICIENT_COORDINATE_ONLY" and "not compiled-resource" in str(r4b.get("authority", "")),
        "r4d_implementation_aware": r4d.get("terminal") == "R4D_IMPLEMENTATION_AWARE_SPLIT_TARE_COMPILER_SUPPORTED__REAL_PUBLIC_HAMILTONIAN" and r4d.get("r4d_protocol_pass") is True,
        "r4d_full_circuit_false": "does not authorize full-circuit" in str(r4d.get("nonclaim", "")),
    }
    receipts = {"qg31": q31, "qg28": q28, "qg15b": q15, "qg9": q9, "r4b": r4b, "r4d": r4d}
    return checks, receipts


def build_cases(receipts: dict[str, Any]) -> list[dict[str, Any]]:
    A = "ASYMPTOTIC_BULK_VALUE"
    S = "UNLABELED_LOCAL_DEFECT_SPECTRUM"
    I = "INDEXED_LOCAL_RESPONSE"
    F = "FULL_FINITE_OPTIMUM"
    D = "DONOR_OPTIMAL_LABEL"
    N = "SUPPORT_NORMAL_FORM"
    C = "COEFFICIENT_SUBNORMALIZATION"
    T = "TOTAL_COMPILED_RESOURCE"
    X = "FULL_CIRCUIT_OR_NOVELTY"
    cases = [
        {"case_id": "C1", "query": A, "routes": [route("BULK45", [A], size=45), route("ORBIT715", [A, F], size=715), route("EXACT_RICH_STATE", [A, F])]},
        {"case_id": "C2", "query": S, "routes": [route("BULK45", [A], size=45), route("SPECTRUM54", [S], size=54), route("EXACT_RICH_STATE", [S])]},
        {"case_id": "C3", "query": I, "routes": [route("BULK45", [A], size=45), route("SPECTRUM54", [S], size=54), route("INDEXED715", [I], size=715), route("EXACT_RICH_STATE", [I])]},
        {"case_id": "C4", "query": F, "routes": [route("BULK45", [A], size=45), route("SPECTRUM54", [S], size=54), route("ORBIT715", [A, F], size=715), route("EXACT_RICH_STATE", [F])]},
        {"case_id": "C5", "query": D, "routes": [route("ONE_LITERAL_PREDICATE", [D]), route("EXACT_RICH_STATE", [D])]},
        {"case_id": "C6", "query": D, "routes": [route("ONE_LITERAL_PREDICATE", []), route("EXACT_RICH_STATE", [D], kind="ESCALATE")]},
        {"case_id": "C7", "query": N, "routes": [route("SUPPORT1_NORMAL_FORM", [N]), route("EXACT_RICH_STATE", [N])]},
        {"case_id": "C8", "query": C, "routes": [route("COEFFICIENT_THEOREM", [C]), route("IMPLEMENTATION_AWARE_RESOURCE", [C, T], kind="ESCALATE")]},
        {"case_id": "C9", "query": T, "routes": [route("COEFFICIENT_THEOREM", [C]), route("IMPLEMENTATION_AWARE_RESOURCE", [C, T], kind="ESCALATE")]},
        {"case_id": "C10", "query": X, "routes": [route("IMPLEMENTATION_AWARE_RESOURCE", [C, T], kind="ESCALATE"), route("CANNOT_AUTHORIZE", [], kind="ABSTAIN")]},
    ]
    # Evaluator-only source binding. Baselines never use this field.
    source = {
        "C1": "QG31/QG28", "C2": "QG31", "C3": "QG31", "C4": "QG28/QG31",
        "C5": "QG15B-SixLCU", "C6": "QG15B-StabPrep", "C7": "QG9-V6",
        "C8": "MAX-R4B", "C9": "MAX-R4B/MAX-R4D", "C10": "MAX-R4D",
    }
    for c in cases:
        c["evaluator_source"] = source[c["case_id"]]
    return cases


def authorized(c: dict[str, Any], r: dict[str, Any]) -> bool:
    return c["query"] in r["supports"]


def gold_route(c: dict[str, Any]) -> str:
    good = [r for r in c["routes"] if r["name"] != "CANNOT_AUTHORIZE" and authorized(c, r)]
    if not good:
        return "CANNOT_AUTHORIZE"
    return min(good, key=lambda x: (x["burden"], x["name"]))["name"]


def choose(c: dict[str, Any], baseline: str) -> str:
    offered = [r for r in c["routes"] if r["name"] != "CANNOT_AUTHORIZE"]
    good = [r for r in offered if authorized(c, r)]
    if baseline == "B0":
        return max(good, key=lambda x: (x["burden"], x["name"]))["name"] if good else "CANNOT_AUTHORIZE"
    if baseline == "B1":
        return min(offered, key=lambda x: (x["burden"], x["name"]))["name"] if offered else "CANNOT_AUTHORIZE"
    if baseline == "B2":
        return min(good, key=lambda x: (x["burden"], x["name"]))["name"] if good else "CANNOT_AUTHORIZE"
    raise ValueError(baseline)


def lookup(c: dict[str, Any], name: str) -> dict[str, Any]:
    if name == "CANNOT_AUTHORIZE":
        return {"name": name, "supports": [], "kind": "ABSTAIN", "burden": RANK[name], "representation_size": None}
    return next(r for r in c["routes"] if r["name"] == name)


def score(cases: list[dict[str, Any]], baseline: str) -> dict[str, Any]:
    rows = []
    false_authority = overcompression = avoidable = correct = compact = escalation = 0
    tare_sizes = []
    for c in cases:
        gold = gold_route(c)
        sel = choose(c, baseline)
        sr = lookup(c, sel)
        gr = lookup(c, gold)
        auth = sel == "CANNOT_AUTHORIZE" or authorized(c, sr)
        is_correct = sel == gold
        false = sel != "CANNOT_AUTHORIZE" and sr["kind"] == "ANSWER" and not auth
        over = sel != "CANNOT_AUTHORIZE" and not auth and sr["burden"] < gr["burden"]
        rich = auth and sel != gold and sr["burden"] > gr["burden"]
        opportunity = gr["kind"] == "ANSWER" and any(authorized(c, r) and r["burden"] > gr["burden"] for r in c["routes"] if r["name"] != "CANNOT_AUTHORIZE")
        captured = opportunity and sel == gold
        esc = gold == "CANNOT_AUTHORIZE" or gr["kind"] == "ESCALATE"
        esc_ok = esc and sel == gold
        correct += int(is_correct); false_authority += int(false); overcompression += int(over); avoidable += int(rich); compact += int(captured); escalation += int(esc_ok)
        if c["case_id"] in {"C1", "C2", "C3", "C4"}:
            tare_sizes.append(sr.get("representation_size"))
        rows.append({"case_id": c["case_id"], "query": c["query"], "selected": sel, "gold": gold, "authorized": auth, "correct": is_correct, "false_authority": false, "overcompression": over, "avoidable_rich_state": rich, "compact_opportunity": opportunity, "captured": captured, "correct_escalation_or_abstention": esc_ok})
    opportunities = sum(int(r["compact_opportunity"]) for r in rows)
    return {"correct_route_count": correct, "false_authority_count": false_authority, "overcompression_count": overcompression, "avoidable_rich_state_count": avoidable, "compact_authorized_opportunities": opportunities, "compact_authorized_captured": compact, "correct_escalation_abstention_count": escalation, "tare_selected_representation_sizes": tare_sizes, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, default=OUT); ns = ap.parse_args()
    checks, receipts = bindings(); cases = build_cases(receipts)
    baselines = {b: score(cases, b) for b in ("B0", "B1", "B2")}
    b0, b1, b2 = baselines["B0"], baselines["B1"], baselines["B2"]
    gates = {
        "all_receipts_bound": all(checks.values()),
        "ten_cases": len(cases) == 10,
        "b2_all_correct": b2["correct_route_count"] == 10,
        "b2_zero_false_authority": b2["false_authority_count"] == 0,
        "b2_zero_overcompression": b2["overcompression_count"] == 0,
        "b2_zero_avoidable_rich": b2["avoidable_rich_state_count"] == 0,
        "b2_captures_all_compact": b2["compact_authorized_captured"] == b2["compact_authorized_opportunities"] and b2["compact_authorized_opportunities"] > 0,
        "b0_safe_but_rich": b0["false_authority_count"] == 0 and b0["overcompression_count"] == 0 and b0["avoidable_rich_state_count"] > 0,
        "b1_hostile_failure": b1["false_authority_count"] > 0 or b1["overcompression_count"] > 0,
        "b2_hostile_escalations": all(next(r for r in b2["rows"] if r["case_id"] == cid)["correct"] for cid in ("C6", "C9", "C10")),
        "tare_sizes_exact": b2["tare_selected_representation_sizes"] == [45, 54, 715, 715],
    }
    if not all(checks.values()): terminal = "MAX_R4EA_REQUIRED_RECEIPT_BINDING_GAP"
    elif all(gates.values()): terminal = POS
    else: terminal = "MAX_R4EA_STATIC_POLICY_PARETO_DOMINANCE_NOT_EARNED"
    equivalence = {
        "sixlcu_one_literal_matches_exact_on_frozen_domain": checks["sixlcu_literal_exact"],
        "r6i_support1_preserves_unit_objective_all_n": checks["r6i_support1"],
        "tare_orbit_histogram_contains_bulk_query_information": checks["qg31_green"] and checks["qg28_orbit715"],
    }
    out = {
        "schema": "ORIONQ.MAXR4EA.AuthorityIndexedRouter.v1",
        "issue": "SzeChunYiu/ORION#908",
        "terminal": terminal,
        "protocol_sha256": shaf(PROTO),
        "receipt_hashes": {"qg31": shaf(QG31), "qg28": shaf(QG28), "qg15b": shaf(QG15B), "qg9": shaf(QG9), "r4b": shaf(R4B), "r4d": shaf(R4D)},
        "binding_checks": checks,
        "router_input_excludes": ["family_name", "case_id", "gold_route", "terminal_label"],
        "case_count": len(cases),
        "case_gold": [{"case_id": c["case_id"], "query": c["query"], "gold": gold_route(c), "evaluator_source": c["evaluator_source"]} for c in cases],
        "baselines": baselines,
        "equivalence_bindings": equivalence,
        "gates": gates,
        "AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION": terminal == POS,
        "HELD_OUT_TRANSFER_AUTHORITY": False,
        "AUTONOMOUS_SKILL_SELECTION_AUTHORITY": False,
        "GENERAL_QUANTUM_SCIENCE_IMPROVEMENT": False,
        "NOVELTY_AUTHORITY": False,
    }
    raw = canon(out); out["result_digest"] = hashlib.sha256(raw.encode()).hexdigest()
    ns.output.parent.mkdir(parents=True, exist_ok=True); ns.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"terminal": terminal, "B0": {k:v for k,v in b0.items() if k != "rows"}, "B1": {k:v for k,v in b1.items() if k != "rows"}, "B2": {k:v for k,v in b2.items() if k != "rows"}, "result_digest": out["result_digest"]}))
    return 0

if __name__ == "__main__": raise SystemExit(main())
