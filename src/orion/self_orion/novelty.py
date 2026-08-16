from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DevelopmentNoveltyClass(str, Enum):
    STORED = "STORED"
    COMPOSITIONAL = "COMPOSITIONAL"
    TRANSFER_NOVEL = "TRANSFER_NOVEL"
    REPRESENTATION_NOVEL = "REPRESENTATION_NOVEL"
    OPERATOR_NOVEL = "OPERATOR_NOVEL"
    ONTOLOGY_NOVEL = "ONTOLOGY_NOVEL"
    UNRESOLVED = "UNRESOLVED"


NOVEL_STRUCTURE_RANK = {
    DevelopmentNoveltyClass.STORED: 0,
    DevelopmentNoveltyClass.COMPOSITIONAL: 0,
    DevelopmentNoveltyClass.TRANSFER_NOVEL: 0,
    DevelopmentNoveltyClass.REPRESENTATION_NOVEL: 1,
    DevelopmentNoveltyClass.OPERATOR_NOVEL: 2,
    DevelopmentNoveltyClass.ONTOLOGY_NOVEL: 3,
    DevelopmentNoveltyClass.UNRESOLVED: -1,
}


@dataclass(frozen=True)
class DevelopmentNoveltyEvidence:
    subject_id: str
    solution_verified: bool
    evidence_ids: tuple[str, ...]
    retrieved_solution_id: str | None = None
    used_operator_ids: tuple[str, ...] = ()
    preexisting_operator_ids: tuple[str, ...] = ()
    transfer_witness_ids: tuple[str, ...] = ()
    new_representation_ids: tuple[str, ...] = ()
    new_operator_ids: tuple[str, ...] = ()
    ontology_change_ids: tuple[str, ...] = ()
    all_required_resources_preexisting: bool = False

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("novelty evidence requires a subject id")
        if self.solution_verified and not self.evidence_ids:
            raise ValueError("verified novelty classification requires evidence")
        if set(self.new_operator_ids) - set(self.used_operator_ids):
            raise ValueError("new operators must be part of the used operator set")
        if set(self.new_operator_ids) & set(self.preexisting_operator_ids):
            raise ValueError("an operator cannot be both new and preexisting")


@dataclass(frozen=True)
class DevelopmentNoveltyReport:
    subject_id: str
    novelty_class: DevelopmentNoveltyClass
    novel_structure_rank: int
    reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    @property
    def requires_new_problem_solving_structure(self) -> bool:
        return self.novel_structure_rank > 0

    @property
    def requires_new_operator(self) -> bool:
        return self.novelty_class in {DevelopmentNoveltyClass.OPERATOR_NOVEL, DevelopmentNoveltyClass.ONTOLOGY_NOVEL}


def classify_development_novelty(evidence: DevelopmentNoveltyEvidence) -> DevelopmentNoveltyReport:
    """Classify the strongest genuinely new structure required by a verified result.

    This prevents Self-ORION from calling a cross-domain reuse or composition a new
    method. Unverified results remain unresolved rather than being assigned novelty.
    """

    if not evidence.solution_verified:
        novelty = DevelopmentNoveltyClass.UNRESOLVED
        reasons = ("result is not verified; structural novelty cannot be closed",)
    elif evidence.ontology_change_ids:
        novelty = DevelopmentNoveltyClass.ONTOLOGY_NOVEL
        reasons = ("verified result required a new ontology/schema-level capability",)
    elif evidence.new_operator_ids:
        novelty = DevelopmentNoveltyClass.OPERATOR_NOVEL
        reasons = ("verified result required at least one newly introduced operator",)
    elif evidence.new_representation_ids:
        novelty = DevelopmentNoveltyClass.REPRESENTATION_NOVEL
        reasons = ("verified result required a new representation/bridge but no new operator",)
    elif evidence.transfer_witness_ids:
        novelty = DevelopmentNoveltyClass.TRANSFER_NOVEL
        reasons = ("verified result reused preexisting structure under an explicit transfer witness",)
    elif evidence.retrieved_solution_id is not None:
        novelty = DevelopmentNoveltyClass.STORED
        reasons = ("verified result was retrieved from already registered knowledge",)
    else:
        all_ops_preexisting = set(evidence.used_operator_ids).issubset(evidence.preexisting_operator_ids)
        if evidence.all_required_resources_preexisting and all_ops_preexisting:
            novelty = DevelopmentNoveltyClass.COMPOSITIONAL
            reasons = ("verified result was composed entirely from preexisting registered resources/operators",)
        else:
            novelty = DevelopmentNoveltyClass.UNRESOLVED
            reasons = ("result is verified but resource/operator ancestry is insufficient to bound novelty",)
    return DevelopmentNoveltyReport(
        subject_id=evidence.subject_id,
        novelty_class=novelty,
        novel_structure_rank=NOVEL_STRUCTURE_RANK[novelty],
        reasons=reasons,
        evidence_ids=evidence.evidence_ids,
    )


__all__ = [
    "DevelopmentNoveltyClass",
    "DevelopmentNoveltyEvidence",
    "DevelopmentNoveltyReport",
    "NOVEL_STRUCTURE_RANK",
    "classify_development_novelty",
]
