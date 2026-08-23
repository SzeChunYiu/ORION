#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import heapq
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import qg15_third_family as qg15  # noqa: E402
import qg15b_predicate_language as qg15b  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
ARTIFACTS = REPO / "artifacts"
PROTOCOL = REPO / "development" / "orion-qg-regime-geometry" / "QG20_RECOVERY_V5_N5_COLLISION_PROTOCOL_V1.md"
SELECTION = ARTIFACTS / "orion-qg-qg20-recovery-v5-n5-selection.json"
RESULT = ARTIFACTS / "orion-qg-qg20-recovery-v5-n5.json"
SP = "ORIONQG_QG20_RECOVERY_V5_N5_SELECTION="
RP = "ORIONQG_QG20_RECOVERY_V5_N5="

N = 5
SEED = 2026082305
WALK_LENGTH = 14
POOL_CAP = 100_000
GROUPS_REQUIRED = 32
STATES_PER_GROUP = 2
TRIPLES = tuple(
    (a, b, c)
    for a in range(N + 1)
    for b in range(N + 1)
    for c in range(N + 1)
    if 1 <= a + b + c <= N
)


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def signed_complete_vector(state: tuple[int, ...], n: int = N) -> tuple[int, ...]:
    mask = (1 << n) - 1
    coeff = {t: 0 for t in TRIPLES}
    for raw in state:
        z = raw & mask
        x = (raw >> n) & mask
        triple = (
            (x & ~z & mask).bit_count(),
            (x & z).bit_count(),
            (z & ~x & mask).bit_count(),
        )
        if triple != (0, 0, 0):
            coeff[triple] += -1 if raw >> (2 * n) else 1
    return tuple(coeff[t] for t in TRIPLES)


def representation_key(state: tuple[int, ...], n: int = N):
    _prep, cd, feats, _gates = qg15.donor(state, n)
    lb, rx, c = qg15.lower_bound(state, n)
    base = qg15b.stab_feature_vector(feats, cd, lb, rx, c, n)
    return base + signed_complete_vector(state, n), cd


def build_label_blind_selection():
    ctx = qg15.make_ctx(N)
    rng = random.Random(SEED)
    seen = set()
    groups: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    donor_cost: dict[tuple[int, ...], int] = {}
    stop_index = 0
    for index in range(1, POOL_CAP + 1):
        state = qg15.start_state(N)
        for _ in range(WALK_LENGTH):
            state = qg15.apply_state(state, rng.choice(ctx["gates"]), N)
        if state in seen:
            continue
        seen.add(state)
        key, cd = representation_key(state, N)
        groups[key].append(state)
        donor_cost[state] = cd
        stop_index = index
        collision_count = sum(len(items) >= STATES_PER_GROUP for items in groups.values())
        if collision_count >= GROUPS_REQUIRED:
            break

    collision_keys = [key for key, items in groups.items() if len(items) >= STATES_PER_GROUP]
    if len(collision_keys) < GROUPS_REQUIRED:
        return None, {
            "pool_unique_states": len(seen),
            "stream_stop_index": stop_index,
            "collision_groups_available": len(collision_keys),
        }
    collision_keys.sort(key=lambda key: canonical(list(key)))
    chosen_keys = collision_keys[:GROUPS_REQUIRED]
    selected_groups = []
    targets = []
    for key in chosen_keys:
        states = sorted(groups[key])[:STATES_PER_GROUP]
        targets.extend(states)
        selected_groups.append({
            "representation_key_sha256": hashlib.sha256(canonical(list(key)).encode()).hexdigest(),
            "state_digests": [hashlib.sha256(canonical(list(s)).encode()).hexdigest() for s in states],
            "states": [list(s) for s in states],
            "donor_costs": [donor_cost[s] for s in states],
        })
    return tuple(targets), {
        "pool_unique_states": len(seen),
        "stream_stop_index": stop_index,
        "collision_groups_available": len(collision_keys),
        "selected_groups": selected_groups,
    }


