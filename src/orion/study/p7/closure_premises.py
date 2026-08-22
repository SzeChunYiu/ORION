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
literal and the body returned ``64``. It has since been repaired to supply no
value and report ``CANNOT_CHECK``; :func:`transport_authority` reads that repair
back off the shipped file, and the measurement below is unchanged by it.

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

``target_ambiguous_if_missing`` is a different case and stays one.
``admissible_target_completions`` --- the class Definition 14 reads --- is not an
axis of anything the shipped transport checker enumerates, so no rule written
against those 64 states could decide it, and the constraint stays
``UNDECIDABLE_IN_MODEL``. That is a statement about the model rather than about
the premise, and :func:`extended_transport_constraint` is what makes the
difference measurable instead of arguable: the *same* :data:`TARGET_AMBIGUITY`
premise, with the same ``decided_from``, measured over a space that carries a
completion class per case and decides ambiguity with the shipped
``extension_ambiguous``, comes back decided on every case with one admissible
rule. That space is **not** what P7 ships and does not repair the shipped result;
it is the demonstration that the shipped model, not the premise, is what cannot
answer.

Each shipped assertion is transcribed here as an :data:`AssertionReplay` that
takes the premise from a supplied deciding rule instead of from the literal, so
:func:`orion.programme.decided_premises.measure_decision_constraint` can ask how
much of the premise the artifact's own assertions pin down. The fidelity anchors
are :data:`SHIPPED_ROWS_SHA256` and :data:`SHIPPED_TRANSPORT_CASES`: the closure
row list is rebuilt byte for byte before any claim is transcribed, and the
transport space is the checker's own ``product((False, True), repeat=6)``.

The wrong theories registered here are for
:mod:`orion.programme.refutation_capacity`, and they exist to make the
independence of the two questions visible. Every one of them is refuted by
``check_support_transport``, which is exactly why a refutation-capacity pass is
not an answer about the premise.
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

#: Transport states ``check_theory_closure_v2.py`` enumerates; once printed as 64.
SHIPPED_TRANSPORT_CASES = 64

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

#: The check id the extended transport space is measured under. Deliberately not
#: ``check_support_transport``: nothing in the paper enumerates this space, and a
#: shared id would let a demonstration be read as the shipped result.
EXTENDED_TRANSPORT_CHECK_ID = "transport_over_admissible_target_completions"


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
# The transport theorem: 64 states, and an ambiguity premise handed in twice
# ---------------------------------------------------------------------------

def transport_cases() -> tuple[ModelPoint, ...]:
    """The checker's own ``product((False, True), repeat=6)``, named by coordinate."""

    return tuple(
        dict(zip(TRANSPORT_COORDINATES, bits))
        for bits in itertools.product((False, True), repeat=6)
    )


TARGET_AMBIGUITY = Premise(
    premise_id="target_ambiguous_if_missing",
    claim_ref="P7 C4 / FORMAL_CORE_V2 Thm. 6 (support transport)",
    decision_obligation=(
        "whether the admissible target model class contains one completion that "
        "preserves the transported certificate and one that invalidates it"
    ),
    # Named as the manuscript states it. The shipped transport model has six
    # boolean witness coordinates and no completion class, so this is the axis
    # whose absence makes the decision unaskable rather than merely unmade ---
    # and it is the axis :func:`extended_transport_cases` adds to show that the
    # unaskability belongs to the model and not to the premise.
    decided_from=("admissible_target_completions",),
    domain=(False, True),
)


def transport_replay(module: ModuleType) -> AssertionReplay:
    """Replay the audited ``check_support_transport`` under a deciding rule.

    That body evaluated both ambiguity literals on every state; a deciding rule
    selects one, so this asserts the branch it picks. It calls only
    ``transfer_terminal``, whose branches the repair left unchanged.
    """

    transport_type = module.Transport
    cases = transport_cases()

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


