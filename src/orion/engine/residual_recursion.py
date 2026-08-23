from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.core.problem import Problem
from orion.core.problem_tree import (
    DiscriminatorKind,
    DiscriminatorSpec,
    ProblemAtom,
    ProblemDecomposition,
    ProblemRecursionPlan,
    RecursiveProblemStopReason,
    ResidualAtom,
    ResidualDecomposition,
    ResidualRecursionPlan,
)
from orion.core.residuals import Residual, Responsibility
from orion.core.state import OrionState


_KIND_PRIORITY = {
    DiscriminatorKind.DOMINANCE_PROOF: 0,
    DiscriminatorKind.FORMAL_PROOF: 1,
    DiscriminatorKind.EXACT_COMPUTATION: 2,
    DiscriminatorKind.DONOR_SEARCH: 3,
    DiscriminatorKind.HOSTILE_TEST: 4,
    DiscriminatorKind.RETRIEVAL: 5,
    DiscriminatorKind.MEASUREMENT: 6,
    DiscriminatorKind.INTERACTION_TEST: 7,
    DiscriminatorKind.EXPERIMENT: 8,
    DiscriminatorKind.CANNOT_CHECK: 99,
}


@dataclass(frozen=True)
class ResidualRecursionPolicy:
    max_depth: int = 5
    max_children_per_residual: int = 12
    max_children_per_problem: int = 12

    def __post_init__(self) -> None:
        for name, value in (
            ("max_depth", self.max_depth),
            ("max_children_per_residual", self.max_children_per_residual),
            ("max_children_per_problem", self.max_children_per_problem),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be positive")


def _order_atoms(atoms):
    return tuple(
        sorted(
            atoms,
            key=lambda atom: (
                float(atom.discriminator.expected_cost_units),
                _KIND_PRIORITY[atom.discriminator.kind],
                atom.atom_id,
            ),
        )
    )


class ProblemRecursionPlanner:
    """Bounded problem-frame decomposition before expensive root solving."""

    def __init__(
        self,
        reasoner: Any,
        *,
        policy: ResidualRecursionPolicy | None = None,
    ) -> None:
        self._reasoner = reasoner
        self._policy = policy or ResidualRecursionPolicy()

    @property
    def policy(self) -> ResidualRecursionPolicy:
        return self._policy

    def decompose(
        self,
        *,
        problem: Problem,
        state: OrionState,
        recursion_depth: int,
    ) -> ProblemDecomposition:
        if recursion_depth >= self._policy.max_depth:
            return ProblemDecomposition(
                parent_problem_id=problem.problem_id,
                stop_reason=RecursiveProblemStopReason.CANNOT_CHECK_RESOURCE_BOUND,
                rationale="recursive depth bound reached before finer problem decomposition",
            )
        method = getattr(self._reasoner, "decompose_problem", None)
        if method is None:
            decomposition = ProblemDecomposition(
                parent_problem_id=problem.problem_id,
                stop_reason=RecursiveProblemStopReason.NO_DECISION_SEPARATING_DECOMPOSITION,
                rationale="reasoner exposes no problem-decomposition method",
            )
        else:
            decomposition = method(problem, state)
        if not isinstance(decomposition, ProblemDecomposition):
            raise TypeError("reasoner.decompose_problem must return ProblemDecomposition")
        decomposition.verify(problem)
        if len(decomposition.atoms) > self._policy.max_children_per_problem:
            raise ValueError(
                "problem decomposition exceeds max_children_per_problem; fail closed "
                "instead of silently truncating atoms"
            )
        return decomposition

    @staticmethod
    def order_atoms(atoms: tuple[ProblemAtom, ...]) -> tuple[ProblemAtom, ...]:
        return _order_atoms(atoms)

    def plan(
        self,
        *,
        problem: Problem,
        state: OrionState,
        recursion_depth: int,
    ) -> ProblemRecursionPlan:
        decomposition = self.decompose(
            problem=problem,
            state=state,
            recursion_depth=recursion_depth,
        )
        ordered = self.order_atoms(decomposition.atoms)
        return ProblemRecursionPlan(
            parent_problem_id=problem.problem_id,
            recursion_depth=recursion_depth,
            decomposition=decomposition,
            ordered_atom_ids=tuple(atom.atom_id for atom in ordered),
        )


class ResidualRecursionPlanner:
    """Turn a material residual into bounded child problems.

    Semantic decomposition may be proposed by the configured recursive reasoner,
    but this planner enforces bounded branching/depth, non-authority and
    deterministic cheapest-first ordering. A dominance/formal obstruction is
    therefore an automatic shortcut whenever it can settle the same atom.
    """

    def __init__(
        self,
        reasoner: Any,
        *,
        policy: ResidualRecursionPolicy | None = None,
    ) -> None:
        self._reasoner = reasoner
        self._policy = policy or ResidualRecursionPolicy()

    @property
    def policy(self) -> ResidualRecursionPolicy:
        return self._policy

    @staticmethod
    def _fallback_kind(responsibility: Responsibility) -> DiscriminatorKind:
        if responsibility in {
            Responsibility.SEARCH,
            Responsibility.ROUTING,
            Responsibility.EVIDENCE,
        }:
            return DiscriminatorKind.RETRIEVAL
        if responsibility in {
            Responsibility.MEASUREMENT,
            Responsibility.EVALUATOR,
            Responsibility.INTERFACE,
        }:
            return DiscriminatorKind.MEASUREMENT
        if responsibility is Responsibility.EXECUTION:
            return DiscriminatorKind.HOSTILE_TEST
        return DiscriminatorKind.EXACT_COMPUTATION

    @classmethod
    def _fallback_decomposition(cls, residual: Residual) -> ResidualDecomposition:
        responsibilities = tuple(dict.fromkeys(residual.candidate_responsibilities))
        if len(responsibilities) <= 1:
            return ResidualDecomposition(
                parent_residual_id=residual.residual_id,
                stop_reason=RecursiveProblemStopReason.IRREDUCIBLE_AT_CURRENT_RESOLUTION,
                rationale=(
                    "reasoner exposes no residual-decomposition method and the residual "
                    "does not carry multiple candidate responsibilities"
                ),
            )
        atoms = tuple(
            ResidualAtom(
                atom_id=f"responsibility:{responsibility.value.lower()}",
                question=(
                    f"Can responsibility {responsibility.value} independently explain or "
                    f"falsify residual {residual.residual_id}: {residual.description}"
                ),
                responsibility=responsibility,
                discriminator=DiscriminatorSpec(
                    discriminator_id=(
                        f"discriminator:{residual.residual_id}:{responsibility.value.lower()}"
                    ),
                    kind=cls._fallback_kind(responsibility),
                    question=(
                        f"Acquire a decision-separating observation for responsibility "
                        f"{responsibility.value}."
                    ),
                    success_criterion=(
                        "Separate this responsibility from the other surviving parent "
                        "responsibilities without changing the parent acceptance criteria."
                    ),
                    expected_cost_units=1.0,
                ),
            )
            for responsibility in responsibilities
        )
        return ResidualDecomposition(
            parent_residual_id=residual.residual_id,
            atoms=atoms,
            rationale="deterministic responsibility-level fallback decomposition",
        )

    def decompose(
        self,
        *,
        residual: Residual,
        problem: Problem,
        state: OrionState,
        recursion_depth: int,
    ) -> ResidualDecomposition:
        if not residual.material:
            return ResidualDecomposition(
                parent_residual_id=residual.residual_id,
                stop_reason=RecursiveProblemStopReason.IRREDUCIBLE_AT_CURRENT_RESOLUTION,
                rationale="non-material residual is not recursively scheduled",
            )
        if recursion_depth >= self._policy.max_depth:
            return ResidualDecomposition(
                parent_residual_id=residual.residual_id,
                stop_reason=RecursiveProblemStopReason.CANNOT_CHECK_RESOURCE_BOUND,
                rationale="recursive depth bound reached with a material residual still open",
            )
        method = getattr(self._reasoner, "decompose_residual", None)
        if method is None:
            decomposition = self._fallback_decomposition(residual)
        else:
            decomposition = method(residual, problem, state)
        if not isinstance(decomposition, ResidualDecomposition):
            raise TypeError("reasoner.decompose_residual must return ResidualDecomposition")
        decomposition.verify(residual)
        if len(decomposition.atoms) > self._policy.max_children_per_residual:
            raise ValueError(
                "residual decomposition exceeds max_children_per_residual; fail closed "
                "instead of silently truncating atoms"
            )
        return decomposition

    @staticmethod
    def order_atoms(atoms: tuple[ResidualAtom, ...]) -> tuple[ResidualAtom, ...]:
        return _order_atoms(atoms)

    def plan(
        self,
        *,
        residual: Residual,
        problem: Problem,
        state: OrionState,
        recursion_depth: int,
    ) -> ResidualRecursionPlan:
        decomposition = self.decompose(
            residual=residual,
            problem=problem,
            state=state,
            recursion_depth=recursion_depth,
        )
        ordered = self.order_atoms(decomposition.atoms)
        return ResidualRecursionPlan(
            parent_problem_id=problem.problem_id,
            residual_id=residual.residual_id,
            recursion_depth=recursion_depth,
            decomposition=decomposition,
            ordered_atom_ids=tuple(atom.atom_id for atom in ordered),
        )

    def child_problems(
        self,
        *,
        residual: Residual,
        problem: Problem,
        state: OrionState,
        recursion_depth: int,
    ) -> tuple[Problem, ...]:
        decomposition = self.decompose(
            residual=residual,
            problem=problem,
            state=state,
            recursion_depth=recursion_depth,
        )
        ordered = self.order_atoms(decomposition.atoms)
        return tuple(
            atom.as_problem(parent_problem=problem, parent_residual=residual)
            for atom in ordered
        )
