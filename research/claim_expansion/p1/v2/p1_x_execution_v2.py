from __future__ import annotations

from typing import Any

import sys
from pathlib import Path

P1X = Path(__file__).resolve().parents[1]
if str(P1X) not in sys.path:
    sys.path.insert(0, str(P1X))

import p1_x_execution as v1  # noqa: E402


def decide_b1_donor_complete_greedy_v2(runtime: v1.ExecutionRuntime) -> dict[str, Any]:
    visible = runtime.visible
    statuses = v1._status_map(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(status == "UNTESTED" for status in statuses.values()) and not unknown:
        return v1._decision("NO_CHANGE")
    if unknown and not any(status == "SUCCEEDED" for status in statuses.values()):
        if visible["candidate_visible"]["discriminator_status"] != "UNAVAILABLE":
            return v1._decision("CANNOT_CHECK")

    priority = {"SUCCEEDED": 0, "CANNOT_CHECK": 1, "UNTESTED": 2, "FAILED": 3}
    order = v1._candidate_order(visible)
    order.sort(key=lambda candidate: priority.get(statuses.get(candidate, "UNTESTED"), 2))
    proposals = v1._proposal_map(visible)

    for candidate in order:
        item = runtime.check_revision(candidate)
        if not v1._passes_generic_checks(item):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in v1.HIGH_LEVEL else "REPAIR_LOCAL"
        reopen = proposals[candidate]["proposed_reopen_set"] if candidate in v1.HIGH_LEVEL else []
        return v1._decision(terminal, candidate, reopen)
    return v1._decision("CANNOT_CHECK")


def decide_b2_success_authorizes_reframe_v2(runtime: v1.ExecutionRuntime) -> dict[str, Any]:
    visible = runtime.visible
    statuses = v1._status_map(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(status == "UNTESTED" for status in statuses.values()) and not unknown:
        return v1._decision("NO_CHANGE")
    if unknown and not any(status == "SUCCEEDED" for status in statuses.values()):
        return v1._decision("CANNOT_CHECK")

    proposals = v1._proposal_map(visible)
    order = v1._candidate_order(visible)
    succeeded_high = [
        candidate
        for candidate in order
        if candidate in v1.HIGH_LEVEL and statuses.get(candidate) == "SUCCEEDED"
    ]
    succeeded_other = [
        candidate
        for candidate in order
        if candidate not in v1.HIGH_LEVEL and statuses.get(candidate) == "SUCCEEDED"
    ]
    fallback = [candidate for candidate in order if candidate not in succeeded_high + succeeded_other]

    for candidate in succeeded_high + succeeded_other + fallback:
        item = runtime.check_revision(candidate)
        if not v1._passes_generic_checks(item):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in v1.HIGH_LEVEL else "REPAIR_LOCAL"
        reopen = proposals[candidate]["proposed_reopen_set"] if candidate in v1.HIGH_LEVEL else []
        return v1._decision(terminal, candidate, reopen)
    return v1._decision("CANNOT_CHECK")


ARM_FUNCTIONS_V2 = {
    "B1_DONOR_COMPLETE_GREEDY": decide_b1_donor_complete_greedy_v2,
    "B2_SUCCESS_AUTHORIZES_REFRAME": decide_b2_success_authorizes_reframe_v2,
    "B3_IDEAL_TYPED_PRODUCT": v1.decide_b3_ideal_typed_product,
    "P1X_MINIMAL_SCIENTIFIC_ESCALATION": v1.decide_p1x,
}


def run_arm_v2(case: dict[str, Any], arm_id: str) -> dict[str, Any]:
    runtime = v1.ExecutionRuntime(case)
    result = ARM_FUNCTIONS_V2[arm_id](runtime)
    result["checks_used"] = runtime.checks_used
    return result

score_esrd = v1.score_esrd
false_high_level_reframe = v1.false_high_level_reframe
invariant_violation = v1.invariant_violation
