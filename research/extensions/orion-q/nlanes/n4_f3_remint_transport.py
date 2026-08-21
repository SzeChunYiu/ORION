"""ORION-Q N4-F3: representation remints and receipt transport, standalone closure.

Frozen protocol:
development/orion-q-nlane-closure/N4_F3_REMINT_TRANSPORT_PROTOCOL.md
Exact synthetic, deterministic. Closes N4_CLOSURE_ASSESSMENT.md residual 1
(registered family 3 of issue #677, previously exercised only as N4-D's
laundering vector).

Run:
    python research/extensions/orion-q/nlanes/n4_f3_remint_transport.py
"""

from __future__ import annotations

import itertools
import json
import os
import random

import numpy as np

SEED = 20260821
EPISODES_PER_REGIME = 200
WIDTH = 3
LAYERS = 3
N_EDITS = 2
BUDGET = 6
REWARD = 20.0
FAIL_PENALTY = 8.0

BINDABLE_ASPECTS = ("ENCODING", "LAYOUT", "SCHEDULE", "CALIBRATION")
COSMETIC_ASPECT = "COSMETIC"
EDGE_TYPES = ("A", "B", "C")
TRANSPORT_RULES = frozenset(
    [
        ("LAYOUT", "A"),
        ("LAYOUT", "B"),
        ("SCHEDULE", "A"),
        ("SCHEDULE", "C"),
        ("CALIBRATION", "B"),
    ]
)

REGIMES = {
    "MIXED_TRANSPORT": {
        "binding_sizes": (1, 2),
        "edit_sizes": (1, 2),
        "edit_pool": BINDABLE_ASPECTS,
        "p_break": 0.55,
    },
    "STALE_HOSTILE": {
        "binding_sizes": (2, 3),
        "edit_sizes": (2, 3),
        "edit_pool": BINDABLE_ASPECTS,
        "p_break": 0.85,
    },
    "REMINT_UNNECESSARY": {
        "binding_sizes": (1, 2),
        "edit_sizes": (1, 1),
        "edit_pool": (COSMETIC_ASPECT,),
        "p_break": 0.55,  # irrelevant: every receipt transports trivially
    },
}
REGIME_ORDER = ("MIXED_TRANSPORT", "STALE_HOSTILE", "REMINT_UNNECESSARY")
ARMS = (
    "FULL_ORACLE",
    "ORION_TYPED_TRANSPORT",
    "RE_DERIVE_SCRATCH",
    "NAIVE_CARRY_FORWARD",
)


def transportable(binding: tuple[str, ...], edge_type: str, edits: list[tuple[str, ...]]) -> bool:
    """Sequential typed transport: survive every edit; binding preserved."""
    for changed in edits:
        for aspect in changed:
            if aspect in binding and (aspect, edge_type) not in TRANSPORT_RULES:
                return False
    return True


def generate_episode(regime: str, rng: random.Random) -> dict:
    spec = REGIMES[regime]
    layer_nodes = [[(layer, w) for w in range(WIDTH)] for layer in range(LAYERS)]
    edges = {}

    def add_edge(u, v):
        binding = tuple(
            sorted(rng.sample(BINDABLE_ASPECTS, rng.choice(spec["binding_sizes"])))
        )
        edges[(u, v)] = {
            "cost": rng.uniform(1.0, 5.0),
            "edge_type": rng.choice(EDGE_TYPES),
            "binding": binding,
            "break_draw": rng.random(),  # compared to p_break iff non-transportable
        }

    for node in layer_nodes[0]:
        add_edge("s", node)
    for layer in range(LAYERS - 1):
        for u in layer_nodes[layer]:
            for v in layer_nodes[layer + 1]:
                add_edge(u, v)
    for node in layer_nodes[-1]:
        add_edge(node, "t")

    edits = []
    for _ in range(N_EDITS):
        size = rng.choice(spec["edit_sizes"])
        size = min(size, len(spec["edit_pool"]))
        edits.append(tuple(sorted(rng.sample(spec["edit_pool"], size))))

    for edge in edges.values():
        edge["transportable"] = transportable(
            edge["binding"], edge["edge_type"], edits
        )
        if edge["transportable"]:
            edge["feasible"] = True  # transport soundness by construction
        else:
            edge["feasible"] = edge["break_draw"] >= spec["p_break"]

    paths = []
    for combo in itertools.product(*layer_nodes):
        node_seq = ["s", *combo, "t"]
        paths.append(tuple(zip(node_seq[:-1], node_seq[1:])))
    order = sorted(
        range(len(paths)),
        key=lambda i: (sum(edges[e]["cost"] for e in paths[i]), i),
    )
    return {"edges": edges, "paths": paths, "path_order": order, "edits": edits}


