from __future__ import annotations

import dataclasses
import re
from enum import Enum
from typing import Any, Iterable, Mapping

from orion.discovery.recursive_atom_calculus_closure import (
    common_result_dispositions,
    interaction_witness_cases,
    negative_history_categories,
    post_map_saturation_rounds,
    recursion_stop_reasons,
)
from orion.engine.trace import MECHANIC_ID_BY_OPERATOR
from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.mechanics.model import MetricObservation
from orion.mechanics.program import observe_mechanics_program
from orion.registry import (
    CORE_OPERATOR_IDS,
    CORE_STATE_COORDINATES,
    FRAMEWORK_VERSION,
    MECHANICS_SUBSTRATE_IDS,
)
from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.development_fibre import (
    compile_development_fibre,
    rank_development_fibres,
)
from orion.self_orion.saturation_vector import DevelopmentSaturationAxis
from orion.kernel.saturation import GROWTH_COORDINATES
from orion.transfer.v2.p6_method_fibres import COORDS as METHOD_FIBRE_COORDINATES

from .workspace import ResearchWorkspace

EXPECTED_MECHANIC_CELL_COUNT = 59

_REQUIRED_ANCHORS = (
    "ORION_SOLVE.v1",
    "FRAME.v1",
    "FRAME.DECOMPOSE.v0",
    "SEARCH.v1",
    "ABSORB.v1",
    "RECONSTRUCT.v1",
    "DETECT.v1",
    "DIAGNOSE.v1",
    "REFRAME.v1",
    "REOPEN.v1",
    "REOPEN.FIBRE.v0",
    "SATURATE_BOUNDED.v3",
    "SATURATE.KNOWLEDGE_FLATNESS.v0",
    "SATURATE.FORMULATION_FLATNESS.v0",
    "SATURATE.ROUTE_COVERAGE.v0",
    "SATURATE.OMISSION_CHALLENGE.v0",
    "SATURATE.STOP.v0",
    "CROSS.AUTHORITY.v0",
    "CROSS.EXPERIENCE.v0",
    "CROSS.BENCHMARK.v0",
    "CROSS.EXPERIMENT_SELECTION.v0",
    "CROSS.EXECUTION.v0",
)

# These are routing/provenance references, not authority grants. They keep the
# harness discoverable without duplicating the paper formalism into another
# implementation.
_FAMILY_SOURCE_REFS: dict[str, tuple[str, ...]] = {
    "ORION_SOLVE": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/solver.py",
    ),
    "FRAME": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/mechanics/decomposition.py",
    ),
    "SEARCH": (
        "provenance/rakl/TRANSFER_INVENTORY_V1.md",
        "src/orion/engine/operators/search.py",
    ),
    "ABSORB": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/absorb.py",
    ),
    "RECONSTRUCT": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/reconstruct.py",
    ),
    "DETECT": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/detect.py",
    ),
    "DIAGNOSE": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/diagnose.py",
    ),
    "REFRAME": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/reframe.py",
    ),
    "REOPEN": (
        "provenance/rakl/PAPER_SALVAGE_LEDGER.md",
        "src/orion/engine/operators/reopen.py",
    ),
    "SATURATE_BOUNDED": (
        "provenance/rakl/TRANSFER_INVENTORY_V1.md",
        "docs/01-engine/saturation/README.md",
        "src/orion/kernel/saturation.py",
    ),
    "SATURATE": (
        "provenance/rakl/TRANSFER_INVENTORY_V1.md",
        "src/orion/mechanics/saturation_plan.py",
        "src/orion/self_orion/saturation_vector.py",
    ),
    "CROSS": (
        "provenance/rakl/TRANSFER_INVENTORY_V1.md",
        "src/orion/mechanics/decomposition.py",
    ),
}

