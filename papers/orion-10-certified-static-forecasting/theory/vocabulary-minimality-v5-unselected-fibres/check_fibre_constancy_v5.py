#!/usr/bin/env python3
"""Is cost constant on every f_B' fibre, over the unselected population?

V1 could not say. Its 64 witnesses were selected on ``C_Dxx < min(C_D+, f_B')``, so
a tight relationship between C_Dxx and f_B' among them is what the selection would
produce whether or not the population has one. V1 said exactly what would settle
it: serialise f_B' and C_D++ for the unselected instances and re-run the grouping.

The V4 run already did. Its receipt carries `full_census_rows_v2`, every evaluated
instance with both fields, so this needs no new computation.

Protocol and pre-recorded prediction: PROTOCOL_V5.md, committed before this ran.

Exit 0 constancy holds, 1 refuted, 3 could not check.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE.parent / "vocabulary-minimality-v4-per-panel-dedupe" / "RUN_3561900_RAW.json.gz"
PROTOCOL = HERE / "PROTOCOL_V5.md"
RECEIPT_SHA256 = "28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f"

#: The predicate V1's 64 witnesses were selected on.
def selected(row: dict) -> bool:
    return row["C_Dxx"] < min(row["C_Dplus"], row["f_Bprime"])


def _find(obj, key, depth: int = 0):
    if depth > 5:
        return None
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = _find(value, key, depth + 1)
            if found is not None:
                return found
    return None


def load_rows() -> list[dict]:
    blob = gzip.decompress(RECEIPT.read_bytes())
    digest = hashlib.sha256(blob).hexdigest()
    if digest != RECEIPT_SHA256:
        raise RuntimeError(f"receipt changed since the protocol was frozen: {digest}")
    for line in blob.decode("utf-8").splitlines():
        if "=" in line and line.split("=", 1)[1].lstrip().startswith("{"):
            rows = _find(json.loads(line.split("=", 1)[1]), "full_census_rows_v2")
            if rows is not None:
                return rows
    return []


def fibres(rows: list[dict]) -> dict[int, Counter]:
    grouped: dict[int, Counter] = defaultdict(Counter)
    for row in rows:
        grouped[row["f_Bprime"]][row["C_Dxx"]] += 1
    return grouped


def main() -> int:
    rows = load_rows()
    required = {"C_DP", "C_Dplus", "C_Dxx", "f_Bprime", "regime", "panel"}
    if not rows or any(not required <= set(r) for r in rows):
        print(json.dumps({"status": "CANNOT_CHECK_INSUFFICIENT_SERIALISATION"}, indent=2))
        return 3

    all_fibres = fibres(rows)
    inconstant = {k: dict(v) for k, v in all_fibres.items() if len(v) > 1}

    sel = [r for r in rows if selected(r)]
    unsel = [r for r in rows if not selected(r)]
    sel_fibres = fibres(sel)
    unsel_fibres = fibres(unsel)

    # V1's three reported offsets, recomputed over the whole census.
    def offsets(sample, a, b):
        return dict(Counter(r[a] - r[b] for r in sample))

    holds = not inconstant
    payload = {
        "schema": "ORION10.FibreConstancyUnselected.v5",
        "receipt_sha256": RECEIPT_SHA256,
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "rows_total": len(rows),
        "rows_matching_v1_selection_predicate": len(sel),
        "rows_unselected": len(unsel),
        "regimes": dict(Counter(r["regime"] for r in rows)),
        "fibres_total": len(all_fibres),
        "fibres_with_more_than_one_cost": len(inconstant),
        "inconstant_fibres": {str(k): v for k, v in sorted(inconstant.items())},
        "fibres_among_selected_only": {
            str(k): dict(v) for k, v in sorted(sel_fibres.items())
        },
        "fibres_with_more_than_one_cost_among_selected_only": sum(
            1 for v in sel_fibres.values() if len(v) > 1
        ),
        "fibres_with_more_than_one_cost_among_unselected": sum(
            1 for v in unsel_fibres.values() if len(v) > 1
        ),
        "v1_offsets_recomputed_over_whole_census": {
            "f_Bprime_minus_C_Dxx": offsets(rows, "f_Bprime", "C_Dxx"),
            "C_Dplus_minus_C_Dxx": offsets(rows, "C_Dplus", "C_Dxx"),
            "C_DP_minus_C_Dxx": offsets(rows, "C_DP", "C_Dxx"),
        },
        "v1_offsets_recomputed_over_selected_only": {
            "f_Bprime_minus_C_Dxx": offsets(sel, "f_Bprime", "C_Dxx"),
            "C_Dplus_minus_C_Dxx": offsets(sel, "C_Dplus", "C_Dxx"),
            "C_DP_minus_C_Dxx": offsets(sel, "C_DP", "C_Dxx"),
        },
        "scientific_authority_delta": "NONE",
        "promotes_no_claim": True,
        "terminal": (
            "FIBRE_CONSTANCY_HOLDS_ON_UNSELECTED_POPULATION"
            if holds
            else "FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION"
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if holds else 1


if __name__ == "__main__":
    raise SystemExit(main())
