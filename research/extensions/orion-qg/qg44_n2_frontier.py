#!/usr/bin/env python3
"""QG-23: n=2 witness frontier — genuine margin geometry vs the t_c=1 boundary.

Protocol: development/orion-qg-regime-geometry/QG44_N2_FRONTIER_PROTOCOL_V1.md
(registered before this outcome run). Successor to QG43 (whose receipt this
run binds via gate G7). Scientifically independent of the benchmark
instruments: imports only scientific/runtime modules, compares the
unrestricted weighted R6M DP with the exact support-<=2 D++ family.

Exit 0 = complete (terminal in json); exit 3 = consistency failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg2_objective_robustness as qg2  # noqa: E402

r6m = qg2.r6m
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG44_N2_FRONTIER_PROTOCOL_V1.md"
QG2_PATH = QG_DIR / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json"
QG43_PATH = QG_DIR / "QG43_CONE_EXACTNESS_RESULTS.json"
DEFAULT_OUTPUT = QG_DIR / "QG44_N2_FRONTIER_RESULTS.json"
SEED = 20260903
RANDOM_N2 = 600
WITNESS_CAP_PER_OB = 12
WITNESS_CAP_JSON = 20
BRUTE_FIXED_INSTANCES = 12


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anti_instrument_import_gate() -> dict[str, Any]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = [n for n in imported if "q3_replacement" in n.lower() or "dual_instrument" in n.lower()]
    return {"imports": sorted(set(imported)), "forbidden_imports": forbidden, "pass": not forbidden}


# ---- objective grid ----------------------------------------------------------

def ob_name(t_r: int, dc: int, dnc: int) -> str:
    return f"Q44G_tr{t_r}_dc{dc}_dnc{dnc}_tag2"


def build_grid() -> list[qg2.Objective]:
    grid: list[qg2.Objective] = []
    # H_main (t_r=2): witness-mass comparators (dc=-3 -> t_c=1), the
    # witness-free column (dc=-2 -> t_c=2), shallow controls (dc=-1).
    for dc in (-3, -2, -1):
        for dnc in (0, 1):
            grid.append(qg2.Objective(ob_name(2, dc, dnc), 4 + dnc, 4 + dc, 2, 2, 0))
    # H_scale: same margins with the absolute central cost lifted off 1.
    for dc, dnc in ((-3, 0), (-3, 1), (-2, 0)):
        for t_r in (3, 4):
            grid.append(qg2.Objective(ob_name(t_r, dc, dnc),
                                      2 * t_r + dnc, 2 * t_r + dc, 2, t_r, 0))
    grid.append(qg2.Objective("Q44G_O1ANCHOR", 7, 1, 4, 3, 0))  # exact frozen QG2 O1
    return grid


def margins(ob: qg2.Objective) -> tuple[int, int]:
    return ob.t_c - 2 * ob.t_r, ob.t_nc - 2 * ob.t_r


# ---- instance panels ---------------------------------------------------------

LETTERS = ((1, 0), (1, 1), (0, 1))


def exhaustive_letter_n2() -> list[tuple]:
    # QG43's n=1 letters embedded at width 2: 3^6 = 729 ordered instances.
    return [
        tuple(((a, b), (c, d), (e, f)))
        for a, b, c, d, e, f in itertools.product(LETTERS, repeat=6)
    ]


def exhaustive_letter_n1() -> list[tuple]:
    return [
        tuple(((a, b), (c, d), (e, f)))
        for a, b, c, d, e, f in itertools.product(LETTERS, repeat=6)
    ]


def hostile_panels() -> list[tuple[str, int, tuple]]:
    out = []
    for name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
        tp = tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in letter_pairs)
        out.append((f"HOSTILE_N1:{name}", 1, tp))
    for name, raw in sorted(r6m._HOSTILE_N2_PANELS.items()):
        tp = tuple((tuple(a), tuple(b)) for a, b in raw)
        out.append((f"HOSTILE_N2:{name}", 2, tp))
    return out


def qg2_o1_witness_instances() -> list[tuple[str, int, tuple]]:
    raw = json.loads(QG2_PATH.read_text(encoding="utf-8"))
    rows: list[tuple[tuple, dict]] = []
    walk_collect(raw, rows)
    out = []
    for path, row in rows:
        targets = tuple((int(t[0]), int(t[1])) for t in row["targets"])
        tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
        out.append((f"QG2_O1_WITNESS:{path}", int(row["n"]), tp))
    return out


def walk_collect(o: Any, rows: list, path: tuple = ()) -> None:
    if isinstance(o, dict):
        if o.get("C_DP") == 11 and o.get("C_Dxx") == 13 and "targets" in o:
            rows.append(("/".join(map(str, path[-2:])), o))
        for k, v in o.items():
            walk_collect(v, rows, (*path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk_collect(v, rows, (*path, i))


def qg43_witness_instances() -> tuple[list[tuple[str, int, tuple]], dict[str, Any]]:
    raw = json.loads(QG43_PATH.read_text(encoding="utf-8"))
    out = []
    for i, w in enumerate(raw.get("witness_rows", [])):
        targets = tuple((int(t[0]), int(t[1])) for t in w["targets"])
        tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
        out.append((f"QG43_WITNESS:{i}:{w['instance']}", int(w["n"]), tp))
    receipt = {
        "sha256": sha256_file(QG43_PATH),
        "terminal": raw.get("terminal"),
        "n_witness_rows": len(raw.get("witness_rows", [])),
    }
    return out, receipt


def random_n2_panels() -> list[tuple[str, int, tuple]]:
    # QG43's generator verbatim (seed differs, per protocol).
    rng = np.random.default_rng(SEED)
    out = []
    for i in range(RANDOM_N2):
        targets = []
        for _ in range(6):
            while True:
                x = int(rng.integers(0, 2**2))
                z = int(rng.integers(0, 2**2))
                if (x, z) != (0, 0):
                    break
            targets.append((x, z))
        tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
        out.append((f"RANDOM_n2:{i}", 2, tp))
    return out


# ---- evaluation ---------------------------------------------------------------

def evaluate(name: str, n: int, tp: tuple, ob: qg2.Objective) -> dict[str, Any]:
    c_dp = qg2.dp_cost_pairs_ob(tp, n, ob)
    c_dxx = qg2.dxx_cost_ob(tp, n, ob)
    if c_dp > c_dxx:
        raise AssertionError({"unrestricted_exceeds_dxx": [name, n, ob.name, c_dp, c_dxx]})
    row: dict[str, Any] = {
        "instance": name,
        "n": n,
        "C_DP": int(c_dp),
        "C_Dxx": int(c_dxx),
        "gap": int(c_dp - c_dxx),
        "support3_required": bool(c_dp < c_dxx),
    }
    if c_dp < c_dxx:
        w = qg2.dp_witness_ob(tp, n, ob)
        row["max_frame_support"] = int(w["max_frame_support"])
        row["dp_witness"] = w
    return row


def n1_brute_check(tp: tuple, ob: qg2.Objective) -> None:
    dp_global = qg2.dp_cost_pairs_ob(tp, 1, ob)
    brute_global = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            for centrals in qg2.CENTRALS8:
                value = qg2.brute_config_n1_ob(tp, perm_b, perm_c, centrals, ob)
                if value is not None and (brute_global is None or value < brute_global):
                    brute_global = value
    if brute_global != dp_global:
        raise AssertionError({"qg44_n1_brute_mismatch": [ob.name, dp_global, brute_global]})


# ---- outcome run ---------------------------------------------------------------

def run() -> dict[str, Any]:
    t_start = time.time()
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    p1 = exhaustive_letter_n2()
    p1_n1 = exhaustive_letter_n1()
    p2 = hostile_panels()
    p3_qg2 = qg2_o1_witness_instances()
    p3_qg43, qg43_receipt = qg43_witness_instances()
    p4 = random_n2_panels()
    grid = build_grid()

    per_ob: dict[str, dict[str, Any]] = {}
    witness_rows_json: list[dict[str, Any]] = []
    # every witness (instance, objective-weights, gap) seen anywhere, for Q1/Q4
    all_witnesses: list[dict[str, Any]] = []

    def scan(ob: qg2.Objective, panels: list[tuple[str, int, tuple, str]]) -> dict[str, Any]:
        qg2.clear_caches()
        agg = {"n_eval": 0, "n_gaps": 0, "min_gap": 0, "n_eval_p4": 0, "n_gaps_p4": 0}
        witnesses: list[dict[str, Any]] = []
        for name, n, tp, pclass in panels:
            row = evaluate(name, n, tp, ob)
            agg["n_eval"] += 1
            if pclass == "P4":
                agg["n_eval_p4"] += 1
            if row["support3_required"]:
                agg["n_gaps"] += 1
                if pclass == "P4":
                    agg["n_gaps_p4"] += 1
                agg["min_gap"] = min(agg["min_gap"], row["gap"])
                if row["max_frame_support"] <= 2:
                    raise AssertionError({"gap_witness_not_support3": [ob.name, name]})
                rec = {
                    "objective": ob.name,
                    "instance": name,
                    "n": n,
                    "panel": pclass,
                    "targets": [list(t) for pair in tp for t in pair],
                    "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                    "gap": row["gap"],
                    "max_frame_support": row["max_frame_support"],
                }
                all_witnesses.append(rec)
                if len(witnesses) < WITNESS_CAP_PER_OB:
                    witnesses.append(rec)
        per_ob[ob.name] = {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
            "margins": {"dc": ob.t_c - 2 * ob.t_r, "dnc": ob.t_nc - 2 * ob.t_r},
            "aggregates": agg,
            "witness_count_capped": len(witnesses),
        }
        witness_rows_json.extend(witnesses[: max(0, WITNESS_CAP_JSON - len(witness_rows_json))])
        return {"agg": agg, "witnesses": witnesses}

    p1_only = [("P1", 2, tp, "P1") for tp in p1]
    small = ([(f"P2:{name}", n, tp, "P2") for name, n, tp in p2]
             + [(f"P3QG2:{name}", n, tp, "P3") for name, n, tp in p3_qg2]
             + [(f"P3QG43:{name}", n, tp, "P3") for name, n, tp in p3_qg43])
    p4_only = [(f"P4:{name}", 2, tp, "P4") for name, _, tp in p4]

    results_by_ob: dict[str, dict[str, Any]] = {}
    for ob in grid:
        t0 = time.time()
        # P1 (exhaustive letter n=2) runs on H_main only; P4 on all non-anchor.
        is_main = ob.t_r == 2 and ob.name.startswith("Q44G_tr2_")
        is_anchor = ob.name == "Q44G_O1ANCHOR"
        panels = (p1_only if is_main else []) + small + ([] if is_anchor else p4_only)
        r = scan(ob, panels)
        results_by_ob[ob.name] = r
        dc, dnc = margins(ob)
        print(f"OB {ob.name} margins=({dc},{dnc}) t_c={ob.t_c} evals={r['agg']['n_eval']} "
              f"gaps={r['agg']['n_gaps']} p4_gaps={r['agg']['n_gaps_p4']} "
              f"min_gap={r['agg']['min_gap']} [{time.time()-t0:.1f}s]", flush=True)

    # ---- Q1: any witness at an objective with t_c >= 2 (any panel) ----
    tc_ge2_cells: dict[str, dict[str, Any]] = {}
    tc1_cells: dict[str, dict[str, Any]] = {}
    for ob in grid:
        if ob.name == "Q44G_O1ANCHOR":
            continue
        key = f"dc{margins(ob)[0]}_dnc{margins(ob)[1]}_tr{ob.t_r}_tc{ob.t_c}"
        cell = {"n_gaps": per_ob[ob.name]["aggregates"]["n_gaps"],
                "n_gaps_p4": per_ob[ob.name]["aggregates"]["n_gaps_p4"],
                "min_gap": per_ob[ob.name]["aggregates"]["min_gap"]}
        (tc_ge2_cells if ob.t_c >= 2 else tc1_cells)[key] = cell
    q1_witness_rows_tc_ge2 = [w for w in all_witnesses
                              if next(ob for ob in grid if ob.name == w["objective"]).t_c >= 2]
    q1_cells_with_witnesses = {k: v for k, v in tc_ge2_cells.items() if v["n_gaps"] > 0}
    q1_p1p3_tc_ge2 = [w for w in q1_witness_rows_tc_ge2 if w["panel"] in ("P1", "P3")]
    q1_yes = len(q1_cells_with_witnesses) >= 2 or bool(q1_p1p3_tc_ge2)

    # ---- Q3: exhaustive letter-subclass verdict at width 2 ----
    q3_verdict = {
        "subclass": "letter_alphabet_729_at_width_2",
        "cells_with_witnesses": {ob.name: per_ob[ob.name]["aggregates"]["n_gaps"]
                                 for ob in grid if ob.t_r == 2
                                 and per_ob[ob.name]["aggregates"]["n_gaps"] > 0},
    }

    # ---- Q4: continuation stability under the t_c lift (t_r ladder) ----
    qg43_by_instance: dict[str, dict[str, Any]] = {}
    for w in json.loads(QG43_PATH.read_text(encoding="utf-8")).get("witness_rows", []):
        qg43_by_instance[w["instance"]] = w
    q4_rows: list[dict[str, Any]] = []
    for name, n, tp in p3_qg43:
        base_name = name.split(":", 2)[2]
        base = qg43_by_instance.get(base_name)
        if base is None:
            continue
        # evaluate ladder directly (cheap: <= 12 objectives x <= 20 instances)
        qg2.clear_caches()
        ladder = {}
        for ob in grid:
            if ob.name == "Q44G_O1ANCHOR":
                continue
            row = evaluate(name, n, tp, ob)
            if row["support3_required"] and row["gap"] < 0:
                ladder[ob.name] = {"gap": row["gap"], "t_c": ob.t_c, "t_r": ob.t_r}
        q4_rows.append({
            "instance": base_name,
            "n": n,
            "qg43_objective": base.get("objective"),
            "qg43_gap": base.get("gap"),
            "qg44_witness_at": ladder,
        })
    print(f"Q4 continuation rows: {len(q4_rows)}", flush=True)

    # ---- G4: n=1 brute cross-check at the two most witness-bearing objectives ----
    ranked = sorted(grid, key=lambda ob: -per_ob[ob.name]["aggregates"]["n_gaps"])
    brute_obs = [ob for ob in ranked if per_ob[ob.name]["aggregates"]["n_gaps"] > 0][:2]
    if not brute_obs and len(grid) >= 2:
        brute_obs = grid[:2]
    brute_report = {"objectives": [ob.name for ob in brute_obs], "instances_checked": 0}
    for ob in brute_obs:
        checked: list[tuple] = [(f"N1LETTER:{i}", tp) for i, tp in enumerate(p1_n1[:BRUTE_FIXED_INSTANCES])]
        for w in results_by_ob[ob.name]["witnesses"]:
            if w["n"] == 1:
                tp = tuple(((w["targets"][2 * j][0], w["targets"][2 * j][1]),
                            (w["targets"][2 * j + 1][0], w["targets"][2 * j + 1][1]))
                           for j in range(3))
                checked.append((w["instance"], tp))
        for name, tp in checked:
            n1_brute_check(tp, ob)
            brute_report["instances_checked"] += 1
        print(f"BRUTE {ob.name}: {len(checked)} instances exact", flush=True)

    # ---- G6: O1-anchor replay (frozen QG2 witnesses must reproduce 11/13) ----
    o1_anchor = qg2.Objective("Q44G_O1ANCHOR", 7, 1, 4, 3, 0)
    qg2.clear_caches()
    o1_replay_ok = True
    o1_replay_rows = []
    for name, n, tp in p3_qg2:
        row = evaluate(name, n, tp, o1_anchor)
        ok = row["C_DP"] == 11 and row["C_Dxx"] == 13 and row["support3_required"]
        o1_replay_ok = o1_replay_ok and ok
        o1_replay_rows.append({"instance": name, "C_DP": row["C_DP"],
                               "C_Dxx": row["C_Dxx"], "replay_ok": ok})
    print(f"O1ANCHOR replay: {o1_replay_ok} ({len(o1_replay_rows)} rows)", flush=True)

    # ---- G7: QG43 receipt binding + round-trip ----
    qg43_roundtrip_ok = True
    qg43_wt = json.loads(QG43_PATH.read_text(encoding="utf-8"))

    def parse_qg43_name(name: str) -> tuple[int, int, int, int] | None:
        # "Q43G_tr{t_r}_dc{dc}_dnc{dnc}_tag{t_tag}" -> (t_r, dc, dnc, t_tag)
        m = re.fullmatch(r"Q43G_tr(-?\d+)_dc(-?\d+)_dnc(-?\d+)_tag(\d+)", str(name))
        if not m:
            return None
        return tuple(int(g) for g in m.groups())

    def find_ob(dc: int, dnc: int, t_r: int, t_tag: int) -> qg2.Objective | None:
        for ob in grid:
            if (margins(ob) == (dc, dnc) and ob.t_r == t_r and ob.t_tag == t_tag
                    and ob.name != "Q44G_O1ANCHOR"):
                return ob
        return None

    roundtrip_checked = 0
    for w in qg43_wt.get("witness_rows", []):
        parsed = parse_qg43_name(w.get("objective", ""))
        if parsed is None:
            continue
        t_r, dc, dnc, t_tag = parsed
        # Bind machinery to the QG43 receipt regardless of grid membership:
        # reconstruct the exact objective from the serialized name and require
        # cost equality (t_nc = 2*t_r + dnc, t_c = 2*t_r + dc).
        ob = find_ob(dc, dnc, t_r, t_tag) or qg2.Objective(
            f"QG43RT_tr{t_r}_dc{dc}_dnc{dnc}_tag{t_tag}",
            2 * t_r + dnc, 2 * t_r + dc, t_tag, t_r, 0)
        row = evaluate(w["instance"], w["n"],
                       tuple(((w["targets"][2 * j][0], w["targets"][2 * j][1]),
                              (w["targets"][2 * j + 1][0], w["targets"][2 * j + 1][1]))
                             for j in range(3)), ob)
        roundtrip_checked += 1
        if row["C_DP"] != w["C_DP"] or row["C_Dxx"] != w["C_Dxx"]:
            qg43_roundtrip_ok = False
    g7 = {
        "qg43_receipt_sha256": qg43_receipt["sha256"],
        "qg43_terminal": qg43_receipt["terminal"],
        "qg43_terminal_ok": qg43_receipt["terminal"] == "QG43_REGION_STRICTLY_CONTAINS_CONE_AT_N1",
        "qg43_witness_rows": qg43_receipt["n_witness_rows"],
        "roundtrip_rows_checked": roundtrip_checked,
        "roundtrip_ok": qg43_roundtrip_ok,
    }
    print(f"G7 QG43 binding: terminal_ok={g7['qg43_terminal_ok']} roundtrip_ok={qg43_roundtrip_ok}", flush=True)

    gates = {
        "all_unrestricted_le_dxx": True,   # enforced by hard assert in evaluate
        "witnesses_support_gt2": True,     # enforced in scan
        "n1_brute_exact": True,            # enforced by hard assert
        "o1_anchor_replay": o1_replay_ok,
        "qg43_receipt_bound": g7["qg43_terminal_ok"] and g7["roundtrip_ok"],
        "no_instrument_import": import_gate["pass"],
        "chemistry_sources_read": False,
        "protected_subject_read": False,
    }

    terminal = ("QG44_FRONTIER_IS_GEOMETRY" if q1_yes else "QG44_TC1_ARTIFACT_DOMINANT")
    if not all(v for k, v in gates.items() if k not in ("chemistry_sources_read", "protected_subject_read")):
        terminal = "QG44_CONSISTENCY_FAILURE"

    result: dict[str, Any] = {
        "schema": "ORION.QG.QG44.N2Frontier.v1",
        "base_revision": subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True).stdout.strip()[:20],
        "protocol_sha256": sha256_file(PROTOCOL),
        "grid": {ob.name: per_ob[ob.name] for ob in grid},
        "panels": {"P1_exhaustive_letter_n2": len(p1), "P2_hostile": len(p2),
                   "P3_qg2_witnesses": len(p3_qg2), "P3_qg43_witnesses": len(p3_qg43),
                   "P4_random_n2": {"n": RANDOM_N2, "seed": SEED}},
        "q1_witness_at_tc_ge2": bool(q1_witness_rows_tc_ge2),
        "q1_n_witness_rows_tc_ge2": len(q1_witness_rows_tc_ge2),
        "q1_cells_with_witnesses": q1_cells_with_witnesses,
        "cells_tc1": tc1_cells,
        "cells_tc_ge2": tc_ge2_cells,
        "q3_p1_verdict": q3_verdict,
        "q4_continuation_rows": q4_rows,
        "o1_anchor_replay_rows": o1_replay_rows,
        "g4_brute_report": brute_report,
        "g7_qg43_binding": g7,
        "witness_rows": witness_rows_json,
        "gates": gates,
        "terminal": terminal,
        "authority": "EXACT_LETTER_SUBCLASS_N2__PANEL_BOUNDED_ELSEWHERE__NO_ALL_N_CLAIM__NOT_R6",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "wall_clock_seconds": round(time.time() - t_start, 1),
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical({"terminal": result["terminal"], "digest": result["result_digest"],
                     "q1": result["q1_witness_at_tc_ge2"],
                     "q1_cells": sorted(result["q1_cells_with_witnesses"])}))
    return 0 if result["terminal"] != "QG44_CONSISTENCY_FAILURE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
