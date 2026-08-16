from dataclasses import FrozenInstanceError

import pytest

from orion.knowledge.bridge_composition import (
    BridgeHandoff,
    BridgeHop,
    BridgePath,
    BridgePathVerdict,
    BridgeTargetVerdict,
    BridgeTransferTrial,
    ErrorCompositionRule,
    ErrorCompositionRuleKind,
    evaluate_bridge_path,
    evaluate_bridge_transfer,
)
from orion.knowledge.similarity import MappingAdmissibility, ProbeFamily, SimilarityRelation, SimilarityWitness


QOI = "does stability structure transfer?"


def _witness(source_id: str, target_id: str, *, qoi: str = QOI, preserved=("feedback_loop", "role_order"), not_preserved=("substrate",), regime=("bounded-input", "low-noise"), relation=SimilarityRelation.RELATIONALLY_ANALOGOUS):
    constraints = ("typed_roles", "causal_direction")
    if relation is SimilarityRelation.MATHEMATICALLY_ISOMORPHIC:
        constraints = ("typed_roles", "type_or_unit_compatibility")
    return SimilarityWitness(
        relation=relation,
        source_id=source_id,
        target_id=target_id,
        source_domain=f"domain-{source_id}",
        target_domain=f"domain-{target_id}",
        question_or_qoi=qoi,
        mapping_pairs=(("driver", "driver"), ("response", "response")),
        preserved=preserved,
        not_preserved=not_preserved,
        regime=regime,
        evidence_ids=(f"evidence-{source_id}-{target_id}",),
        mapping_admissibility=MappingAdmissibility("typed-map-v1", True, constraints, (), True),
        probe_family=ProbeFamily("bridge-probes-v1", ("role", "regime")),
    )


def _hop(source: str, target: str, *, error: float | None = 0.05, semantics="certified_metric_v1", lineage="independent", **overrides):
    return BridgeHop(_witness(source, target, **overrides), error, (lineage,), semantics)


def _rule(**overrides):
    values = dict(rule_id="additive-certified-v1", error_semantics_id="certified_metric_v1", kind=ErrorCompositionRuleKind.ADDITIVE_UPPER_BOUND, certified_before_outcomes=True)
    values.update(overrides)
    return ErrorCompositionRule(**values)


def _path(**overrides):
    values = dict(
        path_id="A-B-C",
        question_or_qoi=QOI,
        hops=(_hop("A", "B", error=0.05, lineage="A"), _hop("B", "C", error=0.07, lineage="B")),
        handoffs=(BridgeHandoff("B", (("driver", "driver"), ("response", "response")), True, ("handoff-B",)),),
        claimed_end_to_end_invariants=("feedback_loop",),
        max_accumulated_error=0.20,
        hidden_labels_exposed=False,
        declared_before_outcomes=True,
        error_composition_rule=_rule(),
    )
    values.update(overrides)
    return BridgePath(**values)


def test_valid_two_hop_path_is_transfer_hypothesis_only():
    report = evaluate_bridge_path(_path())
    assert report.verdict is BridgePathVerdict.COMPOSABLE_TRANSFER_HYPOTHESIS_ONLY
    assert report.accumulated_error_upper_bound == pytest.approx(0.12)
    assert report.inferred_endpoint_relation is None
    assert not report.grants_target_authority


def test_valid_hops_without_common_invariant_are_navigation_only():
    assert evaluate_bridge_path(_path(claimed_end_to_end_invariants=())).verdict is BridgePathVerdict.NAVIGABLE_ONLY


def test_intermediate_identity_and_handoff_mismatch_reject():
    assert evaluate_bridge_path(_path(hops=(_hop("A", "B"), _hop("B2", "C")))).verdict is BridgePathVerdict.REJECT
    bad = BridgeHandoff("B", (("missing", "driver"),), True, ("handoff-B",))
    assert evaluate_bridge_path(_path(handoffs=(bad,))).verdict is BridgePathVerdict.REJECT


