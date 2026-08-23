#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QG = REPO / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG))

import qg15_third_family as qg15  # noqa: E402

ARTIFACTS = REPO / "artifacts"
SOURCE = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4.json"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-complete-n4-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_COMPLETE_N4_VERIFY="


def feature_direct(state: tuple[int, ...], n: int) -> int:
    mask = (1 << n) - 1
    total = 0
    for raw in state:
        if raw >> (2 * n):
            support = (raw & mask) | ((raw >> n) & mask)
            total += support.bit_count()
    return total


def base_direct(state: tuple[int, ...], n: int):
    _prep, cd, feats, _gates = qg15.donor(state, n)
    lb, rx, c = qg15.lower_bound(state, n)
    return (
        feats["nCZ"], feats["nY"], feats["nSignX"], feats["nSignZ"],
        feats["nCN"], cd, rx, c, lb, cd - lb, n - c,
        feats["nCN"] - (n - 1), cd - 2 * n,
    ), cd


def summarize(rows, augmented):
    groups = {}
    for base, feat, label in rows:
        key = base + ((feat,) if augmented else ())
        pair = groups.setdefault(key, [0, 0])
        pair[0 if label else 1] += 1
    return {
        "cells": len(groups),
        "mixed_cells": sum(bool(pos) and bool(neg) for pos, neg in groups.values()),
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
    }


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    n = 4
    dist = qg15.referee(n)
    rows = []
    positives = 0
    for state in sorted(dist):
        base, cd = base_direct(state, n)
        label = dist[state] == cd
        positives += int(label)
        rows.append((base, feature_direct(state, n), label))
    rebuilt = {
        "instances": len(rows),
        "positives": positives,
        "base": summarize(rows, False),
        "augmented": summarize(rows, True),
    }
    checks = {
        "complete_domain_count_36720": rebuilt["instances"] == 36_720,
        "source_count_agrees": rebuilt["instances"] == source.get("instances"),
        "positive_count_agrees": rebuilt["positives"] == source.get("positives"),
        "base_stats_agree": rebuilt["base"] == source.get("base"),
        "augmented_stats_agree": rebuilt["augmented"] == source.get("augmented"),
        "frozen_feature_identity": source.get("frozen_feature") == "negative_weight_sum",
        "no_feature_search": source.get("feature_search_performed") is False,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    payload = {
        "schema": "orion-qg.qg20_recovery_complete_n4_verify.v1",
        "decision": decision,
        "checks": checks,
        "rebuilt": rebuilt,
        "source_result_digest": source.get("result_digest"),
    }
    payload["verification_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if decision == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
