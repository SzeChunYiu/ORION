#!/usr/bin/env python3
"""Synthetic hostile validator for the additive direct-route SLURM preflight."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
BRIDGE_PATH = ROOT / "direct_route_slurm_preflight_v1.py"
CONTRACT_PATH = ROOT / "DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V1.json"
LAUNCHER_PATH = ROOT / "run_direct_route_slurm_preflight_v1.sh"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"

DIRECT_LANE = REPO_ROOT / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24"
ADAPTER_LANE = REPO_ROOT / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24"

UPSTREAM = {
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py": "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh": "1d4655350c1a037cd4e51ee11e15e21491c5bfd7cea125948beb2e152c73b582",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DirectRouteSlurmPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not BRIDGE_PATH.is_file():
            raise AssertionError("direct-route SLURM preflight bridge is not implemented")
        spec = importlib.util.spec_from_file_location("direct_route_slurm_preflight_v1", BRIDGE_PATH)
        if spec is None or spec.loader is None:
            raise AssertionError("preflight bridge cannot be loaded")
        cls.bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.bridge)
        fixture_path = DIRECT_LANE / "validate_direct_route_freeze_v1.py"
        fixture_spec = importlib.util.spec_from_file_location("direct_route_fixture_for_preflight", fixture_path)
        if fixture_spec is None or fixture_spec.loader is None:
            raise AssertionError("direct-route synthetic fixture cannot be loaded")
        cls.fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(cls.fixture)

    def test_01_exact_merged_upstream_bindings(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        declared = {item["path"]: item["sha256"] for item in contract["upstream_bindings"]}
        self.assertEqual(declared, UPSTREAM)
        for relative, expected in UPSTREAM.items():
            self.assertEqual(sha256_file(REPO_ROOT / relative), expected)
        self.bridge.validate_frozen_upstream(contract)

    def test_02_lower_claim_boundary_is_exact(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        self.assertEqual(
            contract["claim_boundary"],
            {
                "official_tasks_opened": 0,
                "official_outcomes_opened": 0,
                "task_fit_status": "CANNOT_CHECK_BEFORE_TASK_OPENING",
                "production_admissibility": "CANNOT_CHECK",
                "scheduler_finalization_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
                "scientific_authority_delta": "NONE",
                "semantic_choice_sensitivity": "NOT_ESTABLISHED",
            },
        )

    def test_03_server_argv_freezes_exact_loopback_geometry(self) -> None:
        argv = self.bridge.build_server_argv(Path("/runtime/llama-server"), Path("/runtime/model.gguf"))
        self.assertEqual(argv[0], "/runtime/llama-server")
        pairs = list(zip(argv, argv[1:]))
        self.assertIn(("--host", "127.0.0.1"), pairs)
        self.assertIn(("--port", "8080"), pairs)
        self.assertIn(("--ctx-size", "32768"), pairs)
        self.assertIn(("--parallel", "1"), pairs)
        self.assertIn("--no-cont-batching", argv)
        self.assertIn("--no-context-shift", argv)
        self.assertNotIn("--context-shift", argv)

    def test_04_runtime_stage_hashes_model_server_backend_launcher_and_inputs(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            files = {}
            for name in ("plan", "owner", "runtime", "masked", "recovered", "model", "server", "backend", "launcher"):
                path = base / name
                path.write_bytes((name + "\n").encode())
                files[name] = path
            expected = {name: sha256_file(path) for name, path in files.items()}
            stage = self.bridge.build_runtime_stage_for_test(
                contract=contract,
                paths=files,
                expected_sha256=expected,
                task_id="1",
                arm_id="OS",
                attempt=1,
            )
            self.assertEqual(stage["runtime_observed_sha256"]["model"], expected["model"])
            self.assertEqual(stage["runtime_observed_sha256"]["llama_server"], expected["server"])
            self.assertEqual(stage["runtime_observed_sha256"]["cuda_backend"], expected["backend"])
            self.assertEqual(stage["runtime_observed_sha256"]["launcher"], expected["launcher"])
            self.assertEqual(stage["runtime_observed_sha256"]["preflight_bridge"], sha256_file(BRIDGE_PATH))
            self.assertEqual(stage["run_plan_binding_extension"]["run_plan_sha256"], expected["plan"])
            self.assertEqual(stage["run_plan_binding_extension"]["direct_driver_sha256"], UPSTREAM[next(iter(UPSTREAM))])
            self.assertEqual(stage["run_plan_binding_extension"]["preflight_bridge_sha256"], sha256_file(BRIDGE_PATH))
            self.assertFalse(stage["run_plan_binding_extension"]["upstream_wrapper_execution_allowed"])
            self.assertEqual(
                stage["run_plan_binding_extension"]["upstream_wrapper_binding_role"],
                "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
            )
            bad = dict(expected); bad["model"] = "0" * 64
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge.build_runtime_stage_for_test(contract, files, bad, "1", "OS", 1)

    def test_05_deadline_client_uses_one_remaining_raw_deadline_across_phases(self) -> None:
        clock_values = iter((10_000_000_000, 11_000_000_000, 12_000_000_000, 15_500_000_000))
        deadline = self.bridge.RawDeadline(5_000_000_000, raw_clock=lambda: next(clock_values))
        self.assertEqual(deadline.capture_clock(), 10_000_000_000)
        self.assertEqual(deadline.remaining_seconds(), 4.0)
        self.assertEqual(deadline.remaining_seconds(), 3.0)
        with self.assertRaises(self.bridge.AttemptDeadlineExceeded):
            deadline.remaining_seconds()

    def test_06_adapter_failure_emits_typed_cannot_check_sidecar(self) -> None:
        fake = mock.Mock()
        fake.cannot_check_sidecar.return_value = {"status": "CANNOT_CHECK", "failure_code": "ATTEMPT_DEADLINE_EXCEEDED"}
        sidecar = self.bridge.capture_failure_sidecar(fake, self.bridge.AttemptDeadlineExceeded("expired"))
        self.assertEqual(sidecar["failure_code"], "ATTEMPT_DEADLINE_EXCEEDED")
        fake.cannot_check_sidecar.assert_called_once()

    def test_07_process_attestation_rejects_executable_or_cmdline_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            server = base / "server"; server.write_bytes(b"server")
            proc = base / "proc"; pid_root = proc / "42"; pid_root.mkdir(parents=True)
            (pid_root / "exe").symlink_to(server)
            model = base / "model"; model.write_bytes(b"model")
            argv = [str(server), "--model", str(model), "--host", "127.0.0.1"]
            backend = base / "backend"; backend.write_bytes(b"backend")
            backend_info = backend.stat()
            backend_device = f"{os.major(backend_info.st_dev):02x}:{os.minor(backend_info.st_dev):02x}"
            model_info = model.stat()
            model_device = f"{os.major(model_info.st_dev):02x}:{os.minor(model_info.st_dev):02x}"
            (pid_root / "cmdline").write_bytes(b"\0".join(item.encode() for item in argv) + b"\0")
            (pid_root / "environ").write_bytes(f"GGML_BACKEND_PATH={backend}\0HTTP_PROXY=\0".encode())
            (pid_root / "maps").write_text(
                f"7e000000-7e001000 r--p 00000000 {model_device} {model_info.st_ino} {model}\n"
                f"7f000000-7f001000 r-xp 00000000 {backend_device} {backend_info.st_ino} {backend}\n"
            )
            attested = self.bridge.attest_process_identity(
                42, server, argv, str(backend), proc_root=proc
            )
            self.assertEqual(attested["executable_sha256"], sha256_file(server))
            self.assertEqual(attested["cuda_backend_mapped_path"], str(backend))
            self.assertEqual(attested["model_mapped_path"], str(model))
            (pid_root / "maps").write_text(
                f"7e000000-7e001000 r--p 00000000 {model_device} {model_info.st_ino} {model}\n"
                f"7f000000-7f001000 r-xp 00000000 {backend_device} {backend_info.st_ino + 1} {backend}\n"
            )
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge.attest_process_identity(42, server, argv, str(backend), proc_root=proc)
            (pid_root / "maps").write_text(
                f"7e000000-7e001000 r--p 00000000 {model_device} {model_info.st_ino} {model}\n"
                f"7f000000-7f001000 r-xp 00000000 {backend_device} {backend_info.st_ino} {backend}\n"
            )
            (pid_root / "cmdline").write_bytes(b"drift\0")
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge.attest_process_identity(42, server, argv, str(backend), proc_root=proc)

    def test_08_launcher_is_only_additive_supervisor_entrypoint(self) -> None:
        source = LAUNCHER_PATH.read_text()
        for token in (
            "#SBATCH --gres=gpu:a40:1",
            "#SBATCH --nodes=1",
            "#SBATCH --ntasks=1",
            "supervise",
        ):
            self.assertIn(token, source)
        self.assertNotIn("pytest", source)

    def test_09_bridge_source_has_no_evaluator_outcome_or_protected_route(self) -> None:
        source = BRIDGE_PATH.read_text()
        for forbidden in ("gold_program", "official_evaluator", "eval_programs", "scoring_rubrics"):
            self.assertNotIn(forbidden, source)
        self.assertIn("127.0.0.1", source)

    def _synthetic_attempt_inputs(self, base: Path, arm: str) -> tuple[dict, dict[str, Path]]:
        contract = json.loads(self.fixture.CONTRACT_PATH.read_text())
        prompt = json.loads(self.fixture.PROMPT_PATH.read_text())
        plan = self.fixture.synthetic_plan(contract, prompt)
        values = {
            "plan": plan,
            "owner": contract["budget_owner_selection_interface"],
            "runtime": contract["model_runtime_binding"],
            "masked": {"synthetic": "masked"},
            "recovered": {"synthetic": "recovered"},
        }
        paths: dict[str, Path] = {}
        for name, value in values.items():
            path = base / f"{name}.json"
            path.write_bytes(self.bridge.canonical_json_bytes(value) + b"\n")
            paths[name] = path
        for name in ("model", "server", "backend", "launcher"):
            path = base / name
            path.write_bytes((name + "\n").encode())
            paths[name] = path
        expected = {name: sha256_file(path) for name, path in paths.items()}
        lane_contract = json.loads(CONTRACT_PATH.read_text())
        stage = self.bridge.build_runtime_stage(lane_contract, paths, expected, "1", arm, 1)
        stage = self.bridge.add_prompt_commitments(stage)
        return stage, paths

    def test_10_real_bridge_success_writes_pending_capture_and_prompt_binding(self) -> None:
        response = self.bridge.canonical_json_bytes(
            {
                "content": '{"kind":"FINAL_PROGRAM","program":"print(1)"}',
                "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
                "tokens_predicted": 12,
                "truncated": False,
            }
        )

        class FakeResponse:
            status = 200
            def read(self) -> bytes: return response

        class FakeConnection:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                self.timeout = timeout
                self.host = host; self.port = port
            def request(self, method: str, path: str, **kwargs) -> None:
                self.method = method; self.path = path
            def getresponse(self): return FakeResponse()
            def close(self) -> None: pass

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            stage, paths = self._synthetic_attempt_inputs(base, "OS")
            ticks = iter((10_000_000_000, 10_100_000_000, 10_200_000_000, 12_500_000_000))
            output_dir_fd = os.open(base, os.O_RDONLY)
            try:
                self.bridge.execute_bridge_attempt(
                    stage=stage,
                    stage_sha256=self.bridge.canonical_hash(stage),
                    attestation_sha256="a" * 64,
                    slurm_identity={
                        "slurm_job_identity": {"cluster": "lunarc", "job_id": "4000001", "array_job_id": None, "array_task_id": None},
                        "slurm_in_job_snapshot_sha256": "b" * 64,
                    },
                    output_dir=base,
                    output_dir_fd=output_dir_fd,
                    raw_clock=lambda: next(ticks),
                    connection_factory=FakeConnection,
                )
            finally:
                os.close(output_dir_fd)
            capture = json.loads((base / "ATTEMPT_CAPTURE_V1.json").read_text())
            binding = json.loads((base / "DIRECT_ROUTE_BRIDGE_BINDING_V1.json").read_text())
            self.assertEqual(capture["status"], "TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING")
            self.assertEqual(capture["base_candidate_record"]["wall_time_seconds"], 2.5)
            self.assertEqual(binding["request_bindings"][0]["phase_id"], "OS_PHASE1")

    def test_11_cross_phase_deadline_emits_real_adapter_cannot_check_sidecar(self) -> None:
        phase0 = self.bridge.canonical_json_bytes(
            {
                "content": self.bridge.canonical_json_bytes(
                    {
                        "kind": "RR_TYPED_STATE",
                        "assumptions": ["synthetic"],
                        "unresolved_inputs": [],
                        "intended_analysis": ["synthetic"],
                        "invariants": ["synthetic"],
                        "output_contract": "synthetic",
                    }
                ).decode(),
                "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
                "tokens_predicted": 12,
                "truncated": False,
            }
        )

        class FakeResponse:
            status = 200
            def read(self) -> bytes: return phase0

        class FakeConnection:
            def __init__(self, host: str, port: int, timeout: float) -> None: pass
            def request(self, method: str, path: str, **kwargs) -> None: pass
            def getresponse(self): return FakeResponse()
            def close(self) -> None: pass

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            stage, _ = self._synthetic_attempt_inputs(base, "RR")
            ticks = iter((
                10_000_000_000,
                10_100_000_000,
                10_200_000_000,
                1_810_000_000_001,
                1_810_100_000_000,
            ))
            output_dir_fd = os.open(base, os.O_RDONLY)
            try:
                with self.assertRaises(self.bridge.PreflightError):
                    self.bridge.execute_bridge_attempt(
                        stage=stage,
                        stage_sha256=self.bridge.canonical_hash(stage),
                        attestation_sha256="a" * 64,
                        slurm_identity={
                            "slurm_job_identity": {"cluster": "lunarc", "job_id": "4000002", "array_job_id": None, "array_task_id": None},
                            "slurm_in_job_snapshot_sha256": "b" * 64,
                        },
                        output_dir=base,
                        output_dir_fd=output_dir_fd,
                        raw_clock=lambda: next(ticks),
                        connection_factory=FakeConnection,
                    )
            finally:
                os.close(output_dir_fd)
            sidecar = json.loads((base / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json").read_text())
            self.assertEqual(sidecar["status"], "CANNOT_CHECK")
            self.assertEqual(sidecar["failure_code"], "ATTEMPT_DEADLINE_EXCEEDED")
            self.assertEqual(sidecar["attempted_phase_sequence"], ["RR_PHASE0", "RR_PHASE1"])
            self.assertFalse((base / "ATTEMPT_CAPTURE_V1.json").exists())

    def test_12_backend_mapping_attestation_occurs_after_server_readiness(self) -> None:
        source = inspect.getsource(self.bridge.run_supervisor)
        ready_index = source.index("ready = wait_for_exact_server(process)")
        identity_index = source.index("process_identity = attest_process_identity(")
        self.assertLess(ready_index, identity_index)

    def test_13_bridge_rehashes_every_staged_input_before_capture(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            stage, paths = self._synthetic_attempt_inputs(base, "OS")
            self.bridge.validate_staged_files_unchanged(stage)
            paths["plan"].write_bytes(b"drift\n")
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge.validate_staged_files_unchanged(stage)

    def test_14_runtime_json_inputs_are_exact_new_file_snapshots(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            source = {}
            for name in ("plan", "owner", "runtime", "masked", "recovered"):
                path = base / f"source-{name}.json"
                path.write_bytes((name + "\n").encode())
                source[name] = path
            snapshots = self.bridge.stage_runtime_snapshots(source, base / "snapshots")
            for name, path in snapshots.items():
                self.assertEqual(path.read_bytes(), source[name].read_bytes())
                self.assertNotEqual(path.stat().st_ino, source[name].stat().st_ino)
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge.stage_runtime_snapshots(source, base / "snapshots")

    def test_15_cleanup_terminates_the_owned_process_group(self) -> None:
        process = mock.Mock()
        process.pid = 42
        process.returncode = -15
        process.poll.return_value = -15
        alive = True
        calls = []

        def fake_killpg(pgid, requested_signal):
            nonlocal alive
            calls.append((pgid, requested_signal))
            if requested_signal == 0:
                if alive:
                    return None
                raise ProcessLookupError
            if requested_signal == self.bridge.signal.SIGTERM:
                alive = False

        with mock.patch.object(self.bridge.os, "killpg", side_effect=fake_killpg):
            receipt = self.bridge.stop_managed_process(process, "llama-server")
        self.assertIn((42, self.bridge.signal.SIGTERM), calls)
        self.assertTrue(receipt["process_group_absent_after_cleanup"])
        self.assertTrue(receipt["process_absent_after_cleanup"])

    def test_16_bridge_outputs_reject_symlink_parent(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            real = base / "real"; real.mkdir()
            linked = base / "linked"; linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(self.bridge.PreflightError):
                self.bridge._write_new_json(linked / "receipt.json", {"x": 1})
            self.assertFalse((real / "receipt.json").exists())

    def test_17_contract_binds_exact_bridge_and_launcher_bytes(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        self.assertEqual(
            contract["lane_artifact_bindings"],
            {
                "bridge_sha256": sha256_file(BRIDGE_PATH),
                "launcher_sha256": sha256_file(LAUNCHER_PATH),
            },
        )

    def test_18_synthetic_receipt_binds_final_core_artifacts(self) -> None:
        receipt = json.loads(RECEIPT_PATH.read_text())
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["tests"], 24)
        self.assertEqual(
            receipt["artifact_sha256"],
            {
                "DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V1.json": sha256_file(CONTRACT_PATH),
                "direct_route_slurm_preflight_v1.py": sha256_file(BRIDGE_PATH),
                "run_direct_route_slurm_preflight_v1.sh": sha256_file(LAUNCHER_PATH),
                "validate_direct_route_slurm_preflight_v1.py": sha256_file(Path(__file__)),
            },
        )
        self.assertEqual(receipt["official_tasks_opened"], 0)
        self.assertEqual(receipt["official_outcomes_opened"], 0)
        self.assertEqual(receipt["task_fit_status"], "CANNOT_CHECK_BEFORE_TASK_OPENING")
        self.assertFalse(receipt["wrapper_execution_allowed"])
        self.assertEqual(
            receipt["wrapper_binding_role"],
            "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
        )
        self.assertFalse(receipt["production_descendant_fd_path_dependency"])

    def test_19_new_json_creation_is_bound_to_pinned_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            parent = base / "parent"
            replacement = base / "replacement"
            displaced = base / "displaced"
            parent.mkdir()
            replacement.mkdir()
            real_open = os.open
            swapped = False

            def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if not swapped and Path(os.fspath(path)).name == "receipt.json":
                    parent.rename(displaced)
                    replacement.rename(parent)
                    swapped = True
                if dir_fd is None:
                    return real_open(path, flags, mode)
                return real_open(path, flags, mode, dir_fd=dir_fd)

            with mock.patch.object(self.bridge.os, "open", side_effect=swapping_open):
                self.bridge._write_new_json(parent / "receipt.json", {"x": 1})

            self.assertTrue(swapped)
            self.assertTrue((displaced / "receipt.json").is_file())
            self.assertFalse((parent / "receipt.json").exists())

    def test_20_output_root_creation_is_bound_to_pinned_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            parent = base / "parent"
            replacement = base / "replacement"
            displaced = base / "displaced"
            parent.mkdir()
            replacement.mkdir()
            real_mkdir = os.mkdir
            swapped = False

            def swapping_mkdir(path, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                if not swapped and Path(os.fspath(path)).name == "output":
                    parent.rename(displaced)
                    replacement.rename(parent)
                    swapped = True
                if dir_fd is None:
                    return real_mkdir(path, mode)
                return real_mkdir(path, mode, dir_fd=dir_fd)

            with mock.patch.object(self.bridge.os, "mkdir", side_effect=swapping_mkdir):
                output_fd = self.bridge._create_new_directory(parent / "output", 0o700)
            os.close(output_fd)

            self.assertTrue(swapped)
            self.assertTrue((displaced / "output").is_dir())
            self.assertFalse((parent / "output").exists())

    def test_21_cleanup_kills_group_when_leader_exited_but_child_survives(self) -> None:
        launcher = (
            "import subprocess,sys\n"
            "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])\n"
            "print(child.pid,flush=True)\n"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", launcher],
            stdout=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            assert process.stdout is not None
            child_pid = int(process.stdout.readline().strip())
            process.wait(timeout=5.0)
            os.kill(child_pid, 0)
            receipt = self.bridge.stop_managed_process(
                process,
                "leader-exited-child-survives",
                term_timeout_seconds=5.0,
                kill_timeout_seconds=5.0,
            )
            self.assertIn(receipt["termination_signal"], {"SIGTERM", "SIGKILL"})
            self.assertTrue(receipt["process_group_absent_after_cleanup"])
            self.assertTrue(receipt["process_absent_after_cleanup"])
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass

    def test_22_noninvoked_wrapper_record_cannot_skip_server_cleanup(self) -> None:
        server = mock.Mock()
        calls = []

        def fake_stop(process, label, **_kwargs):
            calls.append((process, label))
            return {
                "label": label,
                "process_started": True,
                "termination_signal": "SIGTERM",
                "return_code": -15,
                "process_group_absent_after_cleanup": True,
                "process_absent_after_cleanup": True,
            }

        with mock.patch.object(self.bridge, "stop_managed_process", side_effect=fake_stop):
            wrapper_record, server_cleanup = self.bridge.cleanup_managed_processes(server)

        self.assertEqual(calls, [(server, "llama-server")])
        self.assertEqual(wrapper_record["status"], "NONINVOKED")
        self.assertFalse(wrapper_record["process_started"])
        self.assertEqual(
            wrapper_record["binding_role"],
            "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
        )
        self.assertTrue(server_cleanup["process_absent_after_cleanup"])

    def test_23_exact_upstream_wrapper_swap_is_witnessed_and_wrapper_is_noninvoked(self) -> None:
        wrapper = ADAPTER_LANE / "run_lunarc_attempt_v1.sh"
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            fake_bin = base / "fake-bin"
            fake_bin.mkdir()
            output = base / "attempt"
            displaced = base / "attempt.displaced"
            plan = base / "plan.json"
            adapter = base / "adapter.py"
            driver = base / "driver.py"
            plan.write_text("{}\n")
            adapter.write_text("# synthetic adapter placeholder\n")

            fake_mkdir = fake_bin / "mkdir"
            fake_mkdir.write_text(
                "#!/usr/bin/env python3\n"
                "import os, subprocess, sys\n"
                "completed = subprocess.run(['/bin/mkdir', *sys.argv[1:]], check=False)\n"
                "if completed.returncode:\n"
                "    raise SystemExit(completed.returncode)\n"
                "target = os.path.abspath(sys.argv[-1])\n"
                "os.rename(target, target + '.displaced')\n"
                "os.mkdir(target, 0o700)\n"
            )
            fake_mkdir.chmod(0o700)
            fake_scontrol = fake_bin / "scontrol"
            fake_scontrol.write_text(
                "#!/bin/bash\n"
                "[[ \"$1\" == show && \"$2\" == job && \"$3\" == -dd && \"$4\" == 4001180 ]] || exit 9\n"
                "printf 'JobId=%s Cluster=%s Synthetic=YES\\n' \"$4\" \"${SLURM_CLUSTER_NAME}\"\n"
            )
            fake_scontrol.chmod(0o700)
            driver.write_text(
                "#!/usr/bin/env python3\n"
                "import argparse, json\n"
                "from pathlib import Path\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--adapter-module')\n"
                "parser.add_argument('--run-plan')\n"
                "parser.add_argument('--task-id')\n"
                "parser.add_argument('--arm')\n"
                "parser.add_argument('--attempt')\n"
                "parser.add_argument('--slurm-identity-json')\n"
                "parser.add_argument('--output-dir', type=Path)\n"
                "args = parser.parse_args()\n"
                "with (args.output_dir / 'ATTEMPT_CAPTURE_V1.json').open('x') as handle:\n"
                "    json.dump({'status': 'SYNTHETIC_CAPTURE'}, handle)\n"
                "    handle.write('\\n')\n"
            )
            driver.chmod(0o700)
            env = dict(os.environ)
            env["PATH"] = os.fspath(fake_bin) + os.pathsep + env.get("PATH", "")
            env["SLURM_JOB_ID"] = "4001180"
            env["SLURM_CLUSTER_NAME"] = "lunarc"
            env.pop("SLURM_ARRAY_JOB_ID", None)
            env.pop("SLURM_ARRAY_TASK_ID", None)
            completed = subprocess.run(
                [
                    "bash",
                    os.fspath(wrapper),
                    "--run-plan",
                    os.fspath(plan),
                    "--task-id",
                    "1",
                    "--arm",
                    "OS",
                    "--attempt",
                    "1",
                    "--driver",
                    os.fspath(driver),
                    "--adapter-module",
                    os.fspath(adapter),
                    "--output-dir",
                    os.fspath(output),
                ],
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(displaced.is_dir())
            self.assertEqual(list(displaced.iterdir()), [])
            self.assertTrue((output / "SCONTROL_IN_JOB_V1.txt").is_file())
            self.assertTrue((output / "SLURM_IDENTITY_AND_SNAPSHOT_V1.json").is_file())
            self.assertTrue((output / "ATTEMPT_CAPTURE_V1.json").is_file())

            direct_output = base / "direct-attempt"
            direct_output.mkdir()
            direct_output_fd = os.open(direct_output, os.O_RDONLY)
            try:
                direct_identity = self.bridge.capture_slurm_identity(
                    direct_output,
                    direct_output_fd,
                    environment=env,
                )
            finally:
                os.close(direct_output_fd)
            direct_snapshot = (direct_output / "SCONTROL_IN_JOB_V1.txt").read_bytes()
            self.assertEqual(
                direct_identity,
                {
                    "slurm_job_identity": {
                        "cluster": "lunarc",
                        "job_id": "4001180",
                        "array_job_id": None,
                        "array_task_id": None,
                    },
                    "slurm_in_job_snapshot_sha256": hashlib.sha256(direct_snapshot).hexdigest(),
                    "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
                    "environment_only_exclusivity_claimed": False,
                },
            )
            self.assertEqual(
                json.loads((direct_output / "SLURM_IDENTITY_AND_SNAPSHOT_V1.json").read_text()),
                direct_identity,
            )
            invalid_output_fd = os.open(direct_output, os.O_RDONLY)
            try:
                for invalid_updates in (
                    {"SLURM_JOB_ID": "0"},
                    {"SLURM_CLUSTER_NAME": "LUNARC"},
                    {"SLURM_ARRAY_JOB_ID": "9000", "SLURM_ARRAY_TASK_ID": ""},
                    {"SLURM_ARRAY_JOB_ID": "9000", "SLURM_ARRAY_TASK_ID": "-1"},
                ):
                    invalid_env = dict(env)
                    invalid_env.update(invalid_updates)
                    with self.assertRaises(self.bridge.PreflightError):
                        self.bridge.capture_slurm_identity(
                            direct_output,
                            invalid_output_fd,
                            environment=invalid_env,
                        )
            finally:
                os.close(invalid_output_fd)

            array_output = base / "direct-array-attempt"
            array_output.mkdir()
            array_output_fd = os.open(array_output, os.O_RDONLY)
            array_env = dict(env)
            array_env["SLURM_ARRAY_JOB_ID"] = "9000"
            array_env["SLURM_ARRAY_TASK_ID"] = "0"
            try:
                array_identity = self.bridge.capture_slurm_identity(
                    array_output,
                    array_output_fd,
                    environment=array_env,
                )
            finally:
                os.close(array_output_fd)
            self.assertEqual(
                array_identity["slurm_job_identity"],
                {
                    "cluster": "lunarc",
                    "job_id": "9000_0",
                    "array_job_id": "9000",
                    "array_task_id": "0",
                },
            )

        contract = json.loads(CONTRACT_PATH.read_text())
        self.assertFalse(contract["wrapper_execution_allowed"])
        self.assertEqual(
            contract["wrapper_binding_role"],
            "BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED",
        )
        supervisor_source = inspect.getsource(self.bridge.run_supervisor)
        self.assertNotIn("UPSTREAM_WRAPPER_PATH", supervisor_source)
        self.assertNotIn("run_wrapper_driver", supervisor_source)
        self.assertNotIn("run_wrapper_driver", inspect.getsource(self.bridge.main))

    def test_24_descendant_directory_capability_probe_is_portable_and_nonproduction(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory) / "capability-root"
            child = root / "child"
            child.mkdir(parents=True)
            marker = child / "marker.txt"
            marker.write_text("DESCENDANT_CAPABILITY_MARKER\n")
            root_fd = os.open(root, os.O_RDONLY)
            try:
                result = self.bridge.probe_descendant_directory_capability(root_fd, "child/marker.txt")
            finally:
                os.close(root_fd)

        self.assertIn(
            result["status"],
            {
                "PASS_PROC_SELF_FD_DESCENDANT_TRAVERSAL",
                "CANNOT_CHECK_PROC_SELF_FD_DESCENDANT_TRAVERSAL_UNSUPPORTED",
            },
        )
        self.assertFalse(result["production_dependency"])
        if result["status"].startswith("PASS_"):
            self.assertTrue(result["subprocess_traversal_proved"])
            self.assertEqual(result["observed_marker"], "DESCENDANT_CAPABILITY_MARKER")
        else:
            self.assertFalse(result["subprocess_traversal_proved"])
            self.assertNotIn("observed_marker", result)
        supervisor_source = inspect.getsource(self.bridge.run_supervisor)
        self.assertNotIn("/proc/self/fd", supervisor_source)
        self.assertNotIn("/dev/fd", supervisor_source)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DirectRouteSlurmPreflightTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_DIRECT_ROUTE_SLURM_PREFLIGHT_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} official_tasks=0 official_outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
