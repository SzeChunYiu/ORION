from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from orion.study.p1_causal.authority_value_cases import (
    generate_authority_value_tasks,
    serialize_gold,
    serialize_public,
    task_manifest,
)

ROOT = Path(__file__).resolve().parents[4]
P1 = ROOT / "research" / "revival" / "p1"
PROTOCOL = P1 / "protocol" / "P1.authority-value.v2.1.1.json"
HOLDOUT_SCRIPT = P1 / "freeze_authority_value_holdout.py"
EXECUTION_SCRIPT = P1 / "freeze_authority_value_execution.py"
RUNNER_SCRIPT = P1 / "run_authority_value_campaign.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


holdout_freezer = _load("p1_av_holdout_freezer_pipeline", HOLDOUT_SCRIPT)
execution_freezer = _load("p1_av_execution_freezer_pipeline", EXECUTION_SCRIPT)
runner = _load("p1_av_runner_pipeline", RUNNER_SCRIPT)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_development_holdout(tmp_path: Path) -> Path:
    # Never use the frozen confirmatory seed in a unit test.
    tasks = generate_authority_value_tasks(seed=2026)
    public = serialize_public(tasks)
    gold = serialize_gold(tasks)
    manifest = task_manifest(tasks)
    effective, identity = holdout_freezer.load_effective_protocol(PROTOCOL)
    assert int(effective["fresh_holdout_plan"]["confirmatory_seed"]) != 2026
    assert manifest["candidate_view_leak_count"] == 0

    outdir = tmp_path / "holdout"
    outdir.mkdir()
    (outdir / "PUBLIC_CASES.jsonl").write_bytes(public)
    (outdir / "PROTECTED_GOLD.jsonl").write_bytes(gold)
    (outdir / "HOLDOUT_FREEZE.json").write_text(
        json.dumps(
            {
                "schema_version": "P1.authority-value-holdout-freeze.v1",
                "protocol_id": effective["protocol_id"],
                "protocol_version": effective["protocol_version"],
                "protocol_chain": identity,
                "primary_comparator": effective["primary_hypothesis"]["primary_comparator"],
                "confirmatory_seed": 2026,
                "n": manifest["n"],
                "public_sha256": _sha(public),
                "protected_gold_sha256": _sha(gold),
                "candidate_view_leak_count": 0,
                "arms_executed": False,
                "source_sha256": {},
                "by_family": manifest["by_family"],
                "claim_boundary": "DEVELOPMENT_PIPELINE_SELFTEST_ONLY",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return outdir


def test_development_pipeline_binds_and_executes_without_confirmatory_seed(tmp_path: Path) -> None:
    holdout_dir = _write_development_holdout(tmp_path)
    execution_path = tmp_path / "EXECUTION_FREEZE.json"
    binding = execution_freezer.freeze_execution(PROTOCOL, holdout_dir, execution_path)
    assert binding["arms_executed"] is False
    assert binding["outcome_accessed"] is False
    assert binding["primary_comparator"] == "class_conditioned_minimal_repair"
    assert binding["decision_parameters"]["scientifically_valid_repair_superiority_margin"] == 0.10

    outdir = tmp_path / "results"
    result = runner.execute(holdout_dir, execution_path, outdir)
    assert result["n_tasks"] == 384
    assert result["n_arms"] == 8
    assert result["terminal"] in {
        "P1_AUTHORITY_VALUE_SUPPORTED",
        "P1_AUTHORITY_VALUE_NOT_SUPPORTED",
    }
    assert (outdir / "RAW_RESULTS.jsonl").is_file()
    assert len((outdir / "RAW_RESULTS.jsonl").read_text().splitlines()) == 384 * 8
    assert result["analysis"]["primary_arm"] == "orion_typed_permission_dependency_reopen"
    assert result["analysis"]["comparator_arm"] == "class_conditioned_minimal_repair"


def test_execution_freeze_rejects_public_holdout_drift(tmp_path: Path) -> None:
    holdout_dir = _write_development_holdout(tmp_path)
    public_path = holdout_dir / "PUBLIC_CASES.jsonl"
    public_path.write_bytes(public_path.read_bytes() + b"{}\n")
    execution_path = tmp_path / "EXECUTION_FREEZE.json"
    try:
        execution_freezer.freeze_execution(PROTOCOL, holdout_dir, execution_path)
    except ValueError as exc:
        assert "public holdout bytes drifted" in str(exc)
    else:
        raise AssertionError("public holdout drift must be rejected")


def test_campaign_rejects_execution_source_drift(tmp_path: Path) -> None:
    holdout_dir = _write_development_holdout(tmp_path)
    execution_path = tmp_path / "EXECUTION_FREEZE.json"
    execution_freezer.freeze_execution(PROTOCOL, holdout_dir, execution_path)
    payload = json.loads(execution_path.read_text())
    path = next(iter(payload["source_sha256"]))
    payload["source_sha256"][path] = "0" * 64
    execution_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    try:
        runner.execute(holdout_dir, execution_path, tmp_path / "results")
    except ValueError as exc:
        assert "execution source drift" in str(exc)
    else:
        raise AssertionError("execution source drift must be rejected")
