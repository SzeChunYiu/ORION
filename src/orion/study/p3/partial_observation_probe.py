"""The partial-observation failure channel for the P3 identity atlas (P3-U-T5).

P3-U-T5 asks for an identity coordinate *discovered from failure*, and its
unblock says to mine each false merge and each false split for a candidate
discriminating coordinate. Measured with
:mod:`orion.study.p3.public_reference_audit` on all three atlases P3 owns,
ORION commits **zero** false merges and **zero** false splits. The set the
unblock instruction says to mine is empty, and mining harder cannot change that.

The one failure channel that could produce a candidate is over-resolution:
asserting a relation the available coordinates do not determine. Its guard,
``P3.OVERRESOLVED_UNRESOLVED_CASE``, has a zero denominator on every atlas --- no
P3 atlas contains a gold-``UNRESOLVED`` case --- and a census over all nine
coordinates of :class:`~orion.knowledge.semantics.ScientificMeaningProjection`
across all 88 cases in the three atlases finds **no partially-observed pair at
all**: every coordinate is observed on both sides of a pair or absent on both.
So the branch of the identity rule that reads an absent coordinate has never
been exercised by P3's evidence.

That branch is not uniform. ``compare_meaning`` overloads the single "absent"
value three ways in one function: the five list coordinates and the two string
coordinates read absence as *agreement* (``_same_or_empty`` and the
``left.X and right.X`` guards fall through), ``polarity`` reads
``Polarity.UNKNOWN`` as *agreement*, and ``modality`` reads ``Modality.UNKNOWN``
as *a distinct value* --- separation-ward. The projection type has no third value
distinguishing "assessed and empty" from "never assessed", so the rule has to
guess, and it guesses differently in different places. This is the
``not None is True`` shape of
``research/failures/2026-08-vacuous-guard-zero-denominator/`` pushed down into
the coordinate type itself.

This module opens that channel and measures it. It redacts one coordinate on one
side of cases the frozen atlases already contain, scores the result with the
existing three-valued guard machinery of
:mod:`orion.study.p3.identity_opportunity`, and executes the unblock's mining
instruction as a census over every failure any arm commits.

Protocol: ``papers/paper-03-global-knowledge-portrait/protocol/
P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`` and its JSON twin. The
runner recomputes the twin's parameter digest from its own constants and refuses
to run on a mismatch, and it refuses to report an arm number over a probe that
fails the construction precondition.

**Amendment 001 (2026-08-22).** As frozen, gate ``G6_HARM_A1`` --- "A1 changes 0
decisions on the intact corpora" --- had no denominator and said so: with no
one-sided absence anywhere, A1 could not fire, and its zero was structural. That
zero is a fact about three corpora, not about what "intact" means. Observedness
is a per-projection property, nothing in ``ScientificMeaningProjection``
constrains it across a pair, and the five branches of ``compare_meaning`` listed
above are reachable *only* on a pair observed on one side and not the other; they
are untested, not unreachable. The amendment adds a fourth intact corpus,
``research/p3-partial-observation-harm-v1/``, built by
:mod:`orion.study.p3.partial_observation_harm_build`, whose pairs do state a
coordinate on one side only. No threshold moves. A gate reading "changes 0
decisions" can only be left alone or failed by a corpus added to it, never
passed, so supplying its denominator cannot manufacture a positive --- and it
does not: A1 destroys correct answers over it, and G6 fails on evidence.

Nothing here edits ``orion.knowledge.semantics``; the candidate rules are
study-local arms. Nothing here edits a frozen atlas, result or receipt, and the
2026-08-21 freeze document and its twin are left byte-identical.

Run it::

    python -m orion.study.p3.partial_observation_probe --repo-root . \
        --output <result>.json --probe-output <probe>.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    compare_meaning,
)
from orion.programme.guard_exercise import GuardAssessment, assess_guard
from orion.programme.records import Outcome
from orion.study.p3_public_reference import (
    NONMERGE_RELATIONS,
    load_jsonl,
    projection_from_dict,
    sha256_json,
)

from .identity_opportunity import (
    IdentityDecisionKind,
    IdentityDecisionLedger,
    build_identity_ledger,
    classify_identity_decision,
)

RESULT_SCHEMA_VERSION = "orion.p3.partial-observation-result.v1"
PROBE_SCHEMA_VERSION = "orion.p3.partial-observation-probe-case.v1"

FREEZE_DOCUMENT = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md"
)
ORIGINAL_FREEZE_TWIN = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.json"
)

# Amendment 001 (2026-08-22) adds a fourth intact corpus so that G6_HARM_A1 has a
# denominator. The 2026-08-21 freeze and its twin are left byte-identical: the
# amendment is a separate document carrying its own parameter digest, and the
# runner binds to it. Nothing the original document decided is reopened --- no
# threshold moves, no gate is renamed, no adjudicated case is touched.
AMENDMENT_DOCUMENT = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_001.md"
)
AMENDMENT_TWIN = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_001.json"
)

#: The twin the runner checks itself against. Points at the amendment while one
#: is in force, so a digest drift is caught against the record actually running.
FREEZE_TWIN = AMENDMENT_TWIN

CLAIM_SCOPE = "PARTIAL_OBSERVATION_OF_FROZEN_ATLASES_ONLY"

# --------------------------------------------------------------------------
# Coordinates and their absent values (freeze section 4.1)
# --------------------------------------------------------------------------

# The absent value of each coordinate, i.e. the single value the type uses for
# both "assessed, nothing there" and "never assessed". The whole defect lives in
# that overload, so the table is written out rather than inferred from defaults.
ABSENT_VALUE: dict[str, Any] = {
    "referent_ids": (),
    "construct_ids": (),
    "measurement_ids": (),
    "temporal_context_ids": (),
    "assumption_ids": (),
    "attribution_id": "",
    "discourse_relation": "",
    "polarity": Polarity.UNKNOWN,
    "modality": Modality.UNKNOWN,
}

COORDINATES: tuple[str, ...] = tuple(ABSENT_VALUE)

# How ``compare_meaning`` reads an absent value on one side, read off the source.
# Eight coordinates merge-ward, one separation-ward: the inconsistency the freeze
# names in section 1.2.
ABSENCE_READING: dict[str, str] = {
    "referent_ids": "AGREEMENT",
    "construct_ids": "AGREEMENT",
    "measurement_ids": "AGREEMENT",
    "temporal_context_ids": "AGREEMENT",
    "assumption_ids": "AGREEMENT",
    "attribution_id": "AGREEMENT",
    "discourse_relation": "AGREEMENT",
    "polarity": "AGREEMENT",
    "modality": "DISTINCT_VALUE",
}

SIDES: tuple[str, ...] = ("left", "right")


def observed(projection: ScientificMeaningProjection, coordinate: str) -> bool:
    """True when the coordinate holds anything other than its absent value.

    The projection type cannot say more than this: "observed and empty" and
    "never observed" are the same value, which is the candidate coordinate this
    study is about.
    """

    if coordinate not in ABSENT_VALUE:
        raise KeyError(f"{coordinate} is not one of the nine identity coordinates")
    return getattr(projection, coordinate) != ABSENT_VALUE[coordinate]


def discriminating_coordinates(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> tuple[str, ...]:
    """Coordinates on which both sides are observed and the values differ.

    This is the freeze's formalisation of "mine the failure for a candidate
    discriminating coordinate": what, in the representation as it stands, could
    have told these two apart. An empty tuple means nothing in the
    representation could.
    """

    return tuple(
        coordinate
        for coordinate in COORDINATES
        if observed(left, coordinate)
        and observed(right, coordinate)
        and getattr(left, coordinate) != getattr(right, coordinate)
    )


# --------------------------------------------------------------------------
# Arms (freeze section 5)
# --------------------------------------------------------------------------

Arm = Callable[[ScientificMeaningProjection, ScientificMeaningProjection], MeaningRelation]

ARM_CURRENT = "A0_orion_current"
ARM_ASYMMETRIC = "A1_observedness_asymmetric"
ARM_STRICT = "A2_observedness_strict"


def arm_orion_current(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """The system that produced the negative: ``compare_meaning`` verbatim."""

    return compare_meaning(left, right).relation


def _one_sided_absences(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> tuple[str, ...]:
    return tuple(
        coordinate
        for coordinate in COORDINATES
        if observed(left, coordinate) != observed(right, coordinate)
    )


def _any_sided_absences(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> tuple[str, ...]:
    return tuple(
        coordinate
        for coordinate in COORDINATES
        if not observed(left, coordinate) or not observed(right, coordinate)
    )


def arm_observedness_asymmetric(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """Abstain when a coordinate is absent on exactly one side."""

    if _one_sided_absences(left, right):
        return MeaningRelation.UNRESOLVED
    return compare_meaning(left, right).relation


def arm_observedness_strict(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """Abstain when a coordinate is absent on either side.

    Two silences are not agreement under this reading. Its cost on the intact
    atlases is a lower bound on the information the missing third value carries.
    """

    if _any_sided_absences(left, right):
        return MeaningRelation.UNRESOLVED
    return compare_meaning(left, right).relation


ARMS: dict[str, Arm] = {
    ARM_CURRENT: arm_orion_current,
    ARM_ASYMMETRIC: arm_observedness_asymmetric,
    ARM_STRICT: arm_observedness_strict,
}
ARM_ORDER: tuple[str, ...] = (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)


# --------------------------------------------------------------------------
# Corpora (freeze section 4.3)
# --------------------------------------------------------------------------

INTACT_DERIVATION = "INTACT_DERIVATION"
INTACT_HELDOUT_REAL = "INTACT_HELDOUT_REAL"
INTACT_HELDOUT_SYNTHETIC = "INTACT_HELDOUT_SYNTHETIC"
INTACT_HARM_SYNTHETIC = "INTACT_HARM_SYNTHETIC"
PROBE_DERIVATION = "PROBE_DERIVATION"
PROBE_HELDOUT_REAL = "PROBE_HELDOUT_REAL"
PROBE_HELDOUT_SYNTHETIC = "PROBE_HELDOUT_SYNTHETIC"

INTACT_SOURCES: dict[str, str] = {
    INTACT_DERIVATION: (
        "papers/paper-03-global-knowledge-portrait/gold/adjudicated/"
        "public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    ),
    INTACT_HELDOUT_REAL: (
        "papers/paper-03-global-knowledge-portrait/gold/adjudicated/"
        "public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    ),
    INTACT_HELDOUT_SYNTHETIC: "research/p3-coordinate-necessity-v1/cases.jsonl",
    # Amendment 001. Added because G6_HARM_A1 had no denominator: the three
    # corpora above state every coordinate on both sides of every pair or on
    # neither, so A1 could not fire on any of them and its zero was structural.
    # See AMENDMENT_DOCUMENT and research/p3-partial-observation-harm-v1/.
    INTACT_HARM_SYNTHETIC: "research/p3-partial-observation-harm-v1/cases.jsonl",
}

# The redaction of section 4.2 is defined only on a pair that states each
# coordinate on both sides or on neither: silencing a coordinate of a pair that
# already has a one-sided absence yields a probe case with two of them, which C2
# rejects. INTACT_HARM_SYNTHETIC exists precisely because it has one-sided
# absences, so it is a harm corpus and not a probe parent. The three corpora
# frozen on 2026-08-21 are unaffected --- their one-sided-absence census is zero.
PROBE_OF: dict[str, str] = {
    INTACT_DERIVATION: PROBE_DERIVATION,
    INTACT_HELDOUT_REAL: PROBE_HELDOUT_REAL,
    INTACT_HELDOUT_SYNTHETIC: PROBE_HELDOUT_SYNTHETIC,
}

INTACT_ORDER: tuple[str, ...] = (
    INTACT_DERIVATION,
    INTACT_HELDOUT_REAL,
    INTACT_HELDOUT_SYNTHETIC,
    INTACT_HARM_SYNTHETIC,
)

#: The intact corpora frozen on 2026-08-21, every one of them fully symmetric in
#: observedness. Kept as a named tuple so the assertions that pin *their*
#: properties --- zero partially observed pairs, an unexercised over-resolution
#: guard --- stay attached to the corpora they are true of instead of silently
#: widening to whatever is added later.
SYMMETRIC_INTACT_ORDER: tuple[str, ...] = (
    INTACT_DERIVATION,
    INTACT_HELDOUT_REAL,
    INTACT_HELDOUT_SYNTHETIC,
)

#: Intact corpora that do contain one-sided absences, i.e. the denominator that
#: makes G6_HARM_A1 a measurement.
PARTIALLY_OBSERVED_INTACT_ORDER: tuple[str, ...] = (INTACT_HARM_SYNTHETIC,)


# --------------------------------------------------------------------------
# Probe construction (freeze section 4.2)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbeCase:
    """One frozen case with one coordinate silenced on one side.

    ``gold`` is ``UNRESOLVED`` because after the redaction the pair is
    observationally identical to one that genuinely agrees on that coordinate:
    no procedure reading only the projections can separate the two worlds, so any
    other relation is asserted without warrant. ``parent_gold`` carries the
    adjudicated relation so the alternative scoring of freeze section 3.2 can be
    computed from the same decisions.
    """

    case_id: str
    parent_case_id: str
    corpus_id: str
    coordinate: str
    side: str
    left: ScientificMeaningProjection
    right: ScientificMeaningProjection
    parent_left: ScientificMeaningProjection
    parent_right: ScientificMeaningProjection
    parent_gold: MeaningRelation

    gold: MeaningRelation = MeaningRelation.UNRESOLVED

    def __post_init__(self) -> None:
        if self.side not in SIDES:
            raise ValueError(f"{self.case_id}: side must be one of {SIDES}")
        if self.coordinate not in ABSENT_VALUE:
            raise ValueError(f"{self.case_id}: {self.coordinate} is not an identity coordinate")
        if self.gold is not MeaningRelation.UNRESOLVED:
            raise ValueError(f"{self.case_id}: probe gold is UNRESOLVED by the freeze")


def redactable_coordinates(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
    gold: MeaningRelation,
) -> tuple[str, ...]:
    """Coordinates on which this case can be silenced, per freeze section 4.2.

    All four conditions together: observed on both sides, values differ, gold
    forbids merging, and ``compare_meaning`` already reproduces gold on the
    untouched pair. The last one keeps a probe failure from being inherited from
    a pre-existing error.

    Amendment 001 adds a fifth, on the parent rather than on the coordinate: the
    pair must not already have a one-sided absence. Redacting a pair that has one
    produces a probe case with two, which C2 rejects, so the campaign would abort
    on ``CONSTRUCTION_PRECONDITION_FAILED`` rather than report the malformed case.
    Refusing the parent is the same judgement made one step earlier. It is a
    no-op on the three corpora frozen on 2026-08-21, whose one-sided-absence
    census is zero everywhere; ``build_probe`` emits exactly the 12, 8 and 28
    cases it emitted before.
    """

    if gold not in NONMERGE_RELATIONS:
        return ()
    if compare_meaning(left, right).relation is not gold:
        return ()
    if _one_sided_absences(left, right):
        return ()
    return discriminating_coordinates(left, right)


def build_probe(cases: Sequence[Mapping[str, Any]], corpus_id: str) -> tuple[ProbeCase, ...]:
    """Two probe cases per redactable (case, coordinate): silence left, silence right."""

    probe: list[ProbeCase] = []
    for case in cases:
        left = projection_from_dict(case["left_projection"])
        right = projection_from_dict(case["right_projection"])
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        parent_case_id = str(case["case_id"])
        for coordinate in redactable_coordinates(left, right, gold):
            absent = ABSENT_VALUE[coordinate]
            for side in SIDES:
                if side == "left":
                    new_left, new_right = replace(left, **{coordinate: absent}), right
                else:
                    new_left, new_right = left, replace(right, **{coordinate: absent})
                probe.append(
                    ProbeCase(
                        case_id=f"{parent_case_id}|redact={coordinate}|side={side}",
                        parent_case_id=parent_case_id,
                        corpus_id=corpus_id,
                        coordinate=coordinate,
                        side=side,
                        left=new_left,
                        right=new_right,
                        parent_left=left,
                        parent_right=right,
                        parent_gold=gold,
                    )
                )
    return tuple(probe)


def _projection_json(projection: ScientificMeaningProjection) -> dict[str, Any]:
    return {
        "projection_id": projection.projection_id,
        "source_id": projection.source_id,
        "source_span": projection.source_span,
        "predicate": projection.predicate,
        "argument_roles": [list(item) for item in projection.argument_roles],
        "referent_ids": list(projection.referent_ids),
        "construct_ids": list(projection.construct_ids),
        "measurement_ids": list(projection.measurement_ids),
        "temporal_context_ids": list(projection.temporal_context_ids),
        "discourse_relation": projection.discourse_relation,
        "attribution_id": projection.attribution_id,
        "polarity": projection.polarity.value,
        "modality": projection.modality.value,
        "assumption_ids": list(projection.assumption_ids),
        "unresolved_ambiguities": list(projection.unresolved_ambiguities),
    }


def probe_case_json(case: ProbeCase) -> dict[str, Any]:
    return {
        "schema_version": PROBE_SCHEMA_VERSION,
        "case_id": case.case_id,
        "parent_case_id": case.parent_case_id,
        "corpus_id": case.corpus_id,
        "redacted_coordinate": case.coordinate,
        "redacted_side": case.side,
        "absence_reading_in_compare_meaning": ABSENCE_READING[case.coordinate],
        "expected": {"meaning_relation": case.gold.value},
        "parent_expected": {"meaning_relation": case.parent_gold.value},
        "left_projection": _projection_json(case.left),
        "right_projection": _projection_json(case.right),
    }


# --------------------------------------------------------------------------
# Construction precondition (freeze section 4.4)
# --------------------------------------------------------------------------


def construction_precondition(probe: Sequence[ProbeCase], *, require_nonempty: bool) -> dict[str, Any]:
    """C1-C5, evaluated on the probe alone, before any arm is scored.

    A probe that lacks the intended structure is not the world under study, and
    an arm number over it would mean nothing. Reported as a dict of named checks
    so a failure says which one.
    """

    checks: dict[str, bool] = {
        "C1_probe_non_empty": (len(probe) > 0) if require_nonempty else True,
        "C2_exactly_one_coordinate_absent_on_exactly_one_side": True,
        "C3_differs_from_parent_on_exactly_that_field": True,
        "C4_parent_gold_is_non_merge_and_reproduced": True,
        "C5_probe_gold_is_unresolved": True,
    }
    offenders: dict[str, list[str]] = {name: [] for name in checks}

    for case in probe:
        left, right = case.left, case.right
        absences = _one_sided_absences(left, right)
        mirror = right if case.side == "left" else left
        silenced = left if case.side == "left" else right
        if absences != (case.coordinate,) or observed(silenced, case.coordinate):
            checks["C2_exactly_one_coordinate_absent_on_exactly_one_side"] = False
            offenders["C2_exactly_one_coordinate_absent_on_exactly_one_side"].append(case.case_id)
        elif not observed(mirror, case.coordinate):
            checks["C2_exactly_one_coordinate_absent_on_exactly_one_side"] = False
            offenders["C2_exactly_one_coordinate_absent_on_exactly_one_side"].append(case.case_id)

        expected_left = (
            replace(case.parent_left, **{case.coordinate: ABSENT_VALUE[case.coordinate]})
            if case.side == "left"
            else case.parent_left
        )
        expected_right = (
            replace(case.parent_right, **{case.coordinate: ABSENT_VALUE[case.coordinate]})
            if case.side == "right"
            else case.parent_right
        )
        if left != expected_left or right != expected_right:
            checks["C3_differs_from_parent_on_exactly_that_field"] = False
            offenders["C3_differs_from_parent_on_exactly_that_field"].append(case.case_id)

        if case.parent_gold not in NONMERGE_RELATIONS or (
            compare_meaning(case.parent_left, case.parent_right).relation is not case.parent_gold
        ):
            checks["C4_parent_gold_is_non_merge_and_reproduced"] = False
            offenders["C4_parent_gold_is_non_merge_and_reproduced"].append(case.case_id)

        if case.gold is not MeaningRelation.UNRESOLVED:
            checks["C5_probe_gold_is_unresolved"] = False
            offenders["C5_probe_gold_is_unresolved"].append(case.case_id)

    return {
        "n_probe_cases": len(probe),
        "checks": checks,
        "offenders": {name: sorted(ids)[:8] for name, ids in offenders.items() if ids},
        "passed": all(checks.values()),
    }


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScoredCase:
    """One arm's decision on one pair, with the pair kept for the mining census."""

    case_id: str
    arm_id: str
    gold: MeaningRelation
    predicted: MeaningRelation
    left: ScientificMeaningProjection
    right: ScientificMeaningProjection

    @property
    def kind(self) -> IdentityDecisionKind:
        return classify_identity_decision(self.gold, self.predicted)


