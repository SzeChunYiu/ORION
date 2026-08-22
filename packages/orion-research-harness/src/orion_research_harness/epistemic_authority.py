from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from enum import Enum
from typing import Sequence


class AuthorityTerminal(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    CANNOT_CHECK = "CANNOT_CHECK"


class BlockerDetermination(str, Enum):
    ESTABLISHED = "ESTABLISHED"
    REFUTED = "REFUTED"
    UNDETERMINED = "UNDETERMINED"


class RootClass(str, Enum):
    PROTECTED_CUSTODY = "PROTECTED_CUSTODY"
    DELEGATED_GRANT = "DELEGATED_GRANT"
    STANDING_POLICY = "STANDING_POLICY"
    OBLIGATION_FREE = "OBLIGATION_FREE"


def _strings(values: Sequence[str], *, name: str, allow_empty: bool = True) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an array")
    rows = tuple(str(item) for item in values)
    if any(not item.strip() for item in rows):
        raise ValueError(f"{name} entries must be non-empty")
    if len(rows) != len(set(rows)):
        raise ValueError(f"{name} entries must be unique")
    if not allow_empty and not rows:
        raise ValueError(f"{name} cannot be empty")
    return rows


@dataclass(frozen=True)
class JudgmentType:
    domain: str
    kind: str
    scope_ids: tuple[str, ...]
    content_contract: str
    epoch: int

    def __post_init__(self) -> None:
        if not self.domain.strip() or not self.kind.strip() or not self.content_contract.strip():
            raise ValueError("judgment domain/kind/content contract are required")
        object.__setattr__(self, "scope_ids", _strings(self.scope_ids, name="scope_ids", allow_empty=False))
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("judgment epoch must be a non-negative integer")


@dataclass(frozen=True)
class Judgment:
    judgment_id: str
    judgment_type: JudgmentType
    support_premise_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.judgment_id.strip():
            raise ValueError("judgment_id is required")
        object.__setattr__(self, "support_premise_ids", _strings(self.support_premise_ids, name="support_premise_ids"))


@dataclass(frozen=True)
class HardAuthorityObligation:
    obligation_id: str
    required_type: JudgmentType
    additional_premise_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.obligation_id.strip():
            raise ValueError("obligation_id is required")
        object.__setattr__(self, "additional_premise_ids", _strings(self.additional_premise_ids, name="additional_premise_ids"))


@dataclass(frozen=True)
class EffectRequest:
    effect_id: str
    domain: str
    operation: str
    scope_ids: tuple[str, ...]
    payload_digest: str
    epoch: int

    def __post_init__(self) -> None:
        if not self.effect_id.strip() or not self.domain.strip() or not self.operation.strip():
            raise ValueError("effect identity/domain/operation are required")
        if not self.payload_digest.strip():
            raise ValueError("effect payload digest is required")
        object.__setattr__(self, "scope_ids", _strings(self.scope_ids, name="effect scope", allow_empty=False))
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("effect epoch must be a non-negative integer")


@dataclass(frozen=True)
class RootGrant:
    grant_id: str
    domain: str
    scope_ids: tuple[str, ...]
    root_id: str
    root_class: RootClass
    epoch: int
    payload_digest: str

    def __post_init__(self) -> None:
        if not self.grant_id.strip() or not self.domain.strip() or not self.root_id.strip():
            raise ValueError("grant identity/domain/root are required")
        if not self.payload_digest.strip():
            raise ValueError("grant payload digest is required")
        object.__setattr__(self, "scope_ids", _strings(self.scope_ids, name="grant scope", allow_empty=False))
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("grant epoch must be a non-negative integer")


@dataclass(frozen=True)
class Coercion:
    coercion_id: str
    input_type: JudgmentType
    output_type: JudgmentType
    issuer_root_id: str
    semantic_premise_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    valid_from_epoch: int
    valid_through_epoch: int
    allow_scope_widening: bool = False

    def __post_init__(self) -> None:
        if not self.coercion_id.strip() or not self.issuer_root_id.strip():
            raise ValueError("coercion identity/issuer root are required")
        object.__setattr__(self, "semantic_premise_ids", _strings(self.semantic_premise_ids, name="semantic_premise_ids"))
        object.__setattr__(self, "lineage_ids", _strings(self.lineage_ids, name="lineage_ids", allow_empty=False))
        for name, value in (("valid_from_epoch", self.valid_from_epoch), ("valid_through_epoch", self.valid_through_epoch)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.valid_through_epoch < self.valid_from_epoch:
            raise ValueError("coercion validity interval is inverted")
        if not isinstance(self.allow_scope_widening, bool):
            raise TypeError("allow_scope_widening must be boolean")


@dataclass(frozen=True)
class SupportFamily:
    certificate_id: str
    support_sets: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        if not self.certificate_id.strip():
            raise ValueError("certificate_id is required")
        normalized = tuple(_strings(support, name="support set", allow_empty=False) for support in self.support_sets)
        if not normalized:
            raise ValueError("support family requires at least one support set")
        if len(normalized) != len(set(normalized)):
            raise ValueError("support sets must be unique")
        object.__setattr__(self, "support_sets", normalized)


@dataclass(frozen=True)
class AuthorityContext:
    judgments: tuple[Judgment, ...]
    hard_obligations: tuple[HardAuthorityObligation, ...]
    roots: tuple[RootGrant, ...]
    coercions: tuple[Coercion, ...]
    blocker_determinations: tuple[tuple[str, BlockerDetermination], ...]
    required_blocker_type_ids: tuple[str, ...]
    valid_premise_ids: tuple[str, ...]
    revoked_premise_ids: tuple[str, ...]
    support_families: tuple[SupportFamily, ...]
    history: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, values in (
            ("judgment", [x.judgment_id for x in self.judgments]),
            ("obligation", [x.obligation_id for x in self.hard_obligations]),
            ("grant", [x.grant_id for x in self.roots]),
            ("coercion", [x.coercion_id for x in self.coercions]),
            ("blocker", [x[0] for x in self.blocker_determinations]),
            ("support family", [x.certificate_id for x in self.support_families]),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} identities must be unique")
        object.__setattr__(self, "required_blocker_type_ids", _strings(self.required_blocker_type_ids, name="required_blocker_type_ids"))
        object.__setattr__(self, "valid_premise_ids", _strings(self.valid_premise_ids, name="valid_premise_ids"))
        object.__setattr__(self, "revoked_premise_ids", _strings(self.revoked_premise_ids, name="revoked_premise_ids"))
        object.__setattr__(self, "history", tuple(str(item) for item in self.history))


@dataclass(frozen=True)
class AuthorityDecision:
    terminal: AuthorityTerminal
    reason: str
    obligation_ids: tuple[str, ...] = ()
    coercion_path_ids: tuple[str, ...] = ()
    grant_id: str | None = None

    @property
    def authorized(self) -> bool:
        return self.terminal is AuthorityTerminal.AUTHORIZED


def _premise_state(context: AuthorityContext, premise_id: str) -> str:
    if premise_id in set(context.revoked_premise_ids):
        return "REVOKED"
    if premise_id in set(context.valid_premise_ids):
        return "VALID"
    return "MISSING"


def support_family_valid(family: SupportFamily, valid_premise_ids: Sequence[str], revoked_premise_ids: Sequence[str]) -> bool:
    valid = set(valid_premise_ids)
    revoked = set(revoked_premise_ids)
    return any(set(support) <= valid and not (set(support) & revoked) for support in family.support_sets)


def revoke_premises(context: AuthorityContext, premise_ids: Sequence[str], *, epoch: int) -> AuthorityContext:
    revoked = _strings(premise_ids, name="premise_ids", allow_empty=False)
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("revocation epoch must be a non-negative integer")
    next_revoked = tuple(dict.fromkeys((*context.revoked_premise_ids, *revoked)))
    return replace(
        context,
        revoked_premise_ids=next_revoked,
        history=(*context.history, *(f"REVOKE:{premise}@{epoch}" for premise in revoked)),
    )


def _grant_for_effect(effect: EffectRequest, context: AuthorityContext) -> tuple[RootGrant | None, str]:
    domain_grants = [grant for grant in context.roots if grant.domain == effect.domain]
    if not domain_grants:
        return None, "missing grant/root for effect domain"
    for grant in domain_grants:
        if grant.epoch != effect.epoch:
            continue
        if not set(effect.scope_ids) <= set(grant.scope_ids):
            continue
        if grant.payload_digest != effect.payload_digest:
            continue
        if _premise_state(context, grant.root_id) != "VALID":
            continue
        return grant, ""
    return None, "available grant/root is stale, out of scope, payload-mismatched, revoked, or invalid"


def _coercion_usable(coercion: Coercion, effect: EffectRequest, context: AuthorityContext) -> tuple[bool, AuthorityTerminal, str]:
    if not (coercion.valid_from_epoch <= effect.epoch <= coercion.valid_through_epoch):
        return False, AuthorityTerminal.DENIED, "stale coercion epoch"
    roots = {grant.root_id for grant in context.roots}
    if coercion.issuer_root_id not in roots:
        return False, AuthorityTerminal.DENIED, "coercion issuer/root is not registered"
    root_state = _premise_state(context, coercion.issuer_root_id)
    if root_state == "REVOKED":
        return False, AuthorityTerminal.DENIED, "coercion issuer/root revoked"
    if root_state == "MISSING":
        return False, AuthorityTerminal.CANNOT_CHECK, "coercion issuer/root unavailable"
    input_scope = set(coercion.input_type.scope_ids)
    output_scope = set(coercion.output_type.scope_ids)
    if not output_scope <= input_scope and not coercion.allow_scope_widening:
        return False, AuthorityTerminal.DENIED, "coercion scope widening was not explicitly declared"
    for premise in coercion.semantic_premise_ids:
        state = _premise_state(context, premise)
        if state == "REVOKED":
            return False, AuthorityTerminal.DENIED, "coercion semantic premise revoked"
        if state == "MISSING":
            return False, AuthorityTerminal.CANNOT_CHECK, "coercion semantic premise unavailable"
    return True, AuthorityTerminal.AUTHORIZED, ""


def _judgment_usable(judgment: Judgment, context: AuthorityContext) -> tuple[bool, AuthorityTerminal, str]:
    for premise in judgment.support_premise_ids:
        state = _premise_state(context, premise)
        if state == "REVOKED":
            return False, AuthorityTerminal.DENIED, "judgment support premise revoked"
        if state == "MISSING":
            return False, AuthorityTerminal.CANNOT_CHECK, "judgment support premise unavailable"
    return True, AuthorityTerminal.AUTHORIZED, ""


def _coercion_path(start: JudgmentType, target: JudgmentType, effect: EffectRequest, context: AuthorityContext) -> tuple[tuple[str, ...] | None, AuthorityTerminal, str]:
    if start == target:
        return (), AuthorityTerminal.AUTHORIZED, ""
    outgoing: dict[JudgmentType, list[Coercion]] = {}
    for coercion in context.coercions:
        outgoing.setdefault(coercion.input_type, []).append(coercion)
    queue: deque[tuple[JudgmentType, tuple[str, ...]]] = deque(((start, ()),))
    visited = {start}
    strongest_failure = AuthorityTerminal.CANNOT_CHECK
    failure_reason = "no exact typed coercion path"
    while queue:
        current, path = queue.popleft()
        for coercion in outgoing.get(current, ()):
            usable, terminal, reason = _coercion_usable(coercion, effect, context)
            if not usable:
                if terminal is AuthorityTerminal.DENIED:
                    strongest_failure = AuthorityTerminal.DENIED
                    failure_reason = reason
                elif strongest_failure is not AuthorityTerminal.DENIED:
                    failure_reason = reason
                continue
            next_type = coercion.output_type
            next_path = (*path, coercion.coercion_id)
            if next_type == target:
                return next_path, AuthorityTerminal.AUTHORIZED, ""
            if next_type not in visited:
                visited.add(next_type)
                queue.append((next_type, next_path))
    return None, strongest_failure, failure_reason


def _discharge_obligation(obligation: HardAuthorityObligation, effect: EffectRequest, context: AuthorityContext) -> tuple[AuthorityTerminal, tuple[str, ...], str]:
    for premise in obligation.additional_premise_ids:
        state = _premise_state(context, premise)
        if state == "REVOKED":
            return AuthorityTerminal.DENIED, (), f"mandatory premise {premise} revoked"
        if state == "MISSING":
            return AuthorityTerminal.CANNOT_CHECK, (), f"mandatory premise {premise} unavailable"

    best_failure = AuthorityTerminal.CANNOT_CHECK
    best_reason = "required typed judgment unavailable"
    for judgment in context.judgments:
        usable, terminal, reason = _judgment_usable(judgment, context)
        if not usable:
            if terminal is AuthorityTerminal.DENIED:
                best_failure = terminal
                best_reason = reason
            continue
        path, path_terminal, path_reason = _coercion_path(judgment.judgment_type, obligation.required_type, effect, context)
        if path is not None:
            return AuthorityTerminal.AUTHORIZED, path, ""
        if path_terminal is AuthorityTerminal.DENIED:
            best_failure = AuthorityTerminal.DENIED
            best_reason = path_reason
        elif best_failure is not AuthorityTerminal.DENIED:
            best_reason = path_reason
    return best_failure, (), best_reason


def authorize_effect(effect: EffectRequest, context: AuthorityContext, *, confidence: float | None = None, expected_utility: float | None = None) -> AuthorityDecision:
    """P8 authorization. Confidence/utility are intentionally not authority premises."""

    blocker_map = dict(context.blocker_determinations)
    for blocker_id in context.required_blocker_type_ids:
        state = blocker_map.get(blocker_id, BlockerDetermination.UNDETERMINED)
        if state is BlockerDetermination.ESTABLISHED:
            return AuthorityDecision(AuthorityTerminal.DENIED, f"active blocker established: {blocker_id}")
        if state is BlockerDetermination.UNDETERMINED:
            return AuthorityDecision(AuthorityTerminal.CANNOT_CHECK, f"blocker determination unavailable: {blocker_id}")

    grant, grant_reason = _grant_for_effect(effect, context)
    if grant is None:
        return AuthorityDecision(AuthorityTerminal.DENIED, grant_reason)

    paths: list[str] = []
    discharged: list[str] = []
    for obligation in context.hard_obligations:
        terminal, path, reason = _discharge_obligation(obligation, effect, context)
        if terminal is not AuthorityTerminal.AUTHORIZED:
            return AuthorityDecision(terminal, reason, obligation_ids=tuple(discharged), grant_id=grant.grant_id)
        discharged.append(obligation.obligation_id)
        paths.extend(path)

    return AuthorityDecision(
        AuthorityTerminal.AUTHORIZED,
        "all hard obligations discharged by exact typed derivations; blockers refuted; grant fresh and in scope",
        obligation_ids=tuple(discharged),
        coercion_path_ids=tuple(paths),
        grant_id=grant.grant_id,
    )


__all__ = [
    "AuthorityContext",
    "AuthorityDecision",
    "AuthorityTerminal",
    "BlockerDetermination",
    "Coercion",
    "EffectRequest",
    "HardAuthorityObligation",
    "Judgment",
    "JudgmentType",
    "RootClass",
    "RootGrant",
    "SupportFamily",
    "authorize_effect",
    "revoke_premises",
    "support_family_valid",
]
