from __future__ import annotations

from dataclasses import dataclass, field

from orion.knowledge.nearest_work import AbsorptionDecision
from orion.novelty.hashing import sha256_canonical
from orion.novelty.saturation import SearchSaturationProtocol
from orion.novelty.types import (
    SCHEMA_ID,
    ExperimentStatus,
    MechanismOverlap,
    NoveltyFinalState,
    NoveltySearchRoute,
    SourceAccess,
)


@dataclass(frozen=True)
class PriorWorkRef:
    work_id: str
    title: str
    source_id: str
    mechanism_summary: str
    access_status: SourceAccess
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.work_id.strip() or not self.title.strip() or not self.source_id.strip():
            raise ValueError("prior work requires identity, title and source")
        if not self.mechanism_summary.strip():
            raise ValueError("prior work requires a mechanism summary")
        if not isinstance(self.access_status, SourceAccess):
            object.__setattr__(self, "access_status", SourceAccess(self.access_status))
        if not self.evidence_refs or any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("prior work requires evidence references")


@dataclass(frozen=True)
class MechanismAtom:
    mechanism_id: str
    description: str
    role: str

    def __post_init__(self) -> None:
        if not self.mechanism_id.strip() or not self.description.strip() or not self.role.strip():
            raise ValueError("mechanism atom requires id, description and role")


@dataclass(frozen=True)
class OverlapRecord:
    mechanism_id: str
    prior_work_id: str
    classification: MechanismOverlap
    note: str

    def __post_init__(self) -> None:
        if not self.mechanism_id.strip() or not self.prior_work_id.strip() or not self.note.strip():
            raise ValueError("overlap record requires mechanism, prior work and note")
        if not isinstance(self.classification, MechanismOverlap):
            object.__setattr__(self, "classification", MechanismOverlap(self.classification))


@dataclass(frozen=True)
class HostileAlreadySolvedRoute:
    route_id: str
    assumption: str
    queries: tuple[str, ...]
    findings: tuple[PriorWorkRef, ...]
    executed: bool
    residual_changed: bool
    note: str

    def __post_init__(self) -> None:
        if not self.route_id.strip() or not self.assumption.strip() or not self.note.strip():
            raise ValueError("hostile already-solved route requires identity, assumption and note")
        if not self.queries or any(not query.strip() for query in self.queries):
            raise ValueError("hostile already-solved route requires queries")


@dataclass(frozen=True)
class DiscriminatingExperiment:
    experiment_id: str
    hypothesis: str
    observation_if_novel: str
    observation_if_already_solved: str
    status: str
    result: str = ""

    def __post_init__(self) -> None:
        if not self.experiment_id.strip() or not self.hypothesis.strip():
            raise ValueError("discriminating experiment requires id and hypothesis")
        ExperimentStatus(self.status)
        if not self.observation_if_novel.strip() or not self.observation_if_already_solved.strip():
            raise ValueError("discriminating experiment requires both observation branches")

    @property
    def executed(self) -> bool:
        return self.status == ExperimentStatus.EXECUTED.value and bool(self.result.strip())


@dataclass(frozen=True)
class DatedSearchSnapshot:
    snapshot_date: str
    queries_by_route: tuple[tuple[str, tuple[str, ...]], ...]
    source_ids: tuple[str, ...]
    snapshot_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.snapshot_date.strip():
            raise ValueError("search snapshot requires an ISO date")
        if not self.snapshot_hash:
            digest = sha256_canonical(
                {
                    "snapshot_date": self.snapshot_date,
                    "queries_by_route": self.queries_by_route,
                    "source_ids": self.source_ids,
                }
            )
            object.__setattr__(self, "snapshot_hash", digest)


@dataclass(frozen=True)
class CertificateDraft:
    claim_id: str
    claim_text: str
    problem_task_definition: str
    claimed_mechanism_decomposition: tuple[MechanismAtom, ...]
    closest_prior_by_term: tuple[PriorWorkRef, ...]
    closest_prior_by_function: tuple[PriorWorkRef, ...]
    parent_discipline_mechanisms: tuple[PriorWorkRef, ...]
    benchmark_implementation_routes: tuple[PriorWorkRef, ...]
    hostile_already_solved_route: HostileAlreadySolvedRoute | None
    overlap_classifications: tuple[OverlapRecord, ...]
    absorption_decisions: tuple[AbsorptionDecision, ...]
    original_claim_text: str
    smallest_residual: str
    residual_implementation_evidence: tuple[str, ...]
    discriminating_experiment: DiscriminatingExperiment
    unresolved_sources: tuple[str, ...]
    unresolved_search_routes: tuple[str, ...]
    inaccessible_material_sources: tuple[str, ...]
    saturation: SearchSaturationProtocol
    snapshot_date: str
    llm_novelty_score: float | None = None
    llm_proposed_state: NoveltyFinalState | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.claim_text.strip():
            raise ValueError("certificate draft requires claim identity and text")
        if not self.problem_task_definition.strip():
            raise ValueError("certificate draft requires a problem/task definition")
        if not self.claimed_mechanism_decomposition:
            raise ValueError("certificate draft requires a mechanism decomposition")
        if not self.original_claim_text.strip():
            raise ValueError("certificate draft requires the original claim text")
        if self.llm_proposed_state is not None and not isinstance(self.llm_proposed_state, NoveltyFinalState):
            object.__setattr__(self, "llm_proposed_state", NoveltyFinalState(self.llm_proposed_state))


