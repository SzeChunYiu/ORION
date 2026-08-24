#!/usr/bin/env python3
"""Outcome-blind protected packet binding and prompt-fit preflight.

The production CLI accepts only an owner-authorized canonical JSON extraction
of the five protected input fields plus controller ID/domain.  It never accepts
or emits gold, rubric, evaluator, candidate, or outcome bodies.  Receipts retain
only hashes, byte counts, token counts supplied by an optional exact-GGUF
ledger, and typed statuses.  No model, tokenizer, provider, evaluator, runner,
scheduler, subprocess, network, CI, manuscript, or PDF route is invoked.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
MODULE_PATH = Path(__file__).resolve()
CONTRACT_PATH = ROOT / "PROTECTED_PROMPT_FIT_CONTRACT_V1.json"
MASK_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json"
)
PROMPT_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
)
DIRECT_CONTRACT_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
)
DIRECT_DRIVER_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py"
)

EXPECTED_UPSTREAM_HASHES = {
    "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json":
        "442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json":
        "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json":
        "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py":
        "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
}
ROW_FIELDS = (
    "instance_id",
    "domain",
    "task_inst",
    "output_fname",
    "domain_knowledge",
    "dataset_folder_tree",
    "dataset_preview",
)
SOURCE_VALUE_FIELDS = (
    "task_inst",
    "output_fname",
    "domain_knowledge",
    "dataset_folder_tree",
    "dataset_preview",
)
MASKED_FIELDS = ("domain_knowledge", "dataset_folder_tree", "dataset_preview")
STATIC_PHASES = ("RR_PHASE0", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1")
PHASE_TO_ARM = {
    "RR_PHASE0": "RR",
    "RR_PHASE1": "RR",
    "OS_PHASE1": "OS",
    "NR_PHASE0": "NR",
    "NR_PHASE1": "NR",
}
ALLOWED_TEMPLATE_MARKERS_BY_PHASE = {
    "RR_PHASE0": ("{{ATTEMPT_ORDINAL}}", "{{MASKED_PACKET_JSON}}"),
    "RR_PHASE1": (
        "{{ATTEMPT_ORDINAL}}",
        "{{PHASE0_STATE_JSON}}",
        "{{PHASE0_STATE_SHA256}}",
        "{{RECOVERED_PACKET_JSON}}",
    ),
    "OS_PHASE1": ("{{ATTEMPT_ORDINAL}}", "{{RECOVERED_PACKET_JSON}}"),
    "NR_PHASE0": ("{{ATTEMPT_ORDINAL}}", "{{MASKED_PACKET_JSON}}"),
    "NR_PHASE1": ("{{ATTEMPT_ORDINAL}}", "{{RECOVERED_PACKET_JSON}}"),
}
TEMPLATE_MARKER_POLICY = {
    "validation_scope": "FROZEN_TEMPLATE_UTF8_BYTES_BEFORE_SUBSTITUTION",
    "allowed_markers_by_phase": {
        phase_id: list(markers)
        for phase_id, markers in ALLOWED_TEMPLATE_MARKERS_BY_PHASE.items()
    },
    "marker_multiplicity": "EACH_ALLOWED_MARKER_EXACTLY_ONCE",
    "unknown_template_markers": "FORBIDDEN",
    "substitution": "SINGLE_PASS_TEMPLATE_SEGMENT_INSERTION",
    "injected_json_double_braces": "DATA_NOT_TEMPLATE_SYNTAX",
}
RENDERER_COLLISION_REPAIR_BOUNDARY = {
    "reported_pre_receipt_status": "FAIL_BEFORE_RECEIPT",
    "reported_probe_counts": {"total": 1224, "pass": 1200, "fail": 24},
    "reported_affected_instance_ids": ["4", "10", "88", "89"],
    "reported_failures_by_phase": {"OS_PHASE1": 12, "NR_PHASE1": 12},
    "reported_failure_cause": "ALL_AND_ONLY_RECOVERED_PACKET_LITERAL_DOUBLE_OPEN_BRACE_COLLISIONS",
    "adverse_result_packet": "PRESERVED_UNCHANGED_IN_SEPARATE_SOURCE_LANE",
    "repair_validation": "SYNTHETIC_ONLY",
    "production_rerun_required": True,
}
SEED_SCHEDULE = {"1": 101, "2": 202, "3": 303}
PHASE_OUTPUT_CAPS = {
    "RR_PHASE0": 1024,
    "RR_PHASE1": 7168,
    "OS_PHASE1": 8192,
    "NR_PHASE0": 1024,
    "NR_PHASE1": 7168,
}
CONTEXT_WINDOW_TOKENS = 32768
MISSING_LEDGER_STATUS = "CANNOT_CHECK_EXACT_GGUF_TOKEN_LEDGER_NOT_SUPPLIED"
CLAIM_BOUNDARY = {
    "production_admissibility": "CANNOT_CHECK",
    "semantic_choice_sensitivity": "NOT_ESTABLISHED",
    "billed_cost_usd": None,
    "billed_cost_status": "CANNOT_CHECK",
    "official_tasks_executed": 0,
    "official_outcomes_opened": 0,
    "scientific_authority_delta": "NONE",
}
FROZEN_TOKENIZER_BINDING = {
    "model_repository": "unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF",
    "model_revision": "b17cb02dd882d5b6ab62fc777ad2995f19668350",
    "model_filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    "model_bytes": 18556689568,
    "model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
    "inference_tokenizer_binding": "GGUF_BYTES",
    "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
    "llama_cpp_version": "b10434",
    "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
}
LIVE_MEASUREMENT_METHOD = "HELD_FILE_DESCRIPTOR_FSTAT_AND_FULL_SHA256"
LIVE_STAGING_INDEPENDENCE = {
    "completed_before_preflight": True,
    "measurement_method": "FULL_FILE_SHA256_AND_BYTE_COUNT",
    "verifier_role": "INDEPENDENT_STAGING_PROCESS",
}


class ContractError(ValueError):
    """An input cannot satisfy the frozen protected preflight contract."""


class DuplicateJsonMemberError(ValueError):
    """Strict JSON repeated a member name."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return sha256_bytes(candidate.read_bytes())
    except OSError as exc:
        raise ContractError(f"required file is unreadable: {candidate}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractError("value is not strict canonical-JSON serializable") from exc


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonMemberError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> Any:
    raise ValueError(f"non-finite JSON value is forbidden: {value}")


def strict_json_object_from_bytes(payload: bytes, label: str) -> dict[str, Any]:
    if not isinstance(payload, bytes):
        raise ContractError(f"{label} must be strict JSON bytes")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=_reject_nonfinite,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateJsonMemberError,
        ValueError,
    ) as exc:
        raise ContractError(f"{label} must be one strict raw JSON object") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be one strict raw JSON object")
    return value


