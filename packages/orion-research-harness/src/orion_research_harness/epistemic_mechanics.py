from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Sequence


class ClaimStatus(str, Enum):
    OPEN = "OPEN"
    CERTIFIED = "CERTIFIED"
    INVALID = "INVALID"
    CANNOT_CHECK = "CANNOT_CHECK"


class MechanicTerminal(str, Enum):
    APPLIED = "APPLIED"
    DENIED = "DENIED"
    CANNOT_CHECK = "CANNOT_CHECK"


def _unique_strings(values: Sequence[str], name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an array")
    rows = tuple(str(item) for item in values)
    if any(not item.strip() for item in rows):
        raise ValueError(f"{name} entries must be non-empty")
    if len(rows) != len(set(rows)):
        raise ValueError(f"{name} entries must be unique")
    return rows


@dataclass(frozen=True)
class HardObligation:
    obligation_id: str
    required_evidence_ids: tuple[str, ...] = ()
    required_authority_ids: tuple[str, ...] = ()
    active: bool = True

    def __post_init__(self) -> None:
        if not self.obligation_id.strip():
            raise ValueError("obligation_id is required")
        object.__setattr__(
            self,
            "required_evidence_ids",
            _unique_strings(self.required_evidence_ids, "required_evidence_ids"),
        )
        object.__setattr__(
            self,
            "required_authority_ids",
            _unique_strings(self.required_authority_ids, "required_authority_ids"),
        )
        if not isinstance(self.active, bool):
            raise TypeError("active must be boolean")


@dataclass(frozen=True)
class AuthorityGrant:
    authority_id: str
    scope_ids: tuple[str, ...]
    root_id: str
    epoch: int

    def __post_init__(self) -> None:
        if not self.authority_id.strip() or not self.root_id.strip():
            raise ValueError("authority identity and root are required")
        object.__setattr__(self, "scope_ids", _unique_strings(self.scope_ids, "scope_ids"))
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("authority epoch must be a non-negative integer")


@dataclass(frozen=True)
class PreservationCertificate:
    certificate_id: str
    claim_id: str
    changed_ids: tuple[str, ...]
    issuer_id: str
    scope_ids: tuple[str, ...]
    epoch: int
    proof_id: str
    lineage_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("certificate_id", self.certificate_id),
            ("claim_id", self.claim_id),
            ("issuer_id", self.issuer_id),
            ("proof_id", self.proof_id),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "changed_ids", _unique_strings(self.changed_ids, "changed_ids"))
        object.__setattr__(self, "scope_ids", _unique_strings(self.scope_ids, "scope_ids"))
        object.__setattr__(self, "lineage_ids", _unique_strings(self.lineage_ids, "lineage_ids"))
        if not self.lineage_ids:
            raise ValueError("preservation certificate requires lineage")
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("certificate epoch must be a non-negative integer")


@dataclass(frozen=True)
class EpistemicMechanicState:
    coordinate_values: tuple[tuple[str, str], ...]
    claim_statuses: tuple[tuple[str, ClaimStatus], ...]
    dependencies: tuple[tuple[str, str], ...]
    evidence_ids: tuple[str, ...]
    provenance_ids: tuple[str, ...]
    hard_obligations: tuple[HardObligation, ...]
    authorities: tuple[AuthorityGrant, ...]
    protected_root_ids: tuple[str, ...]
    epoch: int
    history: tuple[str, ...]

    def __post_init__(self) -> None:
        coordinates = [name for name, _ in self.coordinate_values]
        claims = [name for name, _ in self.claim_statuses]
        obligations = [item.obligation_id for item in self.hard_obligations]
        authorities = [item.authority_id for item in self.authorities]
        for name, values in (
            ("coordinate", coordinates),
            ("claim", claims),
            ("obligation", obligations),
            ("authority", authorities),
        ):
            if any(not str(item).strip() for item in values):
                raise ValueError(f"{name} identity is required")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} identities must be unique")
        normalized_dependencies: list[tuple[str, str]] = []
        for edge in self.dependencies:
            if not isinstance(edge, (tuple, list)) or len(edge) != 2:
                raise TypeError("dependencies must be binary edges")
            left, right = str(edge[0]), str(edge[1])
            if not left.strip() or not right.strip():
                raise ValueError("dependency endpoints are required")
            if right not in set(claims):
                raise ValueError("dependency target must be a claim identity")
            normalized_dependencies.append((left, right))
        if len(normalized_dependencies) != len(set(normalized_dependencies)):
            raise ValueError("dependencies must be unique")
        object.__setattr__(self, "dependencies", tuple(normalized_dependencies))
        object.__setattr__(self, "evidence_ids", _unique_strings(self.evidence_ids, "evidence_ids"))
        object.__setattr__(self, "provenance_ids", _unique_strings(self.provenance_ids, "provenance_ids"))
        object.__setattr__(
            self,
            "protected_root_ids",
            _unique_strings(self.protected_root_ids, "protected_root_ids"),
        )
        object.__setattr__(self, "history", tuple(str(item) for item in self.history))
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("state epoch must be a non-negative integer")

    def with_evidence(self, *evidence_ids: str) -> "EpistemicMechanicState":
        additions = _unique_strings(evidence_ids, "evidence_ids")
        return replace(
            self,
            evidence_ids=tuple(dict.fromkeys((*self.evidence_ids, *additions))),
        )

    def scientific_projection(self) -> tuple[object, ...]:
        """P6 current-scientific-state projection: everything except ordered history."""

        return (
            self.coordinate_values,
            self.claim_statuses,
            self.dependencies,
            self.evidence_ids,
            self.provenance_ids,
            self.hard_obligations,
            self.authorities,
            self.protected_root_ids,
            self.epoch,
        )


