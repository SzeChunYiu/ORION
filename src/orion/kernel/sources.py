from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from orion.mechanics.answers import AnswerRecord, load_answer_records
from orion.mechanics.model import MechanicCell
from orion.mechanics.research import MechanicResearchTask


@dataclass
class DirectoryAnswerSource:
    """Read candidate answers from a per-lane JSONL inbox on disk.

    This keeps the answering worker outside the kernel: an LLM lane, a
    transfer lane or a person all deliver the same typed record, and the
    kernel's gate treats them identically. Records already consumed by an
    earlier round are not re-offered, so a resumed run does not re-grade its
    own history.
    """

    root: Path
    consumed: set[str] = field(default_factory=set)

    def fetch(
        self,
        tasks: tuple[MechanicResearchTask, ...],
        cells: tuple[MechanicCell, ...],
        round_index: int,
    ) -> tuple[AnswerRecord, ...]:
        del cells, round_index
        if not self.root.is_dir():
            return ()
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        available = load_answer_records(self.root)
        selected = tuple(
            record
            for record in available
            if record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
        )
        self.consumed.update(record.record_id for record in selected)
        return selected

    def offers(
        self, tasks: tuple[MechanicResearchTask, ...], cells: tuple[MechanicCell, ...]
    ) -> bool:
        """Whether unconsumed answers exist for these tasks, without consuming.

        The stop condition asks this before calling a run flat, so the probe
        must not itself consume: a check that spent what it was measuring would
        make the next round's emptiness its own doing.
        """

        del cells
        if not self.root.is_dir():
            return False
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        return any(
            record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
            for record in load_answer_records(self.root)
        )


@dataclass
class StaticAnswerSource:
    """Serve a fixed batch of records once, for benchmarks and replay tests."""

    records: tuple[AnswerRecord, ...] = ()
    consumed: set[str] = field(default_factory=set)

    def fetch(
        self,
        tasks: tuple[MechanicResearchTask, ...],
        cells: tuple[MechanicCell, ...],
        round_index: int,
    ) -> tuple[AnswerRecord, ...]:
        del cells, round_index
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        selected = tuple(
            record
            for record in self.records
            if record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
        )
        self.consumed.update(record.record_id for record in selected)
        return selected

    def offers(
        self, tasks: tuple[MechanicResearchTask, ...], cells: tuple[MechanicCell, ...]
    ) -> bool:
        del cells
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        return any(
            record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
            for record in self.records
        )


@dataclass
class CallableAnswerSource:
    """Serve records produced by a supplier, once each.

    Lets a lane deliver answers from code rather than a JSONL inbox without the
    kernel knowing or caring which, since the gate judges a record by its
    evidence, its lane and its check — never by how it arrived.
    """

    supplier: object
    consumed: set[str] = field(default_factory=set)

    def fetch(
        self,
        tasks: tuple[MechanicResearchTask, ...],
        cells: tuple[MechanicCell, ...],
        round_index: int,
    ) -> tuple[AnswerRecord, ...]:
        del round_index
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        available = self.supplier(cells)  # type: ignore[operator]
        selected = tuple(
            record
            for record in available
            if record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
        )
        self.consumed.update(record.record_id for record in selected)
        return selected

    def offers(
        self, tasks: tuple[MechanicResearchTask, ...], cells: tuple[MechanicCell, ...]
    ) -> bool:
        wanted = {(item.mechanic_id, item.dimension) for item in tasks}
        return any(
            record.record_id not in self.consumed
            and (record.mechanic_id, record.dimension) in wanted
            for record in self.supplier(cells)  # type: ignore[operator]
        )
