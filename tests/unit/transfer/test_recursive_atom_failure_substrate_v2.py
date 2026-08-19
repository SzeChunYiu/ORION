from __future__ import annotations

import pytest

from orion.transfer.v2.bounded_epistemic_study import (
    build_atom_study,
    build_resource_bound,
)
from orion.transfer.v2.failure_knowledge import (
    FailureApplicabilityStatus,
    assess_failure_applicability,
    build_failure_knowledge,
)


def _build_failure(**overrides):
    kwargs = {
        "failure_id": "F-review",
        "target_contract_id": "C",
        "regime_id": "R",
        "attempted_trace_ids": ("attempt",),
        "observed_failure_id": "observed",
        "responsibility_state_id": "resolved",
        "excluded_condition_ids": ("method-a",),
        "frozen_context": {
            "representation": "rep-v1",
            "measurement": "sensor-v1",
            "objective": "goal-v1",
        },
        "required_same_coordinates": ("measurement", "objective"),
        "reopen_on_change_coordinates": ("representation",),
        "evidence_ids": ("ev",),
        "authority_owner_id": "authority",
    }
    kwargs.update(overrides)
    return build_failure_knowledge(**kwargs)


def test_failure_context_roles_must_cover_every_frozen_coordinate() -> None:
    with pytest.raises(ValueError, match="classified"):
        _build_failure(
            required_same_coordinates=(),
            reopen_on_change_coordinates=(),
        )

    with pytest.raises(ValueError, match="lacks applicability role"):
        _build_failure(
            required_same_coordinates=("measurement",),
            reopen_on_change_coordinates=("representation",),
        )


def test_required_same_mismatch_outranks_simultaneous_reopen_change() -> None:
    failure = _build_failure()
    report = assess_failure_applicability(
        failure,
        current_context={
            "representation": "rep-v2",
            "measurement": "sensor-v2",
            "objective": "goal-v1",
        },
    )

    assert report.status is FailureApplicabilityStatus.NOT_APPLICABLE
    assert report.applicable_excluded_condition_ids == ()
    assert set(report.changed_coordinates) == {"representation", "measurement"}
    assert "REQUIRED_SAME_CONTEXT_CHANGED" in report.reasons
    assert "REOPEN_CHANGE_IGNORED_DUE_TO_REQUIRED_SAME_MISMATCH" in report.reasons


def test_atom_study_requires_evaluator_authority_separation() -> None:
    with pytest.raises(ValueError, match="independent"):
        build_atom_study(
            atom_id="atom",
            structure_version="v2",
            target_contract_ids=("contract",),
            resource_bound=build_resource_bound({"steps": 1}),
            positive_case_ids=("p",),
            no_atom_control_ids=("n",),
            parent_baseline_ids=("parent",),
            evaluator_id="same-owner",
            authority_owner_id="same-owner",
        )


def test_distinct_evaluator_and_authority_remain_valid() -> None:
    study = build_atom_study(
        atom_id="atom",
        structure_version="v2",
        target_contract_ids=("contract",),
        resource_bound=build_resource_bound({"steps": 1}),
        positive_case_ids=("p",),
        no_atom_control_ids=("n",),
        parent_baseline_ids=("parent",),
        evaluator_id="independent-evaluator",
        authority_owner_id="external-authority",
    )
    study.verify()
