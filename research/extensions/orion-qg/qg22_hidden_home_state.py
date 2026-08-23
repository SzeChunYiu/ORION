#!/usr/bin/env python3
"""QG-22: exact hidden-home state quotient for the pinned PP J5 move."""
from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(QG))
import qg7c_classification as q7c  # noqa:E402
import qg7d_information_closure as q7dinfo  # noqa:E402

PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG22_HIDDEN_HOME_STATE_PROTOCOL_V1.md"
PARENT_QG7C = QG / "QG7C_CLASSIFICATION_RESULTS.json"
PARENT_PAD = QG / "QG7D_PADDING_ABLATION_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg22-hidden-home-state.json"
TOKEN = "ORIONQG_QG22="
ISSUE = "SzeChunYiu/ORION#868"
POSITIVE = "QG22_HIDDEN_HOME_J5_DELTA_EXACTLY_DETERMINED_BY_MINIMAL_5_PREDICATE_STATE"
PREDICATES = ("a0","b0","c0","ab","ac","bc","am","bm0","cm","a_bm","c_bm")
SELECTED = ("b0","ab","ac","bm0","a_bm")
X, Z = 1, 3


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_map(a: int, b: int, c: int, m: int) -> dict[str, bool]:
    bm = q7c.lmul(b, m)
    return {
        "a0": a == 0,
        "b0": b == 0,
        "c0": c == 0,
        "ab": a == b,
        "ac": a == c,
        "bc": b == c,
        "am": a == m,
        "bm0": bm == 0,
        "cm": c == m,
        "a_bm": a == bm,
        "c_bm": c == bm,
    }


def local_delta(a: int, b: int, c: int, m: int) -> int:
    return q7c.lf3(a, b, c) - q7c.lf3(a, q7c.lmul(b, m), c)


def rows(m: int):
    out = []
    for a, b, c in itertools.product(range(4), repeat=3):
        out.append({"abc": [a,b,c], "delta": local_delta(a,b,c,m), "f": feature_map(a,b,c,m)})
    return out


def subset_cells(subset: tuple[str, ...], rr: list[dict[str, Any]]):
    cells: dict[tuple[int, ...], dict[str, Any]] = {}
    for r in rr:
        key = tuple(int(r["f"][name]) for name in subset)
        cell = cells.setdefault(key, {"deltas": set(), "examples": {}})
        d = int(r["delta"])
        cell["deltas"].add(d)
        cell["examples"].setdefault(d, r["abc"])
    return cells


def first_mixed(cells):
    for key in sorted(cells):
        ds = sorted(cells[key]["deltas"])
        if len(ds) > 1:
            return {
                "signature": list(key),
                "deltas": ds,
                "examples": {str(d): cells[key]["examples"][d] for d in ds[:2]},
            }
    return None


