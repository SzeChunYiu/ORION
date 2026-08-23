#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qg15_third_family as qg15  # noqa: E402
import qg15b_predicate_language as qg15b  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
ARTIFACTS = REPO / "artifacts"
PROTOCOL = (
    REPO
    / "development"
    / "orion-qg-regime-geometry"
    / "QG20_RECOVERY_FEATURE_SEARCH_PROTOCOL_V1.md"
)
PARENT_RESULTS = Path(__file__).resolve().parent / "QG15B_PREDICATE_LANGUAGE_RESULTS.json"
SELECTION_PATH = ARTIFACTS / "orion-qg-qg20-recovery-selection.json"
RESULT_PATH = ARTIFACTS / "orion-qg-qg20-recovery.json"
SELECTION_PREFIX = "ORIONQG_QG20_RECOVERY_SELECTION="
RESULT_PREFIX = "ORIONQG_QG20_RECOVERY="
PARENT_RESULT_DIGEST = "3a4e9e5848d4e8e370d704ee4df8784d7456b93b125ccfd59c1f319676a1021b"

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


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_obj(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _profile_stats(values: list[int]) -> tuple[int, int, int, int]:
    return min(values), max(values), len(set(values)), sum(v * v for v in values)


def candidate_features(state: tuple[int, ...], n: int, gates: list[tuple]) -> dict[str, int]:
    """Frozen target-independent feature grammar; no exact-referee inputs."""
    xs = [qg15._xof(e, n) for e in state]
    zs = [qg15._zof(e, n) for e in state]
    signs = [qg15._sof(e, n) for e in state]
    supports = [x | z for x, z in zip(xs, zs, strict=True)]
    weights = [support.bit_count() for support in supports]

    nonidentity_weights = [w for w in weights if w > 0]
    hist = Counter(nonidentity_weights)
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
        bit = 1 << q
        occ.append(sum(1 for support in supports if support & bit))
        xq.append(sum(1 for x in xs if x & bit))
        zq.append(sum(1 for z in zs if z & bit))
    occ_min, occ_max, occ_distinct, occ_sq_sum = _profile_stats(occ)
    xq_min, xq_max, xq_distinct, xq_sq_sum = _profile_stats(xq)
    zq_min, zq_max, zq_distinct, zq_sq_sum = _profile_stats(zq)

    gate_counts = Counter(g[0] for g in gates)
    control = [0] * n
    target = [0] * n
    for gate in gates:
        if gate[0] == "CX":
            control[gate[1]] += 1
            target[gate[2]] += 1

    values = {
        "r_Z": qg15.rank_f2(zs),
        "n_negative": sum(signs),
        "sum_pauli_weight": sum(nonidentity_weights),
        "max_pauli_weight": max(nonidentity_weights, default=0),
        "odd_weight_count": sum(w % 2 for w in nonidentity_weights),
        "x_nonzero_count": sum(x != 0 for x in xs),
        "z_nonzero_count": sum(z != 0 for z in zs),
        "xz_nonzero_count": sum(x != 0 and z != 0 for x, z in zip(xs, zs, strict=True)),
        "y_position_union": y_union.bit_count(),
        "x_position_union": x_union.bit_count(),
        "z_position_union": z_union.bit_count(),
        "support_pattern_count": len({support for support in supports if support}),
        "negative_weight_sum": sum(w for w, sign in zip(weights, signs, strict=True) if sign),
        "weight_hist_1": hist.get(1, 0),
        "weight_hist_2": hist.get(2, 0),
        "weight_hist_3": hist.get(3, 0),
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
        "gate_H": gate_counts.get("H", 0),
        "gate_S": gate_counts.get("S", 0),
        "gate_SDG": gate_counts.get("SDG", 0),
        "gate_CX": gate_counts.get("CX", 0),
        "phase_gate_total": gate_counts.get("S", 0) + gate_counts.get("SDG", 0),
        "control_profile_max": max(control, default=0),
        "target_profile_max": max(target, default=0),
        "control_profile_sq_sum": sum(v * v for v in control),
        "target_profile_sq_sum": sum(v * v for v in target),
    }
    if tuple(values) != FEATURE_NAMES:
        raise AssertionError("feature implementation/order drift")
    return values


def base_vector(state: tuple[int, ...], n: int, dist: dict[tuple[int, ...], int] | None = None):
    prep, cd, donor_feats, gates = qg15.donor(state, n)
    del prep
    lb, rx, c = qg15.lower_bound(state, n)
    vec = qg15b.stab_feature_vector(donor_feats, cd, lb, rx, c, n)
    label = None if dist is None else (dist[state] == cd)
    return vec, candidate_features(state, n, gates), label, cd


def cell_stats(rows: list[tuple[tuple[int, ...], dict[str, int], bool]], names: tuple[str, ...]):
    groups: dict[tuple, list[int]] = {}
    for base, feats, label in rows:
        key = base + tuple(feats[name] for name in names)
        counts = groups.setdefault(key, [0, 0])
        counts[0 if label else 1] += 1
    mixed = sum(pos > 0 and neg > 0 for pos, neg in groups.values())
    floor = sum(min(pos, neg) for pos, neg in groups.values())
    return {"floor": floor, "mixed_cells": mixed, "cells": len(groups)}


def build_complete_rows():
    rows = []
    per_n = {}
    for n in (1, 2, 3):
        dist = qg15.referee(n)
        local = []
        for state in sorted(dist):
            base, feats, label, _cd = base_vector(state, n, dist)
            assert label is not None
            row = (base, feats, label)
            rows.append(row)
            local.append(row)
        per_n[str(n)] = len(local)
    return rows, per_n


def search_features(rows):
    base = cell_stats(rows, ())
    if base["floor"] != 43 or base["mixed_cells"] != 12:
        raise AssertionError(f"parent QG-15b obstruction did not reproduce: {base}")

    per_arity = {}
    selected = None
    for arity in (1, 2, 3):
        best = None
        best_names = None
        tested = 0
        for names in itertools.combinations(FEATURE_NAMES, arity):
            tested += 1
            stats = cell_stats(rows, names)
            key = (
                stats["floor"],
                stats["mixed_cells"],
                stats["cells"],
                names,
            )
            if best is None or key < best:
                best = key
                best_names = names
        assert best is not None and best_names is not None
        per_arity[str(arity)] = {
            "tested": tested,
            "best_names": list(best_names),
            "floor": best[0],
            "mixed_cells": best[1],
            "cells": best[2],
        }
        if best[0] == 0:
            selected = tuple(best_names)
            break
    if selected is None:
        selected = tuple(per_arity["3"]["best_names"])
    return base, per_arity, selected, cell_stats(rows, selected)


def heldout_rows(selected: tuple[str, ...]):
    # Selection must be passed in from the sealed pre-heldout stage.
    dist4 = qg15.referee(4)
    panel = qg15.build_panel(n4=4, size=120, length=24)
    rows = []
    for state in panel:
        base, feats, label, _cd = base_vector(state, 4, dist4)
        assert label is not None
        rows.append((base, feats, label))
    return {
        "instances": len(rows),
        "positives": sum(label for _base, _feats, label in rows),
        "base": cell_stats(rows, ()),
        "selected": cell_stats(rows, selected),
    }


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    parent = json.loads(PARENT_RESULTS.read_text(encoding="utf-8"))
    if parent.get("result_digest") != PARENT_RESULT_DIGEST:
        raise SystemExit("parent QG-15b result digest drift")

    rows, per_n = build_complete_rows()
    base, per_arity, selected, selected_train = search_features(rows)
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    selection = {
        "schema": "orion-qg.qg20_recovery_selection.v1",
        "protocol_sha256": protocol_sha,
        "parent_result_digest": PARENT_RESULT_DIGEST,
        "training_instances": len(rows),
        "per_n": per_n,
        "base_stats": base,
        "feature_grammar": list(FEATURE_NAMES),
        "per_arity": per_arity,
        "selected_features": list(selected),
        "selected_train_stats": selected_train,
        "selection_digest": "",
        "heldout_labels_accessed": False,
    }
    selection["selection_digest"] = sha256_obj(
        {key: value for key, value in selection.items() if key != "selection_digest"}
    )
    SELECTION_PATH.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(SELECTION_PREFIX + canonical(selection), flush=True)

    heldout = heldout_rows(selected)
    if selected_train["floor"] == 0 and heldout["selected"]["floor"] == 0:
        terminal = "QG20_RECOVERY_COMPACT_COORDINATE_SET_RESTORES_DETERMINATION_ON_FROZEN_TRAIN_AND_N4_PANEL"
    elif selected_train["floor"] == 0:
        terminal = "QG20_RECOVERY_TRAIN_DETERMINATION_ONLY__N4_MIXED"
    else:
        terminal = "QG20_RECOVERY_NO_ARITY3_COORDINATE_SET__FULL_QUOTIENT_REQUIRED"

    result = {
        "schema": "orion-qg.qg20_recovery_feature_search.v1",
        "protocol_sha256": protocol_sha,
        "parent_result_digest": PARENT_RESULT_DIGEST,
        "selection": selection,
        "heldout": heldout,
        "terminal": terminal,
        "feature_construction_reads_exact_referee": False,
        "novelty_authority": False,
        "all_n_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["result_digest"] = sha256_obj(result)
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT_PREFIX + canonical(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
