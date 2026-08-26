from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from . import EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER, INDEPENDENCE_TERMINAL
from .factorization import (
    FactorizationResult,
    FactorizationStatus,
    verify_factorization_certificate,
)
from .group import GroupSpec

DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class ReceiptError(ValueError):
    """A receipt cannot bind the supplied inputs safely."""


class ReceiptTerminal(StrEnum):
    ENGINEERING_POSITIVE = "ENGINEERING_POSITIVE"
    ENGINEERING_NEGATIVE = "ENGINEERING_NEGATIVE"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"
    CANNOT_CHECK_INVALID_CERTIFICATE = "CANNOT_CHECK_INVALID_CERTIFICATE"


@dataclass(frozen=True, slots=True)
class EngineeringReceipt:
    terminal: ReceiptTerminal
    input_sha256: str
    source_manifest_sha256: str
    result_sha256: str
    result_status: FactorizationStatus
    full_coverage: bool
    exhaustive: bool
    certificate_valid: bool | None
    reasons: tuple[str, ...]
    metrics: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "nq-engine-a-receipt-v1",
            "terminal": self.terminal.value,
            "independence_terminal": INDEPENDENCE_TERMINAL,
            "exposure_markers": [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER],
            "input_sha256": self.input_sha256,
            "source_manifest_sha256": self.source_manifest_sha256,
            "result_sha256": self.result_sha256,
            "result_status": self.result_status.value,
            "full_coverage": self.full_coverage,
            "exhaustive": self.exhaustive,
            "certificate_valid": self.certificate_valid,
            "reasons": list(self.reasons),
            "metrics": dict(self.metrics),
        }


def canonical_json_sha256(value: Any) -> str:
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def factorization_input_payload(
    spec: GroupSpec,
    sequence: object,
    k: object,
    *,
    limits: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    vectors = spec.validate_sequence(sequence)
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ReceiptError("k must be a positive integer")
    payload: dict[str, Any] = {
        "schema_version": "nq-engine-a-input-v1",
        "exposure_markers": [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER],
        "group": {"p": spec.p, "d": spec.d},
        "sequence": [list(vector) for vector in vectors],
        "k": k,
    }
    if limits:
        payload["limits"] = dict(sorted(limits.items()))
    return payload


def factorization_result_payload(result: FactorizationResult) -> dict[str, Any]:
    return {
        "status": result.status.value,
        "sequence_length": result.sequence_length,
        "k": result.k,
        "layers_completed": result.layers_completed,
        "states_explored": result.states_explored,
        "frontier_peak": result.frontier_peak,
        "exhaustive": result.exhaustive,
        "certificate": None
        if result.certificate is None
        else {"bins": [list(indices) for indices in result.certificate.bins]},
    }


def _checked_digest(value: object, field: str) -> str:
    if not isinstance(value, str) or DIGEST_RE.fullmatch(value) is None:
        raise ReceiptError(f"{field} must be a lowercase SHA-256 digest")
    return value


def build_factorization_receipt(
    spec: GroupSpec,
    sequence: object,
    k: object,
    result: FactorizationResult,
    *,
    full_coverage: bool,
    source_manifest_sha256: str,
    limits: Mapping[str, int] | None = None,
) -> EngineeringReceipt:
    vectors = spec.validate_sequence(sequence)
    input_payload = factorization_input_payload(spec, vectors, k, limits=limits)
    source_digest = _checked_digest(source_manifest_sha256, "source_manifest_sha256")
    input_digest = canonical_json_sha256(input_payload)
    result_digest = canonical_json_sha256(factorization_result_payload(result))
    metrics = {
        "sequence_length": result.sequence_length,
        "k": result.k,
        "layers_completed": result.layers_completed,
        "states_explored": result.states_explored,
        "frontier_peak": result.frontier_peak,
    }
    if result.sequence_length != len(vectors) or result.k != k:
        return EngineeringReceipt(
            terminal=ReceiptTerminal.CANNOT_CHECK_INVALID_CERTIFICATE,
            input_sha256=input_digest,
            source_manifest_sha256=source_digest,
            result_sha256=result_digest,
            result_status=result.status,
            full_coverage=False,
            exhaustive=False,
            certificate_valid=False,
            reasons=("result metadata does not bind the supplied input",),
            metrics=metrics,
        )
    if result.status is FactorizationStatus.POSITIVE:
        certificate_valid = result.certificate is not None and verify_factorization_certificate(
            spec, vectors, k, result.certificate
        )
        if certificate_valid:
            terminal = ReceiptTerminal.ENGINEERING_POSITIVE
            reasons = ("independently recomputed certificate is valid",)
        else:
            terminal = ReceiptTerminal.CANNOT_CHECK_INVALID_CERTIFICATE
            reasons = ("positive result lacks a valid recomputed certificate",)
        return EngineeringReceipt(
            terminal=terminal,
            input_sha256=input_digest,
            source_manifest_sha256=source_digest,
            result_sha256=result_digest,
            result_status=result.status,
            full_coverage=bool(full_coverage),
            exhaustive=bool(result.exhaustive),
            certificate_valid=certificate_valid,
            reasons=reasons,
            metrics=metrics,
        )
    if result.status is FactorizationStatus.NEGATIVE and result.exhaustive and full_coverage:
        return EngineeringReceipt(
            terminal=ReceiptTerminal.ENGINEERING_NEGATIVE,
            input_sha256=input_digest,
            source_manifest_sha256=source_digest,
            result_sha256=result_digest,
            result_status=result.status,
            full_coverage=True,
            exhaustive=True,
            certificate_valid=None,
            reasons=("all DP layers completed without a target state",),
            metrics=metrics,
        )
    return EngineeringReceipt(
        terminal=ReceiptTerminal.CANNOT_CHECK_RESOURCE_BOUND,
        input_sha256=input_digest,
        source_manifest_sha256=source_digest,
        result_sha256=result_digest,
        result_status=result.status,
        full_coverage=False,
        exhaustive=False,
        certificate_valid=None,
        reasons=("partial or resource-bounded traversal cannot support absence",),
        metrics=metrics,
    )
