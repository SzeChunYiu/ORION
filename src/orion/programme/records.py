"""Vocabulary shared by the three Phase-4 knowledge layers.

Three outcomes, not two. ``CANNOT_CHECK`` is a distinct state from ``FAIL`` and
must never be collapsed into ``PASS``: a boolean return type is exactly how
"could not check" silently becomes "checked and fine". This mirrors the
vocabulary already fixed in the repo — ``ALLOWED_DECISIONS`` in
``orion.study.p5.v2_evidence``, ``empirical_authority = "CANNOT_CHECK"`` in the
negative-history validator, and the issue's own "missing evidence remains
``OPEN``/``CANNOT_CHECK``".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.claims import ClaimAuthority
from orion.programme.identity import is_sha256


class Outcome(str, Enum):
    """Result of any Phase-4 check. ``CANNOT_CHECK`` blocks exactly as ``FAIL`` does."""

    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"

    @property
    def blocks(self) -> bool:
        return self is not Outcome.PASS


class ObjectAuthority(str, Enum):
    """Authority of one object-knowledge record.

    Deliberately a superset of :class:`orion.core.claims.ClaimAuthority`: every
    value of that enum is representable here (pinned by test), plus the two
    states the Phase-4 constitutional boundary requires for absent evidence.
    """

    OPEN = "OPEN"
    CANNOT_CHECK = "CANNOT_CHECK"
    PROPOSED = ClaimAuthority.PROPOSED.value
    SOURCE_PROJECTION = ClaimAuthority.SOURCE_PROJECTION.value
    VERIFIED = ClaimAuthority.VERIFIED.value

    @property
    def is_settled(self) -> bool:
        return self is ObjectAuthority.VERIFIED


class RouteAvailability(str, Enum):
    """Typed state of a search route.

    ``NOT_ATTEMPTED`` is not a form of unavailability. Conflating the two is how
    a search universe claims closure over ground it never walked, so a universe
    that declares saturation while any obligated route is ``NOT_ATTEMPTED`` is
    not merely unsaturated — it is unevaluable.
    """

    AVAILABLE = "AVAILABLE"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    UNAVAILABLE_TRANSIENT = "UNAVAILABLE_TRANSIENT"
    UNAVAILABLE_STRUCTURAL = "UNAVAILABLE_STRUCTURAL"
    CENSORED_LEGAL = "CENSORED_LEGAL"
    CENSORED_PAYWALL = "CENSORED_PAYWALL"

    @property
    def walked(self) -> bool:
        return self is RouteAvailability.AVAILABLE


@dataclass(frozen=True)
class ProvenanceBinding:
    """Where one piece of evidence came from, at which version of that source.

    ``source_version`` is mandatory and free-form (a DOI revision, a git SHA, an
    ``ETag``, a snapshot date). Its purpose is substitution detection: a source
    that silently changes under a stable URI is the ``HC-STALE-AUTHORITY``
    failure, and it is invisible without a recorded version.
    """

    source_id: str
    source_uri: str
    source_family: str
    source_version: str
    content_sha256: str
    retrieved_at_epoch: int

    def __post_init__(self) -> None:
        for field_name in ("source_id", "source_uri", "source_family", "source_version"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"provenance {field_name} is required")
        if not is_sha256(self.content_sha256):
            raise ValueError("provenance content_sha256 must be SHA-256")
        if self.retrieved_at_epoch < 0:
            raise ValueError("provenance retrieved_at_epoch must be non-negative")


def required_text_errors(value: object, label: str) -> tuple[str, ...]:
    """Errors for a field that must be present, a string, and non-blank."""

    if not isinstance(value, str) or not value.strip():
        return (f"{label} is required",)
    return ()


def required_ids_errors(values: object, label: str) -> tuple[str, ...]:
    """Errors for a field that must be a non-empty tuple of non-blank identifiers."""

    if not isinstance(values, tuple) or not values:
        return (f"{label} must be a non-empty tuple",)
    errors = [
        f"{label}[{index}] is not a non-blank identifier"
        for index, value in enumerate(values)
        if not isinstance(value, str) or not value.strip()
    ]
    return tuple(errors)


def dedup(errors: list[str]) -> tuple[str, ...]:
    """Order-preserving deduplication, matching the repo's validator convention."""

    return tuple(dict.fromkeys(errors))


__all__ = [
    "ObjectAuthority",
    "Outcome",
    "ProvenanceBinding",
    "RouteAvailability",
    "dedup",
    "required_ids_errors",
    "required_text_errors",
]
