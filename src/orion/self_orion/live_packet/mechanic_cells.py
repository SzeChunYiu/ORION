"""Section 4a -- the fixed mechanic cells behind the question surface.

The eight dimensions issue #8 names are exposed by this fixed audit grammar
rather than by asking a model what it forgot.
"""

from __future__ import annotations

from orion.mechanics.model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)


#: The eight dimensions issue #8 names. They are exposed by the fixed audit
#: grammar in `orion.mechanics.questioning`, so completeness is a property of
#: the grammar rather than of a model's willingness to volunteer a gap.
ISSUE_8_DIMENSIONS: tuple[MechanicDimension, ...] = (
    MechanicDimension.OBSERVABILITY,
    MechanicDimension.MATHEMATICS,
    MechanicDimension.HANDOFF,
    MechanicDimension.FAILURE,
    MechanicDimension.STORAGE,
    MechanicDimension.VERIFICATION,
    MechanicDimension.PARENT_DISCIPLINE,
    MechanicDimension.SATURATION,
)

#: Which provider role each fibre needs. A fibre with no role runs today; the
#: rest are blocked exactly when their role's variables are absent, which is why
#: the trial is partially rather than wholly credential-blocked.
FIBRE_PROVIDER_ROLES: dict[str, str] = {
    "p5.live.search": "retrieval",
    "p5.live.interpretation": "reasoner",
    "p5.live.absorption": "reasoner",
    "p5.live.reconstruction": "reasoner",
    "p5.live.residual_detection": "",
    "p5.live.diagnosis": "reasoner",
    "p5.live.saturation": "",
    "p5.live.verification": "protected_verification",
}

_SHARED_AUTHORITY = (
    "may emit evidence, residuals and proposals",
    "may never raise its own lesson authority",
    "may never merge, promote or modify the evaluator",
)
_SHARED_RESOURCES = (
    "resource:model_calls",
    "resource:retrieval_calls",
    "resource:model_tokens",
    "resource:wallclock_seconds",
)
_SHARED_ENGINEERING = (
    "every execution emits a receipt, including refusals",
    "no exclusion path: failed and empty executions are retained verbatim",
)
_SHARED_PROVENANCE = (
    "evidence is identified by content digest, never by retrieval id",
    "the frozen packet fingerprint is recorded on every artifact",
)
_SHARED_REOPEN = (
    "a provider identity, limit or evaluator change voids the freeze",
    "a corpus revision change voids every deep-target result",
)


def _fibre(
    mechanic_id: str,
    purpose: str,
    scope: str,
    **fields: object,
) -> MechanicCell:
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose=purpose,
        scope=scope,
        authority_boundaries=_SHARED_AUTHORITY,
        resource_coordinates=_SHARED_RESOURCES,
        engineering_contracts=_SHARED_ENGINEERING,
        provenance_contracts=_SHARED_PROVENANCE,
        reopen_triggers=_SHARED_REOPEN,
        **fields,  # type: ignore[arg-type]
    )


