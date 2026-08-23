#!/usr/bin/env python3
"""General core for the cross-paper preservation theory.

P6, P7 and P8 each proved the same five laws over a different subject matter --
certificate lifting, navigation closure, authority discharge -- with three
independently written finite enumerations. This module is the shared object
those three are instances of: a scientific standing decision over a set of
typed coordinates, decided by systems that retain only some of them.

Nothing here is subject-specific. A model is a coordinate vocabulary plus the
subset of coordinates a contract requires; a system is the subset it retains;
a donor is what it observes plus the native question it actually answers.

Standard library only. Every law in ``check_preservation_dichotomy_v2.py`` is
discharged by exhaustive enumeration over a finite universe, which is proof
support for the registered model and not an empirical claim about deployed
systems.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Iterator

GRANT = "GRANT"
DENY = "DENY"
CANNOT_CHECK = "CANNOT_CHECK"

# The five preservation levels of CROSS_PAPER_PRESERVATION_THEORY_V1, section 2.
LADDER = ("L0_identity", "L1_support", "L2_semantic", "L3_obligation", "L4_authority")

State = tuple[bool, ...]


@dataclass(frozen=True)
class Model:
    """A finite standing problem.

    ``coordinates`` is the vocabulary; ``required`` names those a contract makes
    load-bearing. Standing is granted exactly when every required coordinate is
    preserved. The content of the theory is not this definition -- it is what
    happens to systems that cannot see all of ``required``.
    """

    coordinates: tuple[str, ...]
    required: frozenset[str]

    def __post_init__(self) -> None:
        if not self.required <= set(self.coordinates):
            raise ValueError("required coordinates must be part of the vocabulary")

    def universe(self) -> Iterator[State]:
        return itertools.product((False, True), repeat=len(self.coordinates))

    def index(self, name: str) -> int:
        return self.coordinates.index(name)

    def standing(self, state: State) -> str:
        return GRANT if all(state[self.index(c)] for c in self.required) else DENY

    def project(self, state: State, retained: frozenset[str]) -> tuple:
        return tuple(state[self.index(c)] for c in sorted(retained))


def canonical_rule(model: Model, retained: frozenset[str]) -> Callable[[State], str]:
    """The sound, maximally decisive decision rule for a system retaining ``retained``.

    A system sees only its projection, so it sees a whole fibre of states at
    once. If every state in the fibre has the same standing, that value is
    forced and the system may return it. If they disagree, no sound rule can
    pick one: the honest terminal is CANNOT_CHECK, never a default DENY. This is
    the rule against which every other rule is measured -- anything more
    decisive is unsound, so an impossibility proved here holds for all rules.
    """

    fibres: dict[tuple, set[str]] = {}
    for state in model.universe():
        fibres.setdefault(model.project(state, retained), set()).add(model.standing(state))

    def decide(state: State) -> str:
        values = fibres[model.project(state, retained)]
        return next(iter(values)) if len(values) == 1 else CANNOT_CHECK

    return decide


def separates(model: Model, retained: frozenset[str]) -> bool:
    """True when the retained coordinates distinguish every standing-distinct pair."""
    seen: dict[tuple, str] = {}
    for state in model.universe():
        key = model.project(state, retained)
        value = model.standing(state)
        if seen.setdefault(key, value) != value:
            return False
    return True


def is_decisive(model: Model, retained: frozenset[str]) -> bool:
    decide = canonical_rule(model, retained)
    return all(decide(state) != CANNOT_CHECK for state in model.universe())


@dataclass(frozen=True)
class Donor:
    """A mature parent mechanism, absorbed rather than replaced.

    ``observes`` is what its interface can see. ``native`` is the question it
    actually answers -- its own local verdict, which it is not free to redefine
    into whatever the target contract happens to need. The gap between those two
    is where verdict composition loses information that coordinate composition
    keeps.
    """

    name: str
    observes: frozenset[str]
    native: Callable[[Model, State], bool]

    def verdict(self, model: Model, state: State) -> bool:
        return self.native(model, state)


def coordinate_exposing(name: str, observes: frozenset[str]) -> tuple[Donor, ...]:
    """An *ideal* donor stack: one donor per observed coordinate, reporting it directly.

    This is the ideal product that P6.V4.5, P7.V3.6 and P8.V3.10 each showed ties
    the centralized system extensionally. Modelling it explicitly is what lets
    the tie be stated as a theorem about donor interfaces rather than as a
    concession about architecture.
    """

    def reporter(coordinate: str) -> Callable[[Model, State], bool]:
        return lambda model, state: state[model.index(coordinate)]

    return tuple(
        Donor(f"{name}:{c}", frozenset({c}), reporter(c)) for c in sorted(observes)
    )


def sound_decisive_join_exists(model: Model, donors: tuple[Donor, ...]) -> bool:
    """Whether ANY join over the donors' native verdicts decides standing.

    Enumerates every function from verdict tuples to standing values, so a
    negative result is an impossibility over all composition rules rather than
    the failure of one chosen rule. That distinction is the whole point: a
    product that cannot be rescued by a cleverer join is a structural limit.
    """

    fibres: dict[tuple[bool, ...], set[str]] = {}
    for state in model.universe():
        key = tuple(d.verdict(model, state) for d in donors)
        fibres.setdefault(key, set()).add(model.standing(state))
    # A join is a free choice per verdict tuple, so one exists iff no tuple is
    # forced to two different standings at once.
    return all(len(values) == 1 for values in fibres.values())
