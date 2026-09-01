#!/usr/bin/env python3
"""A1: independently regenerate the admissible multiplicity patterns.

Issue #49 A1 requires an independent implementation that "does not import the
current branch list, current C engines, current fingerprints or current generator
output" and "must independently regenerate the admissible pattern set and branch
partition from the equations/lemmas".

This file does the pattern half from the equations alone, and reports the branch
half honestly rather than guessing at lemma detail it does not have.

Both existing engines are C with bit representations -- a 128-bit weight-layer mask
with coordinate-mask translations, and five 25-bit coordinate planes in AVX2 lanes.
This is exact Python over explicit integer tuples: a materially different backend,
which is what the issue asks for.
"""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = "ORION04.A1.IndependentCoverRegeneration.v1"

TOTAL_LENGTH = 31          # a1 + 2*b2 + 4*c4 = 31
MULTIPLICITIES = (1, 2, 4)
ADMISSIBLE_MIN_SUPPORT = 14   # saturation floor, supports 14..31
ADMISSIBLE_MAX_SUPPORT = 31


def regenerate_patterns() -> list[dict]:
    """Every (a1,b2,c4) with a1+2b2+4c4 = 31, tagged with its support."""
    out = []
    for c4 in range(TOTAL_LENGTH // 4 + 1):
        for b2 in range((TOTAL_LENGTH - 4 * c4) // 2 + 1):
            a1 = TOTAL_LENGTH - 2 * b2 - 4 * c4
            if a1 < 0:
                continue
            out.append({"a1": a1, "b2": b2, "c4": c4, "support": a1 + b2 + c4})
    return sorted(out, key=lambda p: (p["support"], p["c4"], p["b2"]))


def admissible(patterns: list[dict]) -> list[dict]:
    return [p for p in patterns
            if ADMISSIBLE_MIN_SUPPORT <= p["support"] <= ADMISSIBLE_MAX_SUPPORT]


def report() -> dict:
    allp = regenerate_patterns()
    adm = admissible(allp)
    low = [p for p in adm if 14 <= p["support"] <= 22]
    high = [p for p in adm if 23 <= p["support"] <= 31]

    checks = {
        "every_pattern_satisfies_length_equation":
            all(p["a1"] + 2 * p["b2"] + 4 * p["c4"] == TOTAL_LENGTH for p in allp),
        "every_pattern_support_is_sum_of_counts":
            all(p["support"] == p["a1"] + p["b2"] + p["c4"] for p in allp),
        "admissible_count_is_60": len(adm) == 60,
        "no_duplicate_patterns": len({(p["a1"], p["b2"], p["c4"]) for p in allp}) == len(allp),
    }

    # Mutation controls: each must break the pattern count, or the regeneration is
    # not actually sensitive to the equation it claims to solve.
    def count_with(total: int, floor: int) -> int:
        n = 0
        for c4 in range(total // 4 + 1):
            for b2 in range((total - 4 * c4) // 2 + 1):
                a1 = total - 2 * b2 - 4 * c4
                if a1 >= 0 and floor <= a1 + b2 + c4 <= ADMISSIBLE_MAX_SUPPORT:
                    n += 1
        return n

    mutations = {
        "altered_multiplicity_equation_total_30": count_with(30, ADMISSIBLE_MIN_SUPPORT),
        "altered_multiplicity_equation_total_32": count_with(32, ADMISSIBLE_MIN_SUPPORT),
        "altered_support_floor_13": count_with(TOTAL_LENGTH, 13),
        "altered_support_floor_15": count_with(TOTAL_LENGTH, 15),
    }
    mutations_all_differ = all(v != 60 for v in mutations.values())

    return {
        "schema": SCHEMA,
        "independent_of": ["engine_b", "existing C engines", "existing branch list",
                           "existing fingerprints", "existing generator output"],
        "backend": "exact Python over integer tuples (existing engines are C bitmask/AVX2)",
        "raw_solutions_to_length_equation": len(allp),
        "admissible_patterns": len(adm),
        "admissible_supports_14_to_22": len(low),
        "admissible_supports_23_to_31": len(high),
        "expected_by_issue_49": {"admissible_patterns": 60,
                                 "branches_14_22": 51, "branches_23_31": 27,
                                 "branches_total": 78},
        "pattern_regeneration_agrees": checks["admissible_count_is_60"],
        "checks": checks,
        "mutation_controls": mutations,
        "mutation_controls_all_differ_from_60": mutations_all_differ,
        "branch_partition": {
            "status": "NOT_REGENERATED",
            "reason": ("The 78 rank/plane branches subdivide the 60 patterns using the "
                       "corridor and saturation lemmas -- eta(C_5^2)=13, the four "
                       "multiplicity-four rank-three basis, the c_4=3 plane case, and the "
                       "rank(H) profiles (2,2,2)/(4,2,2)/(4,4,2). WAVE3_SCOPED_MANUSCRIPT_V3 "
                       "states these in prose but not at the precision needed to re-derive "
                       "51 and 27 without guessing. Guessing them and matching the published "
                       "counts would be the failure mode this whole exercise exists to avoid."),
            "what_would_close_it": ("the explicit branch predicates, or the lemma statements "
                                    "with enough detail to enumerate the plane-direction and "
                                    "basis-extension cases"),
        },
        "scientific_authority_delta": "NONE",
    }


if __name__ == "__main__":
    r = report()
    out = Path(__file__).with_name("COVER_REGENERATION_V1.json")
    out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in (
        "raw_solutions_to_length_equation", "admissible_patterns",
        "admissible_supports_14_to_22", "admissible_supports_23_to_31",
        "pattern_regeneration_agrees", "checks",
        "mutation_controls", "mutation_controls_all_differ_from_60")},
        indent=2, sort_keys=True))
