"""Typed proposal record for concept/primitive invention studies.

The record is intentionally stricter than free-form hypothesis prose but much
weaker than scientific validation.  It requires structural declarations,
semantic/type-judgment lineage, an old-to-new correspondence map, claimed
unlocked contracts, and protected consequence requests.  All validity, novelty,
utility, and adoption authority remain external.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _ordered(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


def _canonical_correspondence(
    values: Mapping[str, str],
) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for raw_old, raw_new in values.items():
        old = str(raw_old)
        new = str(raw_new)
        if not old or not new:
            raise ValueError("concept correspondence identities must be non-empty")
        rows.append((old, new))
    rows.sort(key=lambda row: row[0])
    if len({old for old, _ in rows}) != len(rows):
        raise ValueError("duplicate concept correspondence source")
    return tuple(rows)


@dataclass(frozen=True)
class ConceptCandidate:
    concept_id: str
    source_regime_id: str
    source_tension_digests: tuple[str, ...]
    thought_experiment_digests: tuple[str, ...]
    transformation_steps: tuple[str, ...]
    structural_declarations: tuple[str, ...]
    semantic_judgment_ids: tuple[str, ...]
    correspondence_map: tuple[tuple[str, str], ...]
    executable_artifact_id: str | None
    unlocked_contract_ids: tuple[str, ...]
    protected_consequence_request_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    validity_state: str
    digest: str

    @property
    def grants_validity_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ConceptCandidate.v1",
            "concept_id": self.concept_id,
            "source_regime_id": self.source_regime_id,
            "source_tension_digests": list(self.source_tension_digests),
            "thought_experiment_digests": list(self.thought_experiment_digests),
            "transformation_steps": list(self.transformation_steps),
            "structural_declarations": list(self.structural_declarations),
            "semantic_judgment_ids": list(self.semantic_judgment_ids),
            "correspondence_map": [list(row) for row in self.correspondence_map],
            "executable_artifact_id": self.executable_artifact_id,
            "unlocked_contract_ids": list(self.unlocked_contract_ids),
            "protected_consequence_request_ids": list(
                self.protected_consequence_request_ids
            ),
            "lineage_ids": list(self.lineage_ids),
            "validity_state": self.validity_state,
            "grants_validity_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if not self.concept_id or not self.source_regime_id:
            raise ValueError("concept and source regime identities are required")
        if not self.transformation_steps:
            raise ValueError("concept candidate requires a transformation trace")
        if any(not step for step in self.transformation_steps):
            raise ValueError("concept transformation step identities must be non-empty")
        if not self.structural_declarations:
            raise ValueError("concept candidate requires structural declarations")
        if not self.semantic_judgment_ids:
            raise ValueError("concept candidate requires semantic/type judgment identities")
        if not self.correspondence_map:
            raise ValueError("concept candidate requires an old-to-new correspondence map")
        if not self.unlocked_contract_ids:
            raise ValueError("concept candidate requires at least one claimed unlocked contract")
        if not self.protected_consequence_request_ids:
            raise ValueError(
                "concept candidate requires a protected consequence request for later validation"
            )
        if self.validity_state != "PROPOSAL_ONLY":
            raise ValueError("concept candidate cannot self-promote beyond PROPOSAL_ONLY")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("concept candidate digest mismatch")


def build_concept_candidate(
    *,
    concept_id: str,
    source_regime_id: str,
    transformation_steps: Sequence[str],
    structural_declarations: Sequence[str],
    semantic_judgment_ids: Sequence[str],
    correspondence_map: Mapping[str, str],
    unlocked_contract_ids: Sequence[str],
    protected_consequence_request_ids: Sequence[str],
    source_tension_digests: Sequence[str] = (),
    thought_experiment_digests: Sequence[str] = (),
    executable_artifact_id: str | None = None,
    lineage_ids: Sequence[str] = (),
) -> ConceptCandidate:
    correspondence = _canonical_correspondence(correspondence_map)
    payload = {
        "version": "ConceptCandidate.v1",
        "concept_id": str(concept_id),
        "source_regime_id": str(source_regime_id),
        "source_tension_digests": list(_sorted_unique(source_tension_digests)),
        "thought_experiment_digests": list(
            _sorted_unique(thought_experiment_digests)
        ),
        "transformation_steps": list(_ordered(transformation_steps)),
        "structural_declarations": list(_sorted_unique(structural_declarations)),
        "semantic_judgment_ids": list(_sorted_unique(semantic_judgment_ids)),
        "correspondence_map": [list(row) for row in correspondence],
        "executable_artifact_id": (
            str(executable_artifact_id) if executable_artifact_id is not None else None
        ),
        "unlocked_contract_ids": list(_sorted_unique(unlocked_contract_ids)),
        "protected_consequence_request_ids": list(
            _sorted_unique(protected_consequence_request_ids)
        ),
        "lineage_ids": list(_sorted_unique(lineage_ids)),
        "validity_state": "PROPOSAL_ONLY",
        "grants_validity_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
    }
    candidate = ConceptCandidate(
        concept_id=payload["concept_id"],
        source_regime_id=payload["source_regime_id"],
        source_tension_digests=tuple(payload["source_tension_digests"]),
        thought_experiment_digests=tuple(payload["thought_experiment_digests"]),
        transformation_steps=tuple(payload["transformation_steps"]),
        structural_declarations=tuple(payload["structural_declarations"]),
        semantic_judgment_ids=tuple(payload["semantic_judgment_ids"]),
        correspondence_map=correspondence,
        executable_artifact_id=payload["executable_artifact_id"],
        unlocked_contract_ids=tuple(payload["unlocked_contract_ids"]),
        protected_consequence_request_ids=tuple(
            payload["protected_consequence_request_ids"]
        ),
        lineage_ids=tuple(payload["lineage_ids"]),
        validity_state="PROPOSAL_ONLY",
        digest=content_digest(payload),
    )
    candidate.verify()
    return candidate


__all__ = ["ConceptCandidate", "build_concept_candidate"]