def score_pairs(
    pairs: Sequence[tuple[str, ScientificMeaningProjection, ScientificMeaningProjection, MeaningRelation]],
) -> tuple[ScoredCase, ...]:
    """Run every arm over every pair. No arm sees gold or the corpus id."""

    return tuple(
        ScoredCase(
            case_id=case_id,
            arm_id=arm_id,
            gold=gold,
            predicted=ARMS[arm_id](left, right),
            left=left,
            right=right,
        )
        for arm_id in ARM_ORDER
        for case_id, left, right, gold in pairs
    )


def ledger_from_scored(corpus_id: str, scored: Sequence[ScoredCase]) -> IdentityDecisionLedger:
    return build_identity_ledger(
        corpus_id,
        [(item.case_id, item.arm_id, item.gold, item.predicted) for item in scored],
    )


FAILURE_KINDS = frozenset(
    {
        IdentityDecisionKind.FALSE_MERGE,
        IdentityDecisionKind.FALSE_SPLIT,
        IdentityDecisionKind.MERGED_WHERE_GOLD_UNRESOLVED,
        IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED,
    }
)


def mining_census(scored: Sequence[ScoredCase]) -> dict[str, Any]:
    """Freeze section 7.1: for every failure, what could have told the pair apart.

    A non-empty ``discriminating_coordinates`` set means the failure is explained
    by a coordinate ORION already carries. An empty set means no coordinate in
    the representation can discriminate the pair, and the missing thing is not a
    dimension.
    """

    rows: list[dict[str, Any]] = []
    for item in scored:
        if item.kind not in FAILURE_KINDS:
            continue
        coords = discriminating_coordinates(item.left, item.right)
        rows.append(
            {
                "case_id": item.case_id,
                "arm_id": item.arm_id,
                "kind": item.kind.value,
                "gold": item.gold.value,
                "predicted": item.predicted.value,
                "discriminating_coordinates": list(coords),
                "demands_a_coordinate_orion_lacks": not coords,
            }
        )
    empty = sum(1 for row in rows if row["demands_a_coordinate_orion_lacks"])
    return {
        "n_failures": len(rows),
        "n_with_no_discriminating_coordinate": empty,
        "n_explained_by_an_existing_coordinate": len(rows) - empty,
        "fraction_with_no_discriminating_coordinate": (empty / len(rows)) if rows else None,
        "failures": rows,
    }


