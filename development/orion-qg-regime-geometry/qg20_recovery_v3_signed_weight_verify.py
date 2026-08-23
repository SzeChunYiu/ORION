#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QG = REPO / "research" / "extensions" / "orion-qg"
DEV = REPO / "development" / "orion-qg-regime-geometry"
sys.path.insert(0, str(QG))
sys.path.insert(0, str(DEV))

import qg15_third_family as qg15  # noqa: E402
from qg20_recovery_generic_verify import independent_base  # noqa: E402

ARTIFACTS = REPO / "artifacts"
SOURCE = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight.json"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V3_SIGNED_WEIGHT_VERIFY="


def signed_vector_direct(state: tuple[int, ...], n: int) -> tuple[int, ...]:
    mask = (1 << n) - 1
    positive = [0] * (n + 1)
    negative = [0] * (n + 1)
    for raw in state:
        z = raw & mask
        x = (raw >> n) & mask
        weight = (x | z).bit_count()
        if raw >> (2 * n):
            negative[weight] += 1
        else:
            positive[weight] += 1
    return tuple(positive[w] - negative[w] for w in range(1, n + 1))


def negative_weight_sum_direct(state: tuple[int, ...], n: int) -> int:
    mask = (1 << n) - 1
    total = 0
    for raw in state:
        if raw >> (2 * n):
            total += (((raw >> n) & mask) | (raw & mask)).bit_count()
    return total


def n_negative_direct(state: tuple[int, ...], n: int) -> int:
    return sum(bool(raw >> (2 * n)) for raw in state)


def y_union_direct(state: tuple[int, ...], n: int) -> int:
    mask = (1 << n) - 1
    union = 0
    for raw in state:
        z = raw & mask
        x = (raw >> n) & mask
        union |= x & z
    return union.bit_count()


def summarize(rows, mode: str):
    groups = {}
    for base, core, nneg, yunion, signed, label in rows:
        if mode == "phi0":
            key = base
        elif mode == "phi1":
            key = base + (core,)
        elif mode == "phi2":
            key = base + (core, nneg, yunion)
        elif mode == "phi3":
            key = base + signed
        else:
            raise ValueError(mode)
        pos, neg = groups.get(key, (0, 0))
        groups[key] = (pos + int(label), neg + int(not label))
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
        base, _feats, label = independent_base(state, n, dist)
        positives += int(label)
        rows.append((
            base,
            negative_weight_sum_direct(state, n),
            n_negative_direct(state, n),
            y_union_direct(state, n),
            signed_vector_direct(state, n),
            label,
        ))
    maps = {name: summarize(rows, name) for name in ("phi0", "phi1", "phi2", "phi3")}
    checks = {
        "domain_36720": len(rows) == 36_720,
        "positive_count_agrees": positives == source.get("positives"),
        "representation_identity": source.get("representation") == "SIGNED_WEIGHT_V1=(S_1,S_2,S_3,S_4)",
        "no_feature_search": source.get("feature_search_performed") is False,
        "all_map_stats_agree": maps == source.get("maps"),
        "independent_signed_weight_implementation": True,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    payload = {
        "schema": "orion-qg.qg20_recovery_v3_signed_weight_verify.v1",
        "decision": decision,
        "checks": checks,
        "rebuilt_maps": maps,
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
