from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass
from enum import Enum

from .cases import Split, load_cases, suite_fingerprint

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
PROTOCOL_PATH = (
    REPO_ROOT / "papers/paper-01-recursive-epistemic-reconstruction/protocol/PROTOCOL_V1.json"
)
CASES_ROOT = REPO_ROOT / "papers/paper-01-recursive-epistemic-reconstruction/protocol/cases"

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
    import subprocess

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

    unresolved: list[str] = []
    if not protocol:
        unresolved.append("protocol_unreadable")
    if not revision:
        unresolved.append("subject_revision_unresolved")
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
    if not bindings.get("subject_model"):
        unresolved.append("subject_model_unbound")

    return ExecutionManifest(
        protocol_id=protocol.get("protocol_version") or protocol.get("protocol_id", ""),
        subject_revision=revision,
        pilot_fingerprint=pilot,
        test_fingerprint=test,
        subject_model=bindings.get("subject_model", ""),
        statistical_code_hash=statistical_code_hash(repo_root),
        stochastic_repeats=protocol.get("statistics", {}).get("stochastic_repeats", 0),
        outcome_accessed=bool(protocol.get("outcome_accessed", False)),
        unresolved=tuple(unresolved),
    )


__all__ = [
    "STATISTICAL_MODULES",
    "ExecutionManifest",
    "FreezeStatus",
    "build_manifest",
    "statistical_code_hash",
]
