"""Independent second checker for P9.D1T4S.INVARIANT_PROFILE_ROBUSTNESS.

Deliberately different implementation from the runner, per freeze §8:

- raw tokens are re-derived straight from
  ``instance.model_payload(D1View.TYPED_SERIALIZED)["sequence"]`` rather than
  through the frozen module's ``serialized_tokens`` helper;
- the base-to-orbit correspondence is verified against the frozen
  ``build_orbit_map`` ground truth, which the runner never touches;
- the stability re-probe builds its design matrices by hand as dense numpy
  arrays with its own column ordering -- no ``DictVectorizer``, no
  ``Pipeline`` -- and fits ``LogisticRegression`` directly;
- the terminal logic is re-derived from the artifact's own recorded numbers
  against the freeze's rules, independently of the runner's code;
- the runner's parameter digest and the frozen module's twin digest are
  re-verified.

Every check is green or red; nothing is tuned.  Run from the repository
root::

    PYTHONPATH=src python3 -m orion.study.p9.invariant_profile_checker

Prints one JSON object.  Exit 0 = all checks green; 4 = any check red.
"""

from __future__ import annotations

import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import scipy
import sklearn
from sklearn.linear_model import LogisticRegression

from orion.study.p9.d1 import D1View

from . import hostile_representation_attacks as _attacks
from .invariant_profile_battery import (
    PERFORMANCE_FLOOR,
    TERMINAL_DEFECT,
    TERMINAL_LEVEL_NOT_RECOVERED,
    TERMINAL_REVIVED,
    frozen_digest,
)
from .invariant_profile_representation import (
    ARM,
    build_colouring,
    features_with_colouring,
)

RESULT_ARTIFACT = (
    Path(__file__).resolve().parents[4]
    / "papers/paper-09-structured-epistemic-learning/evidence/"
    "P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_RESULT_2026-08-24.json"
)


def _payload_tokens(instance: Any) -> tuple[str, ...]:
    """Raw serialized tokens, derived directly from the d1 payload.

    The runner goes through the frozen module's ``serialized_tokens``; this
    is the same underlying token sequence reached by a different code path,
    which is the point.
    """

    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    return tuple(str(token) for token in sequence)


def _atom_of(token: str) -> str:
    body = token[len("token:"):] if token.startswith("token:") else token
    _path, _, value = body.partition("=")
    return value


def _dense_matrix(
    rows: Sequence[dict[str, object]], vocabulary: list[str]
) -> np.ndarray:
    """Hand-built dense design matrix: no DictVectorizer, no Pipeline."""

    index = {name: position for position, name in enumerate(vocabulary)}
    matrix = np.zeros((len(rows), len(vocabulary)), dtype=float)
    for i, row in enumerate(rows):
        for key, value in row.items():
            position = index.get(key)
            if position is not None:
                matrix[i, position] = float(value)
    return matrix


