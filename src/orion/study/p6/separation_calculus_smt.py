"""P6's separation and reopening theorems, over arbitrary state spaces.

P6's formal core is a bounded model check. ``check_finite_models`` establishes
separated commutation by enumerating four coordinates, binary values and one
concrete transformer --- ``(write + sum(reads) + 1) mod 2`` --- and asserting
equality on every combination. It establishes reopening by enumerating the
subsets of a four-node DAG. Both are true statements about four coordinates.
``P6-U-T1`` asks for something else:

    Define primitive evidence/dependency/change semantics independently of the
    desired theorem, then prove soundness, minimality and conservativity from
    them.

The generalisation here moves on two axes at once, and the second is the one
that matters. Coordinates and values become **uninterpreted sorts**, so the
theorems hold for any number of coordinates over any value domain. And the local
mechanic becomes an **uninterpreted function** constrained only by a frame
condition --- it may read the coordinates it declares and no others --- so the
theorems hold for *every* local transformer rather than for the one the finite
check happened to instantiate. A commutation result proved only for
``(write + sum(reads) + 1) mod 2`` could be a property of modular arithmetic;
proved against an arbitrary function, it can only be a property of separation.

That framing also makes the sharp entailment boundary statable.  Read/write
noninterference is sufficient for every frame-faithful transformer.  If either
cross-read exclusion is removed, commutation is no longer entailed: some
frame-faithful transformer and state disagree.  This is not a claim that two
particular interfering mechanics can never happen to commute.
"""

from __future__ import annotations

from typing import Any

from orion.programme.mechanized import (
    DifferentialReport,
    ProofResult,
    Theorem,
    discharge,
    require_z3,
)

SCHEMA_VERSION = "orion.p6.separation-calculus-smt.v1"
COMMUTATION_CONTRACT_ID = "P6.COMMUTE.RW_NONINTERFERENCE.V1"

EXECUTABLE_MODEL = (
    "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py"
)


SEPARATED_COMMUTATION = Theorem(
    name="SEPARATED_COMMUTATION",
    statement=(
        f"{COMMUTATION_CONTRACT_ID}: two local mechanics with distinct write "
        "coordinates, neither reading what "
        "the other writes, commute on any state over any value domain, for every "
        "transformer obeying its declared frame"
    ),
    why_it_matters=(
        "the finite core checks this for four binary coordinates and one modular "
        "transformer; against an arbitrary transformer the result can only be a "
        "property of separation rather than of the arithmetic that instantiated it"
    ),
)

SEPARATION_IS_NECESSARY = Theorem(
    name="SEPARATION_IS_NECESSARY",
    statement=(
        "if one mechanic reads the coordinate the other writes, commutation is not "
        "entailed: there is a state and a pair of frame-respecting transformers "
        "whose two orders disagree"
    ),
    why_it_matters=(
        "states the converse at the level of universal entailment: without either "
        "cross-read exclusion, a countermodel exists; it does not say that every "
        "specific pair of interfering mechanics must fail to commute"
    ),
)

WRITE_LOCALITY = Theorem(
    name="WRITE_LOCALITY",
    statement="a local mechanic changes its own write coordinate and no other",
    why_it_matters=(
        "the soundness half: a mechanic declared local must actually be local, or "
        "every separation argument built on the declaration is void"
    ),
)

FRAME_DETERMINACY = Theorem(
    name="FRAME_DETERMINACY",
    statement=(
        "two states agreeing on a mechanic's declared frame produce the same "
        "written value, so nothing outside the frame can influence the result"
    ),
    why_it_matters=(
        "the minimality half: the declared read set is the whole dependency, which "
        "is what makes a dependency graph a description of the computation rather "
        "than a comment on it"
    ),
)

