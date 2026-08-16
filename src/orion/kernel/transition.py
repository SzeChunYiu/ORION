from __future__ import annotations

import hashlib
import json
import math
import struct
import unicodedata
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from orion.mechanics.model import (
    DimensionWaiver,
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.answers import AnswerRecord

CANONICALIZATION_VERSION = "orion.typed-canonical.v1"
UNICODE_POLICY = "orion.unicode.ucd3.2-nfc-assigned.v1"
_UNICODE_DATABASE = unicodedata.ucd_3_2_0
UNICODE_DATABASE_VERSION = _UNICODE_DATABASE.unidata_version
PROJECTION_SCHEMA_VERSION = "orion.program-projection.v1"
WORKFLOW_VERSION = "orion.mechanics-workflow.v1"
REDUCER_VERSION = "orion.answer-reducer.v1"
MAX_CANONICAL_BYTES = 8_388_608
MAX_CANONICAL_DEPTH = 128
MAX_CANONICAL_NODES = 100_000

_CANONICAL_PREFIX = b"ORION-CANONICAL-DIGEST\x00"
_PROJECTION_DOMAIN = "orion.program-projection.v1"
_HEX_DIGITS = frozenset("0123456789abcdef")


class CanonicalizationError(ValueError):
    """Raised when a value has no unambiguous ORION canonical representation."""


class TransitionKind(str, Enum):
    """Kinds of proposed state change; membership grants no authority."""

    ANSWER = "ANSWER"
    REVALIDATE = "REVALIDATE"
    REOPEN = "REOPEN"
    AUTHORITY_SUPPORT_UPDATE = "AUTHORITY_SUPPORT_UPDATE"


def _require_nfc(value: str, field_name: str) -> None:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError(f"{field_name} cannot contain lone surrogates") from error
    if any(_UNICODE_DATABASE.category(character) == "Cn" for character in value):
        raise ValueError(
            f"{field_name} contains a code point not assigned in Unicode 3.2"
        )
    if _UNICODE_DATABASE.normalize("NFC", value) != value:
        raise ValueError(f"{field_name} must be in Unicode NFC")


def _require_text(value: str, field_name: str) -> None:
    if type(value) is not str or not value or value != value.strip():
        raise ValueError(f"{field_name} must be nonblank exact text")
    _require_nfc(value, field_name)


def _require_sha256(value: str, field_name: str) -> None:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 digest")


def _typed_value(
    value: Any, *, active: set[int], depth: int, nodes: list[int]
) -> Any:
    """Map exact built-in values to a typed, deterministic JSON tree."""

    if depth > MAX_CANONICAL_DEPTH:
        raise CanonicalizationError("canonical value exceeds the maximum depth")
    nodes[0] += 1
    if nodes[0] > MAX_CANONICAL_NODES:
        raise CanonicalizationError("canonical value exceeds the maximum node count")
    if value is None:
        return ["null"]
    if type(value) is bool:
        return ["bool", value]
    if type(value) is int:
        magnitude = abs(value)
        octets = magnitude.to_bytes(max(1, (magnitude.bit_length() + 7) // 8), "big")
        return ["int-sign-magnitude", [int(value < 0), octets.hex()]]
    if type(value) is str:
        try:
            _require_nfc(value, "canonical text")
        except ValueError as error:
            raise CanonicalizationError(str(error)) from error
        return ["str", value]
    if type(value) is float:
        if not math.isfinite(value):
            raise CanonicalizationError("non-finite floats have no canonical form")
        return ["float64-bits", struct.pack(">d", value).hex()]

    if type(value) not in {dict, list, tuple}:
        raise CanonicalizationError(
            f"unsupported canonical type: {value.__class__.__module__}."
            f"{value.__class__.__qualname__}"
        )

    object_id = id(value)
    if object_id in active:
        raise CanonicalizationError("cyclic values have no canonical form")
    active.add(object_id)
    try:
        if type(value) is dict:
            entries: list[list[Any]] = []
            for key, item in value.items():
                if type(key) is not str:
                    raise CanonicalizationError("canonical mappings require string keys")
                try:
                    _require_nfc(key, "canonical mapping key")
                except ValueError as error:
                    raise CanonicalizationError(str(error)) from error
                entries.append(
                    [
                        ["str", key],
                        _typed_value(
                            item, active=active, depth=depth + 1, nodes=nodes
                        ),
                    ]
                )
            entries.sort(key=lambda entry: entry[0][1].encode("utf-8"))
            return ["map", entries]
        tag = "list" if type(value) is list else "tuple"
        return [
            tag,
            [
                _typed_value(item, active=active, depth=depth + 1, nodes=nodes)
                for item in value
            ],
        ]
    finally:
        active.remove(object_id)


def canonical_json_bytes(value: Any) -> bytes:
    """Encode ORION's versioned typed tree; this is not ordinary JSON identity."""

    envelope = [
        "orion-typed-canonical",
        CANONICALIZATION_VERSION,
        UNICODE_POLICY,
        UNICODE_DATABASE_VERSION,
        _typed_value(value, active=set(), depth=0, nodes=[0]),
    ]
    try:
        encoded = json.dumps(
            envelope,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as error:
        raise CanonicalizationError("value cannot be encoded canonically") from error
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise CanonicalizationError("canonical value exceeds the maximum byte count")
    return encoded


def _decode_typed(node: Any, *, depth: int, nodes: list[int]) -> Any:
    if depth > MAX_CANONICAL_DEPTH:
        raise CanonicalizationError("canonical value exceeds the maximum depth")
    nodes[0] += 1
    if nodes[0] > MAX_CANONICAL_NODES:
        raise CanonicalizationError("canonical value exceeds the maximum node count")
    if type(node) is not list or not node or type(node[0]) is not str:
        raise CanonicalizationError("canonical typed value must be a tagged array")
    tag = node[0]
    if tag == "null" and len(node) == 1:
        return None
    if tag == "bool" and len(node) == 2 and type(node[1]) is bool:
        return node[1]
    if tag == "int-sign-magnitude" and len(node) == 2:
        parts = node[1]
        if (
            type(parts) is not list
            or len(parts) != 2
            or type(parts[0]) is not int
            or parts[0] not in {0, 1}
            or type(parts[1]) is not str
            or len(parts[1]) < 2
            or len(parts[1]) % 2
            or any(character not in _HEX_DIGITS for character in parts[1])
            or (len(parts[1]) > 2 and parts[1].startswith("00"))
        ):
            raise CanonicalizationError("invalid canonical integer payload")
        magnitude = int.from_bytes(bytes.fromhex(parts[1]), "big")
        if parts[0] == 1 and magnitude == 0:
            raise CanonicalizationError("canonical integers forbid negative zero")
        return -magnitude if parts[0] else magnitude
    if tag == "str" and len(node) == 2 and type(node[1]) is str:
        try:
            _require_nfc(node[1], "canonical text")
        except ValueError as error:
            raise CanonicalizationError(str(error)) from error
        return node[1]
    if tag == "float64-bits" and len(node) == 2:
        bits = node[1]
        if (
            type(bits) is not str
            or len(bits) != 16
            or any(character not in _HEX_DIGITS for character in bits)
        ):
            raise CanonicalizationError("invalid canonical float64 payload")
        value = struct.unpack(">d", bytes.fromhex(bits))[0]
        if not math.isfinite(value):
            raise CanonicalizationError("non-finite floats have no canonical form")
        return value
    if tag in {"list", "tuple"} and len(node) == 2 and type(node[1]) is list:
        values = [
            _decode_typed(item, depth=depth + 1, nodes=nodes) for item in node[1]
        ]
        return values if tag == "list" else tuple(values)
    if tag == "map" and len(node) == 2 and type(node[1]) is list:
        decoded: dict[str, Any] = {}
        for entry in node[1]:
            if type(entry) is not list or len(entry) != 2:
                raise CanonicalizationError("invalid canonical mapping entry")
            key = _decode_typed(entry[0], depth=depth + 1, nodes=nodes)
            if type(key) is not str:
                raise CanonicalizationError("canonical mappings require string keys")
            if key in decoded:
                raise CanonicalizationError("canonical mapping keys must be unique")
            decoded[key] = _decode_typed(
                entry[1], depth=depth + 1, nodes=nodes
            )
        return decoded
    raise CanonicalizationError(f"unknown or malformed canonical tag: {tag!r}")


def canonical_json_loads(data: bytes) -> Any:
    """Decode only exact v1 canonical bytes; alternate encodings fail closed."""

    if type(data) is not bytes:
        raise CanonicalizationError("canonical input must be exact bytes")
    if len(data) > MAX_CANONICAL_BYTES:
        raise CanonicalizationError("canonical input exceeds the maximum byte count")

    def parse_int(token: str) -> int:
        if token not in {"0", "1"}:
            raise CanonicalizationError("unexpected canonical JSON integer token")
        return 0 if token == "0" else 1

    def reject_float(token: str) -> float:
        raise CanonicalizationError(
            f"unexpected canonical JSON floating-point token: {token!r}"
        )

    def reject_constant(token: str) -> None:
        raise CanonicalizationError(f"unexpected canonical JSON constant: {token!r}")

    try:
        node = json.loads(
            data.decode("utf-8"),
            parse_int=parse_int,
            parse_float=reject_float,
            parse_constant=reject_constant,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise CanonicalizationError("invalid canonical JSON bytes") from error
    if type(node) is not list or len(node) != 5:
        raise CanonicalizationError("invalid canonical envelope")
    if node[0] != "orion-typed-canonical":
        raise CanonicalizationError("invalid canonical envelope marker")
    if node[1] != CANONICALIZATION_VERSION:
        raise CanonicalizationError("unsupported canonicalization version")
    if node[2] != UNICODE_POLICY:
        raise CanonicalizationError("unsupported canonical Unicode policy")
    if node[3] != UNICODE_DATABASE_VERSION:
        raise CanonicalizationError("unsupported canonical Unicode database version")
    try:
        value = _decode_typed(node[4], depth=0, nodes=[0])
    except RecursionError as error:
        raise CanonicalizationError("canonical value exceeds recursion limits") from error
    if canonical_json_bytes(value) != data:
        raise CanonicalizationError("input is not the canonical byte representation")
    return value


def canonical_digest(value: Any, *, domain: str) -> str:
    """Return a versioned, domain-separated SHA-256 commitment."""

    try:
        _require_text(domain, "domain")
    except ValueError as error:
        raise CanonicalizationError(str(error)) from error
    domain_bytes = domain.encode("utf-8")
    encoded = (
        _CANONICAL_PREFIX
        + len(domain_bytes).to_bytes(4, "big")
        + domain_bytes
        + canonical_json_bytes(value)
    )
    return hashlib.sha256(encoded).hexdigest()


def _handoff_payload(field: HandoffField) -> dict[str, Any]:
    return {
        "field_id": field.field_id,
        "description": field.description,
        "schema_ref": field.schema_ref,
        "required": field.required,
    }


def _metric_payload(metric: MetricSpec) -> dict[str, Any]:
    return {
        "metric_id": metric.metric_id,
        "description": metric.description,
        "kind": metric.kind.value,
        "direction": metric.direction.value,
        "unit": metric.unit,
        "required_for_handoff": metric.required_for_handoff,
        "threshold_semantics": metric.threshold_semantics,
        "uncertainty_semantics": metric.uncertainty_semantics,
    }


def _waiver_payload(waiver: DimensionWaiver) -> dict[str, Any]:
    return {"dimension": waiver.dimension.value, "reason": waiver.reason}


def _require_exact_tuple(value: Any, field_name: str) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an exact immutable tuple")


def _require_exact_string(value: Any, field_name: str) -> None:
    if type(value) is not str:
        raise ValueError(f"{field_name} must be an exact immutable string")


def _validate_handoff_field(field: HandoffField, field_name: str) -> None:
    if type(field) is not HandoffField:
        raise ValueError(f"{field_name} must contain exact HandoffField values")
    for name in ("field_id", "description", "schema_ref"):
        _require_exact_string(getattr(field, name), f"{field_name}.{name}")
    if type(field.required) is not bool:
        raise ValueError(f"{field_name}.required must be an exact bool")


def _validate_metric(metric: MetricSpec, field_name: str) -> None:
    if type(metric) is not MetricSpec:
        raise ValueError(f"{field_name} must contain exact MetricSpec values")
    for name in (
        "metric_id",
        "description",
        "unit",
        "threshold_semantics",
        "uncertainty_semantics",
    ):
        _require_exact_string(getattr(metric, name), f"{field_name}.{name}")
    if type(metric.kind) is not MetricKind:
        raise ValueError(f"{field_name}.kind must be an exact MetricKind")
    if type(metric.direction) is not MetricDirection:
        raise ValueError(f"{field_name}.direction must be an exact MetricDirection")
    if type(metric.required_for_handoff) is not bool:
        raise ValueError(f"{field_name}.required_for_handoff must be an exact bool")


def _validate_mechanic_cell(cell: MechanicCell) -> None:
    if type(cell) is not MechanicCell:
        raise ValueError("seed_cells must contain exact MechanicCell values")
    scalar_fields = {"mechanic_id", "purpose", "scope"}
    for field in fields(MechanicCell):
        value = getattr(cell, field.name)
        if field.name in scalar_fields:
            _require_exact_string(value, f"MechanicCell.{field.name}")
        else:
            _require_exact_tuple(value, f"MechanicCell.{field.name}")
    for field_name in (
        "input_ids",
        "output_ids",
        "state_ids",
        "observable_ids",
        "action_ids",
        "transition_semantics",
        "mathematical_semantics",
        "invariant_ids",
        "constraint_ids",
        "objective_ids",
        "optimization_rules",
        "uncertainty_semantics",
        "resource_coordinates",
        "failure_signatures",
        "falsifiers",
        "diagnosis_rules",
        "storage_contracts",
        "provenance_contracts",
        "verification_contracts",
        "authority_boundaries",
        "engineering_contracts",
        "dependency_ids",
        "external_dependency_contract_ids",
        "child_mechanic_ids",
        "reopen_triggers",
        "search_coverage_obligations",
        "parent_domain_hypotheses",
        "saturation_criteria",
        "empirical_open_coordinates",
    ):
        for item in getattr(cell, field_name):
            _require_exact_string(item, f"MechanicCell.{field_name} item")
    for item in cell.handoff_fields:
        _validate_handoff_field(item, "MechanicCell.handoff_fields")
    for item in cell.metrics:
        _validate_metric(item, "MechanicCell.metrics")
    for item in cell.provisional_dimensions:
        if type(item) is not MechanicDimension:
            raise ValueError(
                "MechanicCell.provisional_dimensions must contain exact dimensions"
            )
    for item in cell.waivers:
        if type(item) is not DimensionWaiver:
            raise ValueError("MechanicCell.waivers must contain exact waivers")
        if type(item.dimension) is not MechanicDimension:
            raise ValueError("DimensionWaiver.dimension must be an exact dimension")
        _require_exact_string(item.reason, "DimensionWaiver.reason")


def _validate_answer_record(record: AnswerRecord) -> None:
    if type(record) is not AnswerRecord:
        raise ValueError("records must contain exact AnswerRecord values")
    for field_name in (
        "record_id",
        "mechanic_id",
        "lane",
        "waiver_reason",
        "supersedes",
    ):
        _require_exact_string(getattr(record, field_name), f"AnswerRecord.{field_name}")
    if type(record.dimension) is not MechanicDimension:
        raise ValueError("AnswerRecord.dimension must be an exact dimension")
    for field_name in (
        "evidence_refs",
        "evidence_bindings",
        "payload",
        "handoff_payload",
    ):
        _require_exact_tuple(getattr(record, field_name), f"AnswerRecord.{field_name}")
    for item in record.evidence_refs:
        _require_exact_string(item, "AnswerRecord.evidence_refs item")
    for item in record.evidence_bindings:
        _require_exact_tuple(item, "AnswerRecord.evidence_bindings item")
        if len(item) != 2:
            raise ValueError("AnswerRecord.evidence_bindings items must have length two")
        for value in item:
            _require_exact_string(value, "AnswerRecord.evidence_bindings value")
    for item in record.payload:
        _require_exact_tuple(item, "AnswerRecord.payload item")
        if len(item) != 2:
            raise ValueError("AnswerRecord.payload items must have length two")
        field_name, values = item
        _require_exact_string(field_name, "AnswerRecord.payload field")
        _require_exact_tuple(values, "AnswerRecord.payload values")
        for value in values:
            _require_exact_string(value, "AnswerRecord.payload value")
    for item in record.handoff_payload:
        _validate_handoff_field(item, "AnswerRecord.handoff_payload")


def canonical_answer_record(record: AnswerRecord) -> dict[str, Any]:
    """Return proposal data only; this representation grants no authority."""

    try:
        _validate_answer_record(record)
    except ValueError as error:
        raise CanonicalizationError(str(error)) from error
    payload_fields = [field_name for field_name, _ in record.payload]
    if len(set(payload_fields)) != len(payload_fields):
        raise CanonicalizationError("answer record payload fields must be unique")
    handoff_ids = [item.field_id for item in record.handoff_payload]
    if len(set(handoff_ids)) != len(handoff_ids):
        raise CanonicalizationError("answer record handoff fields must be unique")
    return {
        "record_id": record.record_id,
        "mechanic_id": record.mechanic_id,
        "dimension": record.dimension.value,
        "lane": record.lane,
        "evidence_refs": sorted(record.evidence_refs),
        "evidence_bindings": [
            list(item) for item in sorted(record.evidence_bindings)
        ],
        "payload": [
            [field_name, list(values)]
            for field_name, values in sorted(record.payload)
        ],
        "handoff_payload": [
            _handoff_payload(item)
            for item in sorted(record.handoff_payload, key=lambda item: item.field_id)
        ],
        "waiver_reason": record.waiver_reason,
        "supersedes": record.supersedes,
    }


def answer_record_hash(record: AnswerRecord) -> str:
    """Commit the complete proposal body under the answer-record domain."""

    return canonical_digest(
        canonical_answer_record(record), domain="orion.answer-record.v1"
    )


def canonical_mechanic_cell(cell: MechanicCell) -> dict[str, Any]:
    """Return the complete explicit wire identity of one mechanic cell."""

    try:
        _validate_mechanic_cell(cell)
    except ValueError as error:
        raise CanonicalizationError(str(error)) from error
    return {
        "mechanic_id": cell.mechanic_id,
        "purpose": cell.purpose,
        "scope": cell.scope,
        "input_ids": list(cell.input_ids),
        "output_ids": list(cell.output_ids),
        "handoff_fields": [
            _handoff_payload(item)
            for item in sorted(cell.handoff_fields, key=lambda item: item.field_id)
        ],
        "state_ids": list(cell.state_ids),
        "observable_ids": list(cell.observable_ids),
        "action_ids": list(cell.action_ids),
        "transition_semantics": list(cell.transition_semantics),
        "mathematical_semantics": list(cell.mathematical_semantics),
        "invariant_ids": list(cell.invariant_ids),
        "constraint_ids": list(cell.constraint_ids),
        "objective_ids": list(cell.objective_ids),
        "metrics": [
            _metric_payload(item)
            for item in sorted(cell.metrics, key=lambda item: item.metric_id)
        ],
        "optimization_rules": list(cell.optimization_rules),
        "uncertainty_semantics": list(cell.uncertainty_semantics),
        "resource_coordinates": list(cell.resource_coordinates),
        "failure_signatures": list(cell.failure_signatures),
        "falsifiers": list(cell.falsifiers),
        "diagnosis_rules": list(cell.diagnosis_rules),
        "storage_contracts": list(cell.storage_contracts),
        "provenance_contracts": list(cell.provenance_contracts),
        "verification_contracts": list(cell.verification_contracts),
        "authority_boundaries": list(cell.authority_boundaries),
        "engineering_contracts": list(cell.engineering_contracts),
        "dependency_ids": list(cell.dependency_ids),
        "external_dependency_contract_ids": list(
            cell.external_dependency_contract_ids
        ),
        "child_mechanic_ids": list(cell.child_mechanic_ids),
        "reopen_triggers": list(cell.reopen_triggers),
        "search_coverage_obligations": list(cell.search_coverage_obligations),
        "parent_domain_hypotheses": list(cell.parent_domain_hypotheses),
        "saturation_criteria": list(cell.saturation_criteria),
        "empirical_open_coordinates": list(cell.empirical_open_coordinates),
        "provisional_dimensions": sorted(
            item.value for item in cell.provisional_dimensions
        ),
        "waivers": [
            _waiver_payload(item)
            for item in sorted(cell.waivers, key=lambda item: item.dimension.value)
        ],
    }


@dataclass(frozen=True)
class LedgerExpectation:
    """All revisions a protected transition must compare at commit time."""

    ledger_head: str | None
    research_state_hash: str
    authority_revision: str
    support_revision: str

    def __post_init__(self) -> None:
        if self.ledger_head is not None:
            _require_sha256(self.ledger_head, "ledger_head")
        _require_sha256(self.research_state_hash, "research_state_hash")
        _require_sha256(self.authority_revision, "authority_revision")
        _require_sha256(self.support_revision, "support_revision")


@dataclass(frozen=True)
class ProgramProjection:
    """Canonical mechanics-reducer state, not ORION's complete global state.

    The exact seed and complete structurally admissible record graph make
    supersession reversible by recomputation. Candidate inventory, evidence, authority,
    support, knowledge-read state, and transaction history remain separately
    revisioned inputs; constructing this value grants none of those authorities.
    """

    schema_version: str
    workflow_version: str
    reducer_version: str
    seed_cells: tuple[MechanicCell, ...]
    records: tuple[AnswerRecord, ...] = ()
    active_record_ids: tuple[str, ...] = ()
    reopened_coordinates: tuple[tuple[str, str, str], ...] = ()

    def __post_init__(self) -> None:
        expected_versions = (
            ("schema_version", self.schema_version, PROJECTION_SCHEMA_VERSION),
            ("workflow_version", self.workflow_version, WORKFLOW_VERSION),
            ("reducer_version", self.reducer_version, REDUCER_VERSION),
        )
        for field_name, actual, expected in expected_versions:
            _require_text(actual, field_name)
            if actual != expected:
                raise ValueError(f"unsupported {field_name}: {actual!r}")

        for field_name in (
            "seed_cells",
            "records",
            "active_record_ids",
            "reopened_coordinates",
        ):
            _require_exact_tuple(getattr(self, field_name), field_name)
        for cell in self.seed_cells:
            _validate_mechanic_cell(cell)
        for record in self.records:
            _validate_answer_record(record)
        for record_id in self.active_record_ids:
            _require_exact_string(record_id, "active_record_ids item")
        for coordinate in self.reopened_coordinates:
            _require_exact_tuple(coordinate, "reopened_coordinates item")
            if len(coordinate) != 3:
                raise ValueError("reopened coordinate must have exactly three fields")
            for value in coordinate:
                _require_exact_string(value, "reopened coordinate value")

        mechanic_ids = tuple(cell.mechanic_id for cell in self.seed_cells)
        if len(set(mechanic_ids)) != len(mechanic_ids):
            raise ValueError("projection mechanic ids must be unique")

        reopened_coordinates: list[tuple[str, str]] = []
        for mechanic_id, dimension, reason in self.reopened_coordinates:
            _require_text(mechanic_id, "reopened mechanic_id")
            _require_text(dimension, "reopened dimension")
            _require_text(reason, "reopened reason")
            if mechanic_id not in mechanic_ids:
                raise ValueError("reopened coordinate targets an unknown mechanic")
            if dimension not in {item.value for item in MechanicDimension}:
                raise ValueError("reopened coordinate uses an unknown dimension")
            reopened_coordinates.append((mechanic_id, dimension))
        if len(set(reopened_coordinates)) != len(reopened_coordinates):
            raise ValueError("reopened coordinates must be unique")
        reopened_set = set(reopened_coordinates)

        record_ids = [record.record_id for record in self.records]
        if len(set(record_ids)) != len(record_ids):
            raise ValueError("projection records must have unique record ids")

        by_id = {record.record_id: record for record in self.records}
        children: dict[str, list[str]] = {record_id: [] for record_id in by_id}
        grouped: dict[tuple[str, MechanicDimension], list[AnswerRecord]] = {}
        for record in self.records:
            if record.mechanic_id not in mechanic_ids:
                raise ValueError("projection record targets an unknown mechanic")
            payload_fields = [field_name for field_name, _ in record.payload]
            if len(set(payload_fields)) != len(payload_fields):
                raise ValueError("accepted record payload fields must be unique")
            handoff_ids = [item.field_id for item in record.handoff_payload]
            if len(set(handoff_ids)) != len(handoff_ids):
                raise ValueError("accepted record handoff fields must be unique")
            grouped.setdefault((record.mechanic_id, record.dimension), []).append(record)
            if not record.supersedes:
                continue
            parent = by_id.get(record.supersedes)
            if parent is None:
                raise ValueError("projection record has a missing supersession parent")
            if (parent.mechanic_id, parent.dimension) != (
                record.mechanic_id,
                record.dimension,
            ):
                raise ValueError("supersession parent must share the record coordinate")
            children[parent.record_id].append(record.record_id)
            if len(children[parent.record_id]) > 1:
                raise ValueError("projection record graph contains a supersession branch")

        for record in self.records:
            visited: set[str] = set()
            current = record
            while current.supersedes:
                if current.record_id in visited:
                    raise ValueError("projection record graph contains a cycle")
                visited.add(current.record_id)
                current = by_id[current.supersedes]

        expected_tips: set[str] = set()
        for group in grouped.values():
            roots = [record for record in group if not record.supersedes]
            if len(roots) != 1:
                raise ValueError("projection record coordinate must have one root")
            tips = [record for record in group if not children[record.record_id]]
            if len(tips) != 1:
                raise ValueError("projection record coordinate must have one tip")
            visited: set[str] = set()
            current = tips[0]
            while True:
                if current.record_id in visited:
                    raise ValueError("projection record graph contains a cycle")
                visited.add(current.record_id)
                if not current.supersedes:
                    break
                current = by_id[current.supersedes]
            if len(visited) != len(group):
                raise ValueError("projection record graph is disconnected or cyclic")
            coordinate = (tips[0].mechanic_id, tips[0].dimension.value)
            if coordinate not in reopened_set:
                expected_tips.add(tips[0].record_id)

        if len(set(self.active_record_ids)) != len(self.active_record_ids):
            raise ValueError("active record ids must be unique")
        unknown_active = set(self.active_record_ids) - set(record_ids)
        if unknown_active:
            raise ValueError("projection contains an unknown active record id")
        active_coordinates = {
            (by_id[record_id].mechanic_id, by_id[record_id].dimension.value)
            for record_id in self.active_record_ids
        }
        if active_coordinates & reopened_set:
            raise ValueError("reopened coordinates cannot retain an active record id")
        if set(self.active_record_ids) != expected_tips:
            raise ValueError("active record ids must equal the record graph tips")

    @property
    def seed_hash(self) -> str:
        """Identity of the exact immutable seed cells."""

        payload = [
            canonical_mechanic_cell(item)
            for item in sorted(self.seed_cells, key=lambda item: item.mechanic_id)
        ]
        return canonical_digest(payload, domain="orion.program-seed.v1")

    @property
    def record_bindings(self) -> tuple[tuple[str, str], ...]:
        """Recomputed labels and body digests for the complete record graph."""

        return tuple(
            sorted(
                (record.record_id, answer_record_hash(record))
                for record in self.records
            )
        )

    @property
    def active_records(self) -> tuple[AnswerRecord, ...]:
        """Complete bodies of the current graph tips."""

        active = set(self.active_record_ids)
        return tuple(
            sorted(
                (record for record in self.records if record.record_id in active),
                key=lambda record: (
                    record.mechanic_id,
                    record.dimension.value,
                    record.record_id,
                ),
            )
        )

    @property
    def active_record_tips(self) -> tuple[tuple[str, str, str], ...]:
        """Coordinate-to-record view derived from the active record bodies."""

        return tuple(
            (record.mechanic_id, record.dimension.value, record.record_id)
            for record in self.active_records
        )


def canonical_program_projection(projection: ProgramProjection) -> dict[str, Any]:
    """Return the complete mechanics-reducer normal-form identity."""

    return {
        "schema_version": projection.schema_version,
        "workflow_version": projection.workflow_version,
        "reducer_version": projection.reducer_version,
        "seed_hash": projection.seed_hash,
        "seed_cells": [
            canonical_mechanic_cell(item)
            for item in sorted(
                projection.seed_cells, key=lambda item: item.mechanic_id
            )
        ],
        "record_bindings": [
            [record_id, record_hash]
            for record_id, record_hash in projection.record_bindings
        ],
        "records": [
            canonical_answer_record(item)
            for item in sorted(projection.records, key=lambda item: item.record_id)
        ],
        "active_record_tips": [
            [mechanic_id, dimension, record_id]
            for mechanic_id, dimension, record_id in projection.active_record_tips
        ],
        "reopened_coordinates": [
            [mechanic_id, dimension, reason]
            for mechanic_id, dimension, reason in sorted(
                projection.reopened_coordinates
            )
        ],
    }


def projection_hash(projection: ProgramProjection) -> str:
    """Commit the exact versioned projection under a dedicated digest domain."""

    return canonical_digest(
        canonical_program_projection(projection), domain=_PROJECTION_DOMAIN
    )


__all__ = [
    "CANONICALIZATION_VERSION",
    "MAX_CANONICAL_BYTES",
    "MAX_CANONICAL_DEPTH",
    "MAX_CANONICAL_NODES",
    "PROJECTION_SCHEMA_VERSION",
    "REDUCER_VERSION",
    "UNICODE_DATABASE_VERSION",
    "UNICODE_POLICY",
    "WORKFLOW_VERSION",
    "CanonicalizationError",
    "LedgerExpectation",
    "ProgramProjection",
    "TransitionKind",
    "answer_record_hash",
    "canonical_answer_record",
    "canonical_digest",
    "canonical_json_bytes",
    "canonical_json_loads",
    "canonical_mechanic_cell",
    "canonical_program_projection",
    "projection_hash",
]
