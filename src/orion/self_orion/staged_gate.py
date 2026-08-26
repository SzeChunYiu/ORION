"""Non-compensatory staged self-improvement gate (ORION-P5 V2, issue #141).

The blocking primitive already exists in `orion.kernel.hard_gates`: a failed or
unobserved requirement cannot be bought off by performance elsewhere, the report
carries no aggregate to trade against, contract chronology is pinned to a round,
conflicting observations fail rather than last-write-wins, and a pass without
evidence is unresolved rather than passing. This module **stages** that
primitive; it does not restate it.

Stages, in the shape the P5 programme already uses
(`papers/orion-15-self-orion/protocol/FRESH_TRANSFER_POLICY_V1.md`):

===============  =========  ==============================================
stage            #141 name  refuses
===============  =========  ==============================================
PROPOSAL         STATIC     a proposal that does not bind its request/base,
                            changes nothing, leaves its declared scope,
                            touches a protected path, or predates the gate
                            contract that judges it
EVIDENCE         REPLAY     replay evidence not bound to this candidate or
                            to the observed failure, self-verified replay,
                            an unrepaired motivating failure, and deletion
                            of retained negative history
SANDBOX          FRESH      a sandbox run not bound to this candidate,
                            failing required tests, a fresh split that is
                            not the frozen one / does not predate the
                            candidate / was already candidate feedback, a
                            case that varies no declared axis, ANY fresh
                            regression, and a split with no gain at all
APPRAISAL        PROTECTED  an appraisal not bound to this candidate, an
                            appraiser whose lineage is the subject's, an
                            evaluator that is not the frozen one or does
                            not predate the candidate, a candidate round
                            that does not predate its own appraisal, a
                            failed protected invariant, no development gain
                            and a fresh-assurance regression
AUTHORIZATION    --         *everything*: an appraiser may appraise, never
                            authorize. Reserved to `authorize_commit`.
COMMIT           --         *everything*: the terminal is external custody.
===============  =========  ==============================================

Three things the primitive could not express, which therefore live here:

1. `hard_gates` has no ordering relation between contracts. Staging — a later
   stage cannot be evaluated until its predecessor passed — is layered on top,
   as `appraise_stage`'s typed `StageOutOfOrder` refusal.
2. `HardGateReport` has nowhere to record "not evaluated because a predecessor
   blocked", so `StageOutcome.refusal` carries it. A refused stage is visible in
   the report with a named reason; it is never a silent skip.
3. FAIL-dominates-CANNOT_CHECK holds only *within* one contract. Issue #141
   requires that across stages too ("any known fail/harm dominates missing
   earlier stages"), so `_known_harms` scans every supplied record and can only
   lower the verdict floor. Without it, leaving an early stage unobserved would
   launder a known later harm behind CANDIDATE_ONLY.

Caller-declared authority is the failure mode this gate is built against, so
almost every requirement is **derived** rather than asserted: identity bindings
are hash comparisons, independence is a lineage inequality, freshness is a set
intersection against the candidate's own feedback, custody is a comparison
against a hash named in the (earlier) request, and chronology is a round
comparison. The two assertions that cannot be derived are named here:

* `SelfImprovementCandidate.created_at_round` is the one chronological claim the
  candidate makes about itself. It is sandwiched — `gate_contract_frozen_at_round
  < created_at_round < appraisal.appraised_at_round` — between two rounds set by
  parties that are not the candidate (the request, frozen earlier and fingerprinted
  into every stage contract; and the appraisal, produced by a lineage-distinct
  appraiser). Inflating it to make the freeze checks easier trips the upper bound.
* `ProtectedAppraisal`'s deltas and invariant states are measurements, not
  claims about authority. They are bound to an evaluator artifact hash that the
  request named before the candidate existed, and to an appraiser lineage that
  must differ from the producer's.

Nearest-work disposition (#141): PACE-style anytime-valid acceptance is absorbed
as baseline pressure on *when* evidence may be read, not as standalone novelty.
It governs sequential stopping within a stage; it says nothing about refusing to
average one stage against another, which is what this gate is for.

Exports are deliberately not added to `orion/self_orion/__init__.py`: per
`AGENTS.md`, shared registries are edited by the lane that owns the wave.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from orion.kernel.hard_gates import (
    HardGateContract,
    HardGateObservation,
    HardGateRequirement,
    HardGateState,
    evaluate_hard_gates,
)
from orion.kernel.store import canonical_bytes
from orion.providers.development.base import (
    DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES,
)
from orion.self_orion.change_control import ChangeControlVerdict

#: Additive V2 surface (issue #136): unconsumed by design until separately
#: execution-frozen. Being imported by a V1-frozen module is the defect here,
#: not being unconsumed — `orion.adoption` checks that direction.
ADOPTION_BOUNDARY = "V2_ADDITIVE"

GATE_ID = "orion.p5.v2.staged-gate"
META_OVERFIT_REASON = "meta_overfit:development_gain_with_assurance_regression"


class SelfImprovementStage(str, Enum):
    """Ordered stages. The order is the gate; see `STAGE_ORDER`."""

    PROPOSAL = "PROPOSAL"
    EVIDENCE = "EVIDENCE"
    SANDBOX = "SANDBOX"
    APPRAISAL = "APPRAISAL"
    AUTHORIZATION = "AUTHORIZATION"
    COMMIT = "COMMIT"


STAGE_ORDER: tuple[SelfImprovementStage, ...] = (
    SelfImprovementStage.PROPOSAL,
    SelfImprovementStage.EVIDENCE,
    SelfImprovementStage.SANDBOX,
    SelfImprovementStage.APPRAISAL,
    SelfImprovementStage.AUTHORIZATION,
    SelfImprovementStage.COMMIT,
)
APPRAISABLE_STAGES: tuple[SelfImprovementStage, ...] = STAGE_ORDER[:4]
RESERVED_STAGES: tuple[SelfImprovementStage, ...] = STAGE_ORDER[4:]


class StageRefusal(str, Enum):
    """Why a stage was not evaluated. Never `None` for an unevaluated stage."""

    PREDECESSOR_FAILED = "PREDECESSOR_FAILED"
    PREDECESSOR_UNRESOLVED = "PREDECESSOR_UNRESOLVED"
    RESERVED_TO_EXTERNAL_AUTHORITY = "RESERVED_TO_EXTERNAL_AUTHORITY"


class TransferOutcome(str, Enum):
    """One case's direction of travel. Deliberately not a number.

    A pooled mean over these would let an improvement family erase a regression
    family, which is exactly the substitution the gate exists to refuse.
    """

    IMPROVED = "IMPROVED"
    UNCHANGED = "UNCHANGED"
    REGRESSED = "REGRESSED"
    NOT_OBSERVED = "NOT_OBSERVED"


class StageOutOfOrder(RuntimeError):
    """Typed refusal: a stage was attempted before its predecessor passed."""

    def __init__(
        self,
        stage: SelfImprovementStage,
        *,
        blocked_by: SelfImprovementStage | None = None,
        blocking_state: HardGateState | None = None,
        detail: str = "",
    ) -> None:
        self.stage = stage
        self.blocked_by = blocked_by
        self.blocking_state = blocking_state
        self.detail = detail
        blocker = blocked_by.value if blocked_by is not None else detail or "unknown"
        super().__init__(f"{stage.value} cannot be appraised: blocked by {blocker}")


class AppraisalCannotAuthorize(RuntimeError):
    """Typed refusal: appraisal is not authorization.

    A verifier may appraise every stage it can observe. AUTHORIZATION and COMMIT
    are not among them: an appraiser that could resolve them would be the
    authority, and the subject could then appoint its own.
    """

    def __init__(self, stage: SelfImprovementStage) -> None:
        self.stage = stage
        super().__init__(
            f"{stage.value} is reserved to external custody; use authorize_commit"
        )


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(item in "0123456789abcdef" for item in value)


def _require_sha256(**digests: str) -> None:
    for name, digest in digests.items():
        if not _is_sha256(digest):
            raise ValueError(f"{name} must be a SHA-256 hex digest")


def _touches_protected(path: str, prefix: str) -> bool:
    """Deliberately over-broad: a near-miss on a protected path still blocks."""

    return path == prefix.rstrip("/") or path.startswith(prefix)


def _inside_scope(path: str, prefix: str) -> bool:
    """Deliberately narrow: a near-miss on declared scope is outside it."""

    normalized = prefix.rstrip("/")
    return path == normalized or path.startswith(normalized + "/")


def _state(condition: bool) -> HardGateState:
    return HardGateState.PASS if condition else HardGateState.FAIL


@dataclass(frozen=True)
class StagedChangeRequest:
    """What was frozen *before* the candidate existed.

    Every custody anchor the later stages compare against lives here, so the
    candidate cannot nominate its own evaluator, split or scope after the fact.
    """

    request_id: str
    base_revision_hash: str
    observed_failure_artifact_hash: str
    frozen_evaluator_artifact_hash: str
    frozen_fresh_split_manifest_hash: str
    retained_negative_ids: tuple[str, ...] = ()
    scope_path_prefixes: tuple[str, ...] = ()
    declared_independent_axes: tuple[str, ...] = ()
    protected_path_prefixes: tuple[str, ...] = DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES
    gate_contract_frozen_at_round: int | None = None

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("a staged change request needs an id")
        _require_sha256(
            base_revision_hash=self.base_revision_hash,
            observed_failure_artifact_hash=self.observed_failure_artifact_hash,
            frozen_evaluator_artifact_hash=self.frozen_evaluator_artifact_hash,
            frozen_fresh_split_manifest_hash=self.frozen_fresh_split_manifest_hash,
        )
        if not self.protected_path_prefixes:
            raise ValueError("a request with no protected paths protects nothing")
        if any(not item.strip() for item in self.protected_path_prefixes):
            raise ValueError("protected path prefixes cannot be empty")


@dataclass(frozen=True)
class SelfImprovementCandidate:
    """The subject. It holds no field that claims any authority over itself."""

    candidate_id: str
    request_id: str
    base_revision_hash: str
    candidate_revision_hash: str
    patch_artifact_hash: str
    touched_paths: tuple[str, ...]
    producer_process_lineage_hash: str
    created_at_round: int
    development_feedback_case_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not self.request_id.strip():
            raise ValueError("a candidate needs an id and the request it answers")
        _require_sha256(
            base_revision_hash=self.base_revision_hash,
            candidate_revision_hash=self.candidate_revision_hash,
            patch_artifact_hash=self.patch_artifact_hash,
            producer_process_lineage_hash=self.producer_process_lineage_hash,
        )
        if not self.touched_paths:
            raise ValueError("a candidate that touches nothing changes nothing")
        if any(item.startswith("/") or ".." in item.split("/") for item in self.touched_paths):
            raise ValueError("candidate paths must be repository-relative and traversal-free")


@dataclass(frozen=True)
class ReplayEvidence:
    """Does the candidate repair the exact failure that motivated it?"""

    evidence_artifact_id: str
    subject_revision_hash: str
    motivating_failure_artifact_hash: str
    motivating_case_outcome: TransferOutcome
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    retained_negative_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.evidence_artifact_id.strip():
            raise ValueError("replay evidence needs an artifact id")
        _require_sha256(
            subject_revision_hash=self.subject_revision_hash,
            motivating_failure_artifact_hash=self.motivating_failure_artifact_hash,
            producer_process_lineage_hash=self.producer_process_lineage_hash,
            verifier_process_lineage_hash=self.verifier_process_lineage_hash,
        )


@dataclass(frozen=True)
class FreshTransferCase:
    case_id: str
    varied_axis: str
    outcome: TransferOutcome

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("a fresh-transfer case needs an id")


@dataclass(frozen=True)
class FreshTransferEvidence:
    """The sandboxed run against the frozen fresh split."""

    execution_receipt_id: str
    candidate_revision_hash: str
    required_tests_outcome: HardGateState
    split_manifest_hash: str
    split_frozen_at_round: int
    cases: tuple[FreshTransferCase, ...]

    def __post_init__(self) -> None:
        if not self.execution_receipt_id.strip():
            raise ValueError("sandbox evidence needs an execution receipt id")
        _require_sha256(
            candidate_revision_hash=self.candidate_revision_hash,
            split_manifest_hash=self.split_manifest_hash,
        )
        if not self.cases:
            raise ValueError("a fresh split with no cases tests nothing")
        ids = [item.case_id for item in self.cases]
        if len(set(ids)) != len(ids):
            # Silently de-duplicating would let a regression be hidden behind a
            # same-id improvement, which is missing-stage laundering by another
            # name. Conflicting observations of one case are a reason to stop.
            raise ValueError("fresh-transfer case ids must be unique within a split")


@dataclass(frozen=True)
class ProtectedAppraisal:
    """A measurement made under protected custody by a lineage-distinct party."""

    appraisal_id: str
    appraiser_id: str
    appraiser_process_lineage_hash: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluator_frozen_at_round: int
    appraised_at_round: int
    development_delta: float
    fresh_assurance_delta: float
    blocking_invariant_states: tuple[tuple[str, HardGateState], ...]

    def __post_init__(self) -> None:
        if not self.appraisal_id.strip() or not self.appraiser_id.strip():
            raise ValueError("a protected appraisal needs an id and an appraiser")
        _require_sha256(
            appraiser_process_lineage_hash=self.appraiser_process_lineage_hash,
            subject_revision_hash=self.subject_revision_hash,
            evaluator_artifact_hash=self.evaluator_artifact_hash,
        )
        if not self.blocking_invariant_states:
            raise ValueError("an appraisal with no blocking invariants appraises nothing")
        names = [name for name, _ in self.blocking_invariant_states]
        if len(set(names)) != len(names):
            raise ValueError("blocking invariant names must be unique")


@dataclass(frozen=True)
class StageOutcome:
    """One stage's result, or the named reason it was not evaluated."""

    stage: SelfImprovementStage
    state: HardGateState
    contract_fingerprint: str = ""
    reasons: tuple[str, ...] = ()
    passed_gate_ids: tuple[str, ...] = ()
    failed_gate_ids: tuple[str, ...] = ()
    unresolved_gate_ids: tuple[str, ...] = ()
    refusal: StageRefusal | None = None
    blocked_by: SelfImprovementStage | None = None

    @property
    def evaluated(self) -> bool:
        return self.refusal is None


