#!/usr/bin/env python3
"""NR-06 replay-consistency check: reproduce the archived D1 v1.2 bag exactly.

Classification test for the D1v1.2 locked-env replay failure:
  - data channel: regenerate the frozen dataset, compare manifest digest to the
    archive (ordering/dedup/type-tag deltas would break this);
  - numerical channel: re-run selection + fit + protected prediction under this
    interpreter's solver stack, compare per-case predictions to the archive.

If per-case agreement is exact under an archive-matching solver stack, the
divergence was a replay-lock infrastructure defect (lock drifted past the
archive's numerical environment), and the archived bag is reproducible. It does
NOT relabel the locked-replay terminal or upgrade the prior-valued measurement.

Exit codes: 0 exact agreement, 1 disagreement, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ARCHIVED = (
    REPO
    / "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json"
)
SEED = "p9-d1-method-transfer-v1"


def main() -> int:
    try:
        import numpy as np
        import sklearn
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        sys.path.insert(0, str(REPO / "src"))
        from orion.study.p9 import d1_runtime  # noqa: F401  installs v1.2 estimator
        from orion.study.p9 import d1_experiment as base
        from orion.study.p9.d1 import generate_d1_dataset
        from orion.study.p9.d1_experiment import DictVectorizer
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    archived = json.loads(ARCHIVED.read_text())

    dataset = generate_d1_dataset(
        seed=SEED,
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()
    digest_match = dataset.manifest_digest == archived["dataset_manifest_digest"]

    arms = {}
    for family in base.D1FeatureFamily:
        selected, _ = base._select(dataset.train, dataset.dev, family)
        model = base._fit(dataset.train, family, selected)
        predictions = [
            str(p) for p in model.predict([base.features(row, family) for row in dataset.test])
        ]
        arch = archived["results"][family.value]
        arch_pred = {p["instance_id"]: p["prediction"] for p in arch["test_predictions"]}
        fresh_pred = {
            row.instance_id: p
            for row, p in zip(dataset.test, predictions, strict=True)
        }
        ids_match = set(arch_pred) == set(fresh_pred)
        per_case_match = ids_match and all(
            arch_pred[i] == fresh_pred[i] for i in arch_pred
        )
        arms[family.value] = {
            "selected_config_archived": arch["selected"]["config_id"],
            "selected_config_replay": selected.config_id,
            "selected_match": arch["selected"]["config_id"] == selected.config_id,
            "accuracy_archived": arch["test"]["accuracy"],
            "accuracy_replay": sum(
                p == row.label.value
                for row, p in zip(dataset.test, predictions, strict=True)
            )
            / len(predictions),
            "distinct_predictions_replay": len(set(predictions)),
            "per_case_prediction_agreement": bool(per_case_match),
        }

    subject = arms["TYPED_SERIALIZED_BAG"]
    out = {
        "schema": "orion.p9.nr06-replay-consistency.v1",
        "record": "P9_D1V1_2_ARCHIVE_NUMERICAL_REPLAY_CONSISTENCY",
        "authority_scope": "REPLAY_CHANNEL_DIAGNOSIS_ONLY",
        "relabels_nothing": (
            "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED stays append-only; "
            "agreement here restores replay-channel consistency under the "
            "archive-matching solver stack, not the validity of a prior-valued "
            "measurement. D1v1.3 remains the frozen scientific successor."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "locked_replay_environment": {
            "python": "3.12.13",
            "numpy": "2.5.2",
            "scikit_learn": "1.9.0",
            "source": "uv.lock (P9_D1V1_2_LOCKED_ENV_REPRODUCTION_2026-08-23.json)",
        },
        "data_channel": {
            "dataset_manifest_digest_replay": dataset.manifest_digest,
            "dataset_manifest_digest_archived": archived["dataset_manifest_digest"],
            "digest_match": bool(digest_match),
        },
        "archived_result_digest": archived["result_digest"],
        "arms": arms,
        "checks": {
            "dataset_manifest_digest_identical": bool(digest_match),
            "all_selected_configs_match": all(a["selected_match"] for a in arms.values()),
            "all_per_case_predictions_match": all(
                a["per_case_prediction_agreement"] for a in arms.values()
            ),
            "typed_serialized_bag_accuracy_equals_archived_0_5": (
                subject["accuracy_replay"] == 0.5
            ),
            "typed_serialized_bag_still_constant": (
                subject["distinct_predictions_replay"] == 1
            ),
        },
    }
    out["all_checks_pass"] = all(out["checks"].values())
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["all_checks_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
