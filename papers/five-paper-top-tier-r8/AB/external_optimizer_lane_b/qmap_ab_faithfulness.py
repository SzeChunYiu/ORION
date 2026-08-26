"""Frozen invariant audit for the QMAP-to-AB realization question.

The QMAP projection used here drops tableau phase bits and retains the binary
``(x | z)`` label.  This is sufficient for the discriminator: every supported
Clifford gate is still an invertible linear map on those labels, whereas the AB
delete and fuse productions change the number of live fragments and can lower
their binary rank.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Final

QMAP_SINGLE_QUBIT_GATES: Final = ("NONE", "X", "Y", "Z", "H", "S", "SDG")
QMAP_TWO_QUBIT_GATES: Final = ("CX",)
QMAP_TARGET_METRICS: Final = ("GATES", "TWO_QUBIT_GATES", "DEPTH")

AB_FUSE_LIVE_FRAGMENT_COST_DELTA: Final = -1
QMAP_GATE_SEQUENCE_COST_DELTA: Final = 1
QMAP_TABLEAU_ROW_COUNT_DELTA: Final = 0

QmapGate = tuple[str, int] | tuple[str, int, int]


def gf2_rank(rows: Iterable[int]) -> int:
    """Return the rank of integer bit-vectors over GF(2)."""

    basis: dict[int, int] = {}
    for raw_row in rows:
        if raw_row < 0:
            raise ValueError("GF(2) rows must be nonnegative")
        row = raw_row
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def xor_sum(values: Iterable[int]) -> int:
    """Return the bitwise XOR of all values."""

    total = 0
    for value in values:
        if value < 0:
            raise ValueError("fragments must be nonnegative")
        total ^= value
    return total


def qmap_gate_inventory(n_qubits: int) -> tuple[QmapGate, ...]:
    """Enumerate QMAP's frozen single-step gate choices on ``n_qubits``."""

    if n_qubits < 1:
        raise ValueError("n_qubits must be positive")
    single = tuple(
        (name, qubit) for qubit in range(n_qubits) for name in QMAP_SINGLE_QUBIT_GATES
    )
    two = tuple(
        ("CX", control, target)
        for control in range(n_qubits)
        for target in range(n_qubits)
        if control != target
    )
    return single + two


def apply_qmap_label_gate(label: int, n_qubits: int, gate: QmapGate) -> int:
    """Apply the phase-free QMAP tableau action to one ``(x | z)`` label."""

    if n_qubits < 1:
        raise ValueError("n_qubits must be positive")
    if not 0 <= label < (1 << (2 * n_qubits)):
        raise ValueError("label lies outside the projected tableau width")

    name = gate[0]
    x = label & ((1 << n_qubits) - 1)
    z = label >> n_qubits

    if len(gate) == 2:
        target = gate[1]
        if not 0 <= target < n_qubits or name not in QMAP_SINGLE_QUBIT_GATES:
            raise ValueError(f"illegal single-qubit gate: {gate!r}")
        x_bit = (x >> target) & 1
        z_bit = (z >> target) & 1
        if name == "H":
            x ^= (x_bit ^ z_bit) << target
            z ^= (x_bit ^ z_bit) << target
        elif name in ("S", "SDG"):
            z ^= x_bit << target
        # NONE, X, Y and Z change only the discarded phase coordinate.
    elif len(gate) == 3:
        control, target = gate[1], gate[2]
        if (
            name != "CX"
            or control == target
            or not 0 <= control < n_qubits
            or not 0 <= target < n_qubits
        ):
            raise ValueError(f"illegal two-qubit gate: {gate!r}")
        x ^= ((x >> control) & 1) << target
        z ^= ((z >> target) & 1) << control
    else:
        raise ValueError(f"illegal gate arity: {gate!r}")

    return x | (z << n_qubits)