@dataclass(frozen=True)
class StagedGateReceipt:
    """Content-bound and deterministic: no clock, no counter, no ordering luck."""

    receipt_id: str
    content_hash: str
    payload: bytes


@dataclass(frozen=True)
class StagedGateReport:
    """The appraisal. It recommends; it never authorizes.

    There is no total, count or ratio on this report, on `StageOutcome` or on
    `StagedGateReceipt`, for the same reason `HardGateReport` has none: any such
    field is an invitation to offset one stage against another.
    """

    request_id: str
    candidate_id: str
    candidate_revision_hash: str
    base_revision_hash: str
    patch_artifact_hash: str
    producer_process_lineage_hash: str
    appraiser_process_lineage_hash: str
    stages: tuple[StageOutcome, ...]
    verdict: ChangeControlVerdict
    reasons: tuple[str, ...]
    receipt: StagedGateReceipt

    @property
    def authorizes_commit(self) -> bool:
        """Always false, structurally.

        The strongest verdict this gate can reach is a recommendation bound to
        exact candidate/evidence lineage. Promotion is external host authority
        (`authorize_commit`), matching `readiness.py`'s ceiling of
        READY_PENDING_EXTERNAL_ATTESTATION and `ChangeControlResult`'s
        `self_merge_authorized`.
        """

        return False

    def stage(self, stage: SelfImprovementStage) -> StageOutcome:
        for item in self.stages:
            if item.stage is stage:
                return item
        raise KeyError(stage)


