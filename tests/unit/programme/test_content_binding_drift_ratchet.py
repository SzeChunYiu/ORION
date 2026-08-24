"""CI must read the digest gate, not just ship one.

``content_binding_coverage`` exits 1 on the live tree: fourteen papers carry a
``SHA256SUMS`` that no longer describes their own files. Every existing test of
it builds synthetic ``PaperBinding`` records, so none of them runs it against
the repository -- the gate was reporting a failure no job read, and pull
requests merged green past it.

Turning it on outright would fail CI on fourteen papers that drifted before the
check existed, which reliably ends with the check being switched off. So this is
a ratchet: the drifted set is pinned in a baseline, and only *new* drift fails.

The baseline is a debt record. Entries leave it by reconciling the paper --
never by regenerating digests to match whatever is on disk, which would erase
the evidence that content moved and leave a manifest asserting that nothing did.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.content_binding_coverage import (
    PaperBindingState,
    survey_paper_bindings,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINE = REPO_ROOT / "papers" / "CONTENT_BINDING_DRIFT_BASELINE_V1.json"


def _live_drift() -> dict[str, int]:
    rows = survey_paper_bindings(REPO_ROOT)
    return {
        r.directory: len(r.drifted_paths)
        for r in rows
        if r.state == PaperBindingState.BOUND_DRIFTED
    }


@pytest.fixture(scope="module")
def baseline() -> dict[str, int]:
    if not BASELINE.is_file():
        pytest.fail(f"drift baseline missing: {BASELINE}")
    doc = json.loads(BASELINE.read_text())
    return {k: v["drifted"] for k, v in doc["papers"].items()}


def test_no_paper_drifts_that_was_not_already_drifting(baseline: dict[str, int]) -> None:
    new = sorted(set(_live_drift()) - set(baseline))
    assert not new, (
        "these papers' SHA256SUMS no longer describe their files, and they were "
        f"clean at the baseline: {new}. Reconcile the paper -- do not regenerate "
        "its digests to match the new bytes, and do not add it to the baseline."
    )


def test_no_paper_drifts_further_than_it_already_did(baseline: dict[str, int]) -> None:
    live = _live_drift()
    worse = {
        paper: (was, live[paper])
        for paper, was in baseline.items()
        if paper in live and live[paper] > was
    }
    assert not worse, (
        "more files drifted in papers that were already drifting "
        f"(was, now): {worse}. The baseline pins counts precisely so that new "
        "drift inside an already-indebted paper cannot hide behind it."
    )


def test_baseline_does_not_outlive_the_drift_it_records(baseline: dict[str, int]) -> None:
    """A fixed paper must leave the baseline, or the ratchet stops tightening."""
    live = _live_drift()
    healed = {
        paper: (was, live.get(paper, 0))
        for paper, was in baseline.items()
        if live.get(paper, 0) < was
    }
    assert not healed, (
        "these papers now drift less than the baseline records "
        f"(was, now): {healed}. Update papers/CONTENT_BINDING_DRIFT_BASELINE_V1.json "
        "to the lower count so the gate keeps ratcheting downward."
    )
