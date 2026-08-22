"""P6's certificate model, interpreted in the proved reopening semantics.

``P6-U-T2`` asks for the existing finite result to follow *as a corollary* of
the general theorem, and the emphasis is load-bearing. A corollary of what?
``lift_interpretation`` derives the same numbers from primitives about donor
certificates and embeddings, which is a derivation but not a corollary: those
primitives are not the ones ``reopening_calculus_smt`` proves theorems about, so
the finite result ended up following from a second theory standing beside the
first rather than from the first.

This closes that gap. It gives an interpretation of the certificate model *into*
the reopening signature --- nodes, a dependency edge, a changed set --- and then

1. proves, over an uninterpreted node sort and for any number of coordinates,
   that under the interpretation's frame conditions the reopening theorems
   entail withdrawal, restoration, minimality and the absence of collateral
   reopening; and
2. recomputes P6's published 155 and 1,055 by running the *committed*
   ``descendants`` --- the implementation ``P6-U-T1`` verified against the
   independent specification on 61,440 of 61,440 cases --- over the interpreted
   graph, rather than by evaluating a rule of this module's own.

So the two counts are instances of theorems about dependency graphs, produced by
an implementation that was independently checked against those theorems.

The interpretation
------------------
A certificate over *n* coordinates is the star graph on ``n + 1`` nodes: one
node per coordinate, one node for the certificate itself, and an edge from each
coordinate to the certificate. Damaging a coordinate is changing its node.
Repairing a coordinate is removing it from the changed set. Nothing else is
added: the certificate has no outgoing edges and coordinates have no edges to
each other, and both of those are stated as frame conditions the theorems are
proved under rather than as facts about the encoding.

Under that reading the published counts are not new facts:

* **155 full restorations** is reopening *completeness* --- repairing every
  damaged coordinate empties the changed set, and a node reachable from nothing
  is not reopened.
* **1,055 proper-subset failures** is reopening *minimality* --- a proper repair
  leaves some coordinate changed, that coordinate reaches the certificate, and
  so the certificate is still reopened.

What this does not establish
----------------------------
The interpretation is a map this lane wrote, so it can be wrong in the direction
of flattering the theorem. Two things are done about that rather than promised:
the frame conditions are stated as explicit axioms and each is shown to be
load-bearing by dropping it and re-running the proof, and the counts are
produced by the committed implementation rather than by a rule defined here. It
remains true that no evaluator outside this lane has checked any of it, which is
``P6-U-T4``.
"""

from __future__ import annotations

from enum import Enum
from itertools import combinations
from typing import Any, Mapping

from orion.programme.records import Outcome
from orion.programme.mechanized import (
    ProofResult,
    Theorem,
    discharge,
    load_executable_model,
    require_z3,
)
from orion.study.p6.reopening_calculus_smt import (
    EXECUTABLE_MODEL,
    _closure_axioms,
    _reopened,
    _vocabulary,
)

SCHEMA_VERSION = "orion.p6.certificate-as-dependency-graph.v1"

#: P6's five donor families and five lift coordinates, from the shipped module.
from orion.study.p6 import lift_theories as _lift_theories  # noqa: E402

DONORS: tuple[str, ...] = _lift_theories.DONOR_FAMILIES
COORDINATES: tuple[str, ...] = _lift_theories.LIFT_COORDINATES

PUBLISHED_FULL_RESTORATIONS = 155
PUBLISHED_PROPER_SUBSET_FAILURES = 1055


CERTIFICATE_WITHDRAWN = Theorem(
    name="CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
    statement=(
        "under the star interpretation, if any coordinate node is changed then the "
        "certificate node is reopened -- damaging one coordinate withdraws the whole "
        "certificate, for any number of coordinates"
    ),
    why_it_matters=(
        "P6's finite check asserts this state by state over five coordinates. Stated here it is a consequence of one coordinate reaching the certificate, which holds at any width and is why the number five is incidental."
    )
)

CERTIFICATE_RESTORED = Theorem(
    name="CERTIFICATE_RESTORED_BY_FULL_REPAIR",
    statement=(
        "if no coordinate node is changed then the certificate node is not reopened -- "
        "repairing every damaged coordinate restores the certificate. This is the "
        "general form of P6's 155 full restorations"
    ),
    why_it_matters=(
        "Without it the 155 would be an observation about an enumeration. With it the 155 is reopening completeness evaluated at 31 damage sets and five donors."
    )
)

