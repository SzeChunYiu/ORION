import copy
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "research/orion-discovery-v3/EXECUTION_TAKEOVER_MANIFEST_V1.json"


def _takeover_api():
    try:
        return importlib.import_module("orion.discovery.execution_takeover")
    except ModuleNotFoundError as exc:
        pytest.fail(f"the execution takeover module is missing: {exc}")


def test_v3_workflow_installs_project_dependencies_before_hostile_suite() -> None:
    workflow = (ROOT / ".github/workflows/orion-discovery-v3.yml").read_text()

    install_at = workflow.find("python -m pip install -e .")
    hostile_at = workflow.find("python -m pytest -q tests/unit/discovery/test_frontier_dominance.py")

    assert install_at >= 0, "the V3 workflow must install ORION's declared dependencies"
    assert install_at < hostile_at, "project dependencies must be installed before test collection"


def test_canonical_takeover_manifest_is_valid_but_not_pretended_ready() -> None:
    api = _takeover_api()

    assert MANIFEST.exists(), "the newer 13-job queue needs a canonical machine-readable manifest"
    manifest = api.load_manifest(MANIFEST)
    api.validate_manifest(manifest)

    assert len(manifest["jobs"]) == 13
    assert api.ready_job_ids(manifest) == ()


def test_manifest_rejects_duplicate_canonical_job_identities() -> None:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    manifest["jobs"].append(copy.deepcopy(manifest["jobs"][0]))

    with pytest.raises(api.ManifestError, match="duplicate canonical job id"):
        api.validate_manifest(manifest)


def test_manifest_rejects_false_exact_aliases() -> None:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    predecessor = manifest["jobs"][0]["predecessors"][0]
    predecessor["relationship"] = "EXACT_ALIAS"
    predecessor["scientific_question_sha256"] = "0" * 64

    with pytest.raises(api.ManifestError, match="exact alias question hash mismatch"):
        api.validate_manifest(manifest)


