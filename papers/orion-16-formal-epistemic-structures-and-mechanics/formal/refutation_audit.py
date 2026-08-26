#!/usr/bin/env python3
"""Measure what P6's two shipped graph checkers can reject, not how much they enumerate.

`check_finite_models.py::check_reopening` and
`check_theory_closure_v2_1.py::check_root_inclusive_safety` are the two places
where P6's formal core asserts something about a *reopening operator*. Until
2026-08-22 neither of them did. Their assertions were

    assert not retained.intersection(downstream)            # (A \\ B) & B == {}
    assert retained == certified.difference(downstream)     # x == x
    assert certified & changed <= got                       # A <= A | B
    assert certified & descendants(edges, changed) <= got   # B <= A | B

with `retained = certified.difference(downstream)` and `got` the union of the
two left-hand sides. Every one is the defining property of the operator that
built the right-hand side, so all four held for any graph operator whatsoever.
Replacing `descendants` with the empty set, with every node, with the changed
set, or with the direct successors left `(543, 130320)` and `(960, 2048)`
untouched. A case count cannot distinguish "enumerated a space and rejected
every wrong operator" from "enumerated a space and restated set algebra", which
is the failure class recorded under
`research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/` and,
for this specific check, under
`research/failures/2026-08-tautological-assertion-in-finite-check/`.

This module is the measurement, in the shape
`src/orion/study/p6/` uses for the claim-expansion lane: each shipped assertion
is transcribed as a predicate over a *supplied* reopening operator, a register
of declared false operators is written down, and
`orion.programme.refutation_capacity.measure_refutation_capacity` reports which
of them each assertion rejects. A check that rejects none of them is reported as
`CANNOT_CHECK`, which blocks exactly as `FAIL` does, and the audit exits 3.

The two registers are separate on purpose, because the two checks are about
different operators. FORMAL_CORE_V1's Definition 8 reopens `Desc_D(X)`, the
strict downstream closure; FORMAL_CORE_V2.1's Theorem 1 reopens
`Aff_D(E,X) = (X & Q_cert) | (Desc_D(X) & Q_cert)`, adding the changed certified
roots. Merging the registers would ask each check to reject operators its own
theorem does not talk about.

Run from the repository root::

    PYTHONPATH=src python \\
      papers/orion-16-formal-epistemic-structures-and-mechanics/formal/refutation_audit.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

from orion.programme.guard_exercise import worst_outcome
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    Rule,
    assess_theory_coverage,
    axis_sensitivity,
    UnrefutableCheck,
    measure_refutation_capacity,
    require_refutable,
)

FORMAL_DIR = Path(__file__).resolve().parent


def _load(module_name: str, filename: str):
    """Import a shipped checker by path.

    The checkers live under a directory whose name is not an identifier, so they
    cannot be imported normally, and they are deliberately left as standard-
    library scripts that run with no `PYTHONPATH`. Loading them by path here
    keeps that property: the audit depends on the checkers, never the reverse.
    """

    spec = importlib.util.spec_from_file_location(module_name, FORMAL_DIR / filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


finite_models = _load("p6_check_finite_models", "check_finite_models.py")
theory_closure = _load("p6_check_theory_closure_v2_1", "check_theory_closure_v2_1.py")


# --------------------------------------------------------------------------
# V1 selective reopening: `check_finite_models.check_reopening`
# --------------------------------------------------------------------------

#: The node count the shipped check runs at. Four is the smallest that carries a
#: three-edge chain, which is what separates a transitive operator from one
#: truncated at distance two.
NODE_COUNT = 4

REOPENING_REFERENCE_ID = "check_finite_models.retained_by_descendants"

#: Axis profiling runs on this smaller grid rather than on the 130,320-point
#: space. `axis_sensitivity` compares every sibling pair inside each group, which
#: is quadratic in the axis it holds; at n=4 the `certified` axis alone is
#: 977,400 comparisons. Three nodes still carries a two-edge chain, so the answer
#: it gives about each axis is the same answer, arrived at affordably.
AXIS_NODE_COUNT = 3


def _dags(node_count: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    possible = [
        (source, target)
        for source in range(node_count)
        for target in range(node_count)
        if source != target
    ]
    found = []
    for mask in range(1 << len(possible)):
        edges = tuple(possible[index] for index in range(len(possible)) if (mask >> index) & 1)
        if finite_models.is_dag(node_count, edges):
            found.append(edges)
    return tuple(found)


def reopening_model_space(node_count: int = NODE_COUNT) -> tuple[ModelPoint, ...]:
    """The shipped check's enumerated space, one point per asserted case."""

    nodes = range(node_count)
    return tuple(
        {
            "node_count": node_count,
            "edges": edges,
            "changed": frozenset(int(value) for value in changed_raw),
            "certified": frozenset(int(value) for value in certified_raw),
        }
        for edges in _dags(node_count)
        for changed_raw in finite_models.powerset(nodes)
        if changed_raw
        for certified_raw in finite_models.powerset(nodes)
    )


