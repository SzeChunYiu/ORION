#!/usr/bin/env python3
"""Independent primitive referee for QG-18 TARE intrinsic support.

Does not import R6P/R6O/QG-7 analyzer code. Rebuilds n=3 phase-free Pauli
algebra, the serialized support-2 witness cost, and the complete support<=1
TARE family by direct enumeration.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "artifacts/orion-qg-qg18-intrinsic-support.json"
DEFAULT_OUTPUT = ROOT / "artifacts/orion-qg-qg18-generic-verification.json"
TOKEN = "ORIONQG_QG18_GENERIC="
POSITIVE = "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pc(x: int) -> int:
    return int(x).bit_count()


def wt(k: tuple[int, int]) -> int:
    return pc(k[0] | k[1])


def mul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return (a[0] ^ b[0], a[1] ^ b[1])


def symp(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (pc(a[0] & b[1]) + pc(a[1] & b[0])) & 1


def local(k: tuple[int, int], q: int) -> tuple[int, int]:
    return ((k[0] >> q) & 1, (k[1] >> q) & 1)


def f3(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> int:
    nz = int(a != (0, 0)) + int(b != (0, 0)) + int(c != (0, 0))
    return 1 if a == b == c != (0, 0) else nz


def as_key(v) -> tuple[int, int]:
    return (int(v[0]), int(v[1]))


def restore_cost(residuals: list[tuple[tuple[int, int], tuple[int, int]]], n: int) -> int:
    total = 0
    for branch in (0, 1):
        for q in range(n):
            total += f3(
                local(residuals[0][branch], q),
                local(residuals[1][branch], q),
                local(residuals[2][branch], q),
            )
    return total


def support2_cost(selected: dict[str, Any], n: int) -> dict[str, Any]:
    wit = selected["dxx_witness_verbatim"]
    s = as_key(wit["S"])
    labels = tuple(int(x) for x in wit["labels"])
    targets = [tuple(as_key(x) for x in tp) for tp in selected["target_pairs"]]
    residuals = []
    blocks_out = []
    frame_extra = 0
    checks = []
    for j, blk in enumerate(wit["blocks"]):
        r0, r1 = as_key(blk["R0"]), as_key(blk["R1"])
        perm = int(blk["target_permutation"])
        central = int(blk["central"])
        t0, t1 = targets[j] if perm == 0 else (targets[j][1], targets[j][0])
        w0, w1 = wt(r0), wt(r1)
        u = (2 * (w0 - 1) + 4 * (w1 - 1)) if central == 0 else (4 * (w0 - 1) + 2 * (w1 - 1))
        lab = (symp(s, r0), symp(s, r1))
        ok = 1 <= w0 <= 2 and 1 <= w1 <= 2 and symp(r0, r1) == 1 and lab == labels
        checks.append(ok)
        frame_extra += u
        residuals.append((mul(t0, r0), mul(t1, r1)))
        blocks_out.append({
            "R0": list(r0), "R1": list(r1), "support": [w0, w1],
            "central": central, "target_permutation": perm, "uanti": u,
            "labels": list(lab),
        })
    rcost = restore_cost(residuals, n)
    tag = 2 * wt(s)
    total = frame_extra + tag + rcost
    return {
        "cost": total,
        "frame_extra": frame_extra,
        "tag_cost": tag,
        "restore_f3_cost": rcost,
        "all_blocks_accept": all(checks),
        "max_frame_support": max(max(x["support"]) for x in blocks_out),
        "blocks": blocks_out,
        "S": list(s),
        "labels": list(labels),
    }


def cap1_exact(selected: dict[str, Any], n: int) -> dict[str, Any]:
    limit = 1 << n
    keys = [(x, z) for x in range(limit) for z in range(limit)]
    small = [k for k in keys if k != (0, 0) and wt(k) <= 1]
    pairs = [(a, b) for a in small for b in small if symp(a, b) == 1]
    targets = [tuple(as_key(x) for x in tp) for tp in selected["target_pairs"]]
    best = None
    feasible_tag_orientation_cells = 0
    options_examined = 0
    for s in (k for k in keys if k != (0, 0)):
        for labels in ((0, 1), (1, 0)):
            block_options = []
            for j in range(3):
                opts = []
                for pidx, (r0, r1) in enumerate(pairs):
                    if (symp(s, r0), symp(s, r1)) != labels:
                        continue
                    for perm in (0, 1):
                        t0, t1 = targets[j] if perm == 0 else (targets[j][1], targets[j][0])
                        opts.append((r0, r1, perm, (mul(t0, r0), mul(t1, r1)), pidx))
                block_options.append(opts)
            if any(not opts for opts in block_options):
                continue
            feasible_tag_orientation_cells += 1
            for a, b, c in itertools.product(*block_options):
                options_examined += 1
                residuals = [a[3], b[3], c[3]]
                rcost = restore_cost(residuals, n)
                cost = 2 * wt(s) + rcost
                key = (cost, wt(s), s, labels, a[4], a[2], b[4], b[2], c[4], c[2])
                if best is None or key < best[0]:
                    best = (key, (a, b, c), rcost)
    if best is None:
        raise AssertionError("generic cap1 enumeration found no feasible TARE configuration")
    key, chosen, rcost = best
    cost, _sw, s, labels, *_ = key
    return {
        "cost": int(cost),
        "support1_pair_count": len(pairs),
        "weight1_key_count": len(small),
        "feasible_tag_orientation_cells": feasible_tag_orientation_cells,
        "triple_options_examined": options_examined,
        "witness": {
            "S": list(s),
            "tag_weight": wt(s),
            "labels": list(labels),
            "restore_f3_cost": int(rcost),
            "blocks": [
                {"R0": list(o[0]), "R1": list(o[1]), "target_permutation": int(o[2]), "support": [wt(o[0]), wt(o[1])]}
                for o in chosen
            ],
        },
    }


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = {k: v for k, v in raw.items() if k != "result_digest"}
    return raw.get("result_digest") == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def run(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text())
    selected = raw.get("selected_witness", {})
    n = int(raw.get("n", -1))
    s2 = support2_cost(selected, n) if n > 0 and selected else None
    c1 = cap1_exact(selected, n) if n > 0 and selected else None
    checks = {
        "analyzer_schema": raw.get("schema") == "ORIONQG.QG18.TAREIntrinsicSupport.v1",
        "analyzer_digest": verify_digest(raw),
        "analyzer_positive": raw.get("terminal") == POSITIVE,
        "selected_index_zero": raw.get("qg7_parent", {}).get("selected_index") == 0,
        "generic_support2_acceptance": bool(s2 and s2["all_blocks_accept"]),
        "generic_support2_uses_weight2": bool(s2 and s2["max_frame_support"] == 2),
        "generic_support2_cost": bool(s2 and s2["cost"] == raw.get("support2_feasible_cost") == 7),
        "generic_cap1_cost": bool(c1 and c1["cost"] == raw.get("production_cap1_cost") == 8),
        "generic_strict_gap": bool(s2 and c1 and s2["cost"] < c1["cost"]),
        "support1_pair_count_n3": bool(c1 and c1["support1_pair_count"] == 18),
        "parent_support2_bound": raw.get("r6s_parent", {}).get("universal_support_upper_bound") == 2,
        "authority_bounded": raw.get("novelty_authority") is False and raw.get("r6_authority") is False and raw.get("physical_quantum_advantage_claim") is False,
        "protected_subject_not_read": raw.get("protected_subject_read") is False,
    }
    decision = "ACCEPT_KAPPA2" if all(checks.values()) else "REJECT"
    return {
        "schema": "ORIONQG.QG18.GenericVerification.v1",
        "decision": decision,
        "all_checks": all(checks.values()),
        "checks": checks,
        "independent_support2": s2,
        "independent_cap1": c1,
        "source_result_digest": raw.get("result_digest"),
        "intrinsic_support_conclusion": 2 if decision == "ACCEPT_KAPPA2" else None,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.input))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"decision": result["decision"], "all_checks": result["all_checks"], "cap1": result.get("independent_cap1", {}).get("cost"), "support2": result.get("independent_support2", {}).get("cost")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
