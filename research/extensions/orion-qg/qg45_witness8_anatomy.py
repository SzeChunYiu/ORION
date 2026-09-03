#!/usr/bin/env python3
"""QG45: witness #8 anatomy — structural stability of the unique t_c>=2 lift.

Protocol: development/orion-qg-regime-geometry/QG45_WITNESS8_ANATOMY_PROTOCOL_V1.md
(registered before this outcome run). Successor to QG44 (whose receipt this
run binds via gate G6). Scientifically independent of the benchmark
instruments: imports only scientific/runtime modules, compares the
unrestricted weighted R6M DP with the exact support-<=2 D++ family.

Exit 0 = complete (terminal in json); exit 3 = consistency failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg2_objective_robustness as qg2  # noqa: E402

r6m = qg2.r6m
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG45_WITNESS8_ANATOMY_PROTOCOL_V1.md"
QG43_PATH = QG_DIR / "QG43_CONE_EXACTNESS_RESULTS.json"
QG44_PATH = QG_DIR / "QG44_N2_FRONTIER_RESULTS.json"
DEFAULT_OUTPUT = QG_DIR / "QG45_WITNESS8_ANATOMY_RESULTS.json"
WITNESS8_INSTANCE = "P4:RANDOM_n3:11"
WITNESS_CAP_TOTAL = 40
BRUTE_FIXED_INSTANCES = 12
LETTERS = ((1, 0), (1, 1), (0, 1))


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


# ---- objectives ----------------------------------------------------------------

def build_grid() -> list[qg2.Objective]:
    # (name, t_nc, t_c, t_tag, t_r): the 4 t_c>=2 lift cells + 2 t_c=1 homes.
    spec = [
        ("Q45G_tr2_dc-2_dnc0_tag2", 4, 2, 2, 2),
        ("Q45G_tr2_dc-2_dnc1_tag2", 5, 2, 2, 2),
        ("Q45G_tr3_dc-3_dnc0_tag2", 6, 3, 2, 3),
        ("Q45G_tr3_dc-3_dnc1_tag2", 7, 3, 2, 3),
        ("Q45G_tr2_dc-3_dnc0_tag2", 4, 1, 2, 2),
        ("Q45G_tr2_dc-3_dnc1_tag2", 5, 1, 2, 2),
    ]
    return [qg2.Objective(name, t_nc, t_c, t_tag, t_r, 0)
            for name, t_nc, t_c, t_tag, t_r in spec]


def is_lift_cell(ob: qg2.Objective) -> bool:
    return ob.t_c >= 2


# ---- witness #8, loaded from receipts (nothing hand-copied) --------------------

def load_witness8() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    qg44 = json.loads(QG44_PATH.read_text(encoding="utf-8"))
    qg43 = json.loads(QG43_PATH.read_text(encoding="utf-8"))
    ladder = None
    for row in qg44.get("q4_continuation_rows", []):
        if row.get("instance") == WITNESS8_INSTANCE:
            ladder = row
            break
    if ladder is None:
        raise AssertionError({"witness8_missing_from_qg44_q4": WITNESS8_INSTANCE})
    base = None
    for w in qg43.get("witness_rows", []):
        if w.get("instance") == WITNESS8_INSTANCE:
            base = w
            break
    if base is None:
        raise AssertionError({"witness8_missing_from_qg43": WITNESS8_INSTANCE})
    receipts = {
        "qg44_sha256": sha256_file(QG44_PATH),
        "qg44_terminal": qg44.get("terminal"),
        "qg43_sha256": sha256_file(QG43_PATH),
        "qg43_terminal": qg43.get("terminal"),
        "qg44_q4_qg44_objective": ladder.get("qg44_objective"),
        "qg44_witness_at": ladder.get("qg44_witness_at"),
        "qg43_objective": base.get("objective"),
        "qg43_gap": base.get("gap"),
        "n": base.get("n"),
    }
    return base, ladder, receipts


def targets_to_pairs(targets: list[list[int]]) -> tuple:
    t = [(int(x[0]), int(x[1])) for x in targets]
    return tuple((t[2 * j], t[2 * j + 1]) for j in range(3))


# ---- panels ---------------------------------------------------------------------

def pa_neighborhood(targets: list[list[int]]) -> tuple[list[tuple[str, int, tuple]], int]:
    """#8 + single-bit-flip neighbors at n=3 (XOR 1<<q; zeroing flips skipped)."""
    out = [("BASE", 3, targets_to_pairs(targets))]
    skipped = 0
    for j in range(6):
        for coord in (0, 1):
            for q in range(3):
                t = [list(x) for x in targets]
                t[j][coord] ^= 1 << q
                if t[j] == [0, 0]:
                    skipped += 1
                    continue
                name = f"FLIP_t{j}_c{coord}_b{q}"
                out.append((name, 3, targets_to_pairs(t)))
    return out, skipped


