from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES = (
    ".github/workflows/",
    "src/orion/self_orion/readiness.py",
    "src/orion/experience/authority.py",
    "src/orion/registry.py",
)


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

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.request_id, self.mechanic_id, self.problem_statement, self.base_revision, self.falsifier)):
            raise ValueError("development request identity/mechanic/problem/base/falsifier are required")
        if not self.protected_constraints or not self.required_tests:
            raise ValueError("development request requires protected constraints and tests")
        if any(not item.strip() for item in self.protected_path_prefixes):
            raise ValueError("protected path prefixes cannot be empty")


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


class DevelopmentChangeProvider(Protocol):
    """Coding/implementation worker used by Self-ORION.

    The provider may be an LLM/coding agent, program synthesizer, human-assisted tool,
    or deterministic transformer. It returns proposal artifacts only.
    """

    def propose(self, request: DevelopmentChangeRequest) -> DevelopmentChangeProposal: ...


__all__ = [
    "DEFAULT_PROTECTED_DEVELOPMENT_PATH_PREFIXES",
    "DevelopmentChangeProvider",
    "DevelopmentChangeProposal",
    "DevelopmentChangeRequest",
]