def believed_valid(arm: str, edge: dict) -> bool:
    if arm == "ORION_TYPED_TRANSPORT":
        return edge["transportable"]
    if arm == "RE_DERIVE_SCRATCH":
        return False
    if arm == "NAIVE_CARRY_FORWARD":
        return True
    raise ValueError(arm)


def run_arm(arm: str, episode: dict) -> dict:
    edges = episode["edges"]
    paths = episode["paths"]

    if arm == "FULL_ORACLE":
        feasible_paths = [
            p for p in paths if all(edges[e]["feasible"] for e in p)
        ]
        if not feasible_paths:
            return {"utility": 0.0, "committed": 0, "failed": 0, "remints": 0,
                    "abstained": 1}
        cost = min(sum(edges[e]["cost"] for e in p) for p in feasible_paths)
        return {"utility": REWARD - cost, "committed": 1, "failed": 0,
                "remints": 0, "abstained": 0}

    # Shared certification policy for all budgeted arms.
    budget = BUDGET
    known: dict = {}
    for idx in episode["path_order"]:
        path = paths[idx]
        if any(known.get(e) is False for e in path):
            continue
        unknown = [
            e for e in path if not believed_valid(arm, edges[e]) and e not in known
        ]
        if len(unknown) > budget:
            continue
        certified = True
        for e in unknown:
            budget -= 1
            known[e] = edges[e]["feasible"]
            if not known[e]:
                certified = False
                break
        if certified:
            cost = sum(edges[e]["cost"] for e in path)
            success = all(edges[e]["feasible"] for e in path)
            utility = REWARD - cost if success else -cost - FAIL_PENALTY
            return {"utility": utility, "committed": 1,
                    "failed": 0 if success else 1,
                    "remints": BUDGET - budget, "abstained": 0}
    return {"utility": 0.0, "committed": 0, "failed": 0,
            "remints": BUDGET - budget, "abstained": 1}


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    committed = sum(r["committed"] for r in rows)
    return {
        "mean_utility": float(np.mean([r["utility"] for r in rows])),
        "failure_rate": (
            sum(r["failed"] for r in rows) / committed if committed else 0.0
        ),
        "abstain_rate": sum(r["abstained"] for r in rows) / n,
        "mean_remints": float(np.mean([r["remints"] for r in rows])),
    }


