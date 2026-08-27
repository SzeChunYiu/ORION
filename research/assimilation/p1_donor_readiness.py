#!/usr/bin/env python3
"""Map P1 and P2 nearest-work onto donor cells, and measure what a receipt needs (#318).

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
    / "orion-11-recursive-epistemic-reconstruction"
    / "evidence"
    / "nearest_work_matrix_v2.json"
)
OUTPUT_PATH = Path(__file__).resolve().parent / "P1_DONOR_READINESS_V1.json"
SCHEMA_VERSION = "orion.p1-donor-readiness.v1"

P2_VERDICTS_PATH = (
    REPO_ROOT
    / "papers"
    / "orion-12-open-world-scientific-discovery"
    / "notes"
    / "nearest-work"
    / "mechanism-verdicts.md"
)
P2_OUTPUT_PATH = Path(__file__).resolve().parent / "P2_DONOR_READINESS_V1.json"
P2_SCHEMA_VERSION = "orion.p2-donor-readiness.v1"

#: Parents in P2's verdict table that name a specific system, benchmark or paper.
#: Everything else names a *field*. The distinction is a judgement, so it is made
#: once here in the open rather than inferred from string shape -- a receipt needs
#: a specific artifact, and "the diversification literature" is not one.
P2_NAMED_ARTIFACT_PARENTS = frozenset(
    {
        "AutoResearchBench",
        "SAGE",
        "ResearchArena",
        "OpenScholar",
        "MetaSyn",
        "AgentSLR",
    }
)

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


def _p2_rows() -> list[list[str]]:
    """The `mechanism | parent | verdict | disposition` rows, verbatim."""

    rows: list[list[str]] = []
    for line in P2_VERDICTS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| mechanism"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4:
            rows.append(cells)
    return rows


def build_p2_readiness() -> dict[str, object]:
    """P2's donor map, whose gap is different in kind from P1's.

    P1's matrix names individual works with arXiv ids. P2's verdict table names
    *parents*, and several of them are fields rather than artifacts -- "the
    diversification literature", "information foraging", "SR stopping literature".
    A receipt requires a specific primary paper or official code, so those cannot
    be bound at all until a representative work is chosen for each, which is a
    scientific decision rather than a lookup.
    """

    rows: list[dict[str, object]] = []
    for mechanism, parent, verdict, disposition in _p2_rows():
        named = parent in P2_NAMED_ARTIFACT_PARENTS
        blockers = list(RECEIPT_FIELDS_NOT_IN_MATRIX)
        blockers.append("no access field recorded; body-read state is unknown")
        if not named:
            blockers.append(
                f"parent {parent!r} names a literature family, not an artifact; "
                "a representative primary work must be chosen before a donor id exists"
            )
        rows.append(
            {
                "mechanism": mechanism,
                "parent": parent,
                "verdict": verdict.replace("**", ""),
                "disposition_note": disposition,
                "donor_is_named_artifact": named,
                "receipt_sealable": False,
                "receipt_blockers": blockers,
            }
        )
    rows.sort(key=lambda row: (str(row["parent"]), str(row["mechanism"])))
    named_rows = [row for row in rows if row["donor_is_named_artifact"]]
    return {
        "schema_version": P2_SCHEMA_VERSION,
        "issue": 318,
        "grants_authority": "NONE",
        "closes_gate": None,
        "source": str(P2_VERDICTS_PATH.relative_to(REPO_ROOT)),
        "receipt_schema": "orion.mechanism-assimilation-receipt.v1",
        "summary": {
            "donor_mechanisms": len(rows),
            "distinct_parents": len({row["parent"] for row in rows}),
            "parents_naming_an_artifact": len({row["parent"] for row in named_rows}),
            "mechanisms_bindable_to_an_artifact": len(named_rows),
            "mechanisms_from_a_literature_family": len(rows) - len(named_rows),
            "with_recorded_access": 0,
            "receipt_sealable_now": sum(1 for row in rows if row["receipt_sealable"]),
        },
        "how_p2_differs_from_p1": (
            "P1's matrix names individual works with arXiv identifiers and records whether "
            "each body was read. P2's table names parents, several of which are literature "
            "families rather than artifacts, and records no access state at all. So P2's gap "
            "is upstream of P1's: before a receipt can be blocked on missing ORION-side "
            "fields, a donor artifact has to exist to bind to."
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


def validate_p2(committed: dict[str, object]) -> list[str]:
    derived = build_p2_readiness()
    if _comparable(committed) == _comparable(derived):
        return []
    errors = []
    if committed.get("summary") != derived["summary"]:
        errors.append(f"p2 summary: committed {committed.get('summary')} != derived {derived['summary']}")
    if not errors:
        errors.append("committed P2 readiness report differs from a live re-derivation; regenerate")
    return errors


def main() -> int:
    if "--check" in sys.argv[1:]:
        errors = validate(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")))
        errors += validate_p2(json.loads(P2_OUTPUT_PATH.read_text(encoding="utf-8")))
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    head = _git("rev-parse", "HEAD")
    for builder, path in ((build_readiness, OUTPUT_PATH), (build_p2_readiness, P2_OUTPUT_PATH)):
        payload = builder()
        payload["subject_commit"] = head
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
