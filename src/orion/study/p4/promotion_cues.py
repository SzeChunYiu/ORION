"""The judgement-free cues in P4's protected battery, and the audit that reads them.

P4's promotion terminals are defined over scientific obligations: does the
assigned evidence support the claim, does the cited source own the support, is
the checker independent of the answer's lineage, was the evaluator frozen before
the candidate, did search see gold. None of those obligations mentions how many
objects a case carries, which of its fields are null, or how long a string is.

The battery's construction did. Each family is produced by applying one
mutation to a shared base template, and some of those mutations changed the
shape of the case as well as its content. Measured on batteries regenerated from
``papers/paper-04-verified-scientific-discovery/host/generate_protected_cases.py``,
which now carries every construction it has emitted behind ``--construction``:

- ``v1`` --- the construction the published campaign ran against. ``len(evidence)
  == 0`` recovers all 30 ``CANNOT_CHECK`` cases with no false positives, and with
  no evidence object present every per-evidence cue collapses with it.
- ``v2`` --- the first repair. Object counting is dead and
  ``len(evidence[0]["content"])`` is not: it takes five values across the 420
  cases and two of them --- 107 and 122 --- occur only on ``CANNOT_CHECK`` cases.
  ``declared_content_hash is None`` leaks the other half of the family on its
  own. Both hold for every host seed, because the content templates are fixed
  strings and only the tokens interpolated into them are seed-derived. The
  secret seed protected the case ids and nothing about the leak.
- ``v3`` --- the second repair, written against the property rather than a named
  cue, and frozen in
  ``research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md``. Every
  case is shape-identical and families differ only in the values of fields a hard
  gate is defined over. All fourteen probes below report informedness 0.0 on all
  three terminals, on every seed tried.

That is what this module registers as probes, so that P4-U-T2 --- "identifiability
audit shows the benchmark measures the intended competence" --- is a computation
rather than a sentence.

Three probes were enough to condemn ``v1`` and ``v2``. They were not enough to
*clear* anything, and the difference is the whole lesson of the V1-to-V2 repair:
a fix aimed at a named cue has no reason to produce a construction free of cues.
So the register grew, on 2026-08-21, from three probes to fourteen --- one per
class of judgement-free feature a change to the construction could plausibly
introduce: counts anywhere in the view, key sets and their order, missingness in
the pool as well as the evidence list, character-class profiles, template
identity with the opaque tokens masked out, identifier shape, and the length of
every string in the view. It should keep growing. A passing audit says "no
registered cue recovered this label", which is a statement about the probes as
much as about the benchmark.

Most probes are deliberately conservative: they read only counts, field
missingness, string length and character class. Two --- ``string-length-profile``
and ``scalar-value-profile`` --- are deliberately over-inclusive, reaching the
*shapes and values* of fields the obligations are defined over, such as
``evaluator.integrity`` and the chronology round counters. Including them can
only make the audit stricter, never laxer, so the cost of the over-inclusion is
borne by the benchmark rather than hidden by it. One --- ``digest-prefix`` --- is
a control on the instrument rather than on the battery: it reads the leading
nibble of a SHA-256 over seed-derived content, which is noise, and on a ceiling of
0.0 it fires on roughly a fifth of seeds. Reporting that is the honest way to say
what a 0.0 ceiling can and cannot distinguish.
"""

from __future__ import annotations

import hashlib
import json
import re
import string
from collections.abc import Hashable, Iterable, Mapping
from typing import Any

from orion.programme.benchmark_identifiability import (
    CaseSplit,
    CueKind,
    IdentifiabilityAudit,
    LabelledCase,
    ShortcutProbe,
    audit_label_identifiability,
)
from orion.programme.guard_exercise import GuardExercise

#: Custody classes emitted by the protected-case generator, mapped to the side of
#: the boundary they sit on. ``PUBLIC_*`` is what the protocol lets a candidate
#: see before scoring, so it is the only honest place to fit a shortcut rule;
#: everything protected is what the rule must then be scored on.
CUSTODY_SPLITS: Mapping[str, CaseSplit] = {
    "PUBLIC_CLEAN": CaseSplit.FIT,
    "PUBLIC_HOSTILE": CaseSplit.FIT,
    "PROTECTED_HOSTILE": CaseSplit.EVAL,
    "PROTECTED_HOLDOUT": CaseSplit.EVAL,
}

