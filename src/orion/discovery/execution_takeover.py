"""Fail-closed execution identity and readiness checks for ORION Discovery V3.

This module is an engineering control plane.  It does not infer scientific
equivalence from similar job names and it cannot grant paper or novelty
authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shlex
from typing import Any, Mapping


SCHEMA = "orion.discovery.v3.execution-takeover-manifest.v1"
BLOCKED = "BLOCKED_SPECIFICATION"
READY = "READY_TO_FREEZE"
LATER_STATES = {"FROZEN", "SUBMITTED", "TERMINAL", "VALIDATED"}
ALIAS_RELATIONSHIPS = {"EXACT_ALIAS", "POTENTIAL_PREDECESSOR_NOT_ALIAS"}
PROTOCOL_SCHEMA = "orion.discovery.v3.execution-protocol.v1"
SCIENTIFIC_STUDY = "SCIENTIFIC_STUDY"
_OUTCOME_KEYS = {
    "metrics",
    "observed_results",
    "outcomes",
    "raw_outputs",
    "result",
    "results",
    "terminal",
    "winner",
}
_SAFE_SLURM_TOKEN = re.compile(r"^[A-Za-z0-9_.-]+$")


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


def _reject_outcomes(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key)
            if name in _OUTCOME_KEYS:
                raise ManifestError(f"outcome-bearing key is forbidden before freeze: {'.'.join((*path, name))}")
            if name == "outcomes_accessed" and child is not False:
                raise ManifestError("outcomes_accessed must be exactly false before freeze")
            _reject_outcomes(child, (*path, name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_outcomes(child, (*path, str(index)))


def _canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ManifestError(f"protocol must be canonical JSON: {exc}") from exc


def _require_sha256(mapping: Mapping[str, Any], name: str, context: str) -> str:
    value = mapping.get(name)
    _require(
        isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value)),
        f"{context}.{name} must be a full lowercase SHA-256 identity",
    )
    return value


def _validate_scientific_protocol(protocol: Mapping[str, Any]) -> None:
    inputs = protocol["inputs"]
    _require(isinstance(inputs, Mapping), "scientific protocol inputs are required")
    for name in (
        "source_archive_sha256",
        "input_bundle_sha256",
        "task_manifest_sha256",
        "candidate_artifact_sha256",
        "evaluator_sha256",
        "donor_registry_sha256",
    ):
        _require_sha256(inputs, name, "protocol inputs")

    task_ids = inputs.get("task_ids")
    _require(
        isinstance(task_ids, list)
        and bool(task_ids)
        and all(isinstance(value, str) and value for value in task_ids),
        "protocol inputs.task_ids must be a non-empty identity list",
    )
    _require(len(set(task_ids)) == len(task_ids), "protocol inputs.task_ids must be unique")

    donor_family = inputs.get("donor_family")
    _require(
        isinstance(donor_family, list) and bool(donor_family),
        "protocol inputs.donor_family must contain executable donor records",
    )
    donor_ids: list[str] = []
    donor_fields = {"donor_id", "artifact_sha256", "interface_contract_sha256"}
    for donor in donor_family:
        _require(
            isinstance(donor, Mapping) and donor_fields <= set(donor),
            "protocol inputs.donor_family must contain content-bound donor records",
        )
        donor_id = donor.get("donor_id")
        _require(
            isinstance(donor_id, str) and donor_id,
            "protocol inputs.donor_family donor_id is required",
        )
        donor_ids.append(donor_id)
        _require_sha256(donor, "artifact_sha256", f"protocol inputs.donor_family[{donor_id}]")
        _require_sha256(
            donor,
            "interface_contract_sha256",
            f"protocol inputs.donor_family[{donor_id}]",
        )
    _require(len(set(donor_ids)) == len(donor_ids), "protocol inputs.donor_family IDs must be unique")

    ideal_product = inputs.get("ideal_donor_product")
    _require(
        isinstance(ideal_product, Mapping),
        "protocol inputs.ideal_donor_product must be an executable product record",
    )
    product_id = ideal_product.get("product_id")
    _require(
        isinstance(product_id, str) and product_id,
        "protocol inputs.ideal_donor_product product_id is required",
    )
    component_ids = ideal_product.get("component_donor_ids")
    _require(
        isinstance(component_ids, list)
        and len(component_ids) == len(donor_ids)
        and len(set(component_ids)) == len(component_ids)
        and set(component_ids) == set(donor_ids),
        "protocol inputs.ideal_donor_product component_donor_ids must cover the exact donor family",
    )
    _require_sha256(
        ideal_product,
        "composition_runner_sha256",
        "protocol inputs.ideal_donor_product",
    )
    _require_sha256(
        ideal_product,
        "interface_contract_sha256",
        "protocol inputs.ideal_donor_product",
    )

    matched = protocol["matched_contract"]
    for name in (
        "information_contract_sha256",
        "tool_contract_sha256",
        "resource_contract_sha256",
    ):
        _require_sha256(matched, name, "protocol matched_contract")
    for name in (
        "same_candidate_visible_information",
        "same_tool_access",
        "donor_first_refusal",
        "frozen_before_outcomes",
    ):
        _require(
            matched.get(name) is True,
            f"protocol matched_contract.{name} must be exactly true",
        )
    dimensions = matched.get("resource_dimensions")
    _require(
        isinstance(dimensions, list)
        and bool(dimensions)
        and all(isinstance(value, str) and value for value in dimensions),
        "protocol matched_contract.resource_dimensions must be a non-empty identity list",
    )
    _require(
        len(set(dimensions)) == len(dimensions),
        "protocol matched_contract.resource_dimensions must be unique",
    )
    _require(
        matched.get("resource_order") == "PARETO_COMPONENTWISE",
        "protocol matched_contract.resource_order must be PARETO_COMPONENTWISE",
    )
    scalarization = matched.get("scalarization")
    _require(
        scalarization in {"NONE", "FROZEN_PRICE_VECTOR"},
        "protocol matched_contract.scalarization must be NONE or FROZEN_PRICE_VECTOR",
    )
    price_vector = matched.get("price_vector")
    if scalarization == "NONE":
        _require(
            price_vector is None,
            "protocol matched_contract.price_vector must be null when scalarization is NONE",
        )
    else:
        _require(
            isinstance(price_vector, Mapping)
            and set(price_vector) == set(dimensions)
            and all(type(value) in {int, float} and value > 0 for value in price_vector.values()),
            "protocol matched_contract.price_vector must positively price every resource dimension",
        )
        price_vector_sha256 = _require_sha256(
            matched,
            "price_vector_sha256",
            "protocol matched_contract",
        )
        _require(
            price_vector_sha256 == _sha256_text(_canonical_json(price_vector)),
            "protocol matched_contract.price_vector_sha256 mismatch",
        )

    terminals = protocol.get("terminals")
    _require(isinstance(terminals, Mapping), "scientific protocol terminals are required")
    _require(
        isinstance(terminals.get("positive"), str) and bool(terminals["positive"]),
        "scientific protocol terminals.positive is required",
    )
    adverse = terminals.get("adverse")
    _require(
        isinstance(adverse, list)
        and bool(adverse)
        and all(isinstance(value, str) and value for value in adverse),
        "scientific protocol terminals.adverse must be a non-empty identity list",
    )
    _require(len(set(adverse)) == len(adverse), "scientific protocol terminals.adverse must be unique")
    _require(
        isinstance(terminals.get("cannot_check"), str) and bool(terminals["cannot_check"]),
        "scientific protocol terminals.cannot_check is required",
    )


def freeze_protocol(
    protocol: Mapping[str, Any], *, expected_source_git_sha: str | None = None
) -> dict[str, Any]:
    """Return a deterministic content-addressed protocol in the FROZEN state."""

    _require(protocol.get("schema") == PROTOCOL_SCHEMA, "unsupported execution protocol schema")
    job_id = protocol.get("job_id")
    _require(isinstance(job_id, str) and job_id, "protocol job identity is required")
    source_sha = protocol.get("source_git_sha")
    _require(
        isinstance(source_sha, str) and bool(re.fullmatch(r"[0-9a-f]{40}", source_sha)),
        "protocol source Git SHA must be a full lowercase object identity",
    )
    if expected_source_git_sha is not None:
        _require(
            bool(re.fullmatch(r"[0-9a-f]{40}", expected_source_git_sha)),
            "expected source Git SHA must be a full lowercase object identity",
        )
        _require(source_sha == expected_source_git_sha, "stale source Git SHA")
    _require(protocol.get("paper_authority_delta") == "NONE", "execution cannot grant paper authority")
    _require(bool(protocol.get("authority_ceiling")), "protocol authority ceiling is required")
    inputs = protocol.get("inputs")
    _require(isinstance(inputs, Mapping), "protocol inputs are required")
    runner_sha256 = inputs.get("runner_sha256")
    _require(
        isinstance(runner_sha256, str) and bool(re.fullmatch(r"[0-9a-f]{64}", runner_sha256)),
        "protocol inputs.runner_sha256 must be a full lowercase SHA-256 identity",
    )

    resources = protocol.get("resource_vector")
    required_resources = {"nodes", "cpus", "memory_mb", "minutes"}
    _require(
        isinstance(resources, Mapping) and set(resources) == required_resources,
        "resource vector must name nodes, cpus, memory_mb, and minutes",
    )
    _require(
        all(type(resources[name]) is int and resources[name] > 0 for name in required_resources),
        "resource vector values must be positive integers",
    )
    matched = protocol.get("matched_contract")
    _require(isinstance(matched, Mapping), "matched contract is required")
    _require(matched.get("outcomes_accessed") is False, "outcomes_accessed must be exactly false before freeze")

    execution_class = protocol.get("execution_class")
    if job_id.startswith("V3-ENGINEERING-REFERENCE-"):
        _require(
            execution_class in {None, "ENGINEERING_REFERENCE"},
            "engineering protocol has an invalid execution_class",
        )
    else:
        _require(
            execution_class == SCIENTIFIC_STUDY,
            "scientific protocol execution_class must be SCIENTIFIC_STUDY",
        )
        _validate_scientific_protocol(protocol)

    _reject_outcomes(protocol)
    canonical = _canonical_json(protocol)
    frozen = json.loads(canonical)
    frozen["protocol_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    frozen["state"] = "FROZEN"
    return frozen


def validate_frozen_protocol(frozen_protocol: Mapping[str, Any]) -> None:
    _require(frozen_protocol.get("state") == "FROZEN", "protocol is not frozen")
    expected_hash = frozen_protocol.get("protocol_sha256")
    _require(
        isinstance(expected_hash, str) and bool(re.fullmatch(r"[0-9a-f]{64}", expected_hash)),
        "frozen protocol hash is missing",
    )
    original = dict(frozen_protocol)
    original.pop("state", None)
    original.pop("protocol_sha256", None)
    recomputed = freeze_protocol(original)
    _require(
        recomputed["protocol_sha256"] == expected_hash,
        "frozen protocol hash mismatch",
    )


def submission_key(frozen_protocol: Mapping[str, Any]) -> str:
    validate_frozen_protocol(frozen_protocol)
    material = ":".join(
        (
            "orion-slurm-v1",
            str(frozen_protocol.get("job_id", "")),
            str(frozen_protocol.get("source_git_sha", "")),
            str(frozen_protocol.get("protocol_sha256", "")),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def duplicate_scheduler_records(
    key: str, records: list[Mapping[str, Any]]
) -> tuple[Mapping[str, Any], ...]:
    """Return every scheduler record with the same content-bound submission key."""

    _require(bool(re.fullmatch(r"[0-9a-f]{64}", key)), "invalid submission key")
    return tuple(record for record in records if record.get("submission_key") == key)


def _safe_slurm_value(value: str, label: str) -> str:
    _require(bool(_SAFE_SLURM_TOKEN.fullmatch(value)), f"unsafe {label}")
    return value


def _safe_log_path(value: str) -> str:
    _require(value and "\n" not in value and "\r" not in value, "unsafe SLURM log path")
    return value


def render_slurm_script(
    frozen_protocol: Mapping[str, Any],
    *,
    account: str,
    partition: str,
    command: list[str],
    stdout_path: str,
    stderr_path: str,
) -> str:
    """Render a non-interpolating SLURM script bound to a frozen protocol."""

    key = submission_key(frozen_protocol)
    _require(command and all(isinstance(value, str) and value for value in command), "argv command required")
    resources = frozen_protocol["resource_vector"]
    job_name = re.sub(r"[^A-Za-z0-9_-]", "-", str(frozen_protocol["job_id"]).lower())[:48]
    lines = [
        "#!/bin/bash",
        f"#SBATCH -A {_safe_slurm_value(account, 'account')}",
        f"#SBATCH -p {_safe_slurm_value(partition, 'partition')}",
        f"#SBATCH -N {resources['nodes']}",
        f"#SBATCH -n {resources['cpus']}",
        f"#SBATCH --mem={resources['memory_mb']}M",
        f"#SBATCH -t {resources['minutes']}",
        f"#SBATCH -J {job_name}",
        f"#SBATCH -o {_safe_log_path(stdout_path)}",
        f"#SBATCH -e {_safe_log_path(stderr_path)}",
        "set -euo pipefail",
        f"export ORION_SUBMISSION_KEY={key}",
        shlex.join(command),
        "",
    ]
    return "\n".join(lines)


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"invalid JSON result file {path.name}: {exc}") from exc
    _require(isinstance(payload, dict), f"result file {path.name} must contain an object")
    return payload


def _validate_result_receipt(receipt: Mapping[str, Any]) -> None:
    required_text = {
        "job_id",
        "base_git_sha",
        "head_git_sha",
        "ideal_donor_product",
        "held_out_status",
        "counterfactual_status",
        "prospective_status",
        "authority_ceiling",
    }
    for name in required_text:
        _require(isinstance(receipt.get(name), str) and receipt[name], f"RESULT_RECEIPT missing {name}")
    for name in ("base_git_sha", "head_git_sha"):
        _require(
            bool(re.fullmatch(r"[0-9a-f]{40}", receipt[name])),
            f"RESULT_RECEIPT {name} must be a full lowercase Git SHA",
        )
    for name in ("task_count", "inference_unit_count"):
        value = receipt.get(name)
        _require(type(value) is int and value >= 0, f"RESULT_RECEIPT {name} must be non-negative")
    required_lists = {
        "donor_family",
        "matched_contracts",
        "donor_conservativity_violations",
        "false_promotion_violations",
        "resource_violations_or_incomparabilities",
        "strict_frontier_witnesses",
        "minimal_residual_family",
        "known_donor_absorption",
        "nonclaims",
    }
    for name in required_lists:
        _require(isinstance(receipt.get(name), list), f"RESULT_RECEIPT missing list {name}")
    _require(receipt.get("paper_authority_delta") == "NONE", "RESULT_RECEIPT cannot grant paper authority")


def validate_result_bundle(directory: str | Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a complete V3 result bundle and return immutable file identities."""

    root = Path(directory)
    _require(root.is_dir(), "result bundle directory is missing")
    required = contract.get("required_outputs")
    authority_options = contract.get("required_one_of")
    _require(
        isinstance(required, list) and all(isinstance(name, str) and name for name in required),
        "invalid required result file contract",
    )
    _require(
        isinstance(authority_options, list)
        and len(authority_options) == 2
        and all(isinstance(name, str) and name for name in authority_options),
        "invalid authority route contract",
    )

    missing = sorted(name for name in required if not (root / name).is_file())
    _require(not missing, f"missing required result files: {missing}")
    authority_present = [name for name in authority_options if (root / name).is_file()]
    _require(len(authority_present) == 1, "exactly one authority route must be present")

    filenames = [*required, authority_present[0]]
    payloads = {name: _load_json_object(root / name) for name in filenames}
    _validate_result_receipt(payloads["RESULT_RECEIPT.json"])

    files: dict[str, dict[str, Any]] = {}
    for name in filenames:
        raw = (root / name).read_bytes()
        files[name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    return {
        "schema": "orion.discovery.v3.validated-result-bundle.v1",
        "file_count": len(files),
        "files": files,
        "authority_route": authority_present[0],
        "paper_authority_delta": "NONE",
    }
