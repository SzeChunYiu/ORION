#!/usr/bin/env python3
"""Build P2's route/task closure-receipt ledger for both campaigns (#650).

Issue #650 asks for route-level and task-level closure receipts. This script
produces them for the two campaigns P2 actually has, and reports each one's
false-closure guard *with its denominator*:

1. The frozen 390-task controlled complete-gold world, replayed here from
   ``orion.study.p2`` at the frozen seed. Receipts are built by
   ``closure_receipts.build_task_receipt`` from the host evaluation and trace.

2. The 24-task external Wide acquisition slice. Its runs are not re-executable
   (the frozen adapter binds arXiv/OpenAlex and the official scorer consumes
   arXiv-id sets), so its receipts are reconstructed from the counters the
   campaign itself recorded in
   ``evidence/external_results/P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json``:
   ``tasks_closed_as_complete`` and ``tasks_with_open_obligations``, both 0 for
   both arms. Reconstruction is stated in the artifact and the source digest is
   carried, so a reader can check the derivation.

The point of putting them side by side is that the same guard reports zero in
both, and only one of those zeros is a result.

Usage::

    python papers/orion-12-open-world-scientific-discovery/scripts/\
build_closure_receipt_ledger.py [--out PATH] [--systems id,id,...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from orion.programme.guard_exercise import assess_guard, assess_non_inferiority  # noqa: E402
from orion.study.p2.cases import build_tasks  # noqa: E402
from orion.study.p2.closure_receipts import (  # noqa: E402
    FALSE_CLOSURE_GUARD_ID,
    FALSE_CLOSURE_OPPORTUNITY,
    CampaignClosureLedger,
    FalseClosureKind,
    RouteClosureKind,
    RouteClosureReceipt,
    TaskClosureKind,
    TaskClosureReceipt,
    build_ledger,
    require_closure_receipts,
)
from orion.study.p2.corpus import build_world  # noqa: E402
from orion.study.p2.gold import EvaluationInputs, evaluate  # noqa: E402
from orion.study.p2.offline_systems import ALL_SYSTEMS, system_by_id  # noqa: E402
from orion.study.p2.runner import build_public_index, execute  # noqa: E402

PAPER = REPO_ROOT / "papers" / "orion-12-open-world-scientific-discovery"
DEV3R = PAPER / "evidence" / "external_results" / "P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json"
SUMMARY_V1 = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
DEFAULT_OUT = PAPER / "evidence" / "offline_results" / "CLOSURE_RECEIPT_LEDGER_V1.json"

SEED = 20260816
RUN_MANIFEST_HASH = "0" * 64
ORION_ARM = "orion_full"


def _controlled_ledger(system_ids: tuple[str, ...]) -> CampaignClosureLedger:
    world = build_world(SEED)
    tasks = build_tasks(world)
    index = build_public_index(world)
    pairs = []
    for system_id in system_ids:
        system = system_by_id(system_id)
        for task in tasks:
            outcome = execute(
                system, world, task, seed=SEED, run_manifest_hash=RUN_MANIFEST_HASH, index=index
            )
            evaluation = evaluate(
                EvaluationInputs(world=world, task=task, trace=outcome.trace)
            )
            pairs.append((evaluation, outcome.trace))
        print(f"  replayed {system_id} over {len(tasks)} tasks", file=sys.stderr)

    ledger = build_ledger("p2-controlled-complete-gold-v1", pairs)
    require_closure_receipts(
        ledger,
        expected_arms=system_ids,
        expected_task_ids=[task.task_id for task in tasks],
    )
    return ledger


def _external_ledger() -> tuple[CampaignClosureLedger, dict[str, Any]]:
    """Reconstruct the external slice's receipts from its own recorded counters."""

    payload = json.loads(DEV3R.read_text(encoding="utf-8"))
    systems = payload["systems"]
    n_tasks = payload["official_metrics"]["candidate"]["total_records"]

    receipts: list[TaskClosureReceipt] = []
    for system_id, row in sorted(systems.items()):
        closed = int(row["tasks_closed_as_complete"])
        open_obligations = int(row["tasks_with_open_obligations"])
        if closed or open_obligations:
            raise SystemExit(
                f"{system_id}: this reconstruction is only valid for the recorded "
                f"0/0 counters; found closed={closed} open={open_obligations}"
            )
        calls = int(row["provider_requests"]) // n_tasks
        for position in range(n_tasks):
            receipts.append(
                TaskClosureReceipt(
                    system_id=system_id,
                    task_id=f"arb-wide-dev3r-{position:03d}",
                    seed=0,
                    kind=TaskClosureKind.STOPPED_WITHOUT_CLOSURE_CLAIM,
                    false_closure=FalseClosureKind.NONE,
                    reason="campaign recorded neither a closure claim nor an open obligation",
                    still_reachable_at_closure=0,
                    remaining_route_calls_at_closure=0,
                    route_receipts=(
                        RouteClosureReceipt(
                            route="arxiv_atom",
                            kind=RouteClosureKind.LEFT_OPEN,
                            attempts=calls,
                            premature_stops=0,
                            still_reachable_at_stop=0,
                            remaining_route_calls_at_stop=0,
                        ),
                    ),
                )
            )

    ledger = CampaignClosureLedger(
        campaign_id="p2-v2-external-wide-acquisition-dev3r", receipts=tuple(receipts)
    )
    provenance = {
        "reconstructed_from": str(DEV3R.relative_to(PAPER)),
        "source_sha256": hashlib.sha256(DEV3R.read_bytes()).hexdigest(),
        "derivation": (
            "tasks_closed_as_complete == 0 and tasks_with_open_obligations == 0 for "
            "every arm, so every task maps to STOPPED_WITHOUT_CLOSURE_CLAIM; no run "
            "was re-executed and no outcome was re-scored"
        ),
        "not_re_executed_because": [
            "FROZEN_ADAPTER_REQUIRES_ARXIV",
            "OFFICIAL_SCORER_ARXIV_ID_IOU",
            "NO_ARXIV_MATCHED_RUNNER_ON_MAIN",
        ],
    }
    return ledger, provenance