@dataclass(frozen=True)
class MechanicContract:
    mechanic_id: str
    read_ids: tuple[str, ...]
    write_ids: tuple[str, ...]
    write_values: tuple[tuple[str, str], ...] = ()
    required_evidence_ids: tuple[str, ...] = ()
    required_authority_ids: tuple[str, ...] = ()
    emitted_obligations: tuple[HardObligation, ...] = ()
    discharge_obligation_ids: tuple[str, ...] = ()
    authority_additions: tuple[AuthorityGrant, ...] = ()
    read_obligation_ids: tuple[str, ...] = ()
    write_obligation_ids: tuple[str, ...] = ()
    read_authority_ids: tuple[str, ...] = ()
    write_authority_ids: tuple[str, ...] = ()
    audit_rank: int = 0
    recursive_calls: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip():
            raise ValueError("mechanic_id is required")
        for field_name in (
            "read_ids",
            "write_ids",
            "required_evidence_ids",
            "required_authority_ids",
            "discharge_obligation_ids",
            "read_obligation_ids",
            "write_obligation_ids",
            "read_authority_ids",
            "write_authority_ids",
        ):
            object.__setattr__(self, field_name, _unique_strings(getattr(self, field_name), field_name))
        write_names = [name for name, _ in self.write_values]
        if any(not str(name).strip() for name in write_names):
            raise ValueError("write value coordinate names are required")
        if len(write_names) != len(set(write_names)):
            raise ValueError("write_values may write each coordinate once")
        if isinstance(self.audit_rank, bool) or not isinstance(self.audit_rank, int) or self.audit_rank < 0:
            raise ValueError("audit_rank must be a non-negative integer")
        for target, rank in self.recursive_calls:
            if not str(target).strip() or isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
                raise ValueError("recursive call target/rank invalid")


@dataclass(frozen=True)
class MechanicResult:
    terminal: MechanicTerminal
    state: EpistemicMechanicState
    reason: str
    changed_ids: tuple[str, ...] = ()

    @property
    def applied(self) -> bool:
        return self.terminal is MechanicTerminal.APPLIED


def _descendants(dependencies: Sequence[tuple[str, str]], roots: set[str]) -> set[str]:
    outgoing: dict[str, set[str]] = {}
    for left, right in dependencies:
        outgoing.setdefault(left, set()).add(right)
    seen: set[str] = set()
    frontier = list(roots)
    while frontier:
        current = frontier.pop()
        for child in outgoing.get(current, ()):
            if child in seen:
                continue
            seen.add(child)
            frontier.append(child)
    return seen


def _valid_preservation_certificate(
    state: EpistemicMechanicState,
    certificate: PreservationCertificate,
    changed: tuple[str, ...],
    affected: set[str],
) -> bool:
    # Definition 6: q must not itself be changed, the proof is exact to X/current
    # epoch, issuer is outside candidate authority (represented here by a protected
    # root), and the certificate scope/lineage actually names q/support.
    if certificate.claim_id in set(changed):
        return False
    if tuple(sorted(certificate.changed_ids)) != tuple(sorted(changed)):
        return False
    if certificate.claim_id not in affected:
        return False
    if certificate.claim_id not in certificate.scope_ids:
        return False
    if certificate.issuer_id not in state.protected_root_ids:
        return False
    if certificate.epoch != state.epoch:
        return False
    if not certificate.proof_id or not certificate.lineage_ids:
        return False
    return True


