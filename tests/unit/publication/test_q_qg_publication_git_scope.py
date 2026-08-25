from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "papers/check_q_qg_publication.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_q_qg_publication", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.stdout.strip()


def commit_file(repo: Path, rel: str, body: str, message: str) -> str:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    git(repo, "add", rel)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def new_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "local")
    git(repo, "config", "user.name", "CI Test")
    git(repo, "config", "user.email", "ci-test@example.invalid")
    return repo


def test_pr_diff_uses_merge_base_and_excludes_base_owned_science(tmp_path, monkeypatch):
    checker = load_checker()
    repo = new_repo(tmp_path)
    science_path = "research/extensions/orion-qg/inherited.py"
    original = commit_file(repo, science_path, "original\n", "original cut")
    base = commit_file(repo, science_path, "base-owned\n", "base science update")
    head = commit_file(repo, "papers/branch-owned.md", "publication\n", "branch update")
    git(repo, "update-ref", "refs/remotes/origin/main", base)
    git(repo, "update-ref", "refs/remotes/origin/topic", head)

    monkeypatch.setattr(checker, "ROOT", repo)
    monkeypatch.setattr(checker, "ORIGINAL_CUT", original)
    monkeypatch.setenv("GITHUB_BASE_REF", "main")
    monkeypatch.setenv("GITHUB_HEAD_REF", "topic")

    target, scope_base, changed = checker.changed_for_publication_branch()

    assert target == "origin/topic"
    assert scope_base == base
    assert changed == ["papers/branch-owned.md"]


def test_pr_diff_fails_closed_when_origin_base_ref_is_missing(tmp_path, monkeypatch):
    checker = load_checker()
    repo = new_repo(tmp_path)
    original = commit_file(repo, "README.md", "original\n", "original cut")
    git(repo, "update-ref", "refs/remotes/origin/topic", original)

    monkeypatch.setattr(checker, "ROOT", repo)
    monkeypatch.setattr(checker, "ORIGINAL_CUT", original)
    monkeypatch.setenv("GITHUB_BASE_REF", "missing-base")
    monkeypatch.setenv("GITHUB_HEAD_REF", "topic")

    with pytest.raises(subprocess.CalledProcessError):
        checker.changed_for_publication_branch()


@pytest.mark.parametrize("change", ["modify", "delete"])
def test_existing_authorized_q3_path_cannot_be_modified_or_deleted(tmp_path, monkeypatch, change):
    checker = load_checker()
    repo = new_repo(tmp_path)
    authorized = sorted(checker.Q3_AUTHORIZED_NEW_SCIENCE)[0]
    original = commit_file(repo, "README.md", "original\n", "original cut")
    base = commit_file(repo, authorized, "frozen result\n", "add authorized result")
    if change == "modify":
        head = commit_file(repo, authorized, "mutated result\n", "mutate authorized result")
    else:
        (repo / authorized).unlink()
        git(repo, "add", "-u", authorized)
        git(repo, "commit", "-m", "delete authorized result")
        head = git(repo, "rev-parse", "HEAD")

    monkeypatch.setattr(checker, "ROOT", repo)
    monkeypatch.setattr(checker, "ORIGINAL_CUT", original)

    errors, _present = checker.science_change_errors(base, head, [authorized])

    assert errors == [f"Q3_AUTHORIZED_EXISTING_PATH_MUTATED_OR_DELETED:{authorized}"]


def test_branch_owned_preexisting_science_change_is_not_whitelisted(tmp_path, monkeypatch):
    checker = load_checker()
    repo = new_repo(tmp_path)
    science_path = "research/extensions/orion-qg/inherited.py"
    original = commit_file(repo, science_path, "original\n", "original cut")
    base = commit_file(repo, "README.md", "base\n", "base update")
    head = commit_file(repo, science_path, "branch mutation\n", "branch science mutation")

    monkeypatch.setattr(checker, "ROOT", repo)
    monkeypatch.setattr(checker, "ORIGINAL_CUT", original)

    errors, _present = checker.science_change_errors(base, head, [science_path])

    assert errors == [
        f"PREEXISTING_OR_UNAUTHORIZED_SCIENCE_MUTATED_BY_PUBLICATION_BRANCH:{science_path}"
    ]
