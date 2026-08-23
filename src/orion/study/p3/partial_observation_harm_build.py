"""Build the corpus that gives the A1 harm gate a denominator (P3-U-T5, G6).

``orion.study.p3.partial_observation_probe`` reports gate ``G6_HARM_A1`` as
``CANNOT_CHECK`` with ``vacuous: true``, in its own words:

    A1 cannot fire on any intact pair because no intact pair has a one-sided
    absence; 0 changes is a structural zero, not a demonstration of safety.

The zero is real and the probe is right to refuse to call it a pass. It is not,
however, a property of what "intact" means. ``ScientificMeaningProjection``
places no constraint across the two sides of a pair: observedness is a
per-projection fact, and ``compare_meaning`` carries five separate branches ---
``_same_or_empty``, the three ``left.X and right.X`` guards, the
``Polarity.UNKNOWN`` test --- whose *only* reachable inputs are pairs observed on
one side and not the other. Those branches are not dead code by definition; they
are untested because all three atlases P3 owns happen to have been built from
templates that populate both sides identically. The zero is a fact about three
corpora, not about the type.

This module builds a corpus that has the property those three lack, so that G6
measures something. It does not touch a frozen atlas, and it is deliberately
**adversarial to its own author**: G6 reads "A1 changes 0 decisions", so a corpus
added to it can only leave the gate where it is or make it fail. There is no
construction of this corpus that turns G6 into a pass, which is why building one
is not a way of manufacturing a positive.

Four strata, 33 cases. Every case states all nine identity coordinates on both
sides except where a stratum says otherwise.

``H_UNDECISIVE_ABSENCE`` (12)
    One coordinate absent on exactly one side, where a **strictly
    higher-precedence** coordinate already decides the pair. Gold is determinate
    and is verified determinate by enumeration: the derived relation is constant
    over *every* admissible value the absent coordinate could have taken. These
    are the cases on which an abstain-on-asymmetry rule can do damage, because
    the thing it abstains over cannot change the answer.

``D_DECISIVE_ABSENCE`` (9)
    One coordinate absent on exactly one side, everything else equal, so the
    absent coordinate is exactly what the answer turns on. Gold is ``UNRESOLVED``
    because the relation is *not* constant over the admissible completions. One
    case per coordinate: this stratum is a nine-cell census of the
    absence-reading inconsistency the freeze names in section 1.2, measured on
    authored cases rather than on redactions.

``S_INCOMPARABLE`` (6)
    One coordinate absent on exactly one side, and the two predicates are not the
    same normalized relation, so the pair is ``UNRESOLVED`` for a reason that has
    nothing to do with the absence. A1 fires here and costs nothing. Without this
    stratum "A1 changed every pair it could fire on" would be unfalsifiable.

``C_FULLY_OBSERVED`` (6)
    No absence at all, on either side. A1 must not fire. Without this stratum
    ``fraction_changed`` would have no denominator that A1 was supposed to leave
    alone.

Gold is derived by :func:`gold_from_standard` from the frozen table this module
emits beside the corpus, by one stated rule, and **not** by calling
``compare_meaning``. On fully observed pairs the rule and ``compare_meaning``
agree, and the build report records that agreement case by case rather than
asserting it; on the partially observed pairs of ``D_DECISIVE_ABSENCE`` they
disagree, and that disagreement is the finding.

What this corpus can and cannot support, stated here so it is carried wherever
it is cited: the cases are **synthetic**. They establish that
``compare_meaning``'s reading of a one-sided absence is wrong in a specific way
and that an abstain-on-asymmetry repair destroys correct answers at a specific
rate *on pairs of this shape*. They establish nothing about how often scientific
sources state a coordinate on one side only. No accuracy, false-merge,
false-split or superiority number over this corpus is evidence about ORION's
competence on scientific text.

Build it::

    python -m orion.study.p3.partial_observation_harm_build --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    compare_meaning,
)
from orion.study.p3_public_reference import (
    SCHEMA_VERSION,
    projection_from_dict,
    validate_case,
)

PROTOCOL_ID = "P3.partial-observation-harm-corpus.v1"
ATLAS_ID = "partial-observation-harm-v1"
CORPUS_DIR = "research/p3-partial-observation-harm-v1"
CASES_FILENAME = "cases.jsonl"
STANDARD_FILENAME = "PARTIAL_OBSERVATION_HARM_STANDARD.json"
BUILD_REPORT_FILENAME = "BUILD_REPORT.json"
CONSTRUCTION_DOCUMENT = f"{CORPUS_DIR}/CONSTRUCTION_2026-08-22.md"
STANDARD_DATASET = "ORION-P3-PartialObservationHarmStandard"
STANDARD_SCHEMA_VERSION = "orion.p3.partial-observation-harm-standard.v1"
BUILD_REPORT_SCHEMA_VERSION = "orion.p3.partial-observation-harm-build-report.v1"
DERIVATION_RULE = "identity:observed-coordinate-precedence-with-completion-invariance"

#: The nine identity coordinates, in the precedence order the derivation rule
#: reads them. Held in this order rather than imported so that a reordering of
#: the probe's table cannot silently redefine this corpus's gold.
COORDINATES: tuple[str, ...] = (
    "referent_ids",
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
    "attribution_id",
    "discourse_relation",
    "assumption_ids",
    "polarity",
    "modality",
)

#: The single value each coordinate's type uses for both "assessed, nothing
#: there" and "never assessed". Identical to the probe's table by construction;
#: :func:`absent_value_agreement` checks that rather than assuming it.
ABSENT_VALUE: dict[str, Any] = {
    "referent_ids": (),
    "construct_ids": (),
    "measurement_ids": (),
    "temporal_context_ids": (),
    "attribution_id": "",
    "discourse_relation": "",
    "assumption_ids": (),
    "polarity": Polarity.UNKNOWN,
    "modality": Modality.UNKNOWN,
}

#: Every value each coordinate is allowed to take in this corpus. The admissible
#: completions of a one-sided absence are drawn from here, so "the answer does
#: not depend on the absent coordinate" is a finite, checkable claim rather than
#: a hand wave. Three values per coordinate, so a completion can agree with the
#: mirror side and can also differ from it.
COORDINATE_VALUES: dict[str, tuple[Any, ...]] = {
    "referent_ids": (
        ("poharm:referent:00",),
        ("poharm:referent:01",),
        ("poharm:referent:02",),
    ),
    "construct_ids": (
        ("poharm:construct:00",),
        ("poharm:construct:01",),
        ("poharm:construct:02",),
    ),
    "measurement_ids": (
        ("poharm:measurement:00",),
        ("poharm:measurement:01",),
        ("poharm:measurement:02",),
    ),
    "temporal_context_ids": (
        ("poharm:temporal:00",),
        ("poharm:temporal:01",),
        ("poharm:temporal:02",),
    ),
    "attribution_id": (
        "poharm:attribution:00",
        "poharm:attribution:01",
        "poharm:attribution:02",
    ),
    "discourse_relation": (
        "poharm:discourse:00",
        "poharm:discourse:01",
        "poharm:discourse:02",
    ),
    "assumption_ids": (
        ("poharm:assumption:00",),
        ("poharm:assumption:01",),
        ("poharm:assumption:02",),
    ),
    "polarity": (Polarity.POSITIVE, Polarity.NEGATED),
    "modality": (Modality.ASSERTED, Modality.POSSIBLE, Modality.PROBABLE),
}

#: One normalized predicate per comparable pair. Two projections whose predicates
#: are not the same entry of this table are not yet comparable at all.
PREDICATES: tuple[str, ...] = ("reports_quantity", "reports_observed_state")

DISCIPLINES: tuple[str, ...] = ("biology", "chemistry", "materials", "physics")

STRATUM_H = "H_UNDECISIVE_ABSENCE"
STRATUM_D = "D_DECISIVE_ABSENCE"
STRATUM_S = "S_INCOMPARABLE"
STRATUM_C = "C_FULLY_OBSERVED"

STRATUM_ORDER: tuple[str, ...] = (STRATUM_H, STRATUM_D, STRATUM_S, STRATUM_C)

CASE_FAMILY: dict[str, str] = {
    STRATUM_H: "partial_observation_undecisive_absence",
    STRATUM_D: "partial_observation_decisive_absence",
    STRATUM_S: "partial_observation_incomparable_predicates",
    STRATUM_C: "partial_observation_fully_observed_control",
}

#: ``H`` sub-stratum 1: the pair is decided at ``referent_ids``, so anything at
#: or below ``construct_ids`` can go missing on one side without moving it.
H_REFERENT_ABSENT: tuple[str, ...] = (
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
    "attribution_id",
    "discourse_relation",
    "assumption_ids",
)

#: ``H`` sub-stratum 2: the pair is decided at ``construct_ids``.
H_CONSTRUCT_ABSENT: tuple[str, ...] = (
    "measurement_ids",
    "temporal_context_ids",
    "attribution_id",
    "discourse_relation",
    "assumption_ids",
    "modality",
)

#: ``S``: which coordinate is silenced. The answer does not turn on it either
#: way, because the predicates already make the pair incomparable.
S_ABSENT: tuple[str, ...] = (
    "referent_ids",
    "measurement_ids",
    "attribution_id",
    "discourse_relation",
    "polarity",
    "modality",
)

EXTERNAL_VALIDITY = (
    "The cases are synthetic: gold follows from the emitted standard table by the rule "
    f"{DERIVATION_RULE}, not from an upstream expert corpus. This corpus can establish that "
    "compare_meaning misreads a one-sided absence and that an abstain-on-asymmetry repair "
    "destroys correct answers on pairs of this shape. It cannot establish that such pairs are "
    "frequent in public scientific corpora, and it may not be substituted for the "
    "public-reference atlas in any external-validity claim."
)

ACCURACY_CAVEAT = (
    "This corpus is a harm-gate denominator, not an accuracy benchmark. Its gold on the fully "
    "determined strata is derived by a precedence rule that coincides with what compare_meaning "
    "does on fully observed pairs, so the current system answers those by construction. That is "
    "what a harm measurement needs --- its question is whether a candidate rule moves a decision "
    "the current rule already gets right --- and it is what an accuracy claim must not be built "
    "on. No accuracy, false-merge, false-split or superiority number over this corpus is evidence "
    "about ORION's competence."
)

GATE_NOTE = (
    "G6_HARM_A1 reads 'A1_observedness_asymmetric changes 0 decisions on all intact corpora'. "
    "Adding a corpus to that gate can only leave it where it is or make it fail; no construction "
    "of this corpus can turn it into a pass. The gate's threshold is not amended, only its "
    "denominator."
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decimal_digest(payload: str, width: int = 16) -> str:
    """A fixed-width, all-digit content digest.

    All-digit for the same reason ``p3_coordinate_necessity_build`` uses one: a
    hex digest's leading non-digit run varies across cases, which an
    identifiability probe reads as a construction cue for whatever the digest
    happens to correlate with. Constant alphabetic prefix by construction.
    """

    if width <= 0:
        raise ValueError("a digest needs a positive width")
    return str(int(_sha(payload.encode("utf-8")), 16) % (10**width)).zfill(width)


# --------------------------------------------------------------------------
# The derivation rule
# --------------------------------------------------------------------------


def observed(projection: ScientificMeaningProjection, coordinate: str) -> bool:
    if coordinate not in ABSENT_VALUE:
        raise KeyError(f"{coordinate} is not one of the nine identity coordinates")
    return getattr(projection, coordinate) != ABSENT_VALUE[coordinate]


def one_sided_absences(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> tuple[str, ...]:
    return tuple(
        coordinate
        for coordinate in COORDINATES
        if observed(left, coordinate) != observed(right, coordinate)
    )


def relation_from_observed(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """The relation of a pair in which every coordinate is stated on both sides.

    Written out rather than delegated to ``compare_meaning`` so that gold is not
    defined by the system under test. It reads the coordinates in one fixed
    precedence order and stops at the first that separates. It is defined only on
    fully observed pairs, and raises on any other input rather than guessing ---
    guessing on an absence is the defect this corpus exists to measure.
    """

    for side in (left, right):
        missing = [name for name in COORDINATES if not observed(side, name)]
        if missing:
            raise ValueError(
                "relation_from_observed is defined only on fully observed pairs; "
                f"{side.projection_id} does not state {', '.join(missing)}"
            )
    if left.unresolved_ambiguities or right.unresolved_ambiguities:
        return MeaningRelation.UNRESOLVED
    if left.predicate != right.predicate:
        return MeaningRelation.UNRESOLVED
    if left.referent_ids != right.referent_ids:
        return MeaningRelation.DISTINCT_REFERENT
    if left.construct_ids != right.construct_ids:
        return MeaningRelation.DISTINCT_CONSTRUCT
    if left.measurement_ids != right.measurement_ids:
        return MeaningRelation.DISTINCT_MEASUREMENT
    if (
        left.temporal_context_ids != right.temporal_context_ids
        or left.attribution_id != right.attribution_id
        or left.discourse_relation != right.discourse_relation
        or left.assumption_ids != right.assumption_ids
        or left.modality != right.modality
    ):
        return MeaningRelation.CONTEXTUAL_DIFFERENCE
    if left.polarity != right.polarity:
        if left.modality is Modality.ASSERTED and right.modality is Modality.ASSERTED:
            return MeaningRelation.CONTRADICTORY
        return MeaningRelation.CONTEXTUAL_DIFFERENCE
    return MeaningRelation.COMPATIBLE


def admissible_completions(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> Iterator[tuple[Any, ScientificMeaningProjection, ScientificMeaningProjection]]:
    """Every world the pair could be in, given what the two sources did not say.

    One completion per admissible value of each coordinate absent on exactly one
    side. The table is finite and frozen, so "the answer does not depend on the
    absence" is decidable here rather than argued.
    """

    absences = one_sided_absences(left, right)
    if not absences:
        yield ((), left, right)
        return
    if len(absences) != 1:
        raise ValueError(
            "this corpus states at most one one-sided absence per pair; "
            f"found {absences}"
        )
    coordinate = absences[0]
    silent_side = "left" if not observed(left, coordinate) else "right"
    for value in COORDINATE_VALUES[coordinate]:
        if silent_side == "left":
            yield ((coordinate, value), replace(left, **{coordinate: value}), right)
        else:
            yield ((coordinate, value), left, replace(right, **{coordinate: value}))


def gold_from_standard(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """Gold by the frozen rule.

    1. Predicates that are not the same normalized relation leave the pair
       ``UNRESOLVED``: it is not yet the kind of pair the coordinates describe.
    2. Otherwise, if the relation is not the same in every admissible completion
       of what one source did not state, the pair is ``UNRESOLVED``. Nothing in
       the two projections separates the world in which the silence hides an
       agreement from the world in which it hides a difference.
    3. Otherwise the relation is that constant value.
    """

    if left.predicate != right.predicate:
        return MeaningRelation.UNRESOLVED
    relations = {
        relation_from_observed(completed_left, completed_right)
        for _value, completed_left, completed_right in admissible_completions(left, right)
    }
    if len(relations) == 1:
        return relations.pop()
    return MeaningRelation.UNRESOLVED


# --------------------------------------------------------------------------
# The frozen standard
# --------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return getattr(value, "value", value)


def standard_document() -> dict[str, Any]:
    return {
        "schema_version": STANDARD_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "atlas_id": ATLAS_ID,
        "derivation_rule": DERIVATION_RULE,
        "derivation_rule_statement": (
            "Two projections whose predicates are not the same entry of this table are "
            "UNRESOLVED. Otherwise, complete every coordinate this table lists that is stated "
            "on exactly one side with each admissible value of that coordinate in this table; "
            "if the relation read off the completed pair -- referent, then construct, then "
            "measurement, then the contextual coordinates (temporal, attribution, discourse, "
            "assumption, modal force), then polarity -- is not the same for every completion, "
            "the pair is UNRESOLVED. Otherwise it is that relation."
        ),
        "coordinate_precedence": list(COORDINATES),
        "absent_values": {name: _jsonable(value) for name, value in ABSENT_VALUE.items()},
        "admissible_values": {
            name: [_jsonable(value) for value in values]
            for name, values in COORDINATE_VALUES.items()
        },
        "predicates": list(PREDICATES),
        "disciplines": list(DISCIPLINES),
        "strata": {
            STRATUM_H: (
                "one coordinate absent on exactly one side, decided by a strictly "
                "higher-precedence coordinate; gold determinate"
            ),
            STRATUM_D: (
                "one coordinate absent on exactly one side, everything else equal; gold "
                "UNRESOLVED because the completions disagree"
            ),
            STRATUM_S: (
                "one coordinate absent on exactly one side, predicates not comparable; gold "
                "UNRESOLVED for a reason unrelated to the absence"
            ),
            STRATUM_C: "no coordinate absent on either side; gold determinate",
        },
        "gate_note": GATE_NOTE,
        "external_validity": EXTERNAL_VALIDITY,
        "not_an_accuracy_benchmark": ACCURACY_CAVEAT,
    }


def standard_bytes() -> bytes:
    return json.dumps(standard_document(), indent=2, sort_keys=True).encode("utf-8") + b"\n"


def standard_hash() -> str:
    return _sha(standard_bytes())


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------


def _base_values() -> dict[str, Any]:
    """The value every coordinate takes unless a stratum overrides it."""

    return {name: values[0] for name, values in COORDINATE_VALUES.items()}


def _case_specs() -> list[dict[str, Any]]:
    """Every case as a plain description, before any projection is built.

    Kept separate from :func:`_case` so the shape of the corpus is readable in
    one place and so the counts in the construction document can be checked
    against it.
    """

    specs: list[dict[str, Any]] = []

    for index, coordinate in enumerate(H_REFERENT_ABSENT):
        specs.append(
            {
                "stratum": STRATUM_H,
                "slot": index,
                "decided_by": "referent_ids",
                "absent_coordinate": coordinate,
                "absent_side": "left" if index % 2 == 0 else "right",
                "differ_coordinate": "referent_ids",
            }
        )
    for index, coordinate in enumerate(H_CONSTRUCT_ABSENT):
        specs.append(
            {
                "stratum": STRATUM_H,
                "slot": len(H_REFERENT_ABSENT) + index,
                "decided_by": "construct_ids",
                "absent_coordinate": coordinate,
                "absent_side": "right" if index % 2 == 0 else "left",
                "differ_coordinate": "construct_ids",
            }
        )
    for index, coordinate in enumerate(COORDINATES):
        specs.append(
            {
                "stratum": STRATUM_D,
                "slot": index,
                "decided_by": coordinate,
                "absent_coordinate": coordinate,
                "absent_side": "left" if index % 2 == 0 else "right",
                "differ_coordinate": None,
            }
        )
    for index, coordinate in enumerate(S_ABSENT):
        specs.append(
            {
                "stratum": STRATUM_S,
                "slot": index,
                "decided_by": "predicate",
                "absent_coordinate": coordinate,
                "absent_side": "right" if index % 2 == 0 else "left",
                "differ_coordinate": None,
            }
        )
    for index in range(6):
        specs.append(
            {
                "stratum": STRATUM_C,
                "slot": index,
                "decided_by": "referent_ids" if index % 2 == 0 else None,
                "absent_coordinate": None,
                "absent_side": None,
                "differ_coordinate": "referent_ids" if index % 2 == 0 else None,
            }
        )
    return specs


def _projection_payload(
    side: str, digest: str, predicate: str, values: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "projection_id": f"poharm:{digest}:{side}",
        "source_id": "orion-p3-partial-observation-harm-standard",
        "source_span": f"{STANDARD_FILENAME}#case={digest}&side={side}",
        "predicate": predicate,
        "referent_ids": list(values["referent_ids"]),
        "construct_ids": list(values["construct_ids"]),
        "measurement_ids": list(values["measurement_ids"]),
        "temporal_context_ids": list(values["temporal_context_ids"]),
        "attribution_id": values["attribution_id"],
        "discourse_relation": values["discourse_relation"],
        "assumption_ids": list(values["assumption_ids"]),
        "polarity": values["polarity"].value,
        "modality": values["modality"].value,
    }


def _case(spec: Mapping[str, Any], *, standard_sha: str) -> dict[str, Any]:
    stratum = str(spec["stratum"])
    slot = int(spec["slot"])
    left_values = _base_values()
    right_values = _base_values()

    differ = spec["differ_coordinate"]
    if differ is not None:
        right_values[str(differ)] = COORDINATE_VALUES[str(differ)][1]

    absent = spec["absent_coordinate"]
    if absent is not None:
        target = left_values if spec["absent_side"] == "left" else right_values
        target[str(absent)] = ABSENT_VALUE[str(absent)]

    left_predicate = PREDICATES[0]
    right_predicate = PREDICATES[1] if stratum == STRATUM_S else PREDICATES[0]

    digest = _decimal_digest(
        "|".join(
            [
                PROTOCOL_ID,
                stratum,
                str(slot),
                str(spec["decided_by"]),
                str(absent),
                str(spec["absent_side"]),
                left_predicate,
                right_predicate,
                json.dumps(
                    {name: _jsonable(value) for name, value in sorted(left_values.items())},
                    sort_keys=True,
                ),
                json.dumps(
                    {name: _jsonable(value) for name, value in sorted(right_values.items())},
                    sort_keys=True,
                ),
            ]
        )
    )

    left_payload = _projection_payload("l", digest, left_predicate, left_values)
    right_payload = _projection_payload("r", digest, right_predicate, right_values)
    relation = gold_from_standard(
        projection_from_dict(left_payload), projection_from_dict(right_payload)
    )

    case = {
        "schema_version": SCHEMA_VERSION,
        "case_id": f"poharm-{digest}",
        "discipline": DISCIPLINES[slot % len(DISCIPLINES)],
        "case_family": CASE_FAMILY[stratum],
        "source_records": [
            {
                "dataset": STANDARD_DATASET,
                "revision": standard_sha,
                "locator": STANDARD_FILENAME,
                "content_hash": standard_sha,
                "license": "CC0-1.0",
            }
        ],
        "left_projection": left_payload,
        "right_projection": right_payload,
        "expected": {
            "meaning_relation": relation.value,
            "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [
                    f"{STANDARD_DATASET}@{standard_sha}:{STANDARD_FILENAME}#case={digest}&side=l",
                    f"{STANDARD_DATASET}@{standard_sha}:{STANDARD_FILENAME}#case={digest}&side=r",
                ],
                "derivation": {
                    "rule": DERIVATION_RULE,
                    "inputs": [
                        f"stratum={stratum}",
                        f"decided_by={spec['decided_by']}",
                        f"absent_coordinate={absent}",
                        f"absent_side={spec['absent_side']}",
                    ],
                },
            },
        },
        "partial_observation": {
            "stratum": stratum,
            "absent_coordinate": absent,
            "absent_side": spec["absent_side"],
            "decided_by": spec["decided_by"],
        },
    }
    validate_case(case)
    return case


def harm_cases() -> list[dict[str, Any]]:
    """The 33 cases, emitted in ``case_id`` sort order."""

    standard_sha = standard_hash()
    cases = [_case(spec, standard_sha=standard_sha) for spec in _case_specs()]
    ids = [str(case["case_id"]) for case in cases]
    if len(set(ids)) != len(ids):  # pragma: no cover - a collision would be a hash break
        raise ValueError("partial-observation harm case ids collided")
    return sorted(cases, key=lambda case: str(case["case_id"]))


# --------------------------------------------------------------------------
# Receipts: every construction claim, checked rather than asserted
# --------------------------------------------------------------------------


class HarmCorpusError(RuntimeError):
    """Raised when the corpus does not have the structure the gate needs."""


def _pair(case: Mapping[str, Any]) -> tuple[ScientificMeaningProjection, ScientificMeaningProjection]:
    return (
        projection_from_dict(case["left_projection"]),
        projection_from_dict(case["right_projection"]),
    )


def absent_value_agreement() -> dict[str, Any]:
    """This module's absent-value table against the probe's, coordinate by coordinate.

    Two modules that disagree about what "absent" is would silently measure two
    different things, and the disagreement would show up as a gate number rather
    than as an error.
    """

    from .partial_observation_probe import ABSENT_VALUE as PROBE_ABSENT_VALUE

    mismatched = sorted(
        name
        for name in set(ABSENT_VALUE) | set(PROBE_ABSENT_VALUE)
        if ABSENT_VALUE.get(name, object()) != PROBE_ABSENT_VALUE.get(name, object())
    )
    return {
        "coordinates_compared": sorted(set(ABSENT_VALUE) | set(PROBE_ABSENT_VALUE)),
        "mismatched": mismatched,
        "agrees": not mismatched,
    }


def construction_receipts(cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Per case: what the standard derives, what ``compare_meaning`` answers, and why."""

    receipts: list[dict[str, Any]] = []
    for case in cases:
        left, right = _pair(case)
        meta = case["partial_observation"]
        assert isinstance(meta, Mapping)
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        completions = sorted(
            {
                relation_from_observed(completed_left, completed_right).value
                for _value, completed_left, completed_right in admissible_completions(left, right)
            }
        )
        current = compare_meaning(left, right).relation
        receipts.append(
            {
                "case_id": str(case["case_id"]),
                "stratum": str(meta["stratum"]),
                "absent_coordinate": meta["absent_coordinate"],
                "absent_side": meta["absent_side"],
                "decided_by": meta["decided_by"],
                "one_sided_absences": list(one_sided_absences(left, right)),
                "relations_over_admissible_completions": completions,
                "gold": gold.value,
                "gold_is_determinate": gold is not MeaningRelation.UNRESOLVED,
                "compare_meaning": current.value,
                "compare_meaning_reproduces_gold": current is gold,
                "abstain_on_one_sided_absence_would_change_the_answer": (
                    bool(one_sided_absences(left, right))
                    and current is not MeaningRelation.UNRESOLVED
                ),
                "abstain_on_one_sided_absence_would_destroy_a_correct_answer": (
                    bool(one_sided_absences(left, right))
                    and current is gold
                    and gold is not MeaningRelation.UNRESOLVED
                ),
            }
        )
    return receipts


