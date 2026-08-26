#!/usr/bin/env python3
"""Finite controls for the unbounded certificate-waste theorem R10.

The analytic proof owns all-size authority. This script exhaustively enumerates
small cyclic and rank-two groups, checks that the maximum weak zero-sum-deletion
terminal support equals D(G)-1 for the registered groups, and independently
simulates pair aggregation to the unique singleton total.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Sequence

SCHEMA = "ORION.AB.UnboundedCertificateWaste.R10.v1"


def group_elements(moduli: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [
        x
        for x in itertools.product(*(range(m) for m in moduli))
        if any(x)
    ]


def add(a: tuple[int, ...], b: tuple[int, ...], moduli: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((x + y) % m for x, y, m in zip(a, b, moduli))


def total(seq: Sequence[tuple[int, ...]], moduli: tuple[int, ...]) -> tuple[int, ...]:
    out = tuple(0 for _ in moduli)
    for x in seq:
        out = add(out, x, moduli)
    return out


def is_zero(x: tuple[int, ...]) -> bool:
    return all(v == 0 for v in x)


def weak_terminal(seq: Sequence[tuple[int, ...]], moduli: tuple[int, ...]) -> bool:
    if is_zero(total(seq, moduli)):
        return False
    length = len(seq)
    for mask in range(1, (1 << length) - 1):
        subtotal = tuple(0 for _ in moduli)
        for i, x in enumerate(seq):
            if (mask >> i) & 1:
                subtotal = add(subtotal, x, moduli)
        if is_zero(subtotal):
            return False
    return True


def strong_reduce(seq: Sequence[tuple[int, ...]], moduli: tuple[int, ...]) -> tuple[int, ...]:
    work = list(seq)
    invariant = total(work, moduli)
    assert not is_zero(invariant)
    while len(work) > 1:
        a = work.pop()
        b = work.pop()
        merged = add(a, b, moduli)
        if not is_zero(merged):
            work.append(merged)
        assert total(work, moduli) == invariant
    assert len(work) == 1
    return work[0]


def run_panel(moduli: tuple[int, ...], davenport: int) -> dict[str, object]:
    elements = group_elements(moduli)
    admissible_states = 0
    strong_reductions = 0
    maximum_weak_terminal = 0
    maximum_terminal_witness: list[list[int]] | None = None

    for length in range(1, davenport + 1):
        for indices in itertools.combinations_with_replacement(range(len(elements)), length):
            seq = [elements[i] for i in indices]
            invariant = total(seq, moduli)
            if is_zero(invariant):
                continue
            admissible_states += 1
            assert strong_reduce(seq, moduli) == invariant
            strong_reductions += 1
            if weak_terminal(seq, moduli) and length > maximum_weak_terminal:
                maximum_weak_terminal = length
                maximum_terminal_witness = [list(x) for x in seq]

    assert maximum_weak_terminal == davenport - 1
    assert maximum_terminal_witness is not None
    return {
        "group_moduli": list(moduli),
        "declared_davenport_constant": davenport,
        "admissible_multisets_checked": admissible_states,
        "strong_reductions_checked": strong_reductions,
        "maximum_weak_terminal_support": maximum_weak_terminal,
        "expected_weak_terminal_support": davenport - 1,
        "intrinsic_strong_support": 1,
        "maximum_terminal_witness": maximum_terminal_witness,
        "status": "PASS",
    }


def run() -> dict[str, object]:
    # Registered D(G) values are classical donor facts:
    # D(C_n)=n; D(C_3^2)=5; D(C_2 x C_4)=5.
    panels = [((n,), n) for n in range(2, 9)] + [((3, 3), 5), ((2, 4), 5)]
    rows = [run_panel(moduli, davenport) for moduli, davenport in panels]
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS",
        "panels": rows,
        "total_admissible_multisets_checked": sum(int(r["admissible_multisets_checked"]) for r in rows),
        "total_strong_reductions_checked": sum(int(r["strong_reductions_checked"]) for r in rows),
        "authority": {
            "all_finite_abelian_groups_from_computation": False,
            "all_finite_abelian_groups_from_displayed_proof": True,
            "finite_controls_exact": True,
            "classical_davenport_values_donor_owned": True,
            "external_rewrite_system_significance": False,
        },
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    Path(__file__).with_name("UNBOUNDED_CERTIFICATE_WASTE_R10_RESULTS.json").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
