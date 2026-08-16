from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


RAKL_DONOR_COMMIT = "70f5f7c4a6771ffd1158765b42ac9f8aee8a270f"


class RaklDonorSearchRoute(str, Enum):
    """Independent RAKL donor surfaces that must be checked before invention."""

    PUBLIC_API = "PUBLIC_API"
    SOURCE_TREE = "SOURCE_TREE"
    TESTS = "TESTS"
    RESEARCH_RESULTS = "RESEARCH_RESULTS"
    ENGINEERING_SUBSTRATE = "ENGINEERING_SUBSTRATE"


_REQUIRED_ROUTES = frozenset(RaklDonorSearchRoute)


class RaklDonorRouteVerdict(str, Enum):
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class RaklDonorDisposition(str, Enum):
    """What ORION decided after comparing one RAKL donor with the target need."""

    EXACT_REUSE = "EXACT_REUSE"
    RECONSTRUCTED = "RECONSTRUCTED"
    TESTS_RESULTS_REUSED = "TESTS_RESULTS_REUSED"
    DEFER_WITH_TRIGGER = "DEFER_WITH_TRIGGER"
    REJECT_WITH_REASON = "REJECT_WITH_REASON"
    OPEN = "OPEN"


@dataclass(frozen=True)
class RaklDonorRouteReceipt:
    route: RaklDonorSearchRoute
    verdict: RaklDonorRouteVerdict
    scope: str
    evidence_ids: tuple[str, ...]
    blocker: str = ""

    def __post_init__(self) -> None:
        if not self.scope.strip():
            raise ValueError("RAKL donor route receipt requires a scope")
        if not self.evidence_ids:
            raise ValueError("RAKL donor route receipt requires evidence ids")
        if any(not item.strip() for item in self.evidence_ids):
            raise ValueError("RAKL donor route evidence ids must be non-empty")
        if self.verdict is RaklDonorRouteVerdict.BLOCKED and not self.blocker.strip():
            raise ValueError("blocked RAKL donor route requires a blocker")
        if self.verdict is RaklDonorRouteVerdict.COMPLETE and self.blocker:
            raise ValueError("complete RAKL donor route cannot carry a blocker")


@dataclass(frozen=True)
class RaklDonorCandidate:
    donor_id: str
    source_paths: tuple[str, ...]
    disposition: RaklDonorDisposition
    evidence_ids: tuple[str, ...]
    rationale_or_trigger: str

    def __post_init__(self) -> None:
        if not self.donor_id.strip() or not self.rationale_or_trigger.strip():
            raise ValueError("RAKL donor candidate requires identity and rationale/trigger")
        if not self.source_paths or any(not item.strip() for item in self.source_paths):
            raise ValueError("RAKL donor candidate requires one or more source paths")
        if not self.evidence_ids or any(not item.strip() for item in self.evidence_ids):
            raise ValueError("RAKL donor candidate requires evidence ids")

    @property
    def should_preempt_invention(self) -> bool:
        return self.disposition in {
            RaklDonorDisposition.EXACT_REUSE,
            RaklDonorDisposition.RECONSTRUCTED,
        }


@dataclass(frozen=True)
class RaklDonorAudit:
    """Target-specific, pinned donor search over the frozen RAKL repository."""

    audit_id: str
    target_signature: str
    rakl_commit: str
    route_receipts: tuple[RaklDonorRouteReceipt, ...]
    candidates: tuple[RaklDonorCandidate, ...]

    def __post_init__(self) -> None:
        if not self.audit_id.strip() or not self.target_signature.strip():
            raise ValueError("RAKL donor audit requires audit id and target signature")
        if len(self.rakl_commit) != 40 or any(ch not in "0123456789abcdef" for ch in self.rakl_commit):
            raise ValueError("RAKL donor audit commit must be a 40-character git SHA")


@dataclass(frozen=True)
class RaklDonorAuditReport:
    admissible: bool
    invention_preempted_by_reuse: bool
    reusable_donor_ids: tuple[str, ...]
    undispositioned_donor_ids: tuple[str, ...]
    missing_routes: tuple[RaklDonorSearchRoute, ...]
    blocked_routes: tuple[RaklDonorSearchRoute, ...]
    reasons: tuple[str, ...]

    @property
    def licenses_invention_candidate(self) -> bool:
        return self.admissible and not self.invention_preempted_by_reuse

    @property
    def grants_invention_authority(self) -> bool:
        return False


