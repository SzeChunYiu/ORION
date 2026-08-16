from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    STATIC = "STATIC"
    REPLAY = "REPLAY"
    FRESH = "FRESH"
    PROTECTED = "PROTECTED"


class StageVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class CandidateVerdict(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    REJECT = "REJECT"
    CANNOT_CHECK = "CANNOT_CHECK"
    RECOMMEND_HOST_PROMOTION = "RECOMMEND_HOST_PROMOTION"


@dataclass(frozen=True)
class StageResult:
    stage: Stage
    verdict: StageVerdict
    score_delta: float = 0.0
    cost: float = 0.0
    harmful: bool = False

    def __post_init__(self) -> None:
        if self.cost < 0:
            raise ValueError("cost must be non-negative")


@dataclass
class CandidateRecord:
    candidate_id: str
    results: dict[Stage, StageResult] = field(default_factory=dict)

    def record(self, result: StageResult) -> None:
        if result.stage in self.results:
            raise ValueError(f"stage {result.stage} already recorded")
        self.results[result.stage] = result

    @property
    def total_cost(self) -> float:
        return sum(result.cost for result in self.results.values())


class CandidateArchive:
    def __init__(self) -> None:
        self._records: dict[str, CandidateRecord] = {}

    def retain(self, record: CandidateRecord) -> None:
        self._records[record.candidate_id] = record

    def get(self, candidate_id: str) -> CandidateRecord:
        return self._records[candidate_id]

    def __len__(self) -> int:
        return len(self._records)


class MultiStageCandidateGate:
    """Non-compensatory candidate gate.

    Positive replay gains cannot compensate for fresh/protected failures. The terminal is
    only a host promotion *recommendation*, never self-merge authority.
    """

    required_stages = (Stage.STATIC, Stage.REPLAY, Stage.FRESH, Stage.PROTECTED)

    def next_stage(self, record: CandidateRecord) -> Stage | None:
        verdict = self.evaluate(record)
        if verdict in (CandidateVerdict.REJECT, CandidateVerdict.CANNOT_CHECK):
            return None
        for stage in self.required_stages:
            if stage not in record.results:
                return stage
        return None

    def evaluate(self, record: CandidateRecord) -> CandidateVerdict:
        known = tuple(record.results.values())
        if any(result.harmful or result.verdict is StageVerdict.FAIL for result in known):
            return CandidateVerdict.REJECT
        if any(result.verdict is StageVerdict.CANNOT_CHECK for result in known):
            return CandidateVerdict.CANNOT_CHECK
        if any(stage not in record.results for stage in self.required_stages):
            return CandidateVerdict.IN_PROGRESS
        return CandidateVerdict.RECOMMEND_HOST_PROMOTION
