"""Executable development packet for the #285 V1 freeze fibre."""

from __future__ import annotations

from orion.core.search import SearchRouteKind
from orion.development.protocol import (
    BasisChallenge,
    DevelopmentAtom,
    DevelopmentImpact,
    DevelopmentPacket,
    assert_ready_to_implement,
)
from orion.engine.operators.saturate import SaturationAssessment, SaturationStatus

ADOPTION_BOUNDARY = "V2_ADDITIVE"

PACKET_ID = "issue-285-global-positive-certificate-v1"


def build_packet() -> DevelopmentPacket:
    covered = tuple(kind.value for kind in SearchRouteKind)
    packet = DevelopmentPacket(
        task_id=PACKET_ID,
        impact=DevelopmentImpact.HIGH,
        atoms=(
            DevelopmentAtom(
                "GP-A1",
                "Freeze a heterogeneous dimension schema that cannot be reduced to one mean score.",
            ),
            DevelopmentAtom(
                "GP-A2",
                "Freeze at least four task-family slots with split identities before candidate outcomes.",
            ),
            DevelopmentAtom(
                "GP-A3",
                "Admit a candidate only when every frozen dimension satisfies non-inferiority or safety.",
            ),
            DevelopmentAtom(
                "GP-A4",
                "Reject scalar compensation, dropped failed families, and missing CANNOT_CHECK dimensions.",
            ),
            DevelopmentAtom(
                "GP-A5",
                "Provide baseline stubs the certificate can score against once outcomes exist.",
            ),
        ),
        saturation=SaturationAssessment(
            status=SaturationStatus.BOUNDED_SATURATED,
            semantic_flat_rounds=2,
            search_universe_flat_rounds=2,
            formulation_flat_rounds=2,
            covered_route_kind_ids=covered,
            missing_route_kind_ids=(),
            reasons=(),
        ),
        basis_challenge=BasisChallenge(
            challenge_id="GP-SAT-1",
            saturation_could_be_false_if=(
                "a continual optimizer already performs non-compensatory protected Pareto admission with negative history",
                "worst-family non-regression is already the primary authority rather than a reporting extra",
            ),
            potentially_missing_parent_domains=(
                "hard-constraint multi-objective certification",
                "clinical-style co-primary non-inferiority trials",
            ),
            prior_miss_hypotheses=(
                "searching only ORION vocabulary would miss SPI and scalarization as the actual parent mechanisms",
                "Pareto archive papers can look like a solution while remaining domain-specific admission-free",
            ),
            reopen_triggers=(
                "nearest work implements the residual composition",
                "a bound multi-domain stream lands on main",
                "issue 209 closes; still does not authorize issue 210",
            ),
        ),
        implementation_hypothesis=(
            "Admission is a fail-closed conjunction over frozen dimensions; "
            "family means and retuned margins cannot authorize."
        ),
    )
    assert_ready_to_implement(packet)
    return packet
