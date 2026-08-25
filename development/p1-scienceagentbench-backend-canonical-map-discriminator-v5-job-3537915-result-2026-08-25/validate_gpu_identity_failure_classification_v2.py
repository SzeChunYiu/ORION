#!/usr/bin/env python3
"""Direct offline validator for the job-3537915 GPU failure classification.

This validator reads only the exact body-free result surfaces, frozen V5 source,
the committed classification, its own source, and a locally bound NVIDIA
documentation download.  It does not execute nvidia-smi, submit work, access
protected bodies, or use any task-bearing route.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
CLASSIFICATION_PATH = ROOT / "GPU_IDENTITY_FAILURE_CLASSIFICATION_V2.json"
RECEIPT_PATH = ROOT / "JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json"
TERMINAL_PATH = ROOT / "slurm-3537915.err"
CORE_PATH = (
    ROOT.parent
    / "p1-scienceagentbench-backend-canonical-map-discriminator-v5-2026-08-25"
    / "backend_canonical_map_discriminator_v2.py"
)
DOCUMENT_PATH = ROOT / "NVIDIA_SMI_RETURN_VALUE_SOURCE_V1.txt"

CLASSIFICATION_BYTES = 7557
CLASSIFICATION_SHA256 = "abfc0d0ddddff00412554bc00d59e24e1bb1c811062e87d03b0b18f943a3ce0c"
RECEIPT_BYTES = 1883
RECEIPT_SHA256 = "2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3"
TERMINAL_BYTES = 172
TERMINAL_SHA256 = "c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e"
CORE_BYTES = 63962
CORE_SHA256 = "a9b2d77aa98eaaf02d334da2b444cb8f4e788bafb13b951e8369fd2c77fab285"
DOCUMENT_BYTES = 917
DOCUMENT_SHA256 = "a95583b6d96309dc823b04a7b89f62d7ee2b81847bd2f75b119c97911c6a56a3"

STDOUT_BYTES = 22
STDOUT_SHA256 = "cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd"
STDERR_BYTES = 76
STDERR_SHA256 = "0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a"
DETAIL_SHA256 = "37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2"
CANDIDATE = b"No devices were found\n"
EXPECTED_TERMINAL = (
    "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK "
    "failure_code=GPU_IDENTITY_INVALID detail_sha256=" + DETAIL_SHA256
)
PASS_TERMINAL = (
    "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_V2_PASS "
    "tests=18 protected_bodies=0 tokenize=0 completion=0 generation=0 jobs=0 "
    "outcomes=0 production_admissibility=CANNOT_CHECK scientific_authority=NONE"
)

EXPECTED_STAGES = [
    "CONTRACT_BOUND",
    "RUNTIME_FILES_BOUND",
    "SERVER_STARTED",
    "SERVER_READY_BODY_FREE",
    "CANONICAL_MAP_ATTESTATION_1",
    "SERVER_CLEANUP_PASS",
]
EXPECTED_CAPTURE = {
    "argv": [
        "/usr/bin/nvidia-smi",
        "--query-gpu=index,uuid,name",
        "--format=csv,noheader,nounits",
    ],
    "return_code": 6,
    "status": "COMPLETED",
    "stderr": {"bytes": STDERR_BYTES, "sha256": STDERR_SHA256},
    "stdout": {"bytes": STDOUT_BYTES, "sha256": STDOUT_SHA256},
    "stdout_parse_attempted": False,
}
EXPECTED_TOP_LEVEL_KEYS = {
    "access_boundary",
    "authoritative_return_code_semantics",
    "classification",
    "input_bindings",
    "job_boundary",
    "next_discriminator",
    "observed",
    "schema_version",
    "status",
    "stderr_boundary",
    "stdout_declared_candidate_match",
}


class ValidationError(RuntimeError):
    """A direct validation invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("value is not strict canonical JSON") from exc


def _reject_duplicate_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, member in pairs:
        require(key not in value, "duplicate JSON key: " + key)
        value[key] = member
    return value


def _reject_nonfinite(token: str) -> Any:
    raise ValidationError("nonfinite JSON token: " + token)


def strict_json(raw: bytes, label: str) -> Dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(label + " is not strict UTF-8 JSON") from exc
    require(isinstance(value, dict), label + " is not a JSON object")
    require(canonical_json_bytes(value) == raw, label + " is not canonical JSON plus LF")
    return value


