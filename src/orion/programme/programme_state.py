"""The programme state the hostile checks read.

Every field that a check needs is optional and defaults to absent. That is
deliberate: absence must be representable, because a check that cannot
distinguish "no epochs recorded" from "epochs recorded and clean" will report
clean on an empty programme. Absence here produces ``CANNOT_CHECK``, which
blocks exactly as ``FAIL`` does.

Nothing in this module is populated with programme content. Instances exist only
in tests and in callers that supply their own observations; there is no
module-level snapshot standing in for a cycle that did not run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orion.programme.dependency import ReopenEvent
from orion.programme.method_knowledge import MethodKnowledgeRecord
from orion.programme.object_knowledge import ObjectKnowledgeRecord
from orion.programme.search_universe_knowledge import SearchUniverseKnowledgeRecord

EXTERNAL_CUSTODY = "EXTERNAL"
CANDIDATE_CUSTODY = "CANDIDATE"


@dataclass(frozen=True)
class EpochSnapshot:
    """One immutable evaluation epoch, as observed from outside candidate custody."""

    epoch_id: str
    sequence: int
    protected_metric: float | None = None
    fresh_transfer_metric: float | None = None
    worst_family_metric: float | None = None
    evaluator_artifact_hash: str | None = None
    evaluator_custody: str | None = None
    selected_method_ids: tuple[str, ...] = ()
    evaluated_method_ids: tuple[str, ...] = ()
    source_family_evidence_counts: tuple[tuple[str, int], ...] = ()
    negative_history_entry_ids: tuple[str, ...] = ()
    rejected_result_ids: tuple[str, ...] = ()
    harmful_result_ids: tuple[str, ...] = ()
    cycle_failure_interventions: tuple[tuple[str, str], ...] = ()
    protected_evidence_present: bool = False
    conclusion_claimed: bool = False

    @property
    def total_family_evidence(self) -> int:
        return sum(count for _, count in self.source_family_evidence_counts)

    @property
    def source_families(self) -> tuple[str, ...]:
        return tuple(family for family, _ in self.source_family_evidence_counts)


@dataclass(frozen=True)
class ProgrammeState:
    """Everything the anti-collapse checks are allowed to look at."""

    programme_id: str
    epochs: tuple[EpochSnapshot, ...] = ()
    object_records: tuple[ObjectKnowledgeRecord, ...] = ()
    search_universe: SearchUniverseKnowledgeRecord | None = None
    method_records: tuple[MethodKnowledgeRecord, ...] = ()
    reopen_events: tuple[ReopenEvent, ...] = ()
    current_source_versions: tuple[tuple[str, str], ...] = ()
    internal_source_families: tuple[str, ...] = ()
    source_family_share_ceiling: float | None = None
    min_epochs_for_trend: int = 2
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def ordered_epochs(self) -> tuple[EpochSnapshot, ...]:
        return tuple(sorted(self.epochs, key=lambda epoch: epoch.sequence))

    @property
    def source_version_map(self) -> dict[str, str]:
        return dict(self.current_source_versions)


__all__ = [
    "CANDIDATE_CUSTODY",
    "EXTERNAL_CUSTODY",
    "EpochSnapshot",
    "ProgrammeState",
]
