from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from itertools import combinations
import hashlib
import json
import math
import random
from typing import Iterable, Mapping, Sequence


class RecoveryCause(str, Enum):
    REPRESENTATION_LIMIT = "REPRESENTATION_LIMIT"
    MODEL_CAPACITY_LIMIT = "MODEL_CAPACITY_LIMIT"
    DATA_SCARCITY = "DATA_SCARCITY"
    PARTIAL_INFORMATION = "PARTIAL_INFORMATION"
    LEAKAGE_OR_SHORTCUT = "LEAKAGE_OR_SHORTCUT"
    MISSING_PARENT_METHOD = "MISSING_PARENT_METHOD"
    EXACT_MECHANIC_SUFFICIENT = "EXACT_MECHANIC_SUFFICIENT"
    BENCHMARK_NON_IDENTIFYING = "BENCHMARK_NON_IDENTIFYING"


class RecoveryAction(str, Enum):
    EXPOSE_RELATION_COORDINATE = "EXPOSE_RELATION_COORDINATE"
    INCREASE_INTERACTION_ORDER = "INCREASE_INTERACTION_ORDER"
    ACQUIRE_MORE_DATA = "ACQUIRE_MORE_DATA"
    ACQUIRE_MISSING_OBSERVATION = "ACQUIRE_MISSING_OBSERVATION"
    ENFORCE_INVARIANT_STATE = "ENFORCE_INVARIANT_STATE"
    ADOPT_DONOR_METHOD = "ADOPT_DONOR_METHOD"
    STOP_NEURAL_ESCALATION = "STOP_NEURAL_ESCALATION"
    RUN_DISCRIMINATING_EXPERIMENT = "RUN_DISCRIMINATING_EXPERIMENT"


FEATURES = (
    "relation_gain",
    "degree_gain",
    "sample_gain",
    "missing_info_gain",
    "invariance_gain",
    "donor_gain",
    "exact_ceiling",
    "collision_score",
    "orbit_instability",
    "train_test_gap",
)

_SIGNATURES: Mapping[RecoveryCause, tuple[float, ...]] = {
    RecoveryCause.REPRESENTATION_LIMIT: (
        0.86, 0.52, 0.20, 0.10, 0.35, 0.15, 0.10, 0.12, 0.78, 0.22
    ),
    RecoveryCause.MODEL_CAPACITY_LIMIT: (
        0.34, 0.90, 0.34, 0.10, 0.20, 0.18, 0.10, 0.12, 0.32, 0.18
    ),
    RecoveryCause.DATA_SCARCITY: (
        0.20, 0.28, 0.88, 0.10, 0.20, 0.18, 0.10, 0.10, 0.20, 0.18
    ),
    RecoveryCause.PARTIAL_INFORMATION: (
        0.18, 0.18, 0.18, 0.92, 0.18, 0.16, 0.10, 0.10, 0.18, 0.18
    ),
    RecoveryCause.LEAKAGE_OR_SHORTCUT: (
        0.34, 0.22, 0.24, 0.10, 0.88, 0.16, 0.10, 0.12, 0.76, 0.86
    ),
    RecoveryCause.MISSING_PARENT_METHOD: (
        0.22, 0.26, 0.26, 0.10, 0.22, 0.90, 0.10, 0.10, 0.24, 0.18
    ),
    RecoveryCause.EXACT_MECHANIC_SUFFICIENT: (
        0.15, 0.15, 0.15, 0.10, 0.15, 0.15, 0.96, 0.08, 0.15, 0.12
    ),
    RecoveryCause.BENCHMARK_NON_IDENTIFYING: (
        0.60, 0.60, 0.18, 0.10, 0.20, 0.16, 0.10, 0.96, 0.32, 0.18
    ),
}

