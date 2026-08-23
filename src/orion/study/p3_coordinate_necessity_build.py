"""Extend a frozen P3 atlas with cases whose answer depends on the two absent coordinates.

``orion.study.p3_public_reference_analysis.ablated_relation`` ablates a
coordinate by ``replace(projection, measurement_ids=())``. On both frozen
public-reference atlases ``measurement_ids`` and ``temporal_context_ids`` are
populated on **0 of 32** cases, so that ``replace`` is the identity: the
``remove_measurement`` and ``remove_temporal_context`` arms hand
``compare_meaning`` byte-identical inputs to the full system's and report the
paired difference of a run against itself. The diagnosis is recorded under
``research/failures/2026-08-unapplied-treatment-vacuous-null/`` and measured by
``python -m orion.study.p3.public_reference_audit``.

This module builds the corpus those two arms need. It does not touch either
frozen atlas: it reads one as a parent, copies its cases through unchanged, and
appends constructed cases on which the two coordinates are populated *and*
load-bearing, emitting a new atlas with its own identity and its own hash.

The construction is frozen in
``research/p3-coordinate-necessity-v1/FREEZE_2026-08-21.md``, written before any
case was built or any arm re-run. Two properties of it are worth restating here
because they are what keep the result readable:

**The added cases are synthetic and the artifact says so.** The upstream corpora
the v1.1 builder draws on are not reachable from this environment, and none of
them supplies a pair differing only on a measurement or temporal coordinate.
Gold on the added cases follows from a frozen standard table emitted beside the
atlas, by one stated rule. So this atlas can establish that a coordinate is
load-bearing *in the rule*; it cannot establish that such pairs are frequent in
public scientific corpora, and :func:`build_report` carries that sentence.

**Only the coordinate values vary with the answer.** Every added case has the
same ``case_id`` shape, the same fixed-width ``projection_id``/``source_span``
templates, one source record, one authority kind, one derivation rule and arity
1 on all four coordinate tuples on both sides. The differ cases and the same
cases are indistinguishable at every construction-level feature. That is the
P4 lesson (``research/failures/2026-08-label-recoverable-from-construction-cue/``)
applied before the fact rather than after: a repair that populates a coordinate
is exactly the shape of change that ships a new shortcut cue, and
``orion.study.p3.atlas_identifiability`` is the check that it did not.

The builder refuses to emit an atlas whose differ cases do not actually depend
on their coordinate --- verified with the analysis module's own
``ablated_relation``, so a change to the ablation definitions cannot leave the
extension silently inert. An extension that did not create the dependence would
repeat the failure it repairs, one layer further in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from orion.knowledge.semantics import MeaningRelation
from orion.study.p3_public_reference import (
    canonical_json,
    evaluate_case,
    load_jsonl,
    validate_case,
)
from orion.study.p3_public_reference_analysis import ablated_relation
from orion.study.p3_public_reference_build_v11 import UNIT_DIMENSIONS

PROTOCOL_ID = "P3.coordinate-necessity-extension.v1"
ATLAS_ID = "coordinate-necessity-v1"
SCHEMA_VERSION = "orion.p3.public-reference-case.v1"
STANDARD_FILENAME = "SYNTHETIC_COORDINATE_STANDARD.json"
STANDARD_DATASET = "ORION-P3-SyntheticCoordinateStandard"
DERIVATION_RULE = "identity:frozen-coordinate-standard-distinctness"

COORDINATE_FIELDS = ("referent_ids", "construct_ids", "measurement_ids", "temporal_context_ids")

#: Disciplines cycled by slot so that no discipline is unique to a gold label.
DISCIPLINES = ("biology", "chemistry", "materials", "physics")

#: Slots 0..3 of each stratum differ on the stratum's coordinate; 4..11 agree.
DIFFER_SLOTS = 4
SLOTS_PER_STRATUM = 12

STRATA = {
    "measurement": {
        "case_family": "same_construct_different_measurement",
        "predicate": "reports_quantity",
        "coordinate": "measurement_ids",
    },
    "temporal": {
        "case_family": "same_entity_different_temporal_state",
        "predicate": "reports_observed_state",
        "coordinate": "temporal_context_ids",
    },
}

EXTERNAL_VALIDITY = (
    "The added cases are synthetic: gold follows from the emitted standard table by "
    f"the rule {DERIVATION_RULE}, not from an upstream expert corpus. This atlas can "
    "establish that a coordinate is load-bearing in the comparison rule; it cannot "
    "establish that such pairs are frequent in public scientific corpora, and it may "
    "not be substituted for the public-reference atlas in any external-validity claim."
)

ACCURACY_CAVEAT = (
    "The added cases are an ablation denominator, not an accuracy benchmark. Their gold "
    "is derived by a rule that coincides with what compare_meaning does with these two "
    "coordinates, so the full system answers all of them by construction. That is what an "
    "ablation arm needs --- its question is whether removing the coordinate moves the "
    "decision, a property of the system rather than of the gold --- and it is what an "
    "accuracy claim must not be built on. No accuracy, false-merge or superiority number "
    "over this atlas is evidence about ORION's competence on the added cases."
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decimal_digest(payload: str, width: int = 16) -> str:
    """A fixed-width, all-digit content digest.

    Decimal rather than hex on purpose. The freeze document requires every added
    case to share one ``case_id`` length, separator count **and alphabetic
    prefix**, so that no identifier-shape probe can tell a differ case from a
    same case. A hex digest breaks the third of those: the leading non-digit run
    of ``coordinate-synth-bd4f...`` is ``coordinate-synth-bd``, and the first
    build of this atlas emitted seven distinct prefixes across its 24 cases,
    which the in-sample identifiability audit read as a shortcut cue. An
    all-digit digest makes the prefix constant by construction. The digest is
    still a function of the case's content and of nothing else.
    """

    if width <= 0:
        raise ValueError("a digest needs a positive width")
    return str(int(_sha(payload.encode("utf-8")), 16) % (10**width)).zfill(width)


def measurement_dimensions() -> tuple[tuple[str, str], ...]:
    """``(dimension, representative unit)`` pairs of the frozen unit table.

    Reuses ``p3_public_reference_build_v11.UNIT_DIMENSIONS`` rather than
    restating it: the v1.1 build already treats two units of different
    dimensions as a non-equivalence it is willing to call
    ``DISTINCT_MEASUREMENT``, and the extension inherits that judgement instead
    of inventing a second one.
    """

    by_dimension: dict[str, list[str]] = {}
    for unit, dimension in UNIT_DIMENSIONS.items():
        by_dimension.setdefault(dimension, []).append(unit)
    return tuple(
        (dimension, sorted(units)[0]) for dimension, units in sorted(by_dimension.items())
    )


def observation_epochs(count: int = 8) -> tuple[str, ...]:
    """Disjoint four-year observation windows, oldest first."""

    if count <= 0:
        raise ValueError("an epoch table needs at least one epoch")
    return tuple(f"{1996 + 4 * index}-01-01/{1999 + 4 * index}-12-31" for index in range(count))


def standard_document() -> dict[str, object]:
    """The frozen table the added cases' gold is derived from."""

    return {
        "schema_version": "orion.p3.synthetic-coordinate-standard.v1",
        "protocol_id": PROTOCOL_ID,
        "derivation_rule": DERIVATION_RULE,
        "derivation_rule_statement": (
            "Two projections that agree on every exposed coordinate are COMPATIBLE. Two "
            "that agree on referent and construct and name distinct measurement-dimension "
            "classes of this table are DISTINCT_MEASUREMENT. Two that agree on referent, "
            "construct and measurement and name distinct, disjoint observation epochs of "
            "this table are CONTEXTUAL_DIFFERENCE."
        ),
        "measurement_dimensions": [
            {"dimension": dimension, "representative_unit": unit}
            for dimension, unit in measurement_dimensions()
        ],
        "observation_epochs": list(observation_epochs()),
        "disciplines": list(DISCIPLINES),
        "unit_table_source": "orion.study.p3_public_reference_build_v11.UNIT_DIMENSIONS",
        "external_validity": EXTERNAL_VALIDITY,
        "not_an_accuracy_benchmark": ACCURACY_CAVEAT,
    }


