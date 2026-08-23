"""Build the corpus that gives the A3 harm gate a non-circular denominator (P3-U-T5, G9).

``orion.study.p3.partial_observation_probe`` reports gate ``G9_HARM_A3`` as
``CANNOT_CHECK``, in its own words:

    A3 destroyed 0 correct answers and repaired 9, but no intact corpus supplies
    independent evidence for that zero.

Two holes, one on each side. The three corpora frozen on 2026-08-21 state every
coordinate on both sides of every pair or on neither, so ``A3`` is ``A0`` on all
of them and its zero is structural. ``research/p3-partial-observation-harm-v1/``
does have one-sided absences, but it derives its gold by
``identity:observed-coordinate-precedence-with-completion-invariance`` --- abstain
where the admissible completions of the absent coordinate disagree --- which is
``A3``'s decision rule, so agreeing with that gold is A3's definition restated.

Amendment 002 recorded that the gate is discharged by

    an intact corpus with one-sided absences whose gold is fixed by adjudication,
    or by any rule that does not ask whether the completions agree, containing at
    least one partially observed pair A0 answers correctly

and then said building one "is not a construction task: under partial observation
the relation is genuinely underdetermined, so an independent gold has to come from
adjudicators rather than from a rule". That last sentence conflates two questions,
and this module is the correction.

**What is underdetermined is the inference, not the relation.** A pair of
``ScientificMeaningProjection`` objects is ORION's *view* of two source
statements. The relation between the two source statements is fixed by the
sources. When ORION's extractor carries a coordinate from one source and misses
it on the other, the pair acquires a one-sided absence without the sources having
changed: the ambiguity is in the extraction, not in the world. That is exactly
the situation ``identity:upstream-coreference-edge`` is already gold for --- the
MUSE cases of ``INTACT_DERIVATION`` state neither ``polarity`` nor ``modality`` on
either side, and their gold is ``COMPATIBLE`` anyway, because the annotator read
the sources rather than the projections. The rule never asks what the silence
could have hidden. It asks what the sources say.

This module builds a corpus with that structure. Each case is a **record pair**:
two source statements that state all nine identity coordinates, held in a frozen
standard emitted beside the corpus. Gold is the relation between the *records*,
by :func:`relation_from_records`, a precedence rule written out here rather than
delegated to ``compare_meaning`` and defined only on records that state
everything. An **extraction loss** then blanks one coordinate on one side of the
*projection*. Gold does not move: the record still says what it says.

So the corpus's gold is derived by ``identity:frozen-source-record-relation``, a
rule that never enumerates a completion, and A3 is scored against a standard it
did not write.

Four strata, 36 cases, a systematic census rather than a selection.

``LA_LOSS_ON_AGREEING_RECORDS`` (9)
    The two records state the *same* value of the lost coordinate; everything
    else is identical. Gold is ``COMPATIBLE``. One case per coordinate.

``LD_LOSS_ON_DIFFERING_RECORDS`` (9)
    The two records state *different* values of the lost coordinate; everything
    else is identical. Gold is whatever that difference makes it. One case per
    coordinate.

``LU_LOSS_A_HIGHER_COORDINATE_DECIDES`` (8)
    The records differ on ``referent_ids``, which is stated on both sides, and the
    loss is of some lower-precedence coordinate. Gold is ``DISTINCT_REFERENT``,
    and the loss could not have changed it. This is the stratum A3 is built to
    get right and A1 is built to get wrong; without it "A3 destroyed every answer
    it could have destroyed" would be unfalsifiable.

``NL_NO_LOSS`` (10)
    No extraction loss at all. Nine cases whose records differ on one coordinate
    each and one whose records agree everywhere. An observedness-sensitive arm
    must not fire here.

**LA and LD are both present on purpose, and dropping either is the failure mode
this corpus is guarding against.** On the merge-ward coordinates ``A0`` reads a
one-sided absence as agreement, so it is right on ``LA`` and wrong on ``LD``; on
``modality``, which it reads as a distinct value, it is wrong on ``LA`` and right
on ``LD``. The harm denominator is therefore whatever ``compare_meaning``'s own
eight-to-one inconsistency makes it, not whatever the author wanted. A corpus
built from ``LD`` alone would report ``A3`` destroying almost nothing, and would
be choosing cases by their effect on the gate --- the circularity of amendment 002
wearing a different hat. :func:`verify` refuses to emit a corpus that is missing
either half of any coordinate's pair.

What this corpus can and cannot support. The cases are **synthetic**: the records
are a frozen table this module emits, not an upstream expert corpus, because the
upstream corpora the public-reference builder draws on are not reachable from
this environment. It establishes what a decisiveness-aware abstention costs
*when the gold is anchored outside the projections*, on pairs of this shape. It
establishes nothing about how often scientific extraction drops a coordinate on
one side only. No accuracy, false-merge, false-split or superiority number over
it is evidence about ORION's competence on scientific text.

**Amendment 004 (2026-08-22).** The corpus is unchanged --- ``record_gold_cases()``
with no argument emits the shipped ``cases.jsonl`` byte for byte, and
``standard_document()`` the shipped standard --- and two things are added on top
of it, both in service of a bound rather than of a corpus.

:class:`RecordDraw` names the choices this standard leaves *free*: the id strings
the records use, which of the two values of a closed vocabulary each record
takes, and which side of a pair the extraction loss falls on. The standard fixes
none of them and :func:`relation_from_records` reads none of them.
:func:`fresh_draw` redraws them from a seed and :func:`held_out_corpus` builds and
:func:`verify`s the result without writing it, so a finding measured on the
shipped 36 cases can be re-measured on 36 nobody had in front of them. That is
the guard against a rule --- or a bound --- fitted to the cases it was derived
after seeing.

:func:`undecidability_witness_cases` builds the sharpest form of what amendment
004 establishes: for a coordinate, an ``LA`` case and an ``LD`` case whose loss
falls on the *same* side, whose shipped projections are then identical value for
value, and whose gold differs. Two legal cases of this corpus, one pair of
projections, two golds --- because the value that decides is the one the
extraction destroyed. Gold is not a function of the projections, which is why
``G9_HARM_A3``'s nine destroyed answers are a floor and not a defect.

Build it::

    python -m orion.study.p3.partial_observation_record_gold_build --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
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

PROTOCOL_ID = "P3.partial-observation-record-gold-corpus.v1"
ATLAS_ID = "partial-observation-record-gold-v1"
CORPUS_DIR = "research/p3-partial-observation-record-gold-v1"
CASES_FILENAME = "cases.jsonl"
STANDARD_FILENAME = "PARTIAL_OBSERVATION_RECORD_STANDARD.json"
BUILD_REPORT_FILENAME = "BUILD_REPORT.json"
CONSTRUCTION_DOCUMENT = f"{CORPUS_DIR}/CONSTRUCTION_2026-08-22.md"
STANDARD_DATASET = "ORION-P3-PartialObservationRecordStandard"
STANDARD_SCHEMA_VERSION = "orion.p3.partial-observation-record-standard.v1"
BUILD_REPORT_SCHEMA_VERSION = "orion.p3.partial-observation-record-gold-build-report.v1"

#: The gold-derivation rule this corpus declares on every case. It names the
#: source record, which is what gold is read off. It does not name
#: ``completion-invariance`` --- not as a matter of wording but because
#: :func:`relation_from_records` never enumerates a completion: it is defined only
#: on records that state every coordinate, and raises on anything else.
DERIVATION_RULE = "identity:frozen-source-record-relation"

#: The nine identity coordinates, in the precedence order the derivation rule
#: reads them. Written out rather than imported so that a reordering of the
#: probe's table cannot silently redefine this corpus's gold.
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
#: there" and "never assessed". A projection that has lost a coordinate to
#: extraction is indistinguishable from one whose source stated nothing, which is
#: the whole defect under study. :func:`absent_value_agreement` checks this table
#: against the probe's rather than assuming they match.
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

#: The two values each coordinate takes across a record pair: index 0 on both
#: records when they agree, index 0 and index 1 when they differ. Every value is
#: a value a *record* states, so none of them is the absent value --- a record
#: that stated nothing would not be a fully observed record.
RECORD_VALUES: dict[str, tuple[Any, ...]] = {
    "referent_ids": (("porec:referent:00",), ("porec:referent:01",)),
    "construct_ids": (("porec:construct:00",), ("porec:construct:01",)),
    "measurement_ids": (("porec:measurement:00",), ("porec:measurement:01",)),
    "temporal_context_ids": (("porec:temporal:00",), ("porec:temporal:01",)),
    "attribution_id": ("porec:attribution:00", "porec:attribution:01"),
    "discourse_relation": ("porec:discourse:00", "porec:discourse:01"),
    "assumption_ids": (("porec:assumption:00",), ("porec:assumption:01",)),
    "polarity": (Polarity.POSITIVE, Polarity.NEGATED),
    "modality": (Modality.ASSERTED, Modality.POSSIBLE),
}

#: The one normalized predicate every record in this corpus uses. This corpus has
#: no incomparable stratum: ``LU`` already supplies the pairs a decisiveness-aware
#: arm must leave alone, so a predicate mismatch would add nothing the gate reads.
PREDICATE = "reports_quantity"

DISCIPLINES: tuple[str, ...] = ("biology", "chemistry", "materials", "physics")

STRATUM_LA = "LA_LOSS_ON_AGREEING_RECORDS"
STRATUM_LD = "LD_LOSS_ON_DIFFERING_RECORDS"
STRATUM_LU = "LU_LOSS_A_HIGHER_COORDINATE_DECIDES"
STRATUM_NL = "NL_NO_LOSS"

STRATUM_ORDER: tuple[str, ...] = (STRATUM_LA, STRATUM_LD, STRATUM_LU, STRATUM_NL)

CASE_FAMILY: dict[str, str] = {
    STRATUM_LA: "extraction_loss_on_agreeing_records",
    STRATUM_LD: "extraction_loss_on_differing_records",
    STRATUM_LU: "extraction_loss_below_the_deciding_coordinate",
    STRATUM_NL: "complete_extraction_control",
}

#: The coordinate ``LU`` separates on. It is the top of the precedence order, so
#: every other coordinate can be lost below it.
LU_DECIDING_COORDINATE = "referent_ids"

EXTERNAL_VALIDITY = (
    "The cases are synthetic: the source records are a frozen table this module emits, not an "
    "upstream expert corpus, because the upstream corpora the public-reference builder draws on "
    "are not reachable from this environment. This corpus can establish what a "
    "decisiveness-aware abstention costs when gold is anchored to the source record rather than "
    "to the projections. It cannot establish that extraction drops a coordinate on one side only "
    "at any particular rate in public scientific corpora, and it may not be substituted for the "
    "public-reference atlas in any external-validity claim."
)

ACCURACY_CAVEAT = (
    "This corpus is a harm-gate denominator, not an accuracy benchmark. Its gold is the relation "
    "between two fully stated source records, and on record pairs with nothing missing that "
    "relation is what compare_meaning already answers, by construction. That is what a harm "
    "measurement needs --- its question is whether a candidate rule moves a decision the current "
    "rule already gets right --- and it is what an accuracy claim must not be built on. No "
    "accuracy, false-merge, false-split or superiority number over this corpus is evidence about "
    "ORION's competence."
)

GATE_NOTE = (
    "G9_HARM_A3 reads 'A3_decisive_absence_only destroys 0 correct answers on every intact "
    "corpus, and at least one intact corpus supplies independent evidence for that zero'. Adding "
    "a corpus to that gate can only leave it where it is or make it fail; no construction of "
    "this corpus can turn a destroyed answer into an undestroyed one. The gate's threshold is "
    "not amended, only its denominator."
)

NON_CIRCULARITY_NOTE = (
    "A3_decisive_absence_only abstains where the admissible completions of a one-sided absence "
    "disagree about the relation. This corpus's gold never asks that question: "
    "relation_from_records is defined only on records that state every coordinate and raises on "
    "anything else, so there is no completion for it to quantify over. The two therefore "
    "disagree wherever the records determine a relation that the projections do not, which is "
    "the LA and LD strata, and that disagreement is what makes the harm number a measurement "
    "rather than a restatement. If a later edit removed the strata on which they disagree, the "
    "corpus's gold would coincide with A3's rule wherever A3 can fire and the corpus would be "
    "circular again; verify() refuses to emit such a corpus and the probe withholds the evidence "
    "of one."
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
# Observedness
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


def fully_observed(projection: ScientificMeaningProjection) -> bool:
    return all(observed(projection, coordinate) for coordinate in COORDINATES)


# --------------------------------------------------------------------------
# The derivation rule
# --------------------------------------------------------------------------


class RecordCorpusError(RuntimeError):
    """Raised when the corpus does not have the structure the gate needs."""


# --------------------------------------------------------------------------
# Draws (amendment 004)
# --------------------------------------------------------------------------

#: The label of the draw the shipped corpus is built from. A draw carrying any
#: other label is a *held-out* corpus: it is never written to the repository, and
#: every document it emits says which draw it came from, so a number measured on
#: one can never be quoted as a number about the other.
DEFAULT_DRAW_LABEL = "frozen-2026-08-22"

#: The prefix every value a held-out draw invents carries. Distinct from the
#: frozen table's ``porec:`` so that a held-out record can never be mistaken for
#: a shipped one by a reader or by a grep.
FRESH_DRAW_VALUE_PREFIX = "pofd"

WITNESS_SLOT_BASE = 900


@dataclass(frozen=True)
class RecordDraw:
    """The construction choices the record standard leaves free.

    The standard fixes the coordinate *precedence*, the strata and the shape of a
    case. It does not fix which id strings the records use, which of the two
    values of a closed vocabulary each record takes, or which side of a pair the
    extraction loss falls on. Those are free, and amendment 004 makes them
    explicit so that a finding measured on the shipped corpus can be re-measured
    on a corpus drawn differently.

    ``DEFAULT_DRAW`` reproduces the frozen table exactly, so
    ``record_gold_cases()`` with no argument emits the corpus that already ships,
    byte for byte.
    """

    label: str
    record_values: Mapping[str, tuple[Any, ...]]
    lost_side: Mapping[tuple[str, str], str]

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise RecordCorpusError("a draw needs a label")
        missing = [name for name in COORDINATES if name not in self.record_values]
        if missing:
            raise RecordCorpusError(f"draw {self.label} states no value for {', '.join(missing)}")
        for name in COORDINATES:
            values = tuple(self.record_values[name])
            if len(values) != 2 or values[0] == values[1]:
                raise RecordCorpusError(
                    f"draw {self.label}: {name} needs two distinct record values, got {values!r}"
                )
            if ABSENT_VALUE[name] in values:
                raise RecordCorpusError(
                    f"draw {self.label}: {name} takes its absent value on a record, so the "
                    "record would not be fully observed and gold could not be read off it"
                )
        for stratum in (STRATUM_LA, STRATUM_LD, STRATUM_LU):
            for name in COORDINATES:
                if stratum is STRATUM_LU and name == LU_DECIDING_COORDINATE:
                    continue
                side = self.lost_side.get((stratum, name))
                if side not in ("left", "right"):
                    raise RecordCorpusError(
                        f"draw {self.label}: no loss side for {stratum}/{name}"
                    )


def _frozen_lost_side() -> dict[tuple[str, str], str]:
    """The side each loss falls on in the corpus frozen by amendment 003.

    Written out from the parity rules that produced it rather than restated as a
    literal table, so that this and ``_case_specs`` cannot drift apart.
    """

    sides: dict[tuple[str, str], str] = {}
    for index, coordinate in enumerate(COORDINATES):
        sides[(STRATUM_LA, coordinate)] = "left" if index % 2 == 0 else "right"
        sides[(STRATUM_LD, coordinate)] = "right" if index % 2 == 0 else "left"
    for index, coordinate in enumerate(
        name for name in COORDINATES if name != LU_DECIDING_COORDINATE
    ):
        sides[(STRATUM_LU, coordinate)] = "left" if index % 2 == 0 else "right"
    return sides


DEFAULT_DRAW = RecordDraw(
    label=DEFAULT_DRAW_LABEL,
    record_values=RECORD_VALUES,
    lost_side=_frozen_lost_side(),
)


def fresh_draw(seed: int) -> RecordDraw:
    """A held-out draw: the same standard, different free choices.

    The record vocabulary is redrawn, the two closed vocabularies are redrawn
    from their own value sets, and the side each extraction loss falls on is
    drawn independently per stratum and coordinate. Nothing the derivation rule
    reads changes: the precedence order, the strata and the loss shape are the
    standard's, not the draw's.

    Seeded from a string that names this module, so a draw is reproducible from
    its seed alone and two different studies asking for "seed 7" of different
    things do not collide.
    """

    rng = random.Random(f"{PROTOCOL_ID}:fresh-draw:{seed}")
    values: dict[str, tuple[Any, ...]] = {}
    for name in COORDINATES:
        frozen = RECORD_VALUES[name]
        if isinstance(frozen[0], (Polarity, Modality)):
            pool = [item for item in type(frozen[0]) if item != ABSENT_VALUE[name]]
            values[name] = tuple(rng.sample(pool, 2))
            continue
        stem = name[:-4] if name.endswith("_ids") else name
        first, second = rng.sample(range(10, 100), 2)

        def render(number: int, stem: str = stem) -> str:
            return f"{FRESH_DRAW_VALUE_PREFIX}{seed:02d}:{stem}:{number:02d}"

        if isinstance(frozen[0], tuple):
            values[name] = ((render(first),), (render(second),))
        else:
            values[name] = (render(first), render(second))
    sides: dict[tuple[str, str], str] = {}
    for stratum in (STRATUM_LA, STRATUM_LD, STRATUM_LU):
        for name in COORDINATES:
            if stratum == STRATUM_LU and name == LU_DECIDING_COORDINATE:
                continue
            sides[(stratum, name)] = rng.choice(("left", "right"))
    return RecordDraw(label=f"fresh-draw-{seed}", record_values=values, lost_side=sides)



def relation_from_records(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """The relation between two source records.

    Written out rather than delegated to ``compare_meaning`` so that gold is not
    defined by the system under test. It reads the coordinates in one fixed
    precedence order and stops at the first that separates.

    It is defined only on records that state every coordinate, and raises on any
    other input. That is not a limitation to work around, it is the property that
    makes this corpus's gold non-circular: the rule has no branch that reads an
    absence, so it has no opinion about what an absence could have hidden, so it
    cannot be A3's rule under another name. Gold is attached to the *record*; the
    projection's extraction loss is applied afterwards and does not reach here.
    """

    for role, side in (("left", left), ("right", right)):
        missing = [name for name in COORDINATES if not observed(side, name)]
        if missing:
            raise RecordCorpusError(
                "relation_from_records is defined only on records that state every "
                f"coordinate; the {role} record {side.projection_id} does not state "
                f"{', '.join(missing)}"
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


# --------------------------------------------------------------------------
# The frozen standard
# --------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return getattr(value, "value", value)


def standard_document(draw: RecordDraw = DEFAULT_DRAW) -> dict[str, Any]:
    """The standard, for one draw of the choices it leaves free.

    ``draw`` defaults to the frozen table, and on that default the document is
    byte-identical to the one the corpus ships --- the case ``source_records``
    carry its hash, so anything else would rewrite the shipped corpus. A
    held-out draw adds a ``draw`` block naming itself, so a standard emitted for
    one can never be read as the standard the corpus was built against.
    """

    document: dict[str, Any] = {
        "schema_version": STANDARD_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "atlas_id": ATLAS_ID,
        "derivation_rule": DERIVATION_RULE,
        "derivation_rule_statement": (
            "Every case of this corpus is a pair of source records, and each record states all "
            "nine identity coordinates from this table. Gold is the relation between the two "
            "records: read the coordinates in the order referent, construct, measurement, then "
            "the contextual coordinates (temporal, attribution, discourse, assumption, modal "
            "force), then polarity, and take the first that separates them. The projections a "
            "case ships are the records after an extraction loss, which blanks one coordinate on "
            "one side. The loss does not reach this rule and does not move gold: the record "
            "still states what it states."
        ),
        "why_this_is_not_the_criterion_a3_decides_by": NON_CIRCULARITY_NOTE,
        "coordinate_precedence": list(COORDINATES),
        "absent_values": {name: _jsonable(value) for name, value in ABSENT_VALUE.items()},
        "record_values": {
            name: [_jsonable(value) for value in draw.record_values[name]]
            for name in COORDINATES
        },
        "predicate": PREDICATE,
        "disciplines": list(DISCIPLINES),
        "strata": {
            STRATUM_LA: (
                "the two records state the same value of the lost coordinate and agree "
                "everywhere else; gold COMPATIBLE"
            ),
            STRATUM_LD: (
                "the two records state different values of the lost coordinate and agree "
                "everywhere else; gold is what that difference makes it"
            ),
            STRATUM_LU: (
                "the records differ on referent_ids, which survives extraction on both sides, "
                "and the loss is of a lower-precedence coordinate; gold DISTINCT_REFERENT"
            ),
            STRATUM_NL: "no extraction loss; gold is the plain record relation",
        },
        "census": (
            "one LA case and one LD case per coordinate, so the harm denominator is whatever "
            "compare_meaning's own absence reading makes it and not whatever the author wanted. "
            "Dropping either half of any coordinate's pair is refused by verify()."
        ),
        "gate_note": GATE_NOTE,
        "external_validity": EXTERNAL_VALIDITY,
        "not_an_accuracy_benchmark": ACCURACY_CAVEAT,
    }
    if draw.label != DEFAULT_DRAW_LABEL:
        document["draw"] = {
            "label": draw.label,
            "lost_side": {
                f"{stratum}/{coordinate}": side
                for (stratum, coordinate), side in sorted(draw.lost_side.items())
            },
            "held_out": (
                "this is not the draw the corpus ships. It re-draws the free choices the "
                "standard does not fix --- the record vocabulary, which value of each closed "
                "vocabulary each record takes, and which side each extraction loss falls on "
                "--- and fixes nothing the derivation rule reads. It exists to re-measure a "
                "finding off the corpus it was found on, and it is never written to the "
                "repository."
            ),
        }
    return document


def standard_bytes(draw: RecordDraw = DEFAULT_DRAW) -> bytes:
    return json.dumps(standard_document(draw), indent=2, sort_keys=True).encode("utf-8") + b"\n"


def standard_hash(draw: RecordDraw = DEFAULT_DRAW) -> str:
    return _sha(standard_bytes(draw))


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------


def _base_values(draw: RecordDraw) -> dict[str, Any]:
    """The value every coordinate takes on both records unless a spec overrides it."""

    return {name: draw.record_values[name][0] for name in COORDINATES}


def _case_specs(draw: RecordDraw = DEFAULT_DRAW) -> list[dict[str, Any]]:
    """Every case as a plain description, before any projection is built.

    A census, written so that its shape can be read at a glance and checked
    against the counts in the construction document: nine coordinates times
    {records agree, records differ} with the loss on that coordinate, eight
    losses below a coordinate that already decides, and ten controls with no
    loss at all.
    """

    specs: list[dict[str, Any]] = []
    slot = 0

    for coordinate in COORDINATES:
        specs.append(
            {
                "stratum": STRATUM_LA,
                "slot": slot,
                "lost_coordinate": coordinate,
                "lost_side": draw.lost_side[(STRATUM_LA, coordinate)],
                "records_differ_on": None,
            }
        )
        slot += 1
    for coordinate in COORDINATES:
        specs.append(
            {
                "stratum": STRATUM_LD,
                "slot": slot,
                "lost_coordinate": coordinate,
                "lost_side": draw.lost_side[(STRATUM_LD, coordinate)],
                "records_differ_on": coordinate,
            }
        )
        slot += 1
    for coordinate in (name for name in COORDINATES if name != LU_DECIDING_COORDINATE):
        specs.append(
            {
                "stratum": STRATUM_LU,
                "slot": slot,
                "lost_coordinate": coordinate,
                "lost_side": draw.lost_side[(STRATUM_LU, coordinate)],
                "records_differ_on": LU_DECIDING_COORDINATE,
            }
        )
        slot += 1
    for coordinate in (*COORDINATES, None):
        specs.append(
            {
                "stratum": STRATUM_NL,
                "slot": slot,
                "lost_coordinate": None,
                "lost_side": None,
                "records_differ_on": coordinate,
            }
        )
        slot += 1
    return specs


def _projection_payload(
    side: str, digest: str, values: Mapping[str, Any], *, record: bool
) -> dict[str, Any]:
    """One side of a case, as the record or as the projection extracted from it.

    ``projection_id`` and ``source_span`` are fixed-width templates so that no
    construction-level feature varies with gold.
    """

    kind = "rec" if record else "prj"
    return {
        "projection_id": f"porec:{digest}:{kind}:{side}",
        "source_id": "orion-p3-partial-observation-record-standard",
        "source_span": f"{STANDARD_FILENAME}#case={digest}&part={kind}&side={side}",
        "predicate": PREDICATE,
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


def _case(
    spec: Mapping[str, Any], *, standard_sha: str, draw: RecordDraw = DEFAULT_DRAW
) -> dict[str, Any]:
    stratum = str(spec["stratum"])
    slot = int(spec["slot"])

    left_record_values = _base_values(draw)
    right_record_values = _base_values(draw)
    differ = spec["records_differ_on"]
    if differ is not None:
        right_record_values[str(differ)] = draw.record_values[str(differ)][1]

    digest = _decimal_digest(
        "|".join(
            [
                PROTOCOL_ID,
                stratum,
                str(slot),
                str(spec["lost_coordinate"]),
                str(spec["lost_side"]),
                str(differ),
                json.dumps(
                    {
                        name: _jsonable(value)
                        for name, value in sorted(left_record_values.items())
                    },
                    sort_keys=True,
                ),
                json.dumps(
                    {
                        name: _jsonable(value)
                        for name, value in sorted(right_record_values.items())
                    },
                    sort_keys=True,
                ),
            ]
        )
    )

    left_record = _projection_payload("l", digest, left_record_values, record=True)
    right_record = _projection_payload("r", digest, right_record_values, record=True)

    # Gold is read off the records, before any extraction loss is applied.
    relation = relation_from_records(
        projection_from_dict(left_record), projection_from_dict(right_record)
    )

    left_values = dict(left_record_values)
    right_values = dict(right_record_values)
    lost = spec["lost_coordinate"]
    if lost is not None:
        target = left_values if spec["lost_side"] == "left" else right_values
        target[str(lost)] = ABSENT_VALUE[str(lost)]

    left_payload = _projection_payload("l", digest, left_values, record=False)
    right_payload = _projection_payload("r", digest, right_values, record=False)

    case = {
        "schema_version": SCHEMA_VERSION,
        "case_id": f"porec-{digest}",
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
                    f"{STANDARD_DATASET}@{standard_sha}:{STANDARD_FILENAME}"
                    f"#case={digest}&part=rec&side=l",
                    f"{STANDARD_DATASET}@{standard_sha}:{STANDARD_FILENAME}"
                    f"#case={digest}&part=rec&side=r",
                ],
                "derivation": {
                    "rule": DERIVATION_RULE,
                    "inputs": [
                        f"stratum={stratum}",
                        f"records_differ_on={differ}",
                        f"lost_coordinate={lost}",
                        f"lost_side={spec['lost_side']}",
                    ],
                },
            },
        },
        # The records gold is read off, carried in the case so that a reader can
        # recompute gold without the builder. This is the field that makes the
        # corpus self-describing: the gold's evidence is a pair of records, not a
        # claim about what the projections could have meant.
        "partial_observation_record_gold": {
            "stratum": stratum,
            "lost_coordinate": lost,
            "lost_side": spec["lost_side"],
            "records_differ_on": differ,
            "left_record": left_record,
            "right_record": right_record,
        },
    }
    validate_case(case)
    return case


def record_gold_cases(draw: RecordDraw = DEFAULT_DRAW) -> list[dict[str, Any]]:
    """The 36 cases, emitted in ``case_id`` sort order.

    ``draw`` defaults to the frozen table, on which this emits the corpus that
    already ships, byte for byte. Any other draw is a held-out corpus: the same
    standard, the same strata and the same derivation rule, with the choices the
    standard leaves free re-drawn. It is returned and never written.
    """

    standard_sha = standard_hash(draw)
    cases = [_case(spec, standard_sha=standard_sha, draw=draw) for spec in _case_specs(draw)]
    ids = [str(case["case_id"]) for case in cases]
    if len(set(ids)) != len(ids):  # pragma: no cover - a collision would be a hash break
        raise RecordCorpusError("partial-observation record-gold case ids collided")
    return sorted(cases, key=lambda case: str(case["case_id"]))


def undecidability_witness_cases(
    coordinate: str, *, draw: RecordDraw = DEFAULT_DRAW, lost_side: str = "right"
) -> tuple[dict[str, Any], dict[str, Any]]:
    """One ``LA`` case and one ``LD`` case whose *projections* are the same pair.

    Both are legal cases of this corpus: same standard, same strata, same
    derivation rule, built by the same :func:`_case` and validated by the same
    :func:`validate_case`. The only thing that separates them from the two cases
    the shipped corpus already carries for this coordinate is that the extraction
    loss falls on the *same* side in both, which the standard does not fix and
    the derivation rule does not read.

    Losing the same side makes the two projection pairs identical value for
    value, because ``LD``'s surviving side keeps the base value and ``LA``'s
    records both hold it. So the pair a reader of the projections sees is one
    pair, and the two cases give it two different golds: the ``LA`` records agree
    on the lost coordinate and the ``LD`` records do not, and the extraction that
    produced these projections destroyed exactly the value that decides which.

    This is the mechanical form of the claim that gold is not a function of the
    projections. It needs no canonicalisation beyond dropping ``projection_id``
    and ``source_span``, which are per-case bookkeeping the relation never reads:
    no left/right swap, no renaming of anything.
    """

    if coordinate not in COORDINATES:
        raise KeyError(f"{coordinate} is not one of the nine identity coordinates")
    if lost_side not in ("left", "right"):
        raise ValueError(f"lost_side must be left or right, not {lost_side!r}")
    index = COORDINATES.index(coordinate)
    standard_sha = standard_hash(draw)
    agreeing = _case(
        {
            "stratum": STRATUM_LA,
            "slot": WITNESS_SLOT_BASE + index,
            "lost_coordinate": coordinate,
            "lost_side": lost_side,
            "records_differ_on": None,
        },
        standard_sha=standard_sha,
        draw=draw,
    )
    differing = _case(
        {
            "stratum": STRATUM_LD,
            "slot": WITNESS_SLOT_BASE + len(COORDINATES) + index,
            "lost_coordinate": coordinate,
            "lost_side": "right",
            "records_differ_on": coordinate,
        },
        standard_sha=standard_sha,
        draw=draw,
    )
    return agreeing, differing


def held_out_corpus(seed: int) -> list[dict[str, Any]]:
    """A fresh draw of the corpus, verified by the same :func:`verify` and returned.

    Never written. The point of a held-out draw is to re-measure a number on
    cases that were not in front of whoever proposed the rule, and a draw that
    got written would stop being held out the moment it was.
    """

    cases = record_gold_cases(fresh_draw(seed))
    verify(cases, construction_receipts(cases))
    return cases


# --------------------------------------------------------------------------
# Receipts: every construction claim, checked rather than asserted
# --------------------------------------------------------------------------


def _pair(
    case: Mapping[str, Any],
) -> tuple[ScientificMeaningProjection, ScientificMeaningProjection]:
    return (
        projection_from_dict(case["left_projection"]),
        projection_from_dict(case["right_projection"]),
    )


def _records(
    case: Mapping[str, Any],
) -> tuple[ScientificMeaningProjection, ScientificMeaningProjection]:
    meta = case["partial_observation_record_gold"]
    assert isinstance(meta, Mapping)
    return (
        projection_from_dict(meta["left_record"]),
        projection_from_dict(meta["right_record"]),
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
    """Per case: what the records say, what the arms answer, and what it costs.

    ``a3`` is imported from the probe rather than reimplemented. Scoring an arm
    against a copy of itself would be a second circularity one layer down, and a
    corpus that has to reimplement the arm to describe itself is a corpus whose
    gold is entangled with it. Gold is computed here; the arm is not.
    """

    from .partial_observation_probe import (
        admissible_completions as probe_completions,
        arm_decisive_absence_only,
        arm_observedness_asymmetric,
    )

    receipts: list[dict[str, Any]] = []
    for case in cases:
        left, right = _pair(case)
        record_left, record_right = _records(case)
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, Mapping)
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        absences = one_sided_absences(left, right)
        completions = sorted(
            {
                compare_meaning(completed_left, completed_right).relation.value
                for completed_left, completed_right in probe_completions(left, right)
            }
        )
        current = compare_meaning(left, right).relation
        a1 = arm_observedness_asymmetric(left, right)
        a3 = arm_decisive_absence_only(left, right)
        a0_correct = current is gold
        receipts.append(
            {
                "case_id": str(case["case_id"]),
                "stratum": str(meta["stratum"]),
                "lost_coordinate": meta["lost_coordinate"],
                "lost_side": meta["lost_side"],
                "records_differ_on": meta["records_differ_on"],
                "one_sided_absences": list(absences),
                "gold": gold.value,
                "gold_from_records": relation_from_records(record_left, record_right).value,
                "gold_is_determinate": gold is not MeaningRelation.UNRESOLVED,
                "relations_over_admissible_completions": completions,
                "absence_is_decisive": bool(absences) and len(completions) > 1,
                "compare_meaning": current.value,
                "a0_reproduces_gold": a0_correct,
                "a1_observedness_asymmetric": a1.value,
                "a3_decisive_absence_only": a3.value,
                "a3_reproduces_gold": a3 is gold,
                "a1_destroys_a_correct_answer": a0_correct and a1 is not gold,
                "a3_destroys_a_correct_answer": a0_correct and a3 is not gold,
            }
        )
    return receipts


def rule_agreement_on_records(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The derivation rule against ``compare_meaning`` on every record pair.

    The rule is written out independently so gold is not defined by the system
    under test. That independence is only worth anything if the two are checked
    against each other where both are defined --- on records with nothing missing.
    A disagreement there would mean the corpus measures a rule ORION does not
    have, and the build refuses.
    """

    compared = 0
    offenders: list[dict[str, str]] = []
    for case in cases:
        record_left, record_right = _records(case)
        derived = relation_from_records(record_left, record_right)
        current = compare_meaning(record_left, record_right).relation
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
        "record_pairs_compared": compared,
        "disagreements": len(offenders),
        "offenders": offenders[:8],
        "agrees_everywhere": not offenders,
    }


