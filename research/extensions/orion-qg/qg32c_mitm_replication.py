#!/usr/bin/env python3
"""QG-32c independent exact <=4 fixed-probe replication via 2+2 meet-in-the-middle."""
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "development/orion-qg-regime-geometry"
sys.path.insert(0, str(DEV))
import qg32_generic_verify as base  # noqa:E402

PROTO = DEV / "QG32C_INDEPENDENT_MITM_REPLICATION_PROTOCOL_V1.md"
PARENT = ROOT / "research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg32c-mitm-replication.json"
TOKEN = "ORIONQG_QG32C="
YES = "QG32C_INDEPENDENT_REPLICATION_FINDS_FOUR_OR_FEWER_SEPARATOR"
NO = "QG32C_INDEPENDENT_REPLICATION_CONFIRMS_NO_FOUR_PROBE_SEPARATOR"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def shaf(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collapse(covers):
    groups = defaultdict(list)
    for p, c in enumerate(covers):
        if c:
            groups[int(c)].append(p)
    rows = [(c, min(ps), tuple(ps)) for c, ps in groups.items()]
    rows.sort(key=lambda e: (-e[0].bit_count(), e[1]))
    keep = []
    for row in rows:
        c = row[0]
        if any((c | d) == d for d, _, _ in keep):
            continue
        keep.append(row)
    keep.sort(key=lambda e: e[1])
    return keep


def build_halves(entries):
    first = {0: ()}
    for i, (c, _, _) in enumerate(entries):
        first.setdefault(int(c), (i,))
    for i in range(len(entries)):
        ci = int(entries[i][0])
        for j in range(i + 1, len(entries)):
            u = ci | int(entries[j][0])
            w = (i, j)
            if u not in first or w < first[u]:
                first[u] = w
    return sorted(((int(m), tuple(w)) for m, w in first.items()), key=lambda x: (len(x[1]), x[1], x[0]))


def solve(entries, npairs):
    U = (1 << npairs) - 1
    halves = build_halves(entries)
    post = [0] * npairs
    for hi, (mask, _) in enumerate(halves):
        marker = 1 << hi
        x = mask
        while x:
            low = x & -x
            post[low.bit_length() - 1] |= marker
            x -= low
    rare = sorted(range(npairs), key=lambda j: (post[j].bit_count(), j))
    all_halves = (1 << len(halves)) - 1
    tested = 0
    filters = 0
    max_survivors = 0
    for ai, (a, wa) in enumerate(halves):
        candidates = all_halves
        used = 0
        for j in rare:
            if ((a >> j) & 1) == 0:
                candidates &= post[j]
                used += 1
                if candidates == 0 or used == 8:
                    break
        filters += used
        max_survivors = max(max_survivors, candidates.bit_count())
        while candidates:
            low = candidates & -candidates
            bi = low.bit_length() - 1
            candidates -= low
            tested += 1
            b, wb = halves[bi]
            if (a | b) == U:
                chosen = tuple(sorted(set(wa) | set(wb)))
                physical = tuple(sorted(entries[i][1] for i in chosen))
                return True, physical, {
                    "half_union_count": len(halves), "halves_scanned": ai + 1,
                    "tested_survivors": tested, "posting_filters": filters,
                    "max_survivors_after_filter": max_survivors,
                }
    return False, (), {
        "half_union_count": len(halves), "halves_scanned": len(halves),
        "tested_survivors": tested, "posting_filters": filters,
        "max_survivors_after_filter": max_survivors,
    }


def covers_all(z, probes):
    rem = (1 << len(z["pairs"])) - 1
    for p in probes:
        rem &= ~int(z["covers"][p])
    return rem == 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, default=OUT); ns = ap.parse_args()
    z = base.construct(); entries = collapse(z["covers"])
    exists, witness, stats = solve(entries, len(z["pairs"]))
    parent = json.loads(PARENT.read_text())
    parent_ok = (
        parent.get("terminal") == "QG32_JOINT_SEPARATING_PROBE_UPPER_BOUND_ONLY"
        and parent.get("certified_probe_upper_bound") == 5
        and parent.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True
        and parent.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is False
    )
    recon = {
        "orbits": len(z["reps"]), "probes": z["mat"].shape[1], "joint_classes": len(z["joint"]),
        "unresolved_pairs": len(z["pairs"]), "nondominated_coverage_classes": len(entries),
    }
    recon_ok = recon == {"orbits":715,"probes":384,"joint_classes":92,"unresolved_pairs":5895,"nondominated_coverage_classes":168}
    witness_ok = (not exists) or (1 <= len(witness) <= 4 and covers_all(z, witness))
    terminal = YES if exists else NO
    if not parent_ok or not recon_ok or not witness_ok:
        terminal = "QG32C_CANNOT_CHECK"
    out = {
        "schema":"ORIONQG.QG32C.MITMReplication.v1", "issue":"SzeChunYiu/ORION#928",
        "terminal":terminal, "protocol_sha256":shaf(PROTO), "parent_qg32_sha256":shaf(PARENT),
        "parent_upper_bound_bound":parent_ok, "reconstruction":recon,
        "EXISTS_SEPARATOR_AT_MOST_4": exists if terminal in {YES,NO} else None,
        "witness_probe_indices":list(witness), "witness_size":len(witness),
        "witness_covers_all_unresolved_pairs":bool(exists and witness_ok),
        "independent_method":"EXACT_2_PLUS_2_MEET_IN_THE_MIDDLE_COVER_DECISION", "search":stats,
        "MINIMUM_FIXED_PROBE_CARDINALITY":5 if terminal==NO else None,
        "MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY":terminal==NO,
        "FOUR_OR_FEWER_SEPARATOR_WITNESS_AUTHORITY":terminal==YES,
        "ADAPTIVE_TREE_OPTIMALITY":False, "MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,
        "HARDWARE_MEASUREMENT_MINIMUM":False, "QG28_GLOBAL_STATE_MINIMALITY":False,
        "novelty_authority":False, "physical_quantum_advantage_claim":False,
    }
    raw = canon(out); out["result_digest"] = hashlib.sha256(raw.encode()).hexdigest()
    ns.output.parent.mkdir(parents=True, exist_ok=True); ns.output.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(TOKEN+canon({"terminal":terminal,"exists_le4":out["EXISTS_SEPARATOR_AT_MOST_4"],"witness":list(witness),"half_unions":stats["half_union_count"],"tested":stats["tested_survivors"],"result_digest":out["result_digest"]}))
    return 0
if __name__ == "__main__": raise SystemExit(main())