def transport_baseline(point: ModelPoint) -> Hashable:
    """The ambiguity value the shipped loop's primary call passes: the literal ``True``."""

    del point
    return True


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
    """The transport states crossed with both ambiguity values.

    Ambiguity is an axis *here* and only here: measuring a false theory of the
    terminal map requires the parameter the map reads, which is precisely the
    parameter the claim says should have been derived.
    """

    return tuple(
        {**point, "target_ambiguous_if_missing": ambiguous}
        for point in transport_cases()
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
            "over all 64 transport-coordinate combinations, a complete witness "
            "transports closure and an incomplete one reopens when the target is "
            "ambiguous and is CANNOT_CHECK otherwise"
        ),
        accepts=accepts,
    )


def transport_constraint(module: ModuleType | None = None) -> DecisionConstraint:
    """Measure how much of C4's ambiguity premise the shipped 64 cases pin down."""

    module = module or theory_closure_module()
    return measure_decision_constraint(
        TARGET_AMBIGUITY,
        check_id="check_support_transport",
        cases=transport_cases(),
        replay=transport_replay(module),
        baseline=transport_baseline,
        opportunity_definition=(
            "the 64 transport-coordinate combinations the checker enumerates; each is "
            "an opportunity for the theorem's assertions to exclude one value of the "
            "ambiguity premise"
        ),
    )


def transport_authority(module: ModuleType | None = None) -> dict[str, Any]:
    """What the shipped transport check's case count is a count *of*.

    The audited body returned ``64`` and ``REPRODUCE_V2_1.md`` reported it as "all
    64 transport-coordinate combinations". Only the complete witness decides its
    terminal from the six enumerated coordinates alone; the other 63 turn on
    Definition 14 target-ambiguity, which the six-coordinate ``Transport`` model
    does not carry. Reporting the split is what keeps a count downstream of an
    undecided premise from being read as a count of decided cases.

    Read off the shipped file, not restated: the repaired
    ``check_support_transport`` returns a ``CheckTerminal`` and its ``terminal``
    and ``checked`` fields are carried through here.
    """

    module = module or theory_closure_module()
    decided = tuple(point for point in transport_cases() if _complete(point))
    downstream = tuple(point for point in transport_cases() if not _complete(point))
    shipped = module.check_support_transport()
    return {
        "enumerated_states": len(transport_cases()),
        "decided_by_the_witness_coordinates": len(decided),
        "downstream_of_the_undecided_premise": len(downstream),
        "shipped_terminal": shipped.terminal,
        "shipped_checked": shipped.checked,
        "shipped_undecidable_premise": shipped.undecidable_premise,
        "shipped_decided_from": shipped.decided_from,
        "reading": (
            f"{len(decided)} of {len(transport_cases())} enumerated states decide their "
            "terminal from the six witness coordinates alone; the remaining "
            f"{len(downstream)} are the mapping downstream of "
            f"{TARGET_AMBIGUITY.premise_id}, so the shipped check is entitled to report "
            f"{shipped.checked} decided case and not {len(transport_cases())}"
        ),
    }


# ---------------------------------------------------------------------------
# The same premise in a model that carries what Definition 14 reads
# ---------------------------------------------------------------------------

#: Target completions built from the shipped ``Completion`` type, over the two
#: observation histories the file's own ambiguity checks use. Ambiguity is a
#: property of the *class*: ``extension_ambiguous`` looks for two members sharing
#: an observed history and disagreeing on ``mandatory_satisfied``. The pool is
#: chosen so that both values arise from that structure rather than from a label.
_COMPLETION_POOL: tuple[tuple[str, tuple[Any, bool, str | None]], ...] = (
    ("open:satisfied", (("query:q", "result:empty"), True, None)),
    ("open:unsatisfied", (("query:q", "result:empty"), False, "unseen")),
    ("closed:satisfied", (("manifest:closed-world",), True, None)),
    ("closed:unsatisfied", (("manifest:closed-world",), False, "hidden-relevant")),
)


