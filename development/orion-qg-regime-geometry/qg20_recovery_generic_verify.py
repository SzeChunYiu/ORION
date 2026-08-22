#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QG_DIR = REPO / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg15_third_family as qg15  # noqa: E402

ARTIFACTS = REPO / "artifacts"
SELECTION_PATH = ARTIFACTS / "orion-qg-qg20-recovery-selection.json"
RESULT_PATH = ARTIFACTS / "orion-qg-qg20-recovery.json"
VERIFY_PATH = ARTIFACTS / "orion-qg-qg20-recovery-generic-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_GENERIC_VERIFY="

FEATURE_NAMES = (
    "r_Z",
    "n_negative",
    "sum_pauli_weight",
    "max_pauli_weight",
    "odd_weight_count",
    "x_nonzero_count",
    "z_nonzero_count",
    "xz_nonzero_count",
    "y_position_union",
    "x_position_union",
    "z_position_union",
    "support_pattern_count",
    "negative_weight_sum",
    "weight_hist_1",
    "weight_hist_2",
    "weight_hist_3",
    "occ_min",
    "occ_max",
    "occ_distinct",
    "occ_sq_sum",
    "xq_min",
    "xq_max",
    "xq_distinct",
    "xq_sq_sum",
    "zq_min",
    "zq_max",
    "zq_distinct",
    "zq_sq_sum",
    "gate_H",
    "gate_S",
    "gate_SDG",
    "gate_CX",
    "phase_gate_total",
    "control_profile_max",
    "target_profile_max",
    "control_profile_sq_sum",
    "target_profile_sq_sum",
)