def standard_bytes() -> bytes:
    """Canonical bytes of the standard, hashed into every added case's provenance."""

    return json.dumps(standard_document(), indent=2, sort_keys=True).encode("utf-8") + b"\n"


def _coordinate_values(stratum: str, slot: int) -> tuple[str, str]:
    """The pair of coordinate ids for one slot: distinct below the differ cut, equal above."""

    if stratum == "measurement":
        table = [f"dimension:{dimension}" for dimension, _ in measurement_dimensions()]
    else:
        table = [f"epoch:{epoch}" for epoch in observation_epochs()]
    if slot < DIFFER_SLOTS:
        left = table[(2 * slot) % len(table)]
        right = table[(2 * slot + 1) % len(table)]
        if left == right:  # pragma: no cover - guards a shrunken standard table
            raise ValueError(f"{stratum} slot {slot}: standard table too small to differ")
        return left, right
    value = table[slot % len(table)]
    return value, value


def gold_relation(
    *,
    measurement_left: str,
    measurement_right: str,
    temporal_left: str,
    temporal_right: str,
) -> MeaningRelation:
    """Gold from the coordinates by the frozen rule, not from the slot's name.

    Deriving the label from the values rather than from "this is a differ slot"
    is the point: the case's answer is a function of its coordinates, so an arm
    that empties a coordinate is removing what the answer was computed from.
    """

    if measurement_left != measurement_right:
        return MeaningRelation.DISTINCT_MEASUREMENT
    if temporal_left != temporal_right:
        return MeaningRelation.CONTEXTUAL_DIFFERENCE
    return MeaningRelation.COMPATIBLE