def test_qoi_drift_rejects_and_empty_regime_is_navigation_only():
    assert evaluate_bridge_path(_path(hops=(_hop("A", "B"), _hop("B", "C", qoi="throughput")))).verdict is BridgePathVerdict.REJECT
    report = evaluate_bridge_path(_path(hops=(_hop("A", "B", regime=("low",)), _hop("B", "C", regime=("high",)))))
    assert report.verdict is BridgePathVerdict.NAVIGABLE_ONLY
    assert report.common_regime == ()


def test_broken_or_unresolved_carried_invariant_fails_closed():
    broken = _hop("B", "C", preserved=("role_order",), not_preserved=("substrate", "feedback_loop"))
    assert evaluate_bridge_path(_path(hops=(_hop("A", "B"), broken))).verdict is BridgePathVerdict.REJECT
    unresolved = _hop("B", "C", preserved=("role_order",), not_preserved=("substrate",))
    assert evaluate_bridge_path(_path(hops=(_hop("A", "B"), unresolved))).verdict is BridgePathVerdict.CANNOT_CHECK


def test_error_semantics_and_budget_are_explicit():
    assert evaluate_bridge_path(_path(error_composition_rule=None)).verdict is BridgePathVerdict.CANNOT_CHECK
    mixed = (_hop("A", "B", semantics="tv"), _hop("B", "C", semantics="kl"))
    assert evaluate_bridge_path(_path(hops=mixed, error_composition_rule=_rule(error_semantics_id="tv"))).verdict is BridgePathVerdict.REJECT
    assert evaluate_bridge_path(_path(max_accumulated_error=0.10)).verdict is BridgePathVerdict.NAVIGABLE_ONLY


def test_correlated_evidence_is_flagged_not_independence():
    report = evaluate_bridge_path(_path(hops=(_hop("A", "B", lineage="same"), _hop("B", "C", lineage="same"))))
    assert report.verdict is BridgePathVerdict.COMPOSABLE_TRANSFER_HYPOTHESIS_ONLY
    assert report.correlated_evidence is True


def test_hidden_labels_or_posthoc_selection_invalidate_trial():
    assert evaluate_bridge_path(_path(hidden_labels_exposed=True)).verdict is BridgePathVerdict.TRIAL_INVALID
    assert evaluate_bridge_path(_path(declared_before_outcomes=False)).verdict is BridgePathVerdict.TRIAL_INVALID
    assert evaluate_bridge_path(_path(error_composition_rule=_rule(certified_before_outcomes=False))).verdict is BridgePathVerdict.TRIAL_INVALID


def test_mixed_relations_never_mint_endpoint_relation():
    hops = (
        _hop("A", "B", relation=SimilarityRelation.OBSERVATIONALLY_EQUIVALENT, error=0.0),
        _hop("B", "C", relation=SimilarityRelation.MATHEMATICALLY_ISOMORPHIC, error=0.0),
    )
    report = evaluate_bridge_path(_path(hops=hops))
    assert report.verdict is BridgePathVerdict.COMPOSABLE_TRANSFER_HYPOTHESIS_ONLY
    assert report.inferred_endpoint_relation is None
    assert not report.grants_target_authority


def test_target_refutation_preserves_path_and_target_pass_needs_separate_promotion():
    refuted = evaluate_bridge_transfer(BridgeTransferTrial("refute", _path(), True, False))
    assert refuted.verdict is BridgeTargetVerdict.TARGET_REFUTED_PATH_WITNESSES_PRESERVED
    assert not refuted.activates_canonical_knowledge
    passed = evaluate_bridge_transfer(BridgeTransferTrial("pass", _path(), True, True))
    assert passed.verdict is BridgeTargetVerdict.TARGET_TEST_PASSED_SEPARATE_PROMOTION_REQUIRED
    assert not passed.activates_canonical_knowledge


def test_bridge_contract_is_immutable():
    path = _path()
    with pytest.raises(FrozenInstanceError):
        path.path_id = "changed"  # type: ignore[misc]