PROMOTION_CUE_NAMES: tuple[str, ...] = (
    "evidence_count",
    "retrieval_pool_count",
    "used_evidence_count",
    "access_request_count",
    "search_trace_count",
    "distinct_source_id_count",
    "declared_content_hash_missing",
    "declared_provenance_hash_missing",
    "evidence_content_lengths",
    "pool_content_lengths",
    "pool_declared_content_hash_missing",
    "pool_declared_provenance_hash_missing",
    "container_length_profile",
    "key_shape_profile",
    "string_length_profile",
    "scalar_value_profile",
    "non_content_string_shape",
    "evidence_content_template",
    "pool_content_template",
    "evidence_character_profile",
    "pool_character_profile",
    "assigned_content_digest_nibble",
)

#: A run of eight or more hex characters is one of the generator's opaque tokens
#: --- a case id, a support token, a source id, a filler. Masking them leaves the
#: *template* a record was written from and removes every value the template
#: carries, so a probe over the masked form reads which sentence was used and
#: cannot read what was interpolated into it.
_OPAQUE_RUN = re.compile(r"[0-9a-f]{8,}")

_PUNCTUATION = frozenset(string.punctuation)


def _digest_int(value: object) -> int:
    """A stable integer fingerprint of a structural value.

    Integer, not string, on purpose: :func:`extract_promotion_cues` guarantees
    that no cue value is ever a string, which is what makes "this probe cannot
    read a support token, a digest, a lineage or an integrity status" checkable
    rather than asserted. Key names and JSON paths are structure, not case
    content, so fingerprinting them keeps the guarantee while letting a probe
    notice that the structure changed.

    ``hash()`` would not do: it is salted per process, so an audit's verdict
    would not be reproducible across runs, which is exactly what a frozen
    battery forbids.
    """

    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8], 16)


def _template_digest(text: str) -> int:
    """Fingerprint of a string with its opaque tokens masked out."""

    return _digest_int(_OPAQUE_RUN.sub("\x00", text))


def _character_profile(text: str) -> tuple[int, ...]:
    """Length and character-class counts. Reads no word of the string.

    The class counts are taken over the *masked* body and the raw length is
    carried alongside. Counting digits and uppercase over the raw body instead
    would count the hex of the seed-derived tokens, which is noise: the probe
    then acquires a signature per case, generalises to nothing, and reports a
    clean −0.03 on the V2 construction whose label a plain character count
    recovers at 1.0. A probe too fine to generalise is a probe that cannot find a
    leak, which is the failure mode this register exists to avoid.
    """

    masked = _OPAQUE_RUN.sub("\x00", text)
    return (
        len(text),
        len(masked),
        sum(character.isspace() for character in masked),
        sum(character.isdigit() for character in masked),
        sum(character.isupper() for character in masked),
        sum(character in _PUNCTUATION for character in masked),
    )


def _walk_view(
    view: Mapping[str, Any],
) -> tuple[
    dict[str, str], dict[str, int], dict[str, int], dict[str, tuple[str, ...]]
]:
    """Canonical structural walk of one candidate-visible view.

    Returns, keyed by dotted path: every string, the length of every list, the
    value of every integer and boolean, and the key tuple of every mapping *in
    declaration order* so that a reordered object is visible. The strings are
    returned whole because the caller reduces them to a length or a masked
    fingerprint; no string ever reaches a cue value.

    ``None`` leaves are skipped rather than recorded, so a nulled field drops out
    of the path set and changes the path fingerprint. That is deliberate: it
    means the missingness a V2 battery carries is visible to the structural
    probes as well as to the missingness probes, from two independent directions.
    """

    strings: dict[str, str] = {}
    containers: dict[str, int] = {}
    scalars: dict[str, int] = {}
    keysets: dict[str, tuple[str, ...]] = {}

    def walk(node: object, path: str) -> None:
        if isinstance(node, Mapping):
            keysets[path] = tuple(str(key) for key in node)
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))
        elif isinstance(node, (list, tuple)):
            containers[path] = len(node)
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, str):
            strings[path] = node
        elif isinstance(node, bool):
            scalars[path] = int(node)
        elif isinstance(node, int):
            scalars[path] = node

    walk(view, "")
    return strings, containers, scalars, keysets


