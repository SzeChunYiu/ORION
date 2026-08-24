#!/usr/bin/env python3
"""Outcome-blind adapter primitives for the blocked Codex CLI SAB route."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when an input cannot satisfy the frozen route contract."""


_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)
_CAP_FIELDS = (
    "total_input_token_cap",
    "total_output_token_cap",
    "tool_call_cap",
    "wall_time_seconds_cap",
    "local_execution_seconds_cap",
    "final_candidates_per_attempt",
)
_NON_TOOL_ITEM_TYPES = {"agent_message", "reasoning", "todo_list"}
_TOOL_ITEM_TYPES = {
    "collab_tool_call",
    "command_execution",
    "dynamic_tool_call",
    "file_change",
    "mcp_tool_call",
    "web_search",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the deliberately small JSON-Schema subset frozen in the bundle."""

    expected_type = schema.get("type")
    if expected_type == "object":
        _require(isinstance(value, dict), f"schema mismatch at {path}: expected object")
        required = schema.get("required", [])
        _require(isinstance(required, list), f"schema invalid at {path}: required")
        missing = [key for key in required if key not in value]
        _require(not missing, f"schema mismatch at {path}: missing {missing}")
        properties = schema.get("properties", {})
        _require(isinstance(properties, dict), f"schema invalid at {path}: properties")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            _require(not extra, f"schema mismatch at {path}: extra {extra}")
        for key, child in properties.items():
            if key in value:
                _require(isinstance(child, dict), f"schema invalid at {path}.{key}")
                _validate_schema(value[key], child, f"{path}.{key}")
    elif expected_type == "array":
        _require(isinstance(value, list), f"schema mismatch at {path}: expected array")
        child = schema.get("items")
        _require(isinstance(child, dict), f"schema invalid at {path}: items")
        for index, item in enumerate(value):
            _validate_schema(item, child, f"{path}[{index}]")
    elif expected_type == "string":
        _require(isinstance(value, str), f"schema mismatch at {path}: expected string")
        if "minLength" in schema:
            _require(
                len(value) >= schema["minLength"],
                f"schema mismatch at {path}: minLength",
            )
    elif expected_type == "integer":
        _require(
            isinstance(value, int) and not isinstance(value, bool),
            f"schema mismatch at {path}: expected integer",
        )
    elif expected_type == "number":
        _require(_is_number(value), f"schema mismatch at {path}: expected number")
    elif expected_type == "boolean":
        _require(isinstance(value, bool), f"schema mismatch at {path}: expected boolean")
    elif expected_type == "null":
        _require(value is None, f"schema mismatch at {path}: expected null")
    elif expected_type is not None:
        raise ContractError(f"schema invalid at {path}: unsupported type {expected_type!r}")

    if "const" in schema:
        _require(value == schema["const"], f"schema mismatch at {path}: const")
    if "enum" in schema:
        enum = schema["enum"]
        _require(isinstance(enum, list), f"schema invalid at {path}: enum")
        _require(value in enum, f"schema mismatch at {path}: enum")


def _validate_caps(caps: dict[str, Any]) -> None:
    _require(isinstance(caps, dict), "caps must be an object")
    _require(set(caps) == set(_CAP_FIELDS), "caps fields do not match the frozen contract")
    for field in _CAP_FIELDS:
        value = caps[field]
        _require(_is_number(value), f"{field} must be numeric")
        _require(math.isfinite(float(value)) and value > 0, f"{field} must be positive")
    for field in (
        "total_input_token_cap",
        "total_output_token_cap",
        "tool_call_cap",
        "final_candidates_per_attempt",
    ):
        _require(isinstance(caps[field], int), f"{field} must be an integer")
    _require(
        caps["final_candidates_per_attempt"] == 1,
        "caps must allow exactly one final candidate per attempt",
    )


def _apply_caps(*, input_tokens: int, output_tokens: int, tool_calls: int, wall_time: float, caps: dict[str, Any]) -> None:
    _validate_caps(caps)
    checks = (
        (input_tokens, caps["total_input_token_cap"], "total_input_token_cap"),
        (output_tokens, caps["total_output_token_cap"], "total_output_token_cap"),
        (tool_calls, caps["tool_call_cap"], "tool_call_cap"),
        (wall_time, caps["wall_time_seconds_cap"], "wall_time_seconds_cap"),
    )
    for observed, limit, label in checks:
        _require(observed <= limit, f"{label} exceeded: observed={observed} cap={limit}")


def validate_prompt_bundle(bundle: dict[str, Any]) -> None:
    _require(isinstance(bundle, dict), "prompt bundle must be an object")
    _require(
        bundle.get("schema_version") == "orion.p1.scienceagentbench.codex-prompt-bundle.v1",
        "prompt bundle schema_version mismatch",
    )
    _require(bundle.get("outcomes_opened") is False, "prompt bundle outcomes_opened must be false")
    _require(bundle.get("scientific_authority_delta") == "NONE", "prompt bundle authority delta")
    render = bundle.get("render_contract")
    _require(isinstance(render, dict), "prompt bundle render_contract missing")
    _require(render.get("encoding") == "UTF-8", "prompt encoding must be UTF-8")
    _require(render.get("line_endings") == "LF", "prompt line endings must be LF")
    _require(render.get("terminal_newline") is True, "prompt terminal newline required")
    schemas = bundle.get("output_schemas")
    _require(isinstance(schemas, dict) and set(schemas) == {"phase0_state", "final_program"}, "output schemas mismatch")
    templates = bundle.get("templates")
    _require(
        isinstance(templates, dict)
        and set(templates) == {"RR_PHASE0", "RR_PHASE1", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1"},
        "prompt templates mismatch",
    )
    for name, spec in templates.items():
        _require(isinstance(spec, dict), f"template {name} must be an object")
        _require(spec.get("output_schema") in schemas, f"template {name} output schema")
        markers = spec.get("markers")
        text = spec.get("text")
        _require(isinstance(markers, list) and len(markers) == len(set(markers)), f"template {name} markers")
        _require(isinstance(text, str) and text.endswith("\n"), f"template {name} terminal newline")
        _require("\r" not in text, f"template {name} contains non-LF line ending")
        found = re.findall(r"{{[A-Z0-9_]+}}", text)
        _require(found == markers, f"template {name} declared marker order/count mismatch")
        _require(all(text.count(marker) == 1 for marker in markers), f"template {name} marker must occur exactly once")


def _fixture_is_synthetic(fixture: dict[str, Any]) -> None:
    _require(isinstance(fixture, dict), "fixture must be synthetic object")
    _require(fixture.get("authority") == "SYNTHETIC_NONBENCHMARK_ONLY", "fixture is not synthetic nonbenchmark material")
    _require(fixture.get("official_task_content") is False, "fixture must remain synthetic with no official task content")
    _require(fixture.get("outcomes_opened") is False, "fixture must remain synthetic and outcome blind")
    _require(fixture.get("scientific_authority_delta") == "NONE", "fixture scientific authority delta")
    forbidden_fragments = ("evaluator", "gold", "rubric", "score", "feedback", "outcome")

    def visit(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = key.lower()
                if key not in {"outcomes_opened"} and any(word in lowered for word in forbidden_fragments):
                    raise ContractError(f"forbidden fixture field at {'.'.join((*path, key))}")
                visit(child, (*path, key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, (*path, str(index)))

    visit(fixture)


def render_template(
    bundle: dict[str, Any],
    template_name: str,
    fixture: dict[str, Any],
    *,
    attempt_ordinal: int,
    phase0_state_sha256: str | None = None,
) -> bytes:
    validate_prompt_bundle(bundle)
    _fixture_is_synthetic(fixture)
    _require(
        isinstance(attempt_ordinal, int) and not isinstance(attempt_ordinal, bool) and attempt_ordinal > 0,
        "attempt ordinal must be a positive integer",
    )
    _require(template_name in bundle["templates"], f"unknown template {template_name}")
    spec = bundle["templates"][template_name]
    replacements = {
        "{{ATTEMPT_ORDINAL}}": _canonical_json(attempt_ordinal),
        "{{MASKED_PACKET_JSON}}": _canonical_json(fixture.get("masked_packet")),
        "{{RECOVERED_PACKET_JSON}}": _canonical_json(fixture.get("recovered_packet")),
    }
    if "{{PHASE0_STATE_SHA256}}" in spec["markers"]:
        _require(
            isinstance(phase0_state_sha256, str) and _SHA256_RE.fullmatch(phase0_state_sha256),
            "phase-0 state SHA-256 is required",
        )
        replacements["{{PHASE0_STATE_SHA256}}"] = phase0_state_sha256
    text = spec["text"]
    for marker in spec["markers"]:
        _require(marker in replacements, f"no renderer for declared marker {marker}")
        text = text.replace(marker, replacements[marker])
    _require("{{" not in text and "}}" not in text, "unreplaced prompt marker")
    _require(text.endswith("\n") and "\r" not in text, "rendered prompt byte contract")
    return text.encode("utf-8")


def parse_jsonl(
    raw: bytes,
    *,
    phase: str,
    schema: dict[str, Any],
    wall_time_seconds: float,
    caps: dict[str, Any],
    billed_cost_usd: float | None = None,
) -> dict[str, Any]:
    _require(phase in {"RR_PHASE0", "RR_PHASE1", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1"}, "unknown phase")
    _require(isinstance(raw, bytes) and raw, "raw JSONL must be nonempty bytes")
    _require(billed_cost_usd is None, "billed cost must remain null when JSONL does not emit it")
    _require(_is_number(wall_time_seconds), "wall_time must be numeric")
    _require(math.isfinite(float(wall_time_seconds)) and wall_time_seconds >= 0, "wall_time must be finite and nonnegative")

    rows: list[dict[str, Any]] = []
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("JSONL must be UTF-8") from exc
    _require(decoded.endswith("\n"), "JSONL must end with LF")
    for line_number, line in enumerate(decoded.splitlines(), start=1):
        _require(bool(line), f"blank JSONL line {line_number}")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid JSONL line {line_number}") from exc
        _require(isinstance(row, dict), f"JSONL line {line_number} must be an object")
        rows.append(row)

    thread_ids: list[str] = []
    terminal_usage: list[dict[str, Any]] = []
    agent_messages: list[str] = []
    tool_item_ids: set[str] = set()
    for row in rows:
        event_type = row.get("type")
        _require(isinstance(event_type, str), "JSONL event type missing")
        if event_type == "thread.started":
            thread_id = row.get("thread_id")
            _require(isinstance(thread_id, str) and thread_id, "thread.started thread_id missing")
            thread_ids.append(thread_id)
        elif event_type == "turn.completed":
            usage = row.get("usage")
            _require(isinstance(usage, dict), "terminal usage missing")
            terminal_usage.append(usage)
        elif event_type in {"turn.failed", "error"}:
            raise ContractError(f"Codex turn failed via {event_type}")
        elif event_type in {"turn.started", "item.started", "item.updated", "item.completed"}:
            if event_type.startswith("item."):
                item = row.get("item")
                _require(isinstance(item, dict), "item event payload missing")
                item_type = item.get("type")
                _require(isinstance(item_type, str), "item type missing")
                if item_type == "error" or item_type not in _NON_TOOL_ITEM_TYPES | _TOOL_ITEM_TYPES:
                    raise ContractError(f"unsupported or failed item type {item_type!r}")
                if event_type == "item.completed" and item_type == "agent_message":
                    text = item.get("text")
                    _require(isinstance(text, str) and text, "agent message text missing")
                    agent_messages.append(text)
                if event_type == "item.completed" and item_type in _TOOL_ITEM_TYPES:
                    failed_statuses = {
                        "cancelled",
                        "denied",
                        "error",
                        "failed",
                        "interrupted",
                        "rejected",
                    }
                    if item.get("status") in failed_statuses or (
                        isinstance(item.get("exit_code"), int)
                        and item["exit_code"] != 0
                    ):
                        raise ContractError(f"tool item failed: {item_type}")
                    item_id = item.get("id")
                    _require(isinstance(item_id, str) and item_id, "tool item id missing")
                    tool_item_ids.add(item_id)
        else:
            raise ContractError(f"unsupported JSONL event type {event_type!r}")

    _require(len(thread_ids) == 1, "exactly one thread.started event required")
    _require(len(terminal_usage) == 1, "exactly one terminal usage event required")
    _require(len(agent_messages) == 1, "exactly one completed agent message required")
    usage = terminal_usage[0]
    for field in _USAGE_FIELDS:
        value = usage.get(field)
        _require(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0,
            f"{field} must be a nonnegative integer",
        )

    message = agent_messages[0]
    try:
        output = json.loads(message)
    except json.JSONDecodeError as exc:
        raise ContractError("model output schema violation: not JSON") from exc
    _validate_schema(output, schema)
    tool_calls = len(tool_item_ids)
    _apply_caps(
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        tool_calls=tool_calls,
        wall_time=float(wall_time_seconds),
        caps=caps,
    )
    return {
        "phase": phase,
        "thread_id": thread_ids[0],
        "output_kind": output.get("kind") if isinstance(output, dict) else None,
        "model_output_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
        "model_output_bytes": len(message.encode("utf-8")),
        "raw_jsonl_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_jsonl_bytes": len(raw),
        **{field: usage[field] for field in _USAGE_FIELDS},
        "tool_calls": tool_calls,
        "wall_time_seconds": float(wall_time_seconds),
        "billed_cost_usd": None,
        "billed_cost_status": "CANNOT_CHECK_NOT_EMITTED",
    }


def aggregate_arm_attempt(
    arm: str,
    attempt: int,
    phases: list[dict[str, Any]],
    caps: dict[str, Any],
) -> dict[str, Any]:
    _require(arm in {"RR", "OS", "NR"}, "unknown arm")
    _require(isinstance(attempt, int) and not isinstance(attempt, bool) and attempt > 0, "attempt ordinal invalid")
    _require(isinstance(phases, list) and all(isinstance(row, dict) for row in phases), "phase receipts invalid")
    expected = {
        "RR": ["RR_PHASE0", "RR_PHASE1"],
        "OS": ["OS_PHASE1"],
        "NR": ["NR_PHASE0", "NR_PHASE1"],
    }[arm]
    observed = [row.get("phase") for row in phases]
    _require(observed == expected, f"{arm} phase sequence must be exactly {expected}")
    if arm == "RR":
        _require(phases[0].get("thread_id") == phases[1].get("thread_id"), "RR phases must use the same thread")
    if arm == "NR":
        _require(phases[0].get("thread_id") != phases[1].get("thread_id"), "NR phases must use distinct threads")
    expected_kinds = {
        "RR_PHASE0": "RR_TYPED_STATE",
        "NR_PHASE0": "NR_GENERIC_PLAN",
        "RR_PHASE1": "FINAL_PROGRAM",
        "OS_PHASE1": "FINAL_PROGRAM",
        "NR_PHASE1": "FINAL_PROGRAM",
    }
    for row in phases:
        phase = row["phase"]
        _require(row.get("output_kind") == expected_kinds[phase], f"{phase} output kind mismatch")
        _require(row.get("billed_cost_usd") is None, "billed cost must remain null")

    totals = {field: sum(row[field] for row in phases) for field in _USAGE_FIELDS}
    tool_calls = sum(row["tool_calls"] for row in phases)
    wall_time = sum(row["wall_time_seconds"] for row in phases)
    _apply_caps(
        input_tokens=totals["input_tokens"],
        output_tokens=totals["output_tokens"],
        tool_calls=tool_calls,
        wall_time=wall_time,
        caps=caps,
    )
    return {
        "arm_id": arm,
        "attempt": attempt,
        "seed": None,
        "seed_status": "UNSEEDED_CANNOT_CHECK",
        "phase_receipts": phases,
        **totals,
        "tool_calls": tool_calls,
        "wall_time_seconds": wall_time,
        "billed_cost_usd": None,
        "billed_cost_status": "CANNOT_CHECK_NOT_EMITTED",
        "final_candidates": 1,
        "local_execution_seconds": 0.0,
        "local_execution_status": "NOT_RUN_SYNTHETIC_GENERATION_TRANSPORT_ONLY",
        "transport_status": "PASS",
        "runner_status": "CANNOT_CHECK_BILLED_COST",
    }


def validate_run_plan_candidate(plan: dict[str, Any]) -> None:
    _require(isinstance(plan, dict), "run plan candidate must be an object")
    _require(
        plan.get("schema_version") == "orion.p1.scienceagentbench.codex-run-plan-candidate.v1",
        "run plan schema_version mismatch",
    )
    _require(plan.get("runner_admissible") is False, "runner_admissible must remain false")
    _require(
        plan.get("status") == "BLOCKED_CANNOT_CHECK_IMMUTABLE_MODEL_TOKENIZER_SEED_AND_BILLED_COST",
        "blocked status mismatch",
    )
    _require(plan.get("outcomes_opened") is False, "outcomes_opened must remain false")
    _require(plan.get("scientific_authority_delta") == "NONE", "scientific authority delta")
    route = plan.get("client_route")
    _require(isinstance(route, dict), "client route missing")
    _require(route.get("package") == "@openai/codex" and route.get("version") == "0.147.0", "client package/version mismatch")
    _require(route.get("provider_id") == "openai", "provider route mismatch")
    _require(route.get("model_slug") == "gpt-5.6-sol", "model slug mismatch")
    _require(str(route.get("model_snapshot", "")).startswith("CANNOT_CHECK"), "model snapshot must remain CANNOT_CHECK")
    _require(str(route.get("tokenizer_revision", "")).startswith("CANNOT_CHECK"), "tokenizer must remain CANNOT_CHECK")
    _require(str(route.get("provider_seed_capability", "")).startswith("CANNOT_CHECK"), "seed capability must remain CANNOT_CHECK")
    _require(route.get("approval_policy") == "never" and route.get("sandbox") == "read-only", "sandbox/approval mismatch")
    schedule = plan.get("attempt_schedule")
    _require(isinstance(schedule, dict), "attempt schedule missing")
    _require(schedule.get("attempt_ordinals") == [1, 2, 3], "attempt schedule must be exactly 1,2,3")
    _require(schedule.get("attempt_ordinals_are_seeds") is False, "attempt ordinals cannot be seeds")
    _require(str(schedule.get("seed_status", "")).startswith("UNSEEDED_CANNOT_CHECK"), "seed schedule must remain unseeded")
    budgets = plan.get("matched_acceptance_budget_by_arm")
    _require(isinstance(budgets, dict) and set(budgets) == {"RR", "OS", "NR"}, "matched budgets missing")
    for caps in budgets.values():
        _validate_caps(caps)
    _require(budgets["RR"] == budgets["OS"] == budgets["NR"], "matched acceptance budgets differ")
    _require(plan.get("cap_semantics", {}).get("provider_side_enforcement_claimed") is False, "provider-side enforcement cannot be claimed")
    usage = plan.get("usage_and_cost")
    _require(isinstance(usage, dict), "usage and cost contract missing")
    _require(usage.get("billed_cost_usd") is None, "billed cost must remain null")
    _require(str(usage.get("billed_cost_status", "")).startswith("CANNOT_CHECK"), "billed cost status must remain CANNOT_CHECK")
    blockers = plan.get("blockers")
    _require(isinstance(blockers, list), "blockers missing")
    _require({row.get("field") for row in blockers if isinstance(row, dict)} == {"model_id", "tokenizer_revision", "seed_schedule", "billed_cost_usd"}, "mandatory blocker set mismatch")


def _absolute_path(path: Path, label: str) -> str:
    _require(isinstance(path, Path) and path.is_absolute(), f"{label} must be an absolute Path")
    return str(path)


def build_phase_argv(
    *,
    phase: str,
    codex_home: Path,
    cwd: Path,
    prompt_path: Path,
    schema_path: Path,
    last_message_path: Path,
    thread_id: str | None = None,
) -> list[str]:
    _require(phase in {"RR_PHASE0", "RR_PHASE1", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1"}, "unknown phase")
    clean_home = _absolute_path(codex_home, "codex_home")
    working_dir = _absolute_path(cwd, "cwd")
    prompt = _absolute_path(prompt_path, "prompt_path")
    schema = _absolute_path(schema_path, "schema_path")
    last_message = _absolute_path(last_message_path, "last_message_path")
    common = [
        "--ignore-user-config",
        "--strict-config",
        "--ignore-rules",
        "--disable",
        "plugins",
        "--disable",
        "remote_plugin",
        "--disable",
        "skill_search",
        "--json",
        "--model",
        "gpt-5.6-sol",
        "--output-schema",
        schema,
        "--output-last-message",
        last_message,
        "-c",
        'model_provider="openai"',
        "-c",
        'model_reasoning_effort="low"',
        "-c",
        'model_reasoning_summary="none"',
        "-c",
        'model_verbosity="low"',
        "-c",
        'service_tier="default"',
        "-c",
        'approval_policy="never"',
        "-c",
        'sandbox_mode="read-only"',
    ]
    if phase == "RR_PHASE1":
        _require(isinstance(thread_id, str) and bool(thread_id), "RR_PHASE1 requires a thread_id")
        command = ["env", f"CODEX_HOME={clean_home}", "codex", "exec", "resume", *common, thread_id]
    else:
        _require(thread_id is None, f"{phase} must start a fresh thread")
        command = [
            "env",
            f"CODEX_HOME={clean_home}",
            "codex",
            "exec",
            *common,
            "--sandbox",
            "read-only",
            "--cd",
            working_dir,
        ]
    return [*command, "-"]
