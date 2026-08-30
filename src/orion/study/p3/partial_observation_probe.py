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

Protocol: ``papers/orion-13-global-knowledge-portrait/protocol/
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

**Amendment 002 (2026-08-22).** Amendment 001 measured A1 and A1 failed: it
abstains on the *presence* of a one-sided absence, so on the twelve
``H_UNDECISIVE_ABSENCE`` pairs --- where a higher-precedence coordinate already
decides and the absent one could not have changed the answer --- it destroys an
answer ``compare_meaning`` already had right. That is a defect in A1's design.
What warrants abstention is not that a source was silent but that the silence is
what the answer turns on, and this amendment adds the arm that decides that way:
``A3_decisive_absence_only`` runs ``compare_meaning`` over every admissible
completion of every one-sided absence and abstains only when the completions
disagree. A1 and A2 stay exactly where they are --- A1's measured harm is a
finding and has to stay reproducible --- and ``G6_HARM_A1`` keeps failing, for
A1, with the same statement and the same threshold. The new arm gets its own
gates.

Those gates come back ``CANNOT_CHECK``, which is the point of adding them
carefully. A3 destroys no correct answer anywhere in this repository and repairs
nine of A0's, but the three corpora frozen on 2026-08-21 give it nothing to fire
on, and ``research/p3-partial-observation-harm-v1/`` derives its gold by exactly
the completion-invariance criterion A3 decides by --- so on the one corpus where
A3 can fire, agreeing with gold is its definition restated. ``G9_HARM_A3``
detects that by reading each corpus's declared gold-derivation rule rather than a
hard-coded list, and refuses to report the zero as safety.

**Amendment 003 (2026-08-22).** Amendment 002 named what would discharge
``G9_HARM_A3`` and then judged it unbuildable: "under partial observation the
relation is genuinely underdetermined, so an independent gold has to come from
adjudicators rather than from a rule". That conflates the relation with the
inference. What a one-sided absence underdetermines is what a procedure reading
only the projections may conclude. The relation between the two *source
statements* is fixed by the sources; a projection's silence is a fact about
ORION's extraction of them, and gold anchored to the sources does not move when
the extraction drops a coordinate. ``INTACT_DERIVATION`` already carries gold of
that kind --- its MUSE cases state neither ``polarity`` nor ``modality`` on either
side and their gold is ``COMPATIBLE`` anyway, because
``identity:upstream-coreference-edge`` reads the annotation rather than the
coordinates. This amendment adds the asymmetric version:
``research/p3-partial-observation-record-gold-v1/``, built by
:mod:`orion.study.p3.partial_observation_record_gold_build`, whose every case is
a pair of source records stating all nine coordinates, whose gold is the relation
between those records, and whose shipped projections are those records after an
extraction loss on one side. No threshold moves and no gate changes its subject.

Over that corpus A3 is measured. It destroys 9 of the 17 correct answers it could
have destroyed, against A1's 17 of 17, so ``G9_HARM_A3`` fails on evidence
instead of running ``CANNOT_CHECK`` on circularity, and ``G10_BENEFIT_A3``
finally has a corpus separating A3 from A1 on gold neither of them wrote. The
zero A3 could not earn is not reachable by any non-circular corpus either: A3
abstains on every *decisive* one-sided absence, so wherever gold is determinate
there and A0 is right, A3 must destroy that answer. Only a gold that is
determinate exactly where the completions agree could report otherwise, and that
is completion-invariance under another name --- which the runner now detects
extensionally as well as by declaration, so editing a corpus into circularity
returns the gate to ``CANNOT_CHECK`` rather than passing it.

**Amendment 004 (2026-08-22).** Amendment 003 left ``G9_HARM_A3`` failing on nine
destroyed answers and an open question: is nine a defect of ``A3`` that a better
candidate-visible rule could avoid, or the price of the evidence? It is the
price, and this amendment measures it rather than arguing it. Put two of
``INTACT_RECORD_GOLD``'s cases side by side with everything no rule may read
stripped away --- the bookkeeping fields, the identity of the opaque ids, and the
left/right orientation, none of which the relation reads --- and nine pairs of
cases collapse onto each other while their gold stays different. Gold is
therefore **not a function of the projections**: the information that decides is
exactly the value the extraction destroyed, and a rule reading only the
projections answers one relation for both members of such an orbit and is wrong
on one of them. Nine orbits, so nine of the thirty-six cases cannot be answered
correctly by any candidate-visible rule at all; the best reachable exact
agreement is 27 of 36, and ``A0_orion_current`` already reaches it. On each of
the nine, gold carries both ``COMPATIBLE`` and a separation, so a determinate
answer is a false merge on one member or a false split on the other and the only
answer that is neither is ``UNRESOLVED`` --- which destroys the one answer ``A0``
gets right there. Summed: **9**, exactly what ``A3`` pays. ``A3``'s harm is a
floor and not a repairable defect, and the amendment says so on the gate instead
of leaving a FAIL that reads like a defect. No arm is added, because none can
help: the search for a better rule is not hard, it is impossible, and that is the
stronger result. The builder can construct the witness in its sharpest form ---
an ``LA`` case and an ``LD`` case that lose the *same* side, whose projections are
then identical value for value, needing neither a swap nor a renaming --- and can
redraw the whole corpus under a different seed, on which every one of these
numbers reproduces. ``G9`` keeps its statement, its threshold, its subject and
its ``FAIL``.

Nothing here edits ``orion.knowledge.semantics``; the candidate rules are
study-local arms. Nothing here edits a frozen atlas, result or receipt, and the
2026-08-21 freeze document and its twin are left byte-identical.

Run it::

    python -m orion.study.p3.partial_observation_probe --repo-root . \
        --output <result>.json --probe-output <probe>.jsonl
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, fields, replace
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
    "papers/orion-13-global-knowledge-portrait/protocol/"
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
    "papers/orion-13-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_001.json"
)

# Amendment 002 (2026-08-22) adds a fourth arm, A3_decisive_absence_only, and the
# two gates that carry it. It does not touch G6_HARM_A1: A1's measured harm is a
# finding, the gate that reports it names A1, and pointing a failing gate at a
# different arm would be a relabelling rather than a repair. Amendment 001 and the
# 2026-08-21 freeze are both left byte-identical.
AMENDMENT_002_DOCUMENT = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_002.md"
)
AMENDMENT_002_TWIN = (
    "papers/orion-13-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_002.json"
)

# Amendment 003 (2026-08-22) gives G9_HARM_A3 the denominator amendment 002 said it
# needed and could not find. It adds a fifth intact corpus whose gold is the
# relation between two *source records*, not a rule about what a projection's
# silence could have hidden, so A3 is scored against a standard it did not write.
# No threshold moves and no gate changes its subject. Amendments 001 and 002 and
# the 2026-08-21 freeze are all left byte-identical.
AMENDMENT_003_DOCUMENT = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_003.md"
)
AMENDMENT_003_TWIN = (
    "papers/orion-13-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_003.json"
)

# Amendment 004 (2026-08-22) adds no arm, no corpus and no gate. It settles what
# G9_HARM_A3's FAIL means by measuring the ceiling the corpus imposes on any rule
# that reads only the projections, and annotates the gate with it. G9 keeps its
# statement, its threshold, its subject and its FAIL. Amendments 001, 002 and 003
# and the 2026-08-21 freeze are all left byte-identical.
AMENDMENT_004_DOCUMENT = (
    "papers/paper-03-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_004.md"
)
AMENDMENT_004_TWIN = (
    "papers/orion-13-global-knowledge-portrait/protocol/"
    "P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_004.json"
)

#: The twin the runner checks itself against. Points at the amendment in force, so
#: a digest drift is caught against the record actually running.
FREEZE_TWIN = AMENDMENT_004_TWIN

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
ARM_DECISIVE = "A3_decisive_absence_only"


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


#: The prefix every synthetic completion value carries, so a value invented by
#: :func:`admissible_completions` can never be mistaken for one a source stated.
COMPLETION_WITNESS_PREFIX = "orion:p3:completion-witness"


def _differing_completion(coordinate: str, mirror: Any) -> Any:
    """A value the silent source could have stated that is *not* the mirror's.

    Derived from the coordinate's own type and from the value the other side
    states, and from nothing else. In particular it is not drawn from any
    corpus's vocabulary: a rule that asked "could the silence have hidden one of
    *these* values" would be reading its answer off whichever table it was handed.
    """

    absent = ABSENT_VALUE[coordinate]
    if isinstance(absent, tuple):
        witness = (f"{COMPLETION_WITNESS_PREFIX}:{coordinate}",)
        return witness if witness != mirror else (f"{COMPLETION_WITNESS_PREFIX}:{coordinate}:alt",)
    if isinstance(absent, (Polarity, Modality)):
        for value in type(absent):
            if value is not absent and value != mirror:
                return value
        raise ValueError(f"{coordinate} has no value distinct from both absent and {mirror!r}")
    witness = f"{COMPLETION_WITNESS_PREFIX}:{coordinate}"
    return witness if witness != mirror else f"{COMPLETION_WITNESS_PREFIX}:{coordinate}:alt"


