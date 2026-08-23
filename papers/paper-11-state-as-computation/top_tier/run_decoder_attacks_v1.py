#!/usr/bin/env python3
"""Execute the prospectively frozen P11 decoder-attack frontier V1 (stdlib only).

Enumeration + constructions with direct truth-table comparison. The independent
checker re-derives every claim via exact Fourier spectra, witness extraction,
and Kraft arithmetic instead.
"""

from __future__ import annotations

from itertools import product
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_DECODER_ATTACK_PROTOCOL_V1.md"
GOLD = HERE / "p11_decoder_attack_gold_v1.json"

K_VALUES = (2, 3, 4)
MAX_LIST_LENGTH = 3


def states_and_labels(k: int):
    states = list(product((-1, 1), repeat=k))
    labels = [math.prod(z) for z in states]
    return states, labels


def evaluate_list(nodes, default, z):
    for j, b, leaf in nodes:
        if z[j] == b:
            return leaf
    return default


def build_tree(k: int):
    """Depth-k testing tree; leaf label is the product of branch values."""
    def rec(depth, acc):
        if depth == k:
            return {"leaf": acc}
        return {
            "test": depth,
            "minus": rec(depth + 1, acc * -1),
            "plus": rec(depth + 1, acc * 1),
        }
    return rec(0, 1)


def tree_leaves(node):
    if "leaf" in node:
        return [node]
    return tree_leaves(node["minus"]) + tree_leaves(node["plus"])


def evaluate_tree(node, z):
    while "leaf" not in node:
        node = node["minus"] if z[node["test"]] == -1 else node["plus"]
    return node["leaf"]


def first_node_witness(nodes, default, states, labels, k):
    """First node's matched domain fixes one coordinate; flipping any other
    coordinate keeps the prediction and flips the label."""
    j, b, _ = nodes[0]
    base = [1] * k
    base[j] = b
    free = next(m for m in range(k) if m != j)
    z = tuple(base)
    flipped = list(base)
    flipped[free] *= -1
    z2 = tuple(flipped)
    assert evaluate_list(nodes, default, z) == evaluate_list(nodes, default, z2)
    zi, z2i = states.index(z), states.index(z2)
    return {
        "z": list(z),
        "z_flipped": list(z2),
        "same_prediction": evaluate_list(nodes, default, z) == evaluate_list(nodes, default, z2),
        "labels_differ": labels[zi] != labels[z2i],
    }


