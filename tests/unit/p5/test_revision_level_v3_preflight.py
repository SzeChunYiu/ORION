from __future__ import annotations

import pytest

from orion.study.p5.revision_level_v3_preflight import (
    BaselineBindingDisposition,
    BaselineStructuralBinding,
    ConfirmatoryExecutionBinding,
    ConfirmatoryPreflightStatus,
    assess_confirmatory_preflight,
)

HEX = "a" * 64


def _binding() -> ConfirmatoryExecutionBinding:
    return ConfirmatoryExecutionBinding(
        protocol_id="P5.self-orion-v3.revision-level.v1",
        subject_revision="b" * 40,
        protected_suite_commitment="c" * 64,
        candidate_packet_sha256="d" * 64,
        final_split_sha256="e" * 64,
        evaluator_sha256="f" * 64,
        evaluation_epoch="v3:epoch:1",
        baseline_config_sha256="1" * 64,
        fresh_transfer_evaluator_sha256="2" * 64,
        result_verifier_owner="#283",
        candidate_policy_owner="SelfOrionV3Policy",
        protected_evaluator_owner="ExternalProtectedEvaluator",
        outcome_accessed=False,
    )


def _baseline(baseline_id: str, *, bound: bool = True) -> BaselineStructuralBinding:
    return BaselineStructuralBinding.build(
        baseline_id=baseline_id,
        donor_id={
            "m_open_only": "arxiv:2608.09696",
            "world_model_revision": "arxiv:2606.30639",
            "representation_regime_revision": "arxiv:2606.01444",
        }.get(baseline_id, "orion:internal"),
        source_identity="source:" + baseline_id,
        disposition=(
            BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND
            if bound
            else BaselineBindingDisposition.CANNOT_CHECK
        ),
        structural_binding_id=("t8-struct:" + baseline_id) if bound else "",
        official_reproduction=False,
        notes=("mechanism comparator only",),
    )


def _baselines(*, m_open_bound=True):
    return (
        _baseline("m_open_only", bound=m_open_bound),
        _baseline("world_model_revision"),
        _baseline("representation_regime_revision"),
    )


def test_ready_requires_all_bindings_and_separate_evaluator_owner() -> None:
    report = assess_confirmatory_preflight(
        _binding(),
        _baselines(),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.READY_TO_FREEZE_CONFIRMATORY
    assert report.blockers == ()
    assert report.grants_scientific_authority is False
    assert report.grants_p5_peer_review_ready is False


def test_missing_or_cannot_check_donor_binding_blocks_ready() -> None:
    report = assess_confirmatory_preflight(
        _binding(),
        _baselines(m_open_bound=False),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert any("m_open_only" in blocker for blocker in report.blockers)


def test_missing_required_baseline_record_blocks_ready() -> None:
    report = assess_confirmatory_preflight(
        _binding(),
        (_baseline("m_open_only"),),
        required_baseline_ids=("m_open_only", "world_model_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert "baseline_binding_missing:world_model_revision" in report.blockers


def test_placeholder_hashes_and_epoch_block_ready() -> None:
    binding = _binding()
    binding = ConfirmatoryExecutionBinding(
        **{**binding.__dict__, "final_split_sha256": "UNBOUND", "evaluation_epoch": "UNBOUND"}
    )
    report = assess_confirmatory_preflight(
        binding,
        _baselines(),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert any("final_split" in blocker for blocker in report.blockers)
    assert any("evaluation_epoch" in blocker for blocker in report.blockers)


def test_candidate_cannot_own_protected_evaluator() -> None:
    binding = _binding()
    binding = ConfirmatoryExecutionBinding(
        **{**binding.__dict__, "protected_evaluator_owner": binding.candidate_policy_owner}
    )
    report = assess_confirmatory_preflight(
        binding,
        _baselines(),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert "candidate_controls_protected_evaluator" in report.blockers


def test_outcome_access_before_final_freeze_blocks_ready() -> None:
    binding = _binding()
    binding = ConfirmatoryExecutionBinding(**{**binding.__dict__, "outcome_accessed": True})
    report = assess_confirmatory_preflight(
        binding,
        _baselines(),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert "outcome_accessed_before_confirmatory_freeze" in report.blockers


def test_official_reproduction_label_requires_official_disposition() -> None:
    with pytest.raises(ValueError, match="official reproduction"):
        BaselineStructuralBinding.build(
            baseline_id="m_open_only",
            donor_id="arxiv:2608.09696",
            source_identity="source:mda",
            disposition=BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND,
            structural_binding_id="t8-struct:mda",
            official_reproduction=True,
            notes=(),
        )


def test_result_verifier_owner_must_be_external_283_route() -> None:
    binding = _binding()
    binding = ConfirmatoryExecutionBinding(**{**binding.__dict__, "result_verifier_owner": "candidate"})
    report = assess_confirmatory_preflight(
        binding,
        _baselines(),
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert "result_verifier_owner_not_283" in report.blockers
