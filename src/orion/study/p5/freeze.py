"""Fail-closed freeze utilities for the ORION-P5 hidden-cause study.

The protected suite contains root-cause truth, fresh-task payloads, evaluator
bindings, rubrics, negative variants, and opening nonces. It must remain under
external/protected custody. This module derives two safe-to-share artifacts:

* a candidate packet containing only development-visible information; and
* a commitment manifest binding the protected material without disclosing it.

The commitment is not empirical evidence and cannot promote a P5 result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "orion.p5.protected-hidden-cause-suite.v1"
CANDIDATE_SCHEMA_VERSION = "orion.p5.candidate-hidden-cause-packet.v1"
COMMITMENT_SCHEMA_VERSION = "orion.p5.protected-suite-commitment.v1"

ROOT_CAUSES = frozenset(
    {
        "RETRIEVAL_MISS",
        "ROUTING_PLANNING_MISS",
        "IMPLEMENTATION_BUG",
        "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
        "EVALUATOR_METRIC_BUG",
        "REPRESENTATION_GAP",
        "MEASUREMENT_SPECIFICATION_GAP",
        "METHOD_BASIS_GAP",
    }
)

ALLOWED_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT", "DATA", "TOOL"})
INDEPENDENT_CHANGED_AXES = frozenset({"TASK", "DOMAIN", "MODEL", "ENVIRONMENT"})
_HEX = frozenset("0123456789abcdef")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return a deterministic SHA-256 digest for JSON-compatible ``value``."""

    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(value: Any, field: str, *, min_items: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < min_items:
        raise ValueError(f"{field} must contain at least {min_items} item(s)")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_nonempty_string(item, f"{field}[{index}]"))
    if len(result) != len(set(result)):
        raise ValueError(f"{field} contains duplicate values")
    return result


def _require_sha256(value: Any, field: str) -> str:
    digest = _require_nonempty_string(value, field).lower()
    if len(digest) != 64 or any(char not in _HEX for char in digest):
        raise ValueError(f"{field} must be a 64-character lowercase SHA-256 hex digest")
    return digest


def _require_nonce(value: Any, field: str) -> str:
    nonce = _require_sha256(value, field)
    if nonce == "0" * 64:
        raise ValueError(f"{field} must not be the all-zero nonce")
    return nonce


def _protected_case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_cases = suite.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("cases must be a non-empty array")
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw_case in enumerate(raw_cases):
        case = _require_mapping(raw_case, f"cases[{index}]")
        case_id = _require_nonempty_string(case.get("case_id"), f"cases[{index}].case_id")
        if case_id in result:
            raise ValueError(f"duplicate case_id: {case_id}")
        result[case_id] = case
    return result


