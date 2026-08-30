"""Hostile tests for evidence-derived P6-P8 reproducibility-target states."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/candidates/checkers/check_reproducibility_targets_v2.py"
V1_CHECKER = ROOT / "papers/candidates/checkers/check_content_binding_v1.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_reproducibility_targets_v2", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = _load_checker()


def _copy_subject(tmp_path: Path, candidate_id: str) -> Path:
    destination = tmp_path / "repo"
    source_paper = ROOT / checker.PAPERS[candidate_id]
    target_paper = destination / checker.PAPERS[candidate_id]
    target_paper.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_paper, target_paper)
    records = ROOT / "research/verification/records"
    shutil.copytree(records, destination / "research/verification/records")
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copy2(ROOT / name, destination / name)
    return destination


@pytest.mark.parametrize(
    ("candidate_id", "expected_counts"),
    [
        ("P6", {"BOUND": 8, "CANNOT_CHECK": 1, "DEFERRED": 1}),
        ("P7", {"BOUND": 8, "CANNOT_CHECK": 1, "DEFERRED": 1}),
        # P8's exact_subject_commit_identities moved PARTIAL -> BOUND when the
        # rewrite-master adoption re-pinned subject_commit and subject_tree as a
        # consistent pair; the previous pin recorded a tree that disagreed with
        # its commit. protected_labels_custody_and_attack_replay stays PARTIAL.
        ("P8", {"BOUND": 7, "PARTIAL": 1, "CANNOT_CHECK": 1, "DEFERRED": 1}),
    ],
)
def test_current_tree_is_classified_target_by_target(
    candidate_id: str, expected_counts: dict[str, int]
) -> None:
    report = checker.derive_report(ROOT, candidate_id)
    counts = {key: value for key, value in report["state_counts"].items() if value}
    assert counts == expected_counts
    for target in report["reproducibility_targets"].values():
        assert target["status"] in checker.ALLOWED_STATES
        if target["status"] in {"PARTIAL", "CANNOT_CHECK", "DEFERRED"}:
            assert target["blocker"]


def test_subject_identity_uses_the_content_bound_v2_successor() -> None:
    target = checker.assess_targets(ROOT, "P6")["exact_subject_commit_identities"]
    assert target.status == "BOUND"
    assert target.blocker is None
    assert any(path.endswith("CONTENT_MANIFEST_V2.json") for path in target.evidence)


def test_latest_replay_contract_is_the_authoritative_result_binding() -> None:
    """A V4 successor must be assessed instead of the retained V3 predecessor."""

    target = checker.assess_targets(ROOT, "P6")["immutable_raw_result_formats"]

    assert target.status == "BOUND"
    assert any(path.endswith("P6_LOCAL_REPLAY_CONTRACT_V4.json") for path in target.evidence)


def test_invalid_latest_contract_cannot_fall_back_to_a_valid_predecessor(
    tmp_path: Path,
) -> None:
    """Retaining V3 history must not let a malformed V4 silently disappear."""

    root = _copy_subject(tmp_path, "P6")
    contract_path = (
        root
        / checker.PAPERS["P6"]
        / "evidence/local/P6_LOCAL_REPLAY_CONTRACT_V4.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["schema_version"] = "orion.local-replay-contract.v999"
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    target = checker.assess_targets(root, "P6")["immutable_raw_result_formats"]

    assert target.status == "PARTIAL"
    assert any(path.endswith("P6_LOCAL_REPLAY_CONTRACT_V4.json") for path in target.evidence)


def test_subject_identity_falls_back_to_v1_only_when_v2_is_absent(tmp_path: Path) -> None:
    root = _copy_subject(tmp_path, "P6")
    (root / checker.PAPERS["P6"] / "CONTENT_MANIFEST_V2.json").unlink()
    target = checker.assess_targets(root, "P6")["exact_subject_commit_identities"]
    assert any(path.endswith("CONTENT_MANIFEST_V1.json") for path in target.evidence)
    assert not any(path.endswith("CONTENT_MANIFEST_V2.json") for path in target.evidence)


def test_v2_subject_identity_rejects_a_moving_environment_lock(tmp_path: Path) -> None:
    root = _copy_subject(tmp_path, "P6")
    (root / "uv.lock").write_text("lock drift\n", encoding="utf-8")
    target = checker.assess_targets(root, "P6")["exact_subject_commit_identities"]
    assert target.status == "PARTIAL"
    assert "environment lock drifted" in str(target.blocker)


def test_schema_without_generator_cannot_promote_the_combined_target(tmp_path: Path) -> None:
    root = _copy_subject(tmp_path, "P7")
    benchmark = root / checker.PAPERS["P7"] / "benchmark"
    (benchmark / "instances_v2.schema.json").unlink()
    (benchmark / "generate_instances_v2.py").unlink()
    target = checker.assess_targets(root, "P7")["versioned_protocol_generator_schemas"]
    assert target.status == "CANNOT_CHECK"

    benchmark = root / checker.PAPERS["P7"] / "benchmark"
    (benchmark / "instances_v2.schema.json").write_text("{}\n", encoding="utf-8")
    target = checker.assess_targets(root, "P7")["versioned_protocol_generator_schemas"]
    assert target.status == "CANNOT_CHECK", "an empty JSON object is not a schema"

    (benchmark / "instances_v2.schema.json").write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["case_id"],
                "properties": {"case_id": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )
    target = checker.assess_targets(root, "P7")["versioned_protocol_generator_schemas"]
    assert target.status == "PARTIAL"
    assert "dataset generator" in str(target.blocker)

    (benchmark / "generate_instances_v2.py").write_text(
        "# prospectively frozen\n", encoding="utf-8"
    )
    target = checker.assess_targets(root, "P7")["versioned_protocol_generator_schemas"]
    assert target.status == "PARTIAL", "a comment-only generator cannot discharge the target"

    (benchmark / "generate_instances_v2.py").write_text(
        """\
