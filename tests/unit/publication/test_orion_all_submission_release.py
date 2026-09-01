from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import re
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[3]
BUILDER = (
    ROOT
    / "papers/publication_closure/orion_all_submission_20260831/build_all_submission_materials.py"
)
MIRROR = ROOT / "scripts/mirror_orion_papers_all.py"
RENDER_RECONCILER = ROOT / "scripts/reconcile_ci_manuscript_renders.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
SUPERSEDED_PACKAGES = (
    ROOT / "papers/orion-01-certificate-realization/journal_package_A_final",
    ROOT / "papers/orion-01-certificate-realization/journal_package_B_final",
    ROOT / "papers/orion-02-fiberguard-finite-fibre/journal_package_final",
    ROOT / "papers/orion-03-typed-merge-falsification/journal_package_final",
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_incremental_build_preserves_exact_25_paper_registry(tmp_path: Path) -> None:
    module = load_module(BUILDER, "orion_all_submission_builder")
    records = [{"paper": item["paper"], "value": "old"} for item in module.SPECS]
    registry = tmp_path / "CLOSURE_REGISTRY.json"
    registry.write_text(json.dumps({"papers": records}), encoding="utf-8")

    merged = module.merge_incremental_records(
        registry, [{"paper": "ORION-17", "value": "new"}]
    )

    assert len(merged) == 25
    assert [record["paper"] for record in merged] == [
        item["paper"] for item in module.SPECS
    ]
    assert next(record for record in merged if record["paper"] == "ORION-17") == {
        "paper": "ORION-17",
        "value": "new",
    }


def test_expanded_mirror_has_exact_25_paper_coverage(tmp_path: Path) -> None:
    module = load_module(MIRROR, "mirror_orion_papers_all")
    assert len(module.PAPERS) == 25
    assert len(set(module.PAPERS)) == 25

    paper = module.PAPERS[16]
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source = source_root / "papers" / paper
    package = source / "submission/publication-ready-20260831"
    package.mkdir(parents=True)
    (package / "PACKAGE_MANIFEST.json").write_text("{}\n", encoding="utf-8")
    (source / "paper.txt").write_text("current\n", encoding="utf-8")

    destination = target_root / "v1-papers" / paper
    destination.mkdir(parents=True)
    (destination / "paper.txt").write_text("stale\n", encoding="utf-8")
    (destination / "PROVENANCE.md").write_text("target-owned\n", encoding="utf-8")

    module.mirror_paper(source_root, target_root, paper, "a" * 40)

    assert module.tree_map(source) == module.tree_map(
        destination, exclude_overlays=True
    )
    assert (destination / "PROVENANCE.md").read_text(encoding="utf-8") == (
        "target-owned\n"
    )
    assert f"Source commit: `{'a' * 40}`" in (
        destination / "MIRROR_RECEIPT_2026-08-31.md"
    ).read_text(encoding="utf-8")


def test_mirror_checksum_verification_cannot_pass_with_missing_papers(
    tmp_path: Path,
) -> None:
    module = load_module(MIRROR, "mirror_orion_papers_all_checksum_coverage")
    paper = module.PAPERS[0]
    package = (
        tmp_path
        / "v1-papers"
        / paper
        / "submission/publication-ready-20260831"
    )
    package.mkdir(parents=True)
    payload = package / "payload.txt"
    payload.write_text("current\n", encoding="utf-8")
    (package / "SHA256SUMS").write_text(
        f"{hashlib.sha256(payload.read_bytes()).hexdigest()}  payload.txt\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="checksum file missing"):
        module.verify_mirrored_package_checksums(tmp_path)

    module.PAPERS = (paper,)
    module.verify_mirrored_package_checksums(tmp_path)
    payload.write_text("drift\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        module.verify_mirrored_package_checksums(tmp_path)


def test_ci_render_reconciliation_can_target_one_v1_paper(tmp_path: Path) -> None:
    module = load_module(RENDER_RECONCILER, "targeted_ci_render_reconciliation")
    slug = "orion-23-responsibility-carrying-state"
    paper = tmp_path / "papers" / slug
    pdf = paper / "manuscript/main.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"new pinned render")
    relative = f"papers/{slug}/manuscript/main.pdf"
    old_digest = hashlib.sha256(b"old render").hexdigest()
    (paper / "SHA256SUMS").write_text(
        f"{old_digest}  {relative}\n", encoding="utf-8"
    )

    module.ROOT = tmp_path
    module.RENDERS = {slug: (hashlib.sha256(pdf.read_bytes()).hexdigest(), 1)}
    module.V1_BINDINGS = {"P13": slug}
    module.PRIOR_PDF_DIGESTS = {slug: old_digest}
    module.prepare_digest_subject({slug})

    assert (paper / "SHA256SUMS").read_text(encoding="utf-8") == (
        f"{hashlib.sha256(pdf.read_bytes()).hexdigest()}  {relative}\n"
    )


def test_fast_ci_installs_publication_pdf_tooling() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "poppler-utils" in workflow


def test_full_build_report_is_bound_to_each_current_manifest(tmp_path: Path) -> None:
    module = load_module(MIRROR, "mirror_orion_papers_all_report_binding")
    closure = tmp_path / "papers/publication_closure/orion_all_submission_20260831"
    closure.mkdir(parents=True)
    builder = closure / "build_all_submission_materials.py"
    verifier = closure / "verify_all_submission_materials.py"
    builder.write_text("# builder\n", encoding="utf-8")
    verifier.write_text("# verifier\n", encoding="utf-8")

    papers = []
    for number in range(1, 26):
        paper_id = f"ORION-{number:02d}"
        package = tmp_path / "papers" / paper_id / "submission/publication-ready-20260831"
        package.mkdir(parents=True)
        manifest = package / "PACKAGE_MANIFEST.json"
        manifest.write_text(json.dumps({"paper": paper_id}) + "\n", encoding="utf-8")
        papers.append(
            {
                "paper": paper_id,
                "package": package.relative_to(tmp_path).as_posix(),
                "status": "PASS",
                "checks": ["clean_arxiv_build", "clean_journal_build"],
                "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            }
        )
    report = {
        "aggregate": "PASS",
        "papers": papers,
        "builder_sha256": hashlib.sha256(builder.read_bytes()).hexdigest(),
        "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest(),
    }
    (closure / "VERIFICATION_REPORT.json").write_text(
        json.dumps(report), encoding="utf-8"
    )
    module.verify_full_report(tmp_path)

    first = tmp_path / papers[0]["package"] / "PACKAGE_MANIFEST.json"
    first.write_text('{"paper":"ORION-01","changed":true}\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="full clean-build report is stale for ORION-01"):
        module.verify_full_report(tmp_path)


def test_superseded_packages_retain_pre_existing_binding_drift() -> None:
    for package in SUPERSEDED_PACKAGES:
        receipt = json.loads(
            (package / "SUPERSEDED_RECONCILIATION_V1.json").read_text()
        )
        assert "retained_payload_edited" not in receipt
        assert receipt["payload_edited_by_this_reconciliation"] is False
        assert receipt["pre_existing_payload_binding_drift_detected"] is True
        assert receipt["pre_existing_payload_binding_drift_count"] > 0

        record_path = package / receipt["historical_binding_drift_record"]
        record = json.loads(record_path.read_text())
        assert record["current_submission_authorized"] is False
        assert record["scientific_authority_delta"] == "NONE"
        assert record["historical_checksum_payload_drift"]
        assert "NOT_A_CURRENT_SUBMISSION_SURFACE" in record["disposition"]
        assert not any(
            row["path"].startswith("papers/")
            for row in record["historical_internal_binding_claim_drift"]
        )

        sums = (package / "SHA256SUMS").read_text().splitlines()
        inventory = dict(line.split("  ", 1)[::-1] for line in sums)
        assert inventory[record_path.name] == hashlib.sha256(
            record_path.read_bytes()
        ).hexdigest()


def test_orion01_current_routes_have_one_back_matter_copy() -> None:
    paper = ROOT / "papers/orion-01-certificate-realization"
    current = paper / "submission/publication-ready-20260831"
    for route in ("arxiv", "journal"):
        with zipfile.ZipFile(current / route / "source.zip") as archive:
            source = archive.read("main.tex").decode("utf-8")
        assert len(re.findall(r"\\section\*?\{References\}", source)) == 1
        assert len(
            re.findall(r"\\section\*?\{Data and code availability\}", source)
        ) == 1

    for component in ("journal_package_A_final", "journal_package_B_final"):
        record = json.loads(
            (paper / component / "HISTORICAL_BINDING_DRIFT_V1.json").read_text()
        )
        assert record["legacy_manuscript_back_matter_counts"] == {
            "data_and_code_availability": 2,
            "references": 2,
        }
        assert record["successor_source_back_matter_counts"] == {
            "arxiv": {"data_and_code_availability": 1, "references": 1},
            "journal": {"data_and_code_availability": 1, "references": 1},
        }
