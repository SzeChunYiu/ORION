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


_WIDTH = 900
_ROW_HEIGHT = 26
_PLOT_HEIGHT = 220
_PAD = 56


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def render_svg(report: dict[str, Any]) -> str:
    """Render the run trajectory and per-dimension yield as a standalone SVG.

    Deliberately dependency-free: a diagnostic that needs an install is a
    diagnostic nobody runs when a run has gone wrong.
    """

    rounds = report["rounds"]
    yields = [item for item in report["dimension_yield"] if item["attempts"]]
    bars_height = max(len(yields), 1) * _ROW_HEIGHT + _PAD
    height = _PLOT_HEIGHT + bars_height + _PAD * 2

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_WIDTH} {height}" '
        f'width="{_WIDTH}" height="{height}" font-family="ui-sans-serif,system-ui,sans-serif">',
        f'<rect width="{_WIDTH}" height="{height}" fill="#ffffff"/>',
        f'<text x="{_PAD}" y="32" font-size="16" font-weight="600" fill="#111827">'
        "ORION self-driving run</text>",
        f'<text x="{_PAD}" y="52" font-size="12" fill="#6b7280">'
        f'{len(rounds)} rounds &#183; ledger '
        f'{"intact" if report["ledger_intact"] else "COMPROMISED"} &#183; '
        f'{report["entries"]} entries</text>',
    ]

    if rounds:
        top, bottom = 72, 72 + _PLOT_HEIGHT
        left, right = _PAD, _WIDTH - _PAD
        span = max(len(rounds) - 1, 1)
        peak = max(
            [item["open_before"] for item in rounds]
            + [item["open_after"] for item in rounds]
            + [1]
        )

        def _x(index: int) -> float:
            return left + (right - left) * index / span

        def _y(value: int) -> float:
            return bottom - (bottom - top) * value / peak

        parts.append(
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#d1d5db"/>'
        )
        parts.append(
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#d1d5db"/>'
        )
        parts.append(
            f'<text x="{left}" y="{top - 8}" font-size="11" fill="#6b7280">'
            f"open questions (peak {peak})</text>"
        )
        path = " ".join(
            f"{'M' if index == 0 else 'L'}{_x(index):.1f},{_y(item['open_after']):.1f}"
            for index, item in enumerate(rounds)
        )
        parts.append(f'<path d="{path}" fill="none" stroke="#2563eb" stroke-width="2"/>')
        for index, item in enumerate(rounds):
            colour = "#9ca3af" if item["flat"] else "#059669"
            parts.append(
                f'<circle cx="{_x(index):.1f}" cy="{_y(item["open_after"]):.1f}" r="4" '
                f'fill="{colour}"/>'
            )
            parts.append(
                f'<text x="{_x(index):.1f}" y="{bottom + 16}" font-size="10" '
                f'text-anchor="middle" fill="#6b7280">r{item["round"]}</text>'
            )
            parts.append(
                f'<text x="{_x(index):.1f}" y="{bottom + 30}" font-size="10" '
                f'text-anchor="middle" fill="#9ca3af">g{item["growth_magnitude"]}</text>'
            )

    offset = 72 + _PLOT_HEIGHT + _PAD
    parts.append(
        f'<text x="{_PAD}" y="{offset - 14}" font-size="13" font-weight="600" '
        f'fill="#111827">Observed yield by dimension</text>'
    )
    widest = max([item["observed_value"] for item in yields] + [1e-9])
    for index, item in enumerate(yields):
        y = offset + index * _ROW_HEIGHT
        width = 380 * (item["observed_value"] / widest)
        parts.append(
            f'<text x="{_PAD}" y="{y + 12}" font-size="11" fill="#374151">'
            f'{_escape(item["dimension"])}</text>'
        )
        parts.append(
            f'<rect x="{_PAD + 210}" y="{y + 2}" width="{max(width, 1):.1f}" height="13" '
            f'rx="2" fill="#2563eb" opacity="0.75"/>'
        )
        parts.append(
            f'<text x="{_PAD + 210 + max(width, 1) + 8:.1f}" y="{y + 13}" font-size="10" '
            f'fill="#6b7280">{item["observed_value"]:.2f} '
            f'({item["verified"]}v/{item["evidence_bound"]}e/{item["refused"]}r '
            f'of {item["attempts"]})</text>'
        )
    if not yields:
        parts.append(
            f'<text x="{_PAD}" y="{offset + 12}" font-size="11" fill="#9ca3af">'
            "no answers have been graded yet</text>"
        )

    parts.append("</svg>")
    return "\n".join(parts)