@lru_cache(maxsize=None)
def _closure(node_count: int, edges: tuple[tuple[int, int], ...]):
    return finite_models.transitive_closure(node_count, edges)


@lru_cache(maxsize=None)
def _specified(
    node_count: int, edges: tuple[tuple[int, int], ...], changed: frozenset[int]
) -> tuple[frozenset[int], frozenset[int]]:
    """`(Desc_D(X), Desc_D(X) \\ X)`, from the closure and never from `descendants`."""

    specified = finite_models.specified_downstream(_closure(node_count, edges), changed)
    return specified, specified.difference(changed)


def _point(point: ModelPoint) -> tuple[int, tuple[tuple[int, int], ...], frozenset, frozenset]:
    return (
        int(point["node_count"]),  # type: ignore[arg-type]
        point["edges"],  # type: ignore[return-value]
        point["changed"],  # type: ignore[return-value]
        point["certified"],  # type: ignore[return-value]
    )


def reference_retained(point: ModelPoint) -> frozenset[int]:
    """The shipped operator: `certified - descendants(node_count, edges, changed)`."""

    node_count, edges, changed, certified = _point(point)
    return certified.difference(finite_models.descendants(node_count, edges, changed))


def _accepts_reopening_sufficiency(rule: Rule) -> bool:
    """`assert not retained.intersection(must_reopen)` over the whole space."""

    for point in REOPENING_SPACE:
        node_count, edges, changed, _ = _point(point)
        _, must_reopen = _specified(node_count, edges, changed)
        if rule(point) & must_reopen:
            return False
    return True


def _accepts_reopening_minimality(rule: Rule) -> bool:
    """`assert certified.difference(specified).issubset(retained)` over the whole space."""

    for point in REOPENING_SPACE:
        node_count, edges, changed, certified = _point(point)
        specified, _ = _specified(node_count, edges, changed)
        if not certified.difference(specified) <= rule(point):
            return False
    return True


def _accepts_reopening_exactness(rule: Rule) -> bool:
    """`assert retained == certified.difference(must_reopen)` over the whole space."""

    for point in REOPENING_SPACE:
        node_count, edges, changed, certified = _point(point)
        _, must_reopen = _specified(node_count, edges, changed)
        if rule(point) != certified.difference(must_reopen):
            return False
    return True


REOPENING_CHECKS: tuple[MechanizedCheck, ...] = (
    MechanizedCheck(
        check_id="reopening.sufficiency",
        asserts=(
            "no certified node in the strict downstream closure of the change survives "
            "(FORMAL_CORE_V1 Theorem 1)"
        ),
        accepts=_accepts_reopening_sufficiency,
    ),
    MechanizedCheck(
        check_id="reopening.minimality",
        asserts=(
            "no certified node outside the strict downstream closure is reopened "
            "(FORMAL_CORE_V1 Corollary 2.1)"
        ),
        accepts=_accepts_reopening_minimality,
    ),
    MechanizedCheck(
        check_id="reopening.exactness",
        asserts=(
            "the retained set is exactly the certified nodes minus Desc_D(X) \\ X, which "
            "is the operator V1's Definition 8 describes"
        ),
        accepts=_accepts_reopening_exactness,
    ),
)


def _reachable(point: ModelPoint, *, reverse: bool = False, undirected: bool = False) -> frozenset:
    node_count, edges, changed, _ = _point(point)
    if reverse:
        edges = tuple((target, source) for source, target in edges)
    if undirected:
        edges = edges + tuple((target, source) for source, target in edges)
    return finite_models.specified_downstream(_closure(node_count, edges), changed)


def _bounded_reachable(point: ModelPoint, depth: int) -> frozenset:
    node_count, edges, changed, _ = _point(point)
    frontier = set(changed)
    seen: set[int] = set()
    for _ in range(depth):
        frontier = {target for source, target in edges if source in frontier}
        seen |= frontier
    return frozenset(seen)


