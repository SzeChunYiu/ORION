from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

from .canonical import content_digest


class MethodAuthorityCoordinate(str, Enum):
    VALIDITY = "VALIDITY"
    APPLICABILITY = "APPLICABILITY"
    TRANSFER = "TRANSFER"
    NOVELTY = "NOVELTY"
    UTILITY = "UTILITY"
    ADOPTION = "ADOPTION"


class MethodAuthorityState(str, Enum):
    SUPPORTED = "SUPPORTED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MethodTransferReceipt:
    """Content-bound evidence record for transferred/generated method claims.

    The receipt is evidence input, not an authority declaration.  Coordinate
    authority is derived separately and P4 never grants Self-ORION adoption.
    """

    method_id: str
    target_id: str
    target_digest: str
    donor_ids: tuple[str, ...]
    donor_digests: tuple[str, ...]
    structural_signature_digest: str
    assumptions_retained: tuple[str, ...]
    assumptions_dropped: tuple[str, ...]
    assumptions_modified: tuple[str, ...]
    adaptation_steps: tuple[str, ...]
    predicted_effects: tuple[str, ...]
    reconstruction: str
    source_lineage_valid: bool | None
    assumptions_preserved: bool | None
    reconstruction_valid: bool | None
    visible_result_pass: bool | None
    protected_result_pass: bool | None
    evaluator_independent: bool | None
    evaluator_digest: str
    generator_accessed_evaluator: bool
    novelty_search_digest: str
    prior_art_found: bool | None
    claims_new_primitive: bool
    known_composition: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        if not self.method_id or not self.target_id:
            raise ValueError("method_id and target_id must be non-empty")
        if len(self.donor_ids) != len(self.donor_digests):
            raise ValueError("donor ids and digests must have equal length")
        for label, digest in (
            ("target_digest", self.target_digest),
            ("structural_signature_digest", self.structural_signature_digest),
        ):
            if not digest.startswith("sha256:"):
                raise ValueError(f"{label} must be sha256-prefixed")
        for digest in self.donor_digests:
            if not digest.startswith("sha256:"):
                raise ValueError("donor digests must be sha256-prefixed")
        if self.evaluator_digest and not self.evaluator_digest.startswith("sha256:"):
            raise ValueError("evaluator_digest must be sha256-prefixed when present")
        if self.novelty_search_digest and not self.novelty_search_digest.startswith("sha256:"):
            raise ValueError("novelty_search_digest must be sha256-prefixed when present")

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "MethodTransferReceipt.v1",
            "method_id": self.method_id,
            "target_id": self.target_id,
            "target_digest": self.target_digest,
            "donor_ids": list(self.donor_ids),
            "donor_digests": list(self.donor_digests),
            "structural_signature_digest": self.structural_signature_digest,
            "assumptions_retained": list(self.assumptions_retained),
            "assumptions_dropped": list(self.assumptions_dropped),
            "assumptions_modified": list(self.assumptions_modified),
            "adaptation_steps": list(self.adaptation_steps),
            "predicted_effects": list(self.predicted_effects),
            "reconstruction": self.reconstruction,
            "source_lineage_valid": self.source_lineage_valid,
            "assumptions_preserved": self.assumptions_preserved,
            "reconstruction_valid": self.reconstruction_valid,
            "visible_result_pass": self.visible_result_pass,
            "protected_result_pass": self.protected_result_pass,
            "evaluator_independent": self.evaluator_independent,
            "evaluator_digest": self.evaluator_digest,
            "generator_accessed_evaluator": self.generator_accessed_evaluator,
            "novelty_search_digest": self.novelty_search_digest,
            "prior_art_found": self.prior_art_found,
            "claims_new_primitive": self.claims_new_primitive,
            "known_composition": self.known_composition,
            "authority_terminal": "NONE",
            "adoption_owner": "P5_HOST_GOVERNANCE",
        }

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("MethodTransferReceipt.v1 digest mismatch")


