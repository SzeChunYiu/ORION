from __future__ import annotations

import json
import os

import pytest

import orion.study.p5.freeze_cli as freeze_cli


def _protected(path) -> bytes:
    payload = b'{"protected":"truth"}\n'
    path.write_bytes(payload)
    return payload


def _fake_freeze(_: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    return (
        {"schema_version": "candidate", "empirical_authority": "NONE"},
        {"schema_version": "commitment", "empirical_authority": "CANNOT_CHECK"},
    )


def _args(protected, candidate, commitment) -> list[str]:
    return [
        "--protected-suite",
        str(protected),
        "--candidate-packet",
        str(candidate),
        "--commitment",
        str(commitment),
    ]


def test_candidate_output_cannot_alias_protected_input(tmp_path, monkeypatch) -> None:
    protected = tmp_path / "protected.json"
    original = _protected(protected)
    commitment = tmp_path / "commitment.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(ValueError, match="paths must be distinct"):
        freeze_cli.main(_args(protected, protected, commitment))

    assert protected.read_bytes() == original
    assert not commitment.exists()


def test_candidate_and_commitment_cannot_alias_each_other(tmp_path, monkeypatch) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    output = tmp_path / "same.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(ValueError, match="paths must be distinct"):
        freeze_cli.main(_args(protected, output, output))

    assert not output.exists()


def test_existing_output_is_never_overwritten_and_other_reservation_rolls_back(
    tmp_path, monkeypatch
) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    candidate = tmp_path / "candidate.json"
    commitment = tmp_path / "commitment.json"
    commitment.write_bytes(b"existing commitment")
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(FileExistsError):
        freeze_cli.main(_args(protected, candidate, commitment))

    assert not candidate.exists()
    assert commitment.read_bytes() == b"existing commitment"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_output_symlink_is_not_followed(tmp_path, monkeypatch) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    target = tmp_path / "outside.json"
    target.write_bytes(b"do not overwrite")
    candidate = tmp_path / "candidate.json"
    candidate.symlink_to(target)
    commitment = tmp_path / "commitment.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(FileExistsError):
        freeze_cli.main(_args(protected, candidate, commitment))

    assert target.read_bytes() == b"do not overwrite"
    assert candidate.is_symlink()
    assert not commitment.exists()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_output_parent_symlink_is_not_traversed(tmp_path, monkeypatch) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(outside, target_is_directory=True)
    commitment = tmp_path / "commitment.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(OSError):
        freeze_cli.main(_args(protected, linked / "candidate.json", commitment))

    assert not (outside / "candidate.json").exists()
    assert not commitment.exists()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_protected_input_symlink_is_not_followed(tmp_path, monkeypatch) -> None:
    real = tmp_path / "real-protected.json"
    _protected(real)
    protected = tmp_path / "protected-link.json"
    protected.symlink_to(real)
    candidate = tmp_path / "candidate.json"
    commitment = tmp_path / "commitment.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    with pytest.raises(OSError):
        freeze_cli.main(_args(protected, candidate, commitment))

    assert not candidate.exists()
    assert not commitment.exists()


def test_happy_path_creates_nested_outputs_once_with_expected_payloads(
    tmp_path, monkeypatch
) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    candidate = tmp_path / "artifacts" / "candidate.json"
    commitment = tmp_path / "artifacts" / "nested" / "commitment.json"
    monkeypatch.setattr(freeze_cli, "freeze_protected_suite", _fake_freeze)

    assert freeze_cli.main(_args(protected, candidate, commitment)) == 0

    assert json.loads(candidate.read_text()) == {
        "schema_version": "candidate",
        "empirical_authority": "NONE",
    }
    assert json.loads(commitment.read_text()) == {
        "schema_version": "commitment",
        "empirical_authority": "CANNOT_CHECK",
    }
    assert (candidate.stat().st_mode & 0o777) == 0o600
    assert (commitment.stat().st_mode & 0o777) == 0o600


def test_missing_secure_descriptor_operations_fail_closed(tmp_path, monkeypatch) -> None:
    protected = tmp_path / "protected.json"
    _protected(protected)
    monkeypatch.setattr(freeze_cli, "_secure_open_supported", lambda: False)

    with pytest.raises(RuntimeError, match="secure descriptor-relative"):
        freeze_cli.main(
            _args(
                protected,
                tmp_path / "candidate.json",
                tmp_path / "commitment.json",
            )
        )
