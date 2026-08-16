from dataclasses import replace

import pytest

from orion.kernel.authority_state import (
    AuthorityObjectKind,
    AuthorityObjectStatus,
    AuthorityRegistration,
    AuthorityState,
    AuthorityStatusEvent,
    SupportState,
    append_authority_status,
)
from orion.kernel.support import (
    DependencyStatus,
    DependencyStatusEvent,
    SupportSet,
    SupportVerdict,
)


def _registration(kind=AuthorityObjectKind.EVALUATOR, registration_id="evaluator:v1"):
    return AuthorityRegistration(
        registration_id=registration_id,
        kind=kind,
        artifact_hash="a" * 64,
        epoch_id="epoch:1",
        metadata_hash="b" * 64,
        public_key_hex="c" * 64 if kind in {AuthorityObjectKind.EVALUATOR, AuthorityObjectKind.KEY} else "",
    )


def _event(registration_id="evaluator:v1", status=AuthorityObjectStatus.LIVE, observed_at=1, event_id="event:1"):
    return AuthorityStatusEvent(event_id, registration_id, status, observed_at, "status observation")


def test_registration_commitment_binds_kind_artifact_epoch_metadata_and_key():
    base = _registration()
    assert base.commitment != replace(base, artifact_hash="d" * 64).commitment
    assert base.commitment != replace(base, epoch_id="epoch:2").commitment
    assert base.commitment != replace(base, public_key_hex="e" * 64).commitment


def test_evaluator_and_key_require_public_key_but_policy_and_root_forbid_it():
    with pytest.raises(ValueError):
        AuthorityRegistration("e", AuthorityObjectKind.EVALUATOR, "a" * 64, "epoch", "b" * 64)
    with pytest.raises(ValueError):
        AuthorityRegistration("p", AuthorityObjectKind.POLICY, "a" * 64, "epoch", "b" * 64, "c" * 64)


def test_authority_revision_changes_append_only_with_status_history_and_logical_time():
    registration = _registration()
    state = AuthorityState((registration,), (_event(),), 1)
    later_history = append_authority_status(
        state.status_history,
        _event(status=AuthorityObjectStatus.REVOKED, observed_at=2, event_id="event:2"),
    )
    later = AuthorityState((registration,), later_history, 2)
    assert state.revision != later.revision
    assert state.current_status(registration.registration_id) is AuthorityObjectStatus.LIVE
    assert later.current_status(registration.registration_id) is AuthorityObjectStatus.REVOKED
    assert later.live_registration(registration.registration_id) is None


def test_status_at_explicit_logical_time_does_not_read_future_event():
    registration = _registration()
    state = AuthorityState(
        (registration,),
        (
            _event(),
            _event(status=AuthorityObjectStatus.REVOKED, observed_at=10, event_id="event:10"),
        ),
        5,
    )
    assert state.current_status(registration.registration_id) is AuthorityObjectStatus.LIVE


def test_unknown_registration_status_is_unknown_and_never_live():
    registration = _registration()
    state = AuthorityState((registration,), (), 0)
    assert state.current_status(registration.registration_id) is AuthorityObjectStatus.UNKNOWN
    assert state.live_registration(registration.registration_id) is None
    assert state.registration("missing") is None


def test_status_history_cannot_reference_unknown_registration_or_rewind():
    registration = _registration()
    with pytest.raises(ValueError):
        AuthorityState((registration,), (_event(registration_id="missing"),), 1)
    history = (_event(observed_at=5),)
    with pytest.raises(ValueError):
        append_authority_status(history, _event(observed_at=4, event_id="older"))
    with pytest.raises(ValueError):
        append_authority_status(history, _event(observed_at=6, event_id="event:1"))


def test_support_revision_and_dnf_evaluation_are_separate_from_authority_revision():
    support_sets = (
        SupportSet("primary", ("dep:a", "dep:b")),
        SupportSet("alternate", ("dep:c",)),
    )
    history = (
        DependencyStatusEvent("a", "dep:a", DependencyStatus.REVOKED, 1, "revoked"),
        DependencyStatusEvent("b", "dep:b", DependencyStatus.LIVE, 1, "live"),
        DependencyStatusEvent("c", "dep:c", DependencyStatus.LIVE, 1, "live"),
    )
    state = SupportState(support_sets, history, 1)
    assert state.evaluation.verdict is SupportVerdict.PASS
    assert state.evaluation.live_support_set_ids == ("alternate",)
    changed = SupportState(
        support_sets,
        (*history, DependencyStatusEvent("c2", "dep:c", DependencyStatus.REVOKED, 2, "revoked")),
        2,
    )
    assert state.revision != changed.revision
    assert changed.evaluation.verdict is SupportVerdict.FAIL


def test_unknown_support_dependency_yields_cannot_check_not_fail():
    state = SupportState((SupportSet("primary", ("missing",)),), (), 0)
    assert state.evaluation.verdict is SupportVerdict.CANNOT_CHECK


def test_authority_state_requires_unique_registration_and_event_ids():
    registration = _registration()
    with pytest.raises(ValueError):
        AuthorityState((registration, registration), (), 0)
    with pytest.raises(ValueError):
        AuthorityState((registration,), (_event(), _event()), 1)