_STAGE_REQUIREMENTS: dict[SelfImprovementStage, tuple[HardGateRequirement, ...]] = {
    SelfImprovementStage.PROPOSAL: (
        HardGateRequirement("PROPOSAL_BINDS_ITS_REQUEST", "proposal answers this request"),
        HardGateRequirement("PROPOSAL_BUILDS_ON_THE_DECLARED_BASE", "base revision matches"),
        HardGateRequirement("PROPOSAL_CHANGES_THE_INCUMBENT", "candidate differs from base"),
        HardGateRequirement("PROPOSAL_STAYS_INSIDE_DECLARED_SCOPE", "touches declared scope only"),
        HardGateRequirement(
            "PROPOSAL_LEAVES_PROTECTED_PATHS_UNTOUCHED", "no protected path is touched"
        ),
        HardGateRequirement(
            "CANDIDATE_POSTDATES_ITS_FROZEN_CONTRACT", "gate contract predates the candidate"
        ),
    ),
    SelfImprovementStage.EVIDENCE: (
        HardGateRequirement("REPLAY_EVIDENCE_BINDS_THE_CANDIDATE", "replay judges this revision"),
        HardGateRequirement(
            "REPLAY_EVIDENCE_BINDS_THE_OBSERVED_FAILURE", "replay judges the motivating failure"
        ),
        HardGateRequirement(
            "REPLAY_EVIDENCE_IS_INDEPENDENTLY_VERIFIED", "producer and verifier lineages differ"
        ),
        HardGateRequirement("MOTIVATING_FAILURE_IS_REPAIRED", "the motivating case improved"),
        HardGateRequirement(
            "NEGATIVE_HISTORY_IS_RETAINED", "every retained negative/harmful id survives"
        ),
    ),
    SelfImprovementStage.SANDBOX: (
        HardGateRequirement(
            "SANDBOX_EXECUTION_BINDS_THE_CANDIDATE", "the sandbox ran this revision"
        ),
        HardGateRequirement("REQUIRED_TESTS_PASSED_IN_SANDBOX", "required tests passed"),
        HardGateRequirement("FRESH_SPLIT_IS_THE_FROZEN_SPLIT", "split matches the frozen manifest"),
        HardGateRequirement("FRESH_SPLIT_PREDATES_THE_CANDIDATE", "split was frozen first"),
        HardGateRequirement(
            "FRESH_SPLIT_WAS_NOT_CANDIDATE_FEEDBACK", "no fresh case was development feedback"
        ),
        HardGateRequirement(
            "EVERY_FRESH_CASE_VARIES_A_DECLARED_AXIS", "each case varies a declared axis"
        ),
        HardGateRequirement("NO_FRESH_TRANSFER_HARM", "no fresh case regressed"),
        HardGateRequirement("FRESH_TRANSFER_SHOWS_GAIN", "at least one fresh case improved"),
    ),
    SelfImprovementStage.APPRAISAL: (
        HardGateRequirement("APPRAISAL_BINDS_THE_CANDIDATE", "appraisal judges this revision"),
        HardGateRequirement("APPRAISER_IS_NOT_THE_SUBJECT", "appraiser lineage differs"),
        HardGateRequirement("EVALUATOR_IS_THE_FROZEN_EVALUATOR", "evaluator custody unbroken"),
        HardGateRequirement("EVALUATOR_PREDATES_THE_CANDIDATE", "evaluator was frozen first"),
        HardGateRequirement(
            "CANDIDATE_PREDATES_ITS_APPRAISAL", "the candidate round precedes its appraisal"
        ),
        HardGateRequirement("PROTECTED_INVARIANTS_HOLD", "no protected invariant failed"),
        HardGateRequirement("DEVELOPMENT_TARGET_IMPROVED", "the diagnosed coordinate improved"),
        HardGateRequirement("FRESH_ASSURANCE_DID_NOT_REGRESS", "fresh assurance did not regress"),
    ),
    SelfImprovementStage.AUTHORIZATION: (
        HardGateRequirement(
            "APPRAISAL_RECOMMENDS_HOST_PROMOTION", "every appraisable stage passed"
        ),
        HardGateRequirement("ATTESTATION_BINDS_THIS_APPRAISAL", "attestation cites this receipt"),
        HardGateRequirement("ATTESTATION_BINDS_THIS_CANDIDATE", "attestation cites this revision"),
        HardGateRequirement("AUTHORITY_IS_REGISTERED", "authority is a registered external host"),
        HardGateRequirement("ATTESTATION_SIGNATURE_VERIFIES", "attestation is signed by that host"),
        HardGateRequirement(
            "AUTHORITY_IS_NOT_THE_SUBJECT", "authority lineage is not the producer"
        ),
        HardGateRequirement(
            "AUTHORITY_IS_NOT_THE_APPRAISER", "authority lineage is not the appraiser"
        ),
    ),
    SelfImprovementStage.COMMIT: (
        HardGateRequirement(
            "HOST_APPLIED_THE_CHANGE", "the external host applied the authorized change"
        ),
    ),
}


