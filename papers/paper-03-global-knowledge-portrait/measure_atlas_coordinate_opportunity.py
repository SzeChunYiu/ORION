#!/usr/bin/env python3
"""Which atlas coordinates can separate anything, and which cannot.

The programme ledger records that four P3 coordinates -- referent, construct,
measurement and temporal context -- are "inert in the current artifact". Inert is
one word for two different situations, and the difference decides what a fix has
to change:

* a coordinate that carries **no content at all**: one distinct value across the
  whole artifact, so nothing downstream can read it;
* a coordinate that carries plenty of content but **never differs between the two
  sides of a case**, so it cannot produce a contrast even though it varies
  across cases.

An atlas built to fix the first will not fix the second. Populating a field is
not the same as creating contrasting pairs, and the ledger's success condition
("every formerly inert coordinate varies") is satisfied by an atlas that still
reproduces every zero measured here.

Nothing here reads a model output or a prediction. It reads the frozen gold and
counts. A committed measurement receipt must identify a repository artifact, so
inputs outside this checkout fail closed instead of serializing a machine-local
sandbox path.

Exit codes: 0 measured, 2 a coordinate the ledger calls inert turned out not to
be, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_NAMES_AS_INERT = (
    "referent_ids",
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
)


def load(path: Path) -> tuple[list[dict], str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return rows, digest


def artifact_locator(path: Path) -> str | None:
    """Return a stable repo-relative locator, or None for a machine-local input."""
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return None


#: The two sides of a case, as the frozen schema names them.
LEFT, RIGHT = "left_projection", "right_projection"


def measure(rows: list[dict]) -> dict:
    projections = [
        row[side]
        for row in rows
        for side in (LEFT, RIGHT)
        if isinstance(row.get(side), dict)
    ]
    keys = collections.Counter(key for projection in projections for key in projection)
    coordinates = {}
    for key in sorted(keys):
        values = [
            json.dumps(projection.get(key), sort_keys=True)
            for projection in projections
            if key in projection
        ]
        differs = sum(
            1
            for row in rows
            if isinstance(row.get(LEFT), dict)
            and isinstance(row.get(RIGHT), dict)
            and json.dumps(row[LEFT].get(key), sort_keys=True)
            != json.dumps(row[RIGHT].get(key), sort_keys=True)
        )
        distinct = len(set(values))
        coordinates[key] = {
            "present_in_projections": len(values),
            "distinct_values": distinct,
            "cases_where_the_two_sides_differ": differs,
            "within_case_contrast_fraction": differs / len(rows) if rows else 0.0,
            # The two ways a coordinate fails to be usable, kept apart.
            "carries_no_content": distinct <= 1,
            "cannot_contrast": differs == 0,
        }
    return {
        "cases": len(rows),
        "projections": len(projections),
        "coordinates_present": sorted(keys),
        "coordinates": coordinates,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: measure_atlas_coordinate_opportunity.py GOLD.jsonl")
        return 3
    path = Path(sys.argv[1])
    locator = artifact_locator(path)
    if locator is None:
        print(
            json.dumps(
                {
                    "status": "CANNOT_CHECK",
                    "error": "measurement input is outside the repository and has no stable locator",
                }
            )
        )
        return 3
    try:
        rows, digest = load(path)
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    measured = measure(rows)
    coordinates = measured["coordinates"]

    no_content = sorted(k for k, v in coordinates.items() if v["carries_no_content"])
    no_contrast = sorted(k for k, v in coordinates.items() if v["cannot_contrast"])
    contrasting = sorted(k for k, v in coordinates.items() if not v["cannot_contrast"])
    absent = sorted(set(LEDGER_NAMES_AS_INERT) - set(coordinates))

    checks = {
        "every_coordinate_the_ledger_calls_inert_is_unusable": all(
            name in no_contrast or name in absent for name in LEDGER_NAMES_AS_INERT
        ),
        "at_least_one_coordinate_does_contrast": bool(contrasting),
    }

    print(
        json.dumps(
            {
                "schema": "orion.p3.atlas-coordinate-opportunity.v1",
                "record": "P3_ATLAS_COORDINATE_OPPORTUNITY",
                "authority_scope": "OUTCOME_BLIND_MEASUREMENT",
                "outcome_accessed": False,
                "artifact": locator,
                "artifact_sha256": digest,
                "cases": measured["cases"],
                "projections": measured["projections"],
                "coordinates_present": measured["coordinates_present"],
                "coordinates": coordinates,
                "carry_no_content": no_content,
                "cannot_contrast": no_contrast,
                "do_contrast": contrasting,
                "ledger_named_but_absent_from_the_artifact": absent,
                "checks": checks,
                "why_the_distinction_matters": (
                    "The ledger's remedy is to freeze an atlas in which every formerly inert "
                    "coordinate varies. Varying across cases is not the same as differing within "
                    "one, and only the second produces a contrast. An atlas that populates "
                    "referent_ids with a different value in every case, but the same value on both "
                    "sides of each case, satisfies the stated condition and reproduces every zero "
                    "measured here. The success condition should read non-zero WITHIN-CASE "
                    "contrast."
                ),
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
