"""Runner for the frozen successor protocol P9.D1T4S.INVARIANT_PROFILE_ROBUSTNESS.

Executes exactly what ``P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_FREEZE_2026-08-24``
registers, against the frozen T4 battery rebuilt verbatim:

- the successor arm on all four frozen dataset variants, through the frozen
  ``run_arm`` public extension point (frozen grid, frozen selection, v1.2
  adapter);
- the frozen ``invariance_component`` verbatim for FP-2 and FP-3;
- the companion raw-token guards (denominator = protected cases whose raw
  serialized token multiset changed), through the frozen
  ``GuardExercise``/``assess_guard`` machinery at threshold 0.0;
- the stability battery: the full frozen selection loop re-run under solver
  families and column-order renamings;
- the frozen endpoints and terminal rules.

The frozen attack module is never modified; its twin digest is verified
before anything runs.  Run from the repository root::

    PYTHONPATH=src python3 -m orion.study.p9.invariant_profile_battery

Prints one JSON object.  Exit 0 = revived stable; 3 = invariant but level
not recovered; 4 = canonicalization defect; 5 = precondition failure.
"""

from __future__ import annotations

import json
import platform
import sys
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from orion.programme.comparator_response import score_comparator
from orion.programme.guard_exercise import GuardExercise, assess_guard
from orion.programme.records import Outcome
from orion.transfer.v2.canonical import content_digest

from . import d1_experiment as _experiment
from . import hostile_representation_attacks as _attacks
from .invariant_profile_representation import (
    ARM,
    REFINEMENT_ROUNDS,
    build_colouring,
    features_with_colouring,
)

FREEZE_DOCUMENT = (
    "papers/paper-09-structured-epistemic-learning/protocol/"
    "P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_FREEZE_2026-08-24"
)
EXPECTED_RESULT_ARTIFACT = (
    "papers/paper-09-structured-epistemic-learning/evidence/"
    "P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_RESULT_2026-08-24.json"
)

RESPONSE_DEFINITION = (
    "isomorphism-invariant profile indicators over the typed serialized token "
    "multiset plus sequence length; token value spelling is discarded by construction"
)

PERFORMANCE_FLOOR = 0.75 - 1.0 / 128.0

#: Mirrors the freeze JSON's ``parameters`` block; digest ties the runner to
#: the freeze.  Nothing here may drift without a new dated freeze.
FROZEN_PARAMETERS: dict[str, Any] = {
    "arm_id": ARM,
    "refinement_rounds": REFINEMENT_ROUNDS,
    "corpus": "train-union-dev serialized bags of the variant being run",
    "model_grid": "frozen d1_experiment.model_specs(); selection by (-dev_accuracy, complexity_rank, config_id)",
    "dataset_variants": ["BASE", "EQUAL_LENGTH", "SEMANTIC_ORBIT", "ORDER_PERMUTATION"],
    "companion_guard_max_violation_rate": 0.0,
    "companion_guard_required_semantic_orbit_denominator": 128,
    "stability_solver_families": ["lbfgs", "newton-cg", "sag"],
    "stability_column_orders": ["identity", "reversed", "seeded_shuffle_rng_20260824"],
    "performance_floor": PERFORMANCE_FLOOR,
    "performance_requires_non_constant": True,
    "terminals": {
        "revived": "P9_T4_SUCCESSOR_REVIVED_STABLE",
        "level_not_recovered": "P9_T4_SUCCESSOR_INVARIANT_BUT_LEVEL_NOT_RECOVERED",
        "defect": "P9_T4_SUCCESSOR_CANONICALIZATION_DEFECT",
    },
}

TERMINAL_REVIVED = "P9_T4_SUCCESSOR_REVIVED_STABLE"
TERMINAL_LEVEL_NOT_RECOVERED = "P9_T4_SUCCESSOR_INVARIANT_BUT_LEVEL_NOT_RECOVERED"
TERMINAL_DEFECT = "P9_T4_SUCCESSOR_CANONICALIZATION_DEFECT"


def frozen_digest() -> str:
    payload = json.dumps(FROZEN_PARAMETERS, sort_keys=True, separators=(",", ":"))
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def _bag_dicts(dataset: Any) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    fn = _attacks.FEATURE_FUNCTIONS[_attacks.ARM_SERIALIZED]
    return (
        [fn(row) for row in dataset.train],
        [fn(row) for row in dataset.dev],
        [fn(row) for row in dataset.test],
    )


