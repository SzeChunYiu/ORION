#!/usr/bin/env python3
"""Independent finite checker for P11 decoder-attack frontier V1 (stdlib only).

Re-derives every runner claim by different mathematics:
- function equality via exact Fourier/M\"obius spectra in Fraction arithmetic
  (never by direct truth-table comparison);
- explicit witness pairs for the non-realizing families (flip-one-coordinate
  construction, plus the decision-list first-node reduction);
- decision-tree minimality content via exhaustive proper-subcube checks and the
  Kraft identity in exact Fractions.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_DECODER_ATTACK_PROTOCOL_V1.md"
GOLD = HERE / "p11_decoder_attack_gold_v1.json"
RUN_RECEIPT = Path("p11_decoder_attack_v1.json")

K_VALUES = (2, 3, 4)
MAX_LIST_LENGTH = 3


def states_and_labels(k: int):
    """Built by bit extraction, not itertools.product."""
    states = []
    for i in range(2 ** k):
        states.append(tuple(1 if (i >> (k - 1 - j)) & 1 else -1 for j in range(k)))
    labels = [math.prod(z) for z in states]
    return states, labels


def spectrum(k: int, fn) -> dict:
    """Exact Fourier coefficients keyed by frozenset support."""
    states, _ = states_and_labels(k)
    out = {}
    for mask in range(2 ** k):
        support = frozenset(j for j in range(k) if (mask >> j) & 1)
        total = sum(
            fn[i] * math.prod(z[j] for j in support) for i, z in enumerate(states)
        )
        out[support] = Fraction(total, 2 ** k)
    return out


def spectra_equal(a: dict, b: dict) -> bool:
    return a == b


def evaluate_list(nodes, default, z):
    for j, b, leaf in nodes:
        if z[j] == b:
            return leaf
    return default


def flip_witness(fn, k: int, states, labels):
    """Find z, z'=flip_m(z) with fn equal on both but labels differing."""
    index = {z: i for i, z in enumerate(states)}
    for z in states:
        for m in range(k):
            zm = list(z)
            zm[m] *= -1
            zm = tuple(zm)
            if fn[index[z]] == fn[index[zm]] and labels[index[z]] != labels[index[zm]]:
                return {"z": list(z), "z_flipped": list(zm), "coordinate": m}
    return None


def kraft_identity(depths) -> Fraction:
    return sum((Fraction(1, 2 ** d) for d in depths), Fraction(0))


