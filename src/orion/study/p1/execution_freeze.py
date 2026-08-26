from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from dataclasses import dataclass
from enum import Enum

from .cases import Split, load_cases, suite_fingerprint
from .precision_tier import TierRule

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
PROTOCOL_PATH = (
    REPO_ROOT / "papers/orion-11-recursive-epistemic-reconstruction/protocol/PROTOCOL_V1.json"
)
CASES_ROOT = REPO_ROOT / "papers/orion-11-recursive-epistemic-reconstruction/protocol/cases"

#: Modules whose content decides what a number means. Their hash is part of the
#: execution identity: the same archive scored by different statistics is a
#: different result, and a manifest that pinned only the data would not say so.
STATISTICAL_MODULES = (
    "src/orion/study/p1/metrics.py",
    "src/orion/study/p1/statistics.py",
    "src/orion/study/p1/score_archive.py",
)


class FreezeStatus(str, Enum):
    """Whether the study may access final outcomes.

    EXECUTION_FROZEN is not a formality. Once outcomes are visible, every
    remaining design choice — which margin, which comparator, whether a suite is
    large enough — can be made knowing which choice flatters the result. The
    freeze is what makes `outcome_accessed: false` mean something, and it must
    be checkable rather than asserted.
    """

    EXECUTION_FROZEN = "EXECUTION_FROZEN"
    #: A scientific identity is unresolved. Not a failure, and not a licence to
    #: run: the study is simply not ready to be executed against outcomes.
    IDENTITIES_UNRESOLVED = "IDENTITIES_UNRESOLVED"
    #: Outcomes have already been read. Nothing can re-freeze after that; the
    #: honest record is that this run is not outcome-blind.
    OUTCOME_ALREADY_ACCESSED = "OUTCOME_ALREADY_ACCESSED"


@dataclass(frozen=True)
class ExecutionManifest:
    protocol_id: str
    subject_revision: str
    pilot_fingerprint: str
    test_fingerprint: str
    subject_model: str
    statistical_code_hash: str
    stochastic_repeats: int
    outcome_accessed: bool
    #: Precision tier computed from frozen N
    precision_tier: TierRule
    #: Hash of the adjudication rubric content
    evaluator_hash: str
    #: Model provider configuration (GLM relay pattern)
    model_provider_revisions: str
    unresolved: tuple[str, ...] = ()

    @property
    def status(self) -> FreezeStatus:
        if self.outcome_accessed:
            return FreezeStatus.OUTCOME_ALREADY_ACCESSED
        if self.unresolved:
            return FreezeStatus.IDENTITIES_UNRESOLVED
        return FreezeStatus.EXECUTION_FROZEN

    @property
    def permits_outcome_access(self) -> bool:
        return self.status is FreezeStatus.EXECUTION_FROZEN

    def to_dict(self) -> dict:
        return {
            "protocol_id": self.protocol_id,
            "subject_revision": self.subject_revision,
            "pilot_fingerprint": self.pilot_fingerprint,
            "test_fingerprint": self.test_fingerprint,
            "subject_model": self.subject_model,
            "statistical_code_hash": self.statistical_code_hash,
            "stochastic_repeats": self.stochastic_repeats,
            "outcome_accessed": self.outcome_accessed,
            "precision_tier": self.precision_tier.to_dict(),
            "evaluator_hash": self.evaluator_hash,
            "model_provider_revisions": self.model_provider_revisions,
            "status": self.status.value,
            "unresolved": list(self.unresolved),
        }


def statistical_code_hash(repo_root: pathlib.Path = REPO_ROOT) -> str:
    """One digest over the modules that decide what a number means."""

    digest = hashlib.sha256()
    for relative in STATISTICAL_MODULES:
        path = repo_root / relative
        digest.update(relative.encode())
        digest.update(path.read_bytes() if path.is_file() else b"<absent>")
    return digest.hexdigest()


