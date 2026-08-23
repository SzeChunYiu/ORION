#!/usr/bin/env python3
"""QG-37 production: exact one-corruption robust indexed-probe codes."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array, csr_array

ROOT = Path(__file__).resolve().parents[3]
QGDIR = ROOT / "research/extensions/orion-qg"
DEV = ROOT / "development/orion-qg-regime-geometry"
QG32_RESULT = QGDIR / "QG32_MIN_SEPARATING_PROBES_RESULTS.json"
QG35_RESULT = QGDIR / "QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json"
BINDING = DEV / "QG37_EXECUTION_BINDING_2026-08-22.md"
OUT = ROOT / "artifacts/orion-qg-qg37-robust.json"
TOKEN = "ORIONQG_QG37="

EXACT = "QG37_EXACT_ONE_CORRUPTION_CLASS_CONDITIONED_PROBE_CODE_MACHINE_CHECKED"
UPPER = "QG37_ROBUST_CLASS_CONDITIONED_UPPER_BOUND_ONLY"
CANNOT = "QG37_CANNOT_CHECK"


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_obj(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_qg32_prod():
    p = QGDIR / "qg32_min_separating_probes.py"
    spec = importlib.util.spec_from_file_location("qg32prod", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load QG-32 production primitives")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def construct_universe():
    q = load_qg32_prod()
    aa = q.autos()
    ps = list(itertools.product((0, 1), repeat=3))
    aux = q.aux48()
    obs: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    for t in itertools.product(range(4), repeat=6):
        o = q.orbit(t, aa)
        r = min(o)
        obs.setdefault(r, set()).update(o)
    reps = sorted(obs)
    bulk = [tuple(q.baseline(r, p) for p in ps[:4]) for r in reps]
    mat = np.array([q.response(r, ps, aux) for r in reps], dtype=np.int16)
    spectrum = [tuple(sorted(int(x) for x in row)) for row in mat]
    joint = q.make_groups([(bulk[i], spectrum[i]) for i in range(len(reps))])
    return reps, mat, joint


def class_size_hist(groups):
    return {str(k): int(v) for k, v in sorted(Counter(len(g) for g in groups).items())}


def coverage_model(group, mat, demand):
    pairs = list(itertools.combinations(group, 2))
    physical_masks = [0] * mat.shape[1]
    for ridx, (a, b) in enumerate(pairs):
        diff = np.flatnonzero(mat[a] != mat[b])
        if len(diff) == 0:
            raise AssertionError("joint class contains indistinguishable orbit pair")
        bit = 1 << ridx
        for p in diff:
            physical_masks[int(p)] |= bit

    mask_to_probes: dict[int, list[int]] = defaultdict(list)
    for p, mask in enumerate(physical_masks):
        if mask:
            mask_to_probes[int(mask)].append(p)

    masks = sorted(mask_to_probes, key=lambda m: (min(mask_to_probes[m]), m))
    caps = np.array([min(len(mask_to_probes[m]), demand) for m in masks], dtype=float)
    rows: list[int] = []
    cols: list[int] = []
    for j, mask in enumerate(masks):
        x = mask
        while x:
            low = x & -x
            rows.append(low.bit_length() - 1)
            cols.append(j)
            x -= low
    A = csr_array(
        coo_array(
            (np.ones(len(rows), dtype=float), (np.array(rows), np.array(cols))),
            shape=(len(pairs), len(masks)),
        )
    )
    return pairs, physical_masks, mask_to_probes, masks, caps, A


def decode_selection(x, mask_to_probes, masks):
    selected: list[int] = []
    if x is None:
        return selected
    for j, val in enumerate(x):
        n = int(round(float(val)))
        if n > 0:
            selected.extend(mask_to_probes[masks[j]][:n])
    return sorted(selected)


def solve_exact(group, mat, demand, seconds):
    if len(group) <= 1:
        return {
            "status": "EXACT",
            "minimum": 0,
            "selected": [],
            "solver_status": None,
            "solver_message": "singleton",
            "objective": 0.0,
            "bound": 0.0,
            "mask_groups": 0,
            "max_mask_multiplicity": 0,
        }

    pairs, physical_masks, mask_to_probes, masks, caps, A = coverage_model(group, mat, demand)
    res = milp(
        c=np.ones(len(masks), dtype=float),
        integrality=np.ones(len(masks), dtype=int),
        bounds=Bounds(np.zeros(len(masks)), caps),
        constraints=LinearConstraint(
            A,
            np.full(len(pairs), float(demand)),
            np.full(len(pairs), np.inf),
        ),
        options={"time_limit": float(seconds), "mip_rel_gap": 0.0, "presolve": True},
    )
    selected = decode_selection(res.x, mask_to_probes, masks)
    exact = int(res.status) == 0 and res.fun is not None
    objective = float(res.fun) if res.fun is not None else None
    minimum = int(round(objective)) if objective is not None else None
    dual_bound = getattr(res, "mip_dual_bound", None)
    return {
        "status": "EXACT" if exact else ("UPPER_ONLY" if selected else "CANNOT_CHECK"),
        "minimum": minimum if exact else None,
        "upper_bound": len(selected) if selected else None,
        "selected": selected,
        "solver_status": int(res.status),
        "solver_message": str(res.message),
        "objective": objective,
        "bound": float(dual_bound) if dual_bound is not None else None,
        "mip_gap": float(getattr(res, "mip_gap", math.inf)) if getattr(res, "mip_gap", None) is not None else None,
        "mask_groups": len(masks),
        "max_mask_multiplicity": max((len(v) for v in mask_to_probes.values()), default=0),
        "physical_probe_count": mat.shape[1],
        "pair_count": len(pairs),
        "physical_masks": physical_masks,
    }


def distance_certificate(group, mat, selected):
    if len(group) <= 1:
        return {
            "minimum_distance": None,
            "minimum_distance_pair_count": 0,
            "first_minimum_distance_pair": None,
            "distance_histogram": {},
            "radius1_unique": True,
        }
    ds = []
    first = None
    mind = None
    for a, b in itertools.combinations(group, 2):
        d = sum(int(mat[a, p] != mat[b, p]) for p in selected)
        ds.append(d)
        if mind is None or d < mind:
            mind = d
            first = [int(a), int(b)]
    hist = {str(k): int(v) for k, v in sorted(Counter(ds).items())}

    words = {i: tuple(int(mat[i, p]) for p in selected) for i in group}
    unique = True
    if selected:
        alph = []
        for p in selected:
            vals = sorted({int(mat[i, p]) for i in group})
            foreign = (max(vals) + 1) if vals else 0
            alph.append(vals + [foreign])
        seen: dict[tuple[int, ...], int] = {}
        for i in group:
            w = words[i]
            variants = {w}
            for pos in range(len(selected)):
                for sym in alph[pos]:
                    if sym != w[pos]:
                        z = list(w)
                        z[pos] = sym
                        variants.add(tuple(z))
            for z in variants:
                owner = seen.get(z)
                if owner is not None and owner != i:
                    unique = False
                    break
                seen[z] = i
            if not unique:
                break
    return {
        "minimum_distance": int(mind) if mind is not None else None,
        "minimum_distance_pair_count": int(hist.get(str(mind), 0)) if mind is not None else 0,
        "first_minimum_distance_pair": first,
        "distance_histogram": hist,
        "radius1_unique": bool(unique),
    }


def selected_mask_multiplicity(selected, physical_masks):
    c = Counter(int(physical_masks[p]) for p in selected)
    return max(c.values(), default=0), sum(1 for v in c.values() if v > 1)


def solve_naive_collapse(group, mat, seconds):
    if len(group) <= 1:
        return {"status": "EXACT", "minimum": 0}
    pairs, _physical, _mask_to_probes, masks, _caps, A = coverage_model(group, mat, 3)
    caps = np.ones(len(masks), dtype=float)
    res = milp(
        c=np.ones(len(masks), dtype=float),
        integrality=np.ones(len(masks), dtype=int),
        bounds=Bounds(np.zeros(len(masks)), caps),
        constraints=LinearConstraint(A, np.full(len(pairs), 3.0), np.full(len(pairs), np.inf)),
        options={"time_limit": float(seconds), "mip_rel_gap": 0.0, "presolve": True},
    )
    if int(res.status) == 0 and res.fun is not None:
        return {"status": "EXACT", "minimum": int(round(float(res.fun)))}
    return {
        "status": "CANNOT_CHECK" if res.x is None else "UPPER_ONLY",
        "upper_bound": int(round(float(res.fun))) if res.fun is not None else None,
        "solver_status": int(res.status),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--class-seconds", type=float, default=45.0)
    ap.add_argument("--ablation-seconds", type=float, default=5.0)
    args = ap.parse_args()

    q32 = json.loads(QG32_RESULT.read_text())
    q35 = json.loads(QG35_RESULT.read_text())
    reps, mat, joint = construct_universe()

    parent_checks = {
        "qg32_universe": q32.get("universe", {}).get("orbits") == 715
        and q32.get("universe", {}).get("physical_probes") == 384
        and q32.get("joint_partition", {}).get("class_count") == 92,
        "qg35_exact": q35.get("EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY") is True
        and q35.get("terminal") == "QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED",
        "qg35_universe": q35.get("universe")
        == {
            "joint_class_size_histogram": class_size_hist(joint),
            "joint_classes": 92,
            "orbits": 715,
            "probes": 384,
        },
        "qg35_minima_count": len(q35.get("class_minima", [])) == 92,
        "binding_present": BINDING.exists(),
    }

    class_rows = []
    all_exact = all(parent_checks.values())
    collapse_changed = False
    exceptional = []
    for idx, group in enumerate(joint):
        f = int(q35["class_minima"][idx])
        solved = solve_exact(group, mat, 3, args.class_seconds)
        selected = solved["selected"]
        cert = distance_certificate(group, mat, selected)
        puncturing_floor = 0 if len(group) <= 1 else f + 2
        exact_by_solver = solved["status"] == "EXACT"
        exact_by_puncturing = (
            len(group) <= 1
            or (
                len(selected) == puncturing_floor
                and cert["minimum_distance"] is not None
                and cert["minimum_distance"] >= 3
                and cert["radius1_unique"]
            )
        )
        exact = bool(exact_by_solver or exact_by_puncturing)
        minimum = len(selected) if exact_by_puncturing else solved.get("minimum")
        if len(group) <= 1:
            minimum = 0
        if not exact:
            all_exact = False

        physical_masks = solved.get("physical_masks", [0] * mat.shape[1])
        max_selected_equiv, duplicate_equiv_classes = selected_mask_multiplicity(selected, physical_masks)
        naive = solve_naive_collapse(group, mat, args.ablation_seconds)
        if exact and naive.get("status") == "EXACT" and naive.get("minimum") != minimum:
            collapse_changed = True

        overhead = None if minimum is None else int(minimum - f)
        strict_puncturing = minimum is not None and len(group) > 1 and minimum > puncturing_floor
        if strict_puncturing:
            exceptional.append(idx)
        class_rows.append(
            {
                "class_index": idx,
                "class_size": len(group),
                "D1_noiseless_minimum": f,
                "puncturing_D3_lower_bound": puncturing_floor,
                "D3_status": "EXACT" if exact else solved["status"],
                "D3_minimum": minimum if exact else None,
                "D3_upper_bound": len(selected) if selected else None,
                "robustness_overhead_D3_minus_D1": overhead,
                "strict_beyond_puncturing_floor": bool(strict_puncturing),
                "selected_probe_indices": selected,
                "distance_certificate": cert,
                "solver": {k: v for k, v in solved.items() if k not in ("selected", "physical_masks")},
                "selected_equivalent_mask_max_multiplicity": int(max_selected_equiv),
                "selected_equivalent_mask_duplicate_classes": int(duplicate_equiv_classes),
                "multiplicity_one_collapse_diagnostic": naive,
                "exact_by_puncturing_certificate": bool(exact_by_puncturing),
                "exact_by_production_optimizer": bool(exact_by_solver),
            }
        )

    exact_minima = [r["D3_minimum"] for r in class_rows if r["D3_status"] == "EXACT"]
    rstar = max(exact_minima) if all_exact and exact_minima else None
    overheads = [
        r["robustness_overhead_D3_minus_D1"]
        for r in class_rows
        if r["robustness_overhead_D3_minus_D1"] is not None
    ]
    terminal = EXACT if all_exact else (UPPER if any(r["D3_upper_bound"] is not None for r in class_rows) else CANNOT)

    out = {
        "schema": "ORIONQG.QG37.OneCorruptionRobust.v1",
        "issue": "SzeChunYiu/ORION#937",
        "terminal": terminal,
        "frozen_protocol_blob_sha": "c99f6ee73ab8e44e588a14ad0ab79b3fe426311c",
        "binding_sha256": file_sha(BINDING),
        "parent_hashes": {"qg32": file_sha(QG32_RESULT), "qg35": file_sha(QG35_RESULT)},
        "parent_checks": parent_checks,
        "universe": {
            "orbits": len(reps),
            "physical_probes": int(mat.shape[1]),
            "joint_classes": len(joint),
            "joint_class_size_histogram": class_size_hist(joint),
        },
        "distance_target": 3,
        "classes": class_rows,
        "all_92_class_conditioned_exact": bool(all_exact),
        "R1_star": rstar,
        "robustness_overhead_max": max(overheads) if all_exact and overheads else None,
        "robustness_overhead_histogram": (
            {str(k): int(v) for k, v in sorted(Counter(overheads).items())} if all_exact else None
        ),
        "strict_puncturing_exception_class_indices": exceptional,
        "multiplicity_one_collapse_changed_any_exact_class": bool(collapse_changed),
        "universal": {"status": "CANNOT_CHECK", "minimum": None, "upper_bound": None},
        "ONE_CORRUPTION_CLASS_CONDITIONED_IDENTITY_AUTHORITY": bool(all_exact),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_NOVELTY": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    out["result_digest"] = digest_obj(out)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canon(
            {
                "terminal": terminal,
                "all_exact": all_exact,
                "R1_star": rstar,
                "exceptional_classes": exceptional,
                "collapse_changed": collapse_changed,
                "result_digest": out["result_digest"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