def certificate_aware_reopen(
    state: EpistemicMechanicState,
    *,
    changed_ids: Sequence[str],
    certificates: Sequence[PreservationCertificate],
) -> EpistemicMechanicState:
    changed = _unique_strings(changed_ids, "changed_ids")
    statuses = dict(state.claim_statuses)
    certified = {claim for claim, status in state.claim_statuses if status is ClaimStatus.CERTIFIED}
    affected = (set(changed) & certified) | (_descendants(state.dependencies, set(changed)) & certified)
    preserved = {
        certificate.claim_id
        for certificate in certificates
        if _valid_preservation_certificate(state, certificate, changed, affected)
    }
    reopen = affected - preserved
    if not reopen:
        return state
    for claim in reopen:
        statuses[claim] = ClaimStatus.OPEN
    ordered = tuple((claim, statuses[claim]) for claim, _ in state.claim_statuses)
    return replace(
        state,
        claim_statuses=ordered,
        history=(*state.history, "REOPEN:" + ",".join(sorted(reopen)) + "@" + str(state.epoch)),
    )


def _authority_addition_allowed(state: EpistemicMechanicState, grant: AuthorityGrant) -> bool:
    if grant.epoch != state.epoch:
        return False
    if grant.root_id in state.protected_root_ids:
        return True
    # A restriction of existing legitimate authority is non-escalating even if
    # the root itself is a delegated/standing root rather than protected custody.
    for existing in state.authorities:
        if existing.root_id != grant.root_id or existing.epoch != grant.epoch:
            continue
        if set(grant.scope_ids) <= set(existing.scope_ids):
            return True
    return False


def _recursive_contract_valid(contract: MechanicContract) -> bool:
    return all(rank < contract.audit_rank for _, rank in contract.recursive_calls)


def apply_mechanic(
    state: EpistemicMechanicState,
    contract: MechanicContract,
) -> MechanicResult:
    """Execute P6 admissibility for a declarative bounded mechanic contract.

    Failed admissibility never mutates state. This function intentionally does
    not create scientific authority: it only preserves/restricts existing grants
    or accepts a grant rooted in a state-declared protected root.
    """

    if not _recursive_contract_valid(contract):
        return MechanicResult(
            MechanicTerminal.DENIED,
            state,
            "recursive/self-audit call does not decrease the well-founded audit rank; cycle rejected",
        )
    declared_writes = set(contract.write_ids)
    actual_writes = {name for name, _ in contract.write_values}
    if not actual_writes <= declared_writes:
        return MechanicResult(
            MechanicTerminal.DENIED,
            state,
            "material mutation lies outside declared write footprint",
        )

    missing_evidence = sorted(set(contract.required_evidence_ids) - set(state.evidence_ids))
    missing_authority = sorted(
        set(contract.required_authority_ids) - {item.authority_id for item in state.authorities}
    )
    if missing_evidence or missing_authority:
        return MechanicResult(
            MechanicTerminal.CANNOT_CHECK,
            state,
            "missing hard evidence/authority premises: "
            + ",".join((*missing_evidence, *missing_authority)),
        )

    obligations = {item.obligation_id: item for item in state.hard_obligations}
    for obligation_id in contract.discharge_obligation_ids:
        obligation = obligations.get(obligation_id)
        if obligation is None or not obligation.active:
            return MechanicResult(
                MechanicTerminal.DENIED,
                state,
                f"authorized discharge references absent/inactive hard obligation {obligation_id}",
            )
        missing = set(obligation.required_evidence_ids) - set(state.evidence_ids)
        missing_auth = set(obligation.required_authority_ids) - {
            item.authority_id for item in state.authorities
        }
        if missing or missing_auth:
            return MechanicResult(
                MechanicTerminal.CANNOT_CHECK,
                state,
                f"hard obligation {obligation_id} cannot be discharged: required evidence/authority unavailable",
            )

    for grant in contract.authority_additions:
        if not _authority_addition_allowed(state, grant):
            return MechanicResult(
                MechanicTerminal.DENIED,
                state,
                f"authority addition {grant.authority_id} is an unrooted/stale widening",
            )

    for emitted in contract.emitted_obligations:
        existing = obligations.get(emitted.obligation_id)
        if existing is not None and existing != emitted:
            return MechanicResult(
                MechanicTerminal.DENIED,
                state,
                f"hard obligation identity collision: {emitted.obligation_id}",
            )

    coordinates = dict(state.coordinate_values)
    for name, value in contract.write_values:
        coordinates[name] = value
    coordinate_order = list(name for name, _ in state.coordinate_values)
    for name, _ in contract.write_values:
        if name not in coordinate_order:
            coordinate_order.append(name)
    next_coordinates = tuple((name, coordinates[name]) for name in coordinate_order)

    next_obligations = list(state.hard_obligations)
    by_index = {item.obligation_id: index for index, item in enumerate(next_obligations)}
    for obligation_id in contract.discharge_obligation_ids:
        index = by_index[obligation_id]
        next_obligations[index] = replace(next_obligations[index], active=False)
    for emitted in contract.emitted_obligations:
        if emitted.obligation_id not in by_index:
            next_obligations.append(emitted)
            by_index[emitted.obligation_id] = len(next_obligations) - 1

    next_authorities = list(state.authorities)
    authority_ids = {item.authority_id for item in next_authorities}
    for grant in contract.authority_additions:
        if grant.authority_id in authority_ids:
            existing = next(item for item in next_authorities if item.authority_id == grant.authority_id)
            if existing != grant:
                return MechanicResult(
                    MechanicTerminal.DENIED,
                    state,
                    f"authority identity collision: {grant.authority_id}",
                )
            continue
        next_authorities.append(grant)
        authority_ids.add(grant.authority_id)

    changed = tuple(sorted(actual_writes))
    next_state = replace(
        state,
        coordinate_values=next_coordinates,
        hard_obligations=tuple(next_obligations),
        authorities=tuple(next_authorities),
        history=(*state.history, f"APPLY:{contract.mechanic_id}@{state.epoch}"),
    )
    return MechanicResult(
        MechanicTerminal.APPLIED,
        next_state,
        "admissible mechanic committed; hard residual obligations preserved unless explicitly discharged",
        changed,
    )