def staged_gate_contract(
    stage: SelfImprovementStage, *, frozen_at_round: int | None
) -> HardGateContract:
    """One contract per stage, so each has a distinct fingerprint.

    That distinctness is load-bearing: an observation minted under one stage's
    contract and replayed against another fails CONTRACT_INTEGRITY inside the
    primitive, so cross-stage evidence reuse cannot launder a missing stage.
    """

    return HardGateContract(
        contract_id=f"{GATE_ID}:{stage.value}",
        requirements=_STAGE_REQUIREMENTS[stage],
        frozen_at_round=frozen_at_round,
    )


def _observe(
    contract: HardGateContract,
    gate_id: str,
    subject_id: str,
    state: HardGateState,
    evidence_ids: tuple[str, ...],
    detail: str = "",
) -> HardGateObservation:
    return HardGateObservation(
        gate_id=gate_id,
        subject_id=subject_id,
        state=state,
        contract_fingerprint=contract.fingerprint,
        evidence_ids=evidence_ids,
        detail=detail,
    )


def _proposal_observations(
    contract: HardGateContract,
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
) -> tuple[HardGateObservation, ...]:
    subject = candidate.candidate_id
    request_ref = f"request:{request.request_id}"
    patch_ref = f"patch:{candidate.patch_artifact_hash}"

    if request.scope_path_prefixes:
        outside = tuple(
            path
            for path in candidate.touched_paths
            if not any(_inside_scope(path, item) for item in request.scope_path_prefixes)
        )
        scope_state = _state(not outside)
        scope_detail = ",".join(outside)
    else:
        # An undeclared scope is unresolved, not unlimited.
        scope_state = HardGateState.CANNOT_CHECK
        scope_detail = "no declared scope"

    protected = tuple(
        path
        for path in candidate.touched_paths
        if any(_touches_protected(path, item) for item in request.protected_path_prefixes)
    )
    frozen_round = request.gate_contract_frozen_at_round
    chronology = (
        HardGateState.CANNOT_CHECK
        if frozen_round is None
        else _state(frozen_round < candidate.created_at_round)
    )
    return (
        _observe(
            contract,
            "PROPOSAL_BINDS_ITS_REQUEST",
            subject,
            _state(candidate.request_id == request.request_id),
            (request_ref,),
        ),
        _observe(
            contract,
            "PROPOSAL_BUILDS_ON_THE_DECLARED_BASE",
            subject,
            _state(candidate.base_revision_hash == request.base_revision_hash),
            (request_ref, f"base:{request.base_revision_hash}"),
        ),
        _observe(
            contract,
            "PROPOSAL_CHANGES_THE_INCUMBENT",
            subject,
            _state(candidate.candidate_revision_hash != request.base_revision_hash),
            (f"candidate:{candidate.candidate_revision_hash}",),
        ),
        _observe(
            contract,
            "PROPOSAL_STAYS_INSIDE_DECLARED_SCOPE",
            subject,
            scope_state,
            (patch_ref,),
            scope_detail,
        ),
        _observe(
            contract,
            "PROPOSAL_LEAVES_PROTECTED_PATHS_UNTOUCHED",
            subject,
            _state(not protected),
            (patch_ref,),
            ",".join(protected),
        ),
        _observe(
            contract,
            "CANDIDATE_POSTDATES_ITS_FROZEN_CONTRACT",
            subject,
            chronology,
            (request_ref,),
        ),
    )


def _evidence_observations(
    contract: HardGateContract,
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    replay: ReplayEvidence | None,
) -> tuple[HardGateObservation, ...]:
    if replay is None:
        # No observations at all: the primitive reports every requirement as
        # unobserved, which is CANNOT_CHECK and blocks. Fail closed by omission.
        return ()
    subject = candidate.candidate_id
    replay_ref = f"replay:{replay.evidence_artifact_id}"
    repaired = {
        TransferOutcome.IMPROVED: HardGateState.PASS,
        TransferOutcome.UNCHANGED: HardGateState.FAIL,
        TransferOutcome.REGRESSED: HardGateState.FAIL,
        TransferOutcome.NOT_OBSERVED: HardGateState.CANNOT_CHECK,
    }[replay.motivating_case_outcome]
    deleted = tuple(
        sorted(set(request.retained_negative_ids).difference(replay.retained_negative_ids))
    )
    return (
        _observe(
            contract,
            "REPLAY_EVIDENCE_BINDS_THE_CANDIDATE",
            subject,
            _state(replay.subject_revision_hash == candidate.candidate_revision_hash),
            (replay_ref,),
        ),
        _observe(
            contract,
            "REPLAY_EVIDENCE_BINDS_THE_OBSERVED_FAILURE",
            subject,
            _state(
                replay.motivating_failure_artifact_hash
                == request.observed_failure_artifact_hash
            ),
            (replay_ref, f"failure:{request.observed_failure_artifact_hash}"),
        ),
        _observe(
            contract,
            "REPLAY_EVIDENCE_IS_INDEPENDENTLY_VERIFIED",
            subject,
            _state(
                replay.producer_process_lineage_hash != replay.verifier_process_lineage_hash
            ),
            (replay_ref,),
        ),
        _observe(contract, "MOTIVATING_FAILURE_IS_REPAIRED", subject, repaired, (replay_ref,)),
        _observe(
            contract,
            "NEGATIVE_HISTORY_IS_RETAINED",
            subject,
            _state(not deleted),
            (replay_ref,),
            ",".join(deleted),
        ),
    )


