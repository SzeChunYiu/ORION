#!/usr/bin/env python3
"""Synthetic hostile verification for the LUNARC generation adapter.

The suite constructs only deterministic nonbenchmark metadata. It opens no
archive, task, candidate body, credential, evaluator, outcome, manuscript or
PDF and invokes no provider, model, SLURM command, CI or pytest path.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "sab_lunarc_generation_adapter_v1.py"
WRAPPER_PATH = ROOT / "run_lunarc_attempt_v1.sh"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
SYNTHETIC_CONFIG_SNAPSHOT = b"synthetic scheduler config snapshot\n"
SYNTHETIC_GPU_UUID_1 = "GPU-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"
SYNTHETIC_GPU_UUID_2 = "GPU-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2"


def load_module():
    spec = importlib.util.spec_from_file_location("sab_lunarc_generation_adapter_v1", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load adapter module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load_module()
v2 = adapter.load_v2_module()


def synthetic_hash(label: str) -> str:
    return hashlib.sha256(f"synthetic-nonbenchmark:{label}".encode()).hexdigest()


def canonical_hash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def synthetic_plan() -> dict:
    budget = {
        "total_input_token_cap": 4096,
        "total_output_token_cap": 2048,
        "tool_call_cap": 8,
        "wall_time_seconds_cap": 10.0,
        "local_execution_seconds_cap": 5.0,
        "final_candidates_per_attempt": 1,
    }
    metric = v2._metric_object()
    measurement = {
        **v2.TIMING_CONSTANTS,
        "exclusive_gpu_count_by_arm": {arm: "1" for arm in v2.ARMS},
    }
    route = dict(v2.ROUTE_PROFILE)
    return {
        "schema_version": v2.RUN_PLAN_SCHEMA,
        "split": v2.PRODUCTION_SPLIT,
        "task_ids": list(v2.TASK_IDS),
        "arms": list(v2.ARMS),
        "attempts_per_task_arm": len(v2.ATTEMPTS),
        "bindings": {
            "model_id": "synthetic-open-weight-model",
            "provider": "synthetic-local-llama-server",
            "tokenizer_revision": "synthetic-tokenizer-revision",
            "prompt_bundle_sha256_by_arm": {
                arm: synthetic_hash(f"prompt:{arm}") for arm in v2.ARMS
            },
            "seed_schedule": {"1": 101, "2": 202, "3": 303},
            "provider_seed_capability": "CONFIRMED",
            "model_parameters_sha256": synthetic_hash("model-parameters"),
            "tool_policy_sha256": synthetic_hash("tool-policy"),
            "generation_runtime_manifest_sha256": synthetic_hash("runtime"),
            "credential_route_sha256": synthetic_hash("owner-route-without-secret"),
            "credential_route_status": "BOUND_OWNER_CONTROLLED",
        },
        "budget_by_arm": {arm: copy.deepcopy(budget) for arm in v2.ARMS},
        "cost_accounting": v2.COST_ACCOUNTING,
        "amendment_scope": (
            "ALLOCATED_ACCELERATOR_SECONDS_ONLY__BILLED_USD_REMAINS_UNCHANGED_RUNNER_V1"
        ),
        "base_runner_contract_sha256": v2.V1_CONTRACT_SHA256,
        "base_runner_module_sha256": v2.V1_MODULE_SHA256,
        "analysis_contract_sha256": v2.ANALYSIS_CONTRACT_SHA256,
        "route_profile": route,
        "route_profile_binding_sha256": canonical_hash(route),
        "cost_gate_metric": metric,
        "cost_gate_metric_binding_sha256": canonical_hash(metric),
        "cost_measurement_binding": measurement,
        "cost_measurement_binding_sha256": canonical_hash(measurement),
    }


def base_record(plan: dict, task_id: str, arm: str, attempt: int) -> dict:
    return {
        "task_id": task_id,
        "arm_id": arm,
        "attempt": attempt,
        "seed": plan["bindings"]["seed_schedule"][str(attempt)],
        "input_tokens": 100,
        "output_tokens": 50,
        "tool_calls": 0,
        "wall_time_seconds": 2.0,
        "local_execution_wall_time_seconds": 0.0,
        "billed_cost_usd": None,
        "failure": None,
        "raw_output_sha256": synthetic_hash(f"raw:{task_id}:{arm}:{attempt}"),
        "candidate_program_sha256": synthetic_hash(f"candidate:{task_id}:{arm}:{attempt}"),
    }


def job_identity(index: int) -> dict:
    return {
        "cluster": "lunarc",
        "job_id": str(4_000_000 + index),
        "array_job_id": None,
        "array_task_id": None,
    }


def make_capture(
    plan: dict,
    run_plan_sha256: str,
    task_id: str,
    arm: str,
    attempt: int,
    index: int,
    *,
    start_ns: int | None = None,
    elapsed_ns: int = 2_000_000_001,
) -> dict:
    start = start_ns if start_ns is not None else 10_000_000_000 + index * 3_000_000_000
    readings = iter((start, start + elapsed_ns))
    capture = adapter.GenerationAttemptCapture(
        plan=plan,
        run_plan_sha256=run_plan_sha256,
        task_id=task_id,
        arm_id=arm,
        attempt=attempt,
        slurm_job_identity=job_identity(index),
        slurm_in_job_snapshot_sha256=synthetic_hash(f"scontrol:{index}"),
        raw_clock=lambda: next(readings),
    )
    for phase in adapter.PHASE_SEQUENCE_BY_ARM[arm]:
        capture.call_model(phase, lambda phase=phase: {"synthetic_phase": phase})
    return capture.finish(base_record(plan, task_id, arm, attempt))


def all_captures(plan: dict, run_plan_sha256: str) -> list[dict]:
    captures = []
    index = 0
    for task_id in v2.TASK_IDS:
        for arm in v2.ARMS:
            for attempt in v2.ATTEMPTS:
                captures.append(make_capture(plan, run_plan_sha256, task_id, arm, attempt, index))
                index += 1
    return captures


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scheduler_evidence(captures: list[dict]) -> tuple[dict, bytes]:
    base = datetime(2026, 8, 24, 0, 0, 0, tzinfo=timezone.utc)
    records = []
    raw_lines = []
    for index, capture in enumerate(captures):
        started = base + timedelta(seconds=2 * index)
        raw_record = {
            "task_id": capture["task_id"],
            "arm_id": capture["arm_id"],
            "attempt": capture["attempt"],
            "slurm_job_identity": copy.deepcopy(capture["slurm_job_identity"]),
            "in_job_snapshot_sha256": capture["slurm_in_job_snapshot_sha256"],
            "scheduler_record_source": "SCONTROL_AND_SACCT",
            "scheduler_job_state": "COMPLETED",
            "allocation_started_at_utc": iso_z(started),
            "allocation_ended_at_utc": iso_z(started + timedelta(seconds=1)),
            "node_name": "synthetic-cn001",
            "allocated_gpu_count": capture["exclusive_gpu_count"],
            "gpu_allocations": [
                {
                    "node_name": "synthetic-cn001",
                    "gres_name": "gpu",
                    "gres_type": "a40",
                    "gres_index": "0",
                    "gpu_uuid": SYNTHETIC_GPU_UUID_1,
                }
            ],
            "exclusive_gres_status": "SCHEDULER_CONFIRMED_CONSUMABLE_EXCLUSIVE_GRES",
            "attempt_scope_status": "ONE_TASK_ARM_ATTEMPT_ONLY_CONFIRMED",
        }
        raw_line = adapter.canonical_json_bytes(raw_record) + b"\n"
        raw_lines.append(raw_line)
        records.append(
            {
                **raw_record,
                "scheduler_record_sha256": hashlib.sha256(raw_line).hexdigest(),
            }
        )
    export_snapshot = b"".join(raw_lines)
    evidence = {
        "schema_version": adapter.SCHEDULER_EVIDENCE_SCHEMA,
        "site": "LUNARC",
        "scheduler": "SLURM",
        "scheduler_config_snapshot_sha256": hashlib.sha256(
            SYNTHETIC_CONFIG_SNAPSHOT
        ).hexdigest(),
        "scheduler_export_sha256": hashlib.sha256(export_snapshot).hexdigest(),
        "records": records,
    }
    return evidence, export_snapshot


def rebind_scheduler_export(evidence: dict) -> bytes:
    """Regenerate exact synthetic raw records after an intentional mutation."""

    raw_lines = []
    for record in evidence["records"]:
        raw_record = {
            field: copy.deepcopy(record[field])
            for field in adapter.SCHEDULER_RAW_RECORD_FIELDS
        }
        raw_line = adapter.canonical_json_bytes(raw_record) + b"\n"
        record["scheduler_record_sha256"] = hashlib.sha256(raw_line).hexdigest()
        raw_lines.append(raw_line)
    snapshot = b"".join(raw_lines)
    evidence["scheduler_export_sha256"] = hashlib.sha256(snapshot).hexdigest()
    return snapshot


class AdapterSyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = synthetic_plan()
        cls.run_plan_sha256 = synthetic_hash("run-plan-exact-bytes")
        cls.captures = all_captures(cls.plan, cls.run_plan_sha256)
        cls.evidence, cls.scheduler_export_snapshot = scheduler_evidence(cls.captures)
        cls.scheduler_config_snapshot = SYNTHETIC_CONFIG_SNAPSHOT

    def assert_reject(self, callable_, fragment: str) -> None:
        with self.assertRaises(adapter.ContractError) as caught:
            callable_()
        self.assertIn(fragment.lower(), str(caught.exception).lower())

    def validate_scheduler(self, captures: list[dict], evidence: dict) -> dict:
        scheduler_export_snapshot = rebind_scheduler_export(evidence)
        return adapter.validate_scheduler_allocation_evidence(
            captures,
            evidence,
            self.plan,
            self.run_plan_sha256,
            scheduler_export_snapshot,
        )

    def test_01_upstream_and_contract_hashes_are_frozen(self) -> None:
        adapter.verify_frozen_dependencies()
        contract = json.loads(adapter.CONTRACT_PATH.read_text())
        self.assertEqual(
            hashlib.sha256(adapter.CONTRACT_PATH.read_bytes()).hexdigest(),
            adapter.CONTRACT_SHA256,
        )
        self.assertEqual(
            contract["upstream"]["runner_v1_module_sha256"],
            adapter.RUNNER_V1_MODULE_SHA256,
        )
        self.assertEqual(
            contract["upstream"]["runner_v2_module_sha256"],
            adapter.RUNNER_V2_MODULE_SHA256,
        )
        self.assertEqual(
            contract["upstream"]["runner_v2_contract_sha256"],
            adapter.RUNNER_V2_CONTRACT_SHA256,
        )
        self.assertEqual(
            adapter.RUNNER_V2_MODULE_SHA256,
            "14c7d42b0b5add7c9bc4ae8608f74b422c638d0e795ef26996dcef4a87afe8ae",
        )

    def test_02_raw_clock_uses_exact_clock_gettime_ns_api(self) -> None:
        with (
            mock.patch.object(adapter.time, "CLOCK_MONOTONIC_RAW", 123, create=True),
            mock.patch.object(adapter.time, "clock_gettime_ns", return_value=456) as reader,
        ):
            self.assertEqual(adapter.raw_monotonic_ns(), 456)
        reader.assert_called_once_with(123)

    def test_03_raw_clock_has_no_fallback(self) -> None:
        with mock.patch.object(adapter.time, "CLOCK_MONOTONIC_RAW", None, create=True):
            self.assert_reject(adapter.raw_monotonic_ns, "unavailable")

    def test_04_each_arm_places_two_clock_reads_at_exact_boundaries(self) -> None:
        for arm in v2.ARMS:
            events = []
            values = iter((101, 207))

            def clock():
                events.append("clock")
                return next(values)

            capture = adapter.GenerationAttemptCapture(
                plan=self.plan,
                run_plan_sha256=self.run_plan_sha256,
                task_id="1",
                arm_id=arm,
                attempt=1,
                slurm_job_identity=job_identity(1),
                slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
                raw_clock=clock,
            )
            for phase in adapter.PHASE_SEQUENCE_BY_ARM[arm]:
                capture.call_model(
                    phase,
                    lambda phase=phase: events.extend((f"{phase}:begin", f"{phase}:end")),
                )
            receipt = capture.finish(base_record(self.plan, "1", arm, 1))
            expected = ["clock"]
            for phase in adapter.PHASE_SEQUENCE_BY_ARM[arm]:
                expected.extend((f"{phase}:begin", f"{phase}:end"))
            expected.append("clock")
            self.assertEqual(events, expected)
            self.assertEqual(receipt["monotonic_elapsed_ns"], "106")

    def test_05_wrong_phase_rejects_before_clock_or_operation(self) -> None:
        events = []
        capture = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="RR",
            attempt=1,
            slurm_job_identity=job_identity(1),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
            raw_clock=lambda: events.append("clock") or 1,
        )
        self.assert_reject(
            lambda: capture.call_model("RR_PHASE1", lambda: events.append("operation")),
            "phase",
        )
        self.assertEqual(events, [])
        self.assert_reject(
            lambda: capture.call_model("RR_PHASE0", lambda: events.append("operation")),
            "failed",
        )

    def test_06_incomplete_and_extra_phase_sequences_fail_closed(self) -> None:
        values = iter((1, 2))
        capture = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="RR",
            attempt=1,
            slurm_job_identity=job_identity(1),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
            raw_clock=lambda: next(values),
        )
        capture.call_model("RR_PHASE0", lambda: None)
        self.assert_reject(lambda: capture.finish(base_record(self.plan, "1", "RR", 1)), "incomplete")
        self.assert_reject(lambda: capture.call_model("RR_PHASE1", lambda: None), "failed")
        self.assertEqual(
            capture.cannot_check_sidecar("INCOMPLETE_PHASE_SEQUENCE", b"synthetic")["status"],
            "CANNOT_CHECK",
        )

        complete_values = iter((1, 2))
        complete = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="RR",
            attempt=1,
            slurm_job_identity=job_identity(2),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot-2"),
            raw_clock=lambda: next(complete_values),
        )
        complete.call_model("RR_PHASE0", lambda: None)
        complete.call_model("RR_PHASE1", lambda: None)
        self.assert_reject(
            lambda: complete.call_model("RR_PHASE1", lambda: None), "extra"
        )
        self.assert_reject(
            lambda: complete.finish(base_record(self.plan, "1", "RR", 1)), "failed"
        )

    def test_07_operation_exception_closes_interval_but_never_finishes_v2_capture(self) -> None:
        events = []
        values = iter((10, 20))
        capture = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="RR",
            attempt=1,
            slurm_job_identity=job_identity(1),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
            raw_clock=lambda: events.append("clock") or next(values),
        )
        with self.assertRaisesRegex(RuntimeError, "synthetic generation failure"):
            capture.call_model(
                "RR_PHASE0",
                lambda: (_ for _ in ()).throw(RuntimeError("synthetic generation failure")),
            )
        self.assertEqual(events, ["clock", "clock"])
        self.assert_reject(lambda: capture.finish(base_record(self.plan, "1", "RR", 1)), "failed")
        sidecar = capture.cannot_check_sidecar("SYNTHETIC_GENERATION_FAILURE", b"bounded detail")
        self.assertEqual(sidecar["status"], "CANNOT_CHECK")
        self.assertNotIn("accelerator_allocation_status", sidecar)

    def test_08_noninteger_boolean_negative_or_decreasing_clock_rejects(self) -> None:
        for readings in ((True, 2), (1.0, 2), (-1, 2), (2, 1)):
            values = iter(readings)
            capture = adapter.GenerationAttemptCapture(
                plan=self.plan,
                run_plan_sha256=self.run_plan_sha256,
                task_id="1",
                arm_id="OS",
                attempt=1,
                slurm_job_identity=job_identity(1),
                slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
                raw_clock=lambda: next(values),
            )
            self.assert_reject(
                lambda capture=capture: capture.call_model("OS_PHASE1", lambda: None),
                "clock" if readings[0] in (True, 1.0, -1) else "precedes",
            )

    def test_09_base_record_identity_seed_and_fields_are_exact(self) -> None:
        for mutate, fragment in (
            (lambda row: row.update(task_id="2"), "identity"),
            (lambda row: row.update(seed=999), "seed"),
            (lambda row: row.update(extra="forbidden"), "fields"),
            (lambda row: row.update(raw_output_sha256=b"not-json"), "serializable"),
            (lambda row: row.update(wall_time_seconds=float("nan")), "serializable"),
        ):
            values = iter((1, 2))
            capture = adapter.GenerationAttemptCapture(
                plan=self.plan,
                run_plan_sha256=self.run_plan_sha256,
                task_id="1",
                arm_id="OS",
                attempt=1,
                slurm_job_identity=job_identity(1),
                slurm_in_job_snapshot_sha256=synthetic_hash("snapshot"),
                raw_clock=lambda: next(values),
            )
            capture.call_model("OS_PHASE1", lambda: None)
            row = base_record(self.plan, "1", "OS", 1)
            mutate(row)
            self.assert_reject(lambda capture=capture, row=row: capture.finish(row), fragment)
            self.assert_reject(
                lambda capture=capture: capture.finish(
                    base_record(self.plan, "1", "OS", 1)
                ),
                "failed",
            )

    def test_10_successful_capture_remains_allocation_pending(self) -> None:
        capture = self.captures[0]
        self.assertEqual(capture["status"], "TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING")
        self.assertEqual(
            capture["allocation_status"],
            "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
        )
        self.assertNotIn("accelerator_allocation_status", capture)

    def test_11_complete_scheduler_evidence_builds_exact_index(self) -> None:
        index = self.validate_scheduler(self.captures, copy.deepcopy(self.evidence))
        self.assertEqual(index["status"], "EXCLUSIVE_NO_OVERLAP_CONFIRMED")
        self.assertEqual(index["tuple_count"], 918)
        self.assertEqual(index["unique_slurm_job_count"], 918)
        self.assertEqual(index["scheduler_raw_record_count"], 918)
        self.assertEqual(
            len(adapter.parse_scheduler_export_snapshot(self.scheduler_export_snapshot)),
            918,
        )
        first_raw_line = self.scheduler_export_snapshot.splitlines(keepends=True)[0]
        self.assertEqual(
            self.evidence["records"][0]["scheduler_record_sha256"],
            hashlib.sha256(first_raw_line).hexdigest(),
        )
        self.assertNotEqual(
            self.evidence["records"][0]["scheduler_record_sha256"],
            hashlib.sha256(first_raw_line[:-1]).hexdigest(),
        )
        self.assertEqual(index["overlap_conflict_count"], 0)

    def test_12_missing_duplicate_or_extra_scheduler_tuple_rejects(self) -> None:
        missing = copy.deepcopy(self.evidence)
        missing["records"].pop()
        duplicate = copy.deepcopy(self.evidence)
        duplicate["records"][-1]["task_id"] = duplicate["records"][0]["task_id"]
        duplicate["records"][-1]["arm_id"] = duplicate["records"][0]["arm_id"]
        duplicate["records"][-1]["attempt"] = duplicate["records"][0]["attempt"]
        extra = copy.deepcopy(self.evidence)
        extra["records"].append(copy.deepcopy(extra["records"][0]))
        for evidence, fragment in (
            (missing, "tuple"),
            (duplicate, "tuple"),
            (extra, "reuses"),
        ):
            self.assert_reject(
                lambda evidence=evidence: self.validate_scheduler(self.captures, evidence),
                fragment,
            )

    def test_13_one_slurm_job_cannot_bind_two_attempts(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][1]["slurm_job_identity"] = copy.deepcopy(
            evidence["records"][0]["slurm_job_identity"]
        )
        self.assert_reject(
            lambda: self.validate_scheduler(self.captures, evidence),
            "job",
        )

    def test_14_scheduler_and_capture_identity_snapshot_must_match(self) -> None:
        for field, value, fragment in (
            ("slurm_job_identity", job_identity(9999), "identity"),
            ("in_job_snapshot_sha256", synthetic_hash("wrong"), "snapshot"),
        ):
            evidence = copy.deepcopy(self.evidence)
            evidence["records"][10][field] = value
            self.assert_reject(
                lambda evidence=evidence: self.validate_scheduler(self.captures, evidence),
                fragment,
            )

    def test_15_environment_only_or_unbound_exclusivity_rejects(self) -> None:
        for status in (
            "CUDA_VISIBLE_DEVICES_PRESENT",
            "SLURM_JOB_ID_PRESENT",
            "CANNOT_CHECK",
            "EXCLUSIVE_NO_OVERLAP_CONFIRMED",
        ):
            evidence = copy.deepcopy(self.evidence)
            evidence["records"][0]["exclusive_gres_status"] = status
            self.assert_reject(
                lambda evidence=evidence: self.validate_scheduler(self.captures, evidence),
                "scheduler",
            )

    def test_16_gpu_count_and_key_cardinality_must_match_plan(self) -> None:
        mutations = (
            ("allocated_gpu_count", "2"),
            ("allocated_gpu_count", "0"),
            ("allocated_gpu_count", "01"),
            ("gpu_allocations", []),
            ("gpu_allocations", [{}, {}]),
        )
        for field, value in mutations:
            evidence = copy.deepcopy(self.evidence)
            evidence["records"][0][field] = value
            self.assert_reject(
                lambda evidence=evidence: self.validate_scheduler(self.captures, evidence),
                "gpu",
            )

    def test_17_invalid_or_zero_scheduler_interval_rejects(self) -> None:
        for start, end in (
            ("not-a-time", "2026-08-24T00:00:01Z"),
            ("2026-08-24T00:00:01Z", "2026-08-24T00:00:01Z"),
            ("2026-08-24T00:00:02Z", "2026-08-24T00:00:01Z"),
        ):
            evidence = copy.deepcopy(self.evidence)
            evidence["records"][0]["allocation_started_at_utc"] = start
            evidence["records"][0]["allocation_ended_at_utc"] = end
            self.assert_reject(
                lambda evidence=evidence: self.validate_scheduler(self.captures, evidence),
                "interval",
            )

    def test_18_scheduler_state_must_be_terminal_before_finalization(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][0]["scheduler_job_state"] = "RUNNING"
        self.assert_reject(
            lambda: self.validate_scheduler(self.captures, evidence),
            "terminal",
        )

    def test_19_same_gpu_scheduler_interval_overlap_rejects(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][1]["allocation_started_at_utc"] = evidence["records"][0][
            "allocation_started_at_utc"
        ]
        evidence["records"][1]["allocation_ended_at_utc"] = evidence["records"][0][
            "allocation_ended_at_utc"
        ]
        self.assert_reject(
            lambda: self.validate_scheduler(self.captures, evidence),
            "overlap",
        )

    def test_20_different_gpu_keys_may_run_concurrently(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][1]["allocation_started_at_utc"] = evidence["records"][0][
            "allocation_started_at_utc"
        ]
        evidence["records"][1]["allocation_ended_at_utc"] = evidence["records"][0][
            "allocation_ended_at_utc"
        ]
        evidence["records"][1]["gpu_allocations"][0]["gpu_uuid"] = (
            SYNTHETIC_GPU_UUID_2
        )
        evidence["records"][1]["gpu_allocations"][0]["gres_index"] = "1"
        index = self.validate_scheduler(self.captures, evidence)
        self.assertEqual(index["overlap_conflict_count"], 0)

    def test_21_raw_monotonic_values_are_not_cross_job_overlap_coordinates(self) -> None:
        captures = copy.deepcopy(self.captures)
        captures[0]["monotonic_start_ns"] = captures[1]["monotonic_start_ns"]
        captures[0]["monotonic_end_ns"] = captures[1]["monotonic_end_ns"]
        captures[0]["monotonic_elapsed_ns"] = captures[1]["monotonic_elapsed_ns"]
        index = self.validate_scheduler(captures, copy.deepcopy(self.evidence))
        self.assertFalse(index["cross_job_raw_monotonic_comparison_used"])

    def test_22_finalizer_emits_exact_v2_ledger_and_integer_cost(self) -> None:
        ledger, index, seal = adapter.finalize_v2_candidate_ledger(
            self.plan,
            self.run_plan_sha256,
            self.captures,
            self.evidence,
            self.scheduler_config_snapshot,
            self.scheduler_export_snapshot,
        )
        by_tuple, billed, totals = v2._validate_candidate_ledger(
            ledger,
            self.plan,
            expected_task_ids=v2.TASK_IDS,
            expected_run_plan_sha256=self.run_plan_sha256,
        )
        first = by_tuple[("1", "RR", 1)]
        self.assertEqual(first["generation_cost_quantity"], "2.000000001")
        self.assertEqual(first["accelerator_allocation_status"], "EXCLUSIVE_NO_OVERLAP_CONFIRMED")
        self.assertEqual(len(by_tuple), 918)
        self.assertEqual(billed, {"RR": 0, "OS": 0, "NR": 0})
        self.assertGreater(totals["OS"], 0)
        self.assertEqual(index["tuple_count"], 918)
        self.assertEqual(seal["candidate_record_count"], 918)

    def test_23_missing_billed_usd_stays_null_and_zero_is_not_imputed(self) -> None:
        ledger, _, seal = adapter.finalize_v2_candidate_ledger(
            self.plan,
            self.run_plan_sha256,
            self.captures,
            self.evidence,
            self.scheduler_config_snapshot,
            self.scheduler_export_snapshot,
        )
        self.assertTrue(
            all(
                row["billed_cost_usd"] is None
                and row["generation_billed_cost_usd"] is None
                and row["generation_billed_cost_status"] == "CANNOT_CHECK"
                for row in ledger["records"]
            )
        )
        self.assertFalse(seal["missing_billed_usd_imputed_as_zero"])

    def test_24_per_record_allocation_status_mutation_is_rejected(self) -> None:
        ledger, _, _ = adapter.finalize_v2_candidate_ledger(
            self.plan,
            self.run_plan_sha256,
            self.captures,
            self.evidence,
            self.scheduler_config_snapshot,
            self.scheduler_export_snapshot,
        )
        ledger["records"][0]["accelerator_allocation_status"] = "CANNOT_CHECK"
        with self.assertRaises(v2.ContractError) as caught:
            v2._validate_candidate_ledger(
                ledger,
                self.plan,
                expected_task_ids=v2.TASK_IDS,
                expected_run_plan_sha256=self.run_plan_sha256,
            )
        self.assertIn("exclusive", str(caught.exception).lower())

    def test_25_adapter_seal_hash_binds_all_evidence_and_unchanged_v2(self) -> None:
        ledger, index, seal = adapter.finalize_v2_candidate_ledger(
            self.plan,
            self.run_plan_sha256,
            self.captures,
            self.evidence,
            self.scheduler_config_snapshot,
            self.scheduler_export_snapshot,
        )
        self.assertEqual(seal["capture_ledger_canonical_sha256"], canonical_hash(self.captures))
        self.assertEqual(seal["scheduler_evidence_canonical_sha256"], canonical_hash(self.evidence))
        self.assertEqual(seal["allocation_index_canonical_sha256"], canonical_hash(index))
        self.assertEqual(seal["candidate_ledger_canonical_sha256"], canonical_hash(ledger))
        self.assertEqual(
            seal["scheduler_raw_record_hash_set_sha256"],
            index["scheduler_raw_record_hash_set_sha256"],
        )
        self.assertEqual(
            seal["scheduler_config_snapshot_sha256"],
            hashlib.sha256(self.scheduler_config_snapshot).hexdigest(),
        )
        self.assertEqual(
            seal["scheduler_export_snapshot_sha256"],
            hashlib.sha256(self.scheduler_export_snapshot).hexdigest(),
        )
        self.assertEqual(seal["runner_v2_module_sha256"], adapter.RUNNER_V2_MODULE_SHA256)
        self.assertFalse(seal["official_outcomes_opened"])

    def test_26_strict_json_rejects_duplicate_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"status":"PASS","status":"FAIL"}\n')
            self.assert_reject(lambda: adapter.read_json_snapshot(path, "hostile"), "strict")

    def test_27_outputs_are_new_atomic_and_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "output.json"
            observed = adapter.write_new_canonical_json(path, {"synthetic": True})
            self.assertEqual(observed, hashlib.sha256(path.read_bytes()).hexdigest())
            preserved = path.read_bytes()
            self.assert_reject(
                lambda: adapter.write_new_canonical_json(path, {"synthetic": False}),
                "exists",
            )
            self.assertEqual(path.read_bytes(), preserved)

    def test_28_full_cli_finalization_is_deterministic_and_outcome_blind(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan_path = root / "plan.json"
            captures_path = root / "captures.json"
            evidence_path = root / "scheduler.json"
            config_snapshot_path = root / "scontrol-show-config.txt"
            export_snapshot_path = root / "scontrol-sacct-export.txt"
            ledger_path = root / "ledger.json"
            index_path = root / "allocation-index.json"
            seal_path = root / "adapter-seal.json"
            plan_path.write_text(json.dumps(self.plan, indent=2) + "\n")
            run_plan_sha256 = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            captures = all_captures(self.plan, run_plan_sha256)
            evidence, export_snapshot = scheduler_evidence(captures)
            config_snapshot_path.write_bytes(SYNTHETIC_CONFIG_SNAPSHOT)
            export_snapshot_path.write_bytes(export_snapshot)
            captures_path.write_text(json.dumps({"records": captures}, indent=2) + "\n")
            evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
            with redirect_stdout(io.StringIO()) as stdout:
                status = adapter.main(
                    [
                        "finalize",
                        "--run-plan", str(plan_path),
                        "--capture-ledger", str(captures_path),
                        "--scheduler-evidence", str(evidence_path),
                        "--scheduler-config-snapshot", str(config_snapshot_path),
                        "--scheduler-export-snapshot", str(export_snapshot_path),
                        "--output-ledger", str(ledger_path),
                        "--output-allocation-index", str(index_path),
                        "--output-adapter-seal", str(seal_path),
                    ]
                )
            self.assertEqual(status, 0)
            emitted = json.loads(ledger_path.read_text())
            self.assertEqual(len(emitted["records"]), 918)
            seal = json.loads(seal_path.read_text())
            self.assertEqual(seal["run_plan_sha256"], run_plan_sha256)
            self.assertIn("ADAPTER_CONFORMANCE_PASS", stdout.getvalue())

    def test_29_external_scheduler_snapshot_hash_mismatch_rejects(self) -> None:
        self.assert_reject(
            lambda: adapter.validate_scheduler_snapshot_bindings(
                self.evidence,
                synthetic_hash("wrong-config-snapshot"),
                self.evidence["scheduler_export_sha256"],
            ),
            "config",
        )
        self.assert_reject(
            lambda: adapter.validate_scheduler_snapshot_bindings(
                self.evidence,
                self.evidence["scheduler_config_snapshot_sha256"],
                synthetic_hash("wrong-export-snapshot"),
            ),
            "export",
        )

    def test_30_source_has_no_archive_credential_evaluator_or_outcome_capability(self) -> None:
        source = MODULE_PATH.read_text()
        for forbidden in (
            "import requests",
            "import docker",
            "run_evaluation",
            "success_rate",
            "gold_program",
            "benchmark_verified",
            "OPENAI_API_KEY",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("official_outcomes_opened", source)

    def test_31_cli_rolls_back_earlier_outputs_if_later_output_creation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan_path = root / "plan.json"
            captures_path = root / "captures.json"
            evidence_path = root / "scheduler.json"
            config_snapshot_path = root / "scontrol-show-config.txt"
            export_snapshot_path = root / "scontrol-sacct-export.txt"
            ledger_path = root / "ledger.json"
            index_path = root / "allocation-index.json"
            seal_path = root / "adapter-seal.json"
            plan_path.write_text(json.dumps(self.plan, indent=2) + "\n")
            run_plan_sha256 = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            captures = all_captures(self.plan, run_plan_sha256)
            evidence, export_snapshot = scheduler_evidence(captures)
            config_snapshot_path.write_bytes(SYNTHETIC_CONFIG_SNAPSHOT)
            export_snapshot_path.write_bytes(export_snapshot)
            captures_path.write_text(json.dumps({"records": captures}, indent=2) + "\n")
            evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
            index_path.write_bytes(b"hostile-race-winner\n")

            with (
                mock.patch.object(adapter, "_validate_cli_paths", return_value=None),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                adapter.main(
                    [
                        "finalize",
                        "--run-plan", str(plan_path),
                        "--capture-ledger", str(captures_path),
                        "--scheduler-evidence", str(evidence_path),
                        "--scheduler-config-snapshot", str(config_snapshot_path),
                        "--scheduler-export-snapshot", str(export_snapshot_path),
                        "--output-ledger", str(ledger_path),
                        "--output-allocation-index", str(index_path),
                        "--output-adapter-seal", str(seal_path),
                    ]
                )

            self.assertFalse(ledger_path.exists())
            self.assertEqual(index_path.read_bytes(), b"hostile-race-winner\n")
            self.assertFalse(seal_path.exists())

            ledger_path_2 = root / "ledger-2.json"
            index_path_2 = root / "allocation-index-2.json"
            seal_path_2 = root / "adapter-seal-2.json"
            seal_path_2.write_bytes(b"second-hostile-race-winner\n")
            with (
                mock.patch.object(adapter, "_validate_cli_paths", return_value=None),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                adapter.main(
                    [
                        "finalize",
                        "--run-plan", str(plan_path),
                        "--capture-ledger", str(captures_path),
                        "--scheduler-evidence", str(evidence_path),
                        "--scheduler-config-snapshot", str(config_snapshot_path),
                        "--scheduler-export-snapshot", str(export_snapshot_path),
                        "--output-ledger", str(ledger_path_2),
                        "--output-allocation-index", str(index_path_2),
                        "--output-adapter-seal", str(seal_path_2),
                    ]
                )
            self.assertFalse(ledger_path_2.exists())
            self.assertFalse(index_path_2.exists())
            self.assertEqual(seal_path_2.read_bytes(), b"second-hostile-race-winner\n")

    def test_32_hostile_scheduler_member_types_fail_as_contract_errors(self) -> None:
        hostile_cases = (
            ("scheduler_job_state", [], "state"),
            ("gpu_allocations", [{}], "gpu"),
        )
        for field, value, fragment in hostile_cases:
            with self.subTest(field=field):
                evidence = copy.deepcopy(self.evidence)
                evidence["records"][0][field] = value
                self.assert_reject(
                    lambda evidence=evidence: self.validate_scheduler(
                        self.captures, evidence
                    ),
                    fragment,
                )

    def test_33_wrapper_requires_a_new_attempt_output_directory(self) -> None:
        source = WRAPPER_PATH.read_text()
        self.assertNotIn('mkdir -p "$OUTPUT_DIR"', source)
        self.assertIn('mkdir -m 700 -- "$OUTPUT_DIR"', source)
        self.assertIn("set -C", source)

    def test_34_success_and_cannot_check_are_mutually_exclusive_terminal_receipts(self) -> None:
        values = iter((1, 2))
        capture = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="OS",
            attempt=1,
            slurm_job_identity=job_identity(3),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot-3"),
            raw_clock=lambda: next(values),
        )
        capture.call_model("OS_PHASE1", lambda: None)
        capture.finish(base_record(self.plan, "1", "OS", 1))
        self.assert_reject(
            lambda: capture.cannot_check_sidecar("LATE_FAILURE", b"synthetic"),
            "finalized",
        )

        failed_values = iter((1, 2))
        failed = adapter.GenerationAttemptCapture(
            plan=self.plan,
            run_plan_sha256=self.run_plan_sha256,
            task_id="1",
            arm_id="OS",
            attempt=1,
            slurm_job_identity=job_identity(4),
            slurm_in_job_snapshot_sha256=synthetic_hash("snapshot-4"),
            raw_clock=lambda: next(failed_values),
        )
        failed.call_model("OS_PHASE1", lambda: None)
        sidecar = failed.cannot_check_sidecar("EXTERNAL_FAILURE", b"synthetic")
        self.assertEqual(sidecar["status"], "CANNOT_CHECK")
        self.assert_reject(
            lambda: failed.cannot_check_sidecar("SECOND_FAILURE", b"synthetic"),
            "finalized",
        )

    def test_35_slurm_allocation_identity_has_one_canonical_representation(self) -> None:
        canonical_array = {
            "cluster": "lunarc",
            "job_id": "4000001_1",
            "array_job_id": "4000001",
            "array_task_id": "1",
        }
        self.assertEqual(
            adapter._validate_job_identity(canonical_array, "canonical array"),
            canonical_array,
        )
        self.assertEqual(
            adapter._canonical_job_allocation_key(
                canonical_array, "canonical array"
            ),
            "lunarc:4000001_1",
        )
        hostile_identities = (
            {
                "cluster": "lunarc",
                "job_id": "4000001_1",
                "array_job_id": None,
                "array_task_id": None,
            },
            {
                "cluster": "lunarc",
                "job_id": "04000001",
                "array_job_id": None,
                "array_task_id": None,
            },
            {
                "cluster": "lunarc",
                "job_id": "4000001_1",
                "array_job_id": "4000001",
                "array_task_id": "01",
            },
            {
                "cluster": "lunarc",
                "job_id": "4000001_1",
                "array_job_id": "4000002",
                "array_task_id": "1",
            },
            {
                "cluster": "LUNARC",
                "job_id": "4000001",
                "array_job_id": None,
                "array_task_id": None,
            },
            {
                "cluster": "lunarc",
                "job_id": "4000001.batch",
                "array_job_id": None,
                "array_task_id": None,
            },
        )
        for identity in hostile_identities:
            with self.subTest(identity=identity):
                self.assert_reject(
                    lambda identity=identity: adapter._validate_job_identity(
                        identity, "hostile identity"
                    ),
                    "canonical",
                )

        captures = copy.deepcopy(self.captures)
        evidence = copy.deepcopy(self.evidence)
        alias_null = copy.deepcopy(hostile_identities[0])
        captures[0]["slurm_job_identity"] = copy.deepcopy(alias_null)
        evidence["records"][0]["slurm_job_identity"] = copy.deepcopy(alias_null)
        captures[1]["slurm_job_identity"] = copy.deepcopy(canonical_array)
        evidence["records"][1]["slurm_job_identity"] = copy.deepcopy(canonical_array)
        self.assert_reject(
            lambda: self.validate_scheduler(captures, evidence),
            "canonical",
        )

    def test_36_gpu_case_alias_cannot_evade_same_physical_gpu_overlap(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][1]["allocation_started_at_utc"] = evidence["records"][0][
            "allocation_started_at_utc"
        ]
        evidence["records"][1]["allocation_ended_at_utc"] = evidence["records"][0][
            "allocation_ended_at_utc"
        ]
        evidence["records"][1]["gpu_allocations"][0]["gpu_uuid"] = (
            SYNTHETIC_GPU_UUID_1.upper()
        )
        self.assert_reject(
            lambda: self.validate_scheduler(self.captures, evidence),
            "gpu",
        )

    def test_37_parsed_scheduler_fields_must_equal_exact_raw_record(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][0]["scheduler_job_state"] = "FAILED"
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                evidence,
                self.plan,
                self.run_plan_sha256,
                self.scheduler_export_snapshot,
            ),
            "exact retained raw record",
        )

    def test_38_one_raw_scheduler_record_cannot_bind_two_evidence_rows(self) -> None:
        evidence = copy.deepcopy(self.evidence)
        evidence["records"][1]["scheduler_record_sha256"] = evidence["records"][0][
            "scheduler_record_sha256"
        ]
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                evidence,
                self.plan,
                self.run_plan_sha256,
                self.scheduler_export_snapshot,
            ),
            "reuses",
        )

    def test_39_raw_scheduler_export_line_set_is_exact_and_unambiguous(self) -> None:
        lines = self.scheduler_export_snapshot.splitlines(keepends=True)
        missing = b"".join(lines[:-1])
        missing_evidence = copy.deepcopy(self.evidence)
        missing_evidence["scheduler_export_sha256"] = hashlib.sha256(missing).hexdigest()
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                missing_evidence,
                self.plan,
                self.run_plan_sha256,
                missing,
            ),
            "absent",
        )

        duplicate = self.scheduler_export_snapshot + lines[0]
        duplicate_evidence = copy.deepcopy(self.evidence)
        duplicate_evidence["scheduler_export_sha256"] = hashlib.sha256(
            duplicate
        ).hexdigest()
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                duplicate_evidence,
                self.plan,
                self.run_plan_sha256,
                duplicate,
            ),
            "reuses",
        )

        extra_raw_record = json.loads(lines[0][:-1])
        extra_raw_record["scheduler_job_state"] = "FAILED"
        extra_line = adapter.canonical_json_bytes(extra_raw_record) + b"\n"
        extra = self.scheduler_export_snapshot + extra_line
        extra_evidence = copy.deepcopy(self.evidence)
        extra_evidence["scheduler_export_sha256"] = hashlib.sha256(extra).hexdigest()
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                extra_evidence,
                self.plan,
                self.run_plan_sha256,
                extra,
            ),
            "exact retained scheduler export record set",
        )

        crlf = lines[0][:-1] + b"\r\n" + b"".join(lines[1:])
        crlf_evidence = copy.deepcopy(self.evidence)
        crlf_evidence["scheduler_export_sha256"] = hashlib.sha256(crlf).hexdigest()
        self.assert_reject(
            lambda: adapter.validate_scheduler_allocation_evidence(
                self.captures,
                crlf_evidence,
                self.plan,
                self.run_plan_sha256,
                crlf,
            ),
            "LF-only",
        )

    def test_40_structured_node_uuid_and_gres_aliases_reject(self) -> None:
        hostile_cases = []

        uppercase_node = copy.deepcopy(self.evidence)
        uppercase_node["records"][1]["node_name"] = "SYNTHETIC-CN001"
        uppercase_node["records"][1]["gpu_allocations"][0]["node_name"] = (
            "SYNTHETIC-CN001"
        )
        hostile_cases.append((uppercase_node, "canonical"))

        node_alias = copy.deepcopy(self.evidence)
        node_alias["records"][1]["node_name"] = "synthetic-cn002"
        node_alias["records"][1]["gpu_allocations"][0]["node_name"] = (
            "synthetic-cn002"
        )
        hostile_cases.append((node_alias, "aliases"))

        gres_alias = copy.deepcopy(self.evidence)
        gres_alias["records"][1]["gpu_allocations"][0]["gpu_uuid"] = (
            SYNTHETIC_GPU_UUID_2
        )
        hostile_cases.append((gres_alias, "GRES"))

        lexical_index_alias = copy.deepcopy(self.evidence)
        lexical_index_alias["records"][1]["gpu_allocations"][0]["gres_index"] = "00"
        hostile_cases.append((lexical_index_alias, "canonical"))

        uppercase_gres_type = copy.deepcopy(self.evidence)
        uppercase_gres_type["records"][1]["gpu_allocations"][0]["gres_type"] = "A40"
        hostile_cases.append((uppercase_gres_type, "canonical"))

        for evidence, fragment in hostile_cases:
            with self.subTest(fragment=fragment):
                self.assert_reject(
                    lambda evidence=evidence: self.validate_scheduler(
                        self.captures, evidence
                    ),
                    fragment,
                )

    def test_41_wrapper_emits_canonical_base_or_array_allocation_identity(self) -> None:
        source = WRAPPER_PATH.read_text()
        self.assertIn(
            'CANONICAL_JOB_ID="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"',
            source,
        )
        self.assertIn(
            '[[ "$SLURM_CLUSTER_NAME" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]',
            source,
        )
        self.assertIn('"$CANONICAL_JOB_ID"', source)


def write_receipt(result: unittest.TestResult) -> None:
    receipt = {
        "schema_version": "orion.p1.scienceagentbench.lunarc-generation-adapter-synthetic-validation.v1",
        "fixtures": "SYNTHETIC_NONBENCHMARK_METADATA_ONLY",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "production_shape": {
            "task_count": 102,
            "arms": ["RR", "OS", "NR"],
            "attempts_per_task_arm": 3,
            "tuple_count": 918,
        },
        "clock": "CLOCK_MONOTONIC_RAW_VIA_CLOCK_GETTIME_NS",
        "scheduler_evidence": "SYNTHETIC_SCONTROL_AND_SACCT_SHAPED_METADATA",
        "official_tasks_run": 0,
        "official_outcomes_opened": 0,
        "official_evaluator_invocations": 0,
        "pytest_or_ci_run": False,
        "scientific_authority_delta": "NONE",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdapterSyntheticTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    write_receipt(result)
    if result.wasSuccessful():
        print(
            "P1_SAB_LUNARC_GENERATION_ADAPTER_SYNTHETIC_HOSTILE_VALIDATION_PASS "
            f"tests={result.testsRun} official_tasks=0 official_outcomes=0"
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
