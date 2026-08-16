from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvaluationTarget(str, Enum):
    SOURCE_HEAD = "SOURCE_HEAD"
    INTEGRATION_RESULT = "INTEGRATION_RESULT"


class SubjectVerdict(str, Enum):
    VALID_REVISION_AND_TREE = "VALID_REVISION_AND_TREE"
    VALID_REVISION = "VALID_REVISION"
    PARTIALLY_IDENTIFIED_TREE_ONLY = "PARTIALLY_IDENTIFIED_TREE_ONLY"
    INVALID = "INVALID"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class FrozenSubjectSpec:
    source_sha: str
    base_sha: str
    target: EvaluationTarget

    def __post_init__(self) -> None:
        if not self.source_sha:
            raise ValueError("source_sha cannot be empty")
        if not self.base_sha:
            raise ValueError("base_sha cannot be empty")


@dataclass(frozen=True)
class PlatformSubjectObservation:
    source_sha: str
    base_sha: str
    integration_sha: str | None = None
    integration_tree_sha: str | None = None
    externally_observed: bool = True


@dataclass(frozen=True)
class ExecutionSubjectObservation:
    executed_sha: str | None = None
    executed_tree_sha: str | None = None
    externally_observed: bool = True


@dataclass(frozen=True)
class SubjectAttestationReport:
    verdict: SubjectVerdict
    reasons: tuple[str, ...]
    revision_identified: bool
    tree_identified: bool

    @property
    def valid(self) -> bool:
        return self.verdict in {SubjectVerdict.VALID_REVISION_AND_TREE, SubjectVerdict.VALID_REVISION}


def verify_execution_subject(
    spec: FrozenSubjectSpec,
    platform: PlatformSubjectObservation,
    execution: ExecutionSubjectObservation,
) -> SubjectAttestationReport:
    """Keep exact revision identity distinct from matching content-tree identity.

    Reused from RAKL@70f5f7c4. Candidate-reported subject coordinates never
    substitute for independently observed platform/execution coordinates.
    """

    reasons: list[str] = []
    if not platform.externally_observed:
        reasons.append("platform subject coordinates were not externally observed")
    if not execution.externally_observed:
        reasons.append("execution subject coordinates were not externally observed")
    if reasons:
        return SubjectAttestationReport(SubjectVerdict.CANNOT_CHECK, tuple(reasons), False, False)
    if not platform.source_sha or not platform.base_sha:
        return SubjectAttestationReport(SubjectVerdict.CANNOT_CHECK, ("platform source/base identity is incomplete",), False, False)
    if platform.source_sha != spec.source_sha:
        reasons.append("platform source revision differs from frozen source revision")
    if platform.base_sha != spec.base_sha:
        reasons.append("platform base revision differs from frozen base revision")
    if reasons:
        return SubjectAttestationReport(SubjectVerdict.INVALID, tuple(reasons), False, False)

    if spec.target is EvaluationTarget.SOURCE_HEAD:
        if not execution.executed_sha:
            return SubjectAttestationReport(SubjectVerdict.CANNOT_CHECK, ("executed revision was not observed",), False, False)
        if execution.executed_sha != spec.source_sha:
            return SubjectAttestationReport(
                SubjectVerdict.INVALID,
                ("executed revision is not the declared source head",),
                False,
                bool(execution.executed_tree_sha),
            )
        return SubjectAttestationReport(SubjectVerdict.VALID_REVISION, (), True, bool(execution.executed_tree_sha))

    if not platform.integration_sha and not platform.integration_tree_sha:
        return SubjectAttestationReport(SubjectVerdict.CANNOT_CHECK, ("platform integration subject was not observed",), False, False)
    if not execution.executed_sha and not execution.executed_tree_sha:
        return SubjectAttestationReport(SubjectVerdict.CANNOT_CHECK, ("executed integration subject was not observed",), False, False)

    revision_identified = bool(platform.integration_sha and execution.executed_sha and platform.integration_sha == execution.executed_sha)
    tree_identified = bool(platform.integration_tree_sha and execution.executed_tree_sha and platform.integration_tree_sha == execution.executed_tree_sha)
    if platform.integration_tree_sha and execution.executed_tree_sha and platform.integration_tree_sha != execution.executed_tree_sha:
        return SubjectAttestationReport(
            SubjectVerdict.INVALID,
            ("executed tree differs from platform integration tree",),
            revision_identified,
            False,
        )
    if revision_identified and tree_identified:
        return SubjectAttestationReport(SubjectVerdict.VALID_REVISION_AND_TREE, (), True, True)
    if revision_identified:
        return SubjectAttestationReport(
            SubjectVerdict.VALID_REVISION,
            ("integration revision identified; tree not independently bound",),
            True,
            False,
        )
    if tree_identified:
        return SubjectAttestationReport(
            SubjectVerdict.PARTIALLY_IDENTIFIED_TREE_ONLY,
            ("integration content tree identified but exact revision/history identity is unresolved",),
            False,
            True,
        )
    return SubjectAttestationReport(
        SubjectVerdict.INVALID,
        ("executed subject does not match the declared integration subject",),
        False,
        False,
    )


__all__ = [
    "EvaluationTarget",
    "ExecutionSubjectObservation",
    "FrozenSubjectSpec",
    "PlatformSubjectObservation",
    "SubjectAttestationReport",
    "SubjectVerdict",
    "verify_execution_subject",
]
