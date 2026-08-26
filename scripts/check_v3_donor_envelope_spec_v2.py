#!/usr/bin/env python3
"""Fail-closed checker for the V3-DONOR-ENVELOPE-01 specification packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "research/orion-discovery-v3"
BASE_SHA = "422148dd8ab307e08f6cde1a945ccaab4bb07f1a"
ISSUE_SHA = "966221d12aa3cb93378d5a712c65fa50be7eed8cef659eb2c8d78b4c44f39215"
MATERIAL = V3 / "V3_DONOR_ENVELOPE_01_MATERIAL_REGISTRY_V2.json"
TASKS = V3 / "V3_DONOR_ENVELOPE_01_TASK_PARTITION_MANIFEST_V2.json"
PROTOCOL = V3 / "V3_DONOR_ENVELOPE_01_PROTOCOL_CANDIDATE_V2.json"
STATUS = V3 / "V3_DONOR_ENVELOPE_01_SPECIFICATION_STATUS_V2.json"
CONTENT = V3 / "V3_DONOR_ENVELOPE_01_CONTENT_MANIFEST_V2.json"
ATOMIC = V3 / "ATOMIC_NOVELTY_AND_SUPERIORITY_MAP_V1.json"
BACKLOG = V3 / "EXECUTION_BACKLOG_V1.json"


class SpecificationError(ValueError):
    """Raised when a blocked specification packet becomes inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SpecificationError(f"{path.name} must contain one JSON object")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _taxonomy_id(label: str) -> str:
    slug = re.sub(r"[^A-Z0-9]+", "_", label.upper()).strip("_")
    return f"DONOR-TAXONOMY::{slug}"


def _require_blocked_identity(document: dict[str, Any], name: str) -> None:
    if document.get("job_id") != "V3-DONOR-ENVELOPE-01":
        raise SpecificationError(f"{name}: wrong job_id")
    if document.get("authoritative_v3_base_git_sha") != BASE_SHA:
        raise SpecificationError(f"{name}: wrong authoritative V3 base")
    issue = document.get("issue_1329_body", {})
    if issue.get("sha256") != ISSUE_SHA or issue.get("atom_count_statement") != 25:
        raise SpecificationError(f"{name}: stale issue #1329 binding")
    if document.get("outcomes_accessed") is not False:
        raise SpecificationError(f"{name}: outcomes_accessed must remain false")
    if document.get("execution_authorized") is not False:
        raise SpecificationError(f"{name}: execution_authorized must remain false")
    if document.get("paper_authority_delta") != "NONE":
        raise SpecificationError(f"{name}: paper authority must remain NONE")
    if document.get("external_novelty") != "CANNOT_CHECK":
        raise SpecificationError(f"{name}: external novelty must remain CANNOT_CHECK")


def _require_null_fields(record: dict[str, Any], paths: list[str], label: str) -> None:
    for dotted in paths:
        value: Any = record
        for component in dotted.split("."):
            if not isinstance(value, dict) or component not in value:
                raise SpecificationError(f"{label}: missing declared field {dotted}")
            value = value[component]
        if value is not None:
            raise SpecificationError(f"{label}: unresolved field {dotted} must be null")


