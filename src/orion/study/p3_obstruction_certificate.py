"""Provenance-bound obstruction certificates and their falsifiers.

A certificate explains why two source-local representations must not be globally
identified. It is independently verifiable from source artifacts. LLM labels are
not an admissible gold authority for the certificate itself.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

SCHEMA_VERSION = "orion.p3.obstruction-certificate.v2"
CANONICAL_COORDINATES = (
    "REFERENT_IDENTITY",
    "CONSTRUCT_IDENTITY",
    "MEASUREMENT_OPERATIONALIZATION",
    "TEMPORAL_STATE_CONTEXT",
    "MODALITY_POLARITY_ATTRIBUTION",
    "REPRESENTATION_TRANSFORM",
    "PLURALISM_OBSTRUCTION",
    "UNRESOLVED",
)
HARD_STATUSES = frozenset({"HARD", "CONDITIONAL"})
ADMISSIBLE_STATUSES = frozenset({"HARD", "CONDITIONAL", "UNRESOLVED", "CANNOT_CHECK"})
HEX = frozenset("0123456789abcdef")


class CertificateError(ValueError):
    """Certificate is malformed or fails closed."""


class FalsifierId(str, Enum):
    SOURCE_CONTENT_SUBSTITUTION = "source_content_substitution"
    ATTRIBUTION_SWAP = "attribution_swap"
    MISSING_PRESERVATION_CONDITION = "missing_preservation_condition"
    ACTUALLY_VALID_TRANSFORM = "actually_valid_transform"
    MISSING_ANCHOR = "missing_anchor"
    CORRUPTED_CYCLE = "corrupted_cycle"
    INGESTION_ORDER_CHANGE = "ingestion_order_change"
    EQUIVALENT_VIEWS_REPRESENTED_DIFFERENTLY = "equivalent_views_represented_differently"


@dataclass(frozen=True)
class SourceIdentity:
    source_id: str
    content_hash: str
    locator: str = ""
    attribution_id: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise CertificateError("source identity requires source_id")
        if len(self.content_hash) != 64 or any(ch not in HEX for ch in self.content_hash):
            raise CertificateError("source identity requires a SHA-256 content hash")


@dataclass(frozen=True)
class ObstructionCertificate:
    certificate_id: str
    source_a: SourceIdentity
    source_b: SourceIdentity
    proposed_mapping: str
    failing_coordinates: tuple[str, ...]
    violated_preservation_obligation: str
    supporting_evidence: tuple[str, ...]
    status: str
    retained_local_views: tuple[str, ...]
    forbidden_global_merges: tuple[str, ...]
    schema_version: str = SCHEMA_VERSION
    cycle_anchors: tuple[str, ...] = ()
    valid_transform: bool = False
    content_hash: str = ""

    def payload_for_hash(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "certificate_id": self.certificate_id,
            "source_a": _source_dict(self.source_a),
            "source_b": _source_dict(self.source_b),
            "proposed_mapping": self.proposed_mapping,
            "failing_coordinates": list(self.failing_coordinates),
            "violated_preservation_obligation": self.violated_preservation_obligation,
            "supporting_evidence": list(self.supporting_evidence),
            "status": self.status,
            "retained_local_views": list(self.retained_local_views),
            "forbidden_global_merges": list(self.forbidden_global_merges),
            "cycle_anchors": list(self.cycle_anchors),
            "valid_transform": self.valid_transform,
        }


@dataclass(frozen=True)
class CertificateVerdict:
    ok: bool
    status: str
    blockers: tuple[str, ...]


def canonical_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_json(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def _source_dict(source: SourceIdentity) -> dict[str, str]:
    return {
        "source_id": source.source_id,
        "content_hash": source.content_hash,
        "locator": source.locator,
        "attribution_id": source.attribution_id,
    }


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_pair_key(source_a: SourceIdentity, source_b: SourceIdentity) -> tuple[str, str]:
    """Ingestion order must not change certificate identity."""
    left = source_a.content_hash
    right = source_b.content_hash
    return (left, right) if left <= right else (right, left)


def bind_certificate(certificate: ObstructionCertificate) -> ObstructionCertificate:
    digest = sha256_json(certificate.payload_for_hash())
    object.__setattr__(certificate, "content_hash", digest)
    return certificate


def validate_certificate(certificate: ObstructionCertificate) -> list[str]:
    blockers: list[str] = []
    if certificate.schema_version != SCHEMA_VERSION:
        blockers.append(f"unsupported schema_version: {certificate.schema_version}")
    if not certificate.certificate_id.strip():
        blockers.append("certificate_id is required")
    if certificate.status not in ADMISSIBLE_STATUSES:
        blockers.append(f"invalid status: {certificate.status}")
    if not certificate.proposed_mapping.strip():
        blockers.append("proposed_mapping is required")
    unknown = [item for item in certificate.failing_coordinates if item not in CANONICAL_COORDINATES]
    if unknown:
        blockers.append("unknown failing coordinates: " + ", ".join(unknown))
    if certificate.status in HARD_STATUSES:
        if not certificate.failing_coordinates:
            blockers.append("HARD/CONDITIONAL obstruction requires failing_coordinates")
        if not certificate.violated_preservation_obligation.strip():
            blockers.append("missing_preservation_condition")
        if not certificate.supporting_evidence:
            blockers.append("HARD/CONDITIONAL obstruction requires supporting_evidence")
        if certificate.valid_transform:
            blockers.append("actually_valid_transform")
        if "UNRESOLVED" in certificate.failing_coordinates and certificate.status == "HARD":
            blockers.append("UNRESOLVED cannot be a HARD obstruction coordinate")
    if not certificate.source_a.content_hash or not certificate.source_b.content_hash:
        blockers.append("missing_anchor")
    if certificate.source_a.content_hash == certificate.source_b.content_hash:
        if certificate.status in HARD_STATUSES:
            blockers.append("equivalent_views_represented_differently")
    if certificate.cycle_anchors:
        if len(certificate.cycle_anchors) != len(set(certificate.cycle_anchors)):
            blockers.append("corrupted_cycle")
        if len(certificate.cycle_anchors) < 3 and certificate.status in HARD_STATUSES:
            blockers.append("corrupted_cycle")
    expected = sha256_json(certificate.payload_for_hash())
    if certificate.content_hash and certificate.content_hash != expected:
        blockers.append("certificate content_hash mismatch")
    return blockers


def verify_certificate(
    certificate: ObstructionCertificate,
    artifacts: Mapping[str, bytes],
) -> CertificateVerdict:
    blockers = validate_certificate(certificate)
    for source in (certificate.source_a, certificate.source_b):
        payload = artifacts.get(source.source_id)
        if payload is None:
            blockers.append(f"missing_anchor:{source.source_id}")
            continue
        digest = _sha256_bytes(payload)
        if digest != source.content_hash:
            blockers.append(f"source_content_substitution:{source.source_id}")
        if source.attribution_id and source.attribution_id.encode("utf-8") not in payload:
            blockers.append(f"attribution_swap:{source.source_id}")
    if certificate.status in {"UNRESOLVED", "CANNOT_CHECK"}:
        status = certificate.status
        ok = not any(
            item.startswith("source_content_substitution") or item.startswith("missing_anchor")
            for item in blockers
        ) and "certificate content_hash mismatch" not in blockers
        return CertificateVerdict(ok=ok, status=status, blockers=tuple(blockers))
    if blockers:
        return CertificateVerdict(ok=False, status="REJECTED", blockers=tuple(blockers))
    return CertificateVerdict(ok=True, status=certificate.status, blockers=())


def _replace(certificate: ObstructionCertificate, **changes: object) -> ObstructionCertificate:
    payload = certificate.__dict__.copy()
    payload.update(changes)
    payload.pop("content_hash", None)
    rebound = ObstructionCertificate(**payload)
    return bind_certificate(rebound)


def falsify_source_content_substitution(
    certificate: ObstructionCertificate,
    artifacts: Mapping[str, bytes],
) -> tuple[ObstructionCertificate, dict[str, bytes]]:
    mutated = dict(artifacts)
    original = mutated[certificate.source_a.source_id]
    mutated[certificate.source_a.source_id] = original + b"\nsubstituted"
    return certificate, mutated


def falsify_attribution_swap(certificate: ObstructionCertificate) -> ObstructionCertificate:
    swapped_a = SourceIdentity(
        source_id=certificate.source_a.source_id,
        content_hash=certificate.source_a.content_hash,
        locator=certificate.source_a.locator,
        attribution_id=certificate.source_b.attribution_id,
    )
    swapped_b = SourceIdentity(
        source_id=certificate.source_b.source_id,
        content_hash=certificate.source_b.content_hash,
        locator=certificate.source_b.locator,
        attribution_id=certificate.source_a.attribution_id,
    )
    return _replace(certificate, source_a=swapped_a, source_b=swapped_b)


def falsify_missing_preservation_condition(
    certificate: ObstructionCertificate,
) -> ObstructionCertificate:
    return _replace(certificate, violated_preservation_obligation="")


def falsify_actually_valid_transform(certificate: ObstructionCertificate) -> ObstructionCertificate:
    return _replace(certificate, valid_transform=True)


def falsify_missing_anchor(
    certificate: ObstructionCertificate,
    artifacts: Mapping[str, bytes],
) -> tuple[ObstructionCertificate, dict[str, bytes]]:
    mutated = dict(artifacts)
    mutated.pop(certificate.source_a.source_id, None)
    return certificate, mutated


def falsify_corrupted_cycle(certificate: ObstructionCertificate) -> ObstructionCertificate:
    return _replace(certificate, cycle_anchors=("A", "B", "A"))


def falsify_ingestion_order_change(
    certificate: ObstructionCertificate,
) -> tuple[tuple[str, str], tuple[str, str]]:
    original = canonical_pair_key(certificate.source_a, certificate.source_b)
    swapped = canonical_pair_key(certificate.source_b, certificate.source_a)
    return original, swapped


def falsify_equivalent_views(certificate: ObstructionCertificate) -> ObstructionCertificate:
    twin = SourceIdentity(
        source_id=certificate.source_b.source_id,
        content_hash=certificate.source_a.content_hash,
        locator=certificate.source_b.locator,
        attribution_id=certificate.source_b.attribution_id,
    )
    return _replace(certificate, source_b=twin)


FALSIFIER_IDS: tuple[str, ...] = tuple(item.value for item in FalsifierId)


def apply_falsifier(
    name: str,
    certificate: ObstructionCertificate,
    artifacts: Mapping[str, bytes],
) -> CertificateVerdict | tuple[tuple[str, str], tuple[str, str]]:
    if name == FalsifierId.SOURCE_CONTENT_SUBSTITUTION.value:
        cert, mutated = falsify_source_content_substitution(certificate, artifacts)
        return verify_certificate(cert, mutated)
    if name == FalsifierId.ATTRIBUTION_SWAP.value:
        swapped = falsify_attribution_swap(certificate)
        return verify_certificate(swapped, artifacts)
    if name == FalsifierId.MISSING_PRESERVATION_CONDITION.value:
        return verify_certificate(falsify_missing_preservation_condition(certificate), artifacts)
    if name == FalsifierId.ACTUALLY_VALID_TRANSFORM.value:
        return verify_certificate(falsify_actually_valid_transform(certificate), artifacts)
    if name == FalsifierId.MISSING_ANCHOR.value:
        cert, mutated = falsify_missing_anchor(certificate, artifacts)
        return verify_certificate(cert, mutated)
    if name == FalsifierId.CORRUPTED_CYCLE.value:
        return verify_certificate(falsify_corrupted_cycle(certificate), artifacts)
    if name == FalsifierId.INGESTION_ORDER_CHANGE.value:
        return falsify_ingestion_order_change(certificate)
    if name == FalsifierId.EQUIVALENT_VIEWS_REPRESENTED_DIFFERENTLY.value:
        return verify_certificate(falsify_equivalent_views(certificate), artifacts)
    raise CertificateError(f"unknown falsifier: {name}")


def example_hard_certificate(artifacts: Mapping[str, bytes]) -> ObstructionCertificate:
    ids = tuple(artifacts)
    if len(ids) < 2:
        raise CertificateError("example certificate requires two artifacts")
    source_a = SourceIdentity(
        source_id=ids[0],
        content_hash=_sha256_bytes(artifacts[ids[0]]),
        locator="fixture/a",
        attribution_id="author:a",
    )
    source_b = SourceIdentity(
        source_id=ids[1],
        content_hash=_sha256_bytes(artifacts[ids[1]]),
        locator="fixture/b",
        attribution_id="author:b",
    )
    return bind_certificate(
        ObstructionCertificate(
            certificate_id="P3.CO.CERT.EXAMPLE",
            source_a=source_a,
            source_b=source_b,
            proposed_mapping="IDENTITY",
            failing_coordinates=("REFERENT_IDENTITY",),
            violated_preservation_obligation="referent identity must be preserved under merge",
            supporting_evidence=("fixture/a#span", "fixture/b#span"),
            status="HARD",
            retained_local_views=("source-local view A", "source-local view B"),
            forbidden_global_merges=("global entity identity of A and B",),
            cycle_anchors=("A", "B", "C"),
            valid_transform=False,
        )
    )


def required_falsifier_ids() -> Sequence[str]:
    return FALSIFIER_IDS
