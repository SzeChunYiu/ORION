"""P7's shipped closure checkers, and the premises they are handed rather than decide.

Two artifacts carry P7's formal authority and both are audited here against the
files on disk rather than against a fixture of this module's own.

``papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py``
is what ``REPRODUCE_V2_1.md`` names for the transport theorem --- the paper's C4,
and what ``manuscript/FORMAL_CORE_V2.md`` calls closing "the V1 logical gap". Its
theorem was::

    def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool) -> str:
        if t.complete:
            return "TRANSFER_CLOSURE"
        return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"

As audited, ``check_support_transport`` called it at ``True`` and again at
``False`` on all 64 states, so ambiguity --- the content of C4 --- was a caller
literal and the body returned ``64``. It was then repaired to supply no value and
report ``CANNOT_CHECK`` over 1 decided case, and it has since been repaired
again: it enumerates an admissible target completion class beside each witness
and decides ambiguity from that class with the shipped ``extension_ambiguous``.
:func:`transport_authority` reads both counts back off the shipped file.

``research/claim_expansion/p7/check_p7_x2_closure_carrying.py`` is what the
superiority ledger names for P7-U-T1. Its composition block is::

    for d1 in DONORS:
        for d2 in DONORS:
            c1 = carries(True, full)
            c2 = carries(True, full)
            assert compose(c1, c2, True)
            assert not compose(c1, c2, False)

Neither donor is read by anything, ``c1`` and ``c2`` are the same constant, and
``bridge_match`` --- P7.V3.5's "exact intermediate closure-contract binding" ---
is a literal typed by the caller.

What changed here, and what did not
-----------------------------------
``bridge_match`` is no longer taken from the caller in this audit. V4 §19 and
:mod:`orion.study.p7.donor_stack_as_transformation_family` interpret each donor
family as a transformation with its own hand-off contracts, so P7's own theorem
statement --- ``Match(a, b) := a = b or Bridge(a, b)`` --- is a function of the
two donors and of the registered bridge relation. :func:`composition_match`
computes it, and :func:`composition_replay` asserts the composite verdict that
computation implies rather than the verdict the caller's literal implies. The
premise is then decided on every enumerated row and exactly one deciding rule
survives, where 33,554,432 survived before.

Three facts about that repair are reported rather than left implicit, because
each of them limits it.

* The shipped block asserts **two** rows per donor pair --- one under a registry
  that bridges the hand-off and one under a registry that does not --- so the
  faithful case space is 50 rows, not 25. The registry is the model's ``Bridge``
  relation and is an axis here for that reason.
* The two registries P7 shipped are **uniform** over the stack, so the decided
  value reads the donor pair (through ``Tgt`` and ``Src``) without ever *varying*
  with it. :func:`composition_handoff_axes` measures that directly, and both
  donor axes come back inert.
* The derived value agrees with the shipped literal on all 50 rows, so
  ``composition_successes: 25`` and ``composition_bridge_countermodels: 25`` are
  unchanged. Deciding the premise moved no verdict; it removed the freedom.

``target_ambiguous_if_missing`` was a different case and is no longer one.
``admissible_target_completions`` --- the class Definition 14 reads --- used to be
absent from everything the shipped transport checker enumerated, so no rule
written against those 64 states could decide it and the constraint was
``UNDECIDABLE_IN_MODEL``. That was a statement about the model and not about the
premise, and the model has been given the axis: the shipped check now enumerates
960 cases, 64 witness-coordinate states with each of the 15 admissible completion
classes, and :func:`transport_constraint` comes back decided on every one of them
with a single admissible rule where 2**64 survived before.

Three facts bound that repair too.

* The case count grew from 64 to 960 and the two numbers do not measure the same
  thing. 64 was the size of an enumeration standing downstream of an undecided
  premise, of which the check could report 1 decided case; 960 counts cases whose
  premise the check itself decided. :func:`transport_authority` carries both.
* The completion classes are the 15 non-empty subsets of a fixed four-completion
  pool over two observation histories. Both values of Definition 14 arise from the
  structure of a class rather than from a label, which is what makes the decision
  a decision --- but this is a finite witness family and not a proof over every
  admissible target class.
* :func:`transport_replay` asserts that the rule under test agrees with
  ``extension_ambiguous`` on the case's class, because that is what the shipped
  body computes. On the 15 cases pairing the complete witness with a class,
  Theorem 6 returns ``TRANSFER_CLOSURE`` whatever ambiguity is, so that assertion
  is what pins the premise there. :func:`transport_mapping_only_floor` reports the
  verdict without it: 945 of the 960 cases still exclude a value, leaving 2**15
  rules rather than 2**64.

:func:`witness_only_transport_constraint` keeps the pre-repair model measurable,
under its own check id. It is what says the repair was a missing axis rather than
a loosened assertion: the same premise with the same ``decided_from`` over the
six coordinates alone still comes back ``UNDECIDABLE_IN_MODEL``.

Each shipped assertion is transcribed here as an :data:`AssertionReplay` that
takes the premise from a supplied deciding rule instead of from the literal, so
:func:`orion.programme.decided_premises.measure_decision_constraint` can ask how
much of the premise the artifact's own assertions pin down. The fidelity anchors
are :data:`SHIPPED_ROWS_SHA256` and :data:`SHIPPED_TRANSPORT_CASES`: the closure
row list is rebuilt byte for byte before any claim is transcribed, and the
transport space is the checker's own ``product((False, True), repeat=6)`` crossed
with the checker's own ``admissible_completion_classes()``, both read off the
shipped file.

The wrong theories registered here are for
:mod:`orion.programme.refutation_capacity`, and they exist to make the
independence of the two questions visible. Every one of them was refuted by
``check_support_transport`` while the premise it was handed was still entirely
free, which is why a refutation-capacity pass was never an answer about the
premise --- and why the premise had to be decided separately rather than argued
for from that pass.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import inspect
import io
import itertools
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Hashable

from orion.programme.decided_premises import (
    AssertionReplay,
    Assignment,
    DecisionConstraint,
    Premise,
    case_label,
    measure_decision_constraint,
)
from orion.programme.refutation_capacity import (
    AxisSensitivity,
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    Rule,
    axis_sensitivity,
)
from orion.study.p7.donor_stack_as_transformation_family import (
    CONTRACT_ASSIGNMENTS,
    COUNTERMODEL_REGISTRY,
    INTERPRETATION,
    REGISTRIES,
    SUCCESS_REGISTRY,
    handoff_is_matched,
)

#: Repository root, five parents up from ``src/orion/study/p7/closure_premises.py``.
REPO_ROOT = Path(__file__).resolve().parents[4]

THEORY_CLOSURE_PATH = (
    REPO_ROOT
    / "papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py"
)
CLOSURE_CARRYING_PATH = (
    REPO_ROOT / "research/claim_expansion/p7/check_p7_x2_closure_carrying.py"
)
CLOSURE_CARRYING_RESULT_PATH = (
    REPO_ROOT / "research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json"
)

#: ``canonical_rows_sha256`` as published in ``P7_X2_CLOSURE_CARRYING_RESULT_V1.json``.
SHIPPED_ROWS_SHA256 = "25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f"

#: The six-coordinate product; the whole of what the checker enumerated when its
#: case count was 64 and its premise was undecided.
TRANSPORT_COORDINATE_STATES = 64

#: Cases ``check_theory_closure_v2.py`` now enumerates: each coordinate state with
#: each admissible target completion class. Not comparable to the old 64 --- see
#: :func:`transport_authority`.
SHIPPED_TRANSPORT_CASES = 960

#: The six transport-witness coordinates, in ``Transport``'s field order.
TRANSPORT_COORDINATES: tuple[str, ...] = (
    "maps_support",
    "preserves_semantics",
    "maps_obligation",
    "preserves_satisfaction_meaning",
    "preserves_evidence_identity",
    "excludes_new_defeater",
)

TRANSPORT_REFERENCE_ID = "check_theory_closure_v2.transfer_terminal"
COMPOSITION_REFERENCE_ID = "check_p7_x2_closure_carrying.compose"

#: The shipped closure-carrying checker's one donor-dependent count. Its claim is
#: that a donor transform's native verdict survives projection, and the artifact
#: computes the projection as ``projected_native = native_valid``, so the count is
#: zero by construction rather than by observation.
DONOR_CONSERVATIVITY_COUNT = "donor_conservativity_violations"

#: The check id the pre-repair transport model is measured under. Deliberately not
#: ``check_support_transport``: that name now belongs to a check that enumerates
#: completion classes, and a shared id would let the counterfactual be read as the
#: shipped result.
WITNESS_ONLY_TRANSPORT_CHECK_ID = "check_support_transport_without_completion_classes"


def _accepts(replay: AssertionReplay, assignment: Assignment) -> bool:
    """Whether replayed assertions hold under one deciding rule."""

    try:
        return bool(replay(assignment))
    except AssertionError:
        return False


def _load(module_name: str, path: Path) -> ModuleType:
    """Import a shipped checker by path without running its ``__main__`` block.

    Registered in ``sys.modules`` before execution because both checkers define
    frozen dataclasses, which resolve their annotations through the module entry.
    """

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the shipped checker at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def theory_closure_module() -> ModuleType:
    """The paper's shipped V2 theory-closure checker."""

    return _load("orion_p7_shipped_theory_closure_v2", THEORY_CLOSURE_PATH)