_ACTION_FOR_CAUSE: Mapping[RecoveryCause, RecoveryAction] = {
    RecoveryCause.REPRESENTATION_LIMIT: RecoveryAction.EXPOSE_RELATION_COORDINATE,
    RecoveryCause.MODEL_CAPACITY_LIMIT: RecoveryAction.INCREASE_INTERACTION_ORDER,
    RecoveryCause.DATA_SCARCITY: RecoveryAction.ACQUIRE_MORE_DATA,
    RecoveryCause.PARTIAL_INFORMATION: RecoveryAction.ACQUIRE_MISSING_OBSERVATION,
    RecoveryCause.LEAKAGE_OR_SHORTCUT: RecoveryAction.ENFORCE_INVARIANT_STATE,
    RecoveryCause.MISSING_PARENT_METHOD: RecoveryAction.ADOPT_DONOR_METHOD,
    RecoveryCause.EXACT_MECHANIC_SUFFICIENT: RecoveryAction.STOP_NEURAL_ESCALATION,
    RecoveryCause.BENCHMARK_NON_IDENTIFYING: RecoveryAction.RUN_DISCRIMINATING_EXPERIMENT,
}


@dataclass(frozen=True)
class RecoveryDiagnostics:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) != len(FEATURES):
            raise ValueError("diagnostic vector length mismatch")
        if any(value < 0.0 or value > 1.0 for value in self.values):
            raise ValueError("diagnostic values must be in [0, 1]")

    def as_dict(self) -> dict[str, float]:
        return dict(zip(FEATURES, self.values, strict=True))

    def fingerprint(self) -> str:
        raw = json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class RecoveryEpisode:
    episode_id: str
    active_causes: tuple[RecoveryCause, ...]
    latent_after_discriminator: RecoveryCause | None
    seed: int
    step: int = 0
    action_history: tuple[RecoveryAction, ...] = ()

    def __post_init__(self) -> None:
        if not self.active_causes:
            raise ValueError("episode must contain at least one active cause")
        if (
            RecoveryCause.EXACT_MECHANIC_SUFFICIENT in self.active_causes
            and len(self.active_causes) != 1
        ):
            raise ValueError("exact-sufficiency control cannot be composed with repair causes")
        if (
            RecoveryCause.BENCHMARK_NON_IDENTIFYING in self.active_causes
            and self.latent_after_discriminator
            not in (
                RecoveryCause.REPRESENTATION_LIMIT,
                RecoveryCause.MODEL_CAPACITY_LIMIT,
            )
        ):
            raise ValueError(
                "non-identifying episode needs a hidden representation/capacity subtype"
            )

    def diagnostics(self) -> RecoveryDiagnostics:
        rng = random.Random(self.seed + self.step * 9_973)
        severities = {
            cause: rng.uniform(0.90, 1.06) for cause in self.active_causes
        }
        values: list[float] = []
        for index, name in enumerate(FEATURES):
            base = max(
                min(1.0, _SIGNATURES[cause][index] * severities[cause])
                for cause in self.active_causes
            )
            sigma = 0.04 if name == "collision_score" else 0.06
            value = min(1.0, max(0.0, base + rng.gauss(0.0, sigma)))
            values.append(value)
        return RecoveryDiagnostics(tuple(values))

    def candidate_payload(self) -> dict[str, object]:
        return {
            "episode_id": self.episode_id,
            "step": self.step,
            "diagnostics": self.diagnostics().as_dict(),
            "history": [item.value for item in self.action_history],
        }

    def apply(self, action: RecoveryAction) -> tuple["RecoveryEpisode", bool]:
        active = list(self.active_causes)
        if active == [RecoveryCause.EXACT_MECHANIC_SUFFICIENT]:
            return (
                replace(
                    self,
                    step=self.step + 1,
                    action_history=self.action_history + (action,),
                ),
                action is RecoveryAction.STOP_NEURAL_ESCALATION,
            )

        matched: RecoveryCause | None = None
        for cause in active:
            if _ACTION_FOR_CAUSE[cause] is action:
                matched = cause
                break
        if matched is None:
            return (
                replace(
                    self,
                    step=self.step + 1,
                    action_history=self.action_history + (action,),
                ),
                False,
            )

        active.remove(matched)
        if matched is RecoveryCause.BENCHMARK_NON_IDENTIFYING:
            assert self.latent_after_discriminator is not None
            active.append(self.latent_after_discriminator)

        if not active:
            return (
                RecoveryEpisode(
                    episode_id=self.episode_id,
                    active_causes=(RecoveryCause.EXACT_MECHANIC_SUFFICIENT,),
                    latent_after_discriminator=None,
                    seed=self.seed,
                    step=self.step + 1,
                    action_history=self.action_history + (action,),
                ),
                True,
            )

        return (
            RecoveryEpisode(
                episode_id=self.episode_id,
                active_causes=tuple(active),
                latent_after_discriminator=self.latent_after_discriminator,
                seed=self.seed,
                step=self.step + 1,
                action_history=self.action_history + (action,),
            ),
            False,
        )