def build_method_transfer_receipt(
    *,
    method_id: str,
    target_id: str,
    target_digest: str,
    donor_ids: Sequence[str],
    donor_digests: Sequence[str],
    structural_signature_digest: str,
    assumptions_retained: Sequence[str] = (),
    assumptions_dropped: Sequence[str] = (),
    assumptions_modified: Sequence[str] = (),
    adaptation_steps: Sequence[str] = (),
    predicted_effects: Sequence[str] = (),
    reconstruction: str,
    source_lineage_valid: bool | None,
    assumptions_preserved: bool | None,
    reconstruction_valid: bool | None,
    visible_result_pass: bool | None,
    protected_result_pass: bool | None,
    evaluator_independent: bool | None,
    evaluator_digest: str = "",
    generator_accessed_evaluator: bool = False,
    novelty_search_digest: str = "",
    prior_art_found: bool | None = None,
    claims_new_primitive: bool = False,
    known_composition: bool = False,
) -> MethodTransferReceipt:
    base = {
        "receipt_version": "MethodTransferReceipt.v1",
        "method_id": method_id,
        "target_id": target_id,
        "target_digest": target_digest,
        "donor_ids": sorted(str(value) for value in donor_ids),
        "donor_digests": sorted(str(value) for value in donor_digests),
        "structural_signature_digest": structural_signature_digest,
        "assumptions_retained": sorted(str(value) for value in assumptions_retained),
        "assumptions_dropped": sorted(str(value) for value in assumptions_dropped),
        "assumptions_modified": sorted(str(value) for value in assumptions_modified),
        "adaptation_steps": list(str(value) for value in adaptation_steps),
        "predicted_effects": list(str(value) for value in predicted_effects),
        "reconstruction": reconstruction,
        "source_lineage_valid": source_lineage_valid,
        "assumptions_preserved": assumptions_preserved,
        "reconstruction_valid": reconstruction_valid,
        "visible_result_pass": visible_result_pass,
        "protected_result_pass": protected_result_pass,
        "evaluator_independent": evaluator_independent,
        "evaluator_digest": evaluator_digest,
        "generator_accessed_evaluator": generator_accessed_evaluator,
        "novelty_search_digest": novelty_search_digest,
        "prior_art_found": prior_art_found,
        "claims_new_primitive": claims_new_primitive,
        "known_composition": known_composition,
        "authority_terminal": "NONE",
        "adoption_owner": "P5_HOST_GOVERNANCE",
    }
    receipt = MethodTransferReceipt(
        method_id=method_id,
        target_id=target_id,
        target_digest=target_digest,
        donor_ids=tuple(base["donor_ids"]),
        donor_digests=tuple(base["donor_digests"]),
        structural_signature_digest=structural_signature_digest,
        assumptions_retained=tuple(base["assumptions_retained"]),
        assumptions_dropped=tuple(base["assumptions_dropped"]),
        assumptions_modified=tuple(base["assumptions_modified"]),
        adaptation_steps=tuple(base["adaptation_steps"]),
        predicted_effects=tuple(base["predicted_effects"]),
        reconstruction=reconstruction,
        source_lineage_valid=source_lineage_valid,
        assumptions_preserved=assumptions_preserved,
        reconstruction_valid=reconstruction_valid,
        visible_result_pass=visible_result_pass,
        protected_result_pass=protected_result_pass,
        evaluator_independent=evaluator_independent,
        evaluator_digest=evaluator_digest,
        generator_accessed_evaluator=generator_accessed_evaluator,
        novelty_search_digest=novelty_search_digest,
        prior_art_found=prior_art_found,
        claims_new_primitive=claims_new_primitive,
        known_composition=known_composition,
        receipt_digest=content_digest(base),
    )
    receipt.verify()
    return receipt


@dataclass(frozen=True)
class CoordinateAuthority:
    coordinate: MethodAuthorityCoordinate
    state: MethodAuthorityState
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class MethodAuthorityRecord:
    method_id: str
    target_id: str
    method_receipt_digest: str
    coordinates: tuple[CoordinateAuthority, ...]
    authority_terminal: str
    record_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "record_version": "P4_METHOD_AUTHORITY_RECORD_V1",
            "method_id": self.method_id,
            "target_id": self.target_id,
            "method_receipt_digest": self.method_receipt_digest,
            "coordinates": [
                {
                    "coordinate": entry.coordinate.value,
                    "state": entry.state.value,
                    "reason_codes": list(entry.reason_codes),
                }
                for entry in self.coordinates
            ],
            "authority_terminal": self.authority_terminal,
            "adoption_owner": "P5_HOST_GOVERNANCE",
        }

    def verify(self) -> None:
        if self.authority_terminal != "COORDINATE_PRODUCT_ONLY":
            raise ValueError("P4 method authority must remain coordinate-product scoped")
        if content_digest(self.unsigned_payload()) != self.record_digest:
            raise ValueError("P4 method authority record digest mismatch")

    def state(self, coordinate: MethodAuthorityCoordinate) -> MethodAuthorityState:
        for entry in self.coordinates:
            if entry.coordinate is coordinate:
                return entry.state
        raise KeyError(coordinate)

    def reasons(self, coordinate: MethodAuthorityCoordinate) -> tuple[str, ...]:
        for entry in self.coordinates:
            if entry.coordinate is coordinate:
                return entry.reason_codes
        raise KeyError(coordinate)