def _case(stratum: str, slot: int, *, standard_hash: str) -> dict[str, object]:
    spec = STRATA[stratum]
    discipline = DISCIPLINES[slot % len(DISCIPLINES)]
    if stratum == "measurement":
        measurement_left, measurement_right = _coordinate_values(stratum, slot)
        epochs = observation_epochs()
        temporal_left = temporal_right = f"epoch:{epochs[slot % len(epochs)]}"
    else:
        temporal_left, temporal_right = _coordinate_values(stratum, slot)
        dimensions = measurement_dimensions()
        shared = dimensions[slot % len(dimensions)][0]
        measurement_left = measurement_right = f"dimension:{shared}"

    referent = f"synth:referent:{stratum}:{slot:02d}"
    construct = f"synth:construct:{stratum}:{slot:02d}"
    relation = gold_relation(
        measurement_left=measurement_left,
        measurement_right=measurement_right,
        temporal_left=temporal_left,
        temporal_right=temporal_right,
    )
    digest = _decimal_digest(
        "|".join(
            [
                PROTOCOL_ID,
                stratum,
                str(slot),
                referent,
                construct,
                measurement_left,
                measurement_right,
                temporal_left,
                temporal_right,
            ]
        )
    )

    def projection(side: str, measurement: str, temporal: str) -> dict[str, object]:
        return {
            "projection_id": f"synthcoord:{digest}:{side}",
            "source_id": "orion-p3-synthetic-coordinate-standard",
            "source_span": f"{STANDARD_FILENAME}#case={digest}&side={side}",
            "predicate": str(spec["predicate"]),
            "referent_ids": [referent],
            "construct_ids": [construct],
            "measurement_ids": [f"synth:measurement:{measurement}"],
            "temporal_context_ids": [f"synth:temporal:{temporal}"],
            "polarity": "POSITIVE",
            "modality": "ASSERTED",
        }

    case = {
        "schema_version": SCHEMA_VERSION,
        "case_id": f"coordinate-synth-{digest}",
        "discipline": discipline,
        "case_family": str(spec["case_family"]),
        "source_records": [
            {
                "dataset": STANDARD_DATASET,
                "revision": standard_hash,
                "locator": STANDARD_FILENAME,
                "content_hash": standard_hash,
                "license": "CC0-1.0",
            }
        ],
        "left_projection": projection("l", measurement_left, temporal_left),
        "right_projection": projection("r", measurement_right, temporal_right),
        "expected": {
            "meaning_relation": relation.value,
            "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [
                    f"{STANDARD_DATASET}@{standard_hash}:{STANDARD_FILENAME}#case={digest}&side=l",
                    f"{STANDARD_DATASET}@{standard_hash}:{STANDARD_FILENAME}#case={digest}&side=r",
                ],
                "derivation": {
                    "rule": DERIVATION_RULE,
                    "inputs": [
                        measurement_left,
                        measurement_right,
                        temporal_left,
                        temporal_right,
                    ],
                },
            },
        },
    }
    validate_case(case)
    return case


def synthetic_coordinate_cases() -> list[dict[str, object]]:
    """The 24 added cases: 12 per stratum, 4 differing and 8 agreeing in each."""

    cases = [
        _case(stratum, slot, standard_hash=_sha(standard_bytes()))
        for stratum in sorted(STRATA)
        for slot in range(SLOTS_PER_STRATUM)
    ]
    ids = [str(case["case_id"]) for case in cases]
    if len(set(ids)) != len(ids):  # pragma: no cover - a collision would be a hash break
        raise ValueError("synthetic coordinate case ids collided")
    return cases