def exact(actual: Any, expected: Any, label: str) -> None:
    require(type(actual) is type(expected), label + " type differs")
    if isinstance(expected, dict):
        require(set(actual) == set(expected), label + " keys differ")
        for key in expected:
            exact(actual[key], expected[key], label + "." + key)
        return
    if isinstance(expected, list):
        require(len(actual) == len(expected), label + " length differs")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            exact(actual_item, expected_item, label + "[" + str(index) + "]")
        return
    require(actual == expected, label + " value differs")


def bound_bytes(path: Path, expected_bytes: int, expected_sha256: str, label: str) -> bytes:
    require(path.is_file(), label + " is absent")
    raw = path.read_bytes()
    require(len(raw) == expected_bytes, label + " byte count differs")
    require(sha256_bytes(raw) == expected_sha256, label + " SHA-256 differs")
    return raw


def load_surfaces() -> Tuple[Dict[str, Any], Dict[str, Any], bytes, bytes, bytes, bytes]:
    classification_raw = bound_bytes(
        CLASSIFICATION_PATH, CLASSIFICATION_BYTES, CLASSIFICATION_SHA256, "classification"
    )
    receipt_raw = bound_bytes(RECEIPT_PATH, RECEIPT_BYTES, RECEIPT_SHA256, "job receipt")
    terminal_raw = bound_bytes(TERMINAL_PATH, TERMINAL_BYTES, TERMINAL_SHA256, "terminal")
    core_raw = bound_bytes(CORE_PATH, CORE_BYTES, CORE_SHA256, "frozen V5 core")
    document_raw = bound_bytes(
        DOCUMENT_PATH, DOCUMENT_BYTES, DOCUMENT_SHA256, "NVIDIA documentation"
    )
    classification = strict_json(classification_raw, "classification")
    receipt = strict_json(receipt_raw, "job receipt")
    return classification, receipt, classification_raw, terminal_raw, core_raw, document_raw


def test_validator_is_offline_stdlib_only(context: Dict[str, Any]) -> None:
    del context
    raw = Path(__file__).read_bytes()
    try:
        tree = ast.parse(raw.decode("utf-8", errors="strict"), filename=Path(__file__).name)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ValidationError("validator is not parseable UTF-8 Python") from exc
    allowed_imports = {"__future__", "ast", "hashlib", "json", "sys", "pathlib", "typing"}
    forbidden_calls = {
        "open",
        "popen",
        "remove",
        "rename",
        "replace",
        "rmdir",
        "run",
        "system",
        "touch",
        "unlink",
        "write_bytes",
        "write_text",
    }
    for node in ast.walk(tree):
        require(not isinstance(node, ast.Assert), "validator relies on assert under -O")
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(alias.name.split(".", 1)[0] in allowed_imports, "non-stdlib import")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            require(root in allowed_imports, "non-stdlib from-import")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                require(node.func.id not in forbidden_calls, "forbidden validator call")
            if isinstance(node.func, ast.Attribute):
                require(node.func.attr not in forbidden_calls, "forbidden validator method")


def test_input_bindings(context: Dict[str, Any]) -> None:
    classification = context["classification"]
    expected = {
        "authoritative_nvidia_smi_document": {
            "bytes": DOCUMENT_BYTES,
            "path": "NVIDIA_SMI_RETURN_VALUE_SOURCE_V1.txt",
            "sha256": DOCUMENT_SHA256,
        },
        "frozen_v5_core": {
            "bytes": CORE_BYTES,
            "path": "../p1-scienceagentbench-backend-canonical-map-discriminator-v5-2026-08-25/backend_canonical_map_discriminator_v2.py",
            "sha256": CORE_SHA256,
        },
        "job_receipt": {
            "bytes": RECEIPT_BYTES,
            "path": RECEIPT_PATH.name,
            "sha256": RECEIPT_SHA256,
        },
        "slurm_stderr_terminal": {
            "bytes": TERMINAL_BYTES,
            "path": TERMINAL_PATH.name,
            "sha256": TERMINAL_SHA256,
        },
    }
    exact(classification.get("input_bindings"), expected, "input_bindings")


