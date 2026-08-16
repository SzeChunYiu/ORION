import pytest

from orion.self_orion.rakl_donor_gate import (
    RAKL_DONOR_COMMIT,
    RaklDonorAudit,
    RaklDonorCandidate,
    RaklDonorDisposition,
    RaklDonorRouteReceipt,
    RaklDonorRouteVerdict,
    RaklDonorSearchRoute,
    assess_rakl_donor_audit,
)


def _receipts(*, omit=None, blocked=None):
    omit = set(omit or ())
    blocked = set(blocked or ())
    rows = []
    for route in RaklDonorSearchRoute:
        if route in omit:
            continue
        verdict = (
            RaklDonorRouteVerdict.BLOCKED
            if route in blocked
            else RaklDonorRouteVerdict.COMPLETE
        )
        rows.append(
            RaklDonorRouteReceipt(
                route=route,
                verdict=verdict,
                scope=f"audit {route.value.lower()}",
                evidence_ids=(f"e:{route.value.lower()}",),
                blocker="provider unavailable" if verdict is RaklDonorRouteVerdict.BLOCKED else "",
            )
        )
    return tuple(rows)


def _candidate(disposition):
    return RaklDonorCandidate(
        donor_id="rakl:generator-transport",
        source_paths=("src/rakl/generator_transport.py", "tests/test_generator_transport.py"),
        disposition=disposition,
        evidence_ids=("e:generator-transport",),
        rationale_or_trigger="target-specific comparison completed",
    )


def test_complete_audit_with_only_rejected_or_deferred_donors_can_license_invention_candidate():
    audit = RaklDonorAudit(
        audit_id="audit:1",
        target_signature="new target operation",
        rakl_commit=RAKL_DONOR_COMMIT,
        route_receipts=_receipts(),
        candidates=(
            _candidate(RaklDonorDisposition.REJECT_WITH_REASON),
            RaklDonorCandidate(
                donor_id="rakl:route-health",
                source_paths=("src/rakl/route_family_health.py",),
                disposition=RaklDonorDisposition.DEFER_WITH_TRIGGER,
                evidence_ids=("e:route-health",),
                rationale_or_trigger="activate only after three same-route longitudinal episodes exist",
            ),
        ),
    )
    report = assess_rakl_donor_audit(audit)
    assert report.admissible
    assert report.licenses_invention_candidate
    assert not report.invention_preempted_by_reuse
    assert not report.grants_invention_authority


def test_exact_or_reconstructable_donor_preempts_parallel_invention():
    for disposition in (
        RaklDonorDisposition.EXACT_REUSE,
        RaklDonorDisposition.RECONSTRUCTED,
    ):
        audit = RaklDonorAudit(
            audit_id=f"audit:{disposition.value}",
            target_signature="target operation",
            rakl_commit=RAKL_DONOR_COMMIT,
            route_receipts=_receipts(),
            candidates=(_candidate(disposition),),
        )
        report = assess_rakl_donor_audit(audit)
        assert report.admissible
        assert report.invention_preempted_by_reuse
        assert report.reusable_donor_ids == ("rakl:generator-transport",)
        assert not report.licenses_invention_candidate


def test_missing_route_or_open_candidate_makes_audit_inadmissible():
    audit = RaklDonorAudit(
        audit_id="audit:open",
        target_signature="target operation",
        rakl_commit=RAKL_DONOR_COMMIT,
        route_receipts=_receipts(omit={RaklDonorSearchRoute.TESTS}),
        candidates=(_candidate(RaklDonorDisposition.OPEN),),
    )
    report = assess_rakl_donor_audit(audit)
    assert not report.admissible
    assert report.missing_routes == (RaklDonorSearchRoute.TESTS,)
    assert report.undispositioned_donor_ids == ("rakl:generator-transport",)


def test_blocked_route_is_visible_but_is_an_honest_bounded_terminal():
    audit = RaklDonorAudit(
        audit_id="audit:blocked",
        target_signature="target operation",
        rakl_commit=RAKL_DONOR_COMMIT,
        route_receipts=_receipts(blocked={RaklDonorSearchRoute.ENGINEERING_SUBSTRATE}),
        candidates=(),
    )
    report = assess_rakl_donor_audit(audit)
    assert report.admissible
    assert report.blocked_routes == (RaklDonorSearchRoute.ENGINEERING_SUBSTRATE,)
    assert report.licenses_invention_candidate


def test_wrong_rakl_revision_is_not_an_admissible_donor_audit():
    audit = RaklDonorAudit(
        audit_id="audit:stale",
        target_signature="target operation",
        rakl_commit="a" * 40,
        route_receipts=_receipts(),
        candidates=(),
    )
    report = assess_rakl_donor_audit(audit)
    assert not report.admissible
    assert "rakl_donor_commit_mismatch" in report.reasons


def test_blocked_route_requires_explicit_blocker():
    with pytest.raises(ValueError):
        RaklDonorRouteReceipt(
            route=RaklDonorSearchRoute.TESTS,
            verdict=RaklDonorRouteVerdict.BLOCKED,
            scope="tests",
            evidence_ids=("e:tests",),
        )