_SPECIAL_SURFACES: tuple[dict[str, Any], ...] = (
    {
        "surface_id": "RUNTIME.MECHANICAL_CONTROL.v1",
        "kind": "CONTROL_SURFACE",
        "aliases": (
            "problem atomization",
            "problem questions",
            "mechanical planner",
            "research control",
        ),
        "purpose": "Generate deterministic research-control questions and required search queries from typed problem state and experience.",
        "source_refs": (
            "src/orion/runtime/mechanical_control.py",
            "src/orion/engine/mechanical_planner.py",
            "src/orion/engine/mechanical_questions.py",
        ),
        "authority": "NON_AUTHORIZING_CONTROL",
    },
    {
        "surface_id": "SELF_ORION.DEVELOPMENT_FIBRE.v1",
        "kind": "FIBRE_SURFACE",
        "aliases": (
            "problem fibre",
            "problem fiber",
            "development fibre",
            "development fiber",
            "fibre problem solver",
            "fiber problem solver",
        ),
        "purpose": "Compile the target-conditioned working view for one mechanic: open questions, empirical frontier, related/failure episodes and RAKL transfer receipt.",
        "source_refs": (
            "src/orion/self_orion/development_fibre.py",
            "provenance/rakl/TRANSFER_INVENTORY_V1.md",
        ),
        "authority": "DERIVED_WORKING_VIEW_ONLY",
    },
    {
        "surface_id": "SELF_ORION.RESEARCH_LOOP.v1",
        "kind": "RESEARCH_LOOP",
        "aliases": (
            "self orion research",
            "empirical frontier",
            "failure investigation",
        ),
        "purpose": "Turn ranked empirical mechanic work or a frozen observed failure into governed ORION research problems without self-promotion authority.",
        "source_refs": ("src/orion/self_orion/research_loop.py",),
        "authority": "PROPOSAL_EVIDENCE_ONLY",
    },
    {
        "surface_id": "SELF_ORION.DEVELOPMENT_SATURATION.v1",
        "kind": "SATURATION_SURFACE",
        "aliases": (
            "knowledge saturation",
            "development saturation",
            "saturation vector",
            "search saturation",
        ),
        "purpose": "Assess non-compensatory multi-axis development flatness; resource exhaustion cannot establish closure.",
        "source_refs": (
            "src/orion/self_orion/saturation_vector.py",
            "src/orion/kernel/saturation.py",
        ),
        "authority": "BOUNDED_FLATNESS_ONLY",
    },
    {
        "surface_id": "DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1",
        "kind": "ATOM_STUDY_SURFACE",
        "aliases": (
            "recursive atom",
            "atom calculus",
            "atomization",
            "atomisation",
            "decompose mechanic",
        ),
        "purpose": "Study whether a proposed epistemic mechanic deserves to exist, whether to decompose it, and when recursion must stop while preserving negative evidence.",
        "source_refs": (
            "src/orion/discovery/recursive_atom_calculus_closure.py",
            "research/extensions/orion-jump-recursive-atoms/RECURSIVE_ATOM_CALCULUS_CLOSURE_V1.md",
        ),
        "authority": "STUDY_CALCULUS_ONLY",
    },
    {
        "surface_id": "P6.METHOD_FIBRE.v1",
        "kind": "FORMAL_METHOD_FIBRE_SURFACE",
        "aliases": (
            "method fibre",
            "method fiber",
            "structural signature",
            "structural reduction",
            "method equivalence",
        ),
        "purpose": "Claim-relative formal structural reduction, signatures, evidence-bound fibre membership, substitution and composition checks.",
        "source_refs": (
            "src/orion/transfer/v2/p6_method_fibres.py",
            "src/orion/transfer/v2/p6_method_fibre_completion.py",
            "research/extensions/p6-method-fibres/METHOD_FIBRES_MANUSCRIPT_BRIDGE_V1.md",
        ),
        "authority": "FORMAL_EQUIVALENCE_FOR_DECLARED_CLAIM_ONLY",
    },
)

