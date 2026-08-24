#!/usr/bin/env python3
"""Outcome-blind direct llama-server driver bound to Runner V2 metadata.

The driver launches no process and performs no model pull.  Every completion
uses an injected client; the provided concrete client permits only the frozen
``http://127.0.0.1:8080/completion`` endpoint.  Generation receipts remain at
the existing adapter's scheduler-finalization-pending boundary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import http.client
import importlib.util
import json
import math
import os
import stat
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CONTRACT_PATH = ROOT / "DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
PROMPT_BUNDLE_PATH = ROOT / "DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
ADAPTER_PATH = (
    REPO_ROOT
    / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py"
)
ADAPTER_SHA256 = "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9"
DRIVER_PATH = Path(__file__).resolve()
STATIC_UPSTREAM_RELATIVE_PATHS = (
    "development/p1-scienceagentbench-runner-v1-2026-08-24/RUNNER_CONTRACT_V1.json",
    "development/p1-scienceagentbench-runner-v1-2026-08-24/sab_verified_runner_v1.py",
    "development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/RUNNER_V2_COST_AMENDMENT_CONTRACT.json",
    "development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/sab_runner_v2_cost_amendment.py",
    "development/p1-scienceagentbench-analysis-freeze-v1-2026-08-24/ANALYSIS_CONTRACT_V1.json",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/LUNARC_GENERATION_ADAPTER_CONTRACT_V1.json",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh",
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/FROZEN_LONGSEED_MECHANISM_PROTOCOL_V1.json",
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/LONGSEED_MECHANISM_RECEIPT_V1.json",
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/PROMPT_PROVENANCE_V1.json",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/FROZEN_LONGSEED_STRUCTURED_PROTOCOL_V1.json",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/LONGSEED_STRUCTURED_RECEIPT_V1.json",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/FROZEN_OUTPUT_SCHEMA_V1.json",
)
CONTEXT_WINDOW_TOKENS = 32768
SEED_SCHEDULE = {"1": 101, "2": 202, "3": 303}
PHASE_SEQUENCE_BY_ARM = {
    "RR": ("RR_PHASE0", "RR_PHASE1"),
    "OS": ("OS_PHASE1",),
    "NR": ("NR_PHASE0", "NR_PHASE1"),
}
FROZEN_SAMPLING = {
    "temperature": 0.2,
    "top_k": 20,
    "top_p": 0.95,
    "min_p": 0.0,
    "repeat_penalty": 1.0,
    "stream": False,
    "return_tokens": True,
    "cache_prompt": False,
}
PHASE0_SCHEMA_BINDING = (
    567,
    "11299b5be0c855c1453ef99a14d1637b5c11230409efd68f50fde3394341cba1",
)
FINAL_SCHEMA_BINDING = (
    239,
    "428e793d1f94a5b9e56731a8dd96a28b7e089aaad63d6a2be722d3ed7b266c2c",
)


class ContractError(ValueError):
    """An input or observed response cannot satisfy the frozen route."""


class DuplicateJsonMemberError(ValueError):
    """A strict JSON object repeated a member name."""


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
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonMemberError(f"duplicate JSON member: {key}")
        value[key] = item
    return value


def _reject_nonfinite(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def strict_json_object_from_bytes(payload: bytes, label: str) -> dict[str, Any]:
    if not isinstance(payload, bytes):
        raise ContractError(f"{label} must be bytes")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_members,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonMemberError, ValueError) as exc:
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


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _require_exact_fields(value: Mapping[str, Any], fields: set[str], label: str) -> None:
    observed = set(value)
    if observed != fields:
        raise ContractError(
            f"{label} fields mismatch: missing={sorted(fields - observed)} extra={sorted(observed - fields)}"
        )


def _positive_number(value: Any, label: str, *, integer: bool = False) -> int | float:
    if isinstance(value, bool):
        raise ContractError(f"{label} must be a positive finite number")
    if integer:
        if not isinstance(value, int):
            raise ContractError(f"{label} must be a positive integer")
    elif not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be a positive finite number")
    if not math.isfinite(value) or value <= 0:
        raise ContractError(f"{label} must be positive")
    return value


def _nonnegative_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{label} must be a nonnegative integer")
    return value


def validate_owner_selection(selection: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a pre-task equal budget selection and fixed per-phase caps."""

    selected = dict(_require_mapping(selection, "owner selection"))
    allowed_statuses = {
        "OWNER_FROZEN_BEFORE_TASK_OR_OUTCOME_OPENING",
        "OWNER_PROSPECTIVE_BUDGET_FROZEN_BEFORE_TASK_OR_OUTCOME_OPENING",
    }
    if selected.get("status") not in allowed_statuses:
        raise ContractError("owner selection status is not a frozen pre-opening status")
    if selected.get("selected_before_task_or_outcome_opening") is not True:
        raise ContractError("owner selection must occur before task or outcome opening")
    if selected.get("protected_prompt_sizes_used") is not False:
        raise ContractError("owner selection cannot use protected prompt sizes")
    if selected.get("context_window_tokens") != CONTEXT_WINDOW_TOKENS:
        raise ContractError("owner selection context window must equal 32768")

    budgets = _require_mapping(selected.get("budget_by_arm"), "budget_by_arm")
    if set(budgets) != set(PHASE_SEQUENCE_BY_ARM):
        raise ContractError("budget_by_arm must bind exactly RR, OS, and NR")
    budget_fields = {
        "total_input_token_cap",
        "total_output_token_cap",
        "tool_call_cap",
        "wall_time_seconds_cap",
        "local_execution_seconds_cap",
        "final_candidates_per_attempt",
    }
    canonical_budgets: list[bytes] = []
    for arm in PHASE_SEQUENCE_BY_ARM:
        budget = _require_mapping(budgets[arm], f"budget_by_arm.{arm}")
        _require_exact_fields(budget, budget_fields, f"budget_by_arm.{arm}")
        _positive_number(budget["total_input_token_cap"], "total_input_token_cap", integer=True)
        _positive_number(budget["total_output_token_cap"], "total_output_token_cap", integer=True)
        _positive_number(budget["wall_time_seconds_cap"], "wall_time_seconds_cap")
        _positive_number(
            budget["local_execution_seconds_cap"], "local_execution_seconds_cap"
        )
        if budget["tool_call_cap"] != 0 or isinstance(budget["tool_call_cap"], bool):
            raise ContractError("tool_call_cap must equal zero")
        if (
            budget["final_candidates_per_attempt"] != 1
            or isinstance(budget["final_candidates_per_attempt"], bool)
        ):
            raise ContractError("final_candidates_per_attempt must equal one")
        canonical_budgets.append(canonical_json_bytes(budget))
    if len(set(canonical_budgets)) != 1:
        raise ContractError("RR, OS, and NR budget objects must be byte-equal")

    caps = _require_mapping(
        selected.get("phase_output_caps_by_arm"), "phase_output_caps_by_arm"
    )
    if set(caps) != set(PHASE_SEQUENCE_BY_ARM):
        raise ContractError("phase_output_caps_by_arm must bind exactly RR, OS, and NR")
    total_output = budgets["RR"]["total_output_token_cap"]
    for arm, phases in PHASE_SEQUENCE_BY_ARM.items():
        arm_caps = _require_mapping(caps[arm], f"phase caps {arm}")
        if tuple(arm_caps) != phases:
            raise ContractError(f"phase caps for {arm} must follow exact phase order")
        for phase in phases:
            _positive_number(arm_caps[phase], f"{phase} cap", integer=True)
        if sum(arm_caps.values()) != total_output:
            raise ContractError(f"phase cap sum for {arm} must equal total output envelope")
        if any(value > CONTEXT_WINDOW_TOKENS for value in arm_caps.values()):
            raise ContractError(f"phase cap for {arm} exceeds context window")
    return copy.deepcopy(selected)