def validate() -> dict[str, int]:
    atomic = _load(ATOMIC)
    backlog = _load(BACKLOG)
    material = _load(MATERIAL)
    tasks = _load(TASKS)
    protocol = _load(PROTOCOL)
    status = _load(STATUS)
    content = _load(CONTENT)
    for name, document in (
        (MATERIAL.name, material),
        (TASKS.name, tasks),
        (PROTOCOL.name, protocol),
        (STATUS.name, status),
    ):
        _require_blocked_identity(document, name)

    atoms = atomic.get("atoms")
    if not isinstance(atoms, list) or len(atoms) != 25:
        raise SpecificationError("the canonical atomic map must contain exactly 25 atoms")
    atom_ids = [row.get("atom_id") for row in atoms]
    if len(set(atom_ids)) != 25 or not all(isinstance(value, str) and value for value in atom_ids):
        raise SpecificationError("atomic IDs must be 25 unique non-empty strings")
    atomic_binding = material.get("atomic_map", {})
    if atomic_binding.get("sha256") != _sha256(ATOMIC) or atomic_binding.get("atom_count") != 25:
        raise SpecificationError("atomic map binding is stale")

    labels: list[str] = []
    occurrence_count = 0
    for atom in atoms:
        families = atom.get("nearest_work_families")
        if not isinstance(families, list) or not families:
            raise SpecificationError(f"{atom.get('atom_id')}: nearest donor taxonomy is empty")
        occurrence_count += len(families)
        for label in families:
            if label not in labels:
                labels.append(label)
    if occurrence_count != 77 or len(labels) != 75:
        raise SpecificationError("taxonomy census must remain 77 occurrences / 75 labels")
    census = material.get("taxonomy_census", {})
    if census != {"occurrence_count": 77, "distinct_label_count": 75, "executable_donor_count": 0}:
        raise SpecificationError("material registry must report zero executable donors")

    donor_records = material.get("donor_records")
    if not isinstance(donor_records, list) or len(donor_records) != 75:
        raise SpecificationError("material registry needs 75 taxonomy-only donor records")
    by_label = {row.get("taxonomy_label"): row for row in donor_records}
    if set(by_label) != set(labels):
        raise SpecificationError("donor registry taxonomy labels drifted")
    for label in labels:
        row = by_label[label]
        if row.get("taxonomy_id") != _taxonomy_id(label):
            raise SpecificationError(f"{label}: taxonomy identity drifted")
        expected_atoms = [a["atom_id"] for a in atoms if label in a["nearest_work_families"]]
        if row.get("atom_ids") != expected_atoms:
            raise SpecificationError(f"{label}: atom linkage drifted")
        if row.get("status") != "TAXONOMY_ONLY__NOT_AN_EXECUTABLE_DONOR_IDENTITY":
            raise SpecificationError(f"{label}: taxonomy-only status was weakened")
        missing = row.get("immutable_missing_fields")
        if not isinstance(missing, list) or not missing:
            raise SpecificationError(f"{label}: missing-field list is empty")
        _require_null_fields(row, missing, label)

    products = material.get("ideal_product_records")
    if not isinstance(products, list) or len(products) != 25:
        raise SpecificationError("one blocked ideal-product record is required per atom")
    for atom, product in zip(atoms, products, strict=True):
        atom_id = atom["atom_id"]
        if product.get("atom_id") != atom_id:
            raise SpecificationError(f"{atom_id}: ideal-product order drifted")
        expected = [_taxonomy_id(label) for label in atom["nearest_work_families"]]
        if product.get("required_component_taxonomy_ids") != expected:
            raise SpecificationError(f"{atom_id}: ideal-product taxonomy drifted")
        if (
            product.get("status")
            != "BLOCKED_COMPONENT_DONOR_IDENTITIES_AND_COMPOSITION_BYTES_MISSING"
        ):
            raise SpecificationError(f"{atom_id}: ideal product must remain blocked")
        missing = product.get("immutable_missing_fields")
        if not isinstance(missing, list) or not missing:
            raise SpecificationError(f"{atom_id}: ideal product missing-field list is empty")
        _require_null_fields(product, missing, atom_id)

    task_rows = tasks.get("tasks")
    if not isinstance(task_rows, list) or [row.get("atom_id") for row in task_rows] != atom_ids:
        raise SpecificationError("task manifest must preserve all 25 ordered atoms")
    if tasks.get("scientific_unit_count") != 0 or tasks.get("runnable") is not False:
        raise SpecificationError("semantic atom slots must not be represented as scientific inputs")
    partitions = tasks.get("partitions")
    if not isinstance(partitions, list) or [p.get("partition_id") for p in partitions] != [
        "HELD_OUT",
        "COUNTERFACTUAL",
        "PROSPECTIVE",
    ]:
        raise SpecificationError("the three required partition shapes drifted")
    null_slot_count = 0
    for partition in partitions:
        if partition.get("status") != "REQUIRED_UNPOPULATED":
            raise SpecificationError(
                f"{partition.get('partition_id')}: null slots must be unpopulated"
            )
        slots = partition.get("unit_slots")
        if not isinstance(slots, list) or [slot.get("atom_id") for slot in slots] != atom_ids:
            raise SpecificationError(f"{partition.get('partition_id')}: atom slots drifted")
        missing = partition.get("immutable_missing_fields_per_slot")
        for slot in slots:
            _require_null_fields(
                slot, missing, f"{partition.get('partition_id')}:{slot.get('atom_id')}"
            )
            null_slot_count += 1
    if null_slot_count != 75:
        raise SpecificationError("exactly 75 unresolved partition slots are required")

    for section in ("candidate_bundle", "input_bundle", "evaluator"):
        row = protocol.get(section)
        if not isinstance(row, dict):
            raise SpecificationError(f"protocol section {section} is missing")
        _require_null_fields(row, row.get("immutable_missing_fields", []), section)
    matched = protocol.get("matched_contract", {})
    expected_policy = {
        "same_candidate_visible_information": True,
        "same_tool_access": True,
        "donor_first_refusal": True,
        "frozen_before_outcomes": True,
        "outcomes_accessed": False,
        "resource_order": "PARETO_COMPONENTWISE",
        "scalarization": "NONE",
        "price_vector": None,
    }
    for key, value in expected_policy.items():
        if matched.get(key) != value:
            raise SpecificationError(f"matched policy drifted at {key}")
    _require_null_fields(matched, matched.get("immutable_missing_fields", []), "matched_contract")
    if protocol.get("state") != "BLOCKED_SPECIFICATION__MATERIAL_BYTES_AND_STUDY_UNITS_MISSING":
        raise SpecificationError("protocol candidate must remain BLOCKED_SPECIFICATION")
    if (
        protocol.get("runnable_on_lunarc") is not False
        or protocol.get("scheduler_submission") is not None
    ):
        raise SpecificationError("the blocked protocol cannot carry a scheduler submission")

    predecessor = next(
        (job for job in backlog.get("jobs", []) if job.get("job_id") == "DISC-V3-DONOR-01"), None
    )
    if predecessor is None:
        raise SpecificationError("DISC-V3-DONOR-01 predecessor disappeared")
    terminal_rules = protocol.get("terminal_rules", {})
    if terminal_rules.get("source_sha256") != _sha256(BACKLOG):
        raise SpecificationError("terminal source binding is stale")
    if terminal_rules.get("positive") != [predecessor.get("positive_terminal")]:
        raise SpecificationError("positive terminal was retuned")
    negative = predecessor.get("negative_terminals")
    if terminal_rules.get("adverse_or_null") != negative[:-1] or terminal_rules.get(
        "cannot_check"
    ) != [negative[-1]]:
        raise SpecificationError("adverse/null/CANNOT_CHECK routes were retuned")

    if status.get("readiness") != "BLOCKED_SPECIFICATION":
        raise SpecificationError("status must remain BLOCKED_SPECIFICATION")
    if (
        status.get("terminal")
        != "CANNOT_FREEZE_PROTOCOL__MATERIAL_ARTIFACTS_AND_STUDY_UNITS_UNBOUND"
    ):
        raise SpecificationError("status terminal drifted")
    if (
        status.get("runnable_on_lunarc") is not False
        or status.get("scheduler_submission") is not None
    ):
        raise SpecificationError("status cannot authorize scheduling")
    blockers = status.get("remaining_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise SpecificationError("six exact material blocker classes must remain visible")
    if any(not row.get("exact_missing_fields") for row in blockers):
        raise SpecificationError("every blocker must list exact missing fields")

    files = content.get("files")
    if not isinstance(files, dict) or not files:
        raise SpecificationError("content manifest is empty")
    for relative, record in files.items():
        path = ROOT / relative
        if record.get("sha256") != _sha256(path) or record.get("bytes") != path.stat().st_size:
            raise SpecificationError(f"content binding drift: {relative}")
    if (
        content.get("execution_authorized") is not False
        or content.get("runnable_on_lunarc") is not False
    ):
        raise SpecificationError("content manifest cannot authorize execution")

    return {
        "atoms": 25,
        "taxonomy_occurrences": 77,
        "taxonomy_labels": 75,
        "executable_donors": 0,
        "ideal_products_blocked": 25,
        "partition_slots_unpopulated": 75,
        "remaining_blocker_classes": 6,
    }


def main() -> int:
    counts = validate()
    fields = " ".join(f"{key}={value}" for key, value in counts.items())
    print(f"V3_DONOR_ENVELOPE_01_BLOCKED_SPECIFICATION_VALID {fields}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
