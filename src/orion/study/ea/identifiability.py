"""Evaluator-side information sufficiency for ORION-EA exact cases.

A view is non-identifying when two valid EA cases have the same model-visible
fingerprint but require different minimal gold deltas.  The resulting ceiling is
an exact finite-sample information bound, not a claim about any model family.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from typing import Sequence

from .exact_worlds import ExactCase, ViewMode


@dataclass(frozen=True)
class IdentifiabilityCollision:
    fingerprint: str
    case_ids: tuple[str, ...]
    targets: tuple[str, ...]


@dataclass(frozen=True)
class IdentifiabilityReport:
    mode: ViewMode
    sample_count: int
    unique_fingerprint_count: int
    deterministic_accuracy_ceiling: float
    collisions: tuple[IdentifiabilityCollision, ...]

    @property
    def is_identifying(self) -> bool:
        return not self.collisions


def _target_key(case: ExactCase) -> str:
    return json.dumps(
        [[op.kind.value, op.target_id, op.value] for op in case.gold_delta],
        sort_keys=True,
        separators=(",", ":"),
    )


def analyze_identifiability(
    cases: Sequence[ExactCase],
    mode: ViewMode,
) -> IdentifiabilityReport:
    if not cases:
        raise ValueError("at least one EA case is required")

    seen_case_ids: set[str] = set()
    groups: dict[str, list[ExactCase]] = {}
    for case in cases:
        case.verify()
        if case.case_id in seen_case_ids:
            raise ValueError(f"duplicate case id: {case.case_id}")
        seen_case_ids.add(case.case_id)
        groups.setdefault(case.fingerprint(mode), []).append(case)

    collisions: list[IdentifiabilityCollision] = []
    ceiling_correct = 0
    for fingerprint, group in groups.items():
        target_counts = Counter(_target_key(case) for case in group)
        targets = tuple(sorted(target_counts))
        ceiling_correct += max(target_counts.values())
        if len(targets) > 1:
            collisions.append(
                IdentifiabilityCollision(
                    fingerprint=fingerprint,
                    case_ids=tuple(sorted(case.case_id for case in group)),
                    targets=targets,
                )
            )

    collisions.sort(key=lambda item: (item.fingerprint, item.case_ids, item.targets))
    return IdentifiabilityReport(
        mode=mode,
        sample_count=len(cases),
        unique_fingerprint_count=len(groups),
        deterministic_accuracy_ceiling=ceiling_correct / len(cases),
        collisions=tuple(collisions),
    )
