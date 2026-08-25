"""Fail-closed execution identity and readiness checks for ORION Discovery V3.

This module is an engineering control plane.  It does not infer scientific
equivalence from similar job names and it cannot grant paper or novelty
authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "orion.discovery.v3.execution-takeover-manifest.v1"
BLOCKED = "BLOCKED_SPECIFICATION"
READY = "READY_TO_FREEZE"
LATER_STATES = {"FROZEN", "SUBMITTED", "TERMINAL", "VALIDATED"}
ALIAS_RELATIONSHIPS = {"EXACT_ALIAS", "POTENTIAL_PREDECESSOR_NOT_ALIAS"}


class ManifestError(ValueError):
    """Raised when an execution manifest crosses an identity boundary."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def load_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    _require(isinstance(payload, dict), "manifest root must be an object")
    return payload


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate source, queue, alias, dependency, and readiness boundaries."""

    _require(manifest.get("schema") == SCHEMA, "unsupported takeover manifest schema")
    _require(manifest.get("paper_authority_delta") == "NONE", "execution cannot grant paper authority")

    order = manifest.get("canonical_order")
    jobs = manifest.get("jobs")
    _require(isinstance(order, list) and order, "canonical order must be a non-empty list")
    _require(isinstance(jobs, list) and jobs, "jobs must be a non-empty list")
    _require(all(isinstance(value, str) and value for value in order), "invalid canonical job id")
    _require(len(set(order)) == len(order), "duplicate canonical job id in order")

    ids = [job.get("job_id") for job in jobs if isinstance(job, Mapping)]
    _require(len(ids) == len(jobs), "every job must be an object")
    _require(len(set(ids)) == len(ids), "duplicate canonical job id")
    _require(ids == order, "job records must follow the frozen canonical order")

    contracts = manifest.get("result_bundle_contracts")
    _require(isinstance(contracts, Mapping) and contracts, "result bundle contract is required")

    seen: set[str] = set()
    allowed_states = {BLOCKED, READY, *LATER_STATES}
    for expected_position, job in enumerate(jobs, start=1):
        job_id = job["job_id"]
        _require(job.get("position") == expected_position, f"{job_id}: position mismatch")

        question = job.get("scientific_question")
        _require(isinstance(question, str) and question, f"{job_id}: scientific question is required")
        _require(
            job.get("scientific_question_sha256") == _sha256_text(question),
            f"{job_id}: scientific question hash mismatch",
        )

        state = job.get("status")
        _require(state in allowed_states, f"{job_id}: invalid execution state")
        _require(job.get("paper_authority_delta") == "NONE", f"{job_id}: paper authority must remain NONE")
        contract_id = job.get("result_bundle_contract_id")
        _require(contract_id in contracts, f"{job_id}: unknown result bundle contract")

        dependencies = job.get("dependencies")
        _require(isinstance(dependencies, list), f"{job_id}: dependencies must be a list")
        _require(len(set(dependencies)) == len(dependencies), f"{job_id}: duplicate dependency")
        _require(set(dependencies) <= seen, f"{job_id}: dependency must precede the job")

        predecessors = job.get("predecessors")
        _require(isinstance(predecessors, list), f"{job_id}: predecessors must be a list")
        predecessor_ids: set[str] = set()
        for predecessor in predecessors:
            _require(isinstance(predecessor, Mapping), f"{job_id}: invalid predecessor record")
            predecessor_id = predecessor.get("job_id")
            _require(
                isinstance(predecessor_id, str) and predecessor_id not in predecessor_ids,
                f"{job_id}: duplicate or invalid predecessor identity",
            )
            predecessor_ids.add(predecessor_id)
            relationship = predecessor.get("relationship")
            _require(relationship in ALIAS_RELATIONSHIPS, f"{job_id}: invalid predecessor relationship")
            predecessor_hash = predecessor.get("scientific_question_sha256")
            _require(
                isinstance(predecessor_hash, str) and len(predecessor_hash) == 64,
                f"{job_id}: predecessor question hash is required",
            )
            if relationship == "EXACT_ALIAS":
                _require(
                    predecessor_hash == job["scientific_question_sha256"],
                    f"{job_id}: exact alias question hash mismatch",
                )

        blockers = job.get("blockers")
        if state == BLOCKED:
            _require(isinstance(blockers, list) and blockers, f"{job_id}: blocked job needs blockers")
            _require(job.get("protocol") is None, f"{job_id}: blocked job cannot have a frozen protocol")
            _require(
                job.get("scheduler_submission") is None,
                f"{job_id}: blocked job cannot have a scheduler submission",
            )
        else:
            _require(not blockers, f"{job_id}: executable job cannot retain blockers")
            _require(job.get("resource_class") != "UNFROZEN", f"{job_id}: resource class is not frozen")
            _require(isinstance(job.get("job_specific_terminals"), Mapping), f"{job_id}: terminals missing")
            _require(isinstance(job.get("protocol"), Mapping), f"{job_id}: protocol missing")

        seen.add(job_id)


def ready_job_ids(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    """Return only dependency-ready jobs; validation always runs first."""

    validate_manifest(manifest)
    states = {job["job_id"]: job["status"] for job in manifest["jobs"]}
    return tuple(
        job["job_id"]
        for job in manifest["jobs"]
        if job["status"] == READY
        and all(states[dependency] == "VALIDATED" for dependency in job["dependencies"])
    )