def main() -> int:
    gold = json.loads(GOLD.read_text())
    assert gold["k_values"] == list(K_VALUES)

    per_k = {}
    all_green = True
    for k in K_VALUES:
        states, labels = states_and_labels(k)
        assert labels.count(1) == labels.count(-1)

        # C1 constants.
        constants = [tuple([1] * len(states)), tuple([-1] * len(states))]
        c1_realizing = sum(1 for pred in constants if list(pred) == labels)

        # C2 signed single coordinates.
        c2_functions = []
        for j in range(k):
            c2_functions.append(tuple(z[j] for z in states))
            c2_functions.append(tuple(-z[j] for z in states))
        c2_realizing = sum(1 for pred in c2_functions if list(pred) == labels)

        # C3 characters +-prod_{j in S} z_j.
        c3_functions = []
        c3_degrees = []
        for sign in (1, -1):
            for subset in product((0, 1), repeat=k):
                members = [j for j in range(k) if subset[j]]
                fn = tuple(sign * math.prod(z[j] for j in members) for z in states)
                c3_functions.append(fn)
                c3_degrees.append((sign, tuple(members)))
        c3_hits = [
            c3_degrees[i]
            for i, fn in enumerate(c3_functions)
            if list(fn) == labels
        ]
        assert all(sign == 1 and members == tuple(range(k)) for sign, members in c3_hits)
        minimal_degree = k

        # C4 odd-majority thresholds.
        c4_functions = []
        for size in range(1, k + 1, 2):
            for subset in product((0, 1), repeat=k):
                members = [j for j in range(k) if subset[j]]
                if len(members) != size:
                    continue
                fn = tuple(1 if sum(z[j] for j in members) > 0 else -1 for z in states)
                c4_functions.append(fn)
        c4_realizing = sum(1 for pred in c4_functions if list(pred) == labels)

        # C5 axis decision lists, lengths 1..3, plus the first-node witness.
        node_space = [(j, b, leaf) for j in range(k) for b in (-1, 1) for leaf in (-1, 1)]
        c5_total = 0
        c5_realizing = 0
        c5_witness_ok = 0
        for length in range(1, MAX_LIST_LENGTH + 1):
            for nodes in product(node_space, repeat=length):
                for default in (-1, 1):
                    c5_total += 1
                    pred = [evaluate_list(nodes, default, z) for z in states]
                    if pred == labels:
                        c5_realizing += 1
                    w = first_node_witness(nodes, default, states, labels, k)
                    if w["same_prediction"] and w["labels_differ"]:
                        c5_witness_ok += 1
        assert c5_witness_ok == c5_total

        # C6 decision-tree construction at 2^k leaves.
        tree = build_tree(k)
        leaves = tree_leaves(tree)
        tree_ok = all(
            evaluate_tree(tree, z) == label for z, label in zip(states, labels)
        )
        assert len(leaves) == 2 ** k and tree_ok

        green = (
            c1_realizing == 0
            and c2_realizing == 0
            and len(c3_hits) == 1
            and minimal_degree == k
            and c4_realizing == 0
            and c5_realizing == 0
            and c5_witness_ok == c5_total
            and tree_ok
            and len(leaves) == 2 ** k
        )
        all_green = all_green and green

        per_k[str(k)] = {
            "states_count": len(states),
            "labels_balanced": labels.count(1) == labels.count(-1),
            "C1_constants": {
                "family_size": len(constants),
                "realizing_count": c1_realizing,
                "disposition": "NO_LAUNDER" if c1_realizing == 0 else "LAUNDERS",
            },
            "C2_signed_singles": {
                "family_size": len(c2_functions),
                "realizing_count": c2_realizing,
                "disposition": "NO_LAUNDER" if c2_realizing == 0 else "LAUNDERS",
            },
            "C3_characters": {
                "family_size": len(c3_functions),
                "realizing_count": len(c3_hits),
                "realizing_character": {"sign": 1, "members": list(range(k))},
                "minimal_realizing_degree": minimal_degree,
                "disposition": "DEGREE_THRESHOLD_AT_K",
            },
            "C4_odd_majority": {
                "family_size": len(c4_functions),
                "realizing_count": c4_realizing,
                "disposition": "NO_LAUNDER" if c4_realizing == 0 else "LAUNDERS",
            },
            "C5_axis_decision_lists": {
                "max_length_enumerated": MAX_LIST_LENGTH,
                "family_size": c5_total,
                "realizing_count": c5_realizing,
                "first_node_witness_verified_count": c5_witness_ok,
                "disposition": "NO_LAUNDER" if c5_realizing == 0 else "LAUNDERS",
            },
            "C6_decision_trees": {
                "construction_leaves": len(leaves),
                "construction_depth": k,
                "construction_realizes_target": tree_ok,
                "minimality_argument": "KRAFT_FRACTION",
            },
        }

    exp = gold["expected"]
    gold_ok = (
        all(per_k[str(k)]["C1_constants"]["disposition"] == exp["C1_constants"] for k in K_VALUES)
        and all(per_k[str(k)]["C2_signed_singles"]["disposition"] == exp["C2_signed_singles"] for k in K_VALUES)
        and all(
            per_k[str(k)]["C3_characters"]["realizing_count"]
            == exp["C3_characters"]["realizing_function_count"]
            and per_k[str(k)]["C3_characters"]["minimal_realizing_degree"] == k
            for k in K_VALUES
        )
        and all(per_k[str(k)]["C4_odd_majority"]["disposition"] == exp["C4_odd_majority"] for k in K_VALUES)
        and all(
            per_k[str(k)]["C5_axis_decision_lists"]["disposition"]
            == exp["C5_axis_decision_lists"]["exhaustive_disposition"]
            and per_k[str(k)]["C5_axis_decision_lists"]["max_length_enumerated"]
            == exp["C5_axis_decision_lists"]["exhaustive_max_length"]
            for k in K_VALUES
        )
        and all(
            per_k[str(k)]["C6_decision_trees"]["construction_leaves"] == 2 ** k
            and per_k[str(k)]["C6_decision_trees"]["construction_realizes_target"]
            for k in K_VALUES
        )
    )

    receipt = {
        "protocol": "P11_DECODER_ATTACK_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(GOLD.read_bytes()).hexdigest(),
        "k_values": list(K_VALUES),
        "per_k": per_k,
        "gold_agreement": gold_ok,
        "terminal": (
            "P11_DECODER_ATTACK_V1_GREEN" if (all_green and gold_ok)
            else "P11_DECODER_ATTACK_V1_GATE_NOT_MET"
        ),
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())