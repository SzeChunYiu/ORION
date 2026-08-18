"""P1 was the one paper the clean-install workflow could not hold to byte identity.

Its tables are content-hash-bound and carry a `provenance.generated_utc` wall clock, so
`git diff --exit-code` -- the standard applied to P3, P5 and P4 -- can never pass, and
following `REPRODUCE.md` always drifts the package. The two committed tables were written a
second apart, so no single pinned timestamp reproduces both either.

`--check` compares every field except that clock. These tests pin the two properties that
make the exclusion honest rather than convenient: it is scoped to exactly one field, and it
still catches everything else, including a markdown-only change.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from orion.study.p1 import tables

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction"
RESULTS = PAPER / "results"
ARCHIVE = RESULTS / "raw" / "test_scored.jsonl"
T2_JSON = f"{tables.TABLE_T2}.json"
T2_MD = f"{tables.TABLE_T2}.md"


def _check(out: Path) -> int:
    return tables.main(["--check", "--archive", str(ARCHIVE), "--out", str(out)])


@pytest.fixture
def committed(tmp_path: Path) -> Path:
    """A throwaway copy of the committed results, so a mutation cannot escape."""

    target = tmp_path / "results"
    shutil.copytree(RESULTS, target)
    return target


def test_the_committed_tables_reproduce_exactly() -> None:
    """The no-alarm case, run against the real tree."""

    assert _check(RESULTS) == tables.EXIT_OK


def test_check_writes_nothing_into_the_package(committed: Path) -> None:
    before = {p: p.read_bytes() for p in sorted(committed.rglob("*")) if p.is_file()}
    _check(committed)
    after = {p: p.read_bytes() for p in sorted(committed.rglob("*")) if p.is_file()}
    assert before == after, "--check must regenerate into a scratch directory only"


def test_a_changed_number_is_caught(committed: Path) -> None:
    path = committed / T2_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    row = payload["rows"][0]
    row[sorted(row)[-1]] = "MUTATED"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert _check(committed) == tables.EXIT_ERROR


def test_a_markdown_only_change_is_caught(committed: Path) -> None:
    """The renderings carry no clock, so they get the strict comparison the JSON cannot.

    A drift here while the JSON matches means the renderer changed without the data
    changing, which would otherwise ship silently.
    """

    path = committed / T2_MD
    path.write_text(path.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
    assert _check(committed) == tables.EXIT_ERROR


def test_the_clock_is_the_only_excluded_field(committed: Path) -> None:
    """Scoped exclusion, not a blanket "ignore provenance".

    This is the test that keeps the exclusion honest. Rewriting `generated_utc` to an
    absurd value must still pass; touching any sibling field in the same block must not.
    """

    path = committed / T2_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["provenance"]["generated_utc"] = "1999-01-01T00:00:00+00:00"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert _check(committed) == tables.EXIT_OK

    payload["provenance"]["record_count"] = -1
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert _check(committed) == tables.EXIT_ERROR


def test_an_absent_table_is_cannot_check_not_a_pass(committed: Path) -> None:
    """Absent is not the same as different, and neither is a pass."""

    (committed / T2_JSON).unlink()
    assert _check(committed) == tables.EXIT_CANNOT_CHECK
