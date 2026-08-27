from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path
import subprocess
import sys

import pytest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import verify_convergence_v1 as convergence  # noqa: E402
from verify_convergence_v1 import (  # noqa: E402
    json_pointer,
    validate_changed_paths,
    validate_entry,
    validate_manifest,
    validate_science,
    verify,
)


def test_exact_terminal_json_pointer_is_fail_closed() -> None:
    document = {"top": {"terminal": "PASS"}, "rows": [{"terminal": "NULL"}]}
    assert json_pointer(document, "/top/terminal") == "PASS"
    assert json_pointer(document, "/rows/0/terminal") == "NULL"
    with pytest.raises(AssertionError, match="key absent"):
        json_pointer(document, "/top/missing")


def test_complete_convergence_subject() -> None:
    verify(ROOT, check_diff=False)


def test_changed_path_policy_rejects_destructive_and_extra_paths() -> None:
    with pytest.raises(AssertionError, match="destructive"):
        validate_changed_paths([("D", "papers/README.md")], {"papers/README.md"})
    with pytest.raises(AssertionError, match="mismatch"):
        validate_changed_paths(
            [("A", "research/orion-01-05-convergence-v1/extra.txt")],
            {"research/orion-01-05-convergence-v1/expected.txt"},
        )
    with pytest.raises(AssertionError, match="outside strict"):
        validate_changed_paths([("A", "src/extra.py")], {"src/extra.py"})


def test_changed_path_policy_allows_only_readme_modification_plus_additions() -> None:
    records = [("M", "papers/README.md"), ("A", "research/orion-01-05-convergence-v1/new.json")]
    validate_changed_paths(records, {path for _, path in records})


def test_changed_path_policy_allows_additive_canonical_evidence_for_all_five_papers() -> None:
    records = [
        (
            "A",
            f"papers/orion-{index:02d}-{slug}/evidence/convergence-v1/result.json",
        )
        for index, slug in (
            (1, "certificate-realization"),
            (3, "typed-merge-falsification"),
            (4, "rooted-completion-certificates"),
            (5, "tare-expressivity"),
        )
    ]
    validate_changed_paths(records, {path for _, path in records})


def test_github_artifact_source_requires_exact_member_binding(tmp_path: Path) -> None:
    destination = tmp_path / "result.json"
    destination.write_text("{}\n", encoding="utf-8")
    entry = {
        "destination": "result.json",
        "bytes": destination.stat().st_size,
        "sha256": "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
        "source": {
            "kind": "github_actions_artifact",
            "run": 1,
            "artifact_id": 2,
            "artifact_name": "evidence",
            "artifact_zip_sha256": "0" * 64,
        },
    }
    with pytest.raises(AssertionError, match="artifact member binding absent"):
        validate_entry(tmp_path, entry)


