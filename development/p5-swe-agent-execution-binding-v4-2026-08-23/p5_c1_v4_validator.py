#!/usr/bin/env python3
"""Deterministic non-pytest validator for the P5 C1 SWE-agent V4 packet."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import tempfile
from pathlib import Path

import p5_c1_isolated_runner as runner
import p5_c1_native_parser as native


ROOT = Path(__file__).resolve().parent
EXPECTED_FIELDS = {
    "adapter.isolated_write_surface",
    "adapter.native_parser_binding",
    "custody.external_protected_scorer",
    "custody.one_shot_no_feedback_barrier",
    "custody.protected_panel_freshness",
    "identity.native_entrypoint_bytes",
    "identity.source_license_bytes",
    "identity.source_repository_commit",
    "inputs.candidate_visible_case_bytes",
    "model_provider.fallbacks",
    "model_provider.primary",
    "resources.calls_tokens_usd",
    "resources.retry_network",
    "resources.wallclock",
    "rights.container_and_generated_artifacts",
    "rights.model_provider_and_services",
    "rights.task_and_benchmark_content",
    "runtime.compute",
    "runtime.container_or_environment",
    "runtime.dependency_lock",
    "runtime.task_environment",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synthetic(exit_status=None, submission=None, steps=1, extra_info=None):
    info = {
        "exit_status": exit_status,
        "submission": submission,
        "model_stats": {"api_calls": 1, "tokens_sent": 10, "tokens_received": 2, "instance_cost": 0.01},
    }
    if extra_info:
        info.update(extra_info)
    return json.dumps({"trajectory": [{}] * steps, "history": [], "info": info, "replay_config": "{}"}).encode()


def main() -> int:
    json_paths = sorted(ROOT.glob("*.json"))
    parsed = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in json_paths}
    assert len(json_paths) == 11, len(json_paths)

    for py in sorted(ROOT.glob("*.py")):
        ast.parse(py.read_text(encoding="utf-8"), filename=py.name)

    registry = parsed["P5_C1_V4_FIELD_REGISTRY.json"]
    assert set(registry["fields"]) == EXPECTED_FIELDS
    assert set(registry["required_field_paths"]) == EXPECTED_FIELDS
    bound = sorted(k for k, v in registry["fields"].items() if v["state"] == "BOUND")
    blocking = sorted(k for k, v in registry["fields"].items() if v["state"] != "BOUND")
    assert len(bound) == registry["bound_field_count"] == 9
    assert len(blocking) == registry["blocking_field_count"] == 12
    assert blocking == registry["blocking_fields"]
    assert not registry["execution_ready"]
    assert registry["panel_confirmatory_ready_arms"] == 0

    cases = [
        (synthetic("submitted", "diff --git a/a b/a\n"), "COMPLETE_SUCCESS"),
        (synthetic("submitted (exit_cost)", "diff --git a/a b/a\n"), "PARTIAL"),
        (synthetic("exit_command_timeout", None), "TIMEOUT"),
        (synthetic("exit_cost", None), "ABSTAIN"),
        (synthetic("exit_api", None), "ERROR"),
        (synthetic(None, None, steps=0), "EMPTY"),
        (synthetic(None, "partial", steps=1), "PARTIAL"),
        (synthetic("new_unknown_terminal", None), "INVALID"),
    ]
    for raw, expected in cases:
        output = native.parse_trajectory_bytes(raw, expected_instance_id="SAFE-SYNTHETIC")
        assert output["native_terminal"]["status"] == expected
        assert output["adapter_disposition"]["output"] == "UNRESOLVED"
        assert output["adapter_disposition"]["raw_native_singleton_licensed"] is False
        assert output["outcome_boundary"]["protected_keys_seen"] is False

    refused = False
    try:
        native.parse_trajectory_bytes(synthetic("submitted", "x", extra_info={"gold_patch": "forbidden"}))
    except native.NativeParseError:
        refused = True
    assert refused

    assert runner.blockers(registry) == registry["blocking_fields"]
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / "source"
        task = base / "task"
        output = base / "output"
        source.mkdir()
        task.mkdir()
        output.mkdir()
        refused = False
        try:
            runner.construct_command(registry=registry, source_dir=source, task_seed_dir=task, output_dir=output)
        except runner.IsolationRefusal:
            refused = True
        assert refused

        all_bound = copy.deepcopy(registry)
        for value in all_bound["fields"].values():
            value["state"] = "BOUND"
        command = runner.construct_command(
            registry=all_bound,
            source_dir=source,
            task_seed_dir=task,
            output_dir=output,
        )
        joined = " ".join(command)
        assert "--read-only" in command
        assert "--network" in command and "none" in command
        assert "--cap-drop" in command and "ALL" in command
        assert "dst=/input/source,readonly" in joined
        assert "dst=/input/task,readonly" in joined
        assert "dst=/run/p5-output" in joined and "dst=/run/p5-output,readonly" not in joined
        assert "compare-runs" not in joined and "evaluate" not in joined and "score" not in joined

    assert sha(ROOT / "SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock") == "488077a1f953459ee955ef17588dcb0eb3e7b5e42ed3e1ba252c3af96ff573c8"
    assert sha(ROOT / "UPSTREAM_SIMPLE_INSTANCE.yaml") == "b088b1a7d146afcab66d2c529409066685a2b4d4433ba18df3649aef0c374bd8"
    source = parsed["P5_C1_V4_SOURCE_RIGHTS_MANIFEST.json"]
    assert source["commit_sha"] == "3ea751c087f32b16e039a2233dd6eefecef325d5"
    assert source["rights"]["swe_agent_source"]["state"] == "BOUND"
    assert source["rights"]["p5_task_and_benchmark_content"]["state"] == "UNBOUND"
    assert source["outcome_boundary"]["public_benchmark_first_record_key_names_observed"] is True
    assert source["outcome_boundary"]["gold_patch_or_test_patch_payload_values_disclosed_to_lane"] is False
    assert source["outcome_boundary"]["protected_test_content_disclosed_to_lane"] is False
    assert source["outcome_boundary"]["protected_scores_accessed"] is False
    assert source["outcome_boundary"]["comparator_outcomes_accessed"] is False

    result = parsed["P5_C1_V4_RESULT.json"]
    assert result["execution"]["panel_confirmatory_ready_arms"] == 0
    assert result["preserved_boundaries"]["raw_native_singleton_licences"] == 0
    assert result["preserved_boundaries"]["scienceclaw_supported_singletons"] == 0
    assert result["preserved_claims"]["performance"] == "CANNOT_CHECK"
    assert result["preserved_claims"]["superiority"] == "CANNOT_CHECK"

    checksum_lines = (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    expected_files = sorted(p.name for p in ROOT.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    actual_files = []
    for line in checksum_lines:
        digest, name = line.split("  ", 1)
        actual_files.append(name)
        assert sha(ROOT / name) == digest
    assert sorted(actual_files) == expected_files

    forbidden_payload_suffixes = {".traj", ".patch", ".jsonl"}
    assert not [p for p in ROOT.iterdir() if p.suffix in forbidden_payload_suffixes]

    print(
        "P5_C1_V4_VALIDATED__11_JSON__8_AUTHORED_SYNTHETIC_NATIVE_CASES__"
        "9_BOUND__12_BLOCKING__0_OF_6_PANEL_READY__ZERO_RAW_SINGLETONS__"
        "NO_OUTCOME_EXECUTION"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
