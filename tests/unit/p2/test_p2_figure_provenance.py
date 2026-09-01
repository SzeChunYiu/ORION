"""P2's figure-2 `--check` could not fail, and a real drift survived behind it.

The previous implementation wrote the tex, the PDF and the manifest, and *then* asserted
that those freshly written files existed. It destroyed the evidence of drift before looking
for it. Two drifts had accumulated behind it on `main`:

* `P2-2_manifest.json` recorded `source_hash` `ded21f74…` for `OFFLINE_MECHANISMS_V1.json`,
  which actually hashes to `43da57bb…` -- a version no longer in the tree;
* the committed PDF's decompressed content streams differed from a fresh render of the
  committed data, under the same matplotlib version, so it was not a metadata artifact.

The committed `.tex` matched exactly, which is what makes this a stale-artifact defect
rather than a wrong figure.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
SCRIPT = PAPER / "scripts" / "render_figure_p2_2.py"
FIGURES = PAPER / "manuscript" / "figures"
MANIFEST = FIGURES / "P2-2_manifest.json"
MECHANISMS = PAPER / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json"

pytest.importorskip("matplotlib", reason="the figure check renders a PDF")


def _module():
    spec = importlib.util.spec_from_file_location("render_figure_p2_2", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_committed_figure_matches_the_committed_data() -> None:
    """The no-alarm case, and the state this branch restores."""

    verdict = _module().main(["--check"])
    if verdict == 3:
        pytest.skip("committed figure uses a different Matplotlib version")
    assert verdict == 0


def test_check_writes_nothing() -> None:
    """The property whose absence hid the drift.

    A check that regenerates the artifact it is checking cannot report that the artifact
    was wrong.
    """

    before = {p: p.read_bytes() for p in sorted(FIGURES.iterdir()) if p.is_file()}
    _module().main(["--check"])
    after = {p: p.read_bytes() for p in sorted(FIGURES.iterdir()) if p.is_file()}
    assert before == after


def test_the_manifest_records_the_source_it_was_built_from() -> None:
    """The drift itself, asserted directly rather than only through the checker."""

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = manifest["source_hash"][MECHANISMS.name]
    actual = hashlib.sha256(MECHANISMS.read_bytes()).hexdigest()
    assert recorded == actual, (
        "the figure manifest names a version of the mechanisms data that is not in the tree"
    )


def test_a_stale_source_hash_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative control: the exact defect that survived must now fail the check."""

    scratch = tmp_path / "figures"
    shutil.copytree(FIGURES, scratch)
    module = _module()
    monkeypatch.setattr(module, "MANIFEST_OUTPUT", scratch / MANIFEST.name)
    monkeypatch.setattr(module, "TEX_OUTPUT", scratch / "P2-2_recall_vs_queries.tex")
    monkeypatch.setattr(module, "FIGURE_OUTPUT", scratch / "P2-2_recall_vs_queries.pdf")

    manifest = json.loads((scratch / MANIFEST.name).read_text(encoding="utf-8"))
    manifest["source_hash"][MECHANISMS.name] = "0" * 64
    (scratch / MANIFEST.name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    assert module.main(["--check"]) == 1


def test_an_absent_artifact_is_not_a_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Absent is reported separately from different, and neither is a pass."""

    module = _module()
    monkeypatch.setattr(module, "MANIFEST_OUTPUT", tmp_path / "gone.json")
    monkeypatch.setattr(module, "TEX_OUTPUT", tmp_path / "gone.tex")
    monkeypatch.setattr(module, "FIGURE_OUTPUT", tmp_path / "gone.pdf")
    assert module.main(["--check"]) == 2


def _scratch_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    scratch = tmp_path / "figures"
    shutil.copytree(FIGURES, scratch)
    module = _module()
    monkeypatch.setattr(module, "MANIFEST_OUTPUT", scratch / MANIFEST.name)
    monkeypatch.setattr(module, "TEX_OUTPUT", scratch / "P2-2_recall_vs_queries.tex")
    monkeypatch.setattr(module, "FIGURE_OUTPUT", scratch / "P2-2_recall_vs_queries.pdf")
    return module, scratch


def _set_manifest(scratch: Path, **changes) -> None:
    path = scratch / MANIFEST.name
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update(changes)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def test_a_different_renderer_is_cannot_check_not_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Matplotlib changes its output between minor versions.

    `uv.lock` pins 3.11.1 while this figure was rendered by 3.10.8, so CI runs a different
    renderer than the manifest records. Reporting DRIFT there would be a false alarm on a
    clean tree -- and a checker that cries wolf on its first real run gets switched off.
    Reporting a pass would be worse.
    """

    module, scratch = _scratch_module(tmp_path, monkeypatch)
    _set_manifest(scratch, matplotlib_version="0.0.0-not-a-real-version")
    assert module.main(["--check"]) == 3


def test_a_real_drift_outranks_an_incomparable_renderer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An access limitation must never mask a defect that is already established.

    If the source hash is stale, that is known to be wrong regardless of which renderer is
    installed, so the result is DRIFT and not CANNOT_CHECK.
    """

    module, scratch = _scratch_module(tmp_path, monkeypatch)
    manifest = json.loads((scratch / MANIFEST.name).read_text(encoding="utf-8"))
    manifest["matplotlib_version"] = "0.0.0-not-a-real-version"
    manifest["source_hash"][MECHANISMS.name] = "0" * 64
    (scratch / MANIFEST.name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assert module.main(["--check"]) == 1


def test_the_manifest_records_the_renderer_that_produced_the_figure() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest.get("matplotlib_version"), (
        "without the renderer version the figure comparison cannot tell a real drift "
        "from a version difference"
    )
