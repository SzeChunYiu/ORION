from __future__ import annotations

import dataclasses

import pytest

from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateReport,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)

SUBJECT = "candidate:1"


def _contract(frozen_at_round: int | None = 0, n: int = 2) -> HardGateContract:
    return HardGateContract(
        contract_id="c1",
        requirements=tuple(
            HardGateRequirement(f"gate:{i}", f"blocking condition {i}") for i in range(n)
        ),
        frozen_at_round=frozen_at_round,
    )


def _obs(contract, gate_id, state=HardGateState.PASS, evidence=("e1",), subject=SUBJECT):
    return HardGateObservation(
        gate_id=gate_id,
        subject_id=subject,
        state=state,
        contract_fingerprint=contract.fingerprint,
        evidence_ids=evidence,
    )


def test_all_gates_passed_with_evidence_permits_closure() -> None:
    contract = _contract()
    report = evaluate_hard_gates(
        contract,
        [_obs(contract, "gate:0"), _obs(contract, "gate:1")],
        subject_id=SUBJECT,
        round_index=1,
    )
    assert report.state is HardGateState.PASS
    assert report.permits_closure


def test_one_failed_gate_is_not_compensated_by_every_other_passing() -> None:
    """The whole point. A blocking condition has no scale to trade against."""

    contract = _contract(n=20)
    observations = [_obs(contract, f"gate:{i}") for i in range(19)]
    observations.append(_obs(contract, "gate:19", state=HardGateState.FAIL))
    report = evaluate_hard_gates(
        contract, observations, subject_id=SUBJECT, round_index=1
    )
    assert report.state is HardGateState.FAIL
    assert not report.permits_closure
    assert len(report.passed_gate_ids) == 19


def test_an_unobserved_gate_is_cannot_check_not_pass() -> None:
    contract = _contract()
    report = evaluate_hard_gates(
        contract, [_obs(contract, "gate:0")], subject_id=SUBJECT, round_index=1
    )
    assert report.state is HardGateState.CANNOT_CHECK
    assert report.unresolved_gate_ids == ("gate:1",)


def test_unknown_chronology_refuses_before_any_observation_is_read() -> None:
    """An inadmissible measurement is not a low measurement."""

    contract = _contract(frozen_at_round=None)
    report = evaluate_hard_gates(
        contract,
        [_obs(contract, "gate:0"), _obs(contract, "gate:1")],
        subject_id=SUBJECT,
        round_index=1,
    )
    assert report.state is HardGateState.CANNOT_CHECK
    assert "gate_contract_chronology_unknown" in report.reasons


def test_a_contract_frozen_after_the_round_fails_integrity() -> None:
    contract = _contract(frozen_at_round=5)
    report = evaluate_hard_gates(
        contract, [_obs(contract, "gate:0")], subject_id=SUBJECT, round_index=1
    )
    assert report.state is HardGateState.FAIL
    assert report.failed_gate_ids == ("CONTRACT_INTEGRITY",)


def test_an_observation_made_under_an_edited_contract_fails() -> None:
    """Post-hoc contract edits must not silently re-pass old measurements."""

    original = _contract()
    observations = [_obs(original, "gate:0"), _obs(original, "gate:1")]
    edited = HardGateContract(
        contract_id="c1",
        requirements=(
            *original.requirements,
            HardGateRequirement("gate:2", "added later"),
        ),
        frozen_at_round=0,
    )
    report = evaluate_hard_gates(edited, observations, subject_id=SUBJECT, round_index=1)
    assert report.state is HardGateState.FAIL
    assert report.failed_gate_ids == ("CONTRACT_INTEGRITY",)


def test_conflicting_observations_fail_rather_than_last_write_winning() -> None:
    contract = _contract()
    observations = [
        _obs(contract, "gate:0"),
        _obs(contract, "gate:0", state=HardGateState.FAIL),
        _obs(contract, "gate:1"),
    ]
    report = evaluate_hard_gates(
        contract, observations, subject_id=SUBJECT, round_index=1
    )
    assert report.state is HardGateState.FAIL
    assert "gate_observations_conflict:gate:0" in report.reasons
    reversed_report = evaluate_hard_gates(
        contract, list(reversed(observations)), subject_id=SUBJECT, round_index=1
    )
    assert reversed_report.state is HardGateState.FAIL


def test_a_pass_without_required_evidence_is_unresolved() -> None:
    contract = _contract()
    report = evaluate_hard_gates(
        contract,
        [_obs(contract, "gate:0", evidence=()), _obs(contract, "gate:1")],
        subject_id=SUBJECT,
        round_index=1,
    )
    assert report.state is HardGateState.CANNOT_CHECK
    assert "gate_passed_without_evidence:gate:0" in report.reasons


def test_another_subjects_observations_do_not_satisfy_this_one() -> None:
    contract = _contract()
    report = evaluate_hard_gates(
        contract,
        [_obs(contract, "gate:0"), _obs(contract, "gate:1", subject="candidate:2")],
        subject_id=SUBJECT,
        round_index=1,
    )
    assert report.state is HardGateState.CANNOT_CHECK


def test_failure_dominates_cannot_check() -> None:
    contract = _contract(n=3)
    report = evaluate_hard_gates(
        contract,
        [_obs(contract, "gate:0"), _obs(contract, "gate:1", state=HardGateState.FAIL)],
        subject_id=SUBJECT,
        round_index=1,
    )
    assert report.state is HardGateState.FAIL


def test_the_report_carries_no_aggregate_to_trade_against() -> None:
    """A count or ratio of passes would invite the substitution gates refuse."""

    numeric = [
        item.name
        for item in dataclasses.fields(HardGateReport)
        if item.type in {"int", "float"}
    ]
    assert not numeric


def test_a_contract_with_no_requirements_is_refused() -> None:
    with pytest.raises(ValueError):
        HardGateContract(contract_id="c", requirements=())