IDEMPOTENT_ON_FIXPOINT = Theorem(
    name="IDEMPOTENT_ON_FIXPOINT",
    statement="a mechanic that leaves its state unchanged leaves it unchanged when reapplied",
    why_it_matters=(
        "the conservativity half: reapplying a settled mechanic cannot manufacture "
        "a change, so a fixpoint is a real stopping condition"
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    SEPARATED_COMMUTATION,
    SEPARATION_IS_NECESSARY,
    WRITE_LOCALITY,
    FRAME_DETERMINACY,
    IDEMPOTENT_ON_FIXPOINT,
)


def _vocabulary() -> dict[str, Any]:
    """Coordinates and values are sorts; mechanics are uninterpreted functions."""

    solver = require_z3()
    Coord = solver.DeclareSort("Coord")
    Value = solver.DeclareSort("Value")
    State = solver.ArraySort(Coord, Value)
    return {
        "z3": solver,
        "Coord": Coord,
        "Value": Value,
        "State": State,
        # Read sets, as predicates over coordinates rather than finite lists.
        "ReadsL": solver.Function("ReadsL", Coord, solver.BoolSort()),
        "ReadsR": solver.Function("ReadsR", Coord, solver.BoolSort()),
        # The transformers. Each maps a whole state to the value it writes; the
        # frame axiom is what restricts it to its declared reads.
        "FL": solver.Function("FL", State, Value),
        "FR": solver.Function("FR", State, Value),
        "wl": solver.Const("wl", Coord),
        "wr": solver.Const("wr", Coord),
    }


def _frame_axioms(vocab: dict[str, Any]) -> list[Any]:
    """A transformer sees its declared frame and nothing else.

    Stated as: any two states agreeing on the write coordinate and on every
    declared read produce the same written value. This is the primitive
    ``dependency`` semantics --- it defines what it means for a mechanic to
    depend on a coordinate, without reference to any theorem proved later.
    """

    solver = vocab["z3"]
    s, t = solver.Consts("frame_s frame_t", vocab["State"])
    i = solver.Const("frame_i", vocab["Coord"])
    agree_left = solver.ForAll(
        [i],
        solver.Implies(
            solver.Or(vocab["ReadsL"](i), i == vocab["wl"]),
            solver.Select(s, i) == solver.Select(t, i),
        ),
    )
    agree_right = solver.ForAll(
        [i],
        solver.Implies(
            solver.Or(vocab["ReadsR"](i), i == vocab["wr"]),
            solver.Select(s, i) == solver.Select(t, i),
        ),
    )
    return [
        solver.ForAll([s, t], solver.Implies(agree_left, vocab["FL"](s) == vocab["FL"](t))),
        solver.ForAll([s, t], solver.Implies(agree_right, vocab["FR"](s) == vocab["FR"](t))),
    ]


def prove_all(*, timeout_ms: int = 30000) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS`."""

    vocab = _vocabulary()
    solver = vocab["z3"]
    frame = _frame_axioms(vocab)
    state = solver.Const("state", vocab["State"])
    wl, wr = vocab["wl"], vocab["wr"]

    def apply_left(s: Any) -> Any:
        return solver.Store(s, wl, vocab["FL"](s))

    def apply_right(s: Any) -> Any:
        return solver.Store(s, wr, vocab["FR"](s))

    separated = solver.And(
        wl != wr,
        solver.Not(vocab["ReadsL"](wr)),
        solver.Not(vocab["ReadsR"](wl)),
    )

    results: list[ProofResult] = []
    results.append(
        discharge(
            SEPARATED_COMMUTATION,
            frame,
            solver.Implies(
                separated,
                apply_right(apply_left(state)) == apply_left(apply_right(state)),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # The converse, as a satisfiability question rather than a validity one: the
    # claim is that a disagreeing model *exists*, so it is discharged by finding
    # one, not by refuting a negation.
    results.append(_prove_necessity(timeout_ms=timeout_ms))

    other = solver.Const("other", vocab["Coord"])
    results.append(
        discharge(
            WRITE_LOCALITY,
            frame,
            solver.Implies(
                other != wl,
                solver.Select(apply_left(state), other) == solver.Select(state, other),
            ),
            timeout_ms=timeout_ms,
        )
    )

    s2 = solver.Const("state2", vocab["State"])
    i = solver.Const("loc_i", vocab["Coord"])
    agree_on_frame = solver.ForAll(
        [i],
        solver.Implies(
            solver.Or(vocab["ReadsL"](i), i == wl),
            solver.Select(state, i) == solver.Select(s2, i),
        ),
    )
    results.append(
        discharge(
            FRAME_DETERMINACY,
            frame,
            solver.Implies(agree_on_frame, vocab["FL"](state) == vocab["FL"](s2)),
            timeout_ms=timeout_ms,
        )
    )

    results.append(
        discharge(
            IDEMPOTENT_ON_FIXPOINT,
            frame,
            solver.Implies(
                apply_left(state) == state,
                apply_left(apply_left(state)) == state,
            ),
            timeout_ms=timeout_ms,
        )
    )
    return tuple(results)


def _prove_necessity(*, timeout_ms: int) -> ProofResult:
    """Exhibit symmetric cross-read countermodels with disjoint writes.

    Discharged by satisfiability: the theorem asserts that a disagreeing model
    exists for each omitted cross-read exclusion, so models are the proof and
    ``unsat`` would refute it.  The mechanics below are explicit deterministic
    array updates.  Each writes only its own coordinate and reads only its
    declared coordinate; the sole violated premise is named by the case.
    """

    solver = require_z3()
    State = solver.ArraySort(solver.IntSort(), solver.IntSort())

    def left_reads_right() -> Any:
        state = solver.Const("left_reads_right_state", State)
        left = lambda s: solver.Store(s, 0, solver.Select(s, 1))
        right = lambda s: solver.Store(s, 1, solver.Select(s, 1) + 1)
        return right(left(state)) != left(right(state))

    def right_reads_left() -> Any:
        state = solver.Const("right_reads_left_state", State)
        left = lambda s: solver.Store(s, 0, solver.Select(s, 0) + 1)
        right = lambda s: solver.Store(s, 1, solver.Select(s, 0))
        return right(left(state)) != left(right(state))

    verdicts = []
    for witness in (left_reads_right(), right_reads_left()):
        checker = solver.Solver()
        checker.set("timeout", timeout_ms)
        checker.add(witness)
        verdicts.append(checker.check())
    from orion.programme.mechanized import ProofOutcome

    if verdicts == [solver.sat, solver.sat]:
        return ProofResult(
            SEPARATION_IS_NECESSARY,
            ProofOutcome.PROVED,
            "disagreeing models exist for both cross-read directions with disjoint "
            "writes and explicit frame-faithful deterministic mechanics",
        )
    if solver.unsat in verdicts:
        return ProofResult(
            SEPARATION_IS_NECESSARY,
            ProofOutcome.COUNTEREXAMPLE,
            "one cross-read direction had no disagreeing model; the symmetric "
            "load-bearing claim is not discharged",
        )
    return ProofResult(
        SEPARATION_IS_NECESSARY,
        ProofOutcome.UNKNOWN,
        "solver returned unknown for at least one cross-read direction; NOT discharged",
    )


# ---------------------------------------------------------------------------
# Is P6's concrete mechanic a model of these primitives?
# ---------------------------------------------------------------------------


def instantiation_check(repo_root: Any, *, node_count: int = 5) -> DifferentialReport:
    """Check that P6's committed mechanic satisfies the frame condition.

    The theorems above are about *any* transformer obeying its declared frame.
    They therefore apply to P6's concrete
    ``check_finite_models.apply_local_mechanic`` exactly if that function obeys
    its frame --- if perturbing a coordinate it does not declare as a read never
    changes what it writes. This is what turns the finite enumeration from a
    parallel result into an instance of the general one, which is the shape
    ``P6-U-T2`` asks for.

    Checked exhaustively rather than sampled: over ``node_count`` binary
    coordinates the space is small enough to enumerate, and a sampled answer to
    "does anything outside the frame ever matter" is weaker than it needs to be.

    ``positive_trials`` counts the perturbations that actually changed a
    non-frame coordinate. A run in which nothing was perturbed would report
    perfect agreement while testing nothing, so the count is reported and the
    caller can see the corpus was informative.
    """

    from itertools import product

    from orion.programme.mechanized import load_executable_model

    from pathlib import Path

    model = load_executable_model(
        Path(repo_root) / EXECUTABLE_MODEL, "p6_check_finite_models"
    )

    disagreements: list[str] = []
    trials = 0
    perturbed = 0
    coordinates = range(node_count)

    for write in coordinates:
        others = [c for c in coordinates if c != write]
        for reads_mask in range(1 << len(others)):
            reads = frozenset(
                others[index] for index in range(len(others)) if reads_mask & (1 << index)
            )
            outside = [c for c in others if c not in reads]
            for state in product((0, 1), repeat=node_count):
                base = model.apply_local_mechanic(state, write, reads)[write]
                for victim in outside:
                    flipped = list(state)
                    flipped[victim] = 1 - flipped[victim]
                    trials += 1
                    perturbed += 1
                    got = model.apply_local_mechanic(tuple(flipped), write, reads)[write]
                    if got != base:
                        disagreements.append(
                            f"write={write} reads={sorted(reads)} state={state} "
                            f"flipping {victim} changed the written value {base} -> {got}"
                        )
                # A trial with nothing outside the frame still exercises the
                # mechanic, and is counted so the denominator is the whole space.
                if not outside:
                    trials += 1

    return DifferentialReport(
        trials=trials,
        agreements=trials - len(disagreements),
        disagreements=tuple(disagreements[:20]),
        positive_trials=perturbed,
    )


def build_report(repo_root: Any, *, node_count: int = 5) -> dict[str, object]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    theorems = prove_all()
    instantiation = instantiation_check(repo_root, node_count=node_count)
    undischarged = [r.theorem.name for r in theorems if not r.discharged]
    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P6_SEPARATION_CALCULUS_MECHANIZED",
        "solver": _z3.get_version_string(),
        "theorems": [r.as_json() for r in theorems],
        "instantiation_of_the_committed_mechanic": instantiation.as_json(),
        "instantiation_node_count": node_count,
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "what_this_establishes": (
            "separated commutation, write locality, frame determinacy and fixpoint "
            "conservativity hold for any number of coordinates over any value domain "
            "and for every transformer obeying its declared frame; and P6's committed "
            "mechanic obeys its declared frame, so the bounded enumeration in "
            "check_finite_models is an instance of the general result rather than a "
            "separate finding"
        ),
        "not_licensed": [
            "any claim that P6's full 155-restoration / 1,055-strict-subset result is "
            "hereby re-derived; the reopening and restoration theorems are not lifted here",
            "any claim of independent formal review; these proofs have been checked by a "
            "solver, not reviewed by a person outside this lane",
            "any empirical claim whatsoever",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p6-separation-calculus",
        description="Discharge P6's separation theorems over arbitrary state spaces.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--node-count", type=int, default=5)
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
    inst = report["instantiation_of_the_committed_mechanic"]
    print(
        f"  instantiation: {inst['agreements']}/{inst['trials']} frame-respecting, "
        f"{inst['positive_trials']} perturbations outside the frame"
    )
    if not report["all_discharged"]:
        print(f"UNDISCHARGED: {report['undischarged']}")
        return 3
    if not inst["agreed"]:
        print("THE COMMITTED MECHANIC DOES NOT OBEY ITS DECLARED FRAME")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
