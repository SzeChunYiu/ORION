from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    """A scoped problem presented to ORION.

    Residual children are ordinary problems with explicit parent lineage.  The
    lineage is descriptive/governance state only; it grants no scientific or
    closure authority.
    """

    problem_id: str
    question: str
    scope: str = ""
    initial_domain_ids: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    parent_problem_id: str | None = None
    parent_residual_id: str | None = None
    recursion_depth: int = 0

    def __post_init__(self) -> None:
        if not self.problem_id.strip():
            raise ValueError("problem_id is required")
        if not self.question.strip():
            raise ValueError("question is required")
        if isinstance(self.recursion_depth, bool) or not isinstance(
            self.recursion_depth, int
        ):
            raise TypeError("recursion_depth must be an integer")
        if self.recursion_depth < 0:
            raise ValueError("recursion_depth must be non-negative")
        has_parent_problem = self.parent_problem_id is not None
        has_parent_residual = self.parent_residual_id is not None
        if has_parent_problem != has_parent_residual:
            raise ValueError(
                "recursive problem lineage requires both parent_problem_id and parent_residual_id"
            )
        if self.recursion_depth == 0 and has_parent_problem:
            raise ValueError("root problems cannot declare parent lineage")
        if self.recursion_depth > 0 and not has_parent_problem:
            raise ValueError("child problems require parent lineage")
        if self.parent_problem_id is not None and not self.parent_problem_id.strip():
            raise ValueError("parent_problem_id must be non-empty when provided")
        if self.parent_residual_id is not None and not self.parent_residual_id.strip():
            raise ValueError("parent_residual_id must be non-empty when provided")