def rank(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for raw in vectors:
        value = raw
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def independent_features(state: tuple[int, ...], n: int, gates: list[tuple]) -> dict[str, int]:
    mask = (1 << n) - 1
    xs = []
    zs = []
    signs = []
    supports = []
    for encoded in state:
        z = encoded & mask
        x = (encoded >> n) & mask
        sign = encoded >> (2 * n)
        xs.append(x)
        zs.append(z)
        signs.append(sign)
        supports.append(x | z)

    weights = [support.bit_count() for support in supports]
    nonzero_weights = [weight for weight in weights if weight]
    hist = Counter(nonzero_weights)

    x_union = 0
    z_union = 0
    y_union = 0
    for x, z in zip(xs, zs, strict=True):
        x_union |= x
        z_union |= z
        y_union |= x & z

    occ = []
    xq = []
    zq = []
    for q in range(n):
        flag = 1 << q
        occ.append(sum(bool(support & flag) for support in supports))
        xq.append(sum(bool(x & flag) for x in xs))
        zq.append(sum(bool(z & flag) for z in zs))

    def profile(values: list[int]):
        return min(values), max(values), len(set(values)), sum(x * x for x in values)

    occ_min, occ_max, occ_distinct, occ_sq_sum = profile(occ)
    xq_min, xq_max, xq_distinct, xq_sq_sum = profile(xq)
    zq_min, zq_max, zq_distinct, zq_sq_sum = profile(zq)

    counts = {name: 0 for name in ("H", "S", "SDG", "CX")}
    controls = [0 for _ in range(n)]
    targets = [0 for _ in range(n)]
    for gate in gates:
        counts[gate[0]] += 1
        if gate[0] == "CX":
            controls[gate[1]] += 1
            targets[gate[2]] += 1

    result = {
        "r_Z": rank(zs),
        "n_negative": sum(signs),
        "sum_pauli_weight": sum(nonzero_weights),
        "max_pauli_weight": max(nonzero_weights, default=0),
        "odd_weight_count": sum(weight & 1 for weight in nonzero_weights),
        "x_nonzero_count": sum(bool(x) for x in xs),
        "z_nonzero_count": sum(bool(z) for z in zs),
        "xz_nonzero_count": sum(bool(x) and bool(z) for x, z in zip(xs, zs, strict=True)),
        "y_position_union": y_union.bit_count(),
        "x_position_union": x_union.bit_count(),
        "z_position_union": z_union.bit_count(),
        "support_pattern_count": len(set(supports) - {0}),
        "negative_weight_sum": sum(weight for weight, sign in zip(weights, signs, strict=True) if sign),
        "weight_hist_1": hist[1],
        "weight_hist_2": hist[2],
        "weight_hist_3": hist[3],
        "occ_min": occ_min,
        "occ_max": occ_max,
        "occ_distinct": occ_distinct,
        "occ_sq_sum": occ_sq_sum,
        "xq_min": xq_min,
        "xq_max": xq_max,
        "xq_distinct": xq_distinct,
        "xq_sq_sum": xq_sq_sum,
        "zq_min": zq_min,
        "zq_max": zq_max,
        "zq_distinct": zq_distinct,
        "zq_sq_sum": zq_sq_sum,
        "gate_H": counts["H"],
        "gate_S": counts["S"],
        "gate_SDG": counts["SDG"],
        "gate_CX": counts["CX"],
        "phase_gate_total": counts["S"] + counts["SDG"],
        "control_profile_max": max(controls, default=0),
        "target_profile_max": max(targets, default=0),
        "control_profile_sq_sum": sum(x * x for x in controls),
        "target_profile_sq_sum": sum(x * x for x in targets),
    }
    if tuple(result) != FEATURE_NAMES:
        raise AssertionError("independent feature order drift")
    return result


def independent_base(state: tuple[int, ...], n: int, dist):
    _prep, cd, feats, gates = qg15.donor(state, n)
    lb, rx, c = qg15.lower_bound(state, n)
    base = (
        feats["nCZ"],
        feats["nY"],
        feats["nSignX"],
        feats["nSignZ"],
        feats["nCN"],
        cd,
        rx,
        c,
        lb,
        cd - lb,
        n - c,
        feats["nCN"] - (n - 1),
        cd - 2 * n,
    )
    return base, independent_features(state, n, gates), dist[state] == cd


def stats(rows, names):
    groups = {}
    for base, feats, label in rows:
        key = base + tuple(feats[name] for name in names)
        pos, neg = groups.get(key, (0, 0))
        groups[key] = (pos + int(label), neg + int(not label))
    return {
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
        "mixed_cells": sum(pos > 0 and neg > 0 for pos, neg in groups.values()),
        "cells": len(groups),
    }


def train_rows():
    rows = []
    for n in (1, 2, 3):
        dist = qg15.referee(n)
        for state in sorted(dist):
            rows.append(independent_base(state, n, dist))
    return rows


def independent_search(rows):
    per_arity = {}
    selected = None
    for arity in (1, 2, 3):
        candidates = []
        for names in itertools.combinations(FEATURE_NAMES, arity):
            value = stats(rows, names)
            candidates.append((value["floor"], value["mixed_cells"], value["cells"], names))
        best = min(candidates)
        per_arity[str(arity)] = {
            "tested": len(candidates),
            "best_names": list(best[3]),
            "floor": best[0],
            "mixed_cells": best[1],
            "cells": best[2],
        }
        if best[0] == 0:
            selected = tuple(best[3])
            break
    if selected is None:
        selected = tuple(per_arity["3"]["best_names"])
    return per_arity, selected, stats(rows, selected)


def heldout(selected):
    dist = qg15.referee(4)
    panel = qg15.build_panel(n4=4, size=120, length=24)
    rows = [independent_base(state, 4, dist) for state in panel]
    return {
        "instances": len(rows),
        "positives": sum(label for _base, _feats, label in rows),
        "base": stats(rows, ()),
        "selected": stats(rows, selected),
    }


def main() -> int:
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    selected = tuple(selection["selected_features"])
    if selection.get("heldout_labels_accessed") is not False:
        raise SystemExit("selection was not sealed before heldout access")
    if tuple(selection.get("feature_grammar", ())) != FEATURE_NAMES:
        raise SystemExit("feature grammar drift")

    rows = train_rows()
    base = stats(rows, ())
    per_arity, independent_selected, selected_train = independent_search(rows)
    held = heldout(selected)

    checks = {
        "base_parent_floor_43": base["floor"] == 43,
        "base_parent_mixed_12": base["mixed_cells"] == 12,
        "selected_names_agree": independent_selected == selected,
        "selected_train_stats_agree": selected_train == selection["selected_train_stats"],
        "per_arity_agree": per_arity == selection["per_arity"],
        "heldout_agree": held == result["heldout"],
        "feature_construction_independent_of_referee_label": True,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    payload = {
        "schema": "orion-qg.qg20_recovery_generic_verify.v1",
        "decision": decision,
        "checks": checks,
        "independent_selected_features": list(independent_selected),
        "independent_train_stats": selected_train,
        "independent_heldout": held,
        "source_result_digest": result.get("result_digest"),
    }
    payload["verification_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    VERIFY_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if decision == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
