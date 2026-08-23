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
SOURCE = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete.json"
OUT = ARTIFACTS / "orion-qg-qg20-recovery-v4-signed-complete-verification.json"
PREFIX = "ORIONQG_QG20_RECOVERY_V4_SIGNED_COMPLETE_VERIFY="
TRIPLES = tuple((a, b, c) for a in range(5) for b in range(5) for c in range(5) if 1 <= a + b + c <= 4)


def simple_direct(state, n):
    mask = (1 << n) - 1
    coeff = [0] * n
    for raw in state:
        support = (raw & mask) | ((raw >> n) & mask)
        w = support.bit_count()
        if w:
            coeff[w - 1] += -1 if raw >> (2 * n) else 1
    return tuple(coeff)


def complete_direct(state, n):
    mask = (1 << n) - 1
    coeff = {t: 0 for t in TRIPLES}
    for raw in state:
        z = raw & mask
        x = (raw >> n) & mask
        nx = (x & ~z & mask).bit_count()
        ny = (x & z).bit_count()
        nz = (z & ~x & mask).bit_count()
        t = (nx, ny, nz)
        if t != (0, 0, 0):
            coeff[t] += -1 if raw >> (2 * n) else 1
    return tuple(coeff[t] for t in TRIPLES)


def core_direct(state, n):
    mask = (1 << n) - 1
    nneg = 0
    negsum = 0
    yunion = 0
    for raw in state:
        z = raw & mask
        x = (raw >> n) & mask
        yunion |= x & z
        if raw >> (2 * n):
            nneg += 1
            negsum += (x | z).bit_count()
    return negsum, nneg, yunion.bit_count()


def summarize(rows, mode):
    groups = {}
    for base, core, simple, complete, label in rows:
        if mode == "phi0": key = base
        elif mode == "phi1": key = base + (core[0],)
        elif mode == "phi2": key = base + core
        elif mode == "phi3": key = base + simple
        elif mode == "phi4": key = base + complete
        else: raise ValueError(mode)
        pos, neg = groups.get(key, (0, 0))
        groups[key] = (pos + int(label), neg + int(not label))
    return {"cells": len(groups), "mixed_cells": sum(bool(p) and bool(n) for p,n in groups.values()), "floor": sum(min(p,n) for p,n in groups.values())}


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    dist = qg15.referee(4)
    rows = []
    positives = 0
    for state in sorted(dist):
        base, _feats, label = independent_base(state, 4, dist)
        positives += int(label)
        rows.append((base, core_direct(state, 4), simple_direct(state, 4), complete_direct(state, 4), label))
    maps = {name: summarize(rows, name) for name in ("phi0","phi1","phi2","phi3","phi4")}
    checks = {
        "domain_36720": len(rows) == 36_720,
        "positive_count_agrees": positives == source.get("positives"),
        "representation_identity": source.get("representation") == "SIGNED_COMPLETE_WEIGHT_V1",
        "coefficient_triples_complete": source.get("coefficient_triples") == [list(t) for t in TRIPLES],
        "coefficient_count_agrees": source.get("coefficient_count") == len(TRIPLES),
        "no_feature_search": source.get("feature_search_performed") is False,
        "all_map_stats_agree": maps == source.get("maps"),
        "independent_complete_enumerator_implementation": True,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    payload = {"schema":"orion-qg.qg20_recovery_v4_signed_complete_verify.v1","decision":decision,"checks":checks,"rebuilt_maps":maps,"source_result_digest":source.get("result_digest")}
    payload["verification_digest"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if decision == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