FALSE_REOPENING_THEORIES: tuple[FalseTheory, ...] = (
    FalseTheory(
        theory_id="retain_everything",
        breaks=(
            "Theorem 1: a change would invalidate nothing, so a certified claim whose "
            "support just changed keeps its certification"
        ),
        rule=lambda point: point["certified"],
    ),
    FalseTheory(
        theory_id="retain_nothing",
        breaks=(
            "Corollary 2.1: full reset, which is sound and is exactly the operator the "
            "corollary calls non-minimal whenever independent certified state exists"
        ),
        rule=lambda point: frozenset(),
    ),
    FalseTheory(
        theory_id="direct_successors_only",
        breaks=(
            "Theorem 1 for chains: reopening stops at the immediate children, so a "
            "certified claim two edges downstream of the change survives"
        ),
        rule=lambda point: point["certified"]
        - (_bounded_reachable(point, 1) - point["changed"]),
    ),
    FalseTheory(
        theory_id="depth_capped_at_two",
        breaks=(
            "Theorem 1 at distance three: transitivity is truncated, which no chain "
            "shorter than a->b->c->d can expose"
        ),
        rule=lambda point: point["certified"]
        - (_bounded_reachable(point, 2) - point["changed"]),
    ),
    FalseTheory(
        theory_id="ancestors_reopened",
        breaks=(
            "the direction of dependency: it reopens what the change depends on instead "
            "of what depends on the change"
        ),
        rule=lambda point: point["certified"]
        - (_reachable(point, reverse=True) - point["changed"]),
    ),
    FalseTheory(
        theory_id="undirected_reachability",
        breaks=(
            "Corollary 2.1: anything connected to the change is reopened, including "
            "claims no path reaches, so repair is not inclusion-minimal"
        ),
        rule=lambda point: point["certified"]
        - (_reachable(point, undirected=True) - point["changed"]),
    ),
    FalseTheory(
        theory_id="first_node_immune",
        breaks=(
            "Theorem 1 for one node: node 0 keeps its certification even when the change "
            "reaches it -- a protected claim that outranks its own support"
        ),
        rule=lambda point: (
            point["certified"] - (_specified(*_point(point)[:3])[1])
        )
        | (point["certified"] & frozenset({0})),
    ),
    FalseTheory(
        theory_id="first_node_always_reopened",
        breaks=(
            "Corollary 2.1 for one node: node 0 is reopened whether or not the change "
            "reaches it, so the repair is strictly larger than it needs to be"
        ),
        rule=lambda point: (point["certified"] - _specified(*_point(point)[:3])[1])
        - frozenset({0}),
    ),
)

#: Not a false theory: this is FORMAL_CORE_V2.1's `Aff_D(E,X)`, and it is the
#: correct operator *there*. It is kept out of the register and pinned by a test
#: instead, because the V1 check is about Definition 8 and registering V2.1's
#: correction as "wrong" would make the register say something false. What the
#: exactness assertion buys is that the V1 check can now tell the two apart at
#: all; it does not say which of them P6 should ship.
def root_inclusive_reopening(point: ModelPoint) -> frozenset[int]:
    """`Reopen` with V2.1's `Aff_D(E,X)`: the changed certified roots are reopened too."""

    node_count, edges, changed, certified = _point(point)
    specified, _ = _specified(node_count, edges, changed)
    return certified - specified

REOPENING_AXES: tuple[str, ...] = ("node_count", "edges", "changed", "certified")


# --------------------------------------------------------------------------
# V2.1 root-inclusive reopening: `check_theory_closure_v2_1.check_root_inclusive_safety`
# --------------------------------------------------------------------------

CLOSURE_REFERENCE_ID = "check_theory_closure_v2_1.affected"

NODES: tuple[str, ...] = theory_closure.NODES


def closure_model_space() -> tuple[ModelPoint, ...]:
    """The shipped check's 960 cases: every forward DAG on four nodes, every change."""

    certified = frozenset(NODES)
    return tuple(
        {
            "edges": edges,
            "changed": frozenset(combo),
            "certified": certified,
        }
        for edges in theory_closure.all_forward_dags()
        for size in range(1, len(NODES) + 1)
        for combo in combinations(NODES, size)
    )


