from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from enum import Enum
from typing import Any

from orion.core.problem import Problem
from orion.core.problem_tree import (
    DiscriminatorKind,
    DiscriminatorSpec,
    ProblemAtom,
    ProblemDecomposition,
    RecursiveProblemStopReason,
    ResidualAtom,
    ResidualDecomposition,
)
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.state import OrionState
from orion.engine.mechanical_questions import (
    MechanicalProblemContext,
    generate_problem_questions,
)
from orion.providers.reasoner.llm import LLMResearchReasoner
from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.development_fibre import compile_development_fibre


_DECOMPOSITION_INSTRUCTION = (
    "Treat the target as a research problem. Return a decision-separating recursive "
    "decomposition, not a paraphrase. Each atom must be strictly narrower and must "
    "have exactly one concrete discriminator. Prefer a cheaper valid dominance, "
    "formal, exact-computation or donor-subsumption test over an expensive experiment "
    "when it can settle the same atom. Preserve interaction-only possibilities. If "
    "no finer identifiable split exists, return no atoms and an explicit stop_reason. "
    "Use the model-free mechanical questions, DevelopmentFibre context and negative "
    "history as constraints/evidence about what remains open; do not merely echo them. "
    "Never grant scientific, novelty, adoption, promotion, merge or global-stop authority."
)

_RESPONSIBILITY_MECHANIC = {
    Responsibility.QUESTION: "FRAME.QUESTION.v0",
    Responsibility.REPRESENTATION: "REFRAME.REPRESENTATION.v0",
    Responsibility.SEARCH: "SEARCH.ROUTE.v0",
    Responsibility.ROUTING: "SEARCH.ROUTE.v0",
    Responsibility.DECOMPOSITION: "REFRAME.DECOMPOSITION.v0",
    Responsibility.INTERFACE: "REFRAME.REPRESENTATION.v0",
    Responsibility.MEASUREMENT: "DIAGNOSE.DISCRIMINATOR.v0",
    Responsibility.EVALUATOR: "CROSS.BENCHMARK.v0",
    Responsibility.METHOD: "REFRAME.METHOD.v0",
    Responsibility.EVIDENCE: "SEARCH.QUERY.v0",
    Responsibility.EXECUTION: "CROSS.EXECUTION.v0",
}

_KIND_MECHANIC = {
    ResidualKind.MISSING_EVIDENCE: "SEARCH.QUERY.v0",
    ResidualKind.CONTRADICTION: "DETECT.CONTRADICTION.v0",
    ResidualKind.CONTEXT_GAP: "FRAME.CONTEXT.v0",
    ResidualKind.REPRESENTATION_FAILURE: "REFRAME.REPRESENTATION.v0",
    ResidualKind.SEARCH_COVERAGE_FAILURE: "SEARCH.ROUTE.v0",
    ResidualKind.DECOMPOSITION_FAILURE: "REFRAME.DECOMPOSITION.v0",
    ResidualKind.INTERFACE_FAILURE: "REFRAME.REPRESENTATION.v0",
    ResidualKind.MEASUREMENT_FAILURE: "DIAGNOSE.DISCRIMINATOR.v0",
    ResidualKind.EVALUATOR_FAILURE: "CROSS.BENCHMARK.v0",
    ResidualKind.METHOD_GAP: "REFRAME.METHOD.v0",
    ResidualKind.UNCLASSIFIED: "DIAGNOSE.HYPOTHESES.v0",
}


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _required_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _string_array(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be an array")
    return tuple(_required_string(item, f"{name} entry") for item in value)


def _metadata(value: object, name: str) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be an object")
    rows: list[tuple[str, str]] = []
    for key, item in value.items():
        rows.append(
            (
                _required_string(key, f"{name} key"),
                _required_string(item, f"{name}.{key}"),
            )
        )
    return tuple(sorted(rows))


def _discriminator(raw: object, name: str) -> DiscriminatorSpec:
    if not isinstance(raw, Mapping):
        raise TypeError(f"{name} must be an object")
    cost = raw.get("expected_cost_units")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)):
        raise TypeError(f"{name}.expected_cost_units must be numeric")
    return DiscriminatorSpec(
        discriminator_id=_required_string(
            raw.get("discriminator_id"), f"{name}.discriminator_id"
        ),
        kind=DiscriminatorKind(_required_string(raw.get("kind"), f"{name}.kind")),
        question=_required_string(raw.get("question"), f"{name}.question"),
        success_criterion=_required_string(
            raw.get("success_criterion"), f"{name}.success_criterion"
        ),
        expected_cost_units=float(cost),
        metadata=_metadata(raw.get("metadata", {}), f"{name}.metadata"),
    )


def _stop_reason(value: object) -> RecursiveProblemStopReason | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("stop_reason must be a string or null")
    return RecursiveProblemStopReason(value)


