"""The judgement-free cues in P4's protected battery, and the audit that reads them.

P4's promotion terminals are defined over scientific obligations: does the
assigned evidence support the claim, does the cited source own the support, is
the checker independent of the answer's lineage, was the evaluator frozen before
the candidate, did search see gold. None of those obligations mentions how many
objects a case carries, which of its fields are null, or how long a string is.

The battery's construction does. Each family is produced by applying one
mutation to a shared base template, and some of those mutations change the
shape of the case as well as its content. Measured on a battery regenerated
from ``papers/paper-04-verified-scientific-discovery/host/
generate_protected_cases.py`` at seed ``audit-probe-20260821``:

- ``len(evidence[0]["content"])`` takes five values across all 420 cases, and
  two of them --- 107 and 122 --- occur only on ``CANNOT_CHECK`` cases. All 30,
  no false positives.
- ``declared_content_hash is None`` occurs on 15 cases, all ``CANNOT_CHECK``.
- Both hold for every host seed tried, because the content templates are fixed
  strings and only the tokens interpolated into them are seed-derived. The
  secret seed protects the case ids and nothing about the leak.

That is what this module registers as probes, so that P4-U-T2 --- "identifiability
audit shows the benchmark measures the intended competence" --- is a computation
rather than a sentence.

The probes are deliberately conservative. They read only counts, field
missingness and string length. Enum status fields such as
``evaluator.integrity`` or ``search_trace[*].benchmark_gold_visible`` are *not*
probed even though they also separate families, because a defender can fairly
say those fields are the evidence an obligation is defined over. Counts and
character lengths admit no such defence, which is the point: the weakest
possible probe already recovers the label.
"""

from __future__ import annotations

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
)


def extract_promotion_cues(view: Mapping[str, Any]) -> dict[str, Hashable]:
    """Reduce one candidate-visible view to cues that carry none of the competence.

    Every value here is obtainable by a system that never reads a claim, never
    compares a hash to anything, and never looks for a support token. A rule over
    these values is not a weak implementation of the P4 task; it is not an
    implementation of the P4 task.
    """

    evidence = list(view.get("evidence") or ())
    pool = list(view.get("retrieval_pool") or ())
    access = list(view.get("access_requests") or ())
    trace = list(view.get("behavioral_trace", {}).get("used_evidence_ids") or ())
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
