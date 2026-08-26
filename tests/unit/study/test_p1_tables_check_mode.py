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
import math
import shutil
from pathlib import Path

import pytest

from orion.study.p1 import tables

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction"
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


def _perturb_first_interval(path: Path, nudge) -> tuple[float, float]:
    """Apply ``nudge`` to one bootstrap interval bound. Returns (before, after).

    Asserts the value actually moved. A first version of this helper multiplied by
    ``1 + 1e-16``, which rounds straight back to the same double for a value near
    0.074 -- the test then "passed" while changing nothing at all. Perturbing by ULP
    steps via ``math.nextafter`` is both the honest way to express "one bit different"
    and immune to that.
    """

    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload["rows"]:
        mechanistic = row.get("mechanistic") or {}
        for block in mechanistic.values():
            interval = (block or {}).get("interval") or {}
            before = interval.get("high")
            if isinstance(before, float) and before > 0.0:
                after = nudge(before)
                assert after != before, "the perturbation did not change the stored value"
                interval["high"] = after
                path.write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
                return before, after
    raise AssertionError("no positive interval bound found to perturb")


def _ulps(count: int):
    """A nudge of ``count`` units in the last place, upward."""

    def nudge(value: float) -> float:
        for _ in range(count):
            value = math.nextafter(value, math.inf)
        return value

    return nudge


def test_last_bit_float_noise_is_not_reported_as_drift(committed: Path) -> None:
    """The CI failure this tolerance exists for, reproduced deliberately.

    The committed tables were generated on macOS arm64 and are checked on a Linux
    x86-64 runner. Twenty bootstrap interval bounds came back differing in their last
    bits, the largest delta 5.551e-17 -- two ULP near 0.19 -- while the markdown
    renderings, compared byte-for-byte, matched exactly. Same numbers, different CPU.

    A relative nudge of 1e-16 is that same order of magnitude and must not fail.
    """

    before, after = _perturb_first_interval(committed / T2_JSON, _ulps(2))
    assert 0.0 < abs(after - before) < 1e-15, f"expected ULP-scale nudge, got {after - before:g}"
    assert _check(committed) == tables.EXIT_OK


def test_a_real_numeric_change_still_fails_despite_the_tolerance(committed: Path) -> None:
    """Non-vacuity: the tolerance must not be a hole a real change fits through.

    Widening a float comparison is exactly the kind of fix that silently disables the
    check it was meant to keep honest. A 10,000-resample bootstrap has Monte Carlo
    error around 1e-3, so any genuine change -- different seed, archive, estimator --
    moves these bounds by orders of magnitude more than platform noise. This asserts a
    change far below that, and still nine orders above the noise floor, is caught.
    """

    _perturb_first_interval(committed / T2_JSON, lambda v: v * (1 + 1e-9))
    assert _check(committed) == tables.EXIT_ERROR


def test_the_tolerance_band_is_wide_of_the_noise_and_clear_of_anything_real() -> None:
    """Pin the band itself, so narrowing or widening it is a deliberate edit.

    Observed platform noise is ~3e-16 relative; the tolerance sits four orders above
    it and nine below a real change. The absolute floor covers the one observed case
    of 6.938893903907228e-18 against exactly 0.0, where relative comparison is
    undefined.
    """

    assert tables._near(0.1936076805344364, 0.19360768053443644)
    assert tables._near(6.938893903907228e-18, 0.0)
    assert not tables._near(0.19360768, 0.19360768 * (1 + 1e-9))
    assert not tables._near(0.5, 0.501)
