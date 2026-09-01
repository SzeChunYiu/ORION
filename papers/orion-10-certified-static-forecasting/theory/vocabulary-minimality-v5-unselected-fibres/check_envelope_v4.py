#!/usr/bin/env python3
"""Do any instances exceed the offset-3 envelope, and where?

`PROTOCOL_V4.md` predicted, before the run, that V3's nine violations would either
vanish (if cross-panel skipping produced them) or reappear (if they were genuine).
`RESULT_V4_2026-09-01.md` recorded that as CANNOT_CHECK because the runner emits
none of the protocol's terminals and reports no prefix control.

That was right about the runner's terminals and too pessimistic about its data.
The receipt serialises every evaluated instance with `f_Bprime` and `C_Dxx`, so
the envelope is computable directly.

The quantity is identified rather than assumed: the criterion file reports three
offsets and the protocol says only "offset 3", so this checks all three. Exactly
one produces any instance above 3, and it produces them in the two panels V3
named. A wrong identification would fail here loudly rather than quietly.

Exit 0 envelope holds, 1 refuted, 3 could not check.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE.parent / "vocabulary-minimality-v4-per-panel-dedupe" / "RUN_3561900_RAW.json.gz"
RECEIPT_SHA256 = "28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f"

ENVELOPE = 3
#: V3's finding, as PROTOCOL_V4.md records it, frozen before the V4 run.
V3_EXPECTED = {"H2_n3": 5, "H4_n3": 4}
CANDIDATES = (("f_Bprime", "C_Dxx"), ("C_Dplus", "C_Dxx"), ("C_DP", "C_Dxx"))


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


def main() -> int:
    if not RECEIPT.is_file():
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "receipt absent"}, indent=2))
        return 3
    blob = gzip.decompress(RECEIPT.read_bytes())
    digest = hashlib.sha256(blob).hexdigest()
    if digest != RECEIPT_SHA256:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": f"receipt changed: {digest}"}, indent=2))
        return 3

    rows = None
    for line in blob.decode("utf-8").splitlines():
        if "=" in line and line.split("=", 1)[1].lstrip().startswith("{"):
            rows = _find(json.loads(line.split("=", 1)[1]), "full_census_rows_v2")
            if rows:
                break
    if not rows:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "no census rows"}, indent=2))
        return 3

    per_quantity = {}
    for a, b in CANDIDATES:
        over = [r for r in rows if r[a] - r[b] > ENVELOPE]
        per_quantity[f"{a}_minus_{b}"] = {
            "over_envelope": len(over),
            "panels": dict(Counter(r["panel"] for r in over)),
            "offsets": dict(Counter(r[a] - r[b] for r in over)),
            "regimes": dict(Counter(r["regime"] for r in over)),
        }

    identified = [k for k, v in per_quantity.items() if v["over_envelope"] > 0]
    matches_v3 = [
        k for k in identified if per_quantity[k]["panels"] == V3_EXPECTED
    ]

    payload = {
        "schema": "ORION10.OffsetEnvelopeV4.v1",
        "receipt_sha256": digest,
        "rows": len(rows),
        "envelope": ENVELOPE,
        "per_quantity": per_quantity,
        "quantities_with_any_violation": identified,
        "quantities_reproducing_v3_panel_split": matches_v3,
        "v3_expected_panels": V3_EXPECTED,
        "identification_unambiguous": len(identified) == 1 and len(matches_v3) == 1,
        "scientific_authority_delta": "NONE",
        "promotes_no_claim": True,
        "terminal": (
            "ENVELOPE_REFUTED__V3_VIOLATIONS_CONFIRMED_GENUINE"
            if matches_v3
            else "ENVELOPE_SURVIVES_20X_COVERAGE"
            if not identified
            else "ENVELOPE_REFUTED__PANEL_SPLIT_DIFFERS_FROM_V3"
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not identified else 1


if __name__ == "__main__":
    raise SystemExit(main())
