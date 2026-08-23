#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QG = REPO / "research" / "extensions" / "orion-qg"
DEV = REPO / "development" / "orion-qg-regime-geometry"
sys.path.insert(0, str(QG))
sys.path.insert(0, str(DEV))

import qg15_third_family as qg15  # noqa: E402
from qg20_recovery_generic_verify import FEATURE_NAMES, independent_base  # noqa: E402

ARTIFACTS = REPO / "artifacts"
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-v2-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v2.json"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v2-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V2_VERIFY="
CORE = "negative_weight_sum"
REMAINING = tuple(name for name in FEATURE_NAMES if name != CORE)


def split_holdout(state: tuple[int, ...]) -> bool:
    raw = ",".join(str(value) for value in state).encode()
    return int(hashlib.sha256(raw).hexdigest()[:8], 16) % 5 == 0


def stats(rows, companions):
    groups = {}
    for base, feats, label in rows:
        key = base + (feats[CORE],) + tuple(feats[name] for name in companions)
        pos, neg = groups.get(key, (0, 0))
        groups[key] = (pos + int(label), neg + int(not label))
    return {
        "cells": len(groups),
        "mixed_cells": sum(bool(pos) and bool(neg) for pos, neg in groups.values()),
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
    }


def search(train_rows):
    per_arity = {}
    selected = None
    for arity in (1, 2):
        all_candidates = []
        for names in itertools.combinations(REMAINING, arity):
            value = stats(train_rows, names)
            all_candidates.append((value["floor"], value["mixed_cells"], value["cells"], names))
        best = min(all_candidates)
        per_arity[str(arity)] = {
            "tested": len(all_candidates),
            "best_names": list(best[3]),
            "floor": best[0],
            "mixed_cells": best[1],
            "cells": best[2],
        }
        if best[0] == 0:
            selected = tuple(best[3])
            break
    if selected is None:
        selected = tuple(per_arity["2"]["best_names"])
    return per_arity, selected, stats(train_rows, selected)


def main() -> int:
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if selection.get("holdout_labels_accessed") is not False:
        raise SystemExit("selection receipt did not seal holdout")
    if tuple(selection.get("remaining_prefrozen_grammar", ())) != REMAINING:
        raise SystemExit("prefrozen grammar drift")

    dist = qg15.referee(4)
    train_rows = []
    holdout_rows = []
    for state in sorted(dist):
        base, feats, label = independent_base(state, 4, dist)
        row = (base, feats, label)
        (holdout_rows if split_holdout(state) else train_rows).append(row)

    per_arity, chosen, train_selected = search(train_rows)
    holdout_core = stats(holdout_rows, ())
    holdout_selected = stats(holdout_rows, chosen)
    complete_selected = stats(train_rows + holdout_rows, chosen)
    core_train = stats(train_rows, ())

    checks = {
        "domain_36720": len(train_rows) + len(holdout_rows) == 36_720,
        "split_counts_agree": (
            len(train_rows) == selection.get("train_instances")
            and len(holdout_rows) == selection.get("holdout_instances")
        ),
        "core_train_stats_agree": core_train == selection.get("core_train_stats"),
        "per_arity_search_agrees": per_arity == selection.get("per_arity"),
        "selected_companions_agree": list(chosen) == selection.get("selected_companions"),
        "selected_train_stats_agree": train_selected == selection.get("selected_train_stats"),
        "holdout_core_stats_agree": holdout_core == result.get("holdout_core_stats"),
        "holdout_selected_stats_agree": holdout_selected == result.get("holdout_selected_stats"),
        "complete_selected_stats_agree": complete_selected == result.get("complete_selected_stats"),
        "independent_feature_implementation_used": True,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    payload = {
        "schema": "orion-qg.qg20_recovery_v2_verify.v1",
        "decision": decision,
        "checks": checks,
        "selected_companions": list(chosen),
        "train_stats": train_selected,
        "holdout_stats": holdout_selected,
        "complete_stats": complete_selected,
        "source_result_digest": result.get("result_digest"),
    }
    payload["verification_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if decision == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
