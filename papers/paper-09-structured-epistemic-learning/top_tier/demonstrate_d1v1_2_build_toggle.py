#!/usr/bin/env python3
"""Toggle the 0.50-vs-0.75 serialized-arm divergence by ONE factor: the binary build.

This is the on-demand reproduction of the root cause. The factor that decides
which attractor a D1 v1.2 replay lands on is NOT the recorded version manifest,
NOT the seed, NOT the dataset, NOT the code path, and NOT sparse-vs-dense design
format -- it is the *binary build* of the numerical stack executing lbfgs.
Two builds reporting the same scipy/sklearn versions, given bit-identical inputs,
converge cleanly to different terminal coefficient vectors (n_iter 480 vs 439)
whose last-bit differences flip exactly the 32 sub-margin protected cases.

Two phases, so that both sides run on *bit-identical* inputs even though one side
cannot import the orion package:

  --dump-designs DIR    (interpreter that can import orion) regenerates the
                        frozen dataset, guards its content digest against the
                        archive, and dumps per-family design matrices + labels
                        to npz with a canonical bytes digest in DIR/MANIFEST.json.
  --refit DIR           (any interpreter with numpy+scikit-learn, no orion
                        import) reloads the serialized-arm design, verifies the
                        design digest, mirrors _select/_fit with the v1.2 lbfgs
                        contract, and classifies the attractor by numeric canary.

Running --refit under two different builds of the same recorded versions is the
toggle: same inputs, same versions, same code -> 0.50 on one build, 0.75 on the
other, with the canary predicting the side before any accuracy is read.

Exit codes: 0 coherent; 2 digest mismatch (dataset or design); 3 CANNOT_CHECK;
5 incoherent (canary did not predict the observed side).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import io
import json
import platform
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
ARCHIVED = (
    REPO / "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json"
)
ARCHIVE_DATASET_DIGEST = "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"
KNIFE_EDGE_MARGIN = 0.05
FAMILY = "TYPED_SERIALIZED_BAG"

# Duplicated from replay_d1v1_2_pinned.py (same directory) so the --refit phase
# stays importable without orion; the binding checker asserts the two copies
# are equal, which makes the duplication mechanized rather than trusted.
ARCHIVE_MATCH_COEF_SHA256 = (
    "494186ed594e077904dea4adbd75dbf8104496825e4cdf18d7e075316ecaf3de"
)
ARCHIVE_MATCH_INTERCEPT_SHA256 = (
    "af3a6c166e56cceb9cef6caed28776cf949f022049c180051774fb5c75711d1e"
)
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
        "executable": sys.executable,
    }


def _model_specs() -> list[tuple[str, str, dict[str, Any], int]]:
    # Mirrors d1_experiment.model_specs(): config, rank, and the exact
    # hyperparameters the v1.2 contract (d1_runtime) pins.
    return [
        ("logistic", "logistic-C0.1", {"C": 0.1}, 0),
        ("logistic", "logistic-C1", {"C": 1.0}, 1),
        ("logistic", "logistic-C10", {"C": 10.0}, 2),
        ("tree", "tree-depth3", {"max_depth": 3}, 10),
        ("tree", "tree-depth6", {"max_depth": 6}, 11),
        ("rf", "rf-depth6", {"n_estimators": 200, "max_depth": 6}, 20),
        ("rf", "rf-none", {"n_estimators": 300, "max_depth": None}, 21),
    ]


def _make_estimator(family: str, cfg: dict[str, Any]):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier

    if family == "logistic":  # d1_runtime v1.2 contract: lbfgs, not liblinear
        return LogisticRegression(
            C=float(cfg["C"]), max_iter=2000, random_state=2711, solver="lbfgs"
        )
    if family == "tree":
        return DecisionTreeClassifier(
            max_depth=cfg["max_depth"], min_samples_leaf=2, random_state=2712
        )
    if family == "rf":
        return RandomForestClassifier(
            n_estimators=int(cfg["n_estimators"]),
            max_depth=cfg["max_depth"],
            min_samples_leaf=2,
            random_state=2713,
            n_jobs=1,
        )
    raise ValueError(family)


def _design_digest(family_npz: dict[str, Any]) -> str:
    order = ("Xtr", "Xdev", "Xte", "ytr", "ydev", "yte")
    h = hashlib.sha256()
    for key in order:
        h.update(np_canonical_bytes(family_npz[key]))
    return "sha256:" + h.hexdigest()


def np_canonical_bytes(arr: Any) -> bytes:
    import numpy as np

    a = np.ascontiguousarray(arr)
    return a.tobytes()


def _canary(model: Any) -> dict[str, Any]:
    import numpy as np

    coef = np.asarray(model.coef_, dtype="<f8")
    inter = np.asarray(model.intercept_, dtype="<f8")
    return {
        "coef_sha256": hashlib.sha256(coef.tobytes()).hexdigest(),
        "intercept_sha256": hashlib.sha256(inter.tobytes()).hexdigest(),
        "n_iter": int(np.asarray(model.n_iter_).ravel()[0]),
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


def dump_designs(out_dir: Path) -> int:
    sys.path.insert(0, str(REPO / "src"))
    try:
        import numpy as np  # noqa: F401
        from sklearn.feature_extraction import DictVectorizer

        from orion.study.p9 import d1_runtime  # noqa: F401  v1.2 estimator contract
        from orion.study.p9 import d1_experiment as base
        from orion.study.p9.d1 import generate_d1_dataset
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    dataset = generate_d1_dataset(
        seed="p9-d1-method-transfer-v1",
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()
    if dataset.manifest_digest != ARCHIVE_DATASET_DIGEST:
        print(
            json.dumps(
                {
                    "status": "DATASET_DIGEST_MISMATCH",
                    "observed": dataset.manifest_digest,
                    "archived": ARCHIVE_DATASET_DIGEST,
                }
            )
        )
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    families: dict[str, Any] = {}
    test_ids: list[str] = []
    for fam in base.D1FeatureFamily:
        vec = DictVectorizer(sparse=True)
        arrays = {
            "Xtr": vec.fit_transform([base.features(r, fam) for r in dataset.train]).toarray(),
            "Xdev": vec.transform([base.features(r, fam) for r in dataset.dev]).toarray(),
            "Xte": vec.transform([base.features(r, fam) for r in dataset.test]).toarray(),
            "ytr": np.array([r.label.value for r in dataset.train]),
            "ydev": np.array([r.label.value for r in dataset.dev]),
            "yte": np.array([r.label.value for r in dataset.test]),
        }
        np.savez(out_dir / f"design_{fam.value}.npz", **arrays)
        families[fam.value] = {
            "shapes": {k: list(v.shape) for k, v in arrays.items()},
            "design_digest": _design_digest(arrays),
        }
        if not test_ids:
            test_ids = [r.instance_id for r in dataset.test]

    manifest = {
        "schema": "orion.p9.d1v1_2-build-toggle.designs.v1",
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "dump_environment": _fingerprint_environment(),
        "dataset_manifest_digest": dataset.manifest_digest,
        "families": families,
        "test_instance_ids": test_ids,
    }
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "OK", "families": sorted(families), "dir": str(out_dir)}))
    return 0


def refit(designs_dir: Path, emit_receipt: Path | None) -> int:
    try:
        import numpy as np
        import scipy  # noqa: F401
        import sklearn  # noqa: F401
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    manifest = json.loads((designs_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    npz = np.load(designs_dir / f"design_{FAMILY}.npz", allow_pickle=False)
    arrays = {k: npz[k] for k in ("Xtr", "Xdev", "Xte", "ytr", "ydev", "yte")}
    observed_design_digest = _design_digest(arrays)
    recorded_design_digest = manifest["families"][FAMILY]["design_digest"]
    if observed_design_digest != recorded_design_digest:
        print(
            json.dumps(
                {
                    "status": "DESIGN_DIGEST_MISMATCH",
                    "observed": observed_design_digest,
                    "recorded": recorded_design_digest,
                }
            )
        )
        return 2

    # Mirror _select: fit all seven specs on train, dev accuracy, then
    # sort by (-dev_accuracy, complexity_rank, config_id).
    ranked = []
    for family, cid, cfg, rank in _model_specs():
        m = _make_estimator(family, cfg)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            m.fit(arrays["Xtr"], arrays["ytr"])
        conv_warnings = [str(w.message) for w in caught if issubclass(w.category, UserWarning)]
        acc = float(np.mean(m.predict(arrays["Xdev"]) == arrays["ydev"]))
        ranked.append((-acc, rank, cid, m, family, conv_warnings))
    ranked.sort(key=lambda r: (r[0], r[1], r[2]))
    dev_table = [
        {"config_id": cid, "dev_accuracy": -neg, "complexity_rank": rank}
        for neg, rank, cid, _m, _f, _w in ranked
    ]
    _, _, selected_cid, model, selected_family, selected_warnings = ranked[0]

    pred = [str(x) for x in model.predict(arrays["Xte"])]
    test_accuracy = float(np.mean([p == t for p, t in zip(pred, arrays["yte"], strict=True)]))
    proba = model.predict_proba(arrays["Xte"])
    ordered = np.sort(proba, axis=1)
    margins = ordered[:, -1] - ordered[:, -2]

    # Within-build determinism: refit the same spec, compare coefficient bytes.
    refit_cfg = next(cfg for _f, cid, cfg, _r in _model_specs() if cid == selected_cid)
    refit_model = _make_estimator(selected_family, refit_cfg)
    refit_model.fit(arrays["Xtr"], arrays["ytr"])
    determinism_delta = float(
        np.max(
            np.abs(
                np.asarray(refit_model.coef_, dtype=float)
                - np.asarray(model.coef_, dtype=float)
            )
        )
    )

    canary = _canary(model)
    canary_attractor = _attractor_from_canary(canary)

    archived = json.loads(ARCHIVED.read_text(encoding="utf-8"))
    arch_pred = {
        p["instance_id"]: p["prediction"]
        for p in archived["results"][FAMILY]["test_predictions"]
    }
    test_ids = manifest["test_instance_ids"]
    flips = [
        {
            "instance_id": iid,
            "archive_prediction": arch_pred[iid],
            "this_build_prediction": p,
            "target": t,
            "margin": float(m),
        }
        for iid, p, t, m in zip(test_ids, pred, arrays["yte"], margins, strict=True)
        if p != arch_pred[iid]
    ]
    flip_targets = sorted({f["target"] for f in flips})

    observed_attractor = "UNKNOWN"
    if not flips and test_accuracy == 0.5:
        observed_attractor = "ARCHIVE_MATCH"
    elif test_accuracy == 0.75 and len(set(pred)) == 2:
        observed_attractor = "DIVERGENT_SIDE"
    coherent = (
        canary_attractor == observed_attractor
        and observed_attractor != "UNKNOWN"
        and len([1 for m in margins if m < KNIFE_EDGE_MARGIN]) == 32
    )

    receipt = {
        "schema": "orion.p9.d1v1_2-build-toggle.refit.v1",
        "record": "P9_D1V1_2_BUILD_TOGGLE_REFIT",
        "executed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "environment": _fingerprint_environment(),
        "design_digest": observed_design_digest,
        "dataset_manifest_digest": manifest["dataset_manifest_digest"],
        "dump_environment": manifest["dump_environment"],
        "selection": {
            "selected_config": selected_cid,
            "selection_rule": "sort by (-dev_accuracy, complexity_rank, config_id)",
            "dev_table": dev_table,
        },
        "numeric_canary": canary,
        "canary_attractor": canary_attractor,
        "observed_attractor": observed_attractor,
        "test_accuracy": test_accuracy,
        "distinct_predictions": len(set(pred)),
        "flips_vs_archive": {
            "count": len(flips),
            "targets": flip_targets,
            "cases": flips,
        },
        "margins": {
            "knife_edge_margin": KNIFE_EDGE_MARGIN,
            "n_below": int((margins < KNIFE_EDGE_MARGIN).sum()),
            "min": float(margins.min()),
            "next_above_band": float(np.sort(margins)[int((margins < KNIFE_EDGE_MARGIN).sum())]),
        },
        "within_build_determinism": {
            "method": "refit same spec, max |coef_a - coef_b|",
            "max_abs_coef_delta": determinism_delta,
        },
        "convergence_warnings_on_selected": selected_warnings,
        "coherent": coherent,
    }
    payload = json.dumps(receipt, indent=2, sort_keys=True)
    if emit_receipt is not None:
        emit_receipt.parent.mkdir(parents=True, exist_ok=True)
        emit_receipt.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if coherent else 5


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dump-designs", type=Path, metavar="DIR", default=None)
    parser.add_argument("--refit", type=Path, metavar="DIR", default=None)
    parser.add_argument("--emit-receipt", type=Path, default=None)
    args = parser.parse_args()
    if args.dump_designs is not None:
        return dump_designs(args.dump_designs)
    if args.refit is not None:
        return refit(args.refit, args.emit_receipt)
    parser.error("choose exactly one of --dump-designs DIR or --refit DIR")
    return 3


if __name__ == "__main__":
    sys.exit(main())