def closure_carrying_module() -> ModuleType:
    """The shipped P7-X2 closure-carrying checker behind P7-U-T1's artifact."""

    return _load("orion_p7_shipped_closure_carrying", CLOSURE_CARRYING_PATH)


def _run_shipped_main(module: ModuleType) -> dict[str, Any]:
    """Run a shipped checker's ``main`` and parse the JSON it prints."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module.main()
    return json.loads(buffer.getvalue())


# ---------------------------------------------------------------------------
# The transport theorem: 960 cases, and the ambiguity premise decided on each
# ---------------------------------------------------------------------------

def transport_coordinate_states() -> tuple[ModelPoint, ...]:
    """The checker's ``product((False, True), repeat=6)``, named by coordinate.

    64 of them. This was the whole of the enumerated space while the ambiguity
    premise was undecided; it is now one factor of it.
    """

    return tuple(
        dict(zip(TRANSPORT_COORDINATES, bits))
        for bits in itertools.product((False, True), repeat=6)
    )


def completion_classes(module: ModuleType) -> dict[str, tuple[Any, ...]]:
    """The admissible target completion classes, read off the shipped checker.

    Not a fixture of this module's: ``admissible_completion_classes`` lives in
    ``check_theory_closure_v2.py`` because the shipped check is what enumerates
    them. Fifteen classes, seven target-ambiguous under the shipped
    ``extension_ambiguous`` and eight not, so a rule over this axis has something
    to decide.
    """

    return module.admissible_completion_classes()


def transport_cases(module: ModuleType) -> tuple[ModelPoint, ...]:
    """The space ``check_support_transport`` enumerates: witness x completion class.

    960 cases. The axis Definition 14 reads --- ``admissible_target_completions``
    --- is present, which is the whole of the difference between this and the
    64-case model measured by :func:`witness_only_transport_constraint`.
    """

    return tuple(
        {**point, "admissible_target_completions": name}
        for point in transport_coordinate_states()
        for name in completion_classes(module)
    )


TARGET_AMBIGUITY = Premise(
    premise_id="target_ambiguous_if_missing",
    claim_ref="P7 C4 / FORMAL_CORE_V2 Thm. 6 (support transport)",
    decision_obligation=(
        "whether the admissible target model class contains one completion that "
        "preserves the transported certificate and one that invalidates it"
    ),
    # Named as the manuscript states it. The shipped transport check now carries a
    # completion class beside each witness, so this axis is present in the space it
    # enumerates; :func:`witness_only_transport_constraint` measures the same
    # premise over the model that lacked it, which is what says the repair was a
    # missing axis rather than an inexpressible question.
    decided_from=("admissible_target_completions",),
    domain=(False, True),
)


def transport_baseline(module: ModuleType) -> Assignment:
    """Definition 14, computed: ``extension_ambiguous`` over the case's own class.

    The rule the shipped body runs, so this is the baseline rather than a literal.
    """

    classes = completion_classes(module)

    def baseline(point: ModelPoint) -> Hashable:
        return bool(
            module.extension_ambiguous(classes[point["admissible_target_completions"]])
        )

    return baseline


def transport_replay(module: ModuleType) -> AssertionReplay:
    """The shipped ``check_support_transport``, replayed under a deciding rule.

    Three assertions per case, transcribed from the shipped body in its order.

    The first is the decision. The shipped body computes ambiguity by calling
    ``extension_ambiguous`` on the case's class, so a rule that disagrees with that
    call on that class is not a rule the check runs; asserting ``supplied ==
    decided`` is the transcription of that computation, not an extra assertion.
    Without it the 15 cases pairing the complete witness with a class would read as
    free, because Theorem 6 returns ``TRANSFER_CLOSURE`` there whatever ambiguity
    is --- the premise is decided on those cases but not consumed by the terminal.

    :func:`transport_mapping_only_floor` is what keeps that from being the load the
    verdict rests on: it drops this assertion and reports what the mapping
    assertions alone still exclude, which is 945 of the 960 cases.

    The second is the mapping, unchanged from the shipped theorem. The third is the
    sensitivity assertion the shipped body makes on every case: on an incomplete
    witness the other value of the premise is a different terminal, and on the
    complete one it is the same terminal --- which is Theorem 5's positive transport
    and is why those cases cannot constrain the premise through the mapping.
    """

    transport_type = module.Transport
    classes = completion_classes(module)
    cases = transport_cases(module)

    def replay(assignment: Assignment) -> bool:
        for point in cases:
            witness = transport_type(*(point[name] for name in TRANSPORT_COORDINATES))
            completions = classes[point["admissible_target_completions"]]
            decided = bool(module.extension_ambiguous(completions))
            supplied = bool(assignment(point))
            assert supplied == decided
            terminal = module.transfer_terminal(
                witness, target_ambiguous_if_missing=supplied
            )
            if witness.complete:
                assert terminal == "TRANSFER_CLOSURE"
                assert (
                    module.transfer_terminal(
                        witness, target_ambiguous_if_missing=not supplied
                    )
                    == "TRANSFER_CLOSURE"
                )
                continue
            assert terminal == ("REOPEN" if decided else "CANNOT_CHECK")
            assert (
                module.transfer_terminal(
                    witness, target_ambiguous_if_missing=not supplied
                )
                != terminal
            )
        return True

    return replay


def transport_mapping_only_replay(module: ModuleType) -> AssertionReplay:
    """The shipped assertions minus the one that reads the computed premise back.

    The weakest honest reading of the repaired check: pretend the ambiguity value
    reaching ``transfer_terminal`` could be anything, and keep only the assertions
    about the terminal. What survives is the floor under the verdict.
    """

    transport_type = module.Transport
    classes = completion_classes(module)
    cases = transport_cases(module)

    def replay(assignment: Assignment) -> bool:
        for point in cases:
            witness = transport_type(*(point[name] for name in TRANSPORT_COORDINATES))
            completions = classes[point["admissible_target_completions"]]
            decided = bool(module.extension_ambiguous(completions))
            supplied = bool(assignment(point))
            terminal = module.transfer_terminal(
                witness, target_ambiguous_if_missing=supplied
            )
            if witness.complete:
                assert terminal == "TRANSFER_CLOSURE"
                assert (
                    module.transfer_terminal(
                        witness, target_ambiguous_if_missing=not supplied
                    )
                    == "TRANSFER_CLOSURE"
                )
                continue
            assert terminal == ("REOPEN" if decided else "CANNOT_CHECK")
        return True

    return replay


def transport_mapping_only_floor(module: ModuleType | None = None) -> dict[str, Any]:
    """How much of the premise the terminal assertions alone exclude.

    Reported beside the verdict because :func:`transport_replay` asserts the
    decision directly, and a reader is entitled to know how much of the result that
    assertion carries. Answer: 945 of the 960 cases exclude a value of the premise
    from the terminal assertions by themselves, and the free 15 are exactly the
    complete witness paired with each class, where Theorem 6 does not read
    ambiguity at all.
    """

    module = module or theory_closure_module()
    replay = transport_mapping_only_replay(module)
    baseline = transport_baseline(module)
    cases = transport_cases(module)
    free = 0
    for point in cases:
        label = case_label(point)
        other = not bool(baseline(point))

        def flipped(candidate: ModelPoint, label: str = label, other: bool = other) -> Hashable:
            if case_label(candidate) == label:
                return other
            return baseline(candidate)

        if _accepts(replay, flipped):
            free += 1
    decided = len(cases) - free
    return {
        "cases": len(cases),
        "cases_excluding_a_value_from_the_terminal_assertions_alone": decided,
        "cases_free_under_the_terminal_assertions_alone": free,
        "admissible_ambiguity_rules_under_the_terminal_assertions_alone": 2**free,
        "reading": (
            f"dropping the assertion that the supplied premise equals the computed one, "
            f"{decided} of {len(cases)} cases still exclude a value of "
            f"{TARGET_AMBIGUITY.premise_id} and {2**free} ambiguity rules survive, against "
            f"{2**TRANSPORT_COORDINATE_STATES} before the completion class was carried; the "
            f"{free} free cases are the complete witness with each class, where Theorem 6 "
            "returns TRANSFER_CLOSURE regardless of ambiguity"
        ),
    }


def transport_rule(module: ModuleType) -> Rule:
    """``transfer_terminal`` as a rule over the enumerated space, ambiguity included."""

    transport_type = module.Transport

    def rule(point: ModelPoint) -> Hashable:
        witness = transport_type(*(point[name] for name in TRANSPORT_COORDINATES))
        return module.transfer_terminal(
            witness, target_ambiguous_if_missing=bool(point["target_ambiguous_if_missing"])
        )

    return rule


def transport_theory_space() -> tuple[ModelPoint, ...]:
    """The 64 coordinate states crossed with both ambiguity values.

    Ambiguity is a free axis here rather than a computed one, and deliberately: a
    false theory of the *terminal map* has to be evaluable at both values of the
    map's own parameter, so this space asks a different question from the one
    :func:`transport_cases` asks. The shipped check computes the value; this space
    quantifies over it.
    """

    return tuple(
        {**point, "target_ambiguous_if_missing": ambiguous}
        for point in transport_coordinate_states()
        for ambiguous in (False, True)
    )


def _complete(point: ModelPoint) -> bool:
    return all(bool(point[name]) for name in TRANSPORT_COORDINATES)


FALSE_TRANSPORT_THEORIES: tuple[FalseTheory, ...] = (
    FalseTheory(
        theory_id="incomplete_always_reopens",
        breaks=(
            "C4's boundary: an incomplete but non-ambiguous witness is CANNOT_CHECK, "
            "not a refutation. This is the V1 error the V2 core says it repaired"
        ),
        rule=lambda point: "TRANSFER_CLOSURE" if _complete(point) else "REOPEN",
    ),
    FalseTheory(
        theory_id="incomplete_always_cannot_check",
        breaks="C4's ambiguous branch: an ambiguous incomplete witness must reopen",
        rule=lambda point: "TRANSFER_CLOSURE" if _complete(point) else "CANNOT_CHECK",
    ),
    FalseTheory(
        theory_id="closure_always_transports",
        breaks="the support-transport criterion itself: closure would survive any reframe",
        rule=lambda point: "TRANSFER_CLOSURE",
    ),
    FalseTheory(
        theory_id="five_of_six_coordinates_suffice",
        breaks=(
            "completeness of the witness: dropping excludes_new_defeater would let a "
            "reframe that admits a new defeater carry closure"
        ),
        rule=lambda point: (
            "TRANSFER_CLOSURE"
            if all(bool(point[name]) for name in TRANSPORT_COORDINATES[:5])
            else ("REOPEN" if point["target_ambiguous_if_missing"] else "CANNOT_CHECK")
        ),
    ),
)


def transport_check() -> MechanizedCheck:
    """``check_support_transport``, as a predicate over a supplied terminal rule."""

    def accepts(rule: Rule) -> bool:
        for point in transport_theory_space():
            terminal = rule(point)
            if _complete(point):
                assert terminal == "TRANSFER_CLOSURE"
            elif point["target_ambiguous_if_missing"]:
                assert terminal == "REOPEN"
            else:
                assert terminal == "CANNOT_CHECK"
        return True

    return MechanizedCheck(
        check_id="check_support_transport",
        asserts=(
            "over the 64 transport-coordinate combinations at both values of the "
            "ambiguity premise, a complete witness transports closure and an "
            "incomplete one reopens when the target is ambiguous and is CANNOT_CHECK "
            "otherwise"
        ),
        accepts=accepts,
    )


def transport_constraint(module: ModuleType | None = None) -> DecisionConstraint:
    """Measure how much of C4's ambiguity premise the shipped cases pin down."""

    module = module or theory_closure_module()
    return measure_decision_constraint(
        TARGET_AMBIGUITY,
        check_id="check_support_transport",
        cases=transport_cases(module),
        replay=transport_replay(module),
        baseline=transport_baseline(module),
        opportunity_definition=(
            "the transport-coordinate combinations the checker enumerates, each paired "
            "with one admissible target completion class; each is an opportunity for the "
            "theorem's assertions to exclude one value of the ambiguity premise"
        ),
    )