def _assessment_json(assessment: GuardAssessment) -> dict[str, Any]:
    return assessment.as_json()


def assess_corpus(
    corpus_id: str, ledger: IdentityDecisionLedger
) -> dict[str, dict[str, Any]]:
    """Both single-arm guards, three-valued, for every arm on one corpus."""

    return {
        arm: {
            "decision_kinds": ledger.kind_counts(arm),
            "separations_emitted": ledger.separations_emitted(arm),
            "over_resolution": _assessment_json(
                assess_guard(ledger.unresolved_calibration_exercise(arm))
            ),
            "false_merge": _assessment_json(assess_guard(ledger.false_merge_exercise(arm))),
        }
        for arm in ledger.arms
    }


def _over_resolution_rate(payload: Mapping[str, Any], arm: str) -> float | None:
    """The arm's over-resolution rate, or ``None`` when the guard was not exercised.

    ``None`` is propagated rather than coerced to 0.0: a rate of zero out of zero
    opportunities is the substitution this whole lane exists to prevent, and every
    gate that reads this value tests for ``None`` explicitly before comparing.
    """

    exercises = payload[arm]["over_resolution"]["exercises"]
    for exercise in exercises:
        if exercise["arm_id"] == arm:
            rate = exercise["violation_rate"]
            return None if rate is None else float(rate)
    return None


