from __future__ import annotations

import json

from orion.study.p3_public_reference_analysis import ablated_relation
from orion.study.p3_public_reference_build_v11 import build_atlas_v11
from tests.unit.study.test_p3_public_reference_build import declare


def _write_muse(root):
    root.mkdir(parents=True)
    payload = {
        "document_id": "doc-1",
        "relation_annotations": {
            "expert": [{
                "relation_id": "R1",
                "type": "coreference",
                "entities": [
                    {"1": {"entity_annotation_id": "1", "start": 0, "end": 5, "text": "PD-L1"}},
                    {"2": {"entity_annotation_id": "2", "start": 10, "end": 15, "text": "CD274"}},
                ],
            }]
        },
    }
    (root / "case.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_scifact(path):
    path.write_text(
        json.dumps({
            "id": 1,
            "evidence": {"10": [{"label": "CONTRADICT", "sentences": [0]}]},
        }) + "\n",
        encoding="utf-8",
    )


def _schema(schema_id: str, title: str, *, rich: bool):
    properties = {}
    if rich:
        properties = {
            "detector_radius": {
                "type": "object",
                "properties": {"value": {"type": "number"}, "unit": {"const": "cm"}},
            },
            "fiducial_radius": {
                "type": "object",
                "properties": {"value": {"type": "number"}, "unit": {"const": "cm"}},
            },
            "hit_time": {
                "type": "object",
                "properties": {"value": {"type": "number"}, "unit": {"const": "ns"}},
            },
        }
    return {"$id": schema_id, "title": title, "type": "object", "properties": properties}


def _write_scischema(root):
    for name, rich in (("a", True), ("b", False)):
        directory = root / "physics" / name
        directory.mkdir(parents=True)
        (directory / "master-schema.json").write_text(
            json.dumps(_schema(f"https://example.test/{name}/1.0.0", name, rich=rich)),
            encoding="utf-8",
        )


def test_v11_build_has_stable_locators_required_relations_and_targeted_ablations(tmp_path):
    muse = tmp_path / "muse"
    scifact = tmp_path / "claims_dev.jsonl"
    schemas = tmp_path / "schemas"
    _write_muse(muse)
    _write_scifact(scifact)
    _write_scischema(schemas)

    pins = (
        declare("MUSE", *sorted(muse.rglob("*.json")))
        + declare("SciFact", scifact)
        + declare("SciSchema", *sorted(schemas.glob("*/*/master-schema.json")))
    )
    cases, report = build_atlas_v11(
        muse_root=muse,
        scifact_claims=scifact,
        scischema_root=schemas,
        target_n=6,
        pins=pins,
    )

    assert report["status"] == "READY_FOR_FREEZE"
    assert set(report["required_relations"]) <= set(report["expected_relations"])
    assert len(report["disciplines"]) >= 3

    for case in cases:
        for source in case["source_records"]:
            assert not str(source["locator"]).startswith("/")
        assert not str(case["left_projection"]["source_span"]).startswith("/")
        assert not str(case["right_projection"]["source_span"]).startswith("/")

    by_relation = {str(case["expected"]["meaning_relation"]): case for case in cases}
    assert ablated_relation(by_relation["DISTINCT_REFERENT"], "remove_referent").value == "COMPATIBLE"
    assert ablated_relation(by_relation["DISTINCT_CONSTRUCT"], "remove_construct").value == "COMPATIBLE"
    assert ablated_relation(by_relation["DISTINCT_MEASUREMENT"], "remove_measurement").value == "COMPATIBLE"
    assert (
        ablated_relation(
            by_relation["CONTRADICTORY"],
            "remove_modality_polarity_attribution_discourse",
        ).value
        == "COMPATIBLE"
    )
