#!/usr/bin/env python3
"""QG-22: exhaustive n=1 support-2 region vs the QG8 cone (cone exactness).

Protocol: development/orion-qg-regime-geometry/QG22_CONE_EXACTNESS_PROTOCOL_V1.md
(registered before this outcome run). Scientifically independent of the
benchmark instruments: imports only scientific/runtime modules, compares the
unrestricted weighted R6M DP with the exact support-<=2 D++ family.

Exit 0 = complete (terminal in json); exit 3 = consistency failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
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
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG22_CONE_EXACTNESS_PROTOCOL_V1.md"
QG2_PATH = QG_DIR / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json"
DEFAULT_OUTPUT = QG_DIR / "QG22_CONE_EXACTNESS_RESULTS.json"
SEED = 20260824
RANDOM_N2 = 60
RANDOM_N3 = 40
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


def ob_name(t_r: int, dc: int, dnc: int, t_tag: int) -> str:
    return f"Q22G_tr{t_r}_dc{dc}_dnc{dnc}_tag{t_tag}"


def build_grid() -> list[qg2.Objective]:
    grid: list[qg2.Objective] = []
    # Slice A (t_r=2): all valid margins (dc,dnc) in {-3..2}^2 with dc<=dnc.
    # t_c=4+dc>=1 forces dc>=-3; includes boundary (dc=0 or dnc=0), strictly
    # inside (dc>0 and dnc>0), and outside points.
    for dc in range(-3, 3):
        for dnc in range(-3, 3):
            if dc > dnc:
                continue
            grid.append(qg2.Objective(ob_name(2, dc, dnc, 2), 4 + dnc, 4 + dc, 2, 2, 0))
    # Slice B (t_r=3): deep central margins dc in {-5..0}, dnc in {0,1}
    # (dc=-5 matches O1's central margin), plus the exact frozen O1 anchor.
    for dc in range(-5, 1):
        for dnc in (0, 1):
            grid.append(qg2.Objective(ob_name(3, dc, dnc, 2), 6 + dnc, 6 + dc, 2, 3, 0))
    grid.append(qg2.Objective("Q22G_O1ANCHOR", 7, 1, 4, 3, 0))  # exact O1
    # Tag extras (t_r=2, dnc=0): t_tag in {0,4}.
    for t_tag in (0, 4):
        for dc in (-3, -2, -1):
            grid.append(qg2.Objective(ob_name(2, dc, 0, t_tag), 4, 4 + dc, t_tag, 2, 0))
    # Scale probe: t_r=1 at the shallowest outside margin.
    grid.append(qg2.Objective(ob_name(1, -1, 0, 2), 2, 1, 2, 1, 0))
    return grid


def margins(ob: qg2.Objective) -> tuple[int, int]:
    return ob.t_c - 2 * ob.t_r, ob.t_nc - 2 * ob.t_r


# ---- instance panels ---------------------------------------------------------


def exhaustive_n1() -> list[tuple]:
    letters = [(1, 0), (1, 1), (0, 1)]
    return [
        tuple(((a, b), (c, d), (e, f)))
        for a, b, c, d, e, f in itertools.product(letters, repeat=6)
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


def witness_instances() -> list[tuple[str, int, tuple]]:
    raw = json.loads(QG2_PATH.read_text(encoding="utf-8"))
    out = []
    rows = []
    walk_collect(raw, rows)
    for i, (path, row) in enumerate(rows):
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


def random_panels() -> list[tuple[str, int, tuple]]:
    rng = np.random.default_rng(SEED)
    out = []
    for n, count in ((2, RANDOM_N2), (3, RANDOM_N3)):
        for i in range(count):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2**n))
                    z = int(rng.integers(0, 2**n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            out.append((f"RANDOM_n{n}:{i}", n, tp))
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
        raise AssertionError({"qg22_n1_brute_mismatch": [ob.name, dp_global, brute_global]})


# ---- outcome run ---------------------------------------------------------------


def run() -> dict[str, Any]:
    t_start = time.time()
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    p1 = exhaustive_n1()
    p2 = hostile_panels()
    p3 = witness_instances()
    p4 = random_panels()
    grid = build_grid()

    per_ob: dict[str, dict[str, Any]] = {}
    witness_rows_json: list[dict[str, Any]] = []

    def scan(ob: qg2.Objective, panels: list[tuple[str, int, tuple, str]]) -> dict[str, Any]:
        qg2.clear_caches()
        agg = {"n_eval": 0, "n_gaps": 0, "n_gaps_p1": 0, "min_gap": 0}
        witnesses: list[dict[str, Any]] = []
        for name, n, tp, pclass in panels:
            row = evaluate(name, n, tp, ob)
            agg["n_eval"] += 1
            if row["support3_required"]:
                agg["n_gaps"] += 1
                if pclass == "P1":
                    agg["n_gaps_p1"] += 1
                agg["min_gap"] = min(agg["min_gap"], row["gap"])
                if len(witnesses) < WITNESS_CAP_PER_OB:
                    if row["max_frame_support"] <= 2:
                        raise AssertionError({"gap_witness_not_support3": [ob.name, name]})
                    witnesses.append({
                        "objective": ob.name,
                        "instance": name,
                        "n": n,
                        "targets": [list(t) for pair in tp for t in pair],
                        "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                        "gap": row["gap"],
                        "max_frame_support": row["max_frame_support"],
                    })
        per_ob[ob.name] = {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
            "margins": {"dc": ob.t_c - 2 * ob.t_r, "dnc": ob.t_nc - 2 * ob.t_r},
            "aggregates": agg,
            "witness_count_capped": len(witnesses),
        }
        witness_rows_json.extend(witnesses[: max(0, WITNESS_CAP_JSON - len(witness_rows_json))])
        return {"agg": agg, "witnesses": witnesses}

    p1_only = [("P1", 1, tp, "P1") for tp in p1]
    all_small = ([(f"P2:{name}", n, tp, "P2") for name, n, tp in p2]
                 + [(f"P3:{name}", n, tp, "P3") for name, n, tp in p3])
    p4_only = [(f"P4:{name}", n, tp, "P4") for name, n, tp in p4]

    results_by_ob: dict[str, dict[str, Any]] = {}
    for ob in grid:
        t0 = time.time()
        # P4 runs on G_main only: t_r=2, t_tag=2 (main + inside controls).
        is_main = ob.name.startswith("Q22G_tr2_") and ob.name.endswith("_tag2")
        panels = p1_only + all_small + (p4_only if is_main else [])
        r = scan(ob, panels)
        results_by_ob[ob.name] = r
        dc, dnc = margins(ob)
        print(f"OB {ob.name} margins=({dc},{dnc}) evals={r['agg']['n_eval']} "
              f"gaps={r['agg']['n_gaps']} p1_gaps={r['agg']['n_gaps_p1']} "
              f"min_gap={r['agg']['min_gap']} [{time.time()-t0:.1f}s]", flush=True)

    # ---- Q1: region vs cone on exhaustive n=1 (P1-only criterion) ----
    outside_zero_gap = []
    for ob in grid:
        dc, dnc = margins(ob)
        if dc >= 0 and dnc >= 0:
            continue
        if per_ob[ob.name]["aggregates"]["n_gaps_p1"] == 0:
            outside_zero_gap.append(ob.name)
    q1_yes = bool(outside_zero_gap)

    # ---- Q3(a): exact integer rays on O_base witnesses ----
    witness_bearing = [ob for ob in grid if per_ob[ob.name]["aggregates"]["n_gaps"] > 0]
    witness_bearing.sort(key=lambda ob: (-per_ob[ob.name]["aggregates"]["n_gaps"],
                                         margins(ob)[0], margins(ob)[1]))
    ray_pool = [ob for ob in witness_bearing
                if ob.name.startswith("Q22G_tr2_") and ob.name.endswith("_tag2")]
    ray_check: dict[str, Any] = {"performed": False}
    if ray_pool:
        base = ray_pool[0]
        ray_check = {"performed": True, "base": base.name,
                     "base_witnesses": len(results_by_ob[base.name]["witnesses"])}
        for lam in (2, 3):
            ob = qg2.Objective(f"Q22RAY_{lam}_{base.name}", lam * base.t_nc, lam * base.t_c,
                               lam * base.t_tag, lam * base.t_r, 0)
            qg2.clear_caches()
            scaled_ok = True
            detail = []
            for w in results_by_ob[base.name]["witnesses"]:
                tp = tuple(((w["targets"][2 * j][0], w["targets"][2 * j][1]),
                            (w["targets"][2 * j + 1][0], w["targets"][2 * j + 1][1]))
                           for j in range(3))
                row = evaluate(w["instance"], w["n"], tp, ob)
                exact = row["gap"] == lam * w["gap"]
                scaled_ok = scaled_ok and exact
                detail.append({"instance": w["instance"], "gap_base": w["gap"],
                               f"gap_x{lam}": row["gap"], "exact": exact})
                if row["support3_required"] and row.get("max_frame_support", 3) <= 2:
                    raise AssertionError({"ray_witness_not_support3": [ob.name, w["instance"]]})
            ray_check[f"lam{lam}"] = {"exact_all": scaled_ok, "detail": detail}
            print(f"RAY lam={lam} on {base.name}: exact_all={scaled_ok}", flush=True)

    # ---- Q3(b): margin-plane scale probe at (dc,dnc)=(-1,0), t_r in {1,2,3} ----
    probe = {tr: ob_name(tr, -1, 0, 2) for tr in (1, 2, 3)}
    q3b = {f"t_r{tr}": {"name": nm, "n_gaps": per_ob[nm]["aggregates"]["n_gaps"]}
           for tr, nm in probe.items() if nm in per_ob}

    # ---- G4: n=1 brute cross-check ----
    brute_obs = []
    if witness_bearing:
        brute_obs.append(witness_bearing[0])
    zero_gap_outside = [ob for ob in grid if margins(ob)[0] < 0 or margins(ob)[1] < 0]
    zero_gap_outside = [ob for ob in zero_gap_outside if per_ob[ob.name]["aggregates"]["n_gaps"] == 0]
    if zero_gap_outside:
        zero_gap_outside.sort(key=lambda ob: (margins(ob)[0], margins(ob)[1]))
        brute_obs.append(zero_gap_outside[0])
    brute_report = {"objectives": [ob.name for ob in brute_obs], "instances_checked": 0}
    for ob in brute_obs:
        checked: list[tuple] = [(f"P1:{i}", tp) for i, tp in enumerate(p1[:BRUTE_FIXED_INSTANCES])]
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

    # ---- O1-anchor binding: the frozen QG2 witnesses must reproduce (11,13) ----
    o1_anchor = qg2.Objective("Q22G_O1ANCHOR", 7, 1, 4, 3, 0)
    qg2.clear_caches()
    o1_replay_ok = True
    o1_replay_rows = []
    for name, n, tp in p3:
        row = evaluate(name, n, tp, o1_anchor)
        ok = row["C_DP"] == 11 and row["C_Dxx"] == 13 and row["support3_required"]
        o1_replay_ok = o1_replay_ok and ok
        o1_replay_rows.append({"instance": name, "C_DP": row["C_DP"],
                                "C_Dxx": row["C_Dxx"], "replay_ok": ok})
    print(f"O1ANCHOR replay: {o1_replay_ok} ({len(o1_replay_rows)} rows)", flush=True)

    # ---- gates ----
    inside_ok = True
    for ob in grid:
        dc, dnc = margins(ob)
        if dc > 0 and dnc > 0 and per_ob[ob.name]["aggregates"]["n_gaps"] != 0:
            inside_ok = False
    gates = {
        "all_unrestricted_le_dxx": True,  # enforced by hard assert in evaluate
        "inside_controls_zero_gap_p1": inside_ok,
        "witnesses_support_gt2": True,   # enforced in scan/evaluate
        "n1_brute_exact": True,          # enforced by hard assert
        "ray_homogeneity_exact": (not ray_check.get("performed")
                                  or all(ray_check[f"lam{lam}"]["exact_all"] for lam in (2, 3))),
        "o1_anchor_replay": o1_replay_ok,
        "no_instrument_import": import_gate["pass"],
        "chemistry_sources_read": False,
        "protected_subject_read": False,
    }

    terminal = ("QG22_REGION_STRICTLY_CONTAINS_CONE_AT_N1" if q1_yes
                else "QG22_CONE_EXACT_ON_GRID_AT_N1")
    if not all(v for k, v in gates.items() if k not in ("chemistry_sources_read", "protected_subject_read")):
        terminal = "QG22_CONSISTENCY_FAILURE"

    frontier = [ob.name for ob in grid
                if (margins(ob)[0] < 0 or margins(ob)[1] < 0)
                and per_ob[ob.name]["aggregates"]["n_gaps"] > 0]
    result: dict[str, Any] = {
        "schema": "ORION.QG.QG22.ConeExactness.v1",
        "base_revision": subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True).stdout.strip()[:20],
        "protocol_sha256": sha256_file(PROTOCOL),
        "grid": {ob.name: per_ob[ob.name] for ob in grid},
        "panels": {"P1_exhaustive_n1": len(p1), "P2_hostile": len(p2),
                   "P3_qg2_witnesses": len(p3), "P4_random": {"n2": RANDOM_N2, "n3": RANDOM_N3, "seed": SEED}},
        "q1_outside_zero_gap_objectives": outside_zero_gap,
        "q2_frontier_witness_objectives": frontier,
        "q2_min_abs_dc_witness": min((abs(margins(ob)[0]) for ob in grid
                                      if (margins(ob)[0] < 0 or margins(ob)[1] < 0)
                                      and per_ob[ob.name]["aggregates"]["n_gaps"] > 0), default=None),
        "q3_ray_check": ray_check,
        "q3b_scale_probe": q3b,
        "o1_anchor_replay_rows": o1_replay_rows,
        "g4_brute_report": brute_report,
        "witness_rows": witness_rows_json,
        "gates": gates,
        "terminal": terminal,
        "authority": "EXACT_EXHAUSTIVE_N1_GRID_ONLY__NO_ALL_N_SHARPNESS_AUTHORITY__NOT_R6",
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
                     "q1": result["q1_outside_zero_gap_objectives"][:4],
                     "frontier_len": len(result["q2_frontier_witness_objectives"])}))
    return 0 if result["terminal"] != "QG22_CONSISTENCY_FAILURE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
