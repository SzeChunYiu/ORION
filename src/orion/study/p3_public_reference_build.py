from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from orion.study.p3_public_reference import SCHEMA_VERSION, canonical_json, validate_case

MUSE_REVISION = "f7a40317db46145d0c90b221311d8324db5da1b9"
SCIFACT_REVISION = "68b98a56d93e0f9da0d2aab4e6c3294699a0f72e"
SCISCHEMA_REVISION = "55b6197cdb0b66c3123df16d0b0c70b02c4bde8b"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized_text(value: str) -> str:
    return " ".join(value.lower().split())


def _entity_from_relation_item(item: object) -> Mapping[str, object] | None:
    if not isinstance(item, Mapping) or len(item) != 1:
        return None
    nested = next(iter(item.values()))
    return nested if isinstance(nested, Mapping) else None


def muse_coreference_cases(root: Path) -> list[dict[str, object]]:
    """Build expert-grounded same-referent cases from MUSE coreference edges.

    The emitted case does not copy paragraph text. The upstream expert
    coreference edge becomes the referent identity and the source file is bound
    by path + content hash.
    """
    cases: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.json")):
        raw = path.read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, Mapping):
            continue
        doc_id = str(payload.get("document_id", path.stem))
        relation_sets = payload.get("relation_annotations", {})
        if not isinstance(relation_sets, Mapping):
            continue
        for annotator, relations in sorted(relation_sets.items()):
            if not isinstance(relations, list):
                continue
            for relation in relations:
                if not isinstance(relation, Mapping) or relation.get("type") != "coreference":
                    continue
                rel_id = str(relation.get("relation_id", "coref"))
                entities = relation.get("entities", [])
                if not isinstance(entities, list):
                    continue
                decoded = [
                    entity
                    for item in entities
                    if (entity := _entity_from_relation_item(item)) is not None
                ]
                for pair_index, (left, right) in enumerate(itertools.combinations(decoded, 2)):
                    left_text = str(left.get("text", ""))
                    right_text = str(right.get("text", ""))
                    if not left_text or not right_text:
                        continue
                    if _normalized_text(left_text) == _normalized_text(right_text):
                        continue
                    canonical_ref = f"muse:{doc_id}:coref:{rel_id}"
                    case = {
                        "schema_version": SCHEMA_VERSION,
                        "case_id": f"muse-{doc_id}-{rel_id}-{pair_index}",
                        "discipline": "muse_cross_domain",
                        "case_family": "different_name_same_referent",
                        "source_records": [
                            {
                                "dataset": "MUSE",
                                "revision": MUSE_REVISION,
                                "locator": path.as_posix(),
                                "content_hash": _sha256_bytes(raw),
                                "license": "UPSTREAM_POINTER_ONLY",
                            }
                        ],
                        "left_projection": {
                            "projection_id": f"{doc_id}:{left.get('entity_annotation_id', 'L')}",
                            "source_id": doc_id,
                            "source_span": (
                                f"{path.as_posix()}#{left.get('start', '?')}:{left.get('end', '?')}"
                            ),
                            "predicate": "mentions_concept",
                            "referent_ids": [canonical_ref],
                            "construct_ids": [],
                            "measurement_ids": [],
                            "temporal_context_ids": [],
                            "polarity": "UNKNOWN",
                            "modality": "UNKNOWN",
                        },
                        "right_projection": {
                            "projection_id": f"{doc_id}:{right.get('entity_annotation_id', 'R')}",
                            "source_id": doc_id,
                            "source_span": (
                                f"{path.as_posix()}#{right.get('start', '?')}:{right.get('end', '?')}"
                            ),
                            "predicate": "mentions_concept",
                            "referent_ids": [canonical_ref],
                            "construct_ids": [],
                            "measurement_ids": [],
                            "temporal_context_ids": [],
                            "polarity": "UNKNOWN",
                            "modality": "UNKNOWN",
                        },
                        "expected": {
                            "meaning_relation": "COMPATIBLE",
                            "authority": {
                                "kind": "DERIVED_FROM_ALLOWED",
                                "evidence": [
                                    f"MUSE@{MUSE_REVISION}:{path.as_posix()}#{annotator}:{rel_id}"
                                ],
                                "derivation": {
                                    "rule": "identity:upstream-coreference-edge",
                                    "inputs": [rel_id],
                                },
                            },
                        },
                    }
                    validate_case(case)
                    cases.append(case)
    return cases


