"""Frozen family slots and split identities for GlobalPositiveCertificate.v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from orion.study.global_positive.schema import (
    REPO_ROOT,
    digest,
    load_json,
    load_schema,
)

ADOPTION_BOUNDARY = "V2_ADDITIVE"

PORTFOLIO_PATH = REPO_ROOT / "research/revival/global_positive/PORTFOLIO_FREEZE_V1.json"

REQUIRED_SPLIT_IDS = (
    "motivating",
    "heldout_same_family",
    "cross_family",
    "protected_regression",
)


def portfolio_document() -> dict[str, Any]:
    return load_json(PORTFOLIO_PATH)


def portfolio_hash() -> str:
    return digest(portfolio_document())


def freeze_fingerprint() -> str:
    """Identity of the published V1 freeze: schema + portfolio + protocol."""

    from orion.study.global_positive.schema import protocol_hash, schema_hash

    return digest(
        {
            "portfolio": portfolio_hash(),
            "protocol": protocol_hash(),
            "schema": schema_hash(),
        }
    )


def slot_identity(family_id: str, split_id: str, binding: str) -> str:
    """Content-addressed identity of one split slot.

    UNBOUND payloads still have a frozen slot identity. Binding a real task is
    a successor freeze: it changes this hash rather than editing V1 in place.
    """

    return digest(
        {
            "binding": binding,
            "family_id": family_id,
            "schema": "orion.global-positive.split-identity.v1",
            "split_id": split_id,
        }
    )


@dataclass(frozen=True)
class FamilySlot:
    family_id: str
    domain: str
    required_for_admission: bool
    binding: str
    slot_status: str
    split_identities: tuple[tuple[str, str], ...]
    suggested_role: str

    @property
    def unbound(self) -> bool:
        return self.binding == "UNBOUND" or self.slot_status == "CANNOT_CHECK"

    def identity(self, split_id: str) -> str:
        for name, digest_value in self.split_identities:
            if name == split_id:
                return digest_value
        raise KeyError(split_id)


@dataclass(frozen=True)
class FrozenPortfolio:
    families: tuple[FamilySlot, ...]
    required_splits: tuple[str, ...]
    outcome_accessed: bool
    phase4_operation_authorized: bool
    min_required_families: int

    @property
    def fingerprint(self) -> str:
        return digest(self.to_payload())

    def to_payload(self) -> dict[str, Any]:
        return {
            "families": [
                {
                    "binding": item.binding,
                    "domain": item.domain,
                    "family_id": item.family_id,
                    "required_for_admission": item.required_for_admission,
                    "slot_status": item.slot_status,
                    "split_identities": list(item.split_identities),
                    "suggested_role": item.suggested_role,
                }
                for item in self.families
            ],
            "min_required_families": self.min_required_families,
            "outcome_accessed": self.outcome_accessed,
            "phase4_operation_authorized": self.phase4_operation_authorized,
            "required_splits": list(self.required_splits),
        }

    @property
    def required_family_ids(self) -> tuple[str, ...]:
        return tuple(
            item.family_id for item in self.families if item.required_for_admission
        )

    @property
    def family_ids(self) -> tuple[str, ...]:
        return tuple(item.family_id for item in self.families)

    def family(self, family_id: str) -> FamilySlot:
        for item in self.families:
            if item.family_id == family_id:
                return item
        raise KeyError(family_id)

    def bind_for_tests(self, nonce: str) -> FrozenPortfolio:
        """Known-answer freeze. Not the published V1 identity; fingerprints must differ."""

        if not nonce.strip():
            raise ValueError("test binding nonce is required")
        bound: list[FamilySlot] = []
        for item in self.families:
            if not item.required_for_admission:
                bound.append(item)
                continue
            binding = digest(
                {
                    "family_id": item.family_id,
                    "kind": "test_slot_binding",
                    "nonce": nonce,
                }
            )
            identities = tuple(
                (split_id, slot_identity(item.family_id, split_id, binding))
                for split_id, _existing in item.split_identities
            )
            bound.append(
                FamilySlot(
                    family_id=item.family_id,
                    domain=item.domain,
                    required_for_admission=True,
                    binding=binding,
                    slot_status="TEST_BOUND",
                    split_identities=identities,
                    suggested_role=item.suggested_role,
                )
            )
        return FrozenPortfolio(
            families=tuple(bound),
            required_splits=self.required_splits,
            outcome_accessed=False,
            phase4_operation_authorized=False,
            min_required_families=self.min_required_families,
        )

    def with_margin_document(self, dimension_id: str, margin: float) -> dict[str, Any]:
        """Return a *new* document. V1 is not edited; the fingerprint must change."""

        schema = load_schema()
        spec = schema.spec(dimension_id)
        return {
            "dimension_id": dimension_id,
            "original_margin": spec.non_inferiority_margin,
            "retuned_margin": float(margin),
            "portfolio_fingerprint": self.fingerprint,
        }


def _slot_from_mapping(raw: Mapping[str, Any]) -> FamilySlot:
    family_id = str(raw["family_id"])
    binding = str(raw["binding"])
    splits_raw = raw["splits"]
    if not isinstance(splits_raw, Mapping):
        raise ValueError(f"{family_id} splits must be an object")
    identities: list[tuple[str, str]] = []
    for split_id in REQUIRED_SPLIT_IDS:
        if split_id not in splits_raw:
            raise ValueError(f"{family_id} missing frozen split {split_id}")
        identities.append(
            (split_id, slot_identity(family_id, split_id, str(splits_raw[split_id])))
        )
    return FamilySlot(
        family_id=family_id,
        domain=str(raw["domain"]),
        required_for_admission=bool(raw["required_for_admission"]),
        binding=binding,
        slot_status=str(raw["slot_status"]),
        split_identities=tuple(identities),
        suggested_role=str(raw["suggested_role"]),
    )


def load_portfolio() -> FrozenPortfolio:
    raw = portfolio_document()
    if raw.get("outcome_accessed") is not False:
        raise ValueError("published portfolio freeze was written after outcomes")
    if raw.get("weights_tunable_after_outcomes") is not False:
        raise ValueError("published freeze must forbid post-outcome weight tuning")
    if raw.get("phase4_operation_authorized") is not False:
        raise ValueError("published freeze must not authorize Phase-4 operation")
    families = tuple(_slot_from_mapping(item) for item in raw["families"])
    required = tuple(item for item in families if item.required_for_admission)
    min_required = int(raw["min_required_families"])
    if len(required) < min_required:
        raise ValueError("published freeze has fewer required families than declared")
    splits = tuple(raw["required_splits"])
    if splits != REQUIRED_SPLIT_IDS:
        raise ValueError("published freeze changed the required split set")
    return FrozenPortfolio(
        families=families,
        required_splits=splits,
        outcome_accessed=False,
        phase4_operation_authorized=False,
        min_required_families=min_required,
    )