def _sandbox_observations(
    contract: HardGateContract,
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    fresh: FreshTransferEvidence | None,
) -> tuple[HardGateObservation, ...]:
    if fresh is None:
        return ()
    subject = candidate.candidate_id
    run_ref = f"sandbox:{fresh.execution_receipt_id}"
    split_ref = f"split:{fresh.split_manifest_hash}"
    cases = tuple(sorted(fresh.cases, key=lambda item: item.case_id))
    outcomes = {item.outcome for item in cases}
    reused = tuple(
        sorted(
            {item.case_id for item in cases}.intersection(candidate.development_feedback_case_ids)
        )
    )

    if not request.declared_independent_axes:
        axis_state = HardGateState.CANNOT_CHECK
        axis_detail = "no declared independent axes"
    else:
        undeclared = tuple(
            item.case_id
            for item in cases
            if item.varied_axis not in request.declared_independent_axes
        )
        axis_state = _state(not undeclared)
        axis_detail = ",".join(undeclared)

    if TransferOutcome.REGRESSED in outcomes:
        harm_state = HardGateState.FAIL
    elif TransferOutcome.NOT_OBSERVED in outcomes:
        harm_state = HardGateState.CANNOT_CHECK
    else:
        harm_state = HardGateState.PASS
    if TransferOutcome.IMPROVED in outcomes:
        gain_state = HardGateState.PASS
    elif TransferOutcome.NOT_OBSERVED in outcomes:
        gain_state = HardGateState.CANNOT_CHECK
    else:
        gain_state = HardGateState.FAIL

    return (
        _observe(
            contract,
            "SANDBOX_EXECUTION_BINDS_THE_CANDIDATE",
            subject,
            _state(fresh.candidate_revision_hash == candidate.candidate_revision_hash),
            (run_ref,),
        ),
        _observe(
            contract,
            "REQUIRED_TESTS_PASSED_IN_SANDBOX",
            subject,
            fresh.required_tests_outcome,
            (run_ref,),
        ),
        _observe(
            contract,
            "FRESH_SPLIT_IS_THE_FROZEN_SPLIT",
            subject,
            _state(fresh.split_manifest_hash == request.frozen_fresh_split_manifest_hash),
            (split_ref, f"request:{request.request_id}"),
        ),
        _observe(
            contract,
            "FRESH_SPLIT_PREDATES_THE_CANDIDATE",
            subject,
            _state(fresh.split_frozen_at_round < candidate.created_at_round),
            (split_ref,),
        ),
        _observe(
            contract,
            "FRESH_SPLIT_WAS_NOT_CANDIDATE_FEEDBACK",
            subject,
            _state(not reused),
            (split_ref,),
            ",".join(reused),
        ),
        _observe(
            contract,
            "EVERY_FRESH_CASE_VARIES_A_DECLARED_AXIS",
            subject,
            axis_state,
            (split_ref,),
            axis_detail,
        ),
        _observe(
            contract,
            "NO_FRESH_TRANSFER_HARM",
            subject,
            harm_state,
            (run_ref, split_ref),
            ",".join(item.case_id for item in cases if item.outcome is TransferOutcome.REGRESSED),
        ),
        _observe(contract, "FRESH_TRANSFER_SHOWS_GAIN", subject, gain_state, (run_ref, split_ref)),
    )


def _appraisal_observations(
    contract: HardGateContract,
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    appraisal: ProtectedAppraisal | None,
) -> tuple[HardGateObservation, ...]:
    if appraisal is None:
        return ()
    subject = candidate.candidate_id
    appraisal_ref = f"appraisal:{appraisal.appraisal_id}"
    invariant_states = {state for _, state in appraisal.blocking_invariant_states}
    if HardGateState.FAIL in invariant_states:
        invariants = HardGateState.FAIL
    elif HardGateState.CANNOT_CHECK in invariant_states:
        invariants = HardGateState.CANNOT_CHECK
    else:
        invariants = HardGateState.PASS
    failed_invariants = tuple(
        sorted(
            name
            for name, state in appraisal.blocking_invariant_states
            if state is HardGateState.FAIL
        )
    )
    return (
        _observe(
            contract,
            "APPRAISAL_BINDS_THE_CANDIDATE",
            subject,
            _state(appraisal.subject_revision_hash == candidate.candidate_revision_hash),
            (appraisal_ref,),
        ),
        _observe(
            contract,
            "APPRAISER_IS_NOT_THE_SUBJECT",
            subject,
            _state(
                appraisal.appraiser_process_lineage_hash
                != candidate.producer_process_lineage_hash
            ),
            (appraisal_ref,),
        ),
        _observe(
            contract,
            "EVALUATOR_IS_THE_FROZEN_EVALUATOR",
            subject,
            _state(
                appraisal.evaluator_artifact_hash == request.frozen_evaluator_artifact_hash
            ),
            (appraisal_ref, f"evaluator:{request.frozen_evaluator_artifact_hash}"),
        ),
        _observe(
            contract,
            "EVALUATOR_PREDATES_THE_CANDIDATE",
            subject,
            _state(appraisal.evaluator_frozen_at_round < candidate.created_at_round),
            (appraisal_ref,),
        ),
        _observe(
            contract,
            "CANDIDATE_PREDATES_ITS_APPRAISAL",
            subject,
            _state(candidate.created_at_round < appraisal.appraised_at_round),
            (appraisal_ref,),
        ),
        _observe(
            contract,
            "PROTECTED_INVARIANTS_HOLD",
            subject,
            invariants,
            (appraisal_ref,),
            ",".join(failed_invariants),
        ),
        _observe(
            contract,
            "DEVELOPMENT_TARGET_IMPROVED",
            subject,
            _state(appraisal.development_delta > 0),
            (appraisal_ref,),
        ),
        _observe(
            contract,
            "FRESH_ASSURANCE_DID_NOT_REGRESS",
            subject,
            _state(appraisal.fresh_assurance_delta > 0),
            (appraisal_ref,),
        ),
    )


def appraise_stage(
    stage: SelfImprovementStage,
    *,
    contract: HardGateContract,
    observations: Sequence[HardGateObservation],
    subject_id: str,
    round_index: int,
    preceding: Sequence[StageOutcome] = (),
) -> StageOutcome:
    """Appraise one stage, refusing out-of-order and out-of-competence attempts.

    `preceding` must be exactly the ordered prefix of `STAGE_ORDER` before
    `stage`, every entry PASS. Anything else raises `StageOutOfOrder`; asking for
    AUTHORIZATION or COMMIT raises `AppraisalCannotAuthorize`. Neither is a
    silent skip, and neither returns a value a caller could mistake for a pass.
    """

    if stage in RESERVED_STAGES:
        raise AppraisalCannotAuthorize(stage)
    expected = STAGE_ORDER[: STAGE_ORDER.index(stage)]
    if tuple(item.stage for item in preceding) != expected:
        raise StageOutOfOrder(stage, detail="incomplete_predecessor_chain")
    for item in preceding:
        if item.state is not HardGateState.PASS:
            raise StageOutOfOrder(stage, blocked_by=item.stage, blocking_state=item.state)
    report = evaluate_hard_gates(
        contract, observations, subject_id=subject_id, round_index=round_index
    )
    return StageOutcome(
        stage=stage,
        state=report.state,
        contract_fingerprint=contract.fingerprint,
        reasons=report.reasons,
        passed_gate_ids=report.passed_gate_ids,
        failed_gate_ids=report.failed_gate_ids,
        unresolved_gate_ids=report.unresolved_gate_ids,
    )