def transport_authority(module: ModuleType | None = None) -> dict[str, Any]:
    """What the shipped transport check's case count is a count *of*.

    Two counts have been published for this check and they measure different
    things, so both are carried here.

    ``64`` was the size of the six-coordinate enumeration, and
    ``REPRODUCE_V2_1.md`` reported it as "all 64 transport-coordinate
    combinations". Only the complete witness decided its terminal from those
    coordinates; the other 63 turned on Definition 14 target-ambiguity, which the
    six-coordinate ``Transport`` model does not carry, so the check was entitled to
    report ``1``.

    ``960`` is what the check enumerates now that each witness carries an
    admissible target completion class, and every one of those cases decides the
    premise from its own class. The growth is not a bigger version of the old
    number: the old count stood downstream of an undecided premise and this one
    does not.

    Read off the shipped file, not restated: ``check_support_transport`` returns a
    ``CheckTerminal`` and its ``terminal`` and ``checked`` fields are carried
    through here.
    """

    module = module or theory_closure_module()
    classes = completion_classes(module)
    ambiguous = tuple(
        name for name, members in classes.items() if module.extension_ambiguous(members)
    )
    cases = transport_cases(module)
    fixed_by_completeness = tuple(point for point in cases if _complete(point))
    consuming = tuple(point for point in cases if not _complete(point))
    shipped = module.check_support_transport()
    return {
        "enumerated_cases": len(cases),
        "transport_coordinate_states": TRANSPORT_COORDINATE_STATES,
        "admissible_completion_classes": len(classes),
        "ambiguous_completion_classes": len(ambiguous),
        "unambiguous_completion_classes": len(classes) - len(ambiguous),
        "cases_whose_terminal_consumes_the_premise": len(consuming),
        "cases_whose_terminal_is_fixed_by_completeness": len(fixed_by_completeness),
        "previously_enumerated_states": TRANSPORT_COORDINATE_STATES,
        "previously_decided_cases": 1,
        "shipped_terminal": shipped.terminal,
        "shipped_checked": shipped.checked,
        "shipped_undecidable_premise": shipped.undecidable_premise,
        "shipped_decided_from": shipped.decided_from,
        "reading": (
            f"the check enumerated {TRANSPORT_COORDINATE_STATES} witness-coordinate states "
            f"and was entitled to report 1 decided case; it now enumerates {len(cases)} "
            f"({TRANSPORT_COORDINATE_STATES} states x {len(classes)} admissible target "
            f"completion classes, {len(ambiguous)} of them ambiguous) and decides "
            f"{TARGET_AMBIGUITY.premise_id} on every one of them from that case's own "
            f"class, so the shipped check reports {shipped.checked} decided cases. On "
            f"{len(consuming)} of them the terminal changes with the premise; the other "
            f"{len(fixed_by_completeness)} pair the complete witness with each class, where "
            "Theorem 6 is TRANSFER_CLOSURE whatever ambiguity is"
        ),
    }


