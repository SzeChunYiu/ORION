"""Merge/split guard denominators for the P3 identity atlas (#651).

P3-U-T1 asks for "significant reduction in false scientific merges versus
strongest real competitor" and P3-U-T2 for "no unacceptable false-split/
plurality penalty". Both are reported by
``orion.study.p3_public_reference._rates`` as a count over *every* case in the
atlas::

    "false_merge_rate": false_merge / n,
    "false_split_rate": false_split / n,

The numerator is carried and the denominator is discarded, which is the
``VACUOUS_GUARD_ZERO_DENOMINATOR`` shape recorded for P2
(``research/failures/2026-08-vacuous-guard-zero-denominator/``). On the frozen
P3 atlases it costs the paper in both directions, measured on
``gold/adjudicated/public-reference-v1.1-confirmatory`` (n=32):

============================  ============================  ==============
quantity                      as reported                   on its own
                                                            denominator
============================  ============================  ==============
flat baseline false merges    ``0.1875`` over 32 cases      **6 of 6**
ORION false merges            ``0.0`` over 32 cases         0 of 6
ORION false splits            ``0.0`` over 32 cases         0 of 26
comparator false splits       ``0.0`` over 32 cases         **no denominator**
gold-``UNRESOLVED`` cases     not reported                  **0 of 32**
============================  ============================  ==============

Only 6 of 32 cases have a gold relation a system could falsely merge, so the
headline ``-0.1875`` understates the real contrast by a factor of 5.33: the flat
comparator false-merges on *every* case where a false merge was available. The
honest denominator makes P3-U-T1 stronger, exactly as P2's did.

P3-U-T2 goes the other way. Both comparators emit ``COMPATIBLE`` or
``UNRESOLVED`` and nothing else --- ``flat_predicate_baseline`` and
``exact_coordinate_baseline`` have no branch that returns a non-merge relation
--- so across 32 of 32 cases in both frozen atlases neither ever declines to
merge. A system that never separates cannot false-split, on this atlas or any
other, and
``primary_comparisons.false_split_orion_minus_exact = 0.0 [0.0, 0.0]``
is a non-inferiority comparison against an arm structurally incapable of paying
the penalty. ORION's own side of it is real (it separates 6 times, wrongly 0
times, over 26 mergeable pairs) and this module reports it as such; what it
refuses is to call the *comparison* a pass.

Design follows ``orion.study.p2.closure_receipts``:
:class:`IdentityDecisionKind` is total, so every (gold, prediction) cell lands in
exactly one named state and the states that swallow a denominator --- an
abstention, a gold-``UNRESOLVED`` case --- appear in the ledger instead of
vanishing into a zero. Only kinds whose ``gold_admits_*`` is true enter a
denominator, so an atlas with no mergeable pairs, or an arm that never
separates, produces a ``GuardExercise`` with zero opportunities and
:func:`orion.programme.guard_exercise.assess_guard` returns ``CANNOT_CHECK``.

This module reads decisions, never gold construction: it consumes the
(gold, prediction) pairs the analysis already produced.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from orion.knowledge.semantics import MeaningRelation
from orion.programme.guard_exercise import (
    GuardAssessment,
    GuardExercise,
    assess_guard,
    assess_non_inferiority,
)
from orion.study.p3_public_reference import NONMERGE_RELATIONS

FALSE_MERGE_GUARD_ID = "P3.FALSE_SCIENTIFIC_MERGE"
FALSE_SPLIT_GUARD_ID = "P3.FALSE_SCIENTIFIC_SPLIT"
UNRESOLVED_CALIBRATION_GUARD_ID = "P3.OVERRESOLVED_UNRESOLVED_CASE"

FALSE_MERGE_OPPORTUNITY = (
    "one pair whose gold relation forbids merging; a pair that is genuinely the "
    "same thing offers no opportunity to merge it falsely"
)
FALSE_SPLIT_OPPORTUNITY = (
    "one pair whose gold relation permits merging, scored by an arm that declines "
    "to merge somewhere in the atlas; an arm that never separates cannot separate "
    "wrongly, so it has no false-split denominator on any corpus"
)
UNRESOLVED_CALIBRATION_OPPORTUNITY = (
    "one pair whose gold relation is UNRESOLVED; an atlas that adjudicates every "
    "pair offers no opportunity to over-resolve one"
)


class IdentityDecisionKind(str, Enum):
    """Total taxonomy of one arm's decision on one identity pair.

    The three ``*_WHERE_GOLD_UNRESOLVED`` and two ``ABSTAINED_*`` kinds are the
    states a false-merge/false-split rate pair cannot express. All five are
    legitimate outcomes; none of them is evidence that a merge guard held.

    "Separated" here means only that the arm declined to merge. Which non-merge
    relation it named is the accuracy metric's question, not this one: a guard
    about false merges is a guard about the merge/non-merge boundary.
    """

    MERGED_CORRECTLY = "MERGED_CORRECTLY"
    FALSE_SPLIT = "FALSE_SPLIT"
    ABSTAINED_ON_MERGEABLE = "ABSTAINED_ON_MERGEABLE"
    FALSE_MERGE = "FALSE_MERGE"
    SEPARATED_CORRECTLY = "SEPARATED_CORRECTLY"
    ABSTAINED_ON_SEPARABLE = "ABSTAINED_ON_SEPARABLE"
    ABSTAINED_AS_GOLD_REQUIRES = "ABSTAINED_AS_GOLD_REQUIRES"
    MERGED_WHERE_GOLD_UNRESOLVED = "MERGED_WHERE_GOLD_UNRESOLVED"
    SEPARATED_WHERE_GOLD_UNRESOLVED = "SEPARATED_WHERE_GOLD_UNRESOLVED"

    @property
    def gold_admits_false_merge(self) -> bool:
        """Only a pair gold says must not merge can be merged falsely."""

        return self in {
            IdentityDecisionKind.FALSE_MERGE,
            IdentityDecisionKind.SEPARATED_CORRECTLY,
            IdentityDecisionKind.ABSTAINED_ON_SEPARABLE,
        }

    @property
    def gold_admits_false_split(self) -> bool:
        """Only a pair gold says may merge can be split falsely."""

        return self in {
            IdentityDecisionKind.MERGED_CORRECTLY,
            IdentityDecisionKind.FALSE_SPLIT,
            IdentityDecisionKind.ABSTAINED_ON_MERGEABLE,
        }

    @property
    def gold_admits_over_resolution(self) -> bool:
        """Only a pair gold leaves unresolved can be resolved over-confidently."""

        return self in {
            IdentityDecisionKind.ABSTAINED_AS_GOLD_REQUIRES,
            IdentityDecisionKind.MERGED_WHERE_GOLD_UNRESOLVED,
            IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED,
        }

    @property
    def predicted_separation(self) -> bool:
        """The arm declined to merge. Zero of these means it cannot false-split."""

        return self in {
            IdentityDecisionKind.FALSE_SPLIT,
            IdentityDecisionKind.SEPARATED_CORRECTLY,
            IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED,
        }

    @property
    def is_false_merge(self) -> bool:
        return self is IdentityDecisionKind.FALSE_MERGE

    @property
    def is_false_split(self) -> bool:
        return self is IdentityDecisionKind.FALSE_SPLIT

    @property
    def is_over_resolution(self) -> bool:
        return self in {
            IdentityDecisionKind.MERGED_WHERE_GOLD_UNRESOLVED,
            IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED,
        }


def classify_identity_decision(
    gold: MeaningRelation, predicted: MeaningRelation
) -> IdentityDecisionKind:
    """Place one (gold, prediction) cell in the taxonomy.

    Raises rather than guessing on an unclassifiable relation: a new
    ``MeaningRelation`` that nobody sorted into merge, separation or abstention
    would otherwise be silently dropped out of both denominators.
    """

    for role, relation in (("gold", gold), ("predicted", predicted)):
        if (
            relation is not MeaningRelation.COMPATIBLE
            and relation is not MeaningRelation.UNRESOLVED
            and relation not in NONMERGE_RELATIONS
        ):
            raise ValueError(
                f"{role} relation {relation.value} is neither a merge, a separation nor "
                "an abstention; it cannot be placed in a merge-guard denominator"
            )

    if gold is MeaningRelation.COMPATIBLE:
        if predicted is MeaningRelation.COMPATIBLE:
            return IdentityDecisionKind.MERGED_CORRECTLY
        if predicted is MeaningRelation.UNRESOLVED:
            return IdentityDecisionKind.ABSTAINED_ON_MERGEABLE
        return IdentityDecisionKind.FALSE_SPLIT
    if gold is MeaningRelation.UNRESOLVED:
        if predicted is MeaningRelation.COMPATIBLE:
            return IdentityDecisionKind.MERGED_WHERE_GOLD_UNRESOLVED
        if predicted is MeaningRelation.UNRESOLVED:
            return IdentityDecisionKind.ABSTAINED_AS_GOLD_REQUIRES
        return IdentityDecisionKind.SEPARATED_WHERE_GOLD_UNRESOLVED
    if predicted is MeaningRelation.COMPATIBLE:
        return IdentityDecisionKind.FALSE_MERGE
    if predicted is MeaningRelation.UNRESOLVED:
        return IdentityDecisionKind.ABSTAINED_ON_SEPARABLE
    return IdentityDecisionKind.SEPARATED_CORRECTLY


@dataclass(frozen=True)
class IdentityDecisionReceipt:
    """What one arm decided on one pair, and what gold said about that pair."""

    case_id: str
    arm_id: str
    gold: MeaningRelation
    predicted: MeaningRelation
    kind: IdentityDecisionKind

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("an identity receipt requires a case id")
        if not self.arm_id.strip():
            raise ValueError(f"{self.case_id}: an identity receipt requires an arm id")
        expected = classify_identity_decision(self.gold, self.predicted)
        if self.kind is not expected:
            raise ValueError(
                f"{self.case_id}/{self.arm_id}: kind {self.kind.value} contradicts "
                f"({self.gold.value}, {self.predicted.value}), which is {expected.value}"
            )

    def as_json(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "arm_id": self.arm_id,
            "gold": self.gold.value,
            "predicted": self.predicted.value,
            "kind": self.kind.value,
        }


@dataclass(frozen=True)
class IdentityDecisionLedger:
    """Every arm's decision on every pair, with the denominators they imply."""

    atlas_id: str
    receipts: tuple[IdentityDecisionReceipt, ...]

    def __post_init__(self) -> None:
        if not self.atlas_id.strip():
            raise ValueError("an identity ledger requires an atlas identity")
        if not self.receipts:
            raise ValueError(f"{self.atlas_id}: a ledger with no receipts measures nothing")
        seen = {(item.arm_id, item.case_id) for item in self.receipts}
        if len(seen) != len(self.receipts):
            raise ValueError(f"{self.atlas_id}: an arm may decide each case once")

    @property
    def arms(self) -> tuple[str, ...]:
        return tuple(sorted({item.arm_id for item in self.receipts}))

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(sorted({item.case_id for item in self.receipts}))

    def for_arm(self, arm_id: str) -> tuple[IdentityDecisionReceipt, ...]:
        receipts = tuple(item for item in self.receipts if item.arm_id == arm_id)
        if not receipts:
            raise KeyError(f"{self.atlas_id}: no receipts for arm {arm_id}")
        return receipts

    def kind_counts(self, arm_id: str) -> dict[str, int]:
        """Counts over the *total* taxonomy, so every cell is visible somewhere."""

        counted = Counter(item.kind.value for item in self.for_arm(arm_id))
        return {kind.value: counted.get(kind.value, 0) for kind in IdentityDecisionKind}

    def separations_emitted(self, arm_id: str) -> int:
        """How often the arm declined to merge, anywhere in the atlas.

        Zero is the structural fact that makes a false-split rate meaningless:
        both P3 comparators score zero here on 32 of 32 cases.
        """

        return sum(1 for item in self.for_arm(arm_id) if item.kind.predicted_separation)

    def false_merge_exercise(self, arm_id: str) -> GuardExercise:
        """The false-merge denominator: pairs gold forbids merging, not all pairs."""

        receipts = self.for_arm(arm_id)
        return GuardExercise(
            guard_id=FALSE_MERGE_GUARD_ID,
            arm_id=arm_id,
            opportunities=sum(1 for item in receipts if item.kind.gold_admits_false_merge),
            violations=sum(1 for item in receipts if item.kind.is_false_merge),
            opportunity_definition=FALSE_MERGE_OPPORTUNITY,
        )

    def false_split_exercise(self, arm_id: str) -> GuardExercise:
        """The false-split denominator: mergeable pairs, and only for a separating arm.

        The second condition is the one the P3 analysis is missing. An arm whose
        decision procedure never returns a non-merge relation scores zero false
        splits on every possible corpus, so crediting that zero as parity is
        crediting an arm for a penalty it could not have paid.
        """

        receipts = self.for_arm(arm_id)
        separates = any(item.kind.predicted_separation for item in receipts)
        return GuardExercise(
            guard_id=FALSE_SPLIT_GUARD_ID,
            arm_id=arm_id,
            opportunities=(
                sum(1 for item in receipts if item.kind.gold_admits_false_split)
                if separates
                else 0
            ),
            violations=sum(1 for item in receipts if item.kind.is_false_split),
            opportunity_definition=FALSE_SPLIT_OPPORTUNITY,
        )

    def unresolved_calibration_exercise(self, arm_id: str) -> GuardExercise:
        """The abstention-calibration denominator: pairs gold itself leaves unresolved.

        #651 asks for "unresolved calibration". Both frozen atlases contain zero
        gold-``UNRESOLVED`` pairs, so an abstention there is always an error and
        never a success, and the reported ``abstention_rate`` measures caution
        rather than calibration.
        """

        receipts = self.for_arm(arm_id)
        return GuardExercise(
            guard_id=UNRESOLVED_CALIBRATION_GUARD_ID,
            arm_id=arm_id,
            opportunities=sum(1 for item in receipts if item.kind.gold_admits_over_resolution),
            violations=sum(1 for item in receipts if item.kind.is_over_resolution),
            opportunity_definition=UNRESOLVED_CALIBRATION_OPPORTUNITY,
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": "orion.p3.identity-opportunity.v1",
            "atlas_id": self.atlas_id,
            "arms": list(self.arms),
            "n_cases": len(self.case_ids),
            "n_receipts": len(self.receipts),
            "by_arm": {
                arm: {
                    "decision_kinds": self.kind_counts(arm),
                    "separations_emitted": self.separations_emitted(arm),
                    "false_merge_exercise": self.false_merge_exercise(arm).as_json(),
                    "false_split_exercise": self.false_split_exercise(arm).as_json(),
                    "unresolved_calibration_exercise": (
                        self.unresolved_calibration_exercise(arm).as_json()
                    ),
                }
                for arm in self.arms
            },
        }