def strict_json_object_from_file(path: Path | str, label: str) -> dict[str, Any]:
    candidate = Path(path)
    try:
        payload = candidate.read_bytes()
    except OSError as exc:
        raise ContractError(f"{label} is unreadable: {candidate}") from exc
    return strict_json_object_from_bytes(payload, label)


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _exact_fields(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise ContractError(
            f"{label} mismatch: missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )


def _sha256_text(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ContractError(f"{label} must be one lowercase SHA-256")
    return value


def _contract_semantics(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != "orion.p1.scienceagentbench.protected-prompt-fit-preflight.v1":
        raise ContractError("protected prompt-fit contract schema mismatch")
    if contract.get("claim_boundary") != CLAIM_BOUNDARY:
        raise ContractError("protected prompt-fit claim boundary mismatch")
    if contract.get("production_execution_authority") is not False:
        raise ContractError("protected prompt-fit contract cannot grant execution authority")
    if contract.get("official_outcomes_opened") != 0:
        raise ContractError("protected prompt-fit contract outcomes boundary mismatch")
    if contract.get("renderer_collision_repair_boundary") != RENDERER_COLLISION_REPAIR_BOUNDARY:
        raise ContractError("renderer collision repair boundary mismatch")
    prompt_matrix = _mapping(contract.get("prompt_matrix"), "prompt matrix")
    if prompt_matrix.get("context_window_tokens") != CONTEXT_WINDOW_TOKENS:
        raise ContractError("prompt matrix context window mismatch")
    if prompt_matrix.get("seed_schedule") != SEED_SCHEDULE:
        raise ContractError("prompt matrix seed schedule mismatch")
    if prompt_matrix.get("phase_output_caps") != PHASE_OUTPUT_CAPS:
        raise ContractError("prompt matrix phase output caps mismatch")
    if prompt_matrix.get("state_independent_phases_in_order") != list(STATIC_PHASES):
        raise ContractError("prompt matrix state-independent phase order mismatch")
    if prompt_matrix.get("state_independent_records_for_102_tasks") != 1224:
        raise ContractError("prompt matrix static record count mismatch")
    if prompt_matrix.get("dynamic_rr_phase1_records_for_102_tasks") != 306:
        raise ContractError("prompt matrix dynamic record count mismatch")
    if prompt_matrix.get("template_marker_policy") != TEMPLATE_MARKER_POLICY:
        raise ContractError("prompt matrix template marker policy mismatch")
    token_policy = _mapping(contract.get("token_measurement_policy"), "token policy")
    if token_policy.get("substitute_tokenizer_allowed") is not False:
        raise ContractError("substitute tokenizer must remain forbidden")
    if token_policy.get("missing_ledger_status") != MISSING_LEDGER_STATUS:
        raise ContractError("missing token-ledger status mismatch")
    if contract.get("tokenizer_binding") != FROZEN_TOKENIZER_BINDING:
        raise ContractError("frozen tokenizer binding mismatch")
    live_policy = _mapping(contract.get("live_gguf_staging_policy"), "live GGUF staging policy")
    if live_policy.get("production_required") is not True:
        raise ContractError("live GGUF staging must be required in production")
    if live_policy.get("independent_verification") != LIVE_STAGING_INDEPENDENCE:
        raise ContractError("live GGUF independent staging policy mismatch")
    if live_policy.get("preflight_live_measurement") != LIVE_MEASUREMENT_METHOD:
        raise ContractError("live GGUF descriptor measurement policy mismatch")
    if live_policy.get("accept_receipt_without_live_gguf_remeasurement") is not False:
        raise ContractError("live GGUF remeasurement cannot be substituted by a receipt")
    packet_contract = _mapping(contract.get("packet_contract"), "packet contract")
    if packet_contract.get("masked_packet_fields") != list(ROW_FIELDS):
        raise ContractError("masked packet field order mismatch")
    if packet_contract.get("recovered_packet_fields") != list(ROW_FIELDS):
        raise ContractError("recovered packet field order mismatch")


def validate_live_staging_binding(
    *,
    staging_receipt: Mapping[str, Any],
    staging_receipt_bytes: int,
    staging_receipt_sha256: str,
    live_model_measurement: Mapping[str, Any],
) -> dict[str, Any]:
    """Require an independent receipt and a matching live descriptor rehash."""

    receipt = dict(_mapping(staging_receipt, "live GGUF staging receipt"))
    _exact_fields(
        receipt,
        {
            "schema_version",
            "authority",
            "model_binding",
            "independent_verification",
            "live_measurement",
            "source_receipt_sha256",
            "official_tasks_opened",
            "official_outcomes_opened",
            "scientific_authority_delta",
        },
        "live GGUF staging receipt fields",
    )
    if receipt.get("schema_version") != "orion.p1.scienceagentbench.live-gguf-staging-receipt.v1":
        raise ContractError("live GGUF staging receipt schema mismatch")
    if receipt.get("authority") != "INDEPENDENT_LIVE_GGUF_STAGING_MEASUREMENT__NO_TASK_OR_OUTCOME_AUTHORITY":
        raise ContractError("live GGUF staging receipt authority mismatch")
    if receipt.get("model_binding") != FROZEN_TOKENIZER_BINDING:
        raise ContractError("live GGUF staging receipt model binding mismatch")
    if receipt.get("independent_verification") != LIVE_STAGING_INDEPENDENCE:
        raise ContractError("live GGUF staging receipt independent verification mismatch")
    if receipt.get("official_tasks_opened") != 0 or receipt.get("official_outcomes_opened") != 0:
        raise ContractError("live GGUF staging receipt task/outcome boundary mismatch")
    if receipt.get("scientific_authority_delta") != "NONE":
        raise ContractError("live GGUF staging receipt scientific authority mismatch")
    if (
        isinstance(staging_receipt_bytes, bool)
        or not isinstance(staging_receipt_bytes, int)
        or staging_receipt_bytes <= 0
    ):
        raise ContractError("live GGUF staging receipt byte count must be positive")
    _sha256_text(staging_receipt_sha256, "live GGUF staging receipt SHA-256")
    canonical_receipt = canonical_json_bytes(receipt) + b"\n"
    if (
        staging_receipt_bytes != len(canonical_receipt)
        or staging_receipt_sha256 != sha256_bytes(canonical_receipt)
    ):
        raise ContractError("live GGUF staging receipt byte/hash binding mismatch")

    measured = dict(_mapping(live_model_measurement, "live GGUF descriptor measurement"))
    _exact_fields(
        measured,
        {"model_filename", "live_model_bytes", "live_model_sha256", "measurement_method"},
        "live GGUF descriptor measurement fields",
    )
    expected_measurement = {
        "model_filename": FROZEN_TOKENIZER_BINDING["model_filename"],
        "live_model_bytes": FROZEN_TOKENIZER_BINDING["model_bytes"],
        "live_model_sha256": FROZEN_TOKENIZER_BINDING["model_sha256"],
        "measurement_method": LIVE_MEASUREMENT_METHOD,
    }
    if measured != expected_measurement:
        raise ContractError("live GGUF descriptor measurement does not match frozen size/SHA")
    if receipt.get("live_measurement") != measured:
        raise ContractError("staging receipt live measurement differs from descriptor measurement")
    source_receipt_sha256 = receipt.get("source_receipt_sha256")
    if source_receipt_sha256 is not None:
        _sha256_text(source_receipt_sha256, "external staging source receipt SHA-256")
    return {
        "status": "PASS_INDEPENDENT_RECEIPT_AND_LIVE_GGUF_MATCH",
        "staging_receipt_bytes": staging_receipt_bytes,
        "staging_receipt_sha256": staging_receipt_sha256,
        "source_receipt_sha256": source_receipt_sha256,
        "live_model_bytes": measured["live_model_bytes"],
        "live_model_sha256": measured["live_model_sha256"],
        "live_measurement_method": measured["measurement_method"],
        "source_receipt_substituted_for_live_measurement": False,
    }


def validate_production_bindings(
    contract: Mapping[str, Any],
    mask_manifest: Mapping[str, Any],
    prompt_bundle: Mapping[str, Any],
    verified_upstream_sha256s: Mapping[str, str] | None = None,
) -> None:
    """Bind exact merged upstream files and the on-disk preflight contract."""

    candidate = dict(_mapping(contract, "protected prompt-fit contract"))
    if verified_upstream_sha256s is None:
        on_disk_contract = strict_json_object_from_file(
            CONTRACT_PATH, "on-disk preflight contract"
        )
        if canonical_json_bytes(candidate) != canonical_json_bytes(on_disk_contract):
            raise ContractError("contract differs from the on-disk frozen contract")
    _contract_semantics(candidate)
    entries = candidate.get("upstream_bindings")
    if not isinstance(entries, list):
        raise ContractError("upstream bindings must be a list")
    declared: dict[str, str] = {}
    for entry in entries:
        bound = _mapping(entry, "upstream binding")
        _exact_fields(bound, {"path", "sha256"}, "upstream binding fields")
        path = bound.get("path")
        digest = bound.get("sha256")
        if not isinstance(path, str):
            raise ContractError("upstream binding path must be text")
        _sha256_text(digest, "upstream binding SHA-256")
        if path in declared:
            raise ContractError("duplicate upstream binding path")
        declared[path] = digest
    if declared != EXPECTED_UPSTREAM_HASHES:
        raise ContractError("upstream binding set mismatch")
    if verified_upstream_sha256s is None:
        observed_hashes = {
            relative: sha256_file(REPO_ROOT / relative) for relative in declared
        }
    else:
        observed_hashes = dict(
            _mapping(verified_upstream_sha256s, "held upstream SHA-256 bindings")
        )
        if set(observed_hashes) != set(declared):
            raise ContractError("held upstream SHA-256 binding set mismatch")
    for relative, expected in declared.items():
        observed = observed_hashes[relative]
        if observed != expected:
            raise ContractError(
                f"upstream SHA-256 drift: path={relative} expected={expected} observed={observed}"
            )
    if verified_upstream_sha256s is None:
        on_disk_mask = strict_json_object_from_file(MASK_PATH, "on-disk mask manifest")
        if canonical_json_bytes(mask_manifest) != canonical_json_bytes(on_disk_mask):
            raise ContractError("production mask manifest differs from exact bound artifact")
        on_disk_prompt = strict_json_object_from_file(PROMPT_PATH, "on-disk prompt bundle")
        if canonical_json_bytes(prompt_bundle) != canonical_json_bytes(on_disk_prompt):
            raise ContractError("production prompt bundle differs from exact bound artifact")
    if mask_manifest.get("schema_version") != "orion.p1.scienceagentbench.mask-manifest.v1":
        raise ContractError("production mask manifest schema mismatch")
    if mask_manifest.get("outcomes_opened") is not False:
        raise ContractError("production mask manifest outcomes boundary mismatch")
    records = mask_manifest.get("records")
    if not isinstance(records, list) or len(records) != 102:
        raise ContractError("production mask manifest must contain exactly 102 tasks")
    if [record.get("instance_id") for record in records if isinstance(record, dict)] != [
        str(index) for index in range(1, 103)
    ]:
        raise ContractError("production mask manifest task IDs or order mismatch")
    _validate_prompt_bundle(prompt_bundle)


def _validate_prompt_bundle(prompt_bundle: Mapping[str, Any]) -> None:
    if prompt_bundle.get("schema_version") != "orion.p1.scienceagentbench.direct-route-prompt-bundle.v1":
        raise ContractError("direct-route prompt bundle schema mismatch")
    render = _mapping(prompt_bundle.get("render_contract"), "prompt render contract")
    if render.get("encoding") != "UTF-8" or render.get("line_endings") != "LF":
        raise ContractError("prompt render encoding or line-ending mismatch")
    if render.get("terminal_newline") is not True:
        raise ContractError("prompt render terminal newline mismatch")
    if render.get("inserted_json") != "json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)":
        raise ContractError("prompt canonical JSON insertion rule mismatch")
    templates = _mapping(prompt_bundle.get("templates"), "prompt templates")
    if tuple(templates) != (
        "RR_PHASE0",
        "RR_PHASE1",
        "OS_PHASE1",
        "NR_PHASE0",
        "NR_PHASE1",
    ):
        raise ContractError("direct-route prompt template order mismatch")
    for phase_id in ALLOWED_TEMPLATE_MARKERS_BY_PHASE:
        template = _mapping(templates.get(phase_id), f"prompt template {phase_id}")
        text = template.get("text")
        markers = template.get("markers")
        if not isinstance(text, str) or not isinstance(markers, list):
            raise ContractError(f"prompt template {phase_id} text or markers invalid")
        _validate_template_marker_structure(phase_id, text, markers)


def _manifest_record_binding(record: Mapping[str, Any]) -> str:
    return canonical_hash(
        {
            "instance_id": record.get("instance_id"),
            "domain": record.get("domain"),
            "fields": record.get("fields"),
        }
    )


def packetize_bound_row(
    row: Mapping[str, Any], manifest_record: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one source row against its manifest record and build packets."""

    source = dict(_mapping(row, "authorized row"))
    _exact_fields(source, set(ROW_FIELDS), "row fields")
    record = dict(_mapping(manifest_record, "mask manifest record"))
    _exact_fields(
        record,
        {"instance_id", "domain", "license_partition", "fields", "binding_sha256"},
        "mask manifest record fields",
    )
    if not isinstance(source["instance_id"], str) or not source["instance_id"]:
        raise ContractError("row instance_id type must be a nonempty string")
    if not isinstance(source["domain"], str) or not source["domain"]:
        raise ContractError("row domain type must be a nonempty string")
    if source["instance_id"] != record["instance_id"]:
        raise ContractError("row instance_id differs from mask manifest binding")
    if source["domain"] != record["domain"]:
        raise ContractError("row domain differs from mask manifest domain")
    fields = _mapping(record.get("fields"), "mask manifest source fields")
    _exact_fields(fields, set(SOURCE_VALUE_FIELDS), "manifest source fields")
    declared_binding = _sha256_text(
        record.get("binding_sha256"), "manifest record binding SHA-256"
    )
    observed_binding = _manifest_record_binding(record)
    if declared_binding != observed_binding:
        raise ContractError("manifest record binding SHA-256 mismatch")

    for name in SOURCE_VALUE_FIELDS:
        value = source[name]
        if value is not None and not isinstance(value, str):
            raise ContractError(f"row field type mismatch: {name}")
        descriptor = _mapping(fields[name], f"manifest descriptor {name}")
        _exact_fields(
            descriptor,
            {"state", "value_type", "canonical_json_bytes", "canonical_json_sha256"},
            f"manifest descriptor fields {name}",
        )
        expected_state = (
            "VISIBLE_FROM_PHASE_0"
            if name in {"task_inst", "output_fname"}
            else "MASK_THEN_EXACT_RECOVER"
        )
        if descriptor.get("state") != expected_state:
            raise ContractError(f"manifest field state mismatch: {name}")
        expected_type = "null" if value is None else "string"
        if descriptor.get("value_type") != expected_type:
            raise ContractError(f"row field type differs from manifest binding: {name}")
        raw = canonical_json_bytes(value)
        if (
            descriptor.get("canonical_json_bytes") != len(raw)
            or descriptor.get("canonical_json_sha256") != sha256_bytes(raw)
        ):
            raise ContractError(f"row source value differs from manifest binding: {name}")

    masked = {
        "instance_id": source["instance_id"],
        "domain": source["domain"],
        "task_inst": source["task_inst"],
        "output_fname": source["output_fname"],
    }
    for name in MASKED_FIELDS:
        masked[name] = {
            "state": "MASKED_UNTIL_PHASE1",
            "source_value_type": "null" if source[name] is None else "string",
        }
    masked = {name: masked[name] for name in ROW_FIELDS}
    recovered = {name: copy.deepcopy(source[name]) for name in ROW_FIELDS}
    return {
        "manifest_binding_sha256": declared_binding,
        "masked_packet": masked,
        "recovered_packet": recovered,
    }


def _validate_template_marker_structure(
    phase_id: str,
    text: str,
    markers: Sequence[Any],
) -> tuple[str, ...]:
    expected = ALLOWED_TEMPLATE_MARKERS_BY_PHASE.get(phase_id)
    if expected is None:
        raise ContractError(f"prompt template phase is unknown: {phase_id}")
    if any(not isinstance(marker, str) for marker in markers):
        raise ContractError(f"prompt template {phase_id} marker declaration is invalid")
    if len(markers) != len(set(markers)):
        raise ContractError(f"prompt template {phase_id} has duplicate marker declaration")
    if tuple(markers) != expected:
        raise ContractError(f"prompt template {phase_id} marker declaration mismatch")
    try:
        template_bytes = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ContractError(f"prompt template {phase_id} is not UTF-8") from exc
    if not template_bytes.endswith(b"\n"):
        raise ContractError(f"prompt template {phase_id} is missing terminal LF")
    residual = template_bytes
    for marker in expected:
        marker_bytes = marker.encode("ascii")
        count = template_bytes.count(marker_bytes)
        if count == 0:
            raise ContractError(
                f"prompt template {phase_id} is missing required template marker: {marker}"
            )
        if count != 1:
            raise ContractError(
                f"prompt template {phase_id} has duplicate template marker: {marker}"
            )
        residual = residual.replace(marker_bytes, b"", 1)
    if b"{{" in residual or b"}}" in residual:
        raise ContractError(f"prompt template {phase_id} has unknown template marker syntax")
    return expected


def _render_template(
    prompt_bundle: Mapping[str, Any], phase_id: str, replacements: Mapping[str, str]
) -> bytes:
    templates = _mapping(prompt_bundle.get("templates"), "prompt templates")
    template = _mapping(templates.get(phase_id), f"prompt template {phase_id}")
    text = template.get("text")
    markers = template.get("markers")
    if not isinstance(text, str) or not isinstance(markers, list):
        raise ContractError(f"prompt template {phase_id} text or markers invalid")
    expected = _validate_template_marker_structure(phase_id, text, markers)
    if set(expected) != set(replacements):
        raise ContractError(f"prompt template {phase_id} replacement markers mismatch")
    for marker in expected:
        replacement = replacements[marker]
        if not isinstance(replacement, str):
            raise ContractError(f"prompt template {phase_id} replacement must be text")
    segments: list[str] = []
    cursor = 0
    for offset, marker in sorted((text.index(marker), marker) for marker in expected):
        segments.append(text[cursor:offset])
        segments.append(replacements[marker])
        cursor = offset + len(marker)
    segments.append(text[cursor:])
    rendered = "".join(segments)
    try:
        return rendered.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ContractError(f"prompt template {phase_id} is not UTF-8") from exc


def _render_static_prompt(
    prompt_bundle: Mapping[str, Any],
    phase_id: str,
    attempt: int,
    masked_packet: Mapping[str, Any],
    recovered_packet: Mapping[str, Any],
) -> bytes:
    if phase_id not in STATIC_PHASES:
        raise ContractError("static prompt renderer accepts only state-independent phases")
    if isinstance(attempt, bool) or attempt not in (1, 2, 3):
        raise ContractError("attempt must be 1, 2, or 3")
    if phase_id in {"RR_PHASE0", "NR_PHASE0"}:
        replacements = {
            "{{ATTEMPT_ORDINAL}}": str(attempt),
            "{{MASKED_PACKET_JSON}}": canonical_json_bytes(masked_packet).decode("utf-8"),
        }
    else:
        replacements = {
            "{{ATTEMPT_ORDINAL}}": str(attempt),
            "{{RECOVERED_PACKET_JSON}}": canonical_json_bytes(recovered_packet).decode("utf-8"),
        }
    return _render_template(prompt_bundle, phase_id, replacements)


def _byte_binding(value: Any) -> dict[str, Any]:
    payload = canonical_json_bytes(value)
    return {"canonical_json_bytes": len(payload), "canonical_json_sha256": sha256_bytes(payload)}


def _static_prompt_records(
    prompt_bundle: Mapping[str, Any], packets: Mapping[str, Any]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for phase_id in STATIC_PHASES:
        for attempt in (1, 2, 3):
            payload = _render_static_prompt(
                prompt_bundle,
                phase_id,
                attempt,
                packets["masked_packet"],
                packets["recovered_packet"],
            )
            result.append(
                {
                    "arm_id": PHASE_TO_ARM[phase_id],
                    "phase_id": phase_id,
                    "attempt": attempt,
                    "seed": SEED_SCHEDULE[str(attempt)],
                    "packet_kind": (
                        "MASKED_PACKET"
                        if phase_id in {"RR_PHASE0", "NR_PHASE0"}
                        else "RECOVERED_PACKET"
                    ),
                    "prompt_bytes": len(payload),
                    "prompt_sha256": sha256_bytes(payload),
                    "phase_output_cap": PHASE_OUTPUT_CAPS[phase_id],
                    "context_window_tokens": CONTEXT_WINDOW_TOKENS,
                    "prompt_tokens": None,
                    "fit_status": MISSING_LEDGER_STATUS,
                }
            )
    return result


def _dynamic_rr_phase1_records() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for attempt in (1, 2, 3):
        result.append(
            {
                "arm_id": "RR",
                "phase_id": "RR_PHASE1",
                "attempt": attempt,
                "seed": SEED_SCHEDULE[str(attempt)],
                "packet_kind": "RECOVERED_PACKET_PLUS_DYNAMIC_RR_PHASE0_STATE",
                "prompt_bytes": None,
                "prompt_sha256": None,
                "phase_output_cap": PHASE_OUTPUT_CAPS["RR_PHASE1"],
                "context_window_tokens": CONTEXT_WINDOW_TOKENS,
                "prompt_tokens": None,
                "fit_status": "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
            }
        )
    return result


def _validate_source_metadata(
    row_source: Mapping[str, Any],
    mask_manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    production: bool,
) -> list[Mapping[str, Any]]:
    source_contract = _mapping(
        contract.get("authorized_row_source_contract"), "authorized row source contract"
    )
    _exact_fields(
        row_source,
        set(source_contract.get("top_level_fields", [])),
        "row source fields",
    )
    if row_source.get("schema_version") != source_contract.get("schema_version"):
        raise ContractError("authorized row source schema mismatch")
    if production:
        if row_source.get("authority") != source_contract.get("production_authority"):
            raise ContractError("production row source authority mismatch")
    elif row_source.get("authority") != "SYNTHETIC_NONBENCHMARK_VALIDATION_ONLY":
        raise ContractError("synthetic row source authority mismatch")
    source = _mapping(row_source.get("source"), "row source provenance")
    _exact_fields(
        source,
        set(source_contract.get("source_fields", [])),
        "row source provenance fields",
    )
    if source.get("official_outcomes_opened") is not False:
        raise ContractError("row source outcomes opening is forbidden")
    if source.get("extraction_mode") != "STRICT_JSON_AUTHORIZED_EXTRACTION":
        raise ContractError("row source extraction mode mismatch")
    manifest_source = _mapping(mask_manifest.get("source"), "mask manifest source")
    for name in ("dataset", "revision", "split", "verified_parquet_sha256"):
        if source.get(name) != manifest_source.get(name):
            raise ContractError(f"row source provenance differs from mask manifest: {name}")
    if production:
        frozen_source = _mapping(contract.get("production_source_binding"), "production source binding")
        for name in ("dataset", "revision", "split", "verified_parquet_sha256"):
            if source.get(name) != frozen_source.get(name):
                raise ContractError(f"production row source binding mismatch: {name}")
    rows = row_source.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ContractError("row source rows must be a nonempty list")
    return rows


def _validate_manifest_records(
    mask_manifest: Mapping[str, Any], *, production: bool
) -> list[Mapping[str, Any]]:
    if mask_manifest.get("schema_version") != "orion.p1.scienceagentbench.mask-manifest.v1":
        raise ContractError("mask manifest schema mismatch")
    if mask_manifest.get("outcomes_opened") is not False:
        raise ContractError("mask manifest outcomes boundary mismatch")
    if mask_manifest.get("scientific_authority_delta") != "NONE":
        raise ContractError("mask manifest scientific authority boundary mismatch")
    records = mask_manifest.get("records")
    if not isinstance(records, list) or not records:
        raise ContractError("mask manifest records must be a nonempty list")
    if any(not isinstance(record, dict) for record in records):
        raise ContractError("mask manifest records must be objects")
    ids = [record.get("instance_id") for record in records]
    if any(not isinstance(instance_id, str) or not instance_id for instance_id in ids):
        raise ContractError("mask manifest instance_id must be a nonempty string")
    if len(set(ids)) != len(ids):
        raise ContractError("duplicate task ID in mask manifest")
    if production and ids != [str(index) for index in range(1, 103)]:
        raise ContractError("production mask manifest must contain task IDs 1 through 102 in order")
    return records


def _source_bindings(
    *,
    row_source_bytes: int,
    row_source_sha256: str,
    mask_manifest_sha256: str,
    prompt_bundle_sha256: str,
    direct_route_contract_sha256: str,
    verified_parquet_sha256: str,
    live_staging_receipt_sha256: str | None,
    live_model_bytes: int | None,
    live_model_sha256: str | None,
) -> dict[str, Any]:
    return {
        "row_source_bytes": row_source_bytes,
        "row_source_sha256": row_source_sha256,
        "mask_manifest_sha256": mask_manifest_sha256,
        "prompt_bundle_sha256": prompt_bundle_sha256,
        "direct_route_contract_sha256": direct_route_contract_sha256,
        "verified_parquet_sha256": verified_parquet_sha256,
        "live_staging_receipt_sha256": live_staging_receipt_sha256,
        "live_model_bytes": live_model_bytes,
        "live_model_sha256": live_model_sha256,
    }


def _apply_token_ledger(
    task_receipts: list[dict[str, Any]],
    token_ledger: Mapping[str, Any],
    contract: Mapping[str, Any],
    source_bindings: Mapping[str, Any],
) -> dict[str, Any]:
    ledger = dict(_mapping(token_ledger, "exact GGUF token ledger"))
    _exact_fields(
        ledger,
        {
            "schema_version",
            "authority",
            "tokenizer_binding",
            "source_bindings",
            "records",
            "official_outcomes_opened",
            "scientific_authority_delta",
        },
        "token ledger fields",
    )
    if ledger.get("schema_version") != "orion.p1.scienceagentbench.exact-gguf-token-ledger.v1":
        raise ContractError("token ledger schema mismatch")
    policy = _mapping(contract.get("token_measurement_policy"), "token measurement policy")
    if ledger.get("authority") != policy.get("ledger_authority"):
        raise ContractError("token ledger authority mismatch")
    if canonical_json_bytes(ledger.get("tokenizer_binding")) != canonical_json_bytes(
        contract.get("tokenizer_binding")
    ):
        raise ContractError("token ledger tokenizer binding mismatch")
    if canonical_json_bytes(ledger.get("source_bindings")) != canonical_json_bytes(source_bindings):
        raise ContractError("token ledger source bindings mismatch")
    if ledger.get("official_outcomes_opened") != 0:
        raise ContractError("token ledger outcomes boundary mismatch")
    if ledger.get("scientific_authority_delta") != "NONE":
        raise ContractError("token ledger scientific authority boundary mismatch")
    records = ledger.get("records")
    if not isinstance(records, list):
        raise ContractError("token ledger records must be a list")

    expected: dict[tuple[str, str, int], dict[str, Any]] = {}
    for task in task_receipts:
        for prompt in task["state_independent_prompts"]:
            key = (task["instance_id"], prompt["phase_id"], prompt["attempt"])
            expected[key] = prompt
    supplied: dict[tuple[str, str, int], tuple[str, int]] = {}
    for item in records:
        record = _mapping(item, "token ledger record")
        _exact_fields(
            record,
            {"instance_id", "phase_id", "attempt", "prompt_sha256", "prompt_tokens"},
            "token ledger record fields",
        )
        instance_id = record.get("instance_id")
        phase_id = record.get("phase_id")
        attempt = record.get("attempt")
        if not isinstance(instance_id, str) or phase_id not in STATIC_PHASES:
            raise ContractError("token ledger contains unexpected prompt key")
        if isinstance(attempt, bool) or attempt not in (1, 2, 3):
            raise ContractError("token ledger contains unexpected attempt")
        key = (instance_id, phase_id, attempt)
        if key in supplied:
            raise ContractError("duplicate token ledger prompt key")
        if key not in expected:
            raise ContractError("token ledger contains unexpected prompt key")
        digest = _sha256_text(record.get("prompt_sha256"), "token ledger prompt hash")
        if digest != expected[key]["prompt_sha256"]:
            raise ContractError("token ledger prompt hash mismatch")
        tokens = record.get("prompt_tokens")
        if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0:
            raise ContractError("token ledger prompt_tokens must be a nonnegative integer")
        supplied[key] = (digest, tokens)
    missing = set(expected) - set(supplied)
    if missing:
        raise ContractError(f"token ledger completeness failure: missing={len(missing)}")

    all_fit = True
    for task in task_receipts:
        task_fit = True
        for prompt in task["state_independent_prompts"]:
            key = (task["instance_id"], prompt["phase_id"], prompt["attempt"])
            tokens = supplied[key][1]
            prompt["prompt_tokens"] = tokens
            fits = tokens + prompt["phase_output_cap"] <= CONTEXT_WINDOW_TOKENS
            prompt["fit_status"] = (
                "FIT_FROM_BOUND_TOKEN_LEDGER"
                if fits
                else "DOES_NOT_FIT_FROM_BOUND_TOKEN_LEDGER"
            )
            task_fit = task_fit and fits
        task["static_prompt_fit_status"] = (
            "FIT_FROM_BOUND_TOKEN_LEDGER"
            if task_fit
            else "DOES_NOT_FIT_FROM_BOUND_TOKEN_LEDGER"
        )
        task["overall_prompt_fit_status"] = (
            "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED"
            if task_fit
            else "DOES_NOT_FIT_STATIC_PHASE_FROM_BOUND_TOKEN_LEDGER__RR_PHASE1_STILL_CANNOT_CHECK"
        )
        all_fit = all_fit and task_fit
    return {
        "status": "CHECKED_FROM_BOUND_OWNER_SUPPLIED_EXACT_GGUF_LEDGER",
        "ledger_sha256": canonical_hash(ledger),
        "records": len(records),
        "all_state_independent_prompts_fit": all_fit,
        "token_counts_independently_remeasured_here": False,
        "dynamic_rr_phase1_status": "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
    }


def build_preflight_receipt(
    *,
    row_source: Mapping[str, Any],
    row_source_bytes: int,
    row_source_sha256: str,
    mask_manifest: Mapping[str, Any],
    mask_manifest_sha256: str,
    prompt_bundle: Mapping[str, Any],
    prompt_bundle_sha256: str,
    direct_route_contract_sha256: str,
    contract: Mapping[str, Any],
    token_ledger: Mapping[str, Any] | None,
    production: bool,
    live_staging_receipt: Mapping[str, Any] | None = None,
    live_staging_receipt_bytes: int | None = None,
    live_staging_receipt_sha256: str | None = None,
    live_model_measurement: Mapping[str, Any] | None = None,
    verified_upstream_sha256s: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Create a body-free receipt for protected or invented source rows."""

    frozen = dict(_mapping(contract, "protected prompt-fit contract"))
    _contract_semantics(frozen)
    if not isinstance(production, bool):
        raise ContractError("production mode flag must be boolean")
    if isinstance(row_source_bytes, bool) or not isinstance(row_source_bytes, int) or row_source_bytes <= 0:
        raise ContractError("row source byte count must be a positive integer")
    _sha256_text(row_source_sha256, "row source SHA-256")
    _sha256_text(mask_manifest_sha256, "mask manifest SHA-256")
    _sha256_text(prompt_bundle_sha256, "prompt bundle SHA-256")
    _sha256_text(direct_route_contract_sha256, "direct-route contract SHA-256")

    canonical_source_file = canonical_json_bytes(row_source) + b"\n"
    if row_source_bytes != len(canonical_source_file) or row_source_sha256 != sha256_bytes(
        canonical_source_file
    ):
        raise ContractError("row source byte/hash binding requires canonical JSON plus one LF")
    if production:
        if prompt_bundle_sha256 != EXPECTED_UPSTREAM_HASHES[
            "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
        ]:
            raise ContractError("prompt bundle SHA-256 differs from frozen artifact")
        if direct_route_contract_sha256 != EXPECTED_UPSTREAM_HASHES[
            "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
        ]:
            raise ContractError("direct-route contract SHA-256 differs from frozen artifact")
    else:
        if prompt_bundle_sha256 != sha256_file(PROMPT_PATH):
            raise ContractError("prompt bundle SHA-256 differs from frozen artifact")
        if canonical_json_bytes(prompt_bundle) != canonical_json_bytes(
            strict_json_object_from_file(PROMPT_PATH, "frozen prompt bundle")
        ):
            raise ContractError("prompt bundle object differs from frozen artifact")
        if direct_route_contract_sha256 != sha256_file(DIRECT_CONTRACT_PATH):
            raise ContractError("direct-route contract SHA-256 differs from frozen artifact")
    _validate_prompt_bundle(prompt_bundle)
    if production:
        if verified_upstream_sha256s is None:
            raise ContractError("production requires held-descriptor upstream SHA-256 bindings")
        validate_production_bindings(
            frozen,
            mask_manifest,
            prompt_bundle,
            verified_upstream_sha256s=verified_upstream_sha256s,
        )
        if mask_manifest_sha256 != EXPECTED_UPSTREAM_HASHES[
            "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json"
        ]:
            raise ContractError("production mask manifest SHA-256 mismatch")
        if (
            live_staging_receipt is None
            or live_staging_receipt_bytes is None
            or live_staging_receipt_sha256 is None
            or live_model_measurement is None
        ):
            raise ContractError(
                "production requires independent staging receipt and live GGUF descriptor measurement"
            )
        live_staging = validate_live_staging_binding(
            staging_receipt=live_staging_receipt,
            staging_receipt_bytes=live_staging_receipt_bytes,
            staging_receipt_sha256=live_staging_receipt_sha256,
            live_model_measurement=live_model_measurement,
        )
    elif mask_manifest_sha256 != canonical_hash(mask_manifest):
        raise ContractError("synthetic mask manifest SHA-256 binding mismatch")
    else:
        live_staging = {
            "status": "CANNOT_CHECK_LIVE_GGUF_NOT_OPENED_IN_SYNTHETIC_VALIDATION",
            "staging_receipt_bytes": None,
            "staging_receipt_sha256": None,
            "source_receipt_sha256": None,
            "live_model_bytes": None,
            "live_model_sha256": None,
            "live_measurement_method": None,
            "source_receipt_substituted_for_live_measurement": False,
        }

    records = _validate_manifest_records(mask_manifest, production=production)
    rows = _validate_source_metadata(
        row_source, mask_manifest, frozen, production=production
    )
    row_ids: list[Any] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError("row source rows must be objects")
        row_ids.append(row.get("instance_id"))
    if any(not isinstance(instance_id, str) or not instance_id for instance_id in row_ids):
        raise ContractError("row source instance_id must be a nonempty string")
    if len(set(row_ids)) != len(row_ids):
        raise ContractError("duplicate task ID in row source")
    manifest_ids = [record.get("instance_id") for record in records]
    if set(row_ids) != set(manifest_ids):
        raise ContractError("row source task set differs from mask manifest task set")
    if row_ids != manifest_ids:
        raise ContractError("row source order differs from mask manifest order")

    source = _mapping(row_source.get("source"), "row source provenance")
    bindings = _source_bindings(
        row_source_bytes=row_source_bytes,
        row_source_sha256=row_source_sha256,
        mask_manifest_sha256=mask_manifest_sha256,
        prompt_bundle_sha256=prompt_bundle_sha256,
        direct_route_contract_sha256=direct_route_contract_sha256,
        verified_parquet_sha256=_sha256_text(
            source.get("verified_parquet_sha256"), "verified parquet SHA-256"
        ),
        live_staging_receipt_sha256=live_staging["staging_receipt_sha256"],
        live_model_bytes=live_staging["live_model_bytes"],
        live_model_sha256=live_staging["live_model_sha256"],
    )

    task_receipts: list[dict[str, Any]] = []
    for row, record in zip(rows, records):
        packets = packetize_bound_row(row, record)
        task_receipts.append(
            {
                "instance_id": row["instance_id"],
                "manifest_binding_sha256": packets["manifest_binding_sha256"],
                "masked_packet_binding": _byte_binding(packets["masked_packet"]),
                "recovered_packet_binding": _byte_binding(packets["recovered_packet"]),
                "state_independent_prompts": _static_prompt_records(prompt_bundle, packets),
                "dynamic_rr_phase1_prompts": _dynamic_rr_phase1_records(),
                "static_prompt_fit_status": MISSING_LEDGER_STATUS,
                "overall_prompt_fit_status": (
                    "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_AND_EXACT_GGUF_TOKEN_LEDGER_REQUIRED"
                ),
            }
        )

    if token_ledger is None:
        tokenizer_measurement = {
            "status": MISSING_LEDGER_STATUS,
            "ledger_sha256": None,
            "records": 0,
            "all_state_independent_prompts_fit": None,
            "token_counts_independently_remeasured_here": False,
            "dynamic_rr_phase1_status": "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
        }
    else:
        tokenizer_measurement = _apply_token_ledger(
            task_receipts, token_ledger, frozen, bindings
        )

    task_count = len(task_receipts)
    receipt = {
        "schema_version": "orion.p1.scienceagentbench.protected-prompt-fit-receipt.v1",
        "authority": "HASH_BYTE_COUNT_AND_TYPED_PREFLIGHT_STATUS_ONLY__NO_BODY_EXECUTION_EVALUATION_OR_SCIENTIFIC_AUTHORITY",
        "mode": (
            "PROTECTED_OWNER_AUTHORIZED_PREFLIGHT"
            if production
            else "SYNTHETIC_NONBENCHMARK_VALIDATION"
        ),
        "source_bindings": bindings,
        "live_model_staging": live_staging,
        "counts": {
            "tasks": task_count,
            "authorized_protected_tasks_opened_for_preflight": task_count if production else 0,
            "state_independent_prompt_records": task_count * 12,
            "dynamic_rr_phase1_records": task_count * 3,
            "packet_bodies_retained": 0,
            "prompt_bodies_retained": 0,
            "tasks_executed": 0,
            "official_outcomes_opened": 0,
        },
        "tokenizer_measurement": tokenizer_measurement,
        "task_receipts": task_receipts,
        "claim_boundary": copy.deepcopy(CLAIM_BOUNDARY),
    }
    return receipt


def _descriptor_flags(*, directory: bool) -> int:
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise ContractError("platform lacks required openat/O_NOFOLLOW support")
    flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if directory:
        if not hasattr(os, "O_DIRECTORY"):
            raise ContractError("platform lacks required O_DIRECTORY support")
        flags |= os.O_DIRECTORY
    return flags


def _stat_signature(info: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _directory_signature(info: os.stat_result) -> tuple[int, int, int]:
    return info.st_dev, info.st_ino, info.st_mode


class _HeldDirectoryChain:
    """Hold every directory component from root and recheck each openat edge."""

    def __init__(self, path: Path, label: str) -> None:
        self.path = Path(path)
        self.label = label
        self._fds: list[int] = []
        self._edges: list[tuple[int, str, int, tuple[int, int, int]]] = []
        if not self.path.is_absolute():
            raise ContractError(f"{label} must be absolute")
        parts = self.path.parts
        if not parts or parts[0] != os.sep or any(part in {"", ".", ".."} for part in parts[1:]):
            raise ContractError(f"{label} contains a forbidden lexical component")
        try:
            root_fd = os.open(os.sep, _descriptor_flags(directory=True))
            self._fds.append(root_fd)
            current_fd = root_fd
            for component in parts[1:]:
                child_fd = os.open(
                    component,
                    _descriptor_flags(directory=True),
                    dir_fd=current_fd,
                )
                self._fds.append(child_fd)
                child_info = os.fstat(child_fd)
                if not stat.S_ISDIR(child_info.st_mode):
                    raise ContractError(f"{label} component is not a directory: {component}")
                self._edges.append(
                    (current_fd, component, child_fd, _directory_signature(child_info))
                )
                current_fd = child_fd
        except Exception as exc:
            self.close()
            if isinstance(exc, ContractError):
                raise
            raise ContractError(f"{label} directory chain cannot be opened safely") from exc

    @property
    def leaf_fd(self) -> int:
        if not self._fds:
            raise ContractError(f"{self.label} directory chain is closed")
        return self._fds[-1]

    @property
    def identity(self) -> tuple[int, int]:
        info = os.fstat(self.leaf_fd)
        return info.st_dev, info.st_ino

    def verify(self) -> None:
        for parent_fd, component, child_fd, original in self._edges:
            try:
                held = os.fstat(child_fd)
                named = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
            except OSError as exc:
                raise ContractError(
                    f"{self.label} directory path changed after descriptor acquisition"
                ) from exc
            if (
                not stat.S_ISDIR(named.st_mode)
                or _directory_signature(held) != original
                or (named.st_dev, named.st_ino) != (held.st_dev, held.st_ino)
            ):
                raise ContractError(
                    f"{self.label} directory path changed after descriptor acquisition"
                )

    def close(self) -> None:
        while self._fds:
            try:
                os.close(self._fds.pop())
            except OSError:
                pass


class _HeldRegularFile:
    def __init__(self, path: Path, label: str) -> None:
        self.path = Path(path)
        self.label = label
        if not self.path.is_absolute() or self.path.name in {"", ".", ".."}:
            raise ContractError(f"{label} must be one absolute regular-file path")
        self.parent = _HeldDirectoryChain(self.path.parent, f"{label} parent")
        self.fd = -1
        try:
            self.fd = os.open(
                self.path.name,
                _descriptor_flags(directory=False),
                dir_fd=self.parent.leaf_fd,
            )
            info = os.fstat(self.fd)
            if not stat.S_ISREG(info.st_mode):
                raise ContractError(f"{label} is not a regular file")
            self._opened_signature = _stat_signature(info)
            self.verify_unchanged()
        except Exception as exc:
            self.close()
            if isinstance(exc, ContractError):
                raise
            raise ContractError(
                f"{label} cannot be opened safely; symlink and nonregular inputs are forbidden"
            ) from exc

    @property
    def identity(self) -> tuple[int, int]:
        info = os.fstat(self.fd)
        return info.st_dev, info.st_ino

    def verify_unchanged(self) -> None:
        self.parent.verify()
        try:
            held = os.fstat(self.fd)
            named = os.stat(
                self.path.name,
                dir_fd=self.parent.leaf_fd,
                follow_symlinks=False,
            )
        except OSError as exc:
            raise ContractError(f"{self.label} path changed after descriptor acquisition") from exc
        if (
            not stat.S_ISREG(named.st_mode)
            or _stat_signature(held) != self._opened_signature
            or (named.st_dev, named.st_ino) != (held.st_dev, held.st_ino)
        ):
            raise ContractError(f"{self.label} path changed after descriptor acquisition")

    def _read_or_hash(self, *, return_bytes: bool) -> bytes | tuple[int, str]:
        # The descriptor is the read authority. A concurrent pathname swap is
        # detected by the caller's final verify, but can never redirect these
        # bytes to the replacement path.
        self.parent.verify()
        before = _stat_signature(os.fstat(self.fd))
        os.lseek(self.fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(self.fd, 1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            digest.update(chunk)
            if return_bytes:
                chunks.append(chunk)
        after = _stat_signature(os.fstat(self.fd))
        if after != before:
            raise ContractError(f"{self.label} changed while read from held descriptor")
        self.parent.verify()
        if return_bytes:
            return b"".join(chunks)
        return total, digest.hexdigest()

    def read_bytes(self) -> bytes:
        result = self._read_or_hash(return_bytes=True)
        if not isinstance(result, bytes):
            raise ContractError(f"{self.label} descriptor read failed")
        return result

    def measure(self) -> tuple[int, str]:
        result = self._read_or_hash(return_bytes=False)
        if not isinstance(result, tuple):
            raise ContractError(f"{self.label} descriptor measurement failed")
        return result

    def close(self) -> None:
        if self.fd >= 0:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = -1
        if hasattr(self, "parent"):
            self.parent.close()


class _HeldOutputDestination:
    def __init__(self, path: Path, label: str) -> None:
        self.path = Path(path)
        self.label = label
        if not self.path.is_absolute() or self.path.name in {"", ".", ".."}:
            raise ContractError(f"{label} must be one absolute output path")
        self.parent = _HeldDirectoryChain(self.path.parent, f"{label} parent")
        self._created_identity: tuple[int, int] | None = None
        self._created_sha256: str | None = None
        try:
            self.verify_absent()
        except Exception:
            self.close()
            raise

    @property
    def parent_identity(self) -> tuple[int, int]:
        return self.parent.identity

    def verify_absent(self) -> None:
        self.parent.verify()
        try:
            os.stat(
                self.path.name,
                dir_fd=self.parent.leaf_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return
        except OSError as exc:
            raise ContractError(f"{self.label} cannot be inspected safely") from exc
        raise ContractError(f"output destination already exists: {self.path}")

    def write_canonical_json(self, value: Any) -> str:
        self.verify_absent()
        payload = canonical_json_bytes(value) + b"\n"
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        fd = -1
        identity: tuple[int, int] | None = None
        try:
            fd = os.open(
                self.path.name,
                flags,
                0o600,
                dir_fd=self.parent.leaf_fd,
            )
            info = os.fstat(fd)
            identity = (info.st_dev, info.st_ino)
            if not stat.S_ISREG(info.st_mode):
                raise ContractError(f"output destination is not a regular file: {self.path}")
            view = memoryview(payload)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise ContractError(f"output write made no progress: {self.path}")
                view = view[written:]
            os.fsync(fd)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise ContractError(f"output destination is not a regular file: {self.path}")
            os.lseek(fd, 0, os.SEEK_SET)
            observed_chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                observed_chunks.append(chunk)
            observed = b"".join(observed_chunks)
            named = os.stat(
                self.path.name,
                dir_fd=self.parent.leaf_fd,
                follow_symlinks=False,
            )
            if (
                observed != payload
                or not stat.S_ISREG(named.st_mode)
                or (named.st_dev, named.st_ino) != identity
            ):
                raise ContractError(f"output byte/hash/identity verification failed: {self.path}")
            self.parent.verify()
            digest = sha256_bytes(observed)
            self._created_identity = identity
            self._created_sha256 = digest
            return digest
        except Exception as exc:
            if fd >= 0 and identity is not None:
                try:
                    named = os.stat(
                        self.path.name,
                        dir_fd=self.parent.leaf_fd,
                        follow_symlinks=False,
                    )
                    if (named.st_dev, named.st_ino) == identity:
                        os.unlink(self.path.name, dir_fd=self.parent.leaf_fd)
                except OSError:
                    pass
            if isinstance(exc, ContractError):
                raise
            raise ContractError(f"output write or verification failed: {self.path}") from exc
        finally:
            if fd >= 0:
                os.close(fd)

    def rollback_created_if_unchanged(self) -> bool:
        if self._created_identity is None or self._created_sha256 is None:
            return False
        flags = _descriptor_flags(directory=False)
        try:
            fd = os.open(
                self.path.name,
                flags,
                dir_fd=self.parent.leaf_fd,
            )
        except OSError:
            return False
        try:
            info = os.fstat(fd)
            if (
                not stat.S_ISREG(info.st_mode)
                or (info.st_dev, info.st_ino) != self._created_identity
            ):
                return False
            digest = hashlib.sha256()
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            if digest.hexdigest() != self._created_sha256:
                return False
            named = os.stat(
                self.path.name,
                dir_fd=self.parent.leaf_fd,
                follow_symlinks=False,
            )
            if (named.st_dev, named.st_ino) != self._created_identity:
                return False
            os.unlink(self.path.name, dir_fd=self.parent.leaf_fd)
            self._created_identity = None
            self._created_sha256 = None
            return True
        except OSError:
            return False
        finally:
            os.close(fd)

    def verify_created_unchanged(self) -> None:
        if self._created_identity is None or self._created_sha256 is None:
            raise ContractError(f"{self.label} has no verified created identity")
        self.parent.verify()
        try:
            fd = os.open(
                self.path.name,
                _descriptor_flags(directory=False),
                dir_fd=self.parent.leaf_fd,
            )
        except OSError as exc:
            raise ContractError(f"{self.label} changed after output creation") from exc
        try:
            info = os.fstat(fd)
            if (
                not stat.S_ISREG(info.st_mode)
                or (info.st_dev, info.st_ino) != self._created_identity
            ):
                raise ContractError(f"{self.label} changed after output creation")
            digest = hashlib.sha256()
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            named = os.stat(
                self.path.name,
                dir_fd=self.parent.leaf_fd,
                follow_symlinks=False,
            )
            if (
                digest.hexdigest() != self._created_sha256
                or (named.st_dev, named.st_ino) != self._created_identity
            ):
                raise ContractError(f"{self.label} changed after output creation")
        finally:
            os.close(fd)
        self.parent.verify()

    def close(self) -> None:
        self.parent.close()


class OpenCliResources:
    """Own verified input/upstream file descriptors and output parent FDs."""

    def __init__(
        self,
        inputs: Mapping[str, Path],
        outputs: Mapping[str, Path],
        upstream_paths: Mapping[str, Path],
    ) -> None:
        self.inputs: dict[str, _HeldRegularFile] = {}
        self.upstreams: dict[str, _HeldRegularFile] = {}
        self.outputs: dict[str, _HeldOutputDestination] = {}
        try:
            all_lexical: dict[str, Path] = {}
            for group_name, group in (
                ("input", inputs),
                ("output", outputs),
                ("upstream", upstream_paths),
            ):
                for name, path in group.items():
                    label = f"{group_name} {name}"
                    candidate = Path(path)
                    if not candidate.is_absolute():
                        raise ContractError(f"{label} must be absolute")
                    normalized = Path(os.path.normpath(os.fspath(candidate)))
                    if normalized != candidate:
                        raise ContractError(f"{label} contains a noncanonical lexical path")
                    all_lexical[label] = candidate
            labels = list(all_lexical)
            for index, left in enumerate(labels):
                for right in labels[index + 1 :]:
                    if all_lexical[left] == all_lexical[right]:
                        raise ContractError(f"CLI paths alias lexically: {left} and {right}")
                    if os.fspath(all_lexical[left]).casefold() == os.fspath(
                        all_lexical[right]
                    ).casefold():
                        raise ContractError(f"CLI paths alias after case-fold: {left} and {right}")

            for name, path in inputs.items():
                self.inputs[name] = _HeldRegularFile(Path(path), f"input {name}")
            for name, path in upstream_paths.items():
                self.upstreams[name] = _HeldRegularFile(Path(path), f"upstream {name}")
            for name, path in outputs.items():
                self.outputs[name] = _HeldOutputDestination(Path(path), f"output {name}")

            held_files = [
                (f"input {name}", value) for name, value in self.inputs.items()
            ] + [
                (f"upstream {name}", value) for name, value in self.upstreams.items()
            ]
            for index, (left_name, left) in enumerate(held_files):
                for right_name, right in held_files[index + 1 :]:
                    if left.identity == right.identity:
                        raise ContractError(
                            f"CLI paths alias by device/inode: {left_name} and {right_name}"
                        )
            for output_name, output in self.outputs.items():
                for file_name, held in held_files:
                    if (
                        output.parent_identity == held.parent.identity
                        and output.path.name.casefold() == held.path.name.casefold()
                    ):
                        raise ContractError(
                            f"CLI output aliases held file: output {output_name} and {file_name}"
                        )
            self.verify_all_paths_unchanged()
        except Exception:
            self.close()
            raise

    def __enter__(self) -> "OpenCliResources":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def read_input_bytes(self, name: str) -> bytes:
        if name not in self.inputs:
            raise ContractError(f"unknown held input: {name}")
        return self.inputs[name].read_bytes()

    def read_upstream_bytes(self, name: str) -> bytes:
        if name not in self.upstreams:
            raise ContractError(f"unknown held upstream: {name}")
        return self.upstreams[name].read_bytes()

    def measure_input(self, name: str) -> tuple[int, str]:
        if name not in self.inputs:
            raise ContractError(f"unknown held input: {name}")
        return self.inputs[name].measure()

    def measure_upstream(self, name: str) -> tuple[int, str]:
        if name not in self.upstreams:
            raise ContractError(f"unknown held upstream: {name}")
        return self.upstreams[name].measure()

    def input_filename(self, name: str) -> str:
        if name not in self.inputs:
            raise ContractError(f"unknown held input: {name}")
        return self.inputs[name].path.name

    def write_output_canonical_json(self, name: str, value: Any) -> str:
        if name not in self.outputs:
            raise ContractError(f"unknown held output: {name}")
        self.verify_all_paths_unchanged()
        output = self.outputs[name]
        digest = output.write_canonical_json(value)
        try:
            self.verify_all_paths_unchanged(include_outputs=False)
        except Exception as exc:
            if not output.rollback_created_if_unchanged():
                raise ContractError(
                    "post-write path verification failed and receipt rollback could not be verified"
                ) from exc
            raise
        return digest

    def verify_all_paths_unchanged(self, *, include_outputs: bool = True) -> None:
        for held in self.inputs.values():
            held.verify_unchanged()
        for held in self.upstreams.values():
            held.verify_unchanged()
        if include_outputs:
            for output in self.outputs.values():
                output.verify_absent()
        else:
            for output in self.outputs.values():
                output.verify_created_unchanged()

    def close(self) -> None:
        for held in self.inputs.values():
            held.close()
        for held in self.upstreams.values():
            held.close()
        for output in self.outputs.values():
            output.close()


def open_cli_resources(
    inputs: Mapping[str, Path],
    outputs: Mapping[str, Path],
    upstream_paths: Mapping[str, Path],
) -> OpenCliResources:
    return OpenCliResources(inputs, outputs, upstream_paths)


def validate_cli_paths(
    inputs: Mapping[str, Path],
    outputs: Mapping[str, Path],
    upstream_paths: Mapping[str, Path],
) -> None:
    """Compatibility gate; production keeps the returned descriptors open."""

    with open_cli_resources(inputs, outputs, upstream_paths):
        pass


def write_new_canonical_json(path: Path | str, value: Any) -> str:
    """Compatibility wrapper using a held parent descriptor and openat."""

    candidate = Path(path)
    with open_cli_resources({}, {"output": candidate}, {}) as resources:
        return resources.write_output_canonical_json("output", value)


def _static_upstream_paths() -> dict[str, Path]:
    return {
        "preflight implementation": MODULE_PATH,
        "preflight contract": CONTRACT_PATH,
        "direct-route contract": DIRECT_CONTRACT_PATH,
        "direct-route driver": DIRECT_DRIVER_PATH,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bind authorized protected rows and preflight direct-route prompt fit"
    )
    parser.add_argument("--row-source", type=Path, required=True)
    parser.add_argument("--mask-manifest", type=Path, required=True)
    parser.add_argument("--prompt-bundle", type=Path, required=True)
    parser.add_argument("--live-gguf", type=Path, required=True)
    parser.add_argument("--live-staging-receipt", type=Path, required=True)
    parser.add_argument("--token-ledger", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)

    inputs = {
        "row source": arguments.row_source,
        "mask manifest": arguments.mask_manifest,
        "prompt bundle": arguments.prompt_bundle,
        "live GGUF": arguments.live_gguf,
        "live staging receipt": arguments.live_staging_receipt,
    }
    if arguments.token_ledger is not None:
        inputs["token ledger"] = arguments.token_ledger
    with open_cli_resources(
        inputs, {"receipt": arguments.output}, _static_upstream_paths()
    ) as resources:
        row_source_raw = resources.read_input_bytes("row source")
        row_source = strict_json_object_from_bytes(row_source_raw, "authorized row source")
        canonical_source_raw = canonical_json_bytes(row_source) + b"\n"
        if row_source_raw != canonical_source_raw:
            raise ContractError("authorized row source file must be canonical JSON plus one LF")
        mask_raw = resources.read_input_bytes("mask manifest")
        mask_manifest = strict_json_object_from_bytes(mask_raw, "mask manifest")
        prompt_raw = resources.read_input_bytes("prompt bundle")
        prompt_bundle = strict_json_object_from_bytes(prompt_raw, "prompt bundle")
        staging_raw = resources.read_input_bytes("live staging receipt")
        staging_receipt = strict_json_object_from_bytes(
            staging_raw, "live GGUF staging receipt"
        )
        token_ledger = (
            strict_json_object_from_bytes(
                resources.read_input_bytes("token ledger"), "exact GGUF token ledger"
            )
            if arguments.token_ledger is not None
            else None
        )
        contract = strict_json_object_from_bytes(
            resources.read_upstream_bytes("preflight contract"),
            "protected prompt-fit contract",
        )
        live_model_bytes, live_model_sha256 = resources.measure_input("live GGUF")
        live_model_measurement = {
            "model_filename": resources.input_filename("live GGUF"),
            "live_model_bytes": live_model_bytes,
            "live_model_sha256": live_model_sha256,
            "measurement_method": LIVE_MEASUREMENT_METHOD,
        }
        _, direct_contract_sha256 = resources.measure_upstream("direct-route contract")
        _, direct_driver_sha256 = resources.measure_upstream("direct-route driver")
        verified_upstream_sha256s = {
            "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json": sha256_bytes(mask_raw),
            "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": sha256_bytes(prompt_raw),
            "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": direct_contract_sha256,
            "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py": direct_driver_sha256,
        }
        receipt = build_preflight_receipt(
            row_source=row_source,
            row_source_bytes=len(row_source_raw),
            row_source_sha256=sha256_bytes(row_source_raw),
            mask_manifest=mask_manifest,
            mask_manifest_sha256=sha256_bytes(mask_raw),
            prompt_bundle=prompt_bundle,
            prompt_bundle_sha256=sha256_bytes(prompt_raw),
            direct_route_contract_sha256=direct_contract_sha256,
            contract=contract,
            token_ledger=token_ledger,
            production=True,
            live_staging_receipt=staging_receipt,
            live_staging_receipt_bytes=len(staging_raw),
            live_staging_receipt_sha256=sha256_bytes(staging_raw),
            live_model_measurement=live_model_measurement,
            verified_upstream_sha256s=verified_upstream_sha256s,
        )
        receipt_sha256 = resources.write_output_canonical_json("receipt", receipt)
    print(
        "P1_SAB_PROTECTED_PROMPT_FIT_PREFLIGHT_V1_RECEIPT_WRITTEN "
        f"tasks={receipt['counts']['tasks']} "
        f"static_prompts={receipt['counts']['state_independent_prompt_records']} "
        f"dynamic_rr_phase1={receipt['counts']['dynamic_rr_phase1_records']} "
        f"receipt_sha256={receipt_sha256} "
        "outcomes_opened=0 tasks_executed=0 production_admissibility=CANNOT_CHECK"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as exc:
        raise SystemExit(f"P1_SAB_PROTECTED_PROMPT_FIT_PREFLIGHT_V1_FAIL: {exc}") from exc
