"""How stable is the sparse-decoder threshold P11's gates turn on?

``P11C`` and ``P11E`` ask the same question of the same construction --- cells
``(17,4,5)`` and ``(19,3,7)``, five compiled components against 2,380 and 969
parity features, the same training grid --- and differ only in their master
seed. They disagree about the answer in the first cell:

=========  ============  ==================================
protocol   master seed   ``UNIVERSAL_L1`` threshold, cell 1
=========  ============  ==================================
``P11E``   2026082117    128
``P11C``   2026082111    256
=========  ============  ==================================

That gap is not incidental. ``P11C``'s gate 3 requires the best hostile
universal threshold to be at least four times the compiled one, the compiled
threshold is 64 in both cells and both protocols, and ``4 x 64 = 256``. So the
gate boundary falls exactly between the two observed values: ``P11C``'s draw
passes it and ``P11E``'s draw would not. ``P11D`` failed the same gate for the
same reason and ``P11E``'s protocol then froze a weaker ``>=2x`` target
"because P11D already ruled out the stronger >=4x-in-both-cells claim".

One run of a frozen protocol cannot settle that, in either direction. This
measures the threshold across many seeds of the same construction and reports
the distribution.

What this is not
----------------
It is not a protocol, it authorizes no terminal, and it does not touch
``P11C``'s. Sweeping seeds *after* an outcome is exactly how a result gets
selected rather than measured, so nothing here may be used to prefer one
terminal over another: the frozen runs stand as they are, and what this adds is
a statement about how much a single draw of this construction is worth. It
measures the instrument, not the compiler.

Scope
-----
Only ``UNIVERSAL_L1`` is swept. The gate reads the earliest threshold reached by
any universal arm, and in both frozen runs ``UNIVERSAL_L2`` never reaches the
target while ``UNIVERSAL_EXTRA_TREES`` reaches it at 2,048 or not at all, so L1
is the binding arm and the one the boundary turns on. Sweeping the other two
would cost far more and move nothing; that this is a proxy is stated rather than
hidden, and the frozen runs' own numbers are what justify it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA_VERSION = "orion.p11.threshold-stability.v1"

#: The frozen P11C runner. Its construction is reused verbatim; only the master
#: seed varies, and only the L1 arm is scored.
FROZEN_RUNNER = (
    "papers/paper-11-state-as-computation/run_p11c_stronger_decoder_attack_v1.py"
)

#: What the two frozen runs observed, so the sweep is compared against them
#: rather than against a memory of them.
FROZEN_OBSERVATIONS: dict[str, dict[str, Any]] = {
    "P11C": {"seed": 2026082111, "l1_threshold": {"(17,4,5)": 256, "(19,3,7)": 256}},
    "P11E": {"seed": 2026082117, "l1_threshold": {"(17,4,5)": 128, "(19,3,7)": 256}},
}

#: The gate boundary: four times the compiled threshold, which is 64 in every
#: frozen run of this construction.
COMPILED_THRESHOLD = 64
GATE_MULTIPLE = 4


def _load_frozen(repo_root: Any) -> Any:
    source = Path(repo_root).resolve() / FROZEN_RUNNER
    spec = importlib.util.spec_from_file_location("p11c_frozen_for_stability", source)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load the frozen runner at {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parity_bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    """The amendment's vectorized bank, elementwise identical to the frozen one."""

    indices = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, indices], axis=2, dtype=np.int8)