# ---------------------------------------------------------------------------
# The same premise in the model that did not carry what Definition 14 reads
# ---------------------------------------------------------------------------

def witness_only_transport_replay(module: ModuleType) -> AssertionReplay:
    """The transport theorem over the six coordinates alone, under a deciding rule.

    The body ``check_support_transport`` ran before it carried completion classes,
    which evaluated both ambiguity literals on every state; a deciding rule selects
    one, so this asserts the branch it picks. It calls only ``transfer_terminal``,
    whose branches the repair left unchanged.
    """

    transport_type = module.Transport
    cases = transport_coordinate_states()

    def replay(assignment: Assignment) -> bool:
        for point in cases:
            witness = transport_type(*(point[name] for name in TRANSPORT_COORDINATES))
            ambiguous = bool(assignment(point))
            terminal = module.transfer_terminal(
                witness, target_ambiguous_if_missing=ambiguous
            )
            if witness.complete:
                assert terminal == "TRANSFER_CLOSURE"
            elif ambiguous:
                assert terminal == "REOPEN"
            else:
                assert terminal == "CANNOT_CHECK"
        return True

    return replay


def witness_only_transport_baseline(point: ModelPoint) -> Hashable:
    """The ambiguity value that body's primary call passed: the literal ``True``."""

    del point
    return True