def scifact_claim_cases(claims_path: Path) -> list[dict[str, object]]:
    """Build contradiction/support semantic controls from SciFact expert labels.

    This evaluates the contradiction gate, not raw-text understanding: the
    upstream label fixes the polarity relationship while other coordinates are
    aligned to the claim id.
    """
    raw_file = claims_path.read_bytes()
    file_hash = _sha256_bytes(raw_file)
    cases: list[dict[str, object]] = []
    for line_number, line in enumerate(raw_file.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, Mapping):
            continue
        claim_id = str(payload.get("id", line_number))
        evidence = payload.get("evidence", {})
        if not isinstance(evidence, Mapping):
            continue
        for doc_id, rationales in sorted(evidence.items(), key=lambda item: str(item[0])):
            if not isinstance(rationales, list):
                continue
            for rationale_index, rationale in enumerate(rationales):
                if not isinstance(rationale, Mapping):
                    continue
                label = str(rationale.get("label", ""))
                if label not in {"SUPPORT", "CONTRADICT"}:
                    continue
                expected = "COMPATIBLE" if label == "SUPPORT" else "CONTRADICTORY"
                right_polarity = "POSITIVE" if label == "SUPPORT" else "NEGATED"
                shared = f"scifact:claim:{claim_id}"
                case = {
                    "schema_version": SCHEMA_VERSION,
                    "case_id": f"scifact-{claim_id}-{doc_id}-{rationale_index}",
                    "discipline": "scientific_claim_verification",
                    "case_family": "polarity_modality_attribution_context",
                    "source_records": [
                        {
                            "dataset": "SciFact",
                            "revision": SCIFACT_REVISION,
                            "locator": f"{claims_path.as_posix()}#line={line_number}",
                            "content_hash": file_hash,
                            "license": "CC-BY-4.0-ANNOTATIONS",
                        }
                    ],
                    "left_projection": {
                        "projection_id": f"claim:{claim_id}",
                        "source_id": f"claim:{claim_id}",
                        "source_span": f"{claims_path.as_posix()}#claim={claim_id}",
                        "predicate": "scientific_claim_truth",
                        "referent_ids": [shared],
                        "construct_ids": [shared],
                        "measurement_ids": [],
                        "temporal_context_ids": [],
                        "polarity": "POSITIVE",
                        "modality": "ASSERTED",
                    },
                    "right_projection": {
                        "projection_id": f"evidence:{doc_id}:{rationale_index}",
                        "source_id": f"evidence:{doc_id}",
                        "source_span": (
                            f"{claims_path.as_posix()}#claim={claim_id};doc={doc_id};"
                            f"rationale={rationale_index}"
                        ),
                        "predicate": "scientific_claim_truth",
                        "referent_ids": [shared],
                        "construct_ids": [shared],
                        "measurement_ids": [],
                        "temporal_context_ids": [],
                        "polarity": right_polarity,
                        "modality": "ASSERTED",
                    },
                    "expected": {
                        "meaning_relation": expected,
                        "authority": {
                            "kind": "DERIVED_FROM_ALLOWED",
                            "evidence": [
                                f"SciFact@{SCIFACT_REVISION}:{claims_path.as_posix()}#"
                                f"claim={claim_id};doc={doc_id};rationale={rationale_index};"
                                f"label={label}"
                            ],
                            "derivation": {
                                "rule": "polarity:scifact-support-contradict",
                                "inputs": [label],
                            },
                        },
                    },
                }
                validate_case(case)
                cases.append(case)
    return cases


def scischema_identity_cases(root: Path) -> list[dict[str, object]]:
    """Build exact-version identity controls from SciSchema master schemas."""
    cases: list[dict[str, object]] = []
    for path in sorted(root.glob("*/*/master-schema.json")):
        raw = path.read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, Mapping):
            continue
        schema_id = str(payload.get("$id", ""))
        title = str(payload.get("title", ""))
        if not schema_id or not title:
            continue
        relative = path.as_posix()
        parts = path.parts
        discipline = parts[-3] if len(parts) >= 3 else "scischema"
        shared = f"scischema:{schema_id}"
        case = {
            "schema_version": SCHEMA_VERSION,
            "case_id": f"scischema-{hashlib.sha256(schema_id.encode()).hexdigest()[:16]}",
            "discipline": discipline,
            "case_family": "valid_invalid_representation_mapping",
            "source_records": [
                {
                    "dataset": "SciSchema",
                    "revision": SCISCHEMA_REVISION,
                    "locator": relative,
                    "content_hash": _sha256_bytes(raw),
                    "license": "CC-BY-SA-4.0",
                }
            ],
            "left_projection": {
                "projection_id": f"{shared}:canonical",
                "source_id": schema_id,
                "source_span": relative,
                "predicate": "describes_scientific_process",
                "referent_ids": [shared],
                "construct_ids": [shared],
                "measurement_ids": [],
                "temporal_context_ids": [],
                "polarity": "POSITIVE",
                "modality": "ASSERTED",
            },
            "right_projection": {
                "projection_id": f"{shared}:versioned",
                "source_id": schema_id,
                "source_span": relative,
                "predicate": "describes_scientific_process",
                "referent_ids": [shared],
                "construct_ids": [shared],
                "measurement_ids": [],
                "temporal_context_ids": [],
                "polarity": "POSITIVE",
                "modality": "ASSERTED",
            },
            "expected": {
                "meaning_relation": "COMPATIBLE",
                "authority": {
                    "kind": "DETERMINISTIC_STANDARD",
                    "evidence": [f"SciSchema@{SCISCHEMA_REVISION}:{relative};id={schema_id}"],
                },
            },
        }
        validate_case(case)
        cases.append(case)
    return cases