def _flat_rounds(state: OrionState) -> int:
    count = 0
    for record in reversed(state.iterations):
        if (
            bool(getattr(record, "semantic_flat", False))
            and bool(getattr(record, "search_universe_flat", False))
            and bool(getattr(record, "formulation_flat", False))
        ):
            count += 1
        else:
            break
    return count


def _mechanical_questions(problem: Problem, state: OrionState) -> list[dict[str, Any]]:
    context = MechanicalProblemContext(
        evidence_ids=state.knowledge.evidence_ids,
        residual_ids=state.knowledge.residual_ids,
        active_domain_ids=state.search_universe.active_domain_ids,
        searched_domain_ids=state.search_universe.searched_domain_ids,
        completed_route_kind_ids=state.search_universe.route_kind_ids,
        recent_flat_rounds=_flat_rounds(state),
        verified_target=any(
            getattr(claim.authority, "value", "") == "VERIFIED"
            for claim in state.knowledge.claims
        ),
    )
    return [
        {
            "question_id": item.question_id,
            "kind": item.kind.value,
            "question": item.question,
            "route_kind": None if item.route_kind is None else item.route_kind.value,
            "action_hint": item.action_hint,
            "blocking": item.blocking,
        }
        for item in generate_problem_questions(problem, context)
    ]


def _affected_mechanic_ids(residual: Residual) -> tuple[str, ...]:
    ids: list[str] = [
        "DIAGNOSE.HYPOTHESES.v0",
        "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0",
        "DIAGNOSE.DISCRIMINATOR.v0",
        "DIAGNOSE.ATTRIBUTION.v0",
        "REOPEN.FIBRE.v0",
    ]
    for responsibility in residual.candidate_responsibilities:
        owner = _RESPONSIBILITY_MECHANIC.get(responsibility)
        if owner is not None:
            ids.append(owner)
    owner = _KIND_MECHANIC.get(residual.kind)
    if owner is not None:
        ids.append(owner)
    return tuple(dict.fromkeys(ids))


def _automatic_fibre_context(residual: Residual) -> list[dict[str, Any]]:
    cells = SelfOrionDevelopmentDriver().local_transfer_cells()
    known = {cell.mechanic_id for cell in cells}
    rows: list[dict[str, Any]] = []
    for mechanic_id in _affected_mechanic_ids(residual):
        if mechanic_id not in known:
            continue
        fibre = compile_development_fibre(mechanic_id, cells, episodes=())
        rows.append(
            {
                "source": "AUTOMATIC_REOPEN_FIBRE",
                "mechanic_id": mechanic_id,
                "fibre": _jsonable(fibre),
                "authority": "DERIVED_WORKING_VIEW_ONLY",
            }
        )
    return rows


