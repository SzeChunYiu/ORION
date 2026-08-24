#!/usr/bin/env python3
"""Outcome-blind structural parser for complete DeepOnto BERTMap artifacts.

The parser never opens ontologies, a model, gold/reference alignments, or
protected outcomes.  A separately frozen universe manifest supplies the
expected source and target IRIs.  Passing this parser establishes artifact
shape/completeness only; rows are never interpreted as correct mappings.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "orion.p3.bertmap-native-parser.v7"
REQUIRED_FILES = (
    "raw_mappings.json",
    "raw_mappings.tsv",
    "extended_mappings.tsv",
    "filtered_mappings.tsv",
    "repaired_mappings.tsv",
)
EXPECTED_HEADER = ["SrcEntity", "TgtEntity", "Score"]
FORBIDDEN_KEY_FRAGMENTS = (
    "gold",
    "reference",
    "protected",
    "truth",
    "outcome",
    "score_label",
)


class ContractError(ValueError):
    """Fail-closed structural contract error."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _decimal(value: Any, context: str) -> Decimal:
    if isinstance(value, bool):
        raise ContractError(f"{context}: boolean score is forbidden")
    try:
        score = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ContractError(f"{context}: invalid decimal score") from exc
    if not score.is_finite() or score < 0 or score > 1:
        raise ContractError(f"{context}: score must be finite in [0,1]")
    return score.normalize()


