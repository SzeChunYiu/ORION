"""Objective hidden worlds for P1 epistemic-mutation necessity v2.2.

The candidate sees repair/test descriptions but never the protected response
matrix. Gold validity is derived from counterfactual responses and an explicit
K/W/M level order, not from the ORION licensing implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import random
from typing import Iterable


class RepairLevel(str, Enum):
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"
    FORMULATION = "FORMULATION"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"


LEVEL_ORDER = {
    RepairLevel.EVIDENCE: 0,
    RepairLevel.EXECUTION: 1,
    RepairLevel.FORMULATION: 2,
    RepairLevel.SEARCH_UNIVERSE: 2,
}


@dataclass(frozen=True)
class PublicRepair:
    repair_id: str
    level: RepairLevel
    coordinate: str
    declared_cost: float
    proposal_confidence: float

    def to_payload(self) -> dict:
        return {
            "repair_id": self.repair_id,
            "level": self.level.value,
            "coordinate": self.coordinate,
            "declared_cost": self.declared_cost,
            "proposal_confidence": self.proposal_confidence,
        }


@dataclass(frozen=True)
class PublicDiagnosticProbe:
    probe_id: str
    description: str
    declared_cost: float = 1.0

    def to_payload(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "description": self.description,
            "declared_cost": self.declared_cost,
        }


@dataclass(frozen=True)
class PublicDependency:
    closure_id: str
    parent_ids: tuple[str, ...]
    declared_coordinate: str

    def to_payload(self) -> dict:
        return {
            "closure_id": self.closure_id,
            "parent_ids": list(self.parent_ids),
            "declared_coordinate": self.declared_coordinate,
        }


@dataclass(frozen=True)
class NecessityPublicWorld:
    task_id: str
    surface: str
    initial_high_level_confidence: float
    repairs: tuple[PublicRepair, ...]
    diagnostic_probes: tuple[PublicDiagnosticProbe, ...]
    dependencies: tuple[PublicDependency, ...]

    def to_payload(self) -> dict:
        return {
            "task_id": self.task_id,
            "surface": self.surface,
            "initial_high_level_confidence": self.initial_high_level_confidence,
            "repairs": [item.to_payload() for item in self.repairs],
            "diagnostic_probes": [item.to_payload() for item in self.diagnostic_probes],
            "dependencies": [item.to_payload() for item in self.dependencies],
        }


@dataclass(frozen=True)
class RepairResponse:
    target_success: bool
    protected_sibling_ok: bool
    observed_invalidated_ids: tuple[str, ...]

    def to_payload(self) -> dict:
        return {
            "target_success": self.target_success,
            "protected_sibling_ok": self.protected_sibling_ok,
            "observed_invalidated_ids": list(self.observed_invalidated_ids),
        }


@dataclass(frozen=True)
class ProbeResponse:
    observation: str

    def to_payload(self) -> dict:
        return {"observation": self.observation}


@dataclass(frozen=True)
class NecessityProtectedWorld:
    family_id: str
    true_level: RepairLevel
    response_by_repair: tuple[tuple[str, RepairResponse], ...]
    response_by_probe: tuple[tuple[str, ProbeResponse], ...]
    gold_minimal_repair_ids: tuple[str, ...]
    gold_dependency_impact_ids: tuple[str, ...]
    hidden_shift: bool
    negative_control: bool

    def repair_response(self, repair_id: str) -> RepairResponse:
        return dict(self.response_by_repair)[repair_id]

    def probe_response(self, probe_id: str) -> ProbeResponse:
        return dict(self.response_by_probe)[probe_id]

    def to_payload(self) -> dict:
        return {
            "family_id": self.family_id,
            "true_level": self.true_level.value,
            "response_by_repair": {
                key: value.to_payload() for key, value in self.response_by_repair
            },
            "response_by_probe": {
                key: value.to_payload() for key, value in self.response_by_probe
            },
            "gold_minimal_repair_ids": list(self.gold_minimal_repair_ids),
            "gold_dependency_impact_ids": list(self.gold_dependency_impact_ids),
            "hidden_shift": self.hidden_shift,
            "negative_control": self.negative_control,
        }


@dataclass(frozen=True)
class NecessityWorld:
    public: NecessityPublicWorld
    protected: NecessityProtectedWorld


_FAMILY_LEVEL = {
    "hidden_parent_domain_search_universe": RepairLevel.SEARCH_UNIVERSE,
    "hidden_representation_formulation": RepairLevel.FORMULATION,
    "hidden_decomposition_formulation": RepairLevel.FORMULATION,
    "hidden_measurement_formulation": RepairLevel.FORMULATION,
    "evidence_only_control": RepairLevel.EVIDENCE,
    "execution_only_control": RepairLevel.EXECUTION,
}

_HIDDEN_FAMILIES = tuple(key for key in _FAMILY_LEVEL if key.startswith("hidden_"))
_CONTROL_FAMILIES = ("evidence_only_control", "execution_only_control")
_SURFACES = tuple(
    f"Frozen research task exhibits unresolved signature U{i:02d}; choose bounded diagnostic/repair actions."
    for i in range(20)
)


def _opaque(prefix: str, *parts: object) -> str:
    body = ":".join(str(item) for item in parts)
    return f"{prefix}-{hashlib.sha256(body.encode()).hexdigest()[:16]}"


def _dependency_graph(task_id: str, coordinate: str, depth: int) -> tuple[PublicDependency, ...]:
    root = _opaque("dep", task_id, "root")
    rows = [PublicDependency(root, (), coordinate)]
    parent = root
    for index in range(1, depth):
        child = _opaque("dep", task_id, "child", index)
        rows.append(PublicDependency(child, (parent,), "DERIVED"))
        parent = child
    rows.append(PublicDependency(_opaque("dep", task_id, "unrelated"), (), "UNRELATED"))
    return tuple(rows)


def _impact_for(repair: PublicRepair, dependencies: tuple[PublicDependency, ...]) -> tuple[str, ...]:
    if repair.level not in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}:
        return ()
    direct = {
        item.closure_id
        for item in dependencies
        if item.declared_coordinate == repair.coordinate
    }
    selected = set(direct)
    changed = True
    while changed:
        changed = False
        for item in dependencies:
            if item.closure_id in selected:
                continue
            if any(parent in selected for parent in item.parent_ids):
                selected.add(item.closure_id)
                changed = True
    return tuple(item.closure_id for item in dependencies if item.closure_id in selected)


def _cost(rng: random.Random) -> float:
    # Cost is intentionally independent of causal level and gold validity.
    return round(0.80 + 0.40 * rng.random(), 3)


def _confidence(rng: random.Random, *, hidden_shift: bool) -> float:
    # Overlapping distributions: confidence alone cannot safely distinguish
    # genuine high-level shifts from controls.
    low, high = ((0.72, 0.96) if hidden_shift else (0.58, 0.92))
    return round(low + (high - low) * rng.random(), 3)


def _repair_set(rng: random.Random, *, task_id: str, true_level: RepairLevel, family_id: str) -> tuple[PublicRepair, ...]:
    high_coordinate = {
        "hidden_parent_domain_search_universe": "W.ACTIVE_DOMAINS",
        "hidden_representation_formulation": "W.REPRESENTATIONS",
        "hidden_decomposition_formulation": "W.DECOMPOSITION",
        "hidden_measurement_formulation": "M.MEASUREMENT",
    }.get(family_id, "W.REPRESENTATIONS")
    high_level = RepairLevel.SEARCH_UNIVERSE if "parent_domain" in family_id else RepairLevel.FORMULATION
    repairs = [
        PublicRepair(_opaque("repair", task_id, "evidence"), RepairLevel.EVIDENCE, "", _cost(rng), round(0.45 + 0.25 * rng.random(), 3)),
        PublicRepair(_opaque("repair", task_id, "execution"), RepairLevel.EXECUTION, "", _cost(rng), round(0.45 + 0.25 * rng.random(), 3)),
        PublicRepair(_opaque("repair", task_id, "high-primary"), high_level, high_coordinate, _cost(rng), _confidence(rng, hidden_shift=true_level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE})),
        PublicRepair(_opaque("repair", task_id, "high-decoy"), high_level, high_coordinate, _cost(rng), _confidence(rng, hidden_shift=False)),
    ]
    rng.shuffle(repairs)
    return tuple(repairs)


def _probes(task_id: str) -> tuple[PublicDiagnosticProbe, ...]:
    probes = [
        PublicDiagnosticProbe(_opaque("probe", task_id, "source"), "check whether the missing evidence is already available under the current search universe"),
        PublicDiagnosticProbe(_opaque("probe", task_id, "execution"), "check whether the current implementation/environment can execute the existing formulation"),
        PublicDiagnosticProbe(_opaque("probe", task_id, "high"), "check whether a formulation/search-universe change is causally implicated after lower-level alternatives"),
    ]
    return tuple(probes)


def _probe_responses(public: NecessityPublicWorld, true_level: RepairLevel) -> tuple[tuple[str, ProbeResponse], ...]:
    source = next(item for item in public.diagnostic_probes if item.description.startswith("check whether the missing evidence"))
    execution = next(item for item in public.diagnostic_probes if item.description.startswith("check whether the current implementation"))
    high = next(item for item in public.diagnostic_probes if item.description.startswith("check whether a formulation"))
    return (
        (source.probe_id, ProbeResponse("SOURCE_GAP" if true_level is RepairLevel.EVIDENCE else "SOURCE_OK")),
        (execution.probe_id, ProbeResponse("EXECUTION_GAP" if true_level is RepairLevel.EXECUTION else "EXECUTION_OK")),
        (high.probe_id, ProbeResponse("HIGH_LEVEL_IMPLICATED" if true_level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE} else "HIGH_LEVEL_NOT_NEEDED")),
    )


def _world_from_family(rng: random.Random, *, seed: int, family_id: str, index: int) -> NecessityWorld:
    true_level = _FAMILY_LEVEL[family_id]
    hidden_shift = family_id in _HIDDEN_FAMILIES
    task_id = _opaque("p1nc", seed, family_id, index)
    surface = _SURFACES[index % len(_SURFACES)]
    coordinate = {
        "hidden_parent_domain_search_universe": "W.ACTIVE_DOMAINS",
        "hidden_representation_formulation": "W.REPRESENTATIONS",
        "hidden_decomposition_formulation": "W.DECOMPOSITION",
        "hidden_measurement_formulation": "M.MEASUREMENT",
    }.get(family_id, "")
    dependencies = _dependency_graph(task_id, coordinate, 1 + (index % 4))
    repairs = _repair_set(rng, task_id=task_id, true_level=true_level, family_id=family_id)
    probes = _probes(task_id)
    high_confidence = max(
        item.proposal_confidence
        for item in repairs
        if item.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}
    )
    public = NecessityPublicWorld(
        task_id=task_id,
        surface=surface,
        initial_high_level_confidence=high_confidence,
        repairs=repairs,
        diagnostic_probes=probes,
        dependencies=dependencies,
    )

    responses: list[tuple[str, RepairResponse]] = []
    for repair in repairs:
        impact = _impact_for(repair, dependencies)
        if repair.level is true_level:
            target_success = True
            sibling_ok = True
        elif true_level in {RepairLevel.EVIDENCE, RepairLevel.EXECUTION} and repair.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}:
            # A high-level reframe often masks the motivating symptom even when
            # a lower-level repair is sufficient. Half are locally safe but
            # still unnecessary; half additionally break a protected sibling.
            target_success = True
            sibling_ok = (index % 2 == 0)
        elif true_level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE} and repair.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}:
            # One high-level proposal is the valid mutation; the other is a
            # plausible target-flip that fails a protected sibling. The v2
            # wrapper randomizes which public proposal is objectively safe.
            target_success = True
            sibling_ok = False
        else:
            target_success = False
            sibling_ok = True
        responses.append((repair.repair_id, RepairResponse(target_success, sibling_ok, impact)))

    # Base-v1 compatibility: mark the highest-confidence high-level proposal
    # safe. The v2 generator subsequently swaps safety on a parity-balanced
    # subset, breaking confidence/gold alignment before any confirmatory use.
    if hidden_shift:
        high_repairs = sorted(
            (item for item in repairs if item.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}),
            key=lambda item: (-item.proposal_confidence, item.repair_id),
        )
        safe_id = high_repairs[0].repair_id
        rewritten = []
        for repair_id, response in responses:
            if repair_id == safe_id:
                response = RepairResponse(True, True, response.observed_invalidated_ids)
            rewritten.append((repair_id, response))
        responses = rewritten

    response_map = dict(responses)
    successful = [
        repair
        for repair in repairs
        if response_map[repair.repair_id].target_success
        and response_map[repair.repair_id].protected_sibling_ok
    ]
    min_level = min(LEVEL_ORDER[item.level] for item in successful)
    valid_minimal = [item.repair_id for item in successful if LEVEL_ORDER[item.level] == min_level]
    gold_impact = ()
    if true_level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}:
        gold_impact = response_map[valid_minimal[0]].observed_invalidated_ids
    protected = NecessityProtectedWorld(
        family_id=family_id,
        true_level=true_level,
        response_by_repair=tuple(responses),
        response_by_probe=_probe_responses(public, true_level),
        gold_minimal_repair_ids=tuple(sorted(valid_minimal)),
        gold_dependency_impact_ids=gold_impact,
        hidden_shift=hidden_shift,
        negative_control=not hidden_shift,
    )
    return NecessityWorld(public, protected)


def generate_necessity_worlds(*, seed: int, hidden_shift_n: int = 480, control_n: int = 2400) -> tuple[NecessityWorld, ...]:
    if hidden_shift_n % len(_HIDDEN_FAMILIES) != 0:
        raise ValueError("hidden_shift_n must divide evenly across four hidden families")
    if control_n % len(_CONTROL_FAMILIES) != 0:
        raise ValueError("control_n must divide evenly across two control families")
    rng = random.Random(seed)
    rows: list[NecessityWorld] = []
    per_hidden = hidden_shift_n // len(_HIDDEN_FAMILIES)
    per_control = control_n // len(_CONTROL_FAMILIES)
    for family_id in _HIDDEN_FAMILIES:
        for index in range(per_hidden):
            rows.append(_world_from_family(rng, seed=seed, family_id=family_id, index=index))
    for family_id in _CONTROL_FAMILIES:
        for index in range(per_control):
            rows.append(_world_from_family(rng, seed=seed, family_id=family_id, index=index))
    rng.shuffle(rows)
    return tuple(rows)


def candidate_view_leaks(world: NecessityPublicWorld) -> tuple[str, ...]:
    blob = json.dumps(world.to_payload(), sort_keys=True).lower()
    leaks = []
    for forbidden in (
        "family_id",
        "true_level",
        "response_by_repair",
        "protected_sibling_ok",
        "gold_minimal_repair_ids",
        "gold_dependency_impact_ids",
        "hidden_shift",
        "negative_control",
    ):
        if forbidden in blob:
            leaks.append(forbidden)
    return tuple(leaks)


def serialize_public(worlds: Iterable[NecessityWorld]) -> bytes:
    return b"".join(
        (json.dumps(item.public.to_payload(), sort_keys=True, separators=(",", ":")) + "\n").encode()
        for item in worlds
    )


def serialize_protected(worlds: Iterable[NecessityWorld]) -> bytes:
    return b"".join(
        (
            json.dumps(
                {"task_id": item.public.task_id, "protected": item.protected.to_payload()},
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode()
        for item in worlds
    )


def world_manifest(worlds: tuple[NecessityWorld, ...]) -> dict:
    public = serialize_public(worlds)
    protected = serialize_protected(worlds)
    leaks = {
        item.public.task_id: candidate_view_leaks(item.public)
        for item in worlds
        if candidate_view_leaks(item.public)
    }
    return {
        "schema_version": "P1.mutation-necessity-worlds.v1",
        "n": len(worlds),
        "hidden_shift_n": sum(item.protected.hidden_shift for item in worlds),
        "negative_control_n": sum(item.protected.negative_control for item in worlds),
        "by_family": {
            family: sum(item.protected.family_id == family for item in worlds)
            for family in _FAMILY_LEVEL
        },
        "public_sha256": hashlib.sha256(public).hexdigest(),
        "protected_sha256": hashlib.sha256(protected).hexdigest(),
        "candidate_view_leak_count": len(leaks),
        "candidate_view_leaks": {key: list(value) for key, value in leaks.items()},
    }


__all__ = [
    "LEVEL_ORDER",
    "NecessityProtectedWorld",
    "NecessityPublicWorld",
    "NecessityWorld",
    "ProbeResponse",
    "PublicDependency",
    "PublicDiagnosticProbe",
    "PublicRepair",
    "RepairLevel",
    "RepairResponse",
    "candidate_view_leaks",
    "generate_necessity_worlds",
    "serialize_protected",
    "serialize_public",
    "world_manifest",
]