# --------------------------------------------------------------------------
# Harm measurement (freeze gates G6, G7)
# --------------------------------------------------------------------------


def harm_against_current(scored: Sequence[ScoredCase], arm_id: str) -> dict[str, Any]:
    """How many intact decisions this arm moves, and how many correct ones it destroys."""

    baseline = {item.case_id: item for item in scored if item.arm_id == ARM_CURRENT}
    candidate = [item for item in scored if item.arm_id == arm_id]
    changed = [item for item in candidate if item.predicted is not baseline[item.case_id].predicted]
    destroyed = [
        item
        for item in changed
        if baseline[item.case_id].predicted is baseline[item.case_id].gold
        and item.predicted is not item.gold
    ]
    return {
        "arm_id": arm_id,
        "n_cases": len(candidate),
        "decisions_changed": len(changed),
        "fraction_changed": (len(changed) / len(candidate)) if candidate else None,
        "correct_answers_destroyed": len(destroyed),
        "changed_case_ids": sorted(item.case_id for item in changed)[:8],
    }


def one_sided_absence_census(
    pairs: Sequence[tuple[str, ScientificMeaningProjection, ScientificMeaningProjection, MeaningRelation]],
) -> dict[str, Any]:
    """How many intact pairs have a coordinate absent on exactly one side.

    Zero makes the A1 harm gate vacuous, and the freeze pre-declares that. This
    function is what makes the vacuity a measured statement rather than an
    assumption.
    """

    counts: dict[str, int] = {coordinate: 0 for coordinate in COORDINATES}
    total = 0
    for _case_id, left, right, _gold in pairs:
        absences = _one_sided_absences(left, right)
        if absences:
            total += 1
        for coordinate in absences:
            counts[coordinate] += 1
    return {
        "n_pairs": len(pairs),
        "n_pairs_with_a_one_sided_absence": total,
        "by_coordinate": {name: value for name, value in counts.items() if value},
    }


# --------------------------------------------------------------------------
# Frozen parameter block and its digest (freeze section 8.1)
# --------------------------------------------------------------------------

GATES: dict[str, Any] = {
    "G1_CONSTRUCTION": {
        "statement": "C1-C5 of freeze section 4.4 hold on every probe corpus",
        "blocking": True,
    },
    "G2_CHANNEL_OPENED": {
        "statement": (
            "A0_orion_current's P3.OVERRESOLVED_UNRESOLVED_CASE exercise on PROBE_DERIVATION "
            "has opportunities >= 1"
        ),
        "min_opportunities": 1,
        "blocking": True,
    },
    "G3_FAILURE_ON_REAL_CASES": {
        "statement": (
            "A0_orion_current's over-resolution violation rate on PROBE_DERIVATION >= 0.90"
        ),
        "min_violation_rate": 0.90,
        "blocking": True,
        "primary": True,
    },
    "G4_HELD_OUT": {
        "statement": (
            "A0_orion_current's over-resolution violation rate >= 0.90 on PROBE_HELDOUT_REAL "
            "and on PROBE_HELDOUT_SYNTHETIC"
        ),
        "min_violation_rate": 0.90,
        "blocking": False,
    },
    "G5_MINING_YIELD": {
        "statement": (
            "(a) every failure on an intact corpus has a non-empty discriminating-coordinate "
            "set drawn from the nine existing coordinates; (b) every over-resolution on a probe "
            "corpus has an empty set"
        ),
        "blocking": False,
    },
    "G6_HARM_A1": {
        "statement": "A1_observedness_asymmetric changes 0 decisions on all three intact corpora",
        "blocking": True,
        "pre_declared_vacuous": True,
        "vacuity_note": (
            "the intact corpora contain zero one-sided-absent coordinates, so A1 cannot fire on "
            "them; this gate passes for a structural reason and may not be cited as evidence "
            "that A1 is safe"
        ),
        "amendment_001": {
            "statement_as_amended": (
                "A1_observedness_asymmetric changes 0 decisions on every intact corpus, now "
                "including INTACT_HARM_SYNTHETIC"
            ),
            "denominator_corpus": INTACT_HARM_SYNTHETIC,
            "threshold_unchanged": True,
            "note": (
                "the vacuity note above is a true statement about the three corpora frozen on "
                "2026-08-21 and is left standing. It described a property of those corpora, not "
                "of what 'intact' means: observedness is a per-projection fact and "
                "compare_meaning carries branches reachable only on a one-sided absence. "
                "Amendment 001 adds an intact corpus that has them. The gate's threshold is not "
                "relaxed --- a harm gate reading 'changes 0 decisions' can only be left alone or "
                "failed by a corpus added to it, never passed, which is why supplying its "
                "denominator cannot manufacture a positive."
            ),
        },
    },
    "G7_COST_A2": {
        "statement": (
            "report the number and fraction of intact decisions A2_observedness_strict changes "
            "and how many destroy a correct answer"
        ),
        "blocking": False,
    },
    "G8_NOVELTY": {
        "statement": (
            "a candidate counts as a new identity coordinate only if two fully observed "
            "projections can differ on it; observation_status is constant across all fully "
            "observed pairs, so this gate fails by construction"
        ),
        "blocking": True,
        "fails_by_construction": True,
    },
}

