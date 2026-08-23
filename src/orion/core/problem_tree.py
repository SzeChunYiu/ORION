from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.problem import Problem
from orion.core.residuals import Residual, Responsibility


class DiscriminatorKind(str, Enum):
    """Bounded ways an atomic child problem may be separated or falsified."""

    DOMINANCE_PROOF = "DOMINANCE_PROOF"
    EXACT_COMPUTATION = "EXACT_COMPUTATION"
    DONOR_SEARCH = "DONOR_SEARCH"
    HOSTILE_TEST = "HOSTILE_TEST"
    RETRIEVAL = "RETRIEVAL"
    MEASUREMENT = "MEASUREMENT"
    EXPERIMENT = "EXPERIMENT"
    INTERACTION_TEST = "INTERACTION_TEST"
    FORMAL_PROOF = "FORMAL_PROOF"
    CANNOT_CHECK = "CANNOT_CHECK"


class RecursiveProblemStopReason(str, Enum):
    """Fail-closed reasons not to decompose one problem/residual further."""

    IRREDUCIBLE_AT_CURRENT_RESOLUTION = "IRREDUCIBLE_AT_CURRENT_RESOLUTION"
    DONOR_OR_EXISTING_FORMALISM_SUBSUMES = "DONOR_OR_EXISTING_FORMALISM_SUBSUMES"
    NO_DECISION_SEPARATING_DECOMPOSITION = "NO_DECISION_SEPARATING_DECOMPOSITION"
    NONUNIQUE_OBSERVATIONALLY_EQUIVALENT_DECOMPOSITION = (
        "NONUNIQUE_OBSERVATIONALLY_EQUIVALENT_DECOMPOSITION"
    )
    INTERACTION_TERM_ONLY = "INTERACTION_TERM_ONLY"
    NO_PROTECTED_DISCRIMINATOR = "NO_PROTECTED_DISCRIMINATOR"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"


@dataclass(frozen=True)
class DiscriminatorSpec:
    """One bounded observation/computation capable of separating an atom."""

    discriminator_id: str
    kind: DiscriminatorKind
    question: str
    success_criterion: str
    expected_cost_units: float
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.discriminator_id.strip():
            raise ValueError("discriminator_id is required")
        if not self.question.strip():
            raise ValueError("discriminator question is required")
        if not self.success_criterion.strip():
            raise ValueError("discriminator success_criterion is required")
        if isinstance(self.expected_cost_units, bool) or not isinstance(
            self.expected_cost_units, (int, float)
        ):
            raise TypeError("expected_cost_units must be numeric")
        if self.expected_cost_units < 0:
            raise ValueError("expected_cost_units must be non-negative")
        keys = [key for key, _ in self.metadata]
        if len(keys) != len(set(keys)):
            raise ValueError("discriminator metadata keys must be unique")
        if any(not key.strip() for key, _ in self.metadata):
            raise ValueError("discriminator metadata keys must be non-empty")

    def metadata_dict(self) -> dict[str, str]:
        return dict(self.metadata)


@dataclass(frozen=True)
class ProblemAtom:
    """One decision-separating child of a broader problem frame."""

    atom_id: str
    question: str
    responsibility: Responsibility
    discriminator: DiscriminatorSpec
    scope: str = ""
    initial_domain_ids: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _verify_atom_fields(
            atom_id=self.atom_id,
            question=self.question,
            initial_domain_ids=self.initial_domain_ids,
            metadata=self.metadata,
        )

    def as_problem(self, *, parent_problem: Problem) -> Problem:
        return Problem(
            problem_id=f"{parent_problem.problem_id}::problem-atom::{self.atom_id}",
            question=self.question,
            scope=self.scope or parent_problem.scope,
            initial_domain_ids=(
                self.initial_domain_ids
                if self.initial_domain_ids
                else parent_problem.initial_domain_ids
            ),
            success_criteria=(self.discriminator.success_criterion,),
        )


@dataclass(frozen=True)
class ResidualAtom:
    """A decision-separating child of a material residual.

    An atom is not a scientific conclusion. It is a child problem with one declared
    discriminator. The discriminator may prove an obstruction, find missing
    evidence, or expose a deeper residual that must itself be recursively split.
    """

    atom_id: str
    question: str
    responsibility: Responsibility
    discriminator: DiscriminatorSpec
    scope: str = ""
    initial_domain_ids: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _verify_atom_fields(
            atom_id=self.atom_id,
            question=self.question,
            initial_domain_ids=self.initial_domain_ids,
            metadata=self.metadata,
        )

    def metadata_dict(self) -> dict[str, str]:
        return dict(self.metadata)

    def as_problem(
        self,
        *,
        parent_problem: Problem,
        parent_residual: Residual,
    ) -> Problem:
        return Problem(
            problem_id=(
                f"{parent_problem.problem_id}::residual::{parent_residual.residual_id}"
                f"::atom::{self.atom_id}"
            ),
            question=self.question,
            scope=self.scope or parent_problem.scope,
            initial_domain_ids=(
                self.initial_domain_ids
                if self.initial_domain_ids
                else parent_problem.initial_domain_ids
            ),
            success_criteria=(self.discriminator.success_criterion,),
        )