def test_receipt_exact_failure(context: Dict[str, Any]) -> None:
    receipt = context["receipt"]
    require(receipt.get("schema_version") == "orion.p1.scienceagentbench.backend-canonical-map-discriminator-cannot-check.v2", "receipt schema differs")
    require(receipt.get("status") == "CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR", "receipt status differs")
    require(receipt.get("failure_code") == "GPU_IDENTITY_INVALID", "failure code differs")
    require(receipt.get("failure_subcode") == "NVIDIA_SMI_NONZERO_RETURN", "failure subcode differs")
    require(receipt.get("failure_detail_sha256") == DETAIL_SHA256, "failure detail differs")
    exact(receipt.get("completed_stages"), EXPECTED_STAGES, "receipt completed_stages")
    exact(receipt.get("gpu_capture"), EXPECTED_CAPTURE, "receipt gpu_capture")


def test_terminal_exact(context: Dict[str, Any]) -> None:
    require(context["terminal_raw"] == EXPECTED_TERMINAL.encode("ascii") + b"\n", "terminal bytes differ")


def test_v5_source_branch(context: Dict[str, Any]) -> None:
    try:
        source = context["core_raw"].decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError("frozen V5 core is not UTF-8") from exc
    capture_index = source.index("capture = _completed_nvidia_smi_capture(completed)")
    nonzero_index = source.index("if completed.returncode != 0:", capture_index)
    nonzero_subcode_index = source.index('failure_subcode="NVIDIA_SMI_NONZERO_RETURN"', nonzero_index)
    stderr_index = source.index("if completed.stderr:", nonzero_subcode_index)
    parse_index = source.index('capture["stdout_parse_attempted"] = True', stderr_index)
    require(capture_index < nonzero_index < nonzero_subcode_index < stderr_index < parse_index, "V5 branch order differs")
    require('"return_code": completed.returncode' in source, "capture return code binding absent")
    require('"stdout": {' in source and '"stderr": {' in source, "capture stream bindings absent")


def test_authoritative_document(context: Dict[str, Any]) -> None:
    try:
        lines = context["document_raw"].decode("utf-8", errors="strict").splitlines()
    except UnicodeDecodeError as exc:
        raise ValidationError("NVIDIA documentation is not UTF-8") from exc
    require(len(lines) == 29, "committed NVIDIA source excerpt line count differs")
    require(lines[0] == "SOURCE_TITLE=nvidia-smi - NVIDIA System Management Interface program", "source title differs")
    require(lines[1] == "SOURCE_URL=https://docs.nvidia.com/deploy/nvidia-smi/index.html", "source URL differs")
    require(lines[2] == "ACCESSED_DATE=2026-08-25", "access date differs")
    require(lines[3] == "DOWNLOADED_HTML_BYTES=218860", "downloaded HTML byte binding differs")
    require(lines[4] == "DOWNLOADED_HTML_SHA256=017647ae72b332a94e01e6d9672d1d82367e56de1d0685132eb91a972035b17e", "downloaded HTML hash binding differs")
    require(lines[5] == "DOWNLOADED_HTML_LINE_RANGE=478-498", "downloaded HTML line range differs")
    require(lines[6] == "EXCERPT_BEGIN" and lines[28] == "EXCERPT_END", "excerpt framing differs")
    require(lines[7] == "<h1>RETURN VALUE</h1>", "RETURN VALUE heading line differs")
    require(lines[8] == "<p>Return code reflects whether the operation succeeded or failed and", "return-value scope line differs")
    require(lines[25] == "<li><p>Return code 6 - A query to find an object was", "return-code-6 line differs")
    require(lines[26] == "unsuccessful</p></li>", "return-code-6 continuation differs")
    require(lines[27] == "</ul>", "return-code-6 excerpt end differs")


def test_classification_envelope(context: Dict[str, Any]) -> None:
    classification = context["classification"]
    require(set(classification) == EXPECTED_TOP_LEVEL_KEYS, "classification top-level keys differ")
    require(classification.get("schema_version") == "orion.p1.scienceagentbench.gpu-identity-failure-classification.v2", "classification schema differs")
    require(classification.get("status") == "PASS_CLASSIFIED_JOB_3537915_BODY_FREE_GPU_IDENTITY_FAILURE", "classification status differs")


