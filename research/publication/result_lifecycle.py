#!/usr/bin/env python3
"""Typed, fail-closed lifecycle views for scientific result records.

This module does not infer lifecycle from filenames or terminal strings.  A
directory may contain a cross-paper projection; the record's explicit
``paper_id`` and verified identities are authoritative.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "orion.scientific-result-lifecycle.v1"
EDGE_TYPES = {
    "SUPERSEDES",
    "SUCCESSOR_OF",
    "NARROWS",
    "ADJUDICATES",
    "PROJECTS",
    "AMENDS_METADATA",
}
CLAIM_AUTHORITIES = {
    "PRIMARY",
    "SECONDARY",
    "DIAGNOSTIC",
    "NEGATIVE_CONTROL",
    "SCHEMA",
}
RECORD_KINDS = {
    "SCIENTIFIC_RESULT",
    "DIAGNOSTIC_RESULT",
    "MANIFEST",
    "SCHEMA",
    "TEMPLATE",
}
LIFECYCLE_STATUSES = {"ACTIVE", "HISTORICAL"}
DISPOSITIONS = {
    "PENDING",
    "SUPPORTED",
    "ADVERSE",
    "CANNOT_CHECK",
    "NOT_APPLICABLE",
    "SCOPED",
    "INVALID_DESIGN",
}
DESIGN_VALIDITIES = {"VALID", "INVALID", "UNASSESSED"}
GATE_ROLES = {
    "CLAIM_DECISION",
    "INTEGRITY_GATE",
    "DIAGNOSTIC",
    "EXPECTED_NEGATIVE_CONTROL",
}
REQUIRED = {
    "schema_version",
    "paper_id",
    "claim_id",
    "claim_scope",
    "study_id",
    "record_id",
    "lifecycle_status",
    "record_kind",
    "claim_authority",
    "disposition",
    "estimand_id",
    "population_id",
    "outcome_id",
    "decision_rule_id",
    "measurement_id",
    "protocol_digest",
    "dataset_digest",
    "comparator_set_digest",
    "visibility_contract_digest",
    "cluster_id",
    "cluster_members",
    "edge_type",
    "parent_record_id",
    "is_projection",
    "design_validity",
    "gate_role",
    "terminal",
    "result",
    "result_digest",
}
SAME_STUDY_COORDINATES = (
    "paper_id",
    "claim_id",
    "study_id",
    "estimand_id",
    "population_id",
    "outcome_id",
    "decision_rule_id",
    "protocol_digest",
    "comparator_set_digest",
)
_PAPER = re.compile(r"^P(?:[1-9]|1[0-5])$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_CLAIM = re.compile(r"^P(?:[1-9]|1[0-5])\.[A-Za-z0-9_-]+\.[A-Za-z0-9_.-]+$")


class LifecycleError(ValueError):
    """A record or graph cannot support an authoritative lifecycle view."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest_result(result: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(result)).hexdigest()