VERDICT_CHANNEL = "CHANNEL_OPENED_FAILURE_DEMONSTRATED"
VERDICT_HELDOUT = "FAILURE_CARRIES_TO_HELDOUT_STRATA"
VERDICT_T5 = "T5_NOT_DISCHARGED__CANDIDATE_IS_NOT_A_NEW_IDENTITY_AXIS"
VERDICT_NO_NEW_COORDINATE = "NO_NEW_COORDINATE_DEMANDED_BY_ANY_FAILURE_ON_RECORD"
VERDICT_CONSTRUCTION_FAILED = "CONSTRUCTION_PRECONDITION_FAILED"
VERDICT_CHANNEL_NOT_OPENED = "CHANNEL_NOT_OPENED"
VERDICT_FAILURE_WEAKER = "FAILURE_WEAKER_THAN_STATED"

CANDIDATE_COORDINATE = {
    "name": "observation_status",
    "definition": (
        "a per-coordinate value in {OBSERVED, NOT_OBSERVED} attached to each projection, so that "
        "'this source states no measurement' and 'this source was never assessed for a "
        "measurement' are different states of the projection"
    ),
    "mined_from": (
        "silencing one side of the coordinate that carries the decision converts every separation "
        "ORION makes into a merge, reported with the same confidence"
    ),
    "is_a_new_identity_axis": False,
    "why_not": (
        "it is constant across all fully observed pairs, so no two fully observed projections can "
        "differ on it; it is a third value on the existing axes, not a new axis"
    ),
}

FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "amendment": {
        "id": "AMENDMENT_001",
        "date": "2026-08-22",
        "document": AMENDMENT_DOCUMENT,
        "reason": (
            "G6_HARM_A1 was pre-declared vacuous and ran as CANNOT_CHECK: the three intact "
            "corpora state every coordinate on both sides of every pair or on neither, so A1 "
            "could not fire and 0 changes was a structural zero"
        ),
        "changes": [
            "adds INTACT_HARM_SYNTHETIC, a fourth intact corpus that does contain one-sided "
            "absences, built by orion.study.p3.partial_observation_harm_build",
            "excludes that corpus from probe construction, because the redaction of section 4.2 "
            "is defined only on a parent with no one-sided absence",
            "adds the same condition to redactable_coordinates, a no-op on the three corpora "
            "frozen on 2026-08-21",
            "reports correct_answers_destroyed and a per-corpus breakdown on G6",
        ],
        "unchanged": [
            "every gate threshold, including G6's 0",
            "the coordinate table, the absent-value table, the arms and the probe gold",
            "the three corpora frozen on 2026-08-21 and every case in them",
            "the 2026-08-21 freeze document and its twin, both byte-identical",
        ],
    },
    "claim_scope": CLAIM_SCOPE,
    "coordinates": list(COORDINATES),
    "absent_values": {
        name: (list(value) if isinstance(value, tuple) else getattr(value, "value", value))
        for name, value in ABSENT_VALUE.items()
    },
    "absence_reading_in_compare_meaning": dict(ABSENCE_READING),
    "arms": list(ARM_ORDER),
    "sides_per_redactable_pair": list(SIDES),
    "intact_sources": dict(INTACT_SOURCES),
    "symmetric_intact_sources": list(SYMMETRIC_INTACT_ORDER),
    "partially_observed_intact_sources": list(PARTIALLY_OBSERVED_INTACT_ORDER),
    "probe_of": dict(PROBE_OF),
    "probe_gold": MeaningRelation.UNRESOLVED.value,
    "secondary_gold": "PARENT_GOLD",
    "redactability_conditions": [
        "observed on both sides",
        "observed values differ",
        "parent gold is in NONMERGE_RELATIONS",
        "compare_meaning reproduces parent gold on the untouched pair",
        "the parent pair has no one-sided absence of its own (amendment 001)",
    ],
    "primary_outcome": (
        "P3.OVERRESOLVED_UNRESOLVED_CASE for A0_orion_current on PROBE_DERIVATION, assessed by "
        "assess_guard at max_violation_rate = 0.0"
    ),
    "max_violation_rate": 0.0,
    "gates": GATES,
    "candidate_coordinate": CANDIDATE_COORDINATE,
    "verdicts": {
        "channel": VERDICT_CHANNEL,
        "heldout": VERDICT_HELDOUT,
        "t5": VERDICT_T5,
        "no_new_coordinate": VERDICT_NO_NEW_COORDINATE,
        "construction_failed": VERDICT_CONSTRUCTION_FAILED,
        "channel_not_opened": VERDICT_CHANNEL_NOT_OPENED,
        "failure_weaker": VERDICT_FAILURE_WEAKER,
    },
}


def frozen_digest() -> str:
    return sha256_json(FROZEN_PARAMETERS)


class FreezeViolation(RuntimeError):
    """Raised when the runner's constants no longer match the frozen record."""


def verify_against_twin(repo_root: Path) -> dict[str, Any]:
    """Compare the runner's own parameter digest with the frozen twin's."""

    twin_path = repo_root / FREEZE_TWIN
    if not twin_path.exists():
        raise FreezeViolation(f"freeze twin missing: {twin_path}")
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    recorded = twin.get("parameters_sha256")
    computed = frozen_digest()
    if recorded != computed:
        raise FreezeViolation(
            "runner parameters do not match the frozen record: "
            f"recorded {recorded}, computed {computed}"
        )
    return {"parameters_sha256": computed, "freeze_twin": FREEZE_TWIN}


# --------------------------------------------------------------------------
# Campaign
# --------------------------------------------------------------------------


