"""Source and target family slots are independent and frozen before outcomes."""

from __future__ import annotations

from pathlib import Path

from orion.transfer.scientific.benchmark import (
    FAMILY_IDS,
    HOSTILE_FALSIFIER_KINDS,
    PAIR_KINDS,
    load_benchmark_design,
)

ROOT = Path(__file__).resolve().parents[3]
DESIGN_PATH = (
    ROOT
    / "research"
    / "cross-domain-mechanic-transfer-v1"
    / "fixtures"
    / "BENCHMARK_DESIGN_V1.json"
)


def test_benchmark_design_has_independent_source_and_target_family_slots() -> None:
    design = load_benchmark_design(DESIGN_PATH)
    assert design.outcomes_accessed is False
    assert design.freeze_status == "PAIRS_AND_REPRESENTATIONS_FROZEN"
    assert set(design.family_ids) == set(FAMILY_IDS)
    source_ids = {slot.slot_id for slot in design.source_slots}
    target_ids = {slot.slot_id for slot in design.target_slots}
    assert source_ids.isdisjoint(target_ids)
    assert len(source_ids) == len(design.source_slots)
    assert len(target_ids) == len(design.target_slots)
    for family in FAMILY_IDS:
        assert any(slot.family_id == family for slot in design.source_slots)
        assert any(slot.family_id == family for slot in design.target_slots)


def test_each_family_has_positive_near_miss_negative_and_partial_pairs() -> None:
    design = load_benchmark_design(DESIGN_PATH)
    for family in FAMILY_IDS:
        kinds = {
            pair.pair_kind
            for pair in design.pairs
            if pair.source_family_id == family and pair.target_family_id != family
        }
        assert set(PAIR_KINDS) <= kinds


def test_hostile_falsifier_slots_cover_required_kinds() -> None:
    design = load_benchmark_design(DESIGN_PATH)
    present = {item.kind for item in design.hostile_falsifiers}
    assert set(HOSTILE_FALSIFIER_KINDS) <= present
    for item in design.hostile_falsifiers:
        assert item.expected_selector_admission is False


def test_benchmark_payload_has_no_outcome_or_score_fields() -> None:
    design = load_benchmark_design(DESIGN_PATH)
    raw = design.raw_payload
    blob = str(raw)
    for forbidden in ("heldout_answer", "target_label", "net_transfer_gain", "negative_transfer_rate"):
        assert forbidden not in blob
    assert "outcomes" not in raw


def test_source_slots_do_not_embed_target_solution_fragments() -> None:
    design = load_benchmark_design(DESIGN_PATH)
    target_ids = {slot.slot_id for slot in design.target_slots}
    for slot in design.source_slots:
        assert slot.slot_id not in str(slot.transfer_object)
        for target_id in target_ids:
            assert target_id not in str(slot.transfer_object)
