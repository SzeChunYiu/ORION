"""P8 hostile checks: typed evidence discharge, coercion composition and revocation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from itertools import product
from typing import Iterable, Mapping

from .common import ReviewResult, Status


REVIEWED_SNAPSHOT = "999abd4899f3fed906ba024ae8ecd775a69b6560"


class Domain(str, Enum):
    REFRAME = "REFRAME"
    SEARCH_STOP = "SEARCH_STOP"
    MAP_MERGE = "MAP_MERGE"
    ASSERT = "ASSERT"
    SELF_MODIFY = "SELF_MODIFY"


class Decision(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Action:
    action_id: str
    domain: Domain
    scope: str
    epoch: int
    capability_present: bool = True


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    domain: Domain
    kind: str
    scope: str
    epoch: int


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    domain: Domain
    kind: str
    scope: str
    epoch: int
    available: bool = True
    valid: bool = True


@dataclass(frozen=True)
class Satisfaction:
    obligation_id: str
    evidence_id: str


@dataclass(frozen=True)
class Coercion:
    coercion_id: str
    source_domain: Domain
    target_domain: Domain
    source_kind: str
    target_kind: str
    scope_map: frozenset[tuple[str, str]]
    protected_issuer: str
    preserves_epoch: bool = True
    active: bool = True


@dataclass(frozen=True)
class Context:
    protected_roots: frozenset[str]
    coercions: tuple[Coercion, ...] = ()


def coercion_matches(evidence: Evidence, obligation: Obligation, context: Context) -> bool:
    return any(
        coercion.active
        and coercion.protected_issuer in context.protected_roots
        and coercion.source_domain == evidence.domain
        and coercion.target_domain == obligation.domain
        and coercion.source_kind == evidence.kind
        and coercion.target_kind == obligation.kind
        and (evidence.scope, obligation.scope) in coercion.scope_map
        and (not coercion.preserves_epoch or evidence.epoch == obligation.epoch)
        for coercion in context.coercions
    )


def evidence_discharges(evidence: Evidence, obligation: Obligation, context: Context) -> bool:
    if not evidence.available or not evidence.valid:
        return False
    same_type = (
        evidence.domain == obligation.domain
        and evidence.kind == obligation.kind
        and evidence.scope == obligation.scope
        and evidence.epoch == obligation.epoch
    )
    return same_type or coercion_matches(evidence, obligation, context)


def authorize(
    action: Action,
    obligations: Iterable[Obligation],
    evidence: Iterable[Evidence],
    satisfactions: Iterable[Satisfaction],
    *,
    issuer: str,
    context: Context,
    active_blocker: bool = False,
) -> Decision:
    if not action.capability_present or issuer not in context.protected_roots:
        return Decision.DENIED
    if active_blocker:
        return Decision.DENIED
    relevant = tuple(obligations)
    if any(
        obligation.domain != action.domain
        or obligation.scope != action.scope
        or obligation.epoch != action.epoch
        for obligation in relevant
    ):
        return Decision.DENIED
    evidence_by_id = {item.evidence_id: item for item in evidence}
    linked: dict[str, list[Evidence]] = {}
    for satisfaction in satisfactions:
        item = evidence_by_id.get(satisfaction.evidence_id)
        if item is not None:
            linked.setdefault(satisfaction.obligation_id, []).append(item)

    unresolved = False
    for obligation in relevant:
        candidates = linked.get(obligation.obligation_id, [])
        if any(evidence_discharges(item, obligation, context) for item in candidates):
            continue
        if not candidates or any(not item.available for item in candidates):
            unresolved = True
        else:
            return Decision.DENIED
    return Decision.CANNOT_CHECK if unresolved else Decision.AUTHORIZED


def check_evidence_domain_substitution_matrix() -> ReviewResult:
    context = Context(frozenset({"root"}))
    cases = 0
    for target, source in product(tuple(Domain), repeat=2):
        action = Action(f"act-{target.value}", target, "object", 7)
        obligation = Obligation("gate", target, "gate", "object", 7)
        item = Evidence("ev", source, "gate", "object", 7)
        decision = authorize(
            action,
            (obligation,),
            (item,),
            (Satisfaction("gate", "ev"),),
            issuer="root",
            context=context,
        )
        expected = Decision.AUTHORIZED if source == target else Decision.DENIED
        cases += 1
        if decision != expected:
            return ReviewResult(
                "P8",
                "H1 typed evidence-to-obligation discharge",
                Status.FAIL,
                cases,
                "A domain substitution produced an unexpected decision.",
                REVIEWED_SNAPSHOT,
                {"source": source.value, "target": target.value, "decision": decision.value},
            )
    return ReviewResult(
        "P8",
        "H1 typed evidence-to-obligation discharge",
        Status.PASS,
        cases,
        "Every one of the 20 foreign-domain evidence substitutions was denied and all five same-domain cases authorized.",
        REVIEWED_SNAPSHOT,
        scope="Full five-by-five evidence/obligation matrix; this is stricter than typing only the authority-bearing judgment.",
    )


def domain_path_reachable(
    source: Domain,
    target: Domain,
    coercions: Iterable[Coercion],
) -> bool:
    seen = {source}
    pending = [source]
    while pending:
        current = pending.pop()
        if current == target:
            return True
        for coercion in coercions:
            if coercion.active and coercion.source_domain == current and coercion.target_domain not in seen:
                seen.add(coercion.target_domain)
                pending.append(coercion.target_domain)
    return False


def typed_path_reachable(
    source_domain: Domain,
    source_kind: str,
    source_scope: str,
    source_epoch: int,
    target_domain: Domain,
    target_kind: str,
    target_scope: str,
    target_epoch: int,
    coercions: Iterable[Coercion],
    roots: frozenset[str],
) -> bool:
    start = (source_domain, source_kind, source_scope, source_epoch)
    target = (target_domain, target_kind, target_scope, target_epoch)
    seen = {start}
    pending = [start]
    while pending:
        current = pending.pop()
        if current == target:
            return True
        current_domain, current_kind, current_scope, current_epoch = current
        for coercion in coercions:
            if (
                coercion.active
                and coercion.protected_issuer in roots
                and coercion.source_domain == current_domain
                and coercion.source_kind == current_kind
            ):
                for left_scope, right_scope in coercion.scope_map:
                    if left_scope != current_scope:
                        continue
                    next_epoch = current_epoch if coercion.preserves_epoch else target_epoch
                    nxt = (
                        coercion.target_domain,
                        coercion.target_kind,
                        right_scope,
                        next_epoch,
                    )
                    if nxt not in seen:
                        seen.add(nxt)
                        pending.append(nxt)
    return False


def check_scope_incompatible_coercion_path() -> ReviewResult:
    coercions = (
        Coercion(
            "a-to-b",
            Domain.SEARCH_STOP,
            Domain.MAP_MERGE,
            "route-pass",
            "mapping-support",
            frozenset({("claim-A", "map-A")}),
            "root",
        ),
        Coercion(
            "b-to-c",
            Domain.MAP_MERGE,
            Domain.ASSERT,
            "mapping-support",
            "verification",
            frozenset({("map-B", "claim-B")}),
            "root",
        ),
    )
    legacy = domain_path_reachable(Domain.SEARCH_STOP, Domain.ASSERT, coercions)
    corrected = typed_path_reachable(
        Domain.SEARCH_STOP,
        "route-pass",
        "claim-A",
        3,
        Domain.ASSERT,
        "verification",
        "claim-B",
        3,
        coercions,
        frozenset({"root"}),
    )
    if not legacy or corrected:
        return ReviewResult(
            "P8",
            "H2 coercion-path compositionality",
            Status.FAIL,
            1,
            "The scope-incompatible path witness was not reproduced.",
            REVIEWED_SNAPSHOT,
            {"domain_only": legacy, "typed_path": corrected},
        )
    return ReviewResult(
        "P8",
        "H2 coercion-path compositionality",
        Status.COUNTEREXAMPLE_CONFIRMED,
        1,
        "A domain-only path exists even though adjacent coercions have incompatible scope maps; domain reachability alone would authorize an invalid composition.",
        REVIEWED_SNAPSHOT,
        {"first_output_scope": "map-A", "second_input_scope": "map-B"},
    )


@dataclass(frozen=True)
class Derivation:
    derivation_id: str
    evidence_ids: frozenset[str]
    parent_certificates: frozenset[str] = frozenset()


def surviving_certificates(
    derivations: Mapping[str, tuple[Derivation, ...]],
    invalid_evidence: frozenset[str],
) -> frozenset[str]:
    @lru_cache(maxsize=None)
    def valid(certificate: str, stack: tuple[str, ...] = ()) -> bool:
        if certificate in stack:
            return False
        next_stack = (*stack, certificate)
        return any(
            not (derivation.evidence_ids & invalid_evidence)
            and all(valid(parent, next_stack) for parent in derivation.parent_certificates)
            for derivation in derivations.get(certificate, ())
        )

    return frozenset(certificate for certificate in derivations if valid(certificate))


def check_alternative_derivation_revocation() -> ReviewResult:
    derivations = {
        "assert-cert": (
            Derivation("route-A", frozenset({"ev-A"})),
            Derivation("route-B", frozenset({"ev-B"})),
        ),
        "dependent-cert": (
            Derivation("uses-assert", frozenset({"ev-dependent"}), frozenset({"assert-cert"})),
        ),
    }
    after_a = surviving_certificates(derivations, frozenset({"ev-A"}))
    after_both = surviving_certificates(derivations, frozenset({"ev-A", "ev-B"}))
    if after_a != frozenset({"assert-cert", "dependent-cert"}) or after_both:
        return ReviewResult(
            "P8",
            "H3 alternative-derivation revocation",
            Status.FAIL,
            2,
            "OR-derivation revocation produced the wrong surviving set.",
            REVIEWED_SNAPSHOT,
            {"after_A": sorted(after_a), "after_both": sorted(after_both)},
        )
    return ReviewResult(
        "P8",
        "H3 alternative-derivation revocation",
        Status.PASS,
        2,
        "Revoking one evidence route preserved the certificate and its dependent through an independent derivation; revoking both routes removed both.",
        REVIEWED_SNAPSHOT,
        scope="Finite AND/OR derivation graph; a simple descendant graph cannot express this distinction by itself.",
    )


def check_terminal_separation() -> ReviewResult:
    context = Context(frozenset({"root"}))
    action = Action("assert", Domain.ASSERT, "claim", 1)
    obligation = Obligation("independent", Domain.ASSERT, "verification", "claim", 1)
    missing = authorize(action, (obligation,), (), (), issuer="root", context=context)
    wrong = Evidence("wrong", Domain.SEARCH_STOP, "verification", "claim", 1)
    denied = authorize(
        action,
        (obligation,),
        (wrong,),
        (Satisfaction("independent", "wrong"),),
        issuer="root",
        context=context,
    )
    blocked = authorize(action, (), (), (), issuer="root", context=context, active_blocker=True)
    mismatched_obligation = Obligation(
        "foreign-contract", Domain.SEARCH_STOP, "verification", "claim", 1
    )
    malformed = authorize(
        action,
        (mismatched_obligation,),
        (),
        (),
        issuer="root",
        context=context,
    )
    clean = Evidence("clean", Domain.ASSERT, "verification", "claim", 1)
    authorized = authorize(
        action,
        (obligation,),
        (clean,),
        (Satisfaction("independent", "clean"),),
        issuer="root",
        context=context,
    )
    actual = (missing, denied, blocked, malformed, authorized)
    expected = (
        Decision.CANNOT_CHECK,
        Decision.DENIED,
        Decision.DENIED,
        Decision.DENIED,
        Decision.AUTHORIZED,
    )
    if actual != expected:
        return ReviewResult(
            "P8",
            "H4 terminal separation",
            Status.FAIL,
            len(actual),
            "Authorization terminals were collapsed or misclassified.",
            REVIEWED_SNAPSHOT,
            {"actual": [item.value for item in actual]},
        )
    return ReviewResult(
        "P8",
        "H4 terminal separation",
        Status.PASS,
        len(actual),
        "Missing evidence yielded CANNOT_CHECK; mismatched evidence, malformed obligation contracts and blockers yielded DENIED; a clean typed case authorized.",
        REVIEWED_SNAPSHOT,
    )


def run_checks() -> list[ReviewResult]:
    return [
        check_evidence_domain_substitution_matrix(),
        check_scope_incompatible_coercion_path(),
        check_alternative_derivation_revocation(),
        check_terminal_separation(),
    ]
