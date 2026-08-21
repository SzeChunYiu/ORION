"""ORION-Q N2-F3: partial-evidence route selection with typed QUERY / CANNOT_COMPARE.

Executes successor family 3 of issue #675 exactly as frozen in
development/orion-q-nlane-closure/N2_F3_PROTOCOL.md (protocol frozen before outcomes).

Exact-synthetic scope only: stripped QSVT route proxies, interval evidence on
constants, Pareto/typed decisions scored against hidden context weights.
Not a compiled resource estimator; no authority beyond this frozen world.
"""

from __future__ import annotations

import json
import math
import os

import numpy as np

SEED = 20260821
QUERY_PRICE = 0.02
W_VERTICES = ((1.0, 0.0, 0.0), (0.5, 0.5, 0.0), (0.5, 0.0, 0.5))
W_CENTROID = tuple(sum(v[i] for v in W_VERTICES) / 3.0 for i in range(3))
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "N2_F3_PARTIAL_EVIDENCE_RESULTS.json")


def fvec(route: str, c: float, L: int, lam: float, d: float) -> tuple[float, float, float]:
    """Transformed resource vector f_c = log10(1 + resource_c)."""
    if route == "S":
        q = c * L * lam * d
        a = math.floor(math.log2(L)) + 2
        p = float(L)
    else:
        q = c * (lam * d) ** 2
        a = 1.0
        p = 0.0
    return (math.log10(1.0 + q), math.log10(1.0 + a), math.log10(1.0 + p))


def dot(w, f) -> float:
    return w[0] * f[0] + w[1] * f[1] + w[2] * f[2]


def dominates_over_W(f_x_worst, f_y_best) -> bool:
    """X certainly no worse than Y for every w in W (checked at vertices)."""
    return all(dot(w, f_x_worst) - dot(w, f_y_best) <= 0.0 for w in W_VERTICES)


def make_instances(rng: np.random.Generator, n: int, adversarial: bool) -> list[dict]:
    out = []
    for _ in range(n):
        if adversarial:
            L = 2
            d = 256
            lam = float(rng.uniform(2.0, 3.0))
            rho = 2.5
        else:
            L = int(rng.choice([4, 8, 16, 32, 64, 128]))
            lam = float(10.0 ** rng.uniform(-0.3, 0.9))
            d = int(rng.choice([4, 8, 16, 32, 64, 128]))
            rho = 1.05 if rng.uniform() < 0.5 else 2.5
        c_std = float(rng.uniform(0.5, 2.0))
        c_rnd = float(rng.uniform(0.5, 2.0))
        u_s, u_r = float(rng.uniform()), float(rng.uniform())
        std_lo = c_std * rho ** (-u_s)
        rnd_lo = c_rnd * rho ** (-u_r)
        # true weight, uniform over W (revealed only at scoring)
        w_q = float(rng.uniform(0.5, 1.0))
        t = float(rng.uniform())
        w = (w_q, (1.0 - w_q) * t, (1.0 - w_q) * (1.0 - t))
        out.append({
            "L": L, "lam": lam, "d": d,
            "c_std": c_std, "c_rnd": c_rnd,
            "std_iv": (std_lo, std_lo * rho), "rnd_iv": (rnd_lo, rnd_lo * rho),
            "w_true": w,
        })
    return out


def regret(inst: dict, route: str) -> float:
    w = inst["w_true"]
    cs = dot(w, fvec("S", inst["c_std"], inst["L"], inst["lam"], inst["d"]))
    cr = dot(w, fvec("R", inst["c_rnd"], inst["L"], inst["lam"], inst["d"]))
    best = min(cs, cr)
    return (cs if route == "S" else cr) - best


def loss_of(decision, inst: dict) -> float:
    kind, payload, price = decision
    if kind == "point":
        return regret(inst, payload) + price
    return 0.5 * (regret(inst, "S") + regret(inst, "R")) + price  # set answer


def orion_decide(inst: dict) -> tuple[str, object, float]:
    L, lam, d = inst["L"], inst["lam"], inst["d"]
    s_lo, s_hi = inst["std_iv"]
    r_lo, r_hi = inst["rnd_iv"]

    def dom(x_c, y_c, x_route, y_route) -> bool:
        return dominates_over_W(fvec(x_route, x_c, L, lam, d), fvec(y_route, y_c, L, lam, d))

    if dom(s_hi, r_lo, "S", "R"):
        return ("point", "S", 0.0)
    if dom(r_hi, s_lo, "R", "S"):
        return ("point", "R", 0.0)
    pivotal = dom(s_lo, r_hi, "S", "R") or dom(r_lo, s_hi, "R", "S")
    if pivotal:
        cs, cr = inst["c_std"], inst["c_rnd"]  # QUERY reveals exact constants
        if dom(cs, cr, "S", "R"):
            return ("point", "S", QUERY_PRICE)
        if dom(cr, cs, "R", "S"):
            return ("point", "R", QUERY_PRICE)
        return ("set", ("S", "R"), QUERY_PRICE)
    return ("set", ("S", "R"), 0.0)


def b1_midpoint(inst: dict) -> tuple[str, object, float]:
    L, lam, d = inst["L"], inst["lam"], inst["d"]
    cs = dot(W_CENTROID, fvec("S", 0.5 * sum(inst["std_iv"]), L, lam, d))
    cr = dot(W_CENTROID, fvec("R", 0.5 * sum(inst["rnd_iv"]), L, lam, d))
    return ("point", "S" if cs <= cr else "R", 0.0)


