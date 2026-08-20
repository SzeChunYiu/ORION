"""Exact ORION-Q MAX-R1 cross-domain research-operator information lattice.

No learner is required. The benchmark constructs hostile same-information pairs in
four synthetic quantum-research domains and computes exact deterministic ceilings
for progressively richer views.

Authority: exact synthetic representation/state result only. No P10 or quantum
novelty authority.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json

DOMAINS = ("SYNTHESIS", "ALGO_INTERFACE", "QEC_CODESIGN", "FORMAL_REASONING")
REMINTS_PER_DOMAIN = 100

BASE_FIELDS = (
    "search_exhausted",
    "evidence_sufficient",
    "verifier_available",
    "verifier_budget_available",
    "previous_failure",
    "representation_changed",
    "access_changed",
    "representation_obstruction_witness",
    "interface_obstruction_witness",
    "language_obstruction_witness",
    "alternate_representation_available",
    "interface_constructible",
)
SCOPE_FIELDS = (
    "failure_required_same_representation",
    "failure_required_same_access",
)
ALL_FIELDS = BASE_FIELDS + SCOPE_FIELDS

ACTIONS = (
    "SEARCH_MORE",
    "VERIFY_MORE",
    "REOPEN_METHOD",
    "CHANGE_REPRESENTATION",
    "CHANGE_INTERFACE",
    "GROW_LANGUAGE",
    "CANNOT_CHECK",
)
ESCALATION_ACTIONS = {
    "CHANGE_REPRESENTATION",
    "CHANGE_INTERFACE",
    "GROW_LANGUAGE",
}


def make_state(**values: bool) -> dict[str, bool]:
    state = {field: False for field in ALL_FIELDS}
    state.update(values)
    return state


PAIR_STATES = {
    "verify_vs_cannot": (
        make_state(
            verifier_available=True,
            verifier_budget_available=True,
            alternate_representation_available=True,
            interface_constructible=True,
        ),
        make_state(
            representation_changed=True,
            access_changed=True,
            alternate_representation_available=True,
            interface_constructible=True,
        ),
    ),
    "search_vs_grow": (
        make_state(
            evidence_sufficient=True,
            verifier_available=True,
            alternate_representation_available=True,
            interface_constructible=True,
        ),
        make_state(
            search_exhausted=True,
            evidence_sufficient=True,
            language_obstruction_witness=True,
            alternate_representation_available=True,
        ),
    ),
    "representation_vs_interface": (
        make_state(
            search_exhausted=True,
            evidence_sufficient=True,
            representation_obstruction_witness=True,
            alternate_representation_available=True,
        ),
        make_state(
            search_exhausted=True,
            evidence_sufficient=True,
            interface_obstruction_witness=True,
            interface_constructible=True,
        ),
    ),
    "stale_vs_still_applicable_failure": (
        make_state(
            search_exhausted=True,
            evidence_sufficient=True,
            previous_failure=True,
            representation_changed=True,
            failure_required_same_representation=True,
        ),
        make_state(
            search_exhausted=True,
            evidence_sufficient=True,
            previous_failure=True,
            representation_changed=True,
            failure_required_same_access=True,
        ),
    ),
}


def gold_action(state: dict[str, bool]) -> str:
    if not state["evidence_sufficient"]:
        if state["verifier_available"] and state["verifier_budget_available"]:
            return "VERIFY_MORE"
        return "CANNOT_CHECK"

    if state["previous_failure"]:
        reopen = (
            state["failure_required_same_representation"]
            and state["representation_changed"]
        ) or (
            state["failure_required_same_access"] and state["access_changed"]
        )
        if reopen:
            return "REOPEN_METHOD"

    obstruction = (
        state["representation_obstruction_witness"]
        or state["interface_obstruction_witness"]
        or state["language_obstruction_witness"]
    )
    if not state["search_exhausted"] and not obstruction:
        return "SEARCH_MORE"
    if (
        state["representation_obstruction_witness"]
        and state["alternate_representation_available"]
    ):
        return "CHANGE_REPRESENTATION"
    if state["interface_obstruction_witness"] and state["interface_constructible"]:
        return "CHANGE_INTERFACE"
    if state["language_obstruction_witness"]:
        return "GROW_LANGUAGE"
    return "CANNOT_CHECK"


def typed_without_scope_rule(state: dict[str, bool]) -> str:
    """Strong V3 rule with failure binding intentionally unavailable."""

    if not state["evidence_sufficient"]:
        if state["verifier_available"] and state["verifier_budget_available"]:
            return "VERIFY_MORE"
        return "CANNOT_CHECK"
    if state["previous_failure"] and (
        state["representation_changed"] or state["access_changed"]
    ):
        return "REOPEN_METHOD"
    obstruction = (
        state["representation_obstruction_witness"]
        or state["interface_obstruction_witness"]
        or state["language_obstruction_witness"]
    )
    if not state["search_exhausted"] and not obstruction:
        return "SEARCH_MORE"
    if (
        state["representation_obstruction_witness"]
        and state["alternate_representation_available"]
    ):
        return "CHANGE_REPRESENTATION"
    if state["interface_obstruction_witness"] and state["interface_constructible"]:
        return "CHANGE_INTERFACE"
    if state["language_obstruction_witness"]:
        return "GROW_LANGUAGE"
    return "CANNOT_CHECK"


def digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def view_payload(view: str, surface: str, state: dict[str, bool]) -> object:
    if view == "V0_SURFACE":
        return {"surface": surface}
    if view == "V1_UNTYPED_BAG":
        return {
            "surface": surface,
            "values": sorted(int(state[field]) for field in ALL_FIELDS),
        }
    if view == "V2_RAW_HISTORY":
        return {
            "surface": surface,
            "previous_failure": int(state["previous_failure"]),
            "values": sorted(
                int(state[field])
                for field in BASE_FIELDS
                if field != "previous_failure"
            ),
        }
    if view == "V3_TYPED_STATE":
        return {
            "surface": surface,
            "typed": {field: int(state[field]) for field in BASE_FIELDS},
        }
    if view == "V4_TYPED_SCOPED_FAILURE":
        return {
            "surface": surface,
            "typed": {field: int(state[field]) for field in ALL_FIELDS},
        }
    raise ValueError(f"unsupported view: {view}")


def deterministic_ceiling(samples: list[tuple[str, dict[str, bool], str]], view: str) -> dict[str, object]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for surface, state, label in samples:
        buckets[digest(view_payload(view, surface, state))].append(label)
    correct = sum(max(Counter(labels).values()) for labels in buckets.values())
    return {
        "accuracy": correct / len(samples),
        "distinct_views": len(buckets),
        "ambiguous_view_buckets": sum(
            1 for labels in buckets.values() if len(set(labels)) > 1
        ),
    }


def main() -> None:
    samples: list[tuple[str, dict[str, bool], str]] = []
    per_domain_correct = Counter()
    per_domain_total = Counter()
    false_escalations = 0
    cannot_total = 0
    cannot_correct = 0

    for domain in DOMAINS:
        for remint in range(REMINTS_PER_DOMAIN):
            for pair_name, states in PAIR_STATES.items():
                surface = digest(
                    {"domain": domain, "remint": remint, "pair": pair_name}
                )[:16]
                # Same-information check for V1 is load-bearing.
                left_bag = view_payload("V1_UNTYPED_BAG", surface, states[0])
                right_bag = view_payload("V1_UNTYPED_BAG", surface, states[1])
                if left_bag != right_bag:
                    raise AssertionError(f"V1 information mismatch in {pair_name}")

                for state in states:
                    label = gold_action(state)
                    samples.append((surface, state, label))
                    predicted = gold_action(state)
                    per_domain_correct[domain] += int(predicted == label)
                    per_domain_total[domain] += 1
                    if predicted in ESCALATION_ACTIONS and label not in ESCALATION_ACTIONS:
                        false_escalations += 1
                    if label == "CANNOT_CHECK":
                        cannot_total += 1
                        cannot_correct += int(predicted == label)

    views = (
        "V0_SURFACE",
        "V1_UNTYPED_BAG",
        "V2_RAW_HISTORY",
        "V3_TYPED_STATE",
        "V4_TYPED_SCOPED_FAILURE",
    )
    ceilings = {view: deterministic_ceiling(samples, view) for view in views}

    v3_accuracy = fmean(
        1.0 if typed_without_scope_rule(state) == label else 0.0
        for _, state, label in samples
    )

    labels = Counter(label for _, _, label in samples)
    majority = max(labels.values()) / len(samples)

    result = {
        "schema": "ORIONQ.MAXR1OperatorArbitrationResult.v1",
        "domains": list(DOMAINS),
        "remints_per_domain": REMINTS_PER_DOMAIN,
        "sample_count": len(samples),
        "majority_accuracy": majority,
        "view_ceilings": ceilings,
        "v3_frozen_rule_accuracy": v3_accuracy,
        "v4_frozen_rule_accuracy_by_domain": {
            domain: per_domain_correct[domain] / per_domain_total[domain]
            for domain in DOMAINS
        },
        "false_escalation_rate": false_escalations / len(samples),
        "cannot_check_accuracy": cannot_correct / cannot_total,
        "terminal": "MAX_R1_TYPED_RESEARCH_OPERATOR_ARBITRATION_SUPPORTED__EXACT_SYNTHETIC",
        "authority": "exact_synthetic_state_only",
        "p10_authorized": False,
        "novelty_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    from statistics import fmean

    main()
