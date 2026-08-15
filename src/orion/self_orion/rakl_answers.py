from __future__ import annotations

import json
from dataclasses import dataclass

from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint
from orion.mechanics.answers import (
    AnswerApplicationReport,
    AnswerRecord,
    AnswerResidual,
    apply_answer_records,
    audit_answer_application,
)
from orion.mechanics.model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.program import observe_mechanics_program
from orion.self_orion.rakl_transfer import (
    MECHANIC_TO_RAKL_SURFACES,
    RAKL_METHOD_SPEC_PATH,
    RAKL_SOURCE_COMMIT,
    RAKL_SURFACE_PROFILES,
)

TRANSFER_ANSWER_DIMENSIONS = (
    MechanicDimension.VERIFICATION,
    MechanicDimension.FAILURE,
    MechanicDimension.OBSERVABILITY,
    MechanicDimension.HANDOFF,
    MechanicDimension.STATE,
    MechanicDimension.TRANSITION_MODEL,
    MechanicDimension.MATHEMATICS,
    MechanicDimension.DEPENDENCIES,
    MechanicDimension.METRICS,
    MechanicDimension.UNCERTAINTY,
    MechanicDimension.INVARIANTS,
    MechanicDimension.PARENT_DISCIPLINE,
    MechanicDimension.SEARCH_COVERAGE,
    MechanicDimension.SATURATION,
)

SURFACE_PARENT_DISCIPLINES: dict[str, tuple[str, ...]] = {
    "decomposition": ("systems engineering", "hierarchical task planning", "operations research", "graph decomposition"),
    "routing": ("adaptive control", "metareasoning", "mixture-of-experts routing", "operations research"),
    "search_query_generation": ("information retrieval", "active learning", "optimal experimental design", "decision theory"),
    "source_selection_reliability": ("information retrieval evaluation", "systematic review methodology", "source criticism", "data provenance"),
    "claim_extraction": ("computational linguistics", "scientific information extraction", "semantic parsing", "discourse/pragmatics"),
    "ontology_terminology_normalization": ("knowledge representation", "ontology alignment", "entity resolution", "data integration"),
    "mathematical_context_translation": ("measurement science", "dimensional analysis", "representation theory", "metrology"),
    "equivalence_similarity": ("mathematical equivalence", "representation learning", "measurement invariance", "model comparison"),
    "contextual_theory_gluing": ("sheaf/category-inspired gluing", "data integration", "constraint satisfaction", "knowledge representation"),
    "contradiction_diagnosis": ("argumentation theory", "truth maintenance", "belief revision", "causal diagnosis"),
    "gap_discovery": ("metascience", "systematic review", "active learning", "scientific discovery"),
    "experiment_query_selection": ("optimal experimental design", "active learning", "Bayesian decision theory", "causal experimentation"),
    "synthesis": ("evidence synthesis", "model integration", "scientific explanation", "knowledge representation"),
    "memory": ("information retrieval", "database systems", "case-based reasoning", "cognitive memory"),
    "review": ("software verification", "peer review/metascience", "red teaming", "formal methods"),
    "benchmarking": ("psychometrics", "measurement science", "software testing", "experimental design"),
    "authority_promotion": ("assurance cases", "formal verification", "epistemology", "safety governance"),
    "saturation_stopping": ("systematic review stopping", "information foraging", "sequential analysis", "optimal stopping"),
    "prompting_context_policy": ("information retrieval", "context compression", "working-memory models", "knapsack/resource allocation"),
    "capability_shaping": ("adaptive expertise", "program synthesis", "meta-learning", "software experimentation"),
    "software_architecture_execution": ("software architecture", "distributed systems", "reproducible computing", "fault tolerance"),
    "research_portfolio_tree": ("portfolio optimization", "multi-armed bandits", "exploration-exploitation", "project portfolio management"),
    "objective_evolution": ("multi-objective optimization", "Goodhart-aware control", "requirements engineering", "value learning"),
    "generator_transport": ("analogy/transfer learning", "program transformation", "representation mapping", "domain adaptation"),
}


@dataclass(frozen=True)
class RaklAnswerTransferReport:
    answer_records: tuple[AnswerRecord, ...]
    evidence_records: tuple[EvidenceRecord, ...]
    application: AnswerApplicationReport
    audit_residuals: tuple[AnswerResidual, ...]
    open_questions_before: int
    open_questions_after: int

    @property
    def closed_questions(self) -> int:
        return self.open_questions_before - self.open_questions_after

    @property
    def attributable(self) -> bool:
        return not self.application.residuals and not self.audit_residuals


