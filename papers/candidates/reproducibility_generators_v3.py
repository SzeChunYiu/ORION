"""Fail-closed helpers for P6--P8 versioned JSONL generators.

This module deliberately supports a small JSON-Schema subset using only the
standard library.  It is a reproducibility boundary, not a general schema
engine.  Every accepted schema must be non-empty and every generated record is
validated before bytes are compared or written.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_record(record: Mapping[str, Any]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def canonical_jsonl(records: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(canonical_record(record) for record in records)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    if not records:
        raise ValueError(f"{path}: generator source is empty")
    return records


def load_schema(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: schema must be an object")
    required = value.get("required")
    properties = value.get("properties")
    if (
        value.get("type") != "object"
        or not isinstance(required, list)
        or not required
        or not all(isinstance(field, str) and field for field in required)
        or not isinstance(properties, dict)
        or not properties
        or not set(required).issubset(properties)
    ):
        raise ValueError(f"{path}: schema has no enforceable required properties")
    return value


def _is_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported schema type: {expected}")


def _validate_value(value: Any, rule: Mapping[str, Any], location: str) -> None:
    expected = rule.get("type")
    if isinstance(expected, str) and not _is_type(value, expected):
        raise ValueError(f"{location}: expected {expected}")
    enum = rule.get("enum")
    if isinstance(enum, list) and value not in enum:
        raise ValueError(f"{location}: value not in enum")
    if isinstance(value, str):
        minimum = rule.get("minLength")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ValueError(f"{location}: string shorter than {minimum}")
    if isinstance(value, list):
        minimum = rule.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ValueError(f"{location}: array shorter than {minimum}")
        item_rule = rule.get("items")
        if isinstance(item_rule, dict):
            for index, item in enumerate(value):
                _validate_value(item, item_rule, f"{location}[{index}]")
    if isinstance(value, dict):
        nested_required = rule.get("required", [])
        nested_properties = rule.get("properties", {})
        if isinstance(nested_required, list):
            missing = set(nested_required) - set(value)
            if missing:
                raise ValueError(f"{location}: missing {sorted(missing)}")
        if isinstance(nested_properties, dict):
            for key, nested_rule in nested_properties.items():
                if key in value and isinstance(nested_rule, dict):
                    _validate_value(value[key], nested_rule, f"{location}.{key}")


def validate_records(records: Sequence[Mapping[str, Any]], schema: Mapping[str, Any]) -> None:
    required = set(schema["required"])
    properties = schema["properties"]
    identifiers: set[str] = set()
    for index, record in enumerate(records):
        missing = required - set(record)
        if missing:
            raise ValueError(f"record[{index}]: missing {sorted(missing)}")
        for key, rule in properties.items():
            if key in record and isinstance(rule, dict):
                _validate_value(record[key], rule, f"record[{index}].{key}")
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"record[{index}]: non-empty id required")
        if identifier in identifiers:
            raise ValueError(f"duplicate id: {identifier}")
        identifiers.add(identifier)


def ensure_distinct_source(source: Path, target: Path) -> None:
    if source.resolve() == target.resolve():
        raise ValueError("generator source may not be its target output")


def compare_or_write(path: Path, payload: bytes, *, check: bool) -> None:
    if check:
        if not path.is_file():
            raise ValueError(f"missing generated artifact: {path}")
        if path.read_bytes() != payload:
            raise ValueError(f"generated bytes drifted: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def regenerate_jsonl(
    *,
    source: Path,
    schema_path: Path,
    target: Path,
    records: Sequence[Mapping[str, Any]],
    check: bool,
) -> bytes:
    ensure_distinct_source(source, target)
    schema = load_schema(schema_path)
    validate_records(records, schema)
    payload = canonical_jsonl(records)
    compare_or_write(target, payload, check=check)
    return payload
