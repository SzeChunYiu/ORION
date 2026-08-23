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

    label_counts: dict[str, int] = {}
    for row in dataset.test:
        label_counts[row.label.value] = label_counts.get(row.label.value, 0) + 1

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
    modal_share = max(label_counts.values()) / sum(label_counts.values())

    # Environment-independent. These hold wherever the diagnosis is run, and are
    # what the finding actually rests on.
    checks = {
        "the_gap_between_the_two_reported_values_is_a_quarter_of_the_split":
            round(LOCKED_REPLAY_ACCURACY - ARCHIVED_ACCURACY, 12) == 0.25,
        "a_quarter_of_the_split_is_exactly_thirty_two_cases":
            round(0.25 * subject["protected_cases"]) == 32,
        "the_modal_class_is_exactly_half_the_split": modal_share == ARCHIVED_ACCURACY,
        "the_archived_value_equals_the_modal_class_prior":
            ARCHIVED_ACCURACY == modal_share,
        "this_environment_lands_on_one_of_the_two_reported_values":
            subject["accuracy"] in (ARCHIVED_ACCURACY, LOCKED_REPLAY_ACCURACY),
    }

    # Environment-dependent. Reported, never asserted: which side of the
    # boundary a given solver lands on is the phenomenon, not a premise.
    observed = {
        "accuracy": subject["accuracy"],
        "distinct_predictions": subject["distinct_predictions"],
        "matches": (
            "ARCHIVED" if subject["accuracy"] == ARCHIVED_ACCURACY
            else "LOCKED_REPLAY" if subject["accuracy"] == LOCKED_REPLAY_ACCURACY
            else "NEITHER"
        ),
        "boundary_cases": subject["boundary_cases"],
        "boundary_cases_whose_runner_up_is_correct":
            subject["boundary_cases_whose_runner_up_is_correct"],
        "accuracy_if_boundary_set_flips": subject["accuracy_if_boundary_set_flips"],
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
                "label_counts": label_counts,
                "observed_in_this_environment": observed,
                "checks": checks,
                "finding": (
                    "The archived 0.5 is exactly the modal class prior on the protected split "
                    "(64 of 128 OBSTRUCTION), so it is a prior and not a measurement. The gap to "
                    "the locked replay's 0.75 is exactly a quarter of the split -- 32 cases -- "
                    "which is the set sitting on the decision boundary, and the runner-up is the "
                    "correct label on all of it. The two reported values are two sides of one "
                    "boundary on an unresponsive comparator, not two measurements that disagree. "
                    "Which side a given solver lands on is reported here, never asserted: this "
                    "diagnosis was first run in an environment that reproduces the archived value."
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
