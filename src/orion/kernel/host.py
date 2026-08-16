"""Protected host composition for transition appraisal/authorization.

The ordinary ORION candidate path never receives this service, its signer, or
its protected states. Host deployment constructs it from independently
installed material. Its public operation accepts a frozen plan and an already
signed verifier appraisal; it never accepts raw key bytes, registries, trust
stores, evaluator callables, or caller-provided pass flags.
"""

from __future__ import annotations

from dataclasses import dataclass

from .assurance import VerifierAppraisal
from .authority_state import AuthorityState, SupportState
from .authorization import (
    AuthorizationContext,
    AuthorizationDecision,
    ProtectedAuthorizationSigner,
    TransitionAuthorization,
    authorize_transition,
    seal_authorization,
)
from .transition import LedgerExpectation, canonical_digest
from .transition_reducer import TransitionPlan


@dataclass(frozen=True)
class ProtectedHostManifest:
    manifest_id: str
    evaluator_registration_id: str
    policy_registration_id: str
    authorization_key_registration_id: str
    trust_root_registration_id: str
    artifact_hash: str

    def __post_init__(self) -> None:
        values = (
            self.manifest_id,
            self.evaluator_registration_id,
            self.policy_registration_id,
            self.authorization_key_registration_id,
            self.trust_root_registration_id,
        )
        if any(not item.strip() for item in values):
            raise ValueError("protected host manifest identities are required")
        if len(self.artifact_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.artifact_hash
        ):
            raise ValueError("protected host manifest artifact_hash must be SHA-256")

    @property
    def commitment(self) -> str:
        return canonical_digest(
            {
                "manifest_id": self.manifest_id,
                "evaluator_registration_id": self.evaluator_registration_id,
                "policy_registration_id": self.policy_registration_id,
                "authorization_key_registration_id": self.authorization_key_registration_id,
                "trust_root_registration_id": self.trust_root_registration_id,
                "artifact_hash": self.artifact_hash,
            },
            domain="orion.protected-host-manifest.v1",
        )


@dataclass(frozen=True)
class ProtectedHostDecision:
    decision: AuthorizationDecision
    authorization: TransitionAuthorization | None

    @property
    def authorized(self) -> bool:
        return (
            self.authorization is not None
            and self.authorization.authorizes_state_change
        )


class ProtectedHostAuthorizationService:
    """Host-owned authorization service; not exposed through candidate APIs."""

    def __init__(
        self,
        *,
        manifest: ProtectedHostManifest,
        authority_state: AuthorityState,
        support_state: SupportState,
        signer: ProtectedAuthorizationSigner,
    ) -> None:
        if signer.registration_id != manifest.authorization_key_registration_id:
            raise ValueError("installed signer does not match host manifest")
        self._manifest = manifest
        self._authority_state = authority_state
        self._support_state = support_state
        self._signer = signer

    @property
    def manifest(self) -> ProtectedHostManifest:
        return self._manifest

    @property
    def authority_state(self) -> AuthorityState:
        return self._authority_state

    @property
    def support_state(self) -> SupportState:
        return self._support_state

    @property
    def authority_revision(self) -> str:
        return self._authority_state.revision

    @property
    def support_revision(self) -> str:
        return self._support_state.revision

    def authorize(
        self,
        *,
        plan: TransitionPlan,
        appraisal: VerifierAppraisal,
        current_expectation: LedgerExpectation,
        chronology_frozen_before_candidate: bool,
    ) -> ProtectedHostDecision:
        context = AuthorizationContext(
            plan=plan,
            appraisal=appraisal,
            authority_state=self._authority_state,
            support_state=self._support_state,
            current_expectation=current_expectation,
            evaluator_registration_id=self._manifest.evaluator_registration_id,
            policy_registration_id=self._manifest.policy_registration_id,
            authorization_key_registration_id=self._manifest.authorization_key_registration_id,
            trust_root_registration_id=self._manifest.trust_root_registration_id,
            chronology_frozen_before_candidate=chronology_frozen_before_candidate,
        )
        decision = authorize_transition(context)
        if not decision.authorizes_state_change:
            return ProtectedHostDecision(decision, None)
        return ProtectedHostDecision(
            decision,
            seal_authorization(decision, signer=self._signer),
        )


__all__ = [
    "ProtectedHostAuthorizationService",
    "ProtectedHostDecision",
    "ProtectedHostManifest",
]