def ab_fuse(fragments: Sequence[int], left: int, right: int) -> tuple[int, ...]:
    """Apply the strong AB production ``u, v -> u xor v``."""

    if left == right:
        raise ValueError("fuse requires two distinct fragments")
    if not 0 <= left < len(fragments) or not 0 <= right < len(fragments):
        raise IndexError("fragment index outside the live multiset")
    if fragments[left] == 0 or fragments[right] == 0:
        raise ValueError("fuse operands must be nonzero")
    if fragments[left] == fragments[right]:
        raise ValueError("equal operands are weakly deletable, not fusible")
    fused = fragments[left] ^ fragments[right]
    return tuple(
        value for index, value in enumerate(fragments) if index not in (left, right)
    ) + (fused,)


def ab_delete(fragments: Sequence[int], indices: Iterable[int]) -> tuple[int, ...]:
    """Delete a nonempty proper zero-XOR submultiset from the AB weak state."""

    chosen = tuple(indices)
    chosen_set = set(chosen)
    if len(chosen) != len(chosen_set):
        raise ValueError("delete indices must be distinct")
    if not chosen_set or len(chosen_set) >= len(fragments):
        raise ValueError("delete requires a nonempty proper submultiset")
    if min(chosen_set) < 0 or max(chosen_set) >= len(fragments):
        raise IndexError("fragment index outside the live multiset")
    if xor_sum(fragments[index] for index in chosen_set) != 0:
        raise ValueError("deleted fragments must have zero XOR")
    return tuple(
        value for index, value in enumerate(fragments) if index not in chosen_set
    )


def every_qmap_gate_has_legal_inverse() -> bool:
    """State the inverse closure of the frozen QMAP Clifford inventory."""

    inverses = {
        "NONE": "NONE",
        "X": "X",
        "Y": "Y",
        "Z": "Z",
        "H": "H",
        "S": "SDG",
        "SDG": "S",
        "CX": "CX",
    }
    return set(inverses) == set(QMAP_SINGLE_QUBIT_GATES + QMAP_TWO_QUBIT_GATES)


def assess_faithfulness() -> dict[str, object]:
    """Return the frozen, adverse external-realization disposition."""

    mapping_table = [
        {
            "obligation": "AB_WEAK_DELETE_TO_QMAP",
            "disposition": "REFUTED",
            "reason": "AB delete can reduce live-fragment cardinality and GF(2) rank; every QMAP gate preserves tableau row count and projected rank.",
        },
        {
            "obligation": "AB_STRONG_FUSE_TO_QMAP",
            "disposition": "REFUTED",
            "reason": "AB fuse is many-to-one and removes one live fragment; every QMAP gate is invertible on a fixed-size tableau.",
        },
        {
            "obligation": "QMAP_MOVES_TO_AB_BIDIRECTIONAL",
            "disposition": "REFUTED",
            "reason": "QMAP moves have legal Clifford inverses, while AB delete/fuse have no legal inverse without adding allocation or garbage moves.",
        },
        {
            "obligation": "ONE_COST_CONTRACT",
            "disposition": "REFUTED",
            "reason": "AB live-fragment cost decreases under fuse; QMAP gate-count/depth costs accumulate applied nonidentity gates.",
        },
        {
            "obligation": "REALIZED_WEAK_TERMINAL",
            "disposition": "CANNOT_CHECK",
            "reason": "No representation- and cost-faithful mapping survives, so QMAP cannot realize an AB weak terminal under the frozen contract.",
        },
    ]
    return {
        "schema": "orion.ab.external_optimizer_faithfulness.v1",
        "candidate": "MQT_QMAP_CLIFFORD_SYNTHESIS",
        "terminal": "CANNOT_CHECK",
        "faithful_external_realization": False,
        "mapping_table": mapping_table,
        "next_smallest_discriminator": "EXTERNAL_MOVE_DECREASES_LIVE_FRAGMENT_CARDINALITY_WITHOUT_GARBAGE_QUOTIENT",
        "claim_ceiling": [
            "NO_EXTERNAL_PRODUCTION_REALIZATION",
            "NO_RUNTIME_OR_STATE_VOLUME_CONSEQUENCE",
            "NO_NOVELTY_OR_VENUE_INFERENCE",
            "NO_HARDWARE_ADVANTAGE",
            "NO_Q1_EXTENSION",
        ],
    }