def _known_harms(
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    replay: ReplayEvidence | None,
    fresh: FreshTransferEvidence | None,
    appraisal: ProtectedAppraisal | None,
) -> tuple[str, ...]:
    """Scan every supplied record for facts that are known-bad on their own.

    Issue #141: "any known fail/harm dominates missing earlier stages". Ordering
    alone would let a candidate leave PROPOSAL unobserved so that a supplied
    SANDBOX regression is never reached, and collect CANDIDATE_ONLY instead of
    REJECT. This scan can only lower the verdict floor: it never credits a
    later stage, and a stage that was refused still reports zero passed gates.
    """

    harms: list[str] = []
    for path in candidate.touched_paths:
        if any(_touches_protected(path, item) for item in request.protected_path_prefixes):
            harms.append(f"known_harm:protected_path_touched:{path}")
    if replay is not None:
        deleted = sorted(
            set(request.retained_negative_ids).difference(replay.retained_negative_ids)
        )
        harms.extend(f"known_harm:negative_history_deleted:{item}" for item in deleted)
    if fresh is not None:
        if fresh.required_tests_outcome is HardGateState.FAIL:
            harms.append("known_harm:required_tests_failed")
        harms.extend(
            f"known_harm:fresh_transfer_regression:{item.case_id}"
            for item in sorted(fresh.cases, key=lambda case: case.case_id)
            if item.outcome is TransferOutcome.REGRESSED
        )
    if appraisal is not None:
        harms.extend(
            f"known_harm:protected_invariant_failed:{name}"
            for name, state in sorted(appraisal.blocking_invariant_states)
            if state is HardGateState.FAIL
        )
        if appraisal.fresh_assurance_delta <= 0:
            harms.append("known_harm:fresh_assurance_regressed")
    return tuple(harms)


_META_OVERFIT_HARMS = ("fresh_transfer_regression", "fresh_assurance_regressed")


def _is_meta_overfit_harm(harm: str) -> bool:
    """Classify a harm without assuming it is well-formed.

    An unrecognised harm string is treated as hard, so a malformed reason
    downgrades toward REJECT rather than crashing or being waved through.
    """

    parts = harm.split(":", 2)
    return len(parts) > 1 and parts[1] in _META_OVERFIT_HARMS


def _verdict(
    outcomes: Sequence[StageOutcome],
    harms: tuple[str, ...],
    replay: ReplayEvidence | None,
    appraisal: ProtectedAppraisal | None,
) -> tuple[ChangeControlVerdict, tuple[str, ...]]:
    """Precedence: hard harm > META_OVERFIT > soft harm > FAIL > CANNOT_CHECK.

    META_OVERFIT is named once, as one thing. Development gain accompanied by an
    assurance regression is a single diagnosis about a single candidate; emitting
    "it improved" and "assurance regressed" as two independent reasons invites a
    caller to weigh one against the other, which is the trade this gate refuses.
    """

    appraisable = [item for item in outcomes if item.stage in APPRAISABLE_STAGES]
    hard = tuple(item for item in harms if not _is_meta_overfit_harm(item))
    if hard:
        return ChangeControlVerdict.REJECT, hard

    development_gain = (
        replay is not None and replay.motivating_case_outcome is TransferOutcome.IMPROVED
    ) or (appraisal is not None and appraisal.development_delta > 0)
    # Every harm still standing after the hard branch is by construction an
    # assurance regression: a fresh-case regression or a negative assurance delta.
    assurance_regression = bool(harms)
    if development_gain and assurance_regression:
        return ChangeControlVerdict.META_OVERFIT, (META_OVERFIT_REASON,)
    if harms:
        return ChangeControlVerdict.REJECT, harms

    failed = next((item for item in appraisable if item.state is HardGateState.FAIL), None)
    if failed is not None:
        return ChangeControlVerdict.REJECT, (f"blocked_at_stage:{failed.stage.value}:FAIL",)
    unresolved = next(
        (item for item in appraisable if item.state is HardGateState.CANNOT_CHECK), None
    )
    if unresolved is not None:
        return (
            ChangeControlVerdict.CANDIDATE_ONLY,
            (f"blocked_at_stage:{unresolved.stage.value}:CANNOT_CHECK",),
        )
    return ChangeControlVerdict.RECOMMEND_HOST_PROMOTION, ()


def _receipt(
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    appraiser_lineage: str,
    outcomes: Sequence[StageOutcome],
    verdict: ChangeControlVerdict,
    reasons: tuple[str, ...],
) -> StagedGateReceipt:
    payload = canonical_bytes(
        {
            "gate": GATE_ID,
            "request_id": request.request_id,
            "gate_contract_frozen_at_round": request.gate_contract_frozen_at_round,
            "candidate_id": candidate.candidate_id,
            "candidate_revision_hash": candidate.candidate_revision_hash,
            "base_revision_hash": candidate.base_revision_hash,
            "patch_artifact_hash": candidate.patch_artifact_hash,
            "candidate_created_at_round": candidate.created_at_round,
            "producer_process_lineage_hash": candidate.producer_process_lineage_hash,
            "appraiser_process_lineage_hash": appraiser_lineage,
            "stages": [
                {
                    "stage": item.stage.value,
                    "state": item.state.value,
                    "contract_fingerprint": item.contract_fingerprint,
                    "refusal": item.refusal.value if item.refusal is not None else "",
                    "blocked_by": item.blocked_by.value if item.blocked_by is not None else "",
                    "reasons": list(item.reasons),
                    "passed_gate_ids": list(item.passed_gate_ids),
                    "failed_gate_ids": list(item.failed_gate_ids),
                    "unresolved_gate_ids": list(item.unresolved_gate_ids),
                }
                for item in outcomes
            ],
            "verdict": verdict.value,
            "reasons": list(reasons),
        }
    )
    content_hash = hashlib.sha256(payload).hexdigest()
    return StagedGateReceipt(
        receipt_id=f"staged-gate:{content_hash}",
        content_hash=content_hash,
        payload=payload,
    )