_ALIAS_TARGETS: dict[str, tuple[str, ...]] = {
    "atom": ("FRAME.DECOMPOSE.v0", "DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1"),
    "atomization": ("FRAME.DECOMPOSE.v0", "DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1"),
    "atomisation": ("FRAME.DECOMPOSE.v0", "DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1"),
    "decomposition": ("FRAME.DECOMPOSE.v0", "REFRAME.DECOMPOSITION.v0"),
    "fibre": ("SELF_ORION.DEVELOPMENT_FIBRE.v1", "REOPEN.FIBRE.v0", "FRAME.DECOMPOSE.v0", "P6.METHOD_FIBRE.v1"),
    "fiber": ("SELF_ORION.DEVELOPMENT_FIBRE.v1", "REOPEN.FIBRE.v0", "FRAME.DECOMPOSE.v0", "P6.METHOD_FIBRE.v1"),
    "problem fibre": ("SELF_ORION.DEVELOPMENT_FIBRE.v1", "FRAME.DECOMPOSE.v0", "REOPEN.FIBRE.v0"),
    "problem fiber": ("SELF_ORION.DEVELOPMENT_FIBRE.v1", "FRAME.DECOMPOSE.v0", "REOPEN.FIBRE.v0"),
    "method fibre": ("P6.METHOD_FIBRE.v1",),
    "method fiber": ("P6.METHOD_FIBRE.v1",),
    "saturation": ("SATURATE_BOUNDED.v3", "SATURATE.KNOWLEDGE_FLATNESS.v0", "SATURATE.ROUTE_COVERAGE.v0", "SATURATE.OMISSION_CHALLENGE.v0", "SATURATE.STOP.v0", "SELF_ORION.DEVELOPMENT_SATURATION.v1"),
    "knowledge saturation": ("SATURATE.KNOWLEDGE_FLATNESS.v0", "SELF_ORION.DEVELOPMENT_SATURATION.v1", "SATURATE.STOP.v0"),
    "problem solver": ("ORION_SOLVE.v1", "RUNTIME.MECHANICAL_CONTROL.v1", "SELF_ORION.RESEARCH_LOOP.v1"),
    "mechanical planner": ("RUNTIME.MECHANICAL_CONTROL.v1",),
}


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def canonical_mechanic_cells():
    """Return the actual locally-absorbed Self-ORION mechanics graph."""
    return SelfOrionDevelopmentDriver().local_transfer_cells()


def _family(mechanic_id: str) -> str:
    return mechanic_id.split(".", 1)[0]


def _parents(cells) -> dict[str, tuple[str, ...]]:
    parents: dict[str, list[str]] = {}
    for cell in cells:
        for child in cell.child_mechanic_ids:
            parents.setdefault(child, []).append(cell.mechanic_id)
    return {key: tuple(sorted(value)) for key, value in parents.items()}


def mechanic_catalog() -> tuple[dict[str, Any], ...]:
    cells = canonical_mechanic_cells()
    parent_map = _parents(cells)
    runtime_ids = set(MECHANIC_ID_BY_OPERATOR.values())
    rows = []
    for cell in cells:
        family = _family(cell.mechanic_id)
        rows.append(
            {
                "surface_id": cell.mechanic_id,
                "kind": "MECHANIC_CELL",
                "family": family,
                "purpose": cell.purpose,
                "scope": cell.scope,
                "parent_mechanic_ids": list(parent_map.get(cell.mechanic_id, ())),
                "child_mechanic_ids": list(cell.child_mechanic_ids),
                "dependency_ids": list(cell.dependency_ids),
                "external_dependency_contract_ids": list(cell.external_dependency_contract_ids),
                "empirical_open_coordinates": list(cell.empirical_open_coordinates),
                "provisional_dimensions": [item.value for item in cell.provisional_dimensions],
                "runtime_root_invoked": cell.mechanic_id in runtime_ids,
                "development_fibre_compilable": True,
                "source_refs": list(
                    _FAMILY_SOURCE_REFS.get(
                        family,
                        ("src/orion/mechanics/decomposition.py",),
                    )
                ),
                "authority": "MECHANIC_SPECIFICATION_AND_RUNTIME_RECEIPTS_DO_NOT_SELF_PROMOTE",
            }
        )
    return tuple(sorted(rows, key=lambda item: item["surface_id"]))


def special_surface_catalog() -> tuple[dict[str, Any], ...]:
    return tuple(_jsonable(item) for item in _SPECIAL_SURFACES)


