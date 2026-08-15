from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .saturation import GROWTH_COORDINATES
from .scheduler import build_yield_report
from .store import EntryKind, LedgerStore


@dataclass(frozen=True)
class RoundRow:
    """One round, flattened for inspection."""

    round_index: int
    open_before: int
    open_after: int
    verified: int
    evidence_bound: int
    refused: int
    growth_magnitude: int
    flat: bool
    guard_refusals: int
    false_progress: int
    coordinates: tuple[tuple[str, int], ...]

    @property
    def closed(self) -> int:
        return self.open_before - self.open_after


def build_round_rows(store: LedgerStore) -> tuple[RoundRow, ...]:
    """Join ROUND and growth RECEIPT entries into one row per round."""

    growth_by_round: dict[int, dict[str, Any]] = {}
    for entry in store.entries(EntryKind.RECEIPT):
        if entry.payload.get("kind") != "GROWTH_VECTOR":
            continue
        growth_by_round[int(entry.payload.get("round_index", -1))] = dict(entry.payload)

    rows: list[RoundRow] = []
    for entry in store.entries(EntryKind.ROUND):
        payload = entry.payload
        index = int(payload.get("round_index", -1))
        growth = growth_by_round.get(index, {})
        rows.append(
            RoundRow(
                round_index=index,
                open_before=int(payload.get("open_before", 0)),
                open_after=int(payload.get("open_after", 0)),
                verified=len(payload.get("verified_record_ids", ()) or ()),
                evidence_bound=len(payload.get("evidence_bound_record_ids", ()) or ()),
                refused=len(payload.get("refused_record_ids", ()) or ()),
                growth_magnitude=int(growth.get("magnitude", 0)),
                flat=bool(growth.get("flat", False)),
                guard_refusals=len(payload.get("guard_refusals", ()) or ()),
                false_progress=len(payload.get("false_progress_reasons", ()) or ()),
                coordinates=tuple(
                    (name, int(growth.get(name, 0))) for name in GROWTH_COORDINATES
                ),
            )
        )
    return tuple(sorted(rows, key=lambda item: item.round_index))


def build_report(store: LedgerStore) -> dict[str, Any]:
    """Everything a person needs to diagnose a run, read back from the ledger."""

    rows = build_round_rows(store)
    yields = build_yield_report(store)
    guards = [dict(entry.payload) for entry in store.entries(EntryKind.GUARD)]
    residuals = [dict(entry.payload) for entry in store.entries(EntryKind.RESIDUAL)]
    return {
        "ledger": str(store.path),
        "ledger_intact": not store.verify(),
        "entries": len(store.entries()),
        "rounds": [
            {
                "round": row.round_index,
                "open_before": row.open_before,
                "open_after": row.open_after,
                "closed": row.closed,
                "verified": row.verified,
                "evidence_bound": row.evidence_bound,
                "refused": row.refused,
                "growth_magnitude": row.growth_magnitude,
                "flat": row.flat,
                "guard_refusals": row.guard_refusals,
                "false_progress": row.false_progress,
                "growth": dict(row.coordinates),
            }
            for row in rows
        ],
        "dimension_yield": [
            {
                "dimension": item.dimension,
                "attempts": item.attempts,
                "verified": item.verified,
                "evidence_bound": item.evidence_bound,
                "refused": item.refused,
                "observed_value": round(item.observed_value, 4),
                "priority_score": (
                    "inf"
                    if item.attempts == 0
                    else round(item.priority_score(yields.total_attempts), 4)
                ),
            }
            for item in yields.rows
        ],
        "stalled_dimensions": list(yields.stalled),
        "best_dimension": yields.best.dimension if yields.best else None,
        "guards": guards,
        "residuals": residuals,
    }
