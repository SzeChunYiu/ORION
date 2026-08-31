from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/mirror_orion_papers_13_24.py"
WORKFLOW = ROOT / ".github/workflows/orion-paper-mirror-13-24-20260831.yml"
EXTERNAL_RECEIPT = (
    ROOT
    / "papers/publication_closure/orion_13_24_final/EXTERNAL_MIRROR_RECEIPT.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("mirror_orion_13_24", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_mirror_preserves_declared_overlays(tmp_path: Path) -> None:
    module = _module()
    paper = module.PAPERS[0]
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    source = source_root / "papers" / paper
    destination = target_root / "v1-papers" / paper
    (source / "submission/final-20260831").mkdir(parents=True)
    (source / "submission/final-20260831/PACKAGE_MANIFEST.json").write_text("{}\n")
    (source / "paper.txt").write_text("current\n")
    destination.mkdir(parents=True)
    (destination / "paper.txt").write_text("stale\n")
    (destination / "PROVENANCE.md").write_text("target-owned\n")

    module.mirror_paper(source_root, target_root, paper, "a" * 40)

    assert (destination / "paper.txt").read_text() == "current\n"
    assert (destination / "PROVENANCE.md").read_text() == "target-owned\n"
    assert "Source commit: `" + "a" * 40 + "`" in (
        destination / "MIRROR_RECEIPT_2026-08-31.md"
    ).read_text()
    assert module.tree_map(source) == module.tree_map(destination)


def test_target_path_is_bounded(tmp_path: Path) -> None:
    module = _module()
    destination = module.safe_destination(tmp_path, module.PAPERS[-1])
    assert tmp_path.resolve() in destination.parents


def test_workflow_recognizes_only_a_verified_unchanged_external_mirror() -> None:
    workflow = WORKFLOW.read_text()
    receipt = json.loads(EXTERNAL_RECEIPT.read_text())

    assert "fetch-depth: 0" in workflow
    assert "poppler-utils" in workflow
    assert str(EXTERNAL_RECEIPT.relative_to(ROOT)) in workflow
    assert "git diff --quiet" in workflow
    assert "paper trees changed after the verified external receipt" in workflow
    assert workflow.count("if: steps.transport.outputs.mirror_required == 'true'") == 3
    assert receipt["source_commit"] == "0943c43e3d250a38cf2988115929dab60d1205d1"
    assert receipt["target_commit"] == "a5c9b7521f016efbb08894bb9982d4c30bacd94d"
    assert receipt["verification"]["non_overlay_mismatches"] == 0
    assert receipt["verification"]["stale_non_overlay_target_files"] == 0