def _intact_pairs(
    cases: Sequence[Mapping[str, Any]],
) -> list[tuple[str, ScientificMeaningProjection, ScientificMeaningProjection, MeaningRelation]]:
    pairs = []
    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        pairs.append(
            (
                str(case["case_id"]),
                projection_from_dict(case["left_projection"]),
                projection_from_dict(case["right_projection"]),
                MeaningRelation(str(expected["meaning_relation"])),
            )
        )
    return pairs


def run_campaign(repo_root: Path) -> tuple[dict[str, Any], tuple[ProbeCase, ...]]:
    """Build every probe, check the precondition, then score every arm."""

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P3_PARTIAL_OBSERVATION_RESULT",
        "date": "2026-08-21",
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_sha256": frozen_digest(),
        "claim_scope": CLAIM_SCOPE,
        "candidate_coordinate": CANDIDATE_COORDINATE,
    }

    intact_pairs: dict[str, list[Any]] = {}
    probes: dict[str, tuple[ProbeCase, ...]] = {}
    sources: dict[str, Any] = {}
    for corpus_id, relative in INTACT_SOURCES.items():
        path = repo_root / relative
        cases = load_jsonl(path)
        intact_pairs[corpus_id] = _intact_pairs(cases)
        if corpus_id in PROBE_OF:
            probes[PROBE_OF[corpus_id]] = build_probe(cases, PROBE_OF[corpus_id])
        sources[corpus_id] = {
            "path": relative,
            "n_cases": len(cases),
            "role": "HARM_MEASUREMENT_ONLY" if corpus_id not in PROBE_OF else "HARM_AND_PROBE_PARENT",
        }
    payload["sources"] = sources

    preconditions = {
        probe_id: construction_precondition(
            probe, require_nonempty=(probe_id == PROBE_DERIVATION)
        )
        for probe_id, probe in probes.items()
    }
    payload["construction_precondition"] = preconditions

    if not all(item["passed"] for item in preconditions.values()):
        payload["verdicts"] = {
            "channel": VERDICT_CONSTRUCTION_FAILED,
            "t5": VERDICT_T5,
        }
        payload["interpretation"] = (
            "The probe does not have the structure the freeze specifies, so it is not the world "
            "under study. No arm numbers are reported over it."
        )
        payload["overall_outcome"] = Outcome.CANNOT_CHECK.value
        return payload, ()

    corpora: dict[str, dict[str, Any]] = {}
    scored_by_corpus: dict[str, tuple[ScoredCase, ...]] = {}

    for corpus_id, pairs in intact_pairs.items():
        scored = score_pairs(pairs)
        scored_by_corpus[corpus_id] = scored
        ledger = ledger_from_scored(corpus_id, scored)
        corpora[corpus_id] = {
            "kind": "INTACT",
            "n_cases": len(pairs),
            "one_sided_absence_census": one_sided_absence_census(pairs),
            "by_arm": assess_corpus(corpus_id, ledger),
            "harm_vs_current": {
                arm: harm_against_current(scored, arm)
                for arm in (ARM_ASYMMETRIC, ARM_STRICT)
            },
            "mining_census": mining_census(scored),
        }

    for probe_id, probe in probes.items():
        pairs = [(case.case_id, case.left, case.right, case.gold) for case in probe]
        scored = score_pairs(pairs)
        scored_by_corpus[probe_id] = scored
        entry: dict[str, Any] = {
            "kind": "PROBE",
            "n_cases": len(pairs),
            "redacted_coordinates": sorted({case.coordinate for case in probe}),
            "parent_gold_relations": sorted({case.parent_gold.value for case in probe}),
        }
        if pairs:
            ledger = ledger_from_scored(probe_id, scored)
            entry["by_arm"] = assess_corpus(probe_id, ledger)
            entry["mining_census"] = mining_census(scored)
            parent_pairs = [
                (case.case_id, case.left, case.right, case.parent_gold) for case in probe
            ]
            parent_scored = score_pairs(parent_pairs)
            parent_ledger = ledger_from_scored(f"{probe_id}|PARENT_GOLD", parent_scored)
            entry["parent_gold_scoring"] = assess_corpus(
                f"{probe_id}|PARENT_GOLD", parent_ledger
            )
        else:
            entry["by_arm"] = {}
            entry["mining_census"] = mining_census(())
            entry["parent_gold_scoring"] = {}
        corpora[probe_id] = entry

    payload["corpora"] = corpora
    payload["gates"] = evaluate_gates(corpora)
    payload["verdicts"] = derive_verdicts(payload["gates"])
    payload["overall_outcome"] = overall_outcome(payload["gates"]).value
    payload["interpretation"] = INTERPRETATION
    payload["caveats"] = CAVEATS
    return payload, tuple(case for probe in probes.values() for case in probe)


