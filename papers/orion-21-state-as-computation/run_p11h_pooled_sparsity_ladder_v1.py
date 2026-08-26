"""P11H: a pooled universal-decoder attack over a frozen state-sparsity ladder.

P11G froze one universal arm against one pair of cells and survived. The audit in
``orion.study.p11.attack_audit`` then established that it could not have done
anything else: all four of its scientific gates hold in every world its freeze
admits, so the survival was decided before the seed was drawn
(``UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL``).

P11H is a **successor protocol**, not an edit. Nothing of P11C-P11G is touched.
Three things change, and each is answering one of the four requirements
``P11G_ARM_PLACEMENT_ADJUDICATION_V1.md`` states for a successor:

1. **The gate is pooled.** Every universal-state arm the claim covers is
   registered, and the combination rule --- the strongest arm at each training
   size --- is frozen inside this protocol's own positive gate. P11G gated on one
   arm and its terminal was a function of which arm that was.
2. **The gate's failing region is reachable.** The protected regimes are *drawn*
   by the fresh seed from a frozen ladder of state-sparsity regimes that spans
   the decision boundary, so the pooled attack wins in some admissible worlds and
   loses in others. P11G's thresholds are carried over unedited; what changes is
   the support of the statistic they read.
3. **The decoder-held-fixed control is in the receipt.** Each regime publishes
   the gap decomposed into its decoder-family half and its representation half,
   for both registered decoder families, rather than leaving it to an audit.

The ladder was sized at :data:`PREFLIGHT_SEED`, which is *not* the seed the
result is read at. Naming a rung after that sizing would be post-hoc selection,
which is why the executable draws the protected pair from the whole ladder at
:data:`EXECUTION_SEED` instead.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import warnings

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression

SCHEMA = "ORION.P11H.PooledSparsityLadderAttack.v1"
PROTOCOL = "P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md"

#: The seed the ladder was sized at. Used only by the pre-run attainability
#: preflight; no gate is ever read at this seed.
PREFLIGHT_SEED = 2026082201

#: The fresh data seed the terminal is read at. Frozen before execution.
EXECUTION_SEED = 2026082210

#: The frozen ladder of admissible regimes, ``(d, s, r)``: ``d`` binary inputs,
#: parity subsets of size ``s`` spanning the complete universal bank of
#: ``C(d, s)`` columns, and ``r`` of them active in each protected query.
#:
#: ``r`` is the width of the query-conditioned compiled state and is the axis
#: that moves the pooled attack across the 0.95 bar; the bank width ``C(d, s)``
#: is carried at three values so the ladder is not a single-axis artifact. Only
#: coordinates whose every rung gives the same gate verdicts at all three
#: preflight seeds are admitted, which is a statement about power and not about
#: which verdict a rung produces --- the excluded coordinates are excluded in
#: both directions. ``P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md`` publishes the
#: whole candidate table, including the rejected rows.
LADDER: tuple[tuple[int, int, int], ...] = (
    (14, 2, 3),
    (14, 3, 3),
    (19, 3, 3),
    (14, 2, 7),
    (14, 3, 7),
    (19, 3, 7),
)

#: The two declared coordinates the ladder is the complete cross of. It is a
#: 2x3 factorial and not a hand-picked list: ``r`` is the width of the
#: query-conditioned compiled state, ``(d, s)`` is the geometry of the complete
#: universal parity bank, and every combination of the two is on the ladder.
STATE_WIDTHS = (3, 7)
BANK_GEOMETRIES = ((14, 2), (14, 3), (19, 3))

#: How many rungs the fresh seed draws as the protected regimes.
N_PROTECTED = 2

TRAIN_SIZES = (64, 128, 256)

#: Sizes strictly below the threshold gate's 256. A pooled curve that reaches
#: the target only at 256 or later is what the gate calls "not reached below".
GATE_SIZES = (64, 128)
GATE_TRAIN_SIZE = 64
GATE_THRESHOLD_SIZE = 256

N_TEST = 4096
N_QUERIES = 5
N_TREES = 96

#: P11G's own thresholds, carried over unedited.
TARGET_ACCURACY = 0.95
DELTA64_THRESHOLD = 0.20

#: Every universal-state arm this protocol's claim covers. The gate reads the
#: pool, not a member of it.
UNIVERSAL_POOL = ("UNIVERSAL_L1", "UNIVERSAL_L2", "UNIVERSAL_EXTRA_TREES")
DEFENCE_ARM = "COMPILED_L2"
DECODER_CONTROL_ARM = "COMPILED_EXTRA_TREES"
COMPILED_ARMS = (DEFENCE_ARM, DECODER_CONTROL_ARM)
ALL_ARMS = UNIVERSAL_POOL + COMPILED_ARMS

SURVIVED_TERMINAL = "P11H_COMPILED_STATE_ADVANTAGE_SURVIVED_POOLED_ATTACK"
PREVAILED_TERMINAL = "P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED"
PRECONDITION_TERMINAL = "P11H_INSTRUMENT_PRECONDITION_NOT_MET"

#: Gate roles, in ``orion.programme.gate_attainability``'s sense. A precondition
#: certifies the instrument and may hold in every admissible world; a hypothesis
#: carries the claim and may not.
GATE_ROLES = {
    "no_answer_laundering": "PRECONDITION",
    "attack_live_on_ladder": "PRECONDITION",
    "compiled_by_64": "PRECONDITION",
    "pooled_universal_threshold_ge_256": "HYPOTHESIS",
    "delta64_ge_0_20": "HYPOTHESIS",
}
HYPOTHESIS_GATES = tuple(k for k, v in GATE_ROLES.items() if v == "HYPOTHESIS")
PRECONDITION_GATES = tuple(k for k, v in GATE_ROLES.items() if v == "PRECONDITION")

OUT = Path(__file__).with_name("P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json")


def bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    idx = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, idx], axis=2, dtype=np.int8)


def rung_stream(seed: int, cell: tuple[int, int, int]) -> np.random.Generator:
    """The data stream for one rung.

    Keyed by the rung's ``(d, s, r)`` rather than by its position, so a rung's
    readings are a function of the regime and not of where it happens to sit in
    the ladder. Independent of every other rung and of the draw.
    """

    return np.random.default_rng([seed, 0, *cell])


def draw_stream(seed: int) -> np.random.Generator:
    """The stream that selects the protected regimes. Disjoint from every rung's."""

    return np.random.default_rng([seed, 1])