def _guard_block(ledger: CampaignClosureLedger, *, comparator_arms: tuple[str, ...]) -> dict[str, Any]:
    exercises = {arm: ledger.false_closure_exercise(arm) for arm in ledger.arms}
    block: dict[str, Any] = {
        "per_arm": {
            arm: assess_guard(exercise).as_json() for arm, exercise in sorted(exercises.items())
        }
    }
    if ORION_ARM in exercises:
        block["non_inferiority_vs_comparators"] = {
            arm: assess_non_inferiority(
                candidate=exercises[ORION_ARM], comparator=exercises[arm]
            ).as_json()
            for arm in comparator_arms
            if arm in exercises
        }
    return block


def _consistency_check(controlled: CampaignClosureLedger) -> dict[str, Any]:
    """Cross-check the receipts' numerators against the published V1 failure counts.

    The receipts change the *denominator*, never the numerator: if a run was a
    false closure under ``gold._status_and_failure`` it must be one here too.
    Checking that against an artifact this script did not produce is what makes
    the reframing an accounting correction rather than a new measurement. It is
    also how the missing censored-material disjunct was caught --- reading
    prematurity alone put ``no_unavailable_route_open_state`` at 0 against a
    published 12.
    """

    published = json.loads(SUMMARY_V1.read_text(encoding="utf-8"))["systems"]
    rows: dict[str, Any] = {}
    disagreements: list[str] = []
    for arm in controlled.arms:
        expected = int(published.get(arm, {}).get("failure_counts", {}).get("premature_closure", 0))
        observed = controlled.false_closure_exercise(arm).violations
        rows[arm] = {"published_v1_premature_closure": expected, "receipt_violations": observed}
        if expected != observed:
            disagreements.append(f"{arm}: published {expected} vs receipts {observed}")

    return {
        "source": str(SUMMARY_V1.relative_to(PAPER)),
        "source_sha256": hashlib.sha256(SUMMARY_V1.read_bytes()).hexdigest(),
        "compares": "false-closure numerators only; the denominator is what this ledger adds",
        "agreement": not disagreements,
        "disagreements": disagreements,
        "by_arm": rows,
    }


def _headline(controlled: CampaignClosureLedger, external: CampaignClosureLedger) -> dict[str, Any]:
    def summarize(ledger: CampaignClosureLedger) -> dict[str, Any]:
        return {
            arm: {
                "closures_claimed": ledger.false_closure_exercise(arm).opportunities,
                "false_closures": ledger.false_closure_exercise(arm).violations,
                "guard_exercised": ledger.false_closure_exercise(arm).exercised,
                "guard_outcome": assess_guard(ledger.false_closure_exercise(arm)).outcome.value,
            }
            for arm in ledger.arms
        }

    return {
        "controlled": summarize(controlled),
        "external_wide_dev3r": summarize(external),
        "finding": (
            "The false-closure guard reports zero violations in both campaigns. In the "
            "controlled campaign ORION earned that zero across a real denominator of "
            f"{controlled.false_closure_exercise(ORION_ARM).opportunities} declared closures. "
            "On the external Wide slice both arms declared zero closures, so the same zero is "
            "an absent measurement and every arm's guard is CANNOT_CHECK. A violation count "
            "without its denominator cannot tell those apart."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--systems",
        default="",
        help="comma-separated frozen system ids; default is every frozen system",
    )
    args = parser.parse_args()

    system_ids = (
        tuple(item.strip() for item in args.systems.split(",") if item.strip())
        if args.systems
        else tuple(system.system_id for system in ALL_SYSTEMS)
    )
    print(f"replaying {len(system_ids)} frozen systems", file=sys.stderr)

    controlled = _controlled_ledger(system_ids)
    external, provenance = _external_ledger()
    comparators = tuple(arm for arm in controlled.arms if arm != ORION_ARM)

    document = {
        "schema_version": "orion.p2.closure-receipt-ledger.v1",
        "issue": 650,
        "purpose": (
            "route-level and task-level closure receipts, and the guard denominators "
            "they make explicit"
        ),
        "seed": SEED,
        "headline": _headline(controlled, external),
        "consistency_check_vs_published_v1": _consistency_check(controlled),
        "campaigns": {
            "controlled_complete_gold_v1": {
                "ledger": controlled.as_json(),
                "false_closure_guard": _guard_block(controlled, comparator_arms=comparators),
                "replayed": True,
            },
            "external_wide_acquisition_dev3r": {
                "ledger": external.as_json(),
                "false_closure_guard": _guard_block(external, comparator_arms=()),
                "replayed": False,
                "provenance": provenance,
            },
        },
        "guard_vocabulary": {
            "guard_id": FALSE_CLOSURE_GUARD_ID,
            "opportunity": FALSE_CLOSURE_OPPORTUNITY,
            "unexercised_verdict": "CANNOT_CHECK",
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
