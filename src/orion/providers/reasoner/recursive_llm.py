from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict

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
from orion.core.residuals import Residual, Responsibility
from orion.core.state import OrionState
from orion.providers.reasoner.llm import LLMResearchReasoner


_DECOMPOSITION_INSTRUCTION = (
    "Treat the target as a research problem. Return a decision-separating recursive "
    "decomposition, not a paraphrase. Each atom must be strictly narrower and must "
    "have exactly one concrete discriminator. Prefer a cheaper valid dominance, "
    "formal, exact-computation or donor-subsumption test over an expensive experiment "
    "when it can settle the same atom. Preserve interaction-only possibilities. If "
    "no finer identifiable split exists, return no atoms and an explicit stop_reason. "
    "Never grant scientific, novelty, adoption, promotion, merge or global-stop authority."
)


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


class RecursiveLLMResearchReasoner(LLMResearchReasoner):
    """Canonical reasoner plus non-authorizing problem/residual decomposition."""

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
                "known_negative_history_ids": list(state.knowledge.negative_history_ids),
                "active_domains": list(state.search_universe.active_domain_ids),
                "representations": list(state.search_universe.representation_ids),
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
