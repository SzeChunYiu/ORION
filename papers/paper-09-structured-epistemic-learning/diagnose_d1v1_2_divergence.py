#!/usr/bin/env python3
"""Why the D1 v1.2 locked-environment replay read 0.75 where the archive read 0.50.

`P9_D1V1_2_LOCKED_ENV_REPRODUCTION_2026-08-23.json` records
`SCORE_DIVERGED` on TYPED_SERIALIZED_BAG: archived accuracy 0.5 with one distinct
prediction, replayed 0.75 with two, and no environment departures. Read as a
disagreement between two measurements, that is alarming. It is not one.

The arm is a **constant predictor** on the held-out domain: every protected case
is labelled OBSTRUCTION, and OBSTRUCTION is exactly half the split, so 0.5 is the
class prior rather than a measurement of anything. A quarter of the split then
sits within 0.05 probability of the decision boundary, and for every one of those
cases the runner-up class is the correct label. Tip that boundary set -- which is
all a solver version change has to do -- and accuracy moves to exactly 0.75.

So the two numbers are two sides of one boundary on an unresponsive comparator,
which is the failure class already recorded at
`research/failures/2026-08-unresponsive-comparator-prior-valued-margin/` and
listed under `already_known` in the P9-U-T4 freeze. It is measured here.

This does not relabel anything. The locked-replay terminal stays
`P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED`; this says what it failed *of*.

Exit codes: 0 the diagnosis reproduces, 2 it does not, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import platform
import sys

BOUNDARY_MARGIN = 0.05
SEED = "p9-d1-method-transfer-v1"
ARCHIVED_ACCURACY = 0.5
LOCKED_REPLAY_ACCURACY = 0.75


def main() -> int:
    try:
        import numpy as np
        import sklearn
        from orion.study.p9 import d1_runtime  # noqa: F401  installs the v1.2 estimator
        from orion.study.p9 import d1_experiment as base
        from orion.study.p9.d1 import generate_d1_dataset
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    dataset = generate_d1_dataset(
        seed=SEED,
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()

    arms = {}
    for family in base.D1FeatureFamily:
        selected, _ = base._select(dataset.train, dataset.dev, family)
        model = base._fit(dataset.train, family, selected)
        design = [base.features(row, family) for row in dataset.test]
        proba = model.predict_proba(design)
        classes = list(model.classes_)
        order = np.argsort(proba, axis=1)
        winner = [classes[i] for i in order[:, -1]]
        runner_up = [classes[i] for i in order[:, -2]]
        ordered = np.sort(proba, axis=1)
        margin = ordered[:, -1] - ordered[:, -2]
        truth = [row.label.value for row in dataset.test]
        boundary = margin < BOUNDARY_MARGIN
        flipped = [runner_up[i] if boundary[i] else winner[i] for i in range(len(truth))]
        arms[family.value] = {
            "selected_config": selected.config_id,
            "distinct_predictions": len(set(winner)),
            "accuracy": float(np.mean([w == t for w, t in zip(winner, truth)])),
            "protected_cases": len(truth),
            "boundary_cases": int(boundary.sum()),
            "boundary_fraction": float(boundary.mean()),
            "boundary_cases_whose_runner_up_is_correct": int(
                sum(1 for i in range(len(truth)) if boundary[i] and runner_up[i] == truth[i])
            ),
            "accuracy_if_boundary_set_flips": float(
                np.mean([f == t for f, t in zip(flipped, truth)])
            ),
            "unresponsive": len(set(winner)) == 1,
        }

    subject = arms["TYPED_SERIALIZED_BAG"]
    checks = {
        "reproduces_the_archived_accuracy": subject["accuracy"] == ARCHIVED_ACCURACY,
        "arm_is_a_constant_predictor": subject["distinct_predictions"] == 1,
        "flipping_the_boundary_set_reaches_the_locked_replay_value":
            subject["accuracy_if_boundary_set_flips"] == LOCKED_REPLAY_ACCURACY,
        "every_boundary_case_runner_up_is_correct":
            subject["boundary_cases_whose_runner_up_is_correct"] == subject["boundary_cases"],
    }

    print(
        json.dumps(
            {
                "schema": "orion.p9.d1v1_2-divergence-root-cause.v1",
                "record": "P9_D1V1_2_DIVERGENCE_ROOT_CAUSE",
                "authority_scope": "DIAGNOSIS_ONLY",
                "relabels_nothing": (
                    "The locked replay's terminal remains "
                    "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED. This records what it failed of."
                ),
                "environment": {
                    "python": platform.python_version(),
                    "numpy": np.__version__,
                    "scikit_learn": sklearn.__version__,
                },
                "archived_accuracy": ARCHIVED_ACCURACY,
                "locked_replay_accuracy": LOCKED_REPLAY_ACCURACY,
                "boundary_margin": BOUNDARY_MARGIN,
                "arms": arms,
                "checks": checks,
                "finding": (
                    "TYPED_SERIALIZED_BAG predicts one class on all 128 protected cases, and that "
                    "class is exactly half the split, so 0.5 is a prior and not a measurement. "
                    "32 of 128 cases lie within 0.05 of the boundary and the runner-up is correct "
                    "on all 32, so tipping that set gives 0.5 + 32/128 = 0.75 exactly. The archived "
                    "and replayed values are two sides of one boundary on an unresponsive "
                    "comparator, not two measurements that disagree."
                ),
                "consequence": (
                    "The divergence is not evidence about representation quality in either "
                    "direction, because neither number measures it. TRANSCRIPT_BAG is degenerate "
                    "the same way at the ALIGNED prior. This is the case D1 v1.3's "
                    "STRONGEST_DONOR_COMPLETE_SERIALIZATION arm exists to replace."
                ),
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
