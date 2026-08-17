"""Evidence-bound transfer selector. Surface similarity is a baseline, never authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from orion.transfer.scientific.objects import ProblemSignatureV3, ScientificTransferObject
from orion.transfer.v2.canonical import content_digest, verify_digest

RECEIPT_VERSION = "ORION_SCIENTIFIC_TRANSFER_RECEIPT_V1"
ENGINEERING_AUTHORITY = "LOCAL_ENGINEERING_ONLY"


class SelectorKind(str, Enum):
    EVIDENCE_BOUND_CONTRACT = "EVIDENCE_BOUND_CONTRACT"
    SURFACE_SIMILARITY_BASELINE = "SURFACE_SIMILARITY_BASELINE"


class TransferDecision(str, Enum):
    ADMITTED = "ADMITTED"
    RANKED_FOR_INSPECTION = "RANKED_FOR_INSPECTION"
    REFUSED_ASSUMPTION_MISMATCH = "REFUSED_ASSUMPTION_MISMATCH"
    REFUSED_PRECONDITION_OMITTED = "REFUSED_PRECONDITION_OMITTED"
    REFUSED_STALE_EVIDENCE = "REFUSED_STALE_EVIDENCE"
    REFUSED_UNAVAILABLE_TOOL = "REFUSED_UNAVAILABLE_TOOL"
    REFUSED_CORRUPTED_FALSIFIER = "REFUSED_CORRUPTED_FALSIFIER"
    REFUSED_FALSIFIER_FAILED = "REFUSED_FALSIFIER_FAILED"
    REFUSED_NO_EXECUTABLE_MECHANIC = "REFUSED_NO_EXECUTABLE_MECHANIC"
    REFUSED_FORBIDDEN = "REFUSED_FORBIDDEN"
    CANNOT_CHECK = "CANNOT_CHECK"


def _tokens(signature: ProblemSignatureV3) -> set[str]:
    text = " ".join(
        [
            signature.family_id,
            signature.surface_domain,
            signature.hidden_state,
            signature.observability,
            *signature.actions,
        ]
    )
    normalized = text.lower().replace("-", " ").replace("_", " ")
    return {token for token in normalized.split() if token}


def surface_similarity(source: ProblemSignatureV3, target: ProblemSignatureV3) -> float:
    left = _tokens(source)
    right = _tokens(target)
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def _mapping(name: str, raw: Any) -> dict[str, bool | None]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{name} must be an object")
    out: dict[str, bool | None] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or value not in (True, False, None):
            raise ValueError(f"{name} values must be true/false/null")
        out[key] = value
    return out


def evidence_payload(evidence: Mapping[str, Any]) -> dict[str, object]:
    tools = evidence.get("available_tools", [])
    if not isinstance(tools, (list, tuple, set, frozenset)) or not all(
        isinstance(item, str) and item for item in tools
    ):
        raise ValueError("available_tools must be strings")
    provenance = evidence.get("provenance", [])
    if not isinstance(provenance, (list, tuple)) or not all(
        isinstance(item, str) and item for item in provenance
    ):
        raise ValueError("provenance must be non-empty strings")
    return {
        "assumptions": _mapping("assumptions", evidence.get("assumptions", {})),
        "preconditions": _mapping("preconditions", evidence.get("preconditions", {})),
        "falsifiers": _mapping("falsifiers", evidence.get("falsifiers", {})),
        "evidence_fresh": evidence.get("evidence_fresh"),
        "available_tools": sorted(set(tools)),
        "falsifier_integrity": evidence.get("falsifier_integrity"),
        "provenance": sorted(set(provenance)),
    }


def _executable_mechanic(source: ScientificTransferObject) -> bool:
    if any(step == "apply-abstract-advice" for step in source.transformation_steps):
        return False
    return any(
        step == "active_discriminator" or step.startswith("mechanic:")
        for step in source.transformation_steps
    )


def _decide(
    source: ScientificTransferObject,
    evidence: Mapping[str, Any],
    selector: SelectorKind,
) -> tuple[TransferDecision, tuple[str, ...]]:
    if selector is SelectorKind.SURFACE_SIMILARITY_BASELINE:
        return TransferDecision.RANKED_FOR_INSPECTION, ("SURFACE_SIMILARITY_NOT_AUTHORITY",)
    if not _executable_mechanic(source):
        return (
            TransferDecision.REFUSED_NO_EXECUTABLE_MECHANIC,
            ("INSIGHT_NOT_EXECUTABLE_MECHANIC",),
        )
    bound = evidence_payload(evidence)
    if bound["falsifier_integrity"] is False:
        return TransferDecision.REFUSED_CORRUPTED_FALSIFIER, ("FALSIFIER_CORRUPTED",)
    if bound["evidence_fresh"] is False:
        return TransferDecision.REFUSED_STALE_EVIDENCE, ("SOURCE_EVIDENCE_STALE",)
    missing_tools = [
        tool
        for tool in source.cost_requirements.tools_required
        if tool not in set(bound["available_tools"])  # type: ignore[arg-type]
    ]
    if missing_tools:
        return (
            TransferDecision.REFUSED_UNAVAILABLE_TOOL,
            tuple(f"TOOL_UNAVAILABLE:{tool}" for tool in missing_tools),
        )
    assumptions = bound["assumptions"]  # type: ignore[assignment]
    failed_assumptions = tuple(name for name in source.assumptions if assumptions.get(name) is False)
    if failed_assumptions:
        return (
            TransferDecision.REFUSED_ASSUMPTION_MISMATCH,
            tuple(f"ASSUMPTION_FALSE:{name}" for name in failed_assumptions),
        )
    omitted = tuple(name for name in source.preconditions if bound["preconditions"].get(name) is None)
    if omitted:
        return (
            TransferDecision.REFUSED_PRECONDITION_OMITTED,
            tuple(f"PRECONDITION_OMITTED:{name}" for name in omitted),
        )
    failed_pre = tuple(
        name for name in source.preconditions if bound["preconditions"].get(name) is False
    )
    if failed_pre:
        return (
            TransferDecision.REFUSED_PRECONDITION_OMITTED,
            tuple(f"PRECONDITION_FALSE:{name}" for name in failed_pre),
        )
    failed_falsifiers = tuple(
        name for name in source.falsifiers if bound["falsifiers"].get(name) is False
    )
    if failed_falsifiers:
        return (
            TransferDecision.REFUSED_FALSIFIER_FAILED,
            tuple(f"FALSIFIER_FAILED:{name}" for name in failed_falsifiers),
        )
    unknown_assumptions = tuple(
        name for name in source.assumptions if assumptions.get(name) is None
    )
    unknown_falsifiers = tuple(
        name for name in source.falsifiers if bound["falsifiers"].get(name) is None
    )
    if unknown_assumptions or unknown_falsifiers:
        reasons = tuple(f"ASSUMPTION_UNKNOWN:{name}" for name in unknown_assumptions) + tuple(
            f"FALSIFIER_UNKNOWN:{name}" for name in unknown_falsifiers
        )
        return TransferDecision.CANNOT_CHECK, reasons
    forbidden_hit = tuple(
        item for item in source.forbidden_transfers if item in source.transformation_steps
    )
    if forbidden_hit:
        return (
            TransferDecision.REFUSED_FORBIDDEN,
            tuple(f"FORBIDDEN:{item}" for item in forbidden_hit),
        )
    return TransferDecision.ADMITTED, ("ALL_DECLARED_CONDITIONS_PASSED",)


@dataclass(frozen=True)
class ScientificTransferReceipt:
    receipt_version: str
    source_object_id: str
    source_digest: str
    target_signature_id: str
    target_digest: str
    evidence_digest: str
    status: TransferDecision
    reason_codes: tuple[str, ...]
    surface_similarity: float
    selector_kind: SelectorKind
    harmful_candidate_retained: bool
    evidence_level: str
    scientific_authority: bool
    authority: str
    receipt_digest: str

    @property
    def admitted(self) -> bool:
        return self.status is TransferDecision.ADMITTED

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": self.receipt_version,
            "source_object_id": self.source_object_id,
            "source_digest": self.source_digest,
            "target_signature_id": self.target_signature_id,
            "target_digest": self.target_digest,
            "evidence_digest": self.evidence_digest,
            "status": self.status.value,
            "reason_codes": list(self.reason_codes),
            "surface_similarity": self.surface_similarity,
            "selector_kind": self.selector_kind.value,
            "harmful_candidate_retained": self.harmful_candidate_retained,
            "evidence_level": self.evidence_level,
            "scientific_authority": self.scientific_authority,
            "authority": self.authority,
        }

    def verify(self) -> None:
        if self.receipt_version != RECEIPT_VERSION:
            raise ValueError("unsupported scientific transfer receipt version")
        verify_digest(self.unsigned_payload(), self.receipt_digest)


def select_transfer(
    source: ScientificTransferObject,
    target: ProblemSignatureV3,
    *,
    evidence: Mapping[str, Any],
    selector: SelectorKind,
) -> ScientificTransferReceipt:
    source.verify()
    score = surface_similarity(source.problem_signature, target)
    status, reasons = _decide(source, evidence, selector)
    retained = status is not TransferDecision.ADMITTED
    unsigned = {
        "receipt_version": RECEIPT_VERSION,
        "source_object_id": source.object_id,
        "source_digest": source.content_hash,
        "target_signature_id": target.signature_id,
        "target_digest": content_digest(target.to_payload()),
        "evidence_digest": content_digest(evidence_payload(evidence)),
        "status": status.value,
        "reason_codes": list(reasons),
        "surface_similarity": score,
        "selector_kind": selector.value,
        "harmful_candidate_retained": retained,
        "evidence_level": source.evidence_level,
        "scientific_authority": False,
        "authority": ENGINEERING_AUTHORITY,
    }
    return ScientificTransferReceipt(
        receipt_version=RECEIPT_VERSION,
        source_object_id=source.object_id,
        source_digest=source.content_hash,
        target_signature_id=target.signature_id,
        target_digest=unsigned["target_digest"],  # type: ignore[arg-type]
        evidence_digest=unsigned["evidence_digest"],  # type: ignore[arg-type]
        status=status,
        reason_codes=reasons,
        surface_similarity=score,
        selector_kind=selector,
        harmful_candidate_retained=retained,
        evidence_level=source.evidence_level,
        scientific_authority=False,
        authority=ENGINEERING_AUTHORITY,
        receipt_digest=content_digest(unsigned),
    )
