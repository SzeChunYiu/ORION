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
DONOR_ENVELOPE_AUDIT = (
    ROOT / "research/orion-discovery-v3/V3_DONOR_ENVELOPE_01_SPECIFICATION_AUDIT_V1.json"
)


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


def test_donor_envelope_job_binds_exact_specification_gap_audit() -> None:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    job = manifest["jobs"][0]

    assert DONOR_ENVELOPE_AUDIT.exists()
    audit = json.loads(DONOR_ENVELOPE_AUDIT.read_text())
    atomic_map = json.loads(
        (ROOT / "research/orion-discovery-v3/ATOMIC_NOVELTY_AND_SUPERIORITY_MAP_V1.json").read_text()
    )

    assert audit["job_id"] == job["job_id"] == "V3-DONOR-ENVELOPE-01"
    assert audit["readiness"] == job["status"] == api.BLOCKED
    assert audit["remaining_blockers"] == job["blockers"]
    assert audit["observed_task_scope"]["atomic_map_count"] == len(atomic_map["atoms"])
    assert audit["runnable_on_lunarc"] is False
    assert audit["paper_authority_delta"] == "NONE"


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


def _scientific_protocol() -> dict:
    return {
        "schema": "orion.discovery.v3.execution-protocol.v1",
        "execution_class": "SCIENTIFIC_STUDY",
        "job_id": "V3-DONOR-ENVELOPE-01",
        "source_git_sha": "5f4a83dceffbc783e0df946b22378524b123ec7e",
        "authority_ceiling": "INTERNAL_SCIENTIFIC_EXECUTION_ONLY",
        "paper_authority_delta": "NONE",
        "inputs": {
            "runner_sha256": "a" * 64,
            "source_archive_sha256": "b" * 64,
            "input_bundle_sha256": "c" * 64,
            "task_manifest_sha256": "d" * 64,
            "task_ids": ["DONOR-ENVELOPE-TASK-01"],
            "candidate_artifact_sha256": "e" * 64,
            "evaluator_sha256": "f" * 64,
            "donor_registry_sha256": "1" * 64,
            "donor_family": [
                {
                    "donor_id": "D1",
                    "artifact_sha256": "2" * 64,
                    "interface_contract_sha256": "3" * 64,
                }
            ],
            "ideal_donor_product": {
                "product_id": "IDEAL-D1",
                "component_donor_ids": ["D1"],
                "composition_runner_sha256": "4" * 64,
                "interface_contract_sha256": "5" * 64,
            },
        },
        "resource_vector": {"nodes": 1, "cpus": 2, "memory_mb": 4096, "minutes": 10},
        "matched_contract": {
            "environment": "PINNED_PRIVATE_ENVIRONMENT",
            "information_contract_sha256": "6" * 64,
            "tool_contract_sha256": "7" * 64,
            "resource_contract_sha256": "8" * 64,
            "resource_dimensions": ["wall_seconds", "max_rss_mb"],
            "resource_order": "PARETO_COMPONENTWISE",
            "scalarization": "NONE",
            "price_vector": None,
            "same_candidate_visible_information": True,
            "same_tool_access": True,
            "donor_first_refusal": True,
            "frozen_before_outcomes": True,
            "outcomes_accessed": False,
        },
        "terminals": {
            "positive": "IDEAL_DONOR_ENVELOPES_CONSTRUCTED_FOR_FROZEN_TASK_CLASS",
            "adverse": [
                "DONOR_PRODUCT_SUFFICIENT",
                "NO_STRICT_FRONTIER_WIN",
                "CONSERVATIVITY_REGRESSION",
                "FALSE_PROMOTION_REGRESSION",
                "RESOURCE_INCOMPARABLE_OR_WORSE",
            ],
            "cannot_check": "CANNOT_CHECK",
        },
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


@pytest.mark.parametrize(
    "missing_input",
    [
        "source_archive_sha256",
        "input_bundle_sha256",
        "task_manifest_sha256",
        "candidate_artifact_sha256",
        "evaluator_sha256",
        "donor_registry_sha256",
    ],
)
def test_scientific_protocol_requires_content_bound_inputs(missing_input: str) -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()
    del protocol["inputs"][missing_input]

    with pytest.raises(api.ManifestError, match=missing_input):
        api.freeze_protocol(protocol)


def test_scientific_protocol_rejects_taxonomy_only_donors() -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()
    protocol["inputs"]["donor_family"] = ["information retrieval"]

    with pytest.raises(api.ManifestError, match="donor_family"):
        api.freeze_protocol(protocol)


def test_scientific_protocol_requires_ideal_product_to_cover_exact_donor_family() -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()
    protocol["inputs"]["ideal_donor_product"]["component_donor_ids"] = ["D2"]

    with pytest.raises(api.ManifestError, match="component_donor_ids"):
        api.freeze_protocol(protocol)


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("matched_contract", "same_tool_access"), False, "same_tool_access"),
        (("matched_contract", "resource_dimensions"), [], "resource_dimensions"),
        (("matched_contract", "scalarization"), "IMPLICIT_WEIGHTED_SUM", "scalarization"),
        (("terminals", "adverse"), [], "adverse"),
        (("terminals", "cannot_check"), "", "cannot_check"),
    ],
)
def test_scientific_protocol_requires_matched_contracts_and_terminal_routes(
    path: tuple[str, str], value: object, message: str
) -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()
    protocol[path[0]][path[1]] = value

    with pytest.raises(api.ManifestError, match=message):
        api.freeze_protocol(protocol)


def test_scientific_protocol_rejects_unbound_price_vector() -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()
    protocol["matched_contract"].update(
        {
            "scalarization": "FROZEN_PRICE_VECTOR",
            "price_vector": {"wall_seconds": 1, "max_rss_mb": 2},
            "price_vector_sha256": "0" * 64,
        }
    )

    with pytest.raises(api.ManifestError, match="price_vector_sha256 mismatch"):
        api.freeze_protocol(protocol)


def test_protocol_freeze_rejects_stale_source_against_expected_identity() -> None:
    api = _takeover_api()

    with pytest.raises(api.ManifestError, match="stale source Git SHA"):
        api.freeze_protocol(_scientific_protocol(), expected_source_git_sha="0" * 40)


def test_complete_scientific_protocol_freezes_and_revalidates() -> None:
    api = _takeover_api()
    protocol = _scientific_protocol()

    frozen = api.freeze_protocol(
        protocol,
        expected_source_git_sha=protocol["source_git_sha"],
    )

    api.validate_frozen_protocol(frozen)
    assert frozen["execution_class"] == "SCIENTIFIC_STUDY"
    assert frozen["state"] == "FROZEN"


def test_scientific_freeze_cli_requires_live_source_identity(tmp_path: Path) -> None:
    protocol_path = tmp_path / "scientific-draft.json"
    frozen_path = tmp_path / "scientific-frozen.json"
    protocol = _scientific_protocol()
    protocol_path.write_text(json.dumps(protocol))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")

    missing_identity = subprocess.run(
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
    assert missing_identity.returncode != 0
    assert "--expected-source-git-sha" in missing_identity.stderr

    frozen = subprocess.run(
        [
            sys.executable,
            "scripts/freeze_orion_execution_job.py",
            str(protocol_path),
            str(frozen_path),
            "--expected-source-git-sha",
            protocol["source_git_sha"],
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert frozen.returncode == 0, frozen.stderr
    assert "ORION_EXECUTION_PROTOCOL_FROZEN" in frozen.stdout


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
