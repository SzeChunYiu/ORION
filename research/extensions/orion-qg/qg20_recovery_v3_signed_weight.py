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

REPO = Path(__file__).resolve().parents[3]
ARTIFACTS = REPO / "artifacts"
PROTOCOL = (
    REPO
    / "development"
    / "orion-qg-regime-geometry"
    / "QG20_RECOVERY_V3_SIGNED_WEIGHT_PROTOCOL_V1.md"
)
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v3-signed-weight.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V3_SIGNED_WEIGHT="


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def signed_weight_vector(state: tuple[int, ...], n: int) -> tuple[int, ...]:
    mask = (1 << n) - 1
    coeffs = [0 for _ in range(n)]
    for encoded in state:
        z = encoded & mask
        x = (encoded >> n) & mask
        support = x | z
        weight = support.bit_count()
        if weight == 0:
            continue
        negative = encoded >> (2 * n)
        coeffs[weight - 1] += -1 if negative else 1
    return tuple(coeffs)


def map_stats(rows, mode: str):
    groups = {}
    for base, feats, signed, label in rows:
        if mode == "phi0":
            key = base
        elif mode == "phi1":
            key = base + (feats["negative_weight_sum"],)
        elif mode == "phi2":
            key = base + (
                feats["negative_weight_sum"],
                feats["n_negative"],
                feats["y_position_union"],
            )
        elif mode == "phi3":
            key = base + signed
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
        signed = signed_weight_vector(state, n)
        label = dist[state] == cd
        positives += int(label)
        rows.append((base, feats, signed, label))

    maps = {name: map_stats(rows, name) for name in ("phi0", "phi1", "phi2", "phi3")}
    terminal = (
        "QG20_RECOVERY_V3_SIGNED_WEIGHT_ENUMERATOR_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4"
        if maps["phi3"]["floor"] == 0 and maps["phi3"]["mixed_cells"] == 0
        else "QG20_RECOVERY_V3_SIMPLE_SIGNED_WEIGHT_NONIDENTIFYING__COMPLETE_ENUMERATOR_OR_QUOTIENT_REQUIRED"
    )
    payload = {
        "schema": "orion-qg.qg20_recovery_v3_signed_weight.v1",
        "protocol_sha256": protocol_sha,
        "n": n,
        "instances": len(rows),
        "positives": positives,
        "representation": "SIGNED_WEIGHT_V1=(S_1,S_2,S_3,S_4)",
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