def check(repo_root: Path) -> dict[str, Any]:
    artifact = json.loads(RESULT_ARTIFACT.read_text(encoding="utf-8"))
    checks: dict[str, Any] = {}
    environment = {
        "python": sys.version.split()[0],
        "sklearn": sklearn.__version__,
        "scipy": scipy.__version__,
        "numpy": np.__version__,
        "platform": platform.platform(),
    }

    # C1 frozen module integrity, re-verified independently.
    try:
        _attacks.verify_against_twin(repo_root)
        checks["C1_frozen_module_twin"] = {"green": True}
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        checks["C1_frozen_module_twin"] = {"green": False, "error": str(exc)}
        return {"checks": checks, "environment": environment, "all_green": False}

    # C2 dataset fidelity and C3 the orbit correspondence on raw payloads.
    datasets = _attacks.build_datasets()
    base_ds = datasets[_attacks.DATASET_BASE]
    checks["C2_dataset_manifest"] = {
        "green": base_ds.manifest_digest == _attacks.SHIPPED_DATASET_MANIFEST_DIGEST,
        "manifest_digest": base_ds.manifest_digest,
    }
    atom_map = _attacks.build_orbit_map(base_ds)
    image_failures = 0
    compared = 0
    for split in ("train", "dev", "test"):
        for base_row, orbit_row in zip(
            getattr(base_ds, split), getattr(datasets[_attacks.DATASET_ORBIT], split), strict=True
        ):
            base_atoms = Counter(_atom_of(token) for token in _payload_tokens(base_row))
            orbit_atoms = Counter(_atom_of(token) for token in _payload_tokens(orbit_row))
            expected = Counter({atom_map.get(atom, atom): n for atom, n in base_atoms.items()})
            compared += 1
            if expected != orbit_atoms:
                image_failures += 1
    checks["C3_orbit_is_image_on_raw_payloads"] = {
        "green": image_failures == 0,
        "instances_compared": compared,
        "image_failures": image_failures,
    }

    # C4 the successor's features are bitwise identical between BASE and ORBIT,
    #    re-derived here from the representation module's own output.
    def bags(dataset: Any) -> tuple[list[dict[str, object]], ...]:
        fn = _attacks.FEATURE_FUNCTIONS[_attacks.ARM_SERIALIZED]
        return tuple([fn(row) for row in split] for split in (dataset.train, dataset.dev, dataset.test))

    base_bags = bags(base_ds)
    orbit_bags = bags(datasets[_attacks.DATASET_ORBIT])
    base_colouring = build_colouring(base_bags[0], base_bags[1])
    orbit_colouring = build_colouring(orbit_bags[0], orbit_bags[1])
    bitwise = all(
        [features_with_colouring(row, base_colouring) for row in base_bags[i]]
        == [features_with_colouring(row, orbit_colouring) for row in orbit_bags[i]]
        for i in range(3)
    )
    checks["C4_features_bitwise_identical_base_orbit"] = {
        "green": bitwise,
        "corpus_tokens": len(base_colouring),
        "distinct_colours": len(set(base_colouring.values())),
    }

    # C5 the artifact's digest and terminal follow from its own numbers.
    digest_ok = artifact["parameters_digest"] == frozen_digest()
    orbit_guard = next(
        g
        for g in artifact["companion_raw_guards"]
        if g["guard_id"].endswith(_attacks.DATASET_ORBIT)
    )
    e_inv_ok = (
        orbit_guard["opportunities"] == 128
        and orbit_guard["violations"] == 0
        and all(g["violations"] == 0 for g in artifact["companion_raw_guards"])
    )
    e_stab_ok = all(
        p["changed_answers_vs_frozen_run_arm"] == 0
        for p in artifact["stability_battery"].values()
    )
    e_perf_ok = (
        artifact["endpoints"]["base_accuracy"] >= PERFORMANCE_FLOOR
        and artifact["endpoints"]["base_distinct_predictions"] > 1
    )
    if e_inv_ok and e_stab_ok and e_perf_ok:
        derived_terminal = TERMINAL_REVIVED
    elif e_inv_ok and e_stab_ok:
        derived_terminal = TERMINAL_LEVEL_NOT_RECOVERED
    else:
        derived_terminal = TERMINAL_DEFECT
    checks["C5_terminal_follows_from_recorded_numbers"] = {
        "green": digest_ok and derived_terminal == artifact["terminal"],
        "parameters_digest_matches": digest_ok,
        "terminal_recorded": artifact["terminal"],
        "terminal_derived": derived_terminal,
        "E-INV": e_inv_ok,
        "E-STAB": e_stab_ok,
        "E-PERF": e_perf_ok,
    }

    # C6 guard arithmetic recomputed from raw payloads and recorded predictions.
    base_test_multisets = [
        tuple(sorted(_payload_tokens(row))) for row in base_ds.test
    ]
    recomputed: dict[str, dict[str, int]] = {}
    for variant_key, dataset in (
        (_attacks.DATASET_ORBIT, datasets[_attacks.DATASET_ORBIT]),
        (_attacks.DATASET_ORDER, datasets[_attacks.DATASET_ORDER]),
        (_attacks.DATASET_EQUAL_LENGTH, datasets[_attacks.DATASET_EQUAL_LENGTH]),
    ):
        multisets = [tuple(sorted(_payload_tokens(row))) for row in dataset.test]
        opportunities = sum(
            1 for before, after in zip(base_test_multisets, multisets, strict=True) if before != after
        )
        violations = sum(
            1
            for before, after in zip(
                artifact["arms"][_attacks.DATASET_BASE]["predictions"],
                artifact["arms"][variant_key]["predictions"],
                strict=True,
            )
            if before != after
        )
        recomputed[variant_key] = {"opportunities": opportunities, "violations": violations}
    recorded = {
        g["guard_id"].split("::")[1]: {
            "opportunities": g["opportunities"],
            "violations": g["violations"],
        }
        for g in artifact["companion_raw_guards"]
    }
    checks["C6_guard_arithmetic_recomputed"] = {
        "green": recomputed == recorded,
        "recomputed": recomputed,
        "recorded": recorded,
    }

    # C7 stability re-probed with the hand-built matrix, different code path:
    #    the recorded selected config refitted directly on a dense matrix,
    #    under a second solver family and under a reversed column order.
    train_dicts = [features_with_colouring(row, base_colouring) for row in base_bags[0]]
    test_dicts = [features_with_colouring(row, base_colouring) for row in base_bags[2]]
    train_labels = [row.label.value for row in base_ds.train]
    vocabulary = sorted({key for row in train_dicts for key in row})
    recorded_predictions = tuple(artifact["arms"][_attacks.DATASET_BASE]["predictions"])
    selected = artifact["arms"][_attacks.DATASET_BASE]["config_id"]
    c_value = float(selected.split("C")[1])

    def refit(order: Sequence[str], solver: str) -> tuple[str, ...]:
        matrix = _dense_matrix(train_dicts, list(order))
        test_matrix = _dense_matrix(test_dicts, list(order))
        model = LogisticRegression(
            C=c_value, max_iter=2000, random_state=2711, solver=solver
        )
        model.fit(matrix, train_labels)
        return tuple(str(value) for value in model.predict(test_matrix))

    identity_answers = refit(vocabulary, "lbfgs")
    probes = {
        "dense_lbfgs": identity_answers,
        "dense_newton-cg": refit(vocabulary, "newton-cg"),
        "dense_reversed_order": refit(list(reversed(vocabulary)), "lbfgs"),
    }
    changed = {name: sum(1 for x, y in zip(recorded_predictions, answers, strict=True) if x != y) for name, answers in probes.items()}
    checks["C7_stability_reprobed_dense_matrix"] = {
        "green": all(count == 0 for count in changed.values()),
        "changed_answers_vs_recorded": changed,
        "selected_config": selected,
        "train_matrix_rank": int(np.linalg.matrix_rank(_dense_matrix(train_dicts, vocabulary))),
        "train_matrix_columns": len(vocabulary),
    }

    # C8 the frozen battery's own guard verdicts for the successor arm are the
    #    no-op verdicts the freeze pre-registered as expected.
    frozen_verdicts = {
        c["component_id"]: c["outcome"] for c in artifact["frozen_battery_components"]
    }
    checks["C8_frozen_components_as_preregistered"] = {
        "green": all(
            outcome == "CANNOT_CHECK" for outcome in frozen_verdicts.values()
        ),
        "verdicts": frozen_verdicts,
    }

    all_green = all(entry["green"] for entry in checks.values())
    return {
        "schema": "P9.T4SIndependentCheck.v1",
        "arm": ARM,
        "checks": checks,
        "environment": environment,
        "parameters_digest_checked": artifact["parameters_digest"],
        "all_green": all_green,
        "terminal": (
            "P9_T4_SUCCESSOR_SECOND_CHECKER_GREEN"
            if all_green
            else "P9_T4_SUCCESSOR_SECOND_CHECKER_DEFECT"
        ),
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[4]
    report = check(repo_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_green"] else 4


if __name__ == "__main__":
    sys.exit(main())
