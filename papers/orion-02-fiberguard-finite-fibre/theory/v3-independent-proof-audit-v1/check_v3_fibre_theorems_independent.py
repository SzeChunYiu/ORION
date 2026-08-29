#!/usr/bin/env python3
"""Independent regression for the ORION-02 V3 finite-fibre theorem spine.

No ORION module or existing ORION-02 checker is imported. Exact decisions use integers
and fractions. The mathematical proofs live in PROOF_AUDIT.md; this file is an
independent finite transcription/control layer.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement, product
from pathlib import Path


def partitions(n: int):
    """Yield every set partition of range(n) in restricted-growth order."""
    if n == 0:
        yield ()
        return
    blocks = [[0]]

    def rec(i: int):
        if i == n:
            yield tuple(tuple(block) for block in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            yield from rec(i + 1)
            blocks[j].pop()
        blocks.append([i])
        yield from rec(i + 1)
        blocks.pop()

    yield from rec(1)


@lru_cache(None)
def partitions_cached(n: int):
    return tuple(partitions(n))


def diameter(values, block=None) -> int:
    arr = [values[i] for i in block] if block is not None else list(values)
    return max(arr) - min(arr) if arr else 0


def midpoint(values, block=None) -> Fraction:
    arr = [values[i] for i in block] if block is not None else list(values)
    return Fraction(min(arr) + max(arr), 2)


def worst_constant_error(values, certificate: Fraction, block=None) -> Fraction:
    arr = [values[i] for i in block] if block is not None else list(values)
    return max((abs(Fraction(v) - certificate) for v in arr), default=Fraction(0))


def greedy_count(values, length: int) -> int:
    values = sorted(values)
    count = 0
    i = 0
    while i < len(values):
        start = values[i]
        count += 1
        i += 1
        while i < len(values) and values[i] - start <= length:
            i += 1
    return count


def exhaustive_min_parts(values, length: int) -> int:
    best = len(values)
    for partition in partitions_cached(len(values)):
        if len(partition) >= best:
            continue
        if all(diameter(values, block) <= length for block in partition):
            best = len(partition)
    return best


def atom_feasible(values, atom_partition, length: int) -> bool:
    return all(diameter(values, atom) <= length for atom in atom_partition)


def coarsenings_of_atoms(atom_partition):
    """Every partition measurable with respect to the frozen S-signature atoms.

    Such a partition may merge atoms but may never split an atom.
    """
    for partition in partitions_cached(len(atom_partition)):
        merged = []
        for block in partition:
            indices = []
            for atom_index in block:
                indices.extend(atom_partition[atom_index])
            merged.append(tuple(sorted(indices)))
        yield tuple(merged)


def brute_s_measurable_feasible(values, atom_partition, length: int) -> bool:
    return any(
        all(diameter(values, block) <= length for block in partition)
        for partition in coarsenings_of_atoms(atom_partition)
    )


def verify_ledger(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    for claim in range(1, 8):
        marker = f"| V3-C{claim} |"
        if marker not in text:
            errors.append(f"missing {marker}")
            continue
        line = next(line for line in text.splitlines() if marker in line)
        if "**PROVEN**" not in line:
            errors.append(f"V3-C{claim} no longer PROVEN")
    required = {
        "V3-C14": "NOT ESTABLISHED / FORBIDDEN",
        "V3-C15": "NOT CLAIMED / FORBIDDEN",
        "V3-C16": "SUPERSEDED FOR SUBMISSION",
    }
    for claim, phrase in required.items():
        line = next((line for line in text.splitlines() if f"| {claim} |" in line), "")
        if phrase not in line:
            errors.append(f"{claim} boundary changed")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ledger",
        default="papers/orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_V3.md",
    )
    args = ap.parse_args()

    errors = []
    floor_cases = 0
    greedy_cases = 0
    separator_cases = 0
    coverage_cases = 0

    # C1/C4 and midpoint construction.
    for n in range(1, 7):
        for values in combinations_with_replacement(range(-2, 3), n):
            d = diameter(values)
            mid = midpoint(values)
            if worst_constant_error(values, mid) != Fraction(d, 2):
                errors.append(f"midpoint sharpness failed: {values}")
                break
            # Search a denser half-integer certificate grid around the whole fibre.
            for numerator in range(2 * min(values) - 2, 2 * max(values) + 3):
                candidate = Fraction(numerator, 2)
                if worst_constant_error(values, candidate) < Fraction(d, 2):
                    errors.append(f"floor violated: {values}, {candidate}")
                    break
            for length in range(5):  # length = 2 eps
                theorem = d <= length
                construction = worst_constant_error(values, mid) <= Fraction(length, 2)
                if theorem != construction:
                    errors.append(f"certifiability equivalence failed: {values}, L={length}")
            floor_cases += 1

    # C5: independent greedy vs exhaustive arbitrary set partitions.
    for n in range(1, 8):
        for values in combinations_with_replacement(range(4), n):
            for length in range(4):
                if greedy_count(values, length) != exhaustive_min_parts(values, length):
                    errors.append(f"greedy optimum mismatch: {values}, L={length}")
                greedy_cases += 1

    # C6: S is represented solely by its joint-signature atoms. S-measurable
    # refinements are coarsenings of those atoms, never splits inside an atom.
    for n in range(1, 6):
        for values in product(range(3), repeat=n):
            for atom_partition in partitions_cached(n):
                for length in range(3):
                    theorem = atom_feasible(values, atom_partition, length)
                    brute = brute_s_measurable_feasible(values, atom_partition, length)
                    if theorem != brute:
                        errors.append(
                            f"separator theorem mismatch: values={values}, "
                            f"atoms={atom_partition}, L={length}"
                        )
                    separator_cases += 1

    # C7: whole-fibre accept/abstain coverage. Brute force all acceptance subsets.
    masses = (1, 2, 3, 4)
    for diameters in product(range(4), repeat=4):
        for length in range(4):
            theorem = sum(
                masses[i] for i, d in enumerate(diameters) if d <= length
            )
            brute = 0
            for mask in range(1 << 4):
                if all(
                    not ((mask >> i) & 1) or diameters[i] <= length
                    for i in range(4)
                ):
                    brute = max(
                        brute,
                        sum(masses[i] for i in range(4) if (mask >> i) & 1),
                    )
            if theorem != brute:
                errors.append(f"coverage identity mismatch: {diameters}, L={length}")
            coverage_cases += 1

    # Controls that demonstrate the tested predicates can fail and stay silent.
    member_identity_beats_floor = worst_constant_error((0, 2), Fraction(0)) == 2
    if not member_identity_beats_floor:
        errors.append("member-identity positive control failed")

    # Deliberately wrong greedy boundary (< instead of <=) is caught at (0,1), L=1.
    def bad_greedy(values, length):
        values = sorted(values)
        count = 0
        i = 0
        while i < len(values):
            start = values[i]
            count += 1
            i += 1
            while i < len(values) and values[i] - start < length:
                i += 1
        return count

    bad_greedy_detected = bad_greedy((0, 1), 1) != exhaustive_min_parts((0, 1), 1)
    if not bad_greedy_detected:
        errors.append("bad-greedy positive control did not fire")

    same_atom_obstruction_detected = not atom_feasible((0, 2), ((0, 1),), 1)
    if not same_atom_obstruction_detected:
        errors.append("separator obstruction positive control did not fire")

    separate_atom_no_alarm = atom_feasible((0, 2), ((0,), (1,)), 1)
    if not separate_atom_no_alarm:
        errors.append("separator no-alarm control failed")

    errors.extend(verify_ledger(Path(args.ledger)))

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "V3_C1_C7_PROOF_AUDIT_PASS__EXTERNAL_TRANSFER_STILL_OPEN"
            if not errors
            else "CANNOT_CHECK_V3_PROOF_REGRESSION"
        ),
        "counts": {
            "floor_midpoint_cases": floor_cases,
            "greedy_vs_all_partitions_cases": greedy_cases,
            "separator_atom_cases": separator_cases,
            "coverage_subset_cases": coverage_cases,
        },
        "controls": {
            "member_identity_positive_control": member_identity_beats_floor,
            "bad_greedy_detected": bad_greedy_detected,
            "same_atom_obstruction_detected": same_atom_obstruction_detected,
            "separate_atom_no_alarm": separate_atom_no_alarm,
        },
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
