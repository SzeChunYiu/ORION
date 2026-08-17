import json
import subprocess

import pytest

from orion.self_orion.subject_binding import (
    attest_repository_subject,
    is_derived_from_commit,
    write_repository_subject_attestation,
)


def _git(root, *args):
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def _repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.name", "ORION Test")
    _git(root, "config", "user.email", "orion@example.test")
    _git(root, "remote", "add", "origin", "git@github.com:SzeChunYiu/ORION.git")
    (root / "alpha.txt").write_text("alpha\n")
    (root / "nested").mkdir()
    (root / "nested" / "beta.txt").write_text("beta\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root


def test_repository_subject_attestation_binds_clean_commit_tree_and_every_blob(tmp_path):
    root = _repo(tmp_path)
    attestation = attest_repository_subject(root)

    assert attestation.repository_identity == "github.com/SzeChunYiu/ORION"
    assert attestation.commit_oid == _git(root, "rev-parse", "HEAD")
    assert attestation.tree_oid == _git(root, "rev-parse", "HEAD^{tree}")
    assert len(attestation.tracked_objects) == 2
    assert tuple(item.path for item in attestation.tracked_objects) == (
        "alpha.txt",
        "nested/beta.txt",
    )
    assert len(attestation.source_tree_sha256) == 64
    assert len(attestation.subject_revision_hash) == 64

    path = tmp_path / "subject.json"
    write_repository_subject_attestation(attestation, path)
    raw = json.loads(path.read_text())
    assert raw["subject_revision_hash"] == attestation.subject_revision_hash
    assert raw["source_tree_sha256"] == attestation.source_tree_sha256
    assert raw["tracked_object_count"] == 2


def test_subject_attestation_rejects_dirty_or_untracked_execution_subject(tmp_path):
    root = _repo(tmp_path)
    (root / "alpha.txt").write_text("modified\n")
    with pytest.raises(RuntimeError, match="dirty or untracked"):
        attest_repository_subject(root)

    _git(root, "checkout", "--", "alpha.txt")
    (root / "untracked.txt").write_text("not in HEAD\n")
    with pytest.raises(RuntimeError, match="dirty or untracked"):
        attest_repository_subject(root)


def test_new_committed_content_changes_sha256_subject_identity(tmp_path):
    root = _repo(tmp_path)
    before = attest_repository_subject(root)
    (root / "alpha.txt").write_text("alpha changed\n")
    _git(root, "add", "alpha.txt")
    _git(root, "commit", "-m", "change content")
    after = attest_repository_subject(root)

    assert before.commit_oid != after.commit_oid
    assert before.tree_oid != after.tree_oid
    assert before.source_tree_sha256 != after.source_tree_sha256
    assert before.subject_revision_hash != after.subject_revision_hash


def test_repository_identity_is_part_of_subject_identity(tmp_path):
    root = _repo(tmp_path)
    canonical = attest_repository_subject(root)
    mirror = attest_repository_subject(root, repository_identity="mirror.example/ORION")
    assert canonical.source_tree_sha256 == mirror.source_tree_sha256
    assert canonical.subject_revision_hash != mirror.subject_revision_hash


def test_derivation_predicate_answers_ancestry_in_both_directions(tmp_path):
    root = _repo(tmp_path)
    anchor = _git(root, "rev-parse", "HEAD")
    (root / "gamma.txt").write_text("gamma\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "later")
    later = _git(root, "rev-parse", "HEAD")

    assert is_derived_from_commit(root, anchor, later) is True
    assert is_derived_from_commit(root, anchor, anchor) is True
    assert is_derived_from_commit(root, later, anchor) is False


def test_derivation_predicate_refuses_unknown_commits(tmp_path):
    root = _repo(tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    with pytest.raises(RuntimeError):
        is_derived_from_commit(root, "0" * 40, head)
    with pytest.raises(RuntimeError):
        is_derived_from_commit(root, head, "0" * 40)
    with pytest.raises(ValueError):
        is_derived_from_commit(root, "", head)


def test_derivation_predicate_refuses_to_answer_false_in_a_shallow_clone(tmp_path):
    """A truncated history can hide a path, so "not derived" is unsound there.

    A shallow clone otherwise returns a confident wrong answer: the connecting
    commits are simply absent, which is indistinguishable from their never
    having existed. Refusing is the only honest result.
    """

    root = _repo(tmp_path)
    for index in range(4):
        (root / f"file{index}.txt").write_text(f"{index}\n")
        _git(root, "add", ".")
        _git(root, "commit", "-m", f"commit {index}")
    origin_head = _git(root, "rev-parse", "HEAD")

    shallow = tmp_path / "shallow"
    _git(tmp_path, "clone", "--depth", "1", f"file://{root}", str(shallow))
    shallow_head = _git(shallow, "rev-parse", "HEAD")
    assert _git(shallow, "rev-parse", "--is-shallow-repository") == "true"
    assert shallow_head == origin_head

    # Reachable-and-connected still answers True.
    assert is_derived_from_commit(shallow, shallow_head, shallow_head) is True

    # An object that exists but whose path is cut must refuse, not answer False.
    unreachable = _git(root, "rev-list", "--max-parents=0", "HEAD")
    _git(shallow, "fetch", "--depth", "1", f"file://{root}", unreachable)
    with pytest.raises(RuntimeError, match="shallow"):
        is_derived_from_commit(shallow, unreachable, shallow_head)