def _make_episode(
    causes: Sequence[RecoveryCause],
    *,
    seed: int,
    episode_id: str,
) -> RecoveryEpisode:
    latent: RecoveryCause | None = None
    if RecoveryCause.BENCHMARK_NON_IDENTIFYING in causes:
        latent_rng = random.Random(seed ^ 0xBEEF_2026)
        latent = (
            RecoveryCause.REPRESENTATION_LIMIT
            if latent_rng.random() < 0.5
            else RecoveryCause.MODEL_CAPACITY_LIMIT
        )
    return RecoveryEpisode(
        episode_id=episode_id,
        active_causes=tuple(causes),
        latent_after_discriminator=latent,
        seed=seed,
    )


def atomic_panel(*, seed_base: int, per_cause: int) -> tuple[RecoveryEpisode, ...]:
    episodes: list[RecoveryEpisode] = []
    for cause_index, cause in enumerate(RecoveryCause):
        for item_index in range(per_cause):
            seed = seed_base + cause_index * 10_000 + item_index
            episodes.append(
                _make_episode(
                    (cause,),
                    seed=seed,
                    episode_id=f"atomic-{cause_index}-{item_index}",
                )
            )
    return tuple(episodes)


def composite_panel(
    *,
    seed_base: int,
    per_combination: int,
    sizes: Sequence[int] = (2, 3),
) -> tuple[RecoveryEpisode, ...]:
    pool = tuple(
        cause
        for cause in RecoveryCause
        if cause is not RecoveryCause.EXACT_MECHANIC_SUFFICIENT
    )
    episodes: list[RecoveryEpisode] = []
    offset = 0
    for size in sizes:
        for combo_index, combo in enumerate(combinations(pool, size)):
            for item_index in range(per_combination):
                seed = seed_base + offset + combo_index * 1_000 + item_index
                episodes.append(
                    _make_episode(
                        combo,
                        seed=seed,
                        episode_id=f"composite-{size}-{combo_index}-{item_index}",
                    )
                )
        offset += 1_000_000
    return tuple(episodes)


@dataclass(frozen=True)
class CentroidRecoveryPolicy:
    centroids: tuple[tuple[RecoveryAction, tuple[float, ...]], ...]

    @classmethod
    def fit(cls, episodes: Iterable[RecoveryEpisode]) -> "CentroidRecoveryPolicy":
        grouped: dict[RecoveryAction, list[tuple[float, ...]]] = {
            action: [] for action in RecoveryAction
        }
        for episode in episodes:
            if len(episode.active_causes) != 1:
                raise ValueError("training policy accepts atomic episodes only")
            cause = episode.active_causes[0]
            grouped[_ACTION_FOR_CAUSE[cause]].append(episode.diagnostics().values)

        centroids: list[tuple[RecoveryAction, tuple[float, ...]]] = []
        for action in RecoveryAction:
            rows = grouped[action]
            if not rows:
                raise ValueError(f"missing training rows for {action.value}")
            center = tuple(
                sum(row[index] for row in rows) / len(rows)
                for index in range(len(FEATURES))
            )
            centroids.append((action, center))
        return cls(tuple(centroids))

    def decide(self, diagnostics: RecoveryDiagnostics) -> RecoveryAction:
        def distance(center: tuple[float, ...]) -> float:
            return math.sqrt(
                sum(
                    (left - right) ** 2
                    for left, right in zip(
                        diagnostics.values, center, strict=True
                    )
                )
            )

        return min(self.centroids, key=lambda item: distance(item[1]))[0]

    def as_dict(self) -> dict[str, object]:
        return {
            "policy": "nearest-centroid",
            "feature_names": list(FEATURES),
            "centroids": {
                action.value: dict(zip(FEATURES, center, strict=True))
                for action, center in self.centroids
            },
        }


