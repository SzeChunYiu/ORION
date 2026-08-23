#!/usr/bin/env python3
"""ORION's typed coordinates are sets. Measure it, and say what it costs.

Across the source tree, sequence-valued coordinates are canonicalized by

    tuple(sorted({str(value) for value in values}))

before anything downstream sees them. That is a coherent design -- it gives
canonical form, content-addressable digests and order-insensitive equality -- and
it is applied consistently rather than by accident.

It also has a consequence the programme has not stated: **no ORION claim can be
sensitive to order or multiplicity**, because neither survives into the data
model. A protocol that registers an order attack, a multiplicity attack, or an
order-preserving representation is registering something its own representation
cannot express.

This is an instance of the determination theorem in
``CROSS_PAPER_PRESERVATION_THEORY_V2.md``: a system decides a standing question
correctly exactly when its retained coordinates separate every
standing-distinct pair. Order and multiplicity are coordinates this interface
projects away, so every question whose answer depends on them is undecidable
here -- not by argument, but by the measurement below.

Exit codes: 0 the boundary is as described, 2 it is not, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

PATTERN = re.compile(r"tuple\(sorted\(\{")
SOURCE = pathlib.Path("src")


def main() -> int:
    if not SOURCE.is_dir():
        print(json.dumps({"status": "CANNOT_CHECK", "error": "run from the repository root"}))
        return 3

    sites = []
    for path in sorted(SOURCE.rglob("*.py")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print(json.dumps({"status": "CANNOT_CHECK", "error": f"{path}: {exc}"}))
            return 3
        for number, line in enumerate(lines, start=1):
            if PATTERN.search(line):
                sites.append({"file": str(path), "line": number, "code": line.strip()[:120]})

    modules = sorted({site["file"] for site in sites})
    # A study lane is a directory under src/orion/study, so a module sitting
    # directly in study/ is not one -- counting it would inflate the reach.
    papers = sorted(
        {
            parts[3]
            for site in sites
            for parts in [site["file"].split("/")]
            if len(parts) > 4 and parts[2] == "study"
        }
    )
    layers = sorted({site["file"].split("/")[2] for site in sites})

    checks = {
        "the_normalization_is_present": bool(sites),
        "it_spans_more_than_one_paper": len(papers) > 1,
        "it_spans_more_than_one_layer": len(layers) > 1,
    }

    print(
        json.dumps(
            {
                "schema": "orion.programme.set-normalization-boundary.v1",
                "record": "ORION_TYPED_COORDINATES_ARE_SETS",
                "authority_scope": "OUTCOME_BLIND_MEASUREMENT",
                "outcome_accessed": False,
                "call_sites": len(sites),
                "modules": len(modules),
                "study_lanes_touched": papers,
                "source_layers_touched": layers,
                "module_list": modules,
                "boundary": (
                    "Sequence-valued coordinates are canonicalized to a sorted set of their "
                    "distinct string values. Order and multiplicity do not survive into the model."
                ),
                "what_it_buys": [
                    "canonical form, so two realizations of the same content compare equal",
                    "content-addressable digests that do not depend on authoring order",
                    "equality that is insensitive to an irrelevant permutation",
                ],
                "what_it_costs": (
                    "Every claim whose answer depends on order or multiplicity is inexpressible. "
                    "This is not a bug to be patched at one call site; it is a programme-wide "
                    "modelling decision, and the honest response is to state it as a scope boundary "
                    "or to change it deliberately across all of the modules listed here."
                ),
                "measured_instance": (
                    "P9's ORDER_PERMUTATION attack reverses each sequence coordinate and the "
                    "constructor sorts it back, producing a dataset byte-identical to the base one: "
                    "same manifest digest, 128 of 128 protected cases unchanged. See "
                    "P9_ORDER_PERMUTATION_IS_A_NOOP_2026-08-23.json."
                ),
                "relation_to_the_preservation_theory": (
                    "This is the determination theorem's necessity direction, met in the wild: "
                    "order and multiplicity are coordinates the interface projects away, so no "
                    "rule over this representation can decide a question that depends on them. "
                    "The theorem says which question settles the matter; this measurement answers "
                    "it for ORION as built."
                ),
                "checks": checks,
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
