from __future__ import annotations

from copy import deepcopy
from typing import Any

from orion.study.p5.v2_evidence import content_digest, validate_result_archive


CHAIN_PROTOCOL_SCHEMA = "orion.p5.negative-history-chain-protocol.v1"
CHAIN_DOCUMENT_SCHEMA = "orion.p5.negative-history-chain.v1"
GENESIS_SCHEMA = "orion.p5.negative-history-genesis.v1"
LINK_SCHEMA = "orion.p5.negative-history-link.v1"
_HEX = frozenset("0123456789abcdef")


def _sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in _HEX for character in value)
    )


def _record_link_payload(
    record: dict[str, Any],
    *,
    sequence: int,
    previous_chain_hash: str,
) -> dict[str, Any]:
    return {
        "schema": LINK_SCHEMA,
        "sequence": sequence,
        "previous_chain_hash": previous_chain_hash,
        "result_id": record.get("result_id"),
        "system_id": record.get("system_id"),
        "episode_id": record.get("episode_id"),
        "seed": record.get("seed"),
        "candidate_id": record.get("candidate_id"),
        "stage": record.get("stage"),
        "sequence_index": record.get("sequence_index"),
        "negative_history_digest": record.get("negative_history_digest"),
    }


def negative_history_genesis(manifest: dict[str, Any]) -> str:
    return content_digest(
        {
            "schema": GENESIS_SCHEMA,
            "run_manifest_hash": content_digest(manifest),
            "negative_history_root_hash": manifest.get("negative_history_root_hash"),
        }
    )


def build_negative_history_chain(
    manifest: dict[str, Any],
    archive: dict[str, Any],
) -> dict[str, Any]:
    """Build the host-custody append transcript for the archive's current record order.

    This builder is deterministic, but determinism is not authority. The returned
    document only becomes admissible when an external host freezes its document
    hash and later supplies that expected hash to verification.
    """

    records = archive.get("records")
    if not isinstance(records, list):
        raise ValueError("result archive records must be a list")

    run_manifest_hash = content_digest(manifest)
    root_hash = manifest.get("negative_history_root_hash")
    if not _sha256(root_hash):
        raise ValueError("manifest negative_history_root_hash must be SHA-256")

    genesis_hash = negative_history_genesis(manifest)
    tip = genesis_hash
    links: list[dict[str, Any]] = []
    for sequence, raw_record in enumerate(records):
        if not isinstance(raw_record, dict):
            raise ValueError(f"records[{sequence}] must be an object")
        digest = raw_record.get("negative_history_digest")
        if not _sha256(digest):
            raise ValueError(
                f"records[{sequence}].negative_history_digest must be SHA-256"
            )
        payload = _record_link_payload(
            raw_record,
            sequence=sequence,
            previous_chain_hash=tip,
        )
        link_hash = content_digest(payload)
        links.append({**payload, "link_hash": link_hash})
        tip = link_hash

    document: dict[str, Any] = {
        "schema_version": CHAIN_DOCUMENT_SCHEMA,
        "run_manifest_hash": run_manifest_hash,
        "negative_history_root_hash": root_hash,
        "genesis_hash": genesis_hash,
        "links": links,
        "final_chain_hash": tip,
    }
    document["document_hash"] = content_digest(document)
    return document


def verify_negative_history_chain(
    document: dict[str, Any],
    manifest: dict[str, Any],
    archive: dict[str, Any],
    *,
    expected_document_hash: str,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not _sha256(expected_document_hash):
        errors.append("expected negative-history document hash must be SHA-256")

    if not isinstance(document, dict):
        return tuple(errors + ["negative-history chain document must be an object"])
    if document.get("schema_version") != CHAIN_DOCUMENT_SCHEMA:
        errors.append("wrong negative-history chain schema_version")

    claimed_document_hash = document.get("document_hash")
    if not _sha256(claimed_document_hash):
        errors.append("negative-history document_hash must be SHA-256")
    else:
        unsigned = deepcopy(document)
        unsigned.pop("document_hash", None)
        actual_document_hash = content_digest(unsigned)
        if claimed_document_hash != actual_document_hash:
            errors.append("negative-history document_hash mismatch")
        if claimed_document_hash != expected_document_hash:
            errors.append("negative-history document identity mismatch")

    manifest_hash = content_digest(manifest)
    if document.get("run_manifest_hash") != manifest_hash:
        errors.append("negative-history run_manifest_hash mismatch")
    root_hash = manifest.get("negative_history_root_hash")
    if document.get("negative_history_root_hash") != root_hash:
        errors.append("negative-history root hash mismatch")

    expected_genesis = negative_history_genesis(manifest)
    if document.get("genesis_hash") != expected_genesis:
        errors.append("negative-history genesis mismatch")

    records = archive.get("records")
    if not isinstance(records, list):
        errors.append("result archive records must be a list")
        records = []
    links = document.get("links")
    if not isinstance(links, list):
        errors.append("negative-history links must be a list")
        links = []
    if len(links) != len(records):
        errors.append("negative-history link count does not match archive records")

    tip = expected_genesis
    for sequence, (record, link) in enumerate(zip(records, links)):
        if not isinstance(record, dict) or not isinstance(link, dict):
            errors.append(f"negative-history link {sequence} must bind object record/link")
            continue
        expected_payload = _record_link_payload(
            record,
            sequence=sequence,
            previous_chain_hash=tip,
        )
        for key, expected in expected_payload.items():
            if link.get(key) != expected:
                errors.append(f"negative-history link {sequence} mismatch:{key}")
        claimed_link_hash = link.get("link_hash")
        if not _sha256(claimed_link_hash):
            errors.append(f"negative-history link {sequence} hash must be SHA-256")
            continue
        actual_link_hash = content_digest(expected_payload)
        if claimed_link_hash != actual_link_hash:
            errors.append(f"negative-history link {sequence} hash mismatch")
        tip = actual_link_hash

    if document.get("final_chain_hash") != tip:
        errors.append("negative-history final chain hash mismatch")
    if archive.get("finalized") is True:
        if archive.get("final_negative_history_hash") != tip:
            errors.append(
                "finalized archive final_negative_history_hash is not the verified chain tip"
            )

    return tuple(dict.fromkeys(errors))


def validate_result_archive_with_negative_history(
    archive: dict[str, Any],
    manifest: dict[str, Any],
    protocol: dict[str, Any],
    chain_document: dict[str, Any],
    *,
    expected_chain_document_hash: str,
) -> dict[str, Any]:
    """Add the prospective host-custody chain gate to the existing V2 validator."""

    report = validate_result_archive(archive, manifest, protocol)
    chain_errors = verify_negative_history_chain(
        chain_document,
        manifest,
        archive,
        expected_document_hash=expected_chain_document_hash,
    )
    combined = list(report.get("errors", ())) + list(chain_errors)
    result = dict(report)
    result["errors"] = combined
    result["negative_history_chain_document_hash"] = chain_document.get("document_hash")
    result["negative_history_chain_valid"] = not chain_errors
    result["valid"] = bool(report.get("valid")) and not chain_errors
    if combined:
        result["empirical_authority"] = "CANNOT_CHECK"
    return result


__all__ = [
    "CHAIN_DOCUMENT_SCHEMA",
    "CHAIN_PROTOCOL_SCHEMA",
    "build_negative_history_chain",
    "negative_history_genesis",
    "validate_result_archive_with_negative_history",
    "verify_negative_history_chain",
]