@lru_cache(maxsize=None)
def _closure_terms(
    edges: frozenset[tuple[str, str]], changed: frozenset[str], certified: frozenset[str]
) -> tuple[frozenset[str], frozenset[str]]:
    return theory_closure.specified_affected_terms(
        certified, theory_closure.transitive_closure(edges), changed
    )


def _closure_point(point: ModelPoint):
    return point["edges"], point["changed"], point["certified"]


def reference_affected(point: ModelPoint) -> frozenset[str]:
    """The shipped operator: `affected(certified, edges, changed)`."""

    edges, changed, certified = _closure_point(point)
    return theory_closure.affected(certified, edges, changed)


def _accepts_closure_root_term(rule: Rule) -> bool:
    for point in CLOSURE_SPACE:
        roots, _ = _closure_terms(*_closure_point(point))
        if not roots <= rule(point):
            return False
    return True


def _accepts_closure_descendant_term(rule: Rule) -> bool:
    for point in CLOSURE_SPACE:
        _, downstream = _closure_terms(*_closure_point(point))
        if not downstream <= rule(point):
            return False
    return True


def _accepts_closure_minimality(rule: Rule) -> bool:
    for point in CLOSURE_SPACE:
        roots, downstream = _closure_terms(*_closure_point(point))
        if not rule(point) <= roots | downstream:
            return False
    return True


CLOSURE_CHECKS: tuple[MechanizedCheck, ...] = (
    MechanizedCheck(
        check_id="root_inclusive_safety.root_term",
        asserts="every directly changed certified claim is reopened (V2.1 Theorem 1, first term)",
        accepts=_accepts_closure_root_term,
    ),
    MechanizedCheck(
        check_id="root_inclusive_safety.descendant_term",
        asserts=(
            "every certified claim in the strict downstream closure is reopened "
            "(V2.1 Theorem 1, second term)"
        ),
        accepts=_accepts_closure_descendant_term,
    ),
    MechanizedCheck(
        check_id="root_inclusive_safety.minimality",
        asserts="nothing outside Aff_D(E,X) is reopened (V2.1 Theorem 4, Corollary 4.1)",
        accepts=_accepts_closure_minimality,
    ),
)


def _closure_reachable(point: ModelPoint, *, reverse: bool = False, undirected: bool = False):
    edges, changed, _ = _closure_point(point)
    if reverse:
        edges = frozenset((target, source) for source, target in edges)
    if undirected:
        edges = edges | frozenset((target, source) for source, target in edges)
    closure = theory_closure.transitive_closure(edges)
    return frozenset(node for root in changed for node in closure[root])


def _closure_bounded(point: ModelPoint, depth: int) -> frozenset[str]:
    edges, changed, _ = _closure_point(point)
    frontier = set(changed)
    seen: set[str] = set()
    for _ in range(depth):
        frontier = {target for source, target in edges if source in frontier}
        seen |= frontier
    return frozenset(seen)


FALSE_CLOSURE_THEORIES: tuple[FalseTheory, ...] = (
    FalseTheory(
        theory_id="nothing_affected",
        breaks="V2.1 Theorem 1: no certification is ever reopened, so every stale claim stands",
        rule=lambda point: frozenset(),
    ),
    FalseTheory(
        theory_id="full_reset",
        breaks=(
            "V2.1 Corollary 4.1: every certified claim is reopened, which is uniformly "
            "sound and strictly non-minimal"
        ),
        rule=lambda point: point["certified"],
    ),
    FalseTheory(
        theory_id="descendants_only",
        breaks=(
            "V2.1's central correction: the changed certified roots are dropped, so a "
            "claim whose own coordinate changed keeps its certification"
        ),
        rule=lambda point: point["certified"]
        & (_closure_reachable(point) - point["changed"]),
    ),
    FalseTheory(
        theory_id="changed_roots_only",
        breaks=(
            "V2.1 Theorem 1's descendant term: only what changed directly is reopened, "
            "so everything downstream keeps a stale certification"
        ),
        rule=lambda point: point["certified"] & point["changed"],
    ),
    FalseTheory(
        theory_id="direct_successors_only",
        breaks=(
            "V2.1 Theorem 1 for chains: reopening stops at the immediate children of the "
            "change"
        ),
        rule=lambda point: point["certified"]
        & (point["changed"] | _closure_bounded(point, 1)),
    ),
    FalseTheory(
        theory_id="depth_capped_at_two",
        breaks="V2.1 Theorem 1 at distance three: the transitive closure is truncated",
        rule=lambda point: point["certified"]
        & (point["changed"] | _closure_bounded(point, 2)),
    ),
    FalseTheory(
        theory_id="ancestors_instead_of_descendants",
        breaks=(
            "the direction of dependency: what the change depends on is reopened instead "
            "of what depends on the change"
        ),
        rule=lambda point: point["certified"]
        & (point["changed"] | _closure_reachable(point, reverse=True)),
    ),
    FalseTheory(
        theory_id="undirected_reachability",
        breaks=(
            "V2.1 Corollary 4.1: anything connected to the change is reopened, including "
            "its ancestors, so the repair is not inclusion-minimal"
        ),
        rule=lambda point: point["certified"]
        & (point["changed"] | _closure_reachable(point, undirected=True)),
    ),
    FalseTheory(
        theory_id="one_extra_claim",
        breaks=(
            "V2.1 Theorem 4: claim 'a' is reopened whether or not the change reaches it, "
            "so the affected set is strictly larger than the theorem allows"
        ),
        rule=lambda point: (
            point["certified"] & (point["changed"] | _closure_reachable(point))
        )
        | (point["certified"] & frozenset({"a"})),
    ),
)