def live_trial_mechanic_cells() -> tuple[MechanicCell, ...]:
    """The eight fibres issue #8's development protocol asks for, as fixed cells.

    Each cell states what the packet genuinely determines and leaves open what
    only execution can settle. Two mechanisms produce an open question, and both
    are honest: an unfilled field, and a field that is filled but listed in
    `provisional_dimensions` because the contract is stated while its adequacy is
    unestablished. Nothing is blanked to manufacture a question -- if a cell were
    padded to force a dimension open, the surface would be measuring the padding.
    """

    return (
        _fibre(
            "p5.live.search",
            "Issue route-family queries against live retrieval backends and retain every raw query and result.",
            "One frozen task at a time; retrieval only, no interpretation.",
            input_ids=("frozen_task", "route_binding_set"),
            output_ids=("raw_query_trace", "route_captures"),
            handoff_fields=(
                HandoffField(
                    "raw_query_trace",
                    "Every query issued and every item returned, including empties and errors.",
                    "orion.self_orion.live_packet.RawTrialTrace",
                ),
            ),
            state_ids=("issued_query_count", "retained_item_digests"),
            observable_ids=(
                "queries_issued",
                "items_per_route",
                "zero_result_queries",
                "route_errors",
                "distinct_backends",
            ),
            action_ids=("action:issue_query", "action:record_capture"),
            transition_semantics=(
                "stochastic: a live backend may return different results for the same query",
            ),
            mathematical_semantics=(
                "route overlap as capture occasions; Lincoln-Petersen on independent pairs only",
            ),
            objective_ids=("objective:breadth_before_depth",),
            metrics=(
                MetricSpec(
                    metric_id="distinct_route_families",
                    description="Route families that returned at least one item.",
                    kind=MetricKind.COVERAGE,
                    direction=MetricDirection.NON_COMPENSATORY_GATE,
                    unit="families",
                    required_for_handoff=True,
                    threshold_semantics="at least four; breadth cannot be bought with depth",
                ),
            ),
            uncertainty_semantics=(
                "an unavailable route is a coverage gap, never an absence of results",
            ),
            failure_signatures=("route_unavailable", "zero_results", "backend_error"),
            falsifiers=(
                "a later route with a distinct backend returns items this ensemble missed",
            ),
            diagnosis_rules=("separate backend error from genuine empty result",),
            storage_contracts=("the raw trace is persisted verbatim before any use",),
            verification_contracts=(
                "cited ids are checked against the raw trace by the frozen evaluator",
            ),
            dependency_ids=(),
            external_dependency_contract_ids=("provider:retrieval",),
            search_coverage_obligations=(
                "current vocabulary, function-only, parent-discipline and adversarial-omission routes",
            ),
            parent_domain_hypotheses=(
                "information retrieval: recall-oriented query expansion",
                "systematic review screening: source-family coverage",
                "capture-recapture: unseen-mass estimation from occasion overlap",
            ),
            # Stated but unestablished: whether these backends are independent
            # occasions at all is exactly what the live run would measure.
            provisional_dimensions=(
                MechanicDimension.VERIFICATION,
                MechanicDimension.SATURATION,
            ),
            saturation_criteria=(
                "flat when an added route family yields no new content digest",
            ),
        ),
        _fibre(
            "p5.live.interpretation",
            "Turn retrieved documents into typed claims without inventing evidence identifiers.",
            "Per retrieved document; no binding to the knowledge state.",
            input_ids=("retrieved_item", "open_question"),
            output_ids=("typed_claim", "unknown_id_report"),
            handoff_fields=(
                HandoffField(
                    "typed_claims",
                    "Claims with the exact item id each rests on.",
                    "orion.core.solution.Solution.evidence_ids",
                ),
            ),
            state_ids=("claims_extracted",),
            observable_ids=("citation_grounding_rate", "unknown_id_rate", "parse_errors"),
            action_ids=("action:extract_claim", "action:reject_ungrounded_claim"),
            transition_semantics=("stochastic: model output varies across identical prompts",),
            objective_ids=("objective:no_ungrounded_claim",),
            uncertainty_semantics=("an unparseable response is CANNOT_CHECK, never zero claims",),
            failure_signatures=("ungrounded_citation", "unparseable_response"),
            falsifiers=("a claimed item id is absent from the raw trace",),
            diagnosis_rules=("separate transport failure from refusal from malformed output",),
            verification_contracts=("every cited id must appear verbatim in the raw trace",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("re-read a document per question, not per corpus",),
            parent_domain_hypotheses=(
                "information extraction and argumentation mining",
                "citation verification in evidence synthesis",
            ),
            saturation_criteria=("flat when re-reading a document yields no new claim id",),
            # MATHEMATICS and STORAGE stay empty: no formalism for extraction
            # fidelity is committed here, and what must persist from an
            # interpretation pass is genuinely unsettled before a run.
        ),
        _fibre(
            "p5.live.absorption",
            "Bind interpreted claims into the knowledge state under content digests.",
            "Per claim; idempotent under repeated absorption of the same content.",
            input_ids=("typed_claim", "knowledge_state"),
            output_ids=("bound_evidence_id", "absorption_receipt"),
            handoff_fields=(
                HandoffField(
                    "absorbed_evidence_ids",
                    "Evidence ids now bound into the knowledge state.",
                    "orion.experience.model.TaskEpisode.evidence_bindings",
                ),
            ),
            state_ids=("knowledge_state_hash",),
            observable_ids=("absorbed_count", "duplicate_rate", "digest_drift_events"),
            action_ids=("action:bind_evidence",),
            transition_semantics=("deterministic given content: same digest, same binding",),
            invariant_ids=("invariant:every_evidence_id_is_content_bound",),
            objective_ids=("objective:no_unbound_evidence",),
            uncertainty_semantics=("a digest that changed between capture and binding is a hard error",),
            storage_contracts=("bindings are append-only and content-addressed",),
            verification_contracts=("binding digests are recomputed on replay, never trusted",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("absorption never adds sources the trace does not contain",),
            parent_domain_hypotheses=("knowledge-base construction and entity resolution",),
            # Signatures without falsifiers: we know how absorption breaks, and
            # we do not yet know what observation would show it worked.
            failure_signatures=("duplicate_absorption", "digest_drift"),
            provisional_dimensions=(MechanicDimension.SATURATION,),
            saturation_criteria=("flat when no new content digest binds in a round",),
        ),
        _fibre(
            "p5.live.reconstruction",
            "Assemble an answer to the frozen task from absorbed evidence only.",
            "Per task; no new retrieval, no unbound assertion.",
            input_ids=("frozen_task", "absorbed_evidence"),
            output_ids=("answer_text", "cited_evidence_ids"),
            handoff_fields=(
                HandoffField(
                    "answer",
                    "Answer text plus the exact evidence ids it rests on.",
                    "orion.core.solution.Solution",
                ),
            ),
            state_ids=("answer_draft_hash",),
            observable_ids=("cited_count", "uncited_assertion_count", "answer_length"),
            action_ids=("action:compose_answer",),
            transition_semantics=("stochastic: composition varies across identical inputs",),
            objective_ids=("objective:answer_entirely_from_bound_evidence",),
            uncertainty_semantics=("an unsupported span is a residual, not a hedge",),
            failure_signatures=("assertion_without_evidence", "target_not_named"),
            falsifiers=("the protected gold tokens are absent from the answer",),
            diagnosis_rules=("separate a missing retrieval from a present-but-unused document",),
            storage_contracts=("answer text and cited ids are stored together, immutably",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("reconstruction may not silently widen the evidence base",),
            saturation_criteria=("flat when recomposition changes no cited id",),
            # PARENT_DISCIPLINE left empty: which mature discipline owns
            # "reconstruct a claim from retrieved evidence" is contested across
            # evidence synthesis, argumentation and KB construction, and naming
            # one here would be a guess dressed as a hypothesis.
            provisional_dimensions=(MechanicDimension.VERIFICATION,),
            verification_contracts=("the frozen evaluator checks tokens and anchors, not self-reports",),
        ),
        _fibre(
            "p5.live.residual_detection",
            "Name what the answer does not cover, so silence cannot pass as coverage.",
            "Per answer; produces residuals, never repairs them.",
            input_ids=("answer_text", "frozen_task"),
            output_ids=("residual_ids",),
            handoff_fields=(
                HandoffField(
                    "residual_ids",
                    "Named gaps between the task and the answer.",
                    "orion.core.solution.Solution.residual_ids",
                ),
            ),
            state_ids=("declared_residuals",),
            action_ids=("action:declare_residual",),
            transition_semantics=("deterministic given the answer and the task criteria",),
            mathematical_semantics=("set difference between task criteria and satisfied criteria",),
            objective_ids=("objective:no_silent_gap",),
            uncertainty_semantics=("an undetectable gap is CANNOT_CHECK, not an empty residual set",),
            storage_contracts=("residuals are stored on the episode, not recomputed later",),
            verification_contracts=("a non-recovering answer with no residual fails criterion D4",),
            parent_domain_hypotheses=("gap analysis in systematic reviews",),
            saturation_criteria=("flat when a round declares no new residual kind",),
            # OBSERVABILITY empty and FAILURE without falsifiers: what signal
            # distinguishes a declared residual from an undetected one is the
            # open question this fibre exists to expose.
            failure_signatures=("undetected_gap", "residual_without_evidence"),
        ),
        _fibre(
            "p5.live.diagnosis",
            "Separate retrieved-but-unused from present-but-missed and from absent-from-corpus.",
            "Per task, over the raw trace and, where bound, the ground truth.",
            input_ids=("raw_query_trace", "cited_evidence_ids", "ground_truth_or_none"),
            output_ids=("evidence_use_report",),
            handoff_fields=(
                HandoffField(
                    "evidence_use_report",
                    "Every trace item classified, with CANNOT_CHECK where ground truth is unbound.",
                    "orion.self_orion.live_packet.EvidenceUseReport",
                ),
            ),
            state_ids=("classified_item_count",),
            observable_ids=("used", "retrieved_but_unused", "present_but_missed", "cannot_check"),
            action_ids=("action:classify_evidence_use",),
            transition_semantics=("deterministic given trace, citations and ground truth",),
            mathematical_semantics=("set algebra over trace ids, cited ids and corpus ids",),
            objective_ids=("objective:attribute_failure_to_one_stage",),
            uncertainty_semantics=(
                "unbound ground truth yields CANNOT_CHECK for present-but-missed, never zero",
            ),
            storage_contracts=("the report is stored on an immutable episode",),
            verification_contracts=("classification totality is checked: every trace id appears once",),
            parent_domain_hypotheses=(
                "fault localization: separating a missing signal from an ignored one",
                "recall-oriented IR error analysis",
            ),
            # FAILURE without falsifiers and SATURATION empty: with the wide
            # task's ground truth UNBOUND, what would falsify a diagnosis is
            # unestablished, and so is what a saturated diagnosis would mean.
            failure_signatures=("misattributed_stage", "ground_truth_unbound"),
        ),
        _fibre(
            "p5.live.saturation",
            "Decide whether repeated route challenges are flat under a declared basis.",
            "Per task; a budget decision, never a recall claim.",
            input_ids=("growth_vectors", "saturation_basis"),
            output_ids=("bounded_saturation_state",),
            handoff_fields=(
                HandoffField(
                    "bounded_saturation_state",
                    "OPEN, CANNOT_CHECK or a bounded flat verdict, with reasons.",
                    "orion.self_orion.live_packet.BoundedSaturationState",
                ),
            ),
            state_ids=("flat_streak", "basis_fingerprint"),
            observable_ids=("flat_rounds", "independent_flat_rounds", "growth_magnitude"),
            action_ids=("action:assess_saturation",),
            transition_semantics=("deterministic given the growth vectors and the basis",),
            mathematical_semantics=(
                "non-compensatory growth magnitude; rule of three on independent flat rounds",
            ),
            invariant_ids=("invariant:no_verdict_certifies_recall",),
            objective_ids=("objective:stop_honestly",),
            uncertainty_semantics=("OPEN and CANNOT_CHECK are outcomes, not failures",),
            failure_signatures=("false_flatness_by_starvation", "unidentified_lineage"),
            falsifiers=("a new route family produces growth after a flat verdict",),
            diagnosis_rules=("check selection-window starvation before calling a run flat",),
            storage_contracts=("growth vectors are persisted per round with the basis fingerprint",),
            parent_domain_hypotheses=(
                "qualitative research: a priori thematic saturation",
                "technology-assisted review: stopping rules and target recall",
            ),
            # Both provisional: the basis is declared, and whether it measures
            # anything for a live trial is precisely unestablished.
            provisional_dimensions=(
                MechanicDimension.SATURATION,
                MechanicDimension.VERIFICATION,
            ),
            saturation_criteria=("two independent flat rounds under a fixed basis",),
            verification_contracts=("the basis fingerprint is recomputed, never trusted",),
        ),
        _fibre(
            "p5.live.verification",
            "Obtain verification from a lane that did not produce the answer.",
            "Per task; the only fibre that may close a criterion.",
            input_ids=("answer_text", "cited_evidence_ids", "frozen_evaluator"),
            output_ids=("criterion_results",),
            handoff_fields=(
                HandoffField(
                    "criterion_results",
                    "One result per frozen criterion, including CANNOT_CHECK.",
                    "orion.self_orion.live_packet.CriterionResult",
                ),
            ),
            state_ids=("closed_criteria",),
            observable_ids=("passed", "failed", "cannot_check"),
            action_ids=("action:evaluate_criterion",),
            transition_semantics=("deterministic given the answer, the trace and the gold",),
            mathematical_semantics=("predicate evaluation per criterion; no scalar aggregate",),
            invariant_ids=("invariant:verification_never_originates_in_the_answering_lane",),
            objective_ids=("objective:independent_closure",),
            uncertainty_semantics=("an unreachable verifier is CANNOT_CHECK, never a fail",),
            failure_signatures=("verifier_unreachable", "evaluator_hash_mismatch"),
            falsifiers=("a criterion passes under a different evaluator artifact hash",),
            diagnosis_rules=("separate verifier transport failure from a genuine criterion failure",),
            external_dependency_contract_ids=("provider:protected_verification",),
            parent_domain_hypotheses=("independent replication and protected-holdout evaluation",),
            saturation_criteria=("flat when no criterion changes state across rounds",),
            # HANDOFF and VERIFICATION provisional, STORAGE empty: the receipt
            # schema is stated but not shown to make the receipt independently
            # checkable, and what must persist from a verification pass is
            # unsettled until a protected verifier has actually answered.
            provisional_dimensions=(
                MechanicDimension.HANDOFF,
                MechanicDimension.VERIFICATION,
            ),
            verification_contracts=("the evaluator artifact hash is bound into every receipt",),
        ),
    )