def _profile_dicts(
    bags: Sequence[Mapping[str, object]], colouring: Mapping[str, str]
) -> list[dict[str, object]]:
    return [features_with_colouring(row, colouring) for row in bags]


def _raw_multisets(rows: Sequence[Any]) -> list[tuple[str, ...]]:
    """Raw serialized token multiset per instance, multiplicity preserved."""

    return [tuple(sorted(_attacks.serialized_tokens(row))) for row in rows]


def _probe_run(
    *,
    train_rows: Sequence[Mapping[str, object]],
    dev_rows: Sequence[Mapping[str, object]],
    test_rows: Sequence[Mapping[str, object]],
    train_labels: Sequence[str],
    dev_labels: Sequence[str],
    logistic_solver: str | None = None,
    rename: Mapping[str, str] | None = None,
) -> tuple[str, tuple[str, ...]]:
    """The frozen selection loop with an injectable estimator path or renaming.

    Mirrors ``run_arm`` exactly -- same grid, same dev scoring, same sort key,
    same refit of the selected spec -- with the two probe dimensions the
    stability battery needs.  The identity probe (no solver override, no
    rename) must reproduce ``run_arm`` bitwise; the battery checks that.
    """

    def apply_rename(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
        if rename is None:
            return [dict(row) for row in rows]
        return [{rename.get(key, key): value for key, value in row.items()} for row in rows]

    renamed_train = apply_rename(train_rows)
    renamed_dev = apply_rename(dev_rows)
    renamed_test = apply_rename(test_rows)

    def make(spec: Any) -> Any:
        if logistic_solver is None or spec.family != "logistic":
            return _experiment._estimator(spec)
        params = spec.as_dict()
        model = LogisticRegression(
            C=float(params["C"]),
            max_iter=2000,
            random_state=2711,
            solver=logistic_solver,
        )
        return Pipeline([("vectorizer", DictVectorizer(sparse=True)), ("model", model)])

    scored: list[tuple[float, int, str, Any]] = []
    for spec in _experiment.model_specs():
        model = make(spec)
        model.fit(renamed_train, train_labels)
        dev_predictions = [str(value) for value in model.predict(renamed_dev)]
        accuracy = sum(
            1
            for gold, prediction in zip(dev_labels, dev_predictions, strict=True)
            if gold == prediction
        ) / len(dev_labels)
        scored.append((-accuracy, spec.complexity_rank, spec.config_id, spec))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    _negative_accuracy, _rank, config_id, selected = scored[0]
    model = make(selected)
    model.fit(renamed_train, train_labels)
    return config_id, tuple(str(value) for value in model.predict(renamed_test))


def _column_order_rename(
    train_rows: Sequence[Mapping[str, object]], order: Sequence[str]
) -> dict[str, str]:
    rank = {name: position for position, name in enumerate(order)}
    return {name: f"k{rank[name]:04d}" for name in rank}


def run_battery(repo_root: Path) -> dict[str, Any]:
    # PC-2: the frozen attack module must verify against its freeze twin.
    _attacks.verify_against_twin(repo_root)

    datasets = _attacks.build_datasets()
    base_ds = datasets[_attacks.DATASET_BASE]
    dataset_fidelity = {
        "base_manifest_matches_shipped": base_ds.manifest_digest == _attacks.SHIPPED_DATASET_MANIFEST_DIGEST,
        "manifest_digest": base_ds.manifest_digest,
    }

    bags = {variant: _bag_dicts(dataset) for variant, dataset in datasets.items()}
    colourings = {
        variant: build_colouring(bags[variant][0], bags[variant][1]) for variant in bags
    }
    profile_features = {
        variant: tuple(
            _profile_dicts(bags[variant][split], colourings[variant])
            for split in range(3)
        )
        for variant in bags
    }

    def feature_fn_for_variant(variant: str) -> Callable[[Any], dict[str, object]]:
        colouring = colourings[variant]

        def features(instance: Any) -> dict[str, object]:
            row = _attacks.FEATURE_FUNCTIONS[_attacks.ARM_SERIALIZED](instance)
            return features_with_colouring(row, colouring)

        return features

    runs = {
        variant: _attacks.run_arm(
            datasets[variant], variant, ARM, feature_fn_for_variant(variant)
        )
        for variant in datasets
    }

    arms_table = {}
    for variant, run in runs.items():
        response = score_comparator(
            ARM,
            gold=run.gold,
            predicted=run.predictions,
            response_definition=RESPONSE_DEFINITION,
        )
        arms_table[variant] = {
            "config_id": run.config_id,
            "dev_accuracy": run.dev_accuracy,
            "accuracy": run.accuracy,
            "gold": list(run.gold),
            "predictions": list(run.predictions),
            **response.as_json(),
        }

    # -- frozen battery components, verbatim --------------------------------
    frozen_components = [
        _attacks.invariance_component(
            component_id=f"FP-2_SEMANTIC_ORBIT_INVARIANCE::{ARM}",
            hypothesis="H_FMT",
            transform="symbol-remint semantic orbit",
            base=runs[_attacks.DATASET_BASE],
            transformed=runs[_attacks.DATASET_ORBIT],
        ),
        _attacks.invariance_component(
            component_id=f"FP-3_ORDER_REMINT_INVARIANCE::{ARM}",
            hypothesis="H_FMT",
            transform="sequence-order remint",
            base=runs[_attacks.DATASET_BASE],
            transformed=runs[_attacks.DATASET_ORDER],
        ),
    ]

    # -- companion raw-token guards ------------------------------------------
    raw_test = {variant: _raw_multisets(datasets[variant].test) for variant in datasets}
    raw_train_changed = {
        variant: _raw_multisets(datasets[variant].train)
        != _raw_multisets(datasets[_attacks.DATASET_BASE].train)
        for variant in datasets
    }
    companion_guards = []
    for variant in (
        _attacks.DATASET_ORBIT,
        _attacks.DATASET_ORDER,
        _attacks.DATASET_EQUAL_LENGTH,
    ):
        opportunities = sum(
            1
            for before, after in zip(
                raw_test[_attacks.DATASET_BASE], raw_test[variant], strict=True
            )
            if before != after
        )
        violations = sum(
            1
            for before, after in zip(
                runs[_attacks.DATASET_BASE].predictions, runs[variant].predictions, strict=True
            )
            if before != after
        )
        exercise = GuardExercise(
            guard_id=f"FP-R_RAW_TOKEN_INVARIANCE::{variant}",
            arm_id=ARM,
            opportunities=opportunities,
            violations=violations,
            opportunity_definition=(
                f"protected cases whose raw serialized token multiset changed under the "
                f"{variant} transform"
            ),
        )
        assessment = assess_guard(exercise, max_violation_rate=0.0)
        companion_guards.append(
            {
                "guard_id": exercise.guard_id,
                "opportunities": opportunities,
                "violations": violations,
                "violation_rate": exercise.violation_rate,
                "raw_train_multisets_changed": raw_train_changed[variant],
                "outcome": assessment.outcome.value,
                "reason": assessment.reason.value,
                "detail": assessment.detail,
            }
        )

    # -- stability battery ----------------------------------------------------
    train_labels = [row.label.value for row in base_ds.train]
    dev_labels = [row.label.value for row in base_ds.dev]
    base_train, base_dev, base_test = profile_features[_attacks.DATASET_BASE]
    vocabulary = sorted({key for row in base_train for key in row})
    rng = np.random.default_rng(20260824)
    probes: dict[str, dict[str, Any]] = {}

    identity_config, identity_predictions = _probe_run(
        train_rows=base_train,
        dev_rows=base_dev,
        test_rows=base_test,
        train_labels=train_labels,
        dev_labels=dev_labels,
    )
    probes["identity_protocol"] = {
        "config_id": identity_config,
        "changed_answers_vs_frozen_run_arm": sum(
            1
            for before, after in zip(
                runs[_attacks.DATASET_BASE].predictions, identity_predictions, strict=True
            )
            if before != after
        ),
    }
    for solver in ("newton-cg", "sag"):
        config, predictions = _probe_run(
            train_rows=base_train,
            dev_rows=base_dev,
            test_rows=base_test,
            train_labels=train_labels,
            dev_labels=dev_labels,
            logistic_solver=solver,
        )
        probes[f"solver_{solver}"] = {
            "config_id": config,
            "changed_answers_vs_frozen_run_arm": sum(
                1
                for before, after in zip(
                    runs[_attacks.DATASET_BASE].predictions, predictions, strict=True
                )
                if before != after
            ),
        }
    for label, order in (
        ("column_order_reversed", list(reversed(vocabulary))),
        ("column_order_shuffled", [vocabulary[i] for i in rng.permutation(len(vocabulary))]),
    ):
        config, predictions = _probe_run(
            train_rows=base_train,
            dev_rows=base_dev,
            test_rows=base_test,
            train_labels=train_labels,
            dev_labels=dev_labels,
            rename=_column_order_rename(base_train, order),
        )
        probes[label] = {
            "config_id": config,
            "changed_answers_vs_frozen_run_arm": sum(
                1
                for before, after in zip(
                    runs[_attacks.DATASET_BASE].predictions, predictions, strict=True
                )
                if before != after
            ),
        }

    # -- endpoints and terminal ------------------------------------------------
    semantic_orbit_guard = next(
        guard for guard in companion_guards if guard["guard_id"].endswith(_attacks.DATASET_ORBIT)
    )
    e_inv = (
        semantic_orbit_guard["opportunities"] == 128
        and semantic_orbit_guard["violations"] == 0
        and all(guard["violations"] == 0 for guard in companion_guards)
    )
    e_stab = probes["identity_protocol"]["changed_answers_vs_frozen_run_arm"] == 0 and all(
        probe["changed_answers_vs_frozen_run_arm"] == 0
        for name, probe in probes.items()
        if name != "identity_protocol"
    )
    base_response = arms_table[_attacks.DATASET_BASE]
    e_perf = (
        base_response["accuracy"] >= PERFORMANCE_FLOOR
        and base_response["distinct_predictions"] > 1
    )

    if e_inv and e_stab and e_perf:
        terminal = TERMINAL_REVIVED
    elif e_inv and e_stab:
        terminal = TERMINAL_LEVEL_NOT_RECOVERED
    else:
        terminal = TERMINAL_DEFECT

    colouring_stats = {
        "corpus_tokens": len(colourings[_attacks.DATASET_BASE]),
        "distinct_colours": len(set(colourings[_attacks.DATASET_BASE].values())),
        "train_feature_columns": len(vocabulary),
        "orbit_colouring_bitwise_identical": sorted(
            colourings[_attacks.DATASET_ORBIT].values()
        )
        == sorted(colourings[_attacks.DATASET_BASE].values()),
        "base_vs_orbit_profile_features_bitwise_identical": profile_features[
            _attacks.DATASET_BASE
        ]
        == profile_features[_attacks.DATASET_ORBIT],
    }

    payload: dict[str, Any] = {
        "protocol": "P9.D1T4S.INVARIANT_PROFILE_ROBUSTNESS.v1",
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_digest": frozen_digest(),
        "environment": {
            "python": sys.version.split()[0],
            "sklearn": sklearn.__version__,
            "scipy": scipy.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "preconditions": {
            "frozen_module_twin_verified": True,
            **dataset_fidelity,
        },
        "arm": ARM,
        "colouring": colouring_stats,
        "arms": arms_table,
        "frozen_battery_components": [component.as_json() for component in frozen_components],
        "companion_raw_guards": companion_guards,
        "stability_battery": probes,
        "endpoints": {
            "E-INV_invariance": e_inv,
            "E-STAB_stability": e_stab,
            "E-PERF_level": e_perf,
            "performance_floor": PERFORMANCE_FLOOR,
            "base_accuracy": base_response["accuracy"],
            "base_distinct_predictions": base_response["distinct_predictions"],
        },
        "terminal": terminal,
        "non_claims": [
            "BOUNDED_D1_ONLY: a statement about the D1 v1.2 classical-learner benchmark on its "
            "128-case protected split and nothing else; no claim about any language model, any "
            "scale, any second model family, or issue #618",
            "no claim about any frozen arm other than TYPED_SERIALIZED_BAG's recorded defeat",
            "no claim that the successor is a better learner, only that it is a stable and "
            "format-invariant function of the same information",
            "the frozen T4 campaign, its protocol, receipts and the D1 v1.2 execution artifacts "
            "are unmodified; this lane adds files only",
        ],
    }
    payload["result_digest"] = content_digest(payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[4]
    payload = run_battery(repo_root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["terminal"] == TERMINAL_REVIVED:
        return 0
    if payload["terminal"] == TERMINAL_LEVEL_NOT_RECOVERED:
        return 3
    return 4


if __name__ == "__main__":
    sys.exit(main())
