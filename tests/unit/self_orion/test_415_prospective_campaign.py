"""Deterministic #415 prospective campaign: method-evolution governance fixtures.

All tests are deterministic artifact-level checks — they never launch providers,
access credentials, or claim empirical self-improvement benefit.  A passing
suite means the governance architecture is fail-closed against the specified
failure modes; it does not establish that Self-ORION improves fresh development
outcomes.

Each fixture tests one governance invariant using the MethodChallenger.v1
record, the evolution archive, and the invention-readiness gate.
"""

from __future__ import annotations

import pytest

from orion.self_orion.evolution_archive import (
    EvolutionArchive,
    OrionVariant,
    VariantStatus,
    initialize_evolution_archive,
    register_challenger,
    register_method_challenger,
    record_method_challenger_disposition,
)
from orion.self_orion.invention_gate import (
    InventionReadinessEvidence,
    InventionTarget,
    assess_invention_readiness,
)
from orion.self_orion.method_challenger import (
    HostDisposition,
    MethodChallenger,
    MethodEvidenceStatus,
    MethodEvolutionStage,
    MethodStageEvidence,
    assess_method_challenger,
    validate_method_challenger,
)
from orion.self_orion.rakl_donor_gate import (
    RAKL_DONOR_COMMIT,
    RaklDonorAudit,
    RaklDonorCandidate,
    RaklDonorDisposition,
    RaklDonorRouteReceipt,
    RaklDonorRouteVerdict,
    RaklDonorSearchRoute,
)
from orion.self_orion.saturation_vector import (
    DevelopmentNoveltyRound,
    DevelopmentSaturationAxis,
    assess_development_saturation,
)

SHA = "a" * 64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean_challenger(**overrides: object) -> MethodChallenger:
    stages = tuple(
        MethodStageEvidence(
            stage,
            f"evidence:{stage.value}",
            MethodEvidenceStatus.PASS,
            split_id="split:fresh" if stage in (MethodEvolutionStage.FRESH, MethodEvolutionStage.PROTECTED) else "",
            evaluator_id="evaluator:protected" if stage in (MethodEvolutionStage.FRESH, MethodEvolutionStage.PROTECTED) else "",
            result_hash=SHA,
        )
        for stage in MethodEvolutionStage
    )
    values: dict[str, object] = {
        "challenger_id": "challenger:415:1",
        "subject_revision": SHA,
        "generating_failure_ids": ("failure:1",),
        "ordinary_causes_challenged": ("cause:execution", "cause:measurement"),
        "known_method_routes": ("route:literature", "route:transfer"),
        "route_inadequacy_reasons": ("route:literature inadequate", "route:transfer inadequate"),
        "assimilated_donor_mechanisms": ("donor:mechanism:1",),
        "structural_edit": "replace incumbent operator composition",
        "discriminator_prediction": "fresh protected family improves without protected harm",
        "stages": stages,
        "negative_history_ids": ("negative:rejected-1",),
    }
    values.update(overrides)
    return MethodChallenger(**values)


def _flat_saturation_report():
    zero = tuple((axis, 0) for axis in DevelopmentSaturationAxis)
    return assess_development_saturation(
        (
            DevelopmentNoveltyRound("r1", "function-only", True, zero),
            DevelopmentNoveltyRound("r2", "cross-domain", True, zero),
        )
    )