DEPENDENT_ARMS = {
    "measurement_ids": "remove_measurement",
    "temporal_context_ids": "remove_temporal_context",
}


def dependence_receipts(cases: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Per differ case: the full system is right on it and the ablation makes it wrong.

    Both halves are checked, against the analysis module's own
    ``ablated_relation``. A case whose gold the full system misses would not show
    that the coordinate carried the answer, and a case whose ablation leaves the
    decision standing is not a case whose answer depends on the coordinate.
    """

    receipts: list[dict[str, object]] = []
    for case in cases:
        payload = dict(case)
        expected = payload["expected"]
        assert isinstance(expected, dict)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        if gold is MeaningRelation.COMPATIBLE:
            continue
        coordinate = (
            "measurement_ids" if gold is MeaningRelation.DISTINCT_MEASUREMENT else
            "temporal_context_ids"
        )
        arm = DEPENDENT_ARMS[coordinate]
        full = MeaningRelation(evaluate_case(payload).predicted)
        ablated = ablated_relation(payload, arm)
        receipts.append(
            {
                "case_id": str(payload["case_id"]),
                "coordinate": coordinate,
                "arm": arm,
                "gold": gold.value,
                "full_system": full.value,
                "ablated": ablated.value,
                "full_system_correct": full is gold,
                "ablation_changes_answer": ablated is not gold,
            }
        )
    return receipts


def _coordinate_population(cases: Sequence[Mapping[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for field in COORDINATE_FIELDS:
        populated = 0
        for case in cases:
            left = case["left_projection"]
            right = case["right_projection"]
            assert isinstance(left, dict) and isinstance(right, dict)
            if left.get(field) or right.get(field):
                populated += 1
        counts[field] = populated
    return counts


def _alpha_prefix(case_id: str) -> str:
    for index, character in enumerate(case_id):
        if character.isdigit():
            return case_id[:index]
    return case_id


def shape_invariants(cases: Sequence[Mapping[str, object]]) -> dict[str, list[object]]:
    """The construction-level shapes the added cases must hold constant.

    The freeze document requires that nothing outside the coordinate values vary
    with the answer, and lists these. Checking it here rather than trusting it is
    the whole lesson of the P4 record: the first build of this atlas satisfied
    the sentence and not the property, because a hex digest's leading non-digit
    run is not constant, and only the identifiability audit noticed.
    """

    seen: dict[str, set[object]] = {
        "case_id_length": set(),
        "case_id_hyphen_count": set(),
        "case_id_alpha_prefix": set(),
        "projection_id_length": set(),
        "source_span_length": set(),
        "source_record_count": set(),
        "authority_kind": set(),
        "derivation_rule": set(),
        "evidence_count": set(),
        "coordinate_arity": set(),
    }
    for case in cases:
        case_id = str(case["case_id"])
        seen["case_id_length"].add(len(case_id))
        seen["case_id_hyphen_count"].add(case_id.count("-"))
        seen["case_id_alpha_prefix"].add(_alpha_prefix(case_id))
        expected = case["expected"]
        assert isinstance(expected, dict)
        authority = expected["authority"]
        assert isinstance(authority, dict)
        seen["authority_kind"].add(str(authority["kind"]))
        seen["derivation_rule"].add(str(dict(authority["derivation"])["rule"]))
        seen["evidence_count"].add(len(list(authority["evidence"])))
        sources = case["source_records"]
        assert isinstance(sources, list)
        seen["source_record_count"].add(len(sources))
        for side in ("left_projection", "right_projection"):
            projection = case[side]
            assert isinstance(projection, dict)
            seen["projection_id_length"].add(len(str(projection["projection_id"])))
            seen["source_span_length"].add(len(str(projection["source_span"])))
            seen["coordinate_arity"].add(
                tuple(len(list(projection.get(field) or ())) for field in COORDINATE_FIELDS)
            )
    return {name: sorted(values, key=repr) for name, values in sorted(seen.items())}


def _counter(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_report(
    parent_path: Path,
    parent_cases: Sequence[Mapping[str, object]],
    added: Sequence[Mapping[str, object]],
    merged: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """The extension's identity, its coordinate denominators and its blockers."""

    receipts = dependence_receipts(added)
    data = b"\n".join(canonical_json(case) for case in merged) + (b"\n" if merged else b"")
    blockers: list[str] = []
    if not added:
        blockers.append("no coordinate cases were added")
    inert = [item for item in receipts if not item["ablation_changes_answer"]]
    if inert:
        blockers.append(
            "cases whose gold does not depend on their coordinate: "
            + ", ".join(sorted(str(item["case_id"]) for item in inert))
        )
    wrong = [item for item in receipts if not item["full_system_correct"]]
    if wrong:
        blockers.append(
            "cases the full system does not answer correctly: "
            + ", ".join(sorted(str(item["case_id"]) for item in wrong))
        )
    added_population = _coordinate_population(added)
    for field, arm in sorted(DEPENDENT_ARMS.items()):
        if added_population.get(field, 0) != len(added):
            blockers.append(f"{arm}: {field} is not populated on every added case")
    parent_ids = {str(case["case_id"]) for case in parent_cases}
    collisions = sorted(parent_ids & {str(case["case_id"]) for case in added})
    if collisions:
        blockers.append("added case ids collide with the parent: " + ", ".join(collisions))
    invariants = shape_invariants(added) if added else {}
    varying = sorted(name for name, values in invariants.items() if len(values) > 1)
    if varying:
        blockers.append(
            "construction shapes that must be constant across the added cases vary: "
            + ", ".join(varying)
        )

    return {
        "schema_version": "orion.p3.coordinate-necessity-build-report.v1",
        "protocol_id": PROTOCOL_ID,
        "atlas_id": ATLAS_ID,
        "freeze_document": "research/p3-coordinate-necessity-v1/FREEZE_2026-08-21.md",
        "status": "READY" if not blockers else "CANNOT_CHECK",
        "blockers": blockers,
        "parent_atlas": {
            "path": parent_path.as_posix(),
            "sha256": _sha(parent_path.read_bytes()),
            "case_count": len(parent_cases),
            "note": "copied through unchanged; the frozen atlas is never edited",
        },
        "synthetic_case_count": len(added),
        "built_n": len(merged),
        "cases_hash": _sha(data) if merged else None,
        "standard_document": STANDARD_FILENAME,
        "standard_sha256": _sha(standard_bytes()),
        "expected_relations": _counter(
            str(dict(case["expected"])["meaning_relation"]) for case in merged
        ),
        "added_expected_relations": _counter(
            str(dict(case["expected"])["meaning_relation"]) for case in added
        ),
        "disciplines": _counter(str(case["discipline"]) for case in merged),
        "case_families": _counter(str(case["case_family"]) for case in merged),
        "coordinate_population_parent": _coordinate_population(parent_cases),
        "coordinate_population_added": added_population,
        "coordinate_population_merged": _coordinate_population(merged),
        "dependence_receipts": receipts,
        "added_shape_invariants": invariants,
        "external_validity": EXTERNAL_VALIDITY,
        "not_an_accuracy_benchmark": ACCURACY_CAVEAT,
    }


def build_extension(parent_path: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Parent cases plus the added coordinate cases, in ``case_id`` order, with a report."""

    parent_cases = load_jsonl(parent_path)
    added = synthetic_coordinate_cases()
    merged = sorted(
        [*parent_cases, *added], key=lambda case: str(case["case_id"])
    )
    return merged, build_report(parent_path, parent_cases, added, merged)


def write_jsonl(path: Path, cases: Iterable[Mapping[str, object]]) -> None:
    raw = b"\n".join(canonical_json(case) for case in cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw + (b"\n" if raw else b""))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the P3 coordinate-necessity atlas extension"
    )
    parser.add_argument("--parent", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    cases, report = build_extension(args.parent)
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / "cases.jsonl", cases)
    (args.out / STANDARD_FILENAME).write_bytes(standard_bytes())
    (args.out / "BUILD_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ACCURACY_CAVEAT",
    "ATLAS_ID",
    "COORDINATE_FIELDS",
    "DERIVATION_RULE",
    "EXTERNAL_VALIDITY",
    "PROTOCOL_ID",
    "build_extension",
    "build_report",
    "dependence_receipts",
    "gold_relation",
    "measurement_dimensions",
    "observation_epochs",
    "shape_invariants",
    "standard_bytes",
    "standard_document",
    "synthetic_coordinate_cases",
    "write_jsonl",
]
