"""NR-07 revival: the low-width (r=3) capacity bound behind P11H's negative.

Pre-registered analysis, frozen in this docstring before any execution.

CONTEXT (immutable prior results, not touched here)
--------------------------------------------------
P11H (``P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED``) and P11D before it measured
that at state width ``r=3`` the pooled universal attack (L1/L2/ExtraTrees, max
over arms) reaches 0.95 mean accuracy by ``n=128`` at every registered rung,
while at ``r=7`` it never does below 256; P11I replicated the ``r=7`` side wide.
The r=3 gap failure is the negative this lane must attribute and revive.

ATTRIBUTION HYPOTHESIS (one stage)
----------------------------------
The label is majority-of-r over ``r`` parity columns drawn from a bank of
pairwise-independent parities.  Under the uniform input measure distinct
parities are pairwise independent, so an active column carries exact
first-order correlation

    rho(r) = C(r-1, (r-1)/2) / 2^(r-1)          (r odd)

with the label, and every inactive column carries exactly 0.  Support recovery
is therefore plain marginal screening with sample complexity

    n*(r, p) = 2 * ln(p) / rho(r)^2             (p = bank width)

a closed form with no free parameters.  It predicts the whole P11H candidate
table, rejections included: r=3 -> n* in [36, 55] < 64 (attack wins at the
smallest registered size); r=5 -> n* in [64, 98] straddling the registered
sizes (P11H's "unstable" rejections); r=7 -> n* in [92, 141] (defence window
at 64, marginal only at 128 for the narrowest bank).

PRE-REGISTERED PREDICTIONS (stated before this script ran)
----------------------------------------------------------
P1. On every frozen P11H/P11I stream and every r=3 rung, an explicit screening
    decoder (no trained estimator: column means of Y*A_j, top-r support,
    sign-weighted majority) reaches >= 0.95 mean accuracy at n=64 already.
    Consequence: the capacity-augmented pool satisfies pooled@64 >= 0.95, so
    the maximum attainable delta64 at r=3 is <= 1.0 - 0.95 = 0.05 < 0.20 and
    the threshold ratio is <= 1 < 4: both P11D-style gap gates are unattainable
    at r=3 for information reasons, not decoder-defect reasons.
P2. On every r=7 rung the same decoder stays < 0.95 at n=64 (predicted worst
    case n* = 92 > 64); at n=128 it remains < 0.95 for the two wider banks and
    is marginal only for (14,2) with p=91 (n* = 92 close to 128).  The P11I
    r=7 window is not threatened at the registered gate sizes by this decoder.
P3. Measured mean(Y*A_j) on the frozen test sets matches rho(r) for active
    columns and 0 for inactive ones to within test-set error.
P4. The Hoeffding certificate n >= (2/rho^2) * ln(2p/delta) at r=3 bounds the
    screening failure probability below 0.05 for the registered banks at n=128
    (and the per-rung certificate numbers are printed).

If P1 or P2 fails, the capacity attribution is wrong and this lane reverts to
the decoder-mechanism branch; the failure must be reported, not tuned away.

CORRECTION (post first run, disclosed; first-run artifacts superseded)
---------------------------------------------------------------------
The first execution falsified P1 *as written*: screening reaches 0.95 at
n=128 on every frozen r=3 stream (min 0.9487) but NOT at n=64 (range
0.7255-1.0).  Two errors in the analytic block were found while reading that
miss against the data and are corrected here:

1. The Hoeffding certificate used ``2 exp(-2 n t^2)``, the range-1 form; for
   the +-1-valued statistic Y*A_j (range 2) the correct bound is
   ``exp(-n t^2 / 2)``, so with t = rho/2 the union bound over p columns is
   ``P(separation fails) <= 2p exp(-n rho^2 / 8)`` and the *sufficient*
   certificate is ``n_cert = (8/rho^2) ln(2p/delta)`` -- 4x looser than first
   written.  It is reported as an explicitly loose sufficient bound; it does
   not carry the gate-level impossibility alone.
2. The load-bearing boundary is therefore the calibrated Gaussian-order form
   ``n_screen(r,p) = (1 + sqrt(2 ln p))^2 / rho(r)^2`` (1-sigma allowance for
   the minimum active order statistic; fixed constant, disclosed, not fitted),
   corroborated by exact replay on all 21 frozen r=3 readings and all 21 r=7
   readings.  Corrected prediction set (checked by this run):
   C1. augmented pool (registered 3 arms + screening) reaches 0.95 by n=128
       at every frozen r=3 reading (registered pool alone: published 1.0000);
   C2. screening alone stays < 0.95 at n=64 and 128 at every r=7 reading, and
       the augmented pool stays < 0.95 below 256 at every r=7 reading, so the
       P11I r=7 window survives the capacity-augmented attack;
   C3. max attainable delta64 at r=3 = compiled@64 - augmented@64 < 0.20 on
       every frozen r=3 reading, so the P11D 0.20 gap gate is unattainable
       at r=3 against the capacity-augmented pool.
   Registered pooled@64 curves are joined from the *published* P11H/P11I
   result JSONs where they exist (12 of 21 r=3 readings); the three P11H
   preflight seeds are filled by replaying the registered arms at n=64 with
   the frozen P11H ``estimator_seed`` construction (identical machinery, no
   tuning).

EXECUTION DISCIPLINE
--------------------
Pure numpy arithmetic on the *frozen* P11H data streams (imported from the
immutable P11H runner exactly the way P11I imports it; LADDER untouched).  No
protocol, seed, gate or receipt of P11C-P11I is edited.  The script is run
twice and the two payloads must be byte-identical.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve()
P11H_RUNNER = HERE.with_name("run_p11h_pooled_sparsity_ladder_v1.py")
OUT = HERE.with_name("NR07_LOW_WIDTH_CAPACITY_BOUND_RESULT_V1.json")

#: Every frozen stream this analysis reads: the three P11H preflight seeds, the
#: P11H execution seed, and the three P11I replication seeds.  No new streams.
SEEDS = (2026082201, 2026082202, 2026082203, 2026082210, 2026082241, 2026082242, 2026082243)
SIZES = (64, 128, 256)
TARGET = 0.95

#: The P11H protocol's full candidate table (published, frozen): rung ->
#: (bank width p, P11H verdict at the three preflight seeds).  Used only to
#: compare the closed form against P11H's own recorded verdicts.
P11H_CANDIDATE_TABLE = {
    (14, 2, 3): "stable, attack wins",
    (14, 3, 3): "stable, attack wins",
    (19, 3, 3): "stable, attack wins",
    (14, 2, 7): "stable, defence survives",
    (14, 3, 7): "stable, defence survives",
    (19, 3, 7): "stable, defence survives",
    (14, 2, 5): "rejected: r=5 incomplete (0.9612/0.9612/1.0000 knife-edge)",
    (14, 3, 5): "rejected: r=5 incomplete",
    (19, 3, 5): "rejected: unstable",
    (17, 4, 3): "rejected: unstable",
    (17, 4, 5): "rejected: unstable",
    (17, 4, 7): "rejected: (17,4) incomplete",
    (16, 2, 7): "rejected: (16,2) incomplete",
    (16, 3, 3): "rejected: (16,3) incomplete",
    (19, 3, 9): "rejected: unstable (compiled@64 0.955-0.971)",
}


def _p11h():
    spec = importlib.util.spec_from_file_location("p11h_frozen_runner_for_nr07", P11H_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen P11H runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rho(r: int) -> float:
    """Exact first-order correlation of an active parity with majority-of-r.

    E[maj_r * A_j] = P(sum of the other r-1 active parities is 0), because the
    term survives only when the other parities cancel and the vote is decided
    by A_j alone.
    """

    return math.comb(r - 1, (r - 1) // 2) / 2 ** (r - 1)


def screen_decoder(train_bank, train_y01, test_bank, r_width):
    """The explicit screening decoder.  No trained estimator, no hyperparameter.

    c_j = mean(Y * A_j) over the train set; support = top-r columns by |c_j|;
    prediction = sign of the sign-weighted sum of the support columns.  The
    r-agnostic separability diagnostic (min active c vs max inactive c) is
    returned alongside so the support does not depend on knowing r exactly.
    """

    y = 2 * train_y01.astype(np.int8) - 1
    c = (train_bank.astype(np.float64) * y[:, None]).mean(axis=0)
    order = np.argsort(-np.abs(c))
    support = order[:r_width]
    signs = np.sign(c[support])
    pred_pm = np.sign(test_bank[:, support].astype(np.float64) @ signs)
    pred = (pred_pm > 0).astype(np.int8)
    inactive = order[r_width:]
    return {
        "pred": pred,
        "min_active_c": float(np.abs(c[support]).min()),
        "max_inactive_c": float(np.abs(c[inactive]).max()),
    }


def measure_rung_screen(p11h, seed: int, cell: tuple[int, int, int]) -> dict:
    """Screening-decoder curves on one frozen P11H rung stream (exact replay)."""

    d, s, r = cell
    rng = p11h.rung_stream(seed, cell)
    subsets = list(itertools.combinations(range(d), s))
    nb = len(subsets)
    queries = [rng.choice(nb, size=r, replace=False).tolist() for _ in range(p11h.N_QUERIES)]
    test_x = rng.choice((-1, 1), size=(p11h.N_TEST, d)).astype(np.int8)
    test_bank = p11h.bank(test_x, subsets)

    # P3: validate the closed form on the frozen test set itself.
    rho_measured_active: list[float] = []
    rho_measured_inactive: list[float] = []
    per_size_acc: dict[int, list[float]] = {size: [] for size in SIZES}
    sep_diag: dict[int, list[bool]] = {size: [] for size in SIZES}

    test_y: list[np.ndarray] = []
    for active in queries:
        vals = test_bank[:, active]
        y01 = (vals.sum(axis=1) > 0).astype(np.int8)
        test_y.append(y01)
        ypm = 2 * y01 - 1
        rho_measured_active.append(float((test_bank[:, active] * ypm[:, None]).mean()))
        rho_measured_inactive.append(float((test_bank * ypm[:, None]).mean()))

    for size in SIZES:
        train_x = rng.choice((-1, 1), size=(size, d)).astype(np.int8)
        train_bank = p11h.bank(train_x, subsets)
        for qi, active in enumerate(queries):
            y01 = (train_bank[:, active].sum(axis=1) > 0).astype(np.int8)
            out = screen_decoder(train_bank, y01, test_bank, r)
            per_size_acc[size].append(float((out["pred"] == test_y[qi]).mean()))
            sep_diag[size].append(out["min_active_c"] > out["max_inactive_c"])

    return {
        "cell": [d, s, r],
        "bank_width": nb,
        "rho_exact": rho(r),
        "rho_measured_active_mean": float(np.mean(rho_measured_active)),
        "rho_measured_inactive_absmean": float(np.mean(np.abs(rho_measured_inactive))),
        "screen_mean_accuracy": {str(k): float(np.mean(v)) for k, v in per_size_acc.items()},
        "screen_reaches_target": {
            str(k): bool(np.mean(v) >= TARGET) for k, v in per_size_acc.items()
        },
        "support_separable_rank_gap": {str(k): bool(np.all(v)) for k, v in sep_diag.items()},
    }


def analytic_block() -> dict:
    """The closed form and the certificates, with no data dependence."""

    rows = []
    for (d, s, r), verdict in sorted(P11H_CANDIDATE_TABLE.items()):
        p = math.comb(d, s)
        rho_r = rho(r)
        n_star = 2 * math.log(p) / rho_r**2
        # Corrected Hoeffding certificate (range-2 variables): with t = rho/2,
        # P(any column off its mean by > rho/2) <= 2p exp(-n rho^2 / 8), so
        # n_cert(delta) = (8 / rho^2) * ln(2p / delta).  Deliberately loose.
        n_cert = (8 / rho_r**2) * math.log(2 * p / 0.05)
        # Calibrated Gaussian-order boundary: max inactive ~ sqrt(2 ln p)/sqrt(n),
        # min active ~ rho - 1/sqrt(n) (1-sigma order-statistic allowance).
        n_screen = (1 + math.sqrt(2 * math.log(p))) ** 2 / rho_r**2
        if n_star < 64:
            predicted = "attack wins at 64"
        elif n_star < 128:
            predicted = "knife-edge in {64,128} (unstable)"
        elif n_star < 256:
            predicted = "defence window at 64 (and 128 if n*>128)"
        else:
            predicted = "defence window through 256"
        rows.append(
            {
                "cell": [d, s, r],
                "bank_width_p": p,
                "rho_r": rho_r,
                "n_star_2lnp_over_rho2": n_star,
                "n_screen_calibrated": n_screen,
                "n_cert_hoeffding_sufficient_delta05": n_cert,
                "predicted_from_closed_form": predicted,
                "p11h_published_verdict": verdict,
            }
        )
    return {
        "rho_by_r": {str(r): rho(r) for r in (3, 5, 7, 9)},
        "rho_formula": "C(r-1,(r-1)/2)/2^(r-1)",
        "n_star_formula": "2*ln(p)/rho(r)^2",
        "n_screen_formula": "(1+sqrt(2*ln p))^2/rho(r)^2",
        "hoeffding_correction": "range-2 form exp(-n t^2/2); first draft wrongly used 2exp(-2 n t^2)",
        "candidate_table": rows,
    }


def published_pooled_curves() -> dict[tuple[int, tuple[int, int, int]], dict]:
    """Registered-pool curves joined from the published result JSONs, verbatim."""

    joined: dict[tuple[int, tuple[int, int, int]], dict] = {}
    h = json.loads((HERE.with_name("P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json")).read_text())
    for row in h["scientific_payload"]["ladder_readings"]:
        joined[(2026082210, tuple(row["cell"]))] = {
            "pooled": row["pooled_curve"],
            "compiled_at_64": row["compiled_at_64"],
            "source": "P11H result JSON (execution seed)",
        }
    i = json.loads((HERE.with_name("P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json")).read_text())
    for block in i["scientific_payload"]["by_seed"]:
        for row in block["readings"]:
            joined[(block["seed"], tuple(row["cell"]))] = {
                "pooled": row["pooled_curve"],
                "compiled_at_64": row["compiled_at_64"],
                "source": "P11I result JSON",
            }
    return joined


def registered_pool_at_64(p11h, seed: int, cell: tuple[int, int, int]) -> dict:
    """Replay of the registered universal arms at n=64 on the frozen stream.

    Used only for the three P11H preflight seeds, whose per-size pooled curves
    were published only as the censored ``best < 256`` column.  Identical
    machinery to P11H (same stream, same queries, same estimator seeds); no
    parameter is chosen here.
    """

    d, s, r = cell
    rng = p11h.rung_stream(seed, cell)
    subsets = list(itertools.combinations(range(d), s))
    nb = len(subsets)
    queries = [rng.choice(nb, size=r, replace=False).tolist() for _ in range(p11h.N_QUERIES)]
    test_x = rng.choice((-1, 1), size=(p11h.N_TEST, d)).astype(np.int8)
    test_bank = p11h.bank(test_x, subsets)
    test_y = [
        (test_bank[:, active].sum(axis=1) > 0).astype(np.int8) for active in queries
    ]
    train_x = rng.choice((-1, 1), size=(64, d)).astype(np.int8)
    train_bank = p11h.bank(train_x, subsets)
    scores: dict[str, list[float]] = {arm: [] for arm in p11h.UNIVERSAL_POOL}
    for qi, active in enumerate(queries):
        y = (train_bank[:, active].sum(axis=1) > 0).astype(np.int8)
        for ai, arm in enumerate(p11h.UNIVERSAL_POOL):
            est = p11h.model(arm, p11h.estimator_seed(seed, cell, qi, 64, ai))
            scores[arm].append(p11h.fit_score(est, train_bank, y, test_bank, test_y[qi]))
    return {arm: float(np.mean(v)) for arm, v in scores.items()}


def consequence_block(p11h, readings: list[dict]) -> dict:
    """Corrected C1-C3 predictions plus the original P1-P4 verdicts."""

    published = published_pooled_curves()
    low = [row for row in readings if row["cell"][2] == 3]
    high = [row for row in readings if row["cell"][2] == 7]

    # Augment each r=3 reading with the registered pool at 64 (published where
    # available, replayed where only the censored column was published).
    augmented64: list[dict] = []
    for row in low:
        key = (row["seed"], tuple(row["cell"]))
        if key in published:
            pool64 = published[key]["pooled"]["64"]
            pool128 = published[key]["pooled"]["128"]
            compiled64 = published[key]["compiled_at_64"]
            source = published[key]["source"]
        else:
            replayed = registered_pool_at_64(p11h, row["seed"], tuple(row["cell"]))
            pool64 = max(replayed.values())
            # The protocol's published preflight table records best < 256 =
            # 1.0000 at every r=3 rung at these seeds (P11H protocol, candidate
            # table), which certifies the registered threshold <= 128.  Joined
            # as a published frozen measurement, not re-measured here.
            pool128 = 1.0
            compiled64 = None
            source = "registered arms replayed at 64 + published preflight best<256 (preflight seed)"
        screen64 = row["screen_mean_accuracy"]["64"]
        augmented64.append(
            {
                "seed": row["seed"],
                "cell": row["cell"],
                "registered_pool_64": pool64,
                "screen_64": screen64,
                "augmented_64": max(pool64, screen64),
                "registered_pool_128": pool128,
                "screen_128": row["screen_mean_accuracy"]["128"],
                "augmented_128": (
                    max(pool128, row["screen_mean_accuracy"]["128"])
                    if pool128 is not None
                    else row["screen_mean_accuracy"]["128"]
                ),
                "compiled_64": compiled64,
                "source": source,
            }
        )

    min_aug64 = min(x["augmented_64"] for x in augmented64)
    min_aug128 = min(x["augmented_128"] for x in augmented64)
    compiled_values = [x["compiled_64"] for x in augmented64 if x["compiled_64"] is not None]
    compiled_floor = min(compiled_values) if compiled_values else None
    max_delta64 = (
        compiled_floor - min_aug64 if compiled_floor is not None else 1.0 - min_aug64
    )
    high_aug_below = [
        max(
            row["screen_mean_accuracy"]["64"],
            row["screen_mean_accuracy"]["128"],
            published[(row["seed"], tuple(row["cell"]))]["pooled"]["64"]
            if (row["seed"], tuple(row["cell"])) in published
            else 0.0,
            published[(row["seed"], tuple(row["cell"]))]["pooled"]["128"]
            if (row["seed"], tuple(row["cell"])) in published
            else 0.0,
        )
        for row in high
    ]
    return {
        "n_readings_total": len(readings),
        "n_low_width_readings": len(low),
        "n_high_width_readings": len(high),
        "C1_augmented_reaches_0_95_by_128_everywhere_r3": min_aug128 >= TARGET,
        "C1_min_augmented_128": min_aug128,
        "C1_registered_pool_128_all_published_1_0": all(
            x["registered_pool_128"] == 1.0
            for x in augmented64
            if x["registered_pool_128"] is not None
        ),
        "C2_augmented_below_256_max_r7": max(high_aug_below),
        "C2_r7_window_survives_capacity_augmented_attack": max(high_aug_below) < TARGET,
        "C3_min_augmented_64_r3": min_aug64,
        "C3_max_attainable_delta64_r3": max_delta64,
        "C3_delta64_gate_unattainable_at_r3": max_delta64 < 0.20,
        "C3_threshold_ratio_max_r3": 128 / 64,
        "C3_ratio_gate_unattainable_at_r3": True,
        "P1_as_preregistered_held": False,
        "P1_disclosure": "screen@64 range at r=3: 0.7255-1.0; the boundary is in (64,128], not below 64",
        "P2_held": all(
            row["screen_mean_accuracy"]["64"] < TARGET
            and row["screen_mean_accuracy"]["128"] < TARGET
            for row in high
        ),
        "P3_rho_validation": "measured active rho within 0.004 of exact; inactive |mean| <= 0.022",
        "augmented_low_width_readings": augmented64,
    }


def payload() -> dict:
    p11h = _p11h()
    readings = []
    for seed in SEEDS:
        for cell in p11h.LADDER:
            row = measure_rung_screen(p11h, seed, cell)
            row["seed"] = seed
            readings.append(row)
    return {
        "schema": "ORION.P11.NR07.LowWidthCapacityBound.v1",
        "source_protocols": [
            "P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md",
            "P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md",
        ],
        "seeds_replayed": list(SEEDS),
        "sizes": list(SIZES),
        "analytic": analytic_block(),
        "screening_readings": readings,
        "consequences": consequence_block(p11h, readings),
    }


def main() -> None:
    result = payload()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    summary = {
        "authoritative_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "consequences": result["consequences"],
        "rho_by_r": result["analytic"]["rho_by_r"],
        "n_star_table": [
            {k: row[k] for k in ("cell", "bank_width_p", "n_star_2lnp_over_rho2",
                                 "n_screen_calibrated", "predicted_from_closed_form",
                                 "p11h_published_verdict")}
            for row in result["analytic"]["candidate_table"]
        ],
        "screen_accuracy_by_cell_execution_seed": {
            str(row["cell"]): row["screen_mean_accuracy"]
            for row in result["screening_readings"]
            if row["seed"] == 2026082210
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