@dataclass(frozen=True)
class ScientificNoveltyCertificate:
    schema_id: str
    claim_id: str
    claim_text: str
    problem_task_definition: str
    claimed_mechanism_decomposition: tuple[MechanismAtom, ...]
    closest_prior_by_term: tuple[PriorWorkRef, ...]
    closest_prior_by_function: tuple[PriorWorkRef, ...]
    parent_discipline_mechanisms: tuple[PriorWorkRef, ...]
    benchmark_implementation_routes: tuple[PriorWorkRef, ...]
    hostile_already_solved_route: HostileAlreadySolvedRoute | None
    overlap_classifications: tuple[OverlapRecord, ...]
    absorption_decisions: tuple[AbsorptionDecision, ...]
    original_claim_text: str
    smallest_residual: str
    residual_implementation_evidence: tuple[str, ...]
    discriminating_experiment: DiscriminatingExperiment
    unresolved_sources: tuple[str, ...]
    unresolved_search_routes: tuple[str, ...]
    inaccessible_material_sources: tuple[str, ...]
    saturation: SearchSaturationProtocol
    search_snapshot: DatedSearchSnapshot
    final_state: NoveltyFinalState
    authority_reasons: tuple[str, ...]
    llm_novelty_score: float | None
    llm_proposed_state: NoveltyFinalState | None
    confidence: float | None
    content_hash: str
    snapshot_hash: str

    def hash_payload(self) -> dict[str, object]:
        from orion.novelty.hashing import HASH_EXCLUDED_FIELDS, jsonable

        return jsonable(self, exclude=HASH_EXCLUDED_FIELDS)

    def to_payload(self) -> dict[str, object]:
        from orion.novelty.hashing import jsonable

        payload = jsonable(self)
        payload["schema_id"] = self.schema_id
        return payload

    def to_draft(self) -> CertificateDraft:
        return CertificateDraft(
            claim_id=self.claim_id,
            claim_text=self.claim_text,
            problem_task_definition=self.problem_task_definition,
            claimed_mechanism_decomposition=self.claimed_mechanism_decomposition,
            closest_prior_by_term=self.closest_prior_by_term,
            closest_prior_by_function=self.closest_prior_by_function,
            parent_discipline_mechanisms=self.parent_discipline_mechanisms,
            benchmark_implementation_routes=self.benchmark_implementation_routes,
            hostile_already_solved_route=self.hostile_already_solved_route,
            overlap_classifications=self.overlap_classifications,
            absorption_decisions=self.absorption_decisions,
            original_claim_text=self.original_claim_text,
            smallest_residual=self.smallest_residual,
            residual_implementation_evidence=self.residual_implementation_evidence,
            discriminating_experiment=self.discriminating_experiment,
            unresolved_sources=self.unresolved_sources,
            unresolved_search_routes=self.unresolved_search_routes,
            inaccessible_material_sources=self.inaccessible_material_sources,
            saturation=self.saturation,
            snapshot_date=self.search_snapshot.snapshot_date,
            llm_novelty_score=self.llm_novelty_score,
            llm_proposed_state=self.llm_proposed_state,
            confidence=self.confidence,
        )


def _snapshot_from_draft(draft: CertificateDraft) -> DatedSearchSnapshot:
    queries: list[tuple[str, tuple[str, ...]]] = []
    sources: list[str] = []
    for record in draft.saturation.rounds:
        queries.append((record.route.value, record.queries))
        sources.extend(record.finding_ids)
    for group in (
        draft.closest_prior_by_term,
        draft.closest_prior_by_function,
        draft.parent_discipline_mechanisms,
        draft.benchmark_implementation_routes,
    ):
        sources.extend(item.source_id for item in group)
    if draft.hostile_already_solved_route is not None:
        queries.append(
            (NoveltySearchRoute.HOSTILE_ALREADY_SOLVED.value, draft.hostile_already_solved_route.queries)
        )
        sources.extend(item.source_id for item in draft.hostile_already_solved_route.findings)
    return DatedSearchSnapshot(
        snapshot_date=draft.snapshot_date,
        queries_by_route=tuple(queries),
        source_ids=tuple(dict.fromkeys(sources)),
    )


def seal_certificate(draft: CertificateDraft) -> ScientificNoveltyCertificate:
    from orion.novelty.authority import decide_final_state

    snapshot = _snapshot_from_draft(draft)
    final_state, reasons = decide_final_state(draft)
    certificate = ScientificNoveltyCertificate(
        schema_id=SCHEMA_ID,
        claim_id=draft.claim_id,
        claim_text=draft.claim_text,
        problem_task_definition=draft.problem_task_definition,
        claimed_mechanism_decomposition=draft.claimed_mechanism_decomposition,
        closest_prior_by_term=draft.closest_prior_by_term,
        closest_prior_by_function=draft.closest_prior_by_function,
        parent_discipline_mechanisms=draft.parent_discipline_mechanisms,
        benchmark_implementation_routes=draft.benchmark_implementation_routes,
        hostile_already_solved_route=draft.hostile_already_solved_route,
        overlap_classifications=draft.overlap_classifications,
        absorption_decisions=draft.absorption_decisions,
        original_claim_text=draft.original_claim_text,
        smallest_residual=draft.smallest_residual,
        residual_implementation_evidence=draft.residual_implementation_evidence,
        discriminating_experiment=draft.discriminating_experiment,
        unresolved_sources=draft.unresolved_sources,
        unresolved_search_routes=draft.unresolved_search_routes,
        inaccessible_material_sources=draft.inaccessible_material_sources,
        saturation=draft.saturation,
        search_snapshot=snapshot,
        final_state=final_state,
        authority_reasons=reasons,
        llm_novelty_score=draft.llm_novelty_score,
        llm_proposed_state=draft.llm_proposed_state,
        confidence=draft.confidence,
        content_hash="",
        snapshot_hash=snapshot.snapshot_hash,
    )
    digest = sha256_canonical(certificate)
    object.__setattr__(certificate, "content_hash", digest)
    return certificate
