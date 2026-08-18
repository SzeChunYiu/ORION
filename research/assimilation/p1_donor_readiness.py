#!/usr/bin/env python3
"""Map P1's nearest-work matrix onto donor cells, and measure what a receipt needs (#318).

#318's first box asks to *"audit existing P1/P2 nearest-work matrices and map every
close paper to one or more atomic donor cells"*. This does that, and then reports
the gap between what the matrix records and what
`MechanismAssimilationReceipt.v1` requires.

The gap is the finding. The matrix identifies donors well -- source, arXiv id,
mechanism, disposition, whether the body was read. It records nothing about the
**ORION side**: what ORION calls the mechanism, what ORION added to it, which
target mechanic cells it lands in, what authority either side carries, or which of
the donor's assumptions were kept.

So no receipt can be sealed from this data without inventing that half, and
inventing it is exactly the rebranding/authority-escalation surface the receipt's
hostile checks exist to detect. A readiness report is the honest artifact: it says
which donors are identified, which cannot yet be sealed, and precisely why.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = (
    REPO_ROOT
    / "papers"
    / "paper-01-recursive-epistemic-reconstruction"
    / "evidence"
    / "nearest_work_matrix_v2.json"
)
OUTPUT_PATH = Path(__file__).resolve().parent / "P1_DONOR_READINESS_V1.json"
SCHEMA_VERSION = "orion.p1-donor-readiness.v1"

#: Fields `MechanismAssimilationReceipt.v1` needs that the matrix does not carry.
#: Listed once so the report cannot drift from the schema silently.
RECEIPT_FIELDS_NOT_IN_MATRIX = (
    "claim.orion_name",
    "claim.delta",
    "claim.target_mechanic_ids",
    "claim.orion_authority",
    "mechanism.donor_authority",
    "mechanism.assumptions",
)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def build_readiness() -> dict[str, object]:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for entry in matrix["mechanisms"]:
        arxiv_id = entry.get("arxiv_id") or ""
        body_checked = bool(entry.get("body_checked"))
        rows.append(
            {
                "mechanism": entry["mechanism"],
                "source": entry["source"],
                "donor_id": f"arxiv:{arxiv_id}" if arxiv_id else entry["source"].split(",")[0],
                "has_stable_identifier": bool(arxiv_id),
                "disposition": entry["disposition"],
                # The matrix's own field, mapped onto the receipt's vocabulary.
                "access": "FULL_TEXT" if body_checked else "ABSTRACT_ONLY",
                # Every donor here is a paper, book or agency handbook -- a primary
                # source. None is a survey or secondary write-up, so none would
                # trip the receipt's UNGROUNDED_SOURCE check.
                "source_kind": "PRIMARY_PAPER",
                "receipt_sealable": False,
                "receipt_blockers": list(RECEIPT_FIELDS_NOT_IN_MATRIX)
                + ([] if body_checked else ["donor body not read; access is ABSTRACT_ONLY"]),
            }
        )
    rows.sort(key=lambda row: (str(row["donor_id"]), str(row["mechanism"])))

    abstract_only = [row for row in rows if row["access"] == "ABSTRACT_ONLY"]
    adopt = [row for row in rows if row["disposition"] == "ADOPT"]
    adopt_unread = [row for row in adopt if row["access"] == "ABSTRACT_ONLY"]
    return {
        "schema_version": SCHEMA_VERSION,
        "issue": 318,
        "grants_authority": "NONE",
        "closes_gate": None,
        "matrix": str(MATRIX_PATH.relative_to(REPO_ROOT)),
        "receipt_schema": "orion.mechanism-assimilation-receipt.v1",
        "summary": {
            "donor_mechanisms": len(rows),
            "with_stable_identifier": sum(1 for row in rows if row["has_stable_identifier"]),
            "full_text_read": len(rows) - len(abstract_only),
            "abstract_only": len(abstract_only),
            "adopt": len(adopt),
            "adopt_on_unread_bodies": len(adopt_unread),
            "receipt_sealable_now": sum(1 for row in rows if row["receipt_sealable"]),
        },
        "why_none_are_sealable": (
            "The matrix identifies donors but records nothing about the ORION side: "
            "what ORION calls each mechanism, what ORION added, which target mechanic "
            "cells it lands in, what authority either side carries, or which donor "
            "assumptions were kept. Supplying those from nothing is the rebranding and "
            "authority-escalation surface the receipt's hostile checks exist to detect, "
            "so they must be authored against the donor bodies rather than inferred here."
        ),
        "mechanisms": rows,
    }


def _comparable(payload: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if key != "subject_commit"}


def validate(committed: dict[str, object]) -> list[str]:
    derived = build_readiness()
    if _comparable(committed) == _comparable(derived):
        return []
    errors = []
    if committed.get("summary") != derived["summary"]:
        errors.append(f"summary: committed {committed.get('summary')} != derived {derived['summary']}")
    if not errors:
        errors.append("committed readiness report differs from a live re-derivation; regenerate")
    return errors


def main() -> int:
    if "--check" in sys.argv[1:]:
        errors = validate(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")))
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    payload = build_readiness()
    payload["subject_commit"] = _git("rev-parse", "HEAD")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