def _path_keyed(values: Mapping[str, int]) -> tuple[int, ...]:
    """A path-set fingerprint followed by the values, in sorted path order.

    The leading fingerprint is what makes two cases with *different* path sets
    distinguishable even when their remaining values happen to line up; without
    it a probe could be fooled by a field that simply is not there.
    """

    paths = sorted(values)
    return (_digest_int(paths), *(values[path] for path in paths))


def extract_promotion_cues(view: Mapping[str, Any]) -> dict[str, Hashable]:
    """Reduce one candidate-visible view to cues that carry none of the competence.

    Every value here is obtainable by a system that never reads a claim, never
    compares a hash to anything, and never looks for a support token. A rule over
    these values is not a weak implementation of the P4 task; it is not an
    implementation of the P4 task.

    Every value is an integer, a boolean, or a tuple of them. Every P4 obligation
    is a statement about a string in the view --- a support token, a source id, a
    digest, a lineage, an integrity status --- so a cue map with no strings in it
    cannot express the task, and that is a property a test can check.

    Two of these cues are deliberately over-inclusive and are declared as such in
    the freeze document: ``string_length_profile`` measures the length of
    obligation-bearing enums such as ``evaluator.integrity``, and
    ``scalar_value_profile`` reads the round integers ``EVALUATOR_CHRONOLOGY_INTEGRITY``
    is defined over. Including them can only make the audit stricter, never
    laxer, so the cost of the over-inclusion is borne by the benchmark rather
    than hidden by it.
    """

    evidence = list(view.get("evidence") or ())
    pool = list(view.get("retrieval_pool") or ())
    access = list(view.get("access_requests") or ())
    trace = list(view.get("behavioral_trace", {}).get("used_evidence_ids") or ())
    strings, containers, scalars, keysets = _walk_view(view)
    non_content = {
        path: text for path, text in strings.items() if not path.endswith(".content")
    }
    return {
        "evidence_count": len(evidence),
        "retrieval_pool_count": len(pool),
        "used_evidence_count": len(trace),
        "access_request_count": len(access),
        "search_trace_count": len(view.get("search_trace") or ()),
        "distinct_source_id_count": len({item.get("source_id") for item in pool}),
        "declared_content_hash_missing": tuple(
            sorted(item.get("declared_content_hash") is None for item in evidence)
        ),
        "declared_provenance_hash_missing": tuple(
            sorted(item.get("declared_provenance_hash") is None for item in evidence)
        ),
        "evidence_content_lengths": tuple(
            sorted(len(item.get("content") or "") for item in evidence)
        ),
        "pool_content_lengths": tuple(
            sorted(len(item.get("content") or "") for item in pool)
        ),
        "pool_declared_content_hash_missing": tuple(
            sorted(item.get("declared_content_hash") is None for item in pool)
        ),
        "pool_declared_provenance_hash_missing": tuple(
            sorted(item.get("declared_provenance_hash") is None for item in pool)
        ),
        "container_length_profile": _path_keyed(containers),
        "key_shape_profile": tuple(
            (_digest_int(sorted(keysets)),)
            + tuple(_digest_int(keysets[path]) for path in sorted(keysets))
        ),
        "string_length_profile": _path_keyed(
            {path: len(text) for path, text in strings.items()}
        ),
        "scalar_value_profile": _path_keyed(scalars),
        "non_content_string_shape": tuple(
            (_digest_int(sorted(non_content)),)
            + tuple(
                item
                for path in sorted(non_content)
                for item in (
                    len(non_content[path]),
                    _template_digest(non_content[path]),
                )
            )
        ),
        "evidence_content_template": tuple(
            _template_digest(str(item.get("content") or "")) for item in evidence
        ),
        "pool_content_template": tuple(
            _template_digest(str(item.get("content") or "")) for item in pool
        ),
        "evidence_character_profile": tuple(
            value
            for item in evidence
            for value in _character_profile(str(item.get("content") or ""))
        ),
        "pool_character_profile": tuple(
            value
            for item in pool
            for value in _character_profile(str(item.get("content") or ""))
        ),
        "assigned_content_digest_nibble": (
            int(str(evidence[0].get("content_hash") or "0")[0], 16) if evidence else -1
        ),
    }