class NativeResponsibilityController:
    """Independent typed responsibility rule; it does not consume learned centroids."""

    def decide(self, diagnostics: RecoveryDiagnostics) -> RecoveryAction:
        values = diagnostics.as_dict()
        if values["exact_ceiling"] >= 0.72:
            return RecoveryAction.STOP_NEURAL_ESCALATION
        if values["collision_score"] >= 0.72:
            return RecoveryAction.RUN_DISCRIMINATING_EXPERIMENT
        scores = {
            RecoveryAction.EXPOSE_RELATION_COORDINATE: values["relation_gain"],
            RecoveryAction.INCREASE_INTERACTION_ORDER: values["degree_gain"],
            RecoveryAction.ACQUIRE_MORE_DATA: values["sample_gain"],
            RecoveryAction.ACQUIRE_MISSING_OBSERVATION: values["missing_info_gain"],
            RecoveryAction.ENFORCE_INVARIANT_STATE: values["invariance_gain"],
            RecoveryAction.ADOPT_DONOR_METHOD: values["donor_gain"],
        }
        return max(scores, key=scores.get)


@dataclass(frozen=True)
class RecoveryTrace:
    episode_id: str
    success: bool
    actions: tuple[RecoveryAction, ...]
    steps: int
    final_active_causes: tuple[RecoveryCause, ...]
    first_action: RecoveryAction

    def as_dict(self) -> dict[str, object]:
        return {
            "episode_id": self.episode_id,
            "success": self.success,
            "actions": [action.value for action in self.actions],
            "steps": self.steps,
            "final_active_causes": [
                cause.value for cause in self.final_active_causes
            ],
            "first_action": self.first_action.value,
        }


def run_recovery(
    episode: RecoveryEpisode,
    *,
    policy,
    max_steps: int = 5,
) -> RecoveryTrace:
    current = episode
    actions: list[RecoveryAction] = []
    success = False
    for _ in range(max_steps):
        diagnostics = current.diagnostics()
        action = policy.decide(diagnostics)
        actions.append(action)
        next_episode, terminal = current.apply(action)
        if terminal:
            success = True
            current = next_episode
            break
        if next_episode.active_causes == current.active_causes:
            current = next_episode
            break
        current = next_episode
    return RecoveryTrace(
        episode_id=episode.episode_id,
        success=success,
        actions=tuple(actions),
        steps=len(actions),
        final_active_causes=current.active_causes,
        first_action=actions[0],
    )


class _RandomPolicy:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def decide(self, diagnostics: RecoveryDiagnostics) -> RecoveryAction:
        del diagnostics
        return self._rng.choice(tuple(RecoveryAction))


