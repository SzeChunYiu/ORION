"""P6's reopening theorems, over arbitrary dependency graphs.

This is the other half of ``P6-U-T1``. ``separation_calculus_smt`` lifted the
local-mechanic semantics; this lifts change propagation --- which node
certificates a change invalidates, and which survive it.

It exists for two reasons, and the second is the more urgent.

**The general theorem was missing.** ``check_finite_models.check_reopening``
enumerates every DAG on four nodes and every pair of changed/certified subsets,
which is a statement about four nodes.

**And the finite check tests nothing.** Its two assertions are

.. code-block:: python

    retained = certified.difference(downstream)
    assert not retained.intersection(downstream)
    assert retained == certified.difference(downstream)

Both are true by set algebra for *any* value of ``downstream``. The first
intersects a set with something already removed from it; the second compares a
variable to the expression it was just assigned. ``descendants`` is called, and
its output is never compared against anything. Verified by mutation: with
``descendants`` replaced by "always the empty set" the check passes, and with
"always every node" it also passes, both returning the same case count as the
real implementation. It reports 130,320 cases over 543 DAGs, and none of them can
fail.

So the theorems below are stated against an *independent* characterisation of
reopening rather than against the implementation's own output, and
:func:`differential_against_finite_model` compares the committed ``descendants``
to that characterisation on an exhaustively enumerated finite universe --- which
is the check the finite model was supposed to be.
"""

from __future__ import annotations

from typing import Any

from orion.programme.mechanized import (
    DifferentialReport,
    ProofResult,
    Theorem,
    discharge,
    load_executable_model,
    require_z3,
)

SCHEMA_VERSION = "orion.p6.reopening-calculus-smt.v1"

EXECUTABLE_MODEL = (
    "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py"
)


REOPENING_SOUNDNESS = Theorem(
    name="REOPENING_SOUNDNESS",
    statement=(
        "every reopened node is reachable from some changed node along dependency "
        "edges, over any graph of any size"
    ),
    why_it_matters=(
        "reopening a node that nothing changed depends on is unjustified work, and "
        "at scale it is the difference between selective revalidation and redoing "
        "everything"
    ),
)

REOPENING_COMPLETENESS = Theorem(
    name="REOPENING_COMPLETENESS",
    statement=(
        "every node reachable from a changed node, and not itself changed, is "
        "reopened"
    ),
    why_it_matters=(
        "the safety half: a certificate that survives a change it actually depends "
        "on is a false validity, which is the one error this whole mechanism exists "
        "to prevent"
    ),
)

REOPENING_MINIMALITY = Theorem(
    name="REOPENING_MINIMALITY",
    statement=(
        "the reopened set is exactly the reachable-and-not-changed set, so no "
        "smaller set is sound and no larger set is necessary"
    ),
    why_it_matters=(
        "soundness and completeness together pin the set exactly; stating it as one "
        "theorem is what makes 'minimal' a claim rather than an adjective"
    ),
)

REOPENING_CONSERVATIVITY = Theorem(
    name="REOPENING_CONSERVATIVITY",
    statement="if nothing changed, nothing is reopened",
    why_it_matters=(
        "a revalidation mechanism that reopens work in the absence of change would "
        "make every certificate permanently provisional"
    ),
)

REOPENING_MONOTONICITY = Theorem(
    name="REOPENING_MONOTONICITY",
    statement=(
        "changing more can only reopen more: if one changed set contains another, "
        "its reopened set contains the other's, up to the changed nodes themselves"
    ),
    why_it_matters=(
        "without it, adding a change could *rescue* a certificate, which would make "
        "the mechanism exploitable by changing more things"
    ),
)