def test_observed_exact(context: Dict[str, Any]) -> None:
    classification = context["classification"]
    receipt = context["receipt"]
    expected = {
        "completed_stages": EXPECTED_STAGES,
        "failure_code": receipt["failure_code"],
        "failure_detail_sha256": receipt["failure_detail_sha256"],
        "failure_subcode": receipt["failure_subcode"],
        "gpu_capture": EXPECTED_CAPTURE,
        "receipt_authority": receipt["authority"],
        "receipt_status": receipt["status"],
        "target_job_id": "3537915",
        "terminal": EXPECTED_TERMINAL,
    }
    exact(classification.get("observed"), expected, "observed")


def test_exact_branch_classification(context: Dict[str, Any]) -> None:
    block = context["classification"].get("classification")
    require(isinstance(block, dict), "classification block absent")
    expected_certain = {
        "completed_nvidia_smi_call": True,
        "failure_branch": "NVIDIA_SMI_NONZERO_RETURN",
        "failure_code": "GPU_IDENTITY_INVALID",
        "gpu_identity_bound": False,
        "nvidia_smi_return_code": 6,
        "nvidia_smi_stderr_nonempty": True,
        "nvidia_smi_stdout_nonempty": True,
        "stdout_parse_attempted": False,
    }
    exact(block.get("certain"), expected_certain, "classification.certain")
    require(block.get("status") == "CLASSIFIED_EXACT_V5_NVIDIA_SMI_NONZERO_RETURN_RC6_WITH_RETAINED_STREAM_BINDINGS", "classification conclusion differs")
    require(block.get("predecessor_relation") == "JOB_3537915_SELECTS_THE_NONZERO_RETURN_BRANCH_FOR_ITSELF_ONLY__NO_RETROACTIVE_CLASSIFICATION_REPAIR_OR_PROMOTION_OF_JOB_3537910", "predecessor boundary differs")


def test_stdout_candidate_boundary(context: Dict[str, Any]) -> None:
    block = context["classification"].get("stdout_declared_candidate_match")
    require(isinstance(block, dict), "stdout candidate block absent")
    require(len(CANDIDATE) == STDOUT_BYTES, "declared candidate byte count differs")
    require(sha256_bytes(CANDIDATE) == STDOUT_SHA256, "declared candidate hash differs")
    require(block.get("candidate_python_bytes_literal") == "b'No devices were found\\n'", "candidate literal differs")
    require(block.get("candidate_bytes") == STDOUT_BYTES and type(block.get("candidate_bytes")) is int, "candidate bytes differ")
    require(block.get("candidate_sha256") == STDOUT_SHA256, "candidate SHA-256 differs")
    require(block.get("matches_observed_stdout_binding") is True, "candidate match differs")
    require(block.get("interpretation") == "DECLARED_CANDIDATE_HASH_MATCH_UNDER_SHA256_COLLISION_RESISTANCE_ONLY", "collision-resistance boundary differs")
    require(block.get("candidate_source") == "DECLARED_CANDIDATE_FOR_OFFLINE_HASH_COMPARISON_ONLY__NOT_RECOVERED_FROM_RECEIPT", "candidate source boundary differs")
    require(block.get("observed_plaintext_retained_by_receipt") is False, "plaintext retention was promoted")
    require(block.get("proof_boundary") == "NOT_PROOF_THAT_PLAINTEXT_WAS_RETAINED__NOT_A_DEVICE_VISIBILITY_OR_ROOT_CAUSE_PROOF", "candidate proof boundary differs")


def test_stderr_boundary(context: Dict[str, Any]) -> None:
    block = context["classification"].get("stderr_boundary")
    expected = {
        "bytes": STDERR_BYTES,
        "meaning": "CANNOT_CHECK_NO_PLAINTEXT_OR_CAUSAL_GUESS",
        "plaintext_retained_by_receipt": False,
        "sha256": STDERR_SHA256,
    }
    exact(block, expected, "stderr_boundary")
    cannot_check = context["classification"]["classification"]["cannot_check"]
    require(cannot_check.get("nvidia_smi_stderr_plaintext") == "CANNOT_CHECK_NOT_RETAINED", "stderr plaintext was guessed")