def targeted_dijkstra(targets: tuple[tuple[int, ...], ...]):
    target_set = set(targets)
    ctx = qg15.make_ctx(N)
    start = qg15.start_state(N)
    dist = {start: 0}
    heap = [(0, start)]
    settled = {}
    settled_states = 0
    while heap and len(settled) < len(target_set):
        d, state = heapq.heappop(heap)
        if d != dist.get(state):
            continue
        settled_states += 1
        if state in target_set:
            settled[state] = d
        for gate in ctx["gates"]:
            nxt = qg15.apply_state(state, gate, N)
            nd = d + qg15.COST[gate[0]]
            if nd < dist.get(nxt, 1 << 60):
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    return settled, {
        "settled_state_count": settled_states,
        "discovered_state_count": len(dist),
        "targets_settled": len(settled),
        "max_settled_target_cost": max(settled.values(), default=None),
    }


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    targets, pre = build_label_blind_selection()
    selection = {
        "schema": "orion-qg.qg20_recovery_v5_n5_selection.v1",
        "protocol_sha256": protocol_sha,
        "n": N,
        "seed": SEED,
        "walk_length": WALK_LENGTH,
        "pool_cap": POOL_CAP,
        "groups_required": GROUPS_REQUIRED,
        "states_per_group": STATES_PER_GROUP,
        "coefficient_triples": [list(t) for t in TRIPLES],
        **pre,
        "exact_labels_accessed": False,
    }
    selection["selection_digest"] = digest(selection)
    SELECTION.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n")
    print(SP + canonical(selection), flush=True)

    if targets is None:
        result = {
            "schema": "orion-qg.qg20_recovery_v5_n5.v1",
            "selection_digest": selection["selection_digest"],
            "terminal": "CANNOT_CHECK_N5_COLLISION_DENSITY",
            "novelty_authority": False,
            "all_n_authority": False,
        }
        result["result_digest"] = digest(result)
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(RP + canonical(result))
        return 0

    exact, search_stats = targeted_dijkstra(targets)
    if len(exact) != len(set(targets)):
        terminal = "CANNOT_CHECK_EXACT_N5_RESOURCE"
        result = {
            "schema": "orion-qg.qg20_recovery_v5_n5.v1",
            "selection_digest": selection["selection_digest"],
            "search": search_stats,
            "terminal": terminal,
            "novelty_authority": False,
            "all_n_authority": False,
        }
        result["result_digest"] = digest(result)
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(RP + canonical(result))
        return 0

    exact_count = 0
    inexact_count = 0
    mixed = 0
    floor = 0
    group_results = []
    for group in selection["selected_groups"]:
        states = [tuple(values) for values in group["states"]]
        labels = []
        exact_costs = []
        for state, cd in zip(states, group["donor_costs"], strict=True):
            opt = exact[state]
            label = cd == opt
            labels.append(label)
            exact_costs.append(opt)
            exact_count += int(label)
            inexact_count += int(not label)
        pos = sum(labels)
        neg = len(labels) - pos
        mixed += int(pos > 0 and neg > 0)
        floor += min(pos, neg)
        group_results.append({
            "representation_key_sha256": group["representation_key_sha256"],
            "state_digests": group["state_digests"],
            "donor_costs": group["donor_costs"],
            "exact_costs": exact_costs,
            "labels": labels,
        })

    if exact_count < 4 or inexact_count < 4:
        terminal = "CANNOT_CHECK_LABEL_DIVERSITY"
    elif mixed:
        terminal = "QG20_RECOVERY_V5_SIGNED_COMPLETE_WEIGHT_REFUTED_BY_N5_COLLISION"
    else:
        terminal = "QG20_RECOVERY_V5_SIGNED_COMPLETE_WEIGHT_SURVIVES_N5_COLLISION_CHALLENGE"
    result = {
        "schema": "orion-qg.qg20_recovery_v5_n5.v1",
        "selection_digest": selection["selection_digest"],
        "search": search_stats,
        "target_count": len(targets),
        "exact_label_count": exact_count,
        "inexact_label_count": inexact_count,
        "mixed_groups": mixed,
        "error_floor": floor,
        "group_results": group_results,
        "terminal": terminal,
        "representation_changed_after_v4": False,
        "novelty_authority": False,
        "all_n_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["result_digest"] = digest(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(RP + canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
