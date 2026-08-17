from __future__ import annotations

import json
import pathlib

from orion.study.p1.execution_freeze import (
    STATISTICAL_MODULES,
    FreezeStatus,
    build_manifest,
    statistical_code_hash,
)

REPO = pathlib.Path(__file__).resolve().parents[3]


def test_the_real_protocol_is_execution_frozen() -> None:
    """Every scientific identity is bound: protocol, subject revision, both
    suite fingerprints, subject model and the statistical code."""

    manifest = build_manifest(repo_root=REPO)
    assert manifest.status is FreezeStatus.EXECUTION_FROZEN, manifest.unresolved
    assert manifest.permits_outcome_access


def test_a_credential_is_not_a_scientific_identity() -> None:
    """Deliberately absent from the manifest. A credential is a runtime secret,
    and requiring it here would conflate "we do not know what we are measuring"
    with "we cannot reach the provider" — two states this study has to keep
    apart, since only the first should block a freeze."""

    fields = set(build_manifest(repo_root=REPO).to_dict())
    assert not any("credential" in name or "api_key" in name for name in fields)


def test_an_unbound_dataset_blocks_the_freeze(tmp_path) -> None:
    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "m",
                    "dataset_revisions": {"hidden_shift_suite_test": "UNBOUND_FINAL_HASH"},
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.IDENTITIES_UNRESOLVED
    assert any("dataset_unbound" in item for item in manifest.unresolved)
    assert not manifest.permits_outcome_access


def test_a_bound_hash_that_contradicts_the_suite_is_worse_than_an_unbound_one(tmp_path) -> None:
    """An unbound dataset says nothing. A bound hash that does not match the
    files on disk asserts an identity the artifacts contradict, which is a
    stronger and more misleading claim."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "m",
                    "dataset_revisions": {
                        "hidden_shift_suite_pilot": "0" * 64,
                        "hidden_shift_suite_test": "0" * 64,
                    },
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert any("dataset_hash_mismatch" in item for item in manifest.unresolved)


def test_outcome_access_cannot_be_undone(tmp_path) -> None:
    """Nothing re-freezes after outcomes are read. The honest record is that
    the run is not outcome-blind, and no later binding changes that."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps({"protocol_version": "t", "outcome_accessed": True, "execution_bindings": {}})
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.OUTCOME_ALREADY_ACCESSED
    assert not manifest.permits_outcome_access


def test_the_statistical_code_is_part_of_the_identity() -> None:
    """The same archive scored by different statistics is a different result.
    A manifest pinning only the data would not say so."""

    baseline = statistical_code_hash(REPO)
    assert len(baseline) == 64
    assert statistical_code_hash(REPO) == baseline
    assert any("statistics.py" in item for item in STATISTICAL_MODULES)


def test_the_frozen_split_is_gated_and_the_pilot_is_not() -> None:
    """PILOT is exempt by design: the protocol designates it for debugging and
    variance estimation, and gating it would make the freeze unreachable, since
    the pilot is how the machinery gets working at all."""

    import inspect

    from orion.study.p1 import run_trial

    source = inspect.getsource(run_trial)
    assert "if split is Split.TEST:" in source
    assert "permits_outcome_access" in source
