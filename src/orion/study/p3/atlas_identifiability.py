"""Ask whether a P3 atlas's gold relation falls out of how its cases were built.

The P4 lane's record (``research/failures/2026-08-label-recoverable-from-construction-cue/``)
is that a well-intentioned repair shipped a new cue: after ``len(evidence) == 0``
was closed as a shortcut to ``INSUFFICIENT_EVIDENCE``, ``len(evidence[0]["content"])``
recovered the same label at informedness 1.0, and nothing in the harness was
positioned to notice because no artifact asked whether the label was recoverable.

Populating two coordinates on 24 constructed cases --- what
``orion.study.p3_coordinate_necessity_build`` does to give
``remove_measurement`` and ``remove_temporal_context`` a denominator --- is
exactly the shape of change that can do this again. This module is the question
asked of a P3 atlas: it reduces each case to judgement-free features of its
*construction* and hands them to
:func:`orion.programme.benchmark_identifiability.audit_label_identifiability`.

The boundary between a cue and the task is drawn once, here: the competence
under test is "given two typed meaning projections, decide the meaning
relation", so the coordinate **values** are the input the system is supposed to
read and no probe touches them. What the probes read is everything around them
--- the id's shape, the family and discipline tokens, the provenance stamp, the
coordinate *cardinalities*, and the lengths of the three projection fields
(``projection_id``, ``source_id``, ``source_span``) that ``compare_meaning``
never reads and ``exact_coordinate_baseline`` explicitly excludes.

Two split modes, both reported. ``in_sample`` enters every case as both ``FIT``
and ``EVAL``, so a probe's lookup is fitted on the cases it is graded on; this
upper-bounds recoverability and removes split-sampling noise a 56-case corpus
cannot absorb. ``hash_parity`` splits on ``sha256(case_id)`` and is the
out-of-sample view. The in-sample mode has a known artifact, recorded in the
freeze document before it was run: a probe whose cue is high-cardinality
memorises the corpus and reports a leak that belongs to the probe rather than
the benchmark. :func:`probe_cardinality_flags` reports each probe's fitted
signature count against the case count so that artifact is visible rather than
argued about.

Protocol: ``research/p3-coordinate-necessity-v1/FREEZE_2026-08-21.md`` §5.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Hashable, Iterable, Mapping, Sequence

from orion.programme.benchmark_identifiability import (
    CaseSplit,
    CueKind,
    IdentifiabilityAudit,
    LabelledCase,
    ShortcutProbe,
    audit_label_identifiability,
)
from orion.programme.records import Outcome
from orion.study.p3_public_reference import load_jsonl

COORDINATE_FIELDS = ("referent_ids", "construct_ids", "measurement_ids", "temporal_context_ids")

#: A probe fitting this share of the corpus or more in distinct signatures is
#: reading a high-cardinality value; under the in-sample split it memorises the
#: cases it scores, which the freeze document disqualifies in advance as an
#: artifact of the probe rather than a property of the benchmark.
HIGH_CARDINALITY_SHARE = 0.25

PROBES: tuple[ShortcutProbe, ...] = (
    ShortcutProbe(
        probe_id="case_id_shape",
        kind=CueKind.IDENTIFIER_SHAPE,
        cue_names=("case_id_length", "case_id_hyphen_count", "case_id_alpha_prefix"),
        cue_rationale=(
            "the length, separator count and leading non-digit run of an opaque case "
            "identifier; naming a case involves no judgement about which meaning "
            "relation holds between its two projections"
        ),
    ),
    ShortcutProbe(
        probe_id="case_family",
        kind=CueKind.ENUM_VALUE,
        cue_names=("case_family",),
        cue_rationale=(
            "the closed-vocabulary token naming which contrast dimension the case was "
            "drawn to probe, read as an opaque token; it names the axis, and a family "
            "that determined the answer would be a construction cue by definition"
        ),
    ),
    ShortcutProbe(
        probe_id="discipline",
        kind=CueKind.ENUM_VALUE,
        cue_names=("discipline",),
        cue_rationale=(
            "the closed-vocabulary discipline stratum the case was sampled into; which "
            "field a pair comes from carries none of the comparison"
        ),
    ),
    ShortcutProbe(
        probe_id="source_provenance",
        kind=CueKind.COUNT,
        cue_names=("source_record_count", "source_datasets"),
        cue_rationale=(
            "how many upstream records the case cites and which datasets they came "
            "from; provenance bookkeeping is fixed by the sampling frame before any "
            "relation is adjudicated"
        ),
    ),
    ShortcutProbe(
        probe_id="gold_authority_stamp",
        kind=CueKind.ENUM_VALUE,
        cue_names=("authority_kind", "authority_has_derivation", "evidence_count"),
        cue_rationale=(
            "the gold record's provenance stamp read as tokens and counts, never its "
            "derivation rule text or evidence strings; how the label was authorised is "
            "not what the label says"
        ),
    ),
    ShortcutProbe(
        probe_id="coordinate_arity",
        kind=CueKind.COUNT,
        cue_names=tuple(
            f"arity_{side}_{field}" for side in ("left", "right") for field in COORDINATE_FIELDS
        ),
        cue_rationale=(
            "how many ids each coordinate tuple holds on each side, never which ids; "
            "cardinality is a shape of the extraction, and this is the P4-shaped cue "
            "that a repair populating a coordinate is most likely to introduce"
        ),
    ),
    ShortcutProbe(
        probe_id="coordinate_missingness",
        kind=CueKind.FIELD_MISSINGNESS,
        cue_names=tuple(
            f"empty_{side}_{field}" for side in ("left", "right") for field in COORDINATE_FIELDS
        ),
        cue_rationale=(
            "which coordinate tuples are empty on each side, irrespective of the values "
            "present; a label that follows from which fields the builder filled in is "
            "recoverable without comparing anything"
        ),
    ),
    ShortcutProbe(
        probe_id="identifier_string_shape",
        kind=CueKind.STRING_SHAPE,
        cue_names=(
            "projection_id_length_left",
            "projection_id_length_right",
            "source_span_length_left",
            "source_span_length_right",
        ),
        cue_rationale=(
            "lengths of the three projection fields the comparison rule provably "
            "ignores --- compare_meaning never reads projection_id, source_id or "
            "source_span, and exact_coordinate_baseline excludes them explicitly"
        ),
    ),
    ShortcutProbe(
        probe_id="ordinal_quartile",
        kind=CueKind.ORDINAL_POSITION,
        cue_names=("ordinal_quartile",),
        cue_rationale=(
            "which quartile of the emitted order the case sits in; where a case lands "
            "in a sorted file is a property of the emission, not of the pair"
        ),
    ),
)


def _alpha_prefix(case_id: str) -> str:
    """The leading run of non-digit characters, as declared in the freeze document."""

    for index, character in enumerate(case_id):
        if character.isdigit():
            return case_id[:index]
    return case_id


def case_cues(case: Mapping[str, object], *, index: int, total: int) -> dict[str, Hashable]:
    """Every judgement-free construction feature of one case, and nothing else."""

    if total <= 0:
        raise ValueError("cue extraction needs a non-empty corpus")
    case_id = str(case["case_id"])
    left = case["left_projection"]
    right = case["right_projection"]
    assert isinstance(left, dict) and isinstance(right, dict)
    expected = case["expected"]
    assert isinstance(expected, dict)
    authority = expected["authority"]
    assert isinstance(authority, dict)
    sources = case["source_records"]
    assert isinstance(sources, list)

    cues: dict[str, Hashable] = {
        "case_id_length": len(case_id),
        "case_id_hyphen_count": case_id.count("-"),
        "case_id_alpha_prefix": _alpha_prefix(case_id),
        "case_family": str(case["case_family"]),
        "discipline": str(case["discipline"]),
        "source_record_count": len(sources),
        "source_datasets": tuple(
            sorted(str(dict(record)["dataset"]) for record in sources)
        ),
        "authority_kind": str(authority.get("kind", "")),
        "authority_has_derivation": "derivation" in authority,
        "evidence_count": len(list(authority.get("evidence", ()))),
        "projection_id_length_left": len(str(left.get("projection_id", ""))),
        "projection_id_length_right": len(str(right.get("projection_id", ""))),
        "source_span_length_left": len(str(left.get("source_span", ""))),
        "source_span_length_right": len(str(right.get("source_span", ""))),
        "ordinal_quartile": min(3, index * 4 // total),
    }
    for side, projection in (("left", left), ("right", right)):
        for field in COORDINATE_FIELDS:
            values = projection.get(field) or []
            cues[f"arity_{side}_{field}"] = len(list(values))
            cues[f"empty_{side}_{field}"] = not values
    return cues


def _label(case: Mapping[str, object]) -> str:
    expected = case["expected"]
    assert isinstance(expected, dict)
    return str(expected["meaning_relation"])


def labelled_cases(
    cases: Sequence[Mapping[str, object]], *, split_mode: str
) -> tuple[LabelledCase, ...]:
    """Reduce an atlas to labelled cue rows under one of the two declared splits."""

    if split_mode not in {"in_sample", "hash_parity"}:
        raise ValueError(f"unknown split mode: {split_mode}")
    rows: list[LabelledCase] = []
    total = len(cases)
    for index, case in enumerate(cases):
        case_id = str(case["case_id"])
        cues = case_cues(case, index=index, total=total)
        label = _label(case)
        if split_mode == "in_sample":
            rows.append(
                LabelledCase(case_id=f"{case_id}@FIT", label=label, split=CaseSplit.FIT, cues=cues)
            )
            rows.append(
                LabelledCase(
                    case_id=f"{case_id}@EVAL", label=label, split=CaseSplit.EVAL, cues=cues
                )
            )
            continue
        digest = hashlib.sha256(case_id.encode("utf-8")).hexdigest()
        split = CaseSplit.FIT if int(digest, 16) % 2 == 0 else CaseSplit.EVAL
        rows.append(LabelledCase(case_id=case_id, label=label, split=split, cues=cues))
    return tuple(rows)


def probe_cardinality_flags(audit: IdentifiabilityAudit, *, cases: int) -> dict[str, bool]:
    """Which probes fitted enough distinct signatures to be memorising the corpus."""

    if cases <= 0:
        raise ValueError("cardinality flags need a non-empty corpus")
    return {
        result.probe_id: result.fitted_signatures >= HIGH_CARDINALITY_SHARE * cases
        for result in audit.results
    }


def audit_atlas_identifiability(
    atlas_id: str,
    cases: Sequence[Mapping[str, object]],
    *,
    max_recovery: float = 0.0,
) -> dict[str, object]:
    """Audit every gold relation the atlas carries, under both declared splits."""

    if not cases:
        raise ValueError("an empty atlas has no label to audit")
    labels = sorted({_label(case) for case in cases})
    audits: dict[str, list[dict[str, object]]] = {}
    outcomes: list[Outcome] = []
    for split_mode in ("in_sample", "hash_parity"):
        rows = labelled_cases(cases, split_mode=split_mode)
        rendered: list[dict[str, object]] = []
        for label in labels:
            audit = audit_label_identifiability(
                benchmark_id=f"{atlas_id}:{split_mode}",
                label=label,
                cases=rows,
                probes=PROBES,
                max_recovery=max_recovery,
            )
            payload = audit.as_json()
            payload["high_cardinality_probes"] = sorted(
                probe_id
                for probe_id, flagged in probe_cardinality_flags(audit, cases=len(cases)).items()
                if flagged
            )
            rendered.append(payload)
            if split_mode == "in_sample":
                outcomes.append(audit.outcome)
        audits[split_mode] = rendered

    if Outcome.FAIL in outcomes:
        overall = Outcome.FAIL
    elif Outcome.CANNOT_CHECK in outcomes:
        overall = Outcome.CANNOT_CHECK
    else:
        overall = Outcome.PASS
    return {
        "schema_version": "orion.p3.atlas-identifiability.v1",
        "atlas_id": atlas_id,
        "n_cases": len(cases),
        "labels": labels,
        "max_recovery": max_recovery,
        "primary_split": "in_sample",
        "overall_outcome": overall.value,
        "probes": [
            {
                "probe_id": probe.probe_id,
                "kind": probe.kind.value,
                "cue_names": list(probe.cue_names),
                "cue_rationale": probe.cue_rationale,
            }
            for probe in PROBES
        ],
        "audits": audits,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a P3 atlas for gold recoverable from construction cues"
    )
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument(
        "--exclude-cases",
        type=Path,
        help="drop every case id present in this atlas, to audit an extension's own cases",
    )
    parser.add_argument("--atlas-id", default="")
    parser.add_argument("--max-recovery", type=float, default=0.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    cases: Sequence[Mapping[str, object]] = load_jsonl(args.cases)
    if args.exclude_cases:
        excluded = {str(case["case_id"]) for case in load_jsonl(args.exclude_cases)}
        cases = [case for case in cases if str(case["case_id"]) not in excluded]
        if not cases:
            print("CANNOT_CHECK: every case was excluded")
            return 3
    report = audit_atlas_identifiability(
        args.atlas_id or args.cases.parent.name, cases, max_recovery=args.max_recovery
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
    "COORDINATE_FIELDS",
    "HIGH_CARDINALITY_SHARE",
    "PROBES",
    "audit_atlas_identifiability",
    "case_cues",
    "labelled_cases",
    "probe_cardinality_flags",
]
