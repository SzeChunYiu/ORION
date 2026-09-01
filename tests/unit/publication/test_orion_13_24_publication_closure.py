from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PAPERS = ["ORION-13", "ORION-14", "ORION-19", "ORION-21", "ORION-23", "ORION-24"]
CHECKER = ROOT / "scripts/check_publication_closure.py"
REGISTRY = ROOT / "papers/publication_closure/orion_13_24_final/CLOSURE_REGISTRY.json"


def test_registry_has_exact_requested_coverage() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert registry["requested_papers"] == PAPERS
    assert [record["paper"] for record in registry["papers"]] == PAPERS
    assert len({record["package_manifest"] for record in registry["papers"]}) == len(PAPERS)


def test_publication_packages_pass_fast_verifier() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), *PAPERS],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unknown_paper_fails_closed() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "ORION-999"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode != 0
    assert "unregistered requested papers" in result.stdout


def test_a_missing_pdf_toolchain_is_cannot_check_not_a_failed_verification(
    tmp_path,
) -> None:
    """A host without poppler must say so, not report six refuted packages.

    CI run 33467487052 failed exactly this way: `pdfinfo` was absent, the verifier
    died with FileNotFoundError, and the suite recorded a failed publication-closure
    check for six packages that verify clean wherever the tool is installed. Exit 3
    is this repository's could-not-check code and has to stay distinguishable from
    exit 1, which means refuted.
    """

    empty_bin = tmp_path / "no-tools"
    empty_bin.mkdir()
    # sys.executable is absolute, so emptying PATH removes pdfinfo/pdftotext
    # without also hiding the interpreter.
    stripped = subprocess.run(
        [sys.executable, str(CHECKER), *PAPERS],
        cwd=ROOT,
        env={**os.environ, "PATH": str(empty_bin)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert stripped.returncode == 3, stripped.stdout + stripped.stderr
    payload = json.loads(stripped.stdout)
    assert payload["status"] == "CANNOT_CHECK"
    assert payload["missing_tool"] == "pdfinfo"
    assert "failures" not in payload, "a run that never happened reports no failures"

    # The no-alarm case. Without this the guard could swallow real refutations by
    # taking the could-not-check branch on a healthy host.
    healthy = subprocess.run(
        [sys.executable, str(CHECKER), *PAPERS],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert healthy.returncode == 0, healthy.stdout + healthy.stderr
    assert json.loads(healthy.stdout)["all_checks"] is True


def test_orion24_preflight_denominator_is_not_case_count() -> None:
    manuscript = (ROOT / "papers/orion-24-orion-rse/WAVE3_SCOPED_MANUSCRIPT_V1.md").read_text(encoding="utf-8").lower()
    assert "eight required external-input artifact classes" in manuscript
    assert "not a count of attempted external cases" in manuscript
    assert "not a completed harness" in manuscript
    assert "negative acquisition result" not in manuscript
