#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import qg15_third_family as qg15  # noqa: E402
import qg15b_predicate_language as qg15b  # noqa: E402
from qg20_recovery_feature_search import candidate_features  # noqa: E402
from qg20_recovery_v3_signed_weight import signed_weight_vector  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
ARTIFACTS = REPO / "artifacts"
PROTOCOL = REPO / "development" / "orion-qg-regime-geometry" / "QG20_RECOVERY_V4_SIGNED_COMPLETE_WEIGHT_PROTOCOL_V1.md"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V4_SIGNED_COMPLETE="

TRIPLES = tuple(
    (a, b, c)
    for a in range(5)
    for b in range(5)
    for c in range(5)
    if 1 <= a + b + c <= 4
)


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def signed_complete_vector(state: tuple[int, ...], n: int) -> tuple[int, ...]:
    mask = (1 << n) - 1
    counts = {triple: 0 for triple in TRIPLES}
    for encoded in state:
        z = encoded & mask
        x = (encoded >> n) & mask
        y = x & z
        x_only = x & ~z & mask
        z_only = z & ~x & mask
        triple = (x_only.bit_count(), y.bit_count(), z_only.bit_count())
        if triple == (0, 0, 0):
            continue
        counts[triple] += -1 if (encoded >> (2 * n)) else 1
    return tuple(counts[t] for t in TRIPLES)


def stats(rows, mode: str):
    groups = {}
    for base, feats, simple, complete, label in rows:
        if mode == "phi0":
            key = base
        elif mode == "phi1":
            key = base + (feats["negative_weight_sum"],)
        elif mode == "phi2":
            key = base + (feats["negative_weight_sum"], feats["n_negative"], feats["y_position_union"])
        elif mode == "phi3":
            key = base + simple
        elif mode == "phi4":
            key = base + complete
        else:
            raise ValueError(mode)
        pair = groups.setdefault(key, [0, 0])
        pair[0 if label else 1] += 1
    return {
        "cells": len(groups),
        "mixed_cells": sum(bool(pos) and bool(neg) for pos, neg in groups.values()),
        "floor": sum(min(pos, neg) for pos, neg in groups.values()),
    }


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    n = 4
    dist = qg15.referee(n)
    if len(dist) != 36_720:
        raise SystemExit("complete n=4 domain drift")
    rows = []
    positives = 0
    for state in sorted(dist):
        _prep, cd, donor_feats, gates = qg15.donor(state, n)
        lb, rx, c = qg15.lower_bound(state, n)
        base = qg15b.stab_feature_vector(donor_feats, cd, lb, rx, c, n)
        feats = candidate_features(state, n, gates)
        simple = signed_weight_vector(state, n)
        complete = signed_complete_vector(state, n)
        label = dist[state] == cd
        positives += int(label)
        rows.append((base, feats, simple, complete, label))
    maps = {name: stats(rows, name) for name in ("phi0", "phi1", "phi2", "phi3", "phi4")}
    terminal = (
        "QG20_RECOVERY_V4_SIGNED_COMPLETE_WEIGHT_ENUMERATOR_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4"
        if maps["phi4"]["floor"] == 0 and maps["phi4"]["mixed_cells"] == 0
        else "QG20_RECOVERY_V4_COMPLETE_ENUMERATOR_NONIDENTIFYING__EXACT_QUOTIENT_REQUIRED"
    )
    payload = {
        "schema": "orion-qg.qg20_recovery_v4_signed_complete.v1",
        "protocol_sha256": protocol_sha,
        "n": n,
        "instances": len(rows),
        "positives": positives,
        "representation": "SIGNED_COMPLETE_WEIGHT_V1",
        "coefficient_triples": [list(t) for t in TRIPLES],
        "coefficient_count": len(TRIPLES),
        "feature_search_performed": False,
        "maps": maps,
        "terminal": terminal,
        "same_domain_recovery": True,
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
