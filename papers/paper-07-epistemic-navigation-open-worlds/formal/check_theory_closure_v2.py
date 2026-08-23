#!/usr/bin/env python3
"""Deterministic support checker for P7 formal core V2.

Standard-library only. These finite witnesses support theorem boundaries; they
are not empirical claims about real search agents.

Checks report a terminal, and the terminal is three-valued. `PASS` is a check
whose witnesses were decided by the model it enumerates; `CANNOT_CHECK` is a
check whose claim turns on a premise this model cannot express, and it names
that premise rather than reporting a case count. The distinction is load-bearing
for `check_support_transport`: Theorem 6's terminal is a function of Definition
14 target-ambiguity, and a checker that takes such a premise as an argument and
asserts the terminal the argument implies has restated its own terminal map.

That check no longer takes it as an argument. `Transport` still carries six
boolean witness coordinates and no completion class, so the check enumerates a
completion class alongside each witness and decides target-ambiguity from it with
`extension_ambiguous`, the Definition 14 decider this file already ships. The
enumeration is therefore 64 x 15 = 960 cases rather than 64, and that count is
not comparable to the old one: 64 was the size of an enumeration standing
downstream of a premise the model never decided, and 960 is a count of cases
whose premise the check decides. See that function's docstring for the two bodies
this replaced, and for what the case count does and does not establish.

The `P7 THEORY CLOSURE V2: PASS` banner therefore reports assertion status only.
`theory_closure_terminal`, printed beneath it, is the aggregate over the
three-valued check terminals and is the line to read for what this file
establishes.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product


@dataclass(frozen=True)
class Completion:
    observed_history: tuple[str, ...]
    mandatory_satisfied: bool
    hidden_witness: str | None = None


def observationally_equivalent(a: Completion, b: Completion) -> bool:
    return a.observed_history == b.observed_history


def extension_ambiguous(completions: tuple[Completion, ...]) -> bool:
    return any(
        observationally_equivalent(a, b)
        and a.mandatory_satisfied != b.mandatory_satisfied
        for a in completions
        for b in completions
    )


def check_stopping_impossibility() -> int:
    h = ("query:q", "result:empty")
    complete = Completion(h, True, None)
    incomplete = Completion(h, False, "hidden-relevant")
    assert extension_ambiguous((complete, incomplete))
    for decision in ("TASK_STOP", "CONTINUE", "CANNOT_CHECK"):
        if decision == "TASK_STOP":
            assert incomplete.mandatory_satisfied is False
        else:
            assert complete.mandatory_satisfied is True
    return 3


def check_certificate_absence_not_ambiguity() -> int:
    singleton = (Completion(("manifest:closed-world",), True, None),)
    assert not extension_ambiguous(singleton)
    rich = (
        Completion(("query:q", "result:empty"), True, None),
        Completion(("query:q", "result:empty"), False, "unseen"),
    )
    assert extension_ambiguous(rich)
    return 2


STATES = ("s0", "s1")
ACTIONS = ("a0", "a1")
RAW = {"s0": ("shared", "bit0"), "s1": ("shared", "bit1")}


def old_obs(state: str) -> str:
    return RAW[state][0]


def new_obs(state: str) -> tuple[str, str]:
    return RAW[state]


def success(state: str, action: str) -> bool:
    return (state, action) in {("s0", "a0"), ("s1", "a1")}


def old_chart_policies():
    for action in ACTIONS:
        yield {"shared": action}


def check_representation_refinement_strictness() -> int:
    for policy in old_chart_policies():
        wins = [success(s, policy[old_obs(s)]) for s in STATES]
        assert not all(wins)
    refined = {
        ("shared", "bit0"): "a0",
        ("shared", "bit1"): "a1",
    }
    assert all(success(s, refined[new_obs(s)]) for s in STATES)
    assert set(RAW) == set(STATES)
    return 3


def check_harmful_coarsening() -> int:
    refined = {new_obs(s): ("a0" if s == "s0" else "a1") for s in STATES}
    assert all(success(s, refined[new_obs(s)]) for s in STATES)
    for action in ACTIONS:
        assert not all(success(s, action) for s in STATES)
    return 3


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    proposition: str
    value: float


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    predicate: str
    threshold: float

    def satisfied_by(self, e: Evidence) -> bool:
        if e.proposition != self.predicate:
            return False
        return e.value > self.threshold


def check_evidence_not_closure_transport() -> int:
    e = Evidence("e1", "x", 5.0)
    old = Obligation("o_old", "x", 3.0)
    new = Obligation("o_new", "x", 7.0)
    assert old.satisfied_by(e)
    assert not new.satisfied_by(e)
    return 1


#: The three terminals a check in this file may report. ``CANNOT_CHECK`` is not a
#: pass and not a failure: it is this checker declining to report either, and it
#: is a written-down name rather than a count so that nothing downstream can
#: recover a verdict from truthiness. ``not 0`` and ``not None`` are both
#: ``True``, so an integer case count cannot carry three values.
CHECK_TERMINALS = ("PASS", "FAIL", "CANNOT_CHECK")


@dataclass(frozen=True)
class CheckTerminal:
    """One check's three-valued terminal, with what it is entitled to report.

    ``PASS`` has to be stated and cannot be inferred from a case count, and it
    cannot be paired with a premise the check could not decide. ``CANNOT_CHECK``
    has to name that premise and what the premise must be decided from, so that
    "the checker could not decide this" is a readable fact rather than a missing
    line.
    """

    terminal: str
    checked: int
    undecidable_premise: str | None = None
    decided_from: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if self.terminal not in CHECK_TERMINALS:
            raise ValueError(f"unknown check terminal: {self.terminal!r}")
        if self.terminal == "PASS" and self.undecidable_premise is not None:
            raise ValueError("PASS cannot carry a premise the check did not decide")
        if self.terminal == "CANNOT_CHECK" and not (
            self.undecidable_premise and self.decided_from
        ):
            raise ValueError(
                "CANNOT_CHECK must name the premise it could not decide and what that "
                "premise is decided from; an unnamed one reads as a clean check"
            )

    def __str__(self) -> str:
        if self.terminal == "PASS":
            head = f"PASS ({self.checked} checked)"
            return f"{head} ({self.detail})" if self.detail else head
        parts = [self.terminal]
        if self.undecidable_premise:
            parts.append(f"premise={self.undecidable_premise}")
        if self.decided_from:
            parts.append(f"decided_from={self.decided_from}")
        head = " ".join(parts)
        return f"{head} ({self.detail})" if self.detail else head


def one_terminal(value: object) -> str:
    """The terminal one check's return value is entitled to.

    A :class:`CheckTerminal` carries its own. A positive ``int`` is a legacy
    count, meaning the check ran that many witnesses to completion, so it earns
    ``PASS``. Everything else --- zero, a negative, ``None``, some other type ---
    earns ``CANNOT_CHECK`` rather than falling through to a pass. That fall-through
    is the whole hazard: ``not 0`` and ``not None`` are both ``True``, so a check
    that witnessed nothing is indistinguishable from a clean one under truthiness,
    and the default here has to be the one that cannot overclaim.
    """

    if isinstance(value, CheckTerminal):
        return value.terminal
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return "PASS"
    return "CANNOT_CHECK"


def aggregate_terminal(results: dict[str, object]) -> str:
    """The worst terminal across the checks, reduced over the three names.

    Over ``CHECK_TERMINALS``, never over truthiness. One ``CANNOT_CHECK`` carries
    the whole file to ``CANNOT_CHECK``.
    """

    terminals = {one_terminal(value) for value in results.values()}
    for terminal in ("FAIL", "CANNOT_CHECK"):
        if terminal in terminals:
            return terminal
    return "PASS"


@dataclass(frozen=True)
class Transport:
    maps_support: bool
    preserves_semantics: bool
    maps_obligation: bool
    preserves_satisfaction_meaning: bool
    preserves_evidence_identity: bool
    excludes_new_defeater: bool

    @property
    def complete(self) -> bool:
        return all((
            self.maps_support,
            self.preserves_semantics,
            self.maps_obligation,
            self.preserves_satisfaction_meaning,
            self.preserves_evidence_identity,
            self.excludes_new_defeater,
        ))


#: Definition 14's admissible target completions, as a finite pool over two
#: observation histories. Ambiguity is a property of the *class* and not of any
#: member: ``extension_ambiguous`` looks for two completions that share an observed
#: history and disagree on ``mandatory_satisfied``. The pool is built so that both
#: values of Definition 14 arise from that structure rather than from a label, and
#: ``check_support_transport`` asserts that both of them do arise.
ADMISSIBLE_COMPLETION_POOL: tuple[tuple[str, Completion], ...] = (
    ("open:satisfied", Completion(("query:q", "result:empty"), True, None)),
    ("open:unsatisfied", Completion(("query:q", "result:empty"), False, "unseen")),
    ("closed:satisfied", Completion(("manifest:closed-world",), True, None)),
    (
        "closed:unsatisfied",
        Completion(("manifest:closed-world",), False, "hidden-relevant"),
    ),
)


def admissible_completion_classes() -> dict[str, tuple[Completion, ...]]:
    """Every non-empty admissible target completion class over the pool.

    Fifteen classes, keyed by the members they are built from. Seven are
    target-ambiguous under ``extension_ambiguous`` and eight are not, so the
    quantity Theorem 6 reads varies across the enumeration instead of being a
    constant the enumeration cannot see.

    This is a finite family, not the set of all admissible target completions.
    What it supports is a check that *decides* Definition 14 per case; it is not a
    proof over every completion class a target model could admit.
    """

    classes: dict[str, tuple[Completion, ...]] = {}
    for size in range(1, len(ADMISSIBLE_COMPLETION_POOL) + 1):
        for chosen in combinations(ADMISSIBLE_COMPLETION_POOL, size):
            classes["+".join(name for name, _ in chosen)] = tuple(
                completion for _, completion in chosen
            )
    return classes


#: Definition 14's target-ambiguity premise, by the name Theorem 6's terminal map
#: takes it under, and the class it must be decided from. ``Transport`` above has
#: six boolean witness coordinates and no completions, so the class is enumerated
#: beside the witness by ``check_support_transport`` and this name is decided from
#: it rather than supplied to it.
TRANSPORT_PREMISE = "target_ambiguous_if_missing"
TRANSPORT_PREMISE_DECIDED_FROM = "admissible_target_completions"


def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool | None) -> str:
    """Theorem 6's terminal for one transport witness.

    ``target_ambiguous_if_missing`` is Definition 14 --- whether the admissible
    target completions contain one preserving the transported certificate
    derivation and one invalidating it --- and it is three-valued here. ``None``
    is "not decided" and returns ``PREMISE_UNDECIDED``; it does not fall through
    to either branch. The theorem's own ``CANNOT_CHECK`` is a different fact (the
    witness is incomplete and the target class is *decided* to be unambiguous),
    so the two cannot share a name without the undecided case reading as the
    boundary case the V2 core says it repaired.

    ``check_support_transport`` no longer passes ``None``; it decides the premise
    from a completion class. The branch stays because it is the guard: a caller
    that has not decided Definition 14 gets ``PREMISE_UNDECIDED`` and not a
    terminal it can quote.
    """

    if t.complete:
        return "TRANSFER_CLOSURE"
    if target_ambiguous_if_missing is None:
        return "PREMISE_UNDECIDED"
    return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"


def check_support_transport() -> CheckTerminal:
    """Theorem 6 over every transport witness crossed with a completion class.

    The premise is decided here rather than supplied. Definition 14 asks whether
    the admissible target completions contain one preserving the transported
    certificate derivation and one invalidating it. That is a question about a
    *class*, so this check enumerates the classes beside the witnesses and answers
    it with ``extension_ambiguous`` --- the decider this file already ships, and
    which this theorem previously could not call.

    Two earlier bodies are recorded, because the case count moved twice and the
    numbers are not comparable to each other.

    The first supplied the premise as a literal and returned ``64``::

        count = 0
        for bits in product((False, True), repeat=6):
            t = Transport(*bits)
            good = transfer_terminal(t, target_ambiguous_if_missing=True)
            if t.complete:
                assert good == "TRANSFER_CLOSURE"
            else:
                assert good == "REOPEN"
                assert transfer_terminal(t, target_ambiguous_if_missing=False) == "CANNOT_CHECK"
            count += 1
        return count

    The expected value moved with the input, so those assertions restated
    ``transfer_terminal`` rather than constraining it: 0 of the 64 states excluded
    either value of the premise, leaving all 2**64 ambiguity predicates admissible
    --- including the constant-``False`` one, which is "incompleteness never means
    ambiguity", the exact V1 error the Boundary paragraph under Theorem 6 says
    deciding this premise repaired.

    The second supplied no value, passed ``None``, and reported ``CANNOT_CHECK``
    naming the premise and what it is decided from. It returned ``1``: honest about
    the first body, but it left 63 of the 64 states with no terminal at all, and it
    reported the premise as inexpressible when what was missing was one axis.

    This body carries that axis. 64 witness-coordinate states x 15 admissible
    completion classes is 960 cases, and every one of them decides ambiguity from
    its own class. ``960`` is a count of cases whose premise the check decided;
    ``64`` was the size of an enumeration standing downstream of a premise nothing
    decided, and ``1`` was what survived saying so.

    What this establishes
    ---------------------
    On all 960 cases the terminal Theorem 6 assigns is the terminal computed from
    the witness's completeness and from Definition 14 applied to that case's own
    completion class, with nothing about ambiguity taken from a caller. On the 945
    cases whose witness is incomplete the terminal *changes* when ambiguity does,
    which is asserted directly, so the premise is consumed rather than carried
    past. Both values of Definition 14 occur --- 7 of the 15 classes are ambiguous
    --- so the decision is not a constant wearing a decision's name.

    What this does not establish
    ----------------------------
    The remaining 15 cases pair the one complete witness with each class, and there
    Theorem 6 returns ``TRANSFER_CLOSURE`` whatever ambiguity is. Those cases decide
    the premise but do not test the terminal's dependence on it, which is why the
    split is reported and not folded into the single number. That insensitivity is
    itself asserted --- a complete witness transports closure at both values of
    Definition 14 --- so it is a checked property of Theorem 5's positive transport
    rather than a case the check quietly failed to constrain.

    And this is a finite witness family, not a proof over Definition 14. The
    classes are the 15 non-empty subsets of a fixed four-completion pool over two
    observation histories; a target model admitting completions outside that pool
    is not enumerated here. The claim earned is that this check decides its own
    ambiguity premise on every case it enumerates, not that every admissible target
    class has been examined.
    """

    classes = admissible_completion_classes()
    ambiguous_classes = tuple(
        name for name, members in classes.items() if extension_ambiguous(members)
    )
    # A premise that came out constant across the enumeration would be decided and
    # inert at once, and the count would be back to measuring only the mapping.
    assert 0 < len(ambiguous_classes) < len(classes)

    consumed = 0
    fixed_by_completeness = 0
    for bits in product((False, True), repeat=6):
        t = Transport(*bits)
        for members in classes.values():
            ambiguous = extension_ambiguous(members)
            terminal = transfer_terminal(t, target_ambiguous_if_missing=ambiguous)
            if t.complete:
                # Decided, but Theorem 6 does not read it here --- and that is
                # asserted rather than left implicit, so the insensitivity of these
                # cases is a checked property of the theorem and not a gap.
                assert terminal == "TRANSFER_CLOSURE"
                assert (
                    transfer_terminal(t, target_ambiguous_if_missing=not ambiguous)
                    == "TRANSFER_CLOSURE"
                )
                fixed_by_completeness += 1
                continue
            assert terminal == ("REOPEN" if ambiguous else "CANNOT_CHECK")
            # Consumed: the other value of the decided premise is another terminal.
            assert (
                transfer_terminal(t, target_ambiguous_if_missing=not ambiguous) != terminal
            )
            consumed += 1

    checked = consumed + fixed_by_completeness
    assert len(classes) == 15
    assert len(ambiguous_classes) == 7
    assert fixed_by_completeness == len(classes) == 15
    assert consumed == 63 * len(classes) == 945
    assert checked == 64 * len(classes) == 960
    return CheckTerminal(
        "PASS",
        checked=checked,
        detail=(
            f"{checked} cases = 64 transport-coordinate states x {len(classes)} admissible "
            f"target completion classes, {len(ambiguous_classes)} of them ambiguous; "
            "target_ambiguous_if_missing is decided per case from that case's own class "
            f"by extension_ambiguous, and on {consumed} of the cases the terminal changes "
            f"when it does. The other {fixed_by_completeness} pair the complete witness "
            "with each class, where Theorem 6 is TRANSFER_CLOSURE regardless of ambiguity"
        ),
    )


def task_terminal(
    *,
    route_exhausted: bool,
    mandatory_open: bool,
    censored_unknown: bool,
    budget_exhausted: bool,
) -> str:
    if mandatory_open or censored_unknown:
        if budget_exhausted:
            return "CANNOT_CHECK"
        return "CONTINUE"
    if route_exhausted:
        return "ROUTE_STOP"
    return "TASK_STOP"


def check_stop_terminals() -> int:
    assert task_terminal(route_exhausted=True, mandatory_open=True, censored_unknown=False, budget_exhausted=False) == "CONTINUE"
    assert task_terminal(route_exhausted=True, mandatory_open=False, censored_unknown=False, budget_exhausted=False) == "ROUTE_STOP"
    assert task_terminal(route_exhausted=False, mandatory_open=False, censored_unknown=False, budget_exhausted=False) == "TASK_STOP"
    assert task_terminal(route_exhausted=True, mandatory_open=True, censored_unknown=True, budget_exhausted=True) == "CANNOT_CHECK"
    return 4


@dataclass(frozen=True)
class RouteStructure:
    chart: str
    objective: str
    nodes: frozenset[str]
    edges: frozenset[tuple[str, str]]
    initial_obligations: frozenset[str]
    normalized_trace: tuple[str, ...]
    terminal_semantics: tuple[str, ...]


def structurally_equivalent(
    source: RouteStructure,
    target: RouteStructure,
    renaming: dict[str, str],
) -> bool:
    return (
        {renaming[node] for node in source.nodes} == set(target.nodes)
        and {(renaming[a], renaming[b]) for a, b in source.edges} == set(target.edges)
        and source.objective == target.objective
        and source.initial_obligations == target.initial_obligations
        and tuple(renaming[node] for node in source.normalized_trace) == target.normalized_trace
        and source.terminal_semantics == target.terminal_semantics
    )


def route_refines(
    coarse: RouteStructure,
    fine: RouteStructure,
    projection: dict[str, str],
) -> bool:
    return (
        {projection[node] for node in fine.nodes} == set(coarse.nodes)
        and {(projection[a], projection[b]) for a, b in fine.edges} == set(coarse.edges)
        and fine.objective == coarse.objective
        and fine.initial_obligations == coarse.initial_obligations
        and tuple(projection[node] for node in fine.normalized_trace) == coarse.normalized_trace
        and fine.terminal_semantics == coarse.terminal_semantics
    )


def check_route_relations() -> int:
    terminals = ("ROUTE_STOP", "TASK_STOP", "CANNOT_CHECK")
    original = RouteStructure(
        "coarse",
        "objective-1",
        frozenset({"a", "b"}),
        frozenset({("a", "b")}),
        frozenset({"o"}),
        ("a", "b"),
        terminals,
    )
    renamed = RouteStructure(
        "renamed",
        "objective-1",
        frozenset({"x", "y"}),
        frozenset({("x", "y")}),
        frozenset({"o"}),
        ("x", "y"),
        terminals,
    )
    assert structurally_equivalent(original, renamed, {"a": "x", "b": "y"})

    refined = RouteStructure(
        "fine",
        "objective-1",
        frozenset({"a0", "a1", "b"}),
        frozenset({("a0", "b"), ("a1", "b")}),
        frozenset({"o"}),
        ("a0", "b"),
        terminals,
    )
    assert route_refines(original, refined, {"a0": "a", "a1": "a", "b": "b"})

    changed_obligation = RouteStructure(
        original.chart,
        original.objective,
        original.nodes,
        original.edges,
        frozenset({"different"}),
        original.normalized_trace,
        terminals,
    )
    assert not structurally_equivalent(original, changed_obligation, {"a": "a", "b": "b"})
    assert not route_refines(original, changed_obligation, {"a": "a", "b": "b"})
    return 4


def recovery_transition(
    *,
    open_obligation: bool,
    dead_end_or_loop: bool,
    alternative_frontier: bool,
    revisit_trigger: bool,
    current_chart_can_resolve: bool,
    candidate_chart_expresses_need: bool,
) -> str:
    if not open_obligation:
        return "TASK_STOP"
    if not current_chart_can_resolve and candidate_chart_expresses_need:
        return "REFRAME"
    if revisit_trigger:
        return "DEFER_REVISIT"
    if dead_end_or_loop and alternative_frontier:
        return "BACKTRACK"
    return "CANNOT_CHECK"


def check_recovery_transitions() -> int:
    common = {
        "open_obligation": True,
        "dead_end_or_loop": False,
        "alternative_frontier": False,
        "revisit_trigger": False,
        "current_chart_can_resolve": True,
        "candidate_chart_expresses_need": False,
    }
    assert recovery_transition(**(common | {"open_obligation": False})) == "TASK_STOP"
    assert recovery_transition(
        **(common | {"current_chart_can_resolve": False, "candidate_chart_expresses_need": True})
    ) == "REFRAME"
    assert recovery_transition(**(common | {"revisit_trigger": True})) == "DEFER_REVISIT"
    assert recovery_transition(
        **(common | {"dead_end_or_loop": True, "alternative_frontier": True})
    ) == "BACKTRACK"
    assert recovery_transition(**(common | {"dead_end_or_loop": True})) == "CANNOT_CHECK"
    return 5


def check_fixed_chart_special_case() -> int:
    states = ("u", "v")
    edges = {("u", "v")}
    identity = {s: s for s in states}
    assert {(identity[a], identity[b]) for a, b in edges} == edges
    return 1


def main() -> int:
    totals = {
        "stopping_impossibility": check_stopping_impossibility(),
        "certificate_boundary": check_certificate_absence_not_ambiguity(),
        "representation_refinement": check_representation_refinement_strictness(),
        "harmful_coarsening": check_harmful_coarsening(),
        "evidence_vs_closure": check_evidence_not_closure_transport(),
        "support_transport": check_support_transport(),
        "stop_terminals": check_stop_terminals(),
        "route_relations": check_route_relations(),
        "recovery_transitions": check_recovery_transitions(),
        "fixed_chart_special_case": check_fixed_chart_special_case(),
    }
    # The banner reports assertion status only --- every finite witness in this
    # file held --- and is not a verdict on the theorems those witnesses support.
    # `theory_closure_terminal` is that verdict, and it is three-valued: a check
    # that reports CANNOT_CHECK carries the aggregate to CANNOT_CHECK, so a
    # premise this model cannot decide cannot be read off as a clean pass.
    print("P7 THEORY CLOSURE V2: PASS")
    print(f"theory_closure_terminal: {aggregate_terminal(totals)}")
    for key, value in totals.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
