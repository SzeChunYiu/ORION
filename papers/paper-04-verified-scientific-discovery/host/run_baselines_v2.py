#!/usr/bin/env python3
"""P4 V2 gold-blind comparator runner.

Reuses the frozen V1 mechanism implementations and adds the seventh frozen
nearest-work comparator present in the repaired subject: DeepSciVerify-style
abstract-to-full escalation. Input is restricted to opaque ``case_id`` plus
``candidate_visible``; no protected gold or attack-family label is accepted.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("p4_run_baselines_v1", _HERE / "run_baselines.py")
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load frozen P4 V1 baseline runner")
_v1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_v1)

DEEPSCI_ID = "deepsciverify-abstract-to-full-escalation"


def _deepsci(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    """Two-stage assigned-source verification with full-pool escalation.

    Stage 1 accepts exact, attributed assigned evidence with direct support.
    When assigned evidence is unresolved but exact/attributed, stage 2 inspects
    the candidate-visible retrieval pool. Wrong ownership or broken content
    remains fail-closed rather than being repaired by pooled support.
    """
    started = time.perf_counter_ns()
    item = _v1._assigned(view)
    pool = _v1._pool(view)
    if item is None:
        return _v1._result(
            case_id,
            DEEPSCI_ID,
            terminal="CANNOT_CHECK",
            claim_prediction=False,
            source_prediction=False,
            support_prediction="INSUFFICIENT",
            conflation=False,
            substitution=False,
            tamper=False,
            contamination=False,
            resource_units=6.5,
            started_ns=started,
        )

    content = _v1._content_valid(item)
    source = _v1._source_match(item)
    direct_support = _v1._supports(view, item)
    direct_contradiction = _v1._contradicts(view, item)
    pooled_support = _v1._pooled_support(view)
    pooled_contradiction = _v1._pooled_contradiction(view)

    if direct_contradiction:
        terminal = "BLOCK"
    elif content and source and direct_support:
        terminal = "PROMOTE"
    elif content and source and pooled_support and not pooled_contradiction:
        terminal = "PROMOTE"
    elif not content or not source:
        terminal = "BLOCK"
    else:
        terminal = "CANNOT_CHECK"

    support_prediction = _v1._support_label(
        direct_support or (content and source and pooled_support),
        direct_contradiction or pooled_contradiction,
    )
    return _v1._result(
        case_id,
        DEEPSCI_ID,
        terminal=terminal,
        claim_prediction=support_prediction == "SUPPORTED",
        source_prediction=source,
        support_prediction=support_prediction,
        conflation=not source,
        substitution=not content,
        tamper=False,
        contamination=False,
        resource_units=6.5,
        started_ns=started,
    )


def _read(path: Path) -> list[dict[str, Any]]:
    return _v1._read_cases(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    cases = _read(args.manifest)
    runners = (*_v1.RUNNERS, _deepsci)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in cases:
            for runner in runners:
                handle.write(
                    json.dumps(
                        runner(row["case_id"], row["candidate_visible"]),
                        sort_keys=True,
                    )
                    + "\n"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
