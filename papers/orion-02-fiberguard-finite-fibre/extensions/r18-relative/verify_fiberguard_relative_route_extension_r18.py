#!/usr/bin/env python3
"""Finite corroboration for the FiberGuard R18 relative-route theory."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

SCHEMA = "ORION.FiberGuard.RelativeRouteExtension.R18.v1"
SOURCE_BASE_COMMIT = "f34b61e0051289588eaf144a580dca7bc9b7e707"
TERMINAL = "FIBERGUARD_RELATIVE_ROUTE_EXTENSION_R18_PASS"
SEED = 20260827


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def check_relative_baseline_cancellation() -> int:
    checks = 0
    for baseline in range(-5, 6):
        for learned_absolute in range(11):
            for fallback_absolute in range(11):
                learned_excess = learned_absolute - baseline
                fallback_excess = fallback_absolute - baseline
                assert fallback_excess - learned_excess == fallback_absolute - learned_absolute
                checks += 1
    assert checks == 1331
    return checks


def check_paired_action_intervals() -> int:
    checks = 0
    for learned in range(11):
        for fallback in range(11):
            for learned_lower_slack in range(3):
                for learned_upper_slack in range(3):
                    for fallback_lower_slack in range(3):
                        for fallback_upper_slack in range(3):
                            lower_l = learned - learned_lower_slack
                            upper_l = learned + learned_upper_slack
                            lower_f = fallback - fallback_lower_slack
                            upper_f = fallback + fallback_upper_slack
                            if upper_f <= lower_l:
                                assert fallback <= learned
                            if upper_l <= lower_f:
                                assert learned <= fallback
                            checks += 1
    assert checks == 9801
    return checks


def check_direct_relative_intervals() -> int:
    checks = 0
    for delta in range(-10, 11):
        for radius in range(6):
            for estimate in range(delta - radius, delta + radius + 1):
                lower = estimate - radius
                upper = estimate + radius
                assert lower <= delta <= upper
                if upper <= 0:
                    assert delta <= 0
                if lower >= 0:
                    assert delta >= 0
                checks += 1
    assert checks == 756
    return checks


def check_open_world_relative_sign_attack() -> int:
    checks = 0
    frozen_training_bytes = ("representation", "learned", "fallback", "certificate")
    for magnitude in range(1, 101):
        positive_world = {
            "training": frozen_training_bytes,
            "new_representation": "same-signature",
            "learned": 0,
            "fallback": magnitude,
        }
        negative_world = {
            "training": frozen_training_bytes,
            "new_representation": "same-signature",
            "learned": magnitude,
            "fallback": 0,
        }
        assert positive_world["training"] == negative_world["training"]
        assert positive_world["new_representation"] == negative_world["new_representation"]
        assert positive_world["fallback"] - positive_world["learned"] == magnitude
        assert negative_world["fallback"] - negative_world["learned"] == -magnitude
        checks += 1
    assert checks == 100
    return checks


def anchor_interval(
    values: tuple[int, ...], anchors: tuple[int, ...], state: int, constant: int
) -> tuple[int, int]:
    lower = max(values[anchor] - constant * abs(state - anchor) for anchor in anchors)
    upper = min(values[anchor] + constant * abs(state - anchor) for anchor in anchors)
    return lower, upper


def check_lipschitz_relative_extension() -> dict[str, int]:
    bound_checks = 0
    monotonicity_checks = 0
    hostile_underestimates = 0
    state_count = 12
    for slope in range(-4, 5):
        for intercept in range(-3, 4):
            values = tuple(slope * state + intercept for state in range(state_count))
            constant = abs(slope)
            previous = None
            for anchor_count in range(1, state_count + 1):
                anchors = tuple(range(anchor_count))
                current = []
                for state in range(state_count):
                    lower, upper = anchor_interval(values, anchors, state, constant)
                    assert lower <= values[state] <= upper
                    current.append((lower, upper))
                    bound_checks += 1
                if previous is not None:
                    for old, new in zip(previous, current):
                        assert old[0] <= new[0]
                        assert new[1] <= old[1]
                        monotonicity_checks += 1
                previous = current
            if slope != 0:
                underestimated = abs(slope) - 1
                lower, upper = anchor_interval(values, (0,), state_count - 1, underestimated)
                assert not (lower <= values[-1] <= upper)
                hostile_underestimates += 1
    assert bound_checks == 9072
    assert monotonicity_checks == 8316
    assert hostile_underestimates == 56
    return {
        "bound_checks": bound_checks,
        "hostile_underestimated_constant_failures": hostile_underestimates,
        "training_anchor_monotonicity_checks": monotonicity_checks,
    }


def check_finite_route_measurability() -> int:
    checks = 0
    for state_count in range(1, 6):
        for label_mask in range(1 << state_count):
            labels = tuple((label_mask >> state) & 1 for state in range(state_count))
            for gate_mask in range(1 << state_count):
                gate = tuple((gate_mask >> state) & 1 for state in range(state_count))
                by_label: dict[int, int] = {}
                constant_on_fibres = True
                for label, decision in zip(labels, gate):
                    if label in by_label and by_label[label] != decision:
                        constant_on_fibres = False
                    by_label[label] = decision
                implementable = any(
                    all(((route_map >> label) & 1) == decision for label, decision in zip(labels, gate))
                    for route_map in range(4)
                )
                assert implementable == constant_on_fibres
                checks += 1
    assert checks == 1364
    return checks


def check_acquisition_timing() -> dict[str, int]:
    rng = random.Random(SEED)
    systems = 2000
    for _ in range(systems):
        state_count = rng.randint(1, 9)
        learned = [rng.randint(0, 50) for _ in range(state_count)]
        fallback = [rng.randint(0, 50) for _ in range(state_count)]
        acquisition = [rng.randint(0, 20) for _ in range(state_count)]
        gate = [rng.randint(0, 1) for _ in range(state_count)]
        post = [
            acquisition[index]
            + gate[index] * learned[index]
            + (1 - gate[index]) * fallback[index]
            for index in range(state_count)
        ]
        pre = [
            gate[index] * (acquisition[index] + learned[index])
            + (1 - gate[index]) * fallback[index]
            for index in range(state_count)
        ]
        for index in range(state_count):
            assert post[index] - pre[index] == (1 - gate[index]) * acquisition[index]

    unbounded_gap_rows = 0
    for magnitude in range(1, 21):
        post = magnitude + 0
        pre = 0
        assert post - pre == magnitude
        unbounded_gap_rows += 1
    return {
        "pre_post_identity_systems": systems,
        "unbounded_gap_rows": unbounded_gap_rows,
    }


def check_drift_transfer() -> dict[str, int | bool]:
    checks = 0
    for source_delta in range(-10, 11):
        for signed_drift in range(-3, 4):
            tau = abs(signed_drift)
            target_delta = source_delta + signed_drift
            for lower_slack in range(3):
                for upper_slack in range(3):
                    source_lower = source_delta - lower_slack
                    source_upper = source_delta + upper_slack
                    target_lower = source_lower - tau
                    target_upper = source_upper + tau
                    assert target_lower <= target_delta <= target_upper
                    if target_upper <= 0:
                        assert target_delta <= 0
                    if target_lower >= 0:
                        assert target_delta >= 0
                    checks += 1
    assert checks == 1323

    source_lower = source_upper = -1
    tau = 2
    target_delta = 1
    assert source_lower <= -1 <= source_upper
    assert source_lower - tau <= target_delta <= source_upper + tau
    assert source_upper + tau > 0
    return {
        "drift_interval_checks": checks,
        "hostile_margin_sign_flip_preserved": True,
    }


def build_result() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "terminal": TERMINAL,
        "relative_baseline_cancellation": {
            "checks": check_relative_baseline_cancellation(),
        },
        "paired_action_intervals": {
            "cells": check_paired_action_intervals(),
        },
        "direct_relative_intervals": {
            "cells": check_direct_relative_intervals(),
        },
        "open_world_relative_sign_attack": {
            "paired_extensions": check_open_world_relative_sign_attack(),
            "training_bytes_changed": 0,
        },
        "lipschitz_relative_extension": check_lipschitz_relative_extension(),
        "finite_route_measurability": {
            "label_gate_pairs": check_finite_route_measurability(),
        },
        "timing": check_acquisition_timing(),
        "transfer": check_drift_transfer(),
        "controls": {
            "common_statewise_oracle_cancels_exactly": True,
            "direct_relative_interval_requires_sign_separation": True,
            "same_signature_training_bytes_do_not_fix_unseen_route_sign": True,
            "valid_lipschitz_relative_interval_contains_every_state": True,
            "adding_valid_anchors_only_tightens_intervals": True,
            "underestimated_lipschitz_constant_fails_hostile_control": True,
            "pre_post_acquisition_difference_is_rejected_path_cost": True,
            "pre_acquisition_route_iff_constant_on_free_information_fibres": True,
            "acquisition_timing_gap_is_unbounded": True,
            "drift_transfer_requires_sign_margin": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "paired_ASlib_experiment_executed": False,
            "pre_acquisition_route_experiment_executed": False,
            "structural_metric_validated_on_ASlib": False,
            "non_SAT_transfer_executed": False,
            "external_independence": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = canonical_json(build_result()) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
