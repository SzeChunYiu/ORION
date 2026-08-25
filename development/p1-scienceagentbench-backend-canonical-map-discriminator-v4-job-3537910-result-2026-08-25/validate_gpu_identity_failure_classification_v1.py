#!/usr/bin/env python3
"""Hostile offline validator for the job-3537910 GPU classification."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Tuple


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
CLASSIFIER_PATH = ROOT / "classify_gpu_identity_failure_v1.py"
CLASSIFICATION_PATH = ROOT / "OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json"
SOURCE_PATH = (
    ROOT.parent
    / "p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25"
    / "backend_canonical_map_discriminator_v1.py"
)
JOB_RECEIPT_PATH = (
    ROOT / "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json"
)
TERMINAL_PATH = ROOT / "slurm-3537910.err"

EXPECTED_SOURCE_SHA256 = "59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219"
EXPECTED_JOB_RECEIPT_SHA256 = "cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a"
EXPECTED_TERMINAL_SHA256 = "27c5fda40d52f578c90f18d155ae90d3a89fe06049a652b1150a609fe6380dfc"
OBSERVED_DETAIL_SHA256 = "a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4"
EMPTY_STDERR_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EXPECTED_EMPTY_OUTER_HASHES = {
    "NONZERO_RETURN_WITH_STDERR_HASH": (
        "f999b6b2ceeeb0e621bbfd0029d52d86e4ee37665749e859b57d3769668b16a4"
    ),
    "ZERO_RETURN_WITH_STDERR": (
        "d84e9958317bda9f4ee15ede66703d81a35bd70d4da1615d10825e10456fa61c"
    ),
}
EXPECTED_STATIC = (
    (861, "SLURM_JOB_ID is not canonical"),
    (868, "CUDA_VISIBLE_DEVICES is not singular"),
    (894, "nvidia-smi could not be executed exactly"),
    (908, "nvidia-smi stdout is not UTF-8"),
    (910, "nvidia-smi stdout line framing differs"),
    (913, "visible GPU row count differs from one"),
    (920, "visible GPU row is not canonical"),
    (922, "visible GPU is not exactly NVIDIA A40"),
)
EXPECTED_TOP_LEVEL_KEYS = {
    "access_boundary",
    "classification",
    "dynamic_variants",
    "input_bindings",
    "job_boundary",
    "observed",
    "proof",
    "schema_version",
    "static_variants",
}
PASS_TERMINAL = "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_PASS"


class ValidationError(RuntimeError):
    """A validation invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def outer_hash(detail: str) -> str:
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
    require(isinstance(value, dict), label + " is not an object")
    require(canonical_json_bytes(value) == raw, label + " is not canonical JSON plus LF")
    return value


def load_classifier() -> ModuleType:
    require(CLASSIFIER_PATH.is_file(), "classifier is absent")
    spec = importlib.util.spec_from_file_location(
        "gpu_identity_failure_classifier_under_validation", CLASSIFIER_PATH
    )
    require(spec is not None and spec.loader is not None, "classifier import spec failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_classifier_source() -> None:
    raw = CLASSIFIER_PATH.read_bytes()
    try:
        tree = ast.parse(raw.decode("utf-8", errors="strict"), filename=CLASSIFIER_PATH.name)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ValidationError("classifier source is not parseable UTF-8 Python") from exc
    allowed_import_roots = {"__future__", "ast", "hashlib", "json", "sys", "pathlib", "typing"}
    for node in ast.walk(tree):
        require(not isinstance(node, ast.Assert), "classifier relies on assert under -O")
        if isinstance(node, ast.Import):
            for alias in node.names:
                require(
                    alias.name.split(".", 1)[0] in allowed_import_roots,
                    "classifier has a non-offline import: " + alias.name,
                )
        if isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            require(
                module_name.split(".", 1)[0] in allowed_import_roots,
                "classifier has a non-offline from-import: " + module_name,
            )
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                require(
                    node.func.id not in {"eval", "exec", "compile", "__import__", "open"},
                    "classifier contains dynamic execution or generic file open",
                )
            if isinstance(node.func, ast.Attribute):
                require(
                    node.func.attr
                    not in {
                        "open",
                        "rename",
                        "replace",
                        "rmdir",
                        "touch",
                        "unlink",
                        "write_bytes",
                        "write_text",
                    },
                    "classifier contains a filesystem mutation call",
                )


def _gpu_call(node: ast.AST) -> Any:
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


def independently_inventory_source(source_raw: bytes) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    tree = ast.parse(source_raw.decode("utf-8", errors="strict"), filename=SOURCE_PATH.name)
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "capture_gpu_identity"
    ]
    require(len(functions) == 1, "independent function inventory differs")
    raises = [node for node in ast.walk(functions[0]) if _gpu_call(node) is not None]
    raises.sort(key=lambda node: (node.lineno, node.col_offset))
    static: List[Tuple[int, str]] = []
    dynamic: List[Tuple[int, str]] = []
    for raise_node in raises:
        expression = _gpu_call(raise_node).args[1]
        if isinstance(expression, ast.Constant) and isinstance(expression.value, str):
            static.append((raise_node.lineno, expression.value))
            continue
        require(isinstance(expression, ast.JoinedStr), "independent dynamic AST form differs")
        require(len(expression.values) == 2, "independent dynamic f-string arity differs")
        prefix = expression.values[0]
        formatted = expression.values[1]
        require(
            isinstance(prefix, ast.Constant) and isinstance(prefix.value, str),
            "independent dynamic prefix differs",
        )
        require(isinstance(formatted, ast.FormattedValue), "independent formatted value differs")
        dynamic.append((raise_node.lineno, prefix.value))
    require(len(raises) == 10, "independent GPU raise count differs")
    return static, dynamic


