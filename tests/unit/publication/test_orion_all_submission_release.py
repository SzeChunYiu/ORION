from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BUILDER = (
    ROOT
    / "papers/publication_closure/orion_all_submission_20260831/build_all_submission_materials.py"
)
MIRROR = ROOT / "scripts/mirror_orion_papers_all.py"


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