def _semantic_read_footprint(contract: MechanicContract) -> set[str]:
    return (
        {f"coord:{item}" for item in contract.read_ids}
        | {f"evidence:{item}" for item in contract.required_evidence_ids}
        | {f"authority:{item}" for item in (*contract.required_authority_ids, *contract.read_authority_ids)}
        | {f"obligation:{item}" for item in contract.read_obligation_ids}
    )


def _semantic_write_footprint(contract: MechanicContract) -> set[str]:
    return (
        {f"coord:{item}" for item in contract.write_ids}
        | {f"authority:{item.authority_id}" for item in contract.authority_additions}
        | {f"authority:{item}" for item in contract.write_authority_ids}
        | {f"obligation:{item.obligation_id}" for item in contract.emitted_obligations}
        | {f"obligation:{item}" for item in (*contract.discharge_obligation_ids, *contract.write_obligation_ids)}
    )


def semantically_separated(left: MechanicContract, right: MechanicContract) -> bool:
    left_r = _semantic_read_footprint(left)
    left_w = _semantic_write_footprint(left)
    right_r = _semantic_read_footprint(right)
    right_w = _semantic_write_footprint(right)
    return not (left_w & (right_r | right_w)) and not (right_w & (left_r | left_w))


def _event_mechanic_id(event: str) -> str | None:
    if not event.startswith("APPLY:"):
        return None
    body = event[len("APPLY:") :]
    if "@" not in body:
        return None
    return body.rsplit("@", 1)[0]


def _canonical_history(
    history: Sequence[str],
    independent_pairs: Sequence[tuple[str, str]],
) -> tuple[str, ...]:
    independent = {frozenset((left, right)) for left, right in independent_pairs}
    rows = list(history)
    # Repeated adjacent swaps to one lexical normal form for the trace monoid.
    changed = True
    while changed:
        changed = False
        for index in range(len(rows) - 1):
            left_id = _event_mechanic_id(rows[index])
            right_id = _event_mechanic_id(rows[index + 1])
            if left_id is None or right_id is None:
                continue
            if frozenset((left_id, right_id)) not in independent:
                continue
            if rows[index] > rows[index + 1]:
                rows[index], rows[index + 1] = rows[index + 1], rows[index]
                changed = True
    return tuple(rows)


def independently_equivalent_histories(
    left: Sequence[str],
    right: Sequence[str],
    *,
    independent_pairs: Sequence[tuple[str, str]],
) -> bool:
    return _canonical_history(left, independent_pairs) == _canonical_history(right, independent_pairs)


__all__ = [
    "AuthorityGrant",
    "ClaimStatus",
    "EpistemicMechanicState",
    "HardObligation",
    "MechanicContract",
    "MechanicResult",
    "MechanicTerminal",
    "PreservationCertificate",
    "apply_mechanic",
    "certificate_aware_reopen",
    "independently_equivalent_histories",
    "semantically_separated",
]
