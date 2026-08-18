"""P6 hostile checks: root-inclusive reopening and protected preservation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

from .common import ReviewResult, Status


REVIEWED_SNAPSHOT = "999abd4899f3fed906ba024ae8ecd775a69b6560"


@dataclass(frozen=True)
class Graph:
    nodes: frozenset[str]
    edges: frozenset[tuple[str, str]]

    def strict_descendants(self, starts: Iterable[str]) -> frozenset[str]:
        roots = frozenset(starts)
        seen = set(roots)
        pending = list(roots)
        while pending:
            source = pending.pop()
            for left, right in self.edges:
                if left == source and right not in seen:
                    seen.add(right)
                    pending.append(right)
        return frozenset(seen - set(roots))

    def affected_closure(self, starts: Iterable[str]) -> frozenset[str]:
        roots = frozenset(starts)
        return roots | self.strict_descendants(roots)


@dataclass(frozen=True)
class PreservationCertificate:
    node: str
    changed: frozenset[str]
    issuer: str
    evidence_ids: frozenset[str]
    valid: bool


def snapshot_operator(
    graph: Graph,
    changed: frozenset[str],
    certified: frozenset[str],
) -> frozenset[str]:
    """Model the reviewed strict-descendant operator."""

    return graph.strict_descendants(changed) & certified


def corrected_operator(
    graph: Graph,
    changed: frozenset[str],
    certified: frozenset[str],
    certificates: Iterable[PreservationCertificate] = (),
    protected_issuers: frozenset[str] = frozenset({"protected-reviewer"}),
) -> frozenset[str]:
    """Reopen changed certified roots plus descendants, minus valid downstream proofs."""

    affected = graph.affected_closure(changed) & certified
    preserved = {
        certificate.node
        for certificate in certificates
        if certificate.valid
        and certificate.node in affected
        and certificate.node not in changed
        and certificate.changed == changed
        and bool(certificate.evidence_ids)
        and certificate.issuer in protected_issuers
    }
    return frozenset(affected - preserved)


def check_directly_changed_certified_root() -> ReviewResult:
    graph = Graph(frozenset({"q"}), frozenset())
    changed = frozenset({"q"})
    certified = frozenset({"q"})
    snapshot = snapshot_operator(graph, changed, certified)
    corrected = corrected_operator(graph, changed, certified)
    if snapshot or corrected != frozenset({"q"}):
        return ReviewResult(
            "P6",
            "H1 directly changed certified roots",
            Status.FAIL,
            1,
            "The hostile fixture did not reproduce the reviewed root-omission gap.",
            REVIEWED_SNAPSHOT,
            {"snapshot": sorted(snapshot), "corrected": sorted(corrected)},
        )
    return ReviewResult(
        "P6",
        "H1 directly changed certified roots",
        Status.COUNTEREXAMPLE_CONFIRMED,
        1,
        "Strict descendants omit a changed certified root with no outgoing edge; a root-inclusive affected closure reopens it.",
        REVIEWED_SNAPSHOT,
        {"changed": ["q"], "certified": ["q"], "snapshot_reopen": [], "corrected_reopen": ["q"]},
        "Exact one-node counterexample to Definition 8/Theorems 1--2 when X may contain Q.",
    )


def check_preservation_certificate_matrix() -> ReviewResult:
    graph = Graph(
        frozenset({"x", "dependent"}),
        frozenset({("x", "dependent")}),
    )
    changed = frozenset({"x"})
    certified = frozenset({"x", "dependent"})
    cases = 0
    for node, issuer, has_evidence, valid, matching_change in product(
        ("x", "dependent"),
        ("protected-reviewer", "candidate"),
        (False, True),
        (False, True),
        (False, True),
    ):
        certificate = PreservationCertificate(
            node=node,
            changed=changed if matching_change else frozenset({"other"}),
            issuer=issuer,
            evidence_ids=frozenset({"ev"}) if has_evidence else frozenset(),
            valid=valid,
        )
        reopened = corrected_operator(graph, changed, certified, (certificate,))
        should_preserve_dependent = (
            node == "dependent"
            and issuer == "protected-reviewer"
            and has_evidence
            and valid
            and matching_change
        )
        expected = frozenset({"x"}) if should_preserve_dependent else frozenset({"x", "dependent"})
        cases += 1
        if reopened != expected:
            return ReviewResult(
                "P6",
                "H2 protected preservation certificates",
                Status.FAIL,
                cases,
                "A hostile preservation-certificate case produced the wrong fail-closed decision.",
                REVIEWED_SNAPSHOT,
                {"certificate": certificate.__dict__, "actual": sorted(reopened), "expected": sorted(expected)},
            )
    return ReviewResult(
        "P6",
        "H2 protected preservation certificates",
        Status.PASS,
        cases,
        "Only a valid, evidence-bearing, protected certificate for a downstream node preserved certification; changed roots and forged/stale certificates reopened.",
        REVIEWED_SNAPSHOT,
    )


def compose_residual_obligations(
    initial: frozenset[str],
    emitted: frozenset[str],
    requested_discharges: frozenset[str],
    authorized_discharges: frozenset[str],
    later_success: bool,
) -> frozenset[str]:
    del later_success  # success is deliberately not an authorization rule
    active = set(initial | emitted)
    active.difference_update(requested_discharges & authorized_discharges)
    return frozenset(active)


def check_residual_obligation_non_erasure() -> ReviewResult:
    fixtures = (
        (frozenset(), frozenset({"independent-check"}), frozenset(), frozenset(), True, frozenset({"independent-check"})),
        (frozenset(), frozenset({"independent-check"}), frozenset({"independent-check"}), frozenset(), True, frozenset({"independent-check"})),
        (frozenset(), frozenset({"independent-check"}), frozenset({"independent-check"}), frozenset({"independent-check"}), True, frozenset()),
        (frozenset({"coverage"}), frozenset(), frozenset(), frozenset(), False, frozenset({"coverage"})),
    )
    for index, fixture in enumerate(fixtures, start=1):
        actual = compose_residual_obligations(*fixture[:-1])
        if actual != fixture[-1]:
            return ReviewResult(
                "P6",
                "H3 residual-obligation non-erasure",
                Status.FAIL,
                index,
                "Residual-obligation composition produced an unexpected result.",
                REVIEWED_SNAPSHOT,
                {"actual": sorted(actual), "expected": sorted(fixture[-1])},
            )
    return ReviewResult(
        "P6",
        "H3 residual-obligation non-erasure",
        Status.PASS,
        len(fixtures),
        "Later success and an unauthorized discharge request did not erase a hard residual obligation; an authorized discharge did.",
        REVIEWED_SNAPSHOT,
    )


def run_checks() -> list[ReviewResult]:
    return [
        check_directly_changed_certified_root(),
        check_preservation_certificate_matrix(),
        check_residual_obligation_non_erasure(),
    ]