def l1_threshold_for_seed(repo_root: Any, seed: int) -> dict[str, int | None]:
    """The ``UNIVERSAL_L1`` threshold in each cell under one master seed.

    The RNG call order is the frozen runner's, so a given seed reproduces that
    runner's query sets and data exactly. Only the arms that are not being
    measured are skipped.
    """

    import itertools

    frozen = _load_frozen(repo_root)
    rng = np.random.default_rng(seed)
    out: dict[str, int | None] = {}

    for d, s, r in frozen.CELLS:
        subsets = list(itertools.combinations(range(d), s))
        n_basis = len(subsets)
        query_sets = [
            [int(i) for i in rng.choice(n_basis, size=r, replace=False)]
            for _ in range(frozen.N_QUERIES)
        ]
        test_x = rng.choice((-1, 1), size=(frozen.N_TEST, d)).astype(np.int8)
        test_bank = _parity_bank(test_x, subsets)
        test_y = []
        for active in query_sets:
            values = test_bank[:, active]
            signed = np.where(values.sum(axis=1) > 0, 1, -1).astype(np.int8)
            test_y.append((signed > 0).astype(np.int8))

        curve: dict[int, float] = {}
        for n in frozen.TRAIN_SIZES:
            train_x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            train_bank = _parity_bank(train_x, subsets)
            scores = []
            for qi, active in enumerate(query_sets):
                y = (train_bank[:, active].sum(axis=1) > 0).astype(np.int8)
                model = frozen.l1()
                model.fit(train_bank, y)
                scores.append(float(model.score(test_bank, test_y[qi])))
            curve[n] = float(np.mean(scores))
        out[f"({d},{s},{r})"] = frozen.threshold(curve)

    return out


def sweep(repo_root: Any, seeds: tuple[int, ...]) -> dict[str, Any]:
    """Measure the L1 threshold across ``seeds`` and report the distribution."""

    from collections import Counter

    per_seed = {str(seed): l1_threshold_for_seed(repo_root, seed) for seed in seeds}
    cells = sorted({cell for row in per_seed.values() for cell in row})

    distribution: dict[str, dict[str, int]] = {}
    gate_passes: dict[str, int] = {}
    for cell in cells:
        values = [per_seed[str(seed)][cell] for seed in seeds]
        distribution[cell] = {
            ("NOT_REACHED" if value is None else str(value)): count
            for value, count in sorted(
                Counter(values).items(), key=lambda item: (item[0] is None, item[0])
            )
        }
        boundary = COMPILED_THRESHOLD * GATE_MULTIPLE
        gate_passes[cell] = sum(1 for value in values if value is None or value >= boundary)

    both_cells = sum(
        1
        for seed in seeds
        if all(
            per_seed[str(seed)][cell] is None
            or per_seed[str(seed)][cell] >= COMPILED_THRESHOLD * GATE_MULTIPLE
            for cell in cells
        )
    )
    return {
        "seeds": list(seeds),
        "per_seed": per_seed,
        "threshold_distribution": distribution,
        "gate_boundary": COMPILED_THRESHOLD * GATE_MULTIPLE,
        "seeds_passing_the_gate_per_cell": gate_passes,
        "seeds_passing_in_both_cells": both_cells,
        "gate_pass_fraction": round(both_cells / len(seeds), 4) if seeds else None,
    }


def build_report(repo_root: Any, *, date: str, seeds: tuple[int, ...]) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    result = sweep(repo_root, seeds)
    unstable = sorted(
        cell
        for cell, counts in result["threshold_distribution"].items()
        if len(counts) > 1
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P11_THRESHOLD_STABILITY",
        "date": date,
        **result,
        "frozen_observations": FROZEN_OBSERVATIONS,
        "cells_whose_threshold_moves": unstable,
        "what_this_establishes": (
            "P11C's gate 3 asks whether the best hostile universal threshold is at least "
            "four times the compiled one. The compiled threshold is 64 in every frozen "
            "run of this construction, so the boundary is 256 exactly -- and the two "
            "frozen runs of the same construction sit on opposite sides of it in cell "
            "(17,4,5): P11E's seed gives 128 and P11C's gives 256. This sweeps the same "
            "construction across many seeds and reports how often each side comes up, so "
            "the boundary is a measured frequency rather than a single draw."
        ),
        "not_licensed": [
            "any change to P11C's terminal, or to P11D's or P11E's; sweeping seeds after "
            "an outcome is how a result gets selected rather than measured, and nothing "
            "here may be used to prefer one terminal over another",
            "any claim about the other two universal arms; only UNIVERSAL_L1 is swept, "
            "because the frozen runs show it is the arm the boundary turns on",
            "any claim about the compiler; this measures how much one draw of this "
            "benchmark is worth, not what the compiler does",
        ],
    }
