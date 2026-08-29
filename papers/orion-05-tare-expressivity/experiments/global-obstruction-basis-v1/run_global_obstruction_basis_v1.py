#!/usr/bin/env python3
"""ORION05.GLOBAL_OBSTRUCTION_BASIS.v1 batch runner (DRAFT — design artifact).

Wraps the paper's own frozen solver
``papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py``
(imported, never reimplemented) over the complete distinct-target n=2 census
C(15,6)=5005, plus the registered control panel.

Design contract (see PROTOCOL_DRAFT.json):
  * embarrassingly parallel: one JSON result file per instance; a valid
    existing file is never recomputed (resume-safe; SLURM-array friendly);
  * deterministic: no RNG anywhere, PYTHONHASHSEED=0 expected;
  * ``--smoke`` runs ZERO solver instances — it only validates imports,
    enumeration counts, canonical hashing, and the predicate-only controls;
  * every heavy call is guarded by a SIGALRM timeout -> TIMEOUT row.

NEVER run non-smoke modes on the Mac; census execution belongs on the
cluster (see COMPUTE_PLAN.md).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import signal
import sys
import time
from itertools import combinations
from pathlib import Path

SCHEMA = "ORION.ORION05.GLOBAL_OBSTRUCTION_BASIS.InstanceResult.v1"
# NOTE(freeze): re-verify this constant with `shasum -a 256` at freeze time;
# it must equal the protocol's source_bindings.support_two_solver.sha256.
FROZEN_SOLVER_SHA256 = (
    "642cc67a280abb2ca06089ae01510040f1f598ec638d525ddcc29fae8c6b25d3"
)
SOLVER_REL_PATH = (
    "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py"
)
CENSUS_COUNT = 5005

# Registered planted-positive controls (verbatim from the R6O receipt).
CONTROLS_POS = {
    "control:r6o-16": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 0], [2, 2]],
    "control:r6o-17": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 0], [0, 2]],
    "control:r6o-19": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 2], [0, 2]],
}
CONTROL_EXPECT_COSTS = {"c1": 6, "c2": 5}

FAILURE_CLASSES = (
    "phantom_home_off_anti",
    "phantom_tagged_home",
    "l1_phantom_at_home",
    "phantom_untagged_borrow",
    "phantom_home_commute",
    "comm_s2_partner_off",
    "comm_s2_structure",
    "anchored_structure",
    "occupancy",
    "NEEDS_L1_REDUCTION",
    "UNCLASSIFIED",
)


class SolveTimeout(Exception):
    pass


def _alarm(_signum, _frame):  # pragma: no cover - signal path
    raise SolveTimeout()


def load_solver(repo_root: Path, allow_hash_mismatch: bool = False):
    path = repo_root / SOLVER_REL_PATH
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != FROZEN_SOLVER_SHA256 and not allow_hash_mismatch:
        raise SystemExit(
            json.dumps(
                {
                    "fatal": "CANNOT_CHECK_SOURCE_BINDING",
                    "expected": FROZEN_SOLVER_SHA256,
                    "observed": digest,
                    "path": str(path),
                }
            )
        )
    spec = importlib.util.spec_from_file_location("orion05_solver", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["orion05_solver"] = mod  # required for dataclass resolution
    spec.loader.exec_module(mod)
    return mod, digest


def census_instance(index: int) -> list[list[int]]:
    """index -> six dense n=2 targets, canonical lexicographic order."""
    combos = combinations(range(1, 16), 6)
    for i, combo in enumerate(combos):
        if i == index:
            return [[c // 4, c % 4] for c in combo]
    raise IndexError(index)


def input_hash(targets: list[list[int]]) -> str:
    blob = json.dumps(targets, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Classification layer (frozen predicates; QG-7c M1 transcribed to witnesses)
# ---------------------------------------------------------------------------

def roles(mod, pair, tag, orientation):
    """Return (f0, f1) with f0 the Tag-commuting member (label 0)."""
    l0 = mod.sparse_symp(tag, pair.r0)
    l1 = mod.sparse_symp(tag, pair.r1)
    if (l0, l1) != tuple(orientation):
        raise AssertionError({"labels_disagree_with_orientation": [l0, l1]})
    return (pair.r0, pair.r1) if l0 == 0 else (pair.r1, pair.r0)


def letter(mod, sparse, q):
    return mod.sparse_letter(sparse, q)


def frame_classes(mod, frame, partner, tag):
    """[(q, (alpha, beta)) for q in supp(frame)] — R6S class formalism."""
    out = []
    for q, a in frame:
        alpha = mod.local_symp(a, letter(mod, partner, q))
        beta = mod.local_symp(letter(mod, tag, q), a)
        out.append((q, (alpha, beta)))
    return out


def classify_block(mod, f0, f1, tag, other_frames):
    """Frozen M1 shape predicate on one pair (witness geometry).

    Returns dict(shape, failures, pinned, detail). ``other_frames`` are the
    remaining blocks' frame Paulis (for the pinned flag only).
    """
    w0, w1 = len(f0), len(f1)
    supp0 = [q for q, _ in f0]
    supp1 = [q for q, _ in f1]
    union = sorted(set(supp0) | set(supp1))
    occ = sum(
        1
        for q in union
        if mod.local_symp(letter(mod, tag, q), letter(mod, f0, q))
        or mod.local_symp(letter(mod, tag, q), letter(mod, f1, q))
    )
    failures: list[str] = []
    pinned = False
    detail: dict[str, object] = {"w0": w0, "w1": w1, "occ": occ}

    def s(q):
        return letter(mod, tag, q)

    def pin(q):
        return any(
            g_letter != 0 and mod.local_symp(s(q), g_letter) == 1
            for g in other_frames
            for g_letter in (letter(mod, g, q),)
        ) and s(q) != 0

    if w0 == 1 and w1 == 1:
        shape = "anchored"
        q0, q1 = supp0[0], supp1[0]
        good = (
            q0 == q1
            and s(q0) == letter(mod, f0, q0) != 0
            and mod.local_symp(s(q0), letter(mod, f1, q0)) == 1
        )
        if not good:
            failures.append("anchored_structure")
        if occ != 1:
            failures.append("occupancy")
    elif w0 == 1 and w1 == 2:
        shape = "phantom"
        h = supp0[0]
        if h not in supp1:
            return {
                "shape": "UNCLASSIFIED",
                "failures": ["phantom_home_off_anti"],
                "pinned": False,
                "detail": detail,
            }
        b = next(q for q in supp1 if q != h)
        detail |= {"home": h, "borrow": b}
        if s(h) != 0:
            if mod.local_symp(s(h), letter(mod, f1, h)) or mod.local_symp(
                s(h), letter(mod, f0, h)
            ):
                failures.append("l1_phantom_at_home")
            failures.append("phantom_tagged_home")
        if s(b) == 0 or mod.local_symp(s(b), letter(mod, f1, b)) != 1:
            failures.append("phantom_untagged_borrow")
        if letter(mod, f0, h) == letter(mod, f1, h):
            failures.append("phantom_home_commute")
        if occ != 1:
            failures.append("occupancy")
        pinned = pin(b)
    elif w0 == 2 and w1 == 1:
        shape = "comm_s2"
        a = supp1[0]
        if a not in supp0:
            return {
                "shape": "UNCLASSIFIED",
                "failures": ["comm_s2_partner_off"],
                "pinned": False,
                "detail": detail,
            }
        b = next(q for q in supp0 if q != a)
        detail |= {"anchor": a, "borrow": b}
        good = (
            s(b) != 0
            and mod.local_symp(s(b), letter(mod, f0, b)) == 1
            and s(a) != 0
            and mod.local_symp(s(a), letter(mod, f0, a)) == 1
            and letter(mod, f1, a) not in (0, s(a), letter(mod, f0, a))
        )
        if not good:
            failures.append("comm_s2_structure")
        if occ != 2:
            failures.append("occupancy")
        pinned = pin(b)
    elif w0 == 2 and w1 == 2:
        shape = "NEEDS_L1_REDUCTION"
        failures.append("NEEDS_L1_REDUCTION")
    else:
        shape = "UNCLASSIFIED"
        failures.append("UNCLASSIFIED")
    return {"shape": shape, "failures": failures, "pinned": pinned, "detail": detail}


def reduce_witness(mod, targets, witness):
    """Frozen RED: delete class-(0,0) coordinates of weight-two frames.

    Every deletion is re-verified: pair anticommutation, Tag labels equal the
    orientation, exact total-cost equality via the solver's own cost
    functions. Returns (pairs, deletions, audit_failures).
    """
    prep = mod.preprocess_targets(targets)
    pairs = list(witness.pairs)
    tag = witness.tag
    orientation = tuple(witness.orientation)
    baseline_cost = witness.cost

    def total_cost(cur_pairs):
        c_frame = mod.frame_cost(cur_pairs, witness.centrals)
        c_restore = mod.restore_cost_full_scan(prep.targets, cur_pairs)
        return c_frame + 2 * len(tag) + c_restore

    deletions = []
    audit_failures = []
    changed = True
    while changed:
        changed = False
        for pi, pair in enumerate(pairs):
            for member_name in ("r0", "r1"):
                frame = getattr(pair, member_name)
                partner = pair.r1 if member_name == "r0" else pair.r0
                if len(frame) != 2:
                    continue
                for q, a in frame:
                    alpha = mod.local_symp(a, letter(mod, partner, q))
                    beta = mod.local_symp(letter(mod, tag, q), a)
                    if (alpha, beta) != (0, 0):
                        continue
                    new_frame = tuple(e for e in frame if e[0] != q)
                    new_pair = mod.FramePair(
                        new_frame if member_name == "r0" else pair.r0,
                        new_frame if member_name == "r1" else pair.r1,
                    )
                    trial = list(pairs)
                    trial[pi] = new_pair
                    ok_anti = all(
                        mod.sparse_symp(p.r0, p.r1) == 1 for p in trial
                    )
                    ok_labels = all(
                        (
                            mod.sparse_symp(tag, p.r0),
                            mod.sparse_symp(tag, p.r1),
                        )
                        == orientation
                        for p in trial
                    )
                    ok_cost = total_cost(tuple(trial)) == baseline_cost
                    if ok_anti and ok_labels and ok_cost:
                        pairs = trial
                        deletions.append(
                            {"pair": pi, "member": member_name, "q": q, "letter": a}
                        )
                        changed = True
                        break
                    audit_failures.append(
                        {
                            "pair": pi,
                            "member": member_name,
                            "q": q,
                            "ok_anti": ok_anti,
                            "ok_labels": ok_labels,
                            "ok_cost": ok_cost,
                        }
                    )
                if changed:
                    break
            if changed:
                break
    return tuple(pairs), deletions, audit_failures


def classify_witness(mod, targets, witness, pairs=None, basis_mask=None):
    """Full classification of one witness. basis_mask corrupts the basis for
    the C_NEG_CORRUPT control (removes named shapes from membership)."""
    basis_gap = {"phantom", "comm_s2"}
    if basis_mask is not None:
        basis_gap &= set(basis_mask)
    tag = witness.tag
    orientation = tuple(witness.orientation)
    use_pairs = witness.pairs if pairs is None else pairs
    blocks = []
    frames_by_pair = [(p.r0, p.r1) for p in use_pairs]
    for pi, pair in enumerate(use_pairs):
        f0, f1 = roles(mod, pair, tag, orientation)
        others = [
            f
            for pj, fr in enumerate(frames_by_pair)
            if pj != pi
            for f in fr
        ]
        entry = classify_block(mod, f0, f1, tag, others)
        entry["pair_index"] = pi
        entry["classes_f0"] = frame_classes(mod, f0, f1, tag)
        entry["classes_f1"] = frame_classes(mod, f1, f0, tag)
        blocks.append(entry)
    weight2_blocks = [
        b for b in blocks if b["detail"].get("w0", 0) == 2 or b["detail"].get("w1", 0) == 2
    ]
    clean_hits = [
        b
        for b in weight2_blocks
        if b["shape"] in basis_gap and not b["failures"]
    ]
    membership = "IN_BASIS" if clean_hits else "NOT_IN_BASIS"
    return {
        "blocks": blocks,
        "weight2_block_count": len(weight2_blocks),
        "clean_obstruction_shapes": sorted({b["shape"] for b in clean_hits}),
        "pinned_any": any(b["pinned"] for b in clean_hits),
        "membership": membership,
    }


# ---------------------------------------------------------------------------
# Per-instance driver
# ---------------------------------------------------------------------------

def solve_with_timeout(fn, timeout_s):
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def run_instance(mod, solver_sha, instance_id, targets, timeout_s):
    rec = {
        "schema": SCHEMA,
        "instance_id": instance_id,
        "targets": targets,
        "input_sha256": input_hash(targets),
        "solver_sha256": solver_sha,
        "terminal": "OK",
    }
    t0 = time.monotonic()
    try:
        matching2, w2 = solve_with_timeout(
            lambda: mod.solve_six_targets(targets, max_support=2), timeout_s
        )
        rec["t_solve2_s"] = round(time.monotonic() - t0, 3)
        t1 = time.monotonic()
        matching1, w1 = solve_with_timeout(
            lambda: mod.solve_six_targets(targets, max_support=1),
            max(60.0, timeout_s / 10),
        )
        rec["t_solve1_s"] = round(time.monotonic() - t1, 3)
    except SolveTimeout:
        rec["terminal"] = "TIMEOUT"
        rec["t_elapsed_s"] = round(time.monotonic() - t0, 3)
        return rec
    except Exception as exc:  # recorded, never silently dropped
        rec["terminal"] = "ERROR"
        rec["error"] = repr(exc)
        return rec

    tp2 = tuple((targets[i], targets[j]) for i, j in matching2)
    tp1 = tuple((targets[i], targets[j]) for i, j in matching1)
    checks2 = mod.verify_witness(tp2, w2)
    checks1 = mod.verify_witness(tp1, w1)
    rec |= {
        "c_d2": w2.cost,
        "c_d1": w1.cost,
        "gap": w1.cost - w2.cost,
        "matching2": [list(p) for p in matching2],
        "witness2": w2.as_dict(),
        "witness2_checks_all": all(checks2.values()),
        "witness1_checks_all": all(checks1.values()),
    }
    if not all(checks2.values()) or not all(checks1.values()):
        rec["terminal"] = "ERROR"
        rec["error"] = {"witness_checks": {"d2": checks2, "d1": checks1}}
        return rec
    if rec["gap"] < 0:
        rec["terminal"] = "ERROR"
        rec["error"] = "negative_gap_family_containment_violated"
        return rec
    if rec["gap"] == 0:
        rec["outcome"] = "NO_GAP"
        return rec

    raw_cls = classify_witness(mod, targets, w2)
    red_pairs, deletions, audit = reduce_witness(mod, targets, w2)
    red_cls = classify_witness(mod, targets, w2, pairs=red_pairs)
    rec |= {
        "classification_raw": raw_cls,
        "reduction_deletions": deletions,
        "reduction_audit_failures": audit,
        "classification_reduced": red_cls,
    }
    if red_cls["membership"] == "IN_BASIS":
        rec["outcome"] = "GAP_IN_BASIS"
    elif any(
        "NEEDS_L1_REDUCTION" in b["failures"] for b in red_cls["blocks"]
    ):
        rec["outcome"] = "GAP_NEEDS_L1_REDUCTION"
    else:
        rec["outcome"] = "GAP_NOT_IN_BASIS"
    return rec


# ---------------------------------------------------------------------------
# Controls and smoke
# ---------------------------------------------------------------------------

def sparse(entries):
    return tuple(tuple(e) for e in entries)


def run_predicate_controls(mod) -> list[dict]:
    """PREDICATE_ONLY controls; ZERO solver calls; safe in --smoke."""
    out = []
    # C_SYNTH_B: planted violation, must FIRE.
    f0 = sparse([[0, 1]])
    f1 = sparse([[0, 1], [1, 2]])
    tag = sparse([[0, 3], [1, 1]])
    entry = classify_block(mod, f0, f1, tag, other_frames=[])
    fired = (
        entry["shape"] == "phantom"
        and "phantom_tagged_home" in entry["failures"]
        and "phantom_home_commute" in entry["failures"]
    )
    deletable = [
        (q, cls)
        for q, cls in frame_classes(mod, f1, f0, tag)
        if cls == (0, 0)
    ]
    out.append(
        {
            "control": "C_SYNTH_B_planted_violation",
            "passed": fired and not deletable,
            "entry": entry,
            "lemma_e_deletable": deletable,
        }
    )
    # C_SYNTH_A: reduction path — q1 of f1 must be class (0,0).
    f0a = sparse([[0, 1]])
    f1a = sparse([[0, 2], [1, 1]])
    taga = sparse([[0, 1]])
    classes = frame_classes(mod, f1a, f0a, taga)
    has_del = any(cls == (0, 0) for _, cls in classes)
    post = classify_block(mod, f0a, tuple(e for e in f1a if e[0] != 1), taga, [])
    out.append(
        {
            "control": "C_SYNTH_A_reduction_path",
            "passed": has_del
            and post["shape"] == "anchored"
            and not post["failures"],
            "classes_f1": classes,
            "post_reduction": post,
        }
    )
    return out


def run_solver_controls(mod, solver_sha, timeout_s) -> list[dict]:
    """Cluster-side CONTROL_GATE. Heavy (three full n=2 solves)."""
    out = []
    for cid, targets in CONTROLS_POS.items():
        rec = run_instance(mod, solver_sha, cid, targets, timeout_s)
        expected_ok = (
            rec.get("terminal") == "OK"
            and rec.get("c_d2") == CONTROL_EXPECT_COSTS["c2"]
            and rec.get("c_d1") == CONTROL_EXPECT_COSTS["c1"]
            and rec.get("outcome") == "GAP_IN_BASIS"
        )
        corrupt_fired = False
        if expected_ok:
            found = rec["classification_reduced"]["clean_obstruction_shapes"]
            mask = {"phantom", "comm_s2"} - set(found)
            red_pairs, _, _ = reduce_witness(
                mod,
                targets,
                _rebuild_witness(mod, rec),
            )
            corrupted = classify_witness(
                mod,
                targets,
                _rebuild_witness(mod, rec),
                pairs=red_pairs,
                basis_mask=mask,
            )
            corrupt_fired = corrupted["membership"] == "NOT_IN_BASIS"
        out.append(
            {
                "control": cid,
                "passed": expected_ok and corrupt_fired,
                "positive_ok": expected_ok,
                "corrupted_basis_fired": corrupt_fired,
                "record": rec,
            }
        )
    return out


def _rebuild_witness(mod, rec):
    """Reconstruct a SparseWitness from its as_dict serialization."""
    w = rec["witness2"]
    pairs = tuple(
        mod.FramePair(sparse(p[0]), sparse(p[1])) for p in w["frames"]
    )
    return mod.SparseWitness(
        w["cost"],
        pairs,
        sparse(w["tag"]),
        tuple(w["orientation"]),
        tuple(w["centrals"]),
        (w["relative_permutation_B"], w["relative_permutation_C"]),
        w["frame_cost"],
        w["tag_cost"],
        w["restore_cost"],
    )


def smoke(mod, solver_sha) -> dict:
    """Zero solver instances. Import/enumeration/predicate validation only."""
    n_pairs_2 = mod.pair_count_formula(2)
    gen_2 = sum(1 for _ in mod.ordered_anticommuting_pairs(2, max_support=2))
    gen_1 = sum(1 for _ in mod.ordered_anticommuting_pairs(2, max_support=1))
    matchings = len(mod.perfect_matchings(range(6)))
    census = sum(1 for _ in combinations(range(1, 16), 6))
    first = census_instance(0)
    checks = {
        "pair_count_formula_n2_is_120": n_pairs_2 == 120,
        "generator_matches_formula": gen_2 == 120,
        "support_one_pairs_n2_is_12": gen_1 == 12,
        "fifteen_matchings": matchings == 15,
        "census_count_5005": census == CENSUS_COUNT,
        "first_instance": first
        == [[0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2]],
        "solver_sha256": solver_sha,
    }
    controls = run_predicate_controls(mod)
    checks["predicate_controls_all_passed"] = all(c["passed"] for c in controls)
    checks["controls"] = controls
    checks["smoke_ok"] = all(
        v for k, v in checks.items() if isinstance(v, bool)
    )
    return checks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--smoke", action="store_true", help="0 solver instances")
    ap.add_argument("--controls", action="store_true", help="CONTROL_GATE (heavy)")
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--stop", type=int, default=None, help="exclusive")
    ap.add_argument("--array-chunk", type=int, default=15,
                    help="instances per SLURM array task")
    ap.add_argument("--timeout-s", type=float, default=1800.0)
    ap.add_argument("--allow-hash-mismatch", action="store_true")
    args = ap.parse_args()

    mod, solver_sha = load_solver(args.repo_root, args.allow_hash_mismatch)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        result = smoke(mod, solver_sha)
        print(json.dumps(result, default=str))
        return 0 if result["smoke_ok"] else 3

    if args.controls:
        gate = run_solver_controls(mod, solver_sha, args.timeout_s)
        payload = {
            "control_gate_passed": all(c["passed"] for c in gate),
            "controls": gate,
        }
        (args.out_dir / "CONTROL_GATE.json").write_text(
            json.dumps(payload, indent=1, default=str)
        )
        print(json.dumps({k: payload[k] for k in ("control_gate_passed",)}))
        return 0 if payload["control_gate_passed"] else 4

    # Census slice: explicit --start/--stop, else derive from SLURM array id.
    if args.start is None:
        task = int(os.environ.get("SLURM_ARRAY_TASK_ID", "0"))
        args.start = task * args.array_chunk
        args.stop = min(CENSUS_COUNT, args.start + args.array_chunk)
    args.stop = min(CENSUS_COUNT, args.stop if args.stop is not None else CENSUS_COUNT)

    inst_dir = args.out_dir / "instances"
    inst_dir.mkdir(exist_ok=True)
    for idx in range(args.start, args.stop):
        out_path = inst_dir / f"inst_{idx:04d}.json"
        if out_path.exists():
            try:
                json.loads(out_path.read_text())
                continue  # resume: valid file, never recompute
            except json.JSONDecodeError:
                pass
        targets = census_instance(idx)
        rec = run_instance(mod, solver_sha, idx, targets, args.timeout_s)
        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, separators=(",", ":"), default=str))
        tmp.replace(out_path)
        print(
            json.dumps(
                {
                    "instance_id": idx,
                    "terminal": rec["terminal"],
                    "outcome": rec.get("outcome"),
                    "gap": rec.get("gap"),
                }
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
