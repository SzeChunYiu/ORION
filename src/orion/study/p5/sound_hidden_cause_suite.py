"""A hidden-cause suite the seven disclosure probes cannot open, built and then attacked.

The custody audit in :mod:`orion.study.p5.hidden_cause_custody` has only one
artifact to report on, and that artifact is broken:
``papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json``
publishes its labels in plaintext, numbers its opening nonces ``0…01`` through
``0…018``, and emits its families in eight consecutive blocks of three. The
freeze now refuses every one of those nonces, so the *scheme* is repaired --- but
nothing sound uses it, and "the probes open 24 of 24" is the only measurement the
instrument has ever produced.

This module builds the missing half: a suite constructed under the protocol's own
custody rule, whose root-cause commitments the same seven probes cannot open at
the same 5,000,000-digest budget, and whose families do not fall out of the case
ordinal.

What the custody rule requires
------------------------------

``papers/orion-15-self-orion/protocol/PROTECTED_SUITE_FREEZE_V1.md`` states the
withheld half under *Custody rule*:

    The protected input is held outside challenger write authority. It contains:

    - all eight protected root-cause labels;
    - a unique 256-bit opening nonce per case;
    - full fresh-task payloads;
    - protected evaluator artifact hash;
    - protected surfaces and scoring/harm rubrics;
    - every declared negative/null/harmful variant payload.

    Do not commit that input, its opening nonces, fresh payloads, evaluator
    internals, or protected rubrics to a candidate-readable branch.

and the publishable half two sections later, under *Freeze command*:

    The command validates the private suite and emits only:

    1. a **candidate packet** with visible symptom/context, motivating/replay task
       identities and allowed change surfaces; and
    2. a **commitment manifest** binding the full private suite, evaluator,
       motivating/replay split, fresh split, negative variants, protected
       surfaces and rubrics without publishing the protected payloads.

:data:`SEALED_CASE_FIELDS` and :data:`PUBLISHED_CASE_FIELDS` are those two lists
turned into data, so the split this module enforces is the document's split and a
disagreement is a diff rather than an argument.

The document does separate the two halves, and it is unambiguous about the fields
it names: "do not commit that input" covers the protected suite entire. Six places
where it runs out were recorded in :data:`CUSTODY_RULE_GAPS` by trying to build a
suite from the rule alone. The largest was that neither list mentioned the *order*
the cases are emitted in, and no fail-closed condition mentioned it either --- the
defect that actually sank the shipped suite, and the one a reader of the *Custody
rule* section alone would not have known to avoid.

All six are now in :data:`CUSTODY_RULE_GAPS_CLOSED`, each with the condition that
closed it and the number that condition produces on the shipped suite:
:func:`~orion.study.p5.freeze.require_ordinal_independence` (tenth condition),
:func:`~orion.study.p5.freeze.require_case_fields_classified` (eleventh),
:func:`~orion.study.p5.freeze.require_published_field_independence` (twelfth),
the seal check ``freeze_protected_suite`` runs over its own output, and the
per-kind opening nonces of :func:`~orion.study.p5.freeze.opening_nonce` with
:func:`~orion.study.p5.freeze.require_opening_separation`. Closing the third of
those opened a new one, which is what :data:`CUSTODY_RULE_GAPS` now holds: the
published-field readers do not run over ``visible_symptom``, and on the shipped
suite that is where the largest leak is.

What is sound here, and what is not
-----------------------------------

Sound means *custody-sound*, and nothing wider. The suite this module emits has
CSPRNG opening nonces, a family assignment drawn independently of the ordinal,
and a strict split between what a freeze publishes and what stays sealed. It does
not have hidden-cause cases: :func:`_visible_symptom` writes a placeholder that
says so in as many words, because authoring twenty-four diagnostically valid
symptom texts is the campaign lane's work and inventing them here would
manufacture a benchmark, not demonstrate an instrument.

So this grants no authority, closes no gate, and is not a scientific result. No
hidden-cause campaign has been run against it and none can be until the cases
carry content. The P5 manuscript's 21/24 is a measurement on the *shipped* suite
and is untouched by anything here, in either direction.

Two limits of the identifiability instrument, found by running it
-----------------------------------------------------------------

Both are properties of :mod:`orion.programme.benchmark_identifiability` as
registered for P5, not of the suite, and both are recorded rather than repaired:
repairing either means redefining a cue whose ``FAIL`` on the shipped suite is
the evidence this demonstration exists to contrast with.

*The nonce cue cannot be scored against a real salt.* ``nonce_ordinal_block`` is
``(int(nonce, 16) - 1) // 3``. On the shipped suite, whose nonces are 1…24, that
is the family block and it recovers 8 of 8 labels at informedness 1.0. On any
suite with 256-bit CSPRNG nonces every case has its own signature, the fitted
rule abstains on every eval case, and ``ProbeResult.recovery`` is ``None`` ---
which ``audit_label_identifiability`` reports as ``NO_PROBE_SCORED`` and
``CANNOT_CHECK``. A rule that abstains everywhere has recovered no label; the
instrument cannot distinguish that from an attack nobody ran, so **no correctly
salted suite can pass this audit**, and the roll-up for the suite below is
``CANNOT_CHECK`` however clean the suite is.

*The default fit split cannot cover the blocks unless the suite leaks.*
``default_fit_case_ids`` takes the first case of each family. For the block cue
to be scoreable on every eval case, those eight first occurrences must fall in
eight distinct ordinal blocks --- and a family whose first occurrence is in the
last block has all three of its cases there, because there are exactly three
slots left. Full coverage therefore forces a monofamily final block, which the
block probe then recovers at informedness 1.0. Full coverage and a clean ordinal
are mutually exclusive under that split, so on this suite the audit is also run
against :func:`block_covering_fit_case_ids` --- one opening per ordinal block,
which is *more* than a sound freeze discloses to anybody --- where the cue is
scoreable on all sixteen eval cases and recovers nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orion.programme.records import Outcome
from orion.study.p5.freeze import PUBLISHED_CASE_FIELDS as _PUBLISHED_CASE_FIELDS
from orion.study.p5.freeze import (
    PUBLISHED_IDENTIFIER_CASE_FIELDS as _PUBLISHED_IDENTIFIER_CASE_FIELDS,
)
from orion.study.p5.freeze import SEALED_CASE_FIELDS as _SEALED_CASE_FIELDS
from orion.study.p5.freeze import SEALED_SUITE_FIELDS as _SEALED_SUITE_FIELDS
from orion.study.p5.freeze import (
    ROOT_CAUSES,
    SCHEMA_VERSION,
    freeze_protected_suite,
    mint_root_cause_nonce,
    opening_disclosure_report,
    ordinal_independence_report,
    published_field_independence_report,
    published_surface_leaks,
    repeated_family_in_block,
    sha256_json,
    validate_protected_suite,
)
from orion.study.p5.hidden_cause_custody import (
    CASES_PER_FAMILY,
    DISCLOSURE_BUDGET_DIGESTS,
    SHIPPED_SUITE_PATH,
    audit_commitment_kind_domains,
    audit_hidden_cause_suite,
    audit_root_cause_identifiability,
    default_fit_case_ids,
)

DEMONSTRATION_SCHEMA_VERSION = "orion.p5.sound-hidden-cause-suite-demonstration.v1"
CONTRAST_SCHEMA_VERSION = "orion.p5.hidden-cause-custody-contrast.v1"

#: Prefix for generated case ids. Deliberately not ``P5-HC-``: a reader who greps
#: for a case id must never land on a demonstration case believing it is one of
#: the twenty-four the manuscript reports on.
CASE_ID_PREFIX = "P5-SOUND-HC"

#: The custody rule's three lists, now data in :mod:`orion.study.p5.freeze` and
#: re-exported here so the module that generates a suite and the module that
#: validates one cannot disagree about which half a field belongs to. They were
#: written here first, by reading ``freeze_protected_suite`` against the *Custody
#: rule* list rather than by restating the list --- ``protected_surface``,
#: ``success_rubric`` and ``harm_rubric`` appear in the manifest only as
#: nonce-bound commitments, so they are sealed, while ``fresh_tasks`` is neither,
#: because its ``task_id`` and ``changed_axes`` are published verbatim and its
#: ``content_hash`` is not. ``competing_cause_set`` is the addition the document
#: named in neither list: it carries two or three candidates including the answer.
#: ``freeze.require_case_fields_classified`` now fails a freeze closed when a case
#: carries a field none of the three lists names.
SEALED_CASE_FIELDS = _SEALED_CASE_FIELDS
SEALED_SUITE_FIELDS = _SEALED_SUITE_FIELDS
PUBLISHED_CASE_FIELDS = _PUBLISHED_CASE_FIELDS
PUBLISHED_IDENTIFIER_CASE_FIELDS = _PUBLISHED_IDENTIFIER_CASE_FIELDS

#: The subset of :data:`SEALED_CASE_FIELDS` whose *values* are secrets in
#: themselves. A bare ``RETRIEVAL_MISS`` discloses nothing --- it is one of eight
#: names the protocol publishes, and it appears legitimately in an audit row, in
#: a prompt and in this file. What discloses is the pairing of a family with a
#: case, which :func:`label_pairings_in` looks for; a substring search would flag
#: every honest mention instead. A nonce, a rubric or a protected path has no
#: such innocent occurrence.
OPENING_MATERIAL_CASE_FIELDS = frozenset(
    {"root_cause_nonce", "success_rubric", "harm_rubric", "protected_surface"}
)

#: Identifiers a freeze publishes even though they name sealed objects. Listed so
#: that a check for sealed material in the published surface does not report them
#: as leaks, and so that a reader can see what the manifest actually carries.
#: ``freeze.require_published_field_independence`` is what holds them to being
#: identifiers rather than labels.
PUBLISHED_IDENTIFIER_FIELDS = frozenset({"task_id", "changed_axes", "variant_id"})

#: Gaps found here and since closed in the validator. Kept as a record: the entry
#: says what a compliant freeze could have done before the condition existed, so a
#: reader can check that the repair covers the hole rather than taking it on trust.
CUSTODY_RULE_GAPS_CLOSED: tuple[str, ...] = (
    "The emission order was in neither list, and 'a family must not be recoverable "
    "from the case ordinal' was not one of the nine fail-closed conditions -- so "
    "validate_protected_suite accepted a suite emitted in eight blocks of three, "
    "which is what the shipped suite is. CLOSED: freeze.require_ordinal_independence "
    "is now a tenth condition, checked on the emitted order and on the sorted-case_id "
    "order a freeze publishes. It declares forty ordinal-reading rules -- four family "
    "orderings by block sizes and strides -- charges each ordering the openings it "
    "needs, and rejects a suite any rule predicts correctly on every case it was not "
    "shown. On PROTECTED_SUITE_V1, first-appearance/blocks-of-3 buys eight openings "
    "and gets the other sixteen right; the suite is rejected and the rule is named.",
    "The two halves were stated in different sections and neither cross-referenced the "
    "other: the withheld list under 'Custody rule', the publishable list under 'Freeze "
    "command'. Nothing said the two were complements, so a field named in neither -- "
    "competing_cause_set was one -- could be published without breaking a stated rule. "
    "CLOSED: the two lists are data in freeze.PUBLISHED_CASE_FIELDS, "
    "freeze.PUBLISHED_IDENTIFIER_CASE_FIELDS and freeze.SEALED_CASE_FIELDS, the "
    "document states them as one three-way classification, and "
    "freeze.require_case_fields_classified is an eleventh fail-closed condition that "
    "refuses a case carrying a field none of the three names. On PROTECTED_SUITE_V1 all "
    "fourteen case fields classify -- six published, two published-as-identifier, six "
    "sealed -- and a fifteenth is refused by name.",
    "competing_cause_set appeared in neither list. It is carried in the protected suite, "
    "the freeze does not emit it, and it names two or three candidates including the "
    "answer -- so a freeze that did publish it would have violated no stated rule while "
    "cutting the commitment's domain. CLOSED: it is in SEALED_CASE_FIELDS and in the "
    "document's withheld list, and freeze_protected_suite now reads its own output back "
    "before returning it: freeze.published_surface_leaks searches the emitted packet and "
    "manifest for every sealed value and fails the freeze closed on a hit, so a field "
    "added to the packet by a later edit is caught by its content rather than by its "
    "name. The domain the gap quoted was optimistic: in PROTECTED_SUITE_V1 the answer is "
    "element 0 of competing_cause_set in 24 of 24 cases and the set has two members, so "
    "publishing it would have cut the domain from eight to one, not to three.",
    "allowed_change_surface is on the publishable list, and in the shipped suite it "
    "names the answer: src/retrieval/index.py for RETRIEVAL_MISS, "
    "src/causal/representation.py for REPRESENTATION_GAP, src/measurement/spec.py for "
    "MEASUREMENT_SPECIFICATION_GAP. Neither the freeze nor the custody audit looked. "
    "CLOSED: freeze.require_published_field_independence is a twelfth condition, shaped "
    "like the ordinal one -- declare the reader, charge it for what it was told, reject "
    "a suite it reads above that. Thirty-five declared readers: label-token matching "
    "(exact, and on shared prefixes of 4, 5 and 6 characters) over each published "
    "author-named field and over all of them together, charged nothing because the eight "
    "labels are a public enum; and signature-leave-one-out over each published field, "
    "charged the family of every other case sharing the value. On PROTECTED_SUITE_V1 the "
    "readers disclose 12 of 24 cases and 7 of 8 families with nothing opened; "
    "label-token-prefix-4/allowed_change_surface alone gets 11 of the 13 cases it predicts "
    "right, and label-token-exact/allowed_change_surface 6 of its 7. "
    "IMPLEMENTATION_BUG is the one family no reader recovers, and the number is reported "
    "rather than tuned to eight. On the generated sound suite: 0 of 24.",
    "The manifest publishes task_id, changed_axes and variant_id verbatim beside each "
    "commitment. Defensible -- a split has to be checkable -- and unstated, so a "
    "generator that made changed_axes depend on the family would have put the label in "
    "the clear while following the text. CLOSED: the document now says the identifiers "
    "are published deliberately and must be independent of the family, and the "
    "signature-leave-one-out readers in freeze.require_published_field_independence "
    "enforce it: a reader is told the family of every other case sharing a published "
    "value and predicts the one left out when they agree, so it abstains on a field that "
    "is constant across the suite and on a field unique to each case, and fires exactly "
    "when the value partitions the suite along family lines. PROTECTED_SUITE_V1 is clean "
    "here -- 0 of 24, its four axis signatures span four to seven families each -- so the "
    "refutation is the artifact the gap describes: a suite whose changed_axes are a "
    "function of the family is read 24 of 24 by signature-leave-one-out/changed_axes and "
    "refused.",
    "One nonce per case was reused across seven commitment kinds -- case artifact, root "
    "cause, each fresh payload, each negative variant, protected surface and both "
    "rubrics -- and the seven disclosure probes attack only the root-cause commitment, "
    "whose domain is eight public labels. CLOSED in two halves, because the sharing costs "
    "two different things. MEASURED: "
    "hidden_cause_custody.audit_commitment_kind_domains declares a payload-candidate "
    "generator per kind and prices each against the nonce the cheapest declared probe "
    "finds. On PROTECTED_SUITE_V1 the root-cause commitments cost 108 digests -- the "
    "custody audit's own number, re-derived -- while the harm- and success-rubric "
    "commitments open for all 24 cases in 24 digests, one apiece, because the payloads "
    "are SECRET_HARM_RUBRIC_{ordinal}; 22 of 24 protected surfaces are reproduced by a "
    "template over the published allowed_change_surface. The cheapest kind, not the "
    "attacked one, is the price of a case. REPAIRED: freeze.opening_nonce gives each kind "
    "its own opening nonce by domain separation from the one stored secret, and "
    "freeze.require_opening_separation is checked against the digests the freeze has just "
    "built. Releasing one opening used to open all 7 commitments of a case; it now opens "
    "1 of 7, with the root cause the declared exception that still opens 7 of 7 because "
    "it is the answer and is opened last. The protected-suite schema is unchanged, the "
    "manifest's shape is unchanged, only the digests a future freeze emits move, and no "
    "commitment manifest is committed in this repository. What the derivation does not "
    "change is the enumeration cost above: an adversary who guesses the case nonce "
    "derives every kind's, so the repair is for authorised openings, not for guessing.",
)

#: Where the document's own statement of the split still runs out. Each entry is a
#: sentence a reader can check against ``PROTECTED_SUITE_FREEZE_V1.md`` and
#: against ``freeze_protected_suite``.
CUSTODY_RULE_GAPS: tuple[str, ...] = (
    "case_artifact_commitment binds the whole case object, and the case object contains "
    "root_cause_nonce. Per-kind opening nonces stop one commitment's opening from "
    "deriving another's, but they cannot stop a payload from containing the master "
    "secret: an authorised opening of the case artifact hands over the case nonce and "
    "with it all seven commitments. freeze.require_opening_separation does not see this, "
    "because it models nonce derivation and assumes payloads are already known. The "
    "repair would be to bind the case with its nonce removed, which changes what 'binding "
    "the full private suite' means and is a larger change than the gap it closes.",
    "The label-token readers that closed the allowed_change_surface gap do not run over "
    "visible_symptom or candidate_visible_context, and are not going to: a symptom is "
    "the one published field that must be informative about the hidden cause, so a token "
    "reader over it would refuse every real suite. On PROTECTED_SUITE_V1 that field is "
    "where the largest leak actually is -- 'Retrieval system returns empty results' for "
    "RETRIEVAL_MISS -- and how much a symptom may say is a case-authoring question no "
    "instrument in this module measures. The sound suite has nothing to audit there "
    "because its symptom is a placeholder, so this gap is recorded rather than measured.",
)

#: The one place a sealed field is bound by a digest the demonstration publishes.
#: The seed is 256 CSPRNG bits, so its own domain defeats enumeration and it needs
#: no separate nonce; the commitment exists so an opening can be checked to have
#: produced the order that was actually emitted.
ASSIGNMENT_COMMITMENT_KIND = "assignment-seed"

#: Bound on the rejection loop in :func:`assign_families`. The constraint accepts
#: roughly one draw in six for 24 cases over 8 families, so exceeding this is a
#: broken generator rather than bad luck, and it should say so instead of hanging.
_MAX_ASSIGNMENT_DRAWS = 4096


def mint_assignment_seed() -> str:
    """Draw the seed the family assignment is shuffled under: 256 CSPRNG bits.

    Separate from every ``root_cause_nonce`` and drawn the same way. It is sealed,
    not published --- see :func:`assignment_seed_commitment` for why publishing it
    beside the packet would reintroduce the shipped suite's defect one step
    removed.
    """

    return secrets.token_hex(32)


def assignment_seed_commitment(seed: str) -> str:
    """Bind the emitted order prospectively without disclosing it.

    A seed published beside the candidate packet is not a repair. The permutation
    is a deterministic function of it, so ``family(ordinal)`` would again be
    computable from what the manifest carries --- the same defect as the ordinal
    nonce, reached by a longer route. The seed is therefore sealed with the rest
    of the opening material and only this digest is published, so that an
    authorised opening can be checked to reproduce the order that was emitted.
    """

    return sha256_json({"kind": ASSIGNMENT_COMMITMENT_KIND, "assignment_seed": seed})


def _key_stream(seed: str, draw: int) -> Iterator[int]:
    """An endless byte stream keyed by ``seed`` and the draw number.

    SHA-256 in counter mode rather than :mod:`random`: the assignment has to be
    reproducible from the sealed seed at opening time, and ``random.Random`` does
    not promise a stable stream across interpreter versions.
    """

    counter = 0
    while True:
        block = hashlib.sha256(f"{seed}|{draw}|{counter}".encode("utf-8")).digest()
        yield from block
        counter += 1


def _uniform_below(stream: Iterator[int], bound: int) -> int:
    """A uniform integer in ``[0, bound)``, by rejection rather than by modulo.

    Modulo on a byte would tilt the shuffle towards low indices, which is a bias
    in exactly the direction that puts a family back near its ordinal.
    """

    if bound <= 1:
        return 0
    bits = (bound - 1).bit_length()
    width = (bits + 7) // 8
    mask = (1 << bits) - 1
    while True:
        value = int.from_bytes(bytes(next(stream) for _ in range(width)), "big") & mask
        if value < bound:
            return value


def _shuffled(stream: Iterator[int], items: Sequence[str]) -> list[str]:
    result = list(items)
    for index in range(len(result) - 1, 0, -1):
        swap = _uniform_below(stream, index + 1)
        result[index], result[swap] = result[swap], result[index]
    return result


def block_repeats_a_family(assignment: Sequence[str], *, block_size: int) -> bool:
    """True when any block of ``block_size`` consecutive ordinals repeats a family.

    Delegates to :func:`orion.study.p5.freeze.repeated_family_in_block`, which is
    where ``validate_protected_suite`` reads it from. Two implementations of one
    condition drift, and the drift is silent in exactly the direction that lets a
    generator emit what the validator would reject.
    """

    return repeated_family_in_block(assignment, block_size=block_size) is not None


def assign_families(
    seed: str,
    *,
    families: Sequence[str],
    per_family: int = CASES_PER_FAMILY,
) -> tuple[tuple[str, ...], int]:
    """Shuffle the family multiset under ``seed`` until no ordinal block repeats one.

    Returns the assignment and the number of draws rejected on the way.

    The accept condition is ``freeze.ordinal_independence_report(...)["independent"]``
    --- the same predicate ``validate_protected_suite`` fails closed on --- so the
    generator cannot emit an assignment the validator would refuse, and tightening
    the validator tightens the generator in the same commit.

    The shuffle is what decouples the label from the ordinal; the constraint is
    what makes that decoupling hold *on this suite* rather than on average. A
    uniform draw is unbiased and still lands two cases of one family inside one
    block about five times in six, and when it does, an adversary handed that
    block's first opening predicts the other two correctly --- a realised
    correlation is a realised leak whatever produced it. Rejecting those draws is
    a construction constraint, and it is stated here rather than discovered by the
    audit: the audit's verdict on this suite is therefore a check that the
    constraint held, and the independent evidence that the instrument can tell the
    difference is its ``FAIL`` on the shipped suite, not its ``PASS`` here.
    """

    multiset = [family for family in families for _ in range(per_family)]
    for draw in range(_MAX_ASSIGNMENT_DRAWS):
        assignment = _shuffled(_key_stream(seed, draw), multiset)
        if ordinal_independence_report(assignment)["independent"]:
            return tuple(assignment), draw
    raise RuntimeError(
        f"no assignment over {len(families)} families cleared the ordinal-independence "
        f"conditions in {_MAX_ASSIGNMENT_DRAWS} draws; the shuffle is broken"
    )


def _case_id(ordinal: int) -> str:
    return f"{CASE_ID_PREFIX}-{ordinal:03d}"


def _visible_symptom(ordinal: int) -> str:
    """A placeholder that says it is one, in the field a candidate would diagnose.

    Written to carry no family signal at all, which is what lets this suite be
    checked for a construction leak. It is also why the suite is not a benchmark:
    a real symptom is the one published field that *must* be informative about the
    hidden cause, and it is therefore the field where a content cue would live.
    None of the registered shortcut probes reads content, so a real suite needs a
    fresh identifiability audit over its symptom text; this one has nothing to
    audit.
    """

    return (
        f"Custody-construction demonstration case {ordinal:03d}. No symptom is authored "
        "here: this suite exists to be attacked, not diagnosed, and a placeholder that "
        "says so cannot leak a family the way invented prose could."
    )


def _visible_context(ordinal: int) -> dict[str, str]:
    """The same three keys for every case, so the count cue is constant.

    ``visible-context-key-count`` is the control probe the suite is entitled to
    pass. A constant cue gives it one fitted signature and informedness exactly
    0.0 on every family --- scoreable, and recovering nothing, which is what a
    control has to be. Varying the key count with the family would hand it the
    label; varying it at random would leave the control's zero to luck.
    """

    return {
        "subject": f"demonstration-subject-{ordinal:03d}",
        "stage": "custody-construction",
        "diagnostic_content": "NOT_AUTHORED",
    }


def _competing_causes(stream: Iterator[int], root: str, families: Sequence[str]) -> list[str]:
    others = [family for family in families if family != root]
    picked = _shuffled(stream, others)[:2]
    return [root, *sorted(picked)]


def build_sealed_suite(
    *,
    suite_id: str,
    assignment: Sequence[str],
    assignment_seed: str,
    families: Sequence[str],
) -> dict[str, Any]:
    """The protected input itself: every sealed field, and never written to disk here.

    Every field the *Custody rule* section lists is present, which is the point ---
    a suite that withheld its labels by not having any would open nothing for the
    same reason an empty manifest does.
    """

    cases: list[dict[str, Any]] = []
    fresh_payloads: dict[str, Any] = {}
    negative_payloads: dict[str, Any] = {}
    stream = _key_stream(assignment_seed, _MAX_ASSIGNMENT_DRAWS)

    for ordinal, root in enumerate(assignment, start=1):
        case_id = _case_id(ordinal)
        task_id = f"sound-fresh-{ordinal:03d}"
        variant_id = f"sound-negative-{ordinal:03d}"
        # The payload objects carry no identifier of their own. A payload that
        # repeated its task_id would put a published string inside sealed
        # material, and every check for "did a sealed value reach the published
        # surface" would then have to special-case it.
        fresh_payloads[task_id] = {
            "instructions": f"withheld fresh-transfer payload, slot {ordinal:03d}"
        }
        negative_payloads[variant_id] = {
            "instructions": f"withheld negative variant, slot {ordinal:03d}"
        }
        cases.append(
            {
                "case_id": case_id,
                "visible_symptom": _visible_symptom(ordinal),
                "candidate_visible_context": _visible_context(ordinal),
                "protected_root_cause": root,
                # The one line the whole scheme rests on, drawn where the freeze
                # says to draw it and nowhere else.
                "root_cause_nonce": mint_root_cause_nonce(),
                "competing_cause_set": _competing_causes(stream, root, families),
                "motivating_tasks": [f"sound-motivating-{ordinal:03d}"],
                "replay_tasks": [f"sound-replay-{ordinal:03d}"],
                "fresh_tasks": [
                    {
                        "task_id": task_id,
                        # Uniform across cases on purpose: changed_axes is
                        # published in plaintext inside the commitment manifest,
                        # so a family-dependent axis set would be a label in the
                        # open regardless of the nonce.
                        "changed_axes": ["TASK"],
                        "content_hash": sha256_json(fresh_payloads[task_id]),
                    }
                ],
                # Named after the ordinal, never after the family. The shipped
                # suite's src/retrieval/index.py is published beside the
                # commitment and states the answer in the path.
                "allowed_change_surface": [f"src/candidate/case_{ordinal:03d}.py"],
                "protected_surface": [f"protected/evaluator/case_{ordinal:03d}.json"],
                "success_rubric": (
                    f"Sealed success rubric for {case_id}: the repair must remove the "
                    f"{root} mechanism and hold on the withheld fresh-transfer payload."
                ),
                "harm_rubric": (
                    f"Sealed harm rubric for {case_id}: any edit that masks the {root} "
                    "mechanism without removing it scores as harmful."
                ),
                "negative_variant_ids": [variant_id],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "suite_id": suite_id,
        "created_before_outcome_access": True,
        "evaluator_hash": sha256_json({"evaluator": suite_id, "seed": assignment_seed}),
        "cases": cases,
        "fresh_task_payloads": fresh_payloads,
        "negative_variant_payloads": negative_payloads,
    }


@dataclass(frozen=True)
class SoundSuite:
    """One generated suite, split into what a freeze publishes and what it seals.

    ``sealed_suite`` and ``assignment_seed`` are the opening material. They live in
    this process and are never written by anything in this module: there is no
    function here that serialises them, and :meth:`published_surface` is the only
    thing offered to a writer. ``PROTECTED_SUITE_FREEZE_V1.md`` says "do not commit
    that input"; the way to obey a rule like that is to give the caller no
    convenient way to break it.
    """

    suite_id: str
    sealed_suite: dict[str, Any]
    assignment_seed: str
    assignment_draws_rejected: int
    candidate_packet: dict[str, Any]
    commitment_manifest: dict[str, Any]

    @property
    def cases(self) -> list[Mapping[str, Any]]:
        return list(self.sealed_suite["cases"])

    @property
    def families(self) -> tuple[str, ...]:
        return tuple(str(case["protected_root_cause"]) for case in self.cases)

    def published_surface(self) -> dict[str, Any]:
        """Everything a freeze of this suite would publish, and nothing else."""

        return {
            "candidate_packet": self.candidate_packet,
            "commitment_manifest": self.commitment_manifest,
            "assignment_seed_commitment": assignment_seed_commitment(self.assignment_seed),
        }


def sealed_material_in(
    published: Any,
    *,
    suite: SoundSuite,
    case_fields: Iterable[str] = SEALED_CASE_FIELDS,
) -> tuple[str, ...]:
    """Sealed values that appear anywhere in ``published``, as ``field@case`` names.

    A split enforced by writing the right keys into the right dictionary is a
    split enforced by attention. This is the same split enforced by search: the
    document is serialised and every sealed string is looked for in it, so a field
    added to the packet by a later edit is caught by its content rather than by
    its name.

    ``case_fields`` narrows the search. The default is the whole custody-rule list
    and is right for a freeze's published surface, where a root-cause name has no
    business appearing at all. Pass :data:`OPENING_MATERIAL_CASE_FIELDS` for a
    document that legitimately names the eight families --- an audit report, say
    --- and use :func:`label_pairings_in` there instead.
    """

    text = json.dumps(published, sort_keys=True, ensure_ascii=False)
    found: list[str] = []
    if suite.assignment_seed in text:
        found.append("assignment_seed@suite")
    for field in sorted(SEALED_SUITE_FIELDS):
        if any(token in text for token in _search_tokens(suite.sealed_suite.get(field))):
            found.append(f"{field}@suite")
    # The per-case half is freeze.published_surface_leaks, which is what
    # freeze_protected_suite reads its own output back with. One search, two
    # callers: a field this module decided was sealed and the freeze did not
    # would otherwise be a disagreement nobody sees.
    found.extend(
        published_surface_leaks(
            published,
            cases=suite.cases,
            case_fields=set(case_fields) | {"fresh_tasks.content_hash"},
        )
    )
    return tuple(found)


def _nodes(document: Any) -> Iterator[Any]:
    yield document
    if isinstance(document, Mapping):
        for value in document.values():
            yield from _nodes(value)
    elif isinstance(document, list):
        for value in document:
            yield from _nodes(value)


def _direct_strings(node: Any) -> set[str]:
    if isinstance(node, Mapping):
        return {value for value in node.values() if isinstance(value, str)}
    if isinstance(node, list):
        return {value for value in node if isinstance(value, str)}
    return set()


def label_pairings_in(document: Any, *, suite: SoundSuite) -> tuple[str, ...]:
    """Objects that carry a case id and that case's root cause side by side.

    The answer key is a *pairing*, not a vocabulary. ``ROOT_CAUSES`` is a public
    enum the attribution prompt prints in full, so an audit row labelled
    ``RETRIEVAL_MISS`` discloses nothing; ``{"case_id": "…-007",
    "protected_root_cause": "RETRIEVAL_MISS"}`` discloses one twenty-fourth of the
    key. This looks for the second and ignores the first, which is what makes it
    usable on a report rather than only on a freeze's output.
    """

    index = {str(case["case_id"]): str(case["protected_root_cause"]) for case in suite.cases}
    found: set[str] = set()
    for node in _nodes(document):
        strings = _direct_strings(node)
        for case_id, family in index.items():
            if case_id in strings and family in strings:
                found.add(case_id)
    return tuple(sorted(found))


def _search_tokens(value: Any) -> tuple[str, ...]:
    """Every string a sealed value would contribute to a serialised surface.

    A sealed field is a label, a nonce, a list of ids or a list of task objects,
    and each leaks differently: the list has to be searched item by item, because
    a packet that republished one of three competing causes would not contain the
    list's serialisation and would still have disclosed a candidate.
    """

    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Mapping):
        return tuple(
            token for item in value.values() for token in _search_tokens(item)
        )
    if isinstance(value, list):
        return tuple(token for item in value for token in _search_tokens(item))
    return ()


def generate_sound_suite(
    *,
    suite_id: str | None = None,
    assignment_seed: str | None = None,
    per_family: int = CASES_PER_FAMILY,
) -> SoundSuite:
    """Build a suite, validate it with the freeze, and return both halves separated.

    ``validate_protected_suite`` runs first and is not optional. It is the check
    that refuses every nonce shape a registered probe generates, so a generator
    that skipped it could emit a suite the audit then has to discover is weak ---
    and the two would be free to disagree about what a good nonce is.
    """

    families = sorted(ROOT_CAUSES)
    seed = assignment_seed or mint_assignment_seed()
    assignment, rejected = assign_families(seed, families=families, per_family=per_family)
    identifier = suite_id or f"p5-sound-hidden-cause-{assignment_seed_commitment(seed)[:16]}"
    sealed = build_sealed_suite(
        suite_id=identifier,
        assignment=assignment,
        assignment_seed=seed,
        families=families,
    )
    validate_protected_suite(sealed)
    packet, manifest = freeze_protected_suite(sealed)
    return SoundSuite(
        suite_id=identifier,
        sealed_suite=sealed,
        assignment_seed=seed,
        assignment_draws_rejected=rejected,
        candidate_packet=packet,
        commitment_manifest=manifest,
    )


def block_covering_fit_case_ids(
    cases: Sequence[Mapping[str, Any]], *, block_size: int = CASES_PER_FAMILY
) -> frozenset[str]:
    """One opening per ordinal block, all of distinct families: the split that scores.

    ``default_fit_case_ids`` takes the first case of each family. On a suite whose
    families are not in blocks that leaves most ordinal blocks unfitted, the block
    rule abstains on most eval cases, and the probe reports nothing --- so the
    default split cannot test the cue on a suite that has any chance of clearing
    it. Covering every block instead is the *harder* test: it hands the adversary
    an authorised opening in every region of the emitted order, which is strictly
    more than a sound freeze discloses to anybody, and it is chosen to maximise
    the cue's reach rather than to limit it.

    Distinct families as well as distinct blocks, because a split that took all
    three cases of one family would leave that family with no positive on the eval
    split, and a probe with no positive to find reports ``None`` --- an absent
    measurement dressed as a clean one. One per family is also exactly the
    disclosure ``default_fit_case_ids`` assumes, so the two splits differ in
    coverage and not in how much they concede.

    Such a split always exists once no block repeats a family: any *k* blocks hold
    3*k* cases, no family holds more than three, so *k* blocks always show at least
    *k* distinct families and Hall's condition is met. The matching below is
    deterministic in the emitted order, so the split is a property of the suite
    rather than of when it was computed.
    """

    blocks: list[list[tuple[str, str]]] = []
    for start in range(0, len(cases), block_size):
        blocks.append(
            [
                (str(case["case_id"]), str(case["protected_root_cause"]))
                for case in cases[start : start + block_size]
            ]
        )

    #: family -> (case id, index of the block that case came from)
    chosen_by_family: dict[str, tuple[str, int]] = {}

    def _augment(block: int, seen: set[str]) -> bool:
        for case_id, family in blocks[block]:
            if family in seen:
                continue
            seen.add(family)
            holder = chosen_by_family.get(family)
            if holder is None or _augment(holder[1], seen):
                chosen_by_family[family] = (case_id, block)
                return True
        return False

    for index in range(len(blocks)):
        if not _augment(index, set()):
            raise RuntimeError(
                "no fit split covers every ordinal block with a distinct family; the "
                "assignment repeats a family inside a block"
            )
    return frozenset(case_id for case_id, _ in chosen_by_family.values())


def _identifiability_rows(
    cases: Sequence[Mapping[str, Any]], *, fit_case_ids: Iterable[str] | None
) -> list[dict[str, Any]]:
    families = sorted({str(case["protected_root_cause"]) for case in cases})
    return [
        audit_root_cause_identifiability(
            cases, label=family, fit_case_ids=fit_case_ids
        ).as_json()
        for family in families
    ]


def _families_recovered(rows: Sequence[Mapping[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if any(
            (result.get("recovery") or 0.0) > 0.0 for result in row.get("results", [])
        )
    )


def _unscoreable_probes(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Probes that produced no positive or no negative, and so no informedness.

    Reported next to ``families_recovered`` because they are the whole difference
    between the two numbers a reader might otherwise conflate: nothing was
    recovered, and one probe was in no position to recover anything. Only the
    second of those blocks the roll-up.
    """

    return sorted(
        {
            str(result["probe_id"])
            for row in rows
            for result in row.get("results", [])
            if result.get("recovery") is None
        }
    )


