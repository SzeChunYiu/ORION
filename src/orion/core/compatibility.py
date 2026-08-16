"""Typed compatibility complex with cover-level gluing verdicts.

Implements the RECONSTRUCT.GLUE.v0 contract (see the merged answer records and
`candidate-answers/RECONSTRUCT.GLUE.v0.md`): a compatibility layer that stores
typed contexts with witnessed pairwise statuses, and a gluing decision that is
**not** derivable from pairwise checks — the incumbent's three-context parity
obstruction is this module's known-answer falsifier, and any change that makes
`glue` answer GLUED on it is refuted.

Boundaries, per the contract: verdicts are structural facts about the declared
constraint sets only — no scientific authority is minted, no sheaf axioms are
claimed, and a resource bound yields CANNOT_CHECK rather than a verdict.
Lattice vocabulary is deliberately absent at this layer (pairwise witnesses do
not define an order); the closure-layer construction remains future work.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product


class PairwiseStatus(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    NO_OVERLAP = "NO_OVERLAP"


class GlueStatus(str, Enum):
    GLUED = "GLUED"
    OBSTRUCTED = "OBSTRUCTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Context:
    """One local chart: a variable tuple and the assignments it allows."""

    context_id: str
    variables: tuple[str, ...]
    allowed: frozenset[tuple[object, ...]]

    def __post_init__(self) -> None:
        if not self.context_id.strip() or not self.variables:
            raise ValueError("context identity and variables are required")
        if len(set(self.variables)) != len(self.variables):
            raise ValueError("context variables must be unique")
        if not self.allowed:
            raise ValueError(
                "a context with no allowed assignments is an explicit contradiction,"
                " not an empty chart; model it as a residual instead"
            )
        if any(len(row) != len(self.variables) for row in self.allowed):
            raise ValueError("every allowed assignment must bind every context variable")

    def projection(self, variables: tuple[str, ...]) -> frozenset[tuple[object, ...]]:
        indices = tuple(self.variables.index(name) for name in variables)
        return frozenset(tuple(row[i] for i in indices) for row in self.allowed)


@dataclass(frozen=True)
class TypedCompatibilityComplex:
    contexts: tuple[Context, ...]

    def __post_init__(self) -> None:
        ids = [item.context_id for item in self.contexts]
        if len(set(ids)) != len(ids):
            raise ValueError("context ids must be unique")


@dataclass(frozen=True)
class GlueVerdict:
    status: GlueStatus
    section: tuple[tuple[str, object], ...] = ()
    obstruction_cover: tuple[str, ...] = ()
    note: str = ""


def pairwise_compatibility(a: Context, b: Context) -> PairwiseStatus:
    """Marginal consistency on shared variables — deliberately weak.

    Identity is by declared variable name only: distinct names are distinct
    variables, so vocabulary alone can never manufacture an obstruction here
    (alignment/identity resolution is an upstream ABSORB obligation, not a
    gluing question).
    """

    shared = tuple(name for name in a.variables if name in b.variables)
    if not shared:
        return PairwiseStatus.NO_OVERLAP
    if a.projection(shared) & b.projection(shared):
        return PairwiseStatus.COMPATIBLE
    return PairwiseStatus.INCOMPATIBLE


def _domains(complex_: TypedCompatibilityComplex) -> dict[str, tuple[object, ...]]:
    domains: dict[str, set[object]] = {}
    for context in complex_.contexts:
        for index, name in enumerate(context.variables):
            values = domains.setdefault(name, set())
            values.update(row[index] for row in context.allowed)
    return {name: tuple(sorted(values, key=repr)) for name, values in domains.items()}


def glue(
    complex_: TypedCompatibilityComplex, *, search_bound: int = 100_000
) -> GlueVerdict:
    """Cover-level gluing verdict over the whole complex.

    Exhaustive over the declared assignment space, which is what makes an
    OBSTRUCTED verdict a certificate rather than a search failure; when the
    space exceeds `search_bound`, the honest verdict is CANNOT_CHECK — a
    resource bound is never rounded up to an obstruction or a section.
    """

    if search_bound < 1:
        raise ValueError("search bound must be positive")
    if not complex_.contexts:
        return GlueVerdict(GlueStatus.GLUED, note="empty cover glues trivially")

    domains = _domains(complex_)
    names = tuple(sorted(domains))
    space = 1
    for name in names:
        space *= len(domains[name])
        if space > search_bound:
            return GlueVerdict(
                GlueStatus.CANNOT_CHECK,
                note=(
                    f"assignment space exceeds the declared search bound ({search_bound});"
                    " a resource bound licenses no verdict"
                ),
            )

    for values in product(*(domains[name] for name in names)):
        assignment = dict(zip(names, values))
        if all(
            tuple(assignment[name] for name in context.variables) in context.allowed
            for context in complex_.contexts
        ):
            return GlueVerdict(
                GlueStatus.GLUED,
                section=tuple(sorted(assignment.items())),
            )

    return GlueVerdict(
        GlueStatus.OBSTRUCTED,
        obstruction_cover=tuple(item.context_id for item in complex_.contexts),
        note=(
            "no global assignment satisfies every context; pairwise compatibility"
            " does not imply a global section"
        ),
    )


__all__ = [
    "Context",
    "GlueStatus",
    "GlueVerdict",
    "PairwiseStatus",
    "TypedCompatibilityComplex",
    "glue",
    "pairwise_compatibility",
]
