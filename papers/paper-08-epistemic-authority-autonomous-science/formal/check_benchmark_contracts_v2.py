"""Focused cross-domain benchmark contract checks for candidate ORION Paper 8 V2.

This addendum complements the existing V1 bounded checker and does not establish
novelty or live-agent efficacy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Iterable, Mapping, MutableMapping, Optional, Sequence, Set, Tuple


class Domain(str, Enum):
    REFRAME = "REFRAME"
    SEARCH_STOP = "SEARCH_STOP"
    MAP_MERGE = "MAP_MERGE"
    ASSERT = "ASSERT"
    SELF_MODIFY = "SELF_MODIFY"


class Verdict(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    REJECT = "REJECT"
    CANNOT_CHECK = "CANNOT_CHECK"
    UNAUTHORIZED = "UNAUTHORIZED"


@dataclass(frozen=True)
class AuthorityCertificate:
    certificate_id: str
    issuer: str
    domain: Domain
    scope: FrozenSet[str]
    evidence_ids: FrozenSet[str]
    parent_ids: FrozenSet[str] = frozenset()
    epoch: int = 0


@dataclass(frozen=True)
class AuthorizationRequest:
    action_id: str
    domain: Domain
    target: str
    required_hard: FrozenSet[str]
    satisfied: FrozenSet[str]
    active_defeaters: FrozenSet[str] = frozenset()
    unknown_obligations: FrozenSet[str] = frozenset()


def coercion_path_exists(
    source: Domain,
    target: Domain,
    coercions: Iterable[Tuple[Domain, Domain]],
) -> bool:
    """Return whether registered coercions contain a composable path."""

    if source == target:
        return True
    edges = tuple(coercions)
    frontier = [source]
    seen = {source}
    while frontier:
        current = frontier.pop()
        for left, right in edges:
            if left == current and right not in seen:
                if right == target:
                    return True
                seen.add(right)
                frontier.append(right)
    return False


@dataclass
class AuthoritySystem:
    certificates: Dict[str, AuthorityCertificate]
    trusted_issuers: FrozenSet[str]
    coercions: FrozenSet[Tuple[Domain, Domain]]
    revoked: Set[str]

    def coercion_path_exists(self, source: Domain, target: Domain) -> bool:
        return coercion_path_exists(source, target, self.coercions)

    def _certificate_live(self, certificate_id: str, stack: Optional[Set[str]] = None) -> bool:
        if certificate_id in self.revoked:
            return False
        certificate = self.certificates.get(certificate_id)
        if certificate is None:
            return False
        if not certificate.parent_ids:
            return certificate.issuer in self.trusted_issuers
        stack = set() if stack is None else set(stack)
        if certificate_id in stack:
            return False
        stack.add(certificate_id)
        return all(self._certificate_live(parent_id, stack) for parent_id in certificate.parent_ids)

    def authorize(self, request: AuthorizationRequest, certificate_id: str) -> Verdict:
        if request.active_defeaters:
            return Verdict.REJECT
        missing = request.required_hard - request.satisfied
        if request.unknown_obligations.intersection(missing):
            return Verdict.CANNOT_CHECK
        if missing:
            return Verdict.UNAUTHORIZED
        certificate = self.certificates.get(certificate_id)
        if certificate is None or not self._certificate_live(certificate_id):
            return Verdict.UNAUTHORIZED
        if request.target not in certificate.scope:
            return Verdict.UNAUTHORIZED
        if not self.coercion_path_exists(certificate.domain, request.domain):
            return Verdict.UNAUTHORIZED
        return Verdict.AUTHORIZED

    def revoke(self, certificate_id: str) -> Set[str]:
        """Revoke a certificate and every dependency descendant."""
        children: Dict[str, Set[str]] = {}
        for candidate in self.certificates.values():
            for parent in candidate.parent_ids:
                children.setdefault(parent, set()).add(candidate.certificate_id)
        affected = {certificate_id}
        frontier = [certificate_id]
        while frontier:
            current = frontier.pop()
            for child in children.get(current, set()):
                if child not in affected:
                    affected.add(child)
                    frontier.append(child)
        self.revoked.update(affected)
        return affected


def additive_blocker_counterexample(
    threshold: float,
    finite_blocker_penalty: float,
    positive_increment: float = 1.0,
) -> Tuple[int, float]:
    """Find n such that an unbounded additive score passes despite a blocker."""
    if positive_increment <= 0:
        raise ValueError("positive_increment must be positive")
    n = 0
    score = finite_blocker_penalty
    while score < threshold:
        n += 1
        score = finite_blocker_penalty + n * positive_increment
    return n, score


def self_promotion_countermodel(candidate_controls_policy: bool, candidate_controls_evidence: bool) -> bool:
    return candidate_controls_policy and candidate_controls_evidence


P1_P5_EMBEDDINGS: Mapping[str, Mapping[str, object]] = {
    "P1": {
        "domain": Domain.REFRAME,
        "hard_obligations": frozenset({"typed_responsibility", "coordinate_scope", "reopen_plan"}),
    },
    "P2": {
        "domain": Domain.SEARCH_STOP,
        "hard_obligations": frozenset({"route_task_separation", "coverage_discharge"}),
    },
    "P3": {
        "domain": Domain.MAP_MERGE,
        "hard_obligations": frozenset({"referent_compatibility", "measurement_compatibility", "recoverability"}),
    },
    "P4": {
        "domain": Domain.ASSERT,
        "hard_obligations": frozenset({"content_bound_evidence", "independent_check", "protected_evaluator"}),
    },
    "P5": {
        "domain": Domain.SELF_MODIFY,
        "hard_obligations": frozenset({"replay", "fresh_transfer", "protected_assurance", "external_promotion"}),
    },
}


def embedding_is_typed() -> bool:
    domains = {row["domain"] for row in P1_P5_EMBEDDINGS.values()}
    return domains == set(Domain) and all(row["hard_obligations"] for row in P1_P5_EMBEDDINGS.values())


def evaluate_authority_case(case: Mapping[str, object]) -> Verdict:
    """Evaluate a frozen hostile case under the typed reference calculus."""
    domain = Domain(str(case["domain"]))
    source_domain = Domain(str(case.get("source_signal_domain", case["domain"])))
    hard = frozenset(str(item) for item in case.get("hard_obligations", []))
    satisfied = frozenset(str(item) for item in case.get("satisfied", []))
    unknown = frozenset(str(item) for item in case.get("unknown_obligations", []))
    defeaters = frozenset(str(item) for item in case.get("defeaters", []))
    coercions = {
        (Domain(str(left)), Domain(str(right)))
        for left, right in case.get("registered_coercions", [])
    }

    if defeaters:
        return Verdict.REJECT
    missing = hard - satisfied
    if missing.intersection(unknown):
        return Verdict.CANNOT_CHECK
    if missing:
        return Verdict.UNAUTHORIZED
    if not coercion_path_exists(source_domain, domain, coercions):
        return Verdict.UNAUTHORIZED
    return Verdict.AUTHORIZED


def validate_authority_case(case: Mapping[str, object]) -> Tuple[bool, str]:
    required = {
        "id",
        "domain",
        "action",
        "hard_obligations",
        "satisfied",
        "defeaters",
        "source_signal_domain",
        "expected_verdict",
        "pair_id",
        "clean_authorized",
    }
    missing = required - set(case)
    if missing:
        return False, f"missing fields: {sorted(missing)}"
    try:
        Domain(str(case["domain"]))
        Domain(str(case["source_signal_domain"]))
        expected = Verdict(str(case["expected_verdict"]))
    except ValueError as exc:
        return False, str(exc)
    for field in ("hard_obligations", "satisfied", "defeaters"):
        if not isinstance(case[field], list) or not all(isinstance(item, str) for item in case[field]):
            return False, f"{field} must be a string list"
    if "unknown_obligations" in case and not isinstance(case["unknown_obligations"], list):
        return False, "unknown_obligations must be a list"
    predicted = evaluate_authority_case(case)
    if predicted != expected:
        return False, f"verdict mismatch: evaluator={predicted.value}, expected={expected.value}"
    if bool(case["clean_authorized"]) != (expected == Verdict.AUTHORIZED):
        return False, "clean_authorized must agree with AUTHORIZED terminal"
    return True, "ok"


def run_checks() -> dict:
    results: MutableMapping[str, object] = {}

    assert_root = AuthorityCertificate(
        "assert-root", "host", Domain.ASSERT, frozenset({"claim-1"}), frozenset({"e1"})
    )
    assert_child = AuthorityCertificate(
        "assert-child", "checker", Domain.ASSERT, frozenset({"claim-1"}), frozenset({"e2"}), frozenset({"assert-root"})
    )
    search_root = AuthorityCertificate(
        "search-root", "host", Domain.SEARCH_STOP, frozenset({"route-1"}), frozenset({"s1"})
    )
    system = AuthoritySystem(
        certificates={c.certificate_id: c for c in (assert_root, assert_child, search_root)},
        trusted_issuers=frozenset({"host"}),
        coercions=frozenset(),
        revoked=set(),
    )

    assert_request = AuthorizationRequest(
        "a1",
        Domain.ASSERT,
        "claim-1",
        frozenset({"support", "independent_check"}),
        frozenset({"support", "independent_check"}),
    )
    reframe_request = AuthorizationRequest(
        "a2", Domain.REFRAME, "claim-1", frozenset({"diagnosis"}), frozenset({"diagnosis"})
    )
    results["P8.T1.same_domain_authorization"] = system.authorize(assert_request, "assert-child") == Verdict.AUTHORIZED
    results["P8.T1.cross_domain_laundering_blocked"] = system.authorize(reframe_request, "assert-child") == Verdict.UNAUTHORIZED

    n, score = additive_blocker_counterexample(threshold=10.0, finite_blocker_penalty=-100.0, positive_increment=1.0)
    results["P8.T2.additive_blocker_counterexample"] = n == 110 and score >= 10.0

    before_revoke = system.authorize(assert_request, "assert-child") == Verdict.AUTHORIZED
    revoked = system.revoke("assert-root")
    after_revoke = system.authorize(assert_request, "assert-child") == Verdict.UNAUTHORIZED
    results["P8.T3.dependency_revocation"] = before_revoke and {"assert-root", "assert-child"}.issubset(revoked) and after_revoke
    results["P8.T3.unrelated_preservation"] = "search-root" not in revoked

    unknown_request = AuthorizationRequest(
        "a3",
        Domain.ASSERT,
        "claim-1",
        frozenset({"support", "independent_check"}),
        frozenset({"support"}),
        unknown_obligations=frozenset({"independent_check"}),
    )
    # Use the still-live root only to isolate the missing-knowledge terminal.
    fresh_system = AuthoritySystem(
        certificates={"assert-root": assert_root},
        trusted_issuers=frozenset({"host"}),
        coercions=frozenset(),
        revoked=set(),
    )
    results["P8.CANNOT_CHECK.unknown_hard_obligation"] = fresh_system.authorize(unknown_request, "assert-root") == Verdict.CANNOT_CHECK

    defeated_request = AuthorizationRequest(
        "a4",
        Domain.ASSERT,
        "claim-1",
        frozenset({"support"}),
        frozenset({"support"}),
        active_defeaters=frozenset({"content_substitution"}),
    )
    results["P8.REJECT.active_defeater"] = fresh_system.authorize(defeated_request, "assert-root") == Verdict.REJECT

    results["P8.T4.self_promotion_countermodel"] = self_promotion_countermodel(True, True)
    results["P8.T5.domain_gate_embedding"] = embedding_is_typed()

    results["all_passed"] = all(bool(value) for value in results.values())
    return dict(results)


if __name__ == "__main__":
    import json

    print(json.dumps(run_checks(), indent=2, sort_keys=True))
