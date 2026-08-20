"""Deterministic hostile pairs for the ORION-Q QC-2A exact substrate.

These pairs mirror P9's information-lattice discipline: restricted views collide
while evaluator gold differs, so their deterministic information ceiling is 1/2.
The semantic view exposes the small quantum state payload required by the exact
invariant witness and separates the pair.

This v0 generator is evaluator bootstrap only.  It is not yet a protected learned
benchmark and grants no scientific, novelty, adoption, or execution authority.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import math
from typing import Iterable

from orion.transfer.v2.canonical import content_digest

from .quantum_obstruction import (
    PureState,
    QuantumLanguageCapability,
    QuantumObstructionCase,
    QuantumObstructionVerdict,
    classify_quantum_obstruction,
)


class QuantumHostileFamily(str, Enum):
    ENTANGLEMENT = "ENTANGLEMENT"
    COMPLEX_PHASE = "COMPLEX_PHASE"


class QuantumViewMode(str, Enum):
    SURFACE = "SURFACE"
    CONTRACT = "CONTRACT"
    SEMANTIC = "SEMANTIC"


def _token(seed: str, namespace: str, slot: str, *, prefix: str) -> str:
    if not seed:
        raise ValueError("seed is required")
    digest = sha256(f"{seed}|{namespace}|{slot}".encode("utf-8")).hexdigest()
    return f"{prefix}{digest[:16]}"


def _sign(seed: str, slot: str) -> float:
    digest = sha256(f"{seed}|sign|{slot}".encode("utf-8")).hexdigest()
    return 1.0 if int(digest[:2], 16) % 2 == 0 else -1.0


def _phase(seed: str, slot: str) -> complex:
    digest = sha256(f"{seed}|phase|{slot}".encode("utf-8")).hexdigest()
    bucket = 1 + int(digest[:4], 16) % 7
    angle = bucket * math.pi / 16.0
    return complex(math.cos(angle), math.sin(angle))


@dataclass(frozen=True)
class GeneratedQuantumPair:
    """Evaluator-side hostile pair with a shared opaque surface token."""

    family: QuantumHostileFamily
    pair_id: str
    surface_token: str
    cases: tuple[QuantumObstructionCase, QuantumObstructionCase]

    def verify(self) -> None:
        if not self.pair_id or not self.surface_token:
            raise ValueError("pair identity and surface token are required")
        if len(self.cases) != 2:
            raise ValueError("quantum hostile pair requires exactly two cases")
        left, right = self.cases
        left.verify()
        right.verify()
        if left.case_id == right.case_id:
            raise ValueError("quantum pair cases require distinct evaluator ids")
        if left.gold is right.gold:
            raise ValueError("quantum hostile pair must require different gold")
        if quantum_view_fingerprint(self, left, QuantumViewMode.SURFACE) != quantum_view_fingerprint(
            self, right, QuantumViewMode.SURFACE
        ):
            raise ValueError("quantum pair surface views must collide")
        if quantum_view_fingerprint(self, left, QuantumViewMode.CONTRACT) != quantum_view_fingerprint(
            self, right, QuantumViewMode.CONTRACT
        ):
            raise ValueError("quantum pair contract views must collide")
        if quantum_view_fingerprint(self, left, QuantumViewMode.SEMANTIC) == quantum_view_fingerprint(
            self, right, QuantumViewMode.SEMANTIC
        ):
            raise ValueError("quantum pair semantic views must separate")

    @property
    def pair_digest(self) -> str:
        self.verify()
        return content_digest(
            {
                "schema": "ORIONQ.GeneratedQuantumPair.v0",
                "family": self.family.value,
                "pair_id": self.pair_id,
                "case_ids": [case.case_id for case in self.cases],
                "golds": [case.gold.value for case in self.cases],
            }
        )


def quantum_view_payload(
    pair: GeneratedQuantumPair,
    case: QuantumObstructionCase,
    mode: QuantumViewMode,
) -> dict[str, object]:
    """Return one model-visible view; evaluator IDs/family/gold are excluded."""

    case.verify_model_input()
    if case not in pair.cases:
        raise ValueError("case does not belong to supplied quantum pair")

    if mode is QuantumViewMode.SURFACE:
        return {
            "schema": "ORIONQ.QuantumSurface.v0",
            "opaque_problem": pair.surface_token,
        }

    contract = {
        "schema": "ORIONQ.QuantumContract.v0",
        "opaque_problem": pair.surface_token,
        "capability": case.capability.value,
        "state_dimension": len(case.initial.amplitudes),
        "initial": case.initial.model_payload(),
    }
    if mode is QuantumViewMode.CONTRACT:
        return contract

    if mode is QuantumViewMode.SEMANTIC:
        return {
            "schema": "ORIONQ.QuantumSemantic.v0",
            **contract,
            "target": case.target.model_payload(),
        }

    raise ValueError(f"unsupported quantum view mode: {mode}")


def quantum_view_fingerprint(
    pair: GeneratedQuantumPair,
    case: QuantumObstructionCase,
    mode: QuantumViewMode,
) -> str:
    return content_digest(quantum_view_payload(pair, case, mode))


def _entanglement_pair(seed: str) -> GeneratedQuantumPair:
    material = content_digest({"schema": "ORIONQ.EntanglementSeed.v0", "seed": seed})
    half = 1.0 / math.sqrt(2.0)
    sign = _sign(material, "bell")
    initial = PureState(_token(material, "state", "initial", prefix="q"), (1, 0, 0, 0))
    obstruction_target = PureState(
        _token(material, "state", "target-obstruction", prefix="q"),
        (half, 0, 0, sign * half),
    )
    compatible_target = PureState(
        _token(material, "state", "target-compatible", prefix="q"),
        (half, sign * half, 0, 0),
    )
    capability = QuantumLanguageCapability.LOCAL_PRODUCT_ONLY
    obstruction = QuantumObstructionCase(
        case_id=_token(material, "case", "0", prefix="c"),
        capability=capability,
        initial=initial,
        target=obstruction_target,
        gold=classify_quantum_obstruction(capability, initial, obstruction_target),
    )
    compatible = QuantumObstructionCase(
        case_id=_token(material, "case", "1", prefix="c"),
        capability=capability,
        initial=initial,
        target=compatible_target,
        gold=classify_quantum_obstruction(capability, initial, compatible_target),
    )
    pair = GeneratedQuantumPair(
        family=QuantumHostileFamily.ENTANGLEMENT,
        pair_id=_token(material, "pair", "0", prefix="p"),
        surface_token=_token(material, "surface", "0", prefix="s"),
        cases=(obstruction, compatible),
    )
    pair.verify()
    return pair


def _complex_phase_pair(seed: str) -> GeneratedQuantumPair:
    material = content_digest({"schema": "ORIONQ.ComplexPhaseSeed.v0", "seed": seed})
    half = 1.0 / math.sqrt(2.0)
    sign = _sign(material, "imag")
    global_phase = _phase(material, "compatible")
    initial = PureState(_token(material, "state", "initial", prefix="q"), (1, 0))
    obstruction_target = PureState(
        _token(material, "state", "target-obstruction", prefix="q"),
        (half, sign * 1j * half),
    )
    compatible_target = PureState(
        _token(material, "state", "target-compatible", prefix="q"),
        (global_phase * half, global_phase * sign * half),
    )
    capability = QuantumLanguageCapability.REAL_UNITARY_ONLY
    obstruction = QuantumObstructionCase(
        case_id=_token(material, "case", "0", prefix="c"),
        capability=capability,
        initial=initial,
        target=obstruction_target,
        gold=classify_quantum_obstruction(capability, initial, obstruction_target),
    )
    compatible = QuantumObstructionCase(
        case_id=_token(material, "case", "1", prefix="c"),
        capability=capability,
        initial=initial,
        target=compatible_target,
        gold=classify_quantum_obstruction(capability, initial, compatible_target),
    )
    pair = GeneratedQuantumPair(
        family=QuantumHostileFamily.COMPLEX_PHASE,
        pair_id=_token(material, "pair", "0", prefix="p"),
        surface_token=_token(material, "surface", "0", prefix="s"),
        cases=(obstruction, compatible),
    )
    pair.verify()
    return pair


def generate_quantum_hostile_pair(
    family: QuantumHostileFamily,
    *,
    seed: str,
) -> GeneratedQuantumPair:
    if not seed:
        raise ValueError("generator seed is required")
    if family is QuantumHostileFamily.ENTANGLEMENT:
        return _entanglement_pair(seed)
    if family is QuantumHostileFamily.COMPLEX_PHASE:
        return _complex_phase_pair(seed)
    raise ValueError(f"unsupported quantum hostile family: {family}")


def generate_quantum_pairs(
    *,
    seed: str,
    pairs_per_family: int,
) -> tuple[GeneratedQuantumPair, ...]:
    if not seed:
        raise ValueError("generator seed is required")
    if pairs_per_family <= 0:
        raise ValueError("pairs_per_family must be positive")
    pairs: list[GeneratedQuantumPair] = []
    for family in QuantumHostileFamily:
        for index in range(pairs_per_family):
            pairs.append(
                generate_quantum_hostile_pair(
                    family,
                    seed=f"{seed}|{family.value}|{index}",
                )
            )
    if len({pair.pair_id for pair in pairs}) != len(pairs):
        raise ValueError("generated quantum pair identities must be unique")
    return tuple(pairs)


def deterministic_information_ceiling(
    pairs: Iterable[GeneratedQuantumPair],
    *,
    mode: QuantumViewMode,
) -> dict[str, object]:
    """Compute the exact majority ceiling for one model-visible view."""

    buckets: dict[str, list[QuantumObstructionVerdict]] = defaultdict(list)
    sample_count = 0
    for pair in pairs:
        pair.verify()
        for case in pair.cases:
            buckets[quantum_view_fingerprint(pair, case, mode)].append(case.gold)
            sample_count += 1
    if sample_count == 0:
        raise ValueError("information ceiling requires at least one case")
    best_correct = 0
    collision_bucket_count = 0
    for labels in buckets.values():
        counts = Counter(labels)
        best_correct += max(counts.values())
        if len(labels) > 1:
            collision_bucket_count += 1
    return {
        "schema": "ORIONQ.InformationCeiling.v0",
        "view_mode": mode.value,
        "sample_count": sample_count,
        "distinct_view_count": len(buckets),
        "collision_bucket_count": collision_bucket_count,
        "max_deterministic_accuracy": best_correct / sample_count,
    }


__all__ = [
    "GeneratedQuantumPair",
    "QuantumHostileFamily",
    "QuantumViewMode",
    "deterministic_information_ceiling",
    "generate_quantum_hostile_pair",
    "generate_quantum_pairs",
    "quantum_view_fingerprint",
    "quantum_view_payload",
]
