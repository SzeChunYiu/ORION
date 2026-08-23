from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

from orion.study.p3_public_reference import canonical_json, validate_case
from orion.study.p3_public_reference_build import (
    CorpusPin,
    muse_coreference_cases,
    pin_for,
    scifact_claim_cases,
    scischema_identity_cases,
)

PROTOCOL_ID = "P3.public-reference-mapping.v1.1"
REQUIRED_RELATIONS = {
    "COMPATIBLE",
    "CONTRADICTORY",
    "DISTINCT_REFERENT",
    "DISTINCT_CONSTRUCT",
    "DISTINCT_MEASUREMENT",
}

# Conservative families used only to prove non-equivalence. Units in the same
# family are never labelled distinct measurements solely because strings differ.
UNIT_DIMENSIONS = {
    "m": "length", "cm": "length", "mm": "length", "um": "length", "µm": "length", "nm": "length",
    "s": "time", "ms": "time", "us": "time", "µs": "time", "ns": "time", "ps": "time",
    "J": "energy", "eV": "energy", "keV": "energy", "MeV": "energy", "GeV": "energy", "TeV": "energy",
    "K": "temperature", "°C": "temperature",
    "Hz": "frequency", "kHz": "frequency", "MHz": "frequency", "GHz": "frequency",
    "Pa": "pressure", "kPa": "pressure", "MPa": "pressure", "bar": "pressure",
    "rad": "angle", "deg": "angle",
    "kg": "mass", "g": "mass", "mg": "mass", "µg": "mass",
    "L": "volume", "mL": "volume", "µL": "volume",
    "M": "concentration", "mM": "concentration", "µM": "concentration", "nM": "concentration",
    "PE": "photoelectron_count",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stableize(case: dict[str, object], old_root: Path, prefix: str) -> dict[str, object]:
    old = old_root.as_posix().rstrip("/") + "/"

    def convert(value: object) -> object:
        if isinstance(value, str) and value.startswith(old):
            return prefix.rstrip("/") + "/" + value[len(old):]
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        return value

    stable = convert(case)
    assert isinstance(stable, dict)
    validate_case(stable)
    return stable


def stable_muse_cases(
    root: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    return [
        _stableize(case, root, "dataset/human_Expert_annotations")
        for case in muse_coreference_cases(root, pins)
    ]


def stable_scifact_cases(
    path: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    cases = scifact_claim_cases(path, pins)
    old = path.as_posix()
    stable_file = f"data/{path.name}"
    rendered: list[dict[str, object]] = []
    for case in cases:
        text = json.dumps(case, ensure_ascii=False)
        text = text.replace(old, stable_file)
        stable = json.loads(text)
        validate_case(stable)
        rendered.append(stable)
    return rendered


def stable_scischema_identity_cases(
    root: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    return [
        _stableize(case, root, "schemas")
        for case in scischema_identity_cases(root, pins)
    ]


def _schema_records(root: Path) -> list[tuple[Path, str, bytes, Mapping[str, object], str]]:
    records = []
    for path in sorted(root.glob("*/*/master-schema.json")):
        raw = path.read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, Mapping):
            continue
        schema_id = str(payload.get("$id", ""))
        if not schema_id or not str(payload.get("title", "")):
            continue
        locator = "schemas/" + path.relative_to(root).as_posix()
        records.append((path, locator, raw, payload, schema_id))
    return records


def _discipline(path: Path) -> str:
    return path.parts[-3]


def _source(
    locator: str, raw: bytes, pins: Sequence[CorpusPin] | None = None
) -> dict[str, str]:
    digest = _sha(raw)
    return {
        "dataset": "SciSchema",
        "revision": pin_for("SciSchema", digest, pins).identity,
        "locator": locator,
        "content_hash": digest,
        "license": "CC-BY-SA-4.0",
    }


def scischema_referent_cases(
    root: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    grouped: dict[str, list[tuple[Path, str, bytes, Mapping[str, object], str]]] = defaultdict(list)
    for record in _schema_records(root):
        grouped[_discipline(record[0])].append(record)
    cases = []
    for discipline, records in sorted(grouped.items()):
        for index, (left, right) in enumerate(itertools.combinations(records, 2)):
            _, lloc, lraw, _, lid = left
            _, rloc, rraw, _, rid = right
            if lid == rid:
                continue
            case = {
                "schema_version": "orion.p3.public-reference-case.v1",
                "case_id": f"scischema-ref-{discipline}-{index}",
                "discipline": discipline,
                "case_family": "valid_invalid_representation_mapping",
                "source_records": [_source(lloc, lraw, pins), _source(rloc, rraw, pins)],
                "left_projection": {
                    "projection_id": f"ref:{lid}", "source_id": lid, "source_span": lloc,
                    "predicate": "describes_scientific_process",
                    "referent_ids": [f"schema:{lid}"], "construct_ids": ["scientific_process_schema"],
                    "measurement_ids": [], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
                },
                "right_projection": {
                    "projection_id": f"ref:{rid}", "source_id": rid, "source_span": rloc,
                    "predicate": "describes_scientific_process",
                    "referent_ids": [f"schema:{rid}"], "construct_ids": ["scientific_process_schema"],
                    "measurement_ids": [], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
                },
                "expected": {"meaning_relation": "DISTINCT_REFERENT", "authority": {
                    "kind": "DETERMINISTIC_STANDARD",
                    "evidence": [
                        f"SciSchema@{_source(lloc, lraw, pins)['revision']}:{lloc};id={lid}",
                        f"SciSchema@{_source(rloc, rraw, pins)['revision']}:{rloc};id={rid}",
                    ],
                }},
            }
            validate_case(case)
            cases.append(case)
    return cases


def _walk_units(node: object, path: tuple[str, ...] = ()) -> Iterator[tuple[str, str]]:
    if not isinstance(node, Mapping):
        return
    properties = node.get("properties")
    if isinstance(properties, Mapping):
        unit = properties.get("unit")
        if isinstance(unit, Mapping) and isinstance(unit.get("const"), str):
            yield (".".join(path) or "root", str(unit["const"]))
        for name, child in sorted(properties.items(), key=lambda item: str(item[0])):
            yield from _walk_units(child, path + (str(name),))
    if "items" in node:
        yield from _walk_units(node["items"], path + ("[]",))
    for key in ("allOf", "anyOf", "oneOf"):
        values = node.get(key)
        if isinstance(values, list):
            for index, value in enumerate(values):
                yield from _walk_units(value, path + (f"{key}[{index}]",))


def scischema_construct_cases(
    root: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    cases = []
    for path, locator, raw, payload, schema_id in _schema_records(root):
        by_unit: dict[str, list[str]] = defaultdict(list)
        for field, unit in _walk_units(payload):
            if field not in by_unit[unit]:
                by_unit[unit].append(field)
        candidate = next(((unit, fields[0], fields[1]) for unit, fields in sorted(by_unit.items()) if len(fields) >= 2), None)
        if candidate is None:
            continue
        unit, left_field, right_field = candidate
        ref = f"schema:{schema_id}"
        case = {
            "schema_version": "orion.p3.public-reference-case.v1",
            "case_id": "scischema-construct-" + _sha(f"{schema_id}|{unit}|{left_field}|{right_field}".encode())[:16],
            "discipline": _discipline(path), "case_family": "valid_invalid_representation_mapping",
            "source_records": [_source(locator, raw, pins)],
            "left_projection": {
                "projection_id": f"{schema_id}:{left_field}", "source_id": schema_id, "source_span": f"{locator}#property={left_field}",
                "predicate": "reports_quantity", "referent_ids": [ref], "construct_ids": [f"field:{left_field}"],
                "measurement_ids": [f"unit:{unit}"], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
            },
            "right_projection": {
                "projection_id": f"{schema_id}:{right_field}", "source_id": schema_id, "source_span": f"{locator}#property={right_field}",
                "predicate": "reports_quantity", "referent_ids": [ref], "construct_ids": [f"field:{right_field}"],
                "measurement_ids": [f"unit:{unit}"], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
            },
            "expected": {"meaning_relation": "DISTINCT_CONSTRUCT", "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [
                    f"SciSchema@{_source(locator, raw, pins)['revision']}:{locator}#property={left_field};unit={unit}",
                    f"SciSchema@{_source(locator, raw, pins)['revision']}:{locator}#property={right_field};unit={unit}",
                ],
                "derivation": {"rule": "identity:distinct-expert-schema-property-keys-with-shared-unit", "inputs": [left_field, right_field, unit]},
            }},
        }
        validate_case(case)
        cases.append(case)
    return cases


def scischema_measurement_cases(
    root: Path, pins: Sequence[CorpusPin] | None = None
) -> list[dict[str, object]]:
    cases = []
    for path, locator, raw, payload, schema_id in _schema_records(root):
        fields = [(field, unit) for field, unit in _walk_units(payload) if unit in UNIT_DIMENSIONS]
        pair = next(((left, right) for left, right in itertools.combinations(fields, 2) if UNIT_DIMENSIONS[left[1]] != UNIT_DIMENSIONS[right[1]]), None)
        if pair is None:
            continue
        (left_field, left_unit), (right_field, right_unit) = pair
        left_dim, right_dim = UNIT_DIMENSIONS[left_unit], UNIT_DIMENSIONS[right_unit]
        ref = f"schema:{schema_id}"
        construct = f"schema:{schema_id}:reported_quantity"
        case = {
            "schema_version": "orion.p3.public-reference-case.v1",
            "case_id": "scischema-measurement-" + _sha(f"{schema_id}|{left_field}|{left_unit}|{right_field}|{right_unit}".encode())[:16],
            "discipline": _discipline(path), "case_family": "valid_invalid_representation_mapping",
            "source_records": [_source(locator, raw, pins)],
            "left_projection": {
                "projection_id": f"{schema_id}:{left_field}", "source_id": schema_id, "source_span": f"{locator}#property={left_field}",
                "predicate": "reports_quantity", "referent_ids": [ref], "construct_ids": [construct],
                "measurement_ids": [f"dimension:{left_dim}"], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
            },
            "right_projection": {
                "projection_id": f"{schema_id}:{right_field}", "source_id": schema_id, "source_span": f"{locator}#property={right_field}",
                "predicate": "reports_quantity", "referent_ids": [ref], "construct_ids": [construct],
                "measurement_ids": [f"dimension:{right_dim}"], "temporal_context_ids": [], "polarity": "POSITIVE", "modality": "ASSERTED",
            },
            "expected": {"meaning_relation": "DISTINCT_MEASUREMENT", "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [
                    f"SciSchema@{_source(locator, raw, pins)['revision']}:{locator}#property={left_field};unit={left_unit}",
                    f"SciSchema@{_source(locator, raw, pins)['revision']}:{locator}#property={right_field};unit={right_unit}",
                ],
                "derivation": {"rule": "measurement:expert-schema-units-from-distinct-frozen-dimensions", "inputs": [left_unit, left_dim, right_unit, right_dim]},
            }},
        }
        validate_case(case)
        cases.append(case)
    return cases


def _take(pools: Mapping[str, Sequence[dict[str, object]]], total: int) -> list[dict[str, object]]:
    names = sorted(pools)
    positions = {name: 0 for name in names}
    chosen: list[dict[str, object]] = []
    while len(chosen) < total:
        progressed = False
        for name in names:
            pos = positions[name]
            if pos < len(pools[name]):
                chosen.append(pools[name][pos]); positions[name] += 1; progressed = True
                if len(chosen) == total:
                    break
        if not progressed:
            break
    return chosen


def build_atlas_v11(
    *,
    muse_root: Path,
    scifact_claims: Path,
    scischema_root: Path,
    target_n: int = 32,
    pins: Sequence[CorpusPin] | None = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    pools = {
        "MUSECoreference": stable_muse_cases(muse_root, pins),
        "SciFactPolarity": stable_scifact_cases(scifact_claims, pins),
        "SciSchemaConstruct": scischema_construct_cases(scischema_root, pins),
        "SciSchemaIdentity": stable_scischema_identity_cases(scischema_root, pins),
        "SciSchemaMeasurement": scischema_measurement_cases(scischema_root, pins),
        "SciSchemaReferent": scischema_referent_cases(scischema_root, pins),
    }
    chosen = _take(pools, target_n)
    relations = sorted({str(case["expected"]["meaning_relation"]) for case in chosen})
    disciplines = sorted({str(case["discipline"]) for case in chosen})
    families = sorted({str(case["case_family"]) for case in chosen})
    missing = sorted(REQUIRED_RELATIONS - set(relations))
    absolute_locators = []
    for case in chosen:
        for record in case["source_records"]:
            locator = str(record["locator"]).split("#", 1)[0]
            if locator.startswith("/") or ":\\" in locator:
                absolute_locators.append(locator)
    ready = len(chosen) == target_n and len(disciplines) >= 3 and len(families) >= 2 and not missing and not absolute_locators
    data = b"\n".join(canonical_json(case) for case in chosen) + (b"\n" if chosen else b"")
    blockers = []
    if len(chosen) != target_n:
        blockers.append(f"built {len(chosen)} cases, expected {target_n}")
    if len(disciplines) < 3:
        blockers.append("fewer than three discipline strata")
    if len(families) < 2:
        blockers.append("fewer than two case families")
    if missing:
        blockers.append("missing required relations: " + ", ".join(missing))
    if absolute_locators:
        blockers.append("absolute runner-local locators remain")
    return chosen, {
        "schema_version": "orion.p3.public-reference-build-report.v1.1",
        "protocol_id": PROTOCOL_ID,
        "status": "READY_FOR_FREEZE" if ready else "CANNOT_CHECK",
        "target_n": target_n,
        "built_n": len(chosen),
        "pool_counts": {name: len(values) for name, values in sorted(pools.items())},
        "disciplines": disciplines,
        "case_families": families,
        "expected_relations": relations,
        "required_relations": sorted(REQUIRED_RELATIONS),
        "cases_hash": _sha(data) if chosen else None,
        "blockers": blockers,
    }


def write_jsonl(path: Path, cases: Iterable[Mapping[str, object]]) -> None:
    raw = b"\n".join(canonical_json(case) for case in cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw + (b"\n" if raw else b""))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--muse-root", required=True, type=Path)
    parser.add_argument("--scifact-claims", required=True, type=Path)
    parser.add_argument("--scischema-root", required=True, type=Path)
    parser.add_argument("--target-n", type=int, default=32)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    cases, report = build_atlas_v11(muse_root=args.muse_root, scifact_claims=args.scifact_claims, scischema_root=args.scischema_root, target_n=args.target_n)
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / "cases.jsonl", cases)
    (args.out / "BUILD_REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "READY_FOR_FREEZE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
