"""P7's shipped closure checkers, and the premises they are handed rather than decide.

Two artifacts carry P7's formal authority and both are audited here against the
files on disk rather than against a fixture of this module's own.

``papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py``
is what ``REPRODUCE_V2_1.md`` names for "all 64 transport-coordinate
combinations". Its transport theorem --- the paper's C4, and what
``manuscript/FORMAL_CORE_V2.md`` calls closing "the V1 logical gap" --- is::

    def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool) -> str:
        if t.complete:
            return "TRANSFER_CLOSURE"
        return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"

``check_support_transport`` calls it at ``True`` and again at ``False`` for every
one of the 64 transport states, so ambiguity --- the entire content of C4 --- is
a caller literal. The same file already defines ``extension_ambiguous``, a real
decider used by two other checks, and the transport theorem never calls it.

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
is a literal. The published ``composition_successes: 25`` and
``composition_bridge_countermodels: 25`` are one fact, counted 25 times, at 2 of
the 8 possible argument triples.

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

import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Hashable

from orion.programme.decided_premises import (
    AssertionReplay,
    Assignment,
    DecisionConstraint,
    Premise,
    measure_decision_constraint,
)
from orion.programme.refutation_capacity import FalseTheory, MechanizedCheck, ModelPoint, Rule

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

#: ``support_transport`` as printed by the shipped ``check_theory_closure_v2.py``.
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
    # Named as the manuscript states it. The transport model has six boolean
    # witness coordinates and no completion class, so this is the axis whose
    # absence makes the decision unaskable rather than merely unmade.
    decided_from=("admissible_target_completions",),
    domain=(False, True),
)


def transport_replay(module: ModuleType) -> AssertionReplay:
    """Replay ``check_support_transport``'s assertions under a deciding rule.

    The shipped loop evaluates both ambiguity literals on every state; a deciding
    rule selects one, so this asserts exactly the branch that value picks. Nothing
    else about the shipped body changes.
    """

    transport_type = module.Transport

    def replay(assignment: Assignment) -> bool:
        for point in transport_cases():
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


# ---------------------------------------------------------------------------
# The closure-carrying composition block: 25 pairs, one fact, a literal bridge
# ---------------------------------------------------------------------------

def composition_cases(module: ModuleType) -> tuple[ModelPoint, ...]:
    """The 25 ordered donor pairs the shipped composition loop ranges over."""

    return tuple(
        {"left_donor": left, "right_donor": right}
        for left in module.DONORS
        for right in module.DONORS
    )


BRIDGE_MATCH = Premise(
    premise_id="bridge_match",
    claim_ref="P7.V3.5 (heterogeneous composition under exact bridge binding)",
    decision_obligation=(
        "whether the closure contract the left transform emits is exactly the contract "
        "the right transform requires, or is joined to it by a registered equivalence "
        "bridge"
    ),
    # Both donors *are* axes of the enumerated space, so unlike the ambiguity
    # premise this one could have been decided here and simply was not.
    decided_from=("left_donor", "right_donor"),
    domain=(False, True),
)


def composition_replay(module: ModuleType) -> AssertionReplay:
    """Replay the shipped composition block under a bridge-deciding rule.

    The shipped loop asserts ``compose(c1, c2, True)`` and
    ``not compose(c1, c2, False)`` on every pair; a deciding rule gives the pair
    one bridge state, so this asserts the branch that state selects.
    """

    full = (True,) * len(module.COORDS)

    def replay(assignment: Assignment) -> bool:
        for point in composition_cases(module):
            left_carries = module.carries(True, full)
            right_carries = module.carries(True, full)
            bridged = bool(assignment(point))
            if bridged:
                assert module.compose(left_carries, right_carries, True)
            else:
                assert not module.compose(left_carries, right_carries, False)
        return True

    return replay


def composition_baseline(point: ModelPoint) -> Hashable:
    """The bridge value the shipped success assertion passes: the literal ``True``."""

    del point
    return True


def composition_constraint(module: ModuleType | None = None) -> DecisionConstraint:
    """Measure how much of P7.V3.5's bridge premise the shipped 25 pairs pin down."""

    module = module or closure_carrying_module()
    return measure_decision_constraint(
        BRIDGE_MATCH,
        check_id="p7_x2_composition_block",
        cases=composition_cases(module),
        replay=composition_replay(module),
        baseline=composition_baseline,
        opportunity_definition=(
            "the 25 ordered donor-transform pairs the checker enumerates; each is an "
            "opportunity for the composition assertions to exclude one value of the "
            "intermediate-contract premise"
        ),
    )


def composition_argument_triples(module: ModuleType) -> tuple[tuple[bool, bool, bool], ...]:
    """The distinct ``(c1, c2, bridge_match)`` triples the shipped block evaluates.

    Two of the eight, because ``c1`` and ``c2`` are the same constant on every
    pair and the bridge is a literal. What the block constrains about ``compose``
    is exactly what those two points constrain, which is why a rule that ignores
    both operands survives it.
    """

    full = (True,) * len(module.COORDS)
    carried = module.carries(True, full)
    return tuple(sorted({(carried, carried, True), (carried, carried, False)}))


def compose_rules_accepted(module: ModuleType) -> tuple[int, int]:
    """How many of the 256 Boolean composition rules the shipped block accepts.

    Reported as ``(accepted, total)``. The gap between them is the block's entire
    constraint on P7's composition law.
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


__all__ = [
    "BRIDGE_MATCH",
    "CLOSURE_CARRYING_PATH",
    "CLOSURE_CARRYING_RESULT_PATH",
    "COMPOSITION_REFERENCE_ID",
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
    "composition_argument_triples",
    "composition_baseline",
    "composition_cases",
    "composition_constraint",
    "composition_replay",
    "theory_closure_module",
    "transport_baseline",
    "transport_cases",
    "transport_check",
    "transport_constraint",
    "transport_replay",
    "transport_rule",
    "transport_theory_space",
]