def witness_only_transport_constraint(
    module: ModuleType | None = None,
) -> DecisionConstraint:
    """The same premise, measured over the model that lacked its decision inputs.

    Kept, and reported beside the verdict, because it is what says the repair was a
    missing axis and not a loosened assertion. Same :data:`TARGET_AMBIGUITY`, same
    ``decided_from``; ``admissible_target_completions`` is simply not an axis of
    these 64 cases, so the premise comes back ``UNDECIDABLE_IN_MODEL`` with all
    2**64 ambiguity predicates admissible --- including the constant-``False`` one
    that is the V1 error the V2 core says it repaired.

    This is **not** the shipped enumeration any more, and it is measured under its
    own check id for that reason.
    """

    module = module or theory_closure_module()
    return measure_decision_constraint(
        TARGET_AMBIGUITY,
        check_id=WITNESS_ONLY_TRANSPORT_CHECK_ID,
        cases=transport_coordinate_states(),
        replay=witness_only_transport_replay(module),
        baseline=witness_only_transport_baseline,
        opportunity_definition=(
            "the 64 transport-coordinate combinations, without a completion class; each "
            "is an opportunity for the theorem's assertions to exclude one value of the "
            "ambiguity premise"
        ),
    )


# ---------------------------------------------------------------------------
# The closure-carrying composition block: 25 pairs, two registries, a computed
# hand-off
# ---------------------------------------------------------------------------

#: The two bridge registries the shipped block's two assertion families are.
#: ``assert compose(c1, c2, True)`` is the row under a registry that bridges the
#: hand-off; ``assert not compose(c1, c2, False)`` is the row under one that does
#: not. Both are uniform over the stack, which is the residue V4 §20 reports.
COMPOSITION_REGISTRIES: tuple[str, ...] = (SUCCESS_REGISTRY, COUNTERMODEL_REGISTRY)


def composition_stack(module: ModuleType) -> Any:
    """P7's donor families read as transformations with their own hand-off contracts."""

    return CONTRACT_ASSIGNMENTS[INTERPRETATION](tuple(module.DONORS))