def _verify_atom_fields(
    *,
    atom_id: str,
    question: str,
    initial_domain_ids: tuple[str, ...],
    metadata: tuple[tuple[str, str], ...],
) -> None:
    if not atom_id.strip():
        raise ValueError("atom_id is required")
    if not question.strip():
        raise ValueError("atom question is required")
    keys = [key for key, _ in metadata]
    if len(keys) != len(set(keys)):
        raise ValueError("atom metadata keys must be unique")
    if any(not key.strip() for key, _ in metadata):
        raise ValueError("atom metadata keys must be non-empty")
    if any(not item.strip() for item in initial_domain_ids):
        raise ValueError("atom initial_domain_ids must be non-empty strings")


@dataclass(frozen=True)
class ProblemDecomposition:
    """Validated decomposition of a broad problem before expensive solving."""

    parent_problem_id: str
    atoms: tuple[ProblemAtom, ...] = ()
    stop_reason: RecursiveProblemStopReason | None = None
    rationale: str = ""
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_promotion_authority: bool = False

    def verify(self, problem: Problem) -> None:
        if self.parent_problem_id != problem.problem_id:
            raise ValueError("problem decomposition is not bound to parent problem")
        _verify_decomposition_authority_and_shape(
            atoms=self.atoms,
            stop_reason=self.stop_reason,
            authority_flags=(
                self.grants_scientific_authority,
                self.grants_novelty_authority,
                self.grants_promotion_authority,
            ),
            label="problem",
        )
        _verify_unique_atoms(self.atoms)
        if self.atoms:
            parent_text = " ".join(problem.question.lower().split())
            for atom in self.atoms:
                if " ".join(atom.question.lower().split()) == parent_text:
                    raise ValueError("problem atom question must be narrower than parent")


@dataclass(frozen=True)
class ResidualDecomposition:
    """Validated recursive decomposition of one residual.

    Exactly one of ``atoms`` or ``stop_reason`` is present. Decomposition itself
    never grants scientific, novelty, adoption, merge, promotion, or stop authority.
    """

    parent_residual_id: str
    atoms: tuple[ResidualAtom, ...] = ()
    stop_reason: RecursiveProblemStopReason | None = None
    rationale: str = ""
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_promotion_authority: bool = False

    def verify(self, residual: Residual) -> None:
        if self.parent_residual_id != residual.residual_id:
            raise ValueError("decomposition is not bound to the parent residual")
        _verify_decomposition_authority_and_shape(
            atoms=self.atoms,
            stop_reason=self.stop_reason,
            authority_flags=(
                self.grants_scientific_authority,
                self.grants_novelty_authority,
                self.grants_promotion_authority,
            ),
            label="residual",
        )
        _verify_unique_atoms(self.atoms)
        if self.atoms:
            parent_text = " ".join(residual.description.lower().split())
            for atom in self.atoms:
                child_text = " ".join(atom.question.lower().split())
                if child_text == parent_text:
                    raise ValueError("atom question must be narrower than parent residual")


def _verify_decomposition_authority_and_shape(
    *,
    atoms: tuple[object, ...],
    stop_reason: RecursiveProblemStopReason | None,
    authority_flags: tuple[bool, bool, bool],
    label: str,
) -> None:
    if any(authority_flags):
        raise ValueError(f"{label} decomposition cannot grant authority")
    if bool(atoms) == (stop_reason is not None):
        raise ValueError(
            f"{label} decomposition requires exactly one of atoms or stop_reason"
        )


def _verify_unique_atoms(atoms: tuple[ProblemAtom | ResidualAtom, ...]) -> None:
    atom_ids = [atom.atom_id for atom in atoms]
    if len(atom_ids) != len(set(atom_ids)):
        raise ValueError("decomposition atom ids must be unique")
    discriminator_ids = [atom.discriminator.discriminator_id for atom in atoms]
    if len(discriminator_ids) != len(set(discriminator_ids)):
        raise ValueError("decomposition discriminator ids must be unique")


@dataclass(frozen=True)
class ProblemRecursionPlan:
    parent_problem_id: str
    recursion_depth: int
    decomposition: ProblemDecomposition
    ordered_atom_ids: tuple[str, ...]

    @property
    def terminal(self) -> bool:
        return not self.ordered_atom_ids


@dataclass(frozen=True)
class ResidualRecursionPlan:
    parent_problem_id: str
    residual_id: str
    recursion_depth: int
    decomposition: ResidualDecomposition
    ordered_atom_ids: tuple[str, ...]

    @property
    def terminal(self) -> bool:
        return not self.ordered_atom_ids
