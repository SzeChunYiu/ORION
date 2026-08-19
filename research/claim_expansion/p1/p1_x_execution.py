from __future__ import annotations

from copy import deepcopy
from typing import Any

HIGH_LEVEL = {
    "MODEL_CLASS_EXPANSION",
    "REPRESENTATION_REGIME_REVISION",
    "QUESTION_OBJECTIVE_REVISION",
    "METHOD_BASIS_REVISION",
}

ACTION_TERMINALS = {"REPAIR_LOCAL", "REVISE_HIGH_LEVEL"}


def _decision(terminal: str, revision_class: str | None = None, reopen_set: list[str] | None = None) -> dict[str, Any]:
    return {
        "terminal": terminal,
        "revision_class": revision_class,
        "reopen_set": list(reopen_set or []),
    }


class ExecutionRuntime:
    """Shared protected check interface. Controllers never receive protected_gold directly."""

    def __init__(self, case: dict[str, Any]):
        self.visible = {key: deepcopy(value) for key, value in case.items() if key != "protected_gold"}
        self._evaluations = {
            item["candidate_class"]: deepcopy(item)
            for item in case["protected_gold"]["revision_evaluations"]
        }
        self._checks = 0
        self._max_checks = int(case["budget"]["max_interventions"])

    @property
    def checks_used(self) -> int:
        return self._checks

    def check_revision(self, candidate_class: str) -> dict[str, Any] | None:
        if self._checks >= self._max_checks:
            return None
        self._checks += 1
        item = self._evaluations.get(candidate_class)
        return deepcopy(item) if item is not None else None


def _status_map(visible: dict[str, Any]) -> dict[str, str]:
    return {
        item["candidate_class"]: item["candidate_visible_status"]
        for item in visible["registered_narrower_alternatives"]
    }


def _proposal_map(visible: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["candidate_class"]: item
        for item in visible["candidate_visible"]["revision_proposals"]
    }


def _candidate_order(visible: dict[str, Any]) -> list[str]:
    return [item["candidate_class"] for item in visible["candidate_visible"]["revision_proposals"]]


def _transitive_less_than(edges: list[list[str]], narrower: str, broader: str) -> bool:
    if narrower == broader:
        return False
    graph: dict[str, set[str]] = {}
    for left, right in edges:
        graph.setdefault(left, set()).add(right)
    frontier = [narrower]
    seen = set()
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph.get(node, ()):
            if nxt == broader:
                return True
            frontier.append(nxt)
    return False


def _minimal_classes(classes: list[str], edges: list[list[str]]) -> list[str]:
    return [
        candidate
        for candidate in classes
        if not any(
            other != candidate and _transitive_less_than(edges, other, candidate)
            for other in classes
        )
    ]


def _early_nonaction_terminal(visible: dict[str, Any]) -> str | None:
    statuses = list(_status_map(visible).values())
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    discriminator = visible["candidate_visible"]["discriminator_status"]
    if discriminator == "AVAILABLE":
        return "REQUEST_DISCRIMINATOR"
    if discriminator == "UNAVAILABLE":
        return "UNRESOLVED"
    if statuses and all(status == "UNTESTED" for status in statuses) and not unknown:
        return "NO_CHANGE"
    if unknown and not any(status == "SUCCEEDED" for status in statuses):
        return "CANNOT_CHECK"
    return None


def _passes_generic_checks(item: dict[str, Any] | None) -> bool:
    return bool(
        item is not None
        and item["restores_target"]
        and item["preserves_invariants"]
        and item["authorized"]
    )


def decide_p1x(runtime: ExecutionRuntime) -> dict[str, Any]:
    visible = runtime.visible
    early = _early_nonaction_terminal(visible)
    if early is not None:
        return _decision(early)

    statuses = _status_map(visible)
    successes = [candidate for candidate, status in statuses.items() if status == "SUCCEEDED"]
    if not successes:
        return _decision("CANNOT_CHECK")

    checked: dict[str, dict[str, Any]] = {}
    for candidate in successes:
        item = runtime.check_revision(candidate)
        if item is None:
            return _decision("CANNOT_CHECK")
        if _passes_generic_checks(item):
            checked[candidate] = item

    if not checked:
        return _decision("CANNOT_CHECK")

    minima = _minimal_classes(list(checked), visible["invasiveness_edges"])
    if len(minima) > 1:
        discriminator = visible["candidate_visible"]["discriminator_status"]
        if discriminator == "AVAILABLE":
            return _decision("REQUEST_DISCRIMINATOR")
        return _decision("UNRESOLVED")

    candidate = minima[0]
    item = checked[candidate]
    terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH_LEVEL else "REPAIR_LOCAL"
    # P1-X binds the execution certificate to observed dependency impact rather than
    # executing a stale/over-broad proposal.
    reopen = item["observed_reopen_set"] if candidate in HIGH_LEVEL else []
    return _decision(terminal, candidate, reopen)


