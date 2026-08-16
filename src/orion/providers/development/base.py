from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES = (
    ".github/workflows/",
    "src/orion/self_orion/readiness.py",
    "src/orion/experience/authority.py",
    "src/orion/registry.py",
)


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


@dataclass(frozen=True)
class DevelopmentChangeRequest:
    request_id: str
    mechanic_id: str
    problem_statement: str
    base_revision: str
    evidence_ids: tuple[str, ...]
    failure_episode_ids: tuple[str, ...]
    protected_constraints: tuple[str, ...]
    required_tests: tuple[str, ...]
    falsifier: str
    protected_path_prefixes: tuple[str, ...] = DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES
    development_issue_id: str = ""
    observed_failure_artifact_hash: str = ""
    candidate_cause_ids: tuple[str, ...] = ()
    supported_cause_id: str = ""
    discriminator_artifact_hash: str = ""
    discriminator_evidence_ids: tuple[str, ...] = ()
    negative_alternative_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.request_id, self.mechanic_id, self.problem_statement, self.base_revision, self.falsifier)):
            raise ValueError("development request identity/mechanic/problem/base/falsifier are required")
        if not self.protected_constraints or not self.required_tests:
            raise ValueError("development request requires protected constraints and tests")
        if any(not item.strip() for item in self.protected_path_prefixes):
            raise ValueError("protected path prefixes cannot be empty")

        failure_bound = bool(
            self.development_issue_id
            or self.observed_failure_artifact_hash
            or self.candidate_cause_ids
            or self.supported_cause_id
            or self.discriminator_artifact_hash
            or self.discriminator_evidence_ids
            or self.negative_alternative_ids
        )
        if failure_bound:
            if any(
                not value.strip()
                for value in (
                    self.development_issue_id,
                    self.supported_cause_id,
                )
            ):
                raise ValueError("observed-failure development request requires issue and supported-cause identities")
            if not _sha256(self.observed_failure_artifact_hash) or not _sha256(
                self.discriminator_artifact_hash
            ):
                raise ValueError("observed-failure development bindings must use SHA-256 artifact identities")
            if len(self.candidate_cause_ids) < 2:
                raise ValueError("observed-failure development request requires competing cause hypotheses")
            if self.supported_cause_id not in self.candidate_cause_ids:
                raise ValueError("observed-failure supported cause must be one of the candidate causes")
            if not self.discriminator_evidence_ids:
                raise ValueError("observed-failure development request requires discriminator evidence")
            if not self.failure_episode_ids:
                raise ValueError("observed-failure development request requires preserved failure episodes")
            if not self.negative_alternative_ids:
                raise ValueError("observed-failure development request must retain negative/harmful alternatives")

    @property
    def observed_failure_bound(self) -> bool:
        return bool(self.observed_failure_artifact_hash)


@dataclass(frozen=True)
class DevelopmentChangeProposal:
    proposal_id: str
    request_id: str
    base_revision: str
    patch_artifact_id: str
    patch_artifact_hash: str
    touched_paths: tuple[str, ...]
    rationale: str
    expected_effects: tuple[str, ...]
    test_plan: tuple[str, ...]
    falsifier: str
    provenance_ids: tuple[str, ...]
    proposal_only: bool = True

    def __post_init__(self) -> None:
        required = (
            self.proposal_id,
            self.request_id,
            self.base_revision,
            self.patch_artifact_id,
            self.patch_artifact_hash,
            self.rationale,
            self.falsifier,
        )
        if any(not item.strip() for item in required):
            raise ValueError("change proposal identity/base/artifact/hash/rationale/falsifier are required")
        if len(self.patch_artifact_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.patch_artifact_hash):
            raise ValueError("change proposal patch hash must be SHA-256")
        if not self.touched_paths or not self.expected_effects or not self.test_plan:
            raise ValueError("change proposal requires touched paths, effects and tests")
        if any(path.startswith("/") or ".." in path.split("/") for path in self.touched_paths):
            raise ValueError("development proposal paths must be repository-relative and traversal-free")
        if not self.proposal_only:
            raise ValueError("development provider cannot self-assert promotion authority")


@dataclass(frozen=True)
class CandidateExecutionReceipt:
    receipt_id: str
    proposal_id: str
    candidate_revision_hash: str
    passed_required_tests: bool
    test_result_ids: tuple[str, ...]
    failure_signatures: tuple[str, ...]
    resource_units: float
    artifact_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.receipt_id, self.proposal_id, self.candidate_revision_hash)):
            raise ValueError("candidate execution receipt identity fields are required")
        if len(self.candidate_revision_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.candidate_revision_hash):
            raise ValueError("candidate revision hash must be SHA-256")
        if self.resource_units < 0:
            raise ValueError("candidate execution resources cannot be negative")


class DevelopmentChangeProvider(Protocol):
    """Coding/implementation worker used by Self-ORION.

    The provider may be an LLM/coding agent, program synthesizer, human-assisted tool,
    or deterministic transformer. It returns proposal artifacts only.
    """

    def propose(self, request: DevelopmentChangeRequest) -> DevelopmentChangeProposal: ...


__all__ = [
    "CandidateExecutionReceipt",
    "DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES",
    "DevelopmentChangeProvider",
    "DevelopmentChangeProposal",
    "DevelopmentChangeRequest",
]