def b2_minimax(inst: dict) -> tuple[str, object, float]:
    L, lam, d = inst["L"], inst["lam"], inst["d"]
    ub_s = max(dot(w, fvec("S", inst["std_iv"][1], L, lam, d)) for w in W_VERTICES)
    ub_r = max(dot(w, fvec("R", inst["rnd_iv"][1], L, lam, d)) for w in W_VERTICES)
    return ("point", "S" if ub_s <= ub_r else "R", 0.0)


def b3_always_query(inst: dict) -> tuple[str, object, float]:
    L, lam, d = inst["L"], inst["lam"], inst["d"]
    cs = dot(W_CENTROID, fvec("S", inst["c_std"], L, lam, d))
    cr = dot(W_CENTROID, fvec("R", inst["c_rnd"], L, lam, d))
    return ("point", "S" if cs <= cr else "R", QUERY_PRICE)


def lazy(inst: dict) -> tuple[str, object, float]:
    return ("set", ("S", "R"), 0.0)


ARMS = {
    "orion_typed": orion_decide,
    "b1_scalarized_midpoint": b1_midpoint,
    "b2_minimax_always_answer": b2_minimax,
    "b3_always_query_scalarize": b3_always_query,
    "lazy_abstainer": lazy,
}


def eval_world(instances: list[dict]) -> dict:
    out = {}
    for name, fn in ARMS.items():
        losses, queries, abstains = [], 0, 0
        for inst in instances:
            dec = fn(inst)
            losses.append(loss_of(dec, inst))
            if dec[2] > 0:
                queries += 1
            if dec[0] == "set":
                abstains += 1
        out[name] = {
            "mean_loss": float(np.mean(losses)),
            "max_loss": float(np.max(losses)),
            "query_rate": queries / len(instances),
            "abstain_rate": abstains / len(instances),
        }
    out["oracle"] = {"mean_loss": 0.0, "max_loss": 0.0, "query_rate": 0.0, "abstain_rate": 0.0}
    return out


def pipeline() -> dict:
    rng = np.random.default_rng(SEED)
    primary = make_instances(rng, 400, adversarial=False)
    rng_adv = np.random.default_rng(SEED + 1)
    adv = make_instances(rng_adv, 100, adversarial=True)

    res_primary = eval_world(primary)
    res_adv = eval_world(adv)

    baselines = ["b1_scalarized_midpoint", "b2_minimax_always_answer", "b3_always_query_scalarize"]
    best_baseline = min(res_primary[b]["mean_loss"] for b in baselines)
    orion_primary = res_primary["orion_typed"]["mean_loss"]
    orion_adv = res_adv["orion_typed"]

    gates = {
        "F3_G2_hostile_decidable": (
            orion_adv["query_rate"] == 0.0
            and orion_adv["abstain_rate"] == 0.0
            and orion_adv["mean_loss"] <= 1e-12
        ),
        "F3_G3_lazy_punished": (
            res_adv["lazy_abstainer"]["mean_loss"] >= orion_adv["mean_loss"] + 0.05
        ),
        "F3_G4_oracle_bound": all(
            res[a]["mean_loss"] >= -1e-12
            for res in (res_primary, res_adv) for a in res
        ),
        "F3_G5_residual": orion_primary <= 0.99 * best_baseline,
    }
    return {
        "schema": "ORIONQ.N2F3PartialEvidenceResult.v1",
        "issue": "SzeChunYiu/ORION#675",
        "family": "successor_family_3_partial_evidence",
        "protocol": "development/orion-q-nlane-closure/N2_F3_PROTOCOL.md",
        "seed": SEED,
        "query_price": QUERY_PRICE,
        "n_primary": len(primary),
        "n_adversarial": len(adv),
        "arms_primary": res_primary,
        "arms_adversarial": res_adv,
        "best_baseline_primary_mean_loss": best_baseline,
        "orion_primary_mean_loss": orion_primary,
        "orion_vs_best_baseline_ratio": orion_primary / best_baseline if best_baseline > 0 else None,
        "gates": gates,
        "authority": "exact_synthetic_frozen_world_only; not compiled-resource, hardware, or novelty authority",
        "claim_boundary": (
            "Residual (or its absence) holds only for the frozen stripped route proxies, "
            "interval evidence model, weight polytope W and scoring of N2_F3_PROTOCOL.md; "
            "no LOWER_BOUND claim."
        ),
    }


def main() -> None:
    r1 = pipeline()
    r2 = pipeline()
    s1 = json.dumps(r1, sort_keys=True)
    deterministic = s1 == json.dumps(r2, sort_keys=True)
    r1["gates"]["F3_G1_determinism"] = deterministic
    hostile_ok = all(r1["gates"][g] for g in (
        "F3_G1_determinism", "F3_G2_hostile_decidable", "F3_G3_lazy_punished", "F3_G4_oracle_bound"))
    if not hostile_ok:
        terminal = "N2_F3_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED"
    elif r1["gates"]["F3_G5_residual"]:
        terminal = "N2_F3_PARTIAL_EVIDENCE_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY"
    else:
        terminal = "N2_F3_PARTIAL_EVIDENCE_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY"
    r1["terminal"] = terminal
    with open(RESULTS_PATH, "w") as fh:
        json.dump(r1, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N2_F3_PARTIAL_EVIDENCE=" + json.dumps(r1, sort_keys=True))


if __name__ == "__main__":
    main()