CLOSURE_AXES: tuple[str, ...] = ("edges", "changed", "certified")


# --------------------------------------------------------------------------
# The audit
# --------------------------------------------------------------------------

REOPENING_SPACE: tuple[ModelPoint, ...] = reopening_model_space()
REOPENING_AXIS_SPACE: tuple[ModelPoint, ...] = reopening_model_space(AXIS_NODE_COUNT)
CLOSURE_SPACE: tuple[ModelPoint, ...] = closure_model_space()


# --------------------------------------------------------------------------
# The failure record's own diagnostic, run for real
# --------------------------------------------------------------------------
#
# `measure_refutation_capacity` asks whether a wrong *strategy* -- a wrong set of
# reopened claims -- would have made a check fail. It cannot see the defect that
# made these two checks vacuous, because that defect was co-mutation: the
# specification side of each assertion was built by calling the same operator the
# implementation side called, so substituting a wrong operator moved both sides
# together and the comparison survived. `orion.study.p6.finite_model_theories`
# records the same blind spot for T4 ("no capacity measure can see that").
#
# So the substitution probe below is kept beside the capacity table. It is
# `research/failures/2026-08-tautological-assertion-in-finite-check/`'s own
# reproduction recipe -- replace the operator under test and re-run -- executed
# against both the assertions as they stood and the assertions as repaired, so
# the before column is re-derived rather than quoted.

#: Bound once, before any substitution: two of the wrong operators below are the
#: real one perturbed by a single node, and reading them through the module
#: attribute after it has been replaced makes them read themselves.
_TRUE_DESCENDANTS = finite_models.descendants
_TRUE_CLOSURE_DESCENDANTS = theory_closure.descendants

REOPENING_SUBSTITUTIONS: dict[str, Any] = {
    "nothing_is_downstream": lambda node_count, edges, changed: frozenset(),
    "everything_is_downstream": lambda node_count, edges, changed: frozenset(range(node_count)),
    "changed_set_itself": lambda node_count, edges, changed: frozenset(changed),
    "direct_successors_only": lambda node_count, edges, changed: frozenset(
        target for source, target in edges if source in changed
    )
    - frozenset(changed),
    "ancestors_instead_of_descendants": lambda node_count, edges, changed: (
        finite_models.specified_downstream(
            _closure(node_count, tuple((t, s) for s, t in edges)), frozenset(changed)
        )
        - frozenset(changed)
    ),
    "undirected_reachability": lambda node_count, edges, changed: (
        finite_models.specified_downstream(
            _closure(node_count, tuple(edges) + tuple((t, s) for s, t in edges)),
            frozenset(changed),
        )
        - frozenset(changed)
    ),
    "node_zero_never_downstream": lambda node_count, edges, changed: (
        _TRUE_DESCENDANTS(node_count, edges, changed) - frozenset({0})
    ),
    "node_zero_always_downstream": lambda node_count, edges, changed: (
        _TRUE_DESCENDANTS(node_count, edges, changed) | (frozenset({0}) - frozenset(changed))
    ),
}