def validate_runtime_binding(
    runtime_binding: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    observed = dict(_require_mapping(runtime_binding, "runtime binding"))
    frozen = dict(
        _require_mapping(contract.get("model_runtime_binding"), "contract runtime binding")
    )
    if canonical_json_bytes(observed) != canonical_json_bytes(frozen):
        raise ContractError("runtime binding differs from the frozen model/runtime identity")
    geometry = _require_mapping(observed.get("server_geometry"), "server geometry")
    expected_geometry = {
        "listen_host": "127.0.0.1",
        "context_tokens": 32768,
        "parallel_slots": 1,
        "continuous_batching": False,
        "cache_prompt": False,
        "context_shift": False,
    }
    if geometry != expected_geometry:
        raise ContractError("server geometry differs from the frozen loopback geometry")
    return copy.deepcopy(observed)


def validate_packet_contract(
    contract: Mapping[str, Any], prompt_bundle: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify immutable dependencies, route claims, schemas, and templates."""

    frozen = dict(_require_mapping(contract, "direct-route contract"))
    prompt = dict(_require_mapping(prompt_bundle, "direct-route prompt bundle"))
    on_disk_contract = strict_json_object_from_file(CONTRACT_PATH, "on-disk contract")
    on_disk_prompt = strict_json_object_from_file(PROMPT_BUNDLE_PATH, "on-disk prompt bundle")
    if canonical_json_bytes(frozen) != canonical_json_bytes(on_disk_contract):
        raise ContractError("contract object differs from the on-disk frozen contract")
    if canonical_json_bytes(prompt) != canonical_json_bytes(on_disk_prompt):
        raise ContractError("prompt object differs from the on-disk frozen prompt bundle")
    if frozen.get("schema_version") != "orion.p1.scienceagentbench.direct-route-freeze.v1":
        raise ContractError("direct-route contract schema mismatch")
    if prompt.get("schema_version") != "orion.p1.scienceagentbench.direct-route-prompt-bundle.v1":
        raise ContractError("prompt bundle schema mismatch")
    if frozen.get("runner_or_adapter_modification") is not False:
        raise ContractError("runner or adapter modification is forbidden")
    if frozen.get("production_execution_authority") is not False:
        raise ContractError("packet cannot grant production execution authority")
    if frozen.get("seed_schedule") != SEED_SCHEDULE:
        raise ContractError("paired seed schedule mismatch")
    if frozen.get("sampling") != FROZEN_SAMPLING:
        raise ContractError("frozen sampling mismatch")
    if frozen.get("attempt_retention") != "ALL_ATTEMPTS_NO_SELECTION":
        raise ContractError("attempt retention must keep every attempt without selection")
    claim = _require_mapping(frozen.get("claim_boundary"), "claim boundary")
    required_claim = {
        "provider_seed_capability": "CONFIRMED",
        "semantic_choice_sensitivity": "NOT_ESTABLISHED",
        "candidate_semantic_diversity_gate_enabled": False,
        "attempt_retention": "ALL_ATTEMPTS_NO_SELECTION",
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
    }
    if claim != required_claim:
        raise ContractError("claim boundary mismatch")

    expected_files: dict[str, str] = {}
    for group in (
        frozen.get("upstream_bindings"),
        _require_mapping(
            frozen.get("repaired_pr1159_bindings"), "repaired PR binding"
        ).get("files"),
    ):
        if not isinstance(group, list):
            raise ContractError("dependency binding group must be a list")
        for entry in group:
            bound = _require_mapping(entry, "dependency binding")
            path = bound.get("path")
            digest = bound.get("sha256")
            if not isinstance(path, str) or not isinstance(digest, str):
                raise ContractError("dependency binding must contain path and SHA-256")
            expected_files[path] = digest
    for relative, expected in expected_files.items():
        observed = sha256_file(REPO_ROOT / relative)
        if observed != expected:
            raise ContractError(
                f"frozen dependency SHA-256 drift: path={relative} expected={expected} observed={observed}"
            )

    schemas = _require_mapping(prompt.get("output_schemas"), "output schemas")
    bindings = _require_mapping(
        prompt.get("output_schema_canonical_bindings"), "schema canonical bindings"
    )
    for name, expected in {
        "phase0_state": PHASE0_SCHEMA_BINDING,
        "final_program": FINAL_SCHEMA_BINDING,
    }.items():
        raw = canonical_json_bytes(schemas.get(name))
        if (len(raw), sha256_bytes(raw)) != expected:
            raise ContractError(f"{name} canonical schema binding mismatch")
        if bindings.get(name) != {
            "canonical_bytes": expected[0],
            "canonical_sha256": expected[1],
        }:
            raise ContractError(f"{name} declared schema binding mismatch")

    templates = _require_mapping(prompt.get("templates"), "templates")
    if tuple(templates) != (
        "RR_PHASE0",
        "RR_PHASE1",
        "OS_PHASE1",
        "NR_PHASE0",
        "NR_PHASE1",
    ):
        raise ContractError("prompt templates must bind exact phase order")
    diagnostic = canonical_json_bytes(frozen.get("diagnostic_only_bindings"))
    prompt_bytes = canonical_json_bytes(prompt)
    diagnostic_hashes = json.loads(diagnostic.decode("utf-8"))
    for section in ("prompt_prefix", "prompt_suffix", "prompt_combined"):
        if diagnostic_hashes[section]["sha256"].encode() in prompt_bytes:
            raise ContractError("diagnostic prompt hashes cannot be reused by production templates")
    validate_owner_selection(
        _require_mapping(
            frozen.get("budget_owner_selection_interface"), "budget owner selection interface"
        )
    )
    validate_runtime_binding(frozen["model_runtime_binding"], frozen)
    return copy.deepcopy(frozen), copy.deepcopy(prompt)


def validate_direct_plan(
    plan: Mapping[str, Any],
    contract: Mapping[str, Any],
    prompt_bundle: Mapping[str, Any],
    owner_selection: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate direct-route bindings after unchanged Runner V2 validation."""

    candidate = dict(_require_mapping(plan, "run plan"))
    selected = validate_owner_selection(owner_selection)
    frozen_selection = validate_owner_selection(
        _require_mapping(
            contract.get("budget_owner_selection_interface"),
            "contract budget owner selection interface",
        )
    )
    if canonical_json_bytes(selected) != canonical_json_bytes(frozen_selection):
        raise ContractError("owner selection differs from the frozen owner-prospective budget")
    if canonical_json_bytes(candidate.get("budget_by_arm")) != canonical_json_bytes(
        selected["budget_by_arm"]
    ):
        raise ContractError("run plan budget_by_arm differs from owner selection")
    bindings = _require_mapping(candidate.get("bindings"), "run plan bindings")
    prompt_digest = sha256_file(PROMPT_BUNDLE_PATH)
    expected_prompt_hashes = {arm: prompt_digest for arm in PHASE_SEQUENCE_BY_ARM}
    expected = {
        "model_id": contract["model_runtime_binding"]["model_sha256"],
        "provider": "local-llama-server",
        "tokenizer_revision": contract["tokenizer_binding"]["source_revision"],
        "prompt_bundle_sha256_by_arm": expected_prompt_hashes,
        "seed_schedule": SEED_SCHEDULE,
        "provider_seed_capability": "CONFIRMED",
        "model_parameters_sha256": canonical_hash(contract["sampling"]),
        "tool_policy_sha256": canonical_hash(contract["tool_policy"]),
        "generation_runtime_manifest_sha256": canonical_hash(
            contract["model_runtime_binding"]
        ),
        "credential_route_sha256": canonical_hash(contract["route_descriptor"]),
        "credential_route_status": "BOUND_OWNER_CONTROLLED",
    }
    if bindings != expected:
        raise ContractError("run plan direct-route bindings mismatch")
    if contract["seed_schedule"] != SEED_SCHEDULE:
        raise ContractError("contract seed schedule mismatch")
    if prompt_bundle.get("diagnostic_prompt_or_schema_reuse") is not False:
        raise ContractError("diagnostic prompt or schema reuse is forbidden")
    return copy.deepcopy(candidate)


def bind_runner_v2_plan(
    plan: Mapping[str, Any],
    contract: Mapping[str, Any],
    prompt_bundle: Mapping[str, Any],
    owner_selection: Mapping[str, Any],
    adapter_module: ModuleType,
) -> dict[str, Any]:
    """Run the unchanged adapter/Runner V2 validator, then route checks."""

    if not hasattr(adapter_module, "validate_plan"):
        raise ContractError("injected adapter lacks validate_plan")
    try:
        validated = adapter_module.validate_plan(dict(plan))
    except Exception as exc:
        raise ContractError(f"unchanged Runner V2 plan validation failed: {exc}") from exc
    return validate_direct_plan(validated, contract, prompt_bundle, owner_selection)


def build_completion_body(
    prompt: str, output_schema: dict[str, Any], seed: int, n_predict: int
) -> dict[str, Any]:
    if not isinstance(prompt, str) or not prompt.endswith("\n"):
        raise ContractError("rendered prompt must be UTF-8 text with a terminal newline")
    if seed not in SEED_SCHEDULE.values() or isinstance(seed, bool):
        raise ContractError("seed must be one of the three paired frozen seeds")
    _positive_number(n_predict, "n_predict", integer=True)
    schema = _require_mapping(output_schema, "output schema")
    body = {
        "prompt": prompt,
        "seed": seed,
        "cache_prompt": False,
        "temperature": 0.2,
        "top_k": 20,
        "top_p": 0.95,
        "min_p": 0.0,
        "repeat_penalty": 1.0,
        "n_predict": n_predict,
        "stream": False,
        "return_tokens": True,
        "json_schema": schema,
    }
    return body


def _validate_string_array(value: Any, label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ContractError(f"strict raw JSON {label} must be an array of strings")


def parse_phase_content(content: str, output_schema: Mapping[str, Any]) -> dict[str, Any]:
    """Parse the entire raw content once; embedded-object recovery is forbidden."""

    if not isinstance(content, str):
        raise ContractError("phase content must be strict raw JSON text")
    try:
        value = strict_json_object_from_bytes(content.encode("utf-8"), "phase content")
    except ContractError as exc:
        raise ContractError("phase content must be strict raw JSON with no prefix or suffix") from exc
    digest = sha256_bytes(canonical_json_bytes(output_schema))
    observed_fields = set(value)
    if digest == FINAL_SCHEMA_BINDING[1]:
        if observed_fields != {"kind", "program"}:
            raise ContractError("strict raw JSON final_program fields mismatch")
        if value["kind"] != "FINAL_PROGRAM":
            raise ContractError("strict raw JSON final_program kind mismatch")
        if not isinstance(value["program"], str) or not value["program"]:
            raise ContractError("strict raw JSON final_program program must be nonempty")
    elif digest == PHASE0_SCHEMA_BINDING[1]:
        fields = {
            "kind",
            "assumptions",
            "unresolved_inputs",
            "intended_analysis",
            "invariants",
            "output_contract",
        }
        if observed_fields != fields:
            raise ContractError("strict raw JSON phase0_state fields mismatch")
        if value["kind"] not in {"RR_TYPED_STATE", "NR_GENERIC_PLAN"}:
            raise ContractError("strict raw JSON phase0_state kind mismatch")
        for name in ("assumptions", "unresolved_inputs", "intended_analysis", "invariants"):
            _validate_string_array(value[name], name)
        if not isinstance(value["output_contract"], str):
            raise ContractError("strict raw JSON output_contract must be a string")
    else:
        raise ContractError("strict raw JSON output schema is not a frozen phase schema")
    return value


def validate_completion_response(
    response: Mapping[str, Any], n_predict: int, context_window_tokens: int
) -> dict[str, Any]:
    observed = dict(_require_mapping(response, "completion response"))
    if observed.get("error") not in (None, False):
        raise ContractError("completion response contains a server error")
    if not isinstance(observed.get("content"), str):
        raise ContractError("completion response content must be text")
    timings = _require_mapping(observed.get("timings"), "completion timings")
    cache_n = _nonnegative_integer(timings.get("cache_n"), "timings.cache_n")
    if cache_n != 0:
        raise ContractError("timings.cache_n must equal zero")
    prompt_n = _nonnegative_integer(timings.get("prompt_n"), "timings.prompt_n")
    predicted_n = _nonnegative_integer(
        timings.get("predicted_n"), "timings.predicted_n"
    )
    _positive_number(n_predict, "n_predict", integer=True)
    if predicted_n > n_predict:
        raise ContractError("predicted token count exceeds the frozen phase cap")
    if prompt_n + n_predict > context_window_tokens:
        raise ContractError("live prompt_n plus phase cap exceeds context window")
    if observed.get("truncated") is not False:
        raise ContractError("response truncation is forbidden")
    if observed.get("tokens_predicted") != predicted_n:
        raise ContractError("tokens_predicted differs from timings.predicted_n")
    return copy.deepcopy(observed)


def validate_no_local_execution_usage(
    *,
    tool_calls: int,
    candidate_execution_count: int,
    local_execution_wall_time_seconds: float,
) -> float:
    """Bind actual zero local candidate execution for this generation-only route.

    Local JSON serialization and state validation are generation-driver
    overhead inside the captured attempt interval; this Runner field denotes
    local tool/candidate-program execution.  Neither operation exists in this
    driver, so any nonzero event count or duration fails closed.
    """

    if isinstance(tool_calls, bool) or not isinstance(tool_calls, int) or tool_calls != 0:
        raise ContractError("local execution usage requires tool_calls to equal zero")
    if (
        isinstance(candidate_execution_count, bool)
        or not isinstance(candidate_execution_count, int)
        or candidate_execution_count != 0
    ):
        raise ContractError("local execution usage requires candidate execution count zero")
    if (
        isinstance(local_execution_wall_time_seconds, bool)
        or not isinstance(local_execution_wall_time_seconds, (int, float))
        or not math.isfinite(local_execution_wall_time_seconds)
        or local_execution_wall_time_seconds != 0.0
    ):
        raise ContractError("local execution wall time must equal actual zero")
    return 0.0


def _render_template(
    prompt_bundle: Mapping[str, Any], phase_id: str, replacements: Mapping[str, str]
) -> str:
    templates = _require_mapping(prompt_bundle.get("templates"), "prompt templates")
    template = _require_mapping(templates.get(phase_id), f"template {phase_id}")
    text = template.get("text")
    markers = template.get("markers")
    if not isinstance(text, str) or not isinstance(markers, list):
        raise ContractError(f"template {phase_id} text or markers are invalid")
    if set(markers) != set(replacements) or len(markers) != len(replacements):
        raise ContractError(f"template {phase_id} replacement markers mismatch")
    rendered = text
    for marker in markers:
        if not isinstance(marker, str) or rendered.count(marker) != 1:
            raise ContractError(f"template {phase_id} marker must occur exactly once")
        replacement = replacements[marker]
        if not isinstance(replacement, str):
            raise ContractError(f"template {phase_id} replacement must be text")
        rendered = rendered.replace(marker, replacement)
    if "{{" in rendered or "}}" in rendered or not rendered.endswith("\n"):
        raise ContractError(f"template {phase_id} contains an unreplaced marker")
    return rendered


def _render_phase0(
    prompt_bundle: Mapping[str, Any], phase_id: str, attempt: int, masked_packet: Any
) -> str:
    return _render_template(
        prompt_bundle,
        phase_id,
        {
            "{{ATTEMPT_ORDINAL}}": str(attempt),
            "{{MASKED_PACKET_JSON}}": canonical_json_bytes(masked_packet).decode("utf-8"),
        },
    )


def _render_rr_phase1(
    prompt_bundle: Mapping[str, Any],
    attempt: int,
    recovered_packet: Any,
    canonical_state: str,
    state_sha256: str,
) -> str:
    return _render_template(
        prompt_bundle,
        "RR_PHASE1",
        {
            "{{ATTEMPT_ORDINAL}}": str(attempt),
            "{{PHASE0_STATE_JSON}}": canonical_state,
            "{{PHASE0_STATE_SHA256}}": state_sha256,
            "{{RECOVERED_PACKET_JSON}}": canonical_json_bytes(recovered_packet).decode("utf-8"),
        },
    )


def _render_phase1_without_state(
    prompt_bundle: Mapping[str, Any],
    phase_id: str,
    attempt: int,
    recovered_packet: Any,
) -> str:
    """Build OS/NR phase 1 with no phase-zero parameter by construction."""

    if phase_id not in {"OS_PHASE1", "NR_PHASE1"}:
        raise ContractError("state-free phase-1 builder accepts only OS or NR")
    return _render_template(
        prompt_bundle,
        phase_id,
        {
            "{{ATTEMPT_ORDINAL}}": str(attempt),
            "{{RECOVERED_PACKET_JSON}}": canonical_json_bytes(recovered_packet).decode("utf-8"),
        },
    )


def execute_attempt(
    *,
    plan: Mapping[str, Any],
    contract: Mapping[str, Any],
    prompt_bundle: Mapping[str, Any],
    owner_selection: Mapping[str, Any],
    runtime_binding: Mapping[str, Any],
    adapter_module: ModuleType,
    client: Any,
    raw_clock: Any,
    task_id: str,
    arm_id: str,
    attempt: int,
    masked_packet: Mapping[str, Any],
    recovered_packet: Mapping[str, Any],
    run_plan_sha256: str,
    slurm_job_identity: Mapping[str, Any],
    slurm_in_job_snapshot_sha256: str,
) -> dict[str, Any]:
    """Generate one tuple while retaining every call in one adapter capture."""

    frozen, prompts = validate_packet_contract(contract, prompt_bundle)
    validate_runtime_binding(runtime_binding, frozen)
    selected = validate_owner_selection(owner_selection)
    validated_plan = bind_runner_v2_plan(
        plan, frozen, prompts, selected, adapter_module
    )
    if arm_id not in PHASE_SEQUENCE_BY_ARM:
        raise ContractError("arm_id must be RR, OS, or NR")
    if isinstance(attempt, bool) or attempt not in (1, 2, 3):
        raise ContractError("attempt must be 1, 2, or 3")
    if not hasattr(client, "complete") or not callable(client.complete):
        raise ContractError("injected client must provide complete(body)")
    if not callable(raw_clock):
        raise ContractError("injected raw clock must be callable")

    capture_clock_readings: list[int] = []

    def recorded_capture_clock() -> int:
        value = raw_clock()
        capture_clock_readings.append(value)
        return value

    try:
        capture = adapter_module.GenerationAttemptCapture(
            plan=validated_plan,
            run_plan_sha256=run_plan_sha256,
            task_id=task_id,
            arm_id=arm_id,
            attempt=attempt,
            slurm_job_identity=slurm_job_identity,
            slurm_in_job_snapshot_sha256=slurm_in_job_snapshot_sha256,
            raw_clock=recorded_capture_clock,
        )
    except Exception as exc:
        raise ContractError(f"adapter capture initialization failed: {exc}") from exc

    seed = SEED_SCHEDULE[str(attempt)]
    schemas = prompts["output_schemas"]
    caps = selected["phase_output_caps_by_arm"][arm_id]
    response_records: list[dict[str, Any]] = []
    parsed_by_phase: dict[str, dict[str, Any]] = {}

    def call_phase(phase_id: str, rendered_prompt: str) -> dict[str, Any]:
        schema_name = prompts["templates"][phase_id]["output_schema"]
        schema = schemas[schema_name]
        n_predict = caps[phase_id]
        body = build_completion_body(rendered_prompt, schema, seed, n_predict)
        try:
            raw_response = capture.call_model(
                phase_id, lambda: client.complete(copy.deepcopy(body))
            )
        except Exception as exc:
            raise ContractError(f"completion call failed for {phase_id}: {exc}") from exc
        response = validate_completion_response(
            raw_response, n_predict, selected["context_window_tokens"]
        )
        parsed = parse_phase_content(response["content"], schema)
        response_records.append(response)
        parsed_by_phase[phase_id] = parsed
        return parsed

    if arm_id == "RR":
        phase0 = call_phase(
            "RR_PHASE0", _render_phase0(prompts, "RR_PHASE0", attempt, masked_packet)
        )
        if phase0["kind"] != "RR_TYPED_STATE":
            raise ContractError("RR phase 0 must return kind RR_TYPED_STATE")
        state_bytes = canonical_json_bytes(phase0)
        call_phase(
            "RR_PHASE1",
            _render_rr_phase1(
                prompts,
                attempt,
                recovered_packet,
                state_bytes.decode("utf-8"),
                sha256_bytes(state_bytes),
            ),
        )
    elif arm_id == "OS":
        call_phase(
            "OS_PHASE1",
            _render_phase1_without_state(
                prompts, "OS_PHASE1", attempt, recovered_packet
            ),
        )
    else:
        phase0 = call_phase(
            "NR_PHASE0", _render_phase0(prompts, "NR_PHASE0", attempt, masked_packet)
        )
        if phase0["kind"] != "NR_GENERIC_PLAN":
            raise ContractError("NR phase 0 must return kind NR_GENERIC_PLAN")
        call_phase(
            "NR_PHASE1",
            _render_phase1_without_state(
                prompts, "NR_PHASE1", attempt, recovered_packet
            ),
        )

    final_phase = PHASE_SEQUENCE_BY_ARM[arm_id][-1]
    final = parsed_by_phase[final_phase]
    if final.get("kind") != "FINAL_PROGRAM":
        raise ContractError("final phase did not return a final program")
    input_tokens = sum(record["timings"]["prompt_n"] for record in response_records)
    output_tokens = sum(record["timings"]["predicted_n"] for record in response_records)
    budget = selected["budget_by_arm"][arm_id]
    if input_tokens > budget["total_input_token_cap"]:
        raise ContractError("cumulative input tokens exceed the equal acceptance budget")
    if output_tokens > budget["total_output_token_cap"]:
        raise ContractError("cumulative output tokens exceed the equal acceptance budget")
    if len(capture_clock_readings) != 2:
        raise ContractError("adapter capture did not expose exactly two raw clock boundaries")
    start_ns, end_ns = capture_clock_readings
    if (
        isinstance(start_ns, bool)
        or isinstance(end_ns, bool)
        or not isinstance(start_ns, int)
        or not isinstance(end_ns, int)
        or start_ns < 0
        or end_ns < start_ns
    ):
        raise ContractError("adapter capture raw clock boundaries are invalid")
    elapsed_ns = end_ns - start_ns
    wall_seconds = elapsed_ns / 1_000_000_000
    if wall_seconds > budget["wall_time_seconds_cap"]:
        raise ContractError("actual capture wall_time_seconds exceeds the matched wall cap")
    local_execution_wall_time_seconds = validate_no_local_execution_usage(
        tool_calls=0,
        candidate_execution_count=0,
        local_execution_wall_time_seconds=0.0,
    )
    raw_outputs = [
        {"phase_id": phase, "content": response_records[index]["content"]}
        for index, phase in enumerate(PHASE_SEQUENCE_BY_ARM[arm_id])
    ]
    base_record = {
        "task_id": task_id,
        "arm_id": arm_id,
        "attempt": attempt,
        "seed": seed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": 0,
        "wall_time_seconds": wall_seconds,
        "local_execution_wall_time_seconds": local_execution_wall_time_seconds,
        "billed_cost_usd": None,
        "failure": None,
        "raw_output_sha256": canonical_hash(raw_outputs),
        "candidate_program_sha256": sha256_bytes(final["program"].encode("utf-8")),
    }
    try:
        receipt = capture.finish(base_record)
    except Exception as exc:
        raise ContractError(f"adapter capture finalization failed: {exc}") from exc
    if receipt.get("monotonic_elapsed_ns") != str(elapsed_ns):
        raise ContractError("adapter receipt elapsed time differs from recorded raw clock interval")
    if receipt["base_candidate_record"].get("wall_time_seconds") != wall_seconds:
        raise ContractError("adapter receipt wall time differs from recorded raw clock interval")
    return receipt


class LoopbackCompletionClient:
    """Minimal no-secret client for one already-bound literal loopback server."""

    def __init__(self, base_url: str = "http://127.0.0.1:8080") -> None:
        if base_url != "http://127.0.0.1:8080":
            raise ContractError("completion client permits only http://127.0.0.1:8080")

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        payload = canonical_json_bytes(body)
        connection = http.client.HTTPConnection("127.0.0.1", 8080, timeout=1800.0)
        try:
            connection.request(
                "POST",
                "/completion",
                body=payload,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            raw = response.read()
        finally:
            connection.close()
        if response.status != 200:
            raise ContractError(f"loopback completion returned HTTP status {response.status}")
        return strict_json_object_from_bytes(raw, "loopback completion response")


def load_adapter_module() -> ModuleType:
    if sha256_file(ADAPTER_PATH) != ADAPTER_SHA256:
        raise ContractError("generation adapter SHA-256 drift")
    spec = importlib.util.spec_from_file_location(
        "orion_p1_generation_adapter_for_direct_route", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise ContractError("generation adapter cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_new_canonical_json_with_identity(
    path: Path | str, value: Any
) -> tuple[str, tuple[int, int]]:
    """Create one output with O_EXCL/no-follow and verify bytes and identity."""

    candidate = Path(path)
    if not candidate.is_absolute():
        raise ContractError("output destination must be absolute")
    _ensure_output_parent_has_no_symlink(candidate, "output destination")
    payload = canonical_json_bytes(value) + b"\n"
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(candidate, flags, 0o600)
    except FileExistsError as exc:
        raise ContractError(f"output destination already exists: {candidate}") from exc
    except OSError as exc:
        raise ContractError(f"output destination cannot be created: {candidate}") from exc
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise ContractError(f"output write made no progress: {candidate}")
            view = view[written:]
        os.fsync(fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ContractError(f"output destination is not a regular file: {candidate}")
        os.lseek(fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        observed = b"".join(chunks)
        if observed != payload:
            raise ContractError(f"output byte/hash verification failed: {candidate}")
        path_info = candidate.lstat()
        identity = (info.st_dev, info.st_ino)
        if not stat.S_ISREG(path_info.st_mode) or (
            path_info.st_dev,
            path_info.st_ino,
        ) != identity:
            raise ContractError(f"output destination identity changed: {candidate}")
        return sha256_bytes(observed), identity
    except Exception as exc:
        try:
            info = os.fstat(fd)
            path_info = candidate.lstat()
            if stat.S_ISREG(path_info.st_mode) and (
                path_info.st_dev,
                path_info.st_ino,
            ) == (info.st_dev, info.st_ino):
                candidate.unlink()
        except OSError:
            pass
        if isinstance(exc, ContractError):
            raise
        raise ContractError(f"output write or verification failed: {candidate}") from exc
    finally:
        os.close(fd)


def write_new_canonical_json(path: Path | str, value: Any) -> str:
    digest, _ = _write_new_canonical_json_with_identity(path, value)
    return digest


def _rollback_unchanged_output(
    path: Path | str, expected_sha256: str, expected_identity: tuple[int, int]
) -> bool:
    """Remove only a process-created regular output that remains unchanged."""

    candidate = Path(path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(candidate, flags)
    except OSError:
        return False
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or (
            info.st_dev,
            info.st_ino,
        ) != expected_identity:
            return False
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        if sha256_bytes(b"".join(chunks)) != expected_sha256:
            return False
        path_info = candidate.lstat()
        if not stat.S_ISREG(path_info.st_mode) or (
            path_info.st_dev,
            path_info.st_ino,
        ) != expected_identity:
            return False
        candidate.unlink()
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def _ensure_output_parent_has_no_symlink(path: Path, label: str) -> None:
    current = path.parent
    while True:
        try:
            info = current.lstat()
        except OSError as exc:
            raise ContractError(f"{label} parent cannot be inspected: {current}") from exc
        if stat.S_ISLNK(info.st_mode):
            raise ContractError(f"{label} parent contains a symlink component: {current}")
        if not stat.S_ISDIR(info.st_mode):
            raise ContractError(f"{label} parent is not a directory: {current}")
        if current.parent == current:
            break
        current = current.parent


def validate_cli_paths(
    inputs: Mapping[str, Path],
    outputs: Mapping[str, Path],
    upstream_paths: Mapping[str, Path],
) -> None:
    """Reject every lexical, resolved, case-fold, symlink, or inode alias."""

    all_paths: dict[str, Path] = {}
    for group_name, group in (
        ("input", inputs),
        ("output", outputs),
        ("upstream", upstream_paths),
    ):
        for label, path in group.items():
            candidate = Path(path)
            composite = f"{group_name} {label}"
            if composite in all_paths:
                raise ContractError(f"duplicate CLI path label: {composite}")
            if not candidate.is_absolute():
                raise ContractError(f"{composite} must be absolute")
            all_paths[composite] = candidate

    lexical: dict[str, Path] = {}
    resolved: dict[str, Path] = {}
    lexical_casefold: dict[str, str] = {}
    resolved_casefold: dict[str, str] = {}
    identities: dict[str, tuple[int, int]] = {}
    lstat_info: dict[str, os.stat_result] = {}
    for label, path in all_paths.items():
        lexical[label] = Path(os.path.normpath(os.fspath(path)))
        resolved[label] = path.resolve(strict=False)
        lexical_casefold[label] = os.fspath(lexical[label]).casefold()
        resolved_casefold[label] = os.fspath(resolved[label]).casefold()
        try:
            link_info = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ContractError(f"{label} cannot be inspected: {path}") from exc
        lstat_info[label] = link_info
        try:
            info = path.stat()
        except OSError as exc:
            raise ContractError(f"{label} target cannot be inspected: {path}") from exc
        identities[label] = (info.st_dev, info.st_ino)

    labels = list(all_paths)
    for left_index, left in enumerate(labels):
        for right in labels[left_index + 1 :]:
            if lexical[left] == lexical[right]:
                raise ContractError(f"CLI paths alias lexically: {left} and {right}")
            if resolved[left] == resolved[right]:
                raise ContractError(f"CLI paths alias after resolution: {left} and {right}")
            if lexical_casefold[left] == lexical_casefold[right]:
                raise ContractError(f"CLI paths alias after lexical case-fold: {left} and {right}")
            if resolved_casefold[left] == resolved_casefold[right]:
                raise ContractError(f"CLI paths alias after resolved case-fold: {left} and {right}")
            if (
                left in identities
                and right in identities
                and identities[left] == identities[right]
            ):
                raise ContractError(f"CLI paths alias by device/inode: {left} and {right}")

    output_labels = {f"output {label}" for label in outputs}
    for label, path in all_paths.items():
        if label in output_labels:
            _ensure_output_parent_has_no_symlink(path, label)
            if label in lstat_info or path.is_symlink():
                raise ContractError(f"output destination already exists: {label}: {path}")
            continue
        if label not in lstat_info:
            raise ContractError(f"{label} does not exist: {path}")
        if stat.S_ISLNK(lstat_info[label].st_mode):
            raise ContractError(f"{label} is a symlink and is forbidden: {path}")
        if not stat.S_ISREG(lstat_info[label].st_mode):
            raise ContractError(f"{label} is not a regular file: {path}")


def _static_upstream_paths() -> dict[str, Path]:
    result = {
        "direct route driver": DRIVER_PATH,
        "direct route contract": CONTRACT_PATH,
        "direct route prompt bundle": PROMPT_BUNDLE_PATH,
    }
    for index, relative in enumerate(STATIC_UPSTREAM_RELATIVE_PATHS, 1):
        result[f"frozen dependency {index:02d}"] = REPO_ROOT / relative
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one frozen direct-route generation attempt against loopback"
    )
    parser.add_argument("--run-plan", type=Path, required=True)
    parser.add_argument("--owner-selection", type=Path, required=True)
    parser.add_argument("--runtime-binding", type=Path, required=True)
    parser.add_argument("--masked-packet", type=Path, required=True)
    parser.add_argument("--recovered-packet", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--arm-id", choices=("RR", "OS", "NR"), required=True)
    parser.add_argument("--attempt", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--run-plan-sha256", required=True)
    parser.add_argument("--slurm-job-identity", type=Path, required=True)
    parser.add_argument("--slurm-in-job-snapshot-sha256", required=True)
    parser.add_argument(
        "--base-url", choices=("http://127.0.0.1:8080",), default="http://127.0.0.1:8080"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    validate_cli_paths(
        {
            "run plan": args.run_plan,
            "owner selection": args.owner_selection,
            "runtime binding": args.runtime_binding,
            "masked packet": args.masked_packet,
            "recovered packet": args.recovered_packet,
            "SLURM job identity": args.slurm_job_identity,
        },
        {"attempt receipt": args.output},
        _static_upstream_paths(),
    )
    plan = strict_json_object_from_file(args.run_plan, "run plan")
    if sha256_file(args.run_plan) != args.run_plan_sha256:
        raise ContractError("run-plan exact-byte SHA-256 mismatch")
    contract = strict_json_object_from_file(CONTRACT_PATH, "direct-route contract")
    prompts = strict_json_object_from_file(PROMPT_BUNDLE_PATH, "prompt bundle")
    owner = strict_json_object_from_file(args.owner_selection, "owner selection")
    runtime = strict_json_object_from_file(args.runtime_binding, "runtime binding")
    masked = strict_json_object_from_file(args.masked_packet, "masked packet")
    recovered = strict_json_object_from_file(args.recovered_packet, "recovered packet")
    job_identity = strict_json_object_from_file(
        args.slurm_job_identity, "SLURM job identity"
    )
    adapter = load_adapter_module()
    receipt = execute_attempt(
        plan=plan,
        contract=contract,
        prompt_bundle=prompts,
        owner_selection=owner,
        runtime_binding=runtime,
        adapter_module=adapter,
        client=LoopbackCompletionClient(args.base_url),
        raw_clock=adapter.raw_monotonic_ns,
        task_id=args.task_id,
        arm_id=args.arm_id,
        attempt=args.attempt,
        masked_packet=masked,
        recovered_packet=recovered,
        run_plan_sha256=args.run_plan_sha256,
        slurm_job_identity=job_identity,
        slurm_in_job_snapshot_sha256=args.slurm_in_job_snapshot_sha256,
    )
    write_new_canonical_json(args.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