def admissible_completions(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> Iterator[tuple[ScientificMeaningProjection, ScientificMeaningProjection]]:
    """Every pair the two sources' silences are compatible with.

    For each coordinate stated on exactly one side, the silent source either
    agreed with the other (the *mirror* completion) or did not (a *differing*
    completion). Two witnesses per absence is not a sample: every branch of
    ``compare_meaning`` tests an absent coordinate only for equality with the
    mirror --- the three ``left.X and right.X`` guards, ``_same_or_empty``, the
    ``modality`` inequality and the ``polarity`` inequality all do --- so the
    relation, as a function of what the silent source might have said, takes at
    most the two values these witnesses produce. A pair with no one-sided absence
    has exactly one completion, itself.
    """

    absences = _one_sided_absences(left, right)
    if not absences:
        yield left, right
        return
    per_coordinate: list[tuple[tuple[str, str, Any], ...]] = []
    for coordinate in absences:
        if observed(left, coordinate):
            silent_side, mirror = "right", getattr(left, coordinate)
        else:
            silent_side, mirror = "left", getattr(right, coordinate)
        per_coordinate.append(
            tuple(
                (silent_side, coordinate, value)
                for value in (mirror, _differing_completion(coordinate, mirror))
            )
        )
    for combination in itertools.product(*per_coordinate):
        left_overrides = {name: value for side, name, value in combination if side == "left"}
        right_overrides = {name: value for side, name, value in combination if side == "right"}
        yield (
            replace(left, **left_overrides) if left_overrides else left,
            replace(right, **right_overrides) if right_overrides else right,
        )


def arm_decisive_absence_only(
    left: ScientificMeaningProjection, right: ScientificMeaningProjection
) -> MeaningRelation:
    """Abstain only when the absence changes the answer.

    A1 abstains on the *presence* of a one-sided absence. That is a defect in A1's
    design rather than in the measurement that caught it: what warrants abstention
    is not that a source was silent but that the silence is what the answer turns
    on. This arm runs ``compare_meaning`` over every admissible completion of every
    one-sided absence and abstains only when the completions disagree; where they
    agree, the silence could not have changed the relation and there is nothing to
    abstain over.

    It is defined in terms of ``compare_meaning`` --- the system under test --- and
    the coordinate types, and it imports nothing from any corpus builder. That
    matters: any corpus whose gold is *derived* by a completion-invariance rule
    scores this arm against a restatement of its own definition, and this module
    refuses to read a number off such a corpus (see ``G9_HARM_A3``).
    """

    relations = {
        compare_meaning(completed_left, completed_right).relation
        for completed_left, completed_right in admissible_completions(left, right)
    }
    if len(relations) == 1:
        return relations.pop()
    return MeaningRelation.UNRESOLVED


ARMS: dict[str, Arm] = {
    ARM_CURRENT: arm_orion_current,
    ARM_ASYMMETRIC: arm_observedness_asymmetric,
    ARM_STRICT: arm_observedness_strict,
    ARM_DECISIVE: arm_decisive_absence_only,
}
ARM_ORDER: tuple[str, ...] = (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT, ARM_DECISIVE)

#: The arms frozen on 2026-08-21 and amended on 2026-08-22 by amendment 001. The
#: mining census of ``G5_MINING_YIELD`` is a published finding about *these*; it
#: is computed over this tuple so that adding a candidate arm cannot retroactively
#: move it. ``A3``'s own census is reported separately and in full.
MINING_ARM_ORDER: tuple[str, ...] = (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)

#: Candidate repairs, i.e. every arm that is not the system under test. Harm is
#: reported for each of them against ``A0_orion_current``.
CANDIDATE_ARM_ORDER: tuple[str, ...] = (ARM_ASYMMETRIC, ARM_STRICT, ARM_DECISIVE)


# --------------------------------------------------------------------------
# Corpora (freeze section 4.3)
# --------------------------------------------------------------------------

INTACT_DERIVATION = "INTACT_DERIVATION"
INTACT_HELDOUT_REAL = "INTACT_HELDOUT_REAL"
INTACT_HELDOUT_SYNTHETIC = "INTACT_HELDOUT_SYNTHETIC"
INTACT_HARM_SYNTHETIC = "INTACT_HARM_SYNTHETIC"
INTACT_RECORD_GOLD = "INTACT_RECORD_GOLD"
PROBE_DERIVATION = "PROBE_DERIVATION"
PROBE_HELDOUT_REAL = "PROBE_HELDOUT_REAL"
PROBE_HELDOUT_SYNTHETIC = "PROBE_HELDOUT_SYNTHETIC"

INTACT_SOURCES: dict[str, str] = {
    INTACT_DERIVATION: (
        "papers/orion-13-global-knowledge-portrait/gold/adjudicated/"
        "public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    ),
    INTACT_HELDOUT_REAL: (
        "papers/orion-13-global-knowledge-portrait/gold/adjudicated/"
        "public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    ),
    INTACT_HELDOUT_SYNTHETIC: "research/p3-coordinate-necessity-v1/cases.jsonl",
    # Amendment 001. Added because G6_HARM_A1 had no denominator: the three
    # corpora above state every coordinate on both sides of every pair or on
    # neither, so A1 could not fire on any of them and its zero was structural.
    # See AMENDMENT_DOCUMENT and research/p3-partial-observation-harm-v1/.
    INTACT_HARM_SYNTHETIC: "research/p3-partial-observation-harm-v1/cases.jsonl",
    # Amendment 003. Added because G9_HARM_A3 had no *non-circular* denominator:
    # the corpus above does have one-sided absences, but derives its gold by the
    # completion-invariance criterion A3 decides by, so A3 agrees with it by
    # construction. This corpus derives its gold by
    # identity:frozen-source-record-relation --- the relation between two source
    # records, each of which states every coordinate --- and then applies an
    # extraction loss to the projections. Gold never asks what the silence could
    # have hidden. See AMENDMENT_003_DOCUMENT and
    # research/p3-partial-observation-record-gold-v1/.
    INTACT_RECORD_GOLD: "research/p3-partial-observation-record-gold-v1/cases.jsonl",
}

# The addresses these corpora had when the coordinate freeze was taken. R0
# (3a1a83178) moved the paper directory, which changed every path string above and
# therefore changed sha256_json(FROZEN_PARAMETERS) -- breaking a freeze that had
# recorded nothing scientific about the move. INTACT_SOURCES must track the live
# tree because its values are dereferenced (repo_root / relative -> load_jsonl);
# what the freeze recorded must not move at all. Keeping the two separate is what
# lets the digest match while the files stay readable.
INTACT_SOURCES_AS_FROZEN: dict[str, str] = {
    key: value.replace(
        "papers/orion-13-global-knowledge-portrait",
        "papers/paper-03-global-knowledge-portrait",
    )
    for key, value in INTACT_SOURCES.items()
}

#: What each intact corpus is for. Declared per corpus rather than inferred from
#: whether it happens to parent a probe, so a corpus added later has to say what
#: job it is doing instead of inheriting one.
INTACT_ROLE: dict[str, str] = {
    INTACT_DERIVATION: "HARM_AND_PROBE_PARENT",
    INTACT_HELDOUT_REAL: "HARM_AND_PROBE_PARENT",
    INTACT_HELDOUT_SYNTHETIC: "HARM_AND_PROBE_PARENT",
    INTACT_HARM_SYNTHETIC: "HARM_MEASUREMENT_ONLY",
    INTACT_RECORD_GOLD: "HARM_MEASUREMENT_ON_GOLD_ANCHORED_OUTSIDE_THE_PROJECTIONS",
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
    INTACT_RECORD_GOLD,
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
PARTIALLY_OBSERVED_INTACT_ORDER: tuple[str, ...] = (
    INTACT_HARM_SYNTHETIC,
    INTACT_RECORD_GOLD,
)


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


def mining_census(
    scored: Sequence[ScoredCase], *, arms: Sequence[str] = MINING_ARM_ORDER
) -> dict[str, Any]:
    """Freeze section 7.1: for every failure, what could have told the pair apart.

    A non-empty ``discriminating_coordinates`` set means the failure is explained
    by a coordinate ORION already carries. An empty set means no coordinate in
    the representation can discriminate the pair, and the missing thing is not a
    dimension.

    ``arms`` defaults to :data:`MINING_ARM_ORDER`, the three arms ``G5_MINING_YIELD``
    was frozen over. Amendment 002 adds a fourth arm, and a published finding about
    three arms may not silently become a finding about four: A3's census is
    computed separately, reported in full on the gate, and pinned by a test, so
    scoping is a way of keeping the old number honest rather than of hiding the
    new one.
    """

    admitted = set(arms)
    rows: list[dict[str, Any]] = []
    for item in scored:
        if item.arm_id not in admitted:
            continue
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
    """How many intact decisions this arm moves, and how many correct ones it destroys.

    ``pairs_a0_answers_correctly_with_a_one_sided_absence`` is the harm
    denominator proper: a correct answer can only be destroyed on a pair A0
    already answers correctly, and an observedness-sensitive arm can only move a
    pair with an absence in it. A zero there means the corpus could not have
    reported a harm whatever the arm did --- the same emptiness ``G6_HARM_A1``
    carried before amendment 001, made visible per arm rather than inferred.
    """

    baseline = {item.case_id: item for item in scored if item.arm_id == ARM_CURRENT}
    candidate = [item for item in scored if item.arm_id == arm_id]
    changed = [item for item in candidate if item.predicted is not baseline[item.case_id].predicted]
    destroyed = [
        item
        for item in changed
        if baseline[item.case_id].predicted is baseline[item.case_id].gold
        and item.predicted is not item.gold
    ]
    repaired = [
        item
        for item in changed
        if baseline[item.case_id].predicted is not baseline[item.case_id].gold
        and item.predicted is item.gold
    ]
    correct_and_partial = [
        item
        for item in candidate
        if baseline[item.case_id].predicted is baseline[item.case_id].gold
        and _one_sided_absences(item.left, item.right)
    ]
    return {
        "arm_id": arm_id,
        "n_cases": len(candidate),
        "decisions_changed": len(changed),
        "fraction_changed": (len(changed) / len(candidate)) if candidate else None,
        "correct_answers_destroyed": len(destroyed),
        "wrong_answers_repaired": len(repaired),
        "pairs_a0_answers_correctly": sum(
            1 for item in candidate if baseline[item.case_id].predicted is baseline[item.case_id].gold
        ),
        "pairs_a0_answers_correctly_with_a_one_sided_absence": len(correct_and_partial),
        "changed_case_ids": sorted(item.case_id for item in changed)[:8],
    }


def arm_disagreement(
    scored: Sequence[ScoredCase], arm_id: str, other_arm_id: str
) -> dict[str, Any]:
    """On how many cases two arms name different relations, and who is right there.

    A candidate repair that never differs from the arm it repairs has not been
    shown to repair anything. This is the number that says whether a corpus can
    tell them apart at all.
    """

    left = {item.case_id: item for item in scored if item.arm_id == arm_id}
    right = {item.case_id: item for item in scored if item.arm_id == other_arm_id}
    shared = sorted(set(left) & set(right))
    differing = [case_id for case_id in shared if left[case_id].predicted is not right[case_id].predicted]
    return {
        "arm_id": arm_id,
        "other_arm_id": other_arm_id,
        "n_cases": len(shared),
        "n_differing": len(differing),
        "n_differing_where_this_arm_is_right": sum(
            1
            for case_id in differing
            if left[case_id].predicted is left[case_id].gold
            and right[case_id].predicted is not right[case_id].gold
        ),
        "n_differing_where_the_other_arm_is_right": sum(
            1
            for case_id in differing
            if right[case_id].predicted is right[case_id].gold
            and left[case_id].predicted is not left[case_id].gold
        ),
        "differing_case_ids": differing[:8],
    }


def exact_agreement_with_gold(scored: Sequence[ScoredCase], arm_id: str) -> dict[str, Any]:
    """How often this arm names exactly the relation gold names.

    Reported for a single purpose: an arm that reproduces gold on every case of a
    corpus has zero harm there by arithmetic, so that zero carries no information
    the accuracy number does not already carry. Where the corpus's gold is derived
    by the same criterion the arm decides by, neither number is a measurement.
    """

    rows = [item for item in scored if item.arm_id == arm_id]
    exact = [item for item in rows if item.predicted is item.gold]
    return {
        "arm_id": arm_id,
        "n_cases": len(rows),
        "n_exact": len(exact),
        "reproduces_gold_on_every_case": bool(rows) and len(exact) == len(rows),
    }


def exact_agreement_where_the_arm_can_fire(
    scored: Sequence[ScoredCase], arm_id: str
) -> dict[str, Any]:
    """The same question, restricted to the pairs the arm can act on.

    An observedness-sensitive arm is ``A0`` everywhere except on a pair with a
    one-sided absence, so a corpus's gold *restricted to those pairs* is the only
    part of it the arm can be scored against. If gold agrees with the arm on every
    one of them, then the corpus's gold, where the arm can fire, is the arm --- and
    the arm's zero harm there follows by arithmetic, exactly as it does under
    :func:`exact_agreement_with_gold`'s whole-corpus version.

    This is the extensional form of the circularity check.
    :func:`gold_provenance` reads the derivation rule a corpus *declares*; this
    reads what its gold *does*. A corpus that declared an innocent rule and then
    populated its partially observed pairs so that gold and the arm coincide would
    pass the nominal check and fail this one. ``bool(rows)`` keeps it from firing
    vacuously on a corpus with no partially observed pair at all: that corpus is
    already withheld for having no harm denominator, and a vacuous truth is the
    substitution this lane exists to prevent.
    """

    rows = [
        item
        for item in scored
        if item.arm_id == arm_id and _one_sided_absences(item.left, item.right)
    ]
    exact = [item for item in rows if item.predicted is item.gold]
    return {
        "arm_id": arm_id,
        "n_pairs_with_a_one_sided_absence": len(rows),
        "n_exact": len(exact),
        "reproduces_gold_on_every_pair_it_can_fire_on": bool(rows) and len(exact) == len(rows),
    }


#: A gold-derivation rule naming this criterion decides a case by asking whether
#: the relation is constant over the admissible completions of what one source did
#: not state --- which is exactly what ``arm_decisive_absence_only`` asks. A corpus
#: declaring it cannot score that arm: the answer is the definition.
DECISIVENESS_RULE_MARKER = "completion-invariance"

#: What the freeze fixes as the gold of a probe case. Recorded as a rule string so
#: probe corpora carry the same provenance field the intact corpora carry.
PROBE_GOLD_DERIVATION_RULE = "freeze:probe-gold-is-unresolved-after-redaction"


def gold_provenance(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The derivation rules a corpus's own records declare for its gold.

    Read off ``expected.authority.derivation.rule``, i.e. from the corpus rather
    than from a table in this module keyed by corpus id. A hard-coded list of
    "circular corpora" would go stale the moment one was added; a corpus that
    declares how its gold was derived can be checked against a candidate arm's
    criterion mechanically.
    """

    rules: set[str] = set()
    declared = 0
    for case in cases:
        expected = case.get("expected")
        if not isinstance(expected, Mapping):
            continue
        authority = expected.get("authority")
        if not isinstance(authority, Mapping):
            continue
        derivation = authority.get("derivation")
        if not isinstance(derivation, Mapping):
            continue
        rule = derivation.get("rule")
        if rule:
            declared += 1
            rules.add(str(rule))
    marked = sorted(rule for rule in rules if DECISIVENESS_RULE_MARKER in rule)
    return {
        "declared_rules": sorted(rules),
        "n_cases_declaring_a_rule": declared,
        "n_cases": len(cases),
        "rules_naming_completion_invariance": marked,
        "gold_derived_by_completion_invariance": bool(marked),
    }


def independent_harm_evidence(entry: Mapping[str, Any], arm_id: str) -> dict[str, Any]:
    """Whether one corpus can say anything about this arm's harm that its gold
    does not already entail.

    Four ways it cannot. The corpus has no harm denominator, so no arm could have
    reported a harm on it. Its gold is *declared* to be derived by the criterion
    the arm decides by, so the arm's decisions are a restatement of gold. Its
    gold *behaves* that way on every pair the arm can fire on, whatever it
    declares, which is the same circularity reached by construction instead of by
    declaration (amendment 003). Or the arm reproduces gold on every case, so its
    zero harm follows from a perfect score rather than from a comparison.

    All four are deliberately conservative --- they can only refuse a pass, never
    grant one --- because a harm gate that reports safety it did not measure is the
    failure this whole lane exists to prevent. None of them refuses a *failure*:
    an arm that destroys a correct answer has destroyed it whatever the gold
    rule's provenance, which is why the gate reads the harm count before it reads
    this block.
    """

    harm = entry["harm_vs_current"][arm_id]
    provenance = entry["gold_provenance"]
    agreement = entry["exact_agreement_with_gold"][arm_id]
    where_it_fires = entry["exact_agreement_where_the_arm_can_fire"][arm_id]
    denominator = int(harm["pairs_a0_answers_correctly_with_a_one_sided_absence"])
    circular_gold = bool(provenance["gold_derived_by_completion_invariance"])
    reproduces = bool(agreement["reproduces_gold_on_every_case"])
    reproduces_where_it_fires = bool(
        where_it_fires["reproduces_gold_on_every_pair_it_can_fire_on"]
    )
    reasons: list[str] = []
    if denominator == 0:
        reasons.append("NO_HARM_DENOMINATOR")
    if circular_gold:
        reasons.append("GOLD_DERIVED_BY_THE_CRITERION_THE_ARM_DECIDES_BY")
    if reproduces_where_it_fires:
        reasons.append("GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE")
    if reproduces:
        reasons.append("ARM_REPRODUCES_GOLD_ON_EVERY_CASE")
    return {
        "harm_denominator": denominator,
        "gold_derived_by_completion_invariance": circular_gold,
        "declared_gold_rules": list(provenance["declared_rules"]),
        "arm_reproduces_gold_on_every_case": reproduces,
        "arm_reproduces_gold_on_every_pair_it_can_fire_on": reproduces_where_it_fires,
        "n_pairs_the_arm_can_fire_on": int(
            where_it_fires["n_pairs_with_a_one_sided_absence"]
        ),
        "supplies_independent_evidence": not reasons,
        "withheld_because": reasons,
    }


def gold_is_the_arms_own_criterion(entry: Mapping[str, Any], arm_id: str) -> bool:
    """True when this corpus's gold is the arm's rule, by declaration or in effect.

    Kept as one predicate so that the two gates that ask the question ---
    ``G9_HARM_A3``'s evidence block and ``G10_BENEFIT_A3``'s separation count ---
    cannot drift apart into a corpus that is circular for one and independent for
    the other.
    """

    if bool(entry["gold_provenance"]["gold_derived_by_completion_invariance"]):
        return True
    return bool(
        entry["exact_agreement_where_the_arm_can_fire"][arm_id][
            "reproduces_gold_on_every_pair_it_can_fire_on"
        ]
    )


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
# The identifiability ceiling (amendment 004)
# --------------------------------------------------------------------------

#: Fields of a projection that carry per-case bookkeeping and nothing the
#: relation reads: which record a case drew the projection from, and where. Two
#: cases whose projections differ only here are, to any rule about *meaning*, the
#: same pair. A rule that told them apart would be reading the case id.
CANONICAL_BOOKKEEPING_FIELDS: tuple[str, ...] = (
    "projection_id",
    "source_id",
    "source_span",
)

#: Fields whose values are opaque ids minted by whoever built the corpus. Nothing
#: in ``compare_meaning`` or in any arm reads them except for equality --- across
#: the pair and, for the list coordinates, within a value --- so a consistent
#: renaming across both sides changes no arm's answer and no relation. The
#: canonical form relabels them by first occurrence, which is exactly a
#: consistent renaming.
OPEN_VOCABULARY_FIELDS: tuple[str, ...] = (
    "predicate",
    "referent_ids",
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
    "assumption_ids",
    "attribution_id",
    "discourse_relation",
    "unresolved_ambiguities",
)

#: Fields whose values come from a closed enumeration. These are relabelled only
#: when asked, and never across the absent value: ``Polarity.UNKNOWN`` and
#: ``Modality.UNKNOWN`` are what a silence looks like, so a relabelling that moved
#: them would be erasing the very thing under study. Relabelling the *stated*
#: values is a different matter --- ``compare_meaning`` and every arm read
#: ``polarity`` only through ``left.polarity != right.polarity``, so which of the
#: two poles a record happens to state is a labelling, and a rule that answered
#: differently according to which one survived extraction would be reading the
#: label rather than the relation.
CLOSED_VOCABULARY_FIELDS: tuple[str, ...] = ("polarity", "modality")

#: The one structured field. ``argument_roles`` is a tuple of ``(role, filler)``
#: pairs; no rule in this study reads it, but it is part of the projection, so it
#: is canonicalised rather than dropped --- dropping it would make two pairs the
#: same evidence on the strength of a field this module chose to ignore.
CANONICAL_ROLE_FIELDS: tuple[str, ...] = ("argument_roles",)

#: The token every absent value canonicalises to, in every field.
CANONICAL_ABSENT_TOKEN = "ABSENT"


def canonicalisation_field_census() -> dict[str, Any]:
    """Every field of a projection, and what the canonical form does with it.

    A field this module neither reads nor names as bookkeeping would be silently
    ignored, and two pairs that differ only in it would be reported as the same
    evidence --- which is how a ceiling gets overstated. So the split is computed
    against the dataclass rather than asserted, and a field added to
    :class:`~orion.knowledge.semantics.ScientificMeaningProjection` shows up here
    as uncovered until someone decides which side it belongs on.
    """

    declared = tuple(field.name for field in fields(ScientificMeaningProjection))
    accounted = (
        set(CANONICAL_BOOKKEEPING_FIELDS)
        | set(OPEN_VOCABULARY_FIELDS)
        | set(CLOSED_VOCABULARY_FIELDS)
        | set(CANONICAL_ROLE_FIELDS)
    )
    return {
        "projection_fields": list(declared),
        "stripped_as_bookkeeping": list(CANONICAL_BOOKKEEPING_FIELDS),
        "relabelled_as_open_vocabulary": list(OPEN_VOCABULARY_FIELDS),
        "relabelled_as_closed_vocabulary": list(CLOSED_VOCABULARY_FIELDS),
        "relabelled_as_role_structure": list(CANONICAL_ROLE_FIELDS),
        "uncovered": sorted(set(declared) - accounted),
        "named_but_not_a_projection_field": sorted(accounted - set(declared)),
        "covers_every_field": not (set(declared) - accounted)
        and not (accounted - set(declared)),
    }


def _canonical_orientation(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
    *,
    relabel_closed_vocabularies: bool,
) -> str:
    """One orientation's canonical string, ids relabelled by first occurrence."""

    table: dict[tuple[str, Any], str] = {}
    counts: dict[str, int] = {}

    def label(field: str, value: Any) -> str:
        key = (field, value)
        if key not in table:
            counts[field] = counts.get(field, 0) + 1
            table[key] = f"{field}#{counts[field]}"
        return table[key]

    form: list[Any] = []
    for field in OPEN_VOCABULARY_FIELDS:
        for side in (left, right):
            value = getattr(side, field)
            if isinstance(value, tuple):
                form.append([label(field, item) for item in value])
            else:
                form.append(label(field, value) if value else CANONICAL_ABSENT_TOKEN)
    for field in CANONICAL_ROLE_FIELDS:
        for side in (left, right):
            form.append(
                [
                    [label(f"{field}:role", role), label(f"{field}:filler", filler)]
                    for role, filler in getattr(side, field)
                ]
            )
    for field in CLOSED_VOCABULARY_FIELDS:
        for side in (left, right):
            value = getattr(side, field)
            if value == ABSENT_VALUE[field]:
                form.append(CANONICAL_ABSENT_TOKEN)
            elif relabel_closed_vocabularies:
                form.append(label(field, value))
            else:
                form.append(value.value)
    return json.dumps(form, separators=(",", ":"))


def canonical_pair_form(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
    *,
    relabel_closed_vocabularies: bool = True,
) -> str:
    """What two projections look like once everything no rule may read is gone.

    Three things are stripped, and each of them is stripped because *gold* does
    not read it, not because it was convenient:

    * the bookkeeping fields, which say which record the projection came from;
    * the identity of the opaque ids, which every rule reads only for equality,
      so a consistent renaming across both sides is invisible to all of them;
    * the orientation, because a meaning relation is symmetric --- ``COMPATIBLE``
      and ``DISTINCT_REFERENT`` are relations *between* two statements and
      ``compare_meaning`` returns the same value on a swapped pair.

    Two pairs with the same canonical form are the same evidence. A rule that is
    a function of the projections alone and does not read bookkeeping therefore
    gives them the same answer; :func:`identifiability_ceiling` checks that every
    arm on record actually does, rather than assuming it.
    """

    return min(
        _canonical_orientation(
            left, right, relabel_closed_vocabularies=relabel_closed_vocabularies
        ),
        _canonical_orientation(
            right, left, relabel_closed_vocabularies=relabel_closed_vocabularies
        ),
    )


def projection_orbits(
    pairs: Sequence[tuple[str, ScientificMeaningProjection, ScientificMeaningProjection, MeaningRelation]],
    *,
    relabel_closed_vocabularies: bool = True,
) -> dict[str, list[tuple[str, MeaningRelation]]]:
    """Cases grouped by canonical form, each with its case id and its gold."""

    grouped: dict[str, list[tuple[str, MeaningRelation]]] = {}
    for case_id, left, right, gold in pairs:
        form = canonical_pair_form(
            left, right, relabel_closed_vocabularies=relabel_closed_vocabularies
        )
        grouped.setdefault(form, []).append((case_id, gold))
    return grouped


def identifiability_ceiling(
    pairs: Sequence[tuple[str, ScientificMeaningProjection, ScientificMeaningProjection, MeaningRelation]],
    *,
    relabel_closed_vocabularies: bool = True,
) -> dict[str, Any]:
    """How well any rule reading only the projections could possibly do here.

    A corpus can carry two cases whose projections are the same evidence and
    whose gold differs. When it does, gold is not a function of the projections,
    and no rule that reads only the projections is right on both: it answers one
    relation for the two of them and is wrong on at least one. Counting those
    orbits turns "this arm destroys nine correct answers" into a question with a
    determinate answer --- is nine a defect of the arm, or the price of the
    evidence?

    Three numbers come out of it.

    ``n_pairs_no_candidate_visible_rule_can_answer_correctly``
        the cases that must be wrong, summed over orbits: an orbit of size *n*
        whose most common gold covers *m* of them costs *n - m*.

    ``max_exact_agreement_reachable_by_a_candidate_visible_rule``
        the complement, i.e. the best accuracy any such rule can reach.

    ``harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split``
        the cost of the only escape. On an orbit carrying both ``COMPATIBLE`` and
        a non-merge gold, a determinate answer is a false merge on one member or
        a false split on another; the sole answer that is neither is
        ``UNRESOLVED``, and that destroys every answer ``A0`` gets right on the
        orbit. Summed, that is the smallest harm such an arm can pay.

    The last number is a floor and not a target. An arm is free to pay less by
    answering exactly what ``A0`` answers --- and then it *is* ``A0`` on those
    pairs, over-resolving where the projections do not determine the relation,
    which is the failure this whole study exists to demonstrate.
    """

    orbits = projection_orbits(
        pairs, relabel_closed_vocabularies=relabel_closed_vocabularies
    )
    predicted: dict[str, dict[str, MeaningRelation]] = {
        arm_id: {case_id: ARMS[arm_id](left, right) for case_id, left, right, _gold in pairs}
        for arm_id in ARM_ORDER
    }
    gold_of = {case_id: gold for case_id, _left, _right, gold in pairs}

    reachable = 0
    unanswerable = 0
    rows: list[dict[str, Any]] = []
    floor = 0
    trilemma_orbits = 0
    for form in sorted(orbits, key=lambda key: sorted(case_id for case_id, _ in orbits[key])[0]):
        members = orbits[form]
        golds = [gold for _case_id, gold in members]
        best = max(golds.count(relation) for relation in set(golds))
        reachable += best
        unanswerable += len(members) - best
        if len(set(golds)) == 1:
            continue
        a0 = {predicted[ARM_CURRENT][case_id] for case_id, _gold in members}
        a0_correct = sorted(
            case_id for case_id, gold in members if predicted[ARM_CURRENT][case_id] is gold
        )
        forces_a_choice = any(
            gold is MeaningRelation.COMPATIBLE for gold in golds
        ) and any(gold in NONMERGE_RELATIONS for gold in golds)
        if forces_a_choice:
            trilemma_orbits += 1
            floor += len(a0_correct)
        rows.append(
            {
                "case_ids": sorted(case_id for case_id, _gold in members),
                "golds": sorted({gold.value for gold in golds}),
                "a0_answer": sorted(relation.value for relation in a0),
                "a0_is_correct_on": a0_correct,
                "forces_a_false_merge_a_false_split_or_an_abstention": forces_a_choice,
            }
        )

    constant: dict[str, bool] = {}
    for arm_id in ARM_ORDER:
        constant[arm_id] = all(
            len({predicted[arm_id][case_id] for case_id, _gold in members}) == 1
            for members in orbits.values()
        )
    exact = {
        arm_id: sum(
            1 for case_id in gold_of if predicted[arm_id][case_id] is gold_of[case_id]
        )
        for arm_id in ARM_ORDER
    }
    return {
        "canonicalisation": {
            "bookkeeping_fields_stripped": list(CANONICAL_BOOKKEEPING_FIELDS),
            "open_vocabulary_fields_relabelled": list(OPEN_VOCABULARY_FIELDS),
            "closed_vocabulary_fields_relabelled": (
                list(CLOSED_VOCABULARY_FIELDS) if relabel_closed_vocabularies else []
            ),
            "role_structure_fields_relabelled": list(CANONICAL_ROLE_FIELDS),
            "left_right_swap_allowed": True,
            "absent_values_are_never_relabelled": True,
            "covers_every_projection_field": bool(
                canonicalisation_field_census()["covers_every_field"]
            ),
        },
        "n_pairs": len(pairs),
        "n_orbits": len(orbits),
        "n_undecidable_orbits": len(rows),
        "n_pairs_in_an_undecidable_orbit": sum(len(row["case_ids"]) for row in rows),
        "n_pairs_no_candidate_visible_rule_can_answer_correctly": unanswerable,
        "max_exact_agreement_reachable_by_a_candidate_visible_rule": reachable,
        "exact_agreement_by_arm": {arm_id: exact[arm_id] for arm_id in ARM_ORDER},
        "arms_at_the_ceiling": [
            arm_id for arm_id in ARM_ORDER if exact[arm_id] == reachable and pairs
        ],
        "n_orbits_forcing_a_false_merge_a_false_split_or_an_abstention": trilemma_orbits,
        "harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split": floor,
        "every_arm_is_constant_on_every_orbit": all(constant.values()),
        "arm_is_constant_on_every_orbit": constant,
        "undecidable_orbits": rows,
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
    "G9_HARM_A3": {
        "statement": (
            "A3_decisive_absence_only destroys 0 correct answers on every intact corpus, and "
            "at least one intact corpus supplies independent evidence for that zero: it has a "
            "harm denominator (a pair A0 answers correctly and A3 can fire on), its gold is not "
            "derived by the completion-invariance criterion A3 decides by, and A3 does not "
            "reproduce its gold on every case"
        ),
        "blocking": True,
        "why_a_separate_gate": (
            "G6_HARM_A1 names A1_observedness_asymmetric and reports a measured harm of 12 "
            "destroyed answers. That is a finding. Repointing it at the arm that repairs A1 "
            "would turn a failing gate into a passing one by changing its subject, which is "
            "the relabelling this repository keeps finding. G6 keeps failing for A1; this "
            "gate carries A3 and answers for A3 alone."
        ),
        "circularity_note": (
            "research/p3-partial-observation-harm-v1/ derives its gold by "
            "identity:observed-coordinate-precedence-with-completion-invariance --- abstain "
            "where the admissible completions of the absent coordinate disagree. That is A3's "
            "decision rule. On that corpus A3 agrees with gold by construction, so neither its "
            "accuracy nor its harm there is a measurement of A3, and this gate refuses both. "
            "The three corpora frozen on 2026-08-21 have no one-sided absence at all, so A3 "
            "cannot fire on them and its zero there is structural, exactly the emptiness G6 "
            "carried before amendment 001."
        ),
        "discharged_by": (
            "an intact corpus with one-sided absences whose gold is fixed by adjudication or "
            "by a rule that does not ask whether the completions agree, containing at least "
            "one partially observed pair A0 answers correctly"
        ),
        "amendment_003": {
            "denominator_corpus": INTACT_RECORD_GOLD,
            "threshold_unchanged": True,
            "statement_unchanged": True,
            "what_was_added": (
                "the corpus the discharged_by clause above names. Its gold is the relation "
                "between two source *records*, each of which states all nine coordinates, "
                "under the rule identity:frozen-source-record-relation; the projections it "
                "ships are those records after an extraction loss that blanks one coordinate "
                "on one side. The rule is defined only on records that state everything and "
                "raises on anything else, so it has no branch that reads an absence and "
                "cannot be A3's criterion under another name."
            ),
            "why_amendment_002_thought_this_impossible": (
                "amendment 002 recorded that 'under partial observation the relation is "
                "genuinely underdetermined, so an independent gold has to come from "
                "adjudicators rather than from a rule'. That conflates the relation with the "
                "inference. What a one-sided absence underdetermines is what a procedure "
                "reading only the projections may conclude; the relation between the two "
                "source statements is fixed by the sources, and a projection's silence is a "
                "fact about ORION's extraction. INTACT_DERIVATION already carries gold of "
                "that kind: its MUSE cases state neither polarity nor modality on either "
                "side and their gold is COMPATIBLE anyway, because "
                "identity:upstream-coreference-edge reads the annotation rather than the "
                "coordinates."
            ),
            "the_gate_can_now_be_measured_and_it_fails": (
                "A3 destroys correct answers on the new corpus. The count is not a property "
                "of the cases: A3 returns UNRESOLVED on every pair whose one-sided absence is "
                "decisive, so on any such pair whose gold is determinate and which A0 already "
                "answers correctly it must destroy a correct answer. G9 can therefore be "
                "passed non-vacuously only by a corpus whose gold is determinate-and-matching "
                "exactly where the completions agree --- which is the completion-invariance "
                "criterion in extension, whatever rule string it declares. That is the same "
                "shape as the standing caveat about A1 and G6, one arm weaker, and it is "
                "reported rather than repaired."
            ),
            "extensional_circularity_check_added": (
                "supplies_independent_evidence now also fails on "
                "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE, i.e. on a corpus whose "
                "gold agrees with A3 on every pair A3 can fire on regardless of the rule it "
                "declares. Editing the new corpus into circularity --- by deleting the strata "
                "on which its record-anchored gold and A3 disagree --- therefore returns the "
                "gate to CANNOT_CHECK rather than turning it into a PASS."
            ),
        },
        "amendment_004": {
            "threshold_unchanged": True,
            "statement_unchanged": True,
            "subject_unchanged": True,
            "outcome_unchanged": "FAIL",
            "arms_added": [],
            "corpora_added": [],
            "question_it_settles": (
                "whether the nine correct answers A3 destroys on INTACT_RECORD_GOLD are a "
                "defect of A3 that some better candidate-visible rule could avoid, or the "
                "price of the evidence. They are the price."
            ),
            "the_bound": (
                "Strip from a pair of projections everything gold does not read --- the "
                "bookkeeping fields, the identity of the opaque ids (every rule reads them "
                "only for equality, so a consistent renaming across both sides is invisible "
                "to all of them), and the left/right orientation (a meaning relation is "
                "symmetric) --- and nine pairs of INTACT_RECORD_GOLD's cases collapse onto "
                "each other with different gold. Gold is not a function of the projections "
                "there: what decides is the value the extraction destroyed. Nine of the "
                "thirty-six cases therefore cannot be answered correctly by any rule reading "
                "only the projections; the reachable ceiling is 27 of 36 and A0 already "
                "reaches it. On each of the nine orbits gold carries both COMPATIBLE and a "
                "separation, so a determinate answer is a false merge on one member or a "
                "false split on the other, and UNRESOLVED --- the only answer that is neither "
                "--- destroys the one answer A0 gets right there. The harm floor is 9 and A3 "
                "pays exactly 9."
            ),
            "why_no_fifth_arm": (
                "a fifth arm would have to beat 9 while still abstaining where the "
                "projections do not determine the relation, and the bound says no such arm "
                "exists. The best principled candidate --- decide on the coordinates observed "
                "on both sides and ignore the rest, which is the record standard's precedence "
                "order applied to the shared observed frame --- destroys 1 instead of 9 and "
                "buys that by never abstaining at all: its P3.OVERRESOLVED_UNRESOLVED_CASE "
                "violation rate is 1.0 on all three probe corpora against G10's 0.0, i.e. it "
                "surrenders the entire benefit A3 exists for. Registering it as an arm would "
                "be registering A0 with a merge-ward modality reading."
            ),
            "guard_against_fitting_the_measurement": (
                "the bound is stated over the coordinate precedence the record standard "
                "declares and over the symmetries gold itself respects, not over the list of "
                "cases A3 fails; the runner checks mechanically that every arm on record is "
                "constant on every orbit, so the canonicalisation is not stripping something "
                "an arm reads; and the builder can redraw the whole corpus under a different "
                "seed --- new record vocabulary, new closed-vocabulary values, new loss sides "
                "--- on which the orbit count, the ceiling, the floor and A3's harm all "
                "reproduce."
            ),
            "what_did_not_move": (
                "no threshold, no gate statement, no gate subject, no arm, no corpus, no "
                "case. G9 still reads 'destroys 0 correct answers' and still fails. A harm "
                "gate that relaxed its threshold on learning the floor is above zero would be "
                "the relabelling this repository keeps finding; what a floor changes is what "
                "the FAIL means, not whether it fails."
            ),
        },
    },
    "G10_BENEFIT_A3": {
        "statement": (
            "A3_decisive_absence_only's P3.OVERRESOLVED_UNRESOLVED_CASE violation rate is 0.0 "
            "on every probe corpus, i.e. it still abstains everywhere the frozen probe gold "
            "says abstention is right; and report whether any corpus separates A3 from A1"
        ),
        "max_violation_rate": 0.0,
        "blocking": False,
        "note": (
            "probe gold is UNRESOLVED on every probe case, so an arm that abstains "
            "unconditionally scores the same 0.0. A1 and A2 do. This gate therefore shows that "
            "A3 keeps A1's intended benefit; it is not evidence that A3 is better than A1, and "
            "the separation fields say so with a number."
        ),
        "amendment_003": {
            "separating_corpus_added": INTACT_RECORD_GOLD,
            "threshold_unchanged": True,
            "note": (
                "before amendment 003 the only corpus separating A3 from A1 was the one whose "
                "gold is A3's own criterion, so the separation count on non-circular gold was "
                "empty and the gate said so. INTACT_RECORD_GOLD separates them on gold "
                "anchored to the source records, and the separation is reported with which "
                "arm is right on each differing pair. That is a comparison between two "
                "candidate repairs, not evidence that either is safe: G9 carries A3's harm "
                "and G9 fails."
            ),
        },
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
    "amendments": [
    {
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
    {
        "id": "AMENDMENT_002",
        "date": "2026-08-22",
        "document": AMENDMENT_002_DOCUMENT,
        "reason": (
            "G6_HARM_A1 came back FAIL on evidence: A1 abstains on the presence of a "
            "one-sided absence, so on the twelve H_UNDECISIVE_ABSENCE pairs --- where the "
            "absent coordinate is not what the answer turns on --- it destroys an answer A0 "
            "already had right. That is a defect in A1's design, not in the measurement. The "
            "science wants abstention when the absence changes the answer, and no arm on "
            "record decides that way"
        ),
        "changes": [
            "adds A3_decisive_absence_only, a fourth arm that abstains only when the "
            "admissible completions of a one-sided absence disagree about the relation, "
            "alongside A1 and A2 and replacing neither",
            "adds G9_HARM_A3, which reports A3's harm and refuses to read it off a corpus "
            "whose gold is derived by the criterion A3 decides by",
            "adds G10_BENEFIT_A3, which reports whether A3 still abstains where the frozen "
            "probe gold says abstention is right, and whether anything separates A3 from A1",
            "records each corpus's declared gold-derivation rule and each arm's exact "
            "agreement with gold, so the circularity check reads the corpus rather than a "
            "hard-coded list of corpus ids",
            "reports a harm denominator per arm per corpus: the pairs A0 answers correctly "
            "that have a one-sided absence in them",
            "scopes the G5_MINING_YIELD census to the three arms it was frozen over and "
            "reports A3's census beside it, so a published three-arm finding does not "
            "silently become a four-arm one",
        ],
        "unchanged": [
            "G6_HARM_A1: same statement, same threshold, same arm, same FAIL",
            "every other gate threshold and every gate's subject",
            "the coordinate table, the absent-value table, A0, A1, A2 and the probe gold",
            "the four corpora and every case in them",
            "the 2026-08-21 freeze, its twin, and amendment 001 and its twin, all "
            "byte-identical",
        ],
    },
    {
        "id": "AMENDMENT_003",
        "date": "2026-08-22",
        "document": AMENDMENT_003_DOCUMENT,
        "reason": (
            "G9_HARM_A3 ran as CANNOT_CHECK because no intact corpus supplied non-circular "
            "evidence for A3's zero harm: the three corpora frozen on 2026-08-21 have no "
            "one-sided absence for A3 to fire on, and INTACT_HARM_SYNTHETIC derives its gold "
            "by the completion-invariance criterion A3 decides by. Amendment 002 named what "
            "would discharge the gate and judged it unbuildable, on the ground that under "
            "partial observation the relation is genuinely underdetermined. That is true of "
            "the inference and false of the relation: a projection's silence is a fact about "
            "ORION's extraction, and the relation between the two source statements is fixed "
            "by the sources"
        ),
        "changes": [
            "adds INTACT_RECORD_GOLD, a fifth intact corpus whose gold is the relation "
            "between two fully stated source records under "
            "identity:frozen-source-record-relation, with the projections carrying an "
            "extraction loss that blanks one coordinate on one side; built by "
            "orion.study.p3.partial_observation_record_gold_build",
            "excludes that corpus from probe construction, for the same reason "
            "INTACT_HARM_SYNTHETIC is excluded: it has one-sided absences of its own",
            "declares each intact corpus's role in a table rather than inferring it from "
            "whether the corpus happens to parent a probe",
            "adds an extensional circularity check --- a corpus whose gold agrees with A3 on "
            "every pair A3 can fire on is withheld whatever derivation rule it declares --- so "
            "editing a corpus into circularity returns G9 to CANNOT_CHECK instead of passing "
            "it",
            "reports which corpora A3 destroyed a correct answer on and which of those "
            "supply independent gold",
        ],
        "unchanged": [
            "every gate threshold, including G9's 0 and G6's 0",
            "every gate's subject: G6 still names A1 and G9 still names A3",
            "the coordinate table, the absent-value table, A0, A1, A2, A3 and the probe gold",
            "the four corpora frozen before this amendment and every case in them",
            "the 2026-08-21 freeze, its twin, amendments 001 and 002 and their twins, all "
            "byte-identical",
        ],
        "numbers_this_amendment_moves": (
            "G5_MINING_YIELD, G6_HARM_A1 and G7_COST_A2 are totals over the intact corpora, "
            "so adding one moves them. Their per-corpus rows for the four earlier corpora are "
            "unchanged, their thresholds are unchanged, and their outcomes are unchanged: "
            "G5 and G6 were FAIL and stay FAIL. A gate reading 'changes 0 decisions' or "
            "'every failure has a discriminating coordinate' cannot be passed by a corpus "
            "added to it."
        ),
    },
    {
        "id": "AMENDMENT_004",
        "date": "2026-08-22",
        "document": AMENDMENT_004_DOCUMENT,
        "reason": (
            "G9_HARM_A3 came back FAIL on nine destroyed correct answers and left the "
            "question of what the nine mean. A failing harm gate reads as a repairable "
            "defect of the arm it names, and this one is not: the nine are the price of the "
            "evidence, and no rule reading only the projections can pay less while still "
            "abstaining where the projections do not determine the relation. That is a "
            "bound, it is provable from the corpus's own cases, and leaving it unstated "
            "would invite the next amendment to go looking for a fifth arm that cannot exist"
        ),
        "changes": [
            "adds canonical_pair_form and identifiability_ceiling, which group a corpus's "
            "cases by what a rule reading only the projections can see --- bookkeeping "
            "stripped, opaque ids consistently renamed, left/right swap allowed --- and "
            "report the orbits on which gold is not constant",
            "reports, per intact and probe corpus, the ceiling those orbits impose: how many "
            "cases no candidate-visible rule can answer correctly, the best reachable exact "
            "agreement, and which arms reach it",
            "annotates G9_HARM_A3 with the harm floor and with whether A3's harm sits at it, "
            "so the FAIL reads as a floor rather than as a defect",
            "checks mechanically that every arm on record is constant on every orbit, so the "
            "canonicalisation cannot be stripping something an arm actually reads",
            "adds RecordDraw, fresh_draw and held_out_corpus to the corpus builder, so the "
            "whole corpus can be redrawn under a different seed and the finding re-measured "
            "on cases nobody proposed a rule against; the default draw emits the shipped "
            "corpus byte for byte",
            "adds undecidability_witness_cases to the corpus builder, which constructs the "
            "witness in its sharpest form: an LA case and an LD case losing the same side, "
            "whose projections are then identical value for value",
        ],
        "unchanged": [
            "every gate threshold, including G9's 0 and G6's 0",
            "every gate's subject and every gate's outcome; G9 still names A3 and still FAILs",
            "the arms: no fifth arm is registered, because the bound says none can help",
            "the coordinate table, the absent-value table, A0, A1, A2, A3 and the probe gold",
            "the five corpora and every case in them; record_gold_cases() with no argument "
            "still emits research/p3-partial-observation-record-gold-v1/cases.jsonl byte for "
            "byte",
            "the 2026-08-21 freeze, its twin, amendments 001, 002 and 003 and their twins, "
            "all byte-identical",
        ],
        "numbers_this_amendment_moves": (
            "none. No gate's outcome, threshold, subject or count changes. The amendment adds "
            "reported fields --- the ceiling per corpus, the floor on G9 --- and the arms, "
            "corpora and gold are untouched, so every number the runner published before it "
            "publishes after it."
        ),
    },
    ],
    "claim_scope": CLAIM_SCOPE,
    "coordinates": list(COORDINATES),
    "absent_values": {
        name: (list(value) if isinstance(value, tuple) else getattr(value, "value", value))
        for name, value in ABSENT_VALUE.items()
    },
    "absence_reading_in_compare_meaning": dict(ABSENCE_READING),
    "arms": list(ARM_ORDER),
    "mining_census_arms": list(MINING_ARM_ORDER),
    "candidate_arms": list(CANDIDATE_ARM_ORDER),
    "completion_witness_prefix": COMPLETION_WITNESS_PREFIX,
    "decisiveness_rule_marker": DECISIVENESS_RULE_MARKER,
    "canonicalisation": {
        "bookkeeping_fields_stripped": list(CANONICAL_BOOKKEEPING_FIELDS),
        "open_vocabulary_fields_relabelled": list(OPEN_VOCABULARY_FIELDS),
        "closed_vocabulary_fields_relabelled": list(CLOSED_VOCABULARY_FIELDS),
        "role_structure_fields_relabelled": list(CANONICAL_ROLE_FIELDS),
        "absent_token": CANONICAL_ABSENT_TOKEN,
        "left_right_swap_allowed": True,
        "absent_values_are_never_relabelled": True,
        "field_census": canonicalisation_field_census(),
    },
    "probe_gold_derivation_rule": PROBE_GOLD_DERIVATION_RULE,
    "sides_per_redactable_pair": list(SIDES),
    "intact_sources": dict(INTACT_SOURCES_AS_FROZEN),
    "intact_roles": dict(INTACT_ROLE),
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
    provenance: dict[str, dict[str, Any]] = {}
    probes: dict[str, tuple[ProbeCase, ...]] = {}
    sources: dict[str, Any] = {}
    for corpus_id, relative in INTACT_SOURCES.items():
        path = repo_root / relative
        cases = load_jsonl(path)
        intact_pairs[corpus_id] = _intact_pairs(cases)
        provenance[corpus_id] = gold_provenance(cases)
        if corpus_id in PROBE_OF:
            probes[PROBE_OF[corpus_id]] = build_probe(cases, PROBE_OF[corpus_id])
        sources[corpus_id] = {
            "path": relative,
            "n_cases": len(cases),
            "role": INTACT_ROLE[corpus_id],
            "declared_gold_rules": list(provenance[corpus_id]["declared_rules"]),
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
            "gold_provenance": provenance[corpus_id],
            "by_arm": assess_corpus(corpus_id, ledger),
            "harm_vs_current": {
                arm: harm_against_current(scored, arm) for arm in CANDIDATE_ARM_ORDER
            },
            "exact_agreement_with_gold": {
                arm: exact_agreement_with_gold(scored, arm) for arm in ARM_ORDER
            },
            "exact_agreement_where_the_arm_can_fire": {
                arm: exact_agreement_where_the_arm_can_fire(scored, arm) for arm in ARM_ORDER
            },
            "mining_census": mining_census(scored),
            "mining_census_a3": mining_census(scored, arms=(ARM_DECISIVE,)),
            "identifiability_ceiling": identifiability_ceiling(pairs),
            "arm_disagreement": {
                arm: arm_disagreement(scored, ARM_DECISIVE, arm)
                for arm in (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)
            },
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
            "gold_provenance": {
                "declared_rules": [PROBE_GOLD_DERIVATION_RULE],
                "n_cases_declaring_a_rule": len(pairs),
                "n_cases": len(pairs),
                "rules_naming_completion_invariance": [],
                "gold_derived_by_completion_invariance": False,
                "note": (
                    "probe gold is fixed by the freeze, not derived from the completions. It "
                    "is UNRESOLVED on every probe case, so an arm that abstains "
                    "unconditionally is right on all of them; these corpora cannot separate "
                    "an abstaining arm from a decisiveness-aware one, and A0 answers none of "
                    "them correctly, so they carry no harm denominator either."
                ),
            },
            "harm_vs_current": {
                arm: harm_against_current(scored, arm) for arm in CANDIDATE_ARM_ORDER
            },
            "exact_agreement_with_gold": {
                arm: exact_agreement_with_gold(scored, arm) for arm in ARM_ORDER
            },
            "exact_agreement_where_the_arm_can_fire": {
                arm: exact_agreement_where_the_arm_can_fire(scored, arm) for arm in ARM_ORDER
            },
            "identifiability_ceiling": identifiability_ceiling(pairs),
            "arm_disagreement": {
                arm: arm_disagreement(scored, ARM_DECISIVE, arm)
                for arm in (ARM_CURRENT, ARM_ASYMMETRIC, ARM_STRICT)
            },
        }
        if pairs:
            ledger = ledger_from_scored(probe_id, scored)
            entry["by_arm"] = assess_corpus(probe_id, ledger)
            entry["mining_census"] = mining_census(scored)
            entry["mining_census_a3"] = mining_census(scored, arms=(ARM_DECISIVE,))
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
            entry["mining_census_a3"] = mining_census(())
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
    a3_failures = [
        row
        for corpus_id in (*INTACT_ORDER, PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC)
        for row in corpora[corpus_id]["mining_census_a3"]["failures"]
    ]
    gates["G5_MINING_YIELD"] = {
        "outcome": _worst([a_outcome, b_outcome]).value,
        "census_arms": list(MINING_ARM_ORDER),
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
        "c_arm_added_by_amendment_002": {
            "arm_id": ARM_DECISIVE,
            "n_failures": len(a3_failures),
            "n_demanding_a_missing_coordinate": sum(
                1 for row in a3_failures if row["demands_a_coordinate_orion_lacks"]
            ),
            "counted_towards_the_outcome": False,
            "note": (
                "reported, not scored. G5's outcome is a published finding about the three "
                "arms frozen before amendment 002; a fourth arm may not move it silently. If "
                "this count is ever non-zero the finding has changed and this field says so."
            ),
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

    a3_by_corpus: dict[str, Any] = {}
    for corpus_id in INTACT_ORDER:
        entry = corpora[corpus_id]
        harm = entry["harm_vs_current"][ARM_DECISIVE]
        # Amendment 004. ``.get`` rather than ``[...]``: the ceiling is a property
        # of the pairs, and a caller that assembles a corpus payload without them
        # should get a gate that says the floor is unknown, not a KeyError that
        # reads like a bug in the gate.
        ceiling = entry.get("identifiability_ceiling")
        a3_by_corpus[corpus_id] = {
            **harm,
            "pairs_where_a3_could_fire": entry["one_sided_absence_census"][
                "n_pairs_with_a_one_sided_absence"
            ],
            "evidence": independent_harm_evidence(entry, ARM_DECISIVE),
            "harm_floor": (
                None
                if ceiling is None
                else int(
                    ceiling[
                        "harm_floor_for_an_arm_that_commits_no_false_merge_and_no_false_split"
                    ]
                )
            ),
            "undecidable_orbits": (
                None if ceiling is None else int(ceiling["n_undecidable_orbits"])
            ),
        }
    a3_destroyed = sum(int(row["correct_answers_destroyed"]) for row in a3_by_corpus.values())
    a3_changed = sum(int(row["decisions_changed"]) for row in a3_by_corpus.values())
    a3_repaired = sum(int(row["wrong_answers_repaired"]) for row in a3_by_corpus.values())
    independent = sorted(
        corpus_id
        for corpus_id, row in a3_by_corpus.items()
        if row["evidence"]["supplies_independent_evidence"]
    )
    destroying = sorted(
        corpus_id
        for corpus_id, row in a3_by_corpus.items()
        if int(row["correct_answers_destroyed"]) > 0
    )
    destroying_independently = [
        corpus_id for corpus_id in destroying if corpus_id in independent
    ]
    # A partial sum would be a floor over some of the corpora reported as a floor
    # over all of them, which is the substitution this lane exists to prevent. If
    # any corpus could not be measured the total is withheld.
    floors = [row["harm_floor"] for row in a3_by_corpus.values()]
    a3_floor = None if any(value is None for value in floors) else sum(int(v) for v in floors)
    at_the_floor = a3_floor is not None and a3_destroyed == a3_floor
    if a3_destroyed > 0:
        a3_outcome = Outcome.FAIL
        a3_detail = (
            f"A3 destroyed {a3_destroyed} correct answers across the intact corpora, on "
            f"{destroying}; of those, {destroying_independently or 'none'} supplies gold that "
            "is not derived by the criterion A3 decides by. The decisiveness-aware repair is "
            "unsafe on measured evidence: it is a strict improvement on A1, which destroys "
            "more on the same pairs, and it is not free"
        )
        if at_the_floor:
            a3_detail += (
                f". Amendment 004: {a3_floor} is the floor, not a defect. On those corpora "
                "gold is not a function of the projections --- cases whose projections are "
                "the same evidence carry different gold, because the value that decides is "
                "the one the extraction destroyed --- so no rule reading only the "
                "projections is right on both members of such a pair. On every one of them "
                "gold carries both COMPATIBLE and a separation, so a determinate answer is "
                "a false merge or a false split and the only answer that is neither destroys "
                "the answer A0 gets right there. A3 pays exactly that and no more; the gate "
                "still fails, because a floor above zero is a fact about the evidence and "
                "not a licence to move a threshold"
            )
    elif not independent:
        a3_outcome = Outcome.CANNOT_CHECK
        a3_detail = (
            f"A3 destroyed 0 correct answers and repaired {a3_repaired}, but no intact corpus "
            "supplies independent evidence for that zero: the three corpora frozen on "
            "2026-08-21 have no one-sided absence for A3 to fire on, and "
            "INTACT_HARM_SYNTHETIC derives its gold by the completion-invariance criterion A3 "
            "decides by, so A3 agrees with it by construction. The zero is not a demonstration "
            "of safety and may not be cited as one"
        )
    else:
        a3_outcome = Outcome.PASS
        a3_detail = (
            f"A3 destroyed 0 correct answers, with independent evidence from {independent}"
        )
    gates["G9_HARM_A3"] = {
        "outcome": a3_outcome.value,
        "decisions_changed": a3_changed,
        "correct_answers_destroyed": a3_destroyed,
        "wrong_answers_repaired": a3_repaired,
        "harm_floor_for_any_candidate_visible_rule": a3_floor,
        "a3_harm_is_at_the_floor": at_the_floor,
        "floor_note": (
            "the smallest number of correct answers a rule reading only the projections can "
            "destroy on these corpora while committing no false merge and no false split. It "
            "is computed from the corpora's own cases, not from A3: cases whose projections "
            "are the same evidence up to bookkeeping, a consistent renaming of opaque ids and "
            "a left/right swap, but whose gold differs, cannot both be answered correctly by "
            "any such rule. The threshold is not moved. A gate that relaxed because the floor "
            "turned out to be above zero would be the relabelling this repository keeps "
            "finding; what the floor changes is what the FAIL means, not whether it fails"
        ),
        "identifiability_ceiling": {
            corpus_id: corpora[corpus_id].get("identifiability_ceiling")
            for corpus_id in INTACT_ORDER
        },
        "corpora_supplying_independent_evidence": independent,
        "corpora_where_a3_destroyed_a_correct_answer": destroying,
        "corpora_where_a3_destroyed_a_correct_answer_on_independent_gold": (
            destroying_independently
        ),
        "vacuous_or_circular": not independent,
        "by_corpus": a3_by_corpus,
        "detail": a3_detail,
    }

    a3_probe: dict[str, Any] = {}
    a3_rates: list[Outcome] = []
    threshold = float(GATES["G10_BENEFIT_A3"]["max_violation_rate"])
    for probe_id in (PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC):
        by_arm = corpora[probe_id]["by_arm"]
        rate = _over_resolution_rate(by_arm, ARM_DECISIVE) if by_arm else None
        row: dict[str, Any] = {
            "violation_rate": rate,
            "violation_rate_by_arm": {
                arm: (_over_resolution_rate(by_arm, arm) if by_arm else None)
                for arm in ARM_ORDER
            },
            "disagreement_with_a1": corpora[probe_id]["arm_disagreement"][ARM_ASYMMETRIC],
        }
        if rate is None:
            row["outcome"] = Outcome.CANNOT_CHECK.value
            a3_rates.append(Outcome.CANNOT_CHECK)
        else:
            outcome = Outcome.PASS if rate <= threshold else Outcome.FAIL
            row["outcome"] = outcome.value
            a3_rates.append(outcome)
        a3_probe[probe_id] = row
    separating = sorted(
        corpus_id
        for corpus_id in (*INTACT_ORDER, PROBE_DERIVATION, PROBE_HELDOUT_REAL, PROBE_HELDOUT_SYNTHETIC)
        if corpora[corpus_id]["arm_disagreement"][ARM_ASYMMETRIC]["n_differing"] > 0
    )
    separating_independently = sorted(
        corpus_id
        for corpus_id in separating
        if not gold_is_the_arms_own_criterion(corpora[corpus_id], ARM_DECISIVE)
    )
    gates["G10_BENEFIT_A3"] = {
        "outcome": _worst(a3_rates).value,
        "threshold": threshold,
        "by_probe": a3_probe,
        "corpora_separating_a3_from_a1": separating,
        "corpora_separating_a3_from_a1_on_gold_not_derived_by_the_criterion_a3_uses": (
            separating_independently
        ),
        "separation_from_a1_on_independent_gold": {
            corpus_id: corpora[corpus_id]["arm_disagreement"][ARM_ASYMMETRIC]
            for corpus_id in separating_independently
        },
        "detail": (
            "A3 abstains everywhere the frozen probe gold says abstention is right, so it "
            "keeps the benefit A1 was reaching for. A1 and A2 score the same 0.0 there, "
            f"because probe gold is UNRESOLVED on every probe case: {separating} "
            "separate A3 from A1 at all, and "
            f"{separating_independently or 'no corpus'} separates them on gold not derived "
            "by the criterion A3 decides by."
        ),
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
    "CANNOT_CHECK on emptiness. Amendment 002 builds the arm that defect points at --- "
    "A3_decisive_absence_only, which abstains only where the admissible completions of the "
    "absence disagree --- and then declines to certify it. Under amendment 002 A3 destroyed no "
    "correct answer on any corpus and repaired nine of A0's, but every one of those zeros was "
    "either structural (the three symmetric atlases give A3 nothing to fire on) or circular "
    "(the harm corpus derives its gold by A3's own criterion), so G9_HARM_A3 ran CANNOT_CHECK. "
    "Amendment 003 supplies the denominator amendment 002 judged unbuildable. What a one-sided "
    "absence underdetermines is the inference a procedure reading only the projections may "
    "draw, not the relation between the two source statements, which is fixed by the sources: "
    "a projection's silence is a fact about ORION's extraction. INTACT_RECORD_GOLD is built on "
    "that distinction --- gold is the relation between two fully stated source records, and the "
    "projections carry an extraction loss --- and over it A3 is measured rather than assumed. "
    "It destroys 9 of the 17 correct answers it could have destroyed, against A1's 17 of 17, "
    "so A3 is a strict improvement on A1 and is not free. G9_HARM_A3 is a FAIL on evidence "
    "instead of a CANNOT_CHECK on circularity, and the zero it could not earn is not reachable "
    "by any honest corpus either: A3 abstains on every decisive one-sided absence, so wherever "
    "gold is determinate there and A0 is right, A3 must destroy that answer. Only a gold that "
    "is determinate exactly where the completions agree --- completion-invariance under another "
    "name --- could report otherwise. Amendment 004 settles what that FAIL means. Strip from a "
    "pair of projections everything gold does not read --- the bookkeeping fields, the identity "
    "of the opaque ids, the left/right orientation --- and nine pairs of INTACT_RECORD_GOLD's "
    "cases become the same evidence while their gold stays different, because what decides is "
    "the value the extraction destroyed. Gold is not a function of the projections there, so no "
    "rule reading only the projections is right on both members of such a pair: nine of the "
    "thirty-six cases are unanswerable, the reachable ceiling is 27 of 36, and A0_orion_current "
    "already reaches it. Each of the nine orbits carries both COMPATIBLE and a separation, so a "
    "determinate answer is a false merge or a false split and the only answer that is neither "
    "destroys the one answer A0 has right there. The harm floor is 9; A3 pays 9. G9_HARM_A3 "
    "keeps its threshold and its FAIL, and the FAIL is now labelled as a floor rather than as a "
    "defect a fifth arm could repair."
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
    "derived by exactly that criterion, so the comparison would be circular. Amendment 002 "
    "builds the rule anyway, as A3_decisive_absence_only, and keeps the warning: it does not "
    "read A3's number off that corpus. A1 and A2 are also indistinguishable on that corpus -- "
    "identical decision kinds on all 33 cases -- so A2's separate cost remains visible only on "
    "the three corpora frozen on 2026-08-21, where G7 is unchanged.",
    "A3_decisive_absence_only's zero harm is not a demonstration that A3 is safe, and "
    "G9_HARM_A3 refuses to report it as one. On INTACT_DERIVATION, INTACT_HELDOUT_REAL and "
    "INTACT_HELDOUT_SYNTHETIC A3 has no one-sided absence to fire on, so it is A0 exactly and "
    "its zero is the same structural zero G6 carried before amendment 001. On "
    "INTACT_HARM_SYNTHETIC A3 reproduces gold on all 33 cases, which is not a surprise and not "
    "a result: that corpus derives its gold by asking whether the relation is constant over "
    "the admissible completions of the absence, and that is A3's decision rule. Harm is a "
    "different question from accuracy in general -- it asks whether a decision A0 got right was "
    "moved, which no gold-derivation rule fixes -- but on a corpus where the candidate "
    "reproduces gold everywhere the two collapse: zero harm follows from a perfect score by "
    "arithmetic. Reporting that zero as safety would be the identity-dressed-as-a-measurement "
    "defect this lane exists to catch.",
    "A3 and gold_from_standard are different functions, which is why the circularity above is "
    "a fact about this corpus's coverage rather than about A3 being gold. They differ in their "
    "inner relation rule (compare_meaning, the system under test, against the builder's "
    "independently written precedence rule), in their completion set (two witnesses derived "
    "from the pair against three values from a frozen corpus vocabulary) and in their domain "
    "(A3 answers a pair with several one-sided absences; gold_from_standard raises). They "
    "disagree on a pair whose stated side uses a value outside that vocabulary. What no corpus "
    "in this repository does is exercise a difference: the harm corpus states every value from "
    "the vocabulary and has at most one absence per pair.",
    "The probe corpora cannot separate A3 from A1. Probe gold is UNRESOLVED on all 48 cases, "
    "so any arm that abstains unconditionally is right on all of them, and A1, A2 and A3 all "
    "abstain on all of them: every redaction the freeze admits silences the coordinate the "
    "decision turned on, so there is no probe case on which decisiveness-awareness would "
    "change an answer. A0 answers none of the 48 correctly, so the probe corpora carry no harm "
    "denominator either. A3's 0.0 over-resolution rate there says it keeps A1's intended "
    "benefit; it says nothing about A3 being better than A1.",
    "G9_HARM_A3's discharge clause named an intact corpus with one-sided absences whose gold "
    "is fixed by a rule that does not ask whether the completions agree, containing at least "
    "one partially observed pair A0 answers correctly. Amendment 002 judged that unbuildable, "
    "on the ground that under partial observation the relation is genuinely underdetermined so "
    "an independent gold would have to come from adjudicators rather than from a rule. That "
    "reasoning was wrong, and correcting it is amendment 003. Underdetermined is what the "
    "*inference* is: a procedure reading only the projections cannot separate the world in "
    "which the silence hides an agreement from the world in which it hides a difference. The "
    "*relation* between the two source statements is fixed by the sources, and a projection's "
    "silence is a fact about ORION's extraction of them. INTACT_DERIVATION already carries "
    "gold of exactly that kind: its MUSE cases state neither polarity nor modality on either "
    "side and their gold is COMPATIBLE anyway, because identity:upstream-coreference-edge "
    "reads the annotation and not the coordinates. INTACT_RECORD_GOLD makes that asymmetric.",
    "A3's harm on INTACT_RECORD_GOLD is not a property of that corpus, in exactly the sense in "
    "which A1's harm on INTACT_HARM_SYNTHETIC is not a property of that one. A3 returns "
    "UNRESOLVED on every pair whose one-sided absence is decisive, so on any such pair whose "
    "gold is determinate and which A0 already answers correctly it necessarily destroys a "
    "correct answer. G9 can therefore be passed non-vacuously only by a corpus whose partially "
    "observed pairs have determinate gold exactly where the completions agree -- which is the "
    "completion-invariance criterion in extension, whatever derivation rule the corpus "
    "declares, and which the runner now withholds on as "
    "GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE. G9's threshold of zero is "
    "unreachable on non-circular gold. That is a fact about the gate and the arm, not about "
    "the cases, and it is reported rather than repaired: the gate keeps its threshold and "
    "fails.",
    "The 9 answers A3 destroys on INTACT_RECORD_GOLD are ones A0 gets right by a reading the "
    "freeze calls wrong. On eight of the nine coordinates compare_meaning reads a one-sided "
    "absence as agreement, so where the records agree it lands on the record's answer; on "
    "modality it reads absence as a distinct value, so where the records differ it lands on "
    "the record's answer. Destroying an answer that was right for the wrong reason is still "
    "destroying a right answer -- that is what a harm gate measures, and the alternative, "
    "scoring A0's reasons rather than its outputs, is not available to a gate that compares "
    "two arms' decisions. The corpus carries both directions of every coordinate for this "
    "reason: keeping the cells where A0 is right and dropping the ones where it is wrong, or "
    "the reverse, would be choosing cases by their effect on the gate, and the builder refuses "
    "a corpus missing either half.",
    "On INTACT_RECORD_GOLD A3 destroys 9 correct answers and A1 destroys 17, over the same 17 "
    "pairs and the same gold. That is the first measurement in this study that separates the "
    "two candidate repairs on gold neither of them wrote: they differ on 8 pairs and A3 is "
    "right on all 8. It says A3 is the better of two rules. It says nothing about either being "
    "safe -- G9 carries A3's harm, and G9 fails.",
    "On INTACT_RECORD_GOLD A0_orion_current commits 8 false merges and 1 false split, the "
    "first of either on any intact corpus in this study. That is not a contradiction of the "
    "published finding that ORION commits zero false merges and zero false splits on every P3 "
    "atlas: INTACT_RECORD_GOLD is not one of those atlases, and the decisions in question are "
    "the same ones the probe already scores as over-resolution. What changes is the gold "
    "semantics. Where gold is UNRESOLVED on a partially observed pair, merging it is an "
    "over-resolution; where gold is the relation between two source records and stays "
    "determinate through the extraction loss, the identical decision is a false merge. The "
    "eight-to-one split is the absence-reading table restated: the eight coordinates "
    "compare_meaning reads merge-ward produce the false merges on records that differ, and "
    "modality, which it reads as a distinct value, produces the false split on records that "
    "agree.",
    "INTACT_RECORD_GOLD is synthetic. Its source records are a frozen table the builder emits, "
    "not an upstream expert corpus, because the upstream corpora the public-reference builder "
    "draws on are not reachable from this environment. It establishes what a "
    "decisiveness-aware abstention costs when gold is anchored outside the projections, on "
    "pairs of this shape. It establishes nothing about how often scientific extraction drops a "
    "coordinate on one side only, and no accuracy, false-merge, false-split or superiority "
    "number over it is evidence about ORION's competence.",
    "INTACT_HARM_SYNTHETIC is synthetic. It establishes what compare_meaning does with a "
    "one-sided absence and what an abstain-on-asymmetry repair costs on pairs of that shape. It "
    "establishes nothing about how often scientific sources state a coordinate on one side only, "
    "and no accuracy, false-merge, false-split or superiority number over it is evidence about "
    "ORION's competence.",
    "The probe is a mechanical redaction of atlases that already ship here. It establishes a "
    "property of compare_meaning, not a frequency in scientific text. No accuracy, false-merge, "
    "false-split or superiority number over it is evidence about ORION's competence.",
    "A3's nine destroyed answers on INTACT_RECORD_GOLD are a floor and not a defect, and that "
    "is a bound rather than a defence of A3. Nine pairs of that corpus's cases are the same "
    "evidence once bookkeeping, the identity of the opaque ids and the left/right orientation "
    "are stripped --- none of which gold reads --- and carry different gold, so gold there is "
    "not a function of the projections. Any rule reading only the projections answers one "
    "relation for both members and is wrong on one of them; on each orbit gold carries both "
    "COMPATIBLE and a separation, so the only answer that is neither a false merge nor a false "
    "split is UNRESOLVED, which destroys the one answer A0 has right. What this licenses is "
    "narrow: it says the search for a fifth arm that beats 9 while keeping A3's abstention is "
    "not hard but impossible, on pairs of this shape. It does not say A3 is safe, it does not "
    "move G9's threshold, and it is not evidence about scientific text --- the corpus is "
    "synthetic and the bound is a bound over it.",
    "The floor is 9 and not 8 or 17 because of what the corpus contains, so it moves with the "
    "corpus. It counts orbits on which INTACT_RECORD_GOLD carries conflicting gold, and that "
    "corpus was built to carry one per coordinate. A corpus with more coordinates in conflict "
    "would have a higher floor and one with fewer a lower one, which is why the runner computes "
    "it from the cases rather than quoting it, and why a corpus edited to drop the conflicting "
    "strata lowers the floor to zero and is refused for circularity in the same breath.",
    "A rule that reduces the harm without keeping the benefit is not a repair, and one exists: "
    "decide on the coordinates observed on both sides and ignore the rest --- the record "
    "standard's precedence order applied to the shared observed frame. It destroys 1 correct "
    "answer on INTACT_RECORD_GOLD instead of A3's 9, and it buys that by never abstaining, so "
    "its P3.OVERRESOLVED_UNRESOLVED_CASE violation rate is 1.0 on all three probe corpora "
    "where G10 requires 0.0. It is A0 with a merge-ward modality reading, which is why it is "
    "reported here as the arithmetic of the trade-off rather than registered as an arm.",
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
    "ARM_DECISIVE",
    "ARM_ORDER",
    "ARM_STRICT",
    "AMENDMENT_DOCUMENT",
    "AMENDMENT_TWIN",
    "AMENDMENT_002_DOCUMENT",
    "AMENDMENT_002_TWIN",
    "AMENDMENT_003_DOCUMENT",
    "AMENDMENT_003_TWIN",
    "AMENDMENT_004_DOCUMENT",
    "AMENDMENT_004_TWIN",
    "CANDIDATE_ARM_ORDER",
    "CANONICAL_ABSENT_TOKEN",
    "CANONICAL_BOOKKEEPING_FIELDS",
    "CANONICAL_ROLE_FIELDS",
    "CLOSED_VOCABULARY_FIELDS",
    "OPEN_VOCABULARY_FIELDS",
    "CANDIDATE_COORDINATE",
    "COMPLETION_WITNESS_PREFIX",
    "COORDINATES",
    "DECISIVENESS_RULE_MARKER",
    "MINING_ARM_ORDER",
    "PROBE_GOLD_DERIVATION_RULE",
    "FREEZE_DOCUMENT",
    "FREEZE_TWIN",
    "FROZEN_PARAMETERS",
    "FreezeViolation",
    "INTACT_DERIVATION",
    "INTACT_HARM_SYNTHETIC",
    "INTACT_HELDOUT_REAL",
    "INTACT_HELDOUT_SYNTHETIC",
    "INTACT_ORDER",
    "INTACT_RECORD_GOLD",
    "INTACT_ROLE",
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
    "admissible_completions",
    "arm_decisive_absence_only",
    "arm_disagreement",
    "build_probe",
    "canonical_pair_form",
    "canonicalisation_field_census",
    "construction_precondition",
    "derive_verdicts",
    "discriminating_coordinates",
    "exact_agreement_where_the_arm_can_fire",
    "exact_agreement_with_gold",
    "gold_is_the_arms_own_criterion",
    "gold_provenance",
    "independent_harm_evidence",
    "evaluate_gates",
    "frozen_digest",
    "harm_against_current",
    "identifiability_ceiling",
    "main",
    "mining_census",
    "observed",
    "one_sided_absence_census",
    "overall_outcome",
    "probe_case_json",
    "projection_orbits",
    "redactable_coordinates",
    "run_campaign",
    "score_pairs",
    "verify_against_twin",
]