P4_SHORTCUT_PROBES: tuple[ShortcutProbe, ...] = (
    ShortcutProbe(
        probe_id="evidence-object-count",
        kind=CueKind.COUNT,
        cue_names=("evidence_count", "retrieval_pool_count", "used_evidence_count"),
        cue_rationale=(
            "How many evidence objects a case carries is fixed by the generator, not by "
            "any promotion obligation; the V1 INSUFFICIENT_EVIDENCE construction emitted "
            "an empty list and this probe is what recovered its label"
        ),
    ),
    ShortcutProbe(
        probe_id="declared-hash-missingness",
        kind=CueKind.FIELD_MISSINGNESS,
        cue_names=("declared_content_hash_missing", "declared_provenance_hash_missing"),
        cue_rationale=(
            "Whether a declared hash field is null is a fact about which mutation built "
            "the case; verifying provenance means comparing a declared hash to an actual "
            "one, which this probe never does"
        ),
    ),
    ShortcutProbe(
        probe_id="evidence-content-length",
        kind=CueKind.STRING_SHAPE,
        cue_names=("evidence_content_lengths",),
        cue_rationale=(
            "A character count of the evidence body reads no word of it; the content "
            "templates are fixed strings, so their lengths encode the family that wrote "
            "them and are invariant under the host's secret seed"
        ),
    ),
    # --- registered 2026-08-21 for the V3 repair --------------------------------
    #
    # The V1-to-V2 repair failed because it was scoped to a named cue instead of to
    # the property. These probes exist so that the V3 repair is measured against the
    # property: one probe per class of judgement-free feature a change to the
    # construction could plausibly have introduced.
    ShortcutProbe(
        probe_id="pool-content-length",
        kind=CueKind.STRING_SHAPE,
        cue_names=("pool_content_lengths",),
        cue_rationale=(
            "The V2 leak was measured on the evidence list only; the retrieval pool is "
            "the same bodies seen through a second field, and a character count of them "
            "reads no word either"
        ),
    ),
    ShortcutProbe(
        probe_id="pool-hash-missingness",
        kind=CueKind.FIELD_MISSINGNESS,
        cue_names=(
            "pool_declared_content_hash_missing",
            "pool_declared_provenance_hash_missing",
        ),
        cue_rationale=(
            "Which declared hash is null anywhere in the pool is a fact about which "
            "mutation built the case; the probe never compares a declared hash to an "
            "actual one, which is what verifying provenance would require"
        ),
    ),
    ShortcutProbe(
        probe_id="request-and-trace-count",
        kind=CueKind.COUNT,
        cue_names=(
            "access_request_count",
            "search_trace_count",
            "distinct_source_id_count",
        ),
        cue_rationale=(
            "PROTECTED_ACCESS_CLEAR is defined over the scope and path of a request and "
            "SEARCH_CONTAMINATION_CLEAR over a flag on a query; how many requests, "
            "queries or distinct owners a case carries is a fact about the generator"
        ),
    ),
    ShortcutProbe(
        probe_id="container-length-profile",
        kind=CueKind.COUNT,
        cue_names=("container_length_profile",),
        cue_rationale=(
            "The length of every list in the view at once, so that a count cue moved to "
            "a container nobody thought to name is caught by the same probe as the ones "
            "that were named"
        ),
    ),
    ShortcutProbe(
        probe_id="key-shape",
        kind=CueKind.FIELD_MISSINGNESS,
        cue_names=("key_shape_profile",),
        cue_rationale=(
            "Which keys an object carries and in what order is a fact about how the "
            "generator wrote it; no promotion obligation is a statement about a key set, "
            "and the probe reads a fingerprint of the key names rather than any value"
        ),
    ),
    ShortcutProbe(
        probe_id="content-character-profile",
        kind=CueKind.STRING_SHAPE,
        cue_names=("evidence_character_profile", "pool_character_profile"),
        cue_rationale=(
            "Length plus counts of whitespace, digits, uppercase and punctuation is the "
            "strongest description of a body that reads none of it; it catches a length "
            "cue disguised by padding, which a bare character count would miss"
        ),
    ),
    ShortcutProbe(
        probe_id="content-template-identity",
        kind=CueKind.STRING_SHAPE,
        cue_names=("evidence_content_template", "pool_content_template"),
        cue_rationale=(
            "A fingerprint of the body with its opaque tokens masked out: it identifies "
            "which sentence the generator wrote and cannot read what was interpolated "
            "into it, so it can never compare a support token to a claim's token"
        ),
    ),
    ShortcutProbe(
        probe_id="string-length-profile",
        kind=CueKind.STRING_SHAPE,
        cue_names=("string_length_profile",),
        cue_rationale=(
            "The length of every string in the view at once, deliberately including "
            "obligation-bearing enums such as evaluator.integrity; over-inclusion can "
            "only make the audit stricter, and a length is not a value"
        ),
    ),
    ShortcutProbe(
        probe_id="identifier-shape",
        kind=CueKind.IDENTIFIER_SHAPE,
        cue_names=("non_content_string_shape",),
        cue_rationale=(
            "Length and masked template of every non-content string --- ids, urls, "
            "paths, enums --- so a family that betrayed itself through the shape of an "
            "identifier rather than of a body is caught"
        ),
    ),
    ShortcutProbe(
        probe_id="digest-prefix",
        kind=CueKind.IDENTIFIER_SHAPE,
        cue_names=("assigned_content_digest_nibble",),
        cue_rationale=(
            "The leading hex nibble of a SHA-256 over seed-derived content is noise; it "
            "is registered as a control on the instrument, because a non-zero "
            "informedness here would be the majority-vote rule fitting sampling noise "
            "rather than a property of the battery"
        ),
    ),
    ShortcutProbe(
        probe_id="scalar-value-profile",
        kind=CueKind.ENUM_VALUE,
        cue_names=("scalar_value_profile",),
        cue_rationale=(
            "Every integer and boolean in the view, again over-inclusively: it reads the "
            "round counters EVALUATOR_CHRONOLOGY_INTEGRITY is defined over, so a pass "
            "here is a stronger statement than the register strictly needs"
        ),
    ),
)


