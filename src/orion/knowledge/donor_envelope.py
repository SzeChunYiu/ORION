"""Fail-closed construction of theories that absorb and envelope donor work.

Nearest work is scientific input, not merely a reason to shorten a novelty
sentence.  This module makes the stronger workflow executable:

``absorb -> reconstruct -> conservatively embed -> separate -> falsify``.

The assessor deliberately distinguishes three useful outcomes:

* an absorbed special case, where the donor is reconstructed but nothing is
  added;
* a conservative envelope, where added coordinates are defined but no strict
  witness has survived;
* an ideal-product equivalence or candidate strict envelope, depending on what
  the strongest information-matched donor product can express.

None of these outcomes grants publication novelty or scientific truth.  Donor
priority and historical negative results remain explicit inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


SCHEMA_ID = "orion.donor-envelope-assessment.v1"


class IdealDonorProductRelation(str, Enum):
    """Observed relation between the envelope and the strongest donor product."""

    UNTESTED = "UNTESTED"
    TIES_ENVELOPE = "TIES_ENVELOPE"
    ENVELOPE_STRICTLY_SEPARATES = "ENVELOPE_STRICTLY_SEPARATES"


class DonorEnvelopeVerdict(str, Enum):
    """Ordered, non-authorizing status of one donor-envelope construction."""

    BLOCKED_ABSORPTION_INCOMPLETE = "BLOCKED_ABSORPTION_INCOMPLETE"
    BLOCKED_DONOR_RECONSTRUCTION = "BLOCKED_DONOR_RECONSTRUCTION"
    BLOCKED_CONSERVATIVE_EMBEDDING = "BLOCKED_CONSERVATIVE_EMBEDDING"
    ABSORBED_SPECIAL_CASE = "ABSORBED_SPECIAL_CASE"
    CONSERVATIVE_ENVELOPE = "CONSERVATIVE_ENVELOPE"
    BLOCKED_IDEAL_DONOR_PRODUCT = "BLOCKED_IDEAL_DONOR_PRODUCT"
    IDEAL_DONOR_PRODUCT_EQUIVALENCE = "IDEAL_DONOR_PRODUCT_EQUIVALENCE"
    BLOCKED_OPEN_ROUTES = "BLOCKED_OPEN_ROUTES"
    BLOCKED_NO_FALSIFIER = "BLOCKED_NO_FALSIFIER"
    BLOCKED_NO_FRESH_EVALUATION = "BLOCKED_NO_FRESH_EVALUATION"
    CANDIDATE_STRICT_ENVELOPE = "CANDIDATE_STRICT_ENVELOPE"


def _validated_ids(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(value.strip() for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{name} may not contain blank identities")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must contain unique identities")
    return normalized


@dataclass(frozen=True)
class DonorEnvelopeCase:
    """Frozen evidence contract for one proposed donor-envelope theory.

    Identity tuples point to content-addressed receipts, proofs, tests, or
    prospectively frozen artifacts owned elsewhere.  This object does not treat
    a string identity as proof; it ensures that promotion cannot silently skip a
    required evidence class.
    """

    case_id: str
    donor_ids: tuple[str, ...]
    admitted_absorption_receipt_ids: tuple[str, ...] = ()
    donor_claim_ids: tuple[str, ...] = ()
    donor_assumption_ids: tuple[str, ...] = ()
    donor_coordinate_ids: tuple[str, ...] = ()
    donor_reconstruction_ids: tuple[str, ...] = ()
    embedding_map_id: str = ""
    preservation_obligation_ids: tuple[str, ...] = ()
    added_coordinate_ids: tuple[str, ...] = ()
    strict_separation_ids: tuple[str, ...] = ()
    ideal_product_relation: IdealDonorProductRelation = IdealDonorProductRelation.UNTESTED
    ideal_product_evidence_ids: tuple[str, ...] = ()
    falsifier_ids: tuple[str, ...] = ()
    fresh_evaluation_ids: tuple[str, ...] = ()
    unresolved_route_ids: tuple[str, ...] = ()
    derived_from_negative: bool = False
    historical_negative_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("donor-envelope case requires a case identity")
        if not self.donor_ids:
            raise ValueError("donor-envelope case requires at least one donor")

        tuple_fields = (
            "donor_ids",
            "admitted_absorption_receipt_ids",
            "donor_claim_ids",
            "donor_assumption_ids",
            "donor_coordinate_ids",
            "donor_reconstruction_ids",
            "preservation_obligation_ids",
            "added_coordinate_ids",
            "strict_separation_ids",
            "ideal_product_evidence_ids",
            "falsifier_ids",
            "fresh_evaluation_ids",
            "unresolved_route_ids",
            "historical_negative_ids",
        )
        for field_name in tuple_fields:
            object.__setattr__(
                self,
                field_name,
                _validated_ids(field_name, getattr(self, field_name)),
            )

        object.__setattr__(
            self,
            "ideal_product_relation",
            IdealDonorProductRelation(self.ideal_product_relation),
        )

        overlap = set(self.donor_coordinate_ids) & set(self.added_coordinate_ids)
        if overlap:
            raise ValueError(
                "added coordinates must be distinct from donor coordinates: "
                + ", ".join(sorted(overlap))
            )
        if self.strict_separation_ids and not self.added_coordinate_ids:
            raise ValueError("strict separation requires at least one added coordinate")
        if (
            self.ideal_product_relation is not IdealDonorProductRelation.UNTESTED
            and not self.ideal_product_evidence_ids
        ):
            raise ValueError("a tested ideal donor product requires evidence identities")
        if self.derived_from_negative and not self.historical_negative_ids:
            raise ValueError(
                "a successor derived from a negative must preserve the historical negative identity"
            )


@dataclass(frozen=True)
class DonorEnvelopeAssessment:
    schema_id: str
    verdict: DonorEnvelopeVerdict
    reasons: tuple[str, ...]
    donor_count: int
    added_coordinate_count: int
    strict_separation_count: int
    historical_negative_ids: tuple[str, ...]

    @property
    def publication_novelty_authorized(self) -> bool:
        return False

    @property
    def scientific_truth_authorized(self) -> bool:
        return False

    @property
    def grants_authority(self) -> str:
        return "NONE"

    @property
    def self_authorizing(self) -> bool:
        return False

    @property
    def preserves_historical_negative(self) -> bool:
        return bool(self.historical_negative_ids)


def _assessment(
    case: DonorEnvelopeCase,
    verdict: DonorEnvelopeVerdict,
    *reasons: str,
) -> DonorEnvelopeAssessment:
    return DonorEnvelopeAssessment(
        schema_id=SCHEMA_ID,
        verdict=verdict,
        reasons=tuple(reasons),
        donor_count=len(case.donor_ids),
        added_coordinate_count=len(case.added_coordinate_ids),
        strict_separation_count=len(case.strict_separation_ids),
        historical_negative_ids=case.historical_negative_ids,
    )


def assess_donor_envelope(case: DonorEnvelopeCase) -> DonorEnvelopeAssessment:
    """Assess a donor envelope without converting evidence classes into truth.

    The sequence is intentionally fail closed.  Exact reconstruction and a
    conservative envelope are useful positive structures even when strict
    separation is absent; only strict-envelope promotion requires the full
    ideal-product, falsifier, fresh-evaluation, and search-route closure.
    """

    if not case.admitted_absorption_receipt_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_ABSORPTION_INCOMPLETE,
            "no admitted mechanism or structural assimilation receipt is bound",
        )
    if (
        not case.donor_claim_ids
        or not case.donor_assumption_ids
        or not case.donor_reconstruction_ids
    ):
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_DONOR_RECONSTRUCTION,
            "donor claims, assumptions, and an independent reconstruction are required",
        )
    if not case.embedding_map_id.strip() or not case.preservation_obligation_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_CONSERVATIVE_EMBEDDING,
            "an explicit embedding map and preservation obligations are required",
        )
    if not case.added_coordinate_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.ABSORBED_SPECIAL_CASE,
            "the donor is reconstructed as a preserved special case",
            "no distinct envelope coordinate is claimed",
        )
    if not case.strict_separation_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.CONSERVATIVE_ENVELOPE,
            "the donor is conservatively embedded and added coordinates are explicit",
            "no strict-separation proof or witness has survived",
        )
    if (
        case.ideal_product_relation is IdealDonorProductRelation.UNTESTED
        or not case.ideal_product_evidence_ids
    ):
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_IDEAL_DONOR_PRODUCT,
            "the strongest information-matched donor product has not been tested",
        )
    if case.ideal_product_relation is IdealDonorProductRelation.TIES_ENVELOPE:
        return _assessment(
            case,
            DonorEnvelopeVerdict.IDEAL_DONOR_PRODUCT_EQUIVALENCE,
            "the envelope strictly separates the native donor on a registered witness",
            "an ideal donor product with the same information ties the envelope",
            "the supported result is a composition/interface boundary, not inherent superiority",
        )
    if case.unresolved_route_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_OPEN_ROUTES,
            *(f"open donor or formulation route: {route}" for route in case.unresolved_route_ids),
        )
    if not case.falsifier_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_NO_FALSIFIER,
            "strict-envelope promotion requires registered falsifiers",
        )
    if not case.fresh_evaluation_ids:
        return _assessment(
            case,
            DonorEnvelopeVerdict.BLOCKED_NO_FRESH_EVALUATION,
            "strict-envelope promotion requires fresh evaluation after the gate is frozen",
        )
    return _assessment(
        case,
        DonorEnvelopeVerdict.CANDIDATE_STRICT_ENVELOPE,
        "the donor is reconstructed and conservatively embedded",
        "a strict witness survives the strongest information-matched donor product",
        "registered falsifiers and fresh evaluation are bound",
        "the result remains a non-authorizing candidate envelope",
    )


__all__ = [
    "SCHEMA_ID",
    "DonorEnvelopeAssessment",
    "DonorEnvelopeCase",
    "DonorEnvelopeVerdict",
    "IdealDonorProductRelation",
    "assess_donor_envelope",
]
