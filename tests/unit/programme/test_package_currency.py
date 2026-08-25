"""A submission package must not quietly stop being the submission.

All five packages were already stale when this was written, so the assertion is
a ratchet against a pinned baseline rather than a hard gate: new staleness
fails, existing debt stays visible and counted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.package_currency import (
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    EXIT_REGRESSED,
    main,
    survey,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINE = REPO_ROOT / "papers" / "JOURNAL_PACKAGE_STALENESS_BASELINE_V1.json"


@pytest.fixture(scope="module")
def baseline() -> dict[str, dict[str, int]]:
    if not BASELINE.is_file():
        pytest.fail(f"package staleness baseline missing: {BASELINE}")
    return json.loads(BASELINE.read_text())["packages"]


def _live() -> dict[str, dict[str, int]]:
    return {r.paper: {"stale": r.stale, "missing": r.missing} for r in survey(REPO_ROOT)}


def test_no_package_becomes_staler_than_it_already_was(baseline) -> None:
    live = _live()
    worse = {
        p: {"was": baseline[p]["stale"], "now": v["stale"]}
        for p, v in live.items()
        if p in baseline and v["stale"] > baseline[p]["stale"]
    }
    assert not worse, (
        f"these submission packages drifted further from their source: {worse}. "
        "Rebuild the package -- do not rewrite its digests to match the moved "
        "files, which would delete the evidence that it moved."
    )


def test_no_package_starts_claiming_a_file_that_is_not_there(baseline) -> None:
    live = _live()
    worse = {
        p: {"was": baseline[p]["missing"], "now": v["missing"]}
        for p, v in live.items()
        if p in baseline and v["missing"] > baseline[p]["missing"]
    }
    assert not worse, f"packages now claim files that do not exist: {worse}"


def test_a_new_package_is_not_silently_untracked(baseline) -> None:
    """A package added after the baseline must be checked, not inherit silence."""
    new = sorted(set(_live()) - set(baseline))
    assert not new, (
        f"these journal packages are not in the baseline: {new}. Add them, or "
        "they are exempt from the only check that reads them."
    )


def test_baseline_does_not_outlive_the_staleness_it_records(baseline) -> None:
    live = _live()
    healed = {
        p: {"was": baseline[p]["stale"], "now": live.get(p, {}).get("stale", 0)}
        for p in baseline
        if live.get(p, {}).get("stale", 0) < baseline[p]["stale"]
    }
    assert not healed, (
        f"these packages are now less stale than recorded: {healed}. Lower the "
        "baseline so the ratchet keeps tightening."
    )


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_a_current_package_passes(tmp_path: Path) -> None:
    import hashlib

    pkg = tmp_path / "papers" / "paper-99-fake" / "journal_package"
    pkg.mkdir(parents=True)
    src = tmp_path / "papers" / "paper-99-fake" / "MANUSCRIPT.md"
    src.write_text("body\n")
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    (pkg / "SHA256SUMS").write_text(f"{digest}  MANUSCRIPT.md\n")
    assert main(["--root", str(tmp_path)]) == EXIT_PASS
    src.write_text("body moved\n")
    assert main(["--root", str(tmp_path)]) == EXIT_REGRESSED