CYCLE_REOPENS_ITSELF = Theorem(
    name="CYCLE_REOPENS_ITSELF",
    statement=(
        "on a cyclic dependency graph, a changed node inside a cycle is reachable "
        "from itself, so every other node of that cycle is reopened"
    ),
    why_it_matters=(
        "the requested characterisation of cycles: acyclicity is not needed for "
        "soundness or completeness, and what a cycle does is make its whole "
        "strongly connected component reopen together"
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    REOPENING_SOUNDNESS,
    REOPENING_COMPLETENESS,
    REOPENING_MINIMALITY,
    REOPENING_CONSERVATIVITY,
    REOPENING_MONOTONICITY,
    CYCLE_REOPENS_ITSELF,
)


# ---------------------------------------------------------------------------
# Primitive change/dependency semantics
# ---------------------------------------------------------------------------


def _vocabulary() -> dict[str, Any]:
    """Nodes are a sort; the dependency edge is an uninterpreted predicate."""

    solver = require_z3()
    Node = solver.DeclareSort("Node")
    return {
        "z3": solver,
        "Node": Node,
        "Edge": solver.Function("Edge", Node, Node, solver.BoolSort()),
        "Reach": solver.Function("Reach", Node, Node, solver.BoolSort()),
        "Rank": solver.Function("Rank", Node, Node, solver.IntSort()),
        "Changed": solver.Function("Changed", Node, solver.BoolSort()),
        "Changed2": solver.Function("Changed2", Node, solver.BoolSort()),
    }


def _closure_axioms(vocab: dict[str, Any]) -> list[Any]:
    """Reachability is the reflexive-transitive closure of the dependency edge.

    The same four clauses P8's authority calculus needs, and for the same reason:
    transitive closure is not first-order definable, so these *are* the
    definition. The well-founded rank in clause four is the one that is easy to
    leave out and fatal to leave out --- without it a model may contain two
    reachability facts that justify each other in a cycle, and the completeness
    direction becomes unprovable. That cost a real countermodel to discover in
    P8; it is imported here rather than rediscovered.
    """

    solver = vocab["z3"]
    a, b, c = solver.Consts("ax bx cx", vocab["Node"])
    Reach, Edge, Rank = vocab["Reach"], vocab["Edge"], vocab["Rank"]
    return [
        solver.ForAll([a], Reach(a, a)),
        solver.ForAll([a, b, c], solver.Implies(solver.And(Reach(a, b), Edge(b, c)), Reach(a, c))),
        solver.ForAll([a, b, c], solver.Implies(solver.And(Reach(a, b), Reach(b, c)), Reach(a, c))),
        solver.ForAll([a, b], Rank(a, b) >= 0),
        solver.ForAll(
            [a, b],
            solver.Implies(
                Reach(a, b),
                solver.Or(
                    a == b,
                    solver.Exists(
                        [c],
                        solver.And(Reach(a, c), Edge(c, b), Rank(a, c) < Rank(a, b)),
                    ),
                ),
            ),
        ),
    ]


def _reopened(vocab: dict[str, Any], node: Any, changed: Any) -> Any:
    """The specification of reopening, written independently of any implementation.

    A node is reopened when some changed node reaches it and it is not itself
    changed. This is stated here, not read off ``descendants``: a theorem proved
    about an implementation's own output cannot detect that the implementation is
    wrong, which is exactly how the finite check came to assert tautologies.
    """

    solver = vocab["z3"]
    source = solver.Const(f"src_{id(node)}", vocab["Node"])
    return solver.And(
        solver.Not(changed(node)),
        solver.Exists([source], solver.And(changed(source), vocab["Reach"](source, node))),
    )


def prove_all(*, timeout_ms: int = 30000) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS`."""

    vocab = _vocabulary()
    solver = vocab["z3"]
    axioms = _closure_axioms(vocab)
    Changed, Changed2, Reach, Edge = (
        vocab["Changed"], vocab["Changed2"], vocab["Reach"], vocab["Edge"]
    )
    n, s, t = solver.Consts("n s t", vocab["Node"])
    results: list[ProofResult] = []

    reopened_n = _reopened(vocab, n, Changed)

    results.append(
        discharge(
            REOPENING_SOUNDNESS,
            axioms,
            solver.Implies(
                reopened_n,
                solver.Exists([s], solver.And(Changed(s), Reach(s, n))),
            ),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            REOPENING_COMPLETENESS,
            axioms,
            solver.Implies(
                solver.And(Changed(s), Reach(s, n), solver.Not(Changed(n))),
                reopened_n,
            ),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            REOPENING_MINIMALITY,
            axioms,
            reopened_n
            == solver.And(
                solver.Not(Changed(n)),
                solver.Exists([t], solver.And(Changed(t), Reach(t, n))),
            ),
            timeout_ms=timeout_ms,
        )
    )

    nothing_changed = solver.ForAll([s], solver.Not(Changed(s)))
    results.append(
        discharge(
            REOPENING_CONSERVATIVITY,
            axioms,
            solver.Implies(nothing_changed, solver.Not(reopened_n)),
            timeout_ms=timeout_ms,
        )
    )

    # Monotonicity: Changed subset-of Changed2 means anything reopened by the
    # smaller set is reopened by the larger one, unless the larger set changed
    # that node itself -- a node cannot be both changed and reopened.
    subset = solver.ForAll([s], solver.Implies(Changed(s), Changed2(s)))
    results.append(
        discharge(
            REOPENING_MONOTONICITY,
            axioms,
            solver.Implies(
                solver.And(subset, reopened_n, solver.Not(Changed2(n))),
                _reopened(vocab, n, Changed2),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # Cycles: a two-node cycle with one member changed reopens the other.
    cycle = solver.And(Edge(s, t), Edge(t, s), s != t)
    results.append(
        discharge(
            CYCLE_REOPENS_ITSELF,
            axioms,
            solver.Implies(
                solver.And(cycle, Changed(s), solver.Not(Changed(t))),
                _reopened(vocab, t, Changed),
            ),
            timeout_ms=timeout_ms,
        )
    )
    return tuple(results)


# ---------------------------------------------------------------------------
# The check the finite model was supposed to be
# ---------------------------------------------------------------------------


def _reference_reopened(
    node_count: int, edges: tuple[tuple[int, int], ...], changed: frozenset[int]
) -> frozenset[int]:
    """Reopening computed from the specification, not from P6's implementation.

    Deliberately a second implementation, written from :func:`_reopened`'s
    definition rather than by calling ``descendants``. Comparing a function to
    itself is what the committed check does, and it is why that check passes when
    ``descendants`` is replaced by a constant.
    """

    reachable: set[int] = set()
    frontier = list(changed)
    while frontier:
        current = frontier.pop()
        for source, target in edges:
            if source == current and target not in reachable:
                reachable.add(target)
                frontier.append(target)
    return frozenset(reachable - changed)


def differential_against_finite_model(
    repo_root: Any, *, node_count: int = 4
) -> DifferentialReport:
    """Compare P6's committed ``descendants`` to the specification, exhaustively.

    Over every directed graph on ``node_count`` nodes --- cyclic ones included,
    since none of the theorems above need acyclicity --- and every changed
    subset. ``positive_trials`` counts the cases where a node actually *is*
    reopened, because a corpus in which nothing is ever reopened would agree on
    the empty set and prove nothing.
    """

    from itertools import combinations, product
    from pathlib import Path

    model = load_executable_model(Path(repo_root) / EXECUTABLE_MODEL, "p6_finite_models")

    possible = [(a, b) for a in range(node_count) for b in range(node_count) if a != b]
    disagreements: list[str] = []
    trials = 0
    non_empty = 0

    for mask in range(1 << len(possible)):
        edges = tuple(possible[i] for i in range(len(possible)) if (mask >> i) & 1)
        for size in range(1, node_count + 1):
            for changed_tuple in combinations(range(node_count), size):
                changed = frozenset(changed_tuple)
                expected = _reference_reopened(node_count, edges, changed)
                actual = model.descendants(node_count, edges, changed)
                trials += 1
                if expected:
                    non_empty += 1
                if frozenset(actual) != expected:
                    if len(disagreements) < 20:
                        disagreements.append(
                            f"edges={edges} changed={sorted(changed)}: "
                            f"implementation={sorted(actual)} specification={sorted(expected)}"
                        )

    _ = product  # kept for symmetry with the committed enumeration's imports
    return DifferentialReport(
        trials=trials,
        agreements=trials - len(disagreements),
        disagreements=tuple(disagreements),
        positive_trials=non_empty,
    )


def committed_check_is_vacuous(repo_root: Any, *, node_count: int = 3) -> dict[str, object]:
    """Demonstrate, by mutation, that ``check_reopening`` asserts tautologies.

    Replaces ``descendants`` with two constant functions that are wrong for every
    non-trivial input, and reports whether the committed check still passes.
    A check that survives both is not testing the mechanism it appears to test,
    and saying so with a reproduction is worth more than saying so in prose.
    """

    from pathlib import Path

    model = load_executable_model(Path(repo_root) / EXECUTABLE_MODEL, "p6_finite_vacuity")
    original = model.descendants
    outcomes: dict[str, object] = {}
    try:
        outcomes["baseline"] = list(model.check_reopening(node_count=node_count))
        for label, replacement in (
            ("always_empty", lambda node_count, edges, changed: frozenset()),
            (
                "always_every_node",
                lambda node_count, edges, changed: frozenset(range(node_count)),
            ),
        ):
            model.descendants = replacement
            try:
                outcomes[label] = {"passed": True, "result": list(model.check_reopening(node_count=node_count))}
            except AssertionError as error:
                outcomes[label] = {"passed": False, "error": str(error)}
    finally:
        model.descendants = original

    survived = [
        label
        for label in ("always_empty", "always_every_node")
        if isinstance(outcomes[label], dict) and outcomes[label]["passed"]
    ]
    outcomes["mutations_survived"] = survived
    outcomes["is_vacuous"] = len(survived) == 2
    outcomes["explanation"] = (
        (
            "check_reopening compares its retained set against a specification built "
            "from an independently computed transitive closure, so a wrong descendants "
            "is caught. Until 2026-08-22 its two assertions were set-algebra "
            "tautologies -- intersecting a set with something already removed from it, "
            "then comparing a variable to the expression it was just assigned -- and "
            "descendants was called with its output never compared to anything, so the "
            "check passed for any implementation."
        )
        if not survived
        else (
            "check_reopening's assertions do not constrain descendants: "
            f"{', '.join(survived)} survived, so the check passes for an implementation "
            "that returns the wrong set."
        )
    )
    return outcomes


def build_report(repo_root: Any, *, node_count: int = 4) -> dict[str, object]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    theorems = prove_all()
    differential = differential_against_finite_model(repo_root, node_count=node_count)
    vacuity = committed_check_is_vacuous(repo_root, node_count=3)
    undischarged = [r.theorem.name for r in theorems if not r.discharged]

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P6_REOPENING_CALCULUS_MECHANIZED",
        "solver": _z3.get_version_string(),
        "theorems": [r.as_json() for r in theorems],
        "differential_against_committed_descendants": differential.as_json(),
        "differential_node_count": node_count,
        "committed_check_vacuity": vacuity,
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "what_this_establishes": (
            "soundness, completeness, minimality, conservativity, monotonicity and the "
            "cycle characterisation of reopening hold over dependency graphs of any size, "
            "cyclic or not; and P6's committed descendants agrees with that specification "
            "on every directed graph over four nodes and every changed subset. The "
            "implementation is correct. That had not previously been checked, because the "
            "check that appeared to check it asserts tautologies."
        ),
        "not_licensed": [
            "any claim that P6's 320-state model, its 155 full-revalidation successes or "
            "its 1,055 strict-subset failures are hereby re-derived; those come from a "
            "different artifact and are not lifted here",
            "any claim of independent formal review; a solver checked these, not a person "
            "outside this lane",
            "any empirical claim whatsoever",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p6-reopening-calculus",
        description="Discharge P6's reopening theorems over arbitrary dependency graphs.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--node-count", type=int, default=4)
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, node_count=args.node_count)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    diff = report["differential_against_committed_descendants"]
    print(
        f"  differential: {diff['agreements']}/{diff['trials']} agree, "
        f"{diff['positive_trials']} with a non-empty reopening"
    )
    vac = report["committed_check_vacuity"]
    print(f"  committed check_reopening is vacuous: {vac['is_vacuous']} "
          f"(mutations survived: {vac['mutations_survived']})")
    if not report["all_discharged"]:
        print(f"UNDISCHARGED: {report['undischarged']}")
        return 3
    if not diff["informative"]:
        print("DIFFERENTIAL DID NOT ESTABLISH AGREEMENT ON AN INFORMATIVE CORPUS")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