CLOSURE_SUBSTITUTIONS: dict[str, Any] = {
    "nothing_is_downstream": lambda edges, roots: frozenset(),
    "everything_is_downstream": lambda edges, roots: frozenset(NODES) - frozenset(roots),
    "direct_successors_only": lambda edges, roots: frozenset(
        target for source, target in edges if source in roots
    )
    - frozenset(roots),
    "ancestors_instead_of_descendants": lambda edges, roots: frozenset(
        node
        for root in roots
        for node in theory_closure.transitive_closure(
            frozenset((t, s) for s, t in edges)
        )[root]
    )
    - frozenset(roots),
    "undirected_reachability": lambda edges, roots: frozenset(
        node
        for root in roots
        for node in theory_closure.transitive_closure(
            edges | frozenset((t, s) for s, t in edges)
        )[root]
    )
    - frozenset(roots),
    # Kept although it is inert: `all_forward_dags` only emits edges from an
    # earlier node to a later one, so "a" is a universal source and can never be
    # downstream of anything. An operator that hides "a" is the shipped operator
    # under another name over this space, and the probe has to say so rather than
    # score it as a kill.
    "claim_a_never_downstream": lambda edges, roots: (
        _TRUE_CLOSURE_DESCENDANTS(edges, roots) - frozenset({"a"})
    ),
    "claim_d_never_downstream": lambda edges, roots: (
        _TRUE_CLOSURE_DESCENDANTS(edges, roots) - frozenset({"d"})
    ),
    "claim_a_always_downstream": lambda edges, roots: (
        _TRUE_CLOSURE_DESCENDANTS(edges, roots) | (frozenset({"a"}) - frozenset(roots))
    ),
}


def _pre_repair_check_reopening(downstream_of: Any, node_count: int = NODE_COUNT) -> tuple[int, int]:
    """`check_reopening` with the assertions exactly as they stood before 2026-08-22."""

    dag_count = case_count = 0
    for edges in _dags(node_count):
        dag_count += 1
        for changed_raw in finite_models.powerset(range(node_count)):
            changed = frozenset(int(value) for value in changed_raw)
            if not changed:
                continue
            downstream = downstream_of(node_count, edges, changed)
            for certified_raw in finite_models.powerset(range(node_count)):
                certified = frozenset(int(value) for value in certified_raw)
                retained = certified.difference(downstream)
                assert not retained.intersection(downstream)
                assert retained == certified.difference(downstream)
                case_count += 1
    return dag_count, case_count


def _pre_repair_root_inclusive_safety(downstream_of: Any) -> tuple[int, int]:
    """`check_root_inclusive_safety` with the assertions as they stood before 2026-08-22."""

    certified = frozenset(NODES)
    cases = changed_root_occurrences = 0
    for edges in theory_closure.all_forward_dags():
        for size in range(1, len(NODES) + 1):
            for combo in combinations(NODES, size):
                changed = frozenset(combo)
                got = frozenset(
                    (certified & changed) | (certified & downstream_of(edges, changed))
                )
                assert certified & changed <= got
                assert certified & downstream_of(edges, changed) <= got
                cases += 1
                changed_root_occurrences += len(certified & changed)
    return cases, changed_root_occurrences


def _survives(run: Any) -> bool:
    try:
        run()
    except AssertionError:
        return False
    return True


def _reopening_divergence(operator: Any) -> int:
    """Enumerated `(edges, changed)` pairs on which a substitution differs from the real one."""

    return sum(
        1
        for edges in _dags(NODE_COUNT)
        for changed_raw in finite_models.powerset(range(NODE_COUNT))
        if changed_raw
        for changed in (frozenset(int(value) for value in changed_raw),)
        if operator(NODE_COUNT, edges, changed)
        != _TRUE_DESCENDANTS(NODE_COUNT, edges, changed)
    )


def _closure_divergence(operator: Any) -> int:
    return sum(
        1
        for edges in theory_closure.all_forward_dags()
        for size in range(1, len(NODES) + 1)
        for combo in combinations(NODES, size)
        for changed in (frozenset(combo),)
        if operator(edges, changed) != _TRUE_CLOSURE_DESCENDANTS(edges, changed)
    )