def extraction_loss_is_the_only_difference(
    cases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Each projection is its record with at most the declared coordinate blanked.

    Without this the corpus could carry a projection that differs from its record
    in some other way, and gold --- read off the record --- would be gold for a
    pair the corpus does not ship.
    """

    offenders: list[str] = []
    for case in cases:
        left, right = _pair(case)
        record_left, record_right = _records(case)
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, Mapping)
        lost = meta["lost_coordinate"]
        expected_left, expected_right = record_left, record_right
        if lost is not None:
            blank = {str(lost): ABSENT_VALUE[str(lost)]}
            if meta["lost_side"] == "left":
                expected_left = replace(record_left, **blank)
            else:
                expected_right = replace(record_right, **blank)
        same_left = _comparable(left) == _comparable(expected_left)
        same_right = _comparable(right) == _comparable(expected_right)
        if not (same_left and same_right):
            offenders.append(str(case["case_id"]))
    return {
        "n_cases": len(cases),
        "offenders": sorted(offenders)[:8],
        "holds_everywhere": not offenders,
    }


def _comparable(projection: ScientificMeaningProjection) -> tuple[Any, ...]:
    """A projection's coordinates and predicate, without its identity fields.

    A record and the projection extracted from it carry different
    ``projection_id`` and ``source_span`` values by design --- one is the record,
    the other is ORION's view of it --- so identity is excluded from the
    comparison and everything the relation reads is included.
    """

    return (projection.predicate, *(getattr(projection, name) for name in COORDINATES))


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


def coordinate_balance(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Both directions of every coordinate, so no coordinate was chosen by outcome.

    ``compare_meaning`` reads a one-sided absence as agreement on eight
    coordinates and as a distinct value on the ninth, so ``A0`` is right on the
    agreeing records for eight of them and on the differing records for one.
    Which of those cells lands in the harm denominator is therefore fixed by
    ``compare_meaning``, not by the builder --- but only while both cells exist.
    Keeping a coordinate's ``LA`` case and dropping its ``LD`` case, or the
    reverse, would be selecting cases by their effect on the gate.
    """

    present: dict[str, set[str]] = {name: set() for name in COORDINATES}
    for case in cases:
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, Mapping)
        stratum = str(meta["stratum"])
        lost = meta["lost_coordinate"]
        if lost is not None and stratum in {STRATUM_LA, STRATUM_LD}:
            present[str(lost)].add(stratum)
    missing = sorted(
        f"{name}:{stratum}"
        for name, strata in present.items()
        for stratum in (STRATUM_LA, STRATUM_LD)
        if stratum not in strata
    )
    return {
        "coordinates": list(COORDINATES),
        "missing_cells": missing,
        "balanced": not missing,
    }