def composition_cases(module: ModuleType) -> tuple[ModelPoint, ...]:
    """The 50 rows the shipped composition loop asserts, in its emission order.

    Twenty-five ordered donor pairs, each asserted once under each of the two
    registries. The earlier reading of this space collapsed the two rows into one
    case and so had one premise value where the artifact has two.
    """

    return tuple(
        {"left_donor": left, "right_donor": right, "registry": registry}
        for left in module.DONORS
        for right in module.DONORS
        for registry in COMPOSITION_REGISTRIES
    )


BRIDGE_MATCH = Premise(
    premise_id="bridge_match",
    claim_ref="P7.V3.5 (heterogeneous composition under exact bridge binding)",
    decision_obligation=(
        "whether the closure contract the left transform emits is exactly the contract "
        "the right transform requires, or is joined to it by a registered equivalence "
        "bridge"
    ),
    # P7's own theorem statement is Match(a, b) := a = b or Bridge(a, b), so the
    # decision reads the two transformations --- through Tgt and Src --- and the
    # registered bridge relation. All three are axes of the enumerated space.
    decided_from=("left_donor", "right_donor", "registry"),
    domain=(False, True),
)


def composition_match(module: ModuleType) -> Assignment:
    """P7.V3.5's hand-off test, computed from the case instead of typed into it.

    ``Match(Tgt t, Src u) := Tgt t = Src u or Bridge(Tgt t, Src u)``, evaluated by
    the shipped-model interpretation in
    :mod:`orion.study.p7.donor_stack_as_transformation_family`. Under frame
    condition 1 --- no family's target contract is any family's source contract
    --- the equality disjunct is false on every hand-off, so what decides a row is
    whether its hand-off is in the registry.
    """

    stack = composition_stack(module)
    registries = {name: REGISTRIES[name](stack) for name in COMPOSITION_REGISTRIES}

    def decide(point: ModelPoint) -> Hashable:
        return bool(
            handoff_is_matched(
                stack,
                registries[point["registry"]],
                point["left_donor"],
                point["right_donor"],
            )
        )

    return decide


def composition_replay(module: ModuleType) -> AssertionReplay:
    """Replay the shipped composition block with the hand-off decided, not supplied.

    The shipped loop asserts ``compose(c1, c2, True)`` and
    ``not compose(c1, c2, False)``, and the value it expects moves with the value
    it passes --- which is why every deciding rule survived it. Here the expected
    composite verdict comes from Theorem V4.1, ``Carries(Comp(t, u)) <-> Carries(t)
    and Carries(u) and Match(Tgt t, Src u)``, with ``Match`` computed by
    :func:`composition_match`. The candidate rule still supplies the third
    argument of the shipped ``compose``; it no longer supplies the answer.

    On the shipped literals the two assertions are unchanged, row for row.
    """

    full = (True,) * len(module.COORDS)
    decide = composition_match(module)
    cases = composition_cases(module)

    def replay(assignment: Assignment) -> bool:
        for point in cases:
            left_carries = module.carries(True, full)
            right_carries = module.carries(True, full)
            matched = bool(decide(point))
            expected = bool(left_carries and right_carries and matched)
            supplied = bool(assignment(point))
            assert bool(module.compose(left_carries, right_carries, supplied)) == expected
        return True

    return replay


def composition_baseline(point: ModelPoint) -> Hashable:
    """The bridge literal the shipped block passes on this row.

    ``True`` on the success assertion and ``False`` on the bridge-countermodel
    assertion. It coincides with :func:`composition_match` on all 50 rows, which
    is why deciding the premise moves neither published count.
    """

    return point["registry"] == SUCCESS_REGISTRY


def composition_constraint(module: ModuleType | None = None) -> DecisionConstraint:
    """Measure how much of P7.V3.5's bridge premise the shipped rows pin down."""

    module = module or closure_carrying_module()
    return measure_decision_constraint(
        BRIDGE_MATCH,
        check_id="p7_x2_composition_block",
        cases=composition_cases(module),
        replay=composition_replay(module),
        baseline=composition_baseline,
        opportunity_definition=(
            "the 25 ordered donor-transform pairs the checker enumerates, each asserted "
            "under the bridging registry and under the empty one; each row is an "
            "opportunity for the composition assertions to exclude one value of the "
            "intermediate-contract premise"
        ),
    )


def composition_agreement(module: ModuleType) -> dict[str, Any]:
    """Whether deciding the premise moved any verdict the artifact published.

    The row-by-row comparison of the computed hand-off against the literal the
    shipped block passes, and the two published counts recomputed from the
    computed value. Deciding a premise is allowed to change a result; if it does,
    that is the finding, and it has to be measured rather than assumed away.
    """

    decide = composition_match(module)
    cases = composition_cases(module)
    full = (True,) * len(module.COORDS)

    def composes(point: ModelPoint) -> bool:
        return bool(
            module.compose(
                module.carries(True, full),
                module.carries(True, full),
                bool(decide(point)),
            )
        )

    agreements = sum(
        1 for point in cases if bool(decide(point)) == bool(composition_baseline(point))
    )
    successes = sum(
        1 for point in cases if point["registry"] == SUCCESS_REGISTRY and composes(point)
    )
    countermodels = sum(
        1
        for point in cases
        if point["registry"] == COUNTERMODEL_REGISTRY and not composes(point)
    )
    return {
        "rows": len(cases),
        "rows_where_the_decision_agrees_with_the_shipped_literal": agreements,
        "composition_successes": successes,
        "composition_bridge_countermodels": countermodels,
        "verdicts_moved": agreements != len(cases),
    }


