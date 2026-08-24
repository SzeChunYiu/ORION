#!/usr/bin/env python3
"""Finite witnesses for the P1--P5 adversarial theorem audit.

This is a standalone mathematical receipt generator, not pytest/CI and not an
empirical evaluation.  Every witness is intentionally minimal and readable.
"""

from __future__ import annotations

import json
from pathlib import Path


def bayes_error(probabilities: list[float]) -> float:
    return 1.0 - max(probabilities)


def main() -> None:
    cases: list[dict[str, object]] = []

    # P1: two equal classes need not force half error when they do not exhaust
    # the fibre.
    probabilities = [0.1, 0.1, 0.8]
    error = bayes_error(probabilities)
    cases.append(
        {
            "id": "P1_TWO_EQUAL_CLASSES_NOT_HALF_ERROR",
            "witness": {"conditional_class_probabilities": probabilities},
            "computed_bayes_error": error,
            "invalidates_unqualified_half_error": error < 0.5,
        }
    )

    # P1: the separately named licence coordinate can be redundant.
    worlds = [{"x": 0, "j": 0, "decision": 0}, {"x": 1, "j": 1, "decision": 1}]
    decoder = {world["x"]: world["decision"] for world in worlds}
    exact_without_j = all(decoder[world["x"]] == world["decision"] for world in worlds)
    cases.append(
        {
            "id": "P1_OMITTED_LICENCE_CAN_BE_REDUNDANT",
            "witness": worlds,
            "exact_reduced_decoder": decoder,
            "invalidates_unconditional_omission_impossibility": exact_without_j,
        }
    )

    # P2: the old R!=empty realizability premise says nothing about a refused
    # R=empty history.  It may be robust-safe, so the registry rule is not
    # maximal without a completeness premise for every failed guard.
    history = {
        "R": [],
        "registry_contract_flag": False,
        "compatible_world_closure_safe": [True, True],
    }
    registry_closes = not history["R"] and history["registry_contract_flag"]
    robust_safe = all(history["compatible_world_closure_safe"])
    cases.append(
        {
            "id": "P2_REGISTRY_NEEDS_COMPLETENESS_FOR_MAXIMALITY",
            "witness": history,
            "registry_closes": registry_closes,
            "robust_rule_closes": robust_safe,
            "strict_sound_extension_exists": robust_safe and not registry_closes,
        }
    )

    # P3: loose outer bounds are not a sharp credal interval.
    actual_credal_set = [0.5]
    outer_bounds = [0.2, 0.8]
    actual_false_merge_risk = max(1.0 - p for p in actual_credal_set)
    outer_formula = 1.0 - outer_bounds[0]
    cases.append(
        {
            "id": "P3_OUTER_INTERVAL_NOT_RISK_EQUALITY",
            "witness": {"credal_set": actual_credal_set, "reported_outer_bounds": outer_bounds},
            "actual_worst_false_merge_risk": actual_false_merge_risk,
            "outer_bound_expression": outer_formula,
            "equality_fails": actual_false_merge_risk != outer_formula,
        }
    )

    # P4: almost-sure correctness ignores a zero-mass world, pointwise
    # extensional factorization does not.
    p4_worlds = [
        {"world": "w0", "mass": 1.0, "state": "same", "target": 0},
        {"world": "w1", "mass": 0.0, "state": "same", "target": 1},
    ]
    almost_sure_error = sum(w["mass"] * (w["target"] != 0) for w in p4_worlds)
    pointwise_fibre_pure = len({w["target"] for w in p4_worlds}) == 1
    cases.append(
        {
            "id": "P4_AS_EXACT_NOT_POINTWISE_EXACT",
            "witness": p4_worlds,
            "almost_sure_error_of_constant_zero": almost_sure_error,
            "pointwise_fibre_pure": pointwise_fibre_pure,
            "quantifiers_differ": almost_sure_error == 0 and not pointwise_fibre_pure,
        }
    )

    # P5: ordinary classification formula requires target labels to be
    # available actions.
    p5_target_probabilities = {0: 1.0, 1: 0.0}
    available_actions = ["abstain"]
    actual_zero_one_risk = 1.0  # abstain differs from either target label
    displayed_classification_formula = 1.0 - max(p5_target_probabilities.values())
    cases.append(
        {
            "id": "P5_UNAVAILABLE_LABEL_BREAKS_ZERO_ONE_SPECIALIZATION",
            "witness": {
                "target_probabilities": p5_target_probabilities,
                "available_actions": available_actions,
            },
            "actual_risk": actual_zero_one_risk,
            "classification_formula": displayed_classification_formula,
            "equality_fails": actual_zero_one_risk != displayed_classification_formula,
        }
    )

    # P5: an infinite test family can have a set-cover infimum but no minimum.
    # Test t_n covers the one required pair and costs 1/n; t_(n+1) is always
    # strictly cheaper, so no member is a minimizer.
    decreasing_cost_witness = all(1.0 / (n + 1) < 1.0 / n for n in range(1, 1000))
    cases.append(
        {
            "id": "P5_INFINITE_TEST_FAMILY_NO_MINIMUM",
            "witness": "one universe element; t_n covers it at cost 1/n for every positive integer n",
            "infimum": 0.0,
            "infimum_attained": False,
            "strict_decrease_checked_n_1_to_999": decreasing_cost_witness,
        }
    )

    # P5 stochastic prose: equal one-test marginals do not imply equal joint
    # transcript laws.
    joint_state_0 = {(0, 0): 0.5, (1, 1): 0.5}
    joint_state_1 = {(0, 1): 0.5, (1, 0): 0.5}

    def marginal(joint: dict[tuple[int, int], float], coordinate: int) -> dict[int, float]:
        result = {0: 0.0, 1: 0.0}
        for outcome, probability in joint.items():
            result[outcome[coordinate]] += probability
        return result

    same_marginals = all(marginal(joint_state_0, i) == marginal(joint_state_1, i) for i in (0, 1))
    disjoint_joint_support = set(joint_state_0).isdisjoint(joint_state_1)
    cases.append(
        {
            "id": "P5_EQUAL_MARGINALS_JOINTLY_SEPARABLE",
            "witness": {
                "state_0_joint": {str(k): v for k, v in joint_state_0.items()},
                "state_1_joint": {str(k): v for k, v in joint_state_1.items()},
            },
            "each_test_marginal_equal": same_marginals,
            "joint_support_disjoint": disjoint_joint_support,
            "two_test_bayes_error_equal_prior": 0.0,
        }
    )

    required_flags = [
        cases[0]["invalidates_unqualified_half_error"],
        cases[1]["invalidates_unconditional_omission_impossibility"],
        cases[2]["strict_sound_extension_exists"],
        cases[3]["equality_fails"],
        cases[4]["quantifiers_differ"],
        cases[5]["equality_fails"],
        cases[6]["strict_decrease_checked_n_1_to_999"],
        cases[7]["each_test_marginal_equal"] and cases[7]["joint_support_disjoint"],
    ]
    receipt = {
        "schema": "P1_P5_ADVERSARIAL_COUNTEREXAMPLES_V1",
        "authority": "LOCAL_EXACT_MATHEMATICAL_WITNESSES_ONLY",
        "external_peer_review": False,
        "empirical_claim": False,
        "all_witness_checks_pass": all(required_flags),
        "cases": cases,
    }

    output_path = Path(__file__).with_name("COUNTEREXAMPLE_RECEIPT.json")
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