def absence_reading_census(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What ``compare_meaning`` does with an extraction loss, one cell per coordinate.

    Read off ``LA_LOSS_ON_AGREEING_RECORDS``, where the records agree on the lost
    coordinate so the record relation is ``COMPATIBLE``. ``MERGE_WARD`` means the
    rule read the silence as agreement and reached the record's answer;
    ``SEPARATION_WARD`` means it read the silence as a distinct value and
    separated a pair the records call compatible. The freeze's eight-to-one split
    is measured here rather than quoted.
    """

    from .partial_observation_probe import ABSENCE_READING

    cells: dict[str, dict[str, Any]] = {}
    for case in cases:
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, Mapping)
        if str(meta["stratum"]) != STRATUM_LA:
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
        coordinate = str(meta["lost_coordinate"])
        cells[coordinate] = {
            "case_id": str(case["case_id"]),
            "compare_meaning": current.value,
            "observed_reading": reading,
            "freeze_declared_reading": ABSENCE_READING.get(coordinate),
            "matches_freeze": (
                (reading == "MERGE_WARD") == (ABSENCE_READING.get(coordinate) == "AGREEMENT")
            ),
        }
    counts: dict[str, int] = {}
    for cell in cells.values():
        counts[str(cell["observed_reading"])] = counts.get(str(cell["observed_reading"]), 0) + 1
    return {
        "by_coordinate": cells,
        "counts": counts,
        "every_cell_matches_the_freeze": all(
            bool(cell["matches_freeze"]) for cell in cells.values()
        ),
    }


def harm_preview(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What each observedness-sensitive arm costs on this corpus.

    A preview, computed from the construction receipts. The probe is the
    authority for the gate numbers; this exists so the builder cannot emit a
    corpus that silently has no harm opportunities in it, and so the corpus's own
    report states the number it is about to hand a blocking gate.
    """

    could_fire = [row for row in receipts if row["one_sided_absences"]]
    denominator = [row for row in could_fire if row["a0_reproduces_gold"]]
    a1_destroyed = [row for row in could_fire if row["a1_destroys_a_correct_answer"]]
    a3_destroyed = [row for row in could_fire if row["a3_destroys_a_correct_answer"]]
    a3_spared = [
        row
        for row in denominator
        if not row["a3_destroys_a_correct_answer"] and row["a1_destroys_a_correct_answer"]
    ]
    return {
        "n_cases": len(receipts),
        "pairs_with_a_one_sided_absence": len(could_fire),
        "harm_denominator": len(denominator),
        "a1_correct_answers_destroyed": len(a1_destroyed),
        "a3_correct_answers_destroyed": len(a3_destroyed),
        "a3_destroyed_case_ids": sorted(str(row["case_id"]) for row in a3_destroyed),
        "pairs_a1_destroys_and_a3_spares": len(a3_spared),
        "a3_reproduces_gold_on_every_pair_it_can_fire_on": bool(could_fire)
        and all(bool(row["a3_reproduces_gold"]) for row in could_fire),
    }


def decisiveness_census(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """How the corpus's gold lines up with whether the loss was decisive.

    The number that says the corpus is not the circular one wearing a different
    hat. A corpus whose gold is determinate exactly where the loss is undecisive
    has a gold that coincides with the completion-invariance criterion whatever
    rule string it declares, and its A3 numbers would carry nothing. This corpus
    has cells off that diagonal --- pairs whose records determine a relation the
    projections do not --- and this counts them.
    """

    partial = [row for row in receipts if row["one_sided_absences"]]
    determinate_and_decisive = [
        row for row in partial if row["gold_is_determinate"] and row["absence_is_decisive"]
    ]
    determinate_and_undecisive = [
        row for row in partial if row["gold_is_determinate"] and not row["absence_is_decisive"]
    ]
    return {
        "n_partially_observed_pairs": len(partial),
        "n_determinate_gold_with_a_decisive_loss": len(determinate_and_decisive),
        "n_determinate_gold_with_an_undecisive_loss": len(determinate_and_undecisive),
        "n_unresolved_gold": sum(1 for row in partial if not row["gold_is_determinate"]),
        "gold_coincides_with_completion_invariance": not determinate_and_decisive,
        "off_diagonal_case_ids": sorted(
            str(row["case_id"]) for row in determinate_and_decisive
        )[:8],
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
        "predicate": set(),
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
            seen["predicate"].add(str(payload["predicate"]))
    return {name: sorted(values) for name, values in seen.items()}


# --------------------------------------------------------------------------
# Build report and emission
# --------------------------------------------------------------------------

#: What each stratum must be true of, checked before the corpus is written.
STRATUM_CONTRACT: dict[str, dict[str, Any]] = {
    STRATUM_LA: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": True,
        "absence_is_decisive": True,
    },
    STRATUM_LD: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": True,
        "absence_is_decisive": True,
    },
    STRATUM_LU: {
        "n_one_sided_absences": 1,
        "gold_is_determinate": True,
        "absence_is_decisive": False,
    },
    STRATUM_NL: {
        "n_one_sided_absences": 0,
        "gold_is_determinate": True,
        "absence_is_decisive": False,
    },
}


def verify(cases: Sequence[Mapping[str, Any]], receipts: Sequence[Mapping[str, Any]]) -> None:
    """Refuse to emit a corpus that does not have the structure the gate needs.

    Every check here can only make the corpus harder to build. In particular
    nothing here checks that A3 comes out well: the two checks that mention A3 at
    all refuse a corpus on which A3 *cannot be measured*, and both of them refuse
    in the direction that withholds a pass.
    """

    census = one_sided_absence_census(cases)
    if census["n_pairs_with_a_one_sided_absence"] == 0:
        raise RecordCorpusError(
            "the corpus has no one-sided absence, so it leaves G9_HARM_A3 exactly as vacuous "
            "as it was"
        )
    balance = coordinate_balance(cases)
    if not balance["balanced"]:
        raise RecordCorpusError(
            "a coordinate is present on agreeing records but not on differing records or the "
            f"reverse, which is choosing cases by their effect on the gate: {balance['missing_cells']}"
        )
    decisiveness = decisiveness_census(receipts)
    if decisiveness["gold_coincides_with_completion_invariance"]:
        raise RecordCorpusError(
            "every partially observed pair with determinate gold has an undecisive loss, so "
            "this corpus's gold coincides with the completion-invariance criterion A3 decides "
            "by and cannot score it, whatever derivation rule it declares"
        )
    if decisiveness["n_determinate_gold_with_an_undecisive_loss"] == 0:
        raise RecordCorpusError(
            "no partially observed pair whose loss is undecisive, so A3 and A1 make the same "
            "decision everywhere here and the corpus cannot show what A3 was built to do"
        )
    preview = harm_preview(receipts)
    if preview["harm_denominator"] == 0:
        raise RecordCorpusError(
            "no partially observed pair A0 answers correctly; a harm gate over this corpus "
            "could not report a harm even if one existed"
        )
    if preview["a3_reproduces_gold_on_every_pair_it_can_fire_on"]:
        raise RecordCorpusError(
            "A3 reproduces gold on every pair it can fire on, so its harm here follows from a "
            "perfect score by arithmetic and is not a measurement"
        )
    for row in receipts:
        contract = STRATUM_CONTRACT[str(row["stratum"])]
        n_absences = len(list(row["one_sided_absences"]))
        if n_absences != contract["n_one_sided_absences"]:
            raise RecordCorpusError(
                f"{row['case_id']}: {row['stratum']} requires "
                f"{contract['n_one_sided_absences']} one-sided absence(s), found {n_absences}"
            )
        if bool(row["gold_is_determinate"]) is not contract["gold_is_determinate"]:
            raise RecordCorpusError(
                f"{row['case_id']}: {row['stratum']} requires gold determinate="
                f"{contract['gold_is_determinate']}, derived {row['gold']}"
            )
        if bool(row["absence_is_decisive"]) is not contract["absence_is_decisive"]:
            raise RecordCorpusError(
                f"{row['case_id']}: {row['stratum']} requires absence_is_decisive="
                f"{contract['absence_is_decisive']}, measured "
                f"{row['relations_over_admissible_completions']}"
            )
        if str(row["gold"]) != str(row["gold_from_records"]):
            raise RecordCorpusError(
                f"{row['case_id']}: shipped gold {row['gold']} is not the record relation "
                f"{row['gold_from_records']}"
            )

    agreement = rule_agreement_on_records(cases)
    if not agreement["agrees_everywhere"]:
        raise RecordCorpusError(
            "the derivation rule and compare_meaning disagree on a record pair with nothing "
            f"missing: {agreement['offenders']}"
        )
    loss = extraction_loss_is_the_only_difference(cases)
    if not loss["holds_everywhere"]:
        raise RecordCorpusError(
            "a shipped projection is not its record minus the declared coordinate: "
            f"{loss['offenders']}"
        )
    if not absent_value_agreement()["agrees"]:
        raise RecordCorpusError(
            "this module and the probe disagree about which value means 'absent'"
        )
    reading = absence_reading_census(cases)
    if not reading["every_cell_matches_the_freeze"]:
        raise RecordCorpusError(
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
        meta = case["partial_observation_record_gold"]
        assert isinstance(meta, Mapping)
        strata[str(meta["stratum"])] = strata.get(str(meta["stratum"]), 0) + 1
        expected = case["expected"]
        assert isinstance(expected, Mapping)
        relation = str(expected["meaning_relation"])
        relations[relation] = relations.get(relation, 0) + 1
    return {
        "schema_version": BUILD_REPORT_SCHEMA_VERSION,
        "record": "P3_PARTIAL_OBSERVATION_RECORD_GOLD_CORPUS_BUILD",
        "date": "2026-08-22",
        "atlas_id": ATLAS_ID,
        "protocol_id": PROTOCOL_ID,
        "builder": "src/orion/study/p3/partial_observation_record_gold_build.py",
        "construction_document": CONSTRUCTION_DOCUMENT,
        "gate_served": "G9_HARM_A3",
        "gate_note": GATE_NOTE,
        "derivation_rule": DERIVATION_RULE,
        "why_this_is_not_the_criterion_a3_decides_by": NON_CIRCULARITY_NOTE,
        "built_n": len(cases),
        "cases_hash": _sha(cases_bytes(cases)),
        "standard_sha256": standard_hash(),
        "strata": dict(sorted(strata.items())),
        "expected_relations": dict(sorted(relations.items())),
        "one_sided_absence_census": one_sided_absence_census(cases),
        "coordinate_balance": coordinate_balance(cases),
        "decisiveness_census": decisiveness_census(receipts),
        "absent_value_agreement": absent_value_agreement(),
        "rule_agreement_on_records": rule_agreement_on_records(cases),
        "extraction_loss_is_the_only_difference": extraction_loss_is_the_only_difference(cases),
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

    cases = record_gold_cases()
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
        description=(
            "Build the P3 partial-observation record-gold corpus (G9_HARM_A3 denominator)."
        )
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
        cases = record_gold_cases()
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
    "CORPUS_DIR",
    "DEFAULT_DRAW",
    "DEFAULT_DRAW_LABEL",
    "DERIVATION_RULE",
    "FRESH_DRAW_VALUE_PREFIX",
    "LU_DECIDING_COORDINATE",
    "RecordDraw",
    "WITNESS_SLOT_BASE",
    "PREDICATE",
    "PROTOCOL_ID",
    "RECORD_VALUES",
    "RecordCorpusError",
    "STRATUM_CONTRACT",
    "STRATUM_LA",
    "STRATUM_LD",
    "STRATUM_LU",
    "STRATUM_NL",
    "STRATUM_ORDER",
    "absence_reading_census",
    "absent_value_agreement",
    "build_report",
    "cases_bytes",
    "construction_receipts",
    "coordinate_balance",
    "decisiveness_census",
    "extraction_loss_is_the_only_difference",
    "fresh_draw",
    "fully_observed",
    "held_out_corpus",
    "harm_preview",
    "main",
    "observed",
    "one_sided_absence_census",
    "one_sided_absences",
    "record_gold_cases",
    "relation_from_records",
    "rule_agreement_on_records",
    "shape_invariants",
    "standard_bytes",
    "standard_document",
    "standard_hash",
    "undecidability_witness_cases",
    "verify",
    "write_corpus",
]
