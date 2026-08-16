from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.kernel.evidence import expected_binding, resolve_evidence_ref
from orion.mechanics.answers import _STRING_FIELDS_BY_DIMENSION, AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension

from .rakl_transfer import apply_rakl_transfer_profiles, rakl_transfer_receipts

TRANSFER_LANE = "self-orion"


@dataclass(frozen=True)
class TransferAnswerReport:
    """What the transfer produced, and what it could not."""

    records: tuple[AnswerRecord, ...]
    skipped: tuple[tuple[str, int], ...]

    def counts_by_dimension(self) -> tuple[tuple[str, int], ...]:
        tally: dict[str, int] = {}
        for record in self.records:
            tally[record.dimension.value] = tally.get(record.dimension.value, 0) + 1
        return tuple(sorted(tally.items()))


def _delta(base: MechanicCell, applied: MechanicCell, field: str) -> tuple[str, ...]:
    existing = set(getattr(base, field))
    return tuple(item for item in getattr(applied, field) if item not in existing)


def transfer_answer_records(
    cells: Sequence[MechanicCell],
    *,
    evidence_roots: Mapping[str, Path],
    lane: str = TRANSFER_LANE,
) -> TransferAnswerReport:
    """Re-route the RAKL structural transfer through the answer gate.

    The transfer already exists and already binds its content to RAKL sources at
    a pinned commit. What it did not do was emit answers: it wrote into cells
    directly, which bypasses evidence resolution, the discriminating checks and
    the authority ladder entirely. This module changes the delivery path, not
    the content.

    The lane is `self-orion` because that session authored the transfer. This
    module does not author the answers and must not claim to: relabelling
    someone else's work as one's own lane would be as dishonest as the reverse,
    and would defeat the independence the gate is checking. The lane records who
    wrote the answer, which is what makes an independently-laned check
    meaningful.
    """

    base = {cell.mechanic_id: cell for cell in cells}
    applied = {
        cell.mechanic_id: cell
        for cell in apply_rakl_transfer_profiles(tuple(cells))
    }
    receipts = rakl_transfer_receipts(tuple(cells))

    records: list[AnswerRecord] = []
    skipped: dict[str, int] = {}

    def _skip(reason: str) -> None:
        skipped[reason] = skipped.get(reason, 0) + 1

    for receipt in receipts:
        before = base.get(receipt.mechanic_id)
        after = applied.get(receipt.mechanic_id)
        if before is None or after is None:
            _skip("unknown_mechanic")
            continue

        refs: list[str] = []
        bindings: dict[str, str] = {}
        for path in receipt.source_paths:
            ref = f"rakl:{path}@git:{receipt.source_commit}"
            resolution = resolve_evidence_ref(ref, evidence_roots)
            if resolution.resolved:
                refs.append(ref)
                bindings[ref] = expected_binding(resolution)
            else:
                _skip(f"evidence:{resolution.status.value}")
        if not refs:
            _skip("no_resolvable_evidence")
            continue

        for name in receipt.dimensions_closed:
            dimension = MechanicDimension(name)
            common = {
                "record_id": f"{lane}:rakl:{receipt.mechanic_id}:{name}",
                "mechanic_id": receipt.mechanic_id,
                "dimension": dimension,
                "lane": lane,
                "evidence_refs": tuple(refs),
                "evidence_bindings": tuple(sorted(bindings.items())),
            }

            # HANDOFF and METRICS answer with typed objects rather than strings.
            # Routing them through the string path would either drop them or
            # flatten a schema into prose, so each gets its own delta.
            if dimension is MechanicDimension.HANDOFF:
                known = {item.field_id for item in before.handoff_fields}
                fresh = tuple(
                    item for item in after.handoff_fields if item.field_id not in known
                )
                if not fresh:
                    _skip(f"no_delta:{name}")
                    continue
                records.append(AnswerRecord(**common, handoff_payload=fresh))
                continue

            if dimension is MechanicDimension.METRICS:
                known = {item.metric_id for item in before.metrics}
                fresh = tuple(
                    item for item in after.metrics if item.metric_id not in known
                )
                if not fresh:
                    _skip(f"no_delta:{name}")
                    continue
                records.append(AnswerRecord(**common, metric_payload=fresh))
                continue

            fields = _STRING_FIELDS_BY_DIMENSION.get(dimension)
            if not fields:
                _skip(f"structured_payload_required:{name}")
                continue
            payload = tuple(
                (field, values)
                for field in fields
                if (values := _delta(before, after, field))
            )
            if not payload:
                _skip(f"no_delta:{name}")
                continue
            records.append(AnswerRecord(**common, payload=payload))

    return TransferAnswerReport(
        records=tuple(records),
        skipped=tuple(sorted(skipped.items())),
    )
