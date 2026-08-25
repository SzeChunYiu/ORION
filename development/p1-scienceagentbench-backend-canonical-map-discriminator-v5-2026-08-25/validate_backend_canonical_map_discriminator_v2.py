#!/usr/bin/env python3
"""Hostile body-free validation for the V5 canonical-map discriminator.

Every process, map row, path, and payload in this suite is synthetic.  The
suite uses only the standard library, never submits a job, never starts a
model, and never opens protected packet, prompt, completion, token, or outcome
bodies.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "backend_canonical_map_discriminator_v2.py"
CONTRACT_PATH = ROOT / "BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V2.json"
TRAMPOLINE_PATH = ROOT / "run_backend_canonical_map_discriminator_v2.sh"
PREDECESSOR_PATH = ROOT / "JOB_3537910_PREDECESSOR_BINDING_V1.json"
PREDECESSOR_SOURCE_ROOT = (
    ROOT.parent
    / "p1-scienceagentbench-backend-canonical-map-discriminator-v4-job-3537910-result-2026-08-25"
)
SUCCESSOR_ROOT = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "repo-exec-successor-v5-20260825"
)
RUN_ROOT = (
    "/projects/hep/fs10/scratch/scyiu/"
    "orion_p1_sab_protected_rr1_direct_route_v1_20260824/"
    "live-rr1-exec-successor-v5-20260825"
)
SUBMIT_LOG_ROOT = RUN_ROOT + "-submit-logs"
EXPECTED_SBATCH = [
    "#SBATCH --job-name=p1_sab_backend_map_v2",
    "#SBATCH --account=lu2026-2-51",
    "#SBATCH --partition=gpua40i",
    "#SBATCH --gres=gpu:a40:1",
    "#SBATCH --nodes=1",
    "#SBATCH --ntasks=1",
    "#SBATCH --cpus-per-task=8",
    "#SBATCH --mem=64G",
    "#SBATCH --time=01:00:00",
    "#SBATCH --signal=B:TERM@120",
]
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_PREDECESSOR_ARTIFACTS = {
    "JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json": (
        1464,
        "cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a",
    ),
    "JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json": (
        4644,
        "c275878988c6bb2ce0ea9ca4dccca068bcd7678807cd79865e30dbe2e4176402",
    ),
    "OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json": (
        4512,
        "c3138f01a7c83c4740890c0dcddfc0f693f0153e8f7249c51da11f106bca2aa7",
    ),
    "RESULT_EXPORT_MANIFEST_V1.json": (
        3230,
        "c236c934e9f4e261fc631417393f3d2086d7b6ad2ab07d616e1e618b5575d414",
    ),
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalized_trampoline_sha256(payload: bytes) -> str:
    pattern = re.compile(
        rb"(?m)^NORMALIZED_TRAMPOLINE_SHA256='([0-9a-f]{64})'$"
    )
    normalized, count = pattern.subn(
        b"NORMALIZED_TRAMPOLINE_SHA256='" + (b"0" * 64) + b"'", payload
    )
    if count != 1:
        raise AssertionError(
            f"trampoline normalized self-binding count is {count}, not one"
        )
    return sha256_bytes(normalized)


def assignment(source: str, name: str) -> str:
    matches = re.findall(rf"(?m)^{re.escape(name)}='([^']*)'$", source)
    if len(matches) != 1:
        raise AssertionError(f"{name} assignment count is {len(matches)}, not one")
    return matches[0]


def load_module() -> ModuleType:
    if not MODULE_PATH.is_file():
        raise AssertionError("canonical-map discriminator module is absent")
    spec = importlib.util.spec_from_file_location(
        "backend_canonical_map_discriminator_v2_under_test", MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("canonical-map discriminator module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyntheticProcessFixture:
    def __init__(self, base: Path, module: ModuleType) -> None:
        self.base = base
        self.module = module
        self.canonical_parent = base / "canonical-runtime"
        self.canonical_parent.mkdir()
        self.logical_parent = base / "logical-runtime"
        self.logical_parent.symlink_to(self.canonical_parent, target_is_directory=True)
        for name in ("llama-server", "libggml-cuda.so", "model.gguf"):
            path = self.canonical_parent / name
            path.write_bytes(("synthetic-" + name + "\n").encode("ascii"))
            path.chmod(0o600)
        self.server = self.bound("llama-server")
        self.backend = self.bound("libggml-cuda.so")
        self.model = self.bound("model.gguf")
        self.argv = [
            self.server["logical_path"],
            "--model",
            self.model["logical_path"],
            "--host",
            "127.0.0.1",
            "--port",
            "8080",
            "--ctx-size",
            "32768",
            "--parallel",
            "1",
            "--no-cont-batching",
            "--no-context-shift",
        ]
        self.proc_root = base / "proc"
        self.pid = 4242
        self.pid_root = self.proc_root / str(self.pid)
        self.pid_root.mkdir(parents=True)
        (self.pid_root / "exe").symlink_to(self.server["logical_path"])
        self.write_cmdline(self.argv)
        self.write_environ(self.backend["logical_path"])
        self.write_maps(self.good_map_lines())
        self.listener_inode = "900001"
        self.write_listener_tables(
            [("tcp", "0100007F:1F90", self.listener_inode, True)]
        )

    def raw_binding(self, name: str) -> dict[str, Any]:
        logical = self.logical_parent / name
        canonical = self.canonical_parent / name
        info = logical.stat()
        return {
            "logical_path": os.fspath(logical),
            "canonical_path": os.fspath(canonical),
            "bytes": info.st_size,
            "sha256": sha256_bytes(logical.read_bytes()),
            "mode": f"{stat.S_IMODE(info.st_mode):04o}",
            "uid": info.st_uid,
            "gid": info.st_gid,
            "nlink": info.st_nlink,
        }

    def bound(self, name: str) -> dict[str, Any]:
        return self.module.validate_bound_file(self.raw_binding(name), name)

    @staticmethod
    def map_line(
        binding: dict[str, Any],
        path: str,
        *,
        permissions: str = "r--p",
        device: str | None = None,
        inode: str | None = None,
        start: int = 0x70000000,
    ) -> str:
        return (
            f"{start:x}-{start + 0x1000:x} {permissions} 00000000 "
            f"{device or binding['maps_device']} {inode or binding['inode']} {path}"
        )

    def good_map_lines(self) -> list[str]:
        return [
            self.map_line(
                self.server,
                self.server["canonical_path"],
                permissions="r-xp",
                start=0x70000000,
            ),
            self.map_line(
                self.backend,
                self.backend["canonical_path"],
                permissions="r--p",
                start=0x71000000,
            ),
            self.map_line(
                self.backend,
                self.backend["canonical_path"],
                permissions="r-xp",
                start=0x71001000,
            ),
            self.map_line(
                self.backend,
                self.backend["canonical_path"],
                permissions="rw-p",
                start=0x71002000,
            ),
            self.map_line(
                self.model,
                self.model["logical_path"],
                permissions="r--s",
                start=0x72000000,
            ),
        ]

    def write_maps(self, lines: list[str]) -> None:
        (self.pid_root / "maps").write_text("\n".join(lines) + "\n")

    def write_cmdline(self, argv: list[str]) -> None:
        (self.pid_root / "cmdline").write_bytes(
            b"\0".join(item.encode("utf-8") for item in argv) + b"\0"
        )

    def write_environ(self, backend_path: str, *, extra: bytes = b"") -> None:
        fields = [f"GGML_BACKEND_PATH={backend_path}".encode("utf-8")]
        fields.extend(key.encode("ascii") + b"=" for key in self.module.PROXY_KEYS)
        fields.extend(
            (b"NO_PROXY=127.0.0.1,localhost", b"no_proxy=127.0.0.1,localhost")
        )
        (self.pid_root / "environ").write_bytes(b"\0".join(fields) + b"\0" + extra)

    def write_listener_tables(
        self, listeners: list[tuple[str, str, str, bool]]
    ) -> None:
        fd_root = self.pid_root / "fd"
        net_root = self.pid_root / "net"
        fd_root.mkdir(exist_ok=True)
        net_root.mkdir(exist_ok=True)
        for entry in fd_root.iterdir():
            entry.unlink()
        rows: dict[str, list[str]] = {"tcp": [], "tcp6": []}
        fd_number = 3
        for row_number, (protocol, local, inode, owned) in enumerate(listeners):
            if protocol not in rows:
                raise AssertionError(f"synthetic protocol is invalid: {protocol}")
            rows[protocol].append(
                f"{row_number}: {local} 00000000:0000 0A "
                f"00000000:00000000 00:00000000 00000000 1000 0 {inode}"
            )
            if owned:
                (fd_root / str(fd_number)).symlink_to(f"socket:[{inode}]")
                fd_number += 1
        header = "sl local_address rem_address st tx_queue rx_queue tr uid timeout inode"
        for protocol in ("tcp", "tcp6"):
            (net_root / protocol).write_text(
                "\n".join([header, *rows[protocol]]) + "\n", encoding="ascii"
            )

    def attest(self) -> dict[str, Any]:
        return self.module.attest_process_identity(
            self.pid,
            self.server,
            self.backend,
            self.model,
            self.argv,
            proc_root=self.proc_root,
        )

    def attest_listener(self) -> dict[str, Any]:
        return self.module.attest_listener(self.pid, proc_root=self.proc_root)


class BackendCanonicalMapDiscriminatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    @contextlib.contextmanager
    def fixture(self) -> Iterator[SyntheticProcessFixture]:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            yield SyntheticProcessFixture(Path(directory), self.module)

    def assert_gate(self, code: str, callable_: Any) -> None:
        with self.assertRaises(self.module.GateError) as caught:
            callable_()
        self.assertEqual(caught.exception.code, code)

    @staticmethod
    def valid_gpu_environment() -> dict[str, str]:
        return {
            "SLURM_JOB_ID": "3539001",
            "CUDA_VISIBLE_DEVICES": "0",
            "SLURM_JOB_GPUS": "0",
            "HOME": "/home/synthetic",
            "PATH": "/synthetic/bin:/usr/bin",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "LC_CTYPE": "C.UTF-8",
            "SECRET_MUST_NOT_CROSS": "synthetic-secret",
        }

    @contextlib.contextmanager
    def installed_gpu_runner(self, outcome: Any) -> Iterator[list[tuple[list[str], dict[str, Any]]]]:
        calls: list[tuple[list[str], dict[str, Any]]] = []
        original = self.module.subprocess.run

        def runner(argv: list[str], **kwargs: Any) -> Any:
            calls.append((list(argv), dict(kwargs)))
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

        self.module.subprocess.run = runner
        try:
            yield calls
        finally:
            self.module.subprocess.run = original

    def completed_gpu_call(
        self,
        stdout: bytes,
        *,
        stderr: bytes = b"",
        return_code: int = 0,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            list(self.module.NVIDIA_SMI_ARGV),
            return_code,
            stdout=stdout,
            stderr=stderr,
        )

    def assert_gpu_capture(
        self,
        capture: dict[str, Any],
        completed: subprocess.CompletedProcess[bytes],
        *,
        stdout_parse_attempted: bool,
    ) -> None:
        self.assertEqual(
            capture,
            {
                "status": "COMPLETED",
                "argv": list(self.module.NVIDIA_SMI_ARGV),
                "return_code": completed.returncode,
                "stdout": {
                    "bytes": len(completed.stdout),
                    "sha256": sha256_bytes(completed.stdout),
                },
                "stderr": {
                    "bytes": len(completed.stderr),
                    "sha256": sha256_bytes(completed.stderr),
                },
                "stdout_parse_attempted": stdout_parse_attempted,
            },
        )

    def capture_gpu_failure(
        self,
        completed: subprocess.CompletedProcess[bytes],
        expected_subcode: str,
    ) -> Any:
        with self.installed_gpu_runner(completed):
            with self.assertRaises(self.module.GateError) as caught:
                self.module.capture_gpu_identity(self.valid_gpu_environment())
        self.assertEqual(caught.exception.code, "GPU_IDENTITY_INVALID")
        self.assertEqual(caught.exception.failure_subcode, expected_subcode)
        return caught.exception

    def test_01_canonical_parent_alias_is_a_valid_file_and_map_identity(self) -> None:
        with self.fixture() as fixture:
            self.assertNotEqual(
                fixture.backend["logical_path"], fixture.backend["canonical_path"]
            )
            self.assertEqual(
                Path(fixture.backend["logical_path"]).resolve(),
                Path(fixture.backend["canonical_path"]),
            )
            attestation = fixture.attest()
            self.assertEqual(
                attestation["server_mapping"]["observed_mapped_paths"],
                [fixture.server["canonical_path"]],
            )
            self.assertEqual(attestation["server_mapping"]["segment_count"], 1)
            self.assertEqual(
                attestation["cuda_backend_mapping"]["observed_mapped_paths"],
                [fixture.backend["canonical_path"]],
            )
            self.assertEqual(attestation["model_mapping"]["segment_count"], 1)

    def test_02_multiple_elf_segments_are_one_allowed_identity(self) -> None:
        with self.fixture() as fixture:
            result = fixture.attest()["cuda_backend_mapping"]
            self.assertEqual(result["segment_count"], 3)
            self.assertEqual(result["segment_permissions"], ["r--p", "r-xp", "rw-p"])

    def test_03_wrong_device_or_inode_fails_closed(self) -> None:
        with self.fixture() as fixture:
            for drift, expected in (("device", "ff:ff"), ("inode", "999999999")):
                with self.subTest(drift=drift):
                    kwargs = {drift: expected}
                    lines = fixture.good_map_lines()
                    lines[1] = fixture.map_line(
                        fixture.backend,
                        fixture.backend["canonical_path"],
                        start=0x71000000,
                        **kwargs,
                    )
                    fixture.write_maps(lines)
                    self.assert_gate("MAPPING_IDENTITY_DRIFT", fixture.attest)
                    fixture.write_maps(fixture.good_map_lines())

    def test_04_third_hardlink_alias_fails_closed(self) -> None:
        with self.fixture() as fixture:
            third = fixture.base / "third-backend-hardlink.so"
            os.link(fixture.backend["canonical_path"], third)
            third_info = third.stat()
            self.assertEqual(str(third_info.st_ino), fixture.backend["inode"])
            lines = fixture.good_map_lines()
            lines.append(
                fixture.map_line(
                    fixture.backend, os.fspath(third), permissions="r-xp", start=0x71003000
                )
            )
            fixture.write_maps(lines)
            self.assert_gate("MAPPING_ALIAS_DRIFT", fixture.attest)

    def test_05_deleted_suffix_is_not_an_allowed_alias(self) -> None:
        with self.fixture() as fixture:
            lines = fixture.good_map_lines()
            lines.append(
                fixture.map_line(
                    fixture.backend,
                    fixture.backend["canonical_path"] + " (deleted)",
                    permissions="r-xp",
                    start=0x71003000,
                )
            )
            fixture.write_maps(lines)
            self.assert_gate("MAPPING_ALIAS_DRIFT", fixture.attest)

    def test_06_logical_and_canonical_binding_swap_is_rejected(self) -> None:
        with self.fixture() as fixture:
            swapped = fixture.raw_binding("libggml-cuda.so")
            swapped["logical_path"], swapped["canonical_path"] = (
                swapped["canonical_path"],
                swapped["logical_path"],
            )
            self.assert_gate(
                "BOUND_FILE_INVALID",
                lambda: self.module.validate_bound_file(swapped, "swapped backend"),
            )

    def test_07_canonicalized_argv_substitution_is_rejected(self) -> None:
        with self.fixture() as fixture:
            canonicalized = list(fixture.argv)
            canonicalized[0] = fixture.server["canonical_path"]
            canonicalized[2] = fixture.model["canonical_path"]
            fixture.write_cmdline(canonicalized)
            self.assert_gate("ARGV_DRIFT", fixture.attest)

    def test_08_canonicalized_environment_substitution_is_rejected(self) -> None:
        with self.fixture() as fixture:
            fixture.write_environ(fixture.backend["canonical_path"])
            self.assert_gate("ENVIRONMENT_DRIFT", fixture.attest)

    def test_09_process_attestation_is_byte_deterministic(self) -> None:
        with self.fixture() as fixture:
            first = fixture.attest()
            second = fixture.attest()
            self.assertEqual(second, first)
            self.assertEqual(
                self.module.canonical_json_bytes(second),
                self.module.canonical_json_bytes(first),
            )

    def test_10_run_requires_an_identical_second_attestation(self) -> None:
        source = MODULE_PATH.read_text()
        self.assertIn("first_bytes = canonical_json_bytes(first)", source)
        self.assertIn("second_bytes = canonical_json_bytes(second)", source)
        self.assertIn("if second_bytes != first_bytes:", source)
        self.assertIn('GateError("MAPPING_REATTESTATION_DRIFT"', source)
        self.assertLess(
            source.index("first = attest_process_identity("),
            source.index("second = attest_process_identity("),
        )
        self.assertLess(
            source.index("second = attest_process_identity("),
            source.index("if second_bytes != first_bytes:"),
        )
        self.assertIn('"process_reattestation": {', source)
        self.assertIn('"attestation_count": 2', source)
        self.assertIn('"attestation_1_sha256": sha256_bytes(first_bytes)', source)
        self.assertIn('"attestation_2_sha256": sha256_bytes(second_bytes)', source)
        self.assertIn('"byte_identical": True', source)

    def test_11_server_environment_is_allowlisted_and_body_free(self) -> None:
        contract = {
            "loader_environment": {"effective_server_ld_library_path": "/frozen/lib"},
            "runtime_files": {
                "backend": {"logical_path": "/logical/cuda/backend.so"},
                "server": {"logical_path": "/logical/bin/llama-server"},
            },
        }
        contract["loader_environment"]["effective_server_ld_library_path"] = (
            "/logical/bin:/logical/cuda:/frozen/lib"
        )
        source = {
            "HOME": "/home/synthetic",
            "PATH": "/frozen/bin",
            "CUDA_VISIBLE_DEVICES": "0",
            "LD_LIBRARY_PATH": "/attacker/lib",
            "LD_PRELOAD": "/attacker/preload.so",
            "SECRET_TOKEN": "must-not-cross-boundary",
            "HTTP_PROXY": "http://attacker.invalid",
        }
        observed = self.module.build_server_environment(contract, source)
        self.assertNotIn("SECRET_TOKEN", observed)
        self.assertNotIn("LD_PRELOAD", observed)
        self.assertEqual(
            observed["LD_LIBRARY_PATH"], "/logical/bin:/logical/cuda:/frozen/lib"
        )
        self.assertEqual(observed["GGML_BACKEND_PATH"], "/logical/cuda/backend.so")
        for key in self.module.PROXY_KEYS:
            self.assertEqual(observed[key], "")

    def test_12_only_body_free_loopback_get_routes_exist(self) -> None:
        source = MODULE_PATH.read_text()
        tree = ast.parse(source)
        route_literals: list[str] = []
        request_methods: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "_http_get_json":
                self.assertTrue(node.args and isinstance(node.args[0], ast.Constant))
                route_literals.append(node.args[0].value)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "request":
                self.assertTrue(node.args and isinstance(node.args[0], ast.Constant))
                request_methods.append(node.args[0].value)
        self.assertEqual(route_literals, ["/health", "/slots"])
        self.assertEqual(request_methods, ["GET"])
        for forbidden in (
            '"/tokenize"',
            '"/completion"',
            '"/v1/completions"',
            'request("POST"',
            "MASKED_PACKET.json",
            "RECOVERED_PACKET.json",
            "private-inputs",
        ):
            self.assertNotIn(forbidden, source)

    def test_13_trampoline_scheduler_geometry_is_exactly_bounded(self) -> None:
        source = TRAMPOLINE_PATH.read_text()
        directives = [line for line in source.splitlines() if line.startswith("#SBATCH ")]
        self.assertEqual(directives, EXPECTED_SBATCH)
        contract = json.loads(CONTRACT_PATH.read_text())
        allocation = contract["allocation"]
        self.assertEqual(contract["status"], "FROZEN_NOT_EXECUTED")
        self.assertEqual(allocation["account"], "lu2026-2-51")
        self.assertEqual(allocation["partition"], "gpua40i")
        self.assertEqual(allocation["gres"], "gpu:a40:1")
        self.assertEqual(allocation["exact_visible_gpu_count"], 1)
        self.assertEqual(allocation["nodes"], 1)
        self.assertEqual(allocation["tasks"], 1)
        self.assertEqual(allocation["cpus"], 8)
        self.assertEqual(allocation["memory"], "64G")
        self.assertEqual(allocation["time_limit"], "01:00:00")
        self.assertEqual(contract["execution_roots"]["deployment_root"], SUCCESSOR_ROOT)
        self.assertEqual(contract["execution_roots"]["run_root"], RUN_ROOT)
        self.assertEqual(
            contract["execution_roots"]["output_root"], RUN_ROOT + "/evidence"
        )
        self.assertEqual(
            contract["execution_roots"]["submit_log_root"], SUBMIT_LOG_ROOT
        )
        self.assertEqual(
            contract["gpu_identity_gate"]["nvidia_smi_argv"][0],
            "/usr/bin/nvidia-smi",
        )
        self.assertIs(contract["mapping_gate"]["server_backend_and_model_required"], True)
        self.assertIs(
            contract["mapping_gate"]["server_executable_proc_exe_identity_required"],
            True,
        )
        self.assertIs(contract["mapping_gate"]["reattestation_required_after_gpu_identity"], True)
        self.assertEqual(source.splitlines()[0], "#!/usr/bin/bash")
        self.assertIn(f"SUCCESSOR_ROOT='{SUCCESSOR_ROOT}'", source)
        self.assertIn(f"RUN_ROOT='{RUN_ROOT}'", source)
        self.assertNotIn("--wrap", source)
        self.assertNotIn("sbatch ", source)
        self.assertNotIn("srun ", source)
        self.assertNotIn("sacct ", source)
        self.assertNotIn("scontrol ", source)

    def test_14_trampoline_binds_sources_and_exact_zero_input_argv(self) -> None:
        source = TRAMPOLINE_PATH.read_text()
        self.assertIn('[[ "$#" -eq 0 ]]', source)
        self.assertIn("|| fail_body_free 'ARGV_INVALID'", source)
        expected_exec = (
            'exec "$PYTHON_COMMAND" -I -S -B "$MODULE_PATH" '
            '--output-root "$RUN_ROOT/evidence"'
        )
        self.assertEqual(source.count(expected_exec), 1)
        self.assertNotIn('"$@"', source)
        self.assertIn('verify_bound_file "$MODULE_PATH" "$MODULE_SHA256"', source)
        self.assertIn('verify_bound_file "$CONTRACT_PATH" "$CONTRACT_SHA256"', source)
        self.assertIn('"$CMP_PATH" -s -- "$0" "$CANONICAL_TRAMPOLINE"', source)
        self.assertIn('[[ ! -e "$RUN_ROOT" && ! -L "$RUN_ROOT" ]]', source)
        self.assertIn("os.mkdir(path,0o700)", source)
        self.assertIn('[[ ! -e "$RUN_ROOT/evidence"', source)

    def test_15_trampoline_hashes_are_exact_and_self_normalized(self) -> None:
        payload = TRAMPOLINE_PATH.read_bytes()
        source = payload.decode("utf-8")
        module_sha = assignment(source, "MODULE_SHA256")
        contract_sha = assignment(source, "CONTRACT_SHA256")
        normalized_sha = assignment(source, "NORMALIZED_TRAMPOLINE_SHA256")
        for digest in (module_sha, contract_sha, normalized_sha):
            self.assertIsNotNone(SHA_RE.fullmatch(digest))
            self.assertNotEqual(digest, "0" * 64)
        self.assertEqual(module_sha, sha256_bytes(MODULE_PATH.read_bytes()))
        self.assertEqual(contract_sha, sha256_bytes(CONTRACT_PATH.read_bytes()))
        self.assertEqual(normalized_sha, normalized_trampoline_sha256(payload))
        tampered = payload.replace(b"#SBATCH --mem=64G", b"#SBATCH --mem=63G", 1)
        self.assertNotEqual(normalized_trampoline_sha256(tampered), normalized_sha)

    def test_16_trampoline_is_syntax_valid_and_has_no_protected_body_route(self) -> None:
        bash = Path("/usr/bin/bash")
        if not bash.is_file():
            located = subprocess.run(
                ["/usr/bin/env", "bash", "-n", os.fspath(TRAMPOLINE_PATH)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        else:
            located = subprocess.run(
                [os.fspath(bash), "-n", os.fspath(TRAMPOLINE_PATH)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(located.returncode, 0, located.stderr.decode(errors="replace"))
        source = TRAMPOLINE_PATH.read_text()
        for forbidden in (
            "MASKED_PACKET.json",
            "RECOVERED_PACKET.json",
            "private-inputs",
            "tokenize",
            "completion",
            "finalizer",
            "evaluator",
            "watcher",
        ):
            self.assertNotIn(forbidden, source.casefold())

    def test_17_output_root_and_receipt_use_fd_bound_read_write_custody(self) -> None:
        source = MODULE_PATH.read_text()
        self.assertIn("flags = os.O_RDWR | os.O_CREAT | os.O_EXCL", source)
        self.assertIn("os.pread(fd,", source)
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output_root = Path(directory) / "new-evidence"
            root_fd = self.module._create_new_output_root(output_root)
            receipt_path = output_root / self.module.CANNOT_NAME
            try:
                invented = {"status": "SYNTHETIC_CANNOT_CHECK", "protected_bodies": 0}
                self.module._write_new_receipt(
                    output_root,
                    self.module.CANNOT_NAME,
                    invented,
                    root_fd=root_fd,
                )
                self.assertEqual(
                    receipt_path.read_bytes(),
                    self.module.canonical_json_bytes(invented) + b"\n",
                )
                self.assertEqual(stat.S_IMODE(receipt_path.stat().st_mode), 0o400)
                self.module._seal_output_root(root_fd, output_root)
                self.assertEqual(stat.S_IMODE(output_root.stat().st_mode), 0o500)
            finally:
                os.fchmod(root_fd, 0o700)
                if receipt_path.exists():
                    receipt_path.chmod(0o600)
                os.close(root_fd)

    def test_18_same_length_post_hash_content_drift_fails_closed(self) -> None:
        with self.fixture() as fixture:
            binding = fixture.raw_binding("model.gguf")
            canonical = Path(binding["canonical_path"])
            original_hash = self.module._sha256_fd

            def hash_then_mutate(fd: int) -> str:
                digest = original_hash(fd)
                payload = canonical.read_bytes()
                canonical.write_bytes(bytes([payload[0] ^ 1]) + payload[1:])
                return digest

            self.module._sha256_fd = hash_then_mutate
            try:
                self.assert_gate(
                    "BOUND_FILE_INVALID",
                    lambda: self.module.validate_bound_file(binding, "mutating model"),
                )
            finally:
                self.module._sha256_fd = original_hash

    def test_19_post_hash_custody_drift_fails_closed(self) -> None:
        with self.fixture() as fixture:
            binding = fixture.raw_binding("libggml-cuda.so")
            canonical = Path(binding["canonical_path"])
            original_hash = self.module._sha256_fd

            def hash_then_chmod(fd: int) -> str:
                digest = original_hash(fd)
                canonical.chmod(0o640)
                return digest

            self.module._sha256_fd = hash_then_chmod
            try:
                self.assert_gate(
                    "BOUND_FILE_INVALID",
                    lambda: self.module.validate_bound_file(binding, "chmod backend"),
                )
            finally:
                self.module._sha256_fd = original_hash

    def test_20_runtime_files_are_rehashed_after_final_map_attestation(self) -> None:
        source = MODULE_PATH.read_text()
        first = source.index("first = attest_process_identity(")
        gpu = source.index("gpu = capture_gpu_identity()")
        rebound = source.index("rebound_files = _rebind_runtime_files(")
        second = source.index("second = attest_process_identity(")
        comparison = source.index("if second_bytes != first_bytes:")
        self.assertLess(first, gpu)
        self.assertLess(gpu, second)
        self.assertLess(second, comparison)
        self.assertLess(comparison, rebound)
        self.assertIn(
            'completed_stages.append("RUNTIME_FILES_AND_LISTENER_REBOUND_FINAL")',
            source,
        )
        self.assertIn("rebound_listener = attest_listener(process.pid)", source)
        self.assertIn('"RUNTIME_FILE_REATTESTATION_DRIFT"', source)
        with self.fixture() as fixture:
            bindings = {
                "server": fixture.raw_binding("llama-server"),
                "backend": fixture.raw_binding("libggml-cuda.so"),
                "model": fixture.raw_binding("model.gguf"),
            }
            frozen = {
                label: self.module.validate_bound_file(bindings[label], label)
                for label in ("server", "backend", "model")
            }
            model = Path(bindings["model"]["canonical_path"])
            observed = model.stat()
            os.utime(
                model,
                ns=(observed.st_atime_ns, observed.st_mtime_ns + 1_000_000_000),
            )
            self.assert_gate(
                "RUNTIME_FILE_REATTESTATION_DRIFT",
                lambda: self.module._rebind_runtime_files(bindings, frozen),
            )
        schema = json.loads(CONTRACT_PATH.with_name(
            "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json"
        ).read_text())
        runtime_fields = schema["success"]["nested_required_fields"]["runtime_file"]
        self.assertIn("mtime_ns", runtime_fields)
        self.assertIn("ctime_ns", runtime_fields)

    def test_21_request_provenance_names_types_without_implied_counts(self) -> None:
        source = MODULE_PATH.read_text()
        self.assertIn("BODY_FREE_HTTP_REQUEST_TYPES_ALLOWED", source)
        self.assertIn('"body_free_http_request_types_allowed"', source)
        self.assertIn('"successful_response_request_types"', source)
        self.assertNotIn("BODY_FREE_HTTP_REQUESTS", source)
        self.assertNotIn('"body_free_http_requests"', source)
        schema = json.loads(CONTRACT_PATH.with_name(
            "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json"
        ).read_text())
        for section in ("success", "cannot_check"):
            exact = schema[section]["exact_common_values"]
            self.assertEqual(
                exact["body_free_http_request_types_allowed"],
                ["GET /health", "GET /slots"],
            )
            self.assertNotIn("body_free_http_requests", exact)
        readiness = schema["success"]["nested_required_fields"]["readiness"]
        self.assertIn("successful_response_request_types", readiness)
        self.assertNotIn("requests", readiness)

    def test_22_listener_rejects_every_extra_owned_tcp_or_tcp6_socket(self) -> None:
        with self.fixture() as fixture:
            exact = fixture.attest_listener()
            self.assertEqual(exact["listen_host"], "127.0.0.1")
            self.assertEqual(exact["listen_port"], 8080)
            self.assertEqual(exact["socket_inode"], fixture.listener_inode)
            for protocol, local in (
                ("tcp", "00000000:2382"),
                ("tcp6", "00000000000000000000000000000000:2382"),
            ):
                with self.subTest(protocol=protocol):
                    fixture.write_listener_tables(
                        [
                            ("tcp", "0100007F:1F90", fixture.listener_inode, True),
                            (protocol, local, "900002", True),
                        ]
                    )
                    self.assert_gate("LISTENER_DRIFT", fixture.attest_listener)
            fixture.write_listener_tables(
                [
                    ("tcp", "0100007F:1F90", fixture.listener_inode, True),
                    ("tcp6", "00000000000000000000000000000000:2382", "900003", False),
                ]
            )
            self.assertEqual(fixture.attest_listener()["socket_inode"], fixture.listener_inode)
            fd_root = fixture.proc_root / str(fixture.pid) / "fd"
            unreadable = fd_root / "99"
            unreadable.symlink_to("socket:[900004]")
            original_readlink = self.module.os.readlink

            def fail_one_readlink(path: Any) -> str:
                if Path(path) == unreadable:
                    raise OSError("synthetic unreadable fd")
                return original_readlink(path)

            self.module.os.readlink = fail_one_readlink
            try:
                self.assert_gate("LISTENER_DRIFT", fixture.attest_listener)
            finally:
                self.module.os.readlink = original_readlink
            fixture.write_listener_tables(
                [("tcp", "0100007F:1F90", fixture.listener_inode, True)]
            )
            original_snapshot = self.module._snapshot_socket_inodes
            calls = 0

            def inject_persistent_listener(fd_root: Path) -> set[str]:
                nonlocal calls
                calls += 1
                snapshot = original_snapshot(fd_root)
                if calls == 1:
                    (fd_root / "98").symlink_to("socket:[900009]")
                    tcp = fixture.pid_root / "net/tcp"
                    with tcp.open("a", encoding="ascii") as handle:
                        handle.write(
                            "9: 00000000:2382 00000000:0000 0A "
                            "00000000:00000000 00:00000000 00000000 "
                            "1000 0 900009\n"
                        )
                return snapshot

            self.module._snapshot_socket_inodes = inject_persistent_listener
            try:
                self.assert_gate("LISTENER_DRIFT", fixture.attest_listener)
                self.assertEqual(calls, 2)
                self.assertTrue((fd_root / "98").is_symlink())
            finally:
                self.module._snapshot_socket_inodes = original_snapshot

    def test_23_log_capture_unavailable_variant_is_truthful_and_schema_bound(self) -> None:
        class BrokenStream:
            def flush(self) -> None:
                raise OSError("synthetic log capture failure")

        schema = json.loads(CONTRACT_PATH.with_name(
            "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json"
        ).read_text())
        variants = schema["server_log_stream_variants"]
        for handle in (None, BrokenStream()):
            binding, error = self.module._safe_stream_binding(handle, "synthetic")
            self.assertIsNotNone(error)
            self.assertEqual(error.code, "LOG_CAPTURE_FAILED")
            self.assertEqual(
                binding["status"], variants["unavailable"]["exact_values"]["status"]
            )
            self.assertTrue(set(variants["unavailable"]["required_fields"]) <= set(binding))
            self.assertFalse(set(variants["unavailable"]["forbidden_fields"]) & set(binding))
            self.assertIsNotNone(SHA_RE.fullmatch(binding["failure_detail_sha256"]))
        with tempfile.TemporaryFile(mode="w+b") as handle:
            handle.write(b"synthetic-log")
            binding, error = self.module._safe_stream_binding(handle, "synthetic")
        self.assertIsNone(error)
        self.assertTrue(set(variants["available"]["required_fields"]) <= set(binding))
        self.assertFalse(set(variants["available"]["forbidden_fields"]) & set(binding))

    def test_24_gpu_rc_zero_empty_stderr_exact_a40_passes_with_exact_capture(self) -> None:
        stdout = b"0, GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0, NVIDIA A40\n"
        completed = self.completed_gpu_call(stdout)
        environment = self.valid_gpu_environment()
        with self.installed_gpu_runner(completed) as calls:
            observed = self.module.capture_gpu_identity(environment)
        self.assertEqual(len(calls), 1)
        argv, kwargs = calls[0]
        self.assertEqual(argv, list(self.module.NVIDIA_SMI_ARGV))
        self.assertEqual(
            kwargs,
            {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "env": {
                    key: environment[key]
                    for key in (
                        "HOME",
                        "PATH",
                        "LANG",
                        "LC_ALL",
                        "LC_CTYPE",
                        "CUDA_VISIBLE_DEVICES",
                    )
                },
                "check": False,
                "timeout": 30,
            },
        )
        self.assertEqual(observed["slurm_job_id"], "3539001")
        self.assertEqual(observed["cuda_visible_devices"], "0")
        self.assertEqual(observed["slurm_job_gpus"], "0")
        self.assertIsNone(observed["slurm_step_gpus"])
        self.assertEqual(observed["visible_index"], "0")
        self.assertEqual(
            observed["gpu_uuid"], "GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0"
        )
        self.assertEqual(observed["name"], "NVIDIA A40")
        self.assertEqual(set(observed["nvidia_smi"]), {
            "status",
            "argv",
            "return_code",
            "stdout",
            "stderr",
            "stdout_parse_attempted",
        })
        self.assert_gpu_capture(
            observed["nvidia_smi"], completed, stdout_parse_attempted=True
        )

    def test_25_gpu_rc_zero_nonempty_stderr_never_parses_or_promotes_stdout(self) -> None:
        fixtures = (
            b"0, GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16, NVIDIA A40\n",
            b"malformed stdout without a final LF",
        )
        for stdout in fixtures:
            with self.subTest(stdout=stdout):
                completed = self.completed_gpu_call(
                    stdout, stderr=b"synthetic diagnostic\n"
                )
                error = self.capture_gpu_failure(
                    completed, "NVIDIA_SMI_STDERR_NONEMPTY"
                )
                self.assert_gpu_capture(
                    error.gpu_capture,
                    completed,
                    stdout_parse_attempted=False,
                )
                self.assertNotIn("parse", str(error).casefold())
                self.assertNotIn("valid", str(error).casefold())

    def test_26_gpu_nonzero_empty_or_nonempty_stderr_is_typed_and_bound(self) -> None:
        for stderr in (b"", b"synthetic nvml failure\n"):
            with self.subTest(stderr=stderr):
                completed = self.completed_gpu_call(
                    b"untrusted stdout", stderr=stderr, return_code=17
                )
                error = self.capture_gpu_failure(
                    completed, "NVIDIA_SMI_NONZERO_RETURN"
                )
                self.assert_gpu_capture(
                    error.gpu_capture,
                    completed,
                    stdout_parse_attempted=False,
                )

    def test_27_gpu_precompletion_failures_are_typed_without_capture(self) -> None:
        fixtures = (
            (
                subprocess.TimeoutExpired(
                    list(self.module.NVIDIA_SMI_ARGV),
                    30,
                    output=b"partial",
                    stderr=b"partial diagnostic",
                ),
                "NVIDIA_SMI_TIMEOUT",
            ),
            (OSError("synthetic exec failure"), "NVIDIA_SMI_EXECUTION_ERROR"),
        )
        for outcome, subcode in fixtures:
            with self.subTest(subcode=subcode):
                with self.installed_gpu_runner(outcome):
                    with self.assertRaises(self.module.GateError) as caught:
                        self.module.capture_gpu_identity(self.valid_gpu_environment())
                self.assertEqual(caught.exception.code, "GPU_IDENTITY_INVALID")
                self.assertEqual(caught.exception.failure_subcode, subcode)
                self.assertIsNone(caught.exception.gpu_capture)

        invalid_inputs = (
            ({"CUDA_VISIBLE_DEVICES": "0"}, "SLURM_JOB_ID_INVALID"),
            (
                {"SLURM_JOB_ID": "3539001", "CUDA_VISIBLE_DEVICES": "0,1"},
                "CUDA_VISIBLE_DEVICES_INVALID",
            ),
        )
        for environment, subcode in invalid_inputs:
            with self.subTest(subcode=subcode):
                with self.installed_gpu_runner(AssertionError("runner must not execute")) as calls:
                    with self.assertRaises(self.module.GateError) as caught:
                        self.module.capture_gpu_identity(environment)
                self.assertEqual(calls, [])
                self.assertEqual(caught.exception.failure_subcode, subcode)
                self.assertIsNone(caught.exception.gpu_capture)

    def test_28_gpu_utf8_and_framing_failures_retain_attempted_capture(self) -> None:
        fixtures = (
            (b"\xff\n", "NVIDIA_SMI_STDOUT_UTF8_INVALID"),
            (
                b"0, GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0, NVIDIA A40",
                "NVIDIA_SMI_STDOUT_FRAMING_INVALID",
            ),
            (
                b"0, GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0, NVIDIA A40\r\n",
                "NVIDIA_SMI_STDOUT_FRAMING_INVALID",
            ),
        )
        for stdout, subcode in fixtures:
            with self.subTest(subcode=subcode, stdout=stdout):
                completed = self.completed_gpu_call(stdout)
                error = self.capture_gpu_failure(completed, subcode)
                self.assert_gpu_capture(
                    error.gpu_capture,
                    completed,
                    stdout_parse_attempted=True,
                )

    def test_29_gpu_row_index_uuid_and_model_failures_are_distinctly_typed(self) -> None:
        uuid_ = "GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0"
        fixtures = (
            (b"", "NVIDIA_SMI_VISIBLE_ROW_COUNT_INVALID"),
            (
                f"0, {uuid_}, NVIDIA A40\n0, {uuid_}, NVIDIA A40\n".encode(),
                "NVIDIA_SMI_VISIBLE_ROW_COUNT_INVALID",
            ),
            (
                f"-1, {uuid_}, NVIDIA A40\n".encode(),
                "NVIDIA_SMI_VISIBLE_ROW_INVALID",
            ),
            (
                b"0, GPU-not-a-canonical-uuid, NVIDIA A40\n",
                "NVIDIA_SMI_VISIBLE_ROW_INVALID",
            ),
            (
                f"0, {uuid_}, NVIDIA H100\n".encode(),
                "NVIDIA_SMI_GPU_MODEL_INVALID",
            ),
        )
        for stdout, subcode in fixtures:
            with self.subTest(subcode=subcode, stdout=stdout):
                completed = self.completed_gpu_call(stdout)
                error = self.capture_gpu_failure(completed, subcode)
                self.assert_gpu_capture(
                    error.gpu_capture,
                    completed,
                    stdout_parse_attempted=True,
                )

    def test_30_failure_receipt_surface_preserves_typed_gpu_capture_boundary(self) -> None:
        source = MODULE_PATH.read_text()
        self.assertIn('receipt["failure_subcode"] = error.failure_subcode', source)
        self.assertIn("if error.failure_subcode is not None:", source)
        self.assertNotIn('"failure_subcode": error.failure_subcode,', source)
        self.assertIn("if caught is not None and gpu_capture is not None:", source)
        self.assertIn('common["gpu_capture"] = gpu_capture', source)
        self.assertIn('"nvidia_smi": capture', source)
        self.assertNotIn('"gpu_capture": None', source)

    def test_31_contract_and_schema_freeze_the_exact_gpu_capture_policy(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        gate = contract["gpu_identity_gate"]
        self.assertEqual(gate["nvidia_smi_argv"], list(self.module.NVIDIA_SMI_ARGV))
        self.assertEqual(
            gate["precompletion_failure_subcodes"],
            [
                "SLURM_JOB_ID_INVALID",
                "CUDA_VISIBLE_DEVICES_INVALID",
                "NVIDIA_SMI_EXECUTION_ERROR",
                "NVIDIA_SMI_TIMEOUT",
            ],
        )
        self.assertEqual(
            gate["completed_call_failure_subcodes"],
            [
                "NVIDIA_SMI_NONZERO_RETURN",
                "NVIDIA_SMI_STDERR_NONEMPTY",
                "NVIDIA_SMI_STDOUT_UTF8_INVALID",
                "NVIDIA_SMI_STDOUT_FRAMING_INVALID",
                "NVIDIA_SMI_VISIBLE_ROW_COUNT_INVALID",
                "NVIDIA_SMI_VISIBLE_ROW_INVALID",
                "NVIDIA_SMI_GPU_MODEL_INVALID",
            ],
        )
        self.assertEqual(
            gate["completed_call_capture"],
            {
                "receipt_field": "gpu_capture",
                "required_fields": [
                    "status",
                    "argv",
                    "return_code",
                    "stdout",
                    "stderr",
                    "stdout_parse_attempted",
                ],
                "status": "COMPLETED",
                "stream_required_fields": ["bytes", "sha256"],
            },
        )
        self.assertEqual(
            gate["parse_policy"],
            {
                "eligible_condition": "RETURN_CODE_ZERO_AND_STDERR_BYTES_ZERO",
                "malformed_stdout_is_never_described_as_parseable": True,
                "nonempty_stderr_tolerated": False,
                "stdout_parse_attempted_for_nonzero_return": False,
                "stdout_parse_attempted_for_zero_return_nonempty_stderr": False,
            },
        )

        schema = json.loads(
            CONTRACT_PATH.with_name(
                "BACKEND_CANONICAL_MAP_DISCRIMINATOR_OUTPUT_SCHEMA_V2.json"
            ).read_text()
        )
        self.assertEqual(schema["status"], "FROZEN_NOT_EXECUTED")
        self.assertEqual(schema["gpu_capture"]["exact_values"], {
            "argv": list(self.module.NVIDIA_SMI_ARGV),
            "status": "COMPLETED",
        })
        policy = schema["gpu_capture_policy"]
        self.assertIs(policy["completed_call_always_retained"], True)
        self.assertIs(policy["precompletion_failure_omits_gpu_capture"], True)
        self.assertIs(policy["nonempty_stderr_tolerated"], False)
        self.assertEqual(policy["success_location"], "gpu.nvidia_smi")
        variants = schema["cannot_check"]["gpu_failure_variants"]
        self.assertIs(variants["completed_call"]["gpu_capture_required"], True)
        self.assertIs(variants["precompletion"]["gpu_capture_forbidden"], True)
        self.assertEqual(
            variants["non_gpu_failure_with_completed_capture"],
            {
                "capture_may_reflect_prior_gpu_outcome": True,
                "failure_subcode_forbidden": True,
                "gpu_capture_required": True,
                "interpretation": (
                    "RETAIN_EXACT_COMPLETED_CALL_BINDING_WITHOUT_"
                    "REINTERPRETING_THE_NON_GPU_FAILURE"
                ),
            },
        )

    def test_32_predecessor_binding_is_exact_and_nonpromoting(self) -> None:
        raw = PREDECESSOR_PATH.read_bytes()
        predecessor = json.loads(raw.decode("utf-8"))
        self.assertEqual(self.module.canonical_json_bytes(predecessor) + b"\n", raw)
        contract = json.loads(CONTRACT_PATH.read_text())
        self.assertEqual(
            contract["predecessor"]["binding"],
            {
                "bytes": len(raw),
                "file": PREDECESSOR_PATH.name,
                "sha256": sha256_bytes(raw),
            },
        )
        self.assertEqual(
            predecessor["bound_at_merged_main_commit"],
            "cf002879df0aac27d269d6fa1477818ab507d15a",
        )
        self.assertEqual(
            predecessor["status"], "PASS_BOUND_JOB_3537910_ADVERSE_PREDECESSOR"
        )
        self.assertEqual(set(predecessor["artifacts"]), set(EXPECTED_PREDECESSOR_ARTIFACTS))
        for name, (expected_bytes, expected_sha256) in EXPECTED_PREDECESSOR_ARTIFACTS.items():
            source_raw = (PREDECESSOR_SOURCE_ROOT / name).read_bytes()
            self.assertEqual(len(source_raw), expected_bytes)
            self.assertEqual(sha256_bytes(source_raw), expected_sha256)
            self.assertEqual(
                predecessor["artifacts"][name],
                {"bytes": expected_bytes, "sha256": expected_sha256},
            )
        self.assertEqual(
            predecessor["job"],
            {
                "allocated_gpu_count": 1,
                "allocated_gpu_scope": "SCHEDULER_A40_GRES_ONLY__LIVE_GPU_IDENTITY_CANNOT_CHECK",
                "elapsed_seconds": 86,
                "exit_code": "1:0",
                "job_id": "3537910",
                "node": "cg14",
                "scheduler_gpu_allocation_seconds": 86,
                "state": "FAILED",
            },
        )
        self.assertEqual(
            predecessor["completed_stages"],
            [
                "CONTRACT_BOUND",
                "RUNTIME_FILES_BOUND",
                "SERVER_STARTED",
                "SERVER_READY_BODY_FREE",
                "CANONICAL_MAP_ATTESTATION_1",
                "SERVER_CLEANUP_PASS",
            ],
        )
        self.assertIs(predecessor["cannot_check_boundary"]["discriminator_pass"], False)
        self.assertIs(predecessor["cannot_check_boundary"]["gpu_identity_bound"], False)
        self.assertEqual(
            predecessor["cannot_check_boundary"]["production_admissibility"],
            "CANNOT_CHECK",
        )
        self.assertEqual(predecessor["truthful_scope"]["scientific_authority_delta"], "NONE")
        for key in (
            "completion_requests",
            "generation_invocations",
            "official_outcomes_opened",
            "protected_packet_bodies_opened",
            "protected_prompt_bodies_opened",
            "tokenize_requests",
        ):
            self.assertEqual(predecessor["truthful_scope"][key], 0)
        self.assertIs(predecessor["truthful_scope"]["official_evaluator_invoked"], False)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BackendCanonicalMapDiscriminatorTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} protected_bodies=0 tokenize=0 completion=0 "
        "generation=0 jobs=0 outcomes=0 production_admissibility=CANNOT_CHECK "
        "scientific_authority=NONE"
    )
