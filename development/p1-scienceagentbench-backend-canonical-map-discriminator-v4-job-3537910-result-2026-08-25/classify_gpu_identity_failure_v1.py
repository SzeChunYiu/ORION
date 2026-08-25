#!/usr/bin/env python3
"""Deterministic offline classification of job 3537910's GPU failure.

This program reads only the frozen public execution core and the body-free
result artifacts beside this file.  It does not import or execute the core,
open protected data, submit a job, or invoke generation.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
SOURCE_RELATIVE_PATH = (
    "../p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25/"
    "backend_canonical_map_discriminator_v1.py"
)
SOURCE_PATH = ROOT / SOURCE_RELATIVE_PATH
JOB_RECEIPT_NAME = "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json"
JOB_RECEIPT_PATH = ROOT / JOB_RECEIPT_NAME
TERMINAL_NAME = "slurm-3537910.err"
TERMINAL_PATH = ROOT / TERMINAL_NAME
CLASSIFICATION_NAME = "OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json"
CLASSIFICATION_PATH = ROOT / CLASSIFICATION_NAME

EXPECTED_SOURCE_SHA256 = "59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219"
EXPECTED_SOURCE_BYTES = 59609
EXPECTED_JOB_RECEIPT_SHA256 = "cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a"
EXPECTED_JOB_RECEIPT_BYTES = 1464
EXPECTED_TERMINAL_SHA256 = "27c5fda40d52f578c90f18d155ae90d3a89fe06049a652b1150a609fe6380dfc"
EXPECTED_TERMINAL_BYTES = 169
OBSERVED_DETAIL_SHA256 = "a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4"
EMPTY_STDERR_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
PASS_TERMINAL = "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_PASS"

EXPECTED_STATIC_DETAILS = (
    "SLURM_JOB_ID is not canonical",
    "CUDA_VISIBLE_DEVICES is not singular",
    "nvidia-smi could not be executed exactly",
    "nvidia-smi stdout is not UTF-8",
    "nvidia-smi stdout line framing differs",
    "visible GPU row count differs from one",
    "visible GPU row is not canonical",
    "visible GPU is not exactly NVIDIA A40",
)
EXPECTED_DYNAMIC_PREFIXES = (
    "nvidia-smi failed stderr_sha256=",
    "nvidia-smi emitted stderr_sha256=",
)


class ClassificationError(RuntimeError):
    """The frozen evidence does not support the requested classification."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def outer_detail_sha256(detail: str) -> str:
    """Reproduce V4's retained hash of ``GateError:<detail>`` exactly."""

    return sha256_bytes(b"GateError:" + detail.encode("utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise ClassificationError("classification is not strict canonical JSON") from exc


def _reject_duplicate_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ClassificationError("duplicate JSON member: " + key)
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> Any:
    raise ClassificationError("nonfinite JSON token: " + token)


def strict_json_bytes(raw: bytes, label: str) -> Dict[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClassificationError(label + " is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ClassificationError(label + " is not a JSON object")
    if canonical_json_bytes(value) != raw:
        raise ClassificationError(label + " is not canonical JSON with one final LF")
    return value


def _read_bound(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ClassificationError(label + " cannot be read") from exc
    if len(raw) != expected_bytes:
        raise ClassificationError(label + " byte count differs")
    if sha256_bytes(raw) != expected_sha256:
        raise ClassificationError(label + " SHA-256 differs")
    return raw


def _gpu_gate_error_call(node: ast.AST) -> Optional[ast.Call]:
    if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
        return None
    call = node.exc
    if not isinstance(call.func, ast.Name) or call.func.id != "GateError":
        return None
    if len(call.args) != 2 or call.keywords:
        return None
    code = call.args[0]
    if not isinstance(code, ast.Constant) or code.value != "GPU_IDENTITY_INVALID":
        return None
    return call


def _stderr_hash_prefix(expression: ast.AST) -> Optional[str]:
    if not isinstance(expression, ast.JoinedStr) or len(expression.values) != 2:
        return None
    prefix_node, formatted = expression.values
    if not isinstance(prefix_node, ast.Constant) or not isinstance(prefix_node.value, str):
        return None
    if not isinstance(formatted, ast.FormattedValue):
        return None
    if formatted.conversion != -1 or formatted.format_spec is not None:
        return None
    call = formatted.value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        return None
    if not isinstance(call.func, ast.Name) or call.func.id != "sha256_bytes":
        return None
    argument = call.args[0]
    if not isinstance(argument, ast.Attribute) or argument.attr != "stderr":
        return None
    if not isinstance(argument.value, ast.Name) or argument.value.id != "completed":
        return None
    return prefix_node.value


def _condition_dump(expression: str) -> str:
    parsed = ast.parse(expression, mode="eval")
    return ast.dump(parsed.body, include_attributes=False)


def _direct_if_conditions(function: ast.FunctionDef) -> Dict[int, str]:
    conditions: Dict[int, str] = {}
    for node in ast.walk(function):
        if not isinstance(node, ast.If):
            continue
        for statement in node.body:
            if _gpu_gate_error_call(statement) is not None:
                conditions[id(statement)] = ast.dump(node.test, include_attributes=False)
    return conditions


def extract_gpu_identity_variants(source_raw: bytes) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Enumerate every V4 GPU_IDENTITY_INVALID detail from the frozen AST."""

    try:
        source_text = source_raw.decode("utf-8", errors="strict")
        tree = ast.parse(source_text, filename=SOURCE_RELATIVE_PATH)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ClassificationError("frozen source is not parseable UTF-8 Python") from exc

    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "capture_gpu_identity"
    ]
    if len(functions) != 1:
        raise ClassificationError("capture_gpu_identity definition count differs from one")
    function = functions[0]
    all_raises = [node for node in ast.walk(tree) if _gpu_gate_error_call(node) is not None]
    function_raises = [
        node for node in ast.walk(function) if _gpu_gate_error_call(node) is not None
    ]
    if {id(node) for node in all_raises} != {id(node) for node in function_raises}:
        raise ClassificationError("GPU_IDENTITY_INVALID exists outside capture_gpu_identity")
    function_raises.sort(key=lambda node: (node.lineno, node.col_offset))
    if_conditions = _direct_if_conditions(function)

    static_variants: List[Dict[str, Any]] = []
    dynamic_variants: List[Dict[str, Any]] = []
    expected_condition_by_prefix = {
        "nvidia-smi failed stderr_sha256=": (
            "NONZERO_RETURN_WITH_STDERR_HASH",
            "completed.returncode != 0",
        ),
        "nvidia-smi emitted stderr_sha256=": (
            "ZERO_RETURN_WITH_STDERR",
            "completed.stderr",
        ),
    }
    for raise_node in function_raises:
        call = _gpu_gate_error_call(raise_node)
        if call is None:
            raise ClassificationError("internal AST enumeration failure")
        detail_expression = call.args[1]
        if isinstance(detail_expression, ast.Constant) and isinstance(
            detail_expression.value, str
        ):
            detail = detail_expression.value
            static_variants.append(
                {
                    "detail": detail,
                    "outer_detail_sha256": outer_detail_sha256(detail),
                    "source_line": raise_node.lineno,
                }
            )
            continue
        prefix = _stderr_hash_prefix(detail_expression)
        if prefix not in expected_condition_by_prefix:
            raise ClassificationError("unsupported dynamic GPU_IDENTITY_INVALID detail")
        branch_id, condition = expected_condition_by_prefix[prefix]
        observed_condition = if_conditions.get(id(raise_node))
        if observed_condition != _condition_dump(condition):
            raise ClassificationError("dynamic GPU failure branch condition differs")
        empty_detail = prefix + EMPTY_STDERR_SHA256
        dynamic_variants.append(
            {
                "branch_id": branch_id,
                "condition": condition,
                "detail_template": prefix + "{sha256_bytes(completed.stderr)}",
                "empty_stderr_counterfactual_detail": empty_detail,
                "empty_stderr_outer_detail_sha256": outer_detail_sha256(empty_detail),
                "empty_stderr_matches_observed": outer_detail_sha256(empty_detail)
                == OBSERVED_DETAIL_SHA256,
                "source_line": raise_node.lineno,
            }
        )

    if tuple(item["detail"] for item in static_variants) != EXPECTED_STATIC_DETAILS:
        raise ClassificationError("static GPU_IDENTITY_INVALID detail inventory differs")
    dynamic_prefixes = tuple(
        item["detail_template"].split("{", 1)[0] for item in dynamic_variants
    )
    if dynamic_prefixes != EXPECTED_DYNAMIC_PREFIXES:
        raise ClassificationError("dynamic GPU_IDENTITY_INVALID template inventory differs")
    if len(function_raises) != len(static_variants) + len(dynamic_variants):
        raise ClassificationError("GPU_IDENTITY_INVALID detail inventory is incomplete")
    return static_variants, dynamic_variants


def _load_job_receipt() -> Tuple[Dict[str, Any], bytes]:
    raw = _read_bound(
        JOB_RECEIPT_PATH,
        EXPECTED_JOB_RECEIPT_BYTES,
        EXPECTED_JOB_RECEIPT_SHA256,
        "job receipt",
    )
    receipt = strict_json_bytes(raw, "job receipt")
    expected_scalars = {
        "status": "CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR",
        "failure_code": "GPU_IDENTITY_INVALID",
        "failure_detail_sha256": OBSERVED_DETAIL_SHA256,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "authority": (
            "BODY_FREE_CANONICAL_MAP_DISCRIMINATOR_FAILURE_ONLY__"
            "NO_TASK_OUTCOME_OR_SCIENTIFIC_AUTHORITY"
        ),
    }
    for key, expected in expected_scalars.items():
        if receipt.get(key) != expected:
            raise ClassificationError("job receipt field differs: " + key)
    zero_fields = (
        "protected_packet_bodies_opened",
        "protected_prompt_bodies_opened",
        "tokenize_requests",
        "completion_requests",
        "generation_invocations",
        "official_outcomes_opened",
    )
    if any(receipt.get(key) != 0 for key in zero_fields):
        raise ClassificationError("job receipt has a nonzero protected/generative counter")
    if receipt.get("official_evaluator_invoked") is not False:
        raise ClassificationError("job receipt evaluator boundary differs")
    return receipt, raw


def _load_terminal() -> bytes:
    raw = _read_bound(
        TERMINAL_PATH,
        EXPECTED_TERMINAL_BYTES,
        EXPECTED_TERMINAL_SHA256,
        "Slurm stderr terminal",
    )
    expected = (
        "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK "
        "failure_code=GPU_IDENTITY_INVALID detail_sha256="
        + OBSERVED_DETAIL_SHA256
        + "\n"
    ).encode("ascii")
    if raw != expected:
        raise ClassificationError("Slurm stderr terminal bytes differ")
    return raw


def build_classification() -> Dict[str, Any]:
    source_raw = _read_bound(
        SOURCE_PATH,
        EXPECTED_SOURCE_BYTES,
        EXPECTED_SOURCE_SHA256,
        "frozen V4 core",
    )
    static_variants, dynamic_variants = extract_gpu_identity_variants(source_raw)
    receipt, receipt_raw = _load_job_receipt()
    terminal_raw = _load_terminal()

    static_matches = [
        item for item in static_variants if item["outer_detail_sha256"] == OBSERVED_DETAIL_SHA256
    ]
    empty_dynamic_matches = [
        item
        for item in dynamic_variants
        if item["empty_stderr_outer_detail_sha256"] == OBSERVED_DETAIL_SHA256
    ]
    if static_matches:
        raise ClassificationError("observed detail hash matches a static variant")
    if empty_dynamic_matches:
        raise ClassificationError("observed detail hash matches an empty-stderr variant")
    if len(static_variants) != 8 or len(dynamic_variants) != 2:
        raise ClassificationError("GPU failure branch inventory is not saturated")

    return {
        "access_boundary": {
            "classifier_execution": "OFFLINE_STATIC_SOURCE_AND_BODY_FREE_RESULT_ONLY",
            "generation_accessed": False,
            "job_submission_authorized": False,
            "protected_data_accessed": False,
            "scientific_authority": "NONE",
        },
        "classification": {
            "cannot_check": {
                "nvidia_smi_raw_stderr_content": "CANNOT_CHECK_NOT_RETAINED",
                "nvidia_smi_return_class": (
                    "CANNOT_CHECK_NONZERO_RETURN_VS_ZERO_RETURN_WITH_STDERR"
                ),
                "nvidia_smi_stderr_sha256": "CANNOT_CHECK_NOT_RETAINED",
                "nvidia_smi_stdout_content_or_validity": "CANNOT_CHECK_NOT_RETAINED",
                "selected_dynamic_branch": "CANNOT_CHECK",
            },
            "certain": {
                "dynamic_stderr_hash_variant": True,
                "matches_any_empty_stderr_dynamic_variant": False,
                "matches_any_static_variant": False,
                "nvidia_smi_stderr_nonempty": True,
                "observed_failure_code": "GPU_IDENTITY_INVALID",
            },
            "possible_dynamic_branches": [
                "NONZERO_RETURN_WITH_NONEMPTY_STDERR",
                "ZERO_RETURN_WITH_NONEMPTY_STDERR",
            ],
            "status": "CLASSIFIED_DYNAMIC_NONEMPTY_NVIDIA_SMI_STDERR",
        },
        "dynamic_variants": dynamic_variants,
        "input_bindings": {
            "frozen_v4_core": {
                "bytes": len(source_raw),
                "path": SOURCE_RELATIVE_PATH,
                "sha256": sha256_bytes(source_raw),
            },
            "job_receipt": {
                "bytes": len(receipt_raw),
                "path": JOB_RECEIPT_NAME,
                "sha256": sha256_bytes(receipt_raw),
            },
            "slurm_stderr_terminal": {
                "bytes": len(terminal_raw),
                "path": TERMINAL_NAME,
                "sha256": sha256_bytes(terminal_raw),
            },
        },
        "job_boundary": {
            "completion_requests": receipt["completion_requests"],
            "generation_invocations": receipt["generation_invocations"],
            "official_evaluator_invoked": receipt["official_evaluator_invoked"],
            "official_outcomes_opened": receipt["official_outcomes_opened"],
            "protected_packet_bodies_opened": receipt["protected_packet_bodies_opened"],
            "protected_prompt_bodies_opened": receipt["protected_prompt_bodies_opened"],
            "scientific_authority_delta": receipt["scientific_authority_delta"],
            "tokenize_requests": receipt["tokenize_requests"],
        },
        "observed": {
            "failure_code": receipt["failure_code"],
            "failure_detail_sha256": receipt["failure_detail_sha256"],
            "target_job_id": "3537910",
        },
        "proof": {
            "dynamic_variant_count": len(dynamic_variants),
            "empty_stderr_sha256": EMPTY_STDERR_SHA256,
            "gpu_identity_invalid_raise_site_count": len(static_variants)
            + len(dynamic_variants),
            "outer_hash_construction": (
                "sha256(b\"GateError:\" + detail.encode(\"utf-8\"))"
            ),
            "static_variant_count": len(static_variants),
        },
        "schema_version": (
            "orion.p1.scienceagentbench."
            "offline-gpu-identity-failure-classification.v1"
        ),
        "static_variants": static_variants,
    }


def classification_bytes() -> bytes:
    return canonical_json_bytes(build_classification())


def verify_committed_classification() -> bytes:
    expected = classification_bytes()
    try:
        observed = CLASSIFICATION_PATH.read_bytes()
    except OSError as exc:
        raise ClassificationError("committed classification receipt cannot be read") from exc
    if observed != expected:
        raise ClassificationError("committed classification differs from generated bytes")
    strict_json_bytes(observed, "committed classification receipt")
    return observed


def main() -> int:
    try:
        receipt_raw = verify_committed_classification()
    except ClassificationError as exc:
        print(
            "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_CANNOT_CHECK "
            + "detail_sha256="
            + sha256_bytes((type(exc).__name__ + ":" + str(exc)).encode("utf-8")),
            file=sys.stderr,
        )
        return 1
    print(PASS_TERMINAL + " receipt_sha256=" + sha256_bytes(receipt_raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
