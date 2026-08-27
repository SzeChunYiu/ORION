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
            "run": 33049783681,
            "artifact_id": 9637176781,
            "artifact_name": "fiberguard-r20-bnsl-adaptive",
            "artifact_zip_sha256": (
                "c5f2d5b5e93596ab82c03a2bd75cd441c74e6ac08b0265b281c3be7a516ab186"
            ),
            "member": "TERMINAL.txt",
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


def test_missing_optional_donor_is_explicitly_cannot_reverify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    destination = tmp_path / "donor.txt"
    destination.write_text("historical donor\n", encoding="utf-8")
    blob = subprocess.check_output(
        ["git", "hash-object", str(destination)], text=True
    ).strip()
    entry = {
        "destination": "donor.txt",
        "bytes": destination.stat().st_size,
        "sha256": convergence.sha256(destination),
        "source": {
            "kind": "git",
            "commit": "f" * 40,
            "path": "historical/donor.txt",
            "blob": blob,
            "object_required_in_checkout": False,
            "object_absence_disposition": (
                "CANNOT_REVERIFY_COMMIT_PATH__DESTINATION_BLOB_ONLY"
            ),
        },
    }
    monkeypatch.setattr(convergence, "git_object_exists", lambda *_args: False)

    validate_entry(tmp_path, entry, require_donor_objects=False)
    assert "CANNOT_REVERIFY_COMMIT_PATH__DESTINATION_BLOB_ONLY" in capsys.readouterr().out

    with pytest.raises(AssertionError, match="required donor commit/path unavailable"):
        validate_entry(tmp_path, entry, require_donor_objects=True)


def test_vendored_bnsl_actions_archive_is_verified_offline() -> None:
    custody_path = (
        ROOT
        / "papers/orion-02-fiberguard-finite-fibre/extensions/r20/"
        "BNSL_R20_ACTION_ARTIFACT_CUSTODY_V1.json"
    )
    assert custody_path.is_file(), "BNSL Actions artifact custody record absent"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    convergence.validate_action_artifact_archive(ROOT, custody)


def test_bnsl_actions_archive_rejects_fabricated_identity_and_tampering(
    tmp_path: Path,
) -> None:
    custody_path = (
        ROOT
        / "papers/orion-02-fiberguard-finite-fibre/extensions/r20/"
        "BNSL_R20_ACTION_ARTIFACT_CUSTODY_V1.json"
    )
    original = json.loads(custody_path.read_text(encoding="utf-8"))
    fabricated = json.loads(json.dumps(original))
    fabricated["github_actions"]["artifact_id"] += 1
    with pytest.raises(AssertionError, match="artifact custody identity"):
        convergence.validate_action_artifact_archive(ROOT, fabricated)

    source = ROOT / original["archive"]["path"]
    tampered_path = tmp_path / "tampered.zip"
    payload = bytearray(source.read_bytes())
    payload[-1] ^= 1
    tampered_path.write_bytes(payload)
    tampered = json.loads(json.dumps(original))
    tampered["archive"]["path"] = str(tampered_path)
    with pytest.raises(AssertionError, match="artifact archive SHA"):
        convergence.validate_action_artifact_archive(ROOT, tampered)


def test_vendored_r18_actions_archive_is_verified_offline() -> None:
    custody_path = (
        ROOT
        / "papers/orion-02-fiberguard-finite-fibre/extensions/r18/"
        "R18_ACTION_ARTIFACT_ARCHIVE_CUSTODY_V1.json"
    )
    assert custody_path.is_file(), "R18 Actions artifact custody record absent"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    convergence.validate_r18_action_artifact_archive(ROOT, custody)


