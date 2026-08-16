from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.mechanics.answers import _STRING_FIELDS_BY_DIMENSION
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.program import plan_program_questions
from orion.mechanics.questioning import _PROMPTS, MechanicQuestion

from .gate import DiscriminatingCheck
from .store import EntryKind, LedgerStore


@dataclass(frozen=True)
class WorkItem:
    """One open question, stated so an external lane can answer it.

    Includes the bar the answer must clear. A work order that named the question
    but hid the acceptance criterion would invite answers that cannot pass, and
    the resulting refusals would look like the answerer's failure rather than
    the request's.
    """

    question_id: str
    mechanic_id: str
    dimension: MechanicDimension
    purpose: str
    question: str
    writable_fields: tuple[str, ...]
    checked_by: tuple[str, ...]
    checking_lanes: tuple[str, ...]
    already_attempted_by: tuple[str, ...]

    @property
    def verifiable(self) -> bool:
        """Whether any registered check could promote an answer here."""

        return bool(self.checked_by)

    def as_dict(self) -> dict[str, object]:
        return {
            "question_id": self.question_id,
            "mechanic_id": self.mechanic_id,
            "dimension": self.dimension.value,
            "purpose": self.purpose,
            "question": self.question,
            "writable_fields": list(self.writable_fields),
            "checked_by": list(self.checked_by),
            "checking_lanes": list(self.checking_lanes),
            "already_attempted_by": list(self.already_attempted_by),
            "verifiable": self.verifiable,
        }


@dataclass(frozen=True)
class WorkOrder:
    """What ORION is asking to be answered, and by whom it may not be."""

    items: tuple[WorkItem, ...]
    unverifiable_dimensions: tuple[str, ...]

    def for_lane(self, lane: str) -> tuple[WorkItem, ...]:
        """Items this lane may usefully answer.

        A lane is excluded from work its own checks would have to judge, because
        the gate refuses a check sharing a lane with the answer. Handing a lane
        work it cannot have verified would generate effort that is guaranteed to
        stall at EVIDENCE_BOUND.
        """

        return tuple(
            item
            for item in self.items
            if item.verifiable and lane not in item.checking_lanes
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "items": [item.as_dict() for item in self.items],
            "unverifiable_dimensions": list(self.unverifiable_dimensions),
            "total": len(self.items),
        }


def build_work_order(
    cells: Sequence[MechanicCell],
    *,
    checks: Mapping[str, DiscriminatingCheck] = {},
    store: LedgerStore | None = None,
    limit: int = 200,
) -> WorkOrder:
    """Turn the open audit into a request external lanes can act on.

    This is what lets the loop drive work rather than wait for it. It reports
    which dimensions no registered check can judge at all: answering those
    produces content that cannot rise above EVIDENCE_BOUND, so naming them is
    more useful than silently including them.
    """

    by_dimension: dict[MechanicDimension, list[tuple[str, str]]] = {}
    for check_id, check in sorted(checks.items()):
        by_dimension.setdefault(check.dimension, []).append((check_id, check.lane))

    attempted: dict[tuple[str, str], set[str]] = {}
    if store is not None:
        for entry in store.entries(EntryKind.ANSWER):
            key = (
                str(entry.payload.get("mechanic_id", "")),
                str(entry.payload.get("dimension", "")),
            )
            attempted.setdefault(key, set()).add(str(entry.payload.get("lane", "")))

    cell_by_id = {cell.mechanic_id: cell for cell in cells}
    questions: Sequence[MechanicQuestion] = plan_program_questions(
        tuple(cells), limit=limit
    )

    items: list[WorkItem] = []
    for question in questions:
        cell = cell_by_id.get(question.mechanic_id)
        if cell is None:
            continue
        registered = by_dimension.get(question.dimension, [])
        items.append(
            WorkItem(
                question_id=question.question_id,
                mechanic_id=question.mechanic_id,
                dimension=question.dimension,
                purpose=cell.purpose,
                question=_PROMPTS[question.dimension],
                writable_fields=_STRING_FIELDS_BY_DIMENSION.get(
                    question.dimension, ()
                ),
                checked_by=tuple(item for item, _ in registered),
                checking_lanes=tuple(dict.fromkeys(lane for _, lane in registered)),
                already_attempted_by=tuple(
                    sorted(
                        attempted.get(
                            (question.mechanic_id, question.dimension.value), set()
                        )
                    )
                ),
            )
        )

    covered = {item.value for item in by_dimension}
    unverifiable = tuple(
        sorted({item.dimension.value for item in items} - covered)
    )
    return WorkOrder(items=tuple(items), unverifiable_dimensions=unverifiable)


def write_work_order(order: WorkOrder, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(order.as_dict(), indent=2), encoding="utf-8")
    return path