def _donor_audit(*, reusable: bool = False) -> RaklDonorAudit:
    receipts = tuple(
        RaklDonorRouteReceipt(
            route=route,
            verdict=RaklDonorRouteVerdict.COMPLETE,
            scope=f"searched {route.value.lower()} for target mechanic",
            evidence_ids=(f"e:rakl:{route.value.lower()}",),
        )
        for route in RaklDonorSearchRoute
    )
    disposition = (
        RaklDonorDisposition.RECONSTRUCTED
        if reusable
        else RaklDonorDisposition.REJECT_WITH_REASON
    )
    return RaklDonorAudit(
        audit_id="rakl-donor-audit:415",
        target_signature="missing operator for test target",
        rakl_commit=RAKL_DONOR_COMMIT,
        route_receipts=receipts,
        candidates=(
            RaklDonorCandidate(
                donor_id="rakl:415-donor",
                source_paths=("src/rakl/415_donor.py",),
                disposition=disposition,
                evidence_ids=("e:rakl:415-donor",),
                rationale_or_trigger=(
                    "existing RAKL contract survives and should be reconstructed"
                    if reusable
                    else "candidate contract is scoped to a different state transition"
                ),
            ),
        ),
    )


def _incumbent_archive() -> EvolutionArchive:
    return initialize_evolution_archive(
        OrionVariant(
            variant_id="incumbent:415",
            revision_hash=SHA,
            parent_ids=(),
            capability_tags=("base",),
            resource_profile=(("cpu", 1.0),),
            created_by_episode_ids=(),
            status=VariantStatus.INCUMBENT,
        )
    )


# ---------------------------------------------------------------------------
# 1. Valid adaptation: clean ladder → RECOMMEND, host-only
# ---------------------------------------------------------------------------


def test_valid_adaptation_reaches_host_recommendation() -> None:
    """A valid adaptation with complete evidence reaches RECOMMEND."""
    candidate = _clean_challenger()
    disposition, reasons = assess_method_challenger(candidate)
    assert disposition is HostDisposition.RECOMMEND
    assert any("complete" in r for r in reasons)
    validate_method_challenger(candidate)


def test_valid_adaptation_cannot_self_promote() -> None:
    """A valid adaptation cannot adopt, promote, or mutate the registry."""
    candidate = _clean_challenger()
    assert candidate.empirical_authority == "NONE"
    assert not candidate.can_mutate_method_registry
    assert candidate.adoption_authority == "EXTERNAL_HOST"


def test_valid_adaptation_registers_and_disposes_in_archive() -> None:
    """A valid method challenger can be registered and given a host disposition."""
    archive = _incumbent_archive()
    candidate = _clean_challenger()
    archive = register_method_challenger(archive, candidate)
    assert any(c.challenger_id == "challenger:415:1" for c in archive.challengers)
    archive = record_method_challenger_disposition(archive, "challenger:415:1", HostDisposition.RECOMMEND)
    assert any(
        rid == "challenger:415:1" and disp is HostDisposition.RECOMMEND
        for rid, disp in archive.challenger_dispositions
    )


# ---------------------------------------------------------------------------
# 2. Replay-only overfit: REPLAY passes but FRESH fails → REJECT
# ---------------------------------------------------------------------------


def test_replay_only_overfit_rejected() -> None:
    """Replay gain without fresh transfer benefit is rejected."""
    stages = list(_clean_challenger().stages)
    stages[5] = MethodStageEvidence(
        MethodEvolutionStage.FRESH,
        "evidence:fresh",
        MethodEvidenceStatus.FAIL,
        split_id="split:fresh",
        evaluator_id="evaluator:protected",
        result_hash=SHA,
    )
    disposition, reasons = assess_method_challenger(_clean_challenger(stages=tuple(stages)))
    assert disposition is HostDisposition.REJECT
    assert any("FAIL" in r or "failed" in r for r in reasons)


# ---------------------------------------------------------------------------
# 3. Protected-family harm: FRESH passes but PROTECTED harms → REJECT
# ---------------------------------------------------------------------------


def test_protected_family_harm_rejected() -> None:
    """Fresh transfer improves but protected family regresses — rejected."""
    stages = list(_clean_challenger().stages)
    stages[6] = MethodStageEvidence(
        MethodEvolutionStage.PROTECTED,
        "evidence:protected",
        MethodEvidenceStatus.HARMFUL,
        split_id="split:protected",
        evaluator_id="evaluator:protected",
        result_hash=SHA,
    )
    disposition, reasons = assess_method_challenger(_clean_challenger(stages=tuple(stages)))
    assert disposition is HostDisposition.REJECT
    assert any("HARMFUL" in r or "harmful" in r for r in reasons)


