"""QG47 driver: exhaustive full-alphabet n=2 ordered sweep (V1).

Question (registered in QG47_N2_FULL_SWEEP_PROTOCOL_V1.md): does ANY n=2
instance over the FULL letter alphabet (all 15 masks (x,z) in {0..3}^2 minus
(0,0), 15^6 = 11,393,390 ordered instances) witness (gap = C_DP - C_Dxx < 0)
at ANY of the frozen 6 objective cells of the QG45/QG46 grid? This settles
the n=2 frontier exactly (prior evidence: QG45 letter subclasses + seeded
random + hostile panels all zero; QG43 n=1 exhaustive zero; QG44/QG46 the
unique t_c>=2 lift is one n=3 instance).

Execution model (batch campaign):
  --chunk T          run task T (T in [0,1350)): one (prefix pair, objective),
                     write a part receipt; 225 prefixes x 6 objectives.
  --merge            verify all 1,350 part receipts (digests, completeness,
                     per-part probe re-evaluation), aggregate, run gates
                     G1/G4/G5/G6, write the final receipt.
  --selftest         reduced-configuration end-to-end plumbing check
                     (2 mini parts + merge + all gates) for pre-registration
                     smoke on a laptop; NOT a result.

Airtightness: ordered enumeration (itertools.product over the fixed LETTERS
order); the frame-permutation invariance verified by the committed probe
(qg47_sweep_invariance_probe.py) is NOT relied upon anywhere.

Frozen machinery imported from qg2_objective_robustness (never copied).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import qg2_objective_robustness as qg2  # noqa: E402

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
QG46_RECEIPT = HERE / "QG46_KERNEL_ANATOMY_RESULTS.json"
QG45_RECEIPT = HERE / "QG45_WITNESS8_ANATOMY_RESULTS.json"

N_BITS = 2
LETTERS: tuple[tuple[int, int], ...] = tuple(
    sorted((x, z) for x in range(1 << N_BITS) for z in range(1 << N_BITS) if (x, z) != (0, 0))
)
assert len(LETTERS) == 15
LETTERS_CANON = json.dumps([list(t) for t in LETTERS], separators=(",", ":"))
LETTERS_SHA = hashlib.sha256(LETTERS_CANON.encode()).hexdigest()

N_PREFIXES = 15 * 15            # 225 (i, j) letter-index prefix pairs
CHUNK_COMPLETIONS = 15 ** 4     # 50,625 completions per (prefix, objective)
WITNESS_CAP_PER_PART = 200      # serialized witness instances per part
PROBE_HEAD = 4                  # first completions bound into each part
SELFTEST_COMPLETIONS = 60
SELFTEST_TASKS = (0, N_PREFIXES * 6 - 1)  # first (ob0) and last (ob5) tasks

# Fixed n=1 letter instances for the G4 brute cross-check (as QG43-QG46):
# 12 sextuples over the 3 n=1 letters (deterministic, authored pre-run).
G4_LETTER_IDX = (
    (0, 1, 2, 0, 1, 2), (0, 1, 2, 0, 2, 1), (0, 1, 2, 1, 0, 2), (0, 1, 2, 1, 2, 0),
    (0, 1, 2, 2, 0, 1), (0, 1, 2, 2, 1, 0), (0, 0, 1, 1, 2, 2), (0, 0, 2, 2, 1, 1),
    (1, 1, 0, 0, 2, 2), (1, 1, 2, 2, 0, 0), (2, 2, 0, 0, 1, 1), (2, 2, 1, 1, 0, 0),
)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_of(obj: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


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


def load_grid() -> tuple[list[qg2.Objective], dict[str, Any], dict[str, Any]]:
    """Frozen 6-cell grid, LOADED from the QG46 receipt (weights verbatim)."""
    rec46 = json.loads(QG46_RECEIPT.read_text(encoding="utf-8"))
    rec45 = json.loads(QG45_RECEIPT.read_text(encoding="utf-8"))
    objs = []
    for name in sorted(rec46["objectives"].keys()):
        w = rec46["objectives"][name]["weights"]
        objs.append(qg2.Objective(name, w["t_nc"], w["t_c"], w["t_tag"], w["t_r"], w.get("rho", 0)))
    return objs, rec46, rec45


def task_decode(t: int) -> tuple[int, int, int]:
    """task id -> (ob_idx, i, j) over the sorted objective order."""
    ob_idx, rem = divmod(t, N_PREFIXES)
    i, j = divmod(rem, 15)
    return ob_idx, i, j


def make_tp(li: int, lj: int, l2: int, l3: int, l4: int, l5: int) -> tuple:
    ts = (LETTERS[li], LETTERS[lj], LETTERS[l2], LETTERS[l3], LETTERS[l4], LETTERS[l5])
    return tuple((ts[2 * k], ts[2 * k + 1]) for k in range(3))


def eval_gap(tp: tuple, n_bits: int, ob: qg2.Objective) -> int:
    c_dp = qg2.dp_cost_pairs_ob(tp, n_bits, ob)
    c_dxx = qg2.dxx_cost_ob(tp, n_bits, ob)
    if c_dp > c_dxx:
        raise AssertionError({"g1_violation": {"tp": [list(f) for f in tp], "objective": ob.name,
                                               "c_dp": c_dp, "c_dxx": c_dxx}})
    return c_dp - c_dxx


# ---- chunk execution ------------------------------------------------------------

def run_chunk(task_id: int, completions: int, parts_dir: Path, objs: list[qg2.Objective]) -> dict[str, Any]:
    ob_idx, i, j = task_decode(task_id)
    assert 0 <= ob_idx < len(objs)
    ob = objs[ob_idx]
    qg2.clear_caches()
    t0 = time.time()
    gap_hist: dict[str, int] = {}
    witnesses: list[dict[str, Any]] = []
    n_witness = 0
    truncated = False
    min_gap = 0
    probes: list[dict[str, Any]] = []
    for c, tail in enumerate(itertools.product(range(15), repeat=4)):
        if c >= completions:
            break
        tp = make_tp(i, j, *tail)
        gap = eval_gap(tp, N_BITS, ob)
        gs = str(gap)
        gap_hist[gs] = gap_hist.get(gs, 0) + 1
        if gap < min_gap:
            min_gap = gap
        if gap < 0:
            n_witness += 1
            if len(witnesses) < WITNESS_CAP_PER_PART:
                witnesses.append({"letters": [i, j, *tail], "gap": gap})
            else:
                truncated = True
        if c < PROBE_HEAD or c == completions - 1:
            probes.append({"c": c, "letters": [i, j, *tail], "gap": gap})
    wall = round(time.time() - t0, 1)
    part: dict[str, Any] = {
        "schema": "ORION.QG.QG47.SweepPart.v1",
        "task_id": task_id,
        "ob_idx": ob_idx,
        "objective": ob.name,
        "objective_weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
        "prefix": [i, j],
        "letters_sha256": LETTERS_SHA,
        "n_bits": N_BITS,
        "completions": completions,
        "instances": completions,
        "gap_histogram": dict(sorted(gap_hist.items(), key=lambda kv: int(kv[0]))),
        "min_gap": min_gap,
        "witness_count": n_witness,
        "witness_sample": witnesses,
        "witness_sample_truncated": truncated,
        "probes": probes,
        "g1_all_le_dxx": True,
        "wall_seconds": wall,
    }
    part["part_digest"] = digest_of(part)
    parts_dir.mkdir(parents=True, exist_ok=True)
    out = parts_dir / f"part_{task_id:05d}.json"
    out.write_text(json.dumps(part, sort_keys=True, indent=1), encoding="utf-8")
    return {"task_id": task_id, "objective": ob.name, "witnesses": n_witness,
            "min_gap": min_gap, "wall_s": wall, "part": out.name}


# ---- G4: independent n=1 brute cross-check --------------------------------------

def g4_brute(objs: list[qg2.Objective], ob_name: str) -> dict[str, Any]:
    ob = next(o for o in objs if o.name == ob_name)
    letters1 = sorted((x, z) for x in range(2) for z in range(2) if (x, z) != (0, 0))
    rows = []
    exact = True
    for idx in G4_LETTER_IDX:
        targets = [letters1[k] for k in idx]
        tp = tuple((targets[2 * k], targets[2 * k + 1]) for k in range(3))
        dp = qg2.dp_cost_pairs_ob(tp, 1, ob)
        bx = qg2.dxx_cost_ob(tp, 1, ob)
        brute = None
        for perm_b in (0, 1):
            for perm_c in (0, 1):
                for centrals in qg2.CENTRALS8:
                    value = qg2.brute_config_n1_ob(tp, perm_b, perm_c, centrals, ob)
                    if value is not None and (brute is None or value < brute):
                        brute = value
        ok = brute == dp
        exact = exact and ok
        rows.append({"targets": [list(t) for t in targets], "dp": dp, "dxx": bx, "brute": brute, "exact": ok})
    return {"objective": ob_name, "instances": len(rows), "all_exact": exact, "rows": rows}


# ---- G6: QG45 + QG46 receipt binding (full panel round-trips) --------------------

FLIP_POSITIONS = [(j, c, q) for j in range(6) for c in (0, 1) for q in range(3)]


def _row_gap(table_row: dict[str, Any], ob_name: str) -> int:
    """Serialized expected gap: home_gaps > lift_cells > 0 (G1: gap <= 0)."""
    if ob_name in table_row["home_gaps"]:
        return table_row["home_gaps"][ob_name]
    if ob_name in table_row["lift_cells"]:
        return table_row["lift_cells"][ob_name]
    return 0


def g6_binding(objs: list[qg2.Objective], rec46: dict[str, Any], rec45: dict[str, Any]) -> dict[str, Any]:
    w8 = rec45["witness8"]
    n3 = w8["n"]
    base_targets = [list(t) for t in w8["targets"]]

    def build(kind: str) -> list[tuple[str, list[list[int]]]]:
        # QG45/QG46 enumeration rule, mirrored exactly: XOR 1<<q per flip;
        # skip an instance iff a FINAL target letter is (0, 0). A zeroed
        # coordinate alone is legal (letters (0, z)); only the identity
        # letter is out of the alphabet.
        out: list[tuple[str, list[list[int]]]] = []
        if kind == "single":
            for (j, c, q) in FLIP_POSITIONS:
                t = [list(x) for x in base_targets]
                t[j][c] ^= 1 << q
                if t[j] == [0, 0]:
                    continue
                out.append((f"FLIP_t{j}_c{c}_b{q}", t))
        else:
            for p1 in range(len(FLIP_POSITIONS)):
                for p2 in range(p1 + 1, len(FLIP_POSITIONS)):
                    f1, f2 = FLIP_POSITIONS[p1], FLIP_POSITIONS[p2]
                    t = [list(x) for x in base_targets]
                    for (j, c, q) in (f1, f2):
                        t[j][c] ^= 1 << q
                    if any(v == [0, 0] for v in t):
                        continue
                    (j1, c1, q1), (j2, c2, q2) = f1, f2
                    out.append((f"2BIT_FLIP_t{j1}_c{c1}_b{q1}__FLIP_t{j2}_c{c2}_b{q2}", t))
        return out

    report: dict[str, Any] = {
        "qg45_receipt_sha256": sha256_file(QG45_RECEIPT),
        "qg45_terminal": rec45["terminal"],
        "qg45_terminal_ok": rec45["terminal"] == "QG45_LIFT_IS_ISOLATED",
        "qg46_receipt_sha256": sha256_file(QG46_RECEIPT),
        "qg46_terminal": rec46["terminal"],
        "qg46_terminal_ok": rec46["terminal"] == "QG46_KERNEL_PARTIAL",
        "chain": rec46["receipts"],
    }
    # Receipt tables first: the rebuilt panels must cover them EXACTLY.
    t45 = {r["neighbor"]: r for r in rec45["q2_flip_table"]}
    t45["BASE"] = rec45["witness8"]["qg45_base_row"]
    assert len(t45) == 36
    t46 = {r["pair"]: r for r in rec46["q2_pair_table"]}
    singles = build("single")
    pairs = build("pair")
    assert {name for name, _ in singles} == set(t45) - {"BASE"}, "qg45 single panel mismatch"
    assert {name for name, _ in pairs} == set(t46), "qg46 pair panel mismatch"
    qg2.clear_caches()
    mismatches: list[dict[str, Any]] = []
    n_eval = 0
    # QG45 single-flip panel: 36 rows (base + 35 valid singles) x 6 objectives.
    for name, targets in [("BASE", base_targets)] + singles:
        tp3 = tuple((targets[2 * k], targets[2 * k + 1]) for k in range(3))
        for ob in objs:
            gap = eval_gap(tp3, n3, ob)
            n_eval += 1
            expected = _row_gap(t45[name], ob.name)
            if gap != expected:
                mismatches.append({"panel": "qg45_single", "pair": name, "objective": ob.name,
                                   "got": gap, "expected": expected})
    # QG46 two-bit panel: 598 rows x 6 objectives (kernel classification not
    # needed for the gap round-trip).
    n46 = 0
    for name, targets in pairs:
        tp3 = tuple((targets[2 * k], targets[2 * k + 1]) for k in range(3))
        for ob in objs:
            gap = eval_gap(tp3, n3, ob)
            n_eval += 1
            n46 += 1
            expected = _row_gap(t46[name], ob.name)
            if gap != expected:
                mismatches.append({"panel": "qg46_pair", "pair": name, "objective": ob.name,
                                   "got": gap, "expected": expected})
    report.update({
        "qg45_single_rows": 36,
        "qg46_pair_rows": n46,
        "roundtrip_evaluations": n_eval,
        "roundtrip_ok": not mismatches,
        "mismatches": mismatches[:20],
    })
    return report


# ---- merge ----------------------------------------------------------------------

def merge(parts_dir: Path, output: Path, selftest: bool) -> dict[str, Any]:
    objs, rec46, rec45 = load_grid()
    n_tasks = len(objs) * N_PREFIXES
    if selftest:
        expected_tasks = set(SELFTEST_TASKS)
        exp_completions = SELFTEST_COMPLETIONS
    else:
        expected_tasks = set(range(n_tasks))
        exp_completions = CHUNK_COMPLETIONS

    per_objective: dict[str, dict[str, Any]] = {}
    for o in objs:
        per_objective[o.name] = {"instances": 0, "witnesses": 0, "min_gap": 0,
                                 "gap_histogram": {}, "wall_s": 0.0,
                                 "cell_class": "lift" if o.t_c >= 2 else "home"}
    witness_letters: dict[str, set[str]] = {o.name: set() for o in objs}
    witness_lists_complete = True
    problems: list[str] = []
    task_ids: list[int] = []
    probe_checks = probe_failures = 0

    part_files = sorted(parts_dir.glob("part_*.json"))
    if not part_files:
        problems.append("no part files found")
    for f in part_files:
        part = json.loads(f.read_text(encoding="utf-8"))
        stored = part.pop("part_digest", None)
        if digest_of(part) != stored:
            problems.append(f"digest mismatch: {f.name}")
            continue
        tid = part["task_id"]
        task_ids.append(tid)
        if part["letters_sha256"] != LETTERS_SHA:
            problems.append(f"letters sha mismatch: {f.name}")
        if part["completions"] != exp_completions:
            problems.append(f"bad completion count: {f.name}: {part['completions']}")
        ob_obj = next((o for o in objs if o.name == part["objective"]), None)
        if ob_obj is None:
            problems.append(f"unknown objective: {f.name}")
            continue
        if part["objective_weights"] != {"t_nc": ob_obj.t_nc, "t_c": ob_obj.t_c, "t_tag": ob_obj.t_tag,
                                         "t_r": ob_obj.t_r, "rho": ob_obj.rho}:
            problems.append(f"objective weights drift: {f.name}")
        po = per_objective[ob_obj.name]
        po["instances"] += part["instances"]
        po["witnesses"] += part["witness_count"]
        po["wall_s"] += part["wall_seconds"]
        if part["min_gap"] < po["min_gap"]:
            po["min_gap"] = part["min_gap"]
        for gs, cnt in part["gap_histogram"].items():
            po["gap_histogram"][gs] = po["gap_histogram"].get(gs, 0) + cnt
        if part["witness_sample_truncated"]:
            witness_lists_complete = False
        witness_letters[ob_obj.name].update(",".join(str(k) for k in w["letters"]) for w in part["witness_sample"])
        for pr in part["probes"]:  # independent re-evaluation of bound slices
            probe_checks += 1
            gap = eval_gap(make_tp(*pr["letters"]), N_BITS, ob_obj)
            if gap != pr["gap"]:
                probe_failures += 1
                problems.append(f"probe mismatch: {f.name} c={pr['c']} got {gap} expected {pr['gap']}")

    missing = sorted(expected_tasks - set(task_ids))
    if len(task_ids) != len(set(task_ids)):
        problems.append("duplicate task ids")
    if missing:
        problems.append(f"missing tasks: {len(missing)} e.g. {missing[:5]}")
    for name, po in per_objective.items():
        exp_total = sum(exp_completions for t in expected_tasks
                        if objs[task_decode(t)[0]].name == name)
        if po["instances"] != exp_total:
            problems.append(f"instance total mismatch at {name}: {po['instances']} != {exp_total}")

    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        problems.append("instrument import gate failed")

    total_witnesses = sum(po["witnesses"] for po in per_objective.values())
    unique_witness_instances = sorted({k for s in witness_letters.values() for k in s})
    by_class = {c: sum(po["witnesses"] for po in per_objective.values() if po["cell_class"] == c)
                for c in ("lift", "home")}

    gates = {
        "parts_complete": not missing and len(task_ids) == len(expected_tasks)
                          and len(task_ids) == len(set(task_ids)),
        "parts_digest_ok": not any(p.startswith("digest") for p in problems),
        "letters_sha_uniform": not any(p.startswith("letters") for p in problems),
        "probe_recheck_ok": probe_failures == 0,
        "totals_ok": not any(p.startswith("instance total") for p in problems),
        "all_unrestricted_le_dxx": True,  # hard-asserted per evaluation in eval_gap
        "no_instrument_import": import_gate["pass"],
    }
    g4 = g4_brute(objs, objs[0].name if total_witnesses == 0
                  else max(per_objective.items(), key=lambda kv: kv[1]["witnesses"])[0])
    g6 = g6_binding(objs, rec46, rec45)
    if not g4["all_exact"]:
        problems.append("g4 brute mismatch")
    if not (g6["qg45_terminal_ok"] and g6["qg46_terminal_ok"] and g6["roundtrip_ok"]):
        problems.append("g6 binding failure")

    terminal = ("QG47_CONSISTENCY_FAILURE" if problems else
                ("QG47_N2_FRONTIER_NONEMPTY" if total_witnesses > 0 else "QG47_N2_FRONTIER_EMPTY"))
    receipt: dict[str, Any] = {
        "schema": "ORION.QG.QG47.N2FullSweep.v1",
        "mode": "SELFTEST" if selftest else "FULL",
        "letters": json.loads(LETTERS_CANON),
        "letters_sha256": LETTERS_SHA,
        "grid_objectives": {o.name: {"weights": {"t_nc": o.t_nc, "t_c": o.t_c, "t_tag": o.t_tag,
                                                 "t_r": o.t_r, "rho": o.rho},
                                     "cell_class": "lift" if o.t_c >= 2 else "home"} for o in objs},
        "n_tasks_expected": len(expected_tasks),
        "n_parts_found": len(task_ids),
        "probe_recheck": {"checks": probe_checks, "failures": probe_failures},
        "q1_frontier": {
            "total_witness_evaluations": total_witnesses,
            "by_cell_class": by_class,
            "per_objective": per_objective,
            "unique_witness_instances": unique_witness_instances,
            "witness_lists_complete": witness_lists_complete,
        },
        "g4_brute_report": g4,
        "g6_binding": g6,
        "problems": problems[:40],
        "gates": gates,
        "authority": "EXHAUSTIVE_ORDERED_N2_FULL_ALPHABET_AT_FROZEN_6_CELL_GRID__EXACT__NO_ALL_N_CLAIM__NOT_R6",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "terminal": terminal,
    }
    receipt["result_digest"] = digest_of(receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, sort_keys=True, indent=1), encoding="utf-8")
    return {"terminal": receipt["terminal"], "digest": receipt["result_digest"],
            "total_witnesses": total_witnesses, "parts": len(task_ids),
            "probe_failures": probe_failures, "problems": problems[:10]}


def main() -> int:
    parser = argparse.ArgumentParser(description="QG47 exhaustive n=2 full-alphabet sweep")
    parser.add_argument("--chunk", type=int, default=None, help="task id in [0,1350)")
    parser.add_argument("--parts-dir", type=Path, default=HERE / "QG47_PARTS")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    objs, _, _ = load_grid()
    n_tasks = len(objs) * N_PREFIXES

    if args.selftest:
        tmp = args.parts_dir / "selftest"
        r1 = run_chunk(SELFTEST_TASKS[0], SELFTEST_COMPLETIONS, tmp, objs)
        r2 = run_chunk(SELFTEST_TASKS[1], SELFTEST_COMPLETIONS, tmp, objs)
        out = args.output or (tmp / "QG47_SELFTEST_RESULTS.json")
        m = merge(tmp, out, selftest=True)
        print(canonical({"selftest_parts": [r1, r2], "merge": m}))
        return 0 if not m["problems"] else 3

    if args.chunk is not None:
        assert 0 <= args.chunk < n_tasks, f"task id out of range [0,{n_tasks})"
        print(canonical(run_chunk(args.chunk, CHUNK_COMPLETIONS, args.parts_dir, objs)))
        return 0

    if args.merge:
        out = args.output or (HERE / "QG47_N2_FULL_SWEEP_RESULTS.json")
        m = merge(args.parts_dir, out, selftest=False)
        print(canonical(m))
        return 0 if m["terminal"] != "QG47_CONSISTENCY_FAILURE" else 3

    parser.error("one of --chunk / --merge / --selftest is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
