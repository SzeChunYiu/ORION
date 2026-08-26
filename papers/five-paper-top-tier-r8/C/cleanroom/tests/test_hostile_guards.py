from __future__ import annotations

import json
from pathlib import Path

import pytest

import fiberguard_cleanroom as fg


def test_manifest_builder_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-cleanroom.txt"
    outside.write_text("not clean-room source\n")
    (tmp_path / "escape.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        fg.build_manifest(tmp_path, ("escape.txt",))


def test_manifest_verifier_rejects_noncanonical_record_shape(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\n")
    manifest = fg.build_manifest(tmp_path, ("a.txt",))
    manifest["files"][0]["unbound_field"] = "ambiguous"
    with pytest.raises(fg.ManifestMismatch, match="record shape"):
        fg.verify_manifest(tmp_path, manifest)


def test_manifest_verifier_rejects_duplicate_or_unsorted_paths(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\n")
    (tmp_path / "b.txt").write_text("b\n")
    manifest = fg.build_manifest(tmp_path, ("a.txt", "b.txt"))
    manifest["files"] = [manifest["files"][1], manifest["files"][0]]
    core = {"schema": manifest["schema"], "files": manifest["files"]}
    manifest["manifest_sha256"] = (
        __import__("hashlib").sha256(fg.canonical_json_bytes(core)).hexdigest()
    )
    with pytest.raises(fg.ManifestMismatch, match="sorted"):
        fg.verify_manifest(tmp_path, manifest)

    duplicate = fg.build_manifest(tmp_path, ("a.txt", "b.txt"))
    duplicate["files"] = [duplicate["files"][0], duplicate["files"][0]]
    core = {"schema": duplicate["schema"], "files": duplicate["files"]}
    duplicate["manifest_sha256"] = (
        __import__("hashlib").sha256(fg.canonical_json_bytes(core)).hexdigest()
    )
    with pytest.raises(fg.ManifestMismatch, match="unique"):
        fg.verify_manifest(tmp_path, duplicate)


def test_packet_gate_rejects_noncanonical_and_symlinked_paths(tmp_path: Path) -> None:
    packet_path = tmp_path / "R8_PACKET_COMMIT.json"
    base = {
        "schema": "ORION.FivePaperR8.PacketCommit.v1",
        "packet_commit": "1" * 40,
        "base_commit": "2" * 40,
        "branch": "codex/five-paper-top-tier-r8-20260826",
    }
    packet_path.write_text(json.dumps({**base, "unexpected": "field"}))
    with pytest.raises(fg.PacketIdentityMismatch, match="canonical v2 packet"):
        fg.require_packet_identity(packet_path, repository=tmp_path)

    canonical = tmp_path / fg.PACKET_PATH
    canonical.parent.mkdir(parents=True)
    canonical.symlink_to(packet_path)
    with pytest.raises(fg.PacketIdentityMismatch, match="canonical v2 packet"):
        fg.require_packet_identity(canonical, repository=tmp_path)


def test_audit_rejects_boolean_and_negative_targets() -> None:
    common = {
        "instances": (1,),
        "representation": lambda value: (value,),
        "candidates": {},
        "serialize_instance": lambda value: value,
        "endpoint_checker": lambda value: {"representation": (value,), "target": value},
    }
    with pytest.raises(TypeError, match="integer"):
        fg.audit_records(
            target_solvers=(lambda _: True, lambda _: True),
            **common,
        )
    with pytest.raises(ValueError, match="nonnegative"):
        fg.audit_records(
            target_solvers=(lambda _: -1, lambda _: -1),
            **common,
        )


def test_sealing_breaks_input_aliases() -> None:
    payload = {"values": [1, 2]}
    sealed = fg.seal_payload(payload, manifest_sha256="a" * 64)
    payload["values"][0] = 999
    assert sealed["payload"] == {"values": [1, 2]}
    assert fg.verify_sealed_payload(sealed)
