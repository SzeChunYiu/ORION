"""Fail-closed freeze utilities for the ORION-P5 hidden-cause study.

The protected suite contains root-cause truth, fresh-task payloads, evaluator
bindings, rubrics, negative variants, and opening nonces.  It must remain under
external/protected custody.  This module derives two safe-to-share artifacts:

* a candidate packet containing only development-visible information; and
* a commitment manifest binding the protected material without disclosing it.

The commitment is not empirical evidence and cannot promote a P5 result.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "orion.p5.protected-hidden-cause-suite.v1"
CANDIDATE_SCHEMA_VERSION = "orion.p5.candidate-hidden-cause-packet.v1"
COMMITMENT_SCHEMA_VERSION = "orion.p5.protected-suite-commitment.v1"

ROOT_CAUSES = frozenset(
    {
        "RETRIEVAL_MISS",
        "ROUTING_PLANNING_MISS",
        "IMPLEMENTATION_BUG",
        "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
        "EVALUATOR_METRIC_BUG",
        "REPRESENTATION_GAP",
        "MEASUREMENT_SPECIFICATION_GAP",
        "METHOD_BASIS_GAP",
    }
)

ALLOWED_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT", "DATA", "TOOL"})
INDEPENDENT_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT"})
_HEX = frozenset("0123456789abcdef")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return a deterministic SHA-256 digest for JSON-compatible ``value``."""

    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _protected_commitment(value: Any, nonce: str, *, kind: str) -> str:
    """Bind protected content without publishing a dictionary-attackable raw hash.

    ``nonce`` is the case's stored secret; what goes into the digest is that
    kind's own opening nonce, derived from it by :func:`opening_nonce`. One nonce
    per case used to mean one nonce for all seven commitment kinds, so opening
    any one of them opened the other six --- see *One opening nonce per
    commitment kind* in ``PROTECTED_SUITE_FREEZE_V1.md``.
    """

    return _commitment_digest(value, opening_nonce(nonce, kind=kind), kind=kind)


def _commitment_digest(value: Any, opening: str, *, kind: str) -> str:
    """The published digest for one commitment, from the nonce that opens it."""

    return sha256_json({"kind": kind, "payload_hash": sha256_json(value), "nonce": opening})


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: Any, field: str, *, min_items: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < min_items:
        raise ValueError(f"{field} must contain at least {min_items} item(s)")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_nonempty_string(item, f"{field}[{index}]"))
    if len(result) != len(set(result)):
        raise ValueError(f"{field} contains duplicate values")
    return result


def _require_sha256(value: Any, field: str) -> str:
    digest = _require_nonempty_string(value, field)
    if digest != digest.lower() or len(digest) != 64 or any(char not in _HEX for char in digest):
        raise ValueError(f"{field} must be a 64-character lowercase SHA-256 hex digest")
    return digest


#: The root-cause commitment binds one of eight public enum labels. Eight digests
#: exhaust that message space, so every bit of protection the scheme has lives in
#: the nonce, and the nonce is the one field no schema can inspect for entropy:
#: `0...01` and a CSPRNG draw are both 64 hex characters, both unique across a
#: suite, both non-zero. The shipped PROTECTED_SUITE_V1 used `int(nonce, 16)`
#: values 1 through 24, and the 24 commitments a freeze of it would publish open
#: in 108 SHA-256 evaluations. See
#: research/failures/2026-08-invertible-commitment-vacuous-custody/.
#:
#: A magnitude floor alone does not repair that. `f"{2**255 + ordinal:064x}"`
#: clears any floor and is enumerated as cheaply as the ordinal was. The rule
#: below is therefore shaped as "reject what a declared cheap adversary
#: enumerates", not "reject what looks small", and
#: `orion.study.p5.hidden_cause_custody` builds its disclosure probes from the
#: same generators so the two cannot drift apart.
_MIN_NONCE_VALUE = 1 << 64

#: A run of 32 identical hex characters is what padding leaves; 32 CSPRNG bytes
#: produce one with probability below 2**-119.
_MAX_IDENTICAL_RUN = 32

#: 32 bytes drawn from a CSPRNG take about 30 distinct values. Taking fewer than
#: twelve has probability near 3e-15 and is the signature of a nonce assembled
#: from a short alphabet -- `"ab" * 24` plus a counter, say, which clears both the
#: magnitude floor and the run limit while carrying about 16 bits.
_MIN_DISTINCT_BYTES = 12

#: Two independent 256-bit draws agree in their first 16 hex characters with
#: probability 2**-64. Agreement at that length across a suite means one salt
#: varied by an index, which is a single secret with a public offset rather than
#: a per-case one.
_MAX_SHARED_NONCE_AFFIX = 16


def mint_root_cause_nonce() -> str:
    """Draw one opening nonce: 256 bits from the OS CSPRNG, per case, never reused.

    The error raised by :func:`nonce_weakness` used to be the only place that
    said how to produce a correct nonce, which left every caller to implement
    the one line that carries the scheme's entire security. This is that line.
    """

    return secrets.token_hex(32)