def test_return_code_scope(context: Dict[str, Any]) -> None:
    block = context["classification"].get("authoritative_return_code_semantics")
    require(isinstance(block, dict), "return-code semantics block absent")
    require(block.get("return_code") == 6 and type(block.get("return_code")) is int, "documented return code differs")
    require(block.get("generic_semantic") == "A query to find an object was unsuccessful", "generic return semantic differs")
    require(block.get("source_url") == "https://docs.nvidia.com/deploy/nvidia-smi/index.html", "documentation URL differs")
    require(block.get("accessed_date") == "2026-08-25", "documentation access date differs")
    require(block.get("local_excerpt_line_start") == 8 and block.get("local_excerpt_line_end") == 28, "documentation line binding differs")
    require(block.get("queried_object_identity") == "CANNOT_CHECK_NOT_IDENTIFIED_BY_RECEIPT_OR_GENERIC_RETURN_VALUE_DOCUMENTATION", "queried object was inferred")
    require(block.get("root_cause") == "CANNOT_CHECK_GENERIC_RETURN_VALUE_DOES_NOT_IDENTIFY_OBJECT_OR_CAUSE", "root cause was inferred")
    require(block.get("applicability_to_executed_binary_version") == "CANNOT_CHECK_EXECUTED_NVIDIA_SMI_VERSION_NOT_RETAINED", "binary-version scope was promoted")
    require(block.get("scope") == "GENERIC_NVIDIA_SMI_RETURN_VALUE_ONLY__NO_OBJECT_DEVICE_VISIBILITY_CGROUP_OR_SLURM_CAUSAL_INFERENCE", "return-code scope differs")


def test_job_boundary(context: Dict[str, Any]) -> None:
    expected = {
        "completion_requests": 0,
        "discriminator_pass": False,
        "first_mapping_attestation_promoted": False,
        "generation_invocations": 0,
        "gpu_identity_bound": False,
        "official_evaluator_invoked": False,
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "protected_packet_bodies_opened": 0,
        "protected_prompt_bodies_opened": 0,
        "scientific_authority_delta": "NONE",
        "tokenize_requests": 0,
    }
    exact(context["classification"].get("job_boundary"), expected, "job_boundary")


def test_access_boundary(context: Dict[str, Any]) -> None:
    expected = {
        "classification_execution": "OFFLINE_EXACT_RECEIPT_SOURCE_AND_LOCAL_AUTHORITATIVE_DOCUMENT_ONLY",
        "generation_accessed": False,
        "job_submission_authorized": False,
        "live_command_executed_during_classification": False,
        "official_outcomes_accessed": False,
        "protected_data_accessed": False,
        "scientific_authority": "NONE",
    }
    exact(context["classification"].get("access_boundary"), expected, "access_boundary")


def test_next_discriminator_authority(context: Dict[str, Any]) -> None:
    proposal = context["classification"].get("next_discriminator")
    require(isinstance(proposal, dict), "next discriminator proposal absent")
    require(proposal.get("proposal_status") == "PROPOSAL_ONLY__NO_DEPLOYMENT_OR_SUBMISSION_AUTHORITY", "proposal grants authority")
    require(proposal.get("smallest_scope") == "ONE_DIAGNOSTIC_ONLY_BODY_FREE_JOB__NO_SERVER_MODEL_PROTECTED_BODY_OR_HTTP", "proposal scope differs")
    require(proposal.get("fresh_custody") == "NEW_ABSENT_DEPLOYMENT_RUN_OUTPUT_AND_LOG_ROOTS_REQUIRED__NO_REUSE_OR_IN_PLACE_RETRY", "fresh-custody boundary differs")
    require(proposal.get("implementation_boundary") == "FREEZE_TOOL_PATHS_HASHES_BOUNDS_SCHEMA_AND_DECISION_ORDER_BEFORE_ANY_SEPARATELY_AUTHORIZED_EXECUTION", "implementation boundary differs")


def test_next_discriminator_evidence(context: Dict[str, Any]) -> None:
    groups = context["classification"]["next_discriminator"].get("evidence_groups")
    require(isinstance(groups, list) and len(groups) == 4, "diagnostic evidence groups differ")
    require([group.get("id") for group in groups] == ["SLURM_ALLOCATION_AND_ENVIRONMENT", "DEVICE_NODE_VISIBILITY", "CGROUP_DEVICE_SCOPE", "NVIDIA_SMI_DIAGNOSTICS"], "diagnostic group order differs")
    require(groups[0].get("retain") == ["exact scheduler allocation record", "SLURM_JOB_ID", "SLURM_JOB_GPUS", "SLURM_STEP_GPUS", "CUDA_VISIBLE_DEVICES"], "SLURM evidence scope differs")
    require("bounded /dev/nvidia* inventory" in groups[1].get("retain", []), "device-node inventory absent")
    require("bounded /proc/self/cgroup" in groups[2].get("retain", []), "cgroup membership binding absent")
    require(groups[2].get("rule") == "CGROUP_V2_DEVICE_BPF_POLICY_REMAINS_CANNOT_CHECK_IF_NOT_DIRECTLY_INTROSPECTABLE", "cgroup-v2 boundary differs")


