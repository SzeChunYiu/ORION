from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path

import jsonschema
import pytest

from nq_engine_a.factorization import (
    FactorizationCertificate,
    FactorizationStatus,
    find_disjoint_zero_sums,
)
from nq_engine_a.group import GroupSpec
from nq_engine_a.manifest import build_source_manifest, verify_source_manifest
from nq_engine_a.receipt import (
    ReceiptError,
    ReceiptTerminal,
    build_factorization_receipt,
    canonical_json_sha256,
    factorization_input_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
MARKERS = ["EXPECTED_OUTCOME_EXPOSURE", "ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK"]
DIGESTS = {"source_manifest_sha256": "b" * 64}


def load_schema(name: str) -> dict[str, object]:
    return json.loads((SCHEMAS / name).read_text())


def test_all_json_schemas_are_valid_draft_2020_12() -> None:
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = json.loads(path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
    assert {path.name for path in SCHEMAS.glob("*.schema.json")} == {
        "input.schema.json",
        "certificate.schema.json",
        "receipt.schema.json",
        "source-manifest.schema.json",
        "coverage.schema.json",
        "normalization-contract.schema.json",
        "normalization-binding-receipt.schema.json",
        "augmentation-coverage.schema.json",
        "canonical-augmentation-controls.schema.json",
        "checkpoint.schema.json",
        "donor-range-manifest.schema.json",
        "target-resource-pilot-receipt.schema.json",
        "target-resource-pilot.schema.json",
    }


def test_input_and_certificate_schema_accept_valid_objects_and_reject_hostile_mutations() -> None:
    input_schema = load_schema("input.schema.json")
    certificate_schema = load_schema("certificate.schema.json")
    valid_input = {
        "schema_version": "nq-engine-a-input-v1",
        "exposure_markers": MARKERS,
        "group": {"p": 3, "d": 1},
        "sequence": [[1], [2], [0]],
        "k": 2,
        "limits": {"max_states": 1000},
    }
    jsonschema.validate(valid_input, input_schema)
    valid_certificate = {
        "schema_version": "nq-engine-a-certificate-v1",
        "input_sha256": canonical_json_sha256(valid_input),
        "sequence_length": 3,
        "k": 2,
        "bins": [[0, 1], [2]],
    }
    jsonschema.validate(valid_certificate, certificate_schema)
    for mutation in (
        {**valid_input, "unexpected": True},
        {**valid_input, "exposure_markers": [MARKERS[0]]},
        {**valid_input, "k": 0},
        {**valid_input, "group": {"p": 1, "d": 1}},
    ):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(mutation, input_schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**valid_certificate, "bins": [[]]}, certificate_schema)


def test_receipt_promotes_only_complete_exhaustive_negative() -> None:
    spec = GroupSpec(2, 1)
    negative = find_disjoint_zero_sums(spec, [], 1)
    receipt = build_factorization_receipt(spec, (), 1, negative, full_coverage=True, **DIGESTS)
    payload = receipt.to_dict()
    assert receipt.terminal is ReceiptTerminal.ENGINEERING_NEGATIVE
    assert payload["independence_terminal"] == "CANNOT_CHECK"
    assert payload["exposure_markers"] == MARKERS
    jsonschema.validate(payload, load_schema("receipt.schema.json"))


def test_partial_or_resource_search_can_never_become_a_negative_receipt() -> None:
    spec = GroupSpec(5, 2)
    sequence = tuple(spec.elements())[:8]
    bounded = find_disjoint_zero_sums(spec, sequence, 3, max_states=2)
    receipt = build_factorization_receipt(
        spec, sequence, 3, bounded, full_coverage=False, **DIGESTS
    )
    assert receipt.terminal is ReceiptTerminal.CANNOT_CHECK_RESOURCE_BOUND
    assert not receipt.full_coverage
    assert not receipt.exhaustive

    forged_negative = replace(bounded, status=FactorizationStatus.NEGATIVE)
    forged_receipt = build_factorization_receipt(
        spec, sequence, 3, forged_negative, full_coverage=True, **DIGESTS
    )
    assert forged_receipt.terminal is ReceiptTerminal.CANNOT_CHECK_RESOURCE_BOUND


def test_invalid_positive_certificate_is_not_promoted() -> None:
    spec = GroupSpec(3, 1)
    sequence = ((1,), (2,), (0,))
    positive = find_disjoint_zero_sums(spec, sequence, 2)
    forged = replace(positive, certificate=FactorizationCertificate(bins=((0,), (2,))))
    receipt = build_factorization_receipt(spec, sequence, 2, forged, full_coverage=True, **DIGESTS)
    assert receipt.terminal is ReceiptTerminal.CANNOT_CHECK_INVALID_CERTIFICATE
    assert receipt.certificate_valid is False


def test_missing_or_malformed_digests_fail_closed() -> None:
    spec = GroupSpec(2, 1)
    result = find_disjoint_zero_sums(spec, [], 1)
    with pytest.raises(ReceiptError):
        build_factorization_receipt(
            spec,
            (),
            1,
            result,
            full_coverage=True,
            source_manifest_sha256="not-a-digest",
        )


def test_manifest_is_mtime_independent_sorted_and_detects_tamper_and_extra_sources(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "b.py").write_text("b = 2\n")
    (tmp_path / "src" / "a.py").write_text("a = 1\n")
    first = build_source_manifest(tmp_path)
    os.utime(tmp_path / "src" / "a.py", (1_000_000, 1_000_000))
    second = build_source_manifest(tmp_path)
    assert first == second
    assert [entry["path"] for entry in first["files"]] == ["src/a.py", "src/b.py"]
    assert verify_source_manifest(tmp_path, first) == ()

    (tmp_path / "src" / "a.py").write_text("a = 9\n")
    assert any("digest mismatch" in error for error in verify_source_manifest(tmp_path, first))
    (tmp_path / "src" / "a.py").write_text("a = 1\n")
    (tmp_path / "src" / "extra.py").write_text("extra = True\n")
    assert any("unmanifested source" in error for error in verify_source_manifest(tmp_path, first))


def test_manifest_schema_and_exposure_markers_are_mandatory(tmp_path: Path) -> None:
    (tmp_path / "module.py").write_text("value = 1\n")
    manifest = build_source_manifest(tmp_path)
    schema = load_schema("source-manifest.schema.json")
    jsonschema.validate(manifest, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**manifest, "exposure_markers": [MARKERS[0]]}, schema)


