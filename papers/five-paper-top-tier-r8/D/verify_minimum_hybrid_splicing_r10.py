#!/usr/bin/env python3
"""Finite hostile controls for MINIMUM HYBRID SPLICING R10.

The all-size NP-completeness theorem is analytic. This verifier checks the
SET-COVER reduction exhaustively on every distinct nonempty set family of size
at most five over universes of size at most four, after the theorem's fresh
singleton normalization. It also checks direct witness semantics and negative
controls. Generic SET COVER algorithms are not claimed as ORION novelty.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable

SCHEMA = "ORION.TypedAuthority.MinimumHybridSplicing.R10.v1"


def minimum_cover(universe: frozenset[int], family: tuple[frozenset[int], ...]) -> int | None:
    for k in range(len(family) + 1):
        for idxs in itertools.combinations(range(len(family)), k):
            covered: set[int] = set()
            for i in idxs:
                covered.update(family[i])
            if universe.issubset(covered):
                return k
    return None


def minimum_splicing_width(
    universe: frozenset[int], family: tuple[frozenset[int], ...]
) -> tuple[int | None, tuple[int, ...] | None]:
    """Single-rule Horn instance used by the restricted hardness proof.

    Each origin independently seeds one set of element claims. Fine-origin
    semantics derives the target iff one selected origin contains all elements.
    Coordinate-erased semantics derives it iff the union of selected origins
    contains all elements.
    """
    for k in range(1, len(family) + 1):
        for idxs in itertools.combinations(range(len(family)), k):
            pooled: set[int] = set()
            fine_authorized = False
            for i in idxs:
                pooled.update(family[i])
                if universe.issubset(family[i]):
                    fine_authorized = True
            if universe.issubset(pooled) and not fine_authorized:
                return k, idxs
    return None, None


def transformed_instance(
    universe: frozenset[int], family: tuple[frozenset[int], ...]
) -> tuple[frozenset[int], tuple[frozenset[int], ...]]:
    fresh = (max(universe) + 1) if universe else 0
    return universe | frozenset({fresh}), family + (frozenset({fresh}),)


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def run() -> dict[str, object]:
    exhaustive_instances = 0
    cover_mismatches = 0
    splicing_mismatches = 0
    witness_failures = 0
    maximum_finite_width = 0
    width_histogram: dict[str, int] = {}

    for n in range(1, 5):
        universe = frozenset(range(n))
        candidates = tuple(
            frozenset(i for i in range(n) if (mask >> i) & 1)
            for mask in range(1, 1 << n)
        )
        for r in range(1, min(5, len(candidates)) + 1):
            for chosen in itertools.combinations(range(len(candidates)), r):
                family = tuple(candidates[i] for i in chosen)
                base = minimum_cover(universe, family)
                u2, f2 = transformed_instance(universe, family)
                transformed_cover = minimum_cover(u2, f2)
                width, witness = minimum_splicing_width(u2, f2)
                exhaustive_instances += 1

                expected = None if base is None else base + 1
                if transformed_cover != expected:
                    cover_mismatches += 1
                if width != expected:
                    splicing_mismatches += 1

                if width is not None:
                    maximum_finite_width = max(maximum_finite_width, width)
                    width_histogram[str(width)] = width_histogram.get(str(width), 0) + 1
                    assert witness is not None
                    pooled: set[int] = set()
                    for i in witness:
                        pooled.update(f2[i])
                    fine = any(u2.issubset(f2[i]) for i in witness)
                    if not u2.issubset(pooled) or fine:
                        witness_failures += 1

    assert exhaustive_instances == 5070
    assert cover_mismatches == 0
    assert splicing_mismatches == 0
    assert witness_failures == 0

    # Hostile control: without the fresh singleton normalization, a universal
    # origin can derive q by itself and must not be counted as a splicing attack.
    u = frozenset({0, 1})
    fam = (frozenset({0, 1}), frozenset({0}), frozenset({1}))
    width, witness = minimum_splicing_width(u, fam)
    # A genuine two-origin witness still exists using origins 1 and 2; selecting
    # the universal origin alone is correctly excluded by fine_authorized.
    assert width == 2 and witness == (1, 2)

    # Negative control: mutually incomplete origins that never cover the full
    # rule body cannot create erased authority.
    u_neg = frozenset({0, 1, 2})
    fam_neg = (frozenset({0}), frozenset({1}))
    neg_width, _ = minimum_splicing_width(u_neg, fam_neg)
    assert neg_width is None

    # Positive minimality control: three singleton origins require all three.
    fam_pos = tuple(frozenset({i}) for i in range(3))
    pos_width, pos_witness = minimum_splicing_width(u_neg, fam_pos)
    assert pos_width == 3 and pos_witness == (0, 1, 2)

    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS",
        "exhaustive_transformed_set_systems": exhaustive_instances,
        "cover_shift_mismatches": cover_mismatches,
        "splicing_width_mismatches": splicing_mismatches,
        "witness_semantics_failures": witness_failures,
        "maximum_finite_splicing_width_in_panel": maximum_finite_width,
        "finite_width_histogram": width_histogram,
        "universal_origin_hostile_control": "PASS",
        "noncover_negative_control": "PASS",
        "three_origin_minimality_control": "PASS",
        "authority": {
            "all_size_np_completeness_from_computation": False,
            "all_size_np_completeness_from_displayed_reduction": True,
            "finite_controls_exact": True,
            "external_policy_value": False,
            "generic_set_cover_novelty": False,
        },
    }
    payload = canonical_json(result).encode("utf-8")
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    output = Path(__file__).with_name("MINIMUM_HYBRID_SPLICING_R10_RESULTS.json")
    output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