def _opening_separation_summary(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What one authorised opening of one case discloses, across the suite.

    Aggregated rather than listed per case: the per-case rows carry nothing
    sealed, but a report that named every commitment of every case would be a
    map of the manifest for no gain over the four numbers below.
    """

    reports = [opening_disclosure_report(case) for case in cases]
    non_root = [
        row
        for report in reports
        for row in report["released"]
        if row["released"] != "root-cause"
    ]
    return {
        "commitment_kinds_per_case": sorted({report["commitment_kinds"] for report in reports}),
        "non_root_openings": len(non_root),
        "worst_non_root_opening_discloses": max(
            (row["opens_count"] for row in non_root), default=0
        ),
        "non_root_openings_that_disclose_the_root_cause": sum(
            1 for row in non_root if row["opens_root_cause"]
        ),
        "every_case_separated": all(report["separated"] for report in reports),
        "note": (
            "Under the shared nonce every one of these openings disclosed all seven "
            "commitments of its case. Each kind now has its own opening nonce derived "
            "from the one stored secret; the root-cause opening is the declared "
            "exception and still discloses all seven, because it is the answer."
        ),
    }


def audit_sound_suite(
    suite: SoundSuite, *, budget_digests: int = DISCLOSURE_BUDGET_DIGESTS
) -> dict[str, Any]:
    """Attack the generated suite with the instruments the shipped suite failed.

    Same seven disclosure probes, same budget, same ``validate_protected_suite``,
    same three shortcut probes. Nothing here is a new measurement device; the only
    thing that changed is the artifact under the instrument.
    """

    cases = suite.cases
    # The whole roll-up, not a re-implementation of it: the sound suite goes
    # through the same audit_hidden_cause_suite the shipped suite does, including
    # its non-compensatory overall verdict, so the two reports can be read side by
    # side without a reader checking whether they were computed the same way.
    roll_up = audit_hidden_cause_suite(
        {"suite_id": suite.suite_id, "cases": cases}, budget_digests=budget_digests
    )
    default_rows = list(roll_up["root_cause_identifiability"])
    covering_rows = _identifiability_rows(
        cases, fit_case_ids=sorted(block_covering_fit_case_ids(cases))
    )
    published = suite.published_surface()

    return {
        "schema_version": DEMONSTRATION_SCHEMA_VERSION,
        "suite_id": suite.suite_id,
        "overall_outcome": roll_up["overall_outcome"],
        # Stated in the artifact, not only in the commit message. This is an
        # instrument demonstration: the cases carry no authored symptom, no
        # hidden-cause campaign has been run against them, and a custody audit
        # that passes says the answer key was kept -- never that anything was
        # measured with it.
        "grants_authority": "NONE",
        "closes_gate": None,
        "is_scientific_result": False,
        "authority_note": (
            "A custody-sound suite with no campaign run against it. It demonstrates that "
            "the repaired freeze can produce commitments the declared adversary cannot "
            "open; it produces no attribution score, promotes no P5 claim, and leaves the "
            "manuscript's 21/24 on the shipped suite exactly where it is."
        ),
        "n_cases": len(cases),
        "custody_rule_gaps": list(CUSTODY_RULE_GAPS),
        "custody_rule_gaps_closed": list(CUSTODY_RULE_GAPS_CLOSED),
        "assignment": {
            "seed_commitment": assignment_seed_commitment(suite.assignment_seed),
            "seed_published": False,
            "draws_rejected": suite.assignment_draws_rejected,
            "no_ordinal_block_repeats_a_family": not block_repeats_a_family(
                suite.families, block_size=CASES_PER_FAMILY
            ),
            "ordinal_independence": ordinal_independence_report(suite.families),
        },
        "published_field_independence": published_field_independence_report(
            cases, list(suite.families)
        ),
        "commitment_openings": _opening_separation_summary(cases),
        "commitment_kind_domains": audit_commitment_kind_domains(suite.sealed_suite),
        "published_surface": {
            "candidate_packet_hash": sha256_json(suite.candidate_packet),
            "commitment_manifest_hash": sha256_json(suite.commitment_manifest),
            "case_fields": sorted(PUBLISHED_CASE_FIELDS),
            "sealed_material_found_in_published_surface": list(
                sealed_material_in(published, suite=suite)
            ),
        },
        "sealed_material": {
            "case_fields": sorted(SEALED_CASE_FIELDS),
            "committed_to_repository": False,
            "note": (
                "Held in process memory for the length of this audit and never serialised "
                "by this module. Re-running the generator draws a new suite; the one "
                "audited here cannot be recovered from anything written."
            ),
        },
        "freeze_validation": "ACCEPTED",
        "disclosure_budget_digests": budget_digests,
        "digests_computed": roll_up["digests_computed"],
        "probes_run": roll_up["probes_run"],
        "enumerable_nonces": roll_up["enumerable_nonces"],
        "commitment_custody": roll_up["commitment_custody"],
        "root_cause_identifiability": {
            "default_fit": {
                "fit_case_ids": sorted(default_fit_case_ids(cases)),
                "families_recovered": _families_recovered(default_rows),
                "probes_that_could_not_be_scored": _unscoreable_probes(default_rows),
                "audits": default_rows,
            },
            "block_covering_fit": {
                "fit_case_ids": sorted(block_covering_fit_case_ids(cases)),
                "families_recovered": _families_recovered(covering_rows),
                "probes_that_could_not_be_scored": _unscoreable_probes(covering_rows),
                "audits": covering_rows,
            },
        },
        "identifiability_instrument_limit": (
            "nonce-ordinal-block reads (int(nonce, 16) - 1) // 3. Against 256-bit CSPRNG "
            "nonces every case has its own signature, the fitted rule abstains on every "
            "eval case, and recovery is undefined -- which audit_label_identifiability "
            "reports as NO_PROBE_SCORED / CANNOT_CHECK. No correctly salted suite can "
            "pass that audit, so the roll-up here blocks on an abstention rather than on "
            "a recovered label. The number that answers the question asked is "
            "families_recovered: 8 of 8 on the shipped suite, 0 of 8 here."
        ),
    }


def contrast_report(
    *,
    shipped_suite: Mapping[str, Any],
    sound_suite: SoundSuite,
    budget_digests: int = DISCLOSURE_BUDGET_DIGESTS,
) -> dict[str, Any]:
    """Both artifacts under one instrument, so the repair is a comparison to run.

    The shipped suite's ``FAIL`` decides the verdict on its own. A demonstration
    that a sound suite is buildable does not make a broken shipped artifact less
    broken, and the roll-up here is non-compensatory for the same reason
    ``audit_hidden_cause_suite``'s is.
    """

    shipped = audit_hidden_cause_suite(shipped_suite, budget_digests=budget_digests)
    sound = audit_sound_suite(sound_suite, budget_digests=budget_digests)
    shipped_custody = shipped["commitment_custody"]
    sound_custody = sound["commitment_custody"]
    shipped_worst = {item["probe_id"]: item for item in shipped_custody["attempts"]}
    sound_worst = {item["probe_id"]: item for item in sound_custody["attempts"]}

    return {
        "schema_version": CONTRAST_SCHEMA_VERSION,
        "grants_authority": "NONE",
        "closes_gate": None,
        "verdict_source": "shipped_suite",
        "verdict_note": (
            "The exit status of this report is the shipped suite's. The sound suite is a "
            "demonstration that the repaired scheme can hold; it is not a repair of the "
            "artifact P5 shipped, which cannot be re-sealed by anybody who has seen the "
            "answers."
        ),
        "shipped_suite": shipped,
        "sound_suite_demonstration": sound,
        "contrast": {
            "commitment_custody": {
                "shipped": {
                    "outcome": shipped_custody["outcome"],
                    "reason": shipped_custody["reason"],
                    "worst_disclosure_rate": shipped_custody["worst_disclosure_rate"],
                    "ordinal_probe_disclosed": shipped_worst["ordinal-nonce"]["disclosed"],
                    "ordinal_probe_digests": shipped_worst["ordinal-nonce"][
                        "digests_computed"
                    ],
                    "digests_computed": shipped["digests_computed"],
                },
                "sound": {
                    "outcome": sound_custody["outcome"],
                    "reason": sound_custody["reason"],
                    "worst_disclosure_rate": sound_custody["worst_disclosure_rate"],
                    "ordinal_probe_disclosed": sound_worst["ordinal-nonce"]["disclosed"],
                    "ordinal_probe_digests": sound_worst["ordinal-nonce"]["digests_computed"],
                    "digests_computed": sound["digests_computed"],
                },
            },
            "families_recovered_by_a_competence_free_cue": {
                "shipped": _families_recovered(shipped["root_cause_identifiability"]),
                "sound_default_fit": sound["root_cause_identifiability"]["default_fit"][
                    "families_recovered"
                ],
                "sound_block_covering_fit": sound["root_cause_identifiability"][
                    "block_covering_fit"
                ]["families_recovered"],
                "of": len(sorted(ROOT_CAUSES)),
            },
            "enumerable_nonces": {
                "shipped": len(shipped["enumerable_nonces"]),
                "sound": len(sound["enumerable_nonces"]),
            },
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a custody-sound ORION-P5 hidden-cause suite and attack it with the "
            "same probes the shipped suite fails"
        )
    )
    parser.add_argument("--shipped-suite", type=Path, default=Path(SHIPPED_SUITE_PATH))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--budget-digests", type=int, default=DISCLOSURE_BUDGET_DIGESTS)
    parser.add_argument(
        "--sound-only",
        action="store_true",
        help=(
            "audit only the generated suite; without it the shipped suite is audited too "
            "and its verdict, not the generated suite's, is the exit status"
        ),
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    # Exit 0 requires the audited suite's own roll-up to pass. It will not pass
    # here, and the reason is in identifiability_instrument_limit rather than in
    # the suite: nonce-ordinal-block abstains on every case of any correctly
    # salted suite, and an abstention is CANNOT_CHECK. A non-zero exit for "the
    # instrument could not certify this" is the honest one; reading it as "the
    # suite leaked" would be wrong, and commitment_custody says so directly.
    suite = generate_sound_suite()
    if args.sound_only:
        report: dict[str, Any] = audit_sound_suite(suite, budget_digests=args.budget_digests)
        blocking = report["overall_outcome"] != Outcome.PASS.value
    else:
        shipped = json.loads(args.shipped_suite.read_text(encoding="utf-8"))
        report = contrast_report(
            shipped_suite=shipped,
            sound_suite=suite,
            budget_digests=args.budget_digests,
        )
        blocking = report["shipped_suite"]["overall_outcome"] != Outcome.PASS.value

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 3 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ASSIGNMENT_COMMITMENT_KIND",
    "CASE_ID_PREFIX",
    "CONTRAST_SCHEMA_VERSION",
    "CUSTODY_RULE_GAPS",
    "CUSTODY_RULE_GAPS_CLOSED",
    "DEMONSTRATION_SCHEMA_VERSION",
    "PUBLISHED_CASE_FIELDS",
    "OPENING_MATERIAL_CASE_FIELDS",
    "SEALED_CASE_FIELDS",
    "SEALED_SUITE_FIELDS",
    "SoundSuite",
    "assign_families",
    "assignment_seed_commitment",
    "audit_sound_suite",
    "block_covering_fit_case_ids",
    "block_repeats_a_family",
    "build_sealed_suite",
    "contrast_report",
    "generate_sound_suite",
    "label_pairings_in",
    "main",
    "mint_assignment_seed",
    "sealed_material_in",
]
