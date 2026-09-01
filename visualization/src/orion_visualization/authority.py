"""Evidence-state vocabulary used by the visualization layer.

Status and authority are deliberately separate axes.  A digest match can establish
byte integrity, but it cannot establish scientific correctness or independent
validation.  Callers must provide authority metadata explicitly.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable


class EvidenceStatus(str, Enum):
    """Non-collapsing states for receipt-derived observations."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"
    NULL = "NULL"
    ADVERSE = "ADVERSE"
    MIXED = "MIXED"


class AuthorityLevel(str, Enum):
    """Provenance/authority labels, ordered only by meaning, not by score."""

    NONE = "NONE"
    INTEGRITY_ONLY = "INTEGRITY_ONLY"
    LOCAL_CONFORMANCE = "LOCAL_CONFORMANCE"
    INTERNAL_REPLAY = "INTERNAL_REPLAY"
    INDEPENDENT_EXTERNAL = "INDEPENDENT_EXTERNAL"
    CANNOT_CHECK = "CANNOT_CHECK"


_ALIASES: dict[str, EvidenceStatus] = {
    "pass": EvidenceStatus.PASS,
    "passed": EvidenceStatus.PASS,
    "success": EvidenceStatus.PASS,
    "succeeded": EvidenceStatus.PASS,
    "fail": EvidenceStatus.FAIL,
    "failed": EvidenceStatus.FAIL,
    "failure": EvidenceStatus.FAIL,
    "unknown": EvidenceStatus.UNKNOWN,
    "undetermined": EvidenceStatus.UNKNOWN,
    "cannot_check": EvidenceStatus.CANNOT_CHECK,
    "cannotcheck": EvidenceStatus.CANNOT_CHECK,
    "cant_check": EvidenceStatus.CANNOT_CHECK,
    "not_checked": EvidenceStatus.CANNOT_CHECK,
    "unchecked": EvidenceStatus.CANNOT_CHECK,
    "null": EvidenceStatus.NULL,
    "none": EvidenceStatus.NULL,
    "missing": EvidenceStatus.NULL,
    "no_data": EvidenceStatus.NULL,
    "adverse": EvidenceStatus.ADVERSE,
    "adverse_result": EvidenceStatus.ADVERSE,
    "harmful": EvidenceStatus.ADVERSE,
    "negative_result": EvidenceStatus.ADVERSE,
    "mixed": EvidenceStatus.MIXED,
}


def _normalise_token(value: str) -> str:
    token = value.strip().lower().replace("-", "_").replace(" ", "_")
    while "__" in token:
        token = token.replace("__", "_")
    return token


def classify_status(value: Any) -> EvidenceStatus:
    """Classify a status without converting uncertainty or adversity to success.

    ``None`` is a first-class null observation.  Booleans and numeric values are
    rejected because interpreting them as PASS/FAIL would be source-schema
    dependent and could silently reverse a result.
    """

    if isinstance(value, EvidenceStatus):
        return value
    if value is None:
        return EvidenceStatus.NULL
    if isinstance(value, bool) or not isinstance(value, str):
        raise TypeError("evidence status must be a string, EvidenceStatus, or None")
    token = _normalise_token(value)
    try:
        return _ALIASES[token]
    except KeyError as exc:
        raise ValueError(f"unrecognised evidence status: {value!r}") from exc


def classify_statuses(values: Iterable[Any]) -> tuple[EvidenceStatus, ...]:
    """Return an immutable, order-preserving sequence of classified states."""

    return tuple(classify_status(value) for value in values)


def status_counts(values: Iterable[Any]) -> dict[EvidenceStatus, int]:
    """Count every semantic state without dropping null/adverse observations."""

    counts = {status: 0 for status in EvidenceStatus}
    for status in classify_statuses(values):
        counts[status] += 1
    return counts