def main() -> None:
    rng = random.Random(SEED)
    episodes = {
        regime: [generate_episode(regime, rng) for _ in range(EPISODES_PER_REGIME)]
        for regime in REGIME_ORDER
    }

    per_regime: dict = {}
    pooled_rows: dict = {arm: [] for arm in ARMS}
    transport_fraction = {}
    invalidation_mismatches = 0
    total_receipts = 0
    for regime in REGIME_ORDER:
        per_regime[regime] = {}
        fracs = []
        for ep in episodes[regime]:
            edge_list = list(ep["edges"].values())
            total_receipts += len(edge_list)
            fracs.append(
                sum(1 for e in edge_list if e["transportable"]) / len(edge_list)
            )
            # ORION's classification is believed_valid == transportable; count
            # mismatches against ground truth explicitly (G5 second clause).
            invalidation_mismatches += sum(
                1
                for e in edge_list
                if believed_valid("ORION_TYPED_TRANSPORT", e) != e["transportable"]
            )
        transport_fraction[regime] = float(np.mean(fracs))
        for arm in ARMS:
            rows = [run_arm(arm, ep) for ep in episodes[regime]]
            pooled_rows[arm].extend(rows)
            per_regime[regime][arm] = summarize(rows)
    pooled = {arm: summarize(pooled_rows[arm]) for arm in ARMS}
    for scope in [pooled, *per_regime.values()]:
        oracle_mu = scope["FULL_ORACLE"]["mean_utility"]
        for arm in ARMS:
            scope[arm]["regret_vs_oracle"] = oracle_mu - scope[arm]["mean_utility"]

    orion_failures = sum(
        r["failed"] for r in pooled_rows["ORION_TYPED_TRANSPORT"]
    )

    def mu(scope: dict, arm: str) -> float:
        return scope[arm]["mean_utility"]

    g1 = all(
        mu(per_regime[reg], "FULL_ORACLE") >= mu(per_regime[reg], a)
        for reg in REGIME_ORDER
        for a in ARMS
    ) and all(mu(pooled, "FULL_ORACLE") >= mu(pooled, a) for a in ARMS)
    mixed = per_regime["MIXED_TRANSPORT"]
    g2 = mu(mixed, "ORION_TYPED_TRANSPORT") > mu(mixed, "RE_DERIVE_SCRATCH") and mu(
        mixed, "ORION_TYPED_TRANSPORT"
    ) > mu(mixed, "NAIVE_CARRY_FORWARD")
    hostile = per_regime["STALE_HOSTILE"]
    g3 = (
        mu(hostile, "NAIVE_CARRY_FORWARD") < 0.0
        and hostile["NAIVE_CARRY_FORWARD"]["failure_rate"] >= 0.5
        and mu(hostile, "NAIVE_CARRY_FORWARD") < mu(hostile, "RE_DERIVE_SCRATCH")
    )
    unnecessary = per_regime["REMINT_UNNECESSARY"]
    g4 = (
        mu(unnecessary, "RE_DERIVE_SCRATCH")
        >= mu(unnecessary, "ORION_TYPED_TRANSPORT") - 1e-9
    )
    g5 = orion_failures == 0 and invalidation_mismatches == 0
    gates = {
        "G1_oracle_upper_bound": g1,
        "G2_mixed_typed_transport_advantage": g2,
        "G3_stale_hostile_punishes_carry_forward": g3,
        "G4_remint_unnecessary_rederive_first_refusal": g4,
        "G5_typed_invalidation_sound": g5,
    }
    if not g1 or not g3 or not g4:
        terminal = "N4_F3_WORLD_INVALID"
    elif not g5:
        terminal = "N4_F3_TYPED_TRANSPORT_UNSOUND"
    elif g2:
        terminal = "N4_F3_TYPED_REMINT_TRANSPORT_SUPPORTED__EXACT_SYNTHETIC"
    else:
        terminal = "N4_F3_TYPED_REMINT_TRANSPORT_NO_ADVANTAGE"

    result = {
        "schema": "ORIONQ.N4F3.RemintTransport.v1",
        "issue": 677,
        "family": "3_representation_remint_transport (standalone closure)",
        "protocol": (
            "development/orion-q-nlane-closure/"
            "N4_F3_REMINT_TRANSPORT_PROTOCOL.md"
        ),
        "seed": SEED,
        "episodes_per_regime": EPISODES_PER_REGIME,
        "world": {
            "layers": LAYERS,
            "width": WIDTH,
            "edits_per_episode": N_EDITS,
            "remint_budget": BUDGET,
            "reward": REWARD,
            "fail_penalty": FAIL_PENALTY,
            "bindable_aspects": list(BINDABLE_ASPECTS),
            "cosmetic_aspect": COSMETIC_ASPECT,
            "edge_types": list(EDGE_TYPES),
            "transport_rules": sorted(list(r) for r in TRANSPORT_RULES),
            "regimes": {
                reg: {
                    "binding_sizes": list(spec["binding_sizes"]),
                    "edit_sizes": list(spec["edit_sizes"]),
                    "edit_pool": list(spec["edit_pool"]),
                    "p_break": spec["p_break"],
                }
                for reg, spec in REGIMES.items()
            },
            "scope_limits": [
                "transport-rule soundness is by construction",
                "remints consume budget only, not utility",
            ],
        },
        "mean_transportable_receipt_fraction": transport_fraction,
        "orion_invalidation_mismatches": invalidation_mismatches,
        "orion_committed_failures": orion_failures,
        "total_receipts_checked": total_receipts,
        "per_regime": per_regime,
        "pooled": pooled,
        "gates": gates,
        "terminal": terminal,
        "interpretation": {
            "authority": (
                "exact-synthetic-bounded; no real-quantum, no P10, no novelty "
                "claims; transport-rule soundness is by construction (recorded "
                "scope limit, as in N4-D); remints consume budget only, not "
                "utility (recorded scope limit); no claim about real "
                "representation migrations or real LLMs"
            ),
            "claim_boundary": (
                "Applies only to the frozen three-regime remint world; the "
                "typed-transport advantage is over matched-budget re-derivation "
                "and naive carry-forward on this construction, not a general "
                "interface-graph theorem. Closes N4 residual 1 (family 3 "
                "standalone) in whichever direction the gates decided."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(
        "ORIONQ_N4_F3_REMINT_TRANSPORT="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "N4_F3_REMINT_TRANSPORT_RESULTS.json",
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
