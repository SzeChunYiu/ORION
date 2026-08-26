"""Tests for the P11 sparse-decoder threshold sweep.

The sweep exists to say whether a preregistered gate's verdict is a property of
the systems or of the draw. That claim is only worth anything if the sweep
reproduces the frozen runs it is commenting on, so that is the first thing
tested and the reason both published seeds are inside the swept range.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p11 import threshold_stability as ts

REPO_ROOT = Path(__file__).resolve().parents[4]
ARTIFACT = (
    REPO_ROOT
    / "papers/orion-21-state-as-computation/evidence/audit"
    / "P11_THRESHOLD_STABILITY_2026-08-22.json"
)


@pytest.fixture(scope="module")
def committed() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestItReproducesTheFrozenRuns:
    """Without this the sweep is measuring something else and saying so about P11."""

    @pytest.mark.parametrize("protocol", ["P11C", "P11E"])
    def test_the_published_seed_reproduces_its_published_thresholds(
        self, protocol: str, committed: dict
    ) -> None:
        expected = ts.FROZEN_OBSERVATIONS[protocol]
        observed = committed["per_seed"][str(expected["seed"])]
        assert observed == expected["l1_threshold"]

    def test_both_frozen_seeds_are_inside_the_swept_range(self, committed: dict) -> None:
        seeds = set(committed["seeds"])
        for protocol in ts.FROZEN_OBSERVATIONS.values():
            assert protocol["seed"] in seeds

    def test_the_two_frozen_runs_disagree_in_the_first_cell(self) -> None:
        # The fact the sweep was built to settle. If these ever agree, the
        # sweep's premise is gone and it should be re-read, not re-run.
        c = ts.FROZEN_OBSERVATIONS["P11C"]["l1_threshold"]["(17,4,5)"]
        e = ts.FROZEN_OBSERVATIONS["P11E"]["l1_threshold"]["(17,4,5)"]
        assert c != e
        assert ts.FROZEN_OBSERVATIONS["P11C"]["l1_threshold"]["(19,3,7)"] == (
            ts.FROZEN_OBSERVATIONS["P11E"]["l1_threshold"]["(19,3,7)"]
        )


class TestTheMeasuredDistribution:
    def test_the_gate_boundary_is_four_times_the_compiled_threshold(self) -> None:
        assert ts.COMPILED_THRESHOLD * ts.GATE_MULTIPLE == 256

    def test_the_first_cell_straddles_the_boundary(self, committed: dict) -> None:
        counts = committed["threshold_distribution"]["(17,4,5)"]
        assert set(counts) == {"128", "256"}
        assert counts["128"] > 0 and counts["256"] > 0

    def test_the_second_cell_does_not_move(self, committed: dict) -> None:
        # The finding is about one cell, not about the construction as a whole.
        assert committed["threshold_distribution"]["(19,3,7)"] == {"256": 20}

    def test_only_the_first_cell_is_reported_as_moving(self, committed: dict) -> None:
        assert committed["cells_whose_threshold_moves"] == ["(17,4,5)"]

    def test_the_gate_is_close_to_a_coin_flip(self, committed: dict) -> None:
        # The number that matters. A preregistered gate whose verdict comes up
        # differently in roughly half the draws of its own construction cannot
        # distinguish the hypotheses it was written to distinguish.
        assert 0.3 <= committed["gate_pass_fraction"] <= 0.7
        assert committed["seeds_passing_in_both_cells"] == 11
        assert len(committed["seeds"]) == 20

    def test_every_seed_reports_both_cells(self, committed: dict) -> None:
        for seed, row in committed["per_seed"].items():
            assert set(row) == {"(17,4,5)", "(19,3,7)"}, seed


class TestWhatItRefusesToLicense:
    def test_it_authorizes_no_terminal(self, committed: dict) -> None:
        assert any("any change to P11C's terminal" in item for item in committed["not_licensed"])
        assert any("selected rather than measured" in item for item in committed["not_licensed"])

    def test_it_does_not_claim_the_result_is_false(self, committed: dict) -> None:
        # A 0.55 pass rate says the construction cannot decide, not that the
        # claim is wrong. Those are different and the artifact must not blur them.
        assert any(
            "not decided in either direction" in item for item in committed["not_licensed"]
        )

    def test_it_states_that_only_l1_is_swept(self, committed: dict) -> None:
        assert any("only UNIVERSAL_L1 is swept" in item for item in committed["not_licensed"])