def completion_classes(module: ModuleType) -> dict[str, tuple[Any, ...]]:
    """Every non-empty admissible target completion class over the pool.

    Fifteen classes, built with the shipped ``Completion`` dataclass. Seven of
    them are target-ambiguous under the shipped ``extension_ambiguous`` and eight
    are not, so a rule over this axis has something to decide.
    """

    completion = module.Completion
    built = [
        (name, completion(history, satisfied, witness))
        for name, (history, satisfied, witness) in _COMPLETION_POOL
    ]
    classes: dict[str, tuple[Any, ...]] = {}
    for size in range(1, len(built) + 1):
        for chosen in itertools.combinations(built, size):
            classes["+".join(name for name, _ in chosen)] = tuple(
                value for _, value in chosen
            )
    return classes


def extended_transport_cases(module: ModuleType) -> tuple[ModelPoint, ...]:
    """The 64 transport witnesses crossed with the admissible completion classes.

    This is **not** a space the paper enumerates. It exists so that
    "no rule written against the shipped model could decide this premise" is a
    measured contrast rather than an assertion: the axis the premise names is
    present here and absent there, and nothing else differs.
    """

    return tuple(
        {**point, "admissible_target_completions": name}
        for point in transport_cases()
        for name in completion_classes(module)
    )


def extended_transport_baseline(module: ModuleType) -> Assignment:
    """Definition 14, computed: ``extension_ambiguous`` over the case's own class."""

    classes = completion_classes(module)

    def baseline(point: ModelPoint) -> Hashable:
        return bool(
            module.extension_ambiguous(classes[point["admissible_target_completions"]])
        )

    return baseline


def extended_transport_replay(module: ModuleType) -> AssertionReplay:
    """Theorem 6 over the extended space, with the premise computed from the case.

    Two assertions per case and they answer different questions. The first is the
    decision: a checker that computes ambiguity from the completion class does not
    accept a rule that disagrees with ``extension_ambiguous`` on that class, so
    every case excludes one value. The second is the mapping, unchanged from the
    shipped theorem.

    The order matters for what the measurement means. On a *complete* witness the
    terminal is ``TRANSFER_CLOSURE`` whatever ambiguity is, so the mapping alone
    would leave those cases free --- not because the premise was supplied but
    because Theorem 6 does not consume it there. The decision is still made on
    those cases, and asserting it is what says so.
    """

    transport_type = module.Transport
    classes = completion_classes(module)
    cases = extended_transport_cases(module)

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
            elif decided:
                assert terminal == "REOPEN"
            else:
                assert terminal == "CANNOT_CHECK"
        return True

    return replay


def extended_transport_constraint(module: ModuleType | None = None) -> DecisionConstraint:
    """Measure the same premise over the model that carries its decision inputs.

    Same :data:`TARGET_AMBIGUITY`, same ``decided_from``. What differs is whether
    ``admissible_target_completions`` is an axis, and that difference is the whole
    of the shipped check's ``UNDECIDABLE_IN_MODEL``.
    """

    module = module or theory_closure_module()
    return measure_decision_constraint(
        TARGET_AMBIGUITY,
        check_id=EXTENDED_TRANSPORT_CHECK_ID,
        cases=extended_transport_cases(module),
        replay=extended_transport_replay(module),
        baseline=extended_transport_baseline(module),
        opportunity_definition=(
            "the transport witnesses crossed with the admissible target completion "
            "classes; each is an opportunity for the theorem's assertions to exclude "
            "one value of the ambiguity premise"
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
    "EXTENDED_TRANSPORT_CHECK_ID",
    "FALSE_TRANSPORT_THEORIES",
    "REPO_ROOT",
    "SHIPPED_ROWS_SHA256",
    "SHIPPED_TRANSPORT_CASES",
    "TARGET_AMBIGUITY",
    "THEORY_CLOSURE_PATH",
    "TRANSPORT_COORDINATES",
    "TRANSPORT_REFERENCE_ID",
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
    "extended_transport_baseline",
    "extended_transport_cases",
    "extended_transport_constraint",
    "extended_transport_replay",
    "functions_taking_a_donor_argument",
    "identity_guards",
    "theory_closure_module",
    "transport_authority",
    "transport_baseline",
    "transport_cases",
    "transport_check",
    "transport_constraint",
    "transport_replay",
    "transport_rule",
    "transport_theory_space",
]
