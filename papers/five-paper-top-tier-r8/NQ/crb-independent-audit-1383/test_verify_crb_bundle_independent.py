from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from verify_crb_bundle_independent import (  # noqa: E402
    CONTRACT_VERSION,
    VerificationError,
    normalize_sequence,
    verify_bundle,
)


CANONICAL_ZERO_AND_BASIS = [
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
]
CANONICAL_DUPLICATED_BASIS_VECTOR = [
    [0, 0, 1],
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
]


def _json_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _make_checker(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib\n"
        "import sys\n"
        "proof = pathlib.Path(sys.argv[2]).read_bytes()\n"
        "raise SystemExit(0 if proof == b'VALID\\n' else 9)\n",
        encoding="utf-8",
    )
    os.chmod(path, 0o755)


def _record(ordinal: int, representative: list[list[int]], outcome: str) -> dict[str, object]:
    return {
        "ordinal": ordinal,
        "representative": representative,
        "representative_sha256": _json_sha256(representative),
        "outcome": outcome,
    }


def _make_valid_bundle(tmp_path: Path) -> tuple[Path, Path, dict[str, object]]:
    bundle_root = tmp_path / "bundle"
    cnf_root = bundle_root / "cnf"
    proof_root = bundle_root / "proofs"
    cnf_root.mkdir(parents=True)
    proof_root.mkdir()

    checker = tmp_path / "external-checker"
    _make_checker(checker)

    cnf = cnf_root / "case-0001.cnf"
    proof = proof_root / "case-0001.drat"
    cnf.write_text("p cnf 1 2\n1 0\n-1 0\n", encoding="ascii")
    proof.write_text("VALID\n", encoding="ascii")

    sat = _record(0, CANONICAL_ZERO_AND_BASIS, "SAT")
    unsat = _record(1, CANONICAL_DUPLICATED_BASIS_VECTOR, "UNSAT")
    unsat["proof"] = {
        "proof_id": "proof-0001",
        "proof_format": "DRAT",
        "cnf_path": "cnf/case-0001.cnf",
        "cnf_bytes": cnf.stat().st_size,
        "cnf_sha256": _file_sha256(cnf),
        "proof_path": "proofs/case-0001.drat",
        "proof_bytes": proof.stat().st_size,
        "proof_sha256": _file_sha256(proof),
    }

    manifest: dict[str, object] = {
        "contract_version": CONTRACT_VERSION,
        "field": {"order": 5, "vector_dimension": 3},
        "domain": {"size": 2, "sequence_length": 4},
        "aggregate": {
            "record_count": 2,
            "outcomes": {"SAT": 1, "UNSAT": 1},
        },
        "proof_root": "proofs",
        "external_checker": {
            "sha256": _file_sha256(checker),
        },
        "partitions": [
            {
                "partition_id": "partition-0000",
                "start": 0,
                "stop": 1,
                "range_sha256": _json_sha256([0, 1]),
                "record_count": 1,
                "records": [sat],
            },
            {
                "partition_id": "partition-0001",
                "start": 1,
                "stop": 2,
                "range_sha256": _json_sha256([1, 2]),
                "record_count": 1,
                "records": [unsat],
            },
        ],
    }
    manifest_path = bundle_root / "CRB_BUNDLE.json"
    _write_json(manifest_path, manifest)
    return manifest_path, checker, manifest


def _rewrite_manifest(path: Path, manifest: dict[str, object]) -> None:
    _write_json(path, manifest)


def _verify(manifest_path: Path, checker: Path) -> dict[str, object]:
    return verify_bundle(
        manifest_path,
        checker,
        checker_sha256=_file_sha256(checker),
    )


def test_normalization_is_independent_of_basis_scaling_and_sequence_order() -> None:
    hostile_order_and_basis = [
        [0, 3, 0],
        [0, 0, 0],
        [2, 0, 0],
        [0, 0, 4],
    ]

    assert normalize_sequence(hostile_order_and_basis) == tuple(
        tuple(vector) for vector in CANONICAL_ZERO_AND_BASIS
    )


def test_normalization_rejects_rank_deficient_input() -> None:
    with pytest.raises(VerificationError, match="full rank"):
        normalize_sequence([[1, 0, 0], [2, 0, 0], [0, 1, 0], [0, 2, 0]])


def test_valid_bundle_checks_every_unsat_with_the_pinned_external_checker(tmp_path: Path) -> None:
    manifest_path, checker, _ = _make_valid_bundle(tmp_path)

    report = _verify(manifest_path, checker)

    assert report == {
        "authority": "internal_conformance_only",
        "checker_sha256": _file_sha256(checker),
        "partitions_checked": 2,
        "proofs_checked": 1,
        "records_checked": 2,
    }


