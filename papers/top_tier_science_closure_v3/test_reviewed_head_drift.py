#!/usr/bin/env python3
"""Adversarial synthetic-history tests for check_reviewed_head_drift.py."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "check_reviewed_head_drift.py"
SPEC = importlib.util.spec_from_file_location("reviewed_head_drift", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to import drift checker from {MODULE_PATH}")
DRIFT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DRIFT
SPEC.loader.exec_module(DRIFT)


@contextmanager
def working_directory(path: Path) -> Iterator[None]:
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


class ReviewedHeadDriftTests(unittest.TestCase):
    def git(self, repo: Path, *args: str) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            self.fail(
                f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
            )
        return proc.stdout.strip()

    def write_and_commit(
        self,
        repo: Path,
        relative_path: str,
        content: str,
        message: str,
    ) -> str:
        path = repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.git(repo, "add", relative_path)
        self.git(repo, "commit", "-m", message)
        return self.git(repo, "rev-parse", "HEAD")

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, str]:
        temp = tempfile.TemporaryDirectory()
        repo = Path(temp.name) / "repo"
        repo.mkdir()
        self.git(repo, "init")
        self.git(repo, "config", "user.name", "ORION CI")
        self.git(repo, "config", "user.email", "orion-ci@example.invalid")
        audited = self.write_and_commit(
            repo,
            "README.md",
            "audited base\n",
            "audited base",
        )
        self.git(repo, "branch", "-M", "main")
        self.git(repo, "update-ref", "refs/remotes/origin/main", audited)
        register = Path(temp.name) / "register.json"
        register.write_text(
            json.dumps({"latest_fully_interpreted_main_head": audited}),
            encoding="utf-8",
        )
        return temp, repo, register, audited

    def evaluate(self, repo: Path, register: Path, ref: str = "origin/main"):
        with working_directory(repo):
            return DRIFT.evaluate(register, ref)

    def test_00_equal_head_is_green(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "GREEN")
            self.assertEqual(
                result["reason"], "REF_EQUALS_LATEST_FULLY_INTERPRETED_MAIN_HEAD"
            )

    def test_01_closure_only_commit_is_green(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            head = self.write_and_commit(
                repo,
                "papers/top_tier_science_closure_v3/audit.md",
                "audit only\n",
                "update audit",
            )
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "GREEN")
            self.assertEqual(
                result["reason"], "ONLY_CLOSURE_PACKAGE_COMMITS_AFTER_AUDITED_HEAD"
            )

    def test_02_dedicated_workflow_commit_is_green(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            head = self.write_and_commit(
                repo,
                ".github/workflows/top-tier-science-gap-register.yml",
                "name: audit\n",
                "update audit workflow",
            )
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "GREEN")

    def test_03_manuscript_commit_is_red(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            head = self.write_and_commit(
                repo,
                "papers/ORION-02/manuscript.md",
                "unsupported positive claim\n",
                "change manuscript",
            )
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "RED")
            self.assertEqual(
                result["reason"],
                "UNREVIEWED_SCIENCE_RELEVANT_COMMITS_AFTER_AUDITED_HEAD",
            )
            paths = {
                path
                for commit in result["science_relevant_commits"]
                for path in commit["disallowed_paths"]
            }
            self.assertIn("papers/ORION-02/manuscript.md", paths)

    def test_04_implementation_commit_is_red(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            head = self.write_and_commit(
                repo,
                "orion/evidence.py",
                "# implementation delta\n",
                "change implementation",
            )
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "RED")

    def test_05_merge_commit_with_science_delta_is_red(self) -> None:
        temp, repo, register, audited = self.make_repo()
        with temp:
            self.git(repo, "checkout", "-b", "science-topic", audited)
            self.write_and_commit(
                repo,
                "papers/ORION-14/panel.csv",
                "claim,outcome\n",
                "add panel evidence",
            )
            self.git(repo, "checkout", "main")
            self.write_and_commit(
                repo,
                "papers/top_tier_science_closure_v3/note.md",
                "closure note\n",
                "add closure note",
            )
            self.git(repo, "merge", "--no-ff", "science-topic", "-m", "merge science")
            head = self.git(repo, "rev-parse", "HEAD")
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "RED")
            paths = {
                path
                for commit in result["science_relevant_commits"]
                for path in commit["disallowed_paths"]
            }
            self.assertIn("papers/ORION-14/panel.csv", paths)

    def test_06_divergent_history_is_red(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            self.git(repo, "checkout", "--orphan", "divergent")
            for child in repo.iterdir():
                if child.name == ".git":
                    continue
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child)
                else:
                    child.unlink()
            self.write_and_commit(
                repo,
                "README.md",
                "different root\n",
                "divergent root",
            )
            head = self.git(repo, "rev-parse", "HEAD")
            self.git(repo, "update-ref", "refs/remotes/origin/main", head)
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "RED")
            self.assertEqual(
                result["reason"], "AUDITED_HEAD_IS_NOT_ANCESTOR_OF_CURRENT_REF"
            )

    def test_07_missing_ref_is_cannot_check(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            result, code = self.evaluate(repo, register, "origin/missing")
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "CANNOT_CHECK")
            self.assertEqual(result["reason"], "COMMIT_RESOLUTION_FAILED")

    def test_08_missing_audited_head_is_cannot_check(self) -> None:
        temp, repo, register, _ = self.make_repo()
        with temp:
            register.write_text("{}", encoding="utf-8")
            result, code = self.evaluate(repo, register)
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "CANNOT_CHECK")
            self.assertEqual(
                result["reason"],
                "REGISTER_HAS_NO_LATEST_FULLY_INTERPRETED_MAIN_HEAD",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
