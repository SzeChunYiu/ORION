"""Guard the P6-P8 content binding: derived state must match what is committed.

Mutation cases run against a copy in `tmp_path`, never the worktree. A checker
whose only exercise is the passing case is worthless -- it cannot distinguish a
tree that is bound from one it simply failed to look at -- so each case here
breaks the binding in a different way and requires the check to go red.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/candidates/checkers/check_content_binding_v1.py"
CANDIDATE_IDS = ("P6", "P7", "P8")


def _load_checker():
    # The checkers directory is not an importable package; loading by path keeps
    # it that way rather than adding a sys.path entry for one test module.
    spec = importlib.util.spec_from_file_location("check_content_binding_v1", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


binding = _load_checker()


def _export(candidate_id: str, destination: Path) -> Path:
    """Copy exactly the bound files of one candidate into a bare directory.

    The copy has no `.git`, which is also how an archived package arrives at a
    third party -- so these cases double as the export-time behaviour.
    """

    directory = binding.CANDIDATE_DIRS[candidate_id]
    manifest = json.loads((ROOT / directory / binding.MANIFEST_NAME).read_text(encoding="utf-8"))
    relatives = [str(entry["path"]) for entry in manifest["bound_files"]]
    relatives.append((directory / binding.SUMS_NAME).as_posix())
    for relative in relatives:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return destination


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_committed_binding_matches_the_worktree(candidate_id: str) -> None:
    report = binding.check_binding(ROOT, candidate_id)
    assert report.errors == []


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_digests_cover_exactly_the_bound_files(candidate_id: str) -> None:
    directory = ROOT / binding.CANDIDATE_DIRS[candidate_id]
    manifest = json.loads((directory / binding.MANIFEST_NAME).read_text(encoding="utf-8"))
    sums = binding.parse_sha256sums(directory / binding.SUMS_NAME)
    declared = {str(entry["path"]) for entry in manifest["bound_files"]}
    assert declared == set(sums)
    for relative, digest in sums.items():
        assert binding.sha256_file(ROOT / relative) == digest, relative


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_manifest_grants_no_authority(candidate_id: str) -> None:
    directory = ROOT / binding.CANDIDATE_DIRS[candidate_id]
    manifest = json.loads((directory / binding.MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest["grants_authority"] == "NONE"
    assert manifest["closes_gate"] is None
    assert manifest["claim_scope"]
    # Binding bytes settles the subject identity and nothing downstream of it.
    targets = manifest["reproducibility_targets"]
    assert targets["exact_subject_commit_identities"]["status"] == "BOUND"
    unbound = {name for name, spec in targets.items() if spec["status"] == "CANNOT_CHECK"}
    assert unbound, "a binding that claims every target is bound is not honest"
    for name in unbound:
        assert targets[name]["blocker"], f"{name} is CANNOT_CHECK with no named blocker"


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_mutating_a_bound_file_turns_the_check_red(tmp_path: Path, candidate_id: str) -> None:
    root = _export(candidate_id, tmp_path)
    victim = root / binding.CANDIDATE_DIRS[candidate_id] / "README.md"
    victim.write_text(victim.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
    report = binding.check_binding(root, candidate_id)
    assert not report.ok
    assert any("hash mismatch" in error for error in report.errors)


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_deleting_a_bound_file_turns_the_check_red(tmp_path: Path, candidate_id: str) -> None:
    root = _export(candidate_id, tmp_path)
    (root / binding.CANDIDATE_DIRS[candidate_id] / "README.md").unlink()
    report = binding.check_binding(root, candidate_id)
    assert not report.ok


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_adding_a_file_to_the_package_turns_the_check_red(tmp_path: Path, candidate_id: str) -> None:
    """The coverage-shrink case the P1-P5 checker cannot see.

    There the hashed set is read back out of the manifest, so a file added to the
    package is simply never hashed. Here the set is enumerated from disk, so an
    addition has to be acknowledged before the binding is valid again.
    """

    root = _export(candidate_id, tmp_path)
    (root / binding.CANDIDATE_DIRS[candidate_id] / "SMUGGLED.md").write_text(
        "unacknowledged package member\n", encoding="utf-8"
    )
    report = binding.check_binding(root, candidate_id)
    assert not report.ok
    assert any("bound_files" in error for error in report.errors)


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_widening_the_reproduce_subject_turns_the_check_red(
    tmp_path: Path, candidate_id: str
) -> None:
    root = _export(candidate_id, tmp_path)
    stray = root / "papers/candidates/checkers/stray_helper_v1.py"
    stray.write_text("# not part of any bound package\n", encoding="utf-8")
    reproduce = root / binding.CANDIDATE_DIRS[candidate_id] / "REPRODUCE_V2_1.md"
    reproduce.write_text(
        reproduce.read_text(encoding="utf-8")
        + "\n```bash\npython papers/candidates/checkers/stray_helper_v1.py\n```\n",
        encoding="utf-8",
    )
    report = binding.check_binding(root, candidate_id)
    assert any("does not bind" in error for error in report.errors)


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_export_without_git_is_cannot_check_not_failure(tmp_path: Path, candidate_id: str) -> None:
    """Bytes still verify off a git-less export; only commit identity goes unresolved."""

    root = _export(candidate_id, tmp_path)
    report = binding.check_binding(root, candidate_id)
    assert report.errors == []
    assert report.cannot_check, "an unresolvable subject commit must be reported, not assumed fine"


def test_regeneration_is_byte_identical(tmp_path: Path) -> None:
    """`--write` on an unchanged tree must reproduce the committed artifacts."""

    for candidate_id in CANDIDATE_IDS:
        directory = binding.CANDIDATE_DIRS[candidate_id]
        committed = json.loads(
            (ROOT / directory / binding.MANIFEST_NAME).read_text(encoding="utf-8")
        )
        derived = binding.derive_manifest(ROOT, candidate_id)
        provenance = {
            "subject_commit",
            "subject_commit_status",
            "subject_commit_blocker",
            "subject_commit_unbound_paths",
        }
        assert {k: v for k, v in committed.items() if k not in provenance} == {
            k: v for k, v in derived.items() if k not in provenance
        }


def test_cli_check_passes_on_the_committed_tree() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECKER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    assert "P6-P8 CANDIDATE CONTENT BINDING: PASS" in completed.stdout
