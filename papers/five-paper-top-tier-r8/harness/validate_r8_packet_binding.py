#!/usr/bin/env python3
"""Fail-closed validator for the non-self-referential R8 packet identity pair."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_PATH = "papers/five-paper-top-tier-r8/R8_PACKET_COMMIT.json"
BINDING_PATH = "papers/five-paper-top-tier-r8/R8_PACKET_PUBLICATION_BINDING.json"
PRESERVED_PATH = "papers/five-paper-top-tier-r8/R8_PACKET_COMMIT_V1_PRESERVED.json"
PLACEHOLDER = "TO_BE_BOUND_AFTER_MATERIALIZATION"
SUBJECT_COMMIT = "0c451e862a0eeddac7c673813c4dc499f134b088"
SUBJECT_TREE = "dbf96cce53d21d25584479fb740473293fae75e0"
SOURCE_BRANCH = "codex/five-paper-top-tier-r8-20260826"
SOURCE_REF = f"refs/heads/{SOURCE_BRANCH}"
SOURCE_REMOTE_REF = f"refs/remotes/origin/{SOURCE_BRANCH}"
PUBLICATION_COMMIT = "a14dfe7872b1d3d814a0f784c359793e8bcadb3c"
PUBLICATION_TREE = "e8023f0b11b56d87ccfd222320995468ecabcef8"
PUBLICATION_BLOB = "549a0d893d17fc5f632ca5084dd92e0f0df54f4b"
PUBLICATION_SHA256 = "1e445a1627b8027c2fe64c639dace2aadfd9e6dee5040b5ca824f4261b1e90aa"
PUBLICATION_BYTES = 2214
PREDECESSOR_COMMIT = "ee685107cf537810fe17df67d7a6bd0f4c7a0116"
PREDECESSOR_TREE = "71413511e5739daeadbaf29abdbd95d8fac976e8"
PREDECESSOR_BLOB = "2712ce1797fcc78d9b5ea9bf533809b2698d106a"
PREDECESSOR_SHA256 = "f71faaea81e0a36a71a60ba7ad591682dccbe80d9e4082e02a4402e77a9f9129"
PREDECESSOR_BYTES = 222
TERMINAL = "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND"

AUTHORITY = {
    "identity_authority": "ENGINEERING_CUSTODY_ONLY",
    "scientific_disposition": "NONE",
    "paper_authority_delta": "NONE",
    "publication_readiness_delta": "NONE",
    "external_novelty": "CANNOT_CHECK",
    "grants_execution_authority": False,
    "grants_lunarc_submission": False,
}


class BindingError(RuntimeError):
    """Raised when any R8 packet identity coordinate fails closed."""


def _must(condition: bool, message: str) -> None:
    if not condition:
        raise BindingError(message)


def _expect_keys(value: Any, keys: set[str], label: str) -> Mapping[str, Any]:
    _must(isinstance(value, Mapping), f"{label} must be an object")
    actual = set(value)
    _must(actual == keys, f"{label} schema fields mismatch: {sorted(actual ^ keys)}")
    return value


def _git_bytes(root: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.PIPE
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        detail = getattr(exc, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace").strip()
        raise BindingError(f"git {' '.join(args)} failed: {detail}") from exc


def _git(root: Path, *args: str) -> str:
    return _git_bytes(root, *args).decode("utf-8").strip()


def _git_exit(root: Path, *args: str) -> int:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
    except OSError as exc:
        raise BindingError(f"git {' '.join(args)} could not run") from exc


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BindingError(f"{label} cannot be loaded: {path}") from exc
    _must(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def _check_commit_tree(root: Path, commit: str, tree: str, label: str) -> None:
    resolved = _git(root, "rev-parse", f"{commit}^{{commit}}")
    _must(resolved == commit, f"{label} commit resolution drift: {resolved}")
    resolved_tree = _git(root, "rev-parse", f"{commit}^{{tree}}")
    _must(resolved_tree == tree, f"{label} tree mismatch: {resolved_tree} != {tree}")


def _check_packet_schema(packet: Mapping[str, Any]) -> None:
    _expect_keys(
        packet,
        {
            "schema",
            "contract",
            "scientific_subject",
            "packet_publication_binding",
            "predecessor_packet",
            "reader_contract",
            "authority",
        },
        "packet",
    )
    _must(packet["schema"] == "ORION.FivePaperR8.PacketIdentity.v2", "packet schema mismatch")
    _must(
        packet["contract"] == "NON_SELF_REFERENTIAL_SUBJECT_PLUS_EXTERNAL_PUBLICATION_BINDING",
        "packet contract mismatch",
    )
    _expect_keys(
        packet["scientific_subject"],
        {
            "commit",
            "tree",
            "source_branch",
            "source_ref",
            "source_ref_observed_commit",
            "exact_checkout_required",
            "scope",
        },
        "packet scientific_subject",
    )
    _expect_keys(
        packet["packet_publication_binding"],
        {
            "mode",
            "path",
            "binding_path",
            "required_schema",
            "required_identities",
            "self_reference_forbidden",
        },
        "packet publication binding contract",
    )
    _expect_keys(
        packet["predecessor_packet"],
        {
            "schema",
            "publication_commit",
            "publication_tree",
            "path",
            "git_blob",
            "sha256",
            "bytes",
            "preserved_path",
            "status",
        },
        "packet predecessor",
    )
    _expect_keys(
        packet["reader_contract"],
        {
            "output",
            "publication_commit_is_not_scientific_subject",
            "binding_validation_required_before_output",
        },
        "packet reader contract",
    )
    _expect_keys(packet["authority"], set(AUTHORITY), "packet authority")


def _check_binding_schema(binding: Mapping[str, Any]) -> None:
    _expect_keys(
        binding,
        {
            "schema",
            "terminal",
            "scientific_subject",
            "packet_publication",
            "predecessor_packet",
            "binding_architecture",
            "authority",
        },
        "binding",
    )
    _must(
        binding["schema"] == "ORION.FivePaperR8.PacketPublicationBinding.v1",
        "binding schema mismatch",
    )
    _expect_keys(
        binding["scientific_subject"],
        {
            "commit",
            "tree",
            "source_branch",
            "source_ref",
            "source_ref_observed_commit",
            "exact_checkout_required",
            "scope",
        },
        "binding scientific_subject",
    )
    _expect_keys(
        binding["packet_publication"],
        {"commit", "tree", "path", "git_blob", "sha256", "bytes"},
        "binding packet_publication",
    )
    _expect_keys(
        binding["predecessor_packet"],
        {
            "schema",
            "publication_commit",
            "publication_tree",
            "path",
            "git_blob",
            "sha256",
            "bytes",
            "preserved_path",
            "status",
        },
        "binding predecessor",
    )
    _expect_keys(
        binding["binding_architecture"],
        {
            "scientific_subject_is_distinct_from_packet_publication",
            "packet_publication_is_bound_by_successor_record",
            "binding_record_self_identity_excluded",
            "reader_returns",
            "exact_checkout_resolution_required",
        },
        "binding architecture",
    )
    _expect_keys(binding["authority"], set(AUTHORITY), "binding authority")


def validate_binding(
    root: Path,
    *,
    packet: Mapping[str, Any] | None = None,
    binding: Mapping[str, Any] | None = None,
    require_source_ref: bool = False,
) -> dict[str, Any]:
    """Validate packet subject, publication, predecessor, ref, and authority identities."""
    root = root.resolve()
    packet_object = dict(packet) if packet is not None else _load_object(root / PACKET_PATH, "packet")
    binding_object = dict(binding) if binding is not None else _load_object(root / BINDING_PATH, "binding")
    _must(PLACEHOLDER not in json.dumps(packet_object, sort_keys=True), "successor packet contains forbidden placeholder")
    _must(PLACEHOLDER not in json.dumps(binding_object, sort_keys=True), "publication binding contains forbidden placeholder")
    _check_packet_schema(packet_object)
    _check_binding_schema(binding_object)

    subject = packet_object["scientific_subject"]
    bound_subject = binding_object["scientific_subject"]
    _must(subject == bound_subject, "scientific subject differs between packet and binding")
    _must(subject["commit"] == SUBJECT_COMMIT, "scientific subject commit mismatch")
    _must(subject["tree"] == SUBJECT_TREE, "scientific subject tree mismatch")
    _must(subject["source_branch"] == SOURCE_BRANCH, "scientific subject source branch mismatch")
    _must(subject["source_ref"] == SOURCE_REF, "scientific subject source ref path mismatch")
    _must(
        subject["source_ref_observed_commit"] == SUBJECT_COMMIT,
        "scientific subject source ref drift",
    )
    _must(subject["exact_checkout_required"] is True, "exact subject checkout is not required")

    packet_contract = packet_object["packet_publication_binding"]
    _must(packet_contract["mode"] == "EXTERNAL_SUCCESSOR_RECORD", "packet publication mode mismatch")
    _must(packet_contract["path"] == PACKET_PATH, "packet publication contract path mismatch")
    _must(packet_contract["binding_path"] == BINDING_PATH, "packet binding path mismatch")
    _must(
        packet_contract["required_schema"]
        == "ORION.FivePaperR8.PacketPublicationBinding.v1",
        "packet required binding schema mismatch",
    )
    _must(
        packet_contract["required_identities"]
        == ["commit", "tree", "path", "git_blob", "sha256", "bytes"],
        "packet publication identity list mismatch",
    )
    _must(packet_contract["self_reference_forbidden"] is True, "packet self-reference is not forbidden")

    publication = binding_object["packet_publication"]
    _must(publication["commit"] == PUBLICATION_COMMIT, "packet publication commit mismatch")
    _must(publication["tree"] == PUBLICATION_TREE, "packet publication tree mismatch")
    _must(publication["path"] == PACKET_PATH, "packet publication path mismatch")
    _must(publication["git_blob"] == PUBLICATION_BLOB, "packet publication blob mismatch")
    _must(publication["sha256"] == PUBLICATION_SHA256, "packet publication SHA-256 mismatch")
    _must(publication["bytes"] == PUBLICATION_BYTES, "packet publication byte count mismatch")
    _must(publication["commit"] != subject["commit"], "subject and publication commits were conflated")

    predecessor = packet_object["predecessor_packet"]
    _must(predecessor == binding_object["predecessor_packet"], "predecessor packet binding mismatch")
    expected_predecessor = {
        "schema": "ORION.FivePaperR8.PacketCommit.v1",
        "publication_commit": PREDECESSOR_COMMIT,
        "publication_tree": PREDECESSOR_TREE,
        "path": PACKET_PATH,
        "git_blob": PREDECESSOR_BLOB,
        "sha256": PREDECESSOR_SHA256,
        "bytes": PREDECESSOR_BYTES,
        "preserved_path": PRESERVED_PATH,
        "status": "PRESERVED_AS_HISTORICAL_INVALID_SELF_REFERENCE_ATTEMPT",
    }
    _must(predecessor == expected_predecessor, "predecessor packet identity mismatch")

    reader = packet_object["reader_contract"]
    _must(reader["output"] == "scientific_subject.commit", "reader output contract mismatch")
    _must(reader["publication_commit_is_not_scientific_subject"] is True, "reader conflates publication and subject")
    _must(reader["binding_validation_required_before_output"] is True, "reader can bypass binding validation")
    architecture = binding_object["binding_architecture"]
    expected_architecture = {
        "scientific_subject_is_distinct_from_packet_publication": True,
        "packet_publication_is_bound_by_successor_record": True,
        "binding_record_self_identity_excluded": True,
        "reader_returns": "scientific_subject.commit",
        "exact_checkout_resolution_required": True,
    }
    _must(architecture == expected_architecture, "binding architecture mismatch")
    _must(binding_object["terminal"] == TERMINAL, "packet binding terminal mismatch")
    _must(packet_object["authority"] == AUTHORITY, "packet authority boundary mismatch")
    _must(binding_object["authority"] == AUTHORITY, "binding authority boundary mismatch")

    _check_commit_tree(root, SUBJECT_COMMIT, SUBJECT_TREE, "scientific subject")
    _check_commit_tree(root, PUBLICATION_COMMIT, PUBLICATION_TREE, "packet publication")
    _check_commit_tree(root, PREDECESSOR_COMMIT, PREDECESSOR_TREE, "predecessor packet publication")
    _must(
        _git_exit(root, "merge-base", "--is-ancestor", SUBJECT_COMMIT, PUBLICATION_COMMIT) == 0,
        "packet publication does not descend from scientific subject",
    )
    head = _git(root, "rev-parse", "HEAD")
    _must(
        _git_exit(root, "merge-base", "--is-ancestor", PUBLICATION_COMMIT, head) == 0,
        "current checkout does not descend from packet publication",
    )

    published_bytes = _git_bytes(root, "show", f"{PUBLICATION_COMMIT}:{PACKET_PATH}")
    current_bytes = (root / PACKET_PATH).read_bytes()
    _must(current_bytes == published_bytes, "current packet bytes differ from publication commit")
    _must(len(published_bytes) == PUBLICATION_BYTES, "published packet byte count mismatch")
    _must(_sha256(published_bytes) == PUBLICATION_SHA256, "published packet SHA-256 mismatch")
    _must(_git_blob(published_bytes) == PUBLICATION_BLOB, "published packet blob mismatch")
    _must(
        _git(root, "rev-parse", f"{PUBLICATION_COMMIT}:{PACKET_PATH}")
        == PUBLICATION_BLOB,
        "publication commit path does not resolve to packet blob",
    )

    predecessor_bytes = _git_bytes(root, "show", f"{PREDECESSOR_COMMIT}:{PACKET_PATH}")
    preserved_bytes = (root / PRESERVED_PATH).read_bytes()
    _must(preserved_bytes == predecessor_bytes, "predecessor packet bytes were not preserved")
    _must(len(predecessor_bytes) == PREDECESSOR_BYTES, "predecessor packet byte count mismatch")
    _must(_sha256(predecessor_bytes) == PREDECESSOR_SHA256, "predecessor packet SHA-256 mismatch")
    _must(_git_blob(predecessor_bytes) == PREDECESSOR_BLOB, "predecessor packet blob mismatch")
    _must(
        _git(root, "rev-parse", f"{PREDECESSOR_COMMIT}:{PACKET_PATH}")
        == PREDECESSOR_BLOB,
        "predecessor commit path does not resolve to packet blob",
    )

    source_ref_exists = _git_exit(root, "show-ref", "--verify", "--quiet", SOURCE_REMOTE_REF) == 0
    if require_source_ref:
        _must(source_ref_exists, f"required source ref is unavailable: {SOURCE_REMOTE_REF}")
    if source_ref_exists:
        resolved_source_ref = _git(root, "rev-parse", SOURCE_REMOTE_REF)
        _must(
            resolved_source_ref == SUBJECT_COMMIT,
            f"source ref drift: {SOURCE_REMOTE_REF} -> {resolved_source_ref}",
        )

    return {
        "schema": binding_object["schema"],
        "terminal": TERMINAL,
        "scientific_subject": dict(subject),
        "packet_publication": dict(publication),
        "predecessor_packet": dict(predecessor),
        "authority": dict(AUTHORITY),
        "validated_at_checkout": head,
        "source_ref_status": "EXACT" if source_ref_exists else "NOT_AVAILABLE_LOCALLY",
    }


def resolve_subject_checkout(root: Path, *, require_source_ref: bool = False) -> str:
    result = validate_binding(root, require_source_ref=require_source_ref)
    commit = result["scientific_subject"]["commit"]
    _must(_git(root, "rev-parse", f"{commit}^{{tree}}") == SUBJECT_TREE, "resolved checkout tree mismatch")
    return str(commit)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--require-source-ref", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = validate_binding(args.repo_root, require_source_ref=args.require_source_ref)
    except BindingError as exc:
        print(f"R8_PACKET_BINDING_INVALID: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