def build_identity_ledger(
    atlas_id: str, rows: Iterable[tuple[str, str, MeaningRelation, MeaningRelation]]
) -> IdentityDecisionLedger:
    """Build a ledger from ``(case_id, arm_id, gold, predicted)`` rows."""

    return IdentityDecisionLedger(
        atlas_id=atlas_id,
        receipts=tuple(
            IdentityDecisionReceipt(
                case_id=case_id,
                arm_id=arm_id,
                gold=gold,
                predicted=predicted,
                kind=classify_identity_decision(gold, predicted),
            )
            for case_id, arm_id, gold, predicted in rows
        ),
    )


def assess_identity_guards(
    ledger: IdentityDecisionLedger,
    *,
    candidate: str,
    comparator: str,
    false_split_margin: float = 0.0,
) -> tuple[GuardAssessment, ...]:
    """Assess P3-U-T1's numerator and P3-U-T2's comparison on real denominators.

    Three assessments, in the order the paper needs them: the candidate's own
    false-merge ceiling, the false-split non-inferiority claim against the
    comparator, and the candidate's abstention calibration. Roll them up with
    :func:`orion.programme.guard_exercise.worst_outcome`; any ``CANNOT_CHECK``
    blocks a promotion exactly as a ``FAIL`` does.
    """

    if candidate == comparator:
        raise ValueError(f"{ledger.atlas_id}: an arm cannot be its own comparator")
    return (
        assess_guard(ledger.false_merge_exercise(candidate)),
        assess_non_inferiority(
            candidate=ledger.false_split_exercise(candidate),
            comparator=ledger.false_split_exercise(comparator),
            margin=false_split_margin,
        ),
        assess_guard(ledger.unresolved_calibration_exercise(candidate)),
    )


__all__ = [
    "FALSE_MERGE_GUARD_ID",
    "FALSE_MERGE_OPPORTUNITY",
    "FALSE_SPLIT_GUARD_ID",
    "FALSE_SPLIT_OPPORTUNITY",
    "IdentityDecisionKind",
    "IdentityDecisionLedger",
    "IdentityDecisionReceipt",
    "UNRESOLVED_CALIBRATION_GUARD_ID",
    "UNRESOLVED_CALIBRATION_OPPORTUNITY",
    "assess_identity_guards",
    "build_identity_ledger",
    "classify_identity_decision",
]
