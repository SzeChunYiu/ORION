"""Tests for the P9 attack-potency audit.

The claim is that an attack could not have succeeded, which is only meaningful
if the same measurement reports that other attacks could have. So the inert
cells and the potent ones are asserted together, and the measurement is checked
to be a comparison of *features* rather than of datasets -- two datasets can
differ in every byte and produce identical feature vectors, and then the attack
reached the file and not the model.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p9 import attack_potency as ap

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def report() -> dict:
    return ap.build_report(date="2026-08-22")


class TestTheGridIsMeasuredNotAsserted:
    def test_the_grid_covers_three_variants_and_eight_arms(self, report: dict) -> None:
        assert report["cells_total"] == 24
        assert sorted(report["per_variant"]) == [
            "EQUAL_LENGTH",
            "ORDER_PERMUTATION",
            "SEMANTIC_ORBIT",
        ]

    def test_order_permutation_reaches_no_arm(self, report: dict) -> None:
        summary = report["per_variant"]["ORDER_PERMUTATION"]
        assert summary["arms_actually_attacked"] == 0
        assert set(summary["instances_changed_by_arm"].values()) == {0}

    def test_it_is_the_only_fully_inert_variant(self, report: dict) -> None:
        assert report["fully_inert_variants"] == ["ORDER_PERMUTATION"]

    def test_equal_length_reaches_seven_of_eight_arms(self, report: dict) -> None:
        summary = report["per_variant"]["EQUAL_LENGTH"]
        assert summary["arms_actually_attacked"] == 7
        changed = summary["instances_changed_by_arm"]
        assert changed["TRANSCRIPT_BAG"] == 0
        assert all(v == 112 for k, v in changed.items() if k != "TRANSCRIPT_BAG")

    def test_semantic_orbit_reaches_two_of_eight_arms(self, report: dict) -> None:
        summary = report["per_variant"]["SEMANTIC_ORBIT"]
        assert summary["arms_actually_attacked"] == 2
        changed = summary["instances_changed_by_arm"]
        assert changed["SERIALIZED_INDEXED"] == 512
        assert changed["TYPED_SERIALIZED_BAG"] == 512

    def test_fifteen_of_twenty_four_cells_are_inert(self, report: dict) -> None:
        assert report["cells_inert"] == 15
        assert len(report["inert_cells"]) == 15
        assert report["every_cell_attacked_something"] is False

    def test_the_measurement_is_not_vacuous(self, report: dict) -> None:
        # If every cell read zero the finding would be about the measurement.
        attacked = [cell for cell in report["cells"] if cell["attacked"]]
        assert len(attacked) == 9
        assert {cell["changed"] for cell in attacked} == {112, 512}


class TestTheRootCause:
    """The reversal is undone by the rebuild, and that is checked rather than argued.

    This class exists because the first version of this module asserted the
    opposite -- that the ORDER_PERMUTATION dataset genuinely differed from the
    base and only the feature functions were order-blind. A test asserting that
    difference failed, which is the only reason the real cause was found.
    """

    @pytest.fixture(scope="module")
    def canon(self) -> dict:
        return ap.canonicalisation_undoes_reordering()

    def test_the_order_variant_is_identical_to_the_base(self, canon: dict) -> None:
        assert canon["order_variant_is_identical_to_base"] is True
        assert canon["manifest_digests_equal"] is True

    def test_a_reversal_does_not_survive_the_rebuild(self, canon: dict) -> None:
        assert canon["reversed_input"] == list(reversed(canon["original"]))
        assert canon["after_rebuild"] == canon["original"]
        assert canon["reversal_survives_the_rebuild"] is False

    def test_a_duplicate_does_not_survive_the_rebuild_either(self, canon: dict) -> None:
        # Same normaliser, second class of transform this data model cannot
        # express: tuple(sorted(set(...))) drops repeats as well as order.
        assert len(canon["duplicated_input"]) == len(canon["original"]) + 1
        assert canon["after_rebuild_with_duplicate"] == canon["original"]
        assert canon["duplicate_survives_the_rebuild"] is False

    def test_the_normaliser_is_quoted_from_the_source(self, canon: dict) -> None:
        source = (
            REPO_ROOT / "src/orion/transfer/v2/p1_method_realization.py"
        ).read_text(encoding="utf-8")
        assert canon["normaliser"] in source

    def test_the_reading_says_repairing_the_wiring_would_not_help(self, canon: dict) -> None:
        assert "would not produce an order attack" in canon["reading"]


class TestTheReport:
    def test_it_names_what_it_does_not_license(self, report: dict) -> None:
        assert any("not robust to reordering" in item for item in report["not_licensed"])
        assert any("committed result is wrong" in item for item in report["not_licensed"])
        assert any("frozen parameter block" in item for item in report["not_licensed"])

    def test_the_count_in_the_prose_is_computed_not_typed(self, report: dict) -> None:
        # A prose count that drifts from the measurement is how a finding
        # becomes a claim.
        assert f"{report['cells_inert']} of the {report['cells_total']}" in (
            report["what_this_establishes"]
        )

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert ap.build_report(date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        assert ap.main(["--date", "2026-08-22", "--output", str(out)]) == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["record"] == "P9_ATTACK_POTENCY"
        assert written["fully_inert_variants"] == ["ORDER_PERMUTATION"]