def evaluate_dual_recovery(
    *,
    training_seed: int = 10_000,
    protected_seed: int = 700_000,
) -> dict[str, object]:
    training = atomic_panel(seed_base=training_seed, per_cause=256)
    learned = CentroidRecoveryPolicy.fit(training)
    native = NativeResponsibilityController()

    atomic = atomic_panel(seed_base=protected_seed, per_cause=64)
    composite = composite_panel(
        seed_base=protected_seed + 1_000_000,
        per_combination=16,
        sizes=(2, 3),
    )

    learned_atomic = [
        run_recovery(item, policy=learned, max_steps=3) for item in atomic
    ]
    native_atomic = [
        run_recovery(item, policy=native, max_steps=3) for item in atomic
    ]
    learned_composite = [
        run_recovery(item, policy=learned, max_steps=5) for item in composite
    ]
    native_composite = [
        run_recovery(item, policy=native, max_steps=5) for item in composite
    ]

    def rate(rows: Sequence[RecoveryTrace]) -> float:
        return sum(item.success for item in rows) / len(rows)

    atomic_first_action_agreement = (
        sum(
            left.first_action is right.first_action
            for left, right in zip(
                learned_atomic, native_atomic, strict=True
            )
        )
        / len(atomic)
    )
    strict_composite_first_action_agreement = (
        sum(
            left.first_action is right.first_action
            for left, right in zip(
                learned_composite, native_composite, strict=True
            )
        )
        / len(composite)
    )

    def valid_first_action(
        episode: RecoveryEpisode, trace: RecoveryTrace
    ) -> bool:
        return any(
            _ACTION_FOR_CAUSE[cause] is trace.first_action
            for cause in episode.active_causes
        )

    composite_both_first_actions_valid = (
        sum(
            valid_first_action(episode, left)
            and valid_first_action(episode, right)
            for episode, left, right in zip(
                composite,
                learned_composite,
                native_composite,
                strict=True,
            )
        )
        / len(composite)
    )
    dual_terminal_agreement = (
        sum(
            left.success == right.success
            for left, right in zip(
                learned_composite, native_composite, strict=True
            )
        )
        / len(composite)
    )

    exact_rows = [
        item
        for item in atomic
        if item.active_causes
        == (RecoveryCause.EXACT_MECHANIC_SUFFICIENT,)
    ]
    exact_learned = [
        run_recovery(item, policy=learned, max_steps=1)
        for item in exact_rows
    ]
    exact_native = [
        run_recovery(item, policy=native, max_steps=1)
        for item in exact_rows
    ]
    no_overescalation = min(rate(exact_learned), rate(exact_native))

    learned_single_shot = [
        run_recovery(item, policy=learned, max_steps=1)
        for item in composite
    ]
    random_policy = _RandomPolicy(seed=protected_seed ^ 0xACE5)
    random_composite = [
        run_recovery(item, policy=random_policy, max_steps=5)
        for item in composite
    ]

    metrics = {
        "learned_atomic_recovery_rate": rate(learned_atomic),
        "native_atomic_recovery_rate": rate(native_atomic),
        "atomic_first_action_agreement": atomic_first_action_agreement,
        "learned_unseen_composite_recovery_rate": rate(learned_composite),
        "native_unseen_composite_recovery_rate": rate(native_composite),
        "composite_both_first_actions_valid_rate": (
            composite_both_first_actions_valid
        ),
        "dual_terminal_agreement": dual_terminal_agreement,
        "strict_composite_first_action_agreement_descriptive": (
            strict_composite_first_action_agreement
        ),
        "exact_control_no_overescalation_rate": no_overescalation,
        "learned_single_shot_composite_recovery_rate": rate(
            learned_single_shot
        ),
        "random_recursive_composite_recovery_rate": rate(
            random_composite
        ),
    }
    gates = {
        "learned_atomic_ge_0_95": (
            metrics["learned_atomic_recovery_rate"] >= 0.95
        ),
        "native_atomic_ge_0_95": (
            metrics["native_atomic_recovery_rate"] >= 0.95
        ),
        "atomic_agreement_ge_0_95": (
            metrics["atomic_first_action_agreement"] >= 0.95
        ),
        "learned_composite_ge_0_90": (
            metrics["learned_unseen_composite_recovery_rate"] >= 0.90
        ),
        "native_composite_ge_0_95": (
            metrics["native_unseen_composite_recovery_rate"] >= 0.95
        ),
        "composite_first_actions_valid_ge_0_95": (
            metrics["composite_both_first_actions_valid_rate"] >= 0.95
        ),
        "dual_terminal_agreement_ge_0_95": (
            metrics["dual_terminal_agreement"] >= 0.95
        ),
        "no_overescalation_eq_1": (
            metrics["exact_control_no_overescalation_rate"] == 1.0
        ),
        "recursion_strictly_beats_single_shot": (
            metrics["learned_unseen_composite_recovery_rate"]
            > metrics["learned_single_shot_composite_recovery_rate"]
        ),
        "learned_beats_random_recursive": (
            metrics["learned_unseen_composite_recovery_rate"]
            > metrics["random_recursive_composite_recovery_rate"]
        ),
    }
    terminal = (
        "ORION_NEGATIVE_RECOVERY_EXACT_GENERATED_WORLDS_SUPPORTED"
        if all(gates.values())
        else "ORION_NEGATIVE_RECOVERY_EXACT_GENERATED_WORLDS_NOT_SUPPORTED"
    )
    return {
        "schema": "ORION.NegativeRecoveryExactGeneratedWorlds.v1",
        "training": {
            "atomic_episode_count": len(training),
            "cause_count": len(RecoveryCause),
            "policy": learned.as_dict(),
        },
        "protected": {
            "atomic_episode_count": len(atomic),
            "composite_episode_count": len(composite),
            "composite_sizes": [2, 3],
            "candidate_payload_excludes_hidden_cause": True,
        },
        "metrics": metrics,
        "gates": gates,
        "terminal": terminal,
        "claim_boundary": (
            "Bounded exact generated recovery worlds only. The learned lane is "
            "trained on atomic diagnostic-to-action episodes and evaluated on "
            "unseen composite failure combinations. This is not yet evidence of "
            "real-world or autonomous scientific recovery."
        ),
    }