def mechanics_coverage() -> dict[str, Any]:
    cells = canonical_mechanic_cells()
    ids = {cell.mechanic_id for cell in cells}
    metrics = observe_mechanics_program(cells)
    missing = tuple(sorted(set(_REQUIRED_ANCHORS) - ids))
    runtime_mechanics = tuple(sorted(set(MECHANIC_ID_BY_OPERATOR.values())))
    missing_runtime_cells = tuple(sorted(set(runtime_mechanics) - ids))
    structurally_discoverable = (
        len(cells) == EXPECTED_MECHANIC_CELL_COUNT
        and not missing
        and not missing_runtime_cells
        and metrics.unknown_child_count == 0
        and metrics.cycle_count == 0
        and metrics.unknown_dependency_count == 0
        and metrics.dependency_cycle_count == 0
        and metrics.mixed_cycle_count == 0
    )
    return {
        "schema": "ORION.ResearchHarnessMechanicsCoverage.v1",
        "framework_version": FRAMEWORK_VERSION,
        "authority": "STRUCTURAL_DISCOVERABILITY_ONLY__NOT_EMPIRICAL_OR_SCIENTIFIC_AUTHORITY",
        "expected_mechanic_cell_count": EXPECTED_MECHANIC_CELL_COUNT,
        "mechanic_cell_count": len(cells),
        "ready_mechanic_count": metrics.ready_mechanic_count,
        "open_question_count": metrics.open_question_count,
        "open_by_dimension": [list(item) for item in metrics.open_by_dimension],
        "unknown_child_count": metrics.unknown_child_count,
        "containment_cycle_count": metrics.cycle_count,
        "unknown_dependency_count": metrics.unknown_dependency_count,
        "dependency_cycle_count": metrics.dependency_cycle_count,
        "mixed_cycle_count": metrics.mixed_cycle_count,
        "required_anchor_ids": list(_REQUIRED_ANCHORS),
        "missing_anchor_ids": list(missing),
        "runtime_mechanic_ids": list(runtime_mechanics),
        "missing_runtime_cells": list(missing_runtime_cells),
        "core_operator_ids": list(CORE_OPERATOR_IDS),
        "core_state_coordinates": list(CORE_STATE_COORDINATES),
        "mechanics_substrate_ids": list(MECHANICS_SUBSTRATE_IDS),
        "special_surface_ids": [item["surface_id"] for item in _SPECIAL_SURFACES],
        "structurally_discoverable": structurally_discoverable,
        "note": (
            "Implemented canonical mechanics are discoverable through this harness. "
            "Research-only/proposed paper gaps remain explicit gaps and are not fabricated as runtime capability."
        ),
    }


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def navigate_mechanics(query: str, *, limit: int = 12) -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("mechanic navigation query is required")
    if limit < 1:
        raise ValueError("mechanic navigation limit must be positive")
    catalog = (*mechanic_catalog(), *special_surface_catalog())
    by_id = {item["surface_id"]: item for item in catalog}
    q = query.strip().casefold()
    q_tokens = _tokens(q)
    forced: list[str] = []
    for alias, targets in _ALIAS_TARGETS.items():
        if alias in q or q in alias:
            for target in targets:
                if target not in forced:
                    forced.append(target)

    scored: list[tuple[int, str, dict[str, Any]]] = []
    for item in catalog:
        surface_id = item["surface_id"]
        fields = [surface_id, str(item.get("purpose", "")), str(item.get("scope", ""))]
        fields.extend(map(str, item.get("aliases", ())))
        fields.extend(map(str, item.get("source_refs", ())))
        text = " ".join(fields).casefold()
        tokens = _tokens(text)
        score = 0
        if surface_id in forced:
            score += 1000 - forced.index(surface_id)
        if q == surface_id.casefold():
            score += 800
        if q in text:
            score += 120
        score += 12 * len(q_tokens & tokens)
        if any(token in surface_id.casefold() for token in q_tokens):
            score += 20
        if score > 0:
            scored.append((score, surface_id, item))
    selected = [item for _, _, item in sorted(scored, key=lambda row: (-row[0], row[1]))[:limit]]
    return {
        "schema": "ORION.ResearchHarnessMechanicNavigation.v1",
        "query": query,
        "matches": selected,
        "match_count": len(selected),
        "authority": "NAVIGATION_ONLY",
    }


def mechanic_detail(mechanic_id: str) -> dict[str, Any]:
    by_id = {
        item["surface_id"]: item
        for item in (*mechanic_catalog(), *special_surface_catalog())
    }
    if mechanic_id not in by_id:
        raise KeyError(f"unknown ORION mechanic/surface: {mechanic_id}")
    return by_id[mechanic_id]


