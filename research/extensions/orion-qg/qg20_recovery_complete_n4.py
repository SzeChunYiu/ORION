#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
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
    / "QG20_RECOVERY_COMPLETE_N4_CONFIRMATION_PROTOCOL_V1.md"
)
OUT = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4.json"
PREFIX = "ORIONQG_QG20_RECOVERY_COMPLETE_N4="
FROZEN_FEATURE = "negative_weight_sum"
DISCOVERY_DUAL_DIGEST = "804aacd8794daae3ba46ac33251725175c3a588f09791e3b70fb1bbaa71e22d2"


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def stats(rows, augmented: bool):
    groups: dict[tuple, list[int]] = {}
    for base, negative_weight_sum, label in rows:
        key = base + ((negative_weight_sum,) if augmented else ())
        counts = groups.setdefault(key, [0, 0])
        counts[0 if label else 1] += 1
    return {
        "cells": len(groups),
        "mixed_cells": sum(pos and neg for pos, neg in groups.values()),
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
    }


def negative_weight_sum(state: tuple[int, ...], n: int) -> int:
    mask = (1 << n) - 1
    total = 0
    for encoded in state:
        sign = encoded >> (2 * n)
        if sign:
            z = encoded & mask
            x = (encoded >> n) & mask
            total += (x | z).bit_count()
    return total


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    n = 4
    dist = qg15.referee(n)
    if len(dist) != 36_720 or len(dist) != qg15.expected_count(n):
        raise SystemExit(f"unexpected complete n=4 domain size: {len(dist)}")

    rows = []
    positives = 0
    for state in sorted(dist):
        _prep, cd, donor_feats, _gates = qg15.donor(state, n)
        lb, rx, c = qg15.lower_bound(state, n)
        base = qg15b.stab_feature_vector(donor_feats, cd, lb, rx, c, n)
        label = dist[state] == cd
        positives += int(label)
        rows.append((base, negative_weight_sum(state, n), label))

    base_stats = stats(rows, augmented=False)
    augmented_stats = stats(rows, augmented=True)
    terminal = (
        "QG20_RECOVERY_NEGATIVE_WEIGHT_SUM_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4"
        if augmented_stats["floor"] == 0 and augmented_stats["mixed_cells"] == 0
        else "QG20_RECOVERY_NEGATIVE_WEIGHT_SUM_REFUTED_COMPLETE_N4"
    )
    payload = {
        "schema": "orion-qg.qg20_recovery_complete_n4.v1",
        "protocol_sha256": protocol_sha,
        "discovery_dual_digest": DISCOVERY_DUAL_DIGEST,
        "frozen_feature": FROZEN_FEATURE,
        "n": n,
        "instances": len(rows),
        "positives": positives,
        "base": base_stats,
        "augmented": augmented_stats,
        "terminal": terminal,
        "feature_search_performed": False,
        "all_n_authority": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    payload["result_digest"] = hashlib.sha256(canonical(payload).encode()).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + canonical(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