def main() -> int:
    run = json.loads(RUN_RECEIPT.read_text())
    gold = json.loads(GOLD.read_text())

    assert run["protocol"] == "P11_DECODER_ATTACK_PROTOCOL_V1"
    assert run["protocol_sha256"] == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    assert run["gold_sha256"] == hashlib.sha256(GOLD.read_bytes()).hexdigest()
    assert run["k_values"] == list(K_VALUES)

    checks = {}
    all_green = True
    for k in K_VALUES:
        states, labels = states_and_labels(k)
        assert labels.count(1) == labels.count(-1)

        parity_fn = [math.prod(z) for z in states]
        parity_spec = spectrum(k, parity_fn)

        # Method self-validation: every character's spectrum is a point mass.
        for sign in (1, -1):
            for mask in range(2 ** k):
                support = frozenset(j for j in range(k) if (mask >> j) & 1)
                chi = [sign * math.prod(z[j] for j in support) for z in states]
                spec = spectrum(k, chi)
                nonzero = [s for s, v in spec.items() if v != 0]
                assert len(nonzero) == 1 and nonzero[0] == support
                assert spec[support] == sign

        # C1 constants via spectra.
        c1_hits = sum(
            1
            for const in (1, -1)
            if spectra_equal(spectrum(k, [const] * len(states)), parity_spec)
        )
        c1_witness = flip_witness([1] * len(states), k, states, labels)
        assert c1_hits == 0 and c1_witness is not None

        # C2 signed singles via spectra + witnesses.
        c2_hits = 0
        c2_witnesses = 0
        for j in range(k):
            for sign in (1, -1):
                fn = [sign * z[j] for z in states]
                if spectra_equal(spectrum(k, fn), parity_spec):
                    c2_hits += 1
                if flip_witness(fn, k, states, labels) is not None:
                    c2_witnesses += 1
        assert c2_hits == 0 and c2_witnesses == 2 * k

        # C3 characters via spectra.
        c3_hits = []
        for sign in (1, -1):
            for mask in range(2 ** k):
                support = frozenset(j for j in range(k) if (mask >> j) & 1)
                chi = [sign * math.prod(z[j] for j in support) for z in states]
                if spectra_equal(spectrum(k, chi), parity_spec):
                    c3_hits.append((sign, tuple(sorted(support))))
        assert c3_hits == [(1, tuple(range(k)))]
        # The parity spectrum itself is the point mass at the full support.
        nonzero = [s for s, v in parity_spec.items() if v != 0]
        assert nonzero == [frozenset(range(k))] and parity_spec[nonzero[0]] == 1

        # C4 odd-majority via spectra + witnesses.
        c4_hits = 0
        c4_witnesses = 0
        c4_count = 0
        for mask in range(2 ** k):
            members = [j for j in range(k) if (mask >> j) & 1]
            if len(members) % 2 != 1:
                continue
            c4_count += 1
            fn = [1 if sum(z[j] for j in members) > 0 else -1 for z in states]
            if spectra_equal(spectrum(k, fn), parity_spec):
                c4_hits += 1
            if flip_witness(fn, k, states, labels) is not None:
                c4_witnesses += 1
        assert c4_hits == 0 and c4_witnesses == c4_count

        # C5 lists: spectrum equality + the first-node reduction witness.
        node_space = [(j, b, leaf) for j in range(k) for b in (-1, 1) for leaf in (-1, 1)]
        c5_total = 0
        c5_hits = 0
        c5_reductions = 0
        for length in range(1, MAX_LIST_LENGTH + 1):
            for nodes in product(node_space, repeat=length):
                for default in (-1, 1):
                    c5_total += 1
                    fn = [evaluate_list(nodes, default, z) for z in states]
                    if spectra_equal(spectrum(k, fn), parity_spec):
                        c5_hits += 1
                    j1, b1, _ = nodes[0]
                    base = [1] * k
                    base[j1] = b1
                    free = next(m for m in range(k) if m != j1)
                    flipped = list(base)
                    flipped[free] *= -1
                    z, z2 = tuple(base), tuple(flipped)
                    zi, z2i = states.index(z), states.index(z2)
                    if fn[zi] == fn[z2i] and labels[zi] != labels[z2i]:
                        c5_reductions += 1
        assert c5_hits == 0 and c5_reductions == c5_total

        # C6 tree: independent iterative construction + evaluation.
        tree = {}
        for code in range(2 ** k):
            node = tree
            for depth in range(k):
                bit = 1 if (code >> (k - 1 - depth)) & 1 else -1
                node = node.setdefault(bit, {})
            node["label"] = math.prod(
                1 if (code >> (k - 1 - d)) & 1 else -1 for d in range(k)
            )

        def eval_tree(z):
            node = tree
            for value in z:
                node = node[value]
            return node["label"]

        tree_ok = all(eval_tree(z) == label for z, label in zip(states, labels))

        # Leaf depths and Kraft identity in exact Fractions.
        depths = []
        stack = [(tree, 0)]
        while stack:
            node, d = stack.pop()
            if "label" in node:
                depths.append(d)
                continue
            for child in node.values():
                stack.append((child, d + 1))
        assert len(depths) == 2 ** k and all(d == k for d in depths)
        assert kraft_identity(depths) == 1

        # Minimality content: every proper subcube (fewer than k fixed
        # coordinates) carries non-constant labels, so no shallower leaf can
        # ever be labeled correctly.
        proper_subcubes_nonconstant = True
        subcubes_checked = 0
        for fixed_coords in product((None, -1, 1), repeat=k):
            assignment = {j: v for j, v in enumerate(fixed_coords) if v is not None}
            if len(assignment) >= k:
                continue
            subcubes_checked += 1
            matched = {
                labels[i]
                for i, z in enumerate(states)
                if all(z[j] == v for j, v in assignment.items())
            }
            if len(matched) != 2:
                proper_subcubes_nonconstant = False

        # Cross-check against the runner receipt block.
        block = run["per_k"][str(k)]
        assert block["C1_constants"]["realizing_count"] == c1_hits == 0
        assert block["C2_signed_singles"]["realizing_count"] == c2_hits == 0
        assert block["C3_characters"]["realizing_count"] == len(c3_hits) == 1
        assert block["C4_odd_majority"]["realizing_count"] == c4_hits == 0
        assert block["C5_axis_decision_lists"]["realizing_count"] == c5_hits == 0
        assert block["C5_axis_decision_lists"]["family_size"] == c5_total
        assert block["C6_decision_trees"]["construction_leaves"] == len(depths)
        assert block["C6_decision_trees"]["construction_realizes_target"] == tree_ok

        checks[str(k)] = {
            "C1_constants": "NO_LAUNDER",
            "C2_signed_singles": "NO_LAUNDER",
            "C3_characters": {"realizing_count": len(c3_hits), "minimal_degree": k},
            "C4_odd_majority": "NO_LAUNDER",
            "C5_lists": {
                "family_size": c5_total,
                "realizing_count": c5_hits,
                "first_node_reduction_verified": c5_reductions == c5_total,
            },
            "C6_trees": {
                "leaves": len(depths),
                "kraft_identity": str(kraft_identity(depths)),
                "proper_subcubes_checked": subcubes_checked,
                "proper_subcubes_nonconstant": proper_subcubes_nonconstant,
            },
        }
        assert subcubes_checked > 0
        all_green = all_green and tree_ok and proper_subcubes_nonconstant

    assert run["terminal"] == "P11_DECODER_ATTACK_V1_GREEN"
    assert run["gold_agreement"] is True

    payload = {
        "checker": "P11_DECODER_ATTACK_INDEPENDENT_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "run_receipt_sha256": run["receipt_sha256"],
        "per_k": checks,
        "terminal": "P11_DECODER_ATTACK_V1_INDEPENDENT_GREEN" if all_green else "CHECK_FAILED",
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())