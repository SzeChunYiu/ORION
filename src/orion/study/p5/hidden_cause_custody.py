"""What actually protects P5's hidden-cause suite, measured rather than declared.

The suite at ``papers/paper-05-self-orion/evidence/hidden-cause-suite/
PROTECTED_SUITE_V1.json`` is the only battery P5 has run. Its 24 cases carry the
protected root cause the candidate must diagnose, and three separate devices are
supposed to keep that label away from the candidate:

* the freeze splits the suite into a candidate packet and a commitment manifest,
  so the label is published only as ``H({protected_root_cause, nonce})``;
* ``validate_protected_suite`` fails closed on nine documented conditions,
  including "a hidden root label has no unique nonzero 256-bit nonce";
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
from orion.study.p5.freeze import ROOT_CAUSES, sha256_json

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
FREEZE_CANARY = SchemeCanary(
    secret="METHOD_BASIS_GAP",
    nonce="7f" * 32,
    digest="3b8530a57e9adbf6c22b31869cd615fbf65a495b76c2d0205ab450b716b20252",
)


def _ordinal_nonce(sealed: SealedSecret) -> tuple[str, ...]:
    return (f"{sealed.ordinal:064x}",)


def _small_integer_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    # 4096 covers any counter a case generator plausibly runs to, and states the
    # attack's cost as a number rather than leaving it as "small".
    return tuple(f"{value:064x}" for value in range(4096))


def _constant_nonces(sealed: SealedSecret) -> tuple[str, ...]:
    # The values a placeholder leaves behind. The all-zero nonce is included even
    # though validate_protected_suite rejects it, because that rejection is the
    # entire entropy check the freeze performs and this records its coverage.
    return (
        "0" * 64,
        "a" * 64,
        "f" * 64,
        hashlib.sha256(b"").hexdigest(),
    )


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
            "a sweep over the first 4096 integers, the range any generator loop counter "
            "falls in; bounded above by 4096 x 8 digests per case on ordinary hardware"
        ),
    ),
    DisclosureProbe(
        probe_id="constant-nonce",
        kind=DisclosureKind.CONSTANT,
        nonce_candidates=_constant_nonces,
        cost_rationale=(
            "four fixed placeholders a fixture leaves behind - all-zero, all-a, all-f and "
            "the digest of the empty string; 32 digests for the whole manifest"
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
    budget_digests: int = 1_000_000,
) -> CustodyAudit:
    """Attack the commitments this suite would publish, with the declared cheap probes."""

    return audit_commitment_custody(
        custody_id=CUSTODY_ID,
        secrets=sealed_root_causes(cases),
        probes=P5_DISCLOSURE_PROBES,
        scheme=root_cause_commitment,
        canary=FREEZE_CANARY,
        budget_digests=budget_digests,
    )


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
    budget_digests: int = 1_000_000,
) -> dict[str, Any]:
    """Full audit: commitment custody, per-family identifiability, and a roll-up.

    The roll-up is non-compensatory in the same way ``worst_outcome`` is: a
    ``FAIL`` anywhere dominates, a ``CANNOT_CHECK`` anywhere blocks. A suite that
    leaks its labels through the ordinal is not partly usable because its
    commitment scheme is sound, and vice versa.
    """

    cases = list(suite.get("cases") or [])
    custody = audit_suite_custody(cases, budget_digests=budget_digests)
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
        "suite_id": suite.get("suite_id", ""),
        "n_cases": len(cases),
        "overall_outcome": overall.value,
        "commitment_custody": custody.as_json(),
        "root_cause_identifiability": [item.as_json() for item in identifiability],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit an ORION-P5 hidden-cause suite for a recoverable protected label"
    )
    parser.add_argument("--suite", type=Path, default=Path(SHIPPED_SUITE_PATH))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--budget-digests", type=int, default=1_000_000)
    args = parser.parse_args(list(argv) if argv is not None else None)

    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    report = audit_hidden_cause_suite(suite, budget_digests=args.budget_digests)
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
    "FREEZE_CANARY",
    "HIDDEN_CAUSE_CUE_NAMES",
    "P5_DISCLOSURE_PROBES",
    "P5_SHORTCUT_PROBES",
    "SHIPPED_SUITE_PATH",
    "audit_hidden_cause_suite",
    "audit_root_cause_identifiability",
    "audit_suite_custody",
    "default_fit_case_ids",
    "extract_hidden_cause_cues",
    "labelled_case",
    "root_cause_commitment",
    "sealed_root_causes",
]
