"""The freeze-state reader must reject mutants and agree with the frozen checker.

Two properties matter and both are asserted against the real repository:

1. at the freeze commit the reader and `check_all25_bounded_science_freeze_v3.py`
   agree -- the reader is not a second opinion, it is the same attestation read
   from a place the frozen checker cannot be run from;
2. after unrelated commits land the reader still answers, distinguishing a valid
   freeze with post-freeze drift from a malformed one. That distinction is the
   whole point: the frozen checker collapses both into `FREEZE_INVALID`.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
READER = ROOT / "scripts/read_all25_freeze_state_v1.py"
FROZEN_CHECKER = ROOT / "papers/check_all25_bounded_science_freeze_v3.py"


def _load():
    spec = importlib.util.spec_from_file_location("_freeze_state_v1", READER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def manifest(mod):
    if not (ROOT / mod.MANIFEST_REL).is_file():
        pytest.skip("the V3 freeze manifest is not present in this tree")
    return json.loads((ROOT / mod.MANIFEST_REL).read_text(encoding="utf-8"))


def test_reader_answers_at_head(mod, manifest):
    """Whatever has landed, the reader returns a verdict rather than failing."""
    assert mod.main(["--repo", str(ROOT)]) == 0


def test_freeze_commit_is_located_by_identity(mod, manifest):
    head = subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    freeze = mod.locate_freeze_commit(ROOT, head)
    # The located commit must be the one that adds the manifest, and its first
    # parent must be the content base the manifest itself declares.
    first_parent = subprocess.run(
        ["/usr/bin/git", "rev-parse", f"{freeze}^"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    assert first_parent == manifest["content_base_commit"]


def test_attestation_holds_at_the_freeze_commit(mod, manifest):
    head = subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    freeze = mod.locate_freeze_commit(ROOT, head)
    assert mod.check_attestation(ROOT, freeze, manifest) == []


def test_reader_and_frozen_checker_agree_at_the_freeze_commit(mod, manifest, tmp_path):
    """Control: the reader is not inventing a laxer verdict."""
    head = subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    freeze = mod.locate_freeze_commit(ROOT, head)

    work = tmp_path / "at-freeze"
    add = subprocess.run(
        ["/usr/bin/git", "worktree", "add", "--detach", str(work), freeze],
        cwd=ROOT, capture_output=True, text=True,
    )
    if add.returncode != 0:  # pragma: no cover
        pytest.skip(f"cannot create a worktree at the freeze commit: {add.stderr.strip()}")
    try:
        frozen = subprocess.run(
            ["python3", str(work / "papers/check_all25_bounded_science_freeze_v3.py")],
            cwd=work, capture_output=True, text=True,
        )
        reader = mod.main(["--repo", str(work), "--require-no-drift"])
        # At the freeze commit there is no drift, so both must pass.
        assert frozen.returncode == 0, frozen.stderr
        assert reader == 0
    finally:
        subprocess.run(
            ["/usr/bin/git", "worktree", "remove", "--force", str(work)],
            cwd=ROOT, capture_output=True, text=True,
        )


def test_broken_attestation_is_a_finding(mod, manifest, monkeypatch):
    mutant = copy.deepcopy(manifest)
    mutant["papers"][0]["final_tree_oid"] = "0" * 40
    monkeypatch.setattr(mod, "read_manifest", lambda repo, freeze: mutant)
    assert mod.main(["--repo", str(ROOT)]) == 2


def test_wrong_content_base_is_a_finding(mod, manifest, monkeypatch):
    mutant = copy.deepcopy(manifest)
    mutant["content_base_commit"] = "0" * 40
    monkeypatch.setattr(mod, "read_manifest", lambda repo, freeze: mutant)
    assert mod.main(["--repo", str(ROOT)]) == 2


def test_absent_freeze_is_cannot_check_not_a_finding(mod, monkeypatch):
    def _no_freeze(repo, head):
        raise mod.CannotCheck("no commit adds the manifest")

    monkeypatch.setattr(mod, "locate_freeze_commit", _no_freeze)
    assert mod.main(["--repo", str(ROOT)]) == 3


def test_ambiguous_history_is_cannot_check(mod, monkeypatch):
    real = mod._git

    def fake(repo, *args):
        if args and args[0] == "log":
            return "a" * 40 + "\n" + "b" * 40
        return real(repo, *args)

    monkeypatch.setattr(mod, "_git", fake)
    assert mod.main(["--repo", str(ROOT)]) == 3


def test_require_no_drift_turns_drift_into_a_failure(mod, manifest, monkeypatch):
    """Drift is information by default and a failure only when asked for."""
    monkeypatch.setattr(
        mod,
        "measure_drift",
        lambda repo, head, m: [
            {
                "paper_id": "ORION-99",
                "canonical_directory": "papers/orion-99",
                "frozen_tree_oid": "0" * 40,
                "head_tree_oid": "1" * 40,
                "state": "MOVED",
            }
        ],
    )
    assert mod.main(["--repo", str(ROOT)]) == 0
    assert mod.main(["--repo", str(ROOT), "--require-no-drift"]) == 2


def test_not_a_repository_is_cannot_check(mod, tmp_path):
    assert mod.main(["--repo", str(tmp_path)]) == 3
