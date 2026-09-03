"""QG48 driver: n=3 frontier prospection (V1) - R1 exact kernel slice + R2
stratified seeded uniform sampling.

Registered question (QG48_N3_FRONTIER_PROSPECTION_PROTOCOL_V1.md; design frozen
in QG47_EMPTY_FRONTIER_ATTRIBUTION_V1.md section 6): after the certified EMPTY
exhaustive n=2 frontier (QG47, 68.3M evaluations, terminal
QG47_N2_FRONTIER_EMPTY), does the dimension lever n -> 3 open a frontier of
non-negligible mass OUTSIDE the known witness8 kernel closures?

Lever hypothesis H_n: dimension opens a frontier of non-negligible mass at
n=3. Prediction: R2 finds >= 1 witness at Hamming distance >= 4 (in the
36-bit target-flip space) from witness8. Falsifier (a): R2 completes at full
size (per-cell N = R2_STREAMS x R2_INSTANCES_PER_TASK, 95% detection floor
ln(20)/N) with 0 witnesses outside the closures -> H_n falsified in favor of
"isolated measure-zero kernel at n=3". Falsifier (b): R1's depth-3 closure
contains 0 witnesses while R2 is sparse -> the kernel decays faster than the
dimension-geometry reading predicts.

Execution model (batch campaign):
  --r1-chunk T        run R1 slice task T (T in [0,6)): one objective, the
                      ordered C(36,3) three-bit-flip closure of the witness8
                      kernel base (targets that hit (0,0) are skipped).
  --r2-chunk T        run R2 sampling task T (T in [0,1350)): one
                      (objective, stream) cell stream of
                      R2_INSTANCES_PER_TASK uniform seeded instances over the
                      full 63-letter n=3 alphabet, 3-pair shape.
  --merge             verify all part receipts, aggregate, run gates
                      G1/G4/G5/G6 (G6 binds QG45+QG46+QG47), classify R2
                      witnesses by kernel distance, write the final receipt.
  --selftest          reduced-configuration end-to-end plumbing check
                      (mini R1 + R2 parts + merge + all gates) for
                      pre-registration smoke; NOT a result.
  --rate-probe N      measure realized n=3 evals/s/core on N uniform seeded
                      instances (pre-registration sizing input; NOT a result).

Airtightness: R1 enumeration is ordered (itertools.combinations over the
fixed FLIP_POSITIONS order); R2 sampling is fully determined by the
registered integer SEED and the task id (integer seed mixing, Mersenne
Twister, version-stable). Kernel distance is exact integer popcount over the
36-bit flip space.

Frozen machinery imported from qg2_objective_robustness (never copied); grid
and QG45/QG46 binding machinery reused from qg47_n2_full_sweep (never copied).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import qg2_objective_robustness as qg2  # noqa: E402
import qg47_n2_full_sweep as qg47  # noqa: E402

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
QG47_RECEIPT = HERE / "QG47_N2_FULL_SWEEP_RESULTS.json"

N_BITS = 3
LETTERS: tuple[tuple[int, int], ...] = tuple(
    sorted((x, z) for x in range(1 << N_BITS) for z in range(1 << N_BITS) if (x, z) != (0, 0))
)
assert len(LETTERS) == 63
LETTERS_CANON = json.dumps([list(t) for t in LETTERS], separators=(",", ":"))
LETTERS_SHA = hashlib.sha256(LETTERS_CANON.encode()).hexdigest()

# Registered R2 sampling parameters (protocol V1): 6 objectives x 225 streams.
R2_SEED = 20260903
R2_STREAMS = 225
R2_INSTANCES_PER_TASK = 15000  # sized by pre-registration rate probe: 8.62 evals/s/core at n=3 (2026-09-03)

R1_TASKS = 6                                   # one per objective
R2_TASKS = R2_STREAMS * 6                      # 1350
WITNESS_CAP_PER_PART = 200
PROBE_HEAD = 4
SELFTEST_R1_TRIPLES = 40
SELFTEST_R2_INSTANCES = 60
SELFTEST_R1_TASKS = (0, R1_TASKS - 1)
SELFTEST_R2_TASKS = (0, R2_TASKS - 1)

KERNEL_DEPTH = 3   # closure depth this study completes (QG45:1, QG46:2, R1:3)


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


def load_grid_and_base() -> tuple[list[qg2.Objective], dict[str, Any], dict[str, Any], list[list[int]]]:
    objs, rec46, rec45 = qg47.load_grid()
    base = [list(t) for t in rec45["witness8"]["targets"]]
    assert len(base) == 6 and all(0 <= v < 8 for t in base for v in t)
    return objs, rec46, rec45, base


def task_decode_r2(t: int) -> tuple[int, int]:
    """R2 task id -> (ob_idx, stream) over the sorted objective order."""
    ob_idx, stream = divmod(t, R2_STREAMS)
    return ob_idx, stream


def kernel_distance(base: list[list[int]], letters_idx: list[int]) -> int:
    """Exact Hamming distance (36-bit flip space) between an instance (indices
    into the 63-letter alphabet) and the witness8 kernel base."""
    d = 0
    for k, li in enumerate(letters_idx):
        x, z = LETTERS[li]
        d += bin(base[k][0] ^ x).count("1") + bin(base[k][1] ^ z).count("1")
    return d


def make_tp(letters_idx: list[int]) -> tuple:
    ts = [LETTERS[k] for k in letters_idx]
    return tuple((ts[2 * k], ts[2 * k + 1]) for k in range(3))


def eval_gap(tp: tuple, ob: qg2.Objective) -> int:
    c_dp = qg2.dp_cost_pairs_ob(tp, N_BITS, ob)
    c_dxx = qg2.dxx_cost_ob(tp, N_BITS, ob)
    if c_dp > c_dxx:
        raise AssertionError({"g1_violation": {"tp": [list(f) for f in tp], "objective": ob.name,
                                               "c_dp": c_dp, "c_dxx": c_dxx}})
    return c_dp - c_dxx


def r1_task_stream(base: list[list[int]]):
    """Ordered depth-3 closure stream: every C(36,3) triple of flip positions
    applied to the kernel base; rows whose targets hit (0,0) are skipped
    (mirrors the QG45/QG46 enumeration rule)."""
    for (f1, f2, f3) in itertools.combinations(range(len(qg47.FLIP_POSITIONS)), 3):
        t = [list(x) for x in base]
        for p in (f1, f2, f3):
            j, c, q = qg47.FLIP_POSITIONS[p]
            t[j][c] ^= 1 << q
        if any(v == [0, 0] for v in t):
            continue
        letters_idx = [LETTERS.index((v[0], v[1])) for v in t]
        yield (f1, f2, f3), letters_idx


# ---- chunk execution ------------------------------------------------------------

def run_r1_chunk(task_id: int, triples_cap: int, parts_dir: Path, objs: list[qg2.Objective],
                 base: list[list[int]]) -> dict[str, Any]:
    ob = objs[task_id]
    qg2.clear_caches()
    t0 = time.time()
    gap_hist: dict[str, int] = {}
    witnesses: list[dict[str, Any]] = []
    n_witness = 0
    truncated = False
    min_gap = 0
    probes: list[dict[str, Any]] = []
    rows = 0
    for c, ((f1, f2, f3), letters_idx) in enumerate(r1_task_stream(base)):
        if c >= triples_cap:
            break
        rows += 1
        gap = eval_gap(make_tp(letters_idx), ob)
        gs = str(gap)
        gap_hist[gs] = gap_hist.get(gs, 0) + 1
        if gap < min_gap:
            min_gap = gap
        if gap < 0:
            n_witness += 1
            if len(witnesses) < WITNESS_CAP_PER_PART:
                witnesses.append({"flips": [f1, f2, f3], "letters": letters_idx, "gap": gap})
            else:
                truncated = True
        if c < PROBE_HEAD or c == triples_cap - 1:
            probes.append({"c": c, "letters": letters_idx, "gap": gap})
    wall = round(time.time() - t0, 1)
    part: dict[str, Any] = {
        "schema": "ORION.QG.QG48.R1Part.v1",
        "arm": "R1_exact_depth3_closure",
        "task_id": task_id,
        "objective": ob.name,
        "objective_weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
        "letters_sha256": LETTERS_SHA,
        "n_bits": N_BITS,
        "triples_cap": triples_cap,
        "rows": rows,
        "instances": rows,
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
    out = parts_dir / f"r1_part_{task_id:05d}.json"
    out.write_text(json.dumps(part, sort_keys=True, indent=1), encoding="utf-8")
    return {"task_id": task_id, "objective": ob.name, "witnesses": n_witness,
            "min_gap": min_gap, "wall_s": wall, "part": out.name}


def run_r2_chunk(task_id: int, instances: int, parts_dir: Path, objs: list[qg2.Objective],
                 base: list[list[int]]) -> dict[str, Any]:
    ob_idx, stream = task_decode_r2(task_id)
    ob = objs[ob_idx]
    rng = random.Random(R2_SEED * 1000003 + task_id)
    qg2.clear_caches()
    t0 = time.time()
    gap_hist: dict[str, int] = {}
    witnesses: list[dict[str, Any]] = []
    n_witness = 0
    n_inside = 0
    truncated = False
    min_gap = 0
    probes: list[dict[str, Any]] = []
    dist_hist: dict[str, int] = {}
    for c in range(instances):
        letters_idx = [rng.randrange(63) for _ in range(6)]
        gap = eval_gap(make_tp(letters_idx), ob)
        gs = str(gap)
        gap_hist[gs] = gap_hist.get(gs, 0) + 1
        if gap < min_gap:
            min_gap = gap
        if gap < 0:
            n_witness += 1
            dist = kernel_distance(base, letters_idx)
            ds = str(dist)
            dist_hist[ds] = dist_hist.get(ds, 0) + 1
            if dist <= KERNEL_DEPTH:
                n_inside += 1
            if len(witnesses) < WITNESS_CAP_PER_PART:
                witnesses.append({"letters": letters_idx, "gap": gap, "kernel_distance": dist})
            else:
                truncated = True
        if c < PROBE_HEAD or c == instances - 1:
            probes.append({"c": c, "letters": letters_idx, "gap": gap})
    wall = round(time.time() - t0, 1)
    part: dict[str, Any] = {
        "schema": "ORION.QG.QG48.R2Part.v1",
        "arm": "R2_stratified_seeded_uniform",
        "task_id": task_id,
        "ob_idx": ob_idx,
        "stream": stream,
        "objective": ob.name,
        "objective_weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag, "t_r": ob.t_r, "rho": ob.rho},
        "letters_sha256": LETTERS_SHA,
        "n_bits": N_BITS,
        "seed": R2_SEED,
        "seed_formula": "R2_SEED * 1000003 + task_id",
        "instances": instances,
        "gap_histogram": dict(sorted(gap_hist.items(), key=lambda kv: int(kv[0]))),
        "min_gap": min_gap,
        "witness_count": n_witness,
        "witness_kernel_distance_histogram": dict(sorted(dist_hist.items(), key=lambda kv: int(kv[0]))),
        "witness_inside_closure": n_inside,
        "witness_sample": witnesses,
        "witness_sample_truncated": truncated,
        "probes": probes,
        "g1_all_le_dxx": True,
        "wall_seconds": wall,
    }
    part["part_digest"] = digest_of(part)
    parts_dir.mkdir(parents=True, exist_ok=True)
    out = parts_dir / f"r2_part_{task_id:05d}.json"
    out.write_text(json.dumps(part, sort_keys=True, indent=1), encoding="utf-8")
    return {"task_id": task_id, "objective": ob.name, "witnesses": n_witness,
            "inside": n_inside, "min_gap": min_gap, "wall_s": wall, "part": out.name}


# ---- G6: QG47 receipt binding (QG45/QG46 binding reused from qg47) ---------------

def g6_binding_qg47() -> dict[str, Any]:
    rec47 = json.loads(QG47_RECEIPT.read_text(encoding="utf-8"))
    return {
        "qg47_receipt_sha256": sha256_file(QG47_RECEIPT),
        "qg47_schema": rec47.get("schema"),
        "qg47_terminal": rec47.get("terminal"),
        "qg47_terminal_ok": rec47.get("terminal") == "QG47_N2_FRONTIER_EMPTY",
        "qg47_total_witnesses": rec47.get("q1_frontier", {}).get("total_witness_evaluations"),
        "qg47_total_witnesses_ok": rec47.get("q1_frontier", {}).get("total_witness_evaluations") == 0,
        "qg47_problems_ok": rec47.get("problems") == [],
        "qg47_authority": rec47.get("authority"),
    }


# ---- merge ----------------------------------------------------------------------

def merge(r1_dir: Path, r2_dir: Path, output: Path, selftest: bool) -> dict[str, Any]:
    objs, rec46, rec45, base = load_grid_and_base()
    exp_r1_tasks = set(SELFTEST_R1_TASKS if selftest else range(R1_TASKS))
    exp_r2_tasks = set(SELFTEST_R2_TASKS if selftest else range(R2_TASKS))
    exp_r2_instances = SELFTEST_R2_INSTANCES if selftest else R2_INSTANCES_PER_TASK

    problems: list[str] = []
    r1_agg = {"rows": 0, "witnesses": 0, "min_gap": 0, "gap_histogram": {}, "wall_s": 0.0}
    r2_agg = {"instances": 0, "witnesses": 0, "inside_closure": 0, "min_gap": 0,
              "gap_histogram": {}, "dist_histogram": {}, "wall_s": 0.0}
    per_objective: dict[str, dict[str, Any]] = {o.name: {"instances": 0, "witnesses": 0,
                                                        "r2_witnesses": 0, "min_gap": 0,
                                                        "cell_class": "lift" if o.t_c >= 2 else "home"}
                                                for o in objs}
    r1_seen: list[int] = []
    r2_seen: list[int] = []
    probe_checks = probe_failures = 0
    outside_witnesses: list[dict[str, Any]] = []

    def fold(part: dict[str, Any], arm: str, f_name: str) -> None:
        nonlocal probe_checks, probe_failures
        stored = part.pop("part_digest", None)
        if digest_of(part) != stored:
            problems.append(f"digest mismatch: {f_name}")
            return
        if part["letters_sha256"] != LETTERS_SHA:
            problems.append(f"letters sha mismatch: {f_name}")
        ob_obj = next((o for o in objs if o.name == part["objective"]), None)
        if ob_obj is None:
            problems.append(f"unknown objective: {f_name}")
            return
        if part["objective_weights"] != {"t_nc": ob_obj.t_nc, "t_c": ob_obj.t_c, "t_tag": ob_obj.t_tag,
                                         "t_r": ob_obj.t_r, "rho": ob_obj.rho}:
            problems.append(f"objective weights drift: {f_name}")
        po = per_objective[ob_obj.name]
        po["instances"] += part["instances"]
        po["witnesses"] += part["witness_count"]
        if part["min_gap"] < po["min_gap"]:
            po["min_gap"] = part["min_gap"]
        agg = r1_agg if arm == "R1" else r2_agg
        if arm == "R1":
            agg["rows"] += part["rows"]
        else:
            agg["instances"] += part["instances"]
            po["r2_witnesses"] += part["witness_count"]
            agg["inside_closure"] += sum(
                v for k, v in part["witness_kernel_distance_histogram"].items() if int(k) <= KERNEL_DEPTH)
            for k, v in part["witness_kernel_distance_histogram"].items():
                agg["dist_histogram"][k] = agg["dist_histogram"].get(k, 0) + v
        agg["witnesses"] += part["witness_count"]
        agg["wall_s"] += part["wall_seconds"]
        if part["min_gap"] < agg["min_gap"]:
            agg["min_gap"] = part["min_gap"]
        for gs, cnt in part["gap_histogram"].items():
            agg["gap_histogram"][gs] = agg["gap_histogram"].get(gs, 0) + cnt
        for pr in part["probes"]:
            probe_checks += 1
            gap = eval_gap(make_tp(pr["letters"]), ob_obj)
            if gap != pr["gap"]:
                probe_failures += 1
                problems.append(f"probe mismatch: {f_name} c={pr['c']} got {gap} expected {pr['gap']}")
        if arm == "R2":
            for w in part["witness_sample"]:
                if w["kernel_distance"] > KERNEL_DEPTH and len(outside_witnesses) < 50:
                    outside_witnesses.append({"objective": ob_obj.name, **w})

    for f in sorted(r1_dir.glob("r1_part_*.json")):
        part = json.loads(f.read_text(encoding="utf-8"))
        r1_seen.append(part["task_id"])
        if not selftest and part["triples_cap"] != 7140:
            problems.append(f"bad r1 triples cap: {f.name}: {part['triples_cap']}")
        fold(part, "R1", f.name)
    for f in sorted(r2_dir.glob("r2_part_*.json")):
        part = json.loads(f.read_text(encoding="utf-8"))
        r2_seen.append(part["task_id"])
        if part["instances"] != exp_r2_instances:
            problems.append(f"bad r2 instance count: {f.name}: {part['instances']}")
        if part["seed"] != R2_SEED:
            problems.append(f"seed drift: {f.name}")
        fold(part, "R2", f.name)

    for label, seen, expected in (("r1", r1_seen, exp_r1_tasks), ("r2", r2_seen, exp_r2_tasks)):
        if len(seen) != len(set(seen)):
            problems.append(f"duplicate {label} task ids")
        missing = sorted(expected - set(seen))
        if missing:
            problems.append(f"missing {label} tasks: {len(missing)} e.g. {missing[:5]}")
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        problems.append("instrument import gate failed")

    n_outside = r2_agg["witnesses"] - r2_agg["inside_closure"]
    g4 = qg47.g4_brute(objs, objs[0].name if r2_agg["witnesses"] == 0
                       else max(per_objective.items(), key=lambda kv: kv[1]["r2_witnesses"])[0])
    g6_4546 = qg47.g6_binding(objs, rec46, rec45)
    g6_47 = g6_binding_qg47()
    if not g4["all_exact"]:
        problems.append("g4 brute mismatch")
    if not (g6_4546["qg45_terminal_ok"] and g6_4546["qg46_terminal_ok"] and g6_4546["roundtrip_ok"]):
        problems.append("g6 qg45/qg46 binding failure")
    if not (g6_47["qg47_terminal_ok"] and g6_47["qg47_total_witnesses_ok"] and g6_47["qg47_problems_ok"]):
        problems.append("g6 qg47 binding failure")

    gates = {
        "parts_complete": (set(r1_seen) == set(exp_r1_tasks) and set(r2_seen) == set(exp_r2_tasks)
                           and len(r1_seen) == len(set(r1_seen)) and len(r2_seen) == len(set(r2_seen))),
        "parts_digest_ok": not any(p.startswith("digest") for p in problems),
        "letters_sha_uniform": not any(p.startswith("letters") for p in problems),
        "probe_recheck_ok": probe_failures == 0,
        "counts_ok": not any(p.startswith(("bad r1", "bad r2", "seed")) for p in problems),
        "all_unrestricted_le_dxx": True,  # hard-asserted per evaluation in eval_gap
        "no_instrument_import": import_gate["pass"],
        "g4_brute_exact": g4["all_exact"],
        "g6_receipt_chain": (g6_4546["roundtrip_ok"] and g6_47["qg47_terminal_ok"]
                             and g6_47["qg47_total_witnesses_ok"]),
    }

    per_cell_n = R2_STREAMS * exp_r2_instances
    detection_floor_95 = 2.995732273553991 / per_cell_n  # ln(20)/N
    terminal = ("QG48_CONSISTENCY_FAILURE" if problems else
                ("QG48_N3_FRONTIER_WITNESSED" if n_outside > 0 else "QG48_N3_FRONTIER_ISOLATED"))
    receipt: dict[str, Any] = {
        "schema": "ORION.QG.QG48.N3FrontierProspection.v1",
        "mode": "SELFTEST" if selftest else "FULL",
        "letters": json.loads(LETTERS_CANON),
        "letters_sha256": LETTERS_SHA,
        "grid_objectives": {o.name: {"weights": {"t_nc": o.t_nc, "t_c": o.t_c, "t_tag": o.t_tag,
                                                 "t_r": o.t_r, "rho": o.rho},
                                     "cell_class": "lift" if o.t_c >= 2 else "home"} for o in objs},
        "kernel_base": base,
        "kernel_depth_completed": KERNEL_DEPTH,
        "r1_exact_closure": r1_agg,
        "r2_sampled_frontier": {
            **r2_agg,
            "seed": R2_SEED,
            "seed_formula": "R2_SEED * 1000003 + task_id",
            "streams_per_cell": R2_STREAMS,
            "instances_per_task": exp_r2_instances,
            "per_cell_n": per_cell_n,
            "detection_floor_95": detection_floor_95,
            "witnesses_outside_closure": n_outside,
            "outside_witness_sample": outside_witnesses,
        },
        "per_objective": per_objective,
        "probe_recheck": {"checks": probe_checks, "failures": probe_failures},
        "g4_brute_report": g4,
        "g6_binding_qg45_qg46": g6_4546,
        "g6_binding_qg47": g6_47,
        "problems": problems[:40],
        "gates": gates,
        "authority": ("R1_EXACT_DEPTH3_KERNEL_SLICE_PLUS_SAMPLED_UNIFORM_N3_FULL_ALPHABET_"
                      "STRATIFIED_PER_CELL_AT_FROZEN_6_CELL_GRID__SEED_BOUNDED__NO_ALL_N_CLAIM__NOT_R6"),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "terminal": terminal,
    }
    receipt["result_digest"] = digest_of(receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, sort_keys=True, indent=1), encoding="utf-8")
    return {"terminal": receipt["terminal"], "digest": receipt["result_digest"],
            "r1_witnesses": r1_agg["witnesses"], "r2_witnesses": r2_agg["witnesses"],
            "r2_outside_closure": n_outside, "r1_parts": len(r1_seen), "r2_parts": len(r2_seen),
            "probe_failures": probe_failures, "problems": problems[:10]}


def main() -> int:
    parser = argparse.ArgumentParser(description="QG48 n=3 frontier prospection (R1 kernel slice + R2 sampling)")
    parser.add_argument("--r1-chunk", type=int, default=None, help="R1 task id in [0,6)")
    parser.add_argument("--r2-chunk", type=int, default=None, help="R2 task id in [0,1350)")
    parser.add_argument("--r1-parts-dir", type=Path, default=HERE / "QG48_R1_PARTS")
    parser.add_argument("--r2-parts-dir", type=Path, default=HERE / "QG48_R2_PARTS")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--rate-probe", type=int, default=None, metavar="N")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    objs, _, _, base = load_grid_and_base()

    if args.rate_probe is not None:
        rng = random.Random(R2_SEED)
        ob = objs[0]
        qg2.clear_caches()
        t0 = time.time()
        for c in range(args.rate_probe):
            letters_idx = [rng.randrange(63) for _ in range(6)]
            eval_gap(make_tp(letters_idx), ob)
        wall = time.time() - t0
        print(canonical({"rate_probe": {"instances": args.rate_probe, "objective": ob.name,
                                        "wall_s": round(wall, 2),
                                        "evals_per_s_core": round(args.rate_probe / wall, 2)}}))
        return 0

    if args.selftest:
        r1 = args.r1_parts_dir / "selftest"
        r2 = args.r2_parts_dir / "selftest"
        a1 = run_r1_chunk(SELFTEST_R1_TASKS[0], SELFTEST_R1_TRIPLES, r1, objs, base)
        a2 = run_r1_chunk(SELFTEST_R1_TASKS[1], SELFTEST_R1_TRIPLES, r1, objs, base)
        b1 = run_r2_chunk(SELFTEST_R2_TASKS[0], SELFTEST_R2_INSTANCES, r2, objs, base)
        b2 = run_r2_chunk(SELFTEST_R2_TASKS[1], SELFTEST_R2_INSTANCES, r2, objs, base)
        out = args.output or (r1 / "QG48_SELFTEST_RESULTS.json")
        m = merge(r1, r2, out, selftest=True)
        print(canonical({"selftest_r1_parts": [a1, a2], "selftest_r2_parts": [b1, b2], "merge": m}))
        return 0 if not m["problems"] else 3

    if args.r1_chunk is not None:
        assert 0 <= args.r1_chunk < R1_TASKS, f"R1 task id out of range [0,{R1_TASKS})"
        print(canonical(run_r1_chunk(args.r1_chunk, 7140, args.r1_parts_dir, objs, base)))
        return 0

    if args.r2_chunk is not None:
        assert 0 <= args.r2_chunk < R2_TASKS, f"R2 task id out of range [0,{R2_TASKS})"
        print(canonical(run_r2_chunk(args.r2_chunk, R2_INSTANCES_PER_TASK, args.r2_parts_dir, objs, base)))
        return 0

    if args.merge:
        out = args.output or (HERE / "QG48_N3_FRONTIER_PROSPECTION_RESULTS.json")
        m = merge(args.r1_parts_dir, args.r2_parts_dir, out, selftest=False)
        print(canonical(m))
        return 0 if m["terminal"] != "QG48_CONSISTENCY_FAILURE" else 3

    parser.error("one of --r1-chunk / --r2-chunk / --merge / --selftest / --rate-probe is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