def _entry(
    coordinate: MethodAuthorityCoordinate,
    state: MethodAuthorityState,
    *reasons: str,
) -> CoordinateAuthority:
    return CoordinateAuthority(coordinate, state, tuple(sorted(set(reasons))))


def derive_method_authority(receipt: MethodTransferReceipt) -> MethodAuthorityRecord:
    receipt.verify()
    entries: list[CoordinateAuthority] = []

    # VALIDITY: visible success never substitutes for protected, independent evidence.
    if receipt.generator_accessed_evaluator:
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.BLOCKED, "EVALUATOR_LEAKAGE"))
    elif receipt.reconstruction_valid is False:
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.BLOCKED, "RECONSTRUCTION_INVALID"))
    elif receipt.protected_result_pass is False:
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.BLOCKED, "PROTECTED_RESULT_FAILED"))
    elif receipt.evaluator_independent is False:
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.BLOCKED, "EVALUATOR_NOT_INDEPENDENT"))
    elif (
        receipt.protected_result_pass is None
        or receipt.reconstruction_valid is None
        or receipt.evaluator_independent is None
        or not receipt.evaluator_digest
    ):
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.CANNOT_CHECK, "PROTECTED_VALIDITY_EVIDENCE_INCOMPLETE"))
    else:
        entries.append(_entry(MethodAuthorityCoordinate.VALIDITY, MethodAuthorityState.SUPPORTED, "PROTECTED_VALIDITY_SUPPORTED"))

    # APPLICABILITY: dropping or changing a load-bearing assumption blocks the target claim.
    if receipt.assumptions_preserved is False or receipt.assumptions_dropped or receipt.assumptions_modified:
        reasons = ["ASSUMPTION_FOOTPRINT_CHANGED"]
        if receipt.assumptions_dropped:
            reasons.append("ASSUMPTION_DROPPED")
        if receipt.assumptions_modified:
            reasons.append("ASSUMPTION_MODIFIED")
        entries.append(_entry(MethodAuthorityCoordinate.APPLICABILITY, MethodAuthorityState.BLOCKED, *reasons))
    elif receipt.assumptions_preserved is None:
        entries.append(_entry(MethodAuthorityCoordinate.APPLICABILITY, MethodAuthorityState.CANNOT_CHECK, "ASSUMPTION_PRESERVATION_UNKNOWN"))
    else:
        entries.append(_entry(MethodAuthorityCoordinate.APPLICABILITY, MethodAuthorityState.SUPPORTED, "TARGET_ASSUMPTIONS_PRESERVED"))

    # TRANSFER: structural similarity alone is insufficient; lineage, assumptions and reconstruction all matter.
    transfer_reasons: list[str] = []
    transfer_blocked = False
    transfer_unknown = False
    if receipt.source_lineage_valid is False:
        transfer_blocked = True
        transfer_reasons.append("SOURCE_LINEAGE_INVALID")
    elif receipt.source_lineage_valid is None or not receipt.donor_ids:
        transfer_unknown = True
        transfer_reasons.append("SOURCE_LINEAGE_UNKNOWN")
    if receipt.assumptions_preserved is False or receipt.assumptions_dropped or receipt.assumptions_modified:
        transfer_blocked = True
        transfer_reasons.append("ASSUMPTION_FOOTPRINT_CHANGED")
    elif receipt.assumptions_preserved is None:
        transfer_unknown = True
        transfer_reasons.append("ASSUMPTION_PRESERVATION_UNKNOWN")
    if receipt.reconstruction_valid is False:
        transfer_blocked = True
        transfer_reasons.append("RECONSTRUCTION_INVALID")
    elif receipt.reconstruction_valid is None:
        transfer_unknown = True
        transfer_reasons.append("RECONSTRUCTION_UNKNOWN")
    if transfer_blocked:
        entries.append(_entry(MethodAuthorityCoordinate.TRANSFER, MethodAuthorityState.BLOCKED, *transfer_reasons))
    elif transfer_unknown:
        entries.append(_entry(MethodAuthorityCoordinate.TRANSFER, MethodAuthorityState.CANNOT_CHECK, *transfer_reasons))
    else:
        entries.append(_entry(MethodAuthorityCoordinate.TRANSFER, MethodAuthorityState.SUPPORTED, "DONOR_TARGET_MAPPING_SUPPORTED"))

    # NOVELTY: semantic distance and generation are irrelevant; current prior-art evidence is required.
    if receipt.prior_art_found is True:
        entries.append(_entry(MethodAuthorityCoordinate.NOVELTY, MethodAuthorityState.BLOCKED, "PRIOR_ART_FOUND"))
    elif receipt.claims_new_primitive and receipt.known_composition:
        entries.append(_entry(MethodAuthorityCoordinate.NOVELTY, MethodAuthorityState.BLOCKED, "KNOWN_COMPOSITION_NOT_NEW_PRIMITIVE"))
    elif receipt.prior_art_found is None or not receipt.novelty_search_digest:
        entries.append(_entry(MethodAuthorityCoordinate.NOVELTY, MethodAuthorityState.CANNOT_CHECK, "NOVELTY_SEARCH_INCOMPLETE"))
    else:
        entries.append(_entry(MethodAuthorityCoordinate.NOVELTY, MethodAuthorityState.SUPPORTED, "BOUNDED_NOVELTY_SEARCH_CLEAR"))

    # UTILITY: protected failure/harm dominates visible success.
    if receipt.generator_accessed_evaluator:
        entries.append(_entry(MethodAuthorityCoordinate.UTILITY, MethodAuthorityState.BLOCKED, "EVALUATOR_LEAKAGE"))
    elif receipt.protected_result_pass is False:
        entries.append(_entry(MethodAuthorityCoordinate.UTILITY, MethodAuthorityState.BLOCKED, "PROTECTED_RESULT_FAILED"))
    elif receipt.evaluator_independent is False:
        entries.append(_entry(MethodAuthorityCoordinate.UTILITY, MethodAuthorityState.BLOCKED, "EVALUATOR_NOT_INDEPENDENT"))
    elif receipt.protected_result_pass is None or receipt.evaluator_independent is None or not receipt.evaluator_digest:
        entries.append(_entry(MethodAuthorityCoordinate.UTILITY, MethodAuthorityState.CANNOT_CHECK, "PROTECTED_UTILITY_EVIDENCE_INCOMPLETE"))
    else:
        entries.append(_entry(MethodAuthorityCoordinate.UTILITY, MethodAuthorityState.SUPPORTED, "PROTECTED_UTILITY_SUPPORTED"))

    # ADOPTION is represented but deliberately cannot be granted by P4.
    entries.append(_entry(MethodAuthorityCoordinate.ADOPTION, MethodAuthorityState.CANNOT_CHECK, "P5_HOST_AUTHORITY_REQUIRED"))

    entries = sorted(entries, key=lambda entry: entry.coordinate.value)
    unsigned = {
        "record_version": "P4_METHOD_AUTHORITY_RECORD_V1",
        "method_id": receipt.method_id,
        "target_id": receipt.target_id,
        "method_receipt_digest": receipt.receipt_digest,
        "coordinates": [
            {
                "coordinate": entry.coordinate.value,
                "state": entry.state.value,
                "reason_codes": list(entry.reason_codes),
            }
            for entry in entries
        ],
        "authority_terminal": "COORDINATE_PRODUCT_ONLY",
        "adoption_owner": "P5_HOST_GOVERNANCE",
    }
    record = MethodAuthorityRecord(
        method_id=receipt.method_id,
        target_id=receipt.target_id,
        method_receipt_digest=receipt.receipt_digest,
        coordinates=tuple(entries),
        authority_terminal="COORDINATE_PRODUCT_ONLY",
        record_digest=content_digest(unsigned),
    )
    record.verify()
    return record


def claim_is_promotable(
    record: MethodAuthorityRecord,
    required: Iterable[MethodAuthorityCoordinate],
) -> bool:
    record.verify()
    required_tuple = tuple(required)
    if not required_tuple:
        raise ValueError("at least one authority coordinate must be required")
    if MethodAuthorityCoordinate.ADOPTION in required_tuple:
        return False
    return all(record.state(coordinate) is MethodAuthorityState.SUPPORTED for coordinate in required_tuple)