def test_next_discriminator_commands(context: Dict[str, Any]) -> None:
    group = context["classification"]["next_discriminator"]["evidence_groups"][3]
    expected_commands = [
        ["/usr/bin/nvidia-smi", "-L"],
        ["/usr/bin/nvidia-smi", "--query-gpu=index,uuid,name", "--format=csv,noheader,nounits"],
    ]
    exact(group.get("commands"), expected_commands, "next_discriminator nvidia-smi commands")
    require(group.get("rule") == "NO_STDOUT_PARSE_UNLESS_RETURN_ZERO_AND_STDERR_EMPTY_FOR_THE_IDENTITY_QUERY", "parse policy differs")
    retain = group.get("retain")
    require(isinstance(retain, list) and "return code" in retain, "return-code retention absent")
    require("bounded stdout bytes and sha256" in retain and "bounded stderr bytes and sha256" in retain, "stream bindings absent")


def test_next_discriminator_forbidden_and_outputs(context: Dict[str, Any]) -> None:
    proposal = context["classification"]["next_discriminator"]
    expected_forbidden = [
        "protected packet or prompt open",
        "task-bearing HTTP route",
        "tokenize request",
        "completion request",
        "model or server start",
        "generation",
        "official evaluator",
        "official outcome access",
        "network access",
    ]
    exact(proposal.get("forbidden_operations"), expected_forbidden, "forbidden_operations")
    expected_outputs = [
        "SCHEDULER_GPU_BINDING_MISSING_OR_INCONSISTENT",
        "NVIDIA_DEVICE_NODES_ABSENT",
        "CGROUP_DEVICE_ACCESS_DENIED_OR_NOT_INTROSPECTABLE",
        "NVIDIA_SMI_OBJECT_QUERY_STILL_UNSUCCESSFUL_WITH_EXACT_CAPTURE",
        "VISIBLE_A40_IDENTITY_BOUND",
        "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE_OR_DRIFTED",
    ]
    exact(proposal.get("decision_outputs"), expected_outputs, "decision_outputs")


TESTS: List[Tuple[str, Callable[[Dict[str, Any]], None]]] = [
    ("validator_is_offline_stdlib_only", test_validator_is_offline_stdlib_only),
    ("input_bindings", test_input_bindings),
    ("receipt_exact_failure", test_receipt_exact_failure),
    ("terminal_exact", test_terminal_exact),
    ("v5_source_branch", test_v5_source_branch),
    ("authoritative_document", test_authoritative_document),
    ("classification_envelope", test_classification_envelope),
    ("observed_exact", test_observed_exact),
    ("exact_branch_classification", test_exact_branch_classification),
    ("stdout_candidate_boundary", test_stdout_candidate_boundary),
    ("stderr_boundary", test_stderr_boundary),
    ("return_code_scope", test_return_code_scope),
    ("job_boundary", test_job_boundary),
    ("access_boundary", test_access_boundary),
    ("next_discriminator_authority", test_next_discriminator_authority),
    ("next_discriminator_evidence", test_next_discriminator_evidence),
    ("next_discriminator_commands", test_next_discriminator_commands),
    ("next_discriminator_forbidden_and_outputs", test_next_discriminator_forbidden_and_outputs),
]


def main() -> int:
    try:
        classification, receipt, classification_raw, terminal_raw, core_raw, document_raw = load_surfaces()
        context = {
            "classification": classification,
            "classification_raw": classification_raw,
            "receipt": receipt,
            "terminal_raw": terminal_raw,
            "core_raw": core_raw,
            "document_raw": document_raw,
        }
        require(len(TESTS) == 18, "test inventory differs")
        for _name, test in TESTS:
            test(context)
    except Exception as exc:
        detail = (type(exc).__name__ + ":" + str(exc)).encode("utf-8", errors="replace")
        print(
            "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_V2_CANNOT_CHECK "
            "validator_detail_sha256=" + sha256_bytes(detail),
            file=sys.stderr,
        )
        return 1
    print(PASS_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