def _substitution_lane(
    substitutions: dict[str, Any],
    *,
    divergence: Any,
    pre_repair: Any,
    module: Any,
    shipped: Any,
) -> dict[str, tuple[str, ...]]:
    """One lane of the probe, with the inert substitutions screened out first.

    A substitution that agrees with the shipped operator on every enumerated pair
    is not a wrong operator over this space; it is the shipped one renamed, and
    counting its acceptance would inflate the before column with something no
    check could ever have caught. `measure_refutation_capacity` screens the same
    way, and for the same reason.
    """

    inert = tuple(name for name, operator in substitutions.items() if not divergence(operator))
    live = tuple(name for name in substitutions if name not in inert)

    before = tuple(
        name
        for name in live
        if _survives(lambda operator=substitutions[name]: pre_repair(operator))
    )
    original = getattr(module, "descendants")
    after: list[str] = []
    rejected_inert: list[str] = []
    try:
        for name in live:
            module.descendants = substitutions[name]
            if _survives(shipped):
                after.append(name)
        for name in inert:
            module.descendants = substitutions[name]
            if not _survives(shipped):
                rejected_inert.append(name)
    finally:
        module.descendants = original
    return {
        "substituted": tuple(substitutions),
        "inert": inert,
        "live": live,
        "accepted_before_repair": before,
        "accepted_after_repair": tuple(after),
        "rejected_inert_after_repair": tuple(rejected_inert),
    }


def operator_substitution_report() -> dict[str, dict[str, tuple[str, ...]]]:
    """Which wrong graph operators the two checks accept, before and after the repair.

    "After" runs the shipped function with the module's `descendants` replaced,
    which is what a reader of the repaired source can reproduce in three lines.
    "Before" replays the same loop carrying the assertions as they stood, so the
    column is re-derived on every run rather than quoted from a commit message.
    """

    return {
        "check_finite_models.check_reopening": _substitution_lane(
            REOPENING_SUBSTITUTIONS,
            divergence=_reopening_divergence,
            pre_repair=_pre_repair_check_reopening,
            module=finite_models,
            shipped=finite_models.check_reopening,
        ),
        "check_theory_closure_v2_1.check_root_inclusive_safety": _substitution_lane(
            CLOSURE_SUBSTITUTIONS,
            divergence=_closure_divergence,
            pre_repair=_pre_repair_root_inclusive_safety,
            module=theory_closure,
            shipped=theory_closure.check_root_inclusive_safety,
        ),
    }


def audit_checker(
    *,
    checker_id: str,
    checks: Sequence[MechanizedCheck],
    reference: Rule,
    reference_id: str,
    theories: Sequence[FalseTheory],
    space: Sequence[ModelPoint],
    axes: Sequence[str],
    axis_space: Sequence[ModelPoint],
) -> dict[str, Any]:
    capacities = tuple(
        measure_refutation_capacity(
            check,
            reference=reference,
            reference_id=reference_id,
            theories=theories,
            space=space,
        )
        for check in checks
    )
    sensitivities = tuple(
        axis_sensitivity(axis, reference=reference, space=axis_space) for axis in axes
    )
    coverage = assess_theory_coverage(capacities, label=checker_id)
    return {
        "checker_id": checker_id,
        "reference_id": reference_id,
        "points": len(space),
        "axis_points": len(axis_space),
        "registered_false_theories": len(theories),
        "outcome": worst_outcome(
            tuple(item.assessment for item in capacities) + (coverage.assessment,)
        ).value,
        "capacities": capacities,
        "coverage": coverage,
        "axes": sensitivities,
    }


def audit_p6_graph_checkers() -> tuple[dict[str, Any], ...]:
    """Audit both shipped graph checkers over their own enumerated spaces."""

    reopening = audit_checker(
        checker_id="check_finite_models.check_reopening",
        checks=REOPENING_CHECKS,
        reference=reference_retained,
        reference_id=REOPENING_REFERENCE_ID,
        theories=FALSE_REOPENING_THEORIES,
        space=REOPENING_SPACE,
        axes=REOPENING_AXES,
        axis_space=REOPENING_AXIS_SPACE,
    )
    closure = audit_checker(
        checker_id="check_theory_closure_v2_1.check_root_inclusive_safety",
        checks=CLOSURE_CHECKS,
        reference=reference_affected,
        reference_id=CLOSURE_REFERENCE_ID,
        theories=FALSE_CLOSURE_THEORIES,
        space=CLOSURE_SPACE,
        axes=CLOSURE_AXES,
        axis_space=CLOSURE_SPACE,
    )
    return (reopening, closure)


