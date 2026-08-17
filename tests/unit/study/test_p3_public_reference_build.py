from __future__ import annotations

import json

from orion.study.p3_public_reference_build import (
    build_atlas,
    muse_coreference_cases,
    scifact_claim_cases,
    scischema_identity_cases,
)


def test_muse_coreference_adapter_emits_pointer_only_gold(tmp_path):
    root = tmp_path / "muse"
    root.mkdir()
    payload = {
        "document_id": "doc-1",
        "relation_annotations": {
            "annotator_1": [
                {
                    "relation_id": "R1",
                    "type": "coreference",
                    "entities": [
                        {"1": {"entity_annotation_id": "1", "start": 0, "end": 4, "text": "PD-L1"}},
                        {"2": {"entity_annotation_id": "2", "start": 10, "end": 15, "text": "CD274"}},
                    ],
                }
            ]
        },
    }
    (root / "case.json").write_text(json.dumps(payload), encoding="utf-8")

    cases = muse_coreference_cases(root)
    assert len(cases) == 1
    case = cases[0]
    assert case["expected"]["meaning_relation"] == "COMPATIBLE"
    assert case["expected"]["authority"]["kind"] == "DERIVED_FROM_ALLOWED"
    assert "text" not in case["source_records"][0]


def test_scifact_adapter_builds_support_and_contradict_controls(tmp_path):
    claims = tmp_path / "claims_train.jsonl"
    claims.write_text(
        json.dumps(
            {
                "id": 1,
                "evidence": {
                    "10": [
                        {"label": "SUPPORT", "sentences": [0]},
                        {"label": "CONTRADICT", "sentences": [1]},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    cases = scifact_claim_cases(claims)
    assert [case["expected"]["meaning_relation"] for case in cases] == [
        "COMPATIBLE",
        "CONTRADICTORY",
    ]


def test_scischema_adapter_keeps_discipline_and_exact_schema_identity(tmp_path):
    root = tmp_path / "schemas"
    schema_dir = root / "physics" / "neutrino"
    schema_dir.mkdir(parents=True)
    (schema_dir / "master-schema.json").write_text(
        json.dumps(
            {
                "$id": "https://example.test/neutrino/1.0.0",
                "title": "Neutrino Event Reconstruction",
            }
        ),
        encoding="utf-8",
    )
    cases = scischema_identity_cases(root)
    assert len(cases) == 1
    assert cases[0]["discipline"] == "physics"
    assert cases[0]["expected"]["authority"]["kind"] == "DETERMINISTIC_STANDARD"


def test_build_atlas_fails_closed_when_coverage_is_insufficient(tmp_path):
    cases, report = build_atlas(
        muse_root=None,
        scifact_claims=None,
        scischema_root=None,
        target_n=32,
    )
    assert cases == []
    assert report["status"] == "CANNOT_CHECK"
    assert report["blockers"]


def test_build_atlas_can_reach_ready_with_multiple_strata_and_outcomes(tmp_path):
    root = tmp_path / "schemas"
    for discipline in ("biology", "physics", "psychology"):
        schema_dir = root / discipline / f"{discipline}-schema"
        schema_dir.mkdir(parents=True)
        (schema_dir / "master-schema.json").write_text(
            json.dumps(
                {
                    "$id": f"https://example.test/{discipline}/1.0.0",
                    "title": f"{discipline} process",
                }
            ),
            encoding="utf-8",
        )

    claims = tmp_path / "claims_train.jsonl"
    claims.write_text(
        json.dumps(
            {
                "id": 10,
                "evidence": {"99": [{"label": "CONTRADICT", "sentences": [0]}]},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cases, report = build_atlas(
        muse_root=None,
        scifact_claims=claims,
        scischema_root=root,
        target_n=4,
    )
    assert len(cases) == 4
    assert report["status"] == "READY_FOR_FREEZE"
    assert len(report["disciplines"]) >= 3
    assert set(report["expected_relations"]) == {"COMPATIBLE", "CONTRADICTORY"}