def validate_mutation_rejection(module: ModuleType, source_raw: bytes) -> None:
    mutations = (
        source_raw.replace(
            b"SLURM_JOB_ID is not canonical",
            b"SLURM_JOB_ID is not canonicaL",
            1,
        ),
        source_raw.replace(b"completed.returncode != 0", b"completed.returncode == 0", 1),
        source_raw.replace(
            b"sha256_bytes(completed.stderr)",
            b"sha256_bytes(completed.stdout)",
            1,
        ),
    )
    for index, mutated in enumerate(mutations):
        require(mutated != source_raw, "mutation fixture did not change source")
        try:
            module.extract_gpu_identity_variants(mutated)
        except module.ClassificationError:
            continue
        raise ValidationError("classifier accepted hostile AST mutation " + str(index))


def validate_receipt(module: ModuleType) -> bytes:
    source_raw = SOURCE_PATH.read_bytes()
    job_raw = JOB_RECEIPT_PATH.read_bytes()
    terminal_raw = TERMINAL_PATH.read_bytes()
    require(sha256_bytes(source_raw) == EXPECTED_SOURCE_SHA256, "frozen source hash differs")
    require(
        sha256_bytes(job_raw) == EXPECTED_JOB_RECEIPT_SHA256,
        "job receipt hash differs",
    )
    require(
        sha256_bytes(terminal_raw) == EXPECTED_TERMINAL_SHA256,
        "terminal hash differs",
    )
    static_inventory, dynamic_inventory = independently_inventory_source(source_raw)
    require(tuple(static_inventory) == EXPECTED_STATIC, "independent static details differ")
    require(
        tuple(dynamic_inventory)
        == (
            (896, "nvidia-smi failed stderr_sha256="),
            (901, "nvidia-smi emitted stderr_sha256="),
        ),
        "independent dynamic templates differ",
    )

    raw = CLASSIFICATION_PATH.read_bytes()
    receipt = strict_json(raw, "classification receipt")
    require(set(receipt) == EXPECTED_TOP_LEVEL_KEYS, "classification top-level keys differ")
    require(
        receipt.get("schema_version")
        == "orion.p1.scienceagentbench.offline-gpu-identity-failure-classification.v1",
        "classification schema differs",
    )
    require(module.classification_bytes() == raw, "classifier generation differs byte-for-byte")
    require(module.verify_committed_classification() == raw, "classifier self-check differs")

    observed = receipt.get("observed")
    require(isinstance(observed, dict), "observed block is absent")
    require(observed.get("target_job_id") == "3537910", "target job differs")
    require(observed.get("failure_code") == "GPU_IDENTITY_INVALID", "failure code differs")
    require(
        observed.get("failure_detail_sha256") == OBSERVED_DETAIL_SHA256,
        "observed detail hash differs",
    )

    static_variants = receipt.get("static_variants")
    require(isinstance(static_variants, list), "static variants are absent")
    require(len(static_variants) == 8, "static variant count differs")
    for expected, item in zip(EXPECTED_STATIC, static_variants):
        line, detail = expected
        require(item.get("source_line") == line, "static source line differs")
        require(item.get("detail") == detail, "static detail differs")
        require(
            item.get("outer_detail_sha256") == outer_hash(detail),
            "static outer hash construction differs",
        )
        require(
            item.get("outer_detail_sha256") != OBSERVED_DETAIL_SHA256,
            "observed hash matches a static detail",
        )

    dynamic_variants = receipt.get("dynamic_variants")
    require(isinstance(dynamic_variants, list), "dynamic variants are absent")
    require(len(dynamic_variants) == 2, "dynamic variant count differs")
    expected_dynamic = (
        (
            "NONZERO_RETURN_WITH_STDERR_HASH",
            "completed.returncode != 0",
            "nvidia-smi failed stderr_sha256=",
        ),
        (
            "ZERO_RETURN_WITH_STDERR",
            "completed.stderr",
            "nvidia-smi emitted stderr_sha256=",
        ),
    )
    for expected, item in zip(expected_dynamic, dynamic_variants):
        branch_id, condition, prefix = expected
        empty_detail = prefix + EMPTY_STDERR_SHA256
        require(item.get("branch_id") == branch_id, "dynamic branch ID differs")
        require(item.get("condition") == condition, "dynamic condition differs")
        require(
            item.get("detail_template")
            == prefix + "{sha256_bytes(completed.stderr)}",
            "dynamic detail template differs",
        )
        require(
            item.get("empty_stderr_counterfactual_detail") == empty_detail,
            "empty-stderr detail differs",
        )
        require(
            item.get("empty_stderr_outer_detail_sha256")
            == EXPECTED_EMPTY_OUTER_HASHES[branch_id]
            == outer_hash(empty_detail),
            "empty-stderr outer hash differs",
        )
        require(
            item.get("empty_stderr_matches_observed") is False,
            "empty stderr unexpectedly matches observed",
        )

    classification = receipt.get("classification")
    require(isinstance(classification, dict), "classification block is absent")
    certain = classification.get("certain")
    cannot_check = classification.get("cannot_check")
    require(isinstance(certain, dict), "certain block is absent")
    require(isinstance(cannot_check, dict), "cannot-check block is absent")
    require(certain.get("matches_any_static_variant") is False, "static exclusion differs")
    require(
        certain.get("matches_any_empty_stderr_dynamic_variant") is False,
        "empty-stderr exclusion differs",
    )
    require(certain.get("dynamic_stderr_hash_variant") is True, "dynamic conclusion differs")
    require(certain.get("nvidia_smi_stderr_nonempty") is True, "nonempty conclusion differs")
    require(
        cannot_check.get("nvidia_smi_return_class")
        == "CANNOT_CHECK_NONZERO_RETURN_VS_ZERO_RETURN_WITH_STDERR",
        "return-code boundary was promoted or changed",
    )
    require(
        cannot_check.get("nvidia_smi_raw_stderr_content")
        == "CANNOT_CHECK_NOT_RETAINED",
        "raw stderr was promoted or changed",
    )
    require(
        classification.get("possible_dynamic_branches")
        == [
            "NONZERO_RETURN_WITH_NONEMPTY_STDERR",
            "ZERO_RETURN_WITH_NONEMPTY_STDERR",
        ],
        "possible branch set differs",
    )

    access = receipt.get("access_boundary")
    require(isinstance(access, dict), "access boundary is absent")
    require(access.get("protected_data_accessed") is False, "protected access promoted")
    require(access.get("generation_accessed") is False, "generation access promoted")
    require(access.get("scientific_authority") == "NONE", "scientific authority promoted")
    require(access.get("job_submission_authorized") is False, "submission was authorized")
    job_boundary = receipt.get("job_boundary")
    require(isinstance(job_boundary, dict), "job boundary is absent")
    for key in (
        "completion_requests",
        "generation_invocations",
        "official_outcomes_opened",
        "protected_packet_bodies_opened",
        "protected_prompt_bodies_opened",
        "tokenize_requests",
    ):
        require(job_boundary.get(key) == 0, "job boundary counter differs: " + key)
    require(job_boundary.get("official_evaluator_invoked") is False, "evaluator boundary differs")
    require(job_boundary.get("scientific_authority_delta") == "NONE", "job authority differs")

    proof = receipt.get("proof")
    require(isinstance(proof, dict), "proof block is absent")
    require(proof.get("static_variant_count") == 8, "proof static count differs")
    require(proof.get("dynamic_variant_count") == 2, "proof dynamic count differs")
    require(proof.get("gpu_identity_invalid_raise_site_count") == 10, "proof site count differs")
    require(proof.get("empty_stderr_sha256") == EMPTY_STDERR_SHA256, "empty digest differs")
    require(
        proof.get("outer_hash_construction")
        == 'sha256(b"GateError:" + detail.encode("utf-8"))',
        "outer hash construction declaration differs",
    )

    validate_mutation_rejection(module, source_raw)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        main_code = module.main()
    require(main_code == 0, "classifier main did not pass")
    require(stdout.getvalue().startswith(PASS_TERMINAL + " "), "classifier terminal differs")
    return raw


def main() -> int:
    try:
        validate_classifier_source()
        module = load_classifier()
        raw = validate_receipt(module)
    except Exception as exc:
        print(
            "P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_CANNOT_CHECK "
            + "validator_detail_sha256="
            + sha256_bytes((type(exc).__name__ + ":" + str(exc)).encode("utf-8")),
            file=sys.stderr,
        )
        return 1
    print(PASS_TERMINAL + " validator=PASS receipt_sha256=" + sha256_bytes(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
