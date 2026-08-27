#!/usr/bin/env python3
"""Run the P4 identifiability register over the v1, v2 and v3 constructions.

One instrument, three constructions, three terminals. The protocol this executes
is frozen in ``FREEZE.md`` beside this file; the seeds are named there so that a
seed cannot be chosen after the fact.

Emits ``IDENTIFIABILITY_V3.json``: every probe's confusion matrix and
informedness, for every (construction, terminal) pair, plus the seed-invariance
check on v3.

Reads no panel output. It is run, and its result recorded, before the frozen
panel is executed --- that ordering is the whole point of the exercise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
GENERATOR = (
    ROOT
    / "papers"
    / "paper-04-verified-scientific-discovery"
    / "host"
    / "generate_protected_cases.py"
)
HERE = Path(__file__).resolve().parent

AUDIT_SEED = "v3-audit-20260821"
INVARIANCE_SEEDS = ("v3-audit-alt-a", "v3-audit-alt-b")
CONSTRUCTIONS = ("v1", "v2", "v3")
TERMINALS = ("CANNOT_CHECK", "PROMOTE", "BLOCK")
CEILING = 0.0


def _generator() -> Any:
    spec = importlib.util.spec_from_file_location("p4_case_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the P4 case generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def battery(seed: str, construction: str) -> list[dict[str, Any]]:
    generator = _generator()
    cases: list[dict[str, Any]] = []
    ordinal = 0
    for family in generator.FAMILIES:
        for within_family in range(generator.COUNTS[family]):
            cases.append(
                generator._case(
                    seed, ordinal, family, within_family, construction=construction
                )
            )
            ordinal += 1
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "IDENTIFIABILITY_V3.json")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "src"))
    from orion.study.p4 import P4_SHORTCUT_PROBES, audit_promotion_terminal

    report: dict[str, Any] = {
        "schema": "P4IdentifiabilityRegister.v1",
        "freeze_document": "research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md",
        "audit_seed": AUDIT_SEED,
        "informedness_ceiling": CEILING,
        "probe_count": len(P4_SHORTCUT_PROBES),
        "probes": [
            {
                "probe_id": probe.probe_id,
                "kind": probe.kind.value,
                "cue_names": list(probe.cue_names),
                "rationale": probe.cue_rationale,
            }
            for probe in P4_SHORTCUT_PROBES
        ],
        "constructions": {},
        "seed_invariance": {},
    }

    for construction in CONSTRUCTIONS:
        cases = battery(AUDIT_SEED, construction)
        entry: dict[str, Any] = {"case_count": len(cases), "terminals": {}}
        for terminal in TERMINALS:
            audit = audit_promotion_terminal(
                cases, label=terminal, max_recovery=CEILING
            )
            entry["terminals"][terminal] = audit.as_json()
        report["constructions"][construction] = entry

    # The two seeds named in FREEZE.md, plus a wider mechanically-named sweep. The
    # sweep exists because one probe in the register --- digest-prefix --- is a
    # noise control that fires at 0.05 on the v1 and v2 PROMOTE axes, and a
    # ceiling of 0.0 will fail on any seed where sixteen digest buckets happen to
    # be dominated by a minority label. Reporting the whole sweep is the only way
    # to say whether v3's clean audit is a property of the construction or of one
    # lucky seed.
    sweep = (
        AUDIT_SEED,
        *INVARIANCE_SEEDS,
        *(f"v3-invariance-{index:02d}" for index in range(10)),
    )
    for seed in sweep:
        cases = battery(seed, "v3")
        block: dict[str, Any] = {}
        for terminal in TERMINALS:
            audit = audit_promotion_terminal(
                cases, label=terminal, max_recovery=CEILING
            )
            block[terminal] = {
                "outcome": audit.outcome.value,
                "reason": audit.reason.value,
                "worst_recovery": audit.worst_recovery,
                "worst_probe": max(
                    (item for item in audit.results if item.recovery is not None),
                    key=lambda item: item.recovery or 0.0,
                ).probe_id,
            }
        report["seed_invariance"][seed] = block

    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    for construction in CONSTRUCTIONS:
        for terminal in TERMINALS:
            block = report["constructions"][construction]["terminals"][terminal]
            print(f"\n=== {construction} / {terminal}: {block['outcome']} ({block['reason']})")
            for result in block["results"]:
                print(
                    f"  {result['probe_id']:<28} recovery={result['recovery']!s:<6} "
                    f"tp={result['true_positive']:>3}/{result['true_positive'] + result['false_negative']:<3} "
                    f"fp={result['false_positive']:>3}/{result['false_positive'] + result['true_negative']:<3} "
                    f"unscored={result['unscored']}"
                )
    print("\nseed sweep (v3):")
    for seed, block in report["seed_invariance"].items():
        summary = "  ".join(
            f"{terminal}={block[terminal]['outcome']}/{block[terminal]['worst_recovery']}"
            for terminal in TERMINALS
        )
        print(f"  {seed:<24} {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