def _slug(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace(":", "_").replace(".", "_")


def _surface_values(surfaces: tuple[str, ...], attribute: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for surface in surfaces for value in getattr(RAKL_SURFACE_PROFILES[surface], attribute)))


def _evidence_record(cell: MechanicCell, surfaces: tuple[str, ...]) -> EvidenceRecord:
    if surfaces:
        content = json.dumps(
            {
                "transfer_kind": "RAKL_METHOD_CONTRACT_PROFILE",
                "rakl_commit": RAKL_SOURCE_COMMIT,
                "rakl_path": RAKL_METHOD_SPEC_PATH,
                "mechanic_id": cell.mechanic_id,
                "surfaces": [
                    {
                        "surface": surface,
                        "observables": list(RAKL_SURFACE_PROFILES[surface].observables),
                        "state": list(RAKL_SURFACE_PROFILES[surface].state),
                        "transition": list(RAKL_SURFACE_PROFILES[surface].transition),
                        "mathematics": list(RAKL_SURFACE_PROFILES[surface].mathematics),
                        "failures": list(RAKL_SURFACE_PROFILES[surface].failures),
                        "verification_refs": list(RAKL_SURFACE_PROFILES[surface].verification_refs),
                        "external_dependencies": list(RAKL_SURFACE_PROFILES[surface].external_dependencies),
                    }
                    for surface in surfaces
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return EvidenceRecord(
            evidence_id=f"rakl-transfer-evidence:{cell.mechanic_id}",
            content=content,
            source_uri=f"github://SzeChunYiu/RAKL/{RAKL_SOURCE_COMMIT}/{RAKL_METHOD_SPEC_PATH}",
            domain_ids=("rakl-provenance", "orion-method-design"),
            certificate_ids=("design-provenance-only",),
        )
    content = json.dumps(
        {
            "transfer_kind": "ORION_COMPOSITION_DERIVATION",
            "mechanic_id": cell.mechanic_id,
            "purpose": cell.purpose,
            "scope": cell.scope,
            "children": list(cell.child_mechanic_ids),
            "dependencies": list(cell.dependency_ids),
            "external_dependencies": list(cell.external_dependency_contract_ids),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return EvidenceRecord(
        evidence_id=f"orion-composition-evidence:{cell.mechanic_id}",
        content=content,
        source_uri=f"orion://mechanics/{cell.mechanic_id}/composition",
        domain_ids=("orion", "mechanic-composition"),
        certificate_ids=("composition-derivation-only",),
    )


def build_rakl_evidence_index(cells: tuple[MechanicCell, ...]) -> dict[str, EvidenceRecord]:
    records: dict[str, EvidenceRecord] = {}
    for cell in cells:
        surfaces = MECHANIC_TO_RAKL_SURFACES.get(cell.mechanic_id, ())
        if not surfaces and not (cell.child_mechanic_ids or cell.mechanic_id.endswith(".v1") or cell.mechanic_id.startswith("SATURATE_BOUNDED")):
            continue
        record = _evidence_record(cell, surfaces)
        records[record.evidence_id] = record
    return records


def _binding(record: EvidenceRecord) -> tuple[tuple[str, str], ...]:
    return ((record.evidence_id, evidence_record_fingerprint(record)),)


def _answer(
    *,
    record_id: str,
    cell: MechanicCell,
    dimension: MechanicDimension,
    lane: str,
    evidence: EvidenceRecord,
    payload: tuple[tuple[str, tuple[str, ...]], ...] = (),
    handoff_payload: tuple[HandoffField, ...] = (),
    metric_payload: tuple[MetricSpec, ...] = (),
) -> AnswerRecord:
    return AnswerRecord(
        record_id=record_id,
        mechanic_id=cell.mechanic_id,
        dimension=dimension,
        lane=lane,
        evidence_refs=(evidence.evidence_id,),
        evidence_bindings=_binding(evidence),
        payload=payload,
        handoff_payload=handoff_payload,
        metric_payload=metric_payload,
    )


def _metric_payload(mechanic_id: str, surfaces: tuple[str, ...], observables: tuple[str, ...]) -> tuple[MetricSpec, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    metrics = [
        MetricSpec(
            metric_id=f"metric:{mechanic_id}:rakl:{_slug(name)}",
            description=f"Step-specific {label} diagnostic observable: {name}.",
            kind=MetricKind.DIAGNOSTIC,
            direction=MetricDirection.OBSERVE_ONLY,
            unit="typed",
            required_for_handoff=True,
            uncertainty_semantics="retain measurement/model/search uncertainty; do not fabricate point confidence",
        )
        for name in (observables[:4] or ("typed_output",))
    ]
    metrics.extend(
        (
            MetricSpec(
                metric_id=f"metric:{mechanic_id}:rakl:root_relevant_effect",
                description=f"Root-relevant effect attributable to the {label} mechanic under a typed transport witness.",
                kind=MetricKind.QUALITY,
                direction=MetricDirection.OBSERVE_ONLY,
                unit="typed_delta",
                required_for_handoff=True,
                uncertainty_semantics="unidentified root effects remain set-valued/local-only",
            ),
            MetricSpec(
                metric_id=f"metric:{mechanic_id}:rakl:blocking_failure",
                description=f"Whether a step-specific {label} failure/falsifier or protected invariant is active.",
                kind=MetricKind.SAFETY,
                direction=MetricDirection.NON_COMPENSATORY_GATE,
                unit="bool",
                required_for_handoff=True,
                threshold_semantics="must be false",
                uncertainty_semantics="unknown blocking status yields CANNOT_CHECK rather than pass",
            ),
        )
    )
    return tuple(metrics)


def _uncertainty(mechanic_id: str, surfaces: tuple[str, ...]) -> tuple[str, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    return (
        f"{mechanic_id}:{label}:use probability only when calibrated data/model assumptions license it; otherwise retain intervals, sets, alternatives, bounds, UNKNOWN or CANNOT_CHECK",
        f"{mechanic_id}:{label}:search coverage remains open until heterogeneous independent route challenges are recorded",
        f"{mechanic_id}:{label}:responsibility remains alternative hypotheses until a discriminator separates causes",
        f"{mechanic_id}:{label}:resource censoring yields CANNOT_CHECK and never closure",
    )


def _invariants(mechanic_id: str, surfaces: tuple[str, ...], failures: tuple[str, ...]) -> tuple[str, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    return tuple(
        dict.fromkeys(
            (
                f"invariant:{mechanic_id}:{label}:generation_and_retrieval_do_not_mint_scientific_authority",
                f"invariant:{mechanic_id}:{label}:negative_null_refuted_history_remains_addressable",
                f"invariant:{mechanic_id}:{label}:missing_mandatory_evidence_fails_closed",
                f"invariant:{mechanic_id}:{label}:new_material_residual_reopens_dependent_closure",
                f"invariant:{mechanic_id}:{label}:resource_exhaustion_is_not_saturation",
                f"invariant:{mechanic_id}:{label}:local_proxy_improvement_requires_root_transport_witness",
                *tuple(f"invariant:{mechanic_id}:detect_or_preserve:{_slug(item)}" for item in failures[:4]),
            )
        )
    )


def _parent_domains(surfaces: tuple[str, ...], *, composition: bool = False) -> tuple[str, ...]:
    values = tuple(dict.fromkeys(domain for surface in surfaces for domain in SURFACE_PARENT_DISCIPLINES.get(surface, ())))
    if values:
        return values
    return ("systems engineering", "workflow orchestration", "formal methods", "control theory") if composition else ("systems engineering", "scientific method", "information science")


def _search_coverage(mechanic_id: str, surfaces: tuple[str, ...]) -> tuple[str, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    routes = [
        f"{mechanic_id}:{label}:current_vocabulary_and_exact_identifier_route",
        f"{mechanic_id}:{label}:lexically_independent_function_only_route",
        f"{mechanic_id}:{label}:parent_discipline_route",
        f"{mechanic_id}:{label}:literature_bridge_route",
        f"{mechanic_id}:{label}:adversarial_omission_route",
        f"{mechanic_id}:{label}:historical_precursor_or_distant_analogue_route",
        f"{mechanic_id}:{label}:freshness_route",
    ]
    if any(surface in {"mathematical_context_translation", "equivalence_similarity", "contextual_theory_gluing", "generator_transport", "saturation_stopping"} for surface in surfaces):
        routes.append(f"{mechanic_id}:{label}:mathematical_equivalent_route")
    if any(surface in {"software_architecture_execution", "capability_shaping", "memory", "benchmarking"} for surface in surfaces):
        routes.append(f"{mechanic_id}:{label}:implementation_analogue_route")
    return tuple(routes)


def _saturation(mechanic_id: str, surfaces: tuple[str, ...]) -> tuple[str, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    return (
        f"{mechanic_id}:{label}:freeze scope search basis metrics and failure coordinates before flatness credit",
        f"{mechanic_id}:{label}:require at least two independent heterogeneous route families with zero retained decision-relevant novelty",
        f"{mechanic_id}:{label}:require no new material contradiction discriminator data requirement failure pattern or native residual",
        f"{mechanic_id}:{label}:require parent-discipline and adversarial-omission challenges",
        f"{mechanic_id}:{label}:new representation parent-domain operator or failure class invalidates inherited flatness",
        f"{mechanic_id}:{label}:resource exhaustion while obligations remain yields CANNOT_CHECK not closure",
        f"{mechanic_id}:{label}:bounded flatness is scoped and never asserts universal completeness",
    )


def _handoff(cell: MechanicCell, surfaces: tuple[str, ...], observables: tuple[str, ...]) -> tuple[HandoffField, ...]:
    label = "+".join(surfaces) if surfaces else "composition"
    fields = [
        HandoffField(
            field_id=f"{cell.mechanic_id}:rakl:{_slug(name)}",
            description=f"Step-specific {label} handoff observable: {name}.",
            schema_ref=f"orion://mechanic/{cell.mechanic_id}/handoff/{_slug(name)}",
            required=True,
        )
        for name in observables[:4]
    ]
    fields.extend(
        (
            HandoffField(f"{cell.mechanic_id}:rakl:evidence_bindings", "Exact evidence/content bindings used by this step.", "orion://schema/evidence-bindings", True),
            HandoffField(f"{cell.mechanic_id}:rakl:uncertainty", "Typed uncertainty/identified-set/CANNOT_CHECK state.", "orion://schema/uncertainty", True),
            HandoffField(f"{cell.mechanic_id}:rakl:provenance", "Source/transformation/execution provenance required downstream.", "orion://schema/provenance", True),
        )
    )
    return tuple(fields)


def _leaf_records(cell: MechanicCell, surfaces: tuple[str, ...], evidence: EvidenceRecord) -> tuple[AnswerRecord, ...]:
    observables = _surface_values(surfaces, "observables")
    state = _surface_values(surfaces, "state")
    transition = _surface_values(surfaces, "transition")
    mathematics = _surface_values(surfaces, "mathematics")
    failures = _surface_values(surfaces, "failures")
    verification_refs = _surface_values(surfaces, "verification_refs")
    dependencies = tuple(f"external:{cell.mechanic_id}:{_slug(item)}" for item in _surface_values(surfaces, "external_dependencies")) or ("external:ORION_RUNTIME",)
    lane = "rakl-transfer-v1"
    return (
        _answer(record_id=f"rakl:{cell.mechanic_id}:verification", cell=cell, dimension=MechanicDimension.VERIFICATION, lane=lane, evidence=evidence, payload=(("verification_contracts", tuple(f"rakl-conformance:{path}" for path in verification_refs) + (f"orion:{cell.mechanic_id}:known-answer", f"orion:{cell.mechanic_id}:hostile-failure", f"orion:{cell.mechanic_id}:fresh-transfer")),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:failure", cell=cell, dimension=MechanicDimension.FAILURE, lane=lane, evidence=evidence, payload=(("failure_signatures", tuple(f"{cell.mechanic_id}:{item}" for item in failures)), ("falsifiers", tuple(f"{cell.mechanic_id}:falsifier:{_slug(item)}" for item in failures)))),
        _answer(record_id=f"rakl:{cell.mechanic_id}:observability", cell=cell, dimension=MechanicDimension.OBSERVABILITY, lane=lane, evidence=evidence, payload=(("observable_ids", observables),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:handoff", cell=cell, dimension=MechanicDimension.HANDOFF, lane=lane, evidence=evidence, handoff_payload=_handoff(cell, surfaces, observables)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:state", cell=cell, dimension=MechanicDimension.STATE, lane=lane, evidence=evidence, payload=(("state_ids", state),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:transition", cell=cell, dimension=MechanicDimension.TRANSITION_MODEL, lane=lane, evidence=evidence, payload=(("transition_semantics", transition),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:mathematics", cell=cell, dimension=MechanicDimension.MATHEMATICS, lane=lane, evidence=evidence, payload=(("mathematical_semantics", mathematics),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:dependencies", cell=cell, dimension=MechanicDimension.DEPENDENCIES, lane=lane, evidence=evidence, payload=(("external_dependency_contract_ids", dependencies),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:metrics", cell=cell, dimension=MechanicDimension.METRICS, lane=lane, evidence=evidence, metric_payload=_metric_payload(cell.mechanic_id, surfaces, observables)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:uncertainty", cell=cell, dimension=MechanicDimension.UNCERTAINTY, lane=lane, evidence=evidence, payload=(("uncertainty_semantics", _uncertainty(cell.mechanic_id, surfaces)),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:invariants", cell=cell, dimension=MechanicDimension.INVARIANTS, lane=lane, evidence=evidence, payload=(("constraint_ids", _invariants(cell.mechanic_id, surfaces, failures)),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:parent-domains", cell=cell, dimension=MechanicDimension.PARENT_DISCIPLINE, lane=lane, evidence=evidence, payload=(("parent_domain_hypotheses", _parent_domains(surfaces)),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:search-coverage", cell=cell, dimension=MechanicDimension.SEARCH_COVERAGE, lane=lane, evidence=evidence, payload=(("search_coverage_obligations", _search_coverage(cell.mechanic_id, surfaces)),)),
        _answer(record_id=f"rakl:{cell.mechanic_id}:saturation", cell=cell, dimension=MechanicDimension.SATURATION, lane=lane, evidence=evidence, payload=(("saturation_criteria", _saturation(cell.mechanic_id, surfaces)),)),
    )


def _composition_records(cell: MechanicCell, evidence: EvidenceRecord) -> tuple[AnswerRecord, ...]:
    surfaces: tuple[str, ...] = ()
    observables = ("child_status_vector", "state_epoch", "material_residual_count", "authority_delta", "resource_spend", "cannot_check_count")
    state = ("K_t", "W_t", "M_t", "epoch", "child_receipt_ledger", f"active:{cell.mechanic_id}")
    transition = (
        f"{cell.mechanic_id}:compose child transition relations in declared dependency order under blocking invariants",
        f"{cell.mechanic_id}:preserve BLOCKED/CANNOT_CHECK/failure child states in the parent receipt",
        f"{cell.mechanic_id}:material child residuals update K/W/M only through declared transitions and scoped reopening",
    )
    mathematics = (
        f"{cell.mechanic_id}:T_parent is relational composition of child transition relations over the dependency partial order",
        f"{cell.mechanic_id}:set-valued child transitions remain set-valued after composition",
    )
    failures = ("child_failure_suppressed", "handoff_contract_violation", "invalid_transition_order", "state_or_authority_escalation", "resource_bound")
    dependencies = tuple(f"mechanic:{child}" for child in cell.child_mechanic_ids) if cell.child_mechanic_ids else ("external:ORION_RUNTIME",)
    lane = "orion-composition-v1"
    return (
        _answer(record_id=f"composition:{cell.mechanic_id}:verification", cell=cell, dimension=MechanicDimension.VERIFICATION, lane=lane, evidence=evidence, payload=(("verification_contracts", (f"orion:{cell.mechanic_id}:all-child-contracts-explicit", f"orion:{cell.mechanic_id}:dependency-handoff-conformance", f"orion:{cell.mechanic_id}:end-to-end-known-answer", f"orion:{cell.mechanic_id}:hostile-child-failure-propagation")),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:failure", cell=cell, dimension=MechanicDimension.FAILURE, lane=lane, evidence=evidence, payload=(("failure_signatures", tuple(f"{cell.mechanic_id}:{item}" for item in failures)), ("falsifiers", tuple(f"{cell.mechanic_id}:falsifier:{item}" for item in failures)))),
        _answer(record_id=f"composition:{cell.mechanic_id}:observability", cell=cell, dimension=MechanicDimension.OBSERVABILITY, lane=lane, evidence=evidence, payload=(("observable_ids", observables),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:handoff", cell=cell, dimension=MechanicDimension.HANDOFF, lane=lane, evidence=evidence, handoff_payload=_handoff(cell, surfaces, observables)),
        _answer(record_id=f"composition:{cell.mechanic_id}:state", cell=cell, dimension=MechanicDimension.STATE, lane=lane, evidence=evidence, payload=(("state_ids", state),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:transition", cell=cell, dimension=MechanicDimension.TRANSITION_MODEL, lane=lane, evidence=evidence, payload=(("transition_semantics", transition),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:mathematics", cell=cell, dimension=MechanicDimension.MATHEMATICS, lane=lane, evidence=evidence, payload=(("mathematical_semantics", mathematics),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:dependencies", cell=cell, dimension=MechanicDimension.DEPENDENCIES, lane=lane, evidence=evidence, payload=(("external_dependency_contract_ids", dependencies),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:metrics", cell=cell, dimension=MechanicDimension.METRICS, lane=lane, evidence=evidence, metric_payload=_metric_payload(cell.mechanic_id, surfaces, observables)),
        _answer(record_id=f"composition:{cell.mechanic_id}:uncertainty", cell=cell, dimension=MechanicDimension.UNCERTAINTY, lane=lane, evidence=evidence, payload=(("uncertainty_semantics", _uncertainty(cell.mechanic_id, surfaces)),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:invariants", cell=cell, dimension=MechanicDimension.INVARIANTS, lane=lane, evidence=evidence, payload=(("constraint_ids", _invariants(cell.mechanic_id, surfaces, failures)),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:parent-domains", cell=cell, dimension=MechanicDimension.PARENT_DISCIPLINE, lane=lane, evidence=evidence, payload=(("parent_domain_hypotheses", _parent_domains(surfaces, composition=True)),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:search-coverage", cell=cell, dimension=MechanicDimension.SEARCH_COVERAGE, lane=lane, evidence=evidence, payload=(("search_coverage_obligations", _search_coverage(cell.mechanic_id, surfaces)),)),
        _answer(record_id=f"composition:{cell.mechanic_id}:saturation", cell=cell, dimension=MechanicDimension.SATURATION, lane=lane, evidence=evidence, payload=(("saturation_criteria", _saturation(cell.mechanic_id, surfaces)),)),
    )


def build_rakl_answer_records(cells: tuple[MechanicCell, ...], *, evidence_records: dict[str, EvidenceRecord] | None = None) -> tuple[AnswerRecord, ...]:
    evidence_index = evidence_records or build_rakl_evidence_index(cells)
    records: list[AnswerRecord] = []
    for cell in cells:
        surfaces = MECHANIC_TO_RAKL_SURFACES.get(cell.mechanic_id)
        evidence_id = f"rakl-transfer-evidence:{cell.mechanic_id}" if surfaces else f"orion-composition-evidence:{cell.mechanic_id}"
        evidence = evidence_index.get(evidence_id)
        if evidence is None:
            continue
        if surfaces:
            records.extend(_leaf_records(cell, surfaces, evidence))
        else:
            records.extend(_composition_records(cell, evidence))
    return tuple(records)


def apply_rakl_answer_transfer(cells: tuple[MechanicCell, ...]) -> tuple[tuple[MechanicCell, ...], RaklAnswerTransferReport]:
    before = observe_mechanics_program(cells)
    evidence_index = build_rakl_evidence_index(cells)
    records = build_rakl_answer_records(cells, evidence_records=evidence_index)
    updated, application = apply_answer_records(cells, records, evidence_records=evidence_index)
    after = observe_mechanics_program(updated)
    audit_residuals = audit_answer_application(before.open_question_count, after.open_question_count, application)
    return updated, RaklAnswerTransferReport(
        answer_records=records,
        evidence_records=tuple(evidence_index.values()),
        application=application,
        audit_residuals=audit_residuals,
        open_questions_before=before.open_question_count,
        open_questions_after=after.open_question_count,
    )


__all__ = [
    "RaklAnswerTransferReport",
    "SURFACE_PARENT_DISCIPLINES",
    "TRANSFER_ANSWER_DIMENSIONS",
    "apply_rakl_answer_transfer",
    "build_rakl_answer_records",
    "build_rakl_evidence_index",
]
