"""The TYPED_ORDERED_MULTIPLICITY arm the D1 v1.3 freeze registers.

The freeze's representation contract asks for four things: order preserved,
multiplicity preserved, ``tuple(sorted(set(values)))`` forbidden as a
normalization, and a round trip back to the source sequence.

Why a fourth typed arm rather than a tweak to the third: measured outcome-blind,
ORDER_PERMUTATION changes nothing in any of the four arms that exist. The
serialized arm reduces its token sequence to set indicators --
``features[f"token:{token}"] = 1.0`` -- which is exactly the forbidden
normalization, and the relational arm compares left against right, so reversing
both sides leaves equality and lengths untouched. An attack that cannot change
the input cannot fail the arm, and the protocol forbids passing a cell with no
opportunity. So this arm is not an addition to the panel; it is the only one on
which the order and multiplicity attacks can have any opportunity at all.

The representation carries the same information as the serialized view. It is
not a stronger view smuggled in under a new name: what it adds back is only the
positional and count structure the serialized view discards.

Nothing here reads a label or an outcome.
"""

from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence

from orion.study.p9.d1 import D1Instance, D1View

ARM = "TYPED_ORDERED_MULTIPLICITY"

#: What the contract forbids. Kept as a named function so the guard below can
#: state precisely what it is checking rather than restating it in prose.
def forbidden_normalization(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def token_sequence(instance: D1Instance) -> tuple[str, ...]:
    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    return tuple(str(token) for token in sequence)


def features(instance: D1Instance) -> dict[str, object]:
    """Positional indicators plus counts.

    Positional indicators make the representation order-sensitive and, taken
    together, determine the sequence exactly -- which is what ``round_trip``
    below checks. Counts make it multiplicity-sensitive on their own, so an
    attack that duplicates a token moves the representation even when it lands
    at a position the model has not seen.
    """
    sequence = token_sequence(instance)
    built: dict[str, object] = {"sequence_length": len(sequence)}
    for position, token in enumerate(sequence):
        built[f"pos:{position}:{token}"] = 1.0
    for token, count in Counter(sequence).items():
        built[f"count:{token}"] = float(count)
    return built


def round_trip(built: Mapping[str, object]) -> tuple[str, ...]:
    """Recover the token sequence from the features, or raise.

    The contract requires a round trip, and a round trip that cannot fail is not
    evidence of one. Every position must be present exactly once.
    """
    length = int(built["sequence_length"])  # type: ignore[arg-type]
    recovered: list[str | None] = [None] * length
    for key in built:
        if not key.startswith("pos:"):
            continue
        _, position, token = key.split(":", 2)
        index = int(position)
        if index >= length:
            raise ValueError(f"position {index} outside a sequence of length {length}")
        if recovered[index] is not None:
            raise ValueError(f"position {index} occupied twice")
        recovered[index] = token
    if any(token is None for token in recovered):
        missing = [i for i, token in enumerate(recovered) if token is None]
        raise ValueError(f"positions absent from the representation: {missing}")
    return tuple(token for token in recovered if token is not None)


def violates_contract(instance: D1Instance) -> list[str]:
    """Contract violations for one instance, empty when the arm is faithful."""
    violations: list[str] = []
    sequence = token_sequence(instance)
    built = features(instance)
    if round_trip(built) != sequence:
        violations.append("ROUND_TRIP_FAILED")
    if len(sequence) != len(set(sequence)):
        # Multiplicity only means something where a token actually repeats.
        counts = {k: v for k, v in built.items() if k.startswith("count:")}
        if not any(float(value) > 1 for value in counts.values()):
            violations.append("MULTIPLICITY_NOT_PRESERVED")
    reversed_built = dict(built)
    if len(sequence) > 1 and built == _features_of(tuple(reversed(sequence))):
        violations.append("ORDER_NOT_PRESERVED")
    del reversed_built
    if set(forbidden_normalization(sequence)) == set(sequence) and any(
        key.startswith("token:") for key in built
    ):
        violations.append("USES_FORBIDDEN_SET_NORMALIZATION")
    return violations


def _features_of(sequence: Sequence[str]) -> dict[str, object]:
    built: dict[str, object] = {"sequence_length": len(sequence)}
    for position, token in enumerate(sequence):
        built[f"pos:{position}:{token}"] = 1.0
    for token, count in Counter(sequence).items():
        built[f"count:{token}"] = float(count)
    return built