def report_as_json(reports: Sequence[dict[str, Any]]) -> dict[str, Any]:
    checkers = []
    for report in reports:
        payload = {
            key: value
            for key, value in report.items()
            if key not in {"capacities", "axes", "coverage"}
        }
        payload["capacities"] = [item.as_json() for item in report["capacities"]]
        payload["axes"] = [item.as_json() for item in report["axes"]]
        payload["coverage"] = report["coverage"].as_json()
        checkers.append(payload)
    substitutions = operator_substitution_report()
    for payload in checkers:
        entry = substitutions.get(str(payload["checker_id"]))
        if entry is not None:
            payload["operator_substitution"] = {
                key: list(value) for key, value in entry.items()
            }
    return {
        "schema": "P6.GraphCheckerRefutationCapacity.v1",
        "outcome": worst_outcome(
            tuple(
                capacity.assessment
                for report in reports
                for capacity in report["capacities"]
            )
            + tuple(report["coverage"].assessment for report in reports)
        ).value,
        "checkers": checkers,
    }


def _render(reports: Sequence[dict[str, Any]]) -> str:
    substitutions = operator_substitution_report()
    lines: list[str] = []
    for report in reports:
        lines.append(
            f"{report['checker_id']}  ({report['points']} enumerated points, "
            f"{report['registered_false_theories']} declared false operators)"
        )
        header = f"  {'check':44} {'refuted':>8} {'survived':>9}  outcome"
        lines.append(header)
        lines.append("  " + "-" * (len(header) - 2))
        for capacity in report["capacities"]:
            lines.append(
                f"  {capacity.check_id:44} {len(capacity.refuted):>8} "
                f"{len(capacity.survivors):>9}  {capacity.outcome.value}"
            )
            if capacity.survivors:
                lines.append(f"      accepted: {', '.join(capacity.survivors)}")
        for axis in report["axes"]:
            if not axis.varied:
                lines.append(f"  axis {axis.axis!r}: constant, nothing about it was tested")
                continue
            state = "INERT" if axis.inert else "read by the operator"
            lines.append(
                f"  axis {axis.axis!r}: {axis.values} values, "
                f"{axis.verdict_changing_pairs}/{axis.comparable_pairs} sibling pairs "
                f"change the verdict -> {state}"
                + (f", every count repeated {axis.multiplier}x" if axis.inert else "")
            )
        entry = substitutions.get(str(report["checker_id"]))
        if entry is not None:
            live = entry["live"]
            before = entry["accepted_before_repair"]
            after = entry["accepted_after_repair"]
            lines.append(
                f"  wrong graph operators substituted for `descendants`: "
                f"{len(live)} live of {len(entry['substituted'])}; accepted before the "
                f"repair {len(before)}/{len(live)}, after {len(after)}/{len(live)}"
            )
            if entry["inert"]:
                lines.append(
                    "      inert over this space, so no check could ever reject them: "
                    + ", ".join(entry["inert"])
                )
            if after:
                lines.append(f"      still accepted: {', '.join(after)}")
            if entry["rejected_inert_after_repair"]:
                lines.append(
                    "      REJECTED though extensionally identical: "
                    + ", ".join(entry["rejected_inert_after_repair"])
                )
        coverage = report["coverage"]
        lines.append(
            f"  false operators rejected by no check: "
            f"{len(coverage.unrefuted)}/{len(coverage.live)}"
            + (f" ({', '.join(coverage.unrefuted)})" if coverage.unrefuted else "")
        )
        lines.append(f"  checker outcome: {report['outcome']}")
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P6 graph-checker refutation capacity")
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    reports = audit_p6_graph_checkers()
    payload = report_as_json(reports)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else _render(reports))
    for report in reports:
        require_refutable(report["capacities"], label=report["checker_id"])
    for checker in payload["checkers"]:
        entry = checker.get("operator_substitution")
        if not entry:
            continue
        if entry["accepted_after_repair"]:
            raise UnrefutableCheck(
                f"{checker['checker_id']}: a wrong graph operator is still accepted: "
                + ", ".join(entry["accepted_after_repair"])
            )
        if entry["rejected_inert_after_repair"]:
            raise ValueError(
                f"{checker['checker_id']}: rejected an operator that agrees with the "
                "shipped one on every enumerated pair, so the check is not a function "
                "of the operator's behaviour: "
                + ", ".join(entry["rejected_inert_after_repair"])
            )
    return 3 if Outcome(payload["outcome"]).blocks else 0


if __name__ == "__main__":
    raise SystemExit(main())
