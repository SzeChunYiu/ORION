from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations_with_replacement, islice
from math import comb

from .canonical import canonical_multiset
from .group import GroupSpec, Vector


class CoverageStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL_SLICE = "PARTIAL_SLICE"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"


@dataclass(frozen=True, slots=True)
class Coverage:
    status: CoverageStatus
    total_raw_candidates: int
    raw_start: int
    raw_stop_exclusive: int
    raw_candidates_seen: int
    canonical_accepted: int
    resume_rank: int | None

    @property
    def full_domain_covered(self) -> bool:
        return (
            self.status is CoverageStatus.COMPLETE
            and self.raw_start == 0
            and self.raw_stop_exclusive == self.total_raw_candidates
            and self.raw_candidates_seen == self.total_raw_candidates
        )

    def to_dict(self) -> dict[str, int | str | bool | None]:
        return {
            "schema_version": "nq-engine-a-coverage-v1",
            "status": self.status.value,
            "total_raw_candidates": self.total_raw_candidates,
            "raw_start": self.raw_start,
            "raw_stop_exclusive": self.raw_stop_exclusive,
            "raw_candidates_seen": self.raw_candidates_seen,
            "canonical_accepted": self.canonical_accepted,
            "resume_rank": self.resume_rank,
            "full_domain_covered": self.full_domain_covered,
        }


@dataclass(frozen=True, slots=True)
class OrderlyRun:
    records: tuple[tuple[Vector, ...], ...]
    coverage: Coverage


def generate_canonical_multisets(
    spec: GroupSpec,
    length: int,
    *,
    start_rank: int = 0,
    stop_rank: int | None = None,
    max_raw_candidates: int | None = None,
) -> OrderlyRun:
    if isinstance(length, bool) or not isinstance(length, int) or length < 0:
        raise ValueError("length must be a nonnegative integer")
    if isinstance(start_rank, bool) or not isinstance(start_rank, int) or start_rank < 0:
        raise ValueError("start_rank must be a nonnegative integer")
    if max_raw_candidates is not None and (
        isinstance(max_raw_candidates, bool)
        or not isinstance(max_raw_candidates, int)
        or max_raw_candidates < 1
    ):
        raise ValueError("max_raw_candidates must be a positive integer")
    total = comb(spec.order + length - 1, length)
    end = total if stop_rank is None else stop_rank
    if isinstance(end, bool) or not isinstance(end, int) or end < start_rank or end > total:
        raise ValueError("stop_rank must lie between start_rank and the raw-domain size")
    processed_end = end
    resource_limited = False
    if max_raw_candidates is not None and start_rank + max_raw_candidates < end:
        processed_end = start_rank + max_raw_candidates
        resource_limited = True
    raw = combinations_with_replacement(tuple(spec.elements()), length)
    records: list[tuple[Vector, ...]] = []
    for candidate in islice(raw, start_rank, processed_end):
        if candidate == canonical_multiset(spec, candidate):
            records.append(candidate)
    seen = processed_end - start_rank
    if resource_limited:
        status = CoverageStatus.CANNOT_CHECK_RESOURCE_BOUND
        resume_rank: int | None = processed_end
    elif start_rank == 0 and processed_end == total:
        status = CoverageStatus.COMPLETE
        resume_rank = None
    else:
        status = CoverageStatus.PARTIAL_SLICE
        resume_rank = processed_end
    return OrderlyRun(
        records=tuple(records),
        coverage=Coverage(
            status=status,
            total_raw_candidates=total,
            raw_start=start_rank,
            raw_stop_exclusive=processed_end,
            raw_candidates_seen=seen,
            canonical_accepted=len(records),
            resume_rank=resume_rank,
        ),
    )
