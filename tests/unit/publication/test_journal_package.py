"""Journal packages: required files, hashes, bounded readiness, and P1 H1 history."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "research" / "paper-programme-v1" / "journal_package" / "check_journal_package.py"
sys.path.insert(0, str(CHECKER.parent))
from check_journal_package import (  # noqa: E402
    PAPER_DIRS,
    check_package,
    check_repository,
    current_claims,
    hashed_paths,
    load_manifest,
    write_sha256sums,
)

P5 = ROOT / PAPER_DIRS["P5"]
P1 = ROOT / PAPER_DIRS["P1"]


def test_all_five_packages_pass_on_committed_tree() -> None:
    reports = check_repository(ROOT)
    failed = [f"{report.paper_id}: {report.errors}" for report in reports if not report.ok]
    assert not failed
    assert {report.paper_id for report in reports} == {"P1", "P2", "P3", "P4", "P5"}


def test_p1_h1_remains_not_supported() -> None:
    manifest = load_manifest(ROOT / PAPER_DIRS["P1"] / "journal_package")
    h1 = next(claim for claim in manifest["claims"] if claim["id"] == "P1.H1")
    assert h1["status"] == "NOT_SUPPORTED"
    report = check_package("P1", ROOT / PAPER_DIRS["P1"], repo_root=ROOT)
    assert report.ok


def test_p1_current_claim_query_excludes_immutable_negative_history() -> None:
    manifest = load_manifest(ROOT / PAPER_DIRS["P1"] / "journal_package")
    active = current_claims(manifest)
    active_ids = {claim["id"] for claim in active}

    assert "P1.H1" not in active_ids
    assert "P1.NECESSITY.V2.2.4" in active_ids
    assert {
        claim["id"] for claim in active if claim["status"] == "OPEN"
    } == {"P1.CURRENT_PACKAGE"}
    assert not [claim for claim in active if claim["status"] in {"NOT_SUPPORTED", "CANNOT_CHECK"}]

    h1 = next(claim for claim in manifest["claims"] if claim["id"] == "P1.H1")
    assert h1["status"] == "NOT_SUPPORTED"
    assert h1["lifecycle"] == "HISTORICAL_IMMUTABLE"


def test_p1_narrow_successor_cannot_launder_historical_h1(tmp_path: Path) -> None:
    paper = tmp_path / "paper-01-recursive-epistemic-reconstruction"
    shutil.copytree(ROOT / PAPER_DIRS["P1"], paper, ignore=shutil.ignore_patterns("__pycache__"))
    manifest_path = paper / "journal_package" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    successor = next(
        claim for claim in manifest["claims"] if claim["id"] == "P1.NECESSITY.V2.2.4"
    )
    successor["relationship_to_previous"] = {
        "type": "SUPERSEDES",
        "claim_id": "P1.H1",
        "scientific_supersession": True,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    report = check_package("P1", paper)
    assert not report.ok
    assert any("narrower, not a scientific supersession" in error for error in report.errors)


def test_nonready_packages_flag_an_open_claim() -> None:
    for paper_id, relative in PAPER_DIRS.items():
        manifest = load_manifest(ROOT / relative / "journal_package")
        if manifest["package_status"] == "SUBMISSION_READY":
            continue
        pdf_claims = [claim for claim in manifest["claims"] if claim["status"] == "OPEN"]
        assert pdf_claims, f"{paper_id} must have at least one OPEN claim (PDF without artifact)"
        assert all(claim["artifacts"] == [] for claim in pdf_claims)


def test_pdf_presence_matches_the_three_package_states() -> None:
    for relative in PAPER_DIRS.values():
        manifest = load_manifest(ROOT / relative / "journal_package")
        pdfs = list((ROOT / relative / "journal_package").glob("*.pdf"))
        if manifest["package_status"] in {"SUPERSEDED", "SUBMISSION_READY"}:
            assert pdfs
            required = {entry["path"] for entry in manifest["required_files"]}
            assert all(f"journal_package/{pdf.name}" in required for pdf in pdfs)
        else:
            assert manifest["package_status"] == "SCAFFOLDING"
            assert pdfs == []


def test_p1_superseded_contract_is_internally_consistent() -> None:
    manifest = load_manifest(P1 / "journal_package")
    assert manifest["package_status"] == "SUPERSEDED"
    assert manifest["package_authority"]["current_submission_authorized"] is False
    assert any(
        claim["status"] == "OPEN" and claim.get("current_claim") is True
        for claim in manifest["claims"]
    )
    state = json.loads((P1 / "journal_package" / "RENDER_CLOSURE_STATE.json").read_text())
    assert state["state"] == "SUPERSEDED"
    assert check_package("P1", P1, repo_root=ROOT).ok


def test_does_not_fork_scientific_result_verification_schema() -> None:
    schema = json.loads(
        (ROOT / "research" / "paper-programme-v1" / "journal_package" / "SCHEMA_V1.json").read_text()
    )
    assert schema["$id"] == "orion.journal-package.v1"
    assert schema["$id"] != "ScientificResultVerification.v1"
    assert schema["properties"]["package_status"]["enum"] == [
        "SCAFFOLDING",
        "SUPERSEDED",
        "SUBMISSION_READY",
    ]
    for relative in PAPER_DIRS.values():
        manifest = load_manifest(ROOT / relative / "journal_package")
        block = manifest["scientific_result_verification"]
        assert block["owner_issue"] == 283
        assert block["schema_name"] == "ScientificResultVerification.v1"
        assert block["records_present"], f"{relative} must consume #283 records now on main"


def _copy_p5(tmp_path: Path) -> Path:
    target = tmp_path / "paper-05-self-orion"
    shutil.copytree(P5, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def _copy_p1(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    target = repo / PAPER_DIRS["P1"]
    target.parent.mkdir(parents=True)
    shutil.copytree(P1, target, ignore=shutil.ignore_patterns("__pycache__"))
    (repo / "research").symlink_to(ROOT / "research", target_is_directory=True)
    return target


def _write_manifest_and_hashes(paper: Path, manifest: dict) -> None:
    (paper / "journal_package" / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    write_sha256sums(paper, hashed_paths(manifest))


def test_superseded_package_requires_retained_pdf(tmp_path: Path) -> None:
    paper = _copy_p1(tmp_path)
    (paper / "journal_package" / "manuscript.pdf").unlink()
    report = check_package("P1", paper)
    assert not report.ok
    assert any("SUPERSEDED package has no retained PDF" in error for error in report.errors)


def test_superseded_package_requires_generator_state(tmp_path: Path) -> None:
    paper = _copy_p1(tmp_path)
    state_path = paper / "journal_package" / "RENDER_CLOSURE_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["state"] = "CURRENT"
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = load_manifest(paper / "journal_package")
    _write_manifest_and_hashes(paper, manifest)
    report = check_package("P1", paper)
    assert not report.ok
    assert any("render-closure state SUPERSEDED" in error for error in report.errors)


def test_superseded_package_denies_current_submission_authority(tmp_path: Path) -> None:
    paper = _copy_p1(tmp_path)
    manifest = load_manifest(paper / "journal_package")
    manifest["package_authority"]["current_submission_authorized"] = True
    _write_manifest_and_hashes(paper, manifest)
    report = check_package("P1", paper)
    assert not report.ok
    assert any("current_submission_authorized=false" in error for error in report.errors)


def test_superseded_package_requires_current_open_claim(tmp_path: Path) -> None:
    paper = _copy_p1(tmp_path)
    manifest = load_manifest(paper / "journal_package")
    manifest["claims"] = [
        claim for claim in manifest["claims"] if claim["id"] != "P1.CURRENT_PACKAGE"
    ]
    _write_manifest_and_hashes(paper, manifest)
    report = check_package("P1", paper)
    assert not report.ok
    assert any("current OPEN claim" in error for error in report.errors)


def test_scaffolding_still_forbids_retained_pdf(tmp_path: Path) -> None:
    paper = _copy_p1(tmp_path)
    manifest = load_manifest(paper / "journal_package")
    manifest["package_status"] = "SCAFFOLDING"
    _write_manifest_and_hashes(paper, manifest)
    report = check_package("P1", paper)
    assert not report.ok
    assert any("SCAFFOLDING package contains a PDF" in error for error in report.errors)


def test_missing_required_package_file_fails(tmp_path: Path) -> None:
    paper = _copy_p5(tmp_path)
    (paper / "journal_package" / "COMPILE.md").unlink()
    report = check_package("P5", paper)
    assert not report.ok
    assert any("COMPILE.md" in error for error in report.errors)


def test_missing_required_manifest_file_fails(tmp_path: Path) -> None:
    paper = _copy_p5(tmp_path)
    (paper / "manuscript" / "main.tex").unlink()
    report = check_package("P5", paper)
    assert not report.ok
    assert any("manuscript/main.tex" in error for error in report.errors)


def test_hash_mismatch_fails(tmp_path: Path) -> None:
    paper = _copy_p5(tmp_path)
    compile_path = paper / "journal_package" / "COMPILE.md"
    compile_path.write_text(compile_path.read_text(encoding="utf-8") + "\n# tamper\n", encoding="utf-8")
    report = check_package("P5", paper)
    assert not report.ok
    assert any("hash mismatch" in error for error in report.errors)


def test_claim_without_artifact_must_be_open(tmp_path: Path) -> None:
    paper = _copy_p5(tmp_path)
    manifest_path = paper / "journal_package" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["claims"].append(
        {
            "id": "P5.GHOST",
            "text": "a claim with no artifact",
            "artifacts": [],
            "status": "SUPPORTED",
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_sha256sums(paper, hashed_paths(manifest))
    report = check_package("P5", paper)
    assert not report.ok
    assert any("P5.GHOST" in error for error in report.errors)


def test_consumes_scientific_result_verification_when_present(tmp_path: Path) -> None:
    paper = _copy_p5(tmp_path)
    record = paper / "evidence" / "scientific_result_verification" / "p5-attr.json"
    record.parent.mkdir(parents=True)
    record.write_text(
        json.dumps({"schema_version": "ScientificResultVerification.v1", "claim_id": "P5.ATTR"}) + "\n",
        encoding="utf-8",
    )
    report = check_package("P5", paper)
    assert not report.ok
    assert any("records_present" in error for error in report.errors)

    manifest_path = paper / "journal_package" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scientific_result_verification"]["records_present"] = [
        "evidence/scientific_result_verification/p5-attr.json"
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_sha256sums(paper, hashed_paths(manifest))
    report = check_package("P5", paper)
    assert report.ok


def test_p1_h1_rewrite_to_supported_fails(tmp_path: Path) -> None:
    paper = tmp_path / "paper-01-recursive-epistemic-reconstruction"
    shutil.copytree(ROOT / PAPER_DIRS["P1"], paper, ignore=shutil.ignore_patterns("__pycache__"))
    manifest_path = paper / "journal_package" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for claim in manifest["claims"]:
        if claim["id"] == "P1.H1":
            claim["status"] = "SUPPORTED"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report = check_package("P1", paper)
    assert not report.ok
    assert any("NOT_SUPPORTED" in error for error in report.errors)