class RecursiveLLMResearchReasoner(LLMResearchReasoner):
    """Canonical reasoner plus non-authorizing problem/residual decomposition.

    The semantic model does not own recursion control. Model-free mechanical questions,
    automatically reopened DevelopmentFibres, negative history, cost ordering and the
    recursive controller constrain the decomposition. The model proposes child semantics only.
    """

    def __init__(self, provider) -> None:
        super().__init__(provider)
        self._development_fibre_context: tuple[Mapping[str, Any], ...] = ()

    def set_development_fibre_context(
        self, rows: Sequence[Mapping[str, Any]]
    ) -> None:
        if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
            raise TypeError("development fibre context must be an array")
        normalized: list[Mapping[str, Any]] = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise TypeError("development fibre context entries must be objects")
            normalized.append(dict(row))
        self._development_fibre_context = tuple(normalized)

    def clear_development_fibre_context(self) -> None:
        self._development_fibre_context = ()

    def decompose_problem(
        self, problem: Problem, state: OrionState
    ) -> ProblemDecomposition:
        data = self._call(
            "decompose_problem",
            {
                "problem": asdict(problem),
                "known_evidence_ids": list(state.knowledge.evidence_ids),
                "known_residual_ids": list(state.knowledge.residual_ids),
                "known_negative_history_ids": list(state.knowledge.negative_history_ids),
                "active_domains": list(state.search_universe.active_domain_ids),
                "representations": list(state.search_universe.representation_ids),
                "mechanical_questions": _mechanical_questions(problem, state),
                "instruction": _DECOMPOSITION_INSTRUCTION,
            },
            (
                '{"atoms":[{"atom_id":"...","question":"...",'
                '"responsibility":"QUESTION","scope":"...","initial_domain_ids":[],'
                '"metadata":{},"discriminator":{"discriminator_id":"...",'
                '"kind":"DOMINANCE_PROOF","question":"...",'
                '"success_criterion":"...","expected_cost_units":1.0,'
                '"metadata":{}}}],"stop_reason":null,"rationale":"..."}'
            ),
        )
        raw_atoms = data.get("atoms", [])
        if not isinstance(raw_atoms, list):
            raise TypeError("decompose_problem.atoms must be an array")
        atoms: list[ProblemAtom] = []
        for index, raw in enumerate(raw_atoms):
            if not isinstance(raw, Mapping):
                raise TypeError("decompose_problem atom must be an object")
            domains = _string_array(
                raw.get("initial_domain_ids", []),
                f"decompose_problem.atoms[{index}].initial_domain_ids",
            )
            scope = raw.get("scope", "")
            if not isinstance(scope, str):
                raise TypeError("decompose_problem atom.scope must be a string")
            atoms.append(
                ProblemAtom(
                    atom_id=_required_string(
                        raw.get("atom_id"), f"decompose_problem.atoms[{index}].atom_id"
                    ),
                    question=_required_string(
                        raw.get("question"),
                        f"decompose_problem.atoms[{index}].question",
                    ),
                    responsibility=Responsibility(
                        _required_string(
                            raw.get("responsibility"),
                            f"decompose_problem.atoms[{index}].responsibility",
                        )
                    ),
                    discriminator=_discriminator(
                        raw.get("discriminator"),
                        f"decompose_problem.atoms[{index}].discriminator",
                    ),
                    scope=scope,
                    initial_domain_ids=domains,
                    metadata=_metadata(
                        raw.get("metadata", {}),
                        f"decompose_problem.atoms[{index}].metadata",
                    ),
                )
            )
        rationale = data.get("rationale", "")
        if not isinstance(rationale, str):
            raise TypeError("decompose_problem.rationale must be a string")
        decomposition = ProblemDecomposition(
            parent_problem_id=problem.problem_id,
            atoms=tuple(atoms),
            stop_reason=_stop_reason(data.get("stop_reason")),
            rationale=rationale,
        )
        decomposition.verify(problem)
        return decomposition

    def decompose_residual(
        self,
        residual: Residual,
        problem: Problem,
        state: OrionState,
    ) -> ResidualDecomposition:
        automatic_fibres = _automatic_fibre_context(residual)
        injected_fibres = [dict(item) for item in self._development_fibre_context]
        data = self._call(
            "decompose_residual",
            {
                "problem": asdict(problem),
                "residual": {
                    "id": residual.residual_id,
                    "kind": residual.kind.value,
                    "description": residual.description,
                    "candidate_responsibilities": [
                        item.value for item in residual.candidate_responsibilities
                    ],
                    "metadata": residual.metadata_dict(),
                },
                "known_evidence_ids": list(state.knowledge.evidence_ids),
                "negative_history": [_jsonable(item) for item in state.knowledge.negative_history],
                "active_domains": list(state.search_universe.active_domain_ids),
                "representations": list(state.search_universe.representation_ids),
                "mechanical_questions": _mechanical_questions(problem, state),
                "development_fibre_context": automatic_fibres + injected_fibres,
                "instruction": _DECOMPOSITION_INSTRUCTION,
            },
            (
                '{"atoms":[{"atom_id":"...","question":"...",'
                '"responsibility":"METHOD","scope":"...","initial_domain_ids":[],'
                '"metadata":{},"discriminator":{"discriminator_id":"...",'
                '"kind":"DOMINANCE_PROOF","question":"...",'
                '"success_criterion":"...","expected_cost_units":1.0,'
                '"metadata":{}}}],"stop_reason":null,"rationale":"..."}'
            ),
        )
        raw_atoms = data.get("atoms", [])
        if not isinstance(raw_atoms, list):
            raise TypeError("decompose_residual.atoms must be an array")
        atoms: list[ResidualAtom] = []
        for index, raw in enumerate(raw_atoms):
            if not isinstance(raw, Mapping):
                raise TypeError("decompose_residual atom must be an object")
            domains = _string_array(
                raw.get("initial_domain_ids", []),
                f"decompose_residual.atoms[{index}].initial_domain_ids",
            )
            scope = raw.get("scope", "")
            if not isinstance(scope, str):
                raise TypeError("decompose_residual atom.scope must be a string")
            atoms.append(
                ResidualAtom(
                    atom_id=_required_string(
                        raw.get("atom_id"),
                        f"decompose_residual.atoms[{index}].atom_id",
                    ),
                    question=_required_string(
                        raw.get("question"),
                        f"decompose_residual.atoms[{index}].question",
                    ),
                    responsibility=Responsibility(
                        _required_string(
                            raw.get("responsibility"),
                            f"decompose_residual.atoms[{index}].responsibility",
                        )
                    ),
                    discriminator=_discriminator(
                        raw.get("discriminator"),
                        f"decompose_residual.atoms[{index}].discriminator",
                    ),
                    scope=scope,
                    initial_domain_ids=domains,
                    metadata=_metadata(
                        raw.get("metadata", {}),
                        f"decompose_residual.atoms[{index}].metadata",
                    ),
                )
            )
        rationale = data.get("rationale", "")
        if not isinstance(rationale, str):
            raise TypeError("decompose_residual.rationale must be a string")
        decomposition = ResidualDecomposition(
            parent_residual_id=residual.residual_id,
            atoms=tuple(atoms),
            stop_reason=_stop_reason(data.get("stop_reason")),
            rationale=rationale,
        )
        decomposition.verify(residual)
        return decomposition