def estimator_seed(
    seed: int, cell: tuple[int, int, int], query: int, size: int, arm: int
) -> int:
    """An explicit deterministic ``random_state`` per regime/query/size/arm.

    Derived arithmetically from the protocol's own seed, the way P11G's
    ``tree_seed``/``compiled_seed`` are, so a reader can evaluate it by hand.
    """

    d, s, r = cell
    regime = (d * 121) + (s * 11) + r
    return seed + 1_000_003 * arm + 10_007 * regime + 101 * query + size


def model(arm: str, seed: int):
    if arm in ("UNIVERSAL_EXTRA_TREES", DECODER_CONTROL_ARM):
        return ExtraTreesClassifier(
            n_estimators=N_TREES, max_features="sqrt", random_state=seed, n_jobs=1
        )
    if arm == "UNIVERSAL_L1":
        return LogisticRegression(
            C=0.1, penalty="l1", solver="liblinear", max_iter=1000, random_state=seed
        )
    return LogisticRegression(C=1.0, solver="liblinear", max_iter=1000, random_state=seed)


def fit_score(estimator, train_x, train_y, test_x, test_y) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        estimator.fit(train_x, train_y)
        return float(estimator.score(test_x, test_y))


def pooled_at(curves: dict[str, dict[int, float]], size: int) -> float:
    """The frozen combination rule: the strongest registered universal arm at this size."""

    return max(curves[arm][size] for arm in UNIVERSAL_POOL)


def censored_threshold(curves: dict[str, dict[int, float]]) -> int:
    """Earliest size at which the pool reaches the target, censored at 256.

    A pooled curve reaching the target at 256, at 1024 or nowhere are one value
    to the gate, and censoring says that without promoting a censored reading to
    ``NOT_REACHED``.
    """

    for size in TRAIN_SIZES:
        if size >= GATE_THRESHOLD_SIZE:
            break
        if pooled_at(curves, size) >= TARGET_ACCURACY:
            return size
    return GATE_THRESHOLD_SIZE


