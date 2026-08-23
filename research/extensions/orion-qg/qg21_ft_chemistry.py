#!/usr/bin/env python3
"""ORION-QG lane QG-21 — real chemistry under a fault-tolerant objective.

Frozen by development/orion-qg-regime-geometry/QG21_FT_OBJECTIVE_PROTOCOL_V1.md
(sha256 recorded in the receipt; the protocol was frozen BEFORE any chemistry
outcome under any QG-21 objective was computed).

Q1  derive the cost weights from explicit fault-tolerant accounting; freeze one
    primary objective theta_FT plus a sensitivity band, bind QG-2's O1 as a
    control point only.
Q2  predict every real row's regime and exact optimal cost from the committed
    trade machinery BEFORE the exact referee is reachable (the referee is
    structurally stubbed during staging), digest-stamp the predictions to disk,
    then open the referee and compare.
Q3  serialize every referee-confirmed strictly-improved compilation verbatim.

Authority ceiling NOT_R6. No novelty credit. No physical quantum-advantage
claim. The protected stretched-N2 subject is never read (structurally guarded).
This script modifies no existing file; committed machinery is imported
unmodified.
"""
from __future__ import annotations

import builtins
import hashlib
import io
import itertools
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ORION_Q = HERE.parent / "orion-q"
for _p in (str(HERE), str(ORION_Q)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import qg2_objective_robustness as qg2  # noqa: E402  (committed, unmodified)
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6r_prospective_fresh_subject as r6r  # noqa: E402

PROTOCOL = "development/orion-qg-regime-geometry/QG21_FT_OBJECTIVE_PROTOCOL_V1.md"
REPO_ROOT = HERE.parents[2]
RESULTS_PATH = HERE / "QG21_FT_CHEMISTRY_RESULTS.json"
STAGE1_PATH = HERE / "QG21_STAGE1_PREDICTIONS.json"
PROTECTED_PATH = "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
K_EXT = 4  # frozen extension cap (protocol section 3)

Objective = qg2.Objective
# ---- frozen objective set (protocol section 2.4) ---------------------------
THETA_FT = Objective("theta_FT", 4, 2, 2, 1, 0)
S1 = Objective("S1", 4, 2, 4, 2, 0)
S2 = Objective("S2", 8, 4, 2, 1, 0)
S3 = Objective("S3", 2, 2, 2, 1, 0)
O1_CONTROL = Objective("O1_control", 7, 1, 4, 3, 0)
OBJECTIVES = (THETA_FT, S1, S2, S3, O1_CONTROL)
DEFENSIBLE = ("theta_FT", "S1", "S2", "S3")
for _ob in OBJECTIVES:
    if _ob.t_c > _ob.t_nc:
        raise AssertionError({"qg21_objective_violates_t_c_le_t_nc": _ob.name})

ROTATIONS = 9  # family-constant non-Clifford count (protocol section 2.3.2)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---- structural guard: the protected subject is never opened ---------------

_GUARD = {"open_calls_blocked": 0, "url_calls_blocked": 0}
_real_open = builtins.open
_real_urlopen = urllib.request.urlopen


def _guarded_open(file, *args, **kwargs):
    if PROTECTED_PATH in str(file):
        _GUARD["open_calls_blocked"] += 1
        raise AssertionError({"qg21_protected_subject_access_attempt": str(file)})
    return _real_open(file, *args, **kwargs)


def _guarded_urlopen(url, *args, **kwargs):
    target = url if isinstance(url, str) else getattr(url, "full_url", "")
    if PROTECTED_PATH in str(target):
        _GUARD["url_calls_blocked"] += 1
        raise AssertionError({"qg21_protected_subject_fetch_attempt": str(target)})
    return _real_urlopen(url, *args, **kwargs)


builtins.open = _guarded_open
io.open = _guarded_open
urllib.request.urlopen = _guarded_urlopen


# ---- referee custody: stage 1 has no reachable exact referee ---------------

REFEREE_NAMES = (
    "dp_cost_pairs_ob", "dp_cost_n2_ob", "dp_config_cost_ob",
    "dp_witness_ob", "dxx_cost_ob",
)
_REAL_REFEREE = {name: getattr(qg2, name) for name in REFEREE_NAMES}
_REFEREE_STATE = {"stage": "stage1", "calls_in_stage1": 0, "stub_installed": False}


def _make_stub(name):
    def _stub(*_a, **_k):
        _REFEREE_STATE["calls_in_stage1"] += 1
        raise AssertionError({"qg21_referee_called_during_stage1": name})
    return _stub


def install_referee_stub() -> None:
    for name in REFEREE_NAMES:
        setattr(qg2, name, _make_stub(name))
    _REFEREE_STATE["stub_installed"] = True


def restore_referee() -> None:
    for name, fn in _REAL_REFEREE.items():
        setattr(qg2, name, fn)
    _REFEREE_STATE["stage"] = "stage2"


# ---- family scoring (objective-independent primitives) ---------------------

def score(prim: qg2.Primitives, ob: Objective) -> dict[str, int]:
    c_r6l, c_dplus, f_b = qg2.score_families(prim, ob)
    predicted = min(c_r6l, c_dplus, f_b)
    if predicted == c_r6l:
        regime = "DONOR_EXACT"
    elif predicted == c_dplus:
        regime = "SPLIT"
    else:
        regime = "BORROW"
    return {
        "C_R6L": int(c_r6l), "C_Dplus": int(c_dplus), "f_Bprime": int(f_b),
        "predicted_optimal_cost": int(predicted),
        "predicted_regime": regime,
        "predicted_delta_vs_donor": int(c_r6l - predicted),
    }


def truth_regime(c_dp: int, c_dplus: int, c_r6l: int) -> str:
    if c_dp == c_r6l:
        return "DONOR_EXACT"
    if c_dp < c_dplus:
        return "BORROW"
    if c_dp == c_dplus < c_r6l:
        return "SPLIT"
    return "OTHER"


# ---- subject loading -------------------------------------------------------

def clear_row_caches() -> None:
    qg2.clear_caches()
    r6q._borrow_block_cache.clear()


def load_d1() -> list[dict[str, Any]]:
    out = []
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        if cfg["path"] == PROTECTED_PATH:
            raise AssertionError("qg21 protected subject appeared in D1")
        terms, six, _champ, _mi, blob = r6f._frozen_batch(cfg)
        if blob != cfg["blob"]:
            raise AssertionError({"qg21_blob_mismatch": name})
        out.append({
            "domain": "D1", "subject": name, "path": cfg["path"], "blob": blob,
            "n": int(cfg["n_qubits"]), "terms": terms,
            "six": [int(i) for i in six],
        })
    return out


def load_d2() -> list[dict[str, Any]]:
    qg3 = json.loads((HERE / "QG3_BOUNDARY_PROSPECTIVE_RESULTS.json").read_text())
    batches = qg3["track_a"]["admitted_batches"][:K_EXT]
    out = []
    for batch in batches:
        sub = batch["subject"]
        if sub["path"] == PROTECTED_PATH:
            raise AssertionError("qg21 protected subject appeared in D2")
        cfg = {k: sub[k] for k in
               ("commit", "blob", "path", "n_occ", "n_virt", "n_orb", "n_qubits")}
        res = r6r.try_admit(cfg)
        if not res.get("admitted"):
            raise AssertionError({"qg21_d2_admission_failed": sub["path"]})
        six = [int(i) for i in res["six"]]
        if six != [int(i) for i in sub["frozen_source_indices"]]:
            raise AssertionError({"qg21_d2_source_indices_mismatch": sub["path"]})
        out.append({
            "domain": "D2", "subject": sub["path"].split("/")[0] + ":" + sub["path"],
            "path": sub["path"], "blob": sub["blob"], "n": int(sub["n_qubits"]),
            "terms": res["terms"], "six": six,
            "qg3_rows": {canonical_json(r["matching"]): r for r in batch["rows"]},
        })
    return out


def receipt_baselines_d1() -> dict[str, dict[str, dict[str, int]]]:
    r6m_rec = json.loads((ORION_Q / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json").read_text())
    r6o_rec = json.loads((ORION_Q / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json").read_text())
    r6q_rec = json.loads((ORION_Q / "MAX_R6Q_REGIME_PREDICATE_RESULTS.json").read_text())
    out = {}
    for name in sorted(p10.base.SUBJECTS):
        rows = {}
        for row in r6m_rec["subjects"][name]["candidate_points"]:
            rows[canonical_json(row["matching"])] = {
                "C_DP": int(row["C_R6M"]), "C_R6L": int(row["C_R6L_same_matching"])}
        for row in r6o_rec["domains"]["chemistry"]["subjects"][name]["rows"]:
            rows[canonical_json(row["matching"])]["C_Dplus"] = int(row["C_Dplus"])
        for row in r6q_rec["panels"]["chemistry"]["rows"][name]:
            key = canonical_json(row["matching"])
            rows[key]["f_B"] = int(row["f_B"])
            if int(row["C_DP"]) != rows[key]["C_DP"]:
                raise AssertionError({"qg21_receipt_internal_disagreement": name})
        out[name] = rows
    return out


# ---- hostile D3: parameterized DP vs independent brute, every objective -----

def hostile_panels() -> dict[str, Any]:
    ok = True
    configs = 0
    per_ob = {}
    for ob in OBJECTIVES:
        ob_ok = True
        for _name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
            tp = tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b])
                       for a, b in letter_pairs)
            for perm_b, perm_c in itertools.product((0, 1), repeat=2):
                for centrals in qg2.CENTRALS8:
                    dp_v = qg2.dp_config_cost_ob(tp, perm_b, perm_c, centrals, 1, ob)
                    br_v = qg2.brute_config_n1_ob(tp, perm_b, perm_c, centrals, ob)
                    configs += 1
                    if dp_v is None or br_v is None or dp_v != br_v:
                        ob_ok = False
        for _name, tp_raw in sorted(r6m._HOSTILE_N2_PANELS.items()):
            tp = tuple((tuple(a), tuple(b)) for a, b in tp_raw)
            for perm_b, perm_c in itertools.product((0, 1), repeat=2):
                for centrals in qg2.CENTRALS8:
                    dp_v = qg2.dp_config_cost_ob(tp, perm_b, perm_c, centrals, 2, ob)
                    br_v = qg2.brute_config_n2_ob(tp, perm_b, perm_c, centrals, ob)
                    configs += 1
                    if dp_v is None or br_v is None or dp_v != br_v:
                        ob_ok = False
        per_ob[ob.name] = ob_ok
        ok = ok and ob_ok
    qg2.clear_caches()
    return {"dp_vs_brute_all_objectives": ok, "configs": configs,
            "per_objective": per_ob,
            "n1_panels": len(r6m._HOSTILE_N1_PANELS),
            "n2_panels": len(r6m._HOSTILE_N2_PANELS)}


# ---- main ------------------------------------------------------------------

def main() -> dict[str, Any]:
    t_start = time.time()
    protocol_sha = sha256_text((REPO_ROOT / PROTOCOL).read_text())

    # --- subjects -----------------------------------------------------------
    subjects = load_d1() + load_d2()
    baselines_d1 = receipt_baselines_d1()
    t_load = time.time()

    # --- stage 1: predictions with the referee structurally unavailable -----
    install_referee_stub()
    rows: list[dict[str, Any]] = []
    for sub in subjects:
        matchings = r6m.perfect_matchings(sub["six"])
        for pairs in matchings:
            key = canonical_json([list(p) for p in pairs])
            tp = tuple((sub["terms"][i][0], sub["terms"][j][0]) for i, j in pairs)
            clear_row_caches()
            prim = qg2.compute_primitives(tp, sub["n"])
            row = {
                "domain": sub["domain"], "subject": sub["subject"],
                "path": sub["path"], "blob": sub["blob"], "n_qubits": sub["n"],
                "matching": [list(p) for p in pairs],
                "target_pairs": [[list(t) for t in pair] for pair in tp],
                "primitives": {"s_star": int(prim.s_star),
                               "u_d": [int(v) for v in prim.u_d],
                               "u_p": (None if prim.u_p is None
                                       else [int(v) for v in prim.u_p])},
                "predictions": {ob.name: score(prim, ob) for ob in OBJECTIVES},
            }
            if sub["domain"] == "D1":
                row["receipt_baseline"] = baselines_d1[sub["subject"]][key]
            else:
                r = sub["qg3_rows"][key]
                row["receipt_baseline"] = {
                    "C_DP": int(r["C_DP"]), "C_R6L": int(r["C_R6L"]),
                    "C_Dplus": int(r["C_Dplus"]), "f_B": int(r["f_B"])}
            rows.append(row)
        r6o._block_cache.clear()
    stage1_payload = {
        "schema": "ORIONQG.QG21.Stage1Predictions.v1",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_sha,
        "objectives": {ob.name: {"t_nc": ob.t_nc, "t_c": ob.t_c,
                                 "t_tag": ob.t_tag, "t_r": ob.t_r}
                       for ob in OBJECTIVES},
        "rows": [{k: r[k] for k in
                  ("domain", "subject", "n_qubits", "matching", "target_pairs",
                   "primitives", "predictions")} for r in rows],
        "row_count": len(rows),
        "referee_calls_during_stage1": _REFEREE_STATE["calls_in_stage1"],
        "referee_stub_installed": _REFEREE_STATE["stub_installed"],
    }
    stage1_text = canonical_json(stage1_payload)
    stage1_digest = sha256_text(stage1_text)
    STAGE1_PATH.write_text(json.dumps(stage1_payload, indent=2, sort_keys=True) + "\n")
    print(f"ORIONQG_QG21_STAGE1_DIGEST={stage1_digest}")
    sys.stdout.flush()
    t_stage1 = time.time()

    # --- stage 2: exact referee --------------------------------------------
    restore_referee()
    hostile = hostile_panels()
    improvements: list[dict[str, Any]] = []
    for row in rows:
        tp = tuple((tuple(pair[0]), tuple(pair[1])) for pair in row["target_pairs"])
        n = row["n_qubits"]
        clear_row_caches()
        row["referee"] = {}
        for ob in OBJECTIVES:
            c_dp = int(qg2.dp_cost_pairs_ob(tp, n, ob))
            pred = row["predictions"][ob.name]
            if not (c_dp <= pred["C_Dplus"] <= pred["C_R6L"]):
                raise AssertionError({"qg21_sandwich_violated":
                                      [row["subject"], row["matching"], ob.name]})
            if pred["f_Bprime"] < qg2.INF and c_dp > pred["f_Bprime"]:
                raise AssertionError({"qg21_borrow_soundness_violated":
                                      [row["subject"], row["matching"], ob.name]})
            delta = int(pred["C_R6L"] - c_dp)
            ref = {
                "C_DP": c_dp,
                "truth_regime": truth_regime(c_dp, pred["C_Dplus"], pred["C_R6L"]),
                "delta_vs_donor": delta,
                "strict_improvement": delta > 0,
                "prediction_cost_match": c_dp == pred["predicted_optimal_cost"],
                "prediction_regime_match": None,
            }
            ref["prediction_regime_match"] = (
                ref["truth_regime"] == pred["predicted_regime"])
            if delta > 0:
                wit = qg2.dp_witness_ob(tp, n, ob)
                if int(wit["C_DP"]) != c_dp:
                    raise AssertionError({"qg21_witness_cost_disagrees":
                                          [row["subject"], ob.name]})
                improvements.append({
                    "domain": row["domain"], "subject": row["subject"],
                    "path": row["path"], "n_qubits": n,
                    "matching": row["matching"],
                    "target_pairs": row["target_pairs"],
                    "objective": ob.name,
                    "objective_weights": {"t_nc": ob.t_nc, "t_c": ob.t_c,
                                          "t_tag": ob.t_tag, "t_r": ob.t_r},
                    "objective_defensible": ob.name in DEFENSIBLE,
                    "donor_cost_C_R6L": int(pred["C_R6L"]),
                    "predicted_optimal_cost": int(pred["predicted_optimal_cost"]),
                    "referee_optimal_cost": c_dp,
                    "delta_vs_donor": delta,
                    "improved_compilation": wit,
                })
            row["referee"][ob.name] = ref
        # baseline receipt binding at theta_FT (= committed structural weights)
        base = row["receipt_baseline"]
        pred_ft = row["predictions"]["theta_FT"]
        row["baseline_binding"] = (
            row["referee"]["theta_FT"]["C_DP"] == base["C_DP"]
            and pred_ft["C_R6L"] == base["C_R6L"]
            and pred_ft["C_Dplus"] == base["C_Dplus"]
            and pred_ft["f_Bprime"] == base.get("f_B", base.get("f_Bprime"))
        )
    t_stage2 = time.time()

    # --- summaries ----------------------------------------------------------
    per_objective = {}
    for ob in OBJECTIVES:
        deltas = [r["referee"][ob.name]["delta_vs_donor"] for r in rows]
        improved = [d for d in deltas if d > 0]
        per_objective[ob.name] = {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag,
                        "t_r": ob.t_r},
            "derivable_from_ft_accounting": ob.name in DEFENSIBLE,
            "rows": len(rows),
            "donor_exact_rows": sum(
                1 for r in rows if r["referee"][ob.name]["truth_regime"] == "DONOR_EXACT"),
            "strictly_improved_rows": len(improved),
            "regime_census": {
                reg: sum(1 for r in rows if r["referee"][ob.name]["truth_regime"] == reg)
                for reg in ("DONOR_EXACT", "SPLIT", "BORROW", "OTHER")},
            "delta_max": int(max(deltas)) if deltas else 0,
            "delta_median_over_improved": (
                float(statistics.median(improved)) if improved else 0.0),
            "delta_mean_over_improved": (
                float(sum(improved) / len(improved)) if improved else 0.0),
            "donor_cost_median": float(statistics.median(
                [r["predictions"][ob.name]["C_R6L"] for r in rows])),
            "prediction_cost_match_rows": sum(
                1 for r in rows if r["referee"][ob.name]["prediction_cost_match"]),
            "prediction_regime_match_rows": sum(
                1 for r in rows if r["referee"][ob.name]["prediction_regime_match"]),
            "two_trade_identity_holds_rows": sum(
                1 for r in rows if r["referee"][ob.name]["prediction_cost_match"]),
        }

    # --- QG-2 binding (chemistry summaries over the 30 D1 rows) -------------
    qg2_rec = json.loads((HERE / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json").read_text())
    d1_rows = [r for r in rows if r["domain"] == "D1"]
    qg2_o0 = qg2_rec["baseline_control_O0"]["chemistry_summary"]
    qg2_o1 = qg2_rec["objectives"]["O1"]["panels"]["chemistry"]

    def _census(name):
        return {
            "instances": len(d1_rows),
            "donor_exact_count": sum(
                1 for r in d1_rows if r["referee"][name]["truth_regime"] == "DONOR_EXACT"),
            "regime_split_count": sum(
                1 for r in d1_rows if r["referee"][name]["truth_regime"] == "SPLIT"),
            "regime_borrow_count": sum(
                1 for r in d1_rows if r["referee"][name]["truth_regime"] == "BORROW"),
            "identity_two_trade_count": sum(
                1 for r in d1_rows if r["referee"][name]["prediction_cost_match"]),
        }

    mine_o0, mine_o1 = _census("theta_FT"), _census("O1_control")
    qg2_binding = {
        "note": ("QG-2 records chemistry as panel summaries, not per-row values; "
                 "per-row baseline binding is therefore carried by gate 3 against "
                 "the committed R6M/R6O/R6Q receipts, and QG-2 is bound here on "
                 "its published chemistry census under O0 and O1."),
        "O0_census_match": all(mine_o0[k] == int(qg2_o0[k]) for k in mine_o0),
        "O1_census_match": all(mine_o1[k] == int(qg2_o1[k]) for k in mine_o1),
        "qg2_O0_census": {k: int(qg2_o0[k]) for k in mine_o0},
        "qg2_O1_census": {k: int(qg2_o1[k]) for k in mine_o1},
        "qg21_O0_census": mine_o0,
        "qg21_O1_census": mine_o1,
        "qg2_o1_chemistry_donor_exact_count": int(
            qg2_rec["objectives"]["O1"]["chemistry_donor_exact_count"]),
        "qg21_o1_control_donor_exact_count_on_D1": mine_o1["donor_exact_count"],
    }

    # --- gates --------------------------------------------------------------
    gates = {
        "stage1_referee_calls_zero": _REFEREE_STATE["calls_in_stage1"] == 0,
        "stage1_referee_stub_installed": _REFEREE_STATE["stub_installed"],
        "stage1_digest_recomputes": sha256_text(canonical_json(
            json.loads(STAGE1_PATH.read_text()))) == stage1_digest,
        "baseline_receipt_binding_all_rows": all(r["baseline_binding"] for r in rows),
        "qg2_chemistry_census_binding_O0": qg2_binding["O0_census_match"],
        "qg2_chemistry_census_binding_O1": qg2_binding["O1_census_match"],
        "hostile_dp_vs_brute_all_objectives": hostile["dp_vs_brute_all_objectives"],
        "rotation_constant_is_nine": r6m.ROTATIONS_R6M == ROTATIONS,
        "protected_subject_never_opened": (
            _GUARD["open_calls_blocked"] == 0 and _GUARD["url_calls_blocked"] == 0),
        "protected_subject_not_in_any_domain": all(
            r["path"] != PROTECTED_PATH for r in rows),
        "domain_sizes_complete": (
            len(d1_rows) == 30 and len(rows) == 30 + 15 * K_EXT),
        "every_improvement_has_witness": all(
            imp["improved_compilation"]["cost_recomputed_ok"] for imp in improvements),
        "sandwich_and_borrow_soundness_all_rows": True,  # asserted in-loop
    }

    # --- terminal -----------------------------------------------------------
    defensible_improved = sum(
        per_objective[name]["strictly_improved_rows"] for name in DEFENSIBLE)
    if not all(gates.values()):
        terminal = "QG21_CANNOT_CHECK"
    elif defensible_improved > 0:
        terminal = "QG21_REAL_CHEMISTRY_STRICTLY_IMPROVED_UNDER_FT_OBJECTIVE"
    else:
        terminal = "QG21_NO_IMPROVEMENT__CHEMISTRY_DONOR_EXACT_UNDER_FT_OBJECTIVE"

    control_improved = per_objective["O1_control"]["strictly_improved_rows"]
    q3 = {
        "unit": ("two-qubit Clifford gates (parity entanglers and controlled-Pauli "
                 "letters), the unit in which all four cost coordinates are counted "
                 "(protocol section 2.2)"),
        "family_constant_non_clifford_backdrop": {
            "rotations_per_compilation": ROTATIONS,
            "t_gates_per_rotation_range": [30, 100],
            "implied_t_gate_backdrop_range": [30 * ROTATIONS, 100 * ROTATIONS],
            "note": ("every member of the frozen family carries exactly nine "
                     "arbitrary-angle rotations at identical angles for a fixed "
                     "matching, so the entire non-Clifford cost is invariant and "
                     "no compilation choice inside this grammar can change it"),
        },
        "defensible_objective_improved_rows": defensible_improved,
        "control_point_improved_rows": control_improved,
        "magnitude_statement": None,  # filled below
    }
    def _dist(pool):
        if not pool:
            return None
        ds = [imp["delta_vs_donor"] for imp in pool]
        cs = [imp["donor_cost_C_R6L"] for imp in pool]
        return {
            "improved_rows": len(pool),
            "delta_min": int(min(ds)), "delta_max": int(max(ds)),
            "delta_median": float(statistics.median(ds)),
            "donor_cost_median": float(statistics.median(cs)),
            "relative_median": float(statistics.median(
                [d / c for d, c in zip(ds, cs)])),
        }

    q3["per_objective_distribution"] = {
        ob.name: {"derivable_from_ft_accounting": ob.name in DEFENSIBLE,
                  "distribution": _dist([imp for imp in improvements
                                         if imp["objective"] == ob.name])}
        for ob in OBJECTIVES}
    q3["defensible_only_distribution"] = _dist(
        [imp for imp in improvements if imp["objective"] in DEFENSIBLE])
    if defensible_improved == 0 and control_improved == 0:
        q3["magnitude_statement"] = (
            "No strict improvement on any real row under any objective in the "
            "frozen set; there is no magnitude to assess.")
    else:
        pool = [imp for imp in improvements]
        deltas = [imp["delta_vs_donor"] for imp in pool]
        donor = [imp["donor_cost_C_R6L"] for imp in pool]
        q3["improvement_distribution_all_objectives"] = {
            "rows": len(pool),
            "delta_min": int(min(deltas)), "delta_max": int(max(deltas)),
            "delta_median": float(statistics.median(deltas)),
            "donor_cost_median": float(statistics.median(donor)),
            "relative_median": float(statistics.median(
                [d / c for d, c in zip(deltas, donor)])),
        }
        dd = q3["defensible_only_distribution"]
        rel = ("n/a" if dd is None else
               f"{100.0 * dd['relative_median']:.0f}% of the donor's Clifford cost")
        dmax = "0" if dd is None else str(dd["delta_max"])
        q3["magnitude_statement"] = (
            "Improvements are counted in two-qubit Clifford gates against a "
            "non-Clifford backdrop of nine arbitrary-angle rotations "
            f"(~{30 * ROTATIONS}-{100 * ROTATIONS} T gates) that no member of "
            "this grammar can change. Under the defensible objectives the "
            f"largest improvement on any real row is {dmax} two-qubit Clifford "
            f"gates, a median {rel} and well under one percent of the "
            "fault-tolerant cost of the compilation once the invariant "
            "magic-state term is counted. It is a true strict improvement and a "
            "negligible one in fault-tolerant terms; it is not a fault-tolerant "
            "cost win, and no claim about hardware or algorithmic viability "
            "follows from it.")

    runtimes = {
        "load_s": round(t_load - t_start, 1),
        "stage1_s": round(t_stage1 - t_load, 1),
        "stage2_s": round(t_stage2 - t_stage1, 1),
    }
    print(json.dumps({"qg21_runtime_seconds": runtimes}), file=sys.stderr)

    result = {
        "schema": "ORIONQG.QG21.FTChemistry.v1",
        "lane": "QG-21",
        "protocol": PROTOCOL,
        "protocol_sha256": protocol_sha,
        "terminal": terminal,
        "authority": f"ORIONQG_{terminal}__FROZEN_FT_OBJECTIVE__NOT_R6",
        "r6_authority": False,
        "novelty_credit": False,
        "novelty_authority": False,
        "donor_novelty_credit": False,
        "physical_quantum_advantage_claim": False,
        "reserved_stretched_n2_accessed": False,
        "q1_accounting": {
            "verdict": "FT_OBJECTIVE_DEFENSIBLE__T_DOMINANT_REWEIGHTING_OF_SUPPORT_COORDINATES_NOT_DERIVABLE",
            "non_clifford_operations": (
                "only the Uanti arbitrary-angle Pauli exponentials; 2m-1 = 3 per "
                "TARE-M2 block, nine per three-block compilation, one synthesized "
                "rotation each, count independent of the axis Pauli's weight"),
            "clifford_operations": (
                "frame parity ladders (2 entanglers per support unit, outer axis "
                "applied twice -> 4, central axis once -> 2), Tag and Tag-dagger "
                "(one controlled-Pauli letter per support unit, applied twice), "
                "branch-controlled Restore (one controlled-Pauli letter per unit "
                "per branch)"),
            "implied_t_cost_ratio": (
                "T cost is charged per rotation, not per support unit; within the "
                "frozen family the T term is the constant 9*kappa_T and cancels "
                "from every comparison, so the ratio of T cost between any two "
                "family members is exactly 1"),
            "theta_FT": {"t_nc": 4, "t_c": 2, "t_tag": 2, "t_r": 1,
                         "plus_family_constant": "9*kappa_T"},
            "reduction_lemma": (
                "theta_FT(x) - theta_FT(y) = c_2q * [C_(4,2,2,1)(x) - C_(4,2,2,1)(y)] "
                "for family members x, y on a fixed matching; disclosed in the "
                "protocol before the run, so the primary-objective outcome on D1 is "
                "entailed by the committed R6Q receipt rather than discovered here"),
            "qg2_O1_control_point": (
                "QG-2's O1 = (7,1,4,3) prices T per support unit of a frame branch. "
                "The frame's support buys CNOT-ladder entanglers, not T gates; the "
                "rotation count is 1 per exponential regardless of weight. O1 is "
                "therefore retained as a control point and is not derivable from "
                "fault-tolerant accounting."),
        },
        "objectives": {ob.name: {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag,
                                 "t_r": ob.t_r, "rho": ob.rho,
                                 "role": ("PRIMARY" if ob.name == "theta_FT" else
                                          "CONTROL_NOT_DEFENSIBLE"
                                          if ob.name == "O1_control" else "SENSITIVITY")}
                       for ob in OBJECTIVES},
        "domains": {
            "D1_receipted_chemistry": {
                "rows": len(d1_rows), "subjects": sorted(
                    {r["subject"] for r in d1_rows}),
                "n_qubits": sorted({r["n_qubits"] for r in d1_rows}),
                "complete": True},
            "D2_qg3_track_a_library": {
                "rows": len(rows) - len(d1_rows),
                "K_ext_frozen_cap": K_EXT,
                "subjects": [s["path"] for s in subjects if s["domain"] == "D2"],
                "n_qubits": sorted({r["n_qubits"] for r in rows
                                    if r["domain"] == "D2"}),
                "order": "frozen QG-3 track-A admitted order, first K_ext",
                "complete_within_frozen_cap": True},
            "D3_hostile": hostile,
            "total_real_rows": len(rows),
            "f_Bsecond_note": ("B'' (QG-7b weight-2-Tag hybrid) is not evaluable at "
                               "n >= 8 (option tensor ~1e8 per Tag pair); it is "
                               "NOT_EVALUATED, and since B'' can only lower the "
                               "family minimum, the staged prediction is an upper "
                               "bound on that minimum"),
        },
        "stage1": {
            "digest": stage1_digest,
            "artifact": STAGE1_PATH.name,
            "artifact_sha256": sha256_text(STAGE1_PATH.read_text()),
            "referee_calls_during_stage1": _REFEREE_STATE["calls_in_stage1"],
            "referee_stub_installed": _REFEREE_STATE["stub_installed"],
            "referee_names_stubbed": list(REFEREE_NAMES),
        },
        "per_objective_summary": per_objective,
        "qg2_binding": qg2_binding,
        "gates": gates,
        "hostile": hostile,
        "improvements": improvements,
        "improvement_count": len(improvements),
        "q3_magnitude": q3,
        "rows": rows,
        "claim_boundary": {
            "covers": ("The exact optimal compilation cost of the frozen R6M "
                       "three-block TARE-M2 shared-Tag grammar on "
                       f"{len(rows)} real DUCC chemistry matchings, under the "
                       "frozen fault-tolerant objective theta_FT, three frozen "
                       "sensitivity objectives, and QG-2's O1 control point."),
            "does_not_cover": ("Other grammars, other objectives, hardware, device "
                               "performance, algorithmic viability, or any physical "
                               "quantum-advantage claim. No novelty or R6 authority."),
            "entailment_disclosure": ("theta_FT reduces within the frozen family to "
                                      "the committed structural objective, so its "
                                      "outcome on D1 is entailed by the committed "
                                      "R6Q receipt; this was stated in the protocol "
                                      "before the run."),
        },
    }
    for row in rows:
        row.pop("receipt_baseline_key", None)
    RESULTS_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    token = {k: result[k] for k in (
        "schema", "lane", "terminal", "authority", "protocol_sha256",
        "improvement_count", "r6_authority", "novelty_credit",
        "reserved_stretched_n2_accessed")}
    token["stage1_digest"] = stage1_digest
    token["rows"] = len(rows)
    token["defensible_objective_improved_rows"] = defensible_improved
    token["control_point_improved_rows"] = control_improved
    token["gates_all_pass"] = all(gates.values())
    print(f"ORIONQG_QG21_FT_CHEMISTRY={canonical_json(token)}")
    return result


if __name__ == "__main__":
    main()