def validate_protected_suite(raw_suite: Mapping[str, Any]) -> None:
    """Validate a private P5 suite and fail closed on freshness/integrity gaps."""

    suite = _require_mapping(raw_suite, "suite")
    if suite.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    _require_nonempty_string(suite.get("suite_id"), "suite_id")
    if suite.get("created_before_outcome_access") is not True:
        raise ValueError("created_before_outcome_access must be true")
    _require_sha256(suite.get("evaluator_hash"), "evaluator_hash")

    fresh_payloads = _require_mapping(suite.get("fresh_task_payloads"), "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite.get("negative_variant_payloads"), "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    observed_causes: set[str] = set()
    used_nonces: set[str] = set()
    referenced_fresh: set[str] = set()
    referenced_negative: set[str] = set()

    for case_id, case in cases.items():
        prefix = f"case {case_id}"
        _require_nonempty_string(case.get("visible_symptom"), f"{prefix}.visible_symptom")
        _require_mapping(case.get("candidate_visible_context"), f"{prefix}.candidate_visible_context")

        root = _require_nonempty_string(case.get("protected_root_cause"), f"{prefix}.protected_root_cause")
        if root not in ROOT_CAUSES:
            raise ValueError(f"{prefix}.protected_root_cause is not a registered root cause")
        observed_causes.add(root)

        nonce = _require_nonce(case.get("root_cause_nonce"), f"{prefix}.root_cause_nonce")
        if nonce in used_nonces:
            raise ValueError("root_cause_nonce values must be unique across cases")
        used_nonces.add(nonce)

        competing = _require_string_list(
            case.get("competing_cause_set"), f"{prefix}.competing_cause_set", min_items=2
        )
        if root not in competing:
            raise ValueError(f"{prefix}.competing_cause_set must include protected_root_cause")

        motivating = _require_string_list(case.get("motivating_tasks"), f"{prefix}.motivating_tasks")
        replay = _require_string_list(case.get("replay_tasks"), f"{prefix}.replay_tasks")
        allowed = _require_string_list(
            case.get("allowed_change_surface"), f"{prefix}.allowed_change_surface"
        )
        protected = _require_string_list(case.get("protected_surface"), f"{prefix}.protected_surface")
        if set(allowed) & set(protected):
            raise ValueError(f"{prefix} allowed_change_surface overlaps protected_surface")
        _require_nonempty_string(case.get("success_rubric"), f"{prefix}.success_rubric")
        _require_nonempty_string(case.get("harm_rubric"), f"{prefix}.harm_rubric")

        fresh_tasks = case.get("fresh_tasks")
        if not isinstance(fresh_tasks, list) or not fresh_tasks:
            raise ValueError(f"{prefix}.fresh_tasks must be a non-empty array")
        fresh_ids_for_case: set[str] = set()
        for fresh_index, raw_fresh in enumerate(fresh_tasks):
            fresh = _require_mapping(raw_fresh, f"{prefix}.fresh_tasks[{fresh_index}]")
            task_id = _require_nonempty_string(
                fresh.get("task_id"), f"{prefix}.fresh_tasks[{fresh_index}].task_id"
            )
            if task_id in referenced_fresh:
                raise ValueError(f"fresh task_id must be globally unique: {task_id}")
            referenced_fresh.add(task_id)
            fresh_ids_for_case.add(task_id)

            axes = _require_string_list(
                fresh.get("changed_axes"), f"{prefix}.fresh_tasks[{fresh_index}].changed_axes"
            )
            unknown_axes = set(axes) - ALLOWED_CHANGED_AXES
            if unknown_axes:
                raise ValueError(f"{prefix} fresh task {task_id} has unknown changed axes")
            if not (set(axes) & INDEPENDENT_CHANGED_AXES):
                raise ValueError(
                    f"{prefix} fresh task {task_id} must change TASK, DOMAIN, MODEL, or ENVIRONMENT"
                )

            expected_hash = _require_sha256(
                fresh.get("content_hash"), f"{prefix}.fresh_tasks[{fresh_index}].content_hash"
            )
            if task_id not in fresh_payloads:
                raise ValueError(f"missing protected fresh payload: {task_id}")
            actual_hash = sha256_json(fresh_payloads[task_id])
            if actual_hash != expected_hash:
                raise ValueError(f"fresh payload hash mismatch: {task_id}")

        if (set(motivating) | set(replay)) & fresh_ids_for_case:
            raise ValueError(f"{prefix} motivating/replay task ids overlap the fresh set")

        negative_ids = _require_string_list(
            case.get("negative_variant_ids"), f"{prefix}.negative_variant_ids"
        )
        for variant_id in negative_ids:
            if variant_id in referenced_negative:
                raise ValueError(f"negative variant id must be globally unique: {variant_id}")
            referenced_negative.add(variant_id)
            if variant_id not in negative_payloads:
                raise ValueError(f"missing retained negative variant payload: {variant_id}")

    if observed_causes != ROOT_CAUSES:
        missing = sorted(ROOT_CAUSES - observed_causes)
        extra = sorted(observed_causes - ROOT_CAUSES)
        raise ValueError(f"suite must cover all eight root-cause families; missing={missing}, extra={extra}")

    orphan_fresh = set(fresh_payloads) - referenced_fresh
    if orphan_fresh:
        raise ValueError(f"unreferenced fresh payloads are forbidden: {sorted(orphan_fresh)}")
    orphan_negative = set(negative_payloads) - referenced_negative
    if orphan_negative:
        raise ValueError(f"unreferenced negative variants are forbidden: {sorted(orphan_negative)}")


def _root_commitment(root: str, nonce: str) -> str:
    # The nonce stays only in the protected opening material. Hashing one of eight
    # public enum labels without a nonce would be brute-force disclosure.
    return sha256_json({"protected_root_cause": root, "nonce": nonce})


def freeze_protected_suite(raw_suite: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a candidate-safe packet and a protected-suite commitment manifest."""

    validate_protected_suite(raw_suite)
    suite = dict(raw_suite)
    fresh_payloads = _require_mapping(suite["fresh_task_payloads"], "fresh_task_payloads")
    negative_payloads = _require_mapping(
        suite["negative_variant_payloads"], "negative_variant_payloads"
    )
    cases = _protected_case_index(suite)

    candidate_cases: list[dict[str, Any]] = []
    committed_cases: list[dict[str, Any]] = []
    motivating_replay_split: list[dict[str, Any]] = []
    fresh_split: list[dict[str, Any]] = []

    for case_id in sorted(cases):
        case = cases[case_id]
        motivating = list(case["motivating_tasks"])
        replay = list(case["replay_tasks"])
        fresh_tasks = sorted(case["fresh_tasks"], key=lambda item: item["task_id"])
        negative_ids = sorted(case["negative_variant_ids"])

        candidate_cases.append(
            {
                "case_id": case_id,
                "visible_symptom": case["visible_symptom"],
                "candidate_visible_context": case["candidate_visible_context"],
                "motivating_tasks": motivating,
                "replay_tasks": replay,
                "allowed_change_surface": list(case["allowed_change_surface"]),
            }
        )

        fresh_commitments = [
            {
                "task_id": fresh["task_id"],
                "changed_axes": sorted(fresh["changed_axes"]),
                "content_hash": fresh["content_hash"],
            }
            for fresh in fresh_tasks
        ]
        negative_commitments = [
            {"variant_id": variant_id, "content_hash": sha256_json(negative_payloads[variant_id])}
            for variant_id in negative_ids
        ]
        committed_cases.append(
            {
                "case_id": case_id,
                "case_artifact_hash": sha256_json(case),
                "root_cause_commitment": _root_commitment(
                    case["protected_root_cause"], case["root_cause_nonce"]
                ),
                "fresh_tasks": fresh_commitments,
                "negative_variants": negative_commitments,
                "protected_surface_hash": sha256_json(sorted(case["protected_surface"])),
                "success_rubric_hash": sha256_json(case["success_rubric"]),
                "harm_rubric_hash": sha256_json(case["harm_rubric"]),
            }
        )
        motivating_replay_split.append(
            {"case_id": case_id, "motivating_tasks": motivating, "replay_tasks": replay}
        )
        fresh_split.append({"case_id": case_id, "fresh_tasks": fresh_commitments})

    candidate_packet: dict[str, Any] = {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "empirical_authority": "NONE",
        "cases": candidate_cases,
    }
    commitment_manifest: dict[str, Any] = {
        "schema_version": COMMITMENT_SCHEMA_VERSION,
        "suite_id": suite["suite_id"],
        "created_before_outcome_access": True,
        "empirical_authority": "CANNOT_CHECK",
        "full_protected_suite_hash": sha256_json(suite),
        "candidate_packet_hash": sha256_json(candidate_packet),
        "evaluator_hash": suite["evaluator_hash"],
        "motivating_replay_split_hash": sha256_json(motivating_replay_split),
        "fresh_transfer_split_hash": sha256_json(fresh_split),
        "fresh_payload_set_hash": sha256_json(
            {task_id: sha256_json(fresh_payloads[task_id]) for task_id in sorted(fresh_payloads)}
        ),
        "negative_variant_set_hash": sha256_json(
            {
                variant_id: sha256_json(negative_payloads[variant_id])
                for variant_id in sorted(negative_payloads)
            }
        ),
        "root_cause_family_count": len(ROOT_CAUSES),
        "case_count": len(cases),
        "cases": committed_cases,
    }
    return candidate_packet, commitment_manifest


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze a protected ORION-P5 hidden-cause suite")
    parser.add_argument("--protected-suite", type=Path, required=True)
    parser.add_argument("--candidate-packet", type=Path, required=True)
    parser.add_argument("--commitment", type=Path, required=True)
    args = parser.parse_args(argv)

    protected = json.loads(args.protected_suite.read_text(encoding="utf-8"))
    candidate, commitment = freeze_protected_suite(protected)
    _write_json(args.candidate_packet, candidate)
    _write_json(args.commitment, commitment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
