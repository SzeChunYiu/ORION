from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RENDER = ROOT / "scripts/render_md_tex.py"
REGEN = ROOT / "scripts/regen_paper_manifests.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_markdown_table_declares_only_rows_it_emits() -> None:
    render = _load(RENDER, "render_md_tex_test")
    output = render.render("| A | B |\n|---|---|\n| 1 | 2 |\n")
    assert "\\markdownRendererTable{}{2}{2}{dd}" in output
    assert "\\markdownRendererTable{}{3}{2}{dd}" not in output


def test_manifest_recovery_preserves_duplicate_bound_path_lines() -> None:
    regen = _load(REGEN, "regen_paper_manifests_test")
    raw = '''{
  "bound_files": [
    {
      "path": "tests/unit/candidates/test_p6_formal_refutation_capacity.py",
      "path": "papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier/P6_ETS_PROTOCOL_V1.md",
      "role": null
    }
  ],
  "subject_commit": "abc",
  "subject_commit_blocker": null,
  "subject_commit_status": "BOUND",
  "subject_commit_unbound_paths": []
}
'''
    parsed = regen.parse_tolerant(raw)
    assert parsed is not None
    first, _latest, recovered = parsed
    assert first["bound_files"][0]["path"].endswith("P6_ETS_PROTOCOL_V1.md")
    assert recovered == [
        "tests/unit/candidates/test_p6_formal_refutation_capacity.py",
        "papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier/P6_ETS_PROTOCOL_V1.md",
    ]