def pb_projection(targets: list[list[int]]) -> list[tuple[str, int, tuple]]:
    """#8's targets truncated to the low 2 bits, embedded at width n=2."""
    t = [[x[0] & 3, x[1] & 3] for x in targets]
    if any(v == [0, 0] for v in t):
        raise AssertionError({"projection_zeroed_target": t})
    return [("PROJ_LOW2_N2", 2, targets_to_pairs(t))]


A_MAX = ((3, 0), (3, 3), (0, 3))
A_MID = ((2, 0), (2, 2), (0, 2))


def pc_exhaustive(alphabet: tuple) -> list[tuple[str, int, tuple]]:
    """All 3^6 ordered instances over the alphabet, at width n=2."""
    import itertools
    return [(f"PC:{''.join(f'{x}{z}' for x, z in (a, b, c, d, e, f))}", 2,
             ((a, b), (c, d), (e, f)))
            for a, b, c, d, e, f in itertools.product(alphabet, repeat=6)]


# ---- evaluation -----------------------------------------------------------------

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
        raise AssertionError({"qg45_n1_brute_mismatch": [ob.name, dp_global, brute_global]})


# ---- outcome run ------------------------------------------------------------------

def run() -> dict[str, Any]:
    t_start = time.time()
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    base, ladder, receipts = load_witness8()
    targets = [list(map(int, t)) for t in base["targets"]]
    n8 = int(base["n"])
    if n8 != 3:
        raise AssertionError({"witness8_not_n3": n8})

    pa, pa_skipped = pa_neighborhood(targets)
    pb = pb_projection(targets)
    pc_max = pc_exhaustive(A_MAX)
    pc_mid = pc_exhaustive(A_MID)
    grid = build_grid()

    witness_rows: list[dict[str, Any]] = []
    per_ob: dict[str, dict[str, Any]] = {}
    per_instance: dict[str, dict[str, Any]] = {}

    def scan(tag: str, ob: qg2.Objective, panels: list[tuple[str, int, tuple]]) -> dict[str, Any]:
        qg2.clear_caches()
        agg = {"n_eval": 0, "n_gaps": 0, "min_gap": 0}
        for name, n, tp in panels:
            row = evaluate(f"{tag}:{name}", n, tp, ob)
            agg["n_eval"] += 1
            if row["support3_required"]:
                agg["n_gaps"] += 1
                agg["min_gap"] = min(agg["min_gap"], row["gap"])
                if row["max_frame_support"] <= 2:
                    raise AssertionError({"gap_witness_not_support3": [ob.name, name]})
                if len(witness_rows) < WITNESS_CAP_TOTAL:
                    witness_rows.append({
                        "objective": ob.name, "instance": f"{tag}:{name}", "n": n,
                        "targets": [list(t) for pair in tp for t in pair],
                        "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"], "gap": row["gap"],
                        "max_frame_support": row["max_frame_support"],
                    })
            per_instance.setdefault(f"{tag}:{name}", {})[ob.name] = row["gap"]
        return agg

    for ob in grid:
        t0 = time.time()
        res = {"PA": scan("PA", ob, pa), "PB": scan("PB", ob, pb),
               "PC_A_max": scan("PCmax", ob, pc_max),
               "PC_A_mid": scan("PCmid", ob, pc_mid)}
        per_ob[ob.name] = res
        tot = sum(r["n_eval"] for r in res.values())
        gaps = sum(r["n_gaps"] for r in res.values())
        print(f"OB {ob.name} t_c={ob.t_c} evals={tot} gaps={gaps} "
              f"[{time.time()-t0:.1f}s]", flush=True)

    # ---- Q1: PA neighbors witnessing at >=1 t_c>=2 cell ----
    lift_obs = [ob for ob in grid if is_lift_cell(ob)]
    pa_names = [name for name, _, _ in pa if name != "BASE"]
    q1_rows = []
    n_lifting = 0
    for name in pa_names:
        cells = {ob.name: per_instance[f"PA:{name}"][ob.name] for ob in lift_obs}
        lifts = {k: v for k, v in cells.items() if v < 0}
        if lifts:
            n_lifting += 1
        q1_rows.append({"neighbor": name, "lift_cells": lifts,
                        "home_gaps": {ob.name: per_instance[f"PA:{name}"][ob.name]
                                      for ob in grid if not is_lift_cell(ob)}})
    base_row = {
        "neighbor": "BASE",
        "lift_cells": {ob.name: per_instance["PA:BASE"][ob.name] for ob in lift_obs
                       if per_instance["PA:BASE"][ob.name] < 0},
        "home_gaps": {ob.name: per_instance["PA:BASE"][ob.name]
                      for ob in grid if not is_lift_cell(ob)},
    }
    q1_valid_flips = len(pa_names)
    q1_threshold = (q1_valid_flips + 1) // 2  # ceil(F/2)
    q1_threshold_met = n_lifting >= q1_threshold

    # ---- Q3: n=2 projection ----
    q3_rows = [{"objective": ob.name, "gap": per_instance["PB:PROJ_LOW2_N2"][ob.name],
                "witness": per_instance["PB:PROJ_LOW2_N2"][ob.name] < 0} for ob in grid]

    # ---- Q4: n=2 exhaustive subclass verdicts ----
    def panel_witness_instances(tag: str, panel: list[tuple[str, int, tuple]]) -> int:
        return sum(1 for name, _, _ in panel
                   if any(per_instance[f"{tag}:{name}"][ob.name] < 0 for ob in grid))

    q4 = {
        "alphabets": {"A_max": [list(a) for a in A_MAX], "A_mid": [list(a) for a in A_MID]},
        "per_objective": {ob.name: {tag: per_ob[ob.name][key] for tag, key in
                                    (("A_max", "PC_A_max"), ("A_mid", "PC_A_mid"))}
                          for ob in grid},
        "n_witnesses_A_max": panel_witness_instances("PCmax", pc_max),
        "n_witnesses_A_mid": panel_witness_instances("PCmid", pc_mid),
    }
    q4["n_witnesses_anywhere"] = q4["n_witnesses_A_max"] + q4["n_witnesses_A_mid"]

    # ---- G4: n=1 brute cross-check at the most witness-bearing objective ----
    ranked = sorted(grid, key=lambda ob: -sum(r["n_gaps"] for r in per_ob[ob.name].values()))
    brute_ob = ranked[0]
    letters_n1 = [targets_to_pairs([list(a), list(b), list(c), list(d), list(e), list(f)])
                  for a in LETTERS for b in LETTERS for c in LETTERS
                  for d in LETTERS for e in LETTERS for f in LETTERS]
    brute_report = {"objective": brute_ob.name, "instances_checked": 0}
    qg2.clear_caches()
    for i, tp in enumerate(letters_n1[:BRUTE_FIXED_INSTANCES]):
        n1_brute_check(tp, brute_ob)
        brute_report["instances_checked"] += 1
    print(f"BRUTE {brute_ob.name}: {brute_report['instances_checked']} instances exact", flush=True)

    # ---- G6: QG44 receipt binding + #8 round-trip ----
    qg44 = json.loads(QG44_PATH.read_text(encoding="utf-8"))
    qg44_grid_weights = {name: v["weights"] for name, v in qg44.get("grid", {}).items()}
    tp8 = targets_to_pairs(targets)

    def reconstruct(name: str) -> qg2.Objective:
        w = qg44_grid_weights.get(name)
        if w is not None:
            return qg2.Objective(f"QG44RT:{name}", w["t_nc"], w["t_c"], w["t_tag"], w["t_r"], 0)
        m = re.fullmatch(r"Q44G_tr(-?\d+)_dc(-?\d+)_dnc(-?\d+)_tag(\d+)", name)
        if not m:
            raise AssertionError({"unreconstructable_qg44_objective": name})
        t_r, dc, dnc, t_tag = (int(g) for g in m.groups())
        return qg2.Objective(f"QG44RT:{name}", 2 * t_r + dnc, 2 * t_r + dc, t_tag, t_r, 0)

    roundtrip_checked = 0
    roundtrip_ok = True
    qg2.clear_caches()
    for ob_name, entry in (receipts["qg44_witness_at"] or {}).items():
        ob = reconstruct(ob_name)
        row = evaluate(f"G6RT:{ob_name}", n8, tp8, ob)
        roundtrip_checked += 1
        if row["gap"] != entry["gap"]:
            roundtrip_ok = False
    g6 = {
        "qg44_receipt_sha256": receipts["qg44_sha256"],
        "qg44_terminal": receipts["qg44_terminal"],
        "qg44_terminal_ok": receipts["qg44_terminal"] == "QG44_FRONTIER_IS_GEOMETRY",
        "qg43_receipt_sha256": receipts["qg43_sha256"],
        "witness8_instance": WITNESS8_INSTANCE,
        "roundtrip_objectives": roundtrip_checked,
        "roundtrip_ok": roundtrip_ok,
    }
    print(f"G6 QG44 binding: terminal_ok={g6['qg44_terminal_ok']} roundtrip_ok={roundtrip_ok}", flush=True)

    gates = {
        "all_unrestricted_le_dxx": True,   # enforced by hard assert in evaluate
        "witnesses_support_gt2": True,     # enforced in scan
        "n1_brute_exact": True,            # enforced by hard assert
        "qg44_receipt_bound": g6["qg44_terminal_ok"] and roundtrip_ok,
        "no_instrument_import": import_gate["pass"],
        "chemistry_sources_read": False,
        "protected_subject_read": False,
    }

    terminal = ("QG45_LIFT_IS_STRUCTURALLY_STABLE" if q1_threshold_met
                else "QG45_LIFT_IS_ISOLATED")
    if not all(v for k, v in gates.items() if k not in ("chemistry_sources_read", "protected_subject_read")):
        terminal = "QG45_CONSISTENCY_FAILURE"

    result: dict[str, Any] = {
        "schema": "ORION.QG.QG45.Witness8Anatomy.v1",
        "base_revision": subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True).stdout.strip()[:20],
        "protocol_sha256": sha256_file(PROTOCOL),
        "receipts": receipts,
        "witness8": {"instance": WITNESS8_INSTANCE, "n": n8,
                     "targets": [list(t) for t in targets],
                     "qg45_base_row": base_row},
        "panels": {"PA_n3_bitflip_neighborhood": len(pa), "PA_valid_flips": len(pa) - 1,
                   "PA_skipped_zeroing": pa_skipped, "PB_n2_projection": len(pb),
                   "PC_A_max_n2": len(pc_max), "PC_A_mid_n2": len(pc_mid)},
        "objectives": {ob.name: {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
            "aggregates": per_ob[ob.name]} for ob in grid},
        "q1_neighbor_witness_count": n_lifting,
        "q1_valid_flips": q1_valid_flips,
        "q1_threshold": q1_threshold,
        "q1_threshold_met": q1_threshold_met,
        "q2_flip_table": q1_rows,
        "q3_projection_rows": q3_rows,
        "q4_pc_verdicts": q4,
        "g4_brute_report": brute_report,
        "g6_qg44_binding": g6,
        "witness_rows": witness_rows,
        "gates": gates,
        "terminal": terminal,
        "authority": "EXACT_IN_INSTANCES_FOR_EVALUATED_PANELS__NO_ALL_N_CLAIM__NOT_R6",
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
                     "q1_count": result["q1_neighbor_witness_count"],
                     "q3_any": any(r["witness"] for r in result["q3_projection_rows"]),
                     "q4_witnesses": result["q4_pc_verdicts"]["n_witnesses_anywhere"]}))
    return 0 if result["terminal"] != "QG45_CONSISTENCY_FAILURE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