def measure_rung(seed: int, index: int) -> dict[str, object]:
    """One rung of the ladder: every registered arm's curve on one frozen data stream."""

    cell = LADDER[index]
    d, s, r = cell
    rng = rung_stream(seed, cell)
    subsets = list(itertools.combinations(range(d), s))
    nb = len(subsets)

    queries = [rng.choice(nb, size=r, replace=False).tolist() for _ in range(N_QUERIES)]
    test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
    test_bank = bank(test_x, subsets)

    test_y: list[np.ndarray] = []
    laundering: list[list[object]] = []
    for qi, active in enumerate(queries):
        vals = test_bank[:, active]
        signed = np.where(vals.sum(axis=1) > 0, 1, -1).astype(np.int8)
        test_y.append((signed > 0).astype(np.int8))
        for j in range(r):
            if np.array_equal(vals[:, j], signed):
                laundering.append([index, qi, j, "equals"])
            if np.array_equal(vals[:, j], -signed):
                laundering.append([index, qi, j, "negates"])

    curves: dict[str, dict[int, float]] = {arm: {} for arm in ALL_ARMS}
    for size in TRAIN_SIZES:
        train_x = rng.choice((-1, 1), size=(size, d)).astype(np.int8)
        train_bank = bank(train_x, subsets)
        scores: dict[str, list[float]] = {arm: [] for arm in ALL_ARMS}
        for qi, active in enumerate(queries):
            y = (train_bank[:, active].sum(axis=1) > 0).astype(np.int8)
            for ai, arm in enumerate(ALL_ARMS):
                columns = list(active) if arm in COMPILED_ARMS else slice(None)
                scores[arm].append(
                    fit_score(
                        model(arm, estimator_seed(seed, cell, qi, size, ai)),
                        train_bank[:, columns],
                        y,
                        test_bank[:, columns],
                        test_y[qi],
                    )
                )
        for arm in ALL_ARMS:
            curves[arm][size] = float(np.mean(scores[arm]))

    pooled = {size: pooled_at(curves, size) for size in TRAIN_SIZES}
    compiled64 = curves[DEFENCE_ARM][GATE_TRAIN_SIZE]
    control64 = curves[DECODER_CONTROL_ARM][GATE_TRAIN_SIZE]
    tree64 = curves["UNIVERSAL_EXTRA_TREES"][GATE_TRAIN_SIZE]
    linear64 = curves["UNIVERSAL_L2"][GATE_TRAIN_SIZE]
    published = compiled64 - tree64

    return {
        "rung": index,
        "cell": [d, s, r],
        "universal_dimension": nb,
        "compiled_dimension": r,
        "representation_ratio": nb / r,
        "curves": {arm: {str(k): v for k, v in curve.items()} for arm, curve in curves.items()},
        "pooled_curve": {str(k): v for k, v in pooled.items()},
        "pooled_censored_threshold": censored_threshold(curves),
        "pooled_best_below_gate": max(pooled[size] for size in GATE_SIZES),
        "compiled_at_64": compiled64,
        "delta64_vs_pool": compiled64 - pooled[GATE_TRAIN_SIZE],
        "laundering_failures": laundering,
        # The decoder-held-fixed decomposition, computed here rather than left to
        # an audit. Each family's representation half moves only the columns the
        # decoder is shown; the decoder half moves only the learner.
        "decomposition": {
            "published_gap_at_64": published,
            "tree_family": {
                "decoder_family_gap": compiled64 - control64,
                "representation_gap": control64 - tree64,
                "state_share": (control64 - tree64) / published if published else None,
            },
            "linear_family_representation_gap": compiled64 - linear64,
        },
    }


def measure_ladder(seed: int) -> list[dict[str, object]]:
    return [measure_rung(seed, index) for index in range(len(LADDER))]


def drawn_regimes(seed: int) -> list[int]:
    """The protected regimes the fresh seed selects from the frozen ladder."""

    drawn = draw_stream(seed).choice(len(LADDER), size=N_PROTECTED, replace=False)
    return sorted(int(index) for index in drawn)


def gate_statistics(ladder: list[dict[str, object]], protected: list[int]) -> dict[str, float]:
    """Each gate's statistic, as one number, over the drawn regimes.

    Stated as quantities rather than booleans so a verdict reports a distance to
    its bar and an attainability check has something to bound.
    """

    rungs = [ladder[index] for index in protected]
    return {
        "no_answer_laundering": float(sum(len(r["laundering_failures"]) for r in rungs)),
        "attack_live_on_ladder": max(float(r["pooled_best_below_gate"]) for r in ladder),
        "compiled_by_64": min(float(r["compiled_at_64"]) for r in rungs),
        "pooled_universal_threshold_ge_256": max(
            float(r["pooled_best_below_gate"]) for r in rungs
        ),
        "delta64_ge_0_20": min(float(r["delta64_vs_pool"]) for r in rungs),
    }


