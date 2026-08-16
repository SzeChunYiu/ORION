from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BenchmarkStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class BenchmarkReport:
    """One bounded falsifier result.

    `PASS` means only that the registered benchmark obligations passed for this
    case. It never mints scientific authority or a publication novelty claim.
    """

    paper_id: str
    case_id: str
    status: BenchmarkStatus
    metrics: tuple[tuple[str, float], ...] = ()
    blockers: tuple[str, ...] = ()
    observations: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status is BenchmarkStatus.PASS

    @property
    def metric_dict(self) -> dict[str, float]:
        return dict(self.metrics)


def report_from_checks(
    *,
    paper_id: str,
    case_id: str,
    checks: tuple[tuple[str, bool], ...],
    metrics: tuple[tuple[str, float], ...] = (),
    cannot_check: tuple[str, ...] = (),
    observations: tuple[str, ...] = (),
) -> BenchmarkReport:
    if cannot_check:
        return BenchmarkReport(
            paper_id=paper_id,
            case_id=case_id,
            status=BenchmarkStatus.CANNOT_CHECK,
            metrics=metrics,
            blockers=cannot_check,
            observations=observations,
        )
    failed = tuple(name for name, value in checks if not value)
    return BenchmarkReport(
        paper_id=paper_id,
        case_id=case_id,
        status=BenchmarkStatus.FAIL if failed else BenchmarkStatus.PASS,
        metrics=metrics,
        blockers=failed,
        observations=observations,
    )


__all__ = ["BenchmarkReport", "BenchmarkStatus", "report_from_checks"]