def constant_nonces() -> frozenset[str]:
    """Fixed nonces a generator leaves behind when it never drew one.

    Placeholders, not guesses: each is a value a fixture, template or default
    argument writes into the field, and a commitment opened by one was never
    protected by anything.
    """

    values = {digit * 64 for digit in "0123456789abcdef"}
    blocks = ("01", "0f", "de", "ad", "beef", "dead", "deadbeef", "cafebabe", "0123456789abcdef")
    for block in blocks:
        values.add(block * (64 // len(block)))
    for seed in (b"", b"nonce", b"changeme", b"placeholder", b"secret", b"seed", b"0"):
        values.add(hashlib.sha256(seed).hexdigest())
    values.add(sha256_json(""))
    values.add(sha256_json({}))
    values.add(sha256_json(None))
    values.add(sha256_json(0))
    return frozenset(values)


def published_field_nonces(
    case: Mapping[str, Any], *, ordinal: int, suite_id: str = ""
) -> frozenset[str]:
    """Nonces derivable from what the manifest publishes beside the commitment.

    A nonce computed from the case id, the case's position or the visible
    symptom is published in full the moment the manifest is, whatever its
    entropy looks like. ``ordinal`` is the case's 1-based position in the suite
    as emitted.
    """

    seeds: list[str] = [
        str(case.get("case_id", "")),
        str(ordinal),
        f"{ordinal:064x}",
        str(case.get("visible_symptom", "")),
        suite_id,
        f"{suite_id}|{case.get('case_id', '')}",
        f"{case.get('case_id', '')}|{ordinal}",
    ]
    values: set[str] = set()
    for seed in seeds:
        if not seed:
            continue
        values.add(hashlib.sha256(seed.encode("utf-8")).hexdigest())
        values.add(sha256_json(seed))
        values.add(hashlib.sha512(seed.encode("utf-8")).hexdigest()[:64])
    values.add(sha256_json(ordinal))
    return frozenset(values)


def _max_identical_run(nonce: str) -> int:
    best = run = 1
    for previous, char in zip(nonce, nonce[1:]):
        run = run + 1 if char == previous else 1
        best = max(best, run)
    return best


def nonce_weakness(
    nonce: str,
    *,
    case: Mapping[str, Any] | None = None,
    ordinal: int | None = None,
    suite_id: str = "",
) -> str | None:
    """Name the cheap enumeration that finds ``nonce``, or ``None`` if none does.

    Returns a sentence rather than a boolean because the caller has to be able
    to say *which* attack the nonce fell to; "invalid nonce" is not a finding an
    operator can act on. ``case`` and ``ordinal`` are optional so the shape rules
    can be applied to a bare nonce, but a suite validation supplies them, since
    the derived-from-published-field family cannot be checked without them.
    """

    value = int(nonce, 16)
    if value == 0:
        return "the all-zero nonce"
    if value < _MIN_NONCE_VALUE:
        return "below 2**64, the range a counter, an ordinal or a small integer occupies"
    if value > (1 << 256) - _MIN_NONCE_VALUE:
        return "within 2**64 of 2**256, the range a counter run down from the top occupies"
    run = _max_identical_run(nonce)
    if run >= _MAX_IDENTICAL_RUN:
        return (
            f"padded with a run of {run} identical hex characters, leaving {64 - run} "
            "characters of anything at all"
        )
    for block in (1, 2, 4, 8, 16, 32):
        if nonce == nonce[:block] * (64 // block):
            return f"a {block}-character block repeated {64 // block} times"
    distinct = len({nonce[index : index + 2] for index in range(0, 64, 2)})
    if distinct < _MIN_DISTINCT_BYTES:
        return (
            f"assembled from {distinct} distinct bytes where 32 CSPRNG bytes take about 30"
        )
    if nonce in constant_nonces():
        return "a fixed placeholder a generator leaves behind"
    if case is not None and ordinal is not None:
        if nonce in published_field_nonces(case, ordinal=ordinal, suite_id=suite_id):
            return "derived from a field the manifest publishes beside the commitment"
    return None


def _require_nonce(
    value: Any,
    field: str,
    *,
    case: Mapping[str, Any] | None = None,
    ordinal: int | None = None,
    suite_id: str = "",
) -> str:
    nonce = _require_sha256(value, field)
    weakness = nonce_weakness(nonce, case=case, ordinal=ordinal, suite_id=suite_id)
    if weakness is not None:
        raise ValueError(
            f"{field} is {weakness} and is therefore enumerable; the protected root "
            "cause has only eight possible values, so a guessable nonce leaves the "
            "commitment openable by brute force. Draw nonces from "
            "orion.study.p5.freeze.mint_root_cause_nonce()."
        )
    return nonce


def _surface_parts(value: str, field: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative non-traversing surface")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if not parts:
        raise ValueError(f"{field} must identify a concrete surface")
    return parts


def _surface_sets_conflict(allowed: list[str], protected: list[str], *, prefix: str) -> bool:
    allowed_parts = [
        _surface_parts(value, f"{prefix}.allowed_change_surface[{index}]")
        for index, value in enumerate(allowed)
    ]
    protected_parts = [
        _surface_parts(value, f"{prefix}.protected_surface[{index}]")
        for index, value in enumerate(protected)
    ]
    for left in allowed_parts:
        for right in protected_parts:
            if left == right[: len(left)] or right == left[: len(right)]:
                return True
    return False


#: The custody rule names the fields a freeze may publish and the fields it must
#: withhold. It does not name the *order* the cases are emitted in, and neither
#: did the nine conditions below until this one was added --- so a suite could
#: satisfy every stated rule and still hand a candidate the answer key, because
#: the answer was a function of a number printed on every case.
#:
#: PROTECTED_SUITE_V1 was exactly that suite. Its twenty-four cases are eight
#: root-cause families in eight consecutive blocks of three, so
#: `family = order[(ordinal - 1) // 3]` reproduces all twenty-four labels from
#: the case ids alone. Its opening nonces were separately broken, and the freeze
#: now refuses them; had they been sound, this validator would still have passed
#: a suite whose commitments no candidate needed to open.
#:
#: "Not recoverable from the ordinal" is not decidable in general -- every
#: assignment is *some* function of the ordinal. So the condition is shaped the
#: way the rest of this programme shapes its guards: declare the adversary, then
#: check that this suite defeats it. `ORDINAL_FAMILY_ORDERINGS` x block sizes x
#: strides is a stated, enumerable family of deciding rules; a suite reproduced
#: exactly by any one of them is rejected and named. A suite that survives is not
#: thereby proved independent of the ordinal --- it is proved to defeat these
#: rules, which is what the check claims and all it claims.
_ORDINAL_MIN_BLOCK = 2


@dataclass(frozen=True)
class OrdinalRule:
    """One declared way of predicting a case's family from its ordinal.

    ``openings`` are the 0-based positions the rule had to be *told* before it
    could predict anything --- the price the adversary pays to instantiate the
    ordering. They are excluded from scoring. Without that exclusion the family
    is vacuous: on a suite with one case per family, the rule that reads families
    off their own first appearances "recovers" every case while predicting none
    of them, and the guard would reject every suite it was shown.
    """

    name: str
    predicted: tuple[str, ...]
    openings: frozenset[int]

    def scored_positions(self, length: int) -> tuple[int, ...]:
        return tuple(index for index in range(length) if index not in self.openings)

    def agreement(self, assignment: Sequence[str]) -> tuple[int, int]:
        """Return (cases predicted correctly, cases predicted at all)."""

        scored = self.scored_positions(len(assignment))
        correct = sum(1 for index in scored if self.predicted[index] == assignment[index])
        return correct, len(scored)

    def recovers(self, assignment: Sequence[str]) -> bool:
        correct, scored = self.agreement(assignment)
        return scored > 0 and correct == scored


def _family_orderings(assignment: Sequence[str]) -> dict[str, tuple[tuple[str, ...], frozenset[int]]]:
    """The orderings an adversary can put the families in, and what each costs.

    Alphabetical order is free: the eight labels are a public enum, so every case
    is a prediction. First-appearance order is not free --- the adversary opens a
    case to learn each family's slot --- so those openings are charged against it
    and only the cases after them count as predictions.
    """

    first_seen: list[str] = []
    openings: list[int] = []
    for index, family in enumerate(assignment):
        if family not in first_seen:
            first_seen.append(family)
            openings.append(index)
    paid = frozenset(openings)
    free: frozenset[int] = frozenset()
    forwards = tuple(first_seen)
    alphabetical = tuple(sorted(first_seen))
    return {
        "first-appearance": (forwards, paid),
        "first-appearance-reversed": (tuple(reversed(forwards)), paid),
        "alphabetical": (alphabetical, free),
        "alphabetical-reversed": (tuple(reversed(alphabetical)), free),
    }


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return left


def ordinal_reading_rules(assignment: Sequence[str]) -> tuple[OrdinalRule, ...]:
    """Return every declared ordinal-reading rule, instantiated for ``assignment``.

    Each rule maps a 1-based ordinal to a family using nothing but the ordinal,
    the suite length, the eight public labels and the openings charged to it.
    Rules are named so a rejection can quote the rule that read the suite rather
    than saying only that something did.
    """

    length = len(assignment)
    if length == 0:
        return ()
    rules: list[OrdinalRule] = []
    for ordering_name, (order, openings) in _family_orderings(assignment).items():
        count = len(order)
        if count == 0:
            continue
        for block in range(_ORDINAL_MIN_BLOCK, length // 2 + 1):
            if length % block:
                continue
            rules.append(
                OrdinalRule(
                    name=f"{ordering_name}/blocks-of-{block}",
                    predicted=tuple(order[(index // block) % count] for index in range(length)),
                    openings=openings,
                )
            )
        for stride in range(1, count):
            if _gcd(stride, count) != 1:
                continue
            rules.append(
                OrdinalRule(
                    name=f"{ordering_name}/stride-{stride}",
                    predicted=tuple(order[(index * stride) % count] for index in range(length)),
                    openings=openings,
                )
            )
    return tuple(rules)


def repeated_family_in_block(assignment: Sequence[str], *, block_size: int) -> int | None:
    """Return the 1-based ordinal opening the first block that repeats a family."""

    if block_size < _ORDINAL_MIN_BLOCK:
        return None
    for start in range(0, len(assignment), block_size):
        window = assignment[start : start + block_size]
        if len(set(window)) != len(window):
            return start + 1
    return None


def _even_family_block(assignment: Sequence[str]) -> int | None:
    """The block size implied by an evenly covered suite, or ``None``."""

    counts: dict[str, int] = {}
    for family in assignment:
        counts[family] = counts.get(family, 0) + 1
    sizes = set(counts.values())
    if len(sizes) != 1:
        return None
    per_family = sizes.pop()
    return per_family if per_family >= _ORDINAL_MIN_BLOCK else None


def ordinal_independence_report(assignment: Sequence[str]) -> dict[str, Any]:
    """Measure how far ``assignment`` is from being readable off the ordinal."""

    rules = ordinal_reading_rules(assignment)
    recovering = sorted(rule.name for rule in rules if rule.recovers(assignment))
    block_size = _even_family_block(assignment)
    repeated_at = (
        None if block_size is None else repeated_family_in_block(assignment, block_size=block_size)
    )
    worst_name = ""
    worst_correct = 0
    worst_scored = 0
    for rule in rules:
        correct, scored = rule.agreement(assignment)
        if scored and (correct, -scored) > (worst_correct, -worst_scored):
            worst_name, worst_correct, worst_scored = rule.name, correct, scored
    return {
        "cases": len(assignment),
        "families": len(set(assignment)),
        "rules_declared": len(rules),
        "rules_recovering_every_predicted_case": recovering,
        "strongest_rule": worst_name,
        "strongest_rule_correct": worst_correct,
        "strongest_rule_predicted": worst_scored,
        "even_block_size": block_size,
        "first_block_repeating_a_family": repeated_at,
        "independent": not recovering and repeated_at is None,
    }


def require_ordinal_independence(assignment: Sequence[str], *, surface: str) -> None:
    """Fail closed when the family assignment is readable off the case ordinal."""

    report = ordinal_independence_report(assignment)
    recovering = report["rules_recovering_every_predicted_case"]
    if recovering:
        raise ValueError(
            f"the {surface} case order hands over every family it was not shown: "
            f"rule {recovering[0]!r} predicts the remaining "
            f"{report['strongest_rule_predicted']} of {report['cases']} cases from the "
            "ordinal alone and gets every one right, so those commitments protect nothing"
        )
    repeated_at = report["first_block_repeating_a_family"]
    if repeated_at is not None:
        # A realised correlation is a realised leak whatever drew it: an adversary
        # handed one opening inside this block has the rest of it above chance.
        # The cost of the rule is that it rejects most honest uniform draws --
        # eight families of three land two in a block about five times in six --
        # and the remedy is to redraw the assignment, not to argue that this one
        # was innocent.
        raise ValueError(
            f"the {surface} case order repeats a root cause inside the block of "
            f"{report['even_block_size']} opening at ordinal {repeated_at}; one opening "
            "in that block predicts the others above chance. Redraw the assignment"
        )


# --- What a freeze publishes, what it seals, and the complement rule ---------
#
# PROTECTED_SUITE_FREEZE_V1.md states the withheld half under *Custody rule* and
# the publishable half under *Freeze command*, two sections apart, and until the
# lists below existed nothing said the two were complements: the only place the
# split was stated as one rule was `freeze_protected_suite` itself, and a field
# that appeared in neither list -- `competing_cause_set` was one -- could be
# published by a freeze without breaking any stated rule. Publishing that one
# would have cut the root-cause commitment's domain from eight candidates to the
# two or three the set names.
#
# The three lists below are that rule as data. `require_case_fields_classified`
# fails a freeze closed when a case carries a field in none of them, so a field
# added to the schema has to be classified before it can be frozen, and the
# classification is a diff against this file rather than an argument about what
# the document meant.

#: Carried verbatim into the candidate packet.
PUBLISHED_CASE_FIELDS = frozenset(
    {
        "case_id",
        "visible_symptom",
        "candidate_visible_context",
        "motivating_tasks",
        "replay_tasks",
        "allowed_change_surface",
    }
)

#: Published as identifiers in the commitment manifest, sealed as payloads.
#: ``fresh_tasks`` contributes ``task_id`` and ``changed_axes`` in the clear and
#: keeps ``content_hash`` behind a nonce-bound commitment; ``negative_variant_ids``
#: names payloads the manifest never carries. The *Freeze command* section
#: described the manifest as binding these "without publishing the protected
#: payloads" and did not say that the identifiers themselves are published, which
#: is what let a generator make ``changed_axes`` a function of the family and put
#: the label in the clear while following the text. See
#: :func:`require_published_field_independence`.
PUBLISHED_IDENTIFIER_CASE_FIELDS = frozenset({"fresh_tasks", "negative_variant_ids"})

#: Never published in any form by a freeze. ``competing_cause_set`` is the entry
#: the document named in neither list.
SEALED_CASE_FIELDS = frozenset(
    {
        "protected_root_cause",
        "root_cause_nonce",
        "competing_cause_set",
        "protected_surface",
        "success_rubric",
        "harm_rubric",
    }
)

#: Sealed values that live on the suite rather than on a case. ``evaluator_hash``
#: is deliberately absent: the manifest publishes it, which *Freeze command*
#: authorises ("binding the full private suite, evaluator, ...").
SEALED_SUITE_FIELDS = frozenset({"fresh_task_payloads", "negative_variant_payloads"})


def require_case_fields_classified(case: Mapping[str, Any], *, prefix: str) -> None:
    """Fail closed when a case carries a field the custody rule does not classify.

    This is the complement rule itself: every field of a protected case is either
    published, published as an identifier, or sealed, and a field in none of the
    three is a field whose custody nobody decided. Refusing it is what stops the
    next schema addition from reaching a candidate-readable branch by default.
    """

    unclassified = sorted(
        set(case)
        - PUBLISHED_CASE_FIELDS
        - PUBLISHED_IDENTIFIER_CASE_FIELDS
        - SEALED_CASE_FIELDS
    )
    if unclassified:
        raise ValueError(
            f"{prefix} carries {unclassified} which the custody rule classifies as "
            "neither published, published-as-identifier nor sealed; add the field to "
            "one of freeze.PUBLISHED_CASE_FIELDS, PUBLISHED_IDENTIFIER_CASE_FIELDS or "
            "SEALED_CASE_FIELDS and to the matching list in "
            "PROTECTED_SUITE_FREEZE_V1.md before freezing"
        )


def _sealed_strings(value: Any) -> tuple[str, ...]:
    """Every string a sealed value contributes to a serialised published surface.

    A sealed field is a label, a nonce, a list of ids or a nested object, and each
    leaks differently: a list has to be searched item by item, because a packet
    that republished one of three competing causes would not contain the list's
    serialisation and would still have disclosed a candidate.
    """

    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, Mapping):
        return tuple(token for item in value.values() for token in _sealed_strings(item))
    if isinstance(value, list):
        return tuple(token for item in value for token in _sealed_strings(item))
    return ()


def sealed_case_values(case: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    """``field -> strings that must not appear in anything a freeze publishes``.

    ``fresh_tasks.content_hash`` is included even though ``fresh_tasks`` is a
    published-identifier field: the id and the axes are published, the unsalted
    content hash is not, and a manifest that carried it would let an adversary
    confirm a guessed payload without opening anything.
    """

    values = {
        field: _sealed_strings(case.get(field))
        for field in sorted(SEALED_CASE_FIELDS)
        if case.get(field) is not None
    }
    hashes = tuple(
        str(fresh.get("content_hash", ""))
        for fresh in (case.get("fresh_tasks") or [])
        if isinstance(fresh, Mapping) and fresh.get("content_hash")
    )
    if hashes:
        values["fresh_tasks.content_hash"] = hashes
    return values


def published_surface_leaks(
    published: Any,
    *,
    cases: Sequence[Mapping[str, Any]],
    case_fields: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Sealed values that appear anywhere in ``published``, as ``field@case_id``.

    A split enforced by writing the right keys into the right dictionary is a
    split enforced by attention. This is the same split enforced by search: the
    published surface is serialised and every sealed string is looked for in it,
    so a field a later edit adds to the packet is caught by its content rather
    than by its name.
    """

    text = json.dumps(published, sort_keys=True, ensure_ascii=False)
    wanted = None if case_fields is None else set(case_fields)
    found: list[str] = []
    for case in cases:
        case_id = str(case.get("case_id", ""))
        for field, tokens in sealed_case_values(case).items():
            if wanted is not None and field not in wanted:
                continue
            if any(token in text for token in tokens):
                found.append(f"{field}@{case_id}")
    return tuple(found)


# --- The published fields must not be a function of the sealed answer --------
#
# `allowed_change_surface` is on the publishable list, and in the shipped suite it
# names the answer: `src/retrieval/index.py` for RETRIEVAL_MISS,
# `src/causal/representation.py` for REPRESENTATION_GAP, `src/measurement/spec.py`
# for MEASUREMENT_SPECIFICATION_GAP. The custody rule permitted publishing a field
# that in practice states the label, and neither the freeze nor the custody audit
# looked at it. The manifest's `task_id`, `changed_axes` and `variant_id` are the
# same hazard one step removed: publishing them is a deliberate choice -- a split
# has to be checkable -- but nothing said they must be independent of the family,
# so a generator that made `changed_axes` depend on it would put the label in the
# clear while following the text.
#
# "Does this path name this family" is not decidable, so the condition is shaped
# the way `require_ordinal_independence` is: declare the adversary, charge it for
# what it was told, and reject a suite it reads above what it was shown. Two
# declared readers, both using only the published surface and the eight public
# labels:
#
# * `label-token`: a published string names a family when its tokens match the
#   family's own label tokens -- exactly, or on a shared prefix of 4, 5 or 6
#   characters, which is what carries `metrics` to METRIC and `dependencies` to
#   DEPENDENCY. It costs no openings, because ROOT_CAUSES is a public enum, so
#   every case it gets right is a case whose commitment protects nothing.
# * `signature-leave-one-out`: the adversary is told the family of every other
#   case sharing a published field's exact value, and predicts the case left out
#   when those agree. This is the reader that catches a family-dependent
#   `changed_axes`: it abstains on a field that is constant across the suite
#   (the openings disagree) and on a field unique to each case (there is nothing
#   to be told), and fires exactly when the published value partitions the suite
#   along family lines.
#
# `visible_symptom` and `candidate_visible_context` are deliberately out of
# scope. A symptom is the one published field that *must* be informative about
# the hidden cause -- a case whose symptom carried no signal would not be a case
# -- so a token reader over it would reject every real suite and measure nothing.
# Whether a symptom says too much is a case-authoring question, and the
# instrument for it is the identifiability audit over symptom content, not this.

_LABEL_TOKEN_PREFIXES: tuple[int, ...] = (0, 4, 5, 6)

#: Published fields whose vocabulary the author chooses, and where a family name
#: is therefore a decision rather than a collision.
LABEL_TOKEN_FIELDS: tuple[str, ...] = (
    "case_id",
    "motivating_tasks",
    "replay_tasks",
    "allowed_change_surface",
    "task_id",
    "variant_id",
)

#: Published fields whose exact value the signature reader partitions on.
#: ``changed_axes`` is here and not above because its vocabulary is a fixed
#: six-element public enum that overlaps the family enum by construction:
#: ENVIRONMENT is both an axis and a family word, so a token reader would charge
#: an author for the axis the protocol told them to use. What must not happen is
#: that the *choice* of axes tracks the family, and that is what the signature
#: reader measures.
SIGNATURE_FIELDS: tuple[str, ...] = LABEL_TOKEN_FIELDS + ("changed_axes",)


def published_case_values(case: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    """The strings a freeze publishes for one case, by field.

    Six come from the candidate packet and three from the commitment manifest;
    they are read here from the protected case so the check can run inside
    ``validate_protected_suite``, before anything is emitted.
    """

    fresh = [item for item in (case.get("fresh_tasks") or []) if isinstance(item, Mapping)]
    return {
        "case_id": (str(case.get("case_id", "")),),
        "motivating_tasks": tuple(str(item) for item in case.get("motivating_tasks") or []),
        "replay_tasks": tuple(str(item) for item in case.get("replay_tasks") or []),
        "allowed_change_surface": tuple(
            str(item) for item in case.get("allowed_change_surface") or []
        ),
        "task_id": tuple(str(item.get("task_id", "")) for item in fresh),
        "changed_axes": tuple(
            sorted({str(axis) for item in fresh for axis in item.get("changed_axes") or []})
        ),
        "variant_id": tuple(str(item) for item in case.get("negative_variant_ids") or []),
    }


def _word_tokens(text: str) -> tuple[str, ...]:
    words: list[str] = []
    for chunk in re.split(r"[^A-Za-z0-9]+", text):
        if not chunk:
            continue
        words.extend(re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+|[0-9]+", chunk))
    return tuple(word.lower() for word in words if word.isalpha())


def family_label_tokens(families: Iterable[str] = ()) -> dict[str, frozenset[str]]:
    """``family -> the lowercase words of its own public label``."""

    names = sorted(families) if families else sorted(ROOT_CAUSES)
    return {name: frozenset(part.lower() for part in name.split("_")) for name in names}


def _shared_prefix(left: str, right: str) -> int:
    count = 0
    for one, other in zip(left, right):
        if one != other:
            break
        count += 1
    return count


def _token_matches(word: str, label_token: str, prefix: int) -> bool:
    if prefix == 0:
        return word == label_token
    return _shared_prefix(word, label_token) >= prefix


def read_family_from_strings(
    strings: Sequence[str], *, prefix: int, families: Iterable[str] = ()
) -> str | None:
    """The family these published strings name, or ``None`` when they name none.

    Scores each family by how many of *its own* label words the strings match and
    returns the unique best. A tie abstains: two families named equally well is a
    reader that has not read anything.
    """

    words = {word for text in strings for word in _word_tokens(text)}
    if not words:
        return None
    scores = {
        family: sum(
            1
            for label_token in tokens
            if any(_token_matches(word, label_token, prefix) for word in words)
        )
        for family, tokens in family_label_tokens(families).items()
    }
    best = max(scores.values(), default=0)
    if best == 0:
        return None
    winners = [family for family, score in scores.items() if score == best]
    return winners[0] if len(winners) == 1 else None


@dataclass(frozen=True)
class FamilyReadingRule:
    """One declared way of predicting a case's family from what a freeze publishes.

    ``predicted[i]`` is ``None`` where the rule abstains. ``charge`` says what the
    rule had to be told to make its predictions at all; a rule that is charged
    nothing is one whose every correct prediction is a free disclosure.
    """

    name: str
    predicted: tuple[str | None, ...]
    charge: str

    def disclosed(self, assignment: Sequence[str]) -> tuple[int, ...]:
        """0-based positions the rule predicts, and gets right."""

        return tuple(
            index
            for index, family in enumerate(assignment)
            if self.predicted[index] is not None and self.predicted[index] == family
        )

    def agreement(self, assignment: Sequence[str]) -> tuple[int, int]:
        """Return (cases predicted correctly, cases predicted at all)."""

        predicted = sum(1 for value in self.predicted if value is not None)
        return len(self.disclosed(assignment)), predicted


def _signature_leave_one_out(
    signatures: Sequence[tuple[str, ...]], assignment: Sequence[str]
) -> tuple[str | None, ...]:
    """Predict each case from the families of the other cases sharing its signature.

    Leave-one-out rather than a global fit, because the adversary's charge is the
    thing being modelled: to predict one case it must have been told every other
    case in that signature's class, and it can only be confident when those agree.
    """

    classes: dict[tuple[str, ...], list[int]] = {}
    for index, signature in enumerate(signatures):
        classes.setdefault(signature, []).append(index)
    predicted: list[str | None] = [None] * len(signatures)
    for members in classes.values():
        for index in members:
            others = {assignment[other] for other in members if other != index}
            predicted[index] = others.pop() if len(others) == 1 else None
    return tuple(predicted)


def published_field_reading_rules(
    cases: Sequence[Mapping[str, Any]], assignment: Sequence[str]
) -> tuple[FamilyReadingRule, ...]:
    """Every declared published-field reader, instantiated for these cases.

    Named so that a rejection can quote the reader and the field that read the
    suite, rather than saying only that something did.
    """

    values = [published_case_values(case) for case in cases]
    rules: list[FamilyReadingRule] = []
    for prefix in _LABEL_TOKEN_PREFIXES:
        label = "exact" if prefix == 0 else f"prefix-{prefix}"
        for field in LABEL_TOKEN_FIELDS:
            rules.append(
                FamilyReadingRule(
                    name=f"label-token-{label}/{field}",
                    predicted=tuple(
                        read_family_from_strings(value[field], prefix=prefix)
                        for value in values
                    ),
                    charge="nothing: the eight family labels are a public enum",
                )
            )
        rules.append(
            FamilyReadingRule(
                name=f"label-token-{label}/all-published-fields",
                predicted=tuple(
                    read_family_from_strings(
                        [text for field in LABEL_TOKEN_FIELDS for text in value[field]],
                        prefix=prefix,
                    )
                    for value in values
                ),
                charge="nothing: the eight family labels are a public enum",
            )
        )
    for field in SIGNATURE_FIELDS:
        rules.append(
            FamilyReadingRule(
                name=f"signature-leave-one-out/{field}",
                predicted=_signature_leave_one_out(
                    [value[field] for value in values], assignment
                ),
                charge=(
                    f"the family of every other case sharing this case's {field} value"
                ),
            )
        )
    return tuple(rules)


def published_field_independence_report(
    cases: Sequence[Mapping[str, Any]], assignment: Sequence[str]
) -> dict[str, Any]:
    """Measure how much of the answer key the published fields hand over."""

    rules = published_field_reading_rules(cases, assignment)
    case_ids = [str(case.get("case_id", "")) for case in cases]
    disclosing: list[dict[str, Any]] = []
    disclosed_cases: set[str] = set()
    disclosed_families: set[str] = set()
    for rule in rules:
        positions = rule.disclosed(assignment)
        if not positions:
            continue
        correct, predicted = rule.agreement(assignment)
        disclosing.append(
            {
                "rule": rule.name,
                "charge": rule.charge,
                "cases_disclosed": correct,
                "cases_predicted": predicted,
                "case_ids": [case_ids[index] for index in positions],
            }
        )
        disclosed_cases.update(case_ids[index] for index in positions)
        disclosed_families.update(assignment[index] for index in positions)
    disclosing.sort(key=lambda item: (-item["cases_disclosed"], item["rule"]))
    return {
        "cases": len(cases),
        "rules_declared": len(rules),
        "rules_disclosing_a_case": disclosing,
        "cases_disclosed": len(disclosed_cases),
        "families_disclosed": len(disclosed_families),
        "strongest_rule": disclosing[0]["rule"] if disclosing else "",
        "strongest_rule_disclosed": disclosing[0]["cases_disclosed"] if disclosing else 0,
        "independent": not disclosing,
    }


def require_published_field_independence(
    cases: Sequence[Mapping[str, Any]], assignment: Sequence[str], *, surface: str
) -> None:
    """Fail closed when a published field names the family it is supposed to seal."""

    report = published_field_independence_report(cases, assignment)
    if report["independent"]:
        return
    worst = report["rules_disclosing_a_case"][0]
    raise ValueError(
        f"the {surface} fields name the root cause they seal: reader {worst['rule']!r} "
        f"is charged {worst['charge']} and reads {worst['cases_disclosed']} of "
        f"{report['cases']} cases correctly ({', '.join(worst['case_ids'][:3])}"
        f"{', ...' if len(worst['case_ids']) > 3 else ''}); {report['cases_disclosed']} "
        f"cases and {report['families_disclosed']} families are disclosed in total by "
        f"{len(report['rules_disclosing_a_case'])} of {report['rules_declared']} declared "
        "readers. Name published fields after the case, never after the mechanism"
    )


# --- One nonce per case was one nonce for seven commitment kinds -------------
#
# A freeze publishes seven kinds of commitment per case -- the case artifact, the
# root cause, each fresh payload, each negative variant, the protected surface
# and both rubrics -- and every one of them used the case's single
# `root_cause_nonce`. Two costs follow, and only one of them is about entropy.
#
# The enumeration cost is real but conditional: an adversary opens the *cheapest*
# kind, not the one the probes attack. The seven disclosure probes in
# `hidden_cause_custody` attack the root-cause commitment, whose domain is the
# eight public labels; on the shipped suite the success- and harm-rubric payloads
# are `SECRET_SUCCESS_RUBRIC_{ordinal}` and the protected surface is a template
# over a word the candidate packet publishes, so those domains are one candidate,
# not eight. Sharing the nonce means the weakest of the seven sets the price of
# all seven. `hidden_cause_custody.audit_commitment_kind_domains` measures that.
# Once the nonce is a CSPRNG draw the whole family is 2**256-hard and the point
# is moot, which is the honest argument for why sharing was survivable.
#
# The disclosure cost is unconditional and no nonce entropy repairs it. Opening
# any one commitment means releasing the nonce that opens it, and a shared nonce
# opens the other six with it: a host that discloses a rubric to an auditor has
# disclosed the root cause. The repair is a per-kind opening nonce, derived by
# domain separation from the one 256-bit secret the case already stores, so the
# protected-suite schema does not change, the manifest's shape does not change,
# and only the digests a future freeze emits move. No shipped artifact moves:
# `PROTECTED_SUITE_V1` cannot be frozen at all (its nonces, content hashes and
# payload maps are all refused), and no commitment manifest is committed anywhere
# in this repository.
#
# The root cause keeps the case nonce itself, and that asymmetry is deliberate:
# it is the answer, it is the last thing opened, and making it the master opening
# is what lets the other six be opened without it. The cost is stated rather than
# hidden -- a host cannot open the label while keeping a fresh payload sealed for
# reuse in a later study. Deriving that one too would move the scheme the
# protocol document publishes and the scheme model the custody audit pins with
# `FREEZE_CANARY`, which is a larger change than this gap justifies.

#: The seven commitment kinds a freeze publishes per case, as kind prefixes. The
#: concrete kind string for a fresh task or a negative variant carries its
#: identifier too, so each payload gets its own opening nonce.
COMMITMENT_KINDS: tuple[str, ...] = (
    "case",
    "root-cause",
    "fresh-task",
    "negative-variant",
    "protected-surface",
    "success-rubric",
    "harm-rubric",
)

#: The one kind whose opening nonce is the case nonce itself.
ROOT_CAUSE_COMMITMENT_KIND = "root-cause"


def opening_nonce(case_nonce: str, *, kind: str) -> str:
    """The nonce that opens one commitment, and opens nothing else.

    Domain separation over the single stored secret: ``SHA-256`` of the kind and
    the case nonce. Releasing a derived nonce discloses that commitment and
    leaves the case nonce -- and therefore the other six commitments -- sealed,
    because inverting the derivation is a preimage search. Releasing the case
    nonce discloses everything, which is what the root-cause opening is for.
    """

    if kind == ROOT_CAUSE_COMMITMENT_KIND:
        return case_nonce
    return sha256_json({"kind": kind, "opening_nonce_for": case_nonce})


def case_commitment_kinds(case: Mapping[str, Any]) -> tuple[str, ...]:
    """The concrete kind strings a freeze emits for one case, in manifest order."""

    fresh = [item for item in (case.get("fresh_tasks") or []) if isinstance(item, Mapping)]
    return (
        f"case:{case.get('case_id', '')}",
        ROOT_CAUSE_COMMITMENT_KIND,
        *(f"fresh-task:{item.get('task_id', '')}" for item in sorted(
            fresh, key=lambda item: str(item.get("task_id", ""))
        )),
        *(
            f"negative-variant:{variant_id}"
            for variant_id in sorted(str(item) for item in case.get("negative_variant_ids") or [])
        ),
        "protected-surface",
        "success-rubric",
        "harm-rubric",
    )


def _derivable_nonces(released: str, kinds: Sequence[str]) -> frozenset[str]:
    """What an adversary holding one released opening nonce can compute.

    Includes the released value treated as a master, because an adversary who is
    handed one opening does not know which position in the derivation it came
    from and will try it as both.
    """

    return frozenset({released, *(opening_nonce(released, kind=kind) for kind in kinds)})


def opening_disclosure_report(case: Mapping[str, Any]) -> dict[str, Any]:
    """What one authorised opening discloses, per released kind.

    Under a shared nonce every release opens every commitment of the case; the
    number below is the whole point of the repair, and it is computed rather than
    asserted so a regression shows up as a number rather than as a comment.
    """

    nonce = str(case.get("root_cause_nonce", ""))
    kinds = case_commitment_kinds(case)
    released_rows: list[dict[str, Any]] = []
    for released_kind in kinds:
        derivable = _derivable_nonces(opening_nonce(nonce, kind=released_kind), kinds)
        opened = [kind for kind in kinds if opening_nonce(nonce, kind=kind) in derivable]
        released_rows.append(
            {
                "released": released_kind,
                "opens": opened,
                "opens_count": len(opened),
                "opens_root_cause": ROOT_CAUSE_COMMITMENT_KIND in opened,
            }
        )
    non_root = [row for row in released_rows if row["released"] != ROOT_CAUSE_COMMITMENT_KIND]
    return {
        "case_id": str(case.get("case_id", "")),
        "commitment_kinds": len(kinds),
        "released": released_rows,
        "worst_non_root_release_opens": max(
            (row["opens_count"] for row in non_root), default=0
        ),
        "non_root_releases_opening_the_root_cause": sum(
            1 for row in non_root if row["opens_root_cause"]
        ),
        "separated": all(row["opens_count"] == 1 for row in non_root),
    }


def require_opening_separation(
    case: Mapping[str, Any],
    committed_case: Mapping[str, Any],
    *,
    fresh_payloads: Mapping[str, Any],
    negative_payloads: Mapping[str, Any],
    prefix: str,
) -> None:
    """Fail closed when one authorised opening of this case would open another.

    Read off the emitted digests rather than off the helper that built them: for
    every commitment the nonce that actually opens it is recovered from the
    artifact, and then released to see what else it opens. A manifest built with
    one nonce for all seven kinds fails here whoever built it, which is what
    makes this a check on the artifact and not a restatement of
    :func:`opening_nonce`.

    The root-cause opening is excluded as a source and included as a target: the
    case nonce opens everything by declaration, and what must not happen is the
    reverse.
    """

    nonce = str(case.get("root_cause_nonce", ""))
    kinds = case_commitment_kinds(case)
    targets: list[tuple[str, str, Any]] = [
        (f"case:{case.get('case_id', '')}", str(committed_case["case_artifact_commitment"]), case),
        (
            "protected-surface",
            str(committed_case["protected_surface_commitment"]),
            sorted(case["protected_surface"]),
        ),
        (
            "success-rubric",
            str(committed_case["success_rubric_commitment"]),
            case["success_rubric"],
        ),
        ("harm-rubric", str(committed_case["harm_rubric_commitment"]), case["harm_rubric"]),
    ]
    for fresh in committed_case["fresh_tasks"]:
        task_id = str(fresh["task_id"])
        targets.append(
            (f"fresh-task:{task_id}", str(fresh["content_commitment"]), fresh_payloads[task_id])
        )
    for variant in committed_case["negative_variants"]:
        variant_id = str(variant["variant_id"])
        targets.append(
            (
                f"negative-variant:{variant_id}",
                str(variant["content_commitment"]),
                negative_payloads[variant_id],
            )
        )

    def _reopen(kind: str, payload: Any, opening: str) -> str:
        """The digest ``payload`` would carry if ``opening`` were its opening nonce."""

        if kind == ROOT_CAUSE_COMMITMENT_KIND:
            return _root_commitment(str(payload), opening)
        return _commitment_digest(payload, opening, kind=kind)

    targets.append(
        (
            ROOT_CAUSE_COMMITMENT_KIND,
            str(committed_case["root_cause_commitment"]),
            str(case["protected_root_cause"]),
        )
    )

    # What actually opens each commitment, taken from the digest rather than
    # assumed: the case nonce, or one of the per-kind derivations of it.
    candidates = [nonce, *(opening_nonce(nonce, kind=kind) for kind in kinds)]
    openings: dict[str, str] = {}
    for kind, digest, payload in targets:
        for candidate in candidates:
            if _reopen(kind, payload, candidate) == digest:
                openings[kind] = candidate
                break
        else:  # pragma: no cover - the freeze built these digests one line above
            raise ValueError(f"{prefix}: the {kind!r} commitment reopens under no known nonce")

    payload_by_kind = {kind: payload for kind, _, payload in targets}
    digest_by_kind = {kind: digest for kind, digest, _ in targets}
    for source, released in openings.items():
        if source == ROOT_CAUSE_COMMITMENT_KIND:
            continue
        derivable = _derivable_nonces(released, kinds)
        opened = sorted(
            kind
            for kind in openings
            if kind != source
            and any(
                _reopen(kind, payload_by_kind[kind], candidate) == digest_by_kind[kind]
                for candidate in derivable
            )
        )
        if opened:
            raise ValueError(
                f"{prefix}: releasing the opening nonce for {source!r} also opens "
                f"{len(opened)} of the {len(openings)} commitments this case publishes "
                f"({', '.join(opened)}). One nonce shared across the commitment kinds "
                "means one authorised opening discloses all of them; derive each kind's "
                "opening nonce with freeze.opening_nonce()"
            )


def _protected_case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_cases = suite.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases must be a non-empty array")
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw_case in enumerate(raw_cases):
        case = _require_mapping(raw_case, f"cases[{index}]")
        case_id = _require_nonempty_string(case.get("case_id"), f"cases[{index}].case_id")
        if case_id in result:
            raise ValueError(f"duplicate case_id: {case_id}")
        result[case_id] = case
    return result


def validate_protected_suite(raw_suite: Mapping[str, Any]) -> None:
    """Validate a private P5 suite and fail closed on freshness/integrity gaps."""

    suite = _require_mapping(raw_suite, "suite")
    if suite.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    suite_id = _require_nonempty_string(suite.get("suite_id"), "suite_id")
    if suite.get("created_before_outcome_access") is not True:
        raise ValueError("created_before_outcome_access must be true")
    _require_sha256(suite.get("evaluator_hash"), "evaluator_hash")

    fresh_payloads = _require_mapping(suite.get("fresh_task_payloads"), "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite.get("negative_variant_payloads"), "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    observed_causes: set[str] = set()
    used_nonces: set[str] = set()
    referenced_fresh: set[str] = set()
    referenced_nonfresh: set[str] = set()
    referenced_negative: set[str] = set()
    allowed_surfaces: list[str] = []
    protected_surfaces: list[str] = []

    emitted_assignment: list[str] = []
    family_by_case_id: dict[str, str] = {}

    for ordinal, (case_id, case) in enumerate(cases.items(), start=1):
        prefix = f"case {case_id}"
        require_case_fields_classified(case, prefix=prefix)
        _require_nonempty_string(case.get("visible_symptom"), f"{prefix}.visible_symptom")
        _require_mapping(case.get("candidate_visible_context"), f"{prefix}.candidate_visible_context")

        root = _require_nonempty_string(case.get("protected_root_cause"), f"{prefix}.protected_root_cause")
        if root not in ROOT_CAUSES:
            raise ValueError(f"{prefix}.protected_root_cause is not a registered root cause")
        observed_causes.add(root)
        emitted_assignment.append(root)
        family_by_case_id[case_id] = root

        nonce = _require_nonce(
            case.get("root_cause_nonce"),
            f"{prefix}.root_cause_nonce",
            case=case,
            ordinal=ordinal,
            suite_id=suite_id,
        )
        if nonce in used_nonces:
            raise ValueError("root_cause_nonce values must be unique across cases")
        # Distinct is not independent. One salt varied by an index shares its head
        # or its tail with every other case, so opening any one case opens the
        # scheme; the affix rule is what makes the salt per-case rather than
        # per-suite. Two real draws collide on 16 hex characters at 2**-64.
        for seen in used_nonces:
            if nonce[:_MAX_SHARED_NONCE_AFFIX] == seen[:_MAX_SHARED_NONCE_AFFIX]:
                raise ValueError(
                    f"{prefix}.root_cause_nonce shares its first "
                    f"{_MAX_SHARED_NONCE_AFFIX} characters with another case; that is one "
                    "salt with a per-case offset, not a per-case salt, and opening either "
                    "case opens both"
                )
            if nonce[-_MAX_SHARED_NONCE_AFFIX:] == seen[-_MAX_SHARED_NONCE_AFFIX:]:
                raise ValueError(
                    f"{prefix}.root_cause_nonce shares its last "
                    f"{_MAX_SHARED_NONCE_AFFIX} characters with another case; that is one "
                    "salt with a per-case offset, not a per-case salt, and opening either "
                    "case opens both"
                )
        used_nonces.add(nonce)

        competing = _require_string_list(
            case.get("competing_cause_set"), f"{prefix}.competing_cause_set", min_items=2
        )
        if root not in competing:
            raise ValueError(f"{prefix}.competing_cause_set must include protected_root_cause")

        motivating = _require_string_list(case.get("motivating_tasks"), f"{prefix}.motivating_tasks")
        replay = _require_string_list(case.get("replay_tasks"), f"{prefix}.replay_tasks")
        referenced_nonfresh.update(motivating)
        referenced_nonfresh.update(replay)
        allowed = _require_string_list(
            case.get("allowed_change_surface"), f"{prefix}.allowed_change_surface"
        )
        protected = _require_string_list(case.get("protected_surface"), f"{prefix}.protected_surface")
        if _surface_sets_conflict(allowed, protected, prefix=prefix):
            raise ValueError(f"{prefix} allowed_change_surface overlaps protected_surface")
        allowed_surfaces.extend(allowed)
        protected_surfaces.extend(protected)
        _require_nonempty_string(case.get("success_rubric"), f"{prefix}.success_rubric")
        _require_nonempty_string(case.get("harm_rubric"), f"{prefix}.harm_rubric")

        fresh_tasks = case.get("fresh_tasks")
        if not isinstance(fresh_tasks, list) or not fresh_tasks:
            raise ValueError(f"{prefix}.fresh_tasks must be a non-empty array")
        fresh_ids_for_case: set[str] = set()
        for fresh_index, raw_fresh in enumerate(fresh_tasks):
            fresh = _require_mapping(raw_fresh, f"{prefix}.fresh_tasks[{fresh_index}]")
            task_id = _require_nonempty_string(
                fresh.get("task_id"), f"{prefix}.fresh_tasks[{fresh_index}].task_id"
            )
            if task_id in referenced_fresh:
                raise ValueError(f"fresh task_id must be globally unique: {task_id}")
            referenced_fresh.add(task_id)
            fresh_ids_for_case.add(task_id)

            axes = _require_string_list(
                fresh.get("changed_axes"), f"{prefix}.fresh_tasks[{fresh_index}].changed_axes"
            )
            unknown_axes = set(axes) - ALLOWED_CHANGED_AXES
            if unknown_axes:
                raise ValueError(f"{prefix} fresh task {task_id} has unknown changed axes")
            if not (set(axes) & INDEPENDENT_CHANGED_AXES):
                raise ValueError(
                    f"{prefix} fresh task {task_id} must change TASK, DOMAIN, MODEL, or ENVIRONMENT"
                )

            expected_hash = _require_sha256(
                fresh.get("content_hash"), f"{prefix}.fresh_tasks[{fresh_index}].content_hash"
            )
            if task_id not in fresh_payloads:
                raise ValueError(f"missing protected fresh payload: {task_id}")
            actual_hash = sha256_json(fresh_payloads[task_id])
            if actual_hash != expected_hash:
                raise ValueError(f"fresh payload hash mismatch: {task_id}")

        if (set(motivating) | set(replay)) & fresh_ids_for_case:
            raise ValueError(f"{prefix} motivating/replay task ids overlap the fresh set")

        negative_ids = _require_string_list(
            case.get("negative_variant_ids"), f"{prefix}.negative_variant_ids"
        )
        for variant_id in negative_ids:
            if variant_id in referenced_negative:
                raise ValueError(f"negative variant id must be globally unique: {variant_id}")
            referenced_negative.add(variant_id)
            if variant_id not in negative_payloads:
                raise ValueError(f"missing retained negative variant payload: {variant_id}")

    global_split_overlap = referenced_nonfresh & referenced_fresh
    if global_split_overlap:
        raise ValueError(
            "motivating/replay task ids must be globally disjoint from fresh task ids: "
            f"{sorted(global_split_overlap)}"
        )
    if _surface_sets_conflict(allowed_surfaces, protected_surfaces, prefix="suite"):
        raise ValueError("allowed_change_surface overlaps protected_surface across cases")

    if observed_causes != ROOT_CAUSES:
        missing = sorted(ROOT_CAUSES - observed_causes)
        extra = sorted(observed_causes - ROOT_CAUSES)
        raise ValueError(f"suite must cover all eight root-cause families; missing={missing}, extra={extra}")

    # The ordinal a candidate can read is the position in the *published* packet,
    # which freeze_protected_suite emits in sorted case_id order; the ordinal an
    # author works in is the position in the `cases` array. A suite has to be
    # independent of both, and when the two permutations agree the second check
    # is free.
    require_ordinal_independence(emitted_assignment, surface="emitted")
    published_assignment = [family_by_case_id[case_id] for case_id in sorted(family_by_case_id)]
    if published_assignment != emitted_assignment:
        require_ordinal_independence(published_assignment, surface="published")

    # The ordinal is not the only published number the family can be a function
    # of. The candidate packet publishes the allowed change surface and the
    # motivating/replay task ids; the manifest publishes every task id, axis set
    # and variant id. Any of them naming the family is the same defect as the
    # ordinal, and this is the same shape of check.
    require_published_field_independence(
        list(cases.values()), emitted_assignment, surface="published"
    )

    orphan_fresh = set(fresh_payloads) - referenced_fresh
    if orphan_fresh:
        raise ValueError(f"unreferenced fresh payloads are forbidden: {sorted(orphan_fresh)}")
    orphan_negative = set(negative_payloads) - referenced_negative
    if orphan_negative:
        raise ValueError(f"unreferenced negative variants are forbidden: {sorted(orphan_negative)}")


def _root_commitment(root: str, nonce: str) -> str:
    # The nonce stays only in the protected opening material. Hashing one of eight
    # public enum labels without a nonce would be brute-force disclosure.
    return sha256_json({"protected_root_cause": root, "nonce": nonce})


def freeze_protected_suite(raw_suite: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a candidate-safe packet and a protected-suite commitment manifest."""

    validate_protected_suite(raw_suite)
    suite = dict(raw_suite)
    fresh_payloads = _require_mapping(suite["fresh_task_payloads"], "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite["negative_variant_payloads"], "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    candidate_cases: list[dict[str, Any]] = []
    committed_cases: list[dict[str, Any]] = []
    motivating_replay_split: list[dict[str, Any]] = []
    fresh_split: list[dict[str, Any]] = []

    for case_id in sorted(cases):
        case = cases[case_id]
        motivating = list(case["motivating_tasks"])
        replay = list(case["replay_tasks"])
        fresh_tasks = sorted(case["fresh_tasks"], key=lambda item: item["task_id"])
        negative_ids = sorted(case["negative_variant_ids"])

        candidate_cases.append(
            {
                "case_id": case_id,
                "visible_symptom": case["visible_symptom"],
                "candidate_visible_context": case["candidate_visible_context"],
                "motivating_tasks": motivating,
                "replay_tasks": replay,
                "allowed_change_surface": list(case["allowed_change_surface"]),
            }
        )

        nonce = case["root_cause_nonce"]
        fresh_commitments = [
            {
                "task_id": fresh["task_id"],
                "changed_axes": sorted(fresh["changed_axes"]),
                "content_commitment": _protected_commitment(
                    fresh_payloads[fresh["task_id"]],
                    nonce,
                    kind=f"fresh-task:{fresh['task_id']}",
                ),
            }
            for fresh in fresh_tasks
        ]
        negative_commitments = [
            {
                "variant_id": variant_id,
                "content_commitment": _protected_commitment(
                    negative_payloads[variant_id], nonce, kind=f"negative-variant:{variant_id}"
                ),
            }
            for variant_id in negative_ids
        ]
        committed_cases.append(
            {
                "case_id": case_id,
                "case_artifact_commitment": _protected_commitment(
                    case, nonce, kind=f"case:{case_id}"
                ),
                "root_cause_commitment": _root_commitment(
                    case["protected_root_cause"], nonce
                ),
                "fresh_tasks": fresh_commitments,
                "negative_variants": negative_commitments,
                "protected_surface_commitment": _protected_commitment(
                    sorted(case["protected_surface"]), nonce, kind="protected-surface"
                ),
                "success_rubric_commitment": _protected_commitment(
                    case["success_rubric"], nonce, kind="success-rubric"
                ),
                "harm_rubric_commitment": _protected_commitment(
                    case["harm_rubric"], nonce, kind="harm-rubric"
                ),
            }
        )
        require_opening_separation(
            case,
            committed_cases[-1],
            fresh_payloads=fresh_payloads,
            negative_payloads=negative_payloads,
            prefix=f"case {case_id}",
        )
        motivating_replay_split.append(
            {"case_id": case_id, "motivating_tasks": motivating, "replay_tasks": replay}
        )
        fresh_split.append({"case_id": case_id, "fresh_tasks": fresh_commitments})

    candidate_packet: dict[str, Any] = {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "empirical_authority": "NONE",
        "cases": candidate_cases,
    }
    commitment_manifest: dict[str, Any] = {
        "schema_version": COMMITMENT_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "created_before_outcome_access": True,
        "empirical_authority": "CANNOT_CHECK",
        "full_protected_suite_hash": sha256_json(suite),
        "candidate_packet_hash": sha256_json(candidate_packet),
        "evaluator_hash": suite["evaluator_hash"],
        "motivating_replay_split_hash": sha256_json(motivating_replay_split),
        "fresh_transfer_split_hash": sha256_json(fresh_split),
        "fresh_payload_commitment_set_hash": sha256_json(fresh_split),
        "negative_variant_commitment_set_hash": sha256_json(
            [
                {"case_id": case["case_id"], "negative_variants": case["negative_variants"]}
                for case in committed_cases
            ]
        ),
        "root_cause_family_count": len(ROOT_CAUSES),
        "case_count": len(cases),
        "cases": committed_cases,
    }

    # The last thing the freeze does is read its own output back. The split
    # between what is published and what is sealed is enforced above by writing
    # the right keys into the right dictionary, which is a split enforced by
    # attention; this is the same split enforced by search, so a field a later
    # edit adds to the packet is caught by its content rather than by its name.
    leaks = published_surface_leaks(
        {"candidate_packet": candidate_packet, "commitment_manifest": commitment_manifest},
        cases=list(cases.values()),
    )
    if leaks:
        raise ValueError(
            "the freeze would publish sealed material: "
            f"{', '.join(leaks[:6])}{', ...' if len(leaks) > 6 else ''}. "
            "PROTECTED_SUITE_FREEZE_V1.md holds these fields outside candidate-readable "
            "custody; publishing one of them cuts the commitment's domain or opens it"
        )
    return candidate_packet, commitment_manifest


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    # Import lazily: freeze_cli imports the frozen semantic API from this module.
    # Delaying the import until execution avoids a module-import cycle while
    # ensuring every executable entrypoint uses the same custody-safe wrapper.
    from .freeze_cli import main as secure_main

    return secure_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