def gate_booleans(values: dict[str, float]) -> dict[str, bool]:
    return {
        "no_answer_laundering": values["no_answer_laundering"] <= 0.0,
        "attack_live_on_ladder": values["attack_live_on_ladder"] >= TARGET_ACCURACY,
        "compiled_by_64": values["compiled_by_64"] >= TARGET_ACCURACY,
        "pooled_universal_threshold_ge_256": (
            values["pooled_universal_threshold_ge_256"] <= TARGET_ACCURACY
        ),
        "delta64_ge_0_20": values["delta64_ge_0_20"] >= DELTA64_THRESHOLD,
    }


def scientific_terminal(gates: dict[str, bool]) -> str:
    """Three-valued, so "the attack won" is not spelled the same as "the instrument failed"."""

    if not all(gates[name] for name in PRECONDITION_GATES):
        return PRECONDITION_TERMINAL
    if all(gates[name] for name in HYPOTHESIS_GATES):
        return SURVIVED_TERMINAL
    return PREVAILED_TERMINAL


def scientific_payload(seed: int = EXECUTION_SEED) -> dict[str, object]:
    ladder = measure_ladder(seed)
    protected = drawn_regimes(seed)
    values = gate_statistics(ladder, protected)
    gates = gate_booleans(values)
    return {
        "schema": "ORION.P11H.PooledSparsityLadderAttack.ScientificPayload.v1",
        "protocol": PROTOCOL,
        "seed": seed,
        "n_trees": N_TREES,
        "n_jobs": 1,
        "n_queries": N_QUERIES,
        "n_test": N_TEST,
        "train_sizes": list(TRAIN_SIZES),
        "universal_pool": list(UNIVERSAL_POOL),
        "defence_arm": DEFENCE_ARM,
        "decoder_control_arm": DECODER_CONTROL_ARM,
        "ladder": [list(cell) for cell in LADDER],
        "state_widths": list(STATE_WIDTHS),
        "bank_geometries": [list(g) for g in BANK_GEOMETRIES],
        "ladder_readings": ladder,
        "protected_regimes": protected,
        "protected_cells": [list(LADDER[index]) for index in protected],
        "gate_statistics": values,
        "gate_roles": dict(GATE_ROLES),
        "scientific_gates": gates,
        "scientific_terminal": scientific_terminal(gates),
    }


def canonical_text(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_once(path: Path) -> None:
    path.write_text(canonical_text(scientific_payload()), encoding="utf-8")


def authoritative_main() -> None:
    with tempfile.TemporaryDirectory(prefix="p11h-replay-") as td:
        root = Path(td)
        a, b = root / "a.json", root / "b.json"
        runs = [
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--once", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            for path in (a, b)
        ]
        subprocess_success = all(run.returncode == 0 for run in runs)
        if not subprocess_success:
            raise SystemExit(
                "P11H subprocess failure\n"
                + "".join(run.stdout + run.stderr for run in runs)
            )
        first_bytes, second_bytes = a.read_bytes(), b.read_bytes()
        first_sha = hashlib.sha256(first_bytes).hexdigest()
        second_sha = hashlib.sha256(second_bytes).hexdigest()
        replay_match = first_bytes == second_bytes and first_sha == second_sha

        scientific = json.loads(first_bytes.decode("utf-8"))
        gates = dict(scientific["scientific_gates"])
        gates["two_fresh_subprocess_payloads_byte_identical"] = replay_match
        gates["subprocesses_successful"] = subprocess_success
        terminal = (
            scientific["scientific_terminal"]
            if replay_match and subprocess_success
            else PRECONDITION_TERMINAL
        )

        result = {
            "schema": SCHEMA,
            "protocol": PROTOCOL,
            "scientific_payload": scientific,
            "replay": {
                "first_sha256": first_sha,
                "second_sha256": second_sha,
                "byte_identical": replay_match,
                "fresh_python_subprocesses": 2,
            },
            "gates": gates,
            "terminal": terminal,
        }
        text = canonical_text(result)
        OUT.write_text(text, encoding="utf-8")
        print(
            json.dumps(
                {
                    "terminal": terminal,
                    "protected_cells": scientific["protected_cells"],
                    "gate_statistics": scientific["gate_statistics"],
                    "gates": gates,
                    "replay": result["replay"],
                    "scientific_payload_sha256": first_sha,
                    "authoritative_sha256": hashlib.sha256(text.encode()).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        # A hypothesis gate that fails is the attack winning, which is a
        # first-class result and exits 0. Only a failed instrument precondition
        # is a broken run.
        if terminal == PRECONDITION_TERMINAL:
            raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", type=Path)
    args = parser.parse_args()
    if args.once is not None:
        write_once(args.once)
        return
    authoritative_main()


if __name__ == "__main__":
    main()
