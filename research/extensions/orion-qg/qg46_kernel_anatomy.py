#!/usr/bin/env python3
"""QG46: kernel anatomy — two-bit-flip closure of the 7-flip lift kernel.

Protocol: development/orion-qg-regime-geometry/QG46_KERNEL_ANATOMY_PROTOCOL_V1.md
(registered before this outcome run). Successor to QG45 (whose receipt this
run binds via gate G6; QG44/QG-43 receipts stay bound transitively). The
7-flip kernel is DERIVED from the QG45 receipt's own q2_flip_table (nothing
hand-copied). Scientifically independent of the benchmark instruments.

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
from itertools import combinations
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg2_objective_robustness as qg2  # noqa: E402

r6m = qg2.r6m
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG46_KERNEL_ANATOMY_PROTOCOL_V1.md"
QG43_PATH = QG_DIR / "QG43_CONE_EXACTNESS_RESULTS.json"
QG44_PATH = QG_DIR / "QG44_N2_FRONTIER_RESULTS.json"
QG45_PATH = QG_DIR / "QG45_WITNESS8_ANATOMY_RESULTS.json"
DEFAULT_OUTPUT = QG_DIR / "QG46_KERNEL_ANATOMY_RESULTS.json"
WITNESS8_INSTANCE = "P4:RANDOM_n3:11"
WITNESS_CAP_TOTAL = 40
BRUTE_FIXED_INSTANCES = 12
LETTERS = ((1, 0), (1, 1), (0, 1))
FLIP_POSITIONS = [(j, c, q) for j in range(6) for c in (0, 1) for q in range(3)]  # 36


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


# ---- objectives (same frozen 6-cell grid as QG45) -------------------------------

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


# ---- witness #8 + kernel, loaded from receipts (nothing hand-copied) ------------

def flip_name(p: tuple[int, int, int]) -> str:
    j, c, q = p
    return f"FLIP_t{j}_c{c}_b{q}"


def parse_flip(name: str) -> tuple[int, int, int]:
    m = re.fullmatch(r"FLIP_t(\d+)_c(\d+)_b(\d+)", name)
    if not m:
        raise AssertionError({"unparseable_flip_name": name})
    return tuple(int(g) for g in m.groups())


def load_witness8_and_kernel() -> dict[str, Any]:
    qg45 = json.loads(QG45_PATH.read_text(encoding="utf-8"))
    qg44 = json.loads(QG44_PATH.read_text(encoding="utf-8"))
    qg43 = json.loads(QG43_PATH.read_text(encoding="utf-8"))
    if qg45.get("witness8", {}).get("instance") != WITNESS8_INSTANCE:
        raise AssertionError({"qg45_receipt_instance": qg45.get("witness8", {}).get("instance")})
    if qg43.get("witness_rows") and not any(
            w.get("instance") == WITNESS8_INSTANCE for w in qg43["witness_rows"]):
        raise AssertionError({"witness8_missing_from_qg43": WITNESS8_INSTANCE})
    kernel = sorted(row["neighbor"] for row in qg45["q2_flip_table"] if row["lift_cells"])
    if len(kernel) != int(qg45["q1_neighbor_witness_count"]):
        raise AssertionError({"kernel_count_mismatch": [len(kernel),
                                                        qg45["q1_neighbor_witness_count"]]})
    return {
        "qg45": qg45, "qg44": qg44, "qg43": qg43,
        "targets": [list(map(int, t)) for t in qg45["witness8"]["targets"]],
        "n": int(qg45["witness8"]["n"]),
        "kernel": kernel,
    }


def targets_to_pairs(targets: list[list[int]]) -> tuple:
    t = [(int(x[0]), int(x[1])) for x in targets]
    return tuple((t[2 * j], t[2 * j + 1]) for j in range(3))


# ---- panel ----------------------------------------------------------------------

def pk2_panel(targets: list[list[int]], kernel: list[str]) -> tuple[list[tuple[str, int, tuple]], int, dict[str, int]]:
    """#8 + all valid two-bit-flip neighbors: unordered pairs of distinct flip
    positions out of the 36 (6 targets x 2 coords x 3 bits); a pair is skipped
    and counted iff applying both flips zeroes any target. Each valid pair is
    classed KK (both flips in the kernel) / KX (exactly one) / XX (neither)."""
    kset = set(kernel)
    out = [("BASE", 3, targets_to_pairs(targets))]
    skipped = 0
    counts = {"KK": 0, "KX": 0, "XX": 0}
    for i1, i2 in combinations(range(len(FLIP_POSITIONS)), 2):
        p1, p2 = FLIP_POSITIONS[i1], FLIP_POSITIONS[i2]
        t = [list(x) for x in targets]
        for (j, c, q) in (p1, p2):
            t[j][c] ^= 1 << q
        if any(v == [0, 0] for v in t):
            skipped += 1
            continue
        cls = "KK" if (flip_name(p1) in kset and flip_name(p2) in kset) else \
              "XX" if (flip_name(p1) not in kset and flip_name(p2) not in kset) else "KX"
        counts[cls] += 1
        out.append((f"2BIT_{flip_name(p1)}__{flip_name(p2)}", 3, targets_to_pairs(t), cls))
    return out, skipped, counts


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
        raise AssertionError({"qg46_n1_brute_mismatch": [ob.name, dp_global, brute_global]})


# ---- outcome run ------------------------------------------------------------------

def run() -> dict[str, Any]:
    t_start = time.time()
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    loaded = load_witness8_and_kernel()
    targets = loaded["targets"]
    n8 = loaded["n"]
    kernel = loaded["kernel"]
    if n8 != 3:
        raise AssertionError({"witness8_not_n3": n8})

    panel, skipped, class_counts = pk2_panel(targets, kernel)
    grid = build_grid()

    witness_rows: list[dict[str, Any]] = []
    per_ob: dict[str, dict[str, Any]] = {}
    per_instance: dict[str, dict[str, Any]] = {}
    pair_class: dict[str, str] = {name: cls for name, _, _, cls in
                                  [p if len(p) == 4 else (*p, "") for p in panel]}

    def scan(ob: qg2.Objective, panels: list[tuple]) -> dict[str, Any]:
        qg2.clear_caches()
        agg = {"n_eval": 0, "n_gaps": 0, "min_gap": 0}
        for entry in panels:
            name, n, tp = entry[0], entry[1], entry[2]
            row = evaluate(name, n, tp, ob)
            agg["n_eval"] += 1
            if row["support3_required"]:
                agg["n_gaps"] += 1
                agg["min_gap"] = min(agg["min_gap"], row["gap"])
                if row["max_frame_support"] <= 2:
                    raise AssertionError({"gap_witness_not_support3": [ob.name, name]})
                if len(witness_rows) < WITNESS_CAP_TOTAL:
                    witness_rows.append({
                        "objective": ob.name, "instance": name, "n": n,
                        "targets": [list(t) for pair in tp for t in pair],
                        "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"], "gap": row["gap"],
                        "max_frame_support": row["max_frame_support"],
                    })
            per_instance.setdefault(name, {})[ob.name] = row["gap"]
        return agg

    for ob in grid:
        t0 = time.time()
        res = {"PK2": scan(ob, panel)}
        per_ob[ob.name] = res
        print(f"OB {ob.name} t_c={ob.t_c} evals={res['PK2']['n_eval']} "
              f"gaps={res['PK2']['n_gaps']} [{time.time()-t0:.1f}s]", flush=True)

    # ---- Q1/Q2: per-pair lift classification over the 4 t_c>=2 cells ----
    lift_obs = [ob for ob in grid if is_lift_cell(ob)]
    home_obs = [ob for ob in grid if not is_lift_cell(ob)]
    pair_rows = []
    cls_lift = {"KK": 0, "KX": 0, "XX": 0}
    cls_home_both = {"KK": 0, "KX": 0, "XX": 0}
    cls_min_gap = {"KK": 0, "KX": 0, "XX": 0}
    for entry in panel:
        name = entry[0]
        if name == "BASE":
            continue
        cls = pair_class[name]
        cells = {ob.name: per_instance[name][ob.name] for ob in lift_obs}
        lifts = {k: v for k, v in cells.items() if v < 0}
        homes = {ob.name: per_instance[name][ob.name] for ob in home_obs}
        if lifts:
            cls_lift[cls] += 1
            cls_min_gap[cls] = min(cls_min_gap[cls], min(lifts.values()))
        if all(v < 0 for v in homes.values()):
            cls_home_both[cls] += 1
        pair_rows.append({"pair": name, "class": cls, "lift_cells": lifts,
                          "home_gaps": homes})
    kk_valid = class_counts["KK"]
    kk_lift = cls_lift["KK"]

    # ---- Q3: depth (min gap anywhere in the panel, lift cells and homes) ----
    q3 = {
        "min_gap_lift_cells": min((per_instance[e[0]][ob.name] for e in panel
                                   for ob in lift_obs), default=0),
        "min_gap_home_cells": min((per_instance[e[0]][ob.name] for e in panel
                                   for ob in home_obs), default=0),
        "base_gap_lift": min(per_instance["BASE"][ob.name] for ob in lift_obs),
        "base_gap_home": min(per_instance["BASE"][ob.name] for ob in home_obs),
    }

    # ---- Q4: home-cell stability ----
    q4 = {"pairs_witnessing_both_homes": {c: cls_home_both[c] for c in ("KK", "KX", "XX")},
          "valid_pairs_per_class": dict(class_counts)}

    # ---- G4: n=1 brute cross-check at the most witness-bearing objective ----
    ranked = sorted(grid, key=lambda ob: -per_ob[ob.name]["PK2"]["n_gaps"])
    brute_ob = ranked[0]
    letters_n1 = [targets_to_pairs([list(a), list(b), list(c), list(d), list(e), list(f)])
                  for a in LETTERS for b in LETTERS for c in LETTERS
                  for d in LETTERS for e in LETTERS for f in LETTERS]
    brute_report = {"objective": brute_ob.name, "instances_checked": 0}
    qg2.clear_caches()
    for tp in letters_n1[:BRUTE_FIXED_INSTANCES]:
        n1_brute_check(tp, brute_ob)
        brute_report["instances_checked"] += 1
    print(f"BRUTE {brute_ob.name}: {brute_report['instances_checked']} instances exact", flush=True)

    # ---- G6: QG45 receipt binding + full single-flip round-trip ----
    qg45 = loaded["qg45"]
    qg45_weights = {name: v["weights"] for name, v in qg45["objectives"].items()}
    tp8 = targets_to_pairs(targets)
    single_rows = [("BASE", qg45["witness8"]["qg45_base_row"])] + \
                  [(row["neighbor"], row) for row in qg45["q2_flip_table"]]
    roundtrip_checked = 0
    roundtrip_ok = True
    qg2.clear_caches()
    for name, row in single_rows:
        tp_single = tp8 if name == "BASE" else apply_single(targets, parse_flip(name))
        for ob in grid:
            # home cells are always present; a lift cell absent from
            # lift_cells means gap == 0 (G1 enforces gap <= 0 everywhere).
            if ob.name in row["home_gaps"]:
                expected = row["home_gaps"][ob.name]
            elif ob.name in row["lift_cells"]:
                expected = row["lift_cells"][ob.name]
            else:
                expected = 0
                if not is_lift_cell(ob):
                    roundtrip_ok = False
                    continue
            got = evaluate(f"G6RT:{name}", 3, tp_single, ob)["gap"]
            roundtrip_checked += 1
            if got != expected:
                roundtrip_ok = False
    g6 = {
        "qg45_receipt_sha256": sha256_file(QG45_PATH),
        "qg45_terminal": qg45.get("terminal"),
        "qg45_terminal_ok": qg45.get("terminal") == "QG45_LIFT_IS_ISOLATED",
        "qg44_receipt_sha256": sha256_file(QG44_PATH),
        "qg43_receipt_sha256": sha256_file(QG43_PATH),
        "witness8_instance": WITNESS8_INSTANCE,
        "kernel": kernel,
        "kernel_count": len(kernel),
        "roundtrip_evaluations": roundtrip_checked,
        "roundtrip_ok": roundtrip_ok,
    }
    print(f"G6 QG45 binding: terminal_ok={g6['qg45_terminal_ok']} "
          f"roundtrip={roundtrip_checked} ok={roundtrip_ok}", flush=True)

    gates = {
        "all_unrestricted_le_dxx": True,   # enforced by hard assert in evaluate
        "witnesses_support_gt2": True,     # enforced in scan
        "n1_brute_exact": True,            # enforced by hard assert
        "qg45_receipt_bound": g6["qg45_terminal_ok"] and roundtrip_ok,
        "no_instrument_import": import_gate["pass"],
        "chemistry_sources_read": False,
        "protected_subject_read": False,
    }
    gate_ok = all(v for k, v in gates.items()
                  if k not in ("chemistry_sources_read", "protected_subject_read"))

    if kk_lift == kk_valid and kk_valid > 0:
        terminal = "QG46_KERNEL_CLOSED"
    elif kk_lift > 0:
        terminal = "QG46_KERNEL_PARTIAL"
    else:
        terminal = "QG46_KERNEL_BROKEN"
    if not gate_ok:
        terminal = "QG46_CONSISTENCY_FAILURE"

    result: dict[str, Any] = {
        "schema": "ORION.QG.QG46.KernelAnatomy.v1",
        "base_revision": subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True).stdout.strip()[:20],
        "protocol_sha256": sha256_file(PROTOCOL),
        "receipts": {
            "qg45_sha256": g6["qg45_receipt_sha256"], "qg45_terminal": g6["qg45_terminal"],
            "qg44_sha256": g6["qg44_receipt_sha256"],
            "qg44_terminal": loaded["qg44"].get("terminal"),
            "qg43_sha256": g6["qg43_receipt_sha256"],
            "qg43_terminal": loaded["qg43"].get("terminal"),
        },
        "witness8": {"instance": WITNESS8_INSTANCE, "n": n8,
                     "targets": [list(t) for t in targets]},
        "kernel": kernel,
        "panels": {"PK2_two_bit_neighbors": len(panel) - 1, "PK2_skipped_zeroing": skipped,
                   "PK2_class_counts": dict(class_counts)},
        "objectives": {ob.name: {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag,
                        "t_r": ob.t_r, "rho": ob.rho},
            "aggregates": per_ob[ob.name]} for ob in grid},
        "q1_kk_closed": {"kk_valid": kk_valid, "kk_lift": kk_lift,
                         "closed": kk_lift == kk_valid},
        "q2_class_lift": {c: {"valid": class_counts[c], "lift": cls_lift[c],
                              "rate": round(cls_lift[c] / class_counts[c], 4) if class_counts[c] else None,
                              "min_gap": cls_min_gap[c]} for c in ("KK", "KX", "XX")},
        "q2_pair_table": pair_rows,
        "q3_depth": q3,
        "q4_home_stability": q4,
        "g4_brute_report": brute_report,
        "g6_qg45_binding": g6,
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


def apply_single(targets: list[list[int]], flip: tuple[int, int, int]) -> tuple:
    j, c, q = flip
    t = [list(x) for x in targets]
    t[j][c] ^= 1 << q
    if any(v == [0, 0] for v in t):
        raise AssertionError({"g6rt_single_zeroed": flip})
    return targets_to_pairs(t)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical({"terminal": result["terminal"], "digest": result["result_digest"],
                     "kk_lift": result["q1_kk_closed"]["kk_lift"],
                     "kk_valid": result["q1_kk_closed"]["kk_valid"],
                     "kx_lift": result["q2_class_lift"]["KX"]["lift"],
                     "xx_lift": result["q2_class_lift"]["XX"]["lift"],
                     "min_gap_lift": result["q3_depth"]["min_gap_lift_cells"]}))
    return 0 if result["terminal"] != "QG46_CONSISTENCY_FAILURE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