def test_github_artifact_member_mapping_must_be_unique(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = json.loads(
        (HERE / "DONOR_MANIFEST_V1.json").read_text(encoding="utf-8")
    )
    artifacts = [
        row for row in manifest["files"]
        if row["source"]["kind"] == "github_actions_artifact"
    ]
    assert len(artifacts) == 2
    artifacts[1]["source"]["member"] = artifacts[0]["source"]["member"]
    monkeypatch.setattr(convergence, "load", lambda _path: manifest)
    with pytest.raises(AssertionError, match="duplicate artifact member mapping"):
        validate_manifest(ROOT)


def test_r18_runner_imports_under_declared_replay_environment() -> None:
    r18 = ROOT / "papers/orion-02-fiberguard-finite-fibre/extensions/r18"
    completed = subprocess.run(
        [sys.executable, "fiberguard_paired_route_r18.py", "--help"],
        cwd=r18,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_r18_replay_dependency_lock_and_data_free_preflight() -> None:
    r18 = ROOT / "papers/orion-02-fiberguard-finite-fibre/extensions/r18"
    lock = r18 / "R18_REPLAY_REQUIREMENTS_LOCK.txt"
    assert lock.is_file(), "R18 replay dependency lock is absent"
    assert lock.read_text(encoding="utf-8").splitlines() == [
        "numpy==2.1.3",
        "scikit-learn==1.5.2",
        "PyYAML==6.0.2",
    ]
    preflight = r18 / "verify_r18_replay_prerequisites.py"
    assert preflight.is_file(), "R18 data-free replay preflight is absent"
    completed = subprocess.run(
        [sys.executable, preflight.name],
        cwd=r18,
        text=True,
        capture_output=True,
        check=False,
    )
    observed = {
        name: version(name) for name in ("numpy", "scikit-learn", "PyYAML")
    }
    exact_environment = sys.version_info[:2] == (3, 12) and observed == {
        "numpy": "2.1.3",
        "scikit-learn": "1.5.2",
        "PyYAML": "6.0.2",
    }
    if not exact_environment:
        assert completed.returncode != 0
        assert "R18 replay requires Python 3.12.x" in completed.stderr or (
            "R18 replay dependency drift" in completed.stderr
        )
        return
    assert completed.returncode == 0, completed.stderr
    assert (
        "R18_REPLAY_CODE_PREFLIGHT_PASS__PINNED_ASLIB_CORPUS_NOT_VENDORED"
        in completed.stdout
    )


def test_cli_rejects_pr_base_whose_tree_differs_from_manifest_baseline() -> None:
    verifier = HERE / "verify_convergence_v1.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(verifier),
            "--repo",
            str(ROOT),
            "--check-diff",
            "--pr-base",
            "HEAD",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "PR base tree mismatch" in completed.stderr


def test_workflow_supplies_the_actual_pull_request_base() -> None:
    workflow = (ROOT / ".github/workflows/orion-01-05-convergence-v1.yml").read_text(
        encoding="utf-8"
    )
    assert "github.event.pull_request.base.sha" in workflow
    assert '--pr-base "$PR_BASE_SHA"' in workflow


def test_manifest_requires_every_expected_path_to_have_a_source_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = json.loads(
        (HERE / "DONOR_MANIFEST_V1.json").read_text(encoding="utf-8")
    )
    manifest["files"].pop()
    monkeypatch.setattr(convergence, "load", lambda _path: manifest)
    with pytest.raises(AssertionError, match="manifest destination coverage mismatch"):
        validate_manifest(ROOT)


def test_manifest_self_binding_and_baseline_tree_are_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = json.loads(
        (HERE / "DONOR_MANIFEST_V1.json").read_text(encoding="utf-8")
    )
    manifest["manifest_self_binding"]["path"] = "research/wrong.json"
    monkeypatch.setattr(convergence, "load", lambda _path: manifest)
    with pytest.raises(AssertionError, match="manifest self-binding path"):
        validate_manifest(ROOT)

    manifest = json.loads(
        (HERE / "DONOR_MANIFEST_V1.json").read_text(encoding="utf-8")
    )
    manifest["baseline"]["tree"] = "0" * 40
    monkeypatch.setattr(convergence, "load", lambda _path: manifest)
    with pytest.raises(AssertionError, match="baseline tree mismatch"):
        validate_manifest(ROOT)


def test_conflicting_d_wrapper_does_not_erase_raw_theorem() -> None:
    status = json.loads((HERE / "SCIENCE_STATUS_V1.json").read_text(encoding="utf-8"))
    d = status["papers"]["ORION-03"]
    records = {
        record["value"]: record
        for record in d["evidence_status"]["preserved_records"]
    }
    assert "TYPED_AUTHORITY_FIRST_MIXING_R12_PASS" in records
    assert records["D_PR1466_THEOREM_AUTHORITY_NOT_ESTABLISHED"]["disposition"] == (
        "PRESERVED_NONCONTROLLING_KNOWN_PREDICATE_DEFECT"
    )
    assert d["authority"]["bounded_internal_first_mixing_theorem"] is True
    assert d["authority"]["external_domain_validation_established"] is False


def test_supersession_is_conditional_and_never_erases_adverse_results() -> None:
    plan = json.loads((HERE / "SUPERSESSION_PLAN_V1.json").read_text(encoding="utf-8"))
    assert plan["global_rule"] == (
        "CLOSE_ONLY_AFTER_SUCCESSOR_MERGE_AND_MERGED_MAIN_VERIFICATION"
    )
    closures = set(plan["after_convergence_merge"]["close_pull_requests"])
    assert {1471, 1475, 1485, 1488, 1489, 1492, 1503, 1506, 1534} <= closures
    assert {1449, 1466, 1469, 1472, 1524}.isdisjoint(closures)
    assert "adverse, null, harmful, timeout, and CANNOT_CHECK outcomes" in plan[
        "never_superseded"
    ]
    assert plan["protected_task3_touched"] is False


def test_science_status_uses_exact_donor_terminals_and_preserves_fiberguard_history() -> None:
    status = json.loads((HERE / "SCIENCE_STATUS_V1.json").read_text(encoding="utf-8"))
    for paper_id in ("ORION-01", "ORION-03", "ORION-05"):
        paper = status["papers"][paper_id]
        assert "preserved_status_terminal" not in paper
        evidence = paper["evidence_status"]
        summary = evidence["convergence_summary"]
        assert summary["label"].startswith(f"{paper_id}_")
        assert summary["kind"] == "CONVERGENCE_GENERATED_SUMMARY"
        assert summary["is_exact_donor_terminal"] is False
        assert evidence["preserved_records"]
        for record in evidence["preserved_records"]:
            assert record["value"]
            assert record["record_kind"] in {
                "RAW_SCIENCE_TERMINAL",
                "AUDIT_DISPOSITION",
                "AUTHORITY_VERDICT",
                "COMPOSITE_INTERPRETATION",
            }
            assert set(record["source"]) >= {"commit", "path", "blob"}

    fiberguard = status["papers"]["ORION-02"]["evidence_status"][
        "preserved_records"
    ]
    terminals = {record["value"] for record in fiberguard}
    assert {
        "FIBERGUARD_ASLIB_SAT12_ALL_PASS",
        "FIBERGUARD_ASLIB_HELDOUT_R14_PARTIAL_MEAN_ONLY",
        "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_TWO_OF_THREE",
        "FIBERGUARD_R16_NO_PORTABLE_CERTIFICATE_VALUE",
        "FIBERGUARD_FALLBACK_ALIGNMENT_R17_PASS",
        "FIBERGUARD_RELATIVE_ROUTE_EXTENSION_R18_PASS",
        "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE",
        "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS",
    } <= terminals


def test_known_d_audit_false_negative_is_preserved_but_not_controlling() -> None:
    path = HERE / "AUDIT_DISPOSITIONS_V1.json"
    assert path.is_file(), "known audit conflict ledger is absent"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    record = ledger["known_conflicts"][0]
    assert record["paper"] == "ORION-03"
    assert record["audit_terminal"] == "D_PR1466_THEOREM_AUTHORITY_NOT_ESTABLISHED"
    assert record["disposition"] == "KNOWN_PREDICATE_FALSE_NEGATIVE"
    assert record["raw_science_terminal"] == "TYPED_AUTHORITY_FIRST_MIXING_R12_PASS"
    assert record["controls"]["exhaustive_hybrid_atoms"] == 12
    assert record["controls"]["random_hybrid_atoms"] == 56
    assert record["controls"]["total_hybrid_atoms"] == 68


def test_authority_summary_does_not_erase_donor_cannot_check_states() -> None:
    status = json.loads((HERE / "SCIENCE_STATUS_V1.json").read_text(encoding="utf-8"))
    assert "external_independence" not in status["global_authority"]
    assert status["global_authority"]["external_independence_established"] is False
    for paper in status["papers"].values():
        authority = paper["authority"]
        assert "external_independence" not in authority
        assert "novelty" not in authority
        assert authority["external_independence_established"] is False
        assert authority["novelty_authority_established"] is False

    ab_records = status["papers"]["ORION-01"]["evidence_status"][
        "preserved_records"
    ]
    raw = next(row for row in ab_records if row["value"] == "AB_REGISTRY_NONIDENTIFIABILITY_R12_PASS")
    assert raw["donor_authority"]["external_independence"] == "CANNOT_CHECK"
    assert raw["donor_authority"]["novelty"] == "CANNOT_CHECK"


def test_typed_evidence_pointer_value_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = convergence.load
    status_path = HERE / "SCIENCE_STATUS_V1.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["papers"]["ORION-01"]["evidence_status"]["preserved_records"][0][
        "value"
    ] = "CORRUPTED_TERMINAL"

    def load_with_corrupted_status(path: Path):
        if path.resolve() == status_path.resolve():
            return status
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_with_corrupted_status)
    with pytest.raises(AssertionError, match="evidence record pointer mismatch"):
        validate_science(ROOT)
