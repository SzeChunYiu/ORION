"""Method layer: versioned methods, their boundaries, and why they failed before.

Extends ``orion.core.method.MethodState`` (method version, operator ids,
evaluator binding) with the four things a self-sustaining programme needs and
that state does not carry: the exact implementation bytes behind a version, the
assumptions under which the method is claimed to apply, the causal link from an
observed failure to the intervention that answered it, and the negative history
that stops a dead branch being re-proposed as new.

Two rules are enforced rather than described. Failure attribution is
single-stage: a causal-support link that names several stages is diffuse effort
wearing the costume of an explanation, and is rejected. And fresh-transfer
evidence must be independently verified — a method that graded its own transfer
has produced no transfer evidence at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orion.programme.coordinates import coordinate_errors
from orion.programme.identity import METHOD_KNOWLEDGE_SCHEMA, is_sha256, seal
from orion.programme.records import Outcome, dedup, required_text_errors


@dataclass(frozen=True)
class ImplementationIdentity:
    """Exactly which bytes and which protocol a method version denotes."""

    module_path: str
    source_sha256: str
    protocol_id: str
    protocol_document_digest: str

    def __post_init__(self) -> None:
        if not self.module_path.strip() or not self.protocol_id.strip():
            raise ValueError("implementation module path and protocol id are required")
        if not is_sha256(self.source_sha256) or not is_sha256(self.protocol_document_digest):
            raise ValueError("implementation identity hashes must be SHA-256")


@dataclass(frozen=True)
class ApplicabilityBoundary:
    """One assumption, and the observation that would put the method outside it."""

    boundary_id: str
    assumption: str
    violated_when: str
    checked: Outcome = Outcome.CANNOT_CHECK


@dataclass(frozen=True)
class CausalSupportLink:
    """A failure, the single stage it was attributed to, and the intervention applied."""

    link_id: str
    failure_class: str
    attributed_stage: str
    intervention_id: str
    evidence_ids: tuple[str, ...] = ()
    competing_explanations: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransferEvidence:
    """Replay or fresh-transfer evidence for one method version."""

    evidence_id: str
    kind: str  # "REPLAY" | "FRESH_TRANSFER"
    epoch_id: str
    evaluator_artifact_hash: str
    outcome: Outcome = Outcome.CANNOT_CHECK
    independently_verified: bool = False
    evaluator_outside_candidate_custody: bool = False

    def __post_init__(self) -> None:
        if self.kind not in {"REPLAY", "FRESH_TRANSFER"}:
            raise ValueError("transfer evidence kind must be REPLAY or FRESH_TRANSFER")
        if not is_sha256(self.evaluator_artifact_hash):
            raise ValueError("transfer evidence evaluator hash must be SHA-256")


@dataclass(frozen=True)
class MethodKnowledgeRecord:
    """One versioned method with its boundaries, causal support and negative history."""

    method_id: str
    method_version: str
    implementation: ImplementationIdentity
    applicability: tuple[ApplicabilityBoundary, ...]
    causal_support: tuple[CausalSupportLink, ...]
    transfer_evidence: tuple[TransferEvidence, ...]
    known_failure_classes: tuple[str, ...] = ()
    negative_history_entry_ids: tuple[str, ...] = ()
    negative_history_chain_digest: str | None = None
    depends_on_coordinates: tuple[str, ...] = ("M",)
    supersedes_method_versions: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def fresh_transfer(self) -> tuple[TransferEvidence, ...]:
        return tuple(item for item in self.transfer_evidence if item.kind == "FRESH_TRANSFER")

    @property
    def replay(self) -> tuple[TransferEvidence, ...]:
        return tuple(item for item in self.transfer_evidence if item.kind == "REPLAY")


def method_knowledge_payload(record: MethodKnowledgeRecord) -> dict[str, Any]:
    """Serialize one record to the sealed wire form."""

    return seal(
        {
            "schema_version": METHOD_KNOWLEDGE_SCHEMA,
            "method_id": record.method_id,
            "method_version": record.method_version,
            "implementation": {
                "module_path": record.implementation.module_path,
                "source_sha256": record.implementation.source_sha256,
                "protocol_id": record.implementation.protocol_id,
                "protocol_document_digest": record.implementation.protocol_document_digest,
            },
            "applicability": [
                {
                    "boundary_id": item.boundary_id,
                    "assumption": item.assumption,
                    "violated_when": item.violated_when,
                    "checked": item.checked.value,
                }
                for item in record.applicability
            ],
            "causal_support": [
                {
                    "link_id": item.link_id,
                    "failure_class": item.failure_class,
                    "attributed_stage": item.attributed_stage,
                    "intervention_id": item.intervention_id,
                    "evidence_ids": list(item.evidence_ids),
                    "competing_explanations": list(item.competing_explanations),
                }
                for item in record.causal_support
            ],
            "transfer_evidence": [
                {
                    "evidence_id": item.evidence_id,
                    "kind": item.kind,
                    "epoch_id": item.epoch_id,
                    "evaluator_artifact_hash": item.evaluator_artifact_hash,
                    "outcome": item.outcome.value,
                    "independently_verified": item.independently_verified,
                    "evaluator_outside_candidate_custody": (
                        item.evaluator_outside_candidate_custody
                    ),
                }
                for item in record.transfer_evidence
            ],
            "known_failure_classes": list(record.known_failure_classes),
            "negative_history_entry_ids": list(record.negative_history_entry_ids),
            "negative_history_chain_digest": record.negative_history_chain_digest,
            "depends_on_coordinates": list(record.depends_on_coordinates),
            "supersedes_method_versions": list(record.supersedes_method_versions),
            "metadata": [list(pair) for pair in record.metadata],
        }
    )


def validate_method_knowledge_record(record: MethodKnowledgeRecord) -> tuple[str, ...]:
    """Return deduplicated blockers for one versioned method."""

    errors: list[str] = []
    errors.extend(required_text_errors(record.method_id, "method_id"))
    errors.extend(required_text_errors(record.method_version, "method_version"))
    errors.extend(coordinate_errors(record.depends_on_coordinates, "depends_on_coordinates"))

    if not record.applicability:
        errors.append(
            "a method with no declared applicability boundary claims to apply"
            " everywhere, which is not a claim that can fail"
        )

    for link in record.causal_support:
        if not link.attributed_stage.strip():
            errors.append(f"causal link {link.link_id} names no attributed stage")
        elif "," in link.attributed_stage or "+" in link.attributed_stage:
            errors.append(
                f"causal link {link.link_id} attributes failure to several stages;"
                " attribution must isolate one stage before an intervention counts"
            )
        if not link.intervention_id.strip():
            errors.append(f"causal link {link.link_id} names no intervention")
        if not link.evidence_ids:
            errors.append(f"causal link {link.link_id} carries no evidence")

    for item in record.transfer_evidence:
        if item.kind == "FRESH_TRANSFER":
            if not item.independently_verified:
                errors.append(
                    f"fresh-transfer evidence {item.evidence_id} is self-verified"
                )
            if not item.evaluator_outside_candidate_custody:
                errors.append(
                    f"fresh-transfer evidence {item.evidence_id} was graded by an"
                    " evaluator inside candidate custody"
                )

    if record.negative_history_entry_ids and record.negative_history_chain_digest is None:
        errors.append(
            "negative history entries are cited without a chain digest binding them;"
            " uncommitted negative history can be edited after the fact"
        )
    if record.negative_history_chain_digest is not None and not is_sha256(
        record.negative_history_chain_digest
    ):
        errors.append("negative_history_chain_digest must be SHA-256")

    return dedup(errors)


def method_promotion_blockers(record: MethodKnowledgeRecord) -> tuple[str, ...]:
    """Blockers that stand between an admissible method record and *selection*.

    Kept separate from :func:`validate_method_knowledge_record` on purpose: a
    record can be perfectly well-formed and still have no business being chosen.
    """

    errors = list(validate_method_knowledge_record(record))
    if not record.replay:
        errors.append("no motivating replay evidence")
    if not record.fresh_transfer:
        errors.append("no independent fresh-transfer evidence")
    if any(item.outcome is not Outcome.PASS for item in record.fresh_transfer):
        errors.append("fresh-transfer evidence does not pass")
    unchecked = [item.boundary_id for item in record.applicability
                 if item.checked is Outcome.CANNOT_CHECK]
    if unchecked:
        errors.append(f"applicability boundaries never checked: {sorted(unchecked)}")
    return dedup(errors)


__all__ = [
    "ApplicabilityBoundary",
    "CausalSupportLink",
    "ImplementationIdentity",
    "MethodKnowledgeRecord",
    "TransferEvidence",
    "method_knowledge_payload",
    "method_promotion_blockers",
    "validate_method_knowledge_record",
]