SCHEMA = "instances_v2.schema.json"
OUTPUT = "instances_v2.jsonl"

def main():
    return (SCHEMA, OUTPUT)

if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )
    target = checker.assess_targets(root, "P7")["versioned_protocol_generator_schemas"]
    assert target.status == "BOUND"


def test_deleting_machine_results_downgrades_only_evidence_they_support(tmp_path: Path) -> None:
    root = _copy_subject(tmp_path, "P6")
    mechanized = root / checker.PAPERS["P6"] / "formal/mechanized"
    for path in mechanized.glob("*.json"):
        path.unlink()

    targets = checker.assess_targets(root, "P6")
    assert targets["immutable_raw_result_formats"].status == "CANNOT_CHECK"
    assert targets["proof_and_checker_reproducibility"].status == "PARTIAL"
    assert "machine-readable checker result" in str(
        targets["proof_and_checker_reproducibility"].blocker
    )
    assert targets["negative_null_history_retained"].status == "BOUND"


def test_root_lock_does_not_claim_clean_reproduction_until_paper_selects_it(
    tmp_path: Path,
) -> None:
    root = _copy_subject(tmp_path, "P8")
    (root / checker.PAPERS["P8"] / "REPRODUCE_V3.md").unlink()
    target = checker.assess_targets(root, "P8")[
        "clean_environment_reproduction_instructions"
    ]
    assert target.status == "CANNOT_CHECK"
    assert (root / "uv.lock").is_file()

    reproduce = root / checker.PAPERS["P8"] / "REPRODUCE_V2_1.md"
    reproduce.write_text(
        reproduce.read_text(encoding="utf-8")
        + "\nUse `uv.lock`: `uv sync --frozen --extra proofs`.\n",
        encoding="utf-8",
    )
    targets = checker.assess_targets(root, "P8")
    assert targets["clean_environment_reproduction_instructions"].status == "BOUND"
    assert targets["dependency_model_provider_tool_versions"].status == "BOUND"


def test_self_authored_or_malformed_attestation_cannot_pass(tmp_path: Path) -> None:
    root = _copy_subject(tmp_path, "P8")
    record = root / "research/verification/records/P8.fake.json"
    record.write_text(
        json.dumps(
            {
                "schema_version": "invented",
                "paper_id": "P8",
                "verification_state": "BOUNDED_VERIFIED",
                "self_authorizing": True,
            }
        ),
        encoding="utf-8",
    )
    target = checker.assess_targets(root, "P8")["independent_replay_attestation"]
    assert target.status == "PARTIAL"

    record.write_text(
        json.dumps(
            {
                "schema_version": "orion.scientific-result-verification.v1",
                "paper_id": "P8",
                "verification_state": "BOUNDED_VERIFIED",
                "self_authorizing": False,
            }
        ),
        encoding="utf-8",
    )
    target = checker.assess_targets(root, "P8")["independent_replay_attestation"]
    assert target.status == "PARTIAL", "four self-declared fields are not an attestation"

    artifact = root / "evidence/result.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{"result": "PASS"}\n', encoding="utf-8")
    record.write_text(
        json.dumps(
            {
                "schema_version": "orion.scientific-result-verification.v1",
                "paper_id": "P8",
                "verification_state": "BOUNDED_VERIFIED",
                "self_authorizing": False,
                "subject": {"commit": "a" * 40, "tree": "b" * 40},
                "raw_artifacts": [
                    {
                        "path": "evidence/result.json",
                        "sha256": checker._sha256_file(artifact),
                    }
                ],
                "scorers": {"independent_from_written_spec": True},
            }
        ),
        encoding="utf-8",
    )
    target = checker.assess_targets(root, "P8")["independent_replay_attestation"]
    assert target.status == "BOUND"


def test_archive_absence_is_lifecycle_deferred_not_cannot_check() -> None:
    for candidate_id in checker.PAPERS:
        target = checker.assess_targets(ROOT, candidate_id)[
            "permanent_archive_after_authority_stabilizes"
        ]
        assert target.status == "DEFERRED"
        assert "post-authority" in str(target.blocker)


def test_v1_frozen_manifests_and_digests_remain_valid() -> None:
    completed = subprocess.run(
        [sys.executable, str(V1_CHECKER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr


def test_cli_json_is_deterministic_and_fail_closed() -> None:
    command = [sys.executable, str(CHECKER), "--root", str(ROOT), "--candidate", "P6"]
    first = subprocess.run(command + ["--json"], capture_output=True, text=True, timeout=120)
    second = subprocess.run(command + ["--json"], capture_output=True, text=True, timeout=120)
    assert first.returncode == 0, first.stderr
    assert first.stdout == second.stdout
    assert json.loads(first.stdout)[0]["schema_version"] == checker.SCHEMA_VERSION

    gated = subprocess.run(
        command + ["--fail-on-unresolved"], capture_output=True, text=True, timeout=120
    )
    assert gated.returncode == 3
