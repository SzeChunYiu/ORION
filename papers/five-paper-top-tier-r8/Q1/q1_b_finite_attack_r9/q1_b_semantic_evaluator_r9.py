#!/usr/bin/env python3
"""Independent, Z3-free semantic evaluator for Q1-B witnesses.

This file deliberately does not import the search encoding.  It recomputes the
phase-free Pauli algebra, feasibility predicates, Restore strings and objective
from a JSON witness.  It is a second implementation inside the same research
lane, not external or same-program independence authority.
"""

from __future__ import annotations

from typing import Any


LETTERS = "IXYZ"


def _weight(pauli: str) -> int:
    return sum(letter != "I" for letter in pauli)


def _local_anticommutes(left: str, right: str) -> int:
    return int(left != "I" and right != "I" and left != right)


def _symplectic(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("Paulis have different lengths")
    return sum(_local_anticommutes(a, b) for a, b in zip(left, right, strict=True)) % 2


def _local_product(left: str, right: str) -> str:
    """Phase-free product using an implementation independent of integer XOR."""

    if left == "I":
        return right
    if right == "I":
        return left
    if left == right:
        return "I"
    return ({"X", "Y", "Z"} - {left, right}).pop()


def _product(left: str, right: str) -> str:
    if len(left) != len(right):
        raise ValueError("Paulis have different lengths")
    return "".join(_local_product(a, b) for a, b in zip(left, right, strict=True))


def _f3(a: str, b: str, c: str) -> int:
    if a == b == c and a != "I":
        return 1
    return int(a != "I") + int(b != "I") + int(c != "I")


def evaluate_witness(instance: Any, witness: dict[str, Any]) -> dict[str, Any]:
    """Recompute one witness and return a typed, machine-checkable evaluation."""

    errors: list[str] = []
    n = int(instance.n)
    tag = str(witness["tag"])
    orientation = int(witness["orientation"])
    blocks = witness["blocks"]
    if len(tag) != n or any(letter not in LETTERS for letter in tag):
        errors.append("invalid Tag alphabet or length")
    if _weight(tag) == 0:
        errors.append("Tag is identity")
    if orientation not in (0, 1):
        errors.append("orientation is not binary")
    if len(blocks) != 3:
        errors.append("witness does not contain three blocks")

    frame_cost = 0
    restores: list[list[str]] = []
    max_support = 0
    if not errors:
        for block_index, (target_pair, block) in enumerate(
            zip(instance.blocks, blocks, strict=True)
        ):
            frames = tuple(str(value) for value in block["frames"])
            permutation = int(block["target_permutation"])
            central = int(block["central_branch"])
            if len(frames) != 2 or any(len(frame) != n for frame in frames):
                errors.append(f"block {block_index}: invalid frames")
                continue
            if any(_weight(frame) == 0 for frame in frames):
                errors.append(f"block {block_index}: identity frame")
            if _symplectic(frames[0], frames[1]) != 1:
                errors.append(f"block {block_index}: frames commute")
            if _symplectic(tag, frames[0]) != orientation:
                errors.append(f"block {block_index}: branch-zero Tag syndrome")
            if _symplectic(tag, frames[1]) != 1 - orientation:
                errors.append(f"block {block_index}: branch-one Tag syndrome")
            if permutation not in (0, 1) or central not in (0, 1):
                errors.append(f"block {block_index}: non-binary production move")
                continue
            assigned = target_pair if permutation == 0 else target_pair[::-1]
            block_restores = []
            for branch in range(2):
                support = _weight(frames[branch])
                max_support = max(max_support, support)
                multiplier = 2 if central == branch else 4
                frame_cost += multiplier * (support - 1)
                block_restores.append(_product(assigned[branch], frames[branch]))
            restores.append(block_restores)

    tag_cost = 2 * _weight(tag)
    restore_cost = 0
    if not errors:
        for branch in range(2):
            for coordinate in range(n):
                restore_cost += _f3(
                    restores[0][branch][coordinate],
                    restores[1][branch][coordinate],
                    restores[2][branch][coordinate],
                )
    objective = frame_cost + tag_cost + restore_cost
    if "objective" in witness and int(witness["objective"]) != objective:
        errors.append(
            f"stored objective {witness['objective']} != recomputed {objective}"
        )

    return {
        "schema": "ORION.Q1B.IndependentSemanticEvaluationR9.v1",
        "instance_id": str(instance.instance_id),
        "valid": not errors,
        "errors": errors,
        "objective": objective,
        "objective_terms": {
            "frame": frame_cost,
            "tag": tag_cost,
            "restore": restore_cost,
        },
        "maximum_frame_support": max_support,
        "restores": restores,
    }