def _metric_observation(raw: Mapping[str, Any]) -> MetricObservation:
    return MetricObservation(
        metric_id=str(raw["metric_id"]),
        value=raw["value"],
        unit=str(raw["unit"]),
        evidence_ids=tuple(map(str, raw.get("evidence_ids", ()))),
        uncertainty=raw.get("uncertainty"),
    )


def _task_episode(raw: Mapping[str, Any]) -> TaskEpisode:
    return TaskEpisode(
        episode_id=str(raw["episode_id"]),
        task_id=str(raw["task_id"]),
        run_id=str(raw["run_id"]),
        parent_run_id=None if raw.get("parent_run_id") is None else str(raw["parent_run_id"]),
        evaluation_epoch_id=str(raw["evaluation_epoch_id"]),
        split_id=str(raw["split_id"]),
        mechanic_id=str(raw["mechanic_id"]),
        problem_signature=tuple(map(str, raw.get("problem_signature", ()))),
        variation_signature=tuple(map(str, raw.get("variation_signature", ()))),
        pre_state_hash=str(raw["pre_state_hash"]),
        action_ids=tuple(map(str, raw.get("action_ids", ()))),
        observation_ids=tuple(map(str, raw.get("observation_ids", ()))),
        outcome=EpisodeOutcome(str(raw["outcome"])),
        failure_signature=tuple(map(str, raw.get("failure_signature", ()))),
        residual_ids=tuple(map(str, raw.get("residual_ids", ()))),
        evidence_ids=tuple(map(str, raw.get("evidence_ids", ()))),
        evidence_bindings=tuple(
            (str(item[0]), str(item[1])) for item in raw.get("evidence_bindings", ())
        ),
        post_state_hash=str(raw["post_state_hash"]),
        timestamp=str(raw["timestamp"]),
        producer_process_lineage_hash=(
            None if raw.get("producer_process_lineage_hash") is None
            else str(raw["producer_process_lineage_hash"])
        ),
        evaluator_artifact_hash=(
            None if raw.get("evaluator_artifact_hash") is None
            else str(raw["evaluator_artifact_hash"])
        ),
        source_receipt_id=(
            None if raw.get("source_receipt_id") is None else str(raw["source_receipt_id"])
        ),
        output_artifact_ids=tuple(map(str, raw.get("output_artifact_ids", ()))),
        handoff_values=tuple(
            (str(item[0]), str(item[1])) for item in raw.get("handoff_values", ())
        ),
        metric_observations=tuple(
            _metric_observation(item) for item in raw.get("metric_observations", ())
        ),
        provenance_ids=tuple(map(str, raw.get("provenance_ids", ()))),
        cost_units=raw.get("cost_units"),
        latency_seconds=raw.get("latency_seconds"),
    )


def workspace_episodes(workspace: ResearchWorkspace) -> tuple[TaskEpisode, ...]:
    episodes: dict[str, TaskEpisode] = {}
    for run_id in workspace.run_ids():
        run = workspace.load_run(run_id)
        raw_episodes = run.get("experience_episodes", ())
        if not isinstance(raw_episodes, list):
            raise TypeError(f"run {run_id} experience_episodes must be an array")
        for raw in raw_episodes:
            if not isinstance(raw, Mapping):
                raise TypeError(f"run {run_id} experience episode must be an object")
            episode = _task_episode(raw)
            existing = episodes.get(episode.episode_id)
            if existing is not None and existing != episode:
                raise ValueError(f"episode identity collision: {episode.episode_id}")
            episodes[episode.episode_id] = episode
    return tuple(episodes[key] for key in sorted(episodes))


def compile_workspace_development_fibre(
    workspace: ResearchWorkspace,
    mechanic_id: str,
) -> dict[str, Any]:
    cells = canonical_mechanic_cells()
    fibre = compile_development_fibre(
        mechanic_id,
        cells,
        episodes=workspace_episodes(workspace),
    )
    return {
        "schema": "ORION.ResearchHarnessDevelopmentFibre.v1",
        "authority": "DERIVED_WORKING_VIEW_ONLY__NO_PROMOTION_AUTHORITY",
        "fibre": _jsonable(fibre),
        "mechanic": mechanic_detail(mechanic_id),
    }


