"""What actually protects P5's hidden-cause suite, measured rather than declared.

The suite at ``papers/paper-05-self-orion/evidence/hidden-cause-suite/
PROTECTED_SUITE_V1.json`` is the only battery P5 has run. Its 24 cases carry the
protected root cause the candidate must diagnose, and three separate devices are
supposed to keep that label away from the candidate:

* the freeze splits the suite into a candidate packet and a commitment manifest,
  so the label is published only as ``H({protected_root_cause, nonce})``;
* ``validate_protected_suite`` fails closed on the conditions the protocol
  documents --- nine when this module was written, fourteen now, including "a
  hidden root label has no unique nonzero 256-bit nonce";
* the campaign scores the candidate on the symptom text alone.

All three rest on one integer. ``root_cause_nonce`` is the case ordinal in hex
(``0…01`` … ``0…018``), and ``protected_root_cause`` is the case ordinal divided
by three, indexing the eight families in the order the attribution prompt in
``scripts/run_p5_glm_attribution.py`` prints them. So the commitment opens to a
guess of the ordinal, and the label falls out of the case id without opening
anything.

This module asks both questions as computations:

* :func:`audit_suite_custody` rebuilds the commitments the freeze would publish
  and runs :mod:`orion.programme.commitment_custody` probes against them. On the
  shipped suite the ordinal probe opens 24 of 24 in 108 SHA-256 evaluations.
* :func:`audit_root_cause_identifiability` registers the ordinal as a
  judgement-free cue in :mod:`orion.programme.benchmark_identifiability` terms.
  Fitted on one case per family and scored on the remaining 16, it recovers
  every one of the eight labels at informedness 1.0 with no false positives ---
  where GLM-5.2, reading the symptoms, scored 21 of 24.

The failure record is ``research/failures/
2026-08-invertible-commitment-vacuous-custody/``.

Nothing here weakens the diagnostic work. It bounds it: 21/24 remains an
honest description of one model's output on 24 symptom texts, and stops being
evidence that a hidden cause was hidden.

Which weakness, and what the repair had to be
---------------------------------------------

The message space and the nonce space fail differently and only one of them can
be fixed. The message space *is* small --- eight registered families --- and it
cannot be enlarged, because the label the candidate must produce is one of
those eight by definition. So the eight-digest cost of testing a nonce guess is
permanent, and the entire budget has to be carried by the nonce. That makes the
nonce a per-item salt in everything but name, and the repair is the standard
one: draw it from a CSPRNG (:func:`orion.study.p5.freeze.mint_root_cause_nonce`),
never derive it from anything published, never share it between cases, and
release it only at opening.

A magnitude floor is not that repair. ``f"{2**255 + ordinal:064x}"`` is 64 hex
characters, non-zero, unique per case, and 2**191 times above any floor, and it
opens to the same single guess the ordinal did --- which is what
``floor-evading-counter-nonce`` demonstrates. :func:`orion.study.p5.freeze.nonce_weakness`
therefore rejects *shapes a declared probe generates* rather than *values that
look small*, and the probes here are built from the freeze's own generators, so
the set the freeze refuses and the set the adversary tries cannot drift apart.
:func:`unenforceable_nonces` reports that answer inside the audit.

What the repair does not do
---------------------------

It does not reopen the shipped suite. ``PROTECTED_SUITE_V1.json`` publishes
``protected_root_cause`` in plaintext next to ``root_cause_nonce``, so its
labels are disclosed by the file existing, not by any weakness in the digest
over them; and the ordinal cue survives whatever the nonce is. Re-drawing its
nonces now, after the run was scored, would produce a commitment made by
somebody who already knows the answers, which is not a commitment. The custody
audit on the shipped cases is therefore expected to keep failing, and
:class:`~orion.programme.commitment_custody.ProspectiveScore` is expected to
keep refusing to hold 0.875. The repair is for the next freeze.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Hashable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from orion.programme.benchmark_identifiability import (
    CaseSplit,
    CueKind,
    IdentifiabilityAudit,
    LabelledCase,
    ShortcutProbe,
    audit_label_identifiability,
)
from orion.programme.commitment_custody import (
    CustodyAudit,
    DisclosureKind,
    DisclosureProbe,
    SchemeCanary,
    SealedSecret,
    audit_commitment_custody,
)
from orion.programme.records import Outcome
from orion.study.p5.freeze import (
    COMMITMENT_KINDS,
    ROOT_CAUSES,
    constant_nonces,
    nonce_weakness,
    published_field_nonces,
    sha256_json,
)

SHIPPED_SUITE_PATH = "papers/paper-05-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json"

CUSTODY_ID = "p5-hidden-cause-root-cause-commitment"
BENCHMARK_ID = "p5-hidden-cause-suite"

#: Cases per root-cause family in the shipped suite. The suite is emitted as
#: eight consecutive blocks of this size, which is what makes the ordinal a cue.
CASES_PER_FAMILY = 3

DOMAIN_RATIONALE = (
    "orion.study.p5.freeze.ROOT_CAUSES is a registered public enum of eight families, "
    "printed in full in the attribution prompt; an adversary knows the secret is one of them"
)


def root_cause_commitment(root_cause: str, nonce: str) -> str:
    """The digest the freeze publishes for one protected root cause.

    Modelled from ``orion.study.p5.freeze._root_commitment`` through that
    module's public ``sha256_json`` rather than imported, so the audit describes
    the *published* scheme and a divergence shows up as a canary mismatch
    instead of silently tracking a refactor. ``test_hidden_cause_custody`` pins
    the two together against a live ``freeze_protected_suite`` run.
    """

    return sha256_json({"protected_root_cause": root_cause, "nonce": nonce})


#: A ``(secret, nonce, digest)`` triple emitted by ``freeze_protected_suite`` and
#: re-derived from a live freeze by the unit tests. Its only job is to make an
#: audit whose scheme model has drifted report ``SCHEME_NOT_DEMONSTRATED``
#: instead of "no commitment was opened".
#:
#: The nonce was ``"7f" * 32`` until the freeze learned to refuse a repeated
#: block, at which point the canary became a triple the real freeze could no
#: longer emit --- a canary that fails its own instrument. It is now a fixed
#: 256-bit value that ``nonce_weakness`` clears, so the triple stays reproducible
#: and stays something a freeze would accept. Fixed rather than drawn, because a
#: canary has to be a constant to be checked against.
FREEZE_CANARY = SchemeCanary(
    secret="METHOD_BASIS_GAP",
    nonce="fb5f297ce3c11215576e39fff4aad5458b2871126a96d12063d08ffb78da047f",
    digest="93b7228a27dd7abeef2ab0f37d7c3079db7e09c798a9542db8989d8d65c23f7e",
)


#: How far each unbounded probe sweeps. Both are stated as numbers rather than
#: as "small" because a probe's finding is the pair (what it opened, what it
#: spent), and a budget nobody can quote is a budget nobody can argue is within
#: an adversary's reach.
SMALL_INTEGER_SWEEP = 16_384
FLOOR_EVASION_SWEEP = 1_024

#: Bases for the counters that clear a magnitude floor without gaining entropy.
#: This family is the reason a floor is not a repair: `f"{2**255 + ordinal:064x}"`
#: is 64 hex characters, non-zero, unique per case, far above 2**64, and opens to
#: the same one guess the ordinal did.
_FLOOR_EVASION_BASES: tuple[int, ...] = (
    1 << 64,
    1 << 65,
    1 << 128,
    1 << 192,
    1 << 255,
    (1 << 256) - 1 - FLOOR_EVASION_SWEEP,
    int("deadbeef" * 8, 16) & ~0xFFFF,
    int("cafebabe" * 8, 16) & ~0xFFFF,
)

#: Per-probe digest ceiling for the P5 audit. Above the 3,145,728 evaluations the
#: widest probe spends against a 24-case suite, so a probe that opens nothing
#: reports WITHHELD_UNDER_ENUMERATION rather than BUDGET_EXHAUSTED: the sweep
#: finished and found nothing, which is a different fact from running out of money.
DISCLOSURE_BUDGET_DIGESTS = 5_000_000


def _ordinal_nonce(sealed: SealedSecret) -> tuple[str, ...]:
    return (f"{sealed.ordinal:064x}",)


def _small_integer_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    return tuple(f"{value:064x}" for value in range(SMALL_INTEGER_SWEEP))


def _floor_evading_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    mask = (1 << 256) - 1
    return tuple(
        f"{(base + counter) & mask:064x}"
        for base in _FLOOR_EVASION_BASES
        for counter in range(FLOOR_EVASION_SWEEP)
    )


def _constant_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    # Taken from freeze.constant_nonces rather than restated, so the set the
    # freeze refuses and the set the adversary tries cannot drift apart. The
    # all-zero nonce is included even though the freeze has always rejected it,
    # because that rejection used to be the entire entropy check and this records
    # its coverage.
    return tuple(sorted(constant_nonces()))


def _case_id_digest_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    return (
        hashlib.sha256(sealed.secret_id.encode("utf-8")).hexdigest(),
        sha256_json(sealed.secret_id),
    )


P5_DISCLOSURE_PROBES: tuple[DisclosureProbe, ...] = (
    DisclosureProbe(
        probe_id="ordinal-nonce",
        kind=DisclosureKind.ORDINAL,
        nonce_candidates=_ordinal_nonce,
        cost_rationale=(
            "one guess per case that the nonce is the case's 1-based position rendered as "
            "64 hex characters; costs at most one digest per family in the public enum"
        ),
    ),
    DisclosureProbe(
        probe_id="small-integer-nonce",
        kind=DisclosureKind.SMALL_INTEGER,
        nonce_candidates=_small_integer_nonces,
        cost_rationale=(
            f"a sweep over the first {SMALL_INTEGER_SWEEP} integers, the range any generator "
            f"loop counter falls in; bounded above by {SMALL_INTEGER_SWEEP} x 8 digests per "
            "case, seconds of ordinary hardware"
        ),
    ),
    DisclosureProbe(
        probe_id="floor-evading-counter-nonce",
        kind=DisclosureKind.SMALL_INTEGER,
        nonce_candidates=_floor_evading_nonces,
        cost_rationale=(
            f"the same counter sweep offset by {len(_FLOOR_EVASION_BASES)} round bases -- "
            "powers of two, the top of the range, and two repeated-word patterns -- which is "
            "what a generator emits when it is told only that its nonce must not look small; "
            f"{len(_FLOOR_EVASION_BASES) * FLOOR_EVASION_SWEEP} candidates per case"
        ),
    ),
    DisclosureProbe(
        probe_id="constant-nonce",
        kind=DisclosureKind.CONSTANT,
        nonce_candidates=_constant_nonces,
        cost_rationale=(
            f"the {len(constant_nonces())} fixed placeholders a fixture leaves behind -- "
            "single-digit repeats, repeated words, and the digests of the empty and default "
            "seeds; well under a thousand digests for the whole manifest"
        ),
    ),
    DisclosureProbe(
        probe_id="case-id-digest-nonce",
        kind=DisclosureKind.PUBLISHED_FIELD,
        nonce_candidates=_case_id_digest_nonces,
        cost_rationale=(
            "the two obvious derivations of a nonce from the case id the manifest already "
            "publishes; a probe that opens nothing, kept so the set is not all-positive"
        ),
    ),
)


def _published_field_probe(
    cases: Sequence[Mapping[str, Any]], *, suite_id: str
) -> DisclosureProbe:
    """Every nonce derivable from a field published beside the commitment.

    Wider than ``case-id-digest-nonce`` and case-aware, so it can reach the
    symptom text and the suite id as well as the case id. Built from
    ``freeze.published_field_nonces`` so that the derivations the freeze refuses
    and the derivations the adversary tries are the same list.
    """

    index = {
        str(case["case_id"]): (case, ordinal)
        for ordinal, case in enumerate(cases, start=1)
    }

    def candidates(sealed: SealedSecret) -> tuple[str, ...]:
        found = index.get(sealed.secret_id)
        if found is None:
            return _case_id_digest_nonces(sealed)
        case, ordinal = found
        return tuple(sorted(published_field_nonces(case, ordinal=ordinal, suite_id=suite_id)))

    return DisclosureProbe(
        probe_id="published-field-nonce",
        kind=DisclosureKind.PUBLISHED_FIELD,
        nonce_candidates=candidates,
        cost_rationale=(
            "every SHA-256, SHA-512-truncated and canonical-JSON derivation of the case id, "
            "the case ordinal, the visible symptom and the suite id -- all of which the "
            "manifest publishes; about twenty candidates per case"
        ),
    )


def _reused_nonce_probe(cases: Sequence[Mapping[str, Any]]) -> DisclosureProbe:
    """One opening's nonce, tried against every other case.

    This is the probe that decides whether the salt is per-item. A scheme with a
    single high-entropy salt shared across the suite passes every shape rule
    above and is still not a commitment: the first authorised opening hands the
    adversary all 24. P5 is not hypothetical about this -- ``evidence/tables/
    P5-ATTRIBUTION_RESIDUAL_ERRORS.json`` names three golds outright and
    ``evidence/glm-5.2-attribution/report.json`` lists every family's case ids,
    so the suite already discloses openings.

    A case's own nonce is excluded from its own candidate list: a case whose
    opening the adversary was handed is disclosed by assumption, and counting it
    would report the assumption back as a finding.
    """

    pairs = tuple(
        (str(case["case_id"]), str(case.get("root_cause_nonce", ""))) for case in cases
    )

    def candidates(sealed: SealedSecret) -> tuple[str, ...]:
        return tuple(
            nonce for case_id, nonce in pairs if nonce and case_id != sealed.secret_id
        )

    return DisclosureProbe(
        probe_id="reused-nonce",
        kind=DisclosureKind.RECOVERED_ELSEWHERE,
        nonce_candidates=candidates,
        cost_rationale=(
            "the nonces of the other cases, as an adversary holding one authorised opening "
            "would try them; n-1 candidates per case, and the only probe that can tell a "
            "per-case salt from one suite-wide salt"
        ),
    )


def disclosure_probes_for(
    cases: Sequence[Mapping[str, Any]], *, suite_id: str = ""
) -> tuple[DisclosureProbe, ...]:
    """The registered probes, plus the two that need the cases to be constructed."""

    return P5_DISCLOSURE_PROBES + (
        _published_field_probe(cases, suite_id=suite_id),
        _reused_nonce_probe(cases),
    )


def sealed_root_causes(cases: Sequence[Mapping[str, Any]]) -> tuple[SealedSecret, ...]:
    """Rebuild the root-cause commitments a freeze of ``cases`` would publish.

    Taken from the suite rather than from a manifest on disk, because the point
    is to answer the question *before* the manifest is published. A freeze whose
    commitments are already open should never reach a candidate-readable branch.
    """

    return tuple(
        SealedSecret(
            secret_id=str(case["case_id"]),
            digest=root_cause_commitment(
                str(case["protected_root_cause"]), str(case["root_cause_nonce"])
            ),
            domain=tuple(sorted(ROOT_CAUSES)),
            domain_rationale=DOMAIN_RATIONALE,
            ordinal=index,
        )
        for index, case in enumerate(cases, start=1)
    )


def audit_suite_custody(
    cases: Sequence[Mapping[str, Any]],
    *,
    suite_id: str = "",
    budget_digests: int = DISCLOSURE_BUDGET_DIGESTS,
) -> CustodyAudit:
    """Attack the commitments this suite would publish, with the declared cheap probes."""

    return audit_commitment_custody(
        custody_id=CUSTODY_ID,
        secrets=sealed_root_causes(cases),
        probes=disclosure_probes_for(cases, suite_id=suite_id),
        scheme=root_cause_commitment,
        canary=FREEZE_CANARY,
        budget_digests=budget_digests,
    )


def unenforceable_nonces(
    cases: Sequence[Mapping[str, Any]], *, suite_id: str = ""
) -> tuple[tuple[str, str], ...]:
    """``(case_id, weakness)`` for every nonce ``validate_protected_suite`` would refuse.

    The custody audit and the freeze validator answer the same question from
    opposite ends --- can a cheap adversary find this nonce --- and this is the
    one call that reports the validator's answer in the audit's vocabulary. A
    suite with an empty result here is one whose nonces no registered probe can
    generate, which is what the audit then tries to falsify by generating them.
    """

    findings: list[tuple[str, str]] = []
    for ordinal, case in enumerate(cases, start=1):
        nonce = str(case.get("root_cause_nonce", ""))
        if len(nonce) != 64:
            findings.append((str(case.get("case_id", "")), "not a 64-character hex nonce"))
            continue
        try:
            weakness = nonce_weakness(nonce, case=case, ordinal=ordinal, suite_id=suite_id)
        except ValueError:
            weakness = "not a hex nonce"
        if weakness is not None:
            findings.append((str(case.get("case_id", "")), weakness))
    return tuple(findings)


# --- The cheapest of the seven commitment kinds, not the one the probes attack


#: What a declared adversary tries for each commitment kind's *payload*, as
#: templates over the fields a freeze publishes. The probes above attack the
#: root-cause commitment, whose domain is the eight public labels; these say what
#: the other six cost, which is the number that decides what opening a case is
#: actually worth. A template is a fair adversary here for the same reason the
#: nonce shapes are: it is what a generator writes when nobody told it the field
#: was secret, and the generator's source is in the repository.
_RUBRIC_PREFIXES: dict[str, tuple[str, ...]] = {
    "success-rubric": ("SECRET_SUCCESS_RUBRIC", "SUCCESS_RUBRIC", "success-rubric"),
    "harm-rubric": ("SECRET_HARM_RUBRIC", "HARM_RUBRIC", "harm-rubric"),
}


def _published_tokens(case: Mapping[str, Any], *, ordinal: int) -> tuple[str, ...]:
    """The strings a payload template can be built out of, all of them published."""

    case_id = str(case.get("case_id", ""))
    words: list[str] = [f"{ordinal:03d}", str(ordinal), case_id]
    for surface in case.get("allowed_change_surface") or []:
        words.extend(part for part in str(surface).replace(".", "/").split("/") if part)
    return tuple(dict.fromkeys(words))


def commitment_payload_candidates(
    case: Mapping[str, Any], *, ordinal: int
) -> dict[str, tuple[Any, ...]]:
    """``kind prefix -> the payloads a declared adversary tries``.

    ``case`` is deliberately empty: the case artifact commitment binds the whole
    case object, which contains the opening nonce, so there is no template over
    published fields that reproduces it. That kind is protected by its payload
    rather than by its nonce, and saying so is part of the measurement.
    """

    tokens = _published_tokens(case, ordinal=ordinal)
    return {
        "case": (),
        "root-cause": tuple(sorted(ROOT_CAUSES)),
        "protected-surface": tuple(
            [f"protected/evaluator/{token}_quality.json"] for token in tokens
        )
        + tuple([f"protected/evaluator/{token}.json"] for token in tokens),
        "success-rubric": tuple(
            f"{prefix}_{token}"
            for prefix in _RUBRIC_PREFIXES["success-rubric"]
            for token in tokens
        ),
        "harm-rubric": tuple(
            f"{prefix}_{token}"
            for prefix in _RUBRIC_PREFIXES["harm-rubric"]
            for token in tokens
        ),
        "fresh-task": tuple(
            {"instructions": f"withheld fresh-transfer payload, slot {token}"}
            for token in tokens
        ),
        "negative-variant": tuple(
            {"instructions": f"withheld negative variant, slot {token}"} for token in tokens
        ),
    }


def _true_payloads(
    case: Mapping[str, Any],
    *,
    fresh_payloads: Mapping[str, Any],
    negative_payloads: Mapping[str, Any],
) -> dict[str, tuple[Any, ...]]:
    fresh = [item for item in (case.get("fresh_tasks") or []) if isinstance(item, Mapping)]
    return {
        "case": (case,),
        "root-cause": (str(case.get("protected_root_cause", "")),),
        "protected-surface": (sorted(case.get("protected_surface") or []),),
        "success-rubric": (case.get("success_rubric"),),
        "harm-rubric": (case.get("harm_rubric"),),
        "fresh-task": tuple(
            fresh_payloads[str(item.get("task_id", ""))]
            for item in fresh
            if str(item.get("task_id", "")) in fresh_payloads
        ),
        "negative-variant": tuple(
            negative_payloads[str(variant_id)]
            for variant_id in (case.get("negative_variant_ids") or [])
            if str(variant_id) in negative_payloads
        ),
    }


def cheapest_nonce_rank(
    cases: Sequence[Mapping[str, Any]], *, suite_id: str = ""
) -> tuple[int | None, ...]:
    """For each case, how many guesses the cheapest declared probe spends on its nonce.

    ``None`` where no declared probe generates the nonce at all, which is what a
    ``mint_root_cause_nonce()`` draw looks like from here. Read off the same probe
    list the custody audit runs, so the two cannot disagree about what a cheap
    nonce is.
    """

    probes = disclosure_probes_for(cases, suite_id=suite_id)
    sealed = sealed_root_causes(cases)
    ranks: list[int | None] = []
    for case, secret in zip(cases, sealed):
        nonce = str(case.get("root_cause_nonce", ""))
        best: int | None = None
        for probe in probes:
            candidates = probe.nonce_candidates(secret)
            if nonce in candidates:
                rank = list(candidates).index(nonce) + 1
                best = rank if best is None else min(best, rank)
        ranks.append(best)
    return tuple(ranks)


def audit_commitment_kind_domains(
    suite: Mapping[str, Any],
) -> dict[str, Any]:
    """What each commitment kind costs to open, and which kind is the cheapest.

    The seven disclosure probes attack the root-cause commitment because that is
    the secret the study is about. Every kind shares the case's nonce, so the
    cheapest kind is what an adversary actually pays: a kind whose payload one
    template reproduces costs ``nonce guesses x 1``, and confirming it confirms
    the nonce for the other six.

    Per-kind rows carry counts and never a recovered payload: this report is a
    thing a caller may write down, and a protected surface or a rubric printed
    into it would be the disclosure the audit exists to measure.
    """

    cases = list(suite.get("cases") or [])
    suite_id = str(suite.get("suite_id", ""))
    fresh_payloads = suite.get("fresh_task_payloads") or {}
    negative_payloads = suite.get("negative_variant_payloads") or {}
    nonce_ranks = cheapest_nonce_rank(cases, suite_id=suite_id)

    rows: dict[str, dict[str, Any]] = {
        kind: {
            "kind": kind,
            "candidates_declared": 0,
            "payloads_committed": 0,
            "payloads_a_candidate_reproduces": 0,
            "payloads_opened": 0,
            "digests_to_open_every_payload_found": 0,
            "worst_case_open_digests": None,
            "cheapest_open_digests": None,
        }
        for kind in COMMITMENT_KINDS
    }
    for ordinal, case in enumerate(cases, start=1):
        candidates = commitment_payload_candidates(case, ordinal=ordinal)
        actual = _true_payloads(
            case, fresh_payloads=fresh_payloads, negative_payloads=negative_payloads
        )
        nonce_rank = nonce_ranks[ordinal - 1]
        for kind, row in rows.items():
            declared = candidates[kind]
            row["candidates_declared"] = max(row["candidates_declared"], len(declared))
            for payload in actual[kind]:
                row["payloads_committed"] += 1
                serialised = [sha256_json(item) for item in declared]
                if sha256_json(payload) not in serialised:
                    continue
                row["payloads_a_candidate_reproduces"] += 1
                if nonce_rank is None:
                    continue
                rank = serialised.index(sha256_json(payload)) + 1
                cost = rank * nonce_rank
                row["payloads_opened"] += 1
                row["digests_to_open_every_payload_found"] += cost
                cheapest = row["cheapest_open_digests"]
                row["cheapest_open_digests"] = cost if cheapest is None else min(cheapest, cost)
                worst = row["worst_case_open_digests"]
                row["worst_case_open_digests"] = cost if worst is None else max(worst, cost)

    openable = [row for row in rows.values() if row["payloads_opened"]]
    cheapest = min(
        openable,
        key=lambda row: (
            row["digests_to_open_every_payload_found"] / row["payloads_opened"],
            row["kind"],
        ),
        default=None,
    )
    return {
        "schema_version": "orion.p5.commitment-kind-domain-audit.v1",
        "suite_id": suite_id,
        "n_cases": len(cases),
        "commitment_kinds": list(COMMITMENT_KINDS),
        "nonce_guesses_the_cheapest_probe_spends": [
            {"case_id": str(case.get("case_id", "")), "nonce_rank": rank}
            for case, rank in zip(cases, nonce_ranks)
        ],
        "cases_with_an_enumerable_nonce": sum(1 for rank in nonce_ranks if rank is not None),
        "kinds": [rows[kind] for kind in COMMITMENT_KINDS],
        "cheapest_kind": None if cheapest is None else cheapest["kind"],
        "cheapest_kind_digests_for_the_suite": (
            None if cheapest is None else cheapest["digests_to_open_every_payload_found"]
        ),
        "root_cause_digests_for_the_suite": rows["root-cause"][
            "digests_to_open_every_payload_found"
        ],
        "payload_templates_note": (
            "payloads_a_candidate_reproduces counts payloads a declared template "
            "reproduces; payloads_opened counts those whose nonce a declared probe also "
            "generates. A suite can have a one-candidate payload domain on every kind and "
            "still open nothing, which is what a CSPRNG nonce buys and the only thing it "
            "buys: the templates are public, so the payloads are not what is protecting "
            "these commitments."
        ),
        "note": (
            "A shared opening nonce makes the cheapest kind the price of the case: "
            "confirming any one commitment confirms the nonce, and the root cause then "
            "costs at most eight more digests. Per-kind opening nonces do not change "
            "these numbers -- an adversary who can guess the case nonce derives every "
            "kind's -- they change what one authorised opening discloses, which is what "
            "freeze.require_opening_separation checks."
        ),
    }


HIDDEN_CAUSE_CUE_NAMES: tuple[str, ...] = (
    "case_ordinal_block",
    "nonce_ordinal_block",
    "visible_context_key_count",
)


def extract_hidden_cause_cues(case: Mapping[str, Any]) -> dict[str, Hashable]:
    """Reduce one case to cues that carry none of the diagnostic competence.

    Attributing a hidden cause means reading a symptom and deciding which of
    eight mechanisms produced it. None of these values is a symptom. Where the
    case sits in the emitted order, what integer its nonce encodes and how many
    keys its context object has are all facts about the generator, and a rule
    over them is not a weak diagnostician --- it is not a diagnostician.
    """

    case_id = str(case["case_id"])
    ordinal = int(case_id.rsplit("-", 1)[1])
    nonce_ordinal = int(str(case["root_cause_nonce"]), 16)
    context = case.get("candidate_visible_context") or {}
    return {
        "case_ordinal_block": (ordinal - 1) // CASES_PER_FAMILY,
        "nonce_ordinal_block": (nonce_ordinal - 1) // CASES_PER_FAMILY,
        "visible_context_key_count": len(context),
    }


P5_SHORTCUT_PROBES: tuple[ShortcutProbe, ...] = (
    ShortcutProbe(
        probe_id="case-id-ordinal-block",
        kind=CueKind.ORDINAL_POSITION,
        cue_names=("case_ordinal_block",),
        cue_rationale=(
            "the case's position in the emitted order, divided by the block size; reads no "
            "symptom, no context value and no root-cause vocabulary"
        ),
    ),
    ShortcutProbe(
        probe_id="nonce-ordinal-block",
        kind=CueKind.IDENTIFIER_SHAPE,
        cue_names=("nonce_ordinal_block",),
        cue_rationale=(
            "the integer the opening nonce encodes, divided by the block size; a nonce is "
            "by construction meant to carry nothing about the case at all"
        ),
    ),
    ShortcutProbe(
        probe_id="visible-context-key-count",
        kind=CueKind.COUNT,
        cue_names=("visible_context_key_count",),
        cue_rationale=(
            "how many keys the candidate-visible context object carries, never their names "
            "or values; kept as the control the suite is entitled to pass"
        ),
    ),
)


def default_fit_case_ids(cases: Sequence[Mapping[str, Any]]) -> frozenset[str]:
    """The first case of each family: what one opened commitment per family reveals.

    P5 has no public/protected split to fit on --- the whole suite is nominally
    protected --- so the fit set has to be justified as something a candidate can
    actually obtain. One label per family is strictly less than the suite already
    publishes: ``evidence/glm-5.2-attribution/report.json`` lists every family's
    case ids, and ``evidence/tables/P5-ATTRIBUTION_RESIDUAL_ERRORS.json`` names
    three golds outright.
    """

    seen: dict[str, str] = {}
    for case in cases:
        family = str(case["protected_root_cause"])
        seen.setdefault(family, str(case["case_id"]))
    return frozenset(seen.values())


def labelled_case(case: Mapping[str, Any], *, split: CaseSplit) -> LabelledCase:
    return LabelledCase(
        case_id=str(case["case_id"]),
        label=str(case["protected_root_cause"]),
        split=split,
        cues=extract_hidden_cause_cues(case),
    )


def audit_root_cause_identifiability(
    cases: Sequence[Mapping[str, Any]],
    *,
    label: str,
    fit_case_ids: Iterable[str] | None = None,
    max_recovery: float = 0.0,
) -> IdentifiabilityAudit:
    """Audit whether one root-cause family is recoverable without reading a symptom."""

    fit = frozenset(fit_case_ids) if fit_case_ids is not None else default_fit_case_ids(cases)
    labelled = [
        labelled_case(
            case,
            split=CaseSplit.FIT if str(case["case_id"]) in fit else CaseSplit.EVAL,
        )
        for case in cases
    ]
    return audit_label_identifiability(
        benchmark_id=BENCHMARK_ID,
        label=label,
        cases=labelled,
        probes=P5_SHORTCUT_PROBES,
        max_recovery=max_recovery,
    )


def audit_hidden_cause_suite(
    suite: Mapping[str, Any],
    *,
    budget_digests: int = DISCLOSURE_BUDGET_DIGESTS,
) -> dict[str, Any]:
    """Full audit: commitment custody, per-family identifiability, and a roll-up.

    The roll-up is non-compensatory in the same way ``worst_outcome`` is: a
    ``FAIL`` anywhere dominates, a ``CANNOT_CHECK`` anywhere blocks. A suite that
    leaks its labels through the ordinal is not partly usable because its
    commitment scheme is sound, and vice versa.
    """

    cases = list(suite.get("cases") or [])
    suite_id = str(suite.get("suite_id", ""))
    custody = audit_suite_custody(cases, suite_id=suite_id, budget_digests=budget_digests)
    families = sorted({str(case["protected_root_cause"]) for case in cases})
    identifiability = tuple(
        audit_root_cause_identifiability(cases, label=family) for family in families
    )

    outcomes = {custody.outcome} | {item.outcome for item in identifiability}
    if Outcome.FAIL in outcomes:
        overall = Outcome.FAIL
    elif Outcome.CANNOT_CHECK in outcomes:
        overall = Outcome.CANNOT_CHECK
    else:
        overall = Outcome.PASS

    return {
        "schema_version": "orion.p5.hidden-cause-custody-audit.v1",
        "suite_id": suite_id,
        "n_cases": len(cases),
        "overall_outcome": overall.value,
        # The work is reported next to the verdict, always. "Nothing was opened"
        # and "nothing was opened in 4.7 million SHA-256 evaluations across six
        # declared adversaries" are different claims, and only the second one is
        # a result. The nonce findings are the freeze validator's answer to the
        # same question, so a suite that would not survive a freeze cannot look
        # clean here just because the probes are bounded.
        "disclosure_budget_digests": budget_digests,
        "digests_computed": sum(item.digests_computed for item in custody.attempts),
        "probes_run": len(custody.attempts),
        "enumerable_nonces": [
            {"case_id": case_id, "weakness": weakness}
            for case_id, weakness in unenforceable_nonces(cases, suite_id=suite_id)
        ],
        "commitment_custody": custody.as_json(),
        "root_cause_identifiability": [item.as_json() for item in identifiability],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit an ORION-P5 hidden-cause suite for a recoverable protected label"
    )
    parser.add_argument("--suite", type=Path, default=Path(SHIPPED_SUITE_PATH))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--budget-digests", type=int, default=DISCLOSURE_BUDGET_DIGESTS)
    parser.add_argument(
        "--contrast-sound-suite",
        action="store_true",
        help=(
            "also generate a custody-sound suite and attack it with the same probes, so "
            "the repair is a comparison a reader can run rather than a claim. The exit "
            "status stays the audited suite's: a demonstration that a sound suite is "
            "buildable does not make a broken one less broken"
        ),
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    report = audit_hidden_cause_suite(suite, budget_digests=args.budget_digests)
    if args.contrast_sound_suite:
        # Imported here, not at module scope: the generator is built on this
        # module's probes and importing it at the top would be a cycle.
        from orion.study.p5.sound_hidden_cause_suite import (
            audit_sound_suite,
            generate_sound_suite,
        )

        report = dict(report)
        report["sound_suite_demonstration"] = audit_sound_suite(
            generate_sound_suite(), budget_digests=args.budget_digests
        )
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["overall_outcome"] == Outcome.PASS.value else 3


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BENCHMARK_ID",
    "CASES_PER_FAMILY",
    "CUSTODY_ID",
    "DISCLOSURE_BUDGET_DIGESTS",
    "FLOOR_EVASION_SWEEP",
    "FREEZE_CANARY",
    "HIDDEN_CAUSE_CUE_NAMES",
    "P5_DISCLOSURE_PROBES",
    "P5_SHORTCUT_PROBES",
    "SHIPPED_SUITE_PATH",
    "SMALL_INTEGER_SWEEP",
    "audit_commitment_kind_domains",
    "audit_hidden_cause_suite",
    "audit_root_cause_identifiability",
    "audit_suite_custody",
    "cheapest_nonce_rank",
    "commitment_payload_candidates",
    "default_fit_case_ids",
    "disclosure_probes_for",
    "extract_hidden_cause_cues",
    "labelled_case",
    "root_cause_commitment",
    "sealed_root_causes",
    "unenforceable_nonces",
]
