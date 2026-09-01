#!/usr/bin/env python3
"""Frozen A2 price/shift failure-atlas analysis.

This module deliberately does not know how a candidate or baseline produced its
normalized score.  It consumes the values supplied by the already-frozen
benchmark-specific accounting and performs only the preregistered aggregation,
uncertainty, terminal classification, and literal lattice-boundary extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

LEVELS = (0.5, 1.0, 2.0)
RESAMPLES = 10_000
REGRET_TOL = 1e-12
MAX_REGRET_REFERENCE = 2.0
TERMINALS = (
    "CANNOT_CHECK",
    "BASELINE_LOSS",
    "POSITIVE_NEAR_ORACLE",
    "POSITIVE_HIGH_REGRET",
    "UNRESOLVED_DIRECTION",
)
REQUIRED = (
    "unit_id",
    "benchmark",
    "stratum",
    "shift_axis",
    "shift_regime",
    "price_materialization",
    "price_retrieval",
    "price_reasoning_tool",
    "eligible",
    "cannot_check_reason",
    "candidate_normalized_points",
    "strongest_baseline_normalized_points",
    "hindsight_oracle_normalized_points",
)


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{field} must be finite")
    return out


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    missing = [k for k in REQUIRED if k not in row]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if not isinstance(row["eligible"], bool):
        raise ValueError("eligible must be boolean")
    for key in ("unit_id", "benchmark", "stratum", "shift_axis", "shift_regime"):
        if not isinstance(row[key], str) or not row[key]:
            raise ValueError(f"{key} must be a nonempty string")
    for key in ("price_materialization", "price_retrieval", "price_reasoning_tool"):
        v = _finite_number(row[key], key)
        if v not in LEVELS:
            raise ValueError(f"{key}={v} is outside frozen price levels {LEVELS}")
        row[key] = v
    if row["eligible"]:
        if row["cannot_check_reason"] not in (None, ""):
            raise ValueError("eligible row cannot carry cannot_check_reason")
        for key in (
            "candidate_normalized_points",
            "strongest_baseline_normalized_points",
            "hindsight_oracle_normalized_points",
        ):
            row[key] = _finite_number(row[key], key)
        regret = row["hindsight_oracle_normalized_points"] - row["candidate_normalized_points"]
        if regret < -REGRET_TOL:
            raise ValueError(f"hindsight regret is materially negative: {regret}")
    else:
        if not isinstance(row["cannot_check_reason"], str) or not row["cannot_check_reason"]:
            raise ValueError("ineligible row requires a nonempty cannot_check_reason")
        for key in (
            "candidate_normalized_points",
            "strongest_baseline_normalized_points",
            "hindsight_oracle_normalized_points",
        ):
            if row[key] is not None:
                raise ValueError(f"ineligible row must use null for {key}")
    return row


def cell_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["benchmark"],
        row["shift_axis"],
        row["shift_regime"],
        row["price_materialization"],
        row["price_retrieval"],
        row["price_reasoning_tool"],
    )


def canonical_key(key: tuple[Any, ...]) -> str:
    return "|".join(str(x) for x in key)


def _deterministic_index(key: str, replicate: int, draw: int, n: int) -> int:
    digest = hashlib.sha256(f"{key}|{replicate}|{draw}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % n


def bootstrap_mean_interval(values: list[float], key: str, resamples: int = RESAMPLES) -> tuple[float, float]:
    if not values:
        raise ValueError("cannot bootstrap empty values")
    if len(values) == 1:
        return values[0], values[0]
    means: list[float] = []
    n = len(values)
    for b in range(resamples):
        total = 0.0
        for j in range(n):
            total += values[_deterministic_index(key, b, j, n)]
        means.append(total / n)
    means.sort()
    lo = means[math.floor(0.025 * (resamples - 1))]
    hi = means[math.ceil(0.975 * (resamples - 1))]
    return lo, hi


def classify_cell(upper_gain: float, lower_gain: float, max_regret: float | None, eligible_n: int) -> str:
    if eligible_n == 0:
        return "CANNOT_CHECK"
    assert max_regret is not None
    if upper_gain <= 0.0:
        return "BASELINE_LOSS"
    if lower_gain > 0.0 and max_regret <= MAX_REGRET_REFERENCE + REGRET_TOL:
        return "POSITIVE_NEAR_ORACLE"
    if lower_gain > 0.0 and max_regret > MAX_REGRET_REFERENCE + REGRET_TOL:
        return "POSITIVE_HIGH_REGRET"
    return "UNRESOLVED_DIRECTION"


def summarize_cell(key: tuple[Any, ...], rows: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [r for r in rows if r["eligible"]]
    cannot = [r for r in rows if not r["eligible"]]
    reason_counts = Counter(r["cannot_check_reason"] for r in cannot)
    strata = Counter(r["stratum"] for r in rows)
    if not eligible:
        return {
            "key": canonical_key(key),
            "benchmark": key[0],
            "shift_axis": key[1],
            "shift_regime": key[2],
            "prices": {"materialization": key[3], "retrieval": key[4], "reasoning_tool": key[5]},
            "eligible_n": 0,
            "cannot_check_n": len(cannot),
            "cannot_check_reasons": dict(sorted(reason_counts.items())),
            "strata": dict(sorted(strata.items())),
            "mean_candidate_gain": None,
            "gain_ci95": None,
            "mean_hindsight_regret": None,
            "max_hindsight_regret": None,
            "terminal": "CANNOT_CHECK",
        }
    gains = [r["candidate_normalized_points"] - r["strongest_baseline_normalized_points"] for r in eligible]
    regrets = [max(0.0, r["hindsight_oracle_normalized_points"] - r["candidate_normalized_points"]) for r in eligible]
    mean_gain = sum(gains) / len(gains)
    mean_regret = sum(regrets) / len(regrets)
    max_regret = max(regrets)
    lo, hi = bootstrap_mean_interval(gains, canonical_key(key))
    terminal = classify_cell(hi, lo, max_regret, len(eligible))
    return {
        "key": canonical_key(key),
        "benchmark": key[0],
        "shift_axis": key[1],
        "shift_regime": key[2],
        "prices": {"materialization": key[3], "retrieval": key[4], "reasoning_tool": key[5]},
        "eligible_n": len(eligible),
        "cannot_check_n": len(cannot),
        "cannot_check_reasons": dict(sorted(reason_counts.items())),
        "strata": dict(sorted(strata.items())),
        "mean_candidate_gain": mean_gain,
        "gain_ci95": [lo, hi],
        "mean_hindsight_regret": mean_regret,
        "max_hindsight_regret": max_regret,
        "terminal": terminal,
    }


def adjacent_prices(a: dict[str, float], b: dict[str, float]) -> bool:
    idx = {v: i for i, v in enumerate(LEVELS)}
    diffs = []
    for dim in ("materialization", "retrieval", "reasoning_tool"):
        diffs.append(abs(idx[a[dim]] - idx[b[dim]]))
    return sum(diffs) == 1 and max(diffs) == 1


def boundary_edges(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, a in enumerate(cells):
        for b in cells[i + 1 :]:
            if (a["benchmark"], a["shift_axis"], a["shift_regime"]) != (
                b["benchmark"], b["shift_axis"], b["shift_regime"]
            ):
                continue
            if adjacent_prices(a["prices"], b["prices"]) and a["terminal"] != b["terminal"]:
                out.append({"a": a["key"], "b": b["key"], "a_terminal": a["terminal"], "b_terminal": b["terminal"]})
    return sorted(out, key=lambda x: (x["a"], x["b"]))


def analyze(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    seen_units: set[tuple[str, tuple[Any, ...]]] = set()
    for raw in rows:
        row = validate_row(dict(raw))
        key = cell_key(row)
        unit_key = (row["unit_id"], key)
        if unit_key in seen_units:
            raise ValueError(f"duplicate unit in cell: {row['unit_id']} {canonical_key(key)}")
        seen_units.add(unit_key)
        grouped[key].append(row)
    cells = [summarize_cell(key, grouped[key]) for key in sorted(grouped, key=canonical_key)]
    terminals = Counter(c["terminal"] for c in cells)
    return {
        "schema": "ORION.A2.ExternalPriceShiftFailureAtlasResult.v1",
        "analysis_identity": "P12_EXTERNAL_PRICE_SHIFT_FAILURE_ATLAS_FREEZE_V1",
        "cells": cells,
        "phase_boundary_edges": boundary_edges(cells),
        "terminal_counts": {t: terminals.get(t, 0) for t in TERMINALS},
        "smoothing_or_interpolation_used": False,
        "hindsight_oracle_selectable_by_candidate": False,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"line {lineno} is not an object")
        rows.append(obj)
    return rows


def _row(unit: str, materialization: float, gain: float | None, regret: float | None, *, regime: str = "observed", reason: str | None = None) -> dict[str, Any]:
    eligible = reason is None
    candidate = 10.0 if eligible else None
    baseline = candidate - gain if eligible and gain is not None else None
    oracle = candidate + regret if eligible and regret is not None else None
    return {
        "unit_id": unit,
        "benchmark": "fixture",
        "stratum": "s0",
        "shift_axis": "fixture_axis",
        "shift_regime": regime,
        "price_materialization": materialization,
        "price_retrieval": 1.0,
        "price_reasoning_tool": 1.0,
        "eligible": eligible,
        "cannot_check_reason": reason,
        "candidate_normalized_points": candidate,
        "strongest_baseline_normalized_points": baseline,
        "hindsight_oracle_normalized_points": oracle,
    }


def self_test() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for i in range(4):
        rows.append(_row(f"near-{i}", 0.5, 3.0, 1.0))
        rows.append(_row(f"high-{i}", 1.0, 3.0, 3.0))
        rows.append(_row(f"loss-{i}", 2.0, -1.0, 0.5))
    rows.append(_row("cc-0", 0.5, None, None, regime="missing", reason="ACCESS_BLOCKED"))
    result = analyze(rows)
    by_key = {c["key"]: c for c in result["cells"]}
    terms = {c["terminal"] for c in result["cells"]}
    assert {"POSITIVE_NEAR_ORACLE", "POSITIVE_HIGH_REGRET", "BASELINE_LOSS", "CANNOT_CHECK"} <= terms
    assert len(result["phase_boundary_edges"]) == 2
    assert result["terminal_counts"]["POSITIVE_NEAR_ORACLE"] == 1
    assert result["terminal_counts"]["POSITIVE_HIGH_REGRET"] == 1
    assert result["terminal_counts"]["BASELINE_LOSS"] == 1
    assert result["terminal_counts"]["CANNOT_CHECK"] == 1
    assert all(c["terminal"] in TERMINALS for c in by_key.values())
    return {"decision": "GREEN", "cells": len(result["cells"]), "boundaries": len(result["phase_boundary_edges"])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.input is None:
        parser.error("input JSONL required unless --self-test is used")
    result = analyze(load_jsonl(args.input))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