def composition_handoff_axes(module: ModuleType) -> tuple[AxisSensitivity, ...]:
    """Whether the decided hand-off value actually varies with each of its inputs.

    Deciding a premise from the model and the decided value *depending* on the
    model are different facts, and the second is the one P7's shipped registries
    do not supply. Both donor axes come back inert here: the decision reads the
    pair through ``Tgt`` and ``Src``, and both registries P7 shipped answer the
    same way for all 25 hand-offs. The registry axis is the one that moves.
    """

    decide = composition_match(module)
    space = composition_cases(module)
    return tuple(
        axis_sensitivity(axis, reference=decide, space=space)
        for axis in ("left_donor", "right_donor", "registry")
    )


def composition_argument_triples(module: ModuleType) -> tuple[tuple[bool, bool, bool], ...]:
    """The distinct ``(c1, c2, bridge_match)`` triples the shipped block evaluates.

    Two of the eight, because ``c1`` and ``c2`` are the same constant on every
    pair and the shipped bridge is a literal. Computing the bridge does not move
    this: both registries are uniform, so the derived value reaches the same two
    triples. What the block constrains about ``compose`` is exactly what those two
    points constrain, which is why a rule that ignores both operands survives it.
    """

    full = (True,) * len(module.COORDS)
    carried = module.carries(True, full)
    return tuple(sorted({(carried, carried, True), (carried, carried, False)}))


def compose_rules_accepted(module: ModuleType) -> tuple[int, int]:
    """How many of the 256 Boolean composition rules the shipped block accepts.

    Reported as ``(accepted, total)``. The gap between them is the block's entire
    constraint on P7's composition law, and it is a constraint on ``compose``
    rather than on the premise: deciding ``bridge_match`` leaves it where it was.
    """

    inputs = tuple(itertools.product((False, True), repeat=3))
    full = (True,) * len(module.COORDS)
    accepted = 0
    for bits in range(1 << len(inputs)):
        table = {inputs[index]: bool((bits >> index) & 1) for index in range(len(inputs))}
        left = module.carries(True, full)
        right = module.carries(True, full)
        if table[(left, right, True)] and not table[(left, right, False)]:
            accepted += 1
    return accepted, 1 << len(inputs)


def closure_model_space(module: ModuleType) -> tuple[ModelPoint, ...]:
    """The 320 rows the shipped checker enumerates, in its emission order.

    The donor axis is enumerated first because the published row list is built in
    that order and :data:`SHIPPED_ROWS_SHA256` depends on it.
    """

    return tuple(
        {"donor": donor, "native_valid": native_valid, **dict(zip(module.COORDS, closure))}
        for donor in module.DONORS
        for native_valid in (False, True)
        for closure in itertools.product((False, True), repeat=len(module.COORDS))
    )


def canonical_rows_digest(module: ModuleType) -> str:
    """Rebuild ``canonical_rows_sha256`` from the shipped checker's own rule.

    The fidelity anchor: an instrument that only ever runs on its own fixture is
    the failure it was written to catch.
    """

    rows = [
        {
            "donor": point["donor"],
            "native_valid": point["native_valid"],
            "closure": {name: point[name] for name in module.COORDS},
            "carries": module.carries(
                point["native_valid"], tuple(point[name] for name in module.COORDS)
            ),
            "ideal_product": point["native_valid"]
            and all(point[name] for name in module.COORDS),
        }
        for point in closure_model_space(module)
    ]
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def closure_reference(module: ModuleType) -> Rule:
    """``carries`` as a rule over the enumerated space."""

    def rule(point: ModelPoint) -> Hashable:
        return module.carries(
            point["native_valid"], tuple(point[name] for name in module.COORDS)
        )

    return rule


# ---------------------------------------------------------------------------
# The inert donor axis: whether the rule cannot read the donor or merely does not
# ---------------------------------------------------------------------------

def functions_taking_a_donor_argument(module: ModuleType) -> tuple[str, ...]:
    """Shipped functions with a donor in their signature. There are none.

    ``axis_sensitivity`` says the donor never changes a verdict; this says why.
    ``carries(native_valid, closure)`` and ``compose(c1, c2, bridge_match)`` have
    no parameter a donor could enter through, so the donor coordinate is not a
    quantity the rule declines to use --- it is not addressable by the rule at all.
    """

    return tuple(
        sorted(
            name
            for name, value in vars(module).items()
            if inspect.isfunction(value)
            and value.__module__ == module.__name__
            and any("donor" in parameter for parameter in inspect.signature(value).parameters)
        )
    )


