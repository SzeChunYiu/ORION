from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from orion.self_orion.change_control import CandidateExecutionReceipt

from .artifacts import DevelopmentArtifactStore
from .base import DevelopmentChangeProposal


@dataclass(frozen=True)
class SandboxExecutionResult:
    candidate_revision_hash: str
    passed_required_tests: bool
    test_result_ids: tuple[str, ...]
    failure_signatures: tuple[str, ...]
    resource_units: float
    artifact_ids: tuple[str, ...]


class SandboxPatchExecutor(Protocol):
    """Host-owned isolated workspace executor for a content-bound patch."""

    def execute_patch(
        self,
        *,
        base_revision: str,
        patch: bytes,
        touched_paths: tuple[str, ...],
        test_plan: tuple[str, ...],
    ) -> SandboxExecutionResult: ...


class ArtifactBackedSandboxCandidateRunner:
    """Resolve exact patch bytes and delegate only to an isolated host executor."""

    def __init__(self, *, artifact_store: DevelopmentArtifactStore, executor: SandboxPatchExecutor) -> None:
        self._artifact_store = artifact_store
        self._executor = executor

    def execute(self, proposal: DevelopmentChangeProposal) -> CandidateExecutionReceipt:
        patch = self._artifact_store.get(proposal.patch_artifact_id)
        digest = hashlib.sha256(patch).hexdigest()
        if digest != proposal.patch_artifact_hash:
            raise ValueError("development patch artifact content hash mismatch")
        result = self._executor.execute_patch(
            base_revision=proposal.base_revision,
            patch=patch,
            touched_paths=proposal.touched_paths,
            test_plan=proposal.test_plan,
        )
        if len(result.candidate_revision_hash) != 64 or any(ch not in "0123456789abcdef" for ch in result.candidate_revision_hash):
            raise ValueError("sandbox executor must return a SHA-256 candidate revision hash")
        if result.resource_units < 0:
            raise ValueError("sandbox execution resource units cannot be negative")
        receipt_seed = f"{proposal.proposal_id}|{proposal.patch_artifact_hash}|{result.candidate_revision_hash}|{result.test_result_ids}"
        receipt_id = "candidate-execution:" + hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()
        return CandidateExecutionReceipt(
            receipt_id=receipt_id,
            proposal_id=proposal.proposal_id,
            candidate_revision_hash=result.candidate_revision_hash,
            passed_required_tests=result.passed_required_tests,
            test_result_ids=result.test_result_ids,
            failure_signatures=result.failure_signatures,
            resource_units=result.resource_units,
            artifact_ids=tuple(dict.fromkeys((proposal.patch_artifact_id, *result.artifact_ids))),
        )


__all__ = [
    "ArtifactBackedSandboxCandidateRunner",
    "SandboxExecutionResult",
    "SandboxPatchExecutor",
]
