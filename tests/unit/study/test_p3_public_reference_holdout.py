from __future__ import annotations

from pathlib import Path

from orion.study.p3_public_reference import SCHEMA_VERSION, canonical_json
from orion.study.p3_public_reference_holdout import _balanced_window, build_holdout


def _case(
    case_id: str,
    discipline: str = "d",
    relation: str = "COMPATIBLE",
    family: str = "different_name_same_referent",
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "discipline": discipline,
        "case_family": family,
        "source_records": [{
            "dataset": "X", "revision": "r", "locator": case_id,
            "content_hash": "a" * 64, "license": "x"
        }],
        "left_projection": {
            "projection_id": f"{case_id}:l", "source_id": "s", "source_span": "l",
            "predicate": "p", "referent_ids": ["x"], "construct_ids": [],
            "measurement_ids": [], "temporal_context_ids": [],
            "polarity": "POSITIVE", "modality": "ASSERTED"
        },
        "right_projection": {
            "projection_id": f"{case_id}:r", "source_id": "s", "source_span": "r",
            "predicate": "p", "referent_ids": ["x"], "construct_ids": [],
            "measurement_ids": [], "temporal_context_ids": [],
            "polarity": "POSITIVE" if relation == "COMPATIBLE" else "NEGATED",
            "modality": "ASSERTED"
        },
        "expected": {
            "meaning_relation": relation,
            "authority": {
                "kind": "DERIVED_FROM_ALLOWED", "evidence": [case_id],
                "derivation": {"rule": "identity:test", "inputs": [case_id]}
            }
        }
    }


def test_balanced_window_is_disjoint_second_window() -> None:
    pools = {
        "A": [_case(f"a{i}") for i in range(5)],
        "B": [_case(f"b{i}") for i in range(5)],
    }
    first = _balanced_window(pools, offset=0, total=4)
    second = _balanced_window(pools, offset=4, total=4)
    assert [x["case_id"] for x in first] == ["a0", "b0", "a1", "b1"]
    assert [x["case_id"] for x in second] == ["a2", "b2", "a3", "b3"]
    assert not {str(x["case_id"]) for x in first} & {str(x["case_id"]) for x in second}


def test_build_holdout_fails_closed_on_overlap(tmp_path: Path, monkeypatch) -> None:
    primary = tmp_path / "primary.jsonl"
    primary.write_bytes(canonical_json(_case("a1")) + b"\n")

    import orion.study.p3_public_reference_holdout as mod
    monkeypatch.setattr(mod, "muse_coreference_cases", lambda _: [_case("a0"), _case("a1"), _case("a2")])
    monkeypatch.setattr(mod, "scifact_claim_cases", lambda _: [
        _case("b0", "e", "CONTRADICTORY", "polarity_modality_attribution_context"),
        _case("b1", "e", "CONTRADICTORY", "polarity_modality_attribution_context"),
    ])
    monkeypatch.setattr(mod, "scischema_identity_cases", lambda _: [
        _case("c0", "f", family="valid_invalid_representation_mapping"),
        _case("c1", "f", family="valid_invalid_representation_mapping"),
    ])

    cases, report = build_holdout(
        muse_root=tmp_path, scifact_claims=tmp_path / "x", scischema_root=tmp_path,
        exclude_cases=primary, offset=0, target_n=6
    )
    assert len(cases) == 6
    assert report["status"] == "CANNOT_CHECK"
    assert report["overlap_count"] == 1


def test_build_holdout_is_ready_when_disjoint_and_supported(tmp_path: Path, monkeypatch) -> None:
    primary = tmp_path / "primary.jsonl"
    primary.write_bytes(canonical_json(_case("old")) + b"\n")

    import orion.study.p3_public_reference_holdout as mod
    monkeypatch.setattr(mod, "muse_coreference_cases", lambda _: [_case("a0", "d1"), _case("a1", "d1")])
    monkeypatch.setattr(mod, "scifact_claim_cases", lambda _: [
        _case("b0", "d2", "CONTRADICTORY", "polarity_modality_attribution_context"),
        _case("b1", "d2", "CONTRADICTORY", "polarity_modality_attribution_context"),
    ])
    monkeypatch.setattr(mod, "scischema_identity_cases", lambda _: [
        _case("c0", "d3", family="valid_invalid_representation_mapping"),
        _case("c1", "d3", family="valid_invalid_representation_mapping"),
    ])

    cases, report = build_holdout(
        muse_root=tmp_path, scifact_claims=tmp_path / "x", scischema_root=tmp_path,
        exclude_cases=primary, offset=0, target_n=6
    )
    assert len(cases) == 6
    assert report["status"] == "READY_FOR_CONFIRMATORY_FREEZE"
    assert report["overlap_count"] == 0
    assert len(report["disciplines"]) == 3
    assert len(report["case_families"]) == 3
    assert report["cases_sha256"]
