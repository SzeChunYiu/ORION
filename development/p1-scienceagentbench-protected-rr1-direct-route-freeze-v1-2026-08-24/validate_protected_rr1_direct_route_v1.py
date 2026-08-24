#!/usr/bin/env python3
"""Synthetic hostile validation for the protected RR1 direct-route freeze.

Only invented in-memory prompts and responses are used. The suite opens no
protected packet body, evaluator material, outcome, credential, external API,
model, scheduler allocation, or GPU job.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import inspect
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
MODULE_PATH = ROOT / "protected_rr1_direct_route_v1.py"
CONTRACT_PATH = ROOT / "PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V1.json"
TUPLE_PATH = ROOT / "TUPLE_FREEZE_V1.json"
PLAN_PATH = ROOT / "RUN_PLAN_V1.json"
OWNER_PATH = ROOT / "OWNER_SELECTION_V1.json"
RUNTIME_PATH = ROOT / "RUNTIME_BINDING_V1.json"
FINALIZATION_PATH = ROOT / "ONE_TUPLE_FINALIZATION_CONTRACT_V1.json"
LAUNCHER_PATH = ROOT / "run_protected_rr1_direct_route_v1.sh"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
MANIFEST_PATH = ROOT / "BODY_FREE_EXPORT_MANIFEST_V1.json"
SHA256SUMS_PATH = ROOT / "SHA256SUMS"
HANDOFF_PATH = ROOT / "HANDOFF_V1.md"
DIRECT_LANE = REPO_ROOT / "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24"
DIRECT_CONTRACT_PATH = DIRECT_LANE / "DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
DIRECT_PROMPT_PATH = DIRECT_LANE / "DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
DIRECT_VALIDATOR_PATH = DIRECT_LANE / "validate_direct_route_freeze_v1.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProtectedRR1DirectRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bridge = (
            load_module(MODULE_PATH, "protected_rr1_direct_route_v1")
            if MODULE_PATH.is_file()
            else None
        )
        cls.fixture = load_module(DIRECT_VALIDATOR_PATH, "direct_route_fixture_for_rr1")
        cls.direct = load_module(
            DIRECT_LANE / "direct_route_generation_driver_v1.py",
            "direct_route_driver_for_rr1",
        )

    def require_bridge(self):
        self.assertIsNotNone(self.bridge, "protected RR1 successor module is missing")
        return self.bridge

    def test_01_required_artifacts_exist(self) -> None:
        for path in (
            MODULE_PATH,
            CONTRACT_PATH,
            TUPLE_PATH,
            PLAN_PATH,
            OWNER_PATH,
            RUNTIME_PATH,
            FINALIZATION_PATH,
            LAUNCHER_PATH,
            RECEIPT_PATH,
            MANIFEST_PATH,
            SHA256SUMS_PATH,
            HANDOFF_PATH,
        ):
            self.assertTrue(path.is_file(), f"required artifact is missing: {path.name}")

    def test_02_exact_tuple_and_body_free_static_fit_binding(self) -> None:
        frozen = json.loads(TUPLE_PATH.read_text())
        self.assertEqual(
            frozen["tuple_identity"],
            {"task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101},
        )
        self.assertEqual(
            frozen["manifest_binding_sha256"],
            "22afbc171d3a132e627bbf2c00a12de0c55c013a38a15fea32e2ec12719577f0",
        )
        self.assertEqual(
            frozen["packet_bindings"],
            {
                "masked": {
                    "canonical_json_bytes": 622,
                    "canonical_json_sha256": "405f5836a21192d0a6d21e4b85143865fec8a2fb7cd9a4eb62100862b9d1a3df",
                },
                "recovered": {
                    "canonical_json_bytes": 1681,
                    "canonical_json_sha256": "3fce9e45e3012845d7dec2e343c224b43a4d79dea0c1192e5bf1972652733722",
                },
            },
        )
        self.assertEqual(frozen["rr_phase0_static_fit"]["prompt_tokens"], 235)
        self.assertEqual(frozen["rr_phase0_static_fit"]["phase_output_cap"], 1024)
        self.assertEqual(
            frozen["rr_phase1_dynamic_fit_status"],
            "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED",
        )
        self.assertFalse(frozen["protected_packet_bodies_in_git"])
        source = frozen["source_evidence"]
        self.assertEqual(
            source["pull_request_head_commit"],
            "9f8bc8294a480b6e8daeac1bde78770dc4e4a531",
        )
        self.assertEqual(
            source["squash_integration_commit"],
            "674152066986d5e2a480ed95ca65431ff0f25b6a",
        )
        expected_artifacts = {
            "protected_prompt_fit_receipt": (
                "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/PROTECTED_PROMPT_FIT_RECEIPT_V1.json",
                539479,
                "4ff1163b7e405b5881a7d2d4aea10bb634aaf49ada7bfc0c02159a1b5e18fa83",
            ),
            "successor_result_v2": (
                "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/SUCCESSOR_RESULT_V2.json",
                5728,
                "63f818cbf0558fb53201f7e7b4b2b97cfae03b0687fbaca91d3d64586df70ce9",
            ),
            "source_sha256sums": (
                "development/p1-scienceagentbench-protected-prompt-fit-successor-v2-2026-08-24/SHA256SUMS",
                1498,
                "bc894b82b7635db206f72ef1fb82a28132a272e36e25330c249b5d1c0695ea7f",
            ),
        }
        for label, (relative, byte_count, digest) in expected_artifacts.items():
            declared = source["artifacts"][label]
            self.assertEqual(
                declared, {"path": relative, "bytes": byte_count, "sha256": digest}
            )
            observed = REPO_ROOT / relative
            self.assertEqual(observed.stat().st_size, byte_count)
            self.assertEqual(sha256_file(observed), digest)

    def test_03_owner_runtime_and_full_runner_plan_are_exact(self) -> None:
        contract = json.loads(DIRECT_CONTRACT_PATH.read_text())
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        owner = json.loads(OWNER_PATH.read_text())
        runtime = json.loads(RUNTIME_PATH.read_text())
        plan = json.loads(PLAN_PATH.read_text())
        self.assertEqual(owner, contract["budget_owner_selection_interface"])
        self.assertEqual(runtime, contract["model_runtime_binding"])
        self.direct.validate_packet_contract(contract, prompts)
        self.direct.validate_runtime_binding(runtime, contract)
        self.direct.validate_owner_selection(owner)
        adapter = self.fixture.adapter
        self.direct.bind_runner_v2_plan(plan, contract, prompts, owner, adapter)
        self.assertEqual(len(plan["task_ids"]), 102)
        self.assertEqual(plan["arms"], ["RR", "OS", "NR"])
        self.assertEqual(plan["attempts_per_task_arm"], 3)

    def _make_client(
        self,
        *,
        tokens: list[int] | None = None,
        rr1_prompt_n: int = 200,
        tokenize_raws: list[bytes] | None = None,
        clock_values: list[int] | None = None,
        rr1_raw_override: bytes | None = None,
    ):
        bridge = self.require_bridge()
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        recovered = {"synthetic": "recovered"}
        masked = {"synthetic": "masked"}
        rr0_prompt = self.direct._render_phase0(prompts, "RR_PHASE0", 1, masked)
        stage = {
            "tuple_identity": {"task_id": "1", "arm_id": "RR", "attempt": 1},
            "prompt_commitments_by_phase": {
                "RR_PHASE0": {
                    "status": "PROSPECTIVE_EXACT",
                    "rendered_prompt_sha256": bridge.sha256_bytes(rr0_prompt.encode()),
                },
                "RR_PHASE1": {
                    "status": "DYNAMIC_SEALED_RR_STATE_RULE",
                },
            },
        }
        rr0_state = {
            "kind": "RR_TYPED_STATE",
            "assumptions": ["invented"],
            "unresolved_inputs": [],
            "intended_analysis": ["invented"],
            "invariants": ["synthetic only"],
            "output_contract": "FINAL_PROGRAM JSON",
        }
        rr0_raw = bridge.canonical_json_bytes(
            {
                "content": bridge.canonical_json_bytes(rr0_state).decode(),
                "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
                "tokens_predicted": 12,
                "truncated": False,
            }
        )
        rr1_raw = rr1_raw_override or bridge.canonical_json_bytes(
            {
                "content": '{"kind":"FINAL_PROGRAM","program":"print(1)"}',
                "timings": {
                    "cache_n": 0,
                    "prompt_n": rr1_prompt_n,
                    "predicted_n": 12,
                },
                "tokens_predicted": 12,
                "truncated": False,
            }
        )
        tokenize_raw = bridge.canonical_json_bytes(
            {"tokens": list(range(200)) if tokens is None else tokens}
        )
        tokenize_responses = tokenize_raws or [tokenize_raw] * 3
        if len(tokenize_responses) != 3:
            raise AssertionError("synthetic tokenize response count must equal three")
        transcript: list[dict[str, Any]] = []
        completion_count = 0
        tokenize_count = 0

        class FakeResponse:
            status = 200

            def __init__(self, raw: bytes) -> None:
                self.raw = raw

            def read(self) -> bytes:
                return self.raw

        class FakeConnection:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                self.path = ""
                self.body = b""

            def request(self, method: str, path: str, **kwargs: Any) -> None:
                self.path = path
                self.body = kwargs.get("body", b"")
                transcript.append({"method": method, "path": path, "body": self.body})

            def getresponse(self) -> FakeResponse:
                nonlocal completion_count, tokenize_count
                if self.path == "/tokenize":
                    raw = tokenize_responses[tokenize_count]
                    tokenize_count += 1
                    return FakeResponse(raw)
                if self.path == "/completion":
                    completion_count += 1
                    return FakeResponse(rr0_raw if completion_count == 1 else rr1_raw)
                raise AssertionError(f"unexpected path: {self.path}")

            def close(self) -> None:
                pass

        tick = 10_000_000_000
        supplied_ticks = iter(clock_values) if clock_values is not None else None

        def clock() -> int:
            nonlocal tick
            if supplied_ticks is not None:
                return next(supplied_ticks)
            tick += 1_000_000
            return tick

        deadline = bridge.RawDeadline(1_800_000_000_000, clock)
        deadline.capture_clock()
        client = bridge.DynamicRR1PretokenizeClient(
            self.direct,
            deadline,
            stage,
            prompts,
            recovered,
            connection_factory=FakeConnection,
        )
        return client, transcript, rr0_prompt, rr0_state, recovered

    def _run_rr_phases(self, client, rr0_prompt: str, rr0_state: dict, recovered: dict):
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        rr0_body = self.direct.build_completion_body(
            rr0_prompt, prompts["output_schemas"]["phase0_state"], 101, 1024
        )
        client.complete(rr0_body)
        state_bytes = self.direct.canonical_json_bytes(rr0_state)
        rr1_prompt = self.direct._render_rr_phase1(
            prompts,
            1,
            recovered,
            state_bytes.decode(),
            self.direct.sha256_bytes(state_bytes),
        )
        rr1_body = self.direct.build_completion_body(
            rr1_prompt, prompts["output_schemas"]["final_program"], 101, 7168
        )
        return client.complete(rr1_body)

    def test_04_dynamic_rr1_is_tokenized_three_times_before_completion(self) -> None:
        bridge = self.require_bridge()
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client()
        result = self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(result["timings"]["prompt_n"], 200)
        self.assertEqual(
            [row["path"] for row in transcript],
            ["/completion", "/tokenize", "/tokenize", "/tokenize", "/completion"],
        )
        for row in transcript[1:4]:
            request = json.loads(row["body"])
            self.assertEqual(set(request), {"content", "add_special", "parse_special"})
            self.assertTrue(request["add_special"])
            self.assertTrue(request["parse_special"])
        self.assertEqual(len(client.dynamic_tokenize_bindings), 1)
        binding = client.dynamic_tokenize_bindings[0]
        self.assertEqual(
            set(binding),
            {
                "phase_id",
                "rendered_prompt_sha256",
                "tokenize_request_sha256",
                "tokenize_repeat_count",
                "tokenize_raw_response_sha256",
                "token_array_sha256",
                "prompt_tokens",
                "phase_output_cap",
                "context_window_tokens",
                "remaining_context_margin_tokens",
                "completion_prompt_n_equal",
                "status",
            },
        )
        self.assertEqual(binding["status"], "PASS_DYNAMIC_RR1_PRETOKENIZE_FIT")
        self.assertEqual(binding["remaining_context_margin_tokens"], 25400)
        self.assertNotIn("content", binding)
        self.assertNotIn("tokens", binding)
        self.assertEqual(len(client.request_bindings), 2)
        for index, request_binding in enumerate(client.request_bindings):
            expected_raw = bridge.canonical_json_bytes(client.responses[index])
            self.assertEqual(
                request_binding["completion_raw_response_sha256"],
                bridge.sha256_bytes(expected_raw),
            )
            self.assertEqual(
                request_binding["transport_status"], "SENT_RESPONSE_ACCEPTED"
            )

    def test_05_dynamic_rr1_overflow_fails_before_rr1_completion(self) -> None:
        overflow = list(range(32768 - 7168 + 1))
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(tokens=overflow)
        with self.assertRaises(self.require_bridge().PreflightError):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(
            [row["path"] for row in transcript],
            ["/completion", "/tokenize", "/tokenize", "/tokenize"],
        )
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_06_completion_prompt_count_must_equal_pretokenize_count(self) -> None:
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            rr1_prompt_n=201
        )
        with self.assertRaises(self.require_bridge().PreflightError):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(transcript[-1]["path"], "/completion")
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_07_malformed_token_response_fails_before_rr1_completion(self) -> None:
        malformed = self.require_bridge().canonical_json_bytes({"tokens": [1, "bad"]})
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            tokenize_raws=[malformed, malformed, malformed]
        )
        with self.assertRaises(self.require_bridge().PreflightError):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(
            [row["path"] for row in transcript], ["/completion", "/tokenize"]
        )
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_08_token_array_disagreement_fails_before_rr1_completion(self) -> None:
        bridge = self.require_bridge()
        raws = [
            bridge.canonical_json_bytes({"tokens": list(range(200))}),
            bridge.canonical_json_bytes({"tokens": list(range(199)) + [999]}),
            bridge.canonical_json_bytes({"tokens": list(range(200))}),
        ]
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            tokenize_raws=raws
        )
        with self.assertRaises(bridge.PreflightError):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(
            [row["path"] for row in transcript],
            ["/completion", "/tokenize", "/tokenize", "/tokenize"],
        )
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_09_raw_tokenize_byte_disagreement_fails_even_when_tokens_match(self) -> None:
        bridge = self.require_bridge()
        tokens = list(range(200))
        canonical = bridge.canonical_json_bytes({"tokens": tokens})
        alternate = json.dumps({"tokens": tokens}, separators=(", ", ": ")).encode()
        self.assertNotEqual(canonical, alternate)
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            tokenize_raws=[canonical, alternate, canonical]
        )
        with self.assertRaises(bridge.PreflightError):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(transcript[-1]["path"], "/tokenize")
        self.assertEqual(
            [row["path"] for row in transcript].count("/completion"), 1
        )
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_10_deadline_expiry_during_tokenize_fails_before_rr1_completion(self) -> None:
        # capture, RR0 pre-request, RR0 post-request, RR1 tokenize pre-request,
        # then the post-request check crosses the 1800-second raw deadline.
        ticks = [
            10_000_000_000,
            10_100_000_000,
            10_200_000_000,
            10_300_000_000,
            1_810_000_000_001,
        ]
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            clock_values=ticks
        )
        with self.assertRaises(self.require_bridge().AttemptDeadlineExceeded):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(
            [row["path"] for row in transcript], ["/completion", "/tokenize"]
        )
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_11_malformed_completion_retains_only_raw_hash_and_fails_closed(self) -> None:
        malformed = b'{"content":'
        client, transcript, rr0_prompt, rr0_state, recovered = self._make_client(
            rr1_raw_override=malformed
        )
        with self.assertRaises(Exception):
            self._run_rr_phases(client, rr0_prompt, rr0_state, recovered)
        self.assertEqual(transcript[-1]["path"], "/completion")
        rejected = client.request_bindings[-1]
        self.assertEqual(
            rejected["completion_raw_response_sha256"],
            self.require_bridge().sha256_bytes(malformed),
        )
        self.assertEqual(rejected["transport_status"], "SENT_RESPONSE_REJECTED")
        self.assertNotIn("completion_raw_response", rejected)
        self.assertEqual(client.dynamic_tokenize_bindings, [])

    def test_12_contract_and_launcher_freeze_one_a40_without_submission(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text())
        self.assertEqual(contract["status"], "FROZEN_PREPARED_NOT_SUBMITTED")
        self.assertFalse(contract["submission_authority"])
        self.assertFalse(contract["merge_authority"])
        self.assertEqual(contract["dynamic_rr1_pretokenize"]["repeat_count"], 3)
        self.assertEqual(contract["dynamic_rr1_pretokenize"]["phase_output_cap"], 7168)
        launcher = LAUNCHER_PATH.read_text()
        for token in (
            "#SBATCH --partition=gpua40i",
            "#SBATCH --gres=gpu:a40:1",
            "#SBATCH --nodes=1",
            "#SBATCH --ntasks=1",
            "#SBATCH --cpus-per-task=8",
            "#SBATCH --mem=64G",
            "#SBATCH --signal=B:TERM@120",
        ):
            self.assertIn(token, launcher)
        self.assertNotIn("sbatch", launcher)
        self.assertIn("supervise", launcher)
        self.assertIn(
            "P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING",
            inspect.getsource(self.require_bridge().main),
        )

    def test_13_executed_successor_bytes_are_self_bound(self) -> None:
        bridge = self.require_bridge()
        contract = json.loads(CONTRACT_PATH.read_text())
        bridge.validate_frozen_upstream(contract)
        self.assertEqual(
            contract["lane_artifact_bindings"]["bridge_sha256"], sha256_file(MODULE_PATH)
        )
        self.assertEqual(
            contract["lane_artifact_bindings"]["launcher_sha256"], sha256_file(LAUNCHER_PATH)
        )
        source = inspect.getsource(bridge.run_supervisor)
        self.assertIn("DynamicRR1PretokenizeClient", inspect.getsource(bridge.execute_bridge_attempt))
        self.assertNotIn("monkeypatch", source.lower())
        self.assertNotIn("UPSTREAM.__file__ =", MODULE_PATH.read_text())

    def test_14_exact_loader_hashes_held_bytes_before_any_execution(self) -> None:
        bridge = self.require_bridge()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            marker = base / "executed.txt"
            donor = base / "donor.py"
            donor.write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('verified bytes executed')\n"
            )
            good = sha256_file(donor)
            with self.assertRaises(RuntimeError):
                bridge._load_exact_module(donor, "rejected_donor", "0" * 64)
            self.assertFalse(marker.exists())
            bridge._load_exact_module(donor, "accepted_donor", good)
            self.assertEqual(marker.read_text(), "verified bytes executed")
        source = MODULE_PATH.read_text()
        self.assertIn("UPSTREAM = _load_exact_module(", source)
        self.assertNotIn("spec_from_file_location", source)

    def test_15_one_tuple_finalization_never_claims_runner_population_finalized(self) -> None:
        finalization = json.loads(FINALIZATION_PATH.read_text())
        self.assertEqual(
            finalization["tuple_identity"],
            {"task_id": "1", "arm_id": "RR", "attempt": 1, "seed": 101},
        )
        self.assertEqual(finalization["expected_tuple_count"], 1)
        self.assertEqual(
            finalization["runner_v2_population_ledger_status"],
            "NOT_FINALIZED_918_TUPLES",
        )
        self.assertEqual(finalization["production_admissibility"], "CANNOT_CHECK")
        self.assertEqual(finalization["scientific_authority_delta"], "NONE")
        required = set(finalization["required_evidence"])
        self.assertTrue(
            {
                "SCONTROL_IN_JOB_V1.txt",
                "SLURM_IDENTITY_AND_SNAPSHOT_V1.json",
                "POST_JOB_SACCT_V1.txt",
                "POST_JOB_SCONTROL_V1.txt",
                "SCHEDULER_CONFIG_V1.txt",
                "SCHEDULER_EXPORT_V1.jsonl",
                "GPU_ALLOCATION_IDENTITY_V1.json",
                "SERVER_CLEANUP_V1.json",
                "DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json",
            }.issubset(required)
        )

    def test_16_execute_failure_emits_typed_sidecar_and_never_calls_rr1_completion(self) -> None:
        bridge = self.require_bridge()
        direct_contract = json.loads(DIRECT_CONTRACT_PATH.read_text())
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        plan = self.fixture.synthetic_plan(direct_contract, prompts)
        values = {
            "plan": plan,
            "owner": direct_contract["budget_owner_selection_interface"],
            "runtime": direct_contract["model_runtime_binding"],
            "masked": {"synthetic": "masked"},
            "recovered": {"synthetic": "recovered"},
        }
        rr0_state = {
            "kind": "RR_TYPED_STATE",
            "assumptions": ["invented"],
            "unresolved_inputs": [],
            "intended_analysis": ["invented"],
            "invariants": ["synthetic only"],
            "output_contract": "FINAL_PROGRAM JSON",
        }
        rr0_raw = bridge.canonical_json_bytes(
            {
                "content": bridge.canonical_json_bytes(rr0_state).decode(),
                "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
                "tokens_predicted": 12,
                "truncated": False,
            }
        )
        malformed = bridge.canonical_json_bytes({"tokens": [1, "bad"]})
        transcript: list[str] = []

        class FakeResponse:
            status = 200

            def __init__(self, raw: bytes) -> None:
                self.raw = raw

            def read(self) -> bytes:
                return self.raw

        class FakeConnection:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                self.path = ""

            def request(self, method: str, path: str, **kwargs: Any) -> None:
                self.path = path
                transcript.append(path)

            def getresponse(self) -> FakeResponse:
                return FakeResponse(rr0_raw if self.path == "/completion" else malformed)

            def close(self) -> None:
                pass

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            paths: dict[str, Path] = {}
            for name, value in values.items():
                path = base / bridge.RUNTIME_INPUT_NAMES[name]
                path.write_bytes(bridge.canonical_json_bytes(value) + b"\n")
                paths[name] = path
            for name in ("model", "server", "backend", "launcher"):
                path = base / name
                path.write_bytes((name + "\n").encode())
                paths[name] = path
            expected = {name: sha256_file(path) for name, path in paths.items()}
            stage = bridge.build_runtime_stage(
                json.loads(CONTRACT_PATH.read_text()), paths, expected
            )
            rr0_prompt = self.direct._render_phase0(
                prompts, "RR_PHASE0", 1, values["masked"]
            )
            stage["prompt_commitments_by_phase"] = {
                "RR_PHASE0": {
                    "status": "PROSPECTIVE_EXACT",
                    "rendered_prompt_sha256": bridge.sha256_bytes(rr0_prompt.encode()),
                },
                "RR_PHASE1": {"status": "DYNAMIC_SEALED_RR_STATE_RULE"},
            }
            output_fd = os.open(base, os.O_RDONLY)
            tick = 10_000_000_000

            def clock() -> int:
                nonlocal tick
                tick += 1_000_000
                return tick

            try:
                with self.assertRaises(bridge.PreflightError):
                    bridge.execute_bridge_attempt(
                        stage=stage,
                        stage_sha256=bridge.canonical_hash(stage),
                        attestation_sha256="a" * 64,
                        slurm_identity={
                            "slurm_job_identity": {
                                "cluster": "lunarc",
                                "job_id": "4000001",
                                "array_job_id": None,
                                "array_task_id": None,
                            },
                            "slurm_in_job_snapshot_sha256": "b" * 64,
                        },
                        output_dir=base,
                        output_dir_fd=output_fd,
                        raw_clock=clock,
                        connection_factory=FakeConnection,
                    )
            finally:
                os.close(output_fd)
            sidecar = json.loads((base / "ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json").read_text())
            binding = json.loads(
                (base / "DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json").read_text()
            )
            self.assertEqual(sidecar["status"], "CANNOT_CHECK")
            self.assertEqual(binding["status"], "CANNOT_CHECK")
            self.assertEqual(transcript, ["/completion", "/tokenize"])
            self.assertFalse((base / "ATTEMPT_CAPTURE_V1.json").exists())

    def test_17_preopen_staged_input_swap_fails_hash_check(self) -> None:
        bridge = self.require_bridge()
        direct_contract = json.loads(DIRECT_CONTRACT_PATH.read_text())
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        values = {
            "plan": self.fixture.synthetic_plan(direct_contract, prompts),
            "owner": direct_contract["budget_owner_selection_interface"],
            "runtime": direct_contract["model_runtime_binding"],
            "masked": {"synthetic": "masked"},
            "recovered": {"synthetic": "recovered"},
        }
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            paths = {}
            for name, value in values.items():
                path = base / bridge.RUNTIME_INPUT_NAMES[name]
                path.write_bytes(bridge.canonical_json_bytes(value) + b"\n")
                paths[name] = path
            for name in ("model", "server", "backend", "launcher"):
                path = base / name
                path.write_bytes((name + "\n").encode())
                paths[name] = path
            expected = {name: sha256_file(path) for name, path in paths.items()}
            stage = bridge.build_runtime_stage(
                json.loads(CONTRACT_PATH.read_text()), paths, expected
            )
            plan = paths["plan"]
            held = base / "held-plan.json"
            plan.rename(held)
            plan.write_text('{"malicious":"swap"}\n')
            with self.assertRaises(bridge.PreflightError):
                bridge.read_staged_inputs(stage)
            plan.unlink()
            held.rename(plan)
            bound = bridge.read_staged_inputs(stage)
            self.assertEqual(bound["plan"], values["plan"])

    def test_18_held_fd_uses_original_bytes_across_path_swap_and_restore(self) -> None:
        bridge = self.require_bridge()
        direct_contract = json.loads(DIRECT_CONTRACT_PATH.read_text())
        prompts = json.loads(DIRECT_PROMPT_PATH.read_text())
        values = {
            "plan": self.fixture.synthetic_plan(direct_contract, prompts),
            "owner": direct_contract["budget_owner_selection_interface"],
            "runtime": direct_contract["model_runtime_binding"],
            "masked": {"synthetic": "masked"},
            "recovered": {"synthetic": "recovered"},
        }
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            paths = {}
            for name, value in values.items():
                path = base / bridge.RUNTIME_INPUT_NAMES[name]
                path.write_bytes(bridge.canonical_json_bytes(value) + b"\n")
                paths[name] = path
            for name in ("model", "server", "backend", "launcher"):
                path = base / name
                path.write_bytes((name + "\n").encode())
                paths[name] = path
            expected = {name: sha256_file(path) for name, path in paths.items()}
            stage = bridge.build_runtime_stage(
                json.loads(CONTRACT_PATH.read_text()), paths, expected
            )
            plan = paths["plan"]
            plan_inode = plan.stat().st_ino
            malicious = base / "malicious-plan.json"
            malicious.write_text('{"malicious":"same-uid-path-swap"}\n')
            displaced = base / "displaced-plan.json"
            original_read = bridge.os.read
            swap_count = 0

            def swap_restore_read(fd: int, count: int) -> bytes:
                nonlocal swap_count
                if swap_count == 0 and os.fstat(fd).st_ino == plan_inode:
                    plan.rename(displaced)
                    malicious.rename(plan)
                    payload = original_read(fd, count)
                    plan.rename(malicious)
                    displaced.rename(plan)
                    swap_count += 1
                    return payload
                return original_read(fd, count)

            with mock.patch.object(bridge.os, "read", swap_restore_read):
                bound = bridge.read_staged_inputs(stage)
            self.assertEqual(swap_count, 1)
            self.assertEqual(bound["plan"], values["plan"])
            self.assertEqual(sha256_file(plan), expected["plan"])
            self.assertTrue(malicious.is_file())

    def test_19_gpu_capture_requires_one_slurm_visible_nvidia_a40(self) -> None:
        bridge = self.require_bridge()

        def completed(stdout: bytes, returncode: int = 0):
            def runner(*args: Any, **kwargs: Any):
                return types.SimpleNamespace(
                    returncode=returncode, stdout=stdout, stderr=b"synthetic stderr"
                )

            return runner

        valid_env = {
            "SLURM_JOB_ID": "4000001",
            "CUDA_VISIBLE_DEVICES": "0",
            "SLURM_JOB_GPUS": "0",
            "SLURM_STEP_GPUS": "0",
        }
        valid_stdout = (
            b"0, GPU-12345678-1234-1234-1234-123456789abc, NVIDIA A40\n"
        )
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            good = base / "good"
            good.mkdir()
            good_fd = os.open(good, os.O_RDONLY)
            try:
                record = bridge.capture_gpu_identity(
                    good,
                    good_fd,
                    environment=valid_env,
                    runner=completed(valid_stdout),
                )
            finally:
                os.close(good_fd)
            self.assertEqual(record["status"], "PASS_EXACTLY_ONE_VISIBLE_NVIDIA_A40")
            self.assertEqual(record["slurm_job_id"], "4000001")
            self.assertEqual(record["gpu"]["name"], "NVIDIA A40")

            for index, (environment, stdout) in enumerate(
                (
                    ({key: value for key, value in valid_env.items() if key != "SLURM_JOB_ID"}, valid_stdout),
                    ({**valid_env, "CUDA_VISIBLE_DEVICES": ""}, valid_stdout),
                    (valid_env, valid_stdout + valid_stdout),
                    (
                        valid_env,
                        b"0, GPU-12345678-1234-1234-1234-123456789abc, NVIDIA H100\n",
                    ),
                )
            ):
                target = base / f"bad-{index}"
                target.mkdir()
                target_fd = os.open(target, os.O_RDONLY)
                try:
                    with self.assertRaises(bridge.PreflightError):
                        bridge.capture_gpu_identity(
                            target,
                            target_fd,
                            environment=environment,
                            runner=completed(stdout),
                        )
                finally:
                    os.close(target_fd)

    def test_20_server_environment_drops_credentials_and_keeps_exact_runtime(self) -> None:
        bridge = self.require_bridge()
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            backend_dir = base / "cuda"
            backend_dir.mkdir()
            backend = backend_dir / "libggml-cuda.so"
            backend.write_bytes(b"synthetic backend")
            source = {
                "HOME": "/synthetic/home",
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "CUDA_VISIBLE_DEVICES": "0",
                "OPENAI_API_KEY": "must-not-cross",
                "HF_TOKEN": "must-not-cross",
                "AWS_SECRET_ACCESS_KEY": "must-not-cross",
                "SSH_AUTH_SOCK": "/must/not/cross",
                "HTTP_PROXY": "http://must-not-cross",
            }
            env = bridge.build_credential_free_server_environment(backend, source)
        self.assertEqual(env["GGML_BACKEND_PATH"], str(backend))
        self.assertEqual(env["CUDA_VISIBLE_DEVICES"], "0")
        self.assertEqual(env["HTTP_PROXY"], "")
        self.assertEqual(env["NO_PROXY"], "127.0.0.1,localhost")
        for forbidden in (
            "OPENAI_API_KEY",
            "HF_TOKEN",
            "AWS_SECRET_ACCESS_KEY",
            "SSH_AUTH_SOCK",
        ):
            self.assertNotIn(forbidden, env)

    def test_21_repository_lane_contains_no_protected_body_or_live_output(self) -> None:
        forbidden_names = {
            "MASKED_PACKET.json",
            "RECOVERED_PACKET.json",
            "ATTEMPT_CAPTURE_V1.json",
            "SCONTROL_IN_JOB_V1.txt",
            "POST_JOB_SACCT_V1.txt",
            "llama-server.log",
        }
        observed = {path.name for path in ROOT.iterdir() if path.is_file()}
        self.assertTrue(forbidden_names.isdisjoint(observed))
        for path in ROOT.iterdir():
            if path.is_file() and path.suffix == ".json":
                value = json.loads(path.read_text())
                self.assertNotIn("masked_packet", value)
                self.assertNotIn("recovered_packet", value)
                self.assertNotIn("prompt_body", value)
                self.assertNotIn("completion_body", value)
                self.assertNotIn("token_ids", value)

    def test_22_body_free_manifest_binds_every_exported_file(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        self.assertEqual(manifest["status"], "PASS_BODY_FREE_EXPORT_SET")
        self.assertFalse(manifest["protected_packet_bodies_in_export_set"])
        self.assertFalse(manifest["live_outputs_in_export_set"])
        self.assertFalse(manifest["token_ids_in_export_set"])
        self.assertEqual(manifest["official_outcomes_opened"], 0)
        for name, binding in manifest["exported_files"].items():
            path = ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(path.stat().st_size, binding["bytes"])
            self.assertEqual(sha256_file(path), binding["sha256"])
        listed = {
            line.split(maxsplit=1)[1]
            for line in SHA256SUMS_PATH.read_text().splitlines()
            if line.strip()
        }
        self.assertEqual(listed, set(manifest["exported_files"]) | {MANIFEST_PATH.name})

    def test_23_synthetic_receipt_binds_final_core_artifacts(self) -> None:
        receipt = json.loads(RECEIPT_PATH.read_text())
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["test_count"], 23)
        self.assertEqual(receipt["official_outcomes_opened"], 0)
        self.assertFalse(receipt["generation_invoked"])
        self.assertFalse(receipt["job_submitted"])
        expected = {
            path.name: sha256_file(path)
            for path in (
                MODULE_PATH,
                CONTRACT_PATH,
                TUPLE_PATH,
                PLAN_PATH,
                OWNER_PATH,
                RUNTIME_PATH,
                FINALIZATION_PATH,
                LAUNCHER_PATH,
            )
        }
        self.assertEqual(receipt["artifact_sha256"], expected)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProtectedRR1DirectRouteTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_PROTECTED_RR1_DIRECT_ROUTE_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} protected_bodies=0 generation=0 jobs=0 outcomes=0 "
        "production_admissibility=CANNOT_CHECK scientific_authority=NONE"
    )