def identity_guards(path: Path) -> tuple[str, ...]:
    """Guards in a shipped checker whose two operands are the same name by assignment.

    A guard comparing ``x`` against a name ``x`` was just assigned from cannot
    fire, whatever the enumeration does around it, so its violation count is a
    property of the source rather than a measurement. The closure-carrying checker
    has exactly one, and it is the only place the donor axis was supposed to do
    work: ``projected_native = native_valid`` immediately before
    ``if projected_native != native_valid: donor_conservativity_violations += 1``.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        aliases: dict[str, str] = {}
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Assign)
                and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)
                and isinstance(child.value, ast.Name)
            ):
                aliases[child.targets[0].id] = child.value.id
        for child in ast.walk(node):
            if not isinstance(child, ast.If) or not isinstance(child.test, ast.Compare):
                continue
            test = child.test
            if len(test.ops) != 1 or not isinstance(test.ops[0], (ast.Eq, ast.NotEq)):
                continue
            left, right = test.left, test.comparators[0]
            if not isinstance(left, ast.Name) or not isinstance(right, ast.Name):
                continue
            if aliases.get(left.id) == right.id or aliases.get(right.id) == left.id:
                found.add(f"{node.name}: {ast.unparse(test)}")
    return tuple(sorted(found))


def donor_axis_multipliers() -> dict[str, Any]:
    """Run the shipped checker at five donors and at one, and diff every count.

    Measured rather than read off the loop's shape, and measured on a second
    import of the same file so the audit's own module object is untouched. A count
    that is five times its one-donor value is a count of the donor loop; a count
    that is unchanged never entered it.
    """

    at_five = _load("orion_p7_closure_carrying_five_donors", CLOSURE_CARRYING_PATH)
    at_one = _load("orion_p7_closure_carrying_one_donor", CLOSURE_CARRYING_PATH)
    at_one.DONORS = at_five.DONORS[:1]
    full = _run_shipped_main(at_five)
    single = _run_shipped_main(at_one)

    counts = {
        key: (value, single[key])
        for key, value in full.items()
        if isinstance(value, int) and not isinstance(value, bool)
    }
    donors = len(at_five.DONORS)
    per_donor = tuple(
        sorted(key for key, (many, one) in counts.items() if one and many == one * donors)
    )
    per_pair = tuple(
        sorted(
            key for key, (many, one) in counts.items() if one and many == one * donors**2
        )
    )
    independent = tuple(
        sorted(key for key, (many, one) in counts.items() if one and many == one)
    )
    always_zero = tuple(sorted(key for key, (many, one) in counts.items() if not many and not one))
    return {
        "donors": donors,
        "counts_at_five_donors": {key: many for key, (many, _) in counts.items()},
        "counts_at_one_donor": {key: one for key, (_, one) in counts.items()},
        "counts_multiplied_by_the_donor_loop": per_donor,
        "counts_multiplied_by_the_donor_pair_loop": per_pair,
        "counts_independent_of_the_donor_loop": independent,
        "counts_zero_at_every_stack_size": always_zero,
    }


def donor_axis_diagnosis(module: ModuleType) -> dict[str, Any]:
    """Why the donor axis is inert, with the evidence that decides between the two causes.

    An inert axis has two possible causes and they call for different repairs. If
    the rule should read the coordinate and does not, the repair is in the rule.
    If the rule cannot read it, the enumeration is a multiplier and the artifact
    has to say so. The evidence here is the second: no shipped function has a
    parameter a donor could enter through, the counts collapse exactly five-fold
    when the stack is cut to one family, and the artifact's one donor-dependent
    claim --- ``donor_conservativity_violations`` --- is guarded by a comparison of
    a name against the name it was assigned from, so its ``0`` is a property of the
    source and not an observation.
    """

    reading_functions = functions_taking_a_donor_argument(module)
    guards = identity_guards(CLOSURE_CARRYING_PATH)
    multipliers = donor_axis_multipliers()
    return {
        "functions_taking_a_donor_argument": reading_functions,
        "the_rule_can_read_the_donor": bool(reading_functions),
        "identity_guards": guards,
        "multipliers": multipliers,
        "verdict": (
            "THE_RULE_CANNOT_READ_THE_DONOR"
            if not reading_functions
            else "THE_RULE_CAN_READ_THE_DONOR_AND_DOES_NOT"
        ),
        "reading": (
            "no shipped function takes a donor argument, so the donor coordinate is not "
            "a quantity the rule declines to use; the enumeration multiplies "
            f"{', '.join(multipliers['counts_multiplied_by_the_donor_loop'])} by "
            f"{multipliers['donors']} and "
            f"{', '.join(multipliers['counts_multiplied_by_the_donor_pair_loop'])} by "
            f"{multipliers['donors'] ** 2}, and must be read as such. The one count "
            f"whose claim needs the donor, {DONOR_CONSERVATIVITY_COUNT}, is guarded by "
            f"{'; '.join(guards) or 'no identity guard'}, which cannot fire, so its zero "
            "is a property of the source and not an observation"
        ),
    }


__all__ = [
    "BRIDGE_MATCH",
    "CLOSURE_CARRYING_PATH",
    "CLOSURE_CARRYING_RESULT_PATH",
    "COMPOSITION_REFERENCE_ID",
    "COMPOSITION_REGISTRIES",
    "DONOR_CONSERVATIVITY_COUNT",
    "FALSE_TRANSPORT_THEORIES",
    "REPO_ROOT",
    "SHIPPED_ROWS_SHA256",
    "SHIPPED_TRANSPORT_CASES",
    "TARGET_AMBIGUITY",
    "THEORY_CLOSURE_PATH",
    "TRANSPORT_COORDINATES",
    "TRANSPORT_COORDINATE_STATES",
    "TRANSPORT_REFERENCE_ID",
    "WITNESS_ONLY_TRANSPORT_CHECK_ID",
    "canonical_rows_digest",
    "closure_carrying_module",
    "closure_model_space",
    "closure_reference",
    "compose_rules_accepted",
    "completion_classes",
    "composition_agreement",
    "composition_argument_triples",
    "composition_baseline",
    "composition_cases",
    "composition_constraint",
    "composition_handoff_axes",
    "composition_match",
    "composition_replay",
    "composition_stack",
    "donor_axis_diagnosis",
    "donor_axis_multipliers",
    "functions_taking_a_donor_argument",
    "identity_guards",
    "theory_closure_module",
    "transport_authority",
    "transport_baseline",
    "transport_cases",
    "transport_check",
    "transport_constraint",
    "transport_coordinate_states",
    "transport_mapping_only_floor",
    "transport_mapping_only_replay",
    "transport_replay",
    "transport_rule",
    "transport_theory_space",
    "witness_only_transport_baseline",
    "witness_only_transport_constraint",
    "witness_only_transport_replay",
]