def _balanced_take(
    pools: Mapping[str, Sequence[dict[str, object]]], *, total: int
) -> list[dict[str, object]]:
    """Round-robin deterministic sampling; never looks at system outputs."""
    if total <= 0:
        return []
    ordered_names = sorted(pools)
    positions = {name: 0 for name in ordered_names}
    chosen: list[dict[str, object]] = []
    while len(chosen) < total:
        progressed = False
        for name in ordered_names:
            seq = pools[name]
            pos = positions[name]
            if pos >= len(seq):
                continue
            chosen.append(seq[pos])
            positions[name] += 1
            progressed = True
            if len(chosen) >= total:
                break
        if not progressed:
            break
    return chosen


def build_atlas(
    *,
    muse_root: Path | None,
    scifact_claims: Path | None,
    scischema_root: Path | None,
    target_n: int = 32,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    pools: dict[str, list[dict[str, object]]] = {}
    if muse_root is not None:
        pools["MUSE"] = muse_coreference_cases(muse_root)
    if scifact_claims is not None:
        pools["SciFact"] = scifact_claim_cases(scifact_claims)
    if scischema_root is not None:
        pools["SciSchema"] = scischema_identity_cases(scischema_root)

    chosen = _balanced_take(pools, total=target_n)
    disciplines = sorted({str(case["discipline"]) for case in chosen})
    families = sorted({str(case["case_family"]) for case in chosen})
    authority = sorted({str(case["expected"]["authority"]["kind"]) for case in chosen})
    expected_relations = sorted({str(case["expected"]["meaning_relation"]) for case in chosen})
    has_merge = "COMPATIBLE" in expected_relations
    has_nonmerge = any(value != "COMPATIBLE" for value in expected_relations)
    ready = (
        len(chosen) == target_n
        and len(disciplines) >= 3
        and len(families) >= 2
        and has_merge
        and has_nonmerge
    )
    case_bytes = b"\n".join(canonical_json(case) for case in chosen) + (b"\n" if chosen else b"")
    report: dict[str, object] = {
        "schema_version": "orion.p3.public-reference-build-report.v1",
        "target_n": target_n,
        "built_n": len(chosen),
        "status": "READY_FOR_FREEZE" if ready else "CANNOT_CHECK",
        "pool_counts": {name: len(records) for name, records in sorted(pools.items())},
        "disciplines": disciplines,
        "case_families": families,
        "authority_kinds": authority,
        "expected_relations": expected_relations,
        "cases_hash": _sha256_bytes(case_bytes) if chosen else None,
        "blockers": [],
    }
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    if len(chosen) < target_n:
        blockers.append(f"authoritative candidate pool produced {len(chosen)} < target {target_n}")
    if len(disciplines) < 3:
        blockers.append(f"only {len(disciplines)} discipline strata available; need at least 3")
    if len(families) < 2:
        blockers.append(f"only {len(families)} case family available; need at least 2")
    if not has_merge or not has_nonmerge:
        blockers.append("atlas must contain both merge-compatible and non-merge authoritative cases")
    return chosen, report


def write_jsonl(path: Path, cases: Iterable[Mapping[str, object]]) -> None:
    rendered = b"\n".join(canonical_json(case) for case in cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(rendered + (b"\n" if rendered else b""))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a zero-budget ORION-P3 atlas from pinned public annotations."
    )
    parser.add_argument("--muse-root", type=Path)
    parser.add_argument("--scifact-claims", type=Path)
    parser.add_argument("--scischema-root", type=Path)
    parser.add_argument("--target-n", type=int, default=32)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    cases, report = build_atlas(
        muse_root=args.muse_root,
        scifact_claims=args.scifact_claims,
        scischema_root=args.scischema_root,
        target_n=args.target_n,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / "cases.jsonl", cases)
    (args.out / "BUILD_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "READY_FOR_FREEZE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