def evaluate_gates(corpora: Mapping[str, Any]) -> dict[str, Any]:
    """Every gate of freeze section 7.2, three-valued, never coercing an absent rate."""

    gates: dict[str, Any] = {}

    gates["G1_CONSTRUCTION"] = {
        "outcome": Outcome.PASS.value,
        "detail": "checked before any arm ran; see construction_precondition",
    }

    derivation = corpora[PROBE_DERIVATION]["by_arm"].get(ARM_CURRENT)
    if derivation is None:
        gates["G2_CHANNEL_OPENED"] = {
            "outcome": Outcome.CANNOT_CHECK.value,
            "detail": "PROBE_DERIVATION produced no case, so the guard has no exercise at all",
        }
        gates["G3_FAILURE_ON_REAL_CASES"] = {
            "outcome": Outcome.CANNOT_CHECK.value,
            "detail": "no derivation probe to measure",
        }
    else:
        exercise = derivation["over_resolution"]["exercises"][0]
        opportunities = int(exercise["opportunities"])
        gates["G2_CHANNEL_OPENED"] = {
            "outcome": (
                Outcome.PASS.value
                if opportunities >= GATES["G2_CHANNEL_OPENED"]["min_opportunities"]
                else Outcome.FAIL.value
            ),
            "opportunities": opportunities,
            "detail": (
                f"P3.OVERRESOLVED_UNRESOLVED_CASE has {opportunities} opportunities on "
                "PROBE_DERIVATION; it had 0 on every atlas before this study"
            ),
        }
        rate = _over_resolution_rate(corpora[PROBE_DERIVATION]["by_arm"], ARM_CURRENT)
        threshold = float(GATES["G3_FAILURE_ON_REAL_CASES"]["min_violation_rate"])
        if rate is None:
            gates["G3_FAILURE_ON_REAL_CASES"] = {
                "outcome": Outcome.CANNOT_CHECK.value,
                "violation_rate": None,
                "detail": "the guard was never exercised, so there is no rate to compare",
            }
        else:
            gates["G3_FAILURE_ON_REAL_CASES"] = {
                "outcome": Outcome.PASS.value if rate >= threshold else Outcome.FAIL.value,
                "violation_rate": rate,
                "threshold": threshold,
                "violations": int(exercise["violations"]),
                "opportunities": opportunities,
                "detail": (
                    f"A0_orion_current over-resolves {exercise['violations']} of {opportunities} "
                    f"partially observed pairs derived from real adjudicated cases (rate {rate})"
                ),
            }

    heldout: dict[str, Any] = {}
    heldout_outcomes: list[Outcome] = []
    for probe_id in (PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC):
        by_arm = corpora[probe_id]["by_arm"]
        rate = _over_resolution_rate(by_arm, ARM_CURRENT) if by_arm else None
        threshold = float(GATES["G4_HELD_OUT"]["min_violation_rate"])
        if rate is None:
            heldout[probe_id] = {"outcome": Outcome.CANNOT_CHECK.value, "violation_rate": None}
            heldout_outcomes.append(Outcome.CANNOT_CHECK)
        else:
            outcome = Outcome.PASS if rate >= threshold else Outcome.FAIL
            heldout[probe_id] = {"outcome": outcome.value, "violation_rate": rate}
            heldout_outcomes.append(outcome)
    gates["G4_HELD_OUT"] = {
        "outcome": _worst(heldout_outcomes).value,
        "by_probe": heldout,
        "threshold": float(GATES["G4_HELD_OUT"]["min_violation_rate"]),
    }

    intact_failures = [
        row
        for corpus_id in INTACT_ORDER
        for row in corpora[corpus_id]["mining_census"]["failures"]
    ]
    probe_over_resolutions = [
        row
        for probe_id in (PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC)
        for row in corpora[probe_id]["mining_census"]["failures"]
        if row["kind"] in {"MERGED_WHERE_GOLD_UNRESOLVED", "SEPARATED_WHERE_GOLD_UNRESOLVED"}
    ]
    a_unexplained = [row for row in intact_failures if row["demands_a_coordinate_orion_lacks"]]
    b_explained = [
        row for row in probe_over_resolutions if not row["demands_a_coordinate_orion_lacks"]
    ]
    if not intact_failures:
        a_outcome = Outcome.CANNOT_CHECK
    else:
        a_outcome = Outcome.PASS if not a_unexplained else Outcome.FAIL
    if not probe_over_resolutions:
        b_outcome = Outcome.CANNOT_CHECK
    else:
        b_outcome = Outcome.PASS if not b_explained else Outcome.FAIL
    gates["G5_MINING_YIELD"] = {
        "outcome": _worst([a_outcome, b_outcome]).value,
        "a_intact_failures": {
            "outcome": a_outcome.value,
            "n_failures": len(intact_failures),
            "n_demanding_a_missing_coordinate": len(a_unexplained),
        },
        "b_probe_over_resolutions": {
            "outcome": b_outcome.value,
            "n_over_resolutions": len(probe_over_resolutions),
            "n_explained_by_an_existing_coordinate": len(b_explained),
        },
    }

    a1_changes = sum(
        corpora[corpus_id]["harm_vs_current"][ARM_ASYMMETRIC]["decisions_changed"]
        for corpus_id in INTACT_ORDER
    )
    a1_opportunities = sum(
        corpora[corpus_id]["one_sided_absence_census"]["n_pairs_with_a_one_sided_absence"]
        for corpus_id in INTACT_ORDER
    )
    a1_destroyed = sum(
        corpora[corpus_id]["harm_vs_current"][ARM_ASYMMETRIC]["correct_answers_destroyed"]
        for corpus_id in INTACT_ORDER
    )
    gates["G6_HARM_A1"] = {
        "outcome": (
            Outcome.CANNOT_CHECK.value
            if a1_opportunities == 0
            else (Outcome.PASS.value if a1_changes == 0 else Outcome.FAIL.value)
        ),
        "decisions_changed": a1_changes,
        "correct_answers_destroyed": a1_destroyed,
        "pairs_where_a1_could_fire": a1_opportunities,
        "vacuous": a1_opportunities == 0,
        "by_corpus": {
            corpus_id: {
                "pairs_where_a1_could_fire": (
                    corpora[corpus_id]["one_sided_absence_census"][
                        "n_pairs_with_a_one_sided_absence"
                    ]
                ),
                **corpora[corpus_id]["harm_vs_current"][ARM_ASYMMETRIC],
            }
            for corpus_id in INTACT_ORDER
        },
        "detail": (
            "A1 cannot fire on any intact pair because no intact pair has a one-sided absence; "
            "0 changes is a structural zero, not a demonstration of safety"
            if a1_opportunities == 0
            else (
                f"A1 could fire on {a1_opportunities} intact pairs, moved {a1_changes} decisions "
                f"and destroyed {a1_destroyed} correct answers"
            )
        ),
    }

    gates["G7_COST_A2"] = {
        "outcome": Outcome.PASS.value,
        "detail": "reported, non-blocking",
        "by_corpus": {
            corpus_id: corpora[corpus_id]["harm_vs_current"][ARM_STRICT]
            for corpus_id in INTACT_ORDER
        },
    }

    gates["G8_NOVELTY"] = {
        "outcome": Outcome.FAIL.value,
        "fails_by_construction": True,
        "detail": (
            "observation_status is constant across every fully observed pair, so no two fully "
            "observed projections can differ on it. It is a third value on the existing axes, "
            "not a new identity axis. P3-U-T5 is not discharged."
        ),
    }
    return gates


def _worst(outcomes: Sequence[Outcome]) -> Outcome:
    if not outcomes:
        return Outcome.CANNOT_CHECK
    if Outcome.FAIL in outcomes:
        return Outcome.FAIL
    if Outcome.CANNOT_CHECK in outcomes:
        return Outcome.CANNOT_CHECK
    return Outcome.PASS


def derive_verdicts(gates: Mapping[str, Any]) -> dict[str, str]:
    """Freeze section 7.3, applied mechanically."""

    def passed(name: str) -> bool:
        return gates[name]["outcome"] == Outcome.PASS.value

    if not passed("G1_CONSTRUCTION"):
        channel = VERDICT_CONSTRUCTION_FAILED
    elif not passed("G2_CHANNEL_OPENED"):
        channel = VERDICT_CHANNEL_NOT_OPENED
    elif not passed("G3_FAILURE_ON_REAL_CASES"):
        channel = VERDICT_FAILURE_WEAKER
    else:
        channel = VERDICT_CHANNEL

    verdicts = {"channel": channel, "t5": VERDICT_T5}
    if channel == VERDICT_CHANNEL and passed("G4_HELD_OUT"):
        verdicts["heldout"] = VERDICT_HELDOUT
    if gates["G5_MINING_YIELD"]["a_intact_failures"]["outcome"] == Outcome.PASS.value:
        verdicts["mining"] = VERDICT_NO_NEW_COORDINATE
    return verdicts


def overall_outcome(gates: Mapping[str, Any]) -> Outcome:
    """Non-compensatory roll-up over the blocking gates.

    ``G8_NOVELTY`` fails by construction, so this is ``FAIL`` by design: the
    study's job is to replace a ``CANNOT_CHECK`` with a demonstrated failure, not
    to produce a pass.
    """

    blocking = [name for name, spec in GATES.items() if spec.get("blocking")]
    return _worst([Outcome(gates[name]["outcome"]) for name in blocking])


