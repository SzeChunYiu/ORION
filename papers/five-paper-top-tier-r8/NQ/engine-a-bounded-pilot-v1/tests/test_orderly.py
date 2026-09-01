from __future__ import annotations

from nq_engine_a.group import GroupSpec
from nq_engine_a.orderly import CoverageStatus, generate_canonical_multisets


def test_orderly_generation_is_deterministic_sorted_and_duplicate_free() -> None:
    spec = GroupSpec(2, 2)
    first = generate_canonical_multisets(spec, length=2)
    second = generate_canonical_multisets(spec, length=2)
    assert first.records == second.records
    assert first.records == tuple(sorted(first.records))
    assert len(first.records) == len(set(first.records)) == 4
    assert first.coverage.status is CoverageStatus.COMPLETE
    assert first.coverage.raw_candidates_seen == 10
    assert first.coverage.canonical_accepted == 4


def test_orderly_slice_reports_exact_raw_interval_without_claiming_full_coverage() -> None:
    spec = GroupSpec(2, 2)
    run = generate_canonical_multisets(spec, length=2, start_rank=2, stop_rank=7)
    assert run.coverage.status is CoverageStatus.PARTIAL_SLICE
    assert run.coverage.raw_start == 2
    assert run.coverage.raw_stop_exclusive == 7
    assert run.coverage.raw_candidates_seen == 5
    assert not run.coverage.full_domain_covered


def test_orderly_resource_limit_is_fail_closed_and_records_resume_rank() -> None:
    spec = GroupSpec(3, 2)
    run = generate_canonical_multisets(spec, length=3, max_raw_candidates=7)
    assert run.coverage.status is CoverageStatus.CANNOT_CHECK_RESOURCE_BOUND
    assert run.coverage.raw_candidates_seen == 7
    assert run.coverage.resume_rank == 7
    assert not run.coverage.full_domain_covered


def test_orderly_rejects_negative_length_and_invalid_ranges() -> None:
    spec = GroupSpec(2, 1)
    for kwargs in (
        {"length": -1},
        {"length": 2, "start_rank": -1},
        {"length": 2, "start_rank": 3, "stop_rank": 2},
        {"length": 2, "max_raw_candidates": 0},
    ):
        try:
            generate_canonical_multisets(spec, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid arguments: {kwargs}")


def test_coverage_hook_emits_versioned_schema_payload() -> None:
    import json
    from pathlib import Path

    import jsonschema

    run = generate_canonical_multisets(GroupSpec(2, 1), length=2)
    payload = run.coverage.to_dict()
    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "coverage.schema.json").read_text()
    )
    jsonschema.validate(payload, schema)
    assert payload["full_domain_covered"] is True
