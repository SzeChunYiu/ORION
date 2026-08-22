from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class OCMETerminal(str, Enum):
    OCME_METHOD_EXPANSION_SUPPORTED = "OCME_METHOD_EXPANSION_SUPPORTED"
    OCME_PROBLEM_SOLVING_ONLY = "OCME_PROBLEM_SOLVING_ONLY"
    OCME_LOWER_LEVEL_CAUSE = "OCME_LOWER_LEVEL_CAUSE"
    OCME_DONOR_SUBSUMED = "OCME_DONOR_SUBSUMED"
    OCME_IMPOSSIBILITY_BOUNDARY = "OCME_IMPOSSIBILITY_BOUNDARY"
    CANNOT_CHECK = "CANNOT_CHECK"


class ObstructionKind(str, Enum):
    EXACT_FINITE_NONREACHABILITY = "EXACT_FINITE_NONREACHABILITY"
    MACHINE_CHECKED_LOWER_BOUND = "MACHINE_CHECKED_LOWER_BOUND"
    EXHAUSTIVE_BOUNDED_NONREACHABILITY = "EXHAUSTIVE_BOUNDED_NONREACHABILITY"
    RESOURCE_BOUNDED_OBSTRUCTION = "RESOURCE_BOUNDED_OBSTRUCTION"


def _ids(values: Sequence[str], *, name: str, allow_empty: bool = True) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an array")
    out = tuple(str(value) for value in values)
    if not allow_empty and not out:
        raise ValueError(f"{name} cannot be empty")
    if any(not value.strip() for value in out):
        raise ValueError(f"{name} entries must be non-empty")
    if len(set(out)) != len(out):
        raise ValueError(f"{name} entries must be unique")
    return out


@dataclass(frozen=True)
class LowerLevelResult:
    check_id: str
    route_kind: str
    succeeded: bool
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.check_id.strip() or not self.route_kind.strip():
            raise ValueError("lower-level check identity and route kind are required")
        if not isinstance(self.succeeded, bool):
            raise TypeError("lower-level succeeded must be boolean")
        object.__setattr__(self, "evidence_ids", _ids(self.evidence_ids, name="evidence_ids", allow_empty=False))


@dataclass(frozen=True)
class ObstructionCertificate:
    certificate_id: str
    kind: ObstructionKind
    target_id: str
    old_closure_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    independently_verified: bool
    all_registered_baselines_exhausted: bool
    timeout_only: bool = False

    def __post_init__(self) -> None:
        if not self.certificate_id.strip() or not self.target_id.strip():
            raise ValueError("obstruction certificate and target identities are required")
        object.__setattr__(self, "old_closure_ids", _ids(self.old_closure_ids, name="old_closure_ids", allow_empty=False))
        object.__setattr__(self, "evidence_ids", _ids(self.evidence_ids, name="evidence_ids", allow_empty=False))
        for value in (
            self.independently_verified,
            self.all_registered_baselines_exhausted,
            self.timeout_only,
        ):
            if not isinstance(value, bool):
                raise TypeError("obstruction booleans must be boolean")


@dataclass(frozen=True)
class MethodEdit:
    edit_id: str
    semantic_operator_ids: tuple[str, ...]
    claimed_new_reach_ids: tuple[str, ...]
    expands_to_old_closure: bool
    access_model_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.edit_id.strip():
            raise ValueError("method edit identity is required")
        object.__setattr__(self, "semantic_operator_ids", _ids(self.semantic_operator_ids, name="semantic_operator_ids", allow_empty=False))
        object.__setattr__(self, "claimed_new_reach_ids", _ids(self.claimed_new_reach_ids, name="claimed_new_reach_ids", allow_empty=False))
        object.__setattr__(self, "access_model_ids", _ids(self.access_model_ids, name="access_model_ids", allow_empty=False))
        if not isinstance(self.expands_to_old_closure, bool):
            raise TypeError("expands_to_old_closure must be boolean")


@dataclass(frozen=True)
class OutsideClosureVerification:
    verification_id: str
    edit_id: str
    verifier_id: str
    candidate_issuer_id: str
    outside_old_closure: bool
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("verification_id", self.verification_id),
            ("edit_id", self.edit_id),
            ("verifier_id", self.verifier_id),
            ("candidate_issuer_id", self.candidate_issuer_id),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.outside_old_closure, bool):
            raise TypeError("outside_old_closure must be boolean")
        object.__setattr__(self, "evidence_ids", _ids(self.evidence_ids, name="evidence_ids", allow_empty=False))


