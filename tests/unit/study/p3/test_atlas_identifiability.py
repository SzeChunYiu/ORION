"""The identifiability adapter must find a planted cue and must not read the task.

Two obligations, both from the P4 record
(``research/failures/2026-08-label-recoverable-from-construction-cue/``): the
probes have to catch a label that follows from construction, and they have to
stop at the boundary. Coordinate *values* are the input the comparison rule
reads; a probe that touched them would be a second implementation of the task
reported as a leak.
"""

from __future__ import annotations

from typing import Any

import pytest

from orion.programme.benchmark_identifiability import CaseSplit
from orion.programme.records import Outcome
from orion.study.p3.atlas_identifiability import (
    COORDINATE_FIELDS,
    PROBES,
    audit_atlas_identifiability,
    case_cues,
    labelled_cases,
    probe_cardinality_flags,
)
from orion.study.p3_coordinate_necessity_build import synthetic_coordinate_cases
from orion.study.p3_public_reference import validate_case

CUE_NAMES = {name for probe in PROBES for name in probe.cue_names}


def _case(
    case_id: str,
    relation: str,
    *,
    discipline: str = "physics",
    family: str = "different_name_same_referent",
    measurement: list[str] | None = None,
) -> dict[str, Any]:
    left = {
        "projection_id": f"{case_id}:l",
        "source_id": "fixture",
        "source_span": "record/a",
        "predicate": "states_effect",
        "referent_ids": ["fixture:referent"],
        "construct_ids": ["fixture:construct"],
        "measurement_ids": measurement or [],
        "temporal_context_ids": [],
        "polarity": "POSITIVE",
        "modality": "ASSERTED",
    }
    right = dict(left, projection_id=f"{case_id}:r", source_span="record/b")
    case = {
        "schema_version": "orion.p3.public-reference-case.v1",
        "case_id": case_id,
        "discipline": discipline,
        "case_family": family,
        "source_records": [
            {
                "dataset": "fixture-upstream",
                "revision": "0123456789abcdef",
                "locator": "record/a",
                "content_hash": "a" * 64,
            }
        ],
        "left_projection": left,
        "right_projection": right,
        "expected": {
            "meaning_relation": relation,
            "authority": {"kind": "UPSTREAM_EXPERT", "evidence": ["fixture:record/a"]},
        },
    }
    validate_case(case)
    return case


def _clean_corpus() -> list[dict[str, Any]]:
    """Construction identical across labels; only the coordinates differ."""

    return [
        _case(f"fixture-{index:04d}", "COMPATIBLE" if index % 4 else "CONTRADICTORY")
        for index in range(24)
    ]


def _leaking_corpus() -> list[dict[str, Any]]:
    """Discipline determines the label, which is what a probe must catch."""

    return [
        _case(
            f"fixture-{index:04d}",
            "COMPATIBLE" if index % 4 else "CONTRADICTORY",
            discipline="physics" if index % 4 else "chemistry",
        )
        for index in range(24)
    ]


class TestCues:
    def test_every_declared_cue_is_produced(self) -> None:
        cues = case_cues(_case("fixture-0001", "COMPATIBLE"), index=0, total=1)
        assert CUE_NAMES <= set(cues)

    def test_no_cue_carries_a_coordinate_value(self) -> None:
        case = _case("fixture-0001", "COMPATIBLE", measurement=["unit:kelvin-marker"])
        cues = case_cues(case, index=0, total=4)
        rendered = repr(sorted((name, value) for name, value in cues.items()))
        assert "kelvin-marker" not in rendered
        assert "fixture:referent" not in rendered
        assert "fixture:construct" not in rendered

    def test_cues_do_not_carry_the_label(self) -> None:
        cues = case_cues(_case("fixture-0001", "CONTRADICTORY"), index=0, total=4)
        assert "CONTRADICTORY" not in repr(sorted(cues.items()))

    def test_arity_and_missingness_cover_all_four_coordinates(self) -> None:
        cues = case_cues(_case("fixture-0001", "COMPATIBLE"), index=0, total=4)
        for side in ("left", "right"):
            for field in COORDINATE_FIELDS:
                assert f"arity_{side}_{field}" in cues
                assert f"empty_{side}_{field}" in cues

    def test_added_cases_share_one_construction_signature(self) -> None:
        cases = synthetic_coordinate_cases()
        signatures = {
            tuple(
                sorted(
                    (name, value)
                    for name, value in case_cues(case, index=index, total=len(cases)).items()
                    if name not in {"ordinal_quartile", "case_family", "discipline"}
                )
            )
            for index, case in enumerate(cases)
        }
        assert len(signatures) == 1


class TestSplits:
    def test_in_sample_enters_every_case_on_both_splits(self) -> None:
        rows = labelled_cases(_clean_corpus(), split_mode="in_sample")
        assert len(rows) == 48
        assert sum(row.split is CaseSplit.FIT for row in rows) == 24
        assert sum(row.split is CaseSplit.EVAL for row in rows) == 24

    def test_hash_parity_places_each_case_once_and_reproducibly(self) -> None:
        first = labelled_cases(_clean_corpus(), split_mode="hash_parity")
        second = labelled_cases(_clean_corpus(), split_mode="hash_parity")
        assert len(first) == 24
        assert [(row.case_id, row.split) for row in first] == [
            (row.case_id, row.split) for row in second
        ]

    def test_unknown_split_mode_is_refused(self) -> None:
        with pytest.raises(ValueError):
            labelled_cases(_clean_corpus(), split_mode="whatever")


class TestAudit:
    def test_a_planted_construction_cue_fails_the_audit(self) -> None:
        report = audit_atlas_identifiability("leaking", _leaking_corpus())
        assert report["overall_outcome"] == Outcome.FAIL.value
        recovered = [
            item
            for item in report["audits"]["in_sample"]
            if item["outcome"] == Outcome.FAIL.value
        ]
        assert recovered
        assert any(
            result["probe_id"] == "discipline" and (result["recovery"] or 0) > 0
            for item in recovered
            for result in item["results"]
        )

    def test_a_shape_invariant_corpus_passes(self) -> None:
        report = audit_atlas_identifiability("clean", _clean_corpus())
        assert report["overall_outcome"] == Outcome.PASS.value
        for item in report["audits"]["in_sample"]:
            assert item["worst_recovery"] == 0.0

    def test_every_label_is_audited_under_both_splits(self) -> None:
        report = audit_atlas_identifiability("clean", _clean_corpus())
        assert report["labels"] == ["COMPATIBLE", "CONTRADICTORY"]
        for mode in ("in_sample", "hash_parity"):
            assert [item["label"] for item in report["audits"][mode]] == report["labels"]

    def test_empty_atlas_is_refused(self) -> None:
        with pytest.raises(ValueError):
            audit_atlas_identifiability("empty", [])

    def test_high_cardinality_probes_are_flagged(self) -> None:
        from orion.programme.benchmark_identifiability import audit_label_identifiability

        corpus = [_case(f"fixture-{index:04d}", "COMPATIBLE") for index in range(4)]
        corpus.append(_case("fixture-9999", "CONTRADICTORY"))
        audit = audit_label_identifiability(
            benchmark_id="flags",
            label="COMPATIBLE",
            cases=labelled_cases(corpus, split_mode="in_sample"),
            probes=PROBES,
        )
        flags = probe_cardinality_flags(audit, cases=len(corpus))
        assert set(flags) == {probe.probe_id for probe in PROBES}
        assert flags["ordinal_quartile"] is True