# ---------------------------------------------------------------------------
# 4. Donor-assumption deletion: missing assimilated_donor_mechanisms → BLOCK
# ---------------------------------------------------------------------------


def test_missing_donor_assimilation_blocked() -> None:
    """A challenger with no donor mechanism assimilation is structurally invalid."""
    with pytest.raises(ValueError, match="donor"):
        _clean_challenger(assimilated_donor_mechanisms=())


# ---------------------------------------------------------------------------
# 5. Evaluator rewrite: candidate cannot rewrite evaluator bindings
# ---------------------------------------------------------------------------


def test_candidate_cannot_rewrite_evaluator_binding() -> None:
    """Fresh/protected stages require split and evaluator identities that are
    bound at construction time — the candidate cannot retroactively change them."""
    with pytest.raises(ValueError, match="split and evaluator"):
        MethodStageEvidence(
            MethodEvolutionStage.FRESH,
            "evidence:fresh",
            MethodEvidenceStatus.PASS,
            result_hash=SHA,
        )


# ---------------------------------------------------------------------------
# 6. Negative-history truncation
# ---------------------------------------------------------------------------


def test_empty_negative_history_rejected() -> None:
    """A challenger with no negative history is structurally invalid."""
    with pytest.raises(ValueError, match="negative history"):
        _clean_challenger(negative_history_ids=())


# ---------------------------------------------------------------------------
# 7. Known method disguised as invention: invention-readiness gate blocks
# ---------------------------------------------------------------------------


def test_repeated_failure_alone_does_not_authorize_invention() -> None:
    """Invention readiness requires ordinary causes excluded, even with
    repeated residual variations."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2", "v3"),
            ordinary_causes_excluded=False,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:discriminator",),
            rakl_donor_audit=_donor_audit(),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert not report.ready
    assert "ordinary_failure_causes_not_excluded" in report.reasons


def test_rakl_surviving_donor_preempts_invention() -> None:
    """Clean generation invention is blocked when a RAKL donor survives."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
            rakl_donor_audit=_donor_audit(reusable=True),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert not report.ready
    assert "rakl_surviving_donor_available" in " ".join(report.reasons)


# ---------------------------------------------------------------------------
# 8. Premature method-basis opening: no method challenger
# ---------------------------------------------------------------------------


def test_method_basis_gap_requires_registered_challenger() -> None:
    """Invention readiness for METHOD_BASIS_GAP requires a registered
    method challenger ID."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2", "v3"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1", "e:2"),
            rakl_donor_audit=_donor_audit(),
        ),
    )
    assert not report.ready
    assert "method_challenger_not_registered" in report.reasons


# ---------------------------------------------------------------------------
# 9. Missing protected evidence
# ---------------------------------------------------------------------------


def test_missing_protected_evidence_is_blocked() -> None:
    """A candidate missing PROTECTED stage evidence is blocked."""
    stages = tuple(
        item for item in _clean_challenger().stages
        if item.stage is not MethodEvolutionStage.PROTECTED
    )
    disposition, reasons = assess_method_challenger(_clean_challenger(stages=stages))
    assert disposition is HostDisposition.BLOCK
    assert "missing_stages" in " ".join(reasons)
    with pytest.raises(ValueError, match="not admissible"):
        validate_method_challenger(_clean_challenger(stages=stages))


def test_missing_fresh_evidence_is_blocked() -> None:
    """A candidate missing FRESH stage evidence is blocked."""
    stages = tuple(
        item for item in _clean_challenger().stages
        if item.stage is not MethodEvolutionStage.FRESH
    )
    disposition, reasons = assess_method_challenger(_clean_challenger(stages=stages))
    assert disposition is HostDisposition.BLOCK
    assert "missing_stages" in " ".join(reasons)


# ---------------------------------------------------------------------------
# 10. Clean no-alarm case: full governance with no false positives
# ---------------------------------------------------------------------------


def test_clean_no_alarm_no_false_positive_authority_claims() -> None:
    """A clean candidate must not accidentally grant authority or self-promotion."""
    candidate = _clean_challenger()
    assert candidate.empirical_authority == "NONE"
    assert not candidate.can_mutate_method_registry
    assert candidate.host_disposition is HostDisposition.CANDIDATE_ONLY
    assert candidate.adoption_authority == "EXTERNAL_HOST"
    assert not candidate.candidate_controls_authority


def test_invention_readiness_cannot_grant_authority() -> None:
    """Invention readiness reports never grant authority."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2", "v3"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1", "e:2"),
            rakl_donor_audit=_donor_audit(),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert report.ready
    assert not report.grants_invention_authority
    assert not report.grants_promotion_authority