@dataclass(frozen=True)
class TransferEvidence:
    held_out_ids: tuple[str, ...]
    positive_transfer_ids: tuple[str, ...]
    frozen_access_model_ids: tuple[str, ...]
    false_expansion_rate: float
    false_expansion_guard: float
    semantic_preservation: bool
    strong_baseline_same_reach: bool
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "held_out_ids", _ids(self.held_out_ids, name="held_out_ids", allow_empty=False))
        object.__setattr__(self, "positive_transfer_ids", _ids(self.positive_transfer_ids, name="positive_transfer_ids", allow_empty=False))
        object.__setattr__(self, "frozen_access_model_ids", _ids(self.frozen_access_model_ids, name="frozen_access_model_ids", allow_empty=False))
        object.__setattr__(self, "evidence_ids", _ids(self.evidence_ids, name="evidence_ids", allow_empty=False))
        if not set(self.positive_transfer_ids) <= set(self.held_out_ids):
            raise ValueError("positive transfer must be a subset of held-out identities")
        for name, value in (
            ("false_expansion_rate", self.false_expansion_rate),
            ("false_expansion_guard", self.false_expansion_guard),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")
            if value < 0.0 or value > 1.0:
                raise ValueError(f"{name} must lie in [0,1]")
        if not isinstance(self.semantic_preservation, bool) or not isinstance(self.strong_baseline_same_reach, bool):
            raise TypeError("transfer flags must be boolean")


@dataclass(frozen=True)
class OCMEEpisode:
    episode_id: str
    problem_model_frozen: bool
    verifier_available: bool
    access_model_frozen: bool
    resource_model_frozen: bool
    lower_level_results: tuple[LowerLevelResult, ...]
    obstruction: ObstructionCertificate | None
    candidate_edit: MethodEdit | None
    outside_closure: OutsideClosureVerification | None
    transfer: TransferEvidence | None
    problem_solving_gain: bool
    donor_same_reach: bool
    independent_reproduction: bool

    def __post_init__(self) -> None:
        if not self.episode_id.strip():
            raise ValueError("OCME episode identity is required")
        ids = [item.check_id for item in self.lower_level_results]
        if len(ids) != len(set(ids)):
            raise ValueError("lower-level check identities must be unique")
        for value in (
            self.problem_model_frozen,
            self.verifier_available,
            self.access_model_frozen,
            self.resource_model_frozen,
            self.problem_solving_gain,
            self.donor_same_reach,
            self.independent_reproduction,
        ):
            if not isinstance(value, bool):
                raise TypeError("OCME episode flags must be boolean")


@dataclass(frozen=True)
class OCMEDecision:
    terminal: OCMETerminal
    jump_open: bool
    edit_disposition: str
    reasons: tuple[str, ...]
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_adoption_authority: bool = False


def _decision(
    terminal: OCMETerminal,
    *,
    jump_open: bool,
    edit_disposition: str = "NONE",
    reasons: Sequence[str],
) -> OCMEDecision:
    return OCMEDecision(
        terminal=terminal,
        jump_open=jump_open,
        edit_disposition=edit_disposition,
        reasons=tuple(reasons),
    )


def _valid_obstruction(obstruction: ObstructionCertificate) -> tuple[bool, str]:
    if obstruction.timeout_only:
        return False, "timeout or failed trace alone is not an obstruction certificate"
    if not obstruction.independently_verified:
        return False, "obstruction lacks independent verification"
    if not obstruction.evidence_ids:
        return False, "obstruction lacks evidence"
    if obstruction.kind is ObstructionKind.RESOURCE_BOUNDED_OBSTRUCTION and not obstruction.all_registered_baselines_exhausted:
        return False, "resource-bounded obstruction requires every registered baseline exhausted"
    if not obstruction.all_registered_baselines_exhausted:
        return False, "registered first-right-of-refusal baselines are not exhausted"
    return True, ""


def assess_ocme_episode(episode: OCMEEpisode) -> OCMEDecision:
    """Execute the P10 OCME O0--O6 decision contract.

    A supported method-language expansion is a research result only. Correctness,
    adoption, novelty and scientific-promotion authority remain owned by protected
    P4/P8/evaluator paths.
    """

    missing_freeze = []
    if not episode.problem_model_frozen:
        missing_freeze.append("problem/access subject not frozen")
    if not episode.access_model_frozen:
        missing_freeze.append("access model not frozen")
    if not episode.resource_model_frozen:
        missing_freeze.append("resource model not frozen")
    if not episode.verifier_available:
        missing_freeze.append("verifier/custody evidence unavailable")
    if missing_freeze:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=False, reasons=missing_freeze)

    successful_lower = [item.check_id for item in episode.lower_level_results if item.succeeded]
    if successful_lower:
        return _decision(
            OCMETerminal.OCME_LOWER_LEVEL_CAUSE,
            jump_open=False,
            reasons=("lower-level first-right-of-refusal route succeeds: " + ",".join(successful_lower),),
        )

    if episode.obstruction is None:
        terminal = OCMETerminal.OCME_PROBLEM_SOLVING_ONLY if episode.problem_solving_gain else OCMETerminal.CANNOT_CHECK
        return _decision(terminal, jump_open=False, reasons=("no independently valid O2 obstruction certificate",))

    obstruction_ok, obstruction_reason = _valid_obstruction(episode.obstruction)
    if not obstruction_ok:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=False, reasons=(obstruction_reason,))

    if episode.candidate_edit is None:
        return _decision(
            OCMETerminal.CANNOT_CHECK,
            jump_open=True,
            reasons=("O2 obstruction established; method-language search is open but no candidate edit is verified",),
        )

    edit = episode.candidate_edit
    if edit.expands_to_old_closure or set(edit.semantic_operator_ids) <= set(episode.obstruction.old_closure_ids):
        return _decision(
            OCMETerminal.CANNOT_CHECK,
            jump_open=True,
            edit_disposition="KNOWN_COMPOSITION",
            reasons=("candidate is an alias/macro/composition already inside the frozen old closure",),
        )

    outside = episode.outside_closure
    if outside is None:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="UNVERIFIED_OUTSIDE_CLOSURE", reasons=("missing independent outside-closure verification",))
    if outside.edit_id != edit.edit_id:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="MISMATCHED_VERIFICATION", reasons=("outside-closure verification refers to another edit",))
    if outside.verifier_id == outside.candidate_issuer_id:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="SELF_CERTIFIED", reasons=("candidate cannot self-certify outside-closure status",))
    if not outside.outside_old_closure:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="KNOWN_COMPOSITION", reasons=("independent checker does not establish outside-closure status",))

    transfer = episode.transfer
    if transfer is None:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="OUTSIDE_CLOSURE", reasons=("outside-closure edit lacks held-out transfer/false-expansion evidence",))
    if set(edit.access_model_ids) != set(transfer.frozen_access_model_ids):
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="ACCESS_MODEL_WIDENED", reasons=("candidate changed the frozen access model",))
    if not transfer.semantic_preservation:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="SEMANTIC_PRESERVATION_FAILED", reasons=("semantic target/verifier preservation is not established",))
    if not transfer.positive_transfer_ids:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="NO_HELD_OUT_TRANSFER", reasons=("no positive held-out transfer",))
    if transfer.false_expansion_rate > transfer.false_expansion_guard:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="FALSE_EXPANSION_GUARD_FAILED", reasons=("false-expansion guard failed",))
    if episode.donor_same_reach or transfer.strong_baseline_same_reach:
        return _decision(
            OCMETerminal.OCME_DONOR_SUBSUMED,
            jump_open=True,
            edit_disposition="DONOR_SUBSUMED",
            reasons=("strong search/synthesis/evolution donor obtains the same reach under the frozen model",),
        )
    if not episode.problem_solving_gain:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="NO_VERIFIED_SOLVING_GAIN", reasons=("no verified problem-solving gain beyond representation-only metrics",))
    if not episode.independent_reproduction:
        return _decision(OCMETerminal.CANNOT_CHECK, jump_open=True, edit_disposition="REPRODUCTION_OPEN", reasons=("independent reproduction remains open",))

    return _decision(
        OCMETerminal.OCME_METHOD_EXPANSION_SUPPORTED,
        jump_open=True,
        edit_disposition="OUTSIDE_CLOSURE_TRANSFERRED",
        reasons=("O0-O5 obligations satisfied under one frozen resource/access semantics; P4/P8 still own promotion authority",),
    )


__all__ = [
    "LowerLevelResult",
    "MethodEdit",
    "OCMEDecision",
    "OCMEEpisode",
    "OCMETerminal",
    "ObstructionCertificate",
    "ObstructionKind",
    "OutsideClosureVerification",
    "TransferEvidence",
    "assess_ocme_episode",
]