def validate_record(record: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED - set(record))
    if missing:
        raise LifecycleError(f"record missing required fields: {missing}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise LifecycleError("unsupported lifecycle schema")
    if not isinstance(record["paper_id"], str) or not _PAPER.fullmatch(record["paper_id"]):
        raise LifecycleError("paper_id must be P1 through P15")
    if not isinstance(record["claim_id"], str) or not _CLAIM.fullmatch(record["claim_id"]):
        raise LifecycleError("claim_id must include paper, claim, and version/study scope")
    if record["lifecycle_status"] not in LIFECYCLE_STATUSES:
        raise LifecycleError("invalid lifecycle_status")
    if record["record_kind"] not in RECORD_KINDS:
        raise LifecycleError("invalid record_kind")
    if record["claim_authority"] not in CLAIM_AUTHORITIES:
        raise LifecycleError("invalid claim_authority")
    if record["disposition"] not in DISPOSITIONS:
        raise LifecycleError("invalid disposition")
    if record["design_validity"] not in DESIGN_VALIDITIES:
        raise LifecycleError("invalid design_validity")
    if record["gate_role"] not in GATE_ROLES:
        raise LifecycleError("invalid gate_role")
    if not isinstance(record["claim_scope"], str) or not record["claim_scope"].strip():
        raise LifecycleError("claim_scope must be explicit")
    for key in (
        "protocol_digest",
        "dataset_digest",
        "comparator_set_digest",
        "visibility_contract_digest",
        "result_digest",
    ):
        if not isinstance(record[key], str) or not _DIGEST.fullmatch(record[key]):
            raise LifecycleError(f"{key} must be a sha256 digest")
    if not isinstance(record["result"], Mapping):
        raise LifecycleError("result must be an object")
    if digest_result(record["result"]) != record["result_digest"]:
        raise LifecycleError("result_digest does not match result")
    if not isinstance(record["cluster_members"], list) or not all(
        isinstance(item, str) and item for item in record["cluster_members"]
    ):
        raise LifecycleError("cluster_members must be a list of non-empty ids")
    edge = record["edge_type"]
    parent = record["parent_record_id"]
    if edge is None:
        if parent is not None:
            raise LifecycleError("parent_record_id requires edge_type")
    else:
        if edge not in EDGE_TYPES or not isinstance(parent, str) or not parent:
            raise LifecycleError("typed edge requires a parent_record_id")
    if bool(record["is_projection"]) != (edge == "PROJECTS"):
        raise LifecycleError("is_projection must exactly match a PROJECTS edge")
    if record["claim_authority"] in {"PRIMARY", "SECONDARY"} and record[
        "record_kind"
    ] != "SCIENTIFIC_RESULT":
        raise LifecycleError("claim authority requires SCIENTIFIC_RESULT")


def validate_graph(records: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    by_id: dict[str, Mapping[str, Any]] = {}
    for record in records:
        validate_record(record)
        record_id = str(record["record_id"])
        if record_id in by_id:
            raise LifecycleError(f"duplicate record_id {record_id}")
        by_id[record_id] = record

    for record in records:
        parent_id = record["parent_record_id"]
        if parent_id is None:
            continue
        if parent_id not in by_id:
            raise LifecycleError(f"missing parent record {parent_id}")
        parent = by_id[parent_id]
        edge = record["edge_type"]
        if edge == "SUPERSEDES":
            changed = [
                key
                for key in SAME_STUDY_COORDINATES
                if record[key] != parent[key]
            ]
            if changed:
                raise LifecycleError(
                    "SUPERSEDES may not change frozen study coordinates: "
                    + ", ".join(changed)
                )
        if edge == "AMENDS_METADATA" and record["result_digest"] != parent["result_digest"]:
            raise LifecycleError("AMENDS_METADATA may not change result content")

    for start in by_id:
        seen: set[str] = set()
        current = start
        while by_id[current]["parent_record_id"] is not None:
            if current in seen:
                raise LifecycleError("lifecycle graph contains a cycle")
            seen.add(current)
            current = str(by_id[current]["parent_record_id"])
    return by_id


def active_leaves(records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    by_id = validate_graph(records)
    superseded = {
        str(record["parent_record_id"])
        for record in records
        if record["edge_type"] == "SUPERSEDES"
        and record["lifecycle_status"] == "ACTIVE"
    }
    leaves = [
        record
        for record_id, record in by_id.items()
        if record_id not in superseded
        and record["lifecycle_status"] == "ACTIVE"
        and record["claim_authority"] in {"PRIMARY", "SECONDARY"}
        and record["record_kind"] == "SCIENTIFIC_RESULT"
        and not record["is_projection"]
    ]
    return sorted(leaves, key=lambda row: (row["paper_id"], row["claim_id"], row["record_id"]))


def publication_view(records: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    by_id = validate_graph(records)
    leaves = active_leaves(records)
    historical: dict[str, Mapping[str, Any]] = {}
    for leaf in leaves:
        parent_id = leaf["parent_record_id"]
        while parent_id is not None:
            parent = by_id[str(parent_id)]
            if parent["disposition"] == "ADVERSE":
                historical[str(parent["record_id"])] = parent
            parent_id = parent["parent_record_id"]
    return {
        "active_leaves": leaves,
        "historical_adverse_ancestors": sorted(
            historical.values(), key=lambda row: (row["paper_id"], row["record_id"])
        ),
    }


def diagnostic_measurements(
    records: Iterable[Mapping[str, Any]],
) -> dict[tuple[str, str], list[str]]:
    """Return deduplicated diagnostic identities, never path-based counts."""

    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    seen_content: dict[tuple[str, str], str] = {}
    for record in records:
        validate_record(record)
        if record["is_projection"]:
            continue
        if record["record_kind"] not in {"SCIENTIFIC_RESULT", "DIAGNOSTIC_RESULT"}:
            continue
        if record["claim_authority"] in {"SCHEMA", "NEGATIVE_CONTROL"}:
            continue
        if record["gate_role"] == "EXPECTED_NEGATIVE_CONTROL":
            continue
        identity = (str(record["paper_id"]), str(record["measurement_id"]))
        prior = seen_content.get(identity)
        if prior is not None and prior != record["result_digest"]:
            raise LifecycleError(
                f"measurement identity {identity} has conflicting result content"
            )
        seen_content[identity] = str(record["result_digest"])
        groups[identity].append(str(record["record_id"]))
    return dict(sorted(groups.items()))