def rank_workspace_development_fibres(
    workspace: ResearchWorkspace,
    *,
    limit: int = 12,
) -> dict[str, Any]:
    fibres = rank_development_fibres(
        canonical_mechanic_cells(),
        episodes=workspace_episodes(workspace),
        limit=limit,
    )
    return {
        "schema": "ORION.ResearchHarnessDevelopmentFibreRanking.v1",
        "authority": "WORK_PRIORITIZATION_ONLY__NO_PROMOTION_AUTHORITY",
        "fibres": [_jsonable(item) for item in fibres],
    }


def atom_calculus_surface() -> dict[str, Any]:
    return {
        "schema": "ORION.ResearchHarnessRecursiveAtomCalculusSurface.v1",
        "authority": "STUDY_CALCULUS_ONLY__NO_ATOM_OR_NOVELTY_AUTHORITY",
        "dispositions": [item.value for item in common_result_dispositions()],
        "recursion_stop_reasons": [item.value for item in recursion_stop_reasons()],
        "negative_history_categories": [item.value for item in negative_history_categories()],
        "post_map_saturation_rounds": [_jsonable(item) for item in post_map_saturation_rounds()],
        "interaction_witness_cases": [_jsonable(item) for item in interaction_witness_cases()],
        "source_refs": list(mechanic_detail("DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1")["source_refs"]),
    }


def saturation_surface() -> dict[str, Any]:
    return {
        "schema": "ORION.ResearchHarnessSaturationSurface.v1",
        "authority": "BOUNDED_FLATNESS_ONLY__NO_ABSOLUTE_COMPLETENESS",
        "runtime_growth_coordinates": list(GROWTH_COORDINATES),
        "development_saturation_axes": [item.value for item in DevelopmentSaturationAxis],
        "mechanic_ids": [
            "SATURATE_BOUNDED.v3",
            "SATURATE.KNOWLEDGE_FLATNESS.v0",
            "SATURATE.FORMULATION_FLATNESS.v0",
            "SATURATE.ROUTE_COVERAGE.v0",
            "SATURATE.OMISSION_CHALLENGE.v0",
            "SATURATE.STOP.v0",
        ],
        "source_refs": list(mechanic_detail("SELF_ORION.DEVELOPMENT_SATURATION.v1")["source_refs"]),
    }


def method_fibre_surface() -> dict[str, Any]:
    return {
        "schema": "ORION.ResearchHarnessMethodFibreSurface.v1",
        "authority": "FORMAL_EQUIVALENCE_FOR_DECLARED_CLAIM_ONLY__NO_TRANSFER_AUTHORITY",
        "claim_relative_coordinates": list(METHOD_FIBRE_COORDINATES),
        "source_refs": list(mechanic_detail("P6.METHOD_FIBRE.v1")["source_refs"]),
    }


def run_mechanic_receipts(workspace: ResearchWorkspace, run_id: str) -> dict[str, Any]:
    run = workspace.load_run(run_id)
    trace = run.get("trace")
    if not isinstance(trace, Mapping):
        raise TypeError("run trace must be an object")
    events = trace.get("events")
    if not isinstance(events, list):
        raise TypeError("run trace events must be an array")
    rows = []
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise TypeError("trace event must be an object")
        receipt = event.get("receipt")
        if not isinstance(receipt, Mapping):
            raise TypeError("trace event receipt must be an object")
        rows.append(
            {
                "index": index,
                "operator": event.get("operator"),
                "epoch": event.get("epoch"),
                "summary": event.get("summary"),
                "mechanic_id": receipt.get("mechanic_id"),
                "status": receipt.get("status"),
                "receipt_id": receipt.get("receipt_id"),
                "action_ids": receipt.get("action_ids"),
                "residual_ids": receipt.get("residual_ids"),
                "evidence_ids": receipt.get("evidence_ids"),
                "failure_signature": receipt.get("failure_signature"),
                "handoff_values": receipt.get("handoff_values"),
            }
        )
    return {
        "schema": "ORION.ResearchHarnessRunMechanics.v1",
        "run_id": run_id,
        "trace_id": trace.get("trace_id"),
        "mechanic_receipts": rows,
        "authority": "TRACE_INSPECTION_ONLY",
    }