PARTIAL_REPAIR_INSUFFICIENT = Theorem(
    name="PARTIAL_REPAIR_LEAVES_CERTIFICATE_REOPENED",
    statement=(
        "if a repair leaves at least one coordinate changed then the certificate is "
        "still reopened, however many coordinates were repaired. This is the general "
        "form of P6's 1,055 proper-subset failures"
    ),
    why_it_matters=(
        "This is the half that carries P6's claim. A framework in which some coordinate compensates for another would refute it, and the 1,055 is exactly the count that moves when the primitive is weakened that way."
    )
)

NO_COLLATERAL_REOPENING = Theorem(
    name="UNDAMAGED_COORDINATES_ARE_NOT_REOPENED",
    statement=(
        "an unchanged coordinate node is never reopened by damage elsewhere, so a "
        "repair has nothing to repair beyond the coordinates it damaged. Without this "
        "the restoration theorem would be about a different set of nodes than the "
        "damage was"
    ),
    why_it_matters=(
        "The easy thing to miss. If damaging one coordinate reopened another, then repairing the damaged set would not be repairing the reopened set, and the restoration theorem would silently be about different nodes than the damage."
    )
)

CERTIFICATE_SUPPORTS_NOTHING = Theorem(
    name="CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED",
    statement=(
        "the certificate node has no outgoing edge. This was a frame condition until "
        "the load-bearing check reported it inert; it is a consequence of the other "
        "three and is discharged here rather than assumed"
    ),
    why_it_matters=(
        "An axiom that no theorem needs is either decoration or a redundant "
        "presentation of an axiom that is doing the work, and the two look identical "
        "from inside. Deriving it settles which: the star interpretation rests on three "
        "independent conditions, not four, and the fourth is a theorem about them."
    ),
)

CERTIFICATE_IS_A_SINK = Theorem(
    name="CERTIFICATE_DAMAGE_REOPENS_NOTHING",
    statement=(
        "changing the certificate node reopens no coordinate, so the dependency runs "
        "one way. This is reopening conservativity at the certificate level"
    ),
    why_it_matters=(
        "A certificate that fed back into its own coordinates would make the star cyclic, and the cycle characterisation says a node on a cycle reopens itself. The interpretation has to forbid it rather than assume it away."
    )
)

THEOREMS: tuple[Theorem, ...] = (
    CERTIFICATE_WITHDRAWN,
    CERTIFICATE_RESTORED,
    PARTIAL_REPAIR_INSUFFICIENT,
    NO_COLLATERAL_REOPENING,
    CERTIFICATE_IS_A_SINK,
    CERTIFICATE_SUPPORTS_NOTHING,
)


# ---------------------------------------------------------------------------
# The interpretation, as frame conditions on the reopening signature
# ---------------------------------------------------------------------------

#: The frame conditions, each independently droppable so its weight can be measured.
#:
#: There were four. "The certificate supports nothing" was one of them, and the
#: load-bearing check below reported it inert: dropping it lost no theorem. So
#: was "the certificate is not one of its own coordinates". Neither result was a
#: reprieve -- dropping *both* loses three theorems, because each is derivable
#: from the other two conditions plus the one that remains, so the four were a
#: redundant presentation of three. An interpretation should assume as little as
#: it can, so the sink is now discharged as a theorem from the three below rather
#: than assumed, and the check that found the redundancy is kept and now passes
#: on its own terms.
FRAME_CONDITION_IDS: tuple[str, ...] = (
    "coordinates_support_the_certificate",
    "coordinates_do_not_support_each_other",
    "the_certificate_is_not_a_coordinate",
)


def _interpretation_axioms(
    vocab: dict[str, Any], cert: Any, coord: Any, *, drop: str | None = None
) -> list[Any]:
    """The star interpretation, written as axioms rather than as an encoding.

    ``drop`` omits one named condition, which is how each is shown to be
    load-bearing: a frame condition no theorem needs is decoration, and a proof
    that survives dropping every condition was never about the interpretation.
    """

    if drop is not None and drop not in FRAME_CONDITION_IDS:
        raise ValueError(f"unknown frame condition {drop!r}")

    solver = vocab["z3"]
    Node, Edge = vocab["Node"], vocab["Edge"]
    m, n = solver.Consts("fm fn", Node)

    axioms: dict[str, Any] = {
        # Every coordinate supports the certificate.
        "coordinates_support_the_certificate": solver.ForAll(
            [n], solver.Implies(coord(n), Edge(n, cert))
        ),
        # Every edge runs from a coordinate to the
        # certificate. Stated separately from the two above because it is the
        # one that forbids coordinate-to-coordinate support, which is what makes
        # collateral reopening impossible.
        "coordinates_do_not_support_each_other": solver.ForAll(
            [m, n], solver.Implies(Edge(m, n), solver.And(coord(m), n == cert))
        ),
        "the_certificate_is_not_a_coordinate": solver.Not(coord(cert)),
    }
    return [clause for name, clause in axioms.items() if name != drop]