def _subject_revision(repo_root: pathlib.Path) -> str:
    """Current git HEAD, bound as the scientific identity of the code."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _evaluator_hash(repo_root: pathlib.Path) -> str:
    """Content hash of the adjudication rubric, which defines the gold standard."""
    rubric_path = (
        repo_root
        / "papers/orion-11-recursive-epistemic-reconstruction/protocol/ADJUDICATION_RUBRIC_V1.md"
    )
    if not rubric_path.is_file():
        return ""
    digest = hashlib.sha256()
    digest.update(rubric_path.read_text(encoding="utf-8").encode())
    return digest.hexdigest()


def _model_provider_revisions() -> str:
    """The GLM relay pattern established by PR #184 and used in PR #207.

    The provider is bound by its INTERFACE contract (Anthropic-compatible API),
    not by a specific deployment — what matters is that the model is glm-5.2
    reached via api2.cmkey.cn/v1 with ANTHROPIC_API_KEY credentialing.

    This is a textual binding, not a content hash, because the provider endpoint
    is environmentally configured (ANTHROPIC_BASE_URL) and the credential is a
    runtime secret (ANTHROPIC_API_KEY) that must never appear in the archive.

    PR #184 fixed BASE_URL to api2.cmkey.cn/v1 for P4 live GLM-5.2.
    PR #207 landed GLM-5.2 campaign artifacts for P4.
    P1 reuses the same provider pattern via src/orion/study/p1/provider.py.
    """
    return "glm-5.2-via-anthropic-compatible-relay@api2.cmkey.cn/v1"


def build_manifest(
    *,
    repo_root: pathlib.Path = REPO_ROOT,
    protocol_path: pathlib.Path | None = None,
    cases_root: pathlib.Path | None = None,
) -> ExecutionManifest:
    """Bind every scientific identity, and name the ones that are missing.

    A credential is deliberately not among them. It is a runtime secret, not a
    scientific identity, and requiring it here would conflate "we do not know
    what we are measuring" with "we cannot reach the provider" — two different
    states that this study has to keep apart.
    """

    protocol_path = protocol_path or PROTOCOL_PATH
    cases_root = cases_root or CASES_ROOT
    protocol = json.loads(protocol_path.read_text()) if protocol_path.is_file() else {}
    bindings = protocol.get("execution_bindings", {})
    datasets = bindings.get("dataset_revisions", {})

    pilot = suite_fingerprint(load_cases(cases_root, split=Split.PILOT))
    test = suite_fingerprint(load_cases(cases_root, split=Split.TEST))
    revision = _subject_revision(repo_root)
    evaluator = _evaluator_hash(repo_root)
    provider = _model_provider_revisions()

    # Count TEST cases for precision tier
    test_cases = load_cases(cases_root, split=Split.TEST)
    n_test = len(test_cases)
    precision_tier = TierRule.from_n(n_test)

    unresolved: list[str] = []
    if not protocol:
        unresolved.append("protocol_unreadable")
    if not revision:
        unresolved.append("subject_revision_unresolved")
    if not evaluator:
        unresolved.append("evaluator_hash_unresolved")
    if not bindings.get("subject_model"):
        unresolved.append("subject_model_unbound")

    # Check dataset fingerprints
    for name, declared in (
        ("hidden_shift_suite_pilot", pilot),
        ("hidden_shift_suite_test", test),
    ):
        bound = datasets.get(name)
        if not bound or bound.startswith("UNBOUND"):
            unresolved.append(f"dataset_unbound:{name}")
        elif bound != declared:
            # A bound hash that does not match the suite on disk is worse than
            # an unbound one: it asserts an identity the artifacts contradict.
            unresolved.append(f"dataset_hash_mismatch:{name}")

    # Check model_provider_revisions binding
    declared_provider = bindings.get("model_provider_revisions")
    if not declared_provider or declared_provider.startswith("UNBOUND"):
        unresolved.append("model_provider_revisions_unbound")
    elif declared_provider != provider:
        unresolved.append("model_provider_revisions_mismatch")

    # Check evaluator_hash binding
    declared_evaluator = bindings.get("evaluator_hash")
    if not declared_evaluator or declared_evaluator.startswith("UNBOUND"):
        unresolved.append("evaluator_hash_unbound")
    elif declared_evaluator != evaluator:
        unresolved.append("evaluator_hash_mismatch")

    # Check baseline_config_hashes binding
    declared_baselines = bindings.get("baseline_config_hashes")
    if not declared_baselines or declared_baselines.startswith("UNBOUND"):
        unresolved.append("baseline_config_hashes_unbound")

    # Check evaluation_epoch binding
    declared_epoch = bindings.get("evaluation_epoch")
    if not declared_epoch or declared_epoch.startswith("UNBOUND"):
        unresolved.append("evaluation_epoch_unbound")

    return ExecutionManifest(
        protocol_id=protocol.get("protocol_version") or protocol.get("protocol_id", ""),
        subject_revision=revision,
        pilot_fingerprint=pilot,
        test_fingerprint=test,
        subject_model=bindings.get("subject_model", ""),
        statistical_code_hash=statistical_code_hash(repo_root),
        stochastic_repeats=protocol.get("statistics", {}).get("stochastic_repeats", 0),
        outcome_accessed=bool(protocol.get("outcome_accessed", False)),
        precision_tier=precision_tier,
        evaluator_hash=evaluator,
        model_provider_revisions=provider,
        unresolved=tuple(unresolved),
    )


__all__ = [
    "STATISTICAL_MODULES",
    "ExecutionManifest",
    "FreezeStatus",
    "build_manifest",
    "statistical_code_hash",
]