def labelled_case(row: Mapping[str, Any]) -> LabelledCase:
    """Turn one protected-manifest row into a case the audit can read.

    Takes the *protected* row rather than the candidate row because the audit
    needs the gold label; the cues come from ``candidate_visible`` only, so no
    protected field ever reaches a probe.
    """

    custody = str(row["custody_class"])
    if custody not in CUSTODY_SPLITS:
        raise ValueError(
            f"{row.get('case_id')}: custody class {custody!r} has no declared split; "
            "an unclassified case would silently leave the audit's eval set"
        )
    return LabelledCase(
        case_id=str(row["case_id"]),
        label=str(row["expected_authority_terminal"]),
        split=CUSTODY_SPLITS[custody],
        cues=extract_promotion_cues(row["candidate_visible"]),
    )


def audit_promotion_terminal(
    rows: Iterable[Mapping[str, Any]],
    *,
    label: str = "CANNOT_CHECK",
    benchmark_id: str = "p4-protected-mechanical-gold",
    max_recovery: float = 0.0,
) -> IdentifiabilityAudit:
    """Audit whether one promotion terminal is recoverable from construction shape.

    ``CANNOT_CHECK`` by default because it is the terminal H3 is computed over,
    and the one whose saturation the V2 campaign reported as a scientific
    negative. The same call with ``label="PROMOTE"`` asks the corresponding
    question of the clean-coverage axis.
    """

    return audit_label_identifiability(
        benchmark_id=benchmark_id,
        label=label,
        cases=[labelled_case(row) for row in rows],
        probes=P4_SHORTCUT_PROBES,
        max_recovery=max_recovery,
    )


def false_promotion_exercise(
    *, arm_id: str, false_promotions: int, promotion_opportunities: int
) -> GuardExercise:
    """P4's headline guard, stated with the denominator it already carries.

    P4 is the well-behaved case for :mod:`orion.programme.guard_exercise`: the
    protected campaign reports ``false_promotions`` and
    ``promotion_opportunities`` side by side, so ORION's zero is a zero over 360
    and not a zero over nothing. Pairing it with an identifiability audit through
    ``AuditedGuardVerdict`` is what asks the next question --- whether those 360
    opportunities test the competence they are named for.
    """

    return GuardExercise(
        guard_id="false_scientific_promotion",
        arm_id=arm_id,
        opportunities=promotion_opportunities,
        violations=false_promotions,
        opportunity_definition=(
            "one protected battery case whose gold authority terminal is not PROMOTE, "
            "on which the system emitted a terminal"
        ),
    )


__all__ = [
    "CUSTODY_SPLITS",
    "P4_SHORTCUT_PROBES",
    "PROMOTION_CUE_NAMES",
    "audit_promotion_terminal",
    "extract_promotion_cues",
    "false_promotion_exercise",
    "labelled_case",
]