def appraise_staged_self_improvement(
    *,
    request: StagedChangeRequest,
    candidate: SelfImprovementCandidate,
    replay: ReplayEvidence | None = None,
    fresh: FreshTransferEvidence | None = None,
    appraisal: ProtectedAppraisal | None = None,
) -> StagedGateReport:
    """Walk PROPOSAL -> EVIDENCE -> SANDBOX -> APPRAISAL, then stop.

    Ordering is real: once a stage does not PASS, every later stage is refused
    with a named reason and is never evaluated, so no later success can be
    credited — let alone used to offset the earlier block. AUTHORIZATION and
    COMMIT are refused outright: this function is the appraiser, and the
    appraiser is not the authority.

    Chronology is taken from `candidate.created_at_round` rather than a caller
    argument, so the gate contract must have been frozen before the candidate it
    judges; see the module docstring for how that round is sandwiched.
    """

    observations = {
        SelfImprovementStage.PROPOSAL: _proposal_observations,
        SelfImprovementStage.EVIDENCE: _evidence_observations,
        SelfImprovementStage.SANDBOX: _sandbox_observations,
        SelfImprovementStage.APPRAISAL: _appraisal_observations,
    }
    supplied = {
        SelfImprovementStage.PROPOSAL: (),
        SelfImprovementStage.EVIDENCE: (replay,),
        SelfImprovementStage.SANDBOX: (fresh,),
        SelfImprovementStage.APPRAISAL: (appraisal,),
    }

    outcomes: list[StageOutcome] = []
    for stage in APPRAISABLE_STAGES:
        contract = staged_gate_contract(
            stage, frozen_at_round=request.gate_contract_frozen_at_round
        )
        derived = observations[stage](contract, request, candidate, *supplied[stage])
        try:
            outcome = appraise_stage(
                stage,
                contract=contract,
                observations=derived,
                subject_id=candidate.candidate_id,
                round_index=candidate.created_at_round,
                preceding=tuple(outcomes),
            )
        except StageOutOfOrder as refusal:
            blocked_by = refusal.blocked_by
            outcome = StageOutcome(
                stage=stage,
                state=HardGateState.CANNOT_CHECK,
                reasons=(
                    f"stage_not_evaluated:blocked_by:{blocked_by.value}"
                    if blocked_by is not None
                    else "stage_not_evaluated:incomplete_predecessor_chain",
                ),
                refusal=(
                    StageRefusal.PREDECESSOR_FAILED
                    if refusal.blocking_state is HardGateState.FAIL
                    else StageRefusal.PREDECESSOR_UNRESOLVED
                ),
                blocked_by=blocked_by,
            )
        outcomes.append(outcome)

    outcomes.extend(
        StageOutcome(
            stage=stage,
            state=HardGateState.CANNOT_CHECK,
            reasons=("appraisal_may_not_authorize",),
            refusal=StageRefusal.RESERVED_TO_EXTERNAL_AUTHORITY,
        )
        for stage in RESERVED_STAGES
    )

    harms = _known_harms(request, candidate, replay, fresh, appraisal)
    verdict, reasons = _verdict(outcomes, harms, replay, appraisal)
    appraiser_lineage = (
        appraisal.appraiser_process_lineage_hash if appraisal is not None else ""
    )
    return StagedGateReport(
        request_id=request.request_id,
        candidate_id=candidate.candidate_id,
        candidate_revision_hash=candidate.candidate_revision_hash,
        base_revision_hash=candidate.base_revision_hash,
        patch_artifact_hash=candidate.patch_artifact_hash,
        producer_process_lineage_hash=candidate.producer_process_lineage_hash,
        appraiser_process_lineage_hash=appraiser_lineage,
        stages=tuple(outcomes),
        verdict=verdict,
        reasons=reasons,
        receipt=_receipt(
            request, candidate, appraiser_lineage, outcomes, verdict, reasons
        ),
    )


@dataclass(frozen=True)
class ExternalAuthorityRegistration:
    authority_id: str
    verification_key: bytes
    process_lineage_hash: str

    def __post_init__(self) -> None:
        if not self.authority_id.strip():
            raise ValueError("an external authority needs an id")
        if len(self.verification_key) != 32:
            raise ValueError("external authority Ed25519 public key must contain 32 bytes")
        _require_sha256(process_lineage_hash=self.process_lineage_hash)


@dataclass(frozen=True)
class ExternalAuthorityRegistry:
    """Who may authorize. ORION cannot add itself: it has no private keys here."""

    registrations: tuple[ExternalAuthorityRegistration, ...] = ()

    def __post_init__(self) -> None:
        ids = [item.authority_id for item in self.registrations]
        if len(set(ids)) != len(ids):
            raise ValueError("external authority ids must be unique")

    def find(self, authority_id: str) -> ExternalAuthorityRegistration | None:
        return next(
            (item for item in self.registrations if item.authority_id == authority_id), None
        )


@dataclass(frozen=True)
class HostAuthorizationAttestation:
    """An external host's signed statement about one exact appraisal receipt.

    `report_receipt_hash` is the chronology proof and needs no timestamp: a hash
    of an appraisal cannot be cited before that appraisal was computed.
    """

    authority_id: str
    authority_process_lineage_hash: str
    subject_revision_hash: str
    report_receipt_hash: str
    signature: str

    def __post_init__(self) -> None:
        if not self.authority_id.strip():
            raise ValueError("an attestation needs an authority id")
        _require_sha256(
            authority_process_lineage_hash=self.authority_process_lineage_hash,
            subject_revision_hash=self.subject_revision_hash,
            report_receipt_hash=self.report_receipt_hash,
        )


def attestation_payload(attestation: HostAuthorizationAttestation) -> bytes:
    """Exactly the bytes that are signed. Every binding field is inside them."""

    return canonical_bytes(
        {
            "gate": GATE_ID,
            "authority_id": attestation.authority_id,
            "authority_process_lineage_hash": attestation.authority_process_lineage_hash,
            "subject_revision_hash": attestation.subject_revision_hash,
            "report_receipt_hash": attestation.report_receipt_hash,
        }
    )


def mint_host_authorization(
    signing_key: bytes,
    *,
    authority_id: str,
    authority_process_lineage_hash: str,
    subject_revision_hash: str,
    report_receipt_hash: str,
) -> HostAuthorizationAttestation:
    """External host tooling. Inert without the host's private key.

    ORION holds no such key, which is what makes requirement 6 structural rather
    than a matter of ORION choosing not to authorize itself.
    """

    if len(signing_key) != 32:
        raise ValueError("external authority Ed25519 signing key must contain 32 bytes")
    unsigned = HostAuthorizationAttestation(
        authority_id=authority_id,
        authority_process_lineage_hash=authority_process_lineage_hash,
        subject_revision_hash=subject_revision_hash,
        report_receipt_hash=report_receipt_hash,
        signature="0" * 128,
    )
    signature = (
        Ed25519PrivateKey.from_private_bytes(signing_key)
        .sign(attestation_payload(unsigned))
        .hex()
    )
    return HostAuthorizationAttestation(
        authority_id=authority_id,
        authority_process_lineage_hash=authority_process_lineage_hash,
        subject_revision_hash=subject_revision_hash,
        report_receipt_hash=report_receipt_hash,
        signature=signature,
    )