def test_noncanonical_claimed_representative_fails_closed(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    record = manifest["partitions"][0]["records"][0]  # type: ignore[index]
    noncanonical = [[2, 0, 0], [0, 3, 0], [0, 0, 4], [0, 0, 0]]
    record["representative"] = noncanonical
    record["representative_sha256"] = _json_sha256(noncanonical)
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="not canonical"):
        _verify(manifest_path, checker)


@pytest.mark.parametrize(
    ("start", "stop", "domain_size", "message"),
    [
        (2, 3, 3, "gap"),
        (0, 1, 2, "overlap"),
    ],
)
def test_partition_gap_or_overlap_fails_closed(
    tmp_path: Path, start: int, stop: int, domain_size: int, message: str
) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    second = manifest["partitions"][1]  # type: ignore[index]
    second["start"] = start
    second["stop"] = stop
    second["range_sha256"] = _json_sha256([start, stop])
    manifest["domain"]["size"] = domain_size  # type: ignore[index]
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match=message):
        _verify(manifest_path, checker)


def test_duplicate_canonical_representative_fails_closed(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    second_record = manifest["partitions"][1]["records"][0]  # type: ignore[index]
    second_record["representative"] = CANONICAL_ZERO_AND_BASIS
    second_record["representative_sha256"] = _json_sha256(CANONICAL_ZERO_AND_BASIS)
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="duplicate representative"):
        _verify(manifest_path, checker)


def test_missing_listed_proof_fails_closed(tmp_path: Path) -> None:
    manifest_path, checker, _ = _make_valid_bundle(tmp_path)
    (manifest_path.parent / "proofs/case-0001.drat").unlink()

    with pytest.raises(VerificationError, match="missing proof"):
        _verify(manifest_path, checker)


def test_unlisted_extra_proof_fails_closed(tmp_path: Path) -> None:
    manifest_path, checker, _ = _make_valid_bundle(tmp_path)
    (manifest_path.parent / "proofs/extra.drup").write_text("VALID\n", encoding="ascii")

    with pytest.raises(VerificationError, match="unlisted proof"):
        _verify(manifest_path, checker)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("cnf_sha256", "CNF hash mismatch"),
        ("proof_sha256", "proof hash mismatch"),
    ],
)
def test_bad_cnf_or_proof_hash_fails_closed(tmp_path: Path, field: str, message: str) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    proof_binding = manifest["partitions"][1]["records"][0]["proof"]  # type: ignore[index]
    proof_binding[field] = "0" * 64
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match=message):
        _verify(manifest_path, checker)


def test_external_checker_rejection_fails_closed(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    proof_path = manifest_path.parent / "proofs/case-0001.drat"
    proof_path.write_text("REJECT\n", encoding="ascii")
    proof_binding = manifest["partitions"][1]["records"][0]["proof"]  # type: ignore[index]
    proof_binding["proof_bytes"] = proof_path.stat().st_size
    proof_binding["proof_sha256"] = _file_sha256(proof_path)
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="external checker rejected"):
        _verify(manifest_path, checker)


def test_checker_binary_hash_mismatch_fails_before_proof_checks(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    manifest["external_checker"]["sha256"] = "f" * 64  # type: ignore[index]
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="checker hash mismatch"):
        _verify(manifest_path, checker)


def test_same_proof_cannot_be_reused_for_a_second_cnf(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    first_record = manifest["partitions"][0]["records"][0]  # type: ignore[index]
    first_record["outcome"] = "UNSAT"
    first_record["proof"] = dict(
        manifest["partitions"][1]["records"][0]["proof"]  # type: ignore[index]
    )
    manifest["aggregate"]["outcomes"] = {"SAT": 0, "UNSAT": 2}  # type: ignore[index]
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="reused proof"):
        _verify(manifest_path, checker)


def test_manifest_cannot_repin_a_modified_checker(tmp_path: Path) -> None:
    manifest_path, checker, manifest = _make_valid_bundle(tmp_path)
    independent_pin = _file_sha256(checker)
    checker.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    os.chmod(checker, 0o755)
    manifest["external_checker"]["sha256"] = _file_sha256(checker)  # type: ignore[index]
    _rewrite_manifest(manifest_path, manifest)

    with pytest.raises(VerificationError, match="independent pin"):
        verify_bundle(
            manifest_path,
            checker,
            checker_sha256=independent_pin,
        )


def test_contract_is_machine_readable_and_freezes_the_expected_shape() -> None:
    contract = json.loads((HERE / "CRB_INDEPENDENT_BUNDLE_CONTRACT.json").read_text())

    assert contract["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert contract["properties"]["contract_version"]["const"] == CONTRACT_VERSION
    assert set(contract["required"]) == {
        "contract_version",
        "field",
        "domain",
        "aggregate",
        "proof_root",
        "external_checker",
        "partitions",
    }
