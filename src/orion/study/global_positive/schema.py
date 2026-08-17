"""GlobalPositiveCertificate.v1 schema freeze (issue #285).

Additive V2-style surface: unconsumed by V1 runtime on purpose. Shared
registries (`orion.__init__`) are not edited here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from orion.kernel.store import canonical_bytes

ADOPTION_BOUNDARY = "V2_ADDITIVE"

SCHEMA_ID = "GlobalPositiveCertificate.v1"
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "research/revival/global_positive/CERTIFICATE_SCHEMA_V1.json"
PROTOCOL_PATH = REPO_ROOT / "research/revival/global_positive/PROTOCOL_V1.json"

FORBIDDEN_SCALAR_KEYS = frozenset(
    {
        "average_score",
        "global_score",
        "mean_score",
        "scalar_utility",
        "weighted_sum",
    }
)


class DimensionKind(str, Enum):
    PRIMARY_UTILITY = "PRIMARY_UTILITY"
    PROTECTED_NONREGRESSION = "PROTECTED_NONREGRESSION"
    CATASTROPHIC_SAFETY = "CATASTROPHIC_SAFETY"
    INTEGRITY = "INTEGRITY"


class DimensionDirection(str, Enum):
    HIGHER_BETTER = "higher_better"
    LOWER_BETTER = "lower_better"
    FAIL_CLOSED = "fail_closed"


class DimensionScope(str, Enum):
    PER_FAMILY = "per_family"
    PORTFOLIO = "portfolio"


class CandidateTerminal(str, Enum):
    GLOBAL_POSITIVE = "GLOBAL_POSITIVE"
    LOCAL_POSITIVE_WITH_TRADEOFF = "LOCAL_POSITIVE_WITH_TRADEOFF"
    NULL_NONINFERIOR_ONLY = "NULL_NONINFERIOR_ONLY"
    HARMFUL_REGRESSION = "HARMFUL_REGRESSION"
    CANNOT_CHECK = "CANNOT_CHECK"


class ProgrammeTerminal(str, Enum):
    GLOBAL_POSITIVE_SUPPORTED = "GLOBAL_POSITIVE_SUPPORTED"
    LOCAL_ONLY = "LOCAL_ONLY"
    OVERCONSERVATIVE = "OVERCONSERVATIVE"
    REFUTED = "REFUTED"
    CANNOT_CHECK = "CANNOT_CHECK"


def digest(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def schema_document() -> dict[str, Any]:
    return load_json(SCHEMA_PATH)


def protocol_document() -> dict[str, Any]:
    return load_json(PROTOCOL_PATH)


def schema_hash() -> str:
    return digest(schema_document())


def protocol_hash() -> str:
    return digest(protocol_document())


@dataclass(frozen=True)
class DimensionSpec:
    dimension_id: str
    kind: DimensionKind
    direction: DimensionDirection
    scope: DimensionScope
    mandatory: bool
    catastrophic: bool
    min_effect: float | None
    non_inferiority_margin: float
    description: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> DimensionSpec:
        min_effect = raw.get("min_effect")
        if min_effect is not None:
            min_effect = float(min_effect)
        return cls(
            dimension_id=str(raw["id"]),
            kind=DimensionKind(str(raw["kind"])),
            direction=DimensionDirection(str(raw["direction"])),
            scope=DimensionScope(str(raw["scope"])),
            mandatory=bool(raw["mandatory"]),
            catastrophic=bool(raw["catastrophic"]),
            min_effect=min_effect,
            non_inferiority_margin=float(raw["non_inferiority_margin"]),
            description=str(raw["description"]),
        )


@dataclass(frozen=True)
class CertificateSchema:
    schema_id: str
    dimensions: tuple[DimensionSpec, ...]
    forbidden_primary_authority: tuple[str, ...]
    candidate_terminals: tuple[str, ...]
    programme_terminals: tuple[str, ...]
    min_prospective_rounds: int
    phase4_operation_authorized: bool
    requires_independent_verification_issue: int

    def spec(self, dimension_id: str) -> DimensionSpec:
        for item in self.dimensions:
            if item.dimension_id == dimension_id:
                return item
        raise KeyError(dimension_id)

    @property
    def mandatory_ids(self) -> tuple[str, ...]:
        return tuple(item.dimension_id for item in self.dimensions if item.mandatory)

    @property
    def primary_utility_ids(self) -> tuple[str, ...]:
        return tuple(
            item.dimension_id
            for item in self.dimensions
            if item.kind is DimensionKind.PRIMARY_UTILITY
        )

    @property
    def per_family_ids(self) -> tuple[str, ...]:
        return tuple(
            item.dimension_id
            for item in self.dimensions
            if item.scope is DimensionScope.PER_FAMILY
        )

    @property
    def fingerprint(self) -> str:
        return digest(schema_document())


def load_schema() -> CertificateSchema:
    raw = schema_document()
    if raw.get("schema_id") != SCHEMA_ID:
        raise ValueError("published schema_id must be GlobalPositiveCertificate.v1")
    if raw.get("authority_rule") != "non_compensatory_all_dimensions":
        raise ValueError("V1 authority must be non-compensatory")
    if raw.get("compensation") != "forbidden":
        raise ValueError("V1 forbids compensation")
    if raw.get("phase4_operation_authorized") is not False:
        raise ValueError("V1 must not authorize Phase-4 operation")
    dimensions = tuple(DimensionSpec.from_mapping(item) for item in raw["dimensions"])
    ids = [item.dimension_id for item in dimensions]
    if len(set(ids)) != len(ids):
        raise ValueError("dimension ids must be unique")
    forbidden = tuple(raw["forbidden_primary_authority"])
    if not FORBIDDEN_SCALAR_KEYS.issubset(forbidden):
        raise ValueError("published schema dropped a forbidden scalar key")
    return CertificateSchema(
        schema_id=str(raw["schema_id"]),
        dimensions=dimensions,
        forbidden_primary_authority=forbidden,
        candidate_terminals=tuple(raw["candidate_terminals"]),
        programme_terminals=tuple(raw["programme_terminals"]),
        min_prospective_rounds=int(raw["min_prospective_rounds_for_global_positive_supported"]),
        phase4_operation_authorized=False,
        requires_independent_verification_issue=int(
            raw["requires_independent_verification_issue"]
        ),
    )
