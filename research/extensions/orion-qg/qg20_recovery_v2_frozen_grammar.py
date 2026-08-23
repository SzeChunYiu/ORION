#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import qg15_third_family as qg15  # noqa: E402
import qg15b_predicate_language as qg15b  # noqa: E402
from qg20_recovery_feature_search import FEATURE_NAMES, candidate_features  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
ARTIFACTS = REPO / "artifacts"
PROTOCOL = (
    REPO
    / "development"
    / "orion-qg-regime-geometry"
    / "QG20_RECOVERY_V2_FROZEN_GRAMMAR_RESIDUAL_PROTOCOL.md"
)
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-v2-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v2.json"
SELECTION_PREFIX = "ORIONQG_QG20_RECOVERY_V2_SELECTION="
RESULT_PREFIX = "ORIONQG_QG20_RECOVERY_V2="
FROZEN_CORE_FEATURE = "negative_weight_sum"
REMAINING = tuple(name for name in FEATURE_NAMES if name != FROZEN_CORE_FEATURE)


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def split_holdout(state: tuple[int, ...]) -> bool:
    raw = ",".join(str(value) for value in state).encode()
    prefix = hashlib.sha256(raw).hexdigest()[:8]
    return int(prefix, 16) % 5 == 0


def stats(rows, companions: tuple[str, ...]):
    groups = {}
    for base, feats, label in rows:
        key = base + (feats[FROZEN_CORE_FEATURE],) + tuple(feats[name] for name in companions)
        pair = groups.setdefault(key, [0, 0])
        pair[0 if label else 1] += 1
    return {
        "cells": len(groups),
        "mixed_cells": sum(bool(pos) and bool(neg) for pos, neg in groups.values()),
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
    }


def make_base_and_features(state: tuple[int, ...], n: int):
    _prep, cd, donor_feats, gates = qg15.donor(state, n)
    lb, rx, c = qg15.lower_bound(state, n)
    base = qg15b.stab_feature_vector(donor_feats, cd, lb, rx, c, n)
    return base, candidate_features(state, n, gates), cd


def choose(train_rows):
    core = stats(train_rows, ())
    per_arity = {}
    selected = None
    for arity in (1, 2):
        best = None
        best_names = None
        tested = 0
        for names in itertools.combinations(REMAINING, arity):
            tested += 1
            value = stats(train_rows, names)
            key = (value["floor"], value["mixed_cells"], value["cells"], names)
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
        selected = tuple(per_arity["2"]["best_names"])
    return core, per_arity, selected, stats(train_rows, selected)


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    n = 4
    dist = qg15.referee(n)
    if len(dist) != 36_720:
        raise SystemExit("n=4 exact domain drift")

    train_rows = []
    holdout_pending = []
    seen = set()
    for state in sorted(dist):
        holdout = split_holdout(state)
        if state in seen:
            raise AssertionError("duplicate state")
        seen.add(state)
        base, feats, cd = make_base_and_features(state, n)
        if holdout:
            # Deliberately retain state/base/features but do not materialize its gold label yet.
            holdout_pending.append((state, base, feats, cd))
        else:
            train_rows.append((base, feats, dist[state] == cd))
    if len(seen) != 36_720 or not train_rows or not holdout_pending:
        raise AssertionError("split coverage failure")

    core_train, per_arity, selected, selected_train = choose(train_rows)
    selection = {
        "schema": "orion-qg.qg20_recovery_v2_selection.v1",
        "protocol_sha256": protocol_sha,
        "core_feature": FROZEN_CORE_FEATURE,
        "remaining_prefrozen_grammar": list(REMAINING),
        "train_instances": len(train_rows),
        "holdout_instances": len(holdout_pending),
        "split_rule": "sha256(decimal_state_tuple)[:8] mod 5 == 0",
        "core_train_stats": core_train,
        "per_arity": per_arity,
        "selected_companions": list(selected),
        "selected_train_stats": selected_train,
        "holdout_labels_accessed": False,
    }
    selection["selection_digest"] = digest(selection)
    SELECTION.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(SELECTION_PREFIX + canonical(selection), flush=True)

    # Protected holdout opened only after the selection receipt is persisted and emitted.
    holdout_rows = [
        (base, feats, dist[state] == cd)
        for state, base, feats, cd in holdout_pending
    ]
    holdout_core = stats(holdout_rows, ())
    holdout_selected = stats(holdout_rows, selected)
    all_rows = train_rows + holdout_rows
    complete_selected = stats(all_rows, selected)

    if selected_train["floor"] == 0 and holdout_selected["floor"] == 0 and complete_selected["floor"] == 0:
        terminal = "QG20_RECOVERY_V2_PREFROZEN_COORDINATES_RESTORE_COMPLETE_N4_DETERMINATION"
    elif selected_train["floor"] == 0:
        terminal = "QG20_RECOVERY_V2_TRAIN_EXACT__HOLDOUT_MIXED"
    else:
        terminal = "QG20_RECOVERY_V2_NO_TWO_FEATURE_COMPANION__NEW_PHASE_DISTRIBUTION_STATE_REQUIRED"

    result = {
        "schema": "orion-qg.qg20_recovery_v2.v1",
        "protocol_sha256": protocol_sha,
        "selection": selection,
        "holdout_core_stats": holdout_core,
        "holdout_selected_stats": holdout_selected,
        "complete_selected_stats": complete_selected,
        "terminal": terminal,
        "new_feature_definitions_added": False,
        "all_n_authority": False,
        "novelty_authority": False,
    }
    result["result_digest"] = digest(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT_PREFIX + canonical(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