def _walk_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            low = str(key).lower()
            if any(fragment in low for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ContractError(f"{path}.{key}: prohibited outcome-bearing manifest key")
            _walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_keys(child, f"{path}[{index}]")


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    _walk_keys(value)
    required = {
        "schema_version",
        "expected_source_iris",
        "expected_target_iris",
        "mapping_extension_threshold",
        "mapping_filtered_threshold",
        "for_oaei",
        "excluded_source_iris",
    }
    if set(value) != required:
        raise ContractError(f"manifest keys must be exactly {sorted(required)}")
    if value["schema_version"] != "orion.p3.bertmap-universe-manifest.v7":
        raise ContractError("manifest schema_version mismatch")
    if value["for_oaei"] is not False:
        raise ContractError("V7 parser binding supports only for_oaei=false")
    if value["excluded_source_iris"] != []:
        raise ContractError("V7 parser binding requires an empty excluded_source_iris list")
    for key in ("expected_source_iris", "expected_target_iris"):
        rows = value[key]
        if not isinstance(rows, list) or not rows or not all(isinstance(x, str) and x for x in rows):
            raise ContractError(f"{key} must be a nonempty list of strings")
        if len(rows) != len(set(rows)):
            raise ContractError(f"{key} contains duplicates")
    _decimal(value["mapping_extension_threshold"], "mapping_extension_threshold")
    _decimal(value["mapping_filtered_threshold"], "mapping_filtered_threshold")
    return value


def _row(
    src: Any,
    tgt: Any,
    score: Any,
    *,
    source_universe: set[str],
    target_universe: set[str],
    context: str,
) -> tuple[str, str, Decimal]:
    if not isinstance(src, str) or not isinstance(tgt, str) or not src or not tgt:
        raise ContractError(f"{context}: source and target must be nonempty strings")
    if src not in source_universe:
        raise ContractError(f"{context}: source IRI is outside the frozen universe")
    if tgt not in target_universe:
        raise ContractError(f"{context}: target IRI is outside the frozen universe")
    return (src, tgt, _decimal(score, context))


def load_raw_json(
    path: Path, source_universe: set[str], target_universe: set[str]
) -> tuple[list[tuple[str, str, Decimal]], set[str]]:
    value = json.loads(path.read_text(), parse_float=Decimal)
    if not isinstance(value, dict):
        raise ContractError("raw_mappings.json must be an object")
    if set(value) != source_universe:
        missing = sorted(source_universe - set(value))
        extra = sorted(set(value) - source_universe)
        raise ContractError(f"raw_mappings.json source-key coverage mismatch; missing={missing}, extra={extra}")
    rows: list[tuple[str, str, Decimal]] = []
    for key, mappings in value.items():
        if not isinstance(mappings, list):
            raise ContractError(f"raw_mappings.json[{key!r}] must be a list")
        for index, mapping in enumerate(mappings):
            if not isinstance(mapping, list) or len(mapping) != 3:
                raise ContractError(f"raw_mappings.json[{key!r}][{index}] must be a three-item list")
            row = _row(
                *mapping,
                source_universe=source_universe,
                target_universe=target_universe,
                context=f"raw_mappings.json[{key!r}][{index}]",
            )
            if row[0] != key:
                raise ContractError(f"raw_mappings.json[{key!r}][{index}] source does not equal its object key")
            rows.append(row)
    if len(rows) != len(set(rows)):
        raise ContractError("raw_mappings.json contains duplicate rows")
    return rows, set(value)


def load_tsv(path: Path, source_universe: set[str], target_universe: set[str]) -> list[tuple[str, str, Decimal]]:
    with path.open(newline="") as handle:
        reader = csv.reader(handle, delimiter="\t", strict=True)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ContractError(f"{path.name}: missing header") from exc
        if header != EXPECTED_HEADER:
            raise ContractError(f"{path.name}: exact header mismatch")
        rows = []
        for line_number, fields in enumerate(reader, start=2):
            if len(fields) != 3:
                raise ContractError(f"{path.name}:{line_number}: expected exactly three fields")
            rows.append(
                _row(
                    *fields,
                    source_universe=source_universe,
                    target_universe=target_universe,
                    context=f"{path.name}:{line_number}",
                )
            )
    if len(rows) != len(set(rows)):
        raise ContractError(f"{path.name}: duplicate rows")
    return rows


def parse_contract(output_dir: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    source_universe = set(manifest["expected_source_iris"])
    target_universe = set(manifest["expected_target_iris"])
    artifacts = {name: output_dir / name for name in REQUIRED_FILES}
    for name, path in artifacts.items():
        if not path.is_file() or path.is_symlink():
            raise ContractError(f"{name}: required regular non-symlink artifact is absent")

    raw_json, completed_sources = load_raw_json(artifacts["raw_mappings.json"], source_universe, target_universe)
    raw_tsv = load_tsv(artifacts["raw_mappings.tsv"], source_universe, target_universe)
    extended = load_tsv(artifacts["extended_mappings.tsv"], source_universe, target_universe)
    filtered = load_tsv(artifacts["filtered_mappings.tsv"], source_universe, target_universe)
    repaired = load_tsv(artifacts["repaired_mappings.tsv"], source_universe, target_universe)

    if Counter(raw_json) != Counter(raw_tsv):
        raise ContractError("raw JSON/TSV row multiset mismatch")

    raw_set, extended_set, filtered_set, repaired_set = map(set, (raw_tsv, extended, filtered, repaired))
    if not raw_set <= extended_set:
        raise ContractError("extended_mappings.tsv does not retain every raw row")
    filter_threshold = _decimal(manifest["mapping_filtered_threshold"], "mapping_filtered_threshold")
    expected_filtered = {row for row in extended_set if row[2] >= filter_threshold}
    if filtered_set != expected_filtered:
        raise ContractError("filtered_mappings.tsv is not the exact thresholded extended set")
    filtered_pairs = {(src, tgt) for src, tgt, _ in filtered_set}
    if not {(src, tgt) for src, tgt, _ in repaired_set} <= filtered_pairs:
        raise ContractError("repaired_mappings.tsv contains a pair absent from filtered_mappings.tsv")

    return {
        "schema_version": SCHEMA_VERSION,
        "terminal": "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS",
        "authority": "INTERFACE_CONFORMANCE_ONLY__NO_MAPPING_TRUTH_OR_PERFORMANCE_AUTHORITY",
        "absence_rule": "Zero mapping rows are permitted when every expected source key is present; absence is never obstruction.",
        "completed_source_key_count": len(completed_sources),
        "expected_source_key_count": len(source_universe),
        "row_counts": {
            "raw_json": len(raw_json),
            "raw_tsv": len(raw_tsv),
            "extended": len(extended),
            "filtered": len(filtered),
            "repaired": len(repaired),
        },
        "artifacts": {
            name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for name, path in artifacts.items()
        },
    }


def _write_tsv(path: Path, rows: list[tuple[str, str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(EXPECTED_HEADER)
        writer.writerows(rows)


def self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, expected_pass: bool, mutate=None, manifest_mutate=None) -> None:
        with tempfile.TemporaryDirectory(prefix="p3v7-parser-") as temp:
            root = Path(temp)
            out = root / "match"
            out.mkdir()
            src = ["urn:source:A", "urn:source:B"]
            tgt = ["urn:target:A", "urn:target:B"]
            manifest = {
                "schema_version": "orion.p3.bertmap-universe-manifest.v7",
                "expected_source_iris": src,
                "expected_target_iris": tgt,
                "mapping_extension_threshold": "0.9",
                "mapping_filtered_threshold": "0.9995",
                "for_oaei": False,
                "excluded_source_iris": [],
            }
            raw = {src[0]: [[src[0], tgt[0], 1.0]], src[1]: []}
            raw_rows = [(src[0], tgt[0], "1.0")]
            _write_tsv(out / "raw_mappings.tsv", raw_rows)
            _write_tsv(out / "extended_mappings.tsv", raw_rows)
            _write_tsv(out / "filtered_mappings.tsv", raw_rows)
            _write_tsv(out / "repaired_mappings.tsv", raw_rows)
            (out / "raw_mappings.json").write_text(json.dumps(raw) + "\n")
            if mutate:
                mutate(out, raw, manifest)
            if manifest_mutate:
                manifest_mutate(manifest)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest) + "\n")
            try:
                parse_contract(out, manifest_path)
                observed_pass, error = True, None
            except ContractError as exc:
                observed_pass, error = False, str(exc)
            checks.append(
                {"check": name, "expected_pass": expected_pass, "observed_pass": observed_pass, "pass": expected_pass == observed_pass, "error": error}
            )

    record("complete_nonempty_fixture", True)

    def empty(out, raw, manifest):
        value = {key: [] for key in manifest["expected_source_iris"]}
        (out / "raw_mappings.json").write_text(json.dumps(value) + "\n")
        for name in REQUIRED_FILES[1:]:
            _write_tsv(out / name, [])

    record("complete_empty_fixture_absence_not_obstruction", True, mutate=empty)

    def partial(out, raw, manifest):
        raw.pop("urn:source:B")
        (out / "raw_mappings.json").write_text(json.dumps(raw) + "\n")

    record("partial_raw_json_refused", False, mutate=partial)
    record(
        "raw_tsv_mismatch_refused",
        False,
        mutate=lambda out, raw, manifest: _write_tsv(out / "raw_mappings.tsv", []),
    )
    record(
        "filtered_threshold_mismatch_refused",
        False,
        mutate=lambda out, raw, manifest: _write_tsv(out / "filtered_mappings.tsv", []),
    )
    record(
        "missing_repaired_artifact_refused",
        False,
        mutate=lambda out, raw, manifest: (out / "repaired_mappings.tsv").unlink(),
    )
    record(
        "prohibited_manifest_key_refused",
        False,
        manifest_mutate=lambda manifest: manifest.__setitem__("gold_path", "/forbidden"),
    )
    failed = [check for check in checks if not check["pass"]]
    return {
        "schema_version": "orion.p3.bertmap-native-parser.self-test.v7",
        "check_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "terminal": "PASS" if not failed else "FAIL",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if not args.output_dir or not args.manifest:
            parser.error("--output-dir and --manifest are required unless --self-test is used")
        try:
            result = parse_contract(args.output_dir, args.manifest)
        except ContractError as exc:
            result = {
                "schema_version": SCHEMA_VERSION,
                "terminal": "CANNOT_CHECK_NATIVE_ARTIFACT_CONTRACT_FAILURE",
                "error": str(exc),
            }
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["terminal"] not in {"PASS", "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS"}:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
