from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from orion.kernel.support import (
    DependencyStatus,
    DependencyStatusEvent,
    SupportReasonCode,
    SupportSet,
    SupportVerdict,
    append_dependency_status,
    evaluate_support,
)


def _event(
    event_id: str,
    dependency_id: str,
    status: DependencyStatus,
    observed_at: int,
) -> DependencyStatusEvent:
    return DependencyStatusEvent(
        event_id=event_id,
        dependency_id=dependency_id,
        status=status,
        observed_at=observed_at,
        reason=f"{dependency_id} became {status.value}",
    )


def test_dependency_statuses_are_explicit_and_frozen() -> None:
    assert {item.value for item in DependencyStatus} == {
        "LIVE",
        "STALE",
        "REVOKED",
        "UNKNOWN",
    }
    event = _event("event:a:live", "a", DependencyStatus.LIVE, 1)

    with pytest.raises(FrozenInstanceError):
        event.status = DependencyStatus.REVOKED  # type: ignore[misc]


def test_one_support_set_is_a_conjunction() -> None:
    support = SupportSet("warrant:ab", ("a", "b"))
    events = (
        _event("event:a:live", "a", DependencyStatus.LIVE, 1),
        _event("event:b:stale", "b", DependencyStatus.STALE, 1),
    )

    report = evaluate_support((support,), events, status_time=1)

    assert report.verdict is SupportVerdict.CANNOT_CHECK
    assert report.live_support_set_ids == ()
    assert report.invalid_support_set_ids == ("warrant:ab",)
    assert report.reasons[0].code is SupportReasonCode.DEPENDENCY_STALE
    assert report.reasons[0].dependency_id == "b"


def test_support_sets_are_alternatives_and_one_live_set_preserves_pass() -> None:
    supports = (
        SupportSet("warrant:ab", ("a", "b")),
        SupportSet("warrant:cd", ("c", "d")),
    )
    history = (
        _event("event:a:live", "a", DependencyStatus.LIVE, 1),
        _event("event:b:live", "b", DependencyStatus.LIVE, 1),
        _event("event:c:live", "c", DependencyStatus.LIVE, 1),
        _event("event:d:live", "d", DependencyStatus.LIVE, 1),
        _event("event:a:revoked", "a", DependencyStatus.REVOKED, 2),
    )

    report = evaluate_support(supports, history, status_time=2)

    assert report.verdict is SupportVerdict.PASS
    assert report.live_support_set_ids == ("warrant:cd",)
    assert report.invalid_support_set_ids == ("warrant:ab",)
    assert any(
        reason.code is SupportReasonCode.DEPENDENCY_REVOKED
        and reason.dependency_id == "a"
        for reason in report.reasons
    )


@pytest.mark.parametrize("status", [DependencyStatus.UNKNOWN, DependencyStatus.STALE])
def test_no_live_set_with_unresolved_dependency_cannot_check(
    status: DependencyStatus,
) -> None:
    report = evaluate_support(
        (SupportSet("warrant:a", ("a",)),),
        (_event(f"event:a:{status.value}", "a", status, 1),),
        status_time=1,
    )

    assert report.verdict is SupportVerdict.CANNOT_CHECK
    assert report.live_support_set_ids == ()
    assert report.invalid_support_set_ids == ("warrant:a",)


def test_missing_dependency_is_typed_unknown_not_failure() -> None:
    report = evaluate_support(
        (SupportSet("warrant:missing", ("not-observed",)),),
        (),
        status_time=4,
    )

    assert report.verdict is SupportVerdict.CANNOT_CHECK
    assert report.reasons[0].code is SupportReasonCode.DEPENDENCY_UNKNOWN
    assert report.reasons[0].status is DependencyStatus.UNKNOWN


def test_all_alternatives_demonstrably_broken_is_fail() -> None:
    supports = (
        SupportSet("warrant:a", ("a",)),
        SupportSet("warrant:bc", ("b", "c")),
    )
    history = (
        _event("event:a:revoked", "a", DependencyStatus.REVOKED, 1),
        _event("event:b:live", "b", DependencyStatus.LIVE, 1),
        _event("event:c:revoked", "c", DependencyStatus.REVOKED, 1),
    )

    report = evaluate_support(supports, history, status_time=1)

    assert report.verdict is SupportVerdict.FAIL
    assert report.live_support_set_ids == ()
    assert report.invalid_support_set_ids == ("warrant:a", "warrant:bc")


def test_status_time_is_explicit_and_future_events_do_not_leak_backward() -> None:
    history = (
        _event("event:a:live", "a", DependencyStatus.LIVE, 1),
        _event("event:a:revoked", "a", DependencyStatus.REVOKED, 3),
    )
    support = (SupportSet("warrant:a", ("a",)),)

    before = evaluate_support(support, history, status_time=2)
    after = evaluate_support(support, history, status_time=3)

    assert before.verdict is SupportVerdict.PASS
    assert after.verdict is SupportVerdict.FAIL
    assert before.status_time == 2
    assert after.status_time == 3


def test_revocation_appends_history_instead_of_deleting_live_observation() -> None:
    live = _event("event:a:live", "a", DependencyStatus.LIVE, 1)
    revoked = _event("event:a:revoked", "a", DependencyStatus.REVOKED, 2)

    history = append_dependency_status((live,), revoked)

    assert history == (live, revoked)
    assert evaluate_support(
        (SupportSet("warrant:a", ("a",)),), history, status_time=1
    ).verdict is SupportVerdict.PASS
    assert evaluate_support(
        (SupportSet("warrant:a", ("a",)),), history, status_time=2
    ).verdict is SupportVerdict.FAIL


def test_duplicate_event_identity_and_backward_dependency_time_are_rejected() -> None:
    live = _event("event:a", "a", DependencyStatus.LIVE, 2)

    with pytest.raises(ValueError, match="event_id"):
        append_dependency_status((live,), _event("event:a", "b", DependencyStatus.LIVE, 3))
    with pytest.raises(ValueError, match="older"):
        append_dependency_status(
            (live,), _event("event:a:older", "a", DependencyStatus.STALE, 1)
        )