def rule_agreement_on_fully_observed(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The derivation rule against ``compare_meaning`` on every completed pair.

    The rule is written out independently so gold is not defined by the system
    under test. That independence is only worth anything if the two are checked
    against each other where both are defined --- on pairs with nothing missing.
    A disagreement there would mean the corpus measures a rule ORION does not
    have, and the build refuses.
    """

    compared = 0
    offenders: list[dict[str, str]] = []
    for case in cases:
        left, right = _pair(case)
        for _value, completed_left, completed_right in admissible_completions(left, right):
            derived = relation_from_observed(completed_left, completed_right)
            current = compare_meaning(completed_left, completed_right).relation
            compared += 1
            if derived is not current:
                offenders.append(
                    {
                        "case_id": str(case["case_id"]),
                        "rule": derived.value,
                        "compare_meaning": current.value,
                    }
                )
    return {
        "completed_pairs_compared": compared,
        "disagreements": len(offenders),
        "offenders": offenders[:8],
        "agrees_everywhere": not offenders,
    }


def absence_reading_census(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What ``compare_meaning`` does with a one-sided absence, one cell per coordinate.

    Read off ``D_DECISIVE_ABSENCE``, where the absent coordinate is the only
    thing that could separate the pair. ``MERGE_WARD`` means the rule read the
    silence as agreement and merged; ``SEPARATION_WARD`` means it read it as a
    distinct value and separated. Both are wrong in the same way --- gold is
    ``UNRESOLVED`` --- and the freeze's claim that they split eight to one is
    measured here rather than quoted.
    """

    from .partial_observation_probe import ABSENCE_READING

    cells: dict[str, dict[str, Any]] = {}
    for case in cases:
        meta = case["partial_observation"]
        assert isinstance(meta, Mapping)
        if str(meta["stratum"]) != STRATUM_D:
            continue
        left, right = _pair(case)
        current = compare_meaning(left, right).relation
        reading = (
            "MERGE_WARD"
            if current is MeaningRelation.COMPATIBLE
            else "ABSTAINED"
            if current is MeaningRelation.UNRESOLVED
            else "SEPARATION_WARD"
        )
        coordinate = str(meta["absent_coordinate"])
        cells[coordinate] = {
            "case_id": str(case["case_id"]),
            "compare_meaning": current.value,
            "observed_reading": reading,
            "freeze_declared_reading": ABSENCE_READING.get(coordinate),
            "matches_freeze": (
                (reading == "MERGE_WARD")
                == (ABSENCE_READING.get(coordinate) == "AGREEMENT")
            ),
        }
    counts: dict[str, int] = {}
    for cell in cells.values():
        counts[str(cell["observed_reading"])] = counts.get(str(cell["observed_reading"]), 0) + 1
    return {
        "by_coordinate": cells,
        "counts": counts,
        "every_cell_matches_the_freeze": all(bool(cell["matches_freeze"]) for cell in cells.values()),
    }


def one_sided_absence_census(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    total = 0
    for case in cases:
        left, right = _pair(case)
        absences = one_sided_absences(left, right)
        if absences:
            total += 1
        for coordinate in absences:
            counts[coordinate] = counts.get(coordinate, 0) + 1
    return {
        "n_pairs": len(cases),
        "n_pairs_with_a_one_sided_absence": total,
        "by_coordinate": dict(sorted(counts.items())),
        "coordinates_never_one_sided": sorted(set(COORDINATES) - set(counts)),
    }


def harm_preview(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What an abstain-on-one-sided-absence rule costs on this corpus.

    A preview, computed from the construction receipts. The probe is the
    authority for the gate number; this exists so the builder cannot emit a
    corpus that silently has no harm opportunities in it.
    """

    could_fire = [row for row in receipts if row["one_sided_absences"]]
    changed = [row for row in could_fire if row["abstain_on_one_sided_absence_would_change_the_answer"]]
    destroyed = [
        row
        for row in could_fire
        if row["abstain_on_one_sided_absence_would_destroy_a_correct_answer"]
    ]
    return {
        "n_cases": len(receipts),
        "pairs_where_it_could_fire": len(could_fire),
        "decisions_it_would_change": len(changed),
        "correct_answers_it_would_destroy": len(destroyed),
        "destroyed_case_ids": sorted(str(row["case_id"]) for row in destroyed),
    }


def shape_invariants(cases: Sequence[Mapping[str, Any]]) -> dict[str, list[Any]]:
    """Construction-level shapes held constant across every case."""

    seen: dict[str, set[Any]] = {
        "case_id_length": set(),
        "case_id_hyphen_count": set(),
        "case_id_alpha_prefix": set(),
        "projection_id_length": set(),
        "source_span_length": set(),
        "source_record_count": set(),
        "authority_kind": set(),
        "derivation_rule": set(),
    }
    for case in cases:
        case_id = str(case["case_id"])
        seen["case_id_length"].add(len(case_id))
        seen["case_id_hyphen_count"].add(case_id.count("-"))
        seen["case_id_alpha_prefix"].add(case_id.split("-")[0])
        seen["source_record_count"].add(len(list(case["source_records"])))
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        authority = expected["authority"]
        assert isinstance(authority, Mapping)
        seen["authority_kind"].add(str(authority["kind"]))
        derivation = authority["derivation"]
        assert isinstance(derivation, Mapping)
        seen["derivation_rule"].add(str(derivation["rule"]))
        for side in ("left_projection", "right_projection"):
            payload = case[side]
            assert isinstance(payload, Mapping)
            seen["projection_id_length"].add(len(str(payload["projection_id"])))
            seen["source_span_length"].add(len(str(payload["source_span"])))
    return {name: sorted(values) for name, values in seen.items()}


# --------------------------------------------------------------------------
# Build report and emission
# --------------------------------------------------------------------------

#: What each stratum must be true of, checked before the corpus is written.
STRATUM_CONTRACT: dict[str, dict[str, Any]] = {
    STRATUM_H: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": True,
        "compare_meaning_reproduces_gold": True,
    },
    STRATUM_D: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": False,
        "compare_meaning_reproduces_gold": False,
    },
    STRATUM_S: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": False,
        "compare_meaning_reproduces_gold": True,
    },
    STRATUM_C: {
        "n_one_sided_absences": 0,
        "gold_is_determinate": True,
        "compare_meaning_reproduces_gold": True,
    },
}


def verify(cases: Sequence[Mapping[str, Any]], receipts: Sequence[Mapping[str, Any]]) -> None:
    """Refuse to emit a corpus that does not have the structure the gate needs.

    A corpus with no one-sided absence would leave G6 exactly as vacuous as it
    was; a corpus whose determinate strata ``compare_meaning`` already gets wrong
    would let an abstaining arm look harmless for the wrong reason. Both are
    checked here, not trusted.
    """

    for row in receipts:
        contract = STRATUM_CONTRACT[str(row["stratum"])]
        n_absences = len(list(row["one_sided_absences"]))
        if n_absences != contract["n_one_sided_absences"]:
            raise HarmCorpusError(
                f"{row['case_id']}: {row['stratum']} requires "
                f"{contract['n_one_sided_absences']} one-sided absence(s), found {n_absences}"
            )
        if bool(row["gold_is_determinate"]) is not contract["gold_is_determinate"]:
            raise HarmCorpusError(
                f"{row['case_id']}: {row['stratum']} requires gold determinate="
                f"{contract['gold_is_determinate']}, derived {row['gold']}"
            )
        if bool(row["compare_meaning_reproduces_gold"]) is not contract[
            "compare_meaning_reproduces_gold"
        ]:
            raise HarmCorpusError(
                f"{row['case_id']}: {row['stratum']} requires "
                f"compare_meaning_reproduces_gold={contract['compare_meaning_reproduces_gold']}, "
                f"got gold={row['gold']} compare_meaning={row['compare_meaning']}"
            )

    census = one_sided_absence_census(cases)
    if census["n_pairs_with_a_one_sided_absence"] == 0:
        raise HarmCorpusError(
            "the corpus has no one-sided absence, so it leaves G6_HARM_A1 exactly as vacuous "
            "as it was"
        )
    preview = harm_preview(receipts)
    if preview["correct_answers_it_would_destroy"] == 0:
        raise HarmCorpusError(
            "no pair on which an abstain-on-asymmetry rule could destroy a correct answer; "
            "a harm gate over this corpus could not report a harm even if one existed"
        )
    if preview["pairs_where_it_could_fire"] == preview["decisions_it_would_change"]:
        raise HarmCorpusError(
            "every pair the rule can fire on is a pair it changes; without a stratum it fires "
            "on harmlessly, 'it changed everything' would be unfalsifiable"
        )
    agreement = rule_agreement_on_fully_observed(cases)
    if not agreement["agrees_everywhere"]:
        raise HarmCorpusError(
            "the derivation rule and compare_meaning disagree on a fully observed pair: "
            f"{agreement['offenders']}"
        )
    if not absent_value_agreement()["agrees"]:
        raise HarmCorpusError(
            "this module and the probe disagree about which value means 'absent'"
        )
    reading = absence_reading_census(cases)
    if not reading["every_cell_matches_the_freeze"]:
        raise HarmCorpusError(
            "the measured absence reading does not match the freeze's declared table: "
            f"{reading['by_coordinate']}"
        )


def cases_bytes(cases: Sequence[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
        for case in cases
    ).encode("utf-8")


def build_report(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    receipts = construction_receipts(cases)
    strata: dict[str, int] = {}
    relations: dict[str, int] = {}
    for case in cases:
        meta = case["partial_observation"]
        assert isinstance(meta, Mapping)
        strata[str(meta["stratum"])] = strata.get(str(meta["stratum"]), 0) + 1
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        relation = str(expected["meaning_relation"])
        relations[relation] = relations.get(relation, 0) + 1
    return {
        "schema_version": BUILD_REPORT_SCHEMA_VERSION,
        "record": "P3_PARTIAL_OBSERVATION_HARM_CORPUS_BUILD",
        "date": "2026-08-22",
        "atlas_id": ATLAS_ID,
        "protocol_id": PROTOCOL_ID,
        "builder": "src/orion/study/p3/partial_observation_harm_build.py",
        "construction_document": CONSTRUCTION_DOCUMENT,
        "gate_served": "G6_HARM_A1",
        "gate_note": GATE_NOTE,
        "built_n": len(cases),
        "cases_hash": _sha(cases_bytes(cases)),
        "standard_sha256": standard_hash(),
        "strata": dict(sorted(strata.items())),
        "expected_relations": dict(sorted(relations.items())),
        "one_sided_absence_census": one_sided_absence_census(cases),
        "absent_value_agreement": absent_value_agreement(),
        "rule_agreement_on_fully_observed": rule_agreement_on_fully_observed(cases),
        "absence_reading_census": absence_reading_census(cases),
        "harm_preview": harm_preview(receipts),
        "shape_invariants": shape_invariants(cases),
        "construction_receipts": receipts,
        "synthetic_case_count": len(cases),
        "external_validity": EXTERNAL_VALIDITY,
        "not_an_accuracy_benchmark": ACCURACY_CAVEAT,
    }


def write_corpus(repo_root: Path) -> dict[str, Any]:
    """Emit the standard, the cases and the build report. Verifies before writing."""

    cases = harm_cases()
    receipts = construction_receipts(cases)
    verify(cases, receipts)
    report = build_report(cases)

    directory = repo_root / CORPUS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    (directory / STANDARD_FILENAME).write_bytes(standard_bytes())
    (directory / CASES_FILENAME).write_bytes(cases_bytes(cases))
    (directory / BUILD_REPORT_FILENAME).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build the P3 partial-observation harm corpus (G6_HARM_A1 denominator)."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the corpus, standard and build report into the repository",
    )
    args = parser.parse_args(list(argv))

    if args.write:
        report = write_corpus(args.repo_root)
    else:
        cases = harm_cases()
        receipts = construction_receipts(cases)
        verify(cases, receipts)
        report = build_report(cases)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(__import__("sys").argv[1:]))


__all__ = [
    "ABSENT_VALUE",
    "ATLAS_ID",
    "CASES_FILENAME",
    "COORDINATES",
    "COORDINATE_VALUES",
    "CORPUS_DIR",
    "DERIVATION_RULE",
    "HarmCorpusError",
    "PROTOCOL_ID",
    "STRATUM_C",
    "STRATUM_CONTRACT",
    "STRATUM_D",
    "STRATUM_H",
    "STRATUM_ORDER",
    "STRATUM_S",
    "absence_reading_census",
    "absent_value_agreement",
    "admissible_completions",
    "build_report",
    "cases_bytes",
    "construction_receipts",
    "gold_from_standard",
    "harm_cases",
    "harm_preview",
    "main",
    "observed",
    "one_sided_absence_census",
    "one_sided_absences",
    "relation_from_observed",
    "rule_agreement_on_fully_observed",
    "shape_invariants",
    "standard_bytes",
    "standard_document",
    "standard_hash",
    "verify",
    "write_corpus",
]