INTERPRETATION = (
    "ORION commits zero false merges and zero false splits on every P3 atlas, so P3-U-T5's "
    "instruction to mine those failures has an empty input. This study opens the one channel that "
    "could yield a candidate -- over-resolution -- by silencing, on one side, the coordinate that "
    "carries the decision. P3.OVERRESOLVED_UNRESOLVED_CASE moves from a 0-of-0 CANNOT_CHECK to a "
    "real denominator with a demonstrated failure. The candidate coordinate mined from that "
    "failure, observation_status, is not a new identity axis: it is the third value the existing "
    "axes lack. P3-U-T5 is NOT discharged, and no accuracy or superiority number over the probe "
    "may be quoted as evidence about ORION on scientific text. Amendment 001 supplies the one "
    "denominator this study was missing: an intact corpus that states a coordinate on one side "
    "only. Over it the absent-means-agreement reading fails on authored cases and not only on "
    "redactions, eight coordinates merge-ward and one separation-ward exactly as section 1.2 "
    "predicted, and the abstain-on-asymmetry repair A1 is measured to destroy correct answers "
    "rather than assumed harmless. G6_HARM_A1 is now a FAIL on evidence instead of a "
    "CANNOT_CHECK on emptiness."
)


CAVEATS: tuple[str, ...] = (
    "A1_observedness_asymmetric and A2_observedness_strict score zero on the over-resolution guard "
    "by construction: they abstain on exactly the property the probe injects. Those zeros license "
    "nothing and are not evidence that either rule is correct. A2's informative number is its cost "
    "on the intact corpora (gate G7), not its probe score.",
    "G6_HARM_A1 was vacuous on the three corpora frozen on 2026-08-21 and is not vacuous now. "
    "Amendment 001 adds INTACT_HARM_SYNTHETIC, an intact corpus that does have one-sided "
    "absences, and over that denominator A1 is measured rather than assumed. The zero it used to "
    "report was never a demonstration of safety and is not now retroactively one; what replaced "
    "it is a harm count.",
    "A1's harm on INTACT_HARM_SYNTHETIC is not a property of that corpus. A1 returns UNRESOLVED "
    "on every pair with a one-sided absence, so on any such pair whose gold is determinate and "
    "which A0 already answers correctly it necessarily destroys a correct answer. G6 can "
    "therefore only be passed non-vacuously by a corpus in which no partially observed pair has "
    "a determinate answer. That is a fact about the gate and the arm, not about the cases.",
    "G5_MINING_YIELD part (a) had no failures to mine while every intact corpus was fully "
    "symmetric in observedness: all three arms can err only by abstaining, and abstention where "
    "gold is determinate is not one of the four failure kinds, so the only possible intact "
    "failure was one A0 itself commits, and A0 answers every symmetric intact pair correctly. "
    "INTACT_HARM_SYNTHETIC's D stratum makes A0 fail on nine intact pairs, so part (a) now has a "
    "denominator. Its outcome is FAIL, and that is the honest reading: those failures have no "
    "discriminating coordinate at all, which is the study's own finding restated, not evidence "
    "for a new axis. Reading part (a)'s earlier emptiness as 'no new coordinate is needed' would "
    "have been the vacuous-guard fallacy this lane exists to prevent.",
    "A rule that abstained only where the one-sided absence is decisive would not pay A1's cost "
    "on INTACT_HARM_SYNTHETIC's H stratum. That corpus cannot score such a rule: its gold is "
    "derived by exactly that criterion, so the comparison would be circular. The candidate is "
    "named, not measured. A1 and A2 are also indistinguishable on that corpus -- identical "
    "decision kinds on all 33 cases -- so A2's separate cost remains visible only on the three "
    "corpora frozen on 2026-08-21, where G7 is unchanged.",
    "INTACT_HARM_SYNTHETIC is synthetic. It establishes what compare_meaning does with a "
    "one-sided absence and what an abstain-on-asymmetry repair costs on pairs of that shape. It "
    "establishes nothing about how often scientific sources state a coordinate on one side only, "
    "and no accuracy, false-merge, false-split or superiority number over it is evidence about "
    "ORION's competence.",
    "The probe is a mechanical redaction of atlases that already ship here. It establishes a "
    "property of compare_meaning, not a frequency in scientific text. No accuracy, false-merge, "
    "false-split or superiority number over it is evidence about ORION's competence.",
    "PROBE_DERIVATION and PROBE_HELDOUT_REAL reach only the polarity coordinate, because the real "
    "atlases populate no other coordinate differently on both sides. The other two coordinate "
    "strata are reached only through the 24 synthetic cases of coordinate-necessity-v1.",
)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run the P3 partial-observation probe (P3-U-T5)."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--probe-output", type=Path)
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the runner's frozen parameter digest and exit without running",
    )
    parser.add_argument(
        "--skip-twin-check",
        action="store_true",
        help="skip the freeze-twin digest check (only for minting the twin)",
    )
    args = parser.parse_args(list(argv))

    if args.print_digest:
        print(frozen_digest())
        return 0

    if not args.skip_twin_check:
        verify_against_twin(args.repo_root)

    payload, probe = run_campaign(args.repo_root)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if args.probe_output is not None:
        args.probe_output.parent.mkdir(parents=True, exist_ok=True)
        args.probe_output.write_text(
            "".join(
                json.dumps(probe_case_json(case), sort_keys=True, ensure_ascii=False) + "\n"
                for case in probe
            ),
            encoding="utf-8",
        )

    outcome = Outcome(payload["overall_outcome"])
    if outcome is Outcome.PASS:
        return 0
    return 3 if outcome is Outcome.FAIL else 4


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(__import__("sys").argv[1:]))


__all__ = [
    "ABSENCE_READING",
    "ABSENT_VALUE",
    "ARMS",
    "ARM_CURRENT",
    "ARM_ASYMMETRIC",
    "ARM_ORDER",
    "ARM_STRICT",
    "AMENDMENT_DOCUMENT",
    "AMENDMENT_TWIN",
    "CANDIDATE_COORDINATE",
    "COORDINATES",
    "FREEZE_DOCUMENT",
    "FREEZE_TWIN",
    "FROZEN_PARAMETERS",
    "FreezeViolation",
    "INTACT_DERIVATION",
    "INTACT_HARM_SYNTHETIC",
    "INTACT_HELDOUT_REAL",
    "INTACT_HELDOUT_SYNTHETIC",
    "INTACT_ORDER",
    "INTACT_SOURCES",
    "ORIGINAL_FREEZE_TWIN",
    "PARTIALLY_OBSERVED_INTACT_ORDER",
    "PROBE_DERIVATION",
    "PROBE_HELDOUT_REAL",
    "PROBE_HELDOUT_SYNTHETIC",
    "PROBE_OF",
    "SYMMETRIC_INTACT_ORDER",
    "ProbeCase",
    "ScoredCase",
    "VERDICT_T5",
    "CAVEATS",
    "build_probe",
    "construction_precondition",
    "derive_verdicts",
    "discriminating_coordinates",
    "evaluate_gates",
    "frozen_digest",
    "harm_against_current",
    "main",
    "mining_census",
    "observed",
    "one_sided_absence_census",
    "overall_outcome",
    "probe_case_json",
    "redactable_coordinates",
    "run_campaign",
    "score_pairs",
    "verify_against_twin",
]
