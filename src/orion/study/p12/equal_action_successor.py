"""Prospectively frozen P12B equal-action signal-complementarity study."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

MASTER_SEED = 2026082312
BOOTSTRAP_SEED = 2026083303
SENSITIVITY_SEED = 2026083304
BOOTSTRAP_DRAWS = 20_000
N_FAMILIES = 32
EPISODES_PER_FAMILY = 1_024
SIGMAS = (0.2, 0.4, 0.6, 0.8)
BUDGET = 2

REGIMES = ("EASY", "ACCESS", "REASON", "BOTH")
ACTIONS: tuple[tuple[int, int], ...] = ((0, 0), (2, 0), (0, 2), (1, 1))
REQUIRED_ACTION: Mapping[str, tuple[int, int]] = dict(zip(REGIMES, ACTIONS))

SUPPORTED = "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_SUPPORTED"
NOT_SUPPORTED = "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_GATE_NOT_MET"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-12-adaptive-state-reasoning"
PROTOCOL = PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_PROTOCOL_V1.md"
AMENDMENT = PAPER / "P12B_PROTOCOL_AMENDMENT_V1_1.md"
PREFLIGHT = PAPER / "P12B_PREFLIGHT_ATTAINABILITY_V1_1.json"


def canonical_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class TwoSignalObservation:
    state_signal: float
    reason_signal: float


@dataclass(frozen=True)
class OneSignalObservation:
    signal: float


def _nearest_two(observation: TwoSignalObservation) -> tuple[int, int]:
    return min(
        (
            (observation.state_signal - action[0]) ** 2
            + (observation.reason_signal - action[1]) ** 2,
            index,
            action,
        )
        for index, action in enumerate(ACTIONS)
    )[2]


def _nearest_one(observation: OneSignalObservation, *, axis: int) -> tuple[int, int]:
    return min(
        ((observation.signal - action[axis]) ** 2, index, action)
        for index, action in enumerate(ACTIONS)
    )[2]


def _family_rng(family: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([MASTER_SEED, family]))


def build_core() -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    for family in range(N_FAMILIES):
        sigma = SIGMAS[family % len(SIGMAS)]
        rng = _family_rng(family)
        labels = np.repeat(np.arange(len(REGIMES)), EPISODES_PER_FAMILY // len(REGIMES))
        rng.shuffle(labels)
        counts = {regime: int(np.sum(labels == index)) for index, regime in enumerate(REGIMES)}
        correct = {"TWO_SIGNAL": 0, "STATE_SIGNAL": 0, "REASON_SIGNAL": 0}
        for index in labels:
            target = REQUIRED_ACTION[REGIMES[int(index)]]
            state_signal = float(target[0] + rng.normal(0.0, sigma))
            reason_signal = float(target[1] + rng.normal(0.0, sigma))
            decisions = {
                "TWO_SIGNAL": _nearest_two(
                    TwoSignalObservation(state_signal, reason_signal)
                ),
                "STATE_SIGNAL": _nearest_one(
                    OneSignalObservation(state_signal), axis=0
                ),
                "REASON_SIGNAL": _nearest_one(
                    OneSignalObservation(reason_signal), axis=1
                ),
            }
            for arm_id, decision in decisions.items():
                correct[arm_id] += int(decision == target)
        rates = {
            arm_id: value / EPISODES_PER_FAMILY for arm_id, value in correct.items()
        }
        stronger_one = max(rates["STATE_SIGNAL"], rates["REASON_SIGNAL"])
        families.append(
            {
                "family_rng_block": family,
                "sigma": sigma,
                "regime_counts": counts,
                "correct_counts": correct,
                "exact_allocation_rates": rates,
                "delta_vs_stronger_one_signal": rates["TWO_SIGNAL"] - stronger_one,
            }
        )

    action_list = [list(action) for action in ACTIONS]
    return {
        "schema": "ORION.P12B.EqualActionSignalComplementarity.Core.v1",
        "paper_id": "P12",
        "claim_id": "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY",
        "protocol": str(PROTOCOL.relative_to(REPO_ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "protocol_amendment": str(AMENDMENT.relative_to(REPO_ROOT)),
        "protocol_amendment_sha256": file_sha256(AMENDMENT),
        "preflight": str(PREFLIGHT.relative_to(REPO_ROOT)),
        "preflight_sha256": file_sha256(PREFLIGHT),
        "master_seed": MASTER_SEED,
        "independent_unit": "family_rng_block",
        "n_independent_units": N_FAMILIES,
        "technical_episodes_per_unit": EPISODES_PER_FAMILY,
        "fixed_sigma_strata": list(SIGMAS),
        "families_per_sigma": N_FAMILIES // len(SIGMAS),
        "subject_identity": {
            "budget": BUDGET,
            "exact_action_set": action_list,
            "arms": {
                "TWO_SIGNAL": {
                    "action_set": action_list,
                    "observation_fields": ["state_signal", "reason_signal"],
                    "policy": "nearest_squared_euclidean_v1",
                },
                "STATE_SIGNAL": {
                    "action_set": action_list,
                    "observation_fields": ["state_signal"],
                    "policy": "nearest_visible_coordinate_table_tie_v1",
                },
                "REASON_SIGNAL": {
                    "action_set": action_list,
                    "observation_fields": ["reason_signal"],
                    "policy": "nearest_visible_coordinate_table_tie_v1",
                },
            },
        },
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
        },
        "families": families,
    }


def _family_deltas(core: Mapping[str, Any]) -> np.ndarray:
    deltas: list[float] = []
    for family in core["families"]:
        counts = family["correct_counts"]
        if set(counts) != {"TWO_SIGNAL", "STATE_SIGNAL", "REASON_SIGNAL"}:
            raise ValueError("P12B family arm register changed")
        if any(not isinstance(value, int) or not 0 <= value <= EPISODES_PER_FAMILY for value in counts.values()):
            raise ValueError("P12B correct count outside the frozen denominator")
        rates = {key: value / EPISODES_PER_FAMILY for key, value in counts.items()}
        deltas.append(rates["TWO_SIGNAL"] - max(rates["STATE_SIGNAL"], rates["REASON_SIGNAL"]))
    return np.asarray(deltas, dtype=float)


def _stratified_bootstrap(deltas: np.ndarray, sigmas: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = np.empty(BOOTSTRAP_DRAWS)
    indices = [np.flatnonzero(sigmas == sigma) for sigma in SIGMAS]
    for index in range(BOOTSTRAP_DRAWS):
        sample = np.concatenate(
            [group[rng.integers(0, len(group), size=len(group))] for group in indices]
        )
        draws[index] = float(np.mean(deltas[sample]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _unstratified_bootstrap(deltas: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(SENSITIVITY_SEED)
    draws = np.empty(BOOTSTRAP_DRAWS)
    for index in range(BOOTSTRAP_DRAWS):
        sample = rng.integers(0, len(deltas), size=len(deltas))
        draws[index] = float(np.mean(deltas[sample]))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def adjudicate(core: Mapping[str, Any], *, byte_identical_replay: bool) -> dict[str, Any]:
    candidate = deepcopy(core)
    families = candidate.get("families", [])
    structure_ok = len(families) == N_FAMILIES
    try:
        deltas = _family_deltas(candidate) if structure_ok else np.asarray([], dtype=float)
    except (KeyError, TypeError, ValueError):
        structure_ok = False
        deltas = np.asarray([], dtype=float)

    sigmas = np.asarray([family.get("sigma") for family in families], dtype=float) if structure_ok else np.asarray([], dtype=float)
    balanced = structure_ok and all(
        family.get("regime_counts")
        == {regime: EPISODES_PER_FAMILY // len(REGIMES) for regime in REGIMES}
        for family in families
    )
    subject = candidate.get("subject_identity", {})
    arms = subject.get("arms", {})
    expected_actions = [list(action) for action in ACTIONS]
    equal_actions = set(arms) == {"TWO_SIGNAL", "STATE_SIGNAL", "REASON_SIGNAL"} and all(
        arm.get("action_set") == expected_actions for arm in arms.values()
    )
    budget_respected = equal_actions and all(sum(action) <= BUDGET for action in ACTIONS)
    hidden_signals = equal_actions and arms["STATE_SIGNAL"].get("observation_fields") == ["state_signal"] and arms["REASON_SIGNAL"].get("observation_fields") == ["reason_signal"]

    if structure_ok:
        stratified_ci = _stratified_bootstrap(deltas, sigmas)
        sensitivity_ci = _unstratified_bootstrap(deltas)
        mean_delta = float(np.mean(deltas))
        by_sigma = {
            str(sigma): float(np.mean(deltas[sigmas == sigma])) for sigma in SIGMAS
        }
        min_family = float(np.min(deltas))
    else:
        stratified_ci = (float("-inf"), float("-inf"))
        sensitivity_ci = (float("-inf"), float("-inf"))
        mean_delta = float("-inf")
        by_sigma = {str(sigma): float("-inf") for sigma in SIGMAS}
        min_family = float("-inf")

    gates = {
        "identical_four_action_sets": equal_actions,
        "budget_two_respected": budget_respected,
        "balanced_regimes_in_all_families": balanced,
        "withheld_signals_absent_from_typed_observations": hidden_signals,
        "mean_delta_ge_0_15": mean_delta >= 0.15,
        "stratified_family_bootstrap_lower_ge_0_12": stratified_ci[0] >= 0.12,
        "every_sigma_stratum_mean_ge_0_12": all(value >= 0.12 for value in by_sigma.values()),
        "every_family_delta_gt_0": min_family > 0.0,
        "byte_identical_replay": byte_identical_replay,
    }
    terminal = SUPPORTED if all(gates.values()) else NOT_SUPPORTED
    return {
        "schema": "ORION.P12B.EqualActionSignalComplementarity.Result.v1",
        "core": candidate,
        "summary": {
            "mean_delta_vs_stronger_one_signal": mean_delta,
            "stratified_family_bootstrap_95ci": list(stratified_ci),
            "unstratified_family_bootstrap_95ci_sensitivity": list(sensitivity_ci),
            "mean_delta_by_sigma": by_sigma,
            "minimum_family_delta": min_family,
            "n_independent_family_rng_blocks": len(families),
        },
        "gates": gates,
        "terminal": terminal,
    }


__all__ = [
    "ACTIONS",
    "EPISODES_PER_FAMILY",
    "N_FAMILIES",
    "NOT_SUPPORTED",
    "OneSignalObservation",
    "SIGMAS",
    "SUPPORTED",
    "TwoSignalObservation",
    "adjudicate",
    "build_core",
    "canonical_text",
]
