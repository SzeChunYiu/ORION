#!/usr/bin/env python3
"""Verify clean-room source and sealed result bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import fiberguard_cleanroom as fg


class ReceiptMismatch(RuntimeError):
    pass


SEALED_FIELDS = {"schema", "payload", "binding", "authority"}
BINDING_FIELDS = {"payload_sha256", "manifest_sha256"}
AUTHORITY = {
    "independence_terminal": "CANNOT_CHECK",
    "comparison_to_frozen_outcomes": "NOT_PERFORMED",
    "scientific_authority_delta": "NONE",
}
FIXTURE_FIELDS = {
    "schema",
    "terminal",
    "independence_terminal",
    "blinding_breach",
    "checks",
    "full_panel_execution",
    "comparison_to_frozen_outcomes",
    "lunarc_submission",
    "scientific_authority_delta",
}
EXECUTION_FIELDS = {
    "schema",
    "panels",
    "execution_terminal",
    "independence_terminal",
    "blinding_breach",
    "comparison_to_frozen_outcomes",
    "scientific_authority_delta",
    "packet_identity",
    "execution_authorization",
    "execution_provenance",
}
PACKET_IDENTITY_FIELDS = fg.PACKET_VALIDATION_FIELDS
EXECUTION_AUTHORIZATION_FIELDS = fg.AUTHORIZATION_FIELDS | {
    "authorization_bytes",
    "authorization_sha256",
}
EXECUTION_PROVENANCE_FIELDS = {
    "schema",
    "git_commit",
    "git_tree",
    "git_status",
    "checkout_scope",
    "python_version",
    "python_executable",
    "python_implementation",
    "platform",
    "processor",
    "cpu_count",
    "workers",
    "command",
    "slurm_job_id",
    "started_at",
    "ended_at",
    "wall_time_seconds",
    "maximum_rss",
    "maximum_rss_unit",
    "maximum_rss_scope",
    "exit_code",
    "stdout_bytes",
    "stdout_sha256",
    "stderr_bytes",
    "stderr_sha256",
}


def verify_receipt(
    *,
    root: Path,
    manifest: Mapping[str, Any],
    receipt: Mapping[str, Any],
    authorization_path: Path | None = None,
) -> None:
    fg.verify_manifest(root, manifest)
    if type(receipt) is not dict or set(receipt) != SEALED_FIELDS:
        raise ReceiptMismatch("sealed receipt fields are not exact")
    if type(receipt.get("binding")) is not dict or set(receipt["binding"]) != BINDING_FIELDS:
        raise ReceiptMismatch("sealed receipt binding fields are not exact")
    if receipt.get("authority") != AUTHORITY:
        raise ReceiptMismatch("sealed receipt authority boundary mismatch")
    if not fg.verify_sealed_payload(receipt):
        raise ReceiptMismatch("sealed receipt payload hash mismatch")
    if receipt["binding"]["manifest_sha256"] != manifest["manifest_sha256"]:
        raise ReceiptMismatch("receipt manifest binding mismatch")
    payload = receipt.get("payload")
    if type(payload) is not dict:
        raise ReceiptMismatch("receipt payload schema is not an object")
    if payload.get("schema") == "ORION.FiberGuardCleanroomNonOutcomeValidation.v1":
        if set(payload) != FIXTURE_FIELDS:
            raise ReceiptMismatch("receipt payload schema is not exact")
        required = {
            "terminal": "NON_OUTCOME_FIXTURES_VALIDATED",
            "independence_terminal": "CANNOT_CHECK",
            "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
            "full_panel_execution": "NOT_RUN",
            "comparison_to_frozen_outcomes": "NOT_PERFORMED",
            "lunarc_submission": "NOT_SUBMITTED",
            "scientific_authority_delta": "NONE",
        }
        if any(payload.get(key) != value for key, value in required.items()):
            raise ReceiptMismatch("fixture receipt overstates scientific authority")
        checks = payload.get("checks")
        if (
            type(checks) is not dict
            or set(checks)
            != {
                "graph_dual_solver_fixture",
                "set_cover_dual_solver_fixture",
                "two_cnf_dual_solver_fixture",
            }
            or not all(value is True for value in checks.values())
        ):
            raise ReceiptMismatch("fixture receipt checks are not exact PASS booleans")
    elif payload.get("schema") == "ORION.FiberGuardCleanroomOutput.v1":
        if set(payload) != EXECUTION_FIELDS:
            raise ReceiptMismatch("receipt payload schema is not exact")
        required = {
            "execution_terminal": "CLEANROOM_EXHAUSTIVE_REPLAY_COMPLETED",
            "independence_terminal": "CANNOT_CHECK",
            "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
            "comparison_to_frozen_outcomes": "NOT_PERFORMED",
            "scientific_authority_delta": "NONE",
        }
        if any(payload.get(key) != value for key, value in required.items()):
            raise ReceiptMismatch("execution receipt overstates scientific authority")
        if type(payload.get("panels")) is not dict or set(payload["panels"]) != {
            "graphs",
            "set_cover",
            "two_cnf",
        }:
            raise ReceiptMismatch("execution receipt panel denominator is not exact")
        provenance = payload.get("execution_provenance")
        if type(provenance) is not dict or set(provenance) != EXECUTION_PROVENANCE_FIELDS:
            raise ReceiptMismatch("execution provenance schema is not exact")
        if provenance.get("schema") != "ORION.FiberGuardCleanroomExecutionProvenance.v1":
            raise ReceiptMismatch("execution provenance schema mismatch")
        if provenance.get("git_status") != "CLEAN":
            raise ReceiptMismatch("execution provenance checkout is dirty")
        if provenance.get("checkout_scope") not in {
            "FULL",
            "SPARSE_EXACT_FIVE_PAPER_R8",
        }:
            raise ReceiptMismatch("execution provenance checkout scope is invalid")
        if provenance.get("exit_code") != 0:
            raise ReceiptMismatch("execution provenance exit code is not zero")
        if (
            type(provenance.get("workers")) is not int
            or not 1 <= provenance["workers"] <= 16
            or type(provenance.get("command")) is not list
            or not provenance["command"]
            or type(provenance.get("maximum_rss")) is not int
            or provenance["maximum_rss"] < 0
            or provenance.get("maximum_rss_unit")
            not in {"KiB", "bytes", "CANNOT_CHECK_PLATFORM_NATIVE"}
            or provenance.get("maximum_rss_scope")
            != "RUSAGE_SELF_EXECUTOR_ONLY__EXCLUDES_CHILD_PROCESS_PEAKS"
            or type(provenance.get("wall_time_seconds")) not in {int, float}
            or provenance["wall_time_seconds"] < 0
        ):
            raise ReceiptMismatch("execution provenance resource fields are invalid")
        for stream in ("stdout", "stderr"):
            if (
                type(provenance.get(f"{stream}_bytes")) is not int
                or provenance[f"{stream}_bytes"] < 0
                or type(provenance.get(f"{stream}_sha256")) is not str
                or not fg.HEX_SHA256.fullmatch(provenance[f"{stream}_sha256"])
            ):
                raise ReceiptMismatch(f"execution provenance {stream} binding is invalid")
        packet = payload.get("packet_identity")
        if type(packet) is not dict or set(packet) != PACKET_IDENTITY_FIELDS:
            raise ReceiptMismatch("execution packet identity schema is not exact")
        subject = packet.get("scientific_subject")
        publication = packet.get("packet_publication")
        predecessor = packet.get("predecessor_packet")
        if (
            packet.get("schema") != "ORION.FivePaperR8.PacketPublicationBinding.v1"
            or packet.get("terminal") != "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND"
            or packet.get("source_ref_status") not in {"EXACT", "NOT_AVAILABLE_LOCALLY"}
            or packet.get("authority") != fg.PACKET_AUTHORITY
            or packet.get("validated_at_checkout") != provenance.get("git_commit")
            or type(subject) is not dict
            or set(subject)
            != {
                "commit",
                "tree",
                "source_branch",
                "source_ref",
                "source_ref_observed_commit",
                "exact_checkout_required",
                "scope",
            }
            or subject.get("source_branch") != "codex/five-paper-top-tier-r8-20260826"
            or subject.get("source_ref") != "refs/heads/codex/five-paper-top-tier-r8-20260826"
            or subject.get("source_ref_observed_commit") != subject.get("commit")
            or subject.get("exact_checkout_required") is not True
            or not fg.HEX_SHA1.fullmatch(str(subject.get("commit")))
            or not fg.HEX_SHA1.fullmatch(str(subject.get("tree")))
            or type(publication) is not dict
            or set(publication) != {"commit", "tree", "path", "git_blob", "sha256", "bytes"}
            or publication.get("commit") == subject.get("commit")
            or publication.get("path") != fg.PACKET_PATH.as_posix()
            or not fg.HEX_SHA1.fullmatch(str(publication.get("commit")))
            or not fg.HEX_SHA1.fullmatch(str(publication.get("tree")))
            or not fg.HEX_SHA1.fullmatch(str(publication.get("git_blob")))
            or not fg.HEX_SHA256.fullmatch(str(publication.get("sha256")))
            or type(publication.get("bytes")) is not int
            or publication["bytes"] <= 0
            or type(predecessor) is not dict
            or set(predecessor)
            != {
                "schema",
                "publication_commit",
                "publication_tree",
                "path",
                "git_blob",
                "sha256",
                "bytes",
                "preserved_path",
                "status",
            }
            or predecessor.get("schema") != "ORION.FivePaperR8.PacketCommit.v1"
            or predecessor.get("path") != fg.PACKET_PATH.as_posix()
            or predecessor.get("preserved_path")
            != "papers/five-paper-top-tier-r8/R8_PACKET_COMMIT_V1_PRESERVED.json"
            or predecessor.get("status") != "PRESERVED_AS_HISTORICAL_INVALID_SELF_REFERENCE_ATTEMPT"
            or not fg.HEX_SHA1.fullmatch(str(predecessor.get("publication_commit")))
            or not fg.HEX_SHA1.fullmatch(str(predecessor.get("publication_tree")))
            or not fg.HEX_SHA1.fullmatch(str(predecessor.get("git_blob")))
            or not fg.HEX_SHA256.fullmatch(str(predecessor.get("sha256")))
            or type(predecessor.get("bytes")) is not int
            or predecessor["bytes"] <= 0
        ):
            raise ReceiptMismatch("execution packet identity values are invalid")
        authorization = payload.get("execution_authorization")
        if type(authorization) is not dict or set(authorization) != EXECUTION_AUTHORIZATION_FIELDS:
            raise ReceiptMismatch("execution authorization schema is not exact")
        if (
            authorization.get("schema") != "ORION.FiberGuardCleanroomExecutionAuthorization.v1"
            or authorization.get("authority_terminal") != "ROOT_REVIEW_AUTHORIZED"
            or authorization.get("grants_execution_authority") is not True
            or authorization.get("grants_lunarc_submission") is not True
            or authorization.get("scientific_subject_commit") != subject["commit"]
            or authorization.get("scientific_subject_tree") != subject["tree"]
            or authorization.get("implementation_commit") != provenance["git_commit"]
            or authorization.get("implementation_tree") != provenance["git_tree"]
            or authorization.get("source_manifest_sha256") != manifest["manifest_sha256"]
            or not fg.HEX_SHA256.fullmatch(str(authorization.get("authorization_sha256")))
            or type(authorization.get("authorization_bytes")) is not int
            or authorization["authorization_bytes"] <= 0
        ):
            raise ReceiptMismatch("execution authorization binding is inconsistent")
        if authorization_path is None:
            raise ReceiptMismatch("external authorization object is required")
        try:
            authorization_bytes = authorization_path.read_bytes()
            authorization_object = json.loads(authorization_bytes)
        except (OSError, json.JSONDecodeError) as error:
            raise ReceiptMismatch("external authorization object is unavailable") from error
        embedded_object = {key: authorization[key] for key in fg.AUTHORIZATION_FIELDS}
        if (
            authorization_object != embedded_object
            or len(authorization_bytes) != authorization["authorization_bytes"]
            or hashlib.sha256(authorization_bytes).hexdigest()
            != authorization["authorization_sha256"]
        ):
            raise ReceiptMismatch("external authorization object binding mismatch")
    else:
        raise ReceiptMismatch("receipt payload schema is unknown")


def parse_args() -> argparse.Namespace:
    cleanroom = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=cleanroom)
    parser.add_argument("--manifest", type=Path, default=cleanroom / "SOURCE_MANIFEST.json")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--authorization-file", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verify_receipt(
        root=args.root,
        manifest=json.loads(args.manifest.read_text()),
        receipt=json.loads(args.receipt.read_text()),
        authorization_path=args.authorization_file,
    )
    print("FIBERGUARD_CLEANROOM_RECEIPT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