def decide_b1_donor_complete_greedy(runtime: ExecutionRuntime) -> dict[str, Any]:
    visible = runtime.visible
    statuses = _status_map(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(status == "UNTESTED" for status in statuses) and not unknown:
        return _decision("NO_CHANGE")
    if unknown and not any(status == "SUCCEEDED" for status in statuses):
        # A donor-complete product is allowed to fail closed on missing evidence, but
        # it has no dedicated incomparable-minima semantics when checks are possible.
        if visible["candidate_visible"]["discriminator_status"] == "UNAVAILABLE":
            pass
        else:
            return _decision("CANNOT_CHECK")

    priority = {"SUCCEEDED": 0, "CANNOT_CHECK": 1, "UNTESTED": 2, "FAILED": 3}
    order = _candidate_order(visible)
    order.sort(key=lambda candidate: priority.get(statuses.get(candidate, "UNTESTED"), 2))
    proposals = _proposal_map(visible)

    for candidate in order:
        item = runtime.check_revision(candidate)
        if not _passes_generic_checks(item):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH_LEVEL else "REPAIR_LOCAL"
        # B1 preserves the candidate's proposed reopen set; it does not add the P1-X
        # observed-impact rebinding rule.
        reopen = proposals[candidate]["proposed_reopen_set"] if candidate in HIGH_LEVEL else []
        return _decision(terminal, candidate, reopen)
    return _decision("CANNOT_CHECK")


def decide_b2_success_authorizes_reframe(runtime: ExecutionRuntime) -> dict[str, Any]:
    visible = runtime.visible
    statuses = _status_map(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(status == "UNTESTED" for status in statuses) and not unknown:
        return _decision("NO_CHANGE")
    if unknown and not any(status == "SUCCEEDED" for status in statuses):
        return _decision("CANNOT_CHECK")

    proposals = _proposal_map(visible)
    order = _candidate_order(visible)
    succeeded_high = [
        candidate for candidate in order if candidate in HIGH_LEVEL and statuses.get(candidate) == "SUCCEEDED"
    ]
    succeeded_other = [
        candidate for candidate in order if candidate not in HIGH_LEVEL and statuses.get(candidate) == "SUCCEEDED"
    ]
    fallback = [candidate for candidate in order if candidate not in succeeded_high + succeeded_other]

    for candidate in succeeded_high + succeeded_other + fallback:
        item = runtime.check_revision(candidate)
        if not _passes_generic_checks(item):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH_LEVEL else "REPAIR_LOCAL"
        reopen = proposals[candidate]["proposed_reopen_set"] if candidate in HIGH_LEVEL else []
        return _decision(terminal, candidate, reopen)
    return _decision("CANNOT_CHECK")


def decide_b3_ideal_typed_product(runtime: ExecutionRuntime) -> dict[str, Any]:
    # The ideal product is deliberately extensionally equivalent when given the same
    # semantics. This is a boundary theorem encoded as an executable oracle.
    return decide_p1x(runtime)


ARM_FUNCTIONS = {
    "B1_DONOR_COMPLETE_GREEDY": decide_b1_donor_complete_greedy,
    "B2_SUCCESS_AUTHORIZES_REFRAME": decide_b2_success_authorizes_reframe,
    "B3_IDEAL_TYPED_PRODUCT": decide_b3_ideal_typed_product,
    "P1X_MINIMAL_SCIENTIFIC_ESCALATION": decide_p1x,
}


def run_arm(case: dict[str, Any], arm_id: str) -> dict[str, Any]:
    runtime = ExecutionRuntime(case)
    result = ARM_FUNCTIONS[arm_id](runtime)
    result["checks_used"] = runtime.checks_used
    return result


def score_esrd(case: dict[str, Any], decision: dict[str, Any]) -> int:
    gold = case["protected_gold"]
    if decision["terminal"] != gold["correct_terminal"]:
        return 0
    if decision["terminal"] not in ACTION_TERMINALS:
        return int(decision["revision_class"] is None and decision["reopen_set"] == [])

    candidate = decision["revision_class"]
    if candidate not in gold["scientifically_justified_revision_set"]:
        return 0
    evaluation = next(
        (item for item in gold["revision_evaluations"] if item["candidate_class"] == candidate),
        None,
    )
    if not _passes_generic_checks(evaluation):
        return 0
    if decision["reopen_set"] != gold["exact_reopen_set"]:
        return 0
    return 1


def false_high_level_reframe(case: dict[str, Any], decision: dict[str, Any]) -> int:
    return int(
        decision["terminal"] == "REVISE_HIGH_LEVEL"
        and case["protected_gold"]["correct_terminal"] != "REVISE_HIGH_LEVEL"
    )


def invariant_violation(case: dict[str, Any], decision: dict[str, Any]) -> int:
    candidate = decision["revision_class"]
    if candidate is None:
        return 0
    evaluation = next(
        (item for item in case["protected_gold"]["revision_evaluations"] if item["candidate_class"] == candidate),
        None,
    )
    return int(evaluation is not None and not evaluation["preserves_invariants"])
