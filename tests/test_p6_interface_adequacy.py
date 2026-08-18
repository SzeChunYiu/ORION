from __future__ import annotations

from orion.transfer.v2.interface_adequacy import (
    InterfaceAdequacyStatus,
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)


def check(
    check_id: str,
    scope: str,
    state: InterfaceCheckState,
    *,
    required: bool = True,
):
    return build_interface_check(
        check_id=check_id,
        scope=scope,
        state=state,
        evidence_ids=(f"evidence:{check_id}",),
        required=required,
    )


def test_required_failure_requires_narrow_interface_repair() -> None:
    report = assess_interface_adequacy(
        (
            check("markov", "OBSERVATION", InterfaceCheckState.FAIL),
            check("reconstruction", "REPRESENTATION", InterfaceCheckState.PASS),
        )
    )

    assert report.status is InterfaceAdequacyStatus.REPAIR_REQUIRED
    assert report.failed_scopes == ("OBSERVATION",)
    assert report.permits_broader_revision_consideration is False
    assert report.grants_scientific_authority is False


def test_all_required_checks_pass_is_adequate_but_non_authorizing() -> None:
    report = assess_interface_adequacy(
        (
            check("markov", "OBSERVATION", InterfaceCheckState.PASS),
            check("measurement", "MEASUREMENT", InterfaceCheckState.PASS),
            check("transport", "REPRESENTATION", InterfaceCheckState.PASS),
        )
    )

    assert report.status is InterfaceAdequacyStatus.ADEQUATE
    assert report.failed_scopes == ()
    assert report.unresolved_scopes == ()
    assert report.permits_broader_revision_consideration is True
    assert report.grants_scientific_authority is False


def test_unresolved_required_check_keeps_interface_unresolved() -> None:
    report = assess_interface_adequacy(
        (
            check("markov", "OBSERVATION", InterfaceCheckState.PASS),
            check("latent", "UNCERTAINTY", InterfaceCheckState.UNRESOLVED),
        )
    )

    assert report.status is InterfaceAdequacyStatus.UNRESOLVED
    assert report.unresolved_scopes == ("UNCERTAINTY",)
    assert report.permits_broader_revision_consideration is False


def test_advisory_pass_cannot_compensate_required_failure() -> None:
    report = assess_interface_adequacy(
        (
            check("native", "OBSERVATION", InterfaceCheckState.FAIL),
            check(
                "latent-confidence",
                "UNCERTAINTY",
                InterfaceCheckState.PASS,
                required=False,
            ),
        )
    )

    assert report.status is InterfaceAdequacyStatus.REPAIR_REQUIRED
    assert report.failed_scopes == ("OBSERVATION",)


def test_failure_has_precedence_but_unresolved_coordinates_are_preserved() -> None:
    report = assess_interface_adequacy(
        (
            check("sensor", "MEASUREMENT", InterfaceCheckState.FAIL),
            check("transport", "REPRESENTATION", InterfaceCheckState.UNRESOLVED),
        )
    )

    assert report.status is InterfaceAdequacyStatus.REPAIR_REQUIRED
    assert report.failed_scopes == ("MEASUREMENT",)
    assert report.unresolved_scopes == ("REPRESENTATION",)


def test_duplicate_check_identity_is_rejected() -> None:
    first = check("same", "OBSERVATION", InterfaceCheckState.PASS)
    second = check("same", "OBSERVATION", InterfaceCheckState.PASS)

    try:
        assess_interface_adequacy((first, second))
    except ValueError as exc:
        assert "duplicate interface check" in str(exc)
    else:
        raise AssertionError("duplicate interface check should fail")