def determining(subset: tuple[str, ...], by_m: dict[int, list[dict[str, Any]]]) -> bool:
    return all(first_mixed(subset_cells(subset, rr)) is None for rr in by_m.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()

    parent = json.loads(PARENT_QG7C.read_text())
    pad = json.loads(PARENT_PAD.read_text())
    by_m = {Z: rows(Z), X: rows(X)}

    selected_tables = {}
    selected_cell_counts = {}
    selected_mixed = {}
    for m, rr in by_m.items():
        cells = subset_cells(SELECTED, rr)
        selected_cell_counts[str(m)] = len(cells)
        selected_mixed[str(m)] = first_mixed(cells)
        selected_tables[str(m)] = {
            "".join(str(x) for x in key): next(iter(cell["deltas"]))
            for key, cell in sorted(cells.items())
        }

    minimum_k = None
    minimum_subsets: list[list[str]] = []
    for k in range(len(PREDICATES) + 1):
        found = []
        for subset in itertools.combinations(PREDICATES, k):
            if determining(subset, by_m):
                found.append(list(subset))
        if found:
            minimum_k = k
            minimum_subsets = found
            break

    four_counterexamples = []
    for subset in itertools.combinations(PREDICATES, 4):
        witness = None
        for m in (Z, X):
            mixed = first_mixed(subset_cells(subset, by_m[m]))
            if mixed is not None:
                witness = {"modifier": m, "mixed": mixed}
                break
        four_counterexamples.append({"subset": list(subset), "witness": witness})

    paired_cells: dict[tuple[tuple[int,...],tuple[int,...]], set[int]] = defaultdict(set)
    paired_hist = Counter()
    for a0,b0,c0,a1,b1,c1 in itertools.product(range(4), repeat=6):
        f0 = feature_map(a0,b0,c0,Z)
        f1 = feature_map(a1,b1,c1,X)
        s0 = tuple(int(f0[n]) for n in SELECTED)
        s1 = tuple(int(f1[n]) for n in SELECTED)
        d = local_delta(a0,b0,c0,Z) + local_delta(a1,b1,c1,X)
        paired_cells[(s0,s1)].add(d)
        paired_hist[d] += 1
    paired_mixed = sum(1 for ds in paired_cells.values() if len(ds) > 1)
    branch_hist = {
        str(m): {str(k): v for k,v in sorted(Counter(r["delta"] for r in rr).items())}
        for m,rr in by_m.items()
    }

    source = inspect.getsource(q7dinfo)
    parent_pp = (
        parent["t4b_pinned"]["failing_census"]["PP_ja0_delta1"]
        + parent["t4b_pinned"]["failing_census"]["PP_ja0_delta2"]
        + parent["t4b_pinned"]["failing_census"]["PP_ja1_delta1"]
    )
    gates = {
        "protocol_frozen": PROTOCOL.exists(),
        "parent_qg7c_terminal": parent.get("terminal") == "QG7C_PARTIAL__L4B_OPEN",
        "parent_pp_failures_32556": parent_pp == 32556,
        "padding_parent_negative": pad.get("terminal") == "QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED" and pad.get("both_accept") is True,
        "parent_info_source_bound": "hidden_domain_4096" in source and "delta_span_pm4" in source,
        "branch_domains_64": all(len(rr) == 64 for rr in by_m.values()),
        "branch_delta_values_exact": all(set(r["delta"] for r in rr) == {-2,-1,0,1,2} for rr in by_m.values()),
        "selected_zero_mixed": all(v is None for v in selected_mixed.values()),
        "selected_cells_18": all(v == 18 for v in selected_cell_counts.values()),
        "selected_table_modifier_invariant": selected_tables[str(Z)] == selected_tables[str(X)],
        "minimum_cardinality_5": minimum_k == 5,
        "selected_is_minimum": list(SELECTED) in minimum_subsets,
        "all_four_subsets_refuted": len(four_counterexamples) == 330 and all(x["witness"] is not None for x in four_counterexamples),
        "paired_domain_4096": sum(paired_hist.values()) == 4096,
        "paired_range_pm4_all_values": set(paired_hist) == set(range(-4,5)),
        "paired_signature_cells_324": len(paired_cells) == 324,
        "paired_zero_mixed": paired_mixed == 0,
    }

    if all(gates.values()):
        terminal = POSITIVE
    elif not gates["parent_qg7c_terminal"] or not gates["padding_parent_negative"] or not gates["parent_info_source_bound"]:
        terminal = "QG22_PARENT_BINDING_GAP"
    elif not gates["selected_zero_mixed"] or not gates["paired_zero_mixed"]:
        terminal = "QG22_SELECTED_STATE_INSUFFICIENT__MIXED_DELTA_CELL_FOUND"
    elif minimum_k is not None and minimum_k < 5:
        terminal = "QG22_MINIMALITY_REFUTED__SMALLER_FROZEN_SIGNATURE_FOUND"
    else:
        terminal = "QG22_CANNOT_CHECK"

    out = {
        "schema": "ORIONQG.QG22.HiddenHomeState.v1",
        "issue": ISSUE,
        "terminal": terminal,
        "protocol_sha256": sha(PROTOCOL) if PROTOCOL.exists() else None,
        "parent": {
            "qg7c_sha256": sha(PARENT_QG7C),
            "padding_sha256": sha(PARENT_PAD),
            "information_closure_source_sha256": sha(Path(inspect.getfile(q7dinfo))),
            "pp_failures": parent_pp,
        },
        "frozen_predicates": list(PREDICATES),
        "selected_signature": list(SELECTED),
        "selected_cell_counts": selected_cell_counts,
        "selected_signature_tables": selected_tables,
        "selected_mixed": selected_mixed,
        "branch_delta_histograms": branch_hist,
        "minimum_determining_cardinality": minimum_k,
        "minimum_determining_subsets": minimum_subsets,
        "cardinality4_counterexamples": four_counterexamples,
        "paired": {
            "raw_states": 4096,
            "signature_cells": len(paired_cells),
            "mixed_cells": paired_mixed,
            "delta_histogram": {str(k):v for k,v in sorted(paired_hist.items())},
            "delta_min": min(paired_hist),
            "delta_max": max(paired_hist),
        },
        "compression": {
            "raw_branch_states": 64,
            "selected_branch_cells": selected_cell_counts[str(Z)],
            "raw_pair_states": 4096,
            "selected_pair_cells": len(paired_cells),
            "delta_only_branch_labels": len(set(r["delta"] for r in by_m[Z])),
            "delta_only_pair_labels": len(paired_hist),
        },
        "gates": gates,
        "all_gates": all(gates.values()),
        "scientific_scope": "EXACT_J5_HIDDEN_HOME_DELTA_STATE_ONLY",
        "all_n_theorem_authority": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "protected_subject_read": False,
    }
    unsigned = dict(out)
    out["result_digest"] = hashlib.sha256(canon(unsigned).encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({
        "terminal": terminal,
        "minimum_k": minimum_k,
        "minimum_subset_count": len(minimum_subsets),
        "branch_cells": selected_cell_counts,
        "pair_cells": len(paired_cells),
        "delta_range": [min(paired_hist), max(paired_hist)],
        "result_digest": out["result_digest"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