@dataclass(frozen=True)
class CommitAuthorization:
    """The choke point's answer. It reports an external decision; it is not one."""

    subject_revision_hash: str
    authority_id: str
    report_receipt_hash: str
    stage: StageOutcome
    refusals: tuple[str, ...] = ()

    @property
    def host_may_commit(self) -> bool:
        return not self.refusals and self.stage.state is HardGateState.PASS


def _signature_state(
    registration: ExternalAuthorityRegistration | None,
    attestation: HostAuthorizationAttestation,
) -> HardGateState:
    if registration is None:
        # Nothing to verify against: unresolved, never a pass.
        return HardGateState.CANNOT_CHECK
    try:
        signature = bytes.fromhex(attestation.signature)
    except ValueError:
        return HardGateState.FAIL
    try:
        Ed25519PublicKey.from_public_bytes(registration.verification_key).verify(
            signature, attestation_payload(attestation)
        )
    except InvalidSignature:
        return HardGateState.FAIL
    return HardGateState.PASS


def authorize_commit(
    report: StagedGateReport,
    attestation: HostAuthorizationAttestation,
    *,
    registry: ExternalAuthorityRegistry,
) -> CommitAuthorization:
    """The single choke point that holds authorization, and it is not the subject.

    Everything here is recomputed from the receipt's own bytes rather than read
    from the report's typed fields, so editing a verdict without re-minting the
    receipt is caught, and re-minting the receipt invalidates the host signature
    that cites its hash. Lineage independence is checked even for a validly
    signed, registered authority: a registered authority whose process lineage
    is the producer's is still the subject authorizing itself.
    """

    recomputed = hashlib.sha256(report.receipt.payload).hexdigest()
    try:
        payload = json.loads(report.receipt.payload)
        for key in ("candidate_id", "candidate_revision_hash", "verdict", "stages"):
            payload[key]
    except (ValueError, TypeError, KeyError):
        # A receipt nobody can read is unresolved, never authorized.
        return CommitAuthorization(
            subject_revision_hash=report.candidate_revision_hash,
            authority_id=attestation.authority_id,
            report_receipt_hash=recomputed,
            stage=StageOutcome(
                stage=SelfImprovementStage.AUTHORIZATION,
                state=HardGateState.CANNOT_CHECK,
                reasons=("receipt_payload_unreadable",),
            ),
            refusals=("receipt_payload_unreadable",),
        )
    refusals: list[str] = []
    if recomputed != report.receipt.content_hash:
        refusals.append("receipt_payload_tampered")
    if payload["candidate_revision_hash"] != report.candidate_revision_hash:
        refusals.append("receipt_subject_mismatch")
    if payload["verdict"] != report.verdict.value:
        refusals.append("receipt_verdict_mismatch")

    sealed_stages = {item["stage"]: item for item in payload["stages"]}
    appraisable_passed = all(
        sealed_stages.get(stage.value, {}).get("state") == HardGateState.PASS.value
        for stage in APPRAISABLE_STAGES
    )
    recommended = (
        payload["verdict"] == ChangeControlVerdict.RECOMMEND_HOST_PROMOTION.value
        and appraisable_passed
    )
    registration = registry.find(attestation.authority_id)
    registered = (
        registration is not None
        and registration.process_lineage_hash == attestation.authority_process_lineage_hash
    )
    contract = staged_gate_contract(
        SelfImprovementStage.AUTHORIZATION,
        frozen_at_round=payload["gate_contract_frozen_at_round"],
    )
    subject = payload["candidate_id"]
    attestation_ref = f"attestation:{attestation.authority_id}:{attestation.report_receipt_hash}"
    receipt_ref = f"receipt:{recomputed}"
    observations = (
        _observe(
            contract,
            "APPRAISAL_RECOMMENDS_HOST_PROMOTION",
            subject,
            _state(recommended),
            (receipt_ref,),
        ),
        _observe(
            contract,
            "ATTESTATION_BINDS_THIS_APPRAISAL",
            subject,
            _state(attestation.report_receipt_hash == recomputed),
            (attestation_ref, receipt_ref),
        ),
        _observe(
            contract,
            "ATTESTATION_BINDS_THIS_CANDIDATE",
            subject,
            _state(
                attestation.subject_revision_hash == payload["candidate_revision_hash"]
            ),
            (attestation_ref, receipt_ref),
        ),
        _observe(
            contract,
            "AUTHORITY_IS_REGISTERED",
            subject,
            _state(registered),
            (attestation_ref,),
        ),
        _observe(
            contract,
            "ATTESTATION_SIGNATURE_VERIFIES",
            subject,
            _signature_state(registration if registered else None, attestation),
            (attestation_ref,),
        ),
        _observe(
            contract,
            "AUTHORITY_IS_NOT_THE_SUBJECT",
            subject,
            _state(
                attestation.authority_process_lineage_hash
                != payload["producer_process_lineage_hash"]
            ),
            (attestation_ref, receipt_ref),
        ),
        _observe(
            contract,
            "AUTHORITY_IS_NOT_THE_APPRAISER",
            subject,
            _state(
                attestation.authority_process_lineage_hash
                != payload["appraiser_process_lineage_hash"]
            ),
            (attestation_ref, receipt_ref),
        ),
    )
    gate = evaluate_hard_gates(
        contract,
        observations,
        subject_id=subject,
        round_index=payload["candidate_created_at_round"],
    )
    outcome = StageOutcome(
        stage=SelfImprovementStage.AUTHORIZATION,
        state=gate.state,
        contract_fingerprint=contract.fingerprint,
        reasons=gate.reasons,
        passed_gate_ids=gate.passed_gate_ids,
        failed_gate_ids=gate.failed_gate_ids,
        unresolved_gate_ids=gate.unresolved_gate_ids,
    )
    return CommitAuthorization(
        subject_revision_hash=report.candidate_revision_hash,
        authority_id=attestation.authority_id,
        report_receipt_hash=recomputed,
        stage=outcome,
        refusals=tuple(refusals),
    )


__all__ = [
    "APPRAISABLE_STAGES",
    "AppraisalCannotAuthorize",
    "CommitAuthorization",
    "ExternalAuthorityRegistration",
    "ExternalAuthorityRegistry",
    "FreshTransferCase",
    "FreshTransferEvidence",
    "GATE_ID",
    "HostAuthorizationAttestation",
    "META_OVERFIT_REASON",
    "ProtectedAppraisal",
    "RESERVED_STAGES",
    "ReplayEvidence",
    "STAGE_ORDER",
    "SelfImprovementCandidate",
    "SelfImprovementStage",
    "StageOutOfOrder",
    "StageOutcome",
    "StageRefusal",
    "StagedChangeRequest",
    "StagedGateReceipt",
    "StagedGateReport",
    "TransferOutcome",
    "appraise_stage",
    "appraise_staged_self_improvement",
    "attestation_payload",
    "authorize_commit",
    "mint_host_authorization",
    "staged_gate_contract",
]
