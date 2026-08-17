from __future__ import annotations

import json
from pathlib import Path

from orion.study.p3_public_reference import SCHEMA_VERSION, canonical_json
from orion.study.p3_public_reference_freeze import freeze_cases


def _case(local_root: str) -> dict[str, object]:
    shared = "x"
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": "portable-1",
        "discipline": "biology",
        "case_family": "different_name_same_referent",
        "source_records": [
            {
                "dataset": "MUSE",
                "revision": "f7a40317db46145d0c90b221311d8324db5da1b9",
                "locator": f"{local_root}/relevant_examples/example.json",
                "content_hash": "a" * 64,
                "license": "UPSTREAM_POINTER_ONLY",
            }
        ],
        "left_projection": {
            "projection_id": "l",
            "source_id": "doc",
            "source_span": f"{local_root}/relevant_examples/example.json#1:2",
            "predicate": "mentions_concept",
            "referent_ids": [shared],
            "construct_ids": [],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": "UNKNOWN",
            "modality": "UNKNOWN",
        },
        "right_projection": {
            "projection_id": "r",
            "source_id": "doc",
            "source_span": f"{local_root}/relevant_examples/example.json#3:4",
            "predicate": "mentions_concept",
            "referent_ids": [shared],
            "construct_ids": [],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": "UNKNOWN",
            "modality": "UNKNOWN",
        },
        "expected": {
            "meaning_relation": "COMPATIBLE",
            "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [f"MUSE@rev:{local_root}/relevant_examples/example.json#R1"],
                "derivation": {"rule": "identity:test", "inputs": ["R1"]},
            },
        },
    }


def test_freeze_rewrites_machine_local_roots_and_is_deterministic(tmp_path: Path) -> None:
    muse_root = tmp_path / "checkout" / "upstream" / "MUSE" / "dataset" / "human_Expert_annotations"
    source = tmp_path / "cases.jsonl"
    source.write_bytes(canonical_json(_case(muse_root.as_posix())) + b"\n")

    first = freeze_cases(source_cases=source, out_dir=tmp_path / "one", muse_root=muse_root)
    second = freeze_cases(source_cases=source, out_dir=tmp_path / "two", muse_root=muse_root)

    assert first["portable_cases_sha256"] == second["portable_cases_sha256"]
    frozen = (tmp_path / "one" / "PUBLIC_REFERENCE_GOLD_V1.jsonl").read_text()
    assert muse_root.as_posix() not in frozen
    assert "dataset/human_Expert_annotations/relevant_examples/example.json" in frozen


def test_freeze_manifest_records_upstream_relative_policy(tmp_path: Path) -> None:
    muse_root = tmp_path / "MUSE" / "dataset" / "human_Expert_annotations"
    source = tmp_path / "cases.jsonl"
    source.write_bytes(canonical_json(_case(muse_root.as_posix())) + b"\n")

    manifest = freeze_cases(source_cases=source, out_dir=tmp_path / "out", muse_root=muse_root)

    assert manifest["status"] == "PUBLIC_REFERENCE_GOLD_FROZEN"
    assert manifest["case_count"] == 1
    assert manifest["locator_policy"].startswith("upstream-relative")
    stored = json.loads((tmp_path / "out" / "PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json").read_text())
    assert stored["portable_cases_sha256"] == manifest["portable_cases_sha256"]