# ---------------------------------------------------------------------------
# Hostile: duplicate challenger ID
# ---------------------------------------------------------------------------


def test_duplicate_challenger_id_rejected() -> None:
    """Registering a method challenger with a duplicate ID is rejected."""
    archive = _incumbent_archive()
    candidate = _clean_challenger()
    archive = register_method_challenger(archive, candidate)
    with pytest.raises(ValueError, match="duplicate method challenger id"):
        register_method_challenger(archive, candidate)


# ---------------------------------------------------------------------------
# Hostile: invention-readiness ambiguous target
# ---------------------------------------------------------------------------


def test_ambiguous_invention_target_blocked() -> None:
    """Multiple supported gap types block invention readiness."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=True,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
            rakl_donor_audit=_donor_audit(),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert not report.ready
    assert "invention_target_responsibility_ambiguous" in report.reasons


# ---------------------------------------------------------------------------
# Hostile: missing discriminator evidence
# ---------------------------------------------------------------------------


def test_missing_discriminator_evidence_blocks_invention() -> None:
    """No discriminator evidence → invention readiness blocked."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=(),
            rakl_donor_audit=_donor_audit(),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert not report.ready
    assert "discriminator_evidence_missing" in report.reasons


# ---------------------------------------------------------------------------
# Hostile: missing RAKL donor audit
# ---------------------------------------------------------------------------


def test_missing_rakl_donor_audit_blocks_invention() -> None:
    """No RAKL donor audit → invention readiness blocked."""
    report = assess_invention_readiness(
        _flat_saturation_report(),
        InventionReadinessEvidence(
            stable_residual_variation_ids=("v1", "v2"),
            ordinary_causes_excluded=True,
            cross_domain_routes_bounded_flat=True,
            representation_gap_supported=False,
            method_basis_gap_supported=True,
            ontology_gap_supported=False,
            discriminator_evidence_ids=("e:1",),
            method_challenger_id="challenger:415:method",
        ),
    )
    assert not report.ready
    assert "rakl_donor_audit_missing" in report.reasons


# ---------------------------------------------------------------------------
# Hostile: no structural edit
# ---------------------------------------------------------------------------


def test_missing_structural_edit_rejected() -> None:
    """A challenger with no structural edit is structurally invalid."""
    with pytest.raises(ValueError, match="structural edit"):
        _clean_challenger(structural_edit="")


# ---------------------------------------------------------------------------
# Hostile: no generating failure records
# ---------------------------------------------------------------------------


def test_missing_failure_records_rejected() -> None:
    """A challenger with no generating failure records is invalid."""
    with pytest.raises(ValueError, match="generating failure"):
        _clean_challenger(generating_failure_ids=())


# ---------------------------------------------------------------------------
# Hostile: no ordinary causes challenged
# ---------------------------------------------------------------------------


def test_missing_ordinary_causes_challenged_rejected() -> None:
    """A challenger that challenges no ordinary causes is invalid."""
    with pytest.raises(ValueError, match="ordinary-cause"):
        _clean_challenger(ordinary_causes_challenged=())