#!/usr/bin/env python3
"""Pinned D1 v1.2 replay: one documented entry point for the serialized-arm question.

The historical 0.50-vs-0.75 divergence was reopened (#1096 comment on #1086)
because a fresh preflight under the *recorded* version manifest
(Python 3.13.12 / NumPy 2.4.x / SciPy 1.17.1 / scikit-learn 1.8.0) produced 0.75
where the receipt asserted 0.50. ``P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json``
resolves that mechanistically: the version manifest does not determine the
computation. Two binary builds of the same recorded versions, given bit-identical
inputs, converge cleanly (no warnings) to *different* lbfgs terminal solutions
whose last-bit coefficient differences flip exactly the 32 sub-margin protected
cases -- the archived 0.50 and the divergent 0.75 are the two attractor terminals
of a degenerate comparator, and which one a build lands on is a property of the
build, not of the protocol.

This script makes that fact operational instead of anecdotal:

1. it fingerprints the executing numerical build *below* the version manifest,
   by hashing the converged coefficient vector of the serialized arm on the
   frozen design (the ``numeric_canary`` -- a build fingerprint that predicts
   the attractor before any accuracy is read);
2. it replays the frozen protocol v1.2 through the same code path the official
   execution used (``d1_runtime`` -> ``_select``/``_fit``/``_predict``), with
   the dataset content digest guarded against the archive;
3. it records per-case predictions *and* per-case margins, flagging the
   knife-edge band explicitly instead of letting it hide inside an accuracy
   scalar;
4. it binds canary to outcome: a run is coherent only if the canary correctly
   predicted the observed per-case attractor. A build whose canary is unknown
   fails closed.

It never relabels history: ``P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED`` stays
append-only, and no accuracy here upgrades the prior-valued measurement.

Exit codes: 0 coherent (and required attractor, if any, observed); 2 dataset
content digest mismatch; 3 CANNOT_CHECK; 4 required attractor not observed;
5 incoherent (canary did not predict the outcome, or a third attractor).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import io
import json
import platform
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
ARCHIVED = (
    REPO / "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json"
)
SEED = "p9-d1-method-transfer-v1"
SPLIT = {"train": 48, "dev": 16, "test": 32}

# Frozen archive anchors (P9_D1V1_2_LOCKED_ENV_REPRODUCTION_2026-08-23.json and
# the archived result itself). Changing these is a protocol change, not a fix.
ARCHIVE_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"
ARCHIVE_DATASET_DIGEST = "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"

# Measured 2026-08-24 (binary-build toggle experiment): the 32 knife-edge cases
# sit at margin 0.0140 (archive-matching build) / 0.0036 (divergent build) and
# the next-smallest margin is 0.9994. 0.05 is the boundary margin the divergence
# root-cause receipt already froze; it separates the band by >3x in the worst case.
KNIFE_EDGE_MARGIN = 0.05

# The numeric canary: full sha256 of the serialized arm's converged coefficients
# (little-endian float64 bytes) plus intercept, under the frozen v1.2 contract.
ARCHIVE_MATCH_COEF_SHA256 = (
    "494186ed594e077904dea4adbd75dbf8104496825e4cdf18d7e075316ecaf3de"
)
ARCHIVE_MATCH_INTERCEPT_SHA256 = (
    "af3a6c166e56cceb9cef6caed28776cf949f022049c180051774fb5c75711d1e"
)
# Dense-path prefix observed on the divergent-side build (full value recorded in
# P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json; sparse==dense verified on the
# archive-matching build only).
DIVERGENT_COEF_SHA256_PREFIX = "9b56df6a102b9b57"


def _fingerprint_environment() -> dict[str, Any]:
    import numpy as np
    import scipy
    import sklearn

    blas = "unrecorded"
    try:
        import numpy.__config__ as cfg

        try:
            blas = cfg.get_config()["Build Dependencies"]["blas"]["name"]
        except Exception:
            buf = io.StringIO()
            with redirect_stdout(buf):
                cfg.show()
            text = buf.getvalue()
            idx = text.find('"blas"')
            chunk = text[idx : idx + 400]
            for line in chunk.splitlines():
                if '"name"' in line:
                    blas = line.split('"')[-2]
                    break
    except Exception:
        pass
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "machine": platform.machine(),
        "system": platform.system(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "blas_best_effort": blas,
    }


def _canary(model: Any) -> dict[str, Any]:
    import numpy as np

    lm = model.named_steps["model"]
    coef = np.asarray(lm.coef_, dtype="<f8")
    inter = np.asarray(lm.intercept_, dtype="<f8")
    return {
        "coef_sha256": hashlib.sha256(coef.tobytes()).hexdigest(),
        "intercept_sha256": hashlib.sha256(inter.tobytes()).hexdigest(),
        "n_iter": int(np.asarray(lm.n_iter_).ravel()[0]),
    }


def _attractor_from_canary(canary: dict[str, Any]) -> str:
    coef = canary.get("coef_sha256")
    if not coef:
        return "UNKNOWN"
    if (
        coef == ARCHIVE_MATCH_COEF_SHA256
        and canary.get("intercept_sha256") == ARCHIVE_MATCH_INTERCEPT_SHA256
    ):
        return "ARCHIVE_MATCH"
    if coef.startswith(DIVERGENT_COEF_SHA256_PREFIX):
        return "DIVERGENT_SIDE"
    return "UNKNOWN"


def _canonical_digest(core: dict[str, Any]) -> str:
    blob = json.dumps(core, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _replay() -> dict[str, Any]:
    import numpy as np

    from orion.study.p9 import d1_runtime  # noqa: F401  installs the v1.2 estimator
    from orion.study.p9 import d1_experiment as base
    from orion.study.p9.d1 import generate_d1_dataset

    dataset = generate_d1_dataset(
        seed=SEED,
        train_instances_per_base_pair=SPLIT["train"],
        dev_instances_per_base_pair=SPLIT["dev"],
        test_instances_per_base_pair=SPLIT["test"],
    )
    dataset.verify()

    arms: dict[str, Any] = {}
    canary: dict[str, Any] | None = None
    for family in base.D1FeatureFamily:
        selected, _ = base._select(dataset.train, dataset.dev, family)
        model = base._fit(dataset.train, family, selected)
        rows = [base.features(row, family) for row in dataset.test]
        proba = model.predict_proba(rows)
        # Labels come from the official predict() path: on exact probability
        # ties (TRANSCRIPT_BAG's tree emits margin-0.0 leaves) sklearn's argmax
        # takes the first max class, which is the tie semantics the archive used.
        # argsort would take the last -- same accuracy, different per-case record.
        labels = [str(x) for x in model.predict(rows)]
        ordered = np.sort(proba, axis=1)
        margin = ordered[:, -1] - ordered[:, -2]
        predictions = [
            {
                "instance_id": row.instance_id,
                "prediction": label,
                "target": row.label.value,
                "correct": label == row.label.value,
                "margin": float(m),
                "knife_edge": bool(m < KNIFE_EDGE_MARGIN),
            }
            for row, label, m in zip(dataset.test, labels, margin, strict=True)
        ]
        arms[family.value] = {
            "selected_config": selected.config_id,
            "test_accuracy": float(np.mean([p["correct"] for p in predictions])),
            "distinct_predictions": len({p["prediction"] for p in predictions}),
            "predictions": predictions,
        }
        if family is base.D1FeatureFamily.TYPED_SERIALIZED_BAG:
            lm = model.named_steps["model"]
            if hasattr(lm, "coef_"):
                canary = _canary(model)
    return {
        "dataset_manifest_digest": dataset.manifest_digest,
        "arms": arms,
        "canary": canary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--emit-receipt", type=Path, default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument(
        "--require-attractor",
        choices=["ARCHIVE_MATCH", "DIVERGENT_SIDE"],
        default=None,
        help="fail (exit 4) unless this attractor is observed; default: record only",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(REPO / "src"))
    try:
        import numpy as np  # noqa: F401
        import scipy  # noqa: F401
        import sklearn  # noqa: F401
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    try:
        replayed = _replay()
    except ImportError as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    if replayed["dataset_manifest_digest"] != ARCHIVE_DATASET_DIGEST:
        print(
            json.dumps(
                {
                    "status": "DATASET_DIGEST_MISMATCH",
                    "observed": replayed["dataset_manifest_digest"],
                    "archived": ARCHIVE_DATASET_DIGEST,
                }
            )
        )
        return 2

    canary = replayed["canary"] or {
        "coef_sha256": None,
        "intercept_sha256": None,
        "n_iter": None,
    }

    archived = json.loads(ARCHIVED.read_text(encoding="utf-8"))
    per_arm_archive_match = {}
    for family_value, arm in replayed["arms"].items():
        arch_pred = {
            p["instance_id"]: p["prediction"]
            for p in archived["results"][family_value]["test_predictions"]
        }
        per_arm_archive_match[family_value] = all(
            p["prediction"] == arch_pred[p["instance_id"]]
            for p in arm["predictions"]
        ) and set(arch_pred) == {p["instance_id"] for p in arm["predictions"]}

    subject = replayed["arms"]["TYPED_SERIALIZED_BAG"]
    observed_attractor = "UNKNOWN"
    if per_arm_archive_match["TYPED_SERIALIZED_BAG"] and subject["test_accuracy"] == 0.5:
        observed_attractor = "ARCHIVE_MATCH"
    elif subject["test_accuracy"] == 0.75 and subject["distinct_predictions"] == 2:
        observed_attractor = "DIVERGENT_SIDE"

    canary_attractor = _attractor_from_canary(canary)
    knife_edge_ids = [p["instance_id"] for p in subject["predictions"] if p["knife_edge"]]
    knife_edge_band_is_the_historical_thirty_two = (
        observed_attractor in ("ARCHIVE_MATCH", "DIVERGENT_SIDE") and len(knife_edge_ids) == 32
    )
    coherent = (
        canary_attractor == observed_attractor
        and observed_attractor != "UNKNOWN"
        and knife_edge_band_is_the_historical_thirty_two
    )
    core = {
        "schema": "orion.p9.d1v1_2-pinned-replay.core.v1",
        "record": "P9_D1V1_2_PINNED_REPLAY",
        "dataset_manifest_digest": replayed["dataset_manifest_digest"],
        "archive_result_digest": ARCHIVE_RESULT_DIGEST,
        "knife_edge_margin": KNIFE_EDGE_MARGIN,
        "arms": replayed["arms"],
        "numeric_canary": canary,
        "canary_attractor": canary_attractor,
        "observed_attractor": observed_attractor,
        "per_arm_archive_match": per_arm_archive_match,
    }
    result_digest = _canonical_digest(core)

    checks = {
        "dataset_digest_matches_archive": True,
        "canary_predicted_the_observed_attractor": canary_attractor == observed_attractor
        and observed_attractor != "UNKNOWN",
        "attractor_is_one_of_the_two_known_values": observed_attractor
        in ("ARCHIVE_MATCH", "DIVERGENT_SIDE"),
        "knife_edge_band_is_the_historical_thirty_two": knife_edge_band_is_the_historical_thirty_two,
    }

    receipt = {
        "schema": "orion.p9.d1v1_2-pinned-replay.v1",
        "record": "P9_D1V1_2_PINNED_REPLAY",
        "run_id": args.run_id,
        "executed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "environment": _fingerprint_environment(),
        "require_attractor": args.require_attractor,
        "result_digest": result_digest,
        "core": core,
        "serialized_arm_summary": {
            "test_accuracy": subject["test_accuracy"],
            "distinct_predictions": subject["distinct_predictions"],
            "knife_edge_cases": len(knife_edge_ids),
        },
        "checks": checks,
        "relabels_nothing": (
            "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED stays append-only; the "
            "archived 0.5 remains the modal-class prior, not a measurement; this "
            "replay records which attractor the executing build lands on and why."
        ),
    }

    payload = json.dumps(receipt, indent=2, sort_keys=True)
    if args.emit_receipt is not None:
        args.emit_receipt.parent.mkdir(parents=True, exist_ok=True)
        args.emit_receipt.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    if not coherent:
        return 5
    if args.require_attractor is not None and observed_attractor != args.require_attractor:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