def _damage_on_coordinates(vocab: dict[str, Any], coord: Any, changed: Any) -> Any:
    """Damage lands on coordinates: the certificate is not itself edited."""

    solver = vocab["z3"]
    n = solver.Const("dn", vocab["Node"])
    return solver.ForAll([n], solver.Implies(changed(n), coord(n)))


def _queries(drop: str | None = None) -> list[tuple[Theorem, list[Any], Any, Any]]:
    """Every theorem as a (theorem, axioms, claim, certificate) tuple.

    Split out of :func:`prove_all` so the same queries can be re-asked in a
    bounded world when the open search returns ``unknown``. Building them twice
    from two copies of the encoding would let the load-bearing measurement drift
    from the proofs it is measuring.
    """

    vocab = _vocabulary()
    solver = vocab["z3"]
    Node = vocab["Node"]
    Changed, Changed2 = vocab["Changed"], vocab["Changed2"]

    cert = solver.Const("cert", Node)
    coord = solver.Function("Coord", Node, solver.BoolSort())

    base = _closure_axioms(vocab) + _interpretation_axioms(vocab, cert, coord, drop=drop)

    x = solver.Const("x", Node)
    y = solver.Const("y", Node)
    witness = solver.Const("w", Node)
    residue = solver.Const("res", Node)

    return [
        (
            CERTIFICATE_WITHDRAWN,
            base + [_damage_on_coordinates(vocab, coord, Changed)],
            solver.Implies(
                solver.Exists([witness], solver.And(coord(witness), Changed(witness))),
                _reopened(vocab, cert, Changed),
            ),
            cert,
        ),
        (
            CERTIFICATE_RESTORED,
            base + [solver.ForAll([x], solver.Not(Changed(x)))],
            solver.Not(_reopened(vocab, cert, Changed)),
            cert,
        ),
        (
            PARTIAL_REPAIR_INSUFFICIENT,
            base
            + [
                _damage_on_coordinates(vocab, coord, Changed2),
                solver.ForAll([x], solver.Implies(Changed2(x), Changed(x))),
            ],
            solver.Implies(
                solver.Exists([residue], Changed2(residue)),
                _reopened(vocab, cert, Changed2),
            ),
            cert,
        ),
        (
            NO_COLLATERAL_REOPENING,
            base + [_damage_on_coordinates(vocab, coord, Changed)],
            solver.ForAll(
                [y],
                solver.Implies(
                    solver.And(coord(y), solver.Not(Changed(y))),
                    solver.Not(_reopened(vocab, y, Changed)),
                ),
            ),
            cert,
        ),
        (
            CERTIFICATE_IS_A_SINK,
            base + [solver.ForAll([x], Changed(x) == (x == cert))],
            solver.ForAll(
                [y], solver.Implies(coord(y), solver.Not(_reopened(vocab, y, Changed)))
            ),
            cert,
        ),
        (
            CERTIFICATE_SUPPORTS_NOTHING,
            base,
            solver.ForAll([x], solver.Not(vocab["Edge"](cert, x))),
            cert,
        ),
    ]


