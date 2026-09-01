#!/usr/bin/env python3
"""Standalone construction verifier, derived from primitive C_5^3 semantics.

`PROOF_OBJECT_CONTRACT_V1.md` requires, for the upper-bound half, "a standalone
verifier derived from primitive C_5^3 semantics, not from the search
implementation", and states that "a search program reporting FOUND_30 is
insufficient unless the emitted construction passes the standalone verifier".

This file is that verifier. It is deliberately naive: it re-derives group
arithmetic from the group order alone, checks a construction's claimed properties
by direct computation, and emits a transcript naming every predicate it evaluated.
Its correctness has to be arguable by reading it, because it is the thing that
judges the search.

It imports nothing from engine_a or engine_b, uses no solver, and accepts a
construction as data. It has no opinion about where the construction came from,
which is what makes it able to referee either route.

Accessing no D4 outcome: this file evaluates whatever construction it is handed.
Handed none, it verifies itself against controls with known answers.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "ORION04.StandaloneConstructionVerifier.v1"

Elem = tuple[int, ...]


# --- primitive semantics, re-derived here rather than imported ----------------

def elements(orders: Sequence[int]) -> list[Elem]:
    """Every element of the abelian group with the given invariant orders."""
    return [tuple(e) for e in itertools.product(*(range(o) for o in orders))]


def identity(orders: Sequence[int]) -> Elem:
    return tuple(0 for _ in orders)


def add(a: Elem, b: Elem, orders: Sequence[int]) -> Elem:
    return tuple((x + y) % o for x, y, o in zip(a, b, orders))


def subsequence_sum(seq: Sequence[Elem], mask: int, orders: Sequence[int]) -> Elem:
    total = identity(orders)
    for i, e in enumerate(seq):
        if mask >> i & 1:
            total = add(total, e, orders)
    return total


# --- predicates, each checked and named individually --------------------------

def p_elements_well_formed(seq: Sequence[Elem], orders: Sequence[int]) -> tuple[bool, str]:
    for i, e in enumerate(seq):
        if len(e) != len(orders):
            return False, f"element {i} has rank {len(e)}, expected {len(orders)}"
        for j, (v, o) in enumerate(zip(e, orders)):
            if not (0 <= v < o):
                return False, f"element {i} coordinate {j} is {v}, outside [0,{o})"
    return True, f"all {len(seq)} elements lie in the declared group"


def p_masks_nonempty(masks: Sequence[int]) -> tuple[bool, str]:
    bad = [i for i, m in enumerate(masks) if m == 0]
    if bad:
        return False, f"claimed zero-sum subsequences at positions {bad} are empty"
    return True, f"all {len(masks)} claimed subsequences are nonempty"


def p_masks_in_range(masks: Sequence[int], n: int) -> tuple[bool, str]:
    bad = [i for i, m in enumerate(masks) if m >> n]
    if bad:
        return False, f"masks at {bad} index beyond the {n} construction elements"
    return True, f"all masks index within the {n} elements"


def p_masks_pairwise_disjoint(masks: Sequence[int]) -> tuple[bool, str]:
    for i in range(len(masks)):
        for j in range(i + 1, len(masks)):
            if masks[i] & masks[j]:
                return False, f"claimed subsequences {i} and {j} share an element"
    return True, f"the {len(masks)} claimed subsequences are pairwise disjoint"


def p_each_sums_to_identity(seq: Sequence[Elem], masks: Sequence[int],
                            orders: Sequence[int]) -> tuple[bool, str]:
    z = identity(orders)
    for i, m in enumerate(masks):
        s = subsequence_sum(seq, m, orders)
        if s != z:
            return False, f"claimed subsequence {i} sums to {s}, not the identity"
    return True, f"each of the {len(masks)} subsequences sums to the identity"


def p_count_matches_claim(masks: Sequence[int], claimed_k: int) -> tuple[bool, str]:
    if len(masks) != claimed_k:
        return False, f"construction claims k={claimed_k} but supplies {len(masks)} subsequences"
    return True, f"the supplied subsequence count matches the claim k={claimed_k}"


def p_length_matches_claim(seq: Sequence[Elem], claimed_len: int) -> tuple[bool, str]:
    if len(seq) != claimed_len:
        return False, f"construction claims length {claimed_len} but supplies {len(seq)}"
    return True, f"the supplied length matches the claim {claimed_len}"


PREDICATES = (
    "elements_well_formed", "length_matches_claim", "masks_nonempty",
    "masks_in_range", "masks_pairwise_disjoint", "each_sums_to_identity",
    "count_matches_claim",
)


def verify(construction: dict[str, Any]) -> dict[str, Any]:
    """Check one construction and emit a deterministic transcript.

    Every predicate in PREDICATES is evaluated and recorded, including those that
    pass. A transcript that only lists failures cannot be distinguished from a
    transcript of a check that never ran.
    """
    orders = tuple(construction["group_orders"])
    seq = [tuple(x) for x in construction["sequence"]]
    masks = list(construction["disjoint_zero_sum_masks"])
    claimed_k = construction["claimed_k"]
    claimed_len = construction["claimed_length"]

    results: list[dict[str, Any]] = []

    def rec(name: str, outcome: tuple[bool, str]) -> None:
        ok, detail = outcome
        results.append({"predicate": name, "passed": ok, "detail": detail})

    rec("elements_well_formed", p_elements_well_formed(seq, orders))
    rec("length_matches_claim", p_length_matches_claim(seq, claimed_len))
    rec("masks_nonempty", p_masks_nonempty(masks))
    rec("masks_in_range", p_masks_in_range(masks, len(seq)))
    rec("masks_pairwise_disjoint", p_masks_pairwise_disjoint(masks))
    rec("each_sums_to_identity", p_each_sums_to_identity(seq, masks, orders))
    rec("count_matches_claim", p_count_matches_claim(masks, claimed_k))

    evaluated = {r["predicate"] for r in results}
    missing = sorted(set(PREDICATES) - evaluated)
    verdict = "ACCEPT" if all(r["passed"] for r in results) and not missing else "REJECT"

    payload = {
        "schema": SCHEMA,
        "group_orders": list(orders),
        "verdict": verdict,
        "predicates_declared": list(PREDICATES),
        "predicates_evaluated": sorted(evaluated),
        "predicates_not_evaluated": missing,
        "transcript": results,
        "construction_sha256": hashlib.sha256(
            json.dumps(construction, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scientific_authority_delta": "NONE",
    }
    return payload


def self_test() -> dict[str, Any]:
    """Controls with known answers, including deliberately broken constructions.

    A verifier exercised only on valid input cannot be distinguished from one that
    always accepts, so every rejection mode is exercised too.
    """
    c3 = [3]
    good = {"group_orders": c3, "sequence": [[1], [1], [1], [2], [2], [2]],
            # bits 0+3 pair a 1 with a 2 (1+2 = 0 mod 3); bits 1+4 likewise.
            # The first version here used 0b000101, i.e. bits 0 and 2 -- two 1s
            # summing to 2 -- and the verifier rejected it. That rejection is how
            # the error was found, and it is why the ACCEPT case is load-bearing:
            # without it a verifier that always rejects looks perfect.
            "disjoint_zero_sum_masks": [0b001001, 0b010010], "claimed_k": 2,
            "claimed_length": 6}
    cases = [("valid construction accepts", good, "ACCEPT")]

    overlap = dict(good, disjoint_zero_sum_masks=[0b001001, 0b001010])
    cases.append(("overlapping subsequences reject", overlap, "REJECT"))

    nonzero = dict(good, disjoint_zero_sum_masks=[0b000011, 0b110000])
    cases.append(("subsequence not summing to identity rejects", nonzero, "REJECT"))

    empty = dict(good, disjoint_zero_sum_masks=[0b001001, 0])
    cases.append(("empty subsequence rejects", empty, "REJECT"))

    miscount = dict(good, claimed_k=3)
    cases.append(("count not matching the claim rejects", miscount, "REJECT"))

    outside = dict(good, sequence=[[1], [1], [1], [2], [2], [7]])
    cases.append(("element outside the group rejects", outside, "REJECT"))

    badlen = dict(good, claimed_length=30)
    cases.append(("length not matching the claim rejects", badlen, "REJECT"))

    rows = []
    for why, c, expected in cases:
        got = verify(c)["verdict"]
        rows.append({"why": why, "expected": expected, "got": got, "ok": got == expected})
    verdicts = {r["got"] for r in rows}
    return {"cases": rows, "all_ok": all(r["ok"] for r in rows),
            "distinct_verdicts": sorted(verdicts),
            "discriminates": len(verdicts) > 1}


if __name__ == "__main__":
    print(json.dumps({"self_test": self_test(), "predicates": list(PREDICATES)},
                     indent=2, sort_keys=True))