def test_manifest_hostile_structures_paths_and_metadata_are_rejected(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(ValueError):
        build_source_manifest(missing)

    (tmp_path / "module.py").write_text("value = 1\n")
    manifest = build_source_manifest(tmp_path)
    assert verify_source_manifest(tmp_path, None) == ("manifest structure is invalid",)

    base_entry = dict(manifest["files"][0])
    hostile_entries = [
        "not-an-entry",
        {**base_entry, "path": "../escape.py"},
        base_entry,
        base_entry,
        {"path": "missing.py", "size_bytes": 0, "sha256": "0" * 64},
    ]
    hostile = {**manifest, "files": hostile_entries, "source_tree_sha256": "0" * 64}
    errors = verify_source_manifest(tmp_path, hostile)
    assert any("invalid file entry" in error for error in errors)
    assert any("unsafe manifest path" in error for error in errors)
    assert any("duplicate manifest path" in error for error in errors)
    assert any("manifested source missing" in error for error in errors)
    assert any("source tree digest mismatch" in error for error in errors)

    metadata_mutation = {
        **manifest,
        "independence_terminal": "PASS",
        "exposure_markers": [],
        "files": [{**base_entry, "size_bytes": 999, "sha256": "0" * 64}],
    }
    errors = verify_source_manifest(tmp_path, metadata_mutation)
    assert any("size mismatch" in error for error in errors)
    assert any("digest mismatch" in error for error in errors)
    assert any("independence terminal mismatch" in error for error in errors)
    assert any("exposure marker mismatch" in error for error in errors)


def test_manifest_rejects_symlinked_source(tmp_path: Path) -> None:
    target = tmp_path / "target.py"
    target.write_text("value = 1\n")
    (tmp_path / "alias.py").symlink_to(target)
    with pytest.raises(ValueError):
        build_source_manifest(tmp_path)


def test_receipt_input_payload_limits_and_metadata_binding_are_fail_closed() -> None:
    spec = GroupSpec(2, 1)
    payload = factorization_input_payload(spec, [[0]], 1, limits={"max_states": 3})
    assert payload["limits"] == {"max_states": 3}
    with pytest.raises(ReceiptError):
        factorization_input_payload(spec, [[0]], 0)

    result = find_disjoint_zero_sums(spec, [[0]], 1)
    mismatched = replace(result, sequence_length=99)
    receipt = build_factorization_receipt(spec, [[0]], 1, mismatched, full_coverage=True, **DIGESTS)
    assert receipt.terminal is ReceiptTerminal.CANNOT_CHECK_INVALID_CERTIFICATE
    assert receipt.full_coverage is False


def test_generated_coverage_report_is_excluded_from_source_manifest(tmp_path: Path) -> None:
    (tmp_path / "module.py").write_text("value = 1\n")
    (tmp_path / "coverage.json").write_text("{}\n")
    (tmp_path / "STAGING_TREE_MANIFEST.json").write_text("{}\n")
    (tmp_path / "STAGING_DIGEST.sha256").write_text("0" * 64 + "\n")
    (tmp_path / "TARGET_RESOURCE_PILOT_RECEIPT.json").write_text("{}\n")
    (tmp_path / "TARGET_RESOURCE_PILOT_SUBMISSION_CONTRACT.json").write_text("{}\n")
    manifest = build_source_manifest(tmp_path)
    assert [entry["path"] for entry in manifest["files"]] == ["module.py"]
