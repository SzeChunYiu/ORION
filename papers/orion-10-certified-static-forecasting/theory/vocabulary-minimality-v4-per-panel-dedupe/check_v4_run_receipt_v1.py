#!/usr/bin/env python3
"""Every number in RESULT_V4_2026-09-01.md, checked against the raw receipt.

A results table typed by hand is a claim about a file, not a reading of it. This
re-derives each one from `RUN_3561900_RAW.json.gz` and fails if any disagrees.

It also asserts the negative finding that document rests on: that the runner emits
none of the three terminals `PROTOCOL_V4.md` declared, which is why the
pre-declared prediction is `CANNOT_CHECK` rather than scored.

Exit 0 all bound, 1 a disagreement, 3 could not check (the receipt is missing).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "RUN_3561900_RAW.json.gz"
RESULT = HERE / "RESULT_V4_2026-09-01.md"
PROTOCOL = HERE / "PROTOCOL_V4.md"
RUNNER = HERE / "run_per_panel_v4.py"

RAW_SHA256 = "28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f"

# The table in RESULT_V4_2026-09-01.md, transcribed once and checked here.
PANELS = {
    "H1_n3": (2400, 56, 1146, 557, 641),
    "H1_n4": (800, 65, 308, 354, 73),
    "H2_n3": (3200, 103, 733, 1460, 904),
    "H2_n4": (800, 134, 157, 367, 142),
    "H3_n3": (1800, 39, 650, 355, 756),
    "H3_n4": (480, 37, 91, 256, 96),
    "H4_n3": (1800, 45, 757, 469, 529),
    "H4_n4": (640, 89, 185, 237, 129),
    "H5_n3": (1058, 14, 492, 242, 310),
    "H5_n4": (480, 1, 204, 134, 141),
}
REFEREES = {
    "containment": 11209,
    "dxx_witness": 6461,
    "bprime_witness": 13458,
    "exact_matcher": 1429,
    "symmetry": 792,
    "replay": 583,
}
#: Declared in PROTOCOL_V4.md before the run. None is emitted by the runner.
PROTOCOL_TERMINALS = (
    "ENVELOPE_SURVIVES_20X_COVERAGE",
    "CANNOT_CHECK_PREFIX_CONTROL_FAILED",
    "CANNOT_CHECK_WALL_CLOCK",
)


def _find(obj, key, depth: int = 0):
    if depth > 4:
        return None
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = _find(value, key, depth + 1)
            if found is not None:
                return found
    return None


def main() -> int:
    if not RAW.is_file():
        print(json.dumps({"status": "CANNOT_CHECK", "reason": f"absent: {RAW.name}"}, indent=2))
        return 3

    blob = gzip.decompress(RAW.read_bytes())
    digest = hashlib.sha256(blob).hexdigest()
    problems: list[str] = []
    if digest != RAW_SHA256:
        problems.append(f"raw receipt digest {digest} != recorded {RAW_SHA256}")

    payload = None
    for line in blob.decode("utf-8").splitlines():
        if "=" in line and line.split("=", 1)[1].lstrip().startswith("{"):
            candidate = json.loads(line.split("=", 1)[1])
            if _find(candidate, "panels") is not None:
                payload = candidate
                break
    if payload is None:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "no panel payload"}, indent=2))
        return 3

    panels = _find(payload, "panels") or {}
    if sorted(panels) != sorted(PANELS):
        problems.append(f"panel set differs: {sorted(panels)}")
    for name, (ev, fourth, borrow, split, tie) in PANELS.items():
        got = panels.get(name, {})
        census = got.get("regime_census", {})
        actual = (
            got.get("evaluated"),
            census.get("fourth"),
            census.get("borrow"),
            census.get("split"),
            census.get("tie"),
        )
        if actual != (ev, fourth, borrow, split, tie):
            problems.append(f"{name}: recorded {(ev, fourth, borrow, split, tie)}, receipt {actual}")

    for referee, rows in REFEREES.items():
        got_rows = _find(payload, f"{referee}_rows")
        if got_rows != rows:
            problems.append(f"{referee}_rows: recorded {rows}, receipt {got_rows}")
        failures = _find(payload, f"{referee}_failures")
        if failures not in ([], None) and referee != "replay":
            problems.append(f"{referee}_failures is non-empty: {failures}")

    terminal = _find(payload, "terminal")
    if terminal != "QG7_FOURTH_SUPPORT2_REGIME_FOUND":
        problems.append(f"terminal is {terminal!r}")

    total = _find(payload, "fourth_regime_candidates_total")
    if total != 583:
        problems.append(f"fourth_regime_candidates_total is {total}, recorded 583")
    if total != sum(v[1] for v in PANELS.values()):
        problems.append("panel fourth counts do not sum to the reported total")

    # Authority must not have been raised anywhere.
    for flag in ("novelty_credit", "r6_authority", "physical_quantum_advantage_claim"):
        if _find(payload, flag) is not False:
            problems.append(f"{flag} is not false")

    # The load-bearing negative: the runner cannot emit the protocol's terminals.
    runner_src = RUNNER.read_text(encoding="utf-8") if RUNNER.is_file() else ""
    protocol_src = PROTOCOL.read_text(encoding="utf-8") if PROTOCOL.is_file() else ""
    emitted = [t for t in PROTOCOL_TERMINALS if f'"{t}"' in runner_src]
    if emitted:
        problems.append(
            f"the runner does emit {emitted}, so the CANNOT_CHECK on the prediction is wrong"
        )
    declared = [t for t in PROTOCOL_TERMINALS if t in protocol_src]
    if len(declared) != len(PROTOCOL_TERMINALS):
        problems.append(f"protocol no longer declares all three terminals: {declared}")

    payload_out = {
        "schema": "ORION10.V4RunReceiptCheck.v1",
        "raw_sha256": digest,
        "panels_checked": len(PANELS),
        "referees_checked": len(REFEREES),
        "terminal": terminal,
        "fourth_regime_candidates_total": total,
        "protocol_terminals_declared": declared,
        "protocol_terminals_emitted_by_runner": emitted,
        "prediction_scoreable": bool(emitted),
        "problems": problems,
        "scientific_authority_delta": "NONE",
        "status": "ALL_BOUND" if not problems else "DISAGREEMENT",
    }
    print(json.dumps(payload_out, indent=2, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