def test_r18_actions_archive_rejects_fabricated_identity_and_tampering(
    tmp_path: Path,
) -> None:
    custody_path = (
        ROOT
        / "papers/orion-02-fiberguard-finite-fibre/extensions/r18/"
        "R18_ACTION_ARTIFACT_ARCHIVE_CUSTODY_V1.json"
    )
    original = json.loads(custody_path.read_text(encoding="utf-8"))
    fabricated = json.loads(json.dumps(original))
    fabricated["api_snapshot"]["artifact_id"] += 1
    with pytest.raises(AssertionError, match="Actions provenance"):
        convergence.validate_r18_action_artifact_archive(ROOT, fabricated)

    source = ROOT / original["archive"]["path"]
    tampered_path = tmp_path / "tampered-r18.zip"
    payload = bytearray(source.read_bytes())
    payload[-1] ^= 1
    tampered_path.write_bytes(payload)
    tampered = json.loads(json.dumps(original))
    tampered["archive"]["path"] = str(tampered_path)
    with pytest.raises(AssertionError, match="archive SHA"):
        convergence.validate_r18_action_artifact_archive(ROOT, tampered)


def test_publication_gate_and_venue_ladder_are_canonical_orion_id_artifacts() -> None:
    gate_path = HERE / "PUBLICATION_GATE_V1.json"
    ladder_path = HERE / "PROVISIONAL_VENUE_LADDER_V1.md"
    assert gate_path.is_file()
    assert ladder_path.is_file()
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    assert set(gate["papers"]) == {f"ORION-{i:02d}" for i in range(1, 6)}
    for paper in gate["papers"].values():
        assert paper["science_status"] == "OPEN"
        assert paper["top_tier_submission_ready"] is False
        assert paper["specialist_submission_ready"] is False
        assert paper["submission_authorized"] is False
    ladder = ladder_path.read_text(encoding="utf-8")
    for paper_id in gate["papers"]:
        assert paper_id in ladder
    assert "Recheck official venue criteria" in ladder


def test_stack_artifact_dispositions_cover_every_frozen_pr_file() -> None:
    ledger = json.loads(
        (HERE / "STACK_ARTIFACT_DISPOSITIONS_V1.json").read_text(encoding="utf-8")
    )
    expected_counts = {
        1471: 11,
        1475: 5,
        1485: 7,
        1488: 11,
        1489: 11,
        1492: 54,
        1503: 3,
        1506: 3,
        1534: 4,
    }
    assert ledger["source_pr_file_counts"] == {
        str(number): count for number, count in expected_counts.items()
    }
    rows = ledger["files"]
    observed = {}
    for row in rows:
        key = (row["source_pr"], row["source_path"])
        assert key not in observed
        observed[key] = row
        assert row["disposition"] in {
            "BYTE_MATERIALIZED_CANONICAL_DONOR",
            "SEMANTICALLY_REPLACED_BY_CANONICAL_STATUS_OR_POLICY",
            "HISTORICAL_ONLY_NOT_CANONICALIZED",
            "FAILED_OR_SUPERSEDED_WORKFLOW_HISTORICAL_ONLY",
            "CONSUMED_AUTHORIZATION_WITH_FAILURE_CUSTODY_PRESERVED",
        }
    for number, count in expected_counts.items():
        assert sum(row["source_pr"] == number for row in rows) == count


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


def test_cli_rejects_event_base_that_differs_from_manifest_baseline() -> None:
    verifier = HERE / "verify_convergence_v1.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(verifier),
            "--repo",
            str(ROOT),
            "--check-diff",
            "--event-base",
            "HEAD",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "event base commit mismatch" in completed.stderr


def test_workflow_supplies_exact_pr_base_but_uses_manifest_baseline_on_push() -> None:
    workflow = (ROOT / ".github/workflows/orion-01-05-convergence-v1.yml").read_text(
        encoding="utf-8"
    )
    assert "github.event.pull_request.base.sha" in workflow
    assert "fetch-depth: 0" in workflow
    assert 'if [ "$GITHUB_EVENT_NAME" = "pull_request" ]' in workflow
    assert '--event-base "$PR_BASE_SHA"' in workflow
    assert "--require-donor-objects" in workflow
    assert "github.event.before" not in workflow


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
    assert closures == {1471, 1475, 1485, 1488, 1489, 1492, 1503, 1506, 1534}
    assert {1449, 1466, 1469, 1472, 1524}.isdisjoint(closures)
    assert "unabsorbed_manuscript_package_and_policy_pull_requests" not in plan[
        "keep_open_after_convergence"
    ]
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