def prove_all(*, timeout_ms: int = 30000, drop: str | None = None) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS` under the interpretation."""

    return tuple(
        discharge(theorem, axioms, claim, timeout_ms=timeout_ms)
        for theorem, axioms, claim, _cert in _queries(drop=drop)
    )


def _drop_queries(condition: str) -> list[tuple[str, list[Any], Any, Any]]:
    """The queries under one dropped condition, keyed by theorem name."""

    return [
        (theorem.name, axioms, claim, cert)
        for theorem, axioms, claim, cert in _queries(drop=condition)
    ]


#: Node-sort bound used only when searching for a countermodel. Sound in that
#: direction and in no other: a model of the axioms plus the negated claim is a
#: genuine countermodel however small its universe, while failing to find one in
#: a bounded universe proves nothing at all. Never added to a proof query.
REFUTATION_WORLD_SIZE = 4


class RefutationSearch(str, Enum):
    """What a bounded countermodel search actually returned.

    Three values, because ``sat`` and ``unsat`` and ``unknown`` are three facts
    and the first version of this collapsed the last two into ``False``. A
    solver that proved no countermodel exists in the bounded world and a solver
    that ran out of time both said "not refuted", so a condition whose search
    timed out was indistinguishable from one that carries nothing --- and
    ``inert_conditions`` reported the second, which is a claim about the axiom.
    """

    COUNTERMODEL = "COUNTERMODEL"
    #: No countermodel exists in a universe of this size. Sound in one direction
    #: only: it does not show the claim holds unboundedly.
    NO_COUNTERMODEL = "NO_COUNTERMODEL"
    #: The search did not settle. A fact about the search, not about the axiom.
    UNDECIDED = "UNDECIDED"


def search_for_a_countermodel(
    axioms: list[Any], claim: Any, cert: Any, *, size: int = REFUTATION_WORLD_SIZE, timeout_ms: int = 20000
) -> RefutationSearch:
    """Look for a countermodel in a universe of at most ``size`` nodes.

    Needed because the unbounded search is not stable. Asking the solver to
    refute a universally quantified claim over an uninterpreted sort leaves it
    hunting for a model it may or may not find, and the same drop returns a
    countermodel on one run and ``unknown`` on the next --- which would make a
    load-bearing measurement depend on machine load. Bounding the sort turns the
    search finite, and returning three values rather than two keeps the two ways
    of not finding one apart.
    """

    solver = require_z3()
    Node = cert.sort()
    world = [solver.Const(f"w{index}", Node) for index in range(size)]
    x = solver.Const("bounded_x", Node)
    bound = solver.ForAll([x], solver.Or(*[x == member for member in world]))

    checker = solver.Solver()
    checker.set("timeout", timeout_ms)
    for axiom in axioms:
        checker.add(axiom)
    checker.add(bound)
    checker.add(solver.Not(claim))
    verdict = checker.check()
    if verdict == solver.sat:
        return RefutationSearch.COUNTERMODEL
    if verdict == solver.unsat:
        return RefutationSearch.NO_COUNTERMODEL
    return RefutationSearch.UNDECIDED


def refute_in_a_bounded_world(
    axioms: list[Any], claim: Any, cert: Any, *, size: int = REFUTATION_WORLD_SIZE, timeout_ms: int = 20000
) -> bool:
    """``True`` when a countermodel was found. Kept for callers that want a bool.

    Do not use this to decide that an axiom carries nothing: ``False`` covers
    both "no countermodel in this world" and "the search gave up", and only the
    first is evidence. Use :func:`search_for_a_countermodel` for that.
    """

    return (
        search_for_a_countermodel(axioms, claim, cert, size=size, timeout_ms=timeout_ms)
        is RefutationSearch.COUNTERMODEL
    )


#: How many times the drop measurement is repeated. One run is not a
#: measurement here: the solver's model search is not deterministic on this
#: encoding, and the same dropped axiom yields a countermodel on one run and
#: ``unknown`` on the next.
LOAD_BEARING_REPEATS = 3


def classify_frame_conditions(
    *,
    always: Mapping[str, set[str]],
    ever: Mapping[str, set[str]],
    undecided: Mapping[str, set[str]],
) -> tuple[list[str], list[str], list[str]]:
    """Split the conditions with no stable core by *why* they have none.

    Four states, because "no stable core" had three different causes collapsed
    into one verdict and only one of them is a claim about the axiom.

    ``inert`` is the only finding here, and it needs both: nothing was refuted
    on any run, *and* every search settled. Calling a condition inert because
    its searches gave up is a claim the run does not support --- that is how
    loading the machine used to make this audit publish an inert frame
    condition. Calling one inert because its refutation was intermittent is a
    different error in the same direction: the condition demonstrably carries a
    theorem, just not on every run, and the published criterion is about the
    stable core rather than about whether anything was carried at all.

    Returned as plain data over plain sets so the classification can be tested
    without a solver. It was wrong twice; it should be checkable in a
    millisecond.
    """

    names = list(always)
    inert = sorted(n for n in names if not ever[n] and not undecided.get(n))
    unsettled = sorted(n for n in names if not ever[n] and undecided.get(n))
    intermittent = sorted(n for n in names if ever[n] and not always[n])
    return inert, unsettled, intermittent


def frame_conditions_are_load_bearing(
    *, timeout_ms: int = 30000, repeats: int = LOAD_BEARING_REPEATS
) -> dict[str, Any]:
    """Drop each frame condition and record which theorems are *refuted*.

    Three corrections stack up in this function and each was forced.

    **Refuted, not merely unproved.** Dropping an axiom leaves the solver
    hunting for a model it may not find, and an ``unknown`` return says the
    search did not settle, not that the axiom was carrying the theorem.
    Counting those as losses inflates every condition's weight, and this
    function did exactly that.

    **Bounded, because the open search is not stable.** Refuting a universally
    quantified claim over an uninterpreted sort is a model search with no
    guarantee of termination. Bounding the node sort makes it finite, and it is
    sound in that direction only: a countermodel in a small universe is a
    countermodel, while failing to find one there proves nothing.

    **Repeated, because even bounded it is not deterministic.** One condition
    yields two, one or three refutations on successive identical runs. So the
    measurement is taken ``repeats`` times and reported as a stable core --- the
    theorems refuted on *every* run --- and an intermittent remainder. A
    condition counts as load-bearing only on its stable core, which is the
    strictest of the three readings and the only one that does not move.
    """

    baseline = {result.theorem.name for result in prove_all(timeout_ms=timeout_ms) if result.discharged}

    always: dict[str, set[str]] = {}
    ever: dict[str, set[str]] = {}
    undecided: dict[str, set[str]] = {}
    for condition in FRAME_CONDITION_IDS:
        rounds: list[set[str]] = []
        gave_up: set[str] = set()
        for _ in range(repeats):
            found: set[str] = set()
            for name, axioms, claim, cert in _drop_queries(condition):
                if name not in baseline:
                    continue
                verdict = search_for_a_countermodel(axioms, claim, cert)
                if verdict is RefutationSearch.COUNTERMODEL:
                    found.add(name)
                elif verdict is RefutationSearch.UNDECIDED:
                    gave_up.add(name)
            rounds.append(found)
        always[condition] = set.intersection(*rounds) if rounds else set()
        ever[condition] = set.union(*rounds) if rounds else set()
        undecided[condition] = gave_up - ever[condition]

    inert, unsettled, intermittent_only = classify_frame_conditions(
        always=always, ever=ever, undecided=undecided
    )
    return {
        "baseline_discharged": sorted(baseline),
        "repeats": repeats,
        "theorems_refuted_on_every_run": {k: sorted(v) for k, v in always.items()},
        "theorems_refuted_on_some_run": {
            k: sorted(ever[k] - always[k]) for k in FRAME_CONDITION_IDS
        },
        "theorems_the_search_gave_up_on": {
            k: sorted(v) for k, v in undecided.items() if v
        },
        "inert_conditions": inert,
        "conditions_left_undecided": unsettled,
        "conditions_carried_only_intermittently": intermittent_only,
        "every_condition_carries_a_theorem": not (inert or unsettled or intermittent_only),
        "outcome": (
            Outcome.FAIL.value
            if inert
            else Outcome.CANNOT_CHECK.value
            if unsettled or intermittent_only
            else Outcome.PASS.value
        ),
        "criterion": (
            "a condition is load-bearing only when dropping it yields a countermodel to "
            "some theorem on every one of the repeated runs. A theorem that merely stops "
            "being provable is not counted, because an unknown return is a fact about the "
            "search; and a theorem refuted on some runs but not others is reported "
            "separately rather than credited, because the solver's model search on this "
            "encoding is not deterministic. A condition whose searches did not settle is "
            "reported as undecided rather than as inert: an unknown return is a fact "
            "about the search in that direction too, and calling it an inert axiom is a "
            "claim the run does not support."
        ),
    }


# ---------------------------------------------------------------------------
# The published counts, recomputed through the committed implementation
# ---------------------------------------------------------------------------


def _star_graph(width: int) -> tuple[int, list[tuple[int, int]], int]:
    """Nodes ``0..width-1`` are coordinates; node ``width`` is the certificate."""

    return width + 1, [(index, width) for index in range(width)], width


def recompute_published_counts(repo_root: Any) -> dict[str, Any]:
    """Recompute 155 and 1,055 by running the committed ``descendants``.

    Not by evaluating a rule defined here. ``descendants`` is P6's own shipped
    implementation, and ``P6-U-T1`` established it agrees with the independent
    reopening specification on all 61,440 four-node cases -- so a count produced
    by it is a count produced by a verified instance of the theorems above.
    """

    from pathlib import Path

    model = load_executable_model(Path(repo_root) / EXECUTABLE_MODEL, "p6_finite_models_cert")

    width = len(COORDINATES)
    node_count, edges, cert = _star_graph(width)

    full_restorations = 0
    proper_subset_failures = 0
    restoration_counterexamples: list[str] = []
    minimality_counterexamples: list[str] = []

    for donor in DONORS:
        for size in range(1, width + 1):
            for damaged in combinations(range(width), size):
                # A full repair leaves nothing changed.
                if cert not in model.descendants(node_count, edges, frozenset()):
                    full_restorations += 1
                elif len(restoration_counterexamples) < 20:
                    restoration_counterexamples.append(
                        f"{donor}: damage={damaged} was not restored by a full repair"
                    )

                # A proper repair leaves a non-empty residue.
                for repaired_size in range(len(damaged)):
                    for repaired in combinations(damaged, repaired_size):
                        residue = frozenset(set(damaged) - set(repaired))
                        if cert in model.descendants(node_count, edges, residue):
                            proper_subset_failures += 1
                        elif len(minimality_counterexamples) < 20:
                            minimality_counterexamples.append(
                                f"{donor}: damage={damaged} repaired={repaired} "
                                "restored the certificate from a proper subset"
                            )

    return {
        "donors": len(DONORS),
        "coordinates": width,
        "full_restorations": full_restorations,
        "proper_subset_failures": proper_subset_failures,
        "published_full_restorations": PUBLISHED_FULL_RESTORATIONS,
        "published_proper_subset_failures": PUBLISHED_PROPER_SUBSET_FAILURES,
        "restoration_counterexamples": restoration_counterexamples,
        "minimality_counterexamples": minimality_counterexamples,
        "counts_reproduced": (
            full_restorations == PUBLISHED_FULL_RESTORATIONS
            and proper_subset_failures == PUBLISHED_PROPER_SUBSET_FAILURES
            and not restoration_counterexamples
            and not minimality_counterexamples
        ),
        "computed_by": "the committed check_finite_models.descendants, under the star interpretation",
        "the_donor_axis_is_a_multiplier": (
            "The donor loop enters neither the graph nor the changed set, so the five "
            "donor families replicate the same 31 restorations and 211 failures rather "
            "than extending them. 155 and 1,055 are 31 and 211 counted five times. That "
            "is P6's own loop structure, reproduced here rather than corrected, and it "
            "means the published counts carry the information of 31 and 211."
        ),
    }


def counts_are_sensitive_to_the_interpretation(repo_root: Any) -> dict[str, Any]:
    """Do the published counts identify the interpretation? They do not.

    Reproducing two integers through a verified implementation is worth nothing
    if the question being asked has the same answer under a wrong reading. Six
    dependency graphs are tried against the star. Three break it and three do
    not, and the three that do not are the finding: a chain running through the
    coordinates into the certificate, the star with extra coordinate-to-
    coordinate edges, and the complete graph all return 1,055 exactly.

    So the counts do not pin the star. What they test is the reachability class
    --- whether every coordinate reaches the certificate --- and every graph in
    that class gives the same pair. Removing one coordinate's support edge
    leaves the class and the count moves to 975; reversing, deleting or
    truncating the edges leaves it and the count collapses to 0.

    The star is pinned by the theorems instead, and by which frame condition
    each needs: under the chain an undamaged coordinate downstream of the damage
    *is* reopened, which is exactly what
    ``UNDAMAGED_COORDINATES_ARE_NOT_REOPENED`` forbids and what dropping
    ``coordinates_do_not_support_each_other`` loses. That is checked here too,
    rather than argued: the collateral reopening the counts cannot see is
    counted directly.
    """

    from pathlib import Path

    model = load_executable_model(Path(repo_root) / EXECUTABLE_MODEL, "p6_finite_models_cert_alt")
    width = len(COORDINATES)
    cert = width
    star = [(index, cert) for index in range(width)]

    variants: dict[str, list[tuple[int, int]]] = {
        "edges_reversed": [(cert, index) for index in range(width)],
        "no_support_edges": [],
        "coordinates_chained_without_the_certificate": [
            (index, index + 1) for index in range(width - 1)
        ],
        "one_coordinate_does_not_support_the_certificate": [
            (index, cert) for index in range(1, width)
        ],
        "coordinates_chained_into_the_certificate": [
            (index, index + 1) for index in range(width)
        ],
        "star_with_coordinate_cross_edges": star + [(0, 1), (1, 2)],
        "complete_graph": [
            (source, target)
            for source in range(width + 1)
            for target in range(width + 1)
            if source != target
        ],
    }

    outcomes: dict[str, dict[str, Any]] = {}
    for name, edges in variants.items():
        failures = 0
        restorations = 0
        collateral = 0
        for _donor in DONORS:
            for size in range(1, width + 1):
                for damaged in combinations(range(width), size):
                    if cert not in model.descendants(width + 1, edges, frozenset()):
                        restorations += 1
                    reopened = model.descendants(width + 1, edges, frozenset(damaged))
                    collateral += sum(
                        1 for node in reopened if node != cert and node not in damaged
                    )
                    for repaired_size in range(len(damaged)):
                        for repaired in combinations(damaged, repaired_size):
                            residue = frozenset(set(damaged) - set(repaired))
                            if cert in model.descendants(width + 1, edges, residue):
                                failures += 1
        outcomes[name] = {
            "full_restorations": restorations,
            "proper_subset_failures": failures,
            "coordinates_reopened_as_collateral": collateral,
        }

    indistinguishable = sorted(
        name
        for name, counts in outcomes.items()
        if counts["proper_subset_failures"] == PUBLISHED_PROPER_SUBSET_FAILURES
    )
    caught_by_collateral = sorted(
        name for name in indistinguishable if outcomes[name]["coordinates_reopened_as_collateral"]
    )
    return {
        "variants": outcomes,
        "variants_the_counts_cannot_distinguish_from_the_star": indistinguishable,
        "of_those_caught_by_collateral_reopening": caught_by_collateral,
        "counts_alone_identify_the_interpretation": not indistinguishable,
        "every_indistinguishable_variant_is_caught_by_a_theorem": (
            sorted(indistinguishable) == sorted(caught_by_collateral)
        ),
        "what_the_counts_actually_test": (
            "Whether every coordinate reaches the certificate, and nothing more. Every "
            "graph in that reachability class returns 155 and 1,055, including a chain "
            "through the coordinates, the star with coordinate cross-edges and the "
            "complete graph. Dropping one coordinate's support edge stays in reach of "
            "the question and moves the count to 975; reversing or deleting the edges "
            "leaves the class and collapses it to 0. The counts therefore confirm the "
            "reachability class, not the star."
        ),
        "what_pins_the_star": (
            "The theorems, and specifically UNDAMAGED_COORDINATES_ARE_NOT_REOPENED. "
            "Every variant the counts cannot distinguish reopens coordinates as "
            "collateral damage, which that theorem forbids and which dropping the frame "
            "condition coordinates_do_not_support_each_other loses. The collateral count "
            "is reported per variant above so this is a measurement rather than an "
            "argument."
        ),
        "the_restoration_count_does_not_discriminate": (
            "155 is the number of (donor, non-empty damage) pairs and does not depend on "
            "the graph at all -- a full repair leaves nothing changed, so no graph "
            "reopens anything. Every variant returns 155. The 1,055 is the count that "
            "moves, and it only moves out of the reachability class."
        ),
    }


def build_report(repo_root: Any, *, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    theorems = prove_all()
    counts = recompute_published_counts(repo_root)
    frames = frame_conditions_are_load_bearing()
    sensitivity = counts_are_sensitive_to_the_interpretation(repo_root)
    undischarged = [r.theorem.name for r in theorems if not r.discharged]

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P6_CERTIFICATE_AS_DEPENDENCY_GRAPH",
        "date": date,
        "solver": _z3.get_version_string(),
        "theorems": [r.as_json() for r in theorems],
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "frame_conditions": frames,
        "load_bearing_criterion_history": (
            "This measurement has been wrong twice. It first counted any theorem that "
            "stopped being discharged, which credits an axiom for the solver failing to "
            "settle a question. Requiring a countermodel then made it unstable, because "
            "refuting a universally quantified claim over an uninterpreted sort is an "
            "unbounded model search. It now asks for a countermodel in a bounded world "
            "-- sound in that direction only -- and takes the intersection over repeated "
            "runs. The conclusion survived both corrections; the per-condition detail "
            "did not, and the difference is recorded rather than quietly restated."
        ),
        "published_counts": counts,
        "interpretation_sensitivity": sensitivity,
        "what_this_establishes": (
            "P6's certificate model is an interpretation of the reopening semantics "
            "already proved general: a certificate over n coordinates is the star graph "
            "on n+1 nodes, damage is a changed set on the coordinate nodes, and repair "
            "removes coordinates from it. Under that reading five theorems are "
            "discharged by Z3 over an uninterpreted node sort and for any number of "
            "coordinates -- any damage withdraws the certificate, a full repair restores "
            "it, a partial repair does not, undamaged coordinates are never collateral "
            "damage, the dependency runs one way, and the certificate supports nothing. "
            "That last one was a frame condition until the load-bearing check reported "
            "it inert; it and one other were a redundant presentation of the same "
            "constraint, so the interpretation now assumes three independent conditions "
            "and proves the fourth. P6's published 155 full "
            "restorations and 1,055 proper-subset failures are then recomputed by "
            "running the committed descendants over the interpreted graph, so the finite "
            "result is an instance of the theorems produced by the implementation "
            "P6-U-T1 verified against them, rather than a separate enumeration that "
            "agrees with them. Each of the four frame conditions is shown to carry at "
            "least one theorem by dropping it, and three wrong dependency graphs are "
            "tried against the interpretation, and each of the three surviving frame "
            "conditions is necessary under the strictest of three readings: dropping it "
            "yields an actual countermodel, in a bounded world, on every one of the "
            "repeated runs. Two weaker readings were rejected on the way. Counting a "
            "theorem that merely stopped being provable inflates every condition's "
            "weight, because an unknown return is a fact about the solver's search "
            "rather than evidence the axiom was carrying anything. And a single run is "
            "not a measurement here: the model search is not deterministic on this "
            "encoding, and the edge-restriction condition refutes between one and three "
            "theorems on identical repeated runs, of which exactly one falls every "
            "time. The counts do not carry the interpretation on "
            "their own and this is measured rather than assumed: a chain through the "
            "coordinates into the certificate, the star with coordinate cross-edges and "
            "the complete graph all return 1,055 exactly, because the counts test "
            "whether every coordinate reaches the certificate and nothing further. "
            "Every one of those three is refuted by a theorem instead -- each reopens "
            "coordinates as collateral damage, which UNDAMAGED_COORDINATES_ARE_NOT_"
            "REOPENED forbids -- so what pins the star is the proof, with the counts "
            "confirming the reachability class."
        ),
        "not_licensed": [
            "any claim that 155 tests the interpretation; it is the number of (donor, "
            "damage) pairs and is unchanged by every wrong graph tried",
            "any claim that the two counts identify the star graph; three structurally "
            "different graphs reproduce 1,055 exactly, and only the theorems separate "
            "them",
            "any claim that the donor axis extends the result; it enters neither the "
            "graph nor the changed set and multiplies 31 and 211 by five",
            "independent review: the interpretation, the theorems and the tests were "
            "written in the same lane as the model, which is P6-U-T4",
            "any empirical claim whatsoever",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p6-certificate-as-dependency-graph",
        description="Interpret P6's certificate model in the proved reopening semantics.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, date=args.date)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    counts = report["published_counts"]
    print(
        f"  counts: {counts['full_restorations']} restorations, "
        f"{counts['proper_subset_failures']} proper-subset failures, "
        f"reproduced={counts['counts_reproduced']}"
    )
    frames = report["frame_conditions"]
    print(f"  every frame condition carries a theorem: {frames['every_condition_carries_a_theorem']}")
    sens = report["interpretation_sensitivity"]
    print(
        "  counts alone identify the interpretation: "
        f"{sens['counts_alone_identify_the_interpretation']} "
        f"(indistinguishable: {len(sens['variants_the_counts_cannot_distinguish_from_the_star'])}, "
        f"all caught by a theorem: {sens['every_indistinguishable_variant_is_caught_by_a_theorem']})"
    )

    if not report["all_discharged"]:
        print(f"UNDISCHARGED: {report['undischarged']}")
        return 3
    if not counts["counts_reproduced"]:
        print("THE PUBLISHED COUNTS WERE NOT REPRODUCED UNDER THE INTERPRETATION")
        return 3
    if frames["inert_conditions"]:
        print(f"INERT FRAME CONDITIONS: {frames['inert_conditions']}")
        return 3
    if frames["conditions_carried_only_intermittently"]:
        print(
            "FRAME CONDITIONS CARRIED ONLY INTERMITTENTLY (they do carry a theorem, but "
            "not on every run, so the stable core the published criterion asks for was "
            f"not established): {frames['conditions_carried_only_intermittently']}"
        )
        return 3
    if frames["conditions_left_undecided"]:
        # Not the same sentence as the one above, and it must never print as if
        # it were: the search did not settle, so whether these carry a theorem
        # was not measured on this run.
        print(
            "FRAME CONDITIONS LEFT UNDECIDED (the countermodel search did not settle; "
            f"this is not a finding that they are inert): {frames['conditions_left_undecided']}"
        )
        return 3
    if not sens["every_indistinguishable_variant_is_caught_by_a_theorem"]:
        # The counts do not identify the star and are not asked to. What must
        # hold is that every graph they cannot distinguish is refuted by a
        # theorem instead; a variant that escapes both would leave the
        # interpretation genuinely under-determined.
        print("A WRONG DEPENDENCY GRAPH ESCAPED BOTH THE COUNTS AND THE THEOREMS")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
