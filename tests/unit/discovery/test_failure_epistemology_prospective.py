from __future__ import annotations

import copy
import json
from pathlib import Path

from orion.discovery.failure_epistemology_prospective import (
    BenchmarkArm,
    DecisionKind,
    FailureEpistemologyTerminal,
    TransportWitnessKind,
    build_failure_epistemology_prospective_report,
    build_frozen_failure_epistemology_cases,
    decide_case,
)
from orion.transfer.v2.failure_knowledge import (
    FailureApplicabilityStatus,
    assess_failure_applicability,
    build_failure_knowledge,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "orion-jump-recursive-atoms" / "failure_epistemology"
CASES = RESEARCH / "FAILURE_EPISTEMOLOGY_CASES_V1.json"
EXPECTED = RESEARCH / "FAILURE_EPISTEMOLOGY_EXPECTED_V1.json"
SATURATION = RESEARCH / "FAILURE_EPISTEMOLOGY_SATURATION_V1.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report(case_packet: dict[str, object] | None = None):
    return build_failure_epistemology_prospective_report(
        case_packet=case_packet or _load(CASES),
        expected=_load(EXPECTED),
    )


def test_prospective_failure_epistemology_matches_pre_frozen_terminal_and_metrics() -> None:
    expected = _load(EXPECTED)
    report = _report()

    assert report.case_count == expected["benchmark"]["cases"] == 32
    assert report.family_count == expected["benchmark"]["families"] == 8
    assert report.standard_parent_equals_orion_all_case_decisions is True
    assert report.standard_parent_equals_orion_all_metrics is True
    assert report.strong_parent_incremental_gap == 0
    assert report.terminal.value == expected["candidate_terminal"]
    assert (
        report.terminal
        is FailureEpistemologyTerminal.FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT
    )
    assert report.all_checks_passed is True

    for arm_name, expected_metrics in expected["protected_expected"].items():
        metric = report.metric(BenchmarkArm(arm_name))
        for field_name, expected_value in expected_metrics.items():
            assert getattr(metric, field_name) == expected_value

    assert report.grants_scientific_refutation is False
    assert report.grants_global_prohibition is False
    assert report.grants_novelty_authority is False
    assert report.grants_real_world_generalization is False
    assert report.grants_issue_closure_authority is False


def test_failure_history_is_useful_but_naive_memory_is_harmful() -> None:
    report = _report()
    no_history = report.metric(BenchmarkArm.NO_FAILURE_HISTORY)
    global_ban = report.metric(BenchmarkArm.GLOBAL_FAILURE_BAN)
    exact = report.metric(BenchmarkArm.EXACT_CONTEXT_MEMORY)
    parent = report.metric(BenchmarkArm.STANDARD_PARENT)
    orion = report.metric(BenchmarkArm.ORION_SCOPED_FAILURE)

    assert no_history.repeat_dead_end_count == 8
    assert orion.repeat_dead_end_count == 0
    assert parent.repeat_dead_end_count == 0

    assert global_ban.false_exclusion_count == 12
    assert orion.false_exclusion_count == 0
    assert parent.false_exclusion_count == 0

    assert exact.false_reopen_count == 4
    assert orion.false_reopen_count == 0
    assert parent.false_reopen_count == 0


def test_semantic_preserving_nonidentity_requires_transport_not_string_equality() -> None:
    cases = build_frozen_failure_epistemology_cases(_load(CASES))
    case = next(case for case in cases if case.case_id == "E3-01")

    failure = build_failure_knowledge(
        failure_id="e3-failure",
        target_contract_id="target",
        regime_id=case.prior_context_dict["regime"],
        attempted_trace_ids=("attempt-method-a",),
        observed_failure_id="observed",
        responsibility_state_id="RESOLVED_SCIENTIFIC",
        excluded_condition_ids=("exclude-method-a",),
        still_live_alternative_ids=("method-b",),
        preserved_success_ids=("old-success",),
        frozen_context=case.prior_context_dict,
        required_same_coordinates=case.required_same_coordinates,
        reopen_on_change_coordinates=case.reopen_on_change_coordinates,
        evidence_ids=("evidence",),
        authority_owner_id=case.authority_owner_id,
    )
    v1 = assess_failure_applicability(failure, current_context=case.current_context_dict)

    assert v1.status is FailureApplicabilityStatus.REOPENED
    assert case.transport_witness_kind is TransportWitnessKind.COMPLETE
    assert decide_case(case, BenchmarkArm.EXACT_CONTEXT_MEMORY).kind is DecisionKind.SELECT_ACTION
    assert decide_case(case, BenchmarkArm.EXACT_CONTEXT_MEMORY).target_id == "method-a"
    assert decide_case(case, BenchmarkArm.STANDARD_PARENT).target_id == "method-b"
    assert decide_case(case, BenchmarkArm.ORION_SCOPED_FAILURE).target_id == "method-b"


def test_execution_failure_does_not_become_scientific_refutation() -> None:
    cases = build_frozen_failure_epistemology_cases(_load(CASES))
    case = next(case for case in cases if case.case_id == "E4-01")

    assert decide_case(case, BenchmarkArm.GLOBAL_FAILURE_BAN).target_id == "method-b"
    assert decide_case(case, BenchmarkArm.EXACT_CONTEXT_MEMORY).target_id == "method-b"
    assert decide_case(case, BenchmarkArm.STANDARD_PARENT).target_id == "method-a"
    assert decide_case(case, BenchmarkArm.ORION_SCOPED_FAILURE).target_id == "method-a"

    report = _report()
    assert report.metric(BenchmarkArm.GLOBAL_FAILURE_BAN).scientific_authority_violation_count == 4
    assert report.metric(BenchmarkArm.ORION_SCOPED_FAILURE).scientific_authority_violation_count == 0


def test_plural_responsibility_queries_only_when_decision_relevant() -> None:
    cases = build_frozen_failure_epistemology_cases(_load(CASES))
    discriminating = next(case for case in cases if case.case_id == "E5-01")
    nondiscriminating = next(case for case in cases if case.case_id == "E6-01")

    for arm in (BenchmarkArm.STANDARD_PARENT, BenchmarkArm.ORION_SCOPED_FAILURE):
        query_decision = decide_case(discriminating, arm)
        assert query_decision.kind is DecisionKind.QUERY
        assert query_decision.target_id == "query-decisive"

        unresolved = decide_case(nondiscriminating, arm)
        assert unresolved.kind is DecisionKind.UNRESOLVED
        assert unresolved.target_id is None


def test_incomplete_negative_results_archive_blocks_global_promotion() -> None:
    cases = build_frozen_failure_epistemology_cases(_load(CASES))
    case = next(case for case in cases if case.case_id == "E8-01")

    assert case.archive_manifest is not None
    assert case.archive_manifest.has_visibility_distortion is True
    assert decide_case(case, BenchmarkArm.NO_FAILURE_HISTORY).kind is DecisionKind.PROMOTE_VISIBLE_SUCCESS
    assert decide_case(case, BenchmarkArm.STANDARD_PARENT).kind is DecisionKind.DISTORTION_SUSPECTED
    assert decide_case(case, BenchmarkArm.ORION_SCOPED_FAILURE).kind is DecisionKind.DISTORTION_SUSPECTED


def test_tampering_with_frozen_gold_or_outcome_access_fails_closure() -> None:
    packet = _load(CASES)
    accessed = copy.deepcopy(packet)
    accessed["outcome_accessed"] = True
    try:
        _report(accessed)
    except ValueError as exc:
        assert "outcome access" in str(exc)
    else:
        raise AssertionError("outcome-accessed case packet should reject")

    tampered = copy.deepcopy(packet)
    e1 = next(row for row in tampered["family_templates"] if row["case_id_prefix"] == "E1")
    e1["gold_decision"] = {"kind":"SELECT_ACTION","target_id":"method-a"}
    report = _report(tampered)
    assert report.terminal is FailureEpistemologyTerminal.CANNOT_CHECK
    assert report.all_checks_passed is False


def test_standard_parent_and_orion_have_no_hidden_incremental_gap() -> None:
    report = _report()
    parent = report.metric(BenchmarkArm.STANDARD_PARENT)
    orion = report.metric(BenchmarkArm.ORION_SCOPED_FAILURE)

    assert parent.decision_keys == orion.decision_keys
    assert parent.decision_accuracy_count == orion.decision_accuracy_count == 32
    assert parent.query_cost == orion.query_cost == 4
    assert report.strong_parent_incremental_gap == 0


def test_two_post_design_saturation_rounds_have_no_material_change() -> None:
    saturation = _load(SATURATION)

    assert saturation["version"] == "FailureEpistemologySaturation.v1"
    assert saturation["design_and_expected_frozen_before_rounds"] is True
    assert len(saturation["rounds"]) == 2
    assert sum(len(round_["primary_sources"]) for round_ in saturation["rounds"]) == 6
    for round_ in saturation["rounds"]:
        assert round_["material_change"] is False
        assert round_["result"] == "NO_MATERIAL_CHANGE"
        assert round_["new_residual_coordinate_ids"] == []
        assert round_["primary_sources"]