def test_orion04_keeps_proved_core_separate_from_failed_replay_authority() -> None:
    status = json.loads((HERE / "SCIENCE_STATUS_V1.json").read_text(encoding="utf-8"))
    nq = status["papers"]["ORION-04"]
    assert any("width-one corridor" in claim for claim in nq["established_scope"])
    assert any(
        "support-through-22" in claim and "bounded computational evidence" in claim
        for claim in nq["established_scope"]
    )
    assert any(
        "exact D_4" in claim and "remain open" in claim
        for claim in nq["established_scope"]
    )
    source = nq["established_scope_source"]
    assert source["path"] == (
        "papers/orion-04-rooted-completion-certificates/CLAIM_LEDGER_R2.md"
    )
    assert nq["authority"]["d2_d3_numerical_authority_established"] is False
    assert nq["authority"]["independent_replay_authority_state"] == "CANNOT_CHECK"


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


def test_science_status_and_candidate_authority_are_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = convergence.load
    status_path = HERE / "SCIENCE_STATUS_V1.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["papers"]["ORION-01"]["science_status"] = "CLOSED"

    def load_closed(path: Path):
        if path.resolve() == status_path.resolve():
            return status
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_closed)
    with pytest.raises(AssertionError, match="ORION-01 science status"):
        validate_science(ROOT)

    status = json.loads(status_path.read_text(encoding="utf-8"))
    candidate = status["papers"]["ORION-05"]["evidence_status"][
        "pending_candidates"
    ][0]
    candidate["current_main_authority"] = True

    def load_promoted_candidate(path: Path):
        if path.resolve() == status_path.resolve():
            return status
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_promoted_candidate)
    with pytest.raises(AssertionError, match="ORION-05 candidate identity drift"):
        validate_science(ROOT)


def test_controlling_adverse_record_cannot_be_omitted_from_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = convergence.load
    status_path = HERE / "SCIENCE_STATUS_V1.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    derived = status["papers"]["ORION-02"]["evidence_status"][
        "convergence_summary"
    ]["derived_from"]
    derived.remove("ORION02_R18_RETRACTION")

    def load_missing_adverse(path: Path):
        if path.resolve() == status_path.resolve():
            return status
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_missing_adverse)
    with pytest.raises(AssertionError, match="summary omits or invents"):
        validate_science(ROOT)


def test_unexecuted_r30_rust_checker_cannot_be_promoted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = convergence.load
    custody_path = HERE / "R30_FAILURE_CUSTODY_V1.json"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    custody["unmaterialized_cross_language_claim"]["live_run_census"][
        "success"
    ] = 1

    def load_promoted_rust(path: Path):
        if path.resolve() == custody_path.resolve():
            return custody
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_promoted_rust)
    with pytest.raises(AssertionError, match="R30 Rust checker execution promoted"):
        validate_science(ROOT)


def test_r30_failure_cause_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_load = convergence.load
    runs_path = HERE / "R30_FAILURE_RUNS_V1.json"
    runs = json.loads(runs_path.read_text(encoding="utf-8"))
    runs["r30_runs"][0]["cause"] = "FABRICATED_PASS_CAUSE"

    def load_corrupted_runs(path: Path):
        if path.resolve() == runs_path.resolve():
            return runs
        return original_load(path)

    monkeypatch.setattr(convergence, "load", load_corrupted_runs)
    with pytest.raises(AssertionError, match="R30 failure receipt drift"):
        validate_science(ROOT)