def assess_rakl_donor_audit(
    audit: RaklDonorAudit,
    *,
    expected_rakl_commit: str = RAKL_DONOR_COMMIT,
) -> RaklDonorAuditReport:
    """Require donor saturation before clean-generation invention.

    The audit is admissible only when all registered donor surfaces were either
    searched or explicitly blocked with evidence, every candidate has a terminal
    disposition, and the audit is pinned to the expected RAKL revision.

    If a surviving donor is marked EXACT_REUSE or RECONSTRUCTED, invention is
    pre-empted: the next action is to reuse/reconstruct that donor rather than
    create a parallel mechanic. TESTS_RESULTS_REUSED, DEFER_WITH_TRIGGER and
    REJECT_WITH_REASON are terminal dispositions that do not by themselves block
    a genuinely new candidate.
    """

    reasons: list[str] = []
    if audit.rakl_commit != expected_rakl_commit:
        reasons.append("rakl_donor_commit_mismatch")

    by_route: dict[RaklDonorSearchRoute, list[RaklDonorRouteReceipt]] = {}
    for receipt in audit.route_receipts:
        by_route.setdefault(receipt.route, []).append(receipt)
    missing_routes = tuple(sorted(_REQUIRED_ROUTES.difference(by_route), key=lambda item: item.value))
    if missing_routes:
        reasons.append("rakl_donor_routes_missing:" + ",".join(item.value for item in missing_routes))
    duplicate_routes = tuple(
        sorted((route for route, receipts in by_route.items() if len(receipts) != 1), key=lambda item: item.value)
    )
    if duplicate_routes:
        reasons.append("rakl_donor_routes_not_uniquely_bound:" + ",".join(item.value for item in duplicate_routes))

    blocked_routes = tuple(
        sorted(
            (
                route
                for route, receipts in by_route.items()
                if len(receipts) == 1 and receipts[0].verdict is RaklDonorRouteVerdict.BLOCKED
            ),
            key=lambda item: item.value,
        )
    )

    donor_ids = [candidate.donor_id for candidate in audit.candidates]
    if len(set(donor_ids)) != len(donor_ids):
        reasons.append("rakl_donor_candidate_identity_collision")
    undispositioned = tuple(
        sorted(
            candidate.donor_id
            for candidate in audit.candidates
            if candidate.disposition is RaklDonorDisposition.OPEN
        )
    )
    if undispositioned:
        reasons.append("rakl_donor_candidates_undispositioned:" + ",".join(undispositioned))

    reusable = tuple(
        sorted(candidate.donor_id for candidate in audit.candidates if candidate.should_preempt_invention)
    )
    if reusable:
        reasons.append("rakl_surviving_donor_available:" + ",".join(reusable))

    # A BLOCKED route is an honest bounded terminal rather than a fabricated
    # complete search. It keeps the audit admissible for *proposal* purposes,
    # but the blocker remains visible in the report and can be treated as a
    # stricter policy failure by callers when the missing surface is material.
    admissibility_reasons = tuple(
        reason
        for reason in reasons
        if not reason.startswith("rakl_surviving_donor_available:")
    )
    admissible = not admissibility_reasons
    return RaklDonorAuditReport(
        admissible=admissible,
        invention_preempted_by_reuse=bool(reusable),
        reusable_donor_ids=reusable,
        undispositioned_donor_ids=undispositioned,
        missing_routes=missing_routes,
        blocked_routes=blocked_routes,
        reasons=tuple(reasons)
        if reasons
        else (
            "all_registered_RAKL_donor_surfaces_checked_and_no_reusable_donor_preempts_invention",
        ),
    )


__all__ = [
    "RAKL_DONOR_COMMIT",
    "RaklDonorAudit",
    "RaklDonorAuditReport",
    "RaklDonorCandidate",
    "RaklDonorDisposition",
    "RaklDonorRouteReceipt",
    "RaklDonorRouteVerdict",
    "RaklDonorSearchRoute",
    "assess_rakl_donor_audit",
]