def test_takeover_checker_reports_blocked_queue_without_pretending_execution() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")

    completed = subprocess.run(
        [sys.executable, "scripts/check_orion_execution_takeover.py"],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == (
        "ORION_DISCOVERY_V3_TAKEOVER_VALID jobs=13 ready=0 blocked=13"
    )


def _engineering_protocol() -> dict:
    return {
        "schema": "orion.discovery.v3.execution-protocol.v1",
        "job_id": "V3-ENGINEERING-REFERENCE-01",
        "source_git_sha": "5f4a83dceffbc783e0df946b22378524b123ec7e",
        "authority_ceiling": "ENGINEERING_REFERENCE_CHECK_ONLY",
        "paper_authority_delta": "NONE",
        "inputs": {
            "commands": ["check", "hostile", "census", "compile"],
            "runner_sha256": "a" * 64,
        },
        "resource_vector": {"nodes": 1, "cpus": 2, "memory_mb": 4096, "minutes": 10},
        "matched_contract": {"environment": "pinned", "outcomes_accessed": False},
    }


def test_protocol_freeze_is_deterministic_and_content_addressed() -> None:
    api = _takeover_api()
    left = _engineering_protocol()
    right = dict(reversed(list(left.items())))

    frozen_left = api.freeze_protocol(left)
    frozen_right = api.freeze_protocol(right)

    assert frozen_left == frozen_right
    assert frozen_left["state"] == "FROZEN"
    assert len(frozen_left["protocol_sha256"]) == 64


def test_protocol_freeze_rejects_outcome_bearing_inputs() -> None:
    api = _takeover_api()
    protocol = _engineering_protocol()
    protocol["inputs"]["observed_results"] = ["winner=A"]

    with pytest.raises(api.ManifestError, match="outcome-bearing key"):
        api.freeze_protocol(protocol)


@pytest.mark.parametrize("runner_hash", [None, "A" * 64, "a" * 63, "g" * 64])
def test_protocol_freeze_requires_content_bound_runner(runner_hash: str | None) -> None:
    api = _takeover_api()
    protocol = _engineering_protocol()
    if runner_hash is None:
        del protocol["inputs"]["runner_sha256"]
    else:
        protocol["inputs"]["runner_sha256"] = runner_hash

    with pytest.raises(api.ManifestError, match="runner_sha256"):
        api.freeze_protocol(protocol)


def test_frozen_protocol_rejects_post_freeze_tampering() -> None:
    api = _takeover_api()
    frozen = api.freeze_protocol(_engineering_protocol())
    frozen["resource_vector"]["cpus"] = 99

    with pytest.raises(api.ManifestError, match="frozen protocol hash mismatch"):
        api.validate_frozen_protocol(frozen)


def test_scheduler_deduplication_blocks_live_and_terminal_records() -> None:
    api = _takeover_api()
    frozen = api.freeze_protocol(_engineering_protocol())
    key = api.submission_key(frozen)

    records = [
        {"submission_key": "different", "state": "FAILED"},
        {"submission_key": key, "state": "COMPLETED"},
    ]

    assert api.duplicate_scheduler_records(key, records) == (records[1],)


def test_slurm_script_binds_protocol_and_uses_argv_command() -> None:
    api = _takeover_api()
    frozen = api.freeze_protocol(_engineering_protocol())

    script = api.render_slurm_script(
        frozen,
        account="hep2023-1-3",
        partition="hep",
        command=["python", "run_reference.py", "--protocol", "EXECUTION_PROTOCOL.json"],
        stdout_path="logs/reference-%j.out",
        stderr_path="logs/reference-%j.err",
    )

    assert f"ORION_SUBMISSION_KEY={api.submission_key(frozen)}" in script
    assert "python run_reference.py --protocol EXECUTION_PROTOCOL.json" in script
    assert "eval" not in script


def test_freeze_and_package_clis_create_bound_slurm_artifacts(tmp_path: Path) -> None:
    protocol_path = tmp_path / "draft.json"
    frozen_path = tmp_path / "EXECUTION_PROTOCOL.json"
    slurm_path = tmp_path / "run.sbatch"
    protocol_path.write_text(json.dumps(_engineering_protocol()))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")

    freeze = subprocess.run(
        [
            sys.executable,
            "scripts/freeze_orion_execution_job.py",
            str(protocol_path),
            str(frozen_path),
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert freeze.returncode == 0, freeze.stderr

    package = subprocess.run(
        [
            sys.executable,
            "scripts/package_orion_slurm_job.py",
            str(frozen_path),
            str(slurm_path),
            "--account",
            "hep2023-1-3",
            "--partition",
            "hep",
            "--stdout",
            "logs/reference-%j.out",
            "--stderr",
            "logs/reference-%j.err",
            "--",
            "python",
            "run_reference.py",
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert package.returncode == 0, package.stderr
    assert frozen_path.is_file()
    assert slurm_path.is_file()
    assert "ORION_EXECUTION_PROTOCOL_FROZEN" in freeze.stdout
    assert "ORION_SLURM_PACKAGE_BOUND" in package.stdout


def _write_valid_result_bundle(directory: Path) -> dict:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    contract = manifest["result_bundle_contracts"]["V3_EXECUTOR_BUNDLE_V1"]
    for filename in contract["required_outputs"]:
        (directory / filename).write_text("{}\n")
    (directory / "INDEPENDENT_CHECKER_RECEIPT.json").write_text("{}\n")
    (directory / "RESULT_RECEIPT.json").write_text(
        json.dumps(
            {
                "job_id": "V3-DONOR-ENVELOPE-01",
                "base_git_sha": "5f4a83dceffbc783e0df946b22378524b123ec7e",
                "head_git_sha": "5f4a83dceffbc783e0df946b22378524b123ec7e",
                "task_count": 1,
                "inference_unit_count": 1,
                "donor_family": ["D1"],
                "ideal_donor_product": "D1",
                "matched_contracts": ["information", "tools", "resources"],
                "donor_conservativity_violations": [],
                "false_promotion_violations": [],
                "resource_violations_or_incomparabilities": [],
                "strict_frontier_witnesses": [],
                "held_out_status": "CANNOT_CHECK",
                "counterfactual_status": "CANNOT_CHECK",
                "prospective_status": "CANNOT_CHECK",
                "minimal_residual_family": [],
                "known_donor_absorption": [],
                "authority_ceiling": "INTERNAL_EXECUTION_ONLY",
                "nonclaims": ["no paper authority"],
                "paper_authority_delta": "NONE",
            },
            sort_keys=True,
        )
        + "\n"
    )
    return contract


def test_result_bundle_validator_hashes_one_complete_authority_route(tmp_path: Path) -> None:
    api = _takeover_api()
    contract = _write_valid_result_bundle(tmp_path)

    receipt = api.validate_result_bundle(tmp_path, contract)

    assert receipt["file_count"] == 9
    assert len(receipt["files"]["RESULT_RECEIPT.json"]["sha256"]) == 64


def test_result_bundle_validator_rejects_missing_or_double_authority(tmp_path: Path) -> None:
    api = _takeover_api()
    contract = _write_valid_result_bundle(tmp_path)
    (tmp_path / "SYSTEM_PROFILES.json").unlink()

    with pytest.raises(api.ManifestError, match="missing required result files"):
        api.validate_result_bundle(tmp_path, contract)

    (tmp_path / "SYSTEM_PROFILES.json").write_text("{}\n")
    (tmp_path / "EXTERNAL_AUTHORITY_BLOCKER.json").write_text("{}\n")
    with pytest.raises(api.ManifestError, match="exactly one authority route"):
        api.validate_result_bundle(tmp_path, contract)
