#!/usr/bin/env python3
"""Structurally independent finite Q1-B shared-Tag search.

The production grammar is encoded directly from the content-bound V3 paper
definition.  This module imports no ORION implementation, canonicalizer,
witness generator, checker, or registered result.  Phase-free Paulis are finite
integer variables and exact optimum certificates are proved with Z3 feasibility
queries plus an explicit objective binary search.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import z3


SOURCE_COMMIT = "1e18787841d99d76a3c7661505838d2eca8780db"
SOURCE_MANUSCRIPT_SHA256 = (
    "8522ab344c105866798ca64019f2e5bdf75f4c4445c0c6a0525a573a0c2b5377"
)
RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
EXACT_OPTIMUM = "EXACT_OPTIMUM"
LETTERS = "IXYZ"


@dataclass(frozen=True)
class Instance:
    """Neutral finite interchange object; no registered artifact is consumed."""

    instance_id: str
    n: int
    blocks: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
    scope: str = "R6M_SHARED_ONE_BIT_TAG"

    def as_dict(self) -> dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "n": self.n,
            "blocks": [list(block) for block in self.blocks],
            "scope": self.scope,
        }


def pauli_product(left: str, right: str) -> str:
    """Phase-free Pauli product in the independent integer-XOR encoding."""

    if len(left) != len(right):
        raise ValueError("Paulis have different lengths")
    try:
        return "".join(
            LETTERS[LETTERS.index(a) ^ LETTERS.index(b)]
            for a, b in zip(left, right, strict=True)
        )
    except ValueError as error:
        raise ValueError("Pauli outside I/X/Y/Z alphabet") from error


def perfect_matchings(items: Sequence[Any]) -> tuple[tuple[tuple[Any, Any], ...], ...]:
    """Return every perfect matching once, in deterministic recursive order."""

    values = tuple(items)
    if len(values) % 2:
        raise ValueError("perfect matching requires an even item count")

    def visit(remaining: tuple[Any, ...]) -> Iterable[tuple[tuple[Any, Any], ...]]:
        if not remaining:
            yield ()
            return
        first = remaining[0]
        for index in range(1, len(remaining)):
            partner = remaining[index]
            tail = remaining[1:index] + remaining[index + 1 :]
            for matching in visit(tail):
                yield ((first, partner),) + matching

    return tuple(visit(values))


def _all_nonidentity_paulis(n: int) -> list[str]:
    return [
        "".join(LETTERS[value] for value in word)
        for word in itertools.product(range(4), repeat=n)
        if any(word)
    ]


def _source_bound_target_set(n: int) -> tuple[str, ...]:
    """Select six neutral targets from the source digest, never from outcomes."""

    seed = int(SOURCE_MANUSCRIPT_SHA256[:16], 16)
    return tuple(random.Random(seed).sample(_all_nonidentity_paulis(n), 6))


def declared_n3_instances() -> tuple[Instance, ...]:
    """Smallest support-three-capable domain, complete over all 15 matchings."""

    targets = _source_bound_target_set(3)
    return tuple(
        Instance(
            instance_id=f"Q1B.N3.SOURCE_DIGEST.MATCHING.{index:02d}",
            n=3,
            blocks=matching,
        )
        for index, matching in enumerate(perfect_matchings(targets))
    )


def lower_control_instance() -> Instance:
    """Outcome-independent n=2 sharpness control selected by the same digest."""

    matching = perfect_matchings(_source_bound_target_set(2))[0]
    return Instance(
        instance_id="Q1B.N2.SOURCE_DIGEST.LOWER_CONTROL",
        n=2,
        blocks=matching,
    )


def simple_support_one_instance() -> Instance:
    return Instance(
        instance_id="Q1B.N1.COMPLETE_LOCAL_SUPPORT_ONE",
        n=1,
        blocks=(("X", "Z"), ("X", "Z"), ("X", "Z")),
    )


def apply_letter_relabeling(instance: Instance, mapping: dict[str, str]) -> Instance:
    if set(mapping) != set(LETTERS) or set(mapping.values()) != set(LETTERS):
        raise ValueError("letter relabeling must be a permutation of I/X/Y/Z")

    def transform(pauli: str) -> str:
        return "".join(mapping[letter] for letter in pauli)

    return Instance(
        instance_id=instance.instance_id + ".LETTER_ORBIT",
        n=instance.n,
        blocks=tuple(
            (transform(left), transform(right)) for left, right in instance.blocks
        ),
        scope=instance.scope,
    )


def apply_coordinate_permutation(
    instance: Instance, permutation: Sequence[int]
) -> Instance:
    order = tuple(permutation)
    if sorted(order) != list(range(instance.n)):
        raise ValueError("coordinate permutation is not bijective")

    def transform(pauli: str) -> str:
        return "".join(pauli[index] for index in order)

    return Instance(
        instance_id=instance.instance_id + ".COORDINATE_ORBIT",
        n=instance.n,
        blocks=tuple(
            (transform(left), transform(right)) for left, right in instance.blocks
        ),
        scope=instance.scope,
    )


def apply_block_permutation(
    instance: Instance, permutation: Sequence[int]
) -> Instance:
    order = tuple(permutation)
    if sorted(order) != [0, 1, 2]:
        raise ValueError("block permutation is not bijective")
    return Instance(
        instance_id=instance.instance_id + ".BLOCK_ORBIT",
        n=instance.n,
        blocks=tuple(instance.blocks[index] for index in order),
        scope=instance.scope,
    )


def apply_target_swap(instance: Instance, block_index: int = 0) -> Instance:
    blocks = list(instance.blocks)
    blocks[block_index] = blocks[block_index][::-1]
    return Instance(
        instance_id=instance.instance_id + ".TARGET_SWAP_ORBIT",
        n=instance.n,
        blocks=tuple(blocks),
        scope=instance.scope,
    )


@dataclass
class _Encoding:
    solver: z3.Solver
    objective: z3.ArithRef
    frames: list[list[list[z3.IntNumRef]]]
    tag: list[z3.IntNumRef]
    permutations: list[z3.BoolRef]
    central_branches: list[z3.BoolRef]


def _build_encoding(
    instance: Instance,
    support_cap: int,
    timeout_ms: int,
    *,
    allow_target_permutation: bool,
    allow_central_choice: bool,
) -> _Encoding:
    n = instance.n
    prefix = re.sub(r"[^A-Za-z0-9]", "_", instance.instance_id)
    prefix += f"_k{support_cap}_{int(allow_target_permutation)}_{int(allow_central_choice)}"
    frames = [
        [
            [z3.Int(f"{prefix}_r_{block}_{branch}_{q}") for q in range(n)]
            for branch in range(2)
        ]
        for block in range(3)
    ]
    tag = [z3.Int(f"{prefix}_s_{q}") for q in range(n)]
    permutations = [z3.Bool(f"{prefix}_perm_{block}") for block in range(3)]
    central = [z3.Bool(f"{prefix}_central_{block}") for block in range(3)]

    solver = z3.Solver()
    solver.set(random_seed=7331, timeout=timeout_ms)
    all_letters = [
        letter for block in frames for branch in block for letter in branch
    ] + tag
    solver.add(*(z3.And(letter >= 0, letter <= 3) for letter in all_letters))
    if not allow_target_permutation:
        solver.add(*(move == z3.BoolVal(False) for move in permutations))
    if not allow_central_choice:
        solver.add(*(move == z3.BoolVal(False) for move in central))

    def nonidentity(letter: z3.ArithRef) -> z3.ArithRef:
        return z3.If(letter != 0, 1, 0)

    def local_anticommutes(left: z3.ArithRef, right: z3.ArithRef) -> z3.ArithRef:
        return z3.If(z3.And(left != 0, right != 0, left != right), 1, 0)

    def phase_free_product(
        left: z3.ArithRef | int, right: z3.ArithRef
    ) -> z3.ArithRef:
        return z3.If(
            left == 0,
            right,
            z3.If(right == 0, left, z3.If(left == right, 0, 6 - left - right)),
        )

    frame_weights: list[list[z3.ArithRef]] = []
    for block in range(3):
        block_weights = []
        for branch in range(2):
            weight = z3.Sum(*(nonidentity(x) for x in frames[block][branch]))
            solver.add(weight >= 1, weight <= support_cap)
            block_weights.append(weight)
        frame_weights.append(block_weights)
        solver.add(
            z3.Sum(
                *(
                    local_anticommutes(
                        frames[block][0][q], frames[block][1][q]
                    )
                    for q in range(n)
                )
            )
            % 2
            == 1
        )
        # Global branch exchange is a grammar symmetry, so orientation zero is
        # fixed without loss.  Target permutation and central-branch decisions
        # remain explicit production moves.
        solver.add(
            z3.Sum(
                *(
                    local_anticommutes(tag[q], frames[block][0][q])
                    for q in range(n)
                )
            )
            % 2
            == 0
        )
        solver.add(
            z3.Sum(
                *(
                    local_anticommutes(tag[q], frames[block][1][q])
                    for q in range(n)
                )
            )
            % 2
            == 1
        )
    solver.add(z3.Sum(*(nonidentity(letter) for letter in tag)) >= 1)

    objective_terms: list[z3.ArithRef] = []
    for block in range(3):
        for branch in range(2):
            multiplier = z3.If(central[block] == z3.BoolVal(branch == 1), 2, 4)
            objective_terms.append(multiplier * (frame_weights[block][branch] - 1))
    objective_terms.append(2 * z3.Sum(*(nonidentity(letter) for letter in tag)))

    for branch in range(2):
        for coordinate in range(n):
            restore_letters = []
            for block in range(3):
                left, right = instance.blocks[block]
                no_swap = left if branch == 0 else right
                swapped = right if branch == 0 else left
                target_letter = z3.If(
                    permutations[block],
                    LETTERS.index(swapped[coordinate]),
                    LETTERS.index(no_swap[coordinate]),
                )
                restore_letters.append(
                    phase_free_product(target_letter, frames[block][branch][coordinate])
                )
            objective_terms.append(
                z3.If(
                    z3.And(
                        restore_letters[0] == restore_letters[1],
                        restore_letters[1] == restore_letters[2],
                        restore_letters[0] != 0,
                    ),
                    1,
                    z3.Sum(*(nonidentity(letter) for letter in restore_letters)),
                )
            )

    return _Encoding(
        solver=solver,
        objective=z3.Sum(*objective_terms),
        frames=frames,
        tag=tag,
        permutations=permutations,
        central_branches=central,
    )


def _model_int(model: z3.ModelRef, expression: z3.ExprRef) -> int:
    return model.eval(expression, model_completion=True).as_long()


def _model_bool(model: z3.ModelRef, expression: z3.ExprRef) -> bool:
    return z3.is_true(model.eval(expression, model_completion=True))


def _extract_witness(
    encoding: _Encoding, model: z3.ModelRef, objective: int, support_cap: int
) -> dict[str, Any]:
    frames: list[list[str]] = []
    for block in encoding.frames:
        frames.append(
            [
                "".join(LETTERS[_model_int(model, value)] for value in branch)
                for branch in block
            ]
        )
    tag = "".join(LETTERS[_model_int(model, value)] for value in encoding.tag)
    blocks = []
    for index in range(3):
        blocks.append(
            {
                "frames": frames[index],
                "target_permutation": int(
                    _model_bool(model, encoding.permutations[index])
                ),
                "central_branch": int(
                    _model_bool(model, encoding.central_branches[index])
                ),
            }
        )
    payload = {
        "tag": tag,
        "orientation": 0,
        "blocks": blocks,
        "support_cap": support_cap,
        "objective": objective,
    }
    core = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["witness_sha256"] = hashlib.sha256(core).hexdigest()
    return payload


def _solve_cap(
    instance: Instance,
    support_cap: int,
    timeout_ms: int,
    *,
    allow_target_permutation: bool,
    allow_central_choice: bool,
) -> dict[str, Any]:
    encoding = _build_encoding(
        instance,
        support_cap,
        timeout_ms,
        allow_target_permutation=allow_target_permutation,
        allow_central_choice=allow_central_choice,
    )
    first = encoding.solver.check()
    if first == z3.unknown:
        return {
            "terminal": RESOURCE_EXHAUSTED,
            "reason": encoding.solver.reason_unknown(),
            "support_cap": support_cap,
        }
    if first == z3.unsat:
        return {"terminal": "INFEASIBLE", "support_cap": support_cap}

    first_model = encoding.solver.model()
    upper = _model_int(first_model, encoding.objective)
    lower = 2  # a feasible shared Tag is nonidentity and costs at least two
    while lower < upper:
        midpoint = (lower + upper) // 2
        encoding.solver.push()
        encoding.solver.add(encoding.objective <= midpoint)
        status = encoding.solver.check()
        if status == z3.unknown:
            reason = encoding.solver.reason_unknown()
            encoding.solver.pop()
            return {
                "terminal": RESOURCE_EXHAUSTED,
                "reason": reason,
                "support_cap": support_cap,
            }
        if status == z3.sat:
            candidate = _model_int(encoding.solver.model(), encoding.objective)
            upper = min(midpoint, candidate)
        else:
            lower = midpoint + 1
        encoding.solver.pop()

    encoding.solver.push()
    encoding.solver.add(encoding.objective == lower)
    exact_status = encoding.solver.check()
    if exact_status == z3.unknown:
        reason = encoding.solver.reason_unknown()
        encoding.solver.pop()
        return {
            "terminal": RESOURCE_EXHAUSTED,
            "reason": reason,
            "support_cap": support_cap,
        }
    if exact_status != z3.sat:
        encoding.solver.pop()
        return {"terminal": "ENCODING_DISAGREEMENT", "support_cap": support_cap}
    witness = _extract_witness(
        encoding, encoding.solver.model(), lower, support_cap
    )
    encoding.solver.pop()
    return {
        "terminal": EXACT_OPTIMUM,
        "support_cap": support_cap,
        "objective": lower,
        "witness": witness,
    }


def solve_instance(
    instance: Instance,
    *,
    timeout_ms: int = 120_000,
    allow_target_permutation: bool = True,
    allow_central_choice: bool = True,
) -> dict[str, Any]:
    """Prove each support-capped optimum and select minimum support at optimum."""

    bounded: dict[str, int] = {}
    rows: dict[int, dict[str, Any]] = {}
    for support_cap in range(1, instance.n + 1):
        row = _solve_cap(
            instance,
            support_cap,
            timeout_ms,
            allow_target_permutation=allow_target_permutation,
            allow_central_choice=allow_central_choice,
        )
        if row["terminal"] == RESOURCE_EXHAUSTED:
            return {
                "instance_id": instance.instance_id,
                "terminal": RESOURCE_EXHAUSTED,
                "reason": row.get("reason", "timeout"),
                "exact_optimum": None,
                "minimum_support_among_optima": None,
                "support_bounded_objectives": bounded,
                "witness": None,
            }
        if row["terminal"] != EXACT_OPTIMUM:
            return {
                "instance_id": instance.instance_id,
                "terminal": row["terminal"],
                "exact_optimum": None,
                "minimum_support_among_optima": None,
                "support_bounded_objectives": bounded,
                "witness": None,
            }
        rows[support_cap] = row
        bounded[str(support_cap)] = int(row["objective"])

    exact = bounded[str(instance.n)]
    minimum_support = min(
        cap for cap in range(1, instance.n + 1) if bounded[str(cap)] == exact
    )
    witness = rows[minimum_support]["witness"]
    return {
        "instance_id": instance.instance_id,
        "terminal": EXACT_OPTIMUM,
        "exact_optimum": exact,
        "minimum_support_among_optima": minimum_support,
        "support_bounded_objectives": bounded,
        "witness": witness,
        "production_moves": {
            "target_permutation": allow_target_permutation,
            "central_branch_choice": allow_central_choice,
        },
    }


def tied_optimum_witnesses(
    instance: Instance,
    support_cap: int,
    objective: int,
    *,
    limit: int = 2,
    timeout_ms: int = 30_000,
) -> list[dict[str, Any]]:
    """Enumerate distinct exact witnesses to exercise objective-tie handling."""

    encoding = _build_encoding(
        instance,
        support_cap,
        timeout_ms,
        allow_target_permutation=True,
        allow_central_choice=True,
    )
    encoding.solver.add(encoding.objective == objective)
    variables: list[z3.ExprRef] = [
        value
        for block in encoding.frames
        for branch in block
        for value in branch
    ] + encoding.tag + encoding.permutations + encoding.central_branches
    witnesses = []
    while len(witnesses) < limit and encoding.solver.check() == z3.sat:
        model = encoding.solver.model()
        witnesses.append(_extract_witness(encoding, model, objective, support_cap))
        encoding.solver.add(
            z3.Or(
                *(
                    variable != model.eval(variable, model_completion=True)
                    for variable in variables
                )
            )
        )
    return witnesses


def broken_two_tag_support_control() -> dict[str, Any]:
    """Out-of-scope rank-three control: partner plus two independent Tags."""

    partner = "XII"
    tag_one = "IXI"
    tag_two = "IIX"

    def anticommutes(left: str, right: str) -> int:
        return sum(
            a != "I" and b != "I" and a != b
            for a, b in zip(left, right, strict=True)
        ) % 2

    feasible = [
        pauli
        for pauli in _all_nonidentity_paulis(3)
        if anticommutes(pauli, partner)
        == anticommutes(pauli, tag_one)
        == anticommutes(pauli, tag_two)
        == 1
    ]
    minimum_support = min(sum(letter != "I" for letter in p) for p in feasible)
    return {
        "schema": "ORION.Q1B.BrokenSharedTagControlR9.v1",
        "scope": "OUTSIDE_R6M_BROKEN_SHARED_ONE_TAG",
        "extension": "one frame partner plus two independent Tag syndromes",
        "partner": partner,
        "tags": [tag_one, tag_two],
        "minimum_support": minimum_support,
        "support_two_feasible": any(
            sum(letter != "I" for letter in p) <= 2 for p in feasible
        ),
        "witness": "ZZZ",
        "witness_valid": "ZZZ" in feasible,
        "terminal": "OUT_OF_SCOPE_SUPPORT3_NEGATIVE_CONTROL",
    }

