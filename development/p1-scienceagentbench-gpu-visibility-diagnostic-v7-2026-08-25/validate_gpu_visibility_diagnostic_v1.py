#!/usr/bin/env python3
"""Hostile, synthetic-only validation for the V7 GPU visibility diagnostic.

This standard-library suite never submits a job, opens a protected body,
starts a model or server, uses a network route, or opens a real device node.
All dynamic diagnostic fixtures are created below temporary directories.
"""

from __future__ import annotations

import ast
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "gpu_visibility_diagnostic_v1.py"
CONTRACT_PATH = ROOT / "GPU_VISIBILITY_DIAGNOSTIC_CONTRACT_V1.json"
SCHEMA_PATH = ROOT / "GPU_VISIBILITY_DIAGNOSTIC_OUTPUT_SCHEMA_V1.json"
TRAMPOLINE_PATH = ROOT / "run_gpu_visibility_diagnostic_v1.sh"
HANDOFF_PATH = ROOT / "HANDOFF_V1.md"
PREDECESSOR_PATH = ROOT / "JOB_3537915_PREDECESSOR_BINDING_V1.json"
V6_DEPLOYMENT_FAILURE_PATH = ROOT / "V6_DEPLOYMENT_VALIDATION_FAILURE_BINDING_V1.json"
PREDECESSOR_SOURCE_ROOT = (
    ROOT.parent
    / "p1-scienceagentbench-backend-canonical-map-discriminator-v5-job-3537915-result-2026-08-25"
)
V6_DEPLOYMENT_FAILURE_SOURCE_ROOT = (
    ROOT.parent
    / "p1-scienceagentbench-gpu-visibility-diagnostic-v6-deployment-validation-result-2026-08-25"
)
DEPLOYMENT_ROOT = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "repo-gpu-visibility-v7-20260825"
)
RUN_ROOT = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "live-gpu-visibility-v7-20260825"
)
OUTPUT_ROOT = RUN_ROOT + "/evidence"
EXPECTED_ENV_ALLOWLIST = [
    "SLURM_JOB_ID",
    "SLURMD_NODENAME",
    "SLURM_JOB_GPUS",
    "SLURM_STEP_GPUS",
    "CUDA_VISIBLE_DEVICES",
]
EXPECTED_UNSCOPED_ARGV = [
    "/usr/bin/nvidia-smi",
    "--query-gpu=index,uuid,name",
    "--format=csv,noheader,nounits",
]
EXPECTED_LIST_ARGV = ["/usr/bin/nvidia-smi", "-L"]
TEST_CHILD_PYTHON = "/usr/bin/python3"
EXPECTED_SBATCH = [
    "#SBATCH --job-name=p1_sab_gpu_visibility_v1",
    "#SBATCH --account=lu2026-2-51",
    "#SBATCH --partition=gpua40i",
    "#SBATCH --exclude=cg14",
    "#SBATCH --gres=gpu:a40:1",
    "#SBATCH --nodes=1",
    "#SBATCH --ntasks=1",
    "#SBATCH --cpus-per-task=1",
    "#SBATCH --mem=4G",
    "#SBATCH --time=00:10:00",
    "#SBATCH --signal=B:TERM@120",
]
EXPECTED_PREDECESSOR_ARTIFACTS = {
    "GPU_IDENTITY_FAILURE_CLASSIFICATION_V2.json": (
        7557,
        "abfc0d0ddddff00412554bc00d59e24e1bb1c811062e87d03b0b18f943a3ce0c",
    ),
    "JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json": (
        1883,
        "2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3",
    ),
    "JOB_3537915_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V2.json": (
        7161,
        "44054d293392d480ca8c4f154f963a3dbb60600a156e042432eab44aa2e63cc5",
    ),
    "NVIDIA_SMI_RETURN_VALUE_SOURCE_V1.txt": (
        917,
        "a95583b6d96309dc823b04a7b89f62d7ee2b81847bd2f75b119c97911c6a56a3",
    ),
    "RESULT_EXPORT_MANIFEST_V2.json": (
        5322,
        "9ffdb5135cf4848863cb49d604a86af7747cbbaf7a241bba627c8f460d33decd",
    ),
    "SHA256SUMS": (
        1728,
        "c169ef799b79ec6c3537e32d61f66fbf9bb3628d82484762b3d2b60fe7841434",
    ),
    "SUBMIT_LINE_AND_RESIDUAL_EVIDENCE.txt": (
        986,
        "7fbb2febbb14b1efd8b2477120a0b6cbfb81f0b5a6820e0817233fb984fbca72",
    ),
    "slurm-3537915.err": (
        172,
        "c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e",
    ),
    "slurm-3537915.out": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
}
EXPECTED_V6_DEPLOYMENT_FAILURE_ARTIFACTS = {
    "DEPLOYMENT_EVIDENCE.txt": (
        722,
        "fe0dee48d672121a73315c4c484abf4e7c0026700129890d157a1d8f39235ed3",
    ),
    "DEPLOYMENT_VALIDATION_FAILURE_V1.json": (
        3481,
        "704f58a1e86653da0664f036c8879c3148a044a985f1d6ea51e1190f890c8db6",
    ),
    "DEVELOPMENT_PACKET.md": (
        4643,
        "6afd3e7bd904df7b7f38ea7c894ee890b9d49c2b68fc76b84d61dd47b9c954e9",
    ),
    "REMOTE_DEPLOYMENT_SCRIPT_V1.sh": (
        2841,
        "0e307de6b0ab46dbff8b65848bcc451d27fcd35b1bd64a6fe6e77e58d471dd12",
    ),
    "RESULT_EXPORT_MANIFEST_V1.json": (
        1743,
        "26e76cb210c998440ffc16c8dedbdc72a8b294e7ba8e8db8efe37641530cce88",
    ),
    "SANITIZED_INTERPRETER_PROBE.txt": (
        403,
        "2afe09d67c50147c2dccfd309f5d0bd8c61a7b33a8e1db42eb00727d47a8bb44",
    ),
    "SHA256SUMS": (
        669,
        "5f70406596941090d200af627055fb6ba663b9b6c3f1869d130d7cc880071c42",
    ),
    "VALIDATOR_FAILURE_OUTPUT.txt": (
        10551,
        "c0b6099a0f08eee01cdda40e2147e8e509ee0d8e62e1a219394a95f4936bc67d",
    ),
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def shell_assignment(source: str, name: str) -> str:
    matches = re.findall(rf"(?m)^{re.escape(name)}='([^']*)'$", source)
    if len(matches) != 1:
        raise AssertionError(f"{name} assignment count is {len(matches)}, not one")
    return matches[0]


def normalized_trampoline_sha256(payload: bytes) -> str:
    pattern = re.compile(rb"(?m)^NORMALIZED_TRAMPOLINE_SHA256='([0-9a-f]{64})'$")
    normalized, count = pattern.subn(
        b"NORMALIZED_TRAMPOLINE_SHA256='" + (b"0" * 64) + b"'", payload
    )
    if count != 1:
        raise AssertionError(
            f"normalized trampoline self-binding count is {count}, not one"
        )
    return sha256_bytes(normalized)


def load_canonical(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON object")
    expected = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    if raw != expected:
        raise AssertionError(f"{path.name} is not canonical JSON plus one LF")
    return value, raw


def load_module() -> ModuleType:
    if not MODULE_PATH.is_file():
        raise AssertionError("GPU visibility diagnostic module is absent")
    spec = importlib.util.spec_from_file_location(
        "gpu_visibility_diagnostic_v1_under_test", MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("GPU visibility diagnostic module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def patched_environ(values: dict[str, str]) -> Iterator[None]:
    saved = dict(os.environ)
    os.environ.clear()
    os.environ.update(values)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


@contextlib.contextmanager
def patched_attribute(target: Any, name: str, value: Any) -> Iterator[None]:
    original = getattr(target, name)
    setattr(target, name, value)
    try:
        yield
    finally:
        setattr(target, name, original)


def raw_binding(payload: bytes, *, complete: bool = True) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(payload).decode("ascii"),
        "bytes": len(payload),
        "complete": complete,
        "encoding": "base64",
        "sha256": sha256_bytes(payload),
    }


def completed_capture(
    argv: list[str], stdout: bytes, stderr: bytes = b"", return_code: int = 0
) -> dict[str, Any]:
    return {
        "status": "COMPLETED",
        "argv": argv,
        "return_code": return_code,
        "stdout": raw_binding(stdout),
        "stderr": raw_binding(stderr),
        "stdout_parse_attempted": False,
    }


def complete_command_set(
    *, list_rc: int = 0, unscoped_rc: int = 0, scoped_rc: int = 0
) -> dict[str, Any]:
    return {
        "nvidia_smi_list": completed_capture(EXPECTED_LIST_ARGV, b"", return_code=list_rc),
        "unscoped_identity": completed_capture(
            EXPECTED_UNSCOPED_ARGV, b"", return_code=unscoped_rc
        ),
        "scoped_identity": completed_capture(
            ["/usr/bin/nvidia-smi", "--id=0", *EXPECTED_UNSCOPED_ARGV[1:]],
            b"",
            return_code=scoped_rc,
        ),
    }


class GPUVisibilityDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.contract, cls.contract_raw = load_canonical(CONTRACT_PATH)
        cls.schema, cls.schema_raw = load_canonical(SCHEMA_PATH)
        cls.predecessor, cls.predecessor_raw = load_canonical(PREDECESSOR_PATH)
        cls.v6_deployment_failure, cls.v6_deployment_failure_raw = load_canonical(
            V6_DEPLOYMENT_FAILURE_PATH
        )

    def assert_gate(self, code: str, function: Any, *args: Any, **kwargs: Any) -> Any:
        with self.assertRaises(self.module.GateError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_01_packet_inputs_are_canonical_and_frozen(self) -> None:
        self.assertEqual(
            self.contract["schema_version"],
            "orion.p1.scienceagentbench.gpu-visibility-diagnostic-contract.v1",
        )
        self.assertEqual(
            self.schema["schema_version"],
            "orion.p1.scienceagentbench.gpu-visibility-diagnostic-output-schema.v1",
        )
        self.assertEqual(self.contract["status"], "FROZEN_NOT_EXECUTED")
        self.assertEqual(self.schema["status"], "FROZEN_NOT_EXECUTED")
        self.assertIs(self.contract["submission_authority"], False)
        self.assertIs(self.schema["submission_authority"], False)
        self.assertEqual(
            self.contract["validation_policy"],
            {
                "live_command_environment_broadened": False,
                "repair_scope": "VALIDATOR_FIXTURE_ONLY",
                "test_child_interpreter": "/usr/bin/python3",
                "test_child_launch_count_in_tests_24_25": 3,
            },
        )
        self.assertEqual(TEST_CHILD_PYTHON, "/usr/bin/python3")
        validator_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        self.assertEqual(
            [
                node
                for node in ast.walk(validator_tree)
                if isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "sys"
                and node.attr == "executable"
            ],
            [],
        )
        portability_tests = [
            node
            for node in ast.walk(validator_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name
            in {
                "test_24_bounded_command_retains_exact_bodies_hashes_and_rc",
                "test_25_bounded_command_fails_closed_at_stream_cap",
            }
        ]
        self.assertEqual(len(portability_tests), 2)
        child_launches: list[ast.Call] = []
        for function in portability_tests:
            assignments = {
                target.id: statement.value
                for statement in function.body
                if isinstance(statement, ast.Assign)
                for target in statement.targets
                if isinstance(target, ast.Name)
            }
            calls = [
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "bounded_command"
            ]
            child_launches.extend(calls)
            for call in calls:
                self.assertTrue(call.args)
                argv_node = call.args[0]
                if isinstance(argv_node, ast.Name):
                    argv_node = assignments.get(argv_node.id)
                self.assertIsInstance(argv_node, ast.List)
                self.assertGreaterEqual(len(argv_node.elts), 5)
                self.assertIsInstance(argv_node.elts[0], ast.Name)
                self.assertEqual(argv_node.elts[0].id, "TEST_CHILD_PYTHON")
                self.assertEqual(
                    [
                        item.value if isinstance(item, ast.Constant) else None
                        for item in argv_node.elts[1:5]
                    ],
                    ["-I", "-S", "-B", "-c"],
                )
        self.assertEqual(len(child_launches), 3)

    def test_02_fresh_root_geometry_is_exact(self) -> None:
        self.assertEqual(
            self.contract["paths"],
            {
                "deployment_root": DEPLOYMENT_ROOT,
                "output_root": OUTPUT_ROOT,
                "run_root": RUN_ROOT,
            },
        )
        self.assertTrue(all(Path(value).is_absolute() for value in self.contract["paths"].values()))
        self.assertEqual(Path(OUTPUT_ROOT).parent, Path(RUN_ROOT))
        self.assertNotEqual(DEPLOYMENT_ROOT, RUN_ROOT)
        self.assertNotIn("successor-v5", " ".join(self.contract["paths"].values()))
        self.assertNotIn("gpu-visibility-v6", " ".join(self.contract["paths"].values()))

    def test_03_allocation_is_small_and_excludes_cg14(self) -> None:
        self.assertEqual(
            self.contract["allocation"],
            {
                "account": "lu2026-2-51",
                "cpus": 1,
                "exact_visible_gpu_count": 1,
                "excluded_nodes": ["cg14"],
                "gres": "gpu:a40:1",
                "memory": "4G",
                "nodes": 1,
                "partition": "gpua40i",
                "scheduler": "SLURM",
                "site": "LUNARC",
                "tasks": 1,
                "time_limit": "00:10:00",
            },
        )

    def test_04_different_node_is_diagnostic_not_causal(self) -> None:
        policy = self.contract["decision_policy"]
        self.assertEqual(
            policy["node_change_interpretation"],
            "NODE_CHANGE_DIAGNOSTIC_ONLY__NO_CAUSAL_PROOF",
        )
        self.assertIs(self.predecessor["no_promotion"]["node_change_is_causal_proof"], False)
        self.assertEqual(self.predecessor["job"]["node"], "cg14")
        self.assertEqual(
            self.schema["node_change_diagnostic"]["excluded_predecessor_node"], "cg14"
        )

    def test_05_body_free_truth_boundary_is_all_zero(self) -> None:
        for key in ("protected_packet_bodies_opened", "protected_prompt_bodies_opened"):
            self.assertEqual(self.contract[key], 0)
        self.assertEqual(self.contract["task_bearing_requests"], 0)
        self.assertIs(self.contract["official_evaluator_invoked"], False)
        self.assertEqual(self.contract["official_outcomes_opened"], 0)
        self.assertEqual(self.contract["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(self.contract["scientific_authority_delta"], "NONE")

    def test_06_forbidden_operations_close_server_model_network_and_task_routes(self) -> None:
        self.assertEqual(
            self.contract["forbidden_operations"],
            [
                "model load",
                "server start",
                "network access",
                "protected packet or prompt open",
                "task-bearing route",
                "tokenize request",
                "completion request",
                "generation",
                "official evaluator",
                "official outcome access",
                "device read",
                "device ioctl",
            ],
        )
        boundary = self.schema["truthful_boundary"]
        self.assertIs(boundary["model_started"], False)
        self.assertIs(boundary["network_accessed"], False)
        self.assertIs(boundary["protected_or_task_routes_reachable"], False)

    def test_07_module_imports_are_stdlib_and_have_no_network_stack(self) -> None:
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertFalse(imports & {"http", "socket", "urllib", "requests", "aiohttp"})
        expected_stdlib_imports = {
            "__future__",
            "argparse",
            "base64",
            "errno",
            "hashlib",
            "json",
            "os",
            "pathlib",
            "re",
            "selectors",
            "signal",
            "stat",
            "subprocess",
            "sys",
            "time",
            "typing",
        }
        self.assertEqual(imports, expected_stdlib_imports)
        runtime_stdlib = set(getattr(sys, "stdlib_module_names", ()))
        if runtime_stdlib:
            self.assertTrue(
                imports - {"__future__"} <= runtime_stdlib,
                f"non-stdlib imports: {sorted(imports - runtime_stdlib)}",
            )

    def test_08_module_has_no_server_model_or_task_route_literals(self) -> None:
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))
        literals = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        joined = "\n".join(literals).lower()
        for forbidden in ("/tokenize", "/completion", "llama-server", ".gguf", "127.0.0.1:8080"):
            self.assertNotIn(forbidden, joined)

    def test_09_environment_allowlist_and_caps_are_exact(self) -> None:
        policy = self.contract["diagnostic_policy"]
        self.assertEqual(policy["environment_allowlist"], EXPECTED_ENV_ALLOWLIST)
        self.assertEqual(policy["environment_value_byte_cap"], 4096)
        self.assertEqual(
            policy["command_environment"],
            {"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(self.schema["environment_capture"]["allowlist"], EXPECTED_ENV_ALLOWLIST)

    def test_10_device_inventory_is_metadata_and_open_only_bounded(self) -> None:
        policy = self.contract["diagnostic_policy"]
        self.assertEqual(policy["device_root"], "/dev")
        self.assertEqual(policy["device_entry_cap"], 64)
        self.assertEqual(policy["device_name_byte_cap"], 255)
        self.assertIn("device read", self.contract["forbidden_operations"])
        self.assertIn("device ioctl", self.contract["forbidden_operations"])

    def test_11_cgroup_sources_and_caps_are_exact(self) -> None:
        policy = self.contract["diagnostic_policy"]
        self.assertEqual(policy["proc_cgroup_path"], "/proc/self/cgroup")
        self.assertEqual(policy["proc_cgroup_byte_cap"], 65536)
        self.assertEqual(policy["mountinfo_path"], "/proc/self/mountinfo")
        self.assertEqual(policy["mountinfo_read_byte_cap"], 1048576)
        self.assertEqual(policy["mountinfo_selected_byte_cap"], 131072)

    def test_12_three_command_argv_templates_are_exact(self) -> None:
        commands = self.contract["diagnostic_policy"]["commands"]
        self.assertEqual(commands["nvidia_smi_list"], EXPECTED_LIST_ARGV)
        self.assertEqual(commands["unscoped_identity"], EXPECTED_UNSCOPED_ARGV)
        self.assertEqual(
            commands["scoped_identity_template"],
            [
                "/usr/bin/nvidia-smi",
                "--id=<VALIDATED_CUDA_VISIBLE_DEVICES_TOKEN>",
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader,nounits",
            ],
        )

    def test_13_raw_capture_schema_binds_body_hash_bytes_and_completeness(self) -> None:
        raw = self.schema["raw_binding"]
        self.assertEqual(
            raw["required_fields"],
            ["base64", "bytes", "complete", "encoding", "sha256"],
        )
        self.assertEqual(raw["exact_encoding"], "base64")
        self.assertEqual(
            self.contract["diagnostic_policy"]["command_stream_byte_cap"], 65536
        )

    def test_14_parse_gate_is_only_rc0_and_empty_stderr(self) -> None:
        expected = (
            "COMMAND_STATUS_COMPLETED_AND_EXACT_INTEGER_RETURN_CODE_ZERO_AND_"
            "COMPLETE_VALID_STREAM_BINDINGS_AND_DECODED_STDERR_EMPTY"
        )
        self.assertEqual(
            self.contract["diagnostic_policy"]["stdout_parse_eligibility"],
            expected,
        )
        self.assertEqual(
            self.schema["command_capture"]["parse_eligible_only_if"],
            expected,
        )

    def test_15_output_custody_is_new_create_only_and_read_only(self) -> None:
        self.assertEqual(
            self.contract["output_policy"],
            {
                "cannot_check_file": "GPU_VISIBILITY_DIAGNOSTIC_CANNOT_CHECK_V1.json",
                "output_directory_mode_after_receipt": "0500",
                "output_directory_must_be_new": True,
                "raw_diagnostic_bodies_retained_under_caps": True,
                "receipt_file_mode": "0400",
                "receipt_write": "O_EXCL_O_NOFOLLOW_IF_AVAILABLE_FSYNC_REREAD",
                "success_file": "GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json",
            },
        )
        self.assertEqual(self.schema["output_custody"], self.contract["output_policy"])

    def test_16_predecessor_binding_is_exact_and_nonpromoting(self) -> None:
        self.assertEqual(
            self.contract["predecessor"]["binding"],
            {
                "bytes": len(self.predecessor_raw),
                "file": PREDECESSOR_PATH.name,
                "sha256": sha256_bytes(self.predecessor_raw),
            },
        )
        self.assertEqual(self.predecessor["status"], "PASS_BOUND_JOB_3537915_ADVERSE_PREDECESSOR")
        self.assertEqual(self.predecessor["result"]["failure_code"], "GPU_IDENTITY_INVALID")
        self.assertEqual(self.predecessor["result"]["failure_subcode"], "NVIDIA_SMI_NONZERO_RETURN")
        self.assertEqual(self.predecessor["result"]["gpu_identity"], "CANNOT_CHECK")
        self.assertFalse(any(self.predecessor["no_promotion"].values()))

    def test_17_predecessor_gpu_capture_and_rc6_are_exact(self) -> None:
        self.assertEqual(
            self.predecessor["gpu_capture"],
            {
                "argv": EXPECTED_UNSCOPED_ARGV,
                "return_code": 6,
                "status": "COMPLETED",
                "stderr": {
                    "bytes": 76,
                    "sha256": "0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a",
                },
                "stdout": {
                    "bytes": 22,
                    "sha256": "cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd",
                },
                "stdout_parse_attempted": False,
            },
        )
        self.assertEqual(
            self.contract["decision_policy"]["rc6_interpretation"],
            "GENERIC_UNSUCCESSFUL_OBJECT_QUERY_ONLY__NO_MISSING_OBJECT_OR_ROOT_CAUSE_INFERENCE",
        )

    def test_18_predecessor_artifact_bytes_and_hashes_are_exact(self) -> None:
        self.assertEqual(set(self.predecessor["artifacts"]), set(EXPECTED_PREDECESSOR_ARTIFACTS))
        for name, (expected_bytes, expected_sha256) in EXPECTED_PREDECESSOR_ARTIFACTS.items():
            raw = (PREDECESSOR_SOURCE_ROOT / name).read_bytes()
            self.assertEqual((len(raw), sha256_bytes(raw)), (expected_bytes, expected_sha256))
            self.assertEqual(
                self.predecessor["artifacts"][name],
                {"bytes": expected_bytes, "sha256": expected_sha256},
            )

    def test_19_predecessors_are_separate_and_v7_cost_not_preclaimed(self) -> None:
        self.assertEqual(
            self.predecessor["accounting_after_job_3537915"],
            {
                "body_free_discriminator_scheduler_gpu_seconds": 170,
                "body_free_discriminator_submissions_completed": 2,
                "combined_scheduler_gpu_seconds": 260,
                "protected_generation_attempts_consumed": 0,
                "protected_infrastructure_scheduler_gpu_seconds": 90,
                "protected_infrastructure_submissions_completed": 3,
            },
        )
        self.assertEqual(self.contract["predecessor"]["scheduler_gpu_seconds_before_v7"], 260)
        self.assertEqual(
            self.contract["predecessor"]["result_commit"],
            "9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67",
        )
        deployment_binding = self.contract["deployment_validation_predecessor"]
        self.assertEqual(
            deployment_binding["binding"],
            {
                "bytes": len(self.v6_deployment_failure_raw),
                "file": V6_DEPLOYMENT_FAILURE_PATH.name,
                "sha256": sha256_bytes(self.v6_deployment_failure_raw),
            },
        )
        self.assertEqual(
            deployment_binding["result_commit"],
            "598fa94273349094848659b7e3357a494e294b5a",
        )
        self.assertEqual(
            self.v6_deployment_failure["bound_at_merged_result_commit"],
            deployment_binding["result_commit"],
        )
        self.assertNotEqual(
            deployment_binding["result_commit"],
            self.contract["predecessor"]["result_commit"],
        )
        self.assertEqual(
            self.v6_deployment_failure["scientific_predecessor"],
            {
                "job_id": "3537915",
                "result_commit": "9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67",
                "unchanged": True,
            },
        )
        self.assertEqual(
            self.v6_deployment_failure["status"],
            "PASS_BOUND_V6_DEPLOYMENT_VALIDATION_FAILURE",
        )
        self.assertEqual(
            self.v6_deployment_failure["failure"],
            {
                "code": "SANITIZED_SELF_INTERPRETER_NOT_EXECUTABLE",
                "exact_loader_diagnostic": (
                    "/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/"
                    "bin/python3: error while loading shared libraries: "
                    "libpython3.11.so.1.0: cannot open shared object file: "
                    "No such file or directory"
                ),
                "failed_tests": [24, 25],
                "normal_validator_failures": 2,
                "normal_validator_tests_run": 50,
                "observed_child_return_code": 127,
                "subcode": "LIBPYTHON_NOT_FOUND_UNDER_COMMAND_ENVIRONMENT",
            },
        )
        self.assertEqual(
            set(self.v6_deployment_failure["artifacts"]),
            set(EXPECTED_V6_DEPLOYMENT_FAILURE_ARTIFACTS),
        )
        for name, (expected_bytes, expected_sha256) in (
            EXPECTED_V6_DEPLOYMENT_FAILURE_ARTIFACTS.items()
        ):
            raw = (V6_DEPLOYMENT_FAILURE_SOURCE_ROOT / name).read_bytes()
            self.assertEqual(
                (len(raw), sha256_bytes(raw)),
                (expected_bytes, expected_sha256),
            )
            self.assertEqual(
                self.v6_deployment_failure["artifacts"][name],
                {"bytes": expected_bytes, "sha256": expected_sha256},
            )

    def test_20_all_decisions_remain_diagnostic_only(self) -> None:
        expected = [
            "VISIBLE_A40_IDENTITY_BOUND",
            "UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND",
            "NVIDIA_DEVICE_NODES_ABSENT",
            "DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK",
            "NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES",
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE",
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        ]
        self.assertEqual(self.contract["decision_policy"]["decision_order"], expected)
        self.assertEqual(self.contract["decision_policy"]["outputs"], expected)
        self.assertEqual(
            self.contract["decision_policy"]["rc6_decision_requirements"],
            [
                "ALL_THREE_COMMANDS_STATUS_COMPLETED",
                "ALL_THREE_COMMAND_ARGV_FROZEN",
                "ALL_THREE_RETURN_CODES_EXACT_INTEGER_6",
                "ALL_SIX_COMMAND_STREAMS_COMPLETE",
                "ALL_SIX_RAW_BINDINGS_VALID",
                "ALL_THREE_STDOUT_PARSE_ATTEMPTED_FALSE",
                "ALL_THREE_PARSED_STATUSES_NOT_PARSE_ELIGIBLE",
                "ALL_THREE_PARSED_IDENTITIES_NULL",
            ],
        )
        self.assertEqual(self.schema["decision_outputs"], expected)
        self.assertEqual(self.schema["truthful_boundary"]["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(self.schema["truthful_boundary"]["scientific_authority_delta"], "NONE")

    def test_21_environment_capture_retains_only_allowlist_with_raw_bindings(self) -> None:
        source = {
            b"SLURM_JOB_ID": b"4000000",
            b"SLURMD_NODENAME": b"cg15",
            b"SLURM_JOB_GPUS": b"GPU-synthetic",
            b"SLURM_STEP_GPUS": b"GPU-synthetic",
            b"CUDA_VISIBLE_DEVICES": b"0",
            b"SECRET_MUST_NOT_BE_CAPTURED": b"synthetic-secret",
        }
        captured = self.module.capture_environment(source)
        self.assertEqual(captured["allowlist"], EXPECTED_ENV_ALLOWLIST)
        self.assertEqual(set(captured["variables"]), set(EXPECTED_ENV_ALLOWLIST))
        self.assertNotIn("SECRET_MUST_NOT_BE_CAPTURED", repr(captured))
        self.assertIs(captured["validation_complete"], True)
        for name in EXPECTED_ENV_ALLOWLIST:
            payload = source[name.encode("ascii")]
            self.assertEqual(captured["variables"][name]["raw"], raw_binding(payload))

    def test_22_environment_rejects_cg14_alias_token_and_oversize(self) -> None:
        common = {
            b"SLURM_JOB_ID": b"4000000",
            b"SLURM_JOB_GPUS": b"0",
            b"SLURM_STEP_GPUS": b"0",
        }
        excluded = self.module.capture_environment(
            {**common, b"SLURMD_NODENAME": b"cg14", b"CUDA_VISIBLE_DEVICES": b"0,1"}
        )
        self.assertIs(excluded["scheduler_node_valid_and_changed"], False)
        self.assertIs(excluded["cuda_visible_devices_token_valid"], False)
        self.assertIs(excluded["validation_complete"], False)
        oversized = self.module.capture_environment(
            {
                **common,
                b"SLURMD_NODENAME": b"cg15",
                b"CUDA_VISIBLE_DEVICES": b"7" * 4097,
            }
        )
        binding = oversized["variables"]["CUDA_VISIBLE_DEVICES"]["raw"]
        self.assertEqual(binding["bytes"], 4096)
        self.assertIs(binding["complete"], False)
        self.assertIs(oversized["capture_complete"], False)

    def test_23_scoped_argv_accepts_one_decimal_or_uuid_and_rejects_aliases(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        self.assertEqual(
            self.module.scoped_identity_argv("0"),
            ["/usr/bin/nvidia-smi", "--id=0", *EXPECTED_UNSCOPED_ARGV[1:]],
        )
        self.assertEqual(
            self.module.scoped_identity_argv(uuid),
            ["/usr/bin/nvidia-smi", f"--id={uuid}", *EXPECTED_UNSCOPED_ARGV[1:]],
        )
        for invalid in ("", "00", "0,1", " 0", "0 ", "GPU-nope", "0\x00"):
            self.assert_gate("ENVIRONMENT_INVALID", self.module.scoped_identity_argv, invalid)

    def test_24_bounded_command_retains_exact_bodies_hashes_and_rc(self) -> None:
        stdout = b"synthetic-stdout\x00\xff\n"
        stderr = b"synthetic-stderr\n"
        script = (
            "import os,sys;"
            f"os.write(1,{stdout!r});"
            f"os.write(2,{stderr!r});"
            "sys.exit(6)"
        )
        self.assertEqual(TEST_CHILD_PYTHON, "/usr/bin/python3")
        argv = [TEST_CHILD_PYTHON, "-I", "-S", "-B", "-c", script]
        capture = self.module.bounded_command(argv, timeout_seconds=10, stream_byte_cap=1024)
        self.assertEqual(capture["status"], "COMPLETED")
        self.assertEqual(capture["argv"], argv)
        self.assertEqual(capture["return_code"], 6)
        self.assertEqual(capture["stdout"], raw_binding(stdout))
        self.assertEqual(capture["stderr"], raw_binding(stderr))
        self.assertIs(capture["stdout_parse_attempted"], False)

    def test_25_bounded_command_fails_closed_at_stream_cap(self) -> None:
        script = "import os;os.write(1,b'x'*65)"
        capture = self.module.bounded_command(
            [TEST_CHILD_PYTHON, "-I", "-S", "-B", "-c", script],
            timeout_seconds=10,
            stream_byte_cap=64,
        )
        self.assertEqual(capture["status"], "OUTPUT_LIMIT")
        self.assertEqual(capture["stdout"], raw_binding(b"x" * 64, complete=False))
        self.assertIs(capture["stderr"]["complete"], False)
        self.assertIs(capture["stdout_parse_attempted"], False)
        timeout = self.module.bounded_command(
            [
                TEST_CHILD_PYTHON,
                "-I",
                "-S",
                "-B",
                "-c",
                "import time;time.sleep(10)",
            ],
            timeout_seconds=0.05,
            stream_byte_cap=64,
        )
        self.assertEqual(timeout["status"], "TIMEOUT")
        self.assertIs(timeout["stdout"]["complete"], False)
        self.assertIs(timeout["stderr"]["complete"], False)
        self.assertIs(timeout["stdout_parse_attempted"], False)

    def test_26_parse_one_a40_binds_exact_identity_body(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        body = f"0, {uuid}, NVIDIA A40\n".encode("ascii")
        capture = completed_capture(EXPECTED_UNSCOPED_ARGV, body)
        parsed = self.module.parse_identity_capture(capture)
        self.assertEqual(
            parsed,
            {
                "identity": {"gpu_uuid": uuid, "index": "0", "name": "NVIDIA A40"},
                "status": "PARSED_ONE_A40",
            },
        )
        self.assertEqual(capture["stdout"], raw_binding(body))
        self.assertIs(capture["stdout_parse_attempted"], True)

    def test_27_list_parse_one_a40_binds_exact_identity_body(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        body = f"GPU 0: NVIDIA A40 (UUID: {uuid})\n".encode("ascii")
        capture = completed_capture(EXPECTED_LIST_ARGV, body)
        parsed = self.module.parse_list_capture(capture)
        self.assertEqual(parsed["status"], "PARSED_ONE_A40")
        self.assertEqual(parsed["identity"], {"gpu_uuid": uuid, "index": "0", "name": "NVIDIA A40"})
        self.assertEqual(capture["stdout"], raw_binding(body))
        self.assertIs(capture["stdout_parse_attempted"], True)

    def test_28_nonzero_or_nonempty_stderr_is_never_parsed(self) -> None:
        body = b"0, GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee, NVIDIA A40\n"
        nonzero = completed_capture(EXPECTED_UNSCOPED_ARGV, body, return_code=6)
        stderr = completed_capture(EXPECTED_UNSCOPED_ARGV, body, b"warning\n", 0)
        self.assertEqual(
            self.module.parse_identity_capture(nonzero),
            {"identity": None, "status": "NOT_PARSE_ELIGIBLE"},
        )
        self.assertEqual(
            self.module.parse_identity_capture(stderr),
            {"identity": None, "status": "NOT_PARSE_ELIGIBLE"},
        )
        self.assertIs(nonzero["stdout_parse_attempted"], False)
        self.assertIs(stderr["stdout_parse_attempted"], False)

    def test_29_malformed_identity_bodies_fail_closed_after_eligible_parse(self) -> None:
        cases = (
            (b"", "VISIBLE_ROW_COUNT_INVALID"),
            (b"0, GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee, NVIDIA A40", "STDOUT_FRAMING_INVALID"),
            (b"0, not-a-uuid, NVIDIA A40\n", "VISIBLE_ROW_INVALID"),
            (b"0, GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee, NVIDIA A40\n1, GPU-11111111-2222-3333-4444-555555555555, NVIDIA A40\n", "VISIBLE_ROW_COUNT_INVALID"),
            (b"\xff\n", "STDOUT_UTF8_INVALID"),
        )
        for body, status_name in cases:
            capture = completed_capture(EXPECTED_UNSCOPED_ARGV, body)
            self.assertEqual(self.module.parse_identity_capture(capture)["status"], status_name)
            self.assertIs(capture["stdout_parse_attempted"], True)

    def test_30_corrupt_raw_binding_is_rejected_not_reinterpreted(self) -> None:
        body = b"0, GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee, NVIDIA A40\n"
        capture = completed_capture(EXPECTED_UNSCOPED_ARGV, body)
        capture["stdout"]["sha256"] = "0" * 64
        self.assert_gate("EVIDENCE_INVALID", self.module.parse_identity_capture, capture)

    def test_31_positive_unscoped_a40_classification_requires_three_matches(self) -> None:
        identity = {
            "identity": {
                "gpu_uuid": "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "index": "0",
                "name": "NVIDIA A40",
            },
            "status": "PARSED_ONE_A40",
            "scope_token_matches_identity": True,
        }
        context = {
            "evidence_complete": True,
            "device_inventory": {
                "character_device_count": 2,
                "entries": [{"path": "/synthetic/nvidia0"}],
                "read_only_open_denied_count": 0,
            },
            "commands": complete_command_set(),
            "parsed_identities": {
                "nvidia_smi_list": dict(identity),
                "unscoped_identity": dict(identity),
                "scoped_identity": dict(identity),
            },
        }
        self.assertEqual(
            self.module.classify_diagnostic(context), "VISIBLE_A40_IDENTITY_BOUND"
        )
        context["parsed_identities"]["scoped_identity"] = {
            "identity": None,
            "status": "VISIBLE_ROW_INVALID",
        }
        self.assertEqual(
            self.module.classify_diagnostic(context),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE",
        )

    def test_32_scoped_recovery_classification_requires_nonzero_unscoped(self) -> None:
        scoped = {
            "identity": {
                "gpu_uuid": "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "index": "0",
                "name": "NVIDIA A40",
            },
            "status": "PARSED_ONE_A40",
            "scope_token_matches_identity": True,
        }
        context = {
            "evidence_complete": True,
            "device_inventory": {
                "character_device_count": 1,
                "entries": [{}],
                "read_only_open_denied_count": 0,
            },
            "commands": complete_command_set(unscoped_rc=6),
            "parsed_identities": {
                "nvidia_smi_list": {"identity": None, "status": "NOT_PARSE_ELIGIBLE"},
                "unscoped_identity": {"identity": None, "status": "NOT_PARSE_ELIGIBLE"},
                "scoped_identity": scoped,
            },
        }
        self.assertEqual(
            self.module.classify_diagnostic(context),
            "UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND",
        )

    def test_33_generic_rc6_and_no_device_classification_follow_frozen_order(self) -> None:
        commands = complete_command_set(list_rc=6, unscoped_rc=6, scoped_rc=6)
        for capture in commands.values():
            capture["stdout"] = raw_binding(b"arbitrary-complete-rc6-body\n")
            capture["stderr"] = raw_binding(b"arbitrary-complete-rc6-stderr\n")
        parsed = {
            name: {"identity": None, "status": "NOT_PARSE_ELIGIBLE"}
            for name in commands
        }
        base = {
            "evidence_complete": True,
            "commands": commands,
            "parsed_identities": parsed,
        }
        with_nodes = {
            **base,
            "device_inventory": {
                "character_device_count": 1,
                "entries": [{}],
                "read_only_open_denied_count": 0,
            },
        }
        no_nodes = {
            **base,
            "device_inventory": {
                "character_device_count": 0,
                "entries": [],
                "read_only_open_denied_count": 0,
            },
        }
        self.assertEqual(
            self.module.classify_diagnostic(with_nodes),
            "NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES",
        )
        self.assertEqual(
            self.module.classify_diagnostic(no_nodes), "NVIDIA_DEVICE_NODES_ABSENT"
        )
        bool_rc = json.loads(json.dumps(with_nodes))
        bool_rc["commands"]["nvidia_smi_list"]["return_code"] = True
        self.assertEqual(
            self.module.classify_diagnostic(bool_rc),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )
        incomplete_stream = json.loads(json.dumps(with_nodes))
        incomplete_stream["commands"]["scoped_identity"]["stdout"]["complete"] = False
        self.assertEqual(
            self.module.classify_diagnostic(incomplete_stream),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )
        corrupt_binding = json.loads(json.dumps(with_nodes))
        corrupt_binding["commands"]["unscoped_identity"]["stderr"]["sha256"] = "0" * 64
        self.assertEqual(
            self.module.classify_diagnostic(corrupt_binding),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )
        alias_argv = json.loads(json.dumps(with_nodes))
        alias_argv["commands"]["scoped_identity"]["argv"][1] = "--id=0,1"
        self.assertEqual(
            self.module.classify_diagnostic(alias_argv),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )
        extra_command = json.loads(json.dumps(with_nodes))
        extra_command["commands"]["unexpected_alias"] = extra_command["commands"][
            "nvidia_smi_list"
        ]
        self.assertEqual(
            self.module.classify_diagnostic(extra_command),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )

    def test_34_incomplete_and_access_restricted_classifications_fail_closed(self) -> None:
        incomplete = {"evidence_complete": False}
        self.assertEqual(
            self.module.classify_diagnostic(incomplete),
            "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE",
        )
        restricted = {
            "evidence_complete": True,
            "device_inventory": {
                "character_device_count": 1,
                "entries": [{}],
                "read_only_open_denied_count": 1,
            },
            "commands": complete_command_set(list_rc=6, unscoped_rc=6, scoped_rc=6),
            "parsed_identities": {},
        }
        self.assertEqual(
            self.module.classify_diagnostic(restricted),
            "DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK",
        )

    def test_35_device_inventory_never_reads_or_follows_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "ordinary-target"
            target.write_bytes(b"MUST_NOT_BE_READ")
            regular = root / "nvidia0"
            regular.write_bytes(b"MUST_NOT_BE_READ")
            alias = root / "nvidia-alias"
            alias.symlink_to(target)
            inventory = self.module.capture_device_inventory(root)
        self.assertEqual(inventory["discovered_entry_count"], 2)
        by_path = {Path(entry["path"]).name: entry for entry in inventory["entries"]}
        self.assertEqual(by_path["nvidia0"]["lstat"]["type"], "REGULAR_FILE")
        self.assertIs(by_path["nvidia0"]["read_only_open"]["opened"], True)
        self.assertEqual(by_path["nvidia-alias"]["lstat"]["type"], "SYMLINK")
        self.assertIs(by_path["nvidia-alias"]["read_only_open"]["opened"], False)
        for entry in inventory["entries"]:
            self.assertIs(entry["read_only_open"]["read_invoked"], False)
            self.assertIs(entry["read_only_open"]["ioctl_invoked"], False)

    def test_36_device_entry_cap_marks_inventory_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index in range(65):
                (root / f"nvidia{index:02d}").touch()
            inventory = self.module.capture_device_inventory(root)
        self.assertEqual(inventory["discovered_entry_count"], 65)
        self.assertEqual(len(inventory["entries"]), 64)
        self.assertIs(inventory["scan_complete"], False)

    def test_37_cgroup_capture_filters_exact_lines_and_enforces_caps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cgroup = root / "cgroup"
            mountinfo = root / "mountinfo"
            cgroup_body = b"0::/synthetic.slice\n"
            selected = b"36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n"
            mountinfo_body = b"1 2 0:1 / / rw - ext4 /dev/x rw\n" + selected
            cgroup.write_bytes(cgroup_body)
            mountinfo.write_bytes(mountinfo_body)
            evidence = self.module.capture_cgroup_evidence(cgroup, mountinfo)
            cgroup.write_bytes(b"x" * 65537)
            capped = self.module.capture_cgroup_evidence(cgroup, mountinfo)
        self.assertIs(evidence["capture_complete"], True)
        self.assertEqual(evidence["proc_self_cgroup"]["raw"], raw_binding(cgroup_body))
        self.assertEqual(
            evidence["proc_self_mountinfo"]["selected_cgroup_lines"]["raw"],
            raw_binding(selected),
        )
        self.assertEqual(capped["proc_self_cgroup"]["status"], "OUTPUT_LIMIT")
        self.assertIs(capped["capture_complete"], False)

    def test_38_source_alias_and_byte_cap_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.write_bytes(b"abc")
            alias = root / "alias"
            alias.symlink_to(target)
            self.assert_gate(
                "SOURCE_INVALID",
                self.module._read_bound_regular,
                alias,
                cap=16,
                label="synthetic alias",
            )
            target.write_bytes(b"x" * 17)
            self.assert_gate(
                "SOURCE_INVALID",
                self.module._read_bound_regular,
                target,
                cap=16,
                label="synthetic oversized source",
            )

    def test_39_receipt_write_is_create_only_and_preserves_existing_receipt(self) -> None:
        receipt = {"synthetic": True}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root_fd = os.open(root, self.module._directory_flags())
            try:
                self.module._write_receipt(root_fd, self.module.SUCCESS_NAME, receipt)
                path = root / self.module.SUCCESS_NAME
                original = path.read_bytes()
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)
                self.assert_gate(
                    "OUTPUT_WRITE_FAILED",
                    self.module._write_receipt,
                    root_fd,
                    self.module.SUCCESS_NAME,
                    {"replacement": False},
                )
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)
            finally:
                os.close(root_fd)

    def test_40_cli_and_trampoline_enforce_zero_operator_argv(self) -> None:
        args = self.module.parse_cli(["--output-root", OUTPUT_ROOT])
        self.assertEqual(args.output_root, Path(OUTPUT_ROOT))
        for invalid in ([], ["--output-root", OUTPUT_ROOT, "extra"], [OUTPUT_ROOT]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises((self.module.GateError, SystemExit)):
                    self.module.parse_cli(invalid)
        source = TRAMPOLINE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            '[[ "$#" -eq 0 ]] \\\n'
            "  || fail_body_free 'ARGV_INVALID' 'trampoline accepts no argv'",
            source,
        )
        self.assertIn("#SBATCH --exclude=cg14", source)
        self.assertIn('--output-root "$RUN_ROOT/evidence"', source)
        self.assertNotIn('"$@"', source)

        handoff = HANDOFF_PATH.read_text(encoding="utf-8")
        easybuild_python = (
            "/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/"
            "bin/python3"
        )
        remote_validation_commands = [
            "/usr/bin/bash -n run_gpu_visibility_diagnostic_v1.sh",
            f"{easybuild_python} -B validate_gpu_visibility_diagnostic_v1.py",
            f"{easybuild_python} -O -B validate_gpu_visibility_diagnostic_v1.py",
            f"{easybuild_python} -I -S -B validate_gpu_visibility_diagnostic_v1.py",
            "/usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py",
            "/usr/bin/sha256sum -c SHA256SUMS",
        ]
        command_positions = []
        for command in remote_validation_commands:
            self.assertEqual(handoff.count(command), 1)
            command_positions.append(handoff.index(command))
        self.assertEqual(command_positions, sorted(command_positions))
        handoff_lines = handoff.splitlines()
        for unfrozen in (
            "/bin/bash -n run_gpu_visibility_diagnostic_v1.sh",
            "python3 -B validate_gpu_visibility_diagnostic_v1.py",
            "python3 -O -B validate_gpu_visibility_diagnostic_v1.py",
            "python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py",
            "shasum -a 256 -c SHA256SUMS",
        ):
            self.assertNotIn(unfrozen, handoff_lines)

        absence_recheck = 'for path in "$RUN" "$OUTPUT" "$LOG"; do'
        log_creation = 'mkdir -- "$LOG"'
        sbatch_environment_gate = (
            "if /usr/bin/env | /usr/bin/grep -q '^SBATCH_'; then"
        )
        sbatch_command = "sbatch --export=NIL"
        for required in (
            absence_recheck,
            log_creation,
            sbatch_environment_gate,
            sbatch_command,
        ):
            self.assertEqual(handoff.count(required), 1)
        self.assertLess(command_positions[-1], handoff.index(absence_recheck))
        self.assertLess(handoff.index(absence_recheck), handoff.index(log_creation))
        self.assertLess(
            handoff.index(log_creation), handoff.index(sbatch_environment_gate)
        )
        self.assertLess(
            handoff.index(sbatch_environment_gate), handoff.index(sbatch_command)
        )

    def test_41_synthetic_run_calls_exact_three_commands_and_seals_receipt(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        list_body = f"GPU 0: NVIDIA A40 (UUID: {uuid})\n".encode("ascii")
        identity_body = f"0, {uuid}, NVIDIA A40\n".encode("ascii")
        observed: list[list[str]] = []

        def runner(argv: list[str], **kwargs: Any) -> dict[str, Any]:
            self.assertEqual(kwargs["timeout_seconds"], 30.0)
            self.assertEqual(kwargs["stream_byte_cap"], 65536)
            self.assertEqual(
                kwargs["environment"],
                {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
            )
            observed.append(list(argv))
            body = list_body if argv == EXPECTED_LIST_ARGV else identity_body
            return completed_capture(list(argv), body)

        environment = {
            b"SLURM_JOB_ID": b"4000000",
            b"SLURMD_NODENAME": b"cg15",
            b"SLURM_JOB_GPUS": b"0",
            b"SLURM_STEP_GPUS": b"0",
            b"CUDA_VISIBLE_DEVICES": b"0",
        }
        synthetic_inventory = {
            "character_device_count": 1,
            "device_root": "/synthetic/dev",
            "directory_error": None,
            "discovered_entry_count": 1,
            "entries": [{"synthetic": "nvidia0-character-device-metadata-only"}],
            "entry_cap": 64,
            "read_only_open_denied_count": 0,
            "scan_complete": True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output_root = parent / "evidence"
            dev = parent / "dev"
            dev.mkdir()
            cgroup = parent / "cgroup"
            mountinfo = parent / "mountinfo"
            cgroup.write_bytes(b"0::/synthetic.slice\n")
            mountinfo.write_bytes(
                b"36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n"
            )
            contract_identity = (1, 2)
            predecessor_identity = (3, 4)

            def load_contract_fixture() -> tuple[dict[str, Any], str, tuple[int, int]]:
                return self.contract, sha256_bytes(self.contract_raw), contract_identity

            def load_predecessor_fixture(
                _contract: dict[str, Any],
            ) -> tuple[dict[str, Any], dict[str, Any], tuple[int, int]]:
                return (
                    self.predecessor,
                    {
                        "bytes": len(self.predecessor_raw),
                        "sha256": sha256_bytes(self.predecessor_raw),
                    },
                    predecessor_identity,
                )

            with (
                patched_attribute(self.module, "EXPECTED_OUTPUT_ROOT", os.fspath(output_root)),
                patched_attribute(self.module, "load_contract", load_contract_fixture),
                patched_attribute(self.module, "load_predecessor", load_predecessor_fixture),
                patched_attribute(
                    self.module,
                    "capture_device_inventory",
                    lambda _dev_root: synthetic_inventory,
                ),
            ):
                code, receipt = self.module.run(
                    output_root,
                    environmentb=environment,
                    dev_root=dev,
                    cgroup_path=cgroup,
                    mountinfo_path=mountinfo,
                    command_runner=runner,
                )
            try:
                self.assertEqual(code, 0)
                self.assertEqual(receipt["status"], "PASS_GPU_VISIBILITY_DIAGNOSTIC")
                self.assertEqual(receipt["decision"], "VISIBLE_A40_IDENTITY_BOUND")
                self.assertEqual(receipt["device_inventory"], synthetic_inventory)
                self.assertEqual(
                    observed,
                    [
                        EXPECTED_LIST_ARGV,
                        EXPECTED_UNSCOPED_ARGV,
                        ["/usr/bin/nvidia-smi", "--id=0", *EXPECTED_UNSCOPED_ARGV[1:]],
                    ],
                )
                self.assertEqual(
                    receipt["commands"]["nvidia_smi_list"]["stdout"],
                    raw_binding(list_body),
                )
                self.assertEqual(
                    receipt["commands"]["unscoped_identity"]["stdout"],
                    raw_binding(identity_body),
                )
                self.assertEqual(
                    receipt["commands"]["scoped_identity"]["stdout"],
                    raw_binding(identity_body),
                )
                receipt_path = output_root / self.module.SUCCESS_NAME
                self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o400)
                self.assertEqual(stat.S_IMODE(output_root.stat().st_mode), 0o500)
                persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertEqual(persisted, receipt)
            finally:
                if output_root.exists():
                    output_root.chmod(0o700)

    def test_42_output_root_is_create_only_and_alias_geometry_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output_root = parent / "evidence"
            alias = parent / "alias"
            with patched_attribute(
                self.module, "EXPECTED_OUTPUT_ROOT", os.fspath(output_root)
            ):
                root_fd = self.module._create_output_root(output_root)
                os.close(root_fd)
                self.assert_gate(
                    "OUTPUT_ROOT_INVALID", self.module._create_output_root, output_root
                )
                alias.symlink_to(output_root, target_is_directory=True)
                self.assert_gate("OUTPUT_ROOT_INVALID", self.module._create_output_root, alias)

    def test_43_trampoline_exact_geometry_and_source_bindings_are_frozen(self) -> None:
        payload = TRAMPOLINE_PATH.read_bytes()
        source = payload.decode("utf-8")
        observed_sbatch = [line for line in source.splitlines() if line.startswith("#SBATCH ")]
        self.assertEqual(observed_sbatch, EXPECTED_SBATCH)
        self.assertEqual(shell_assignment(source, "SUCCESSOR_ROOT"), DEPLOYMENT_ROOT)
        self.assertEqual(shell_assignment(source, "RUN_ROOT"), RUN_ROOT)
        self.assertEqual(
            shell_assignment(source, "MODULE_SHA256"), sha256_bytes(MODULE_PATH.read_bytes())
        )
        self.assertEqual(
            shell_assignment(source, "CONTRACT_SHA256"),
            sha256_bytes(CONTRACT_PATH.read_bytes()),
        )
        self.assertEqual(
            shell_assignment(source, "NORMALIZED_TRAMPOLINE_SHA256"),
            normalized_trampoline_sha256(payload),
        )
        self.assertNotIn("'" + ("0" * 64) + "'", source)
        expected_exec = (
            'exec "$PYTHON_COMMAND" -I -S -B "$MODULE_PATH" '
            '--output-root "$RUN_ROOT/evidence"'
        )
        self.assertEqual(source.count(expected_exec), 1)

    def test_44_cannot_check_receipt_is_create_only_and_sealed(self) -> None:
        receipt = {
            "status": "CANNOT_CHECK_GPU_VISIBILITY_DIAGNOSTIC",
            "scientific_authority_delta": "NONE",
        }
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "evidence"
            output_root.mkdir(mode=0o700)
            root_fd = os.open(output_root, self.module._directory_flags())
            try:
                self.module._persist_receipt(
                    output_root, root_fd, self.module.CANNOT_NAME, receipt
                )
                receipt_path = output_root / self.module.CANNOT_NAME
                self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o400)
                self.assertEqual(stat.S_IMODE(output_root.stat().st_mode), 0o500)
                self.assertEqual(
                    receipt_path.read_bytes(), self.module.canonical_json_bytes(receipt) + b"\n"
                )
                self.assert_gate(
                    "OUTPUT_WRITE_FAILED",
                    self.module._write_receipt,
                    root_fd,
                    self.module.CANNOT_NAME,
                    {"replacement": False},
                )
                self.assertEqual(
                    receipt_path.read_bytes(), self.module.canonical_json_bytes(receipt) + b"\n"
                )
            finally:
                os.close(root_fd)
                output_root.chmod(0o700)

    def assert_complete_full_run_decision(
        self,
        *,
        expected_decision: str,
        synthetic_inventory: dict[str, Any],
        command_results: dict[str, tuple[bytes, bytes, int]],
    ) -> None:
        expected_argv = {
            "nvidia_smi_list": EXPECTED_LIST_ARGV,
            "unscoped_identity": EXPECTED_UNSCOPED_ARGV,
            "scoped_identity": [
                "/usr/bin/nvidia-smi",
                "--id=0",
                *EXPECTED_UNSCOPED_ARGV[1:],
            ],
        }
        argv_to_name = {tuple(argv): name for name, argv in expected_argv.items()}
        observed: list[list[str]] = []

        def runner(argv: list[str], **kwargs: Any) -> dict[str, Any]:
            self.assertEqual(kwargs["timeout_seconds"], 30.0)
            self.assertEqual(kwargs["stream_byte_cap"], 65536)
            self.assertEqual(
                kwargs["environment"],
                {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
            )
            name = argv_to_name[tuple(argv)]
            stdout, stderr, return_code = command_results[name]
            observed.append(list(argv))
            return completed_capture(
                list(argv), stdout, stderr=stderr, return_code=return_code
            )

        environment = {
            b"SLURM_JOB_ID": b"4000000",
            b"SLURMD_NODENAME": b"cg15",
            b"SLURM_JOB_GPUS": b"0",
            b"SLURM_STEP_GPUS": b"0",
            b"CUDA_VISIBLE_DEVICES": b"0",
        }
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output_root = parent / "evidence"
            dev = parent / "empty-synthetic-dev"
            dev.mkdir()
            cgroup = parent / "cgroup"
            mountinfo = parent / "mountinfo"
            cgroup.write_bytes(b"0::/synthetic.slice\n")
            mountinfo.write_bytes(
                b"36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n"
            )
            contract_identity = (11, 12)
            predecessor_identity = (13, 14)

            def load_contract_fixture() -> tuple[dict[str, Any], str, tuple[int, int]]:
                return self.contract, sha256_bytes(self.contract_raw), contract_identity

            def load_predecessor_fixture(
                _contract: dict[str, Any],
            ) -> tuple[dict[str, Any], dict[str, Any], tuple[int, int]]:
                return (
                    self.predecessor,
                    {
                        "bytes": len(self.predecessor_raw),
                        "sha256": sha256_bytes(self.predecessor_raw),
                    },
                    predecessor_identity,
                )

            with (
                patched_attribute(self.module, "EXPECTED_OUTPUT_ROOT", os.fspath(output_root)),
                patched_attribute(self.module, "load_contract", load_contract_fixture),
                patched_attribute(self.module, "load_predecessor", load_predecessor_fixture),
                patched_attribute(
                    self.module,
                    "capture_device_inventory",
                    lambda _dev_root: synthetic_inventory,
                ),
            ):
                code, receipt = self.module.run(
                    output_root,
                    environmentb=environment,
                    dev_root=dev,
                    cgroup_path=cgroup,
                    mountinfo_path=mountinfo,
                    command_runner=runner,
                )
            try:
                self.assertEqual(code, 0)
                self.assertEqual(
                    receipt["schema_version"],
                    "orion.p1.scienceagentbench.gpu-visibility-diagnostic-result.v1",
                )
                self.assertEqual(receipt["status"], "PASS_GPU_VISIBILITY_DIAGNOSTIC")
                self.assertEqual(receipt["decision"], expected_decision)
                self.assertEqual(
                    set(receipt), set(self.schema["success"]["required_fields"])
                )
                self.assertEqual(receipt["device_inventory"], synthetic_inventory)
                self.assertEqual(
                    observed,
                    [
                        expected_argv["nvidia_smi_list"],
                        expected_argv["unscoped_identity"],
                        expected_argv["scoped_identity"],
                    ],
                )
                self.assertIn("DIAGNOSTIC_DECISION_BOUND", receipt["completed_stages"])
                self.assertIs(
                    receipt["node_change_diagnostic"]["different_from_predecessor_node"],
                    True,
                )
                self.assertIs(receipt["no_promotion"]["node_change_is_causal_proof"], False)
                self.assertEqual(receipt["production_admissibility"], "CANNOT_CHECK")
                self.assertEqual(receipt["scientific_authority_delta"], "NONE")
                self.assertIs(receipt["model_started"], False)
                self.assertIs(receipt["network_accessed"], False)
                receipt_path = output_root / self.module.SUCCESS_NAME
                self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o400)
                self.assertEqual(stat.S_IMODE(output_root.stat().st_mode), 0o500)
                persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertEqual(persisted, receipt)
                for name, (stdout, stderr, return_code) in command_results.items():
                    capture = receipt["commands"][name]
                    self.assertEqual(capture["return_code"], return_code)
                    self.assertEqual(capture["stdout"], raw_binding(stdout))
                    self.assertEqual(capture["stderr"], raw_binding(stderr))
                self.assertEqual(
                    receipt["parsed_outputs"]["scoped_identity"]["scope_token"], "0"
                )
            finally:
                if output_root.exists():
                    output_root.chmod(0o700)

    def test_45_full_run_scoped_recovery_binds_exact_decision_and_custody(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        identity_body = f"0, {uuid}, NVIDIA A40\n".encode("ascii")
        self.assert_complete_full_run_decision(
            expected_decision="UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND",
            synthetic_inventory={
                "character_device_count": 1,
                "device_root": "/synthetic/dev",
                "directory_error": None,
                "discovered_entry_count": 1,
                "entries": [{"synthetic": "nvidia0-character-device-metadata-only"}],
                "entry_cap": 64,
                "read_only_open_denied_count": 0,
                "scan_complete": True,
            },
            command_results={
                "nvidia_smi_list": (b"", b"list unavailable", 6),
                "unscoped_identity": (b"", b"unscoped unavailable", 6),
                "scoped_identity": (identity_body, b"", 0),
            },
        )

    def test_46_full_run_absent_devices_precedes_generic_rc6(self) -> None:
        self.assert_complete_full_run_decision(
            expected_decision="NVIDIA_DEVICE_NODES_ABSENT",
            synthetic_inventory={
                "character_device_count": 0,
                "device_root": "/synthetic/dev",
                "directory_error": None,
                "discovered_entry_count": 0,
                "entries": [],
                "entry_cap": 64,
                "read_only_open_denied_count": 0,
                "scan_complete": True,
            },
            command_results={
                "nvidia_smi_list": (b"", b"query failed", 6),
                "unscoped_identity": (b"", b"query failed", 6),
                "scoped_identity": (b"", b"query failed", 6),
            },
        )

    def test_47_full_run_generic_rc6_requires_all_three_exact_calls(self) -> None:
        self.assert_complete_full_run_decision(
            expected_decision="NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES",
            synthetic_inventory={
                "character_device_count": 1,
                "device_root": "/synthetic/dev",
                "directory_error": None,
                "discovered_entry_count": 1,
                "entries": [{"synthetic": "nvidia0-character-device-metadata-only"}],
                "entry_cap": 64,
                "read_only_open_denied_count": 0,
                "scan_complete": True,
            },
            command_results={
                "nvidia_smi_list": (b"", b"query failed", 6),
                "unscoped_identity": (b"", b"query failed", 6),
                "scoped_identity": (b"", b"query failed", 6),
            },
        )

    def test_48_full_run_access_restriction_precedes_generic_rc6(self) -> None:
        self.assert_complete_full_run_decision(
            expected_decision="DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK",
            synthetic_inventory={
                "character_device_count": 1,
                "device_root": "/synthetic/dev",
                "directory_error": None,
                "discovered_entry_count": 1,
                "entries": [{"synthetic": "nvidia0-open-denied-metadata-only"}],
                "entry_cap": 64,
                "read_only_open_denied_count": 1,
                "scan_complete": True,
            },
            command_results={
                "nvidia_smi_list": (b"", b"query failed", 6),
                "unscoped_identity": (b"", b"query failed", 6),
                "scoped_identity": (b"", b"query failed", 6),
            },
        )

    def test_49_full_run_complete_but_unmatched_evidence_is_inconclusive(self) -> None:
        uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        list_body = f"GPU 0: NVIDIA A40 (UUID: {uuid})\n".encode("ascii")
        self.assert_complete_full_run_decision(
            expected_decision="CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE",
            synthetic_inventory={
                "character_device_count": 1,
                "device_root": "/synthetic/dev",
                "directory_error": None,
                "discovered_entry_count": 1,
                "entries": [{"synthetic": "nvidia0-character-device-metadata-only"}],
                "entry_cap": 64,
                "read_only_open_denied_count": 0,
                "scan_complete": True,
            },
            command_results={
                "nvidia_smi_list": (list_body, b"", 0),
                "unscoped_identity": (b"", b"query failed", 6),
                "scoped_identity": (b"", b"query failed", 6),
            },
        )

    def test_50_full_run_invalid_scope_token_seals_schema_complete_cannot_receipt(
        self,
    ) -> None:
        observed: list[list[str]] = []

        def runner(argv: list[str], **kwargs: Any) -> dict[str, Any]:
            self.assertEqual(kwargs["timeout_seconds"], 30.0)
            self.assertEqual(kwargs["stream_byte_cap"], 65536)
            observed.append(list(argv))
            return completed_capture(list(argv), b"", stderr=b"query failed", return_code=6)

        environment = {
            b"SLURM_JOB_ID": b"4000000",
            b"SLURMD_NODENAME": b"cg15",
            b"SLURM_JOB_GPUS": b"0",
            b"SLURM_STEP_GPUS": b"0",
            b"CUDA_VISIBLE_DEVICES": b"0,1",
        }
        synthetic_inventory = {
            "character_device_count": 1,
            "device_root": "/synthetic/dev",
            "directory_error": None,
            "discovered_entry_count": 1,
            "entries": [{"synthetic": "nvidia0-character-device-metadata-only"}],
            "entry_cap": 64,
            "read_only_open_denied_count": 0,
            "scan_complete": True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            output_root = parent / "evidence"
            dev = parent / "empty-synthetic-dev"
            dev.mkdir()
            cgroup = parent / "cgroup"
            mountinfo = parent / "mountinfo"
            cgroup.write_bytes(b"0::/synthetic.slice\n")
            mountinfo.write_bytes(
                b"36 25 0:32 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n"
            )
            contract_identity = (21, 22)
            predecessor_identity = (23, 24)

            def load_contract_fixture() -> tuple[dict[str, Any], str, tuple[int, int]]:
                return self.contract, sha256_bytes(self.contract_raw), contract_identity

            def load_predecessor_fixture(
                _contract: dict[str, Any],
            ) -> tuple[dict[str, Any], dict[str, Any], tuple[int, int]]:
                return (
                    self.predecessor,
                    {
                        "bytes": len(self.predecessor_raw),
                        "sha256": sha256_bytes(self.predecessor_raw),
                    },
                    predecessor_identity,
                )

            with (
                patched_attribute(self.module, "EXPECTED_OUTPUT_ROOT", os.fspath(output_root)),
                patched_attribute(self.module, "load_contract", load_contract_fixture),
                patched_attribute(self.module, "load_predecessor", load_predecessor_fixture),
                patched_attribute(
                    self.module,
                    "capture_device_inventory",
                    lambda _dev_root: synthetic_inventory,
                ),
            ):
                code, receipt = self.module.run(
                    output_root,
                    environmentb=environment,
                    dev_root=dev,
                    cgroup_path=cgroup,
                    mountinfo_path=mountinfo,
                    command_runner=runner,
                )
            try:
                self.assertEqual(code, 1)
                self.assertEqual(
                    receipt["schema_version"],
                    "orion.p1.scienceagentbench.gpu-visibility-diagnostic-cannot-check.v1",
                )
                self.assertEqual(
                    receipt["status"], "CANNOT_CHECK_GPU_VISIBILITY_DIAGNOSTIC"
                )
                self.assertEqual(
                    receipt["decision"], "CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE"
                )
                self.assertEqual(receipt["failure_code"], "ENVIRONMENT_INVALID")
                self.assertRegex(receipt["failure_detail_sha256"], SHA_RE)
                self.assertEqual(
                    set(receipt), set(self.schema["cannot_check"]["required_fields"])
                )
                self.assertEqual(
                    observed, [EXPECTED_LIST_ARGV, EXPECTED_UNSCOPED_ARGV]
                )
                self.assertEqual(
                    receipt["commands"]["scoped_identity"]["status"],
                    "NOT_RUN_INVALID_SCOPED_TOKEN",
                )
                self.assertIn("SCOPED_IDENTITY_NOT_RUN", receipt["completed_stages"])
                self.assertNotIn("DIAGNOSTIC_DECISION_BOUND", receipt["completed_stages"])
                self.assertIs(receipt["no_promotion"]["node_change_is_causal_proof"], False)
                self.assertEqual(receipt["production_admissibility"], "CANNOT_CHECK")
                self.assertEqual(receipt["scientific_authority_delta"], "NONE")
                receipt_path = output_root / self.module.CANNOT_NAME
                self.assertTrue(receipt_path.is_file())
                self.assertFalse((output_root / self.module.SUCCESS_NAME).exists())
                self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o400)
                self.assertEqual(stat.S_IMODE(output_root.stat().st_mode), 0o500)
                persisted = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertEqual(persisted, receipt)
            finally:
                if output_root.exists():
                    output_root.chmod(0o700)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GPUVisibilityDiagnosticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} protected_bodies=0 task_routes=0 tokenize=0 "
        "completion=0 generation=0 jobs=0 outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
