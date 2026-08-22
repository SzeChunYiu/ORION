from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from orion.study.p3_public_reference_build import (
    CorpusPin,
    UnpinnedCorpus,
    build_atlas,
    muse_coreference_cases,
    scifact_claim_cases,
    scischema_identity_cases,
)


def declare(dataset: str, *paths: Path) -> tuple[CorpusPin, ...]:
    """Admit these fixture bytes as `dataset`, the way a real corpus is admitted.

    The adapters refuse bytes no pin declares, and a fixture is not exempt from
    that: a test that could opt out of the check would not be exercising the
    adapter the build actually runs. So a fixture declares itself, and the
    identity its cases carry is the digest of the bytes the test wrote.
    """

    pins = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        pins.append(
            CorpusPin(
                dataset=dataset,
                identity=f"sha256:{digest}",
                sha256=digest,
                source=f"test fixture {path.name}",
            )
        )
    return tuple(pins)


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

    cases = muse_coreference_cases(root, declare("MUSE", root / "case.json"))
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
    cases = scifact_claim_cases(claims, declare("SciFact", claims))
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
    cases = scischema_identity_cases(
        root, declare("SciSchema", schema_dir / "master-schema.json")
    )
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

    pins = declare("SciFact", claims) + declare(
        "SciSchema", *sorted(root.glob("*/*/master-schema.json"))
    )
    cases, report = build_atlas(
        muse_root=None,
        scifact_claims=claims,
        scischema_root=root,
        target_n=4,
        pins=pins,
    )
    assert len(cases) == 4
    assert report["status"] == "READY_FOR_FREEZE"
    assert len(report["disciplines"]) >= 3
    assert set(report["expected_relations"]) == {"COMPATIBLE", "CONTRADICTORY"}


def test_an_undeclared_corpus_is_refused_rather_than_stamped(tmp_path):
    """The defect this pinning replaces: a revision asserted onto any bytes.

    Every emitted case used to record the pinned upstream revision regardless of
    which file the build was handed, while `content_hash` was computed from that
    file. An atlas built from an edited or wrong-version corpus therefore carried
    a provenance nobody had checked, and each case's `DERIVED_FROM_ALLOWED`
    authority cited it as evidence. Refusing is the point: the message has to name
    the digest that was seen, or the operator cannot add the pin deliberately.
    """

    claims = tmp_path / "claims_train.jsonl"
    claims.write_text(
        json.dumps({"id": 1, "evidence": {"9": [{"label": "SUPPORT", "sentences": [0]}]}}) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(claims.read_bytes()).hexdigest()

    with pytest.raises(UnpinnedCorpus) as raised:
        scifact_claim_cases(claims)
    assert digest in str(raised.value)

    # And a case built from declared bytes carries those bytes' identity, not a
    # constant: change one byte and the recorded identity changes with it.
    cases = scifact_claim_cases(claims, declare("SciFact", claims))
    assert cases[0]["source_records"][0]["revision"] == f"sha256:{digest}"

    claims.write_text(
        json.dumps({"id": 2, "evidence": {"9": [{"label": "SUPPORT", "sentences": [0]}]}}) + "\n",
        encoding="utf-8",
    )
    moved = scifact_claim_cases(claims, declare("SciFact", claims))
    assert moved[0]["source_records"][0]["revision"] != f"sha256:{digest}"
