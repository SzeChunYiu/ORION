#!/usr/bin/env python3
"""ORION-02 successor: outcome driver for asymptotics-kmin-v1 (protocol:
PROTOCOL_KMIN_ASYMPTOTICS.md, committed before this pass).

Single certified pass: P1 validation gate (m=5..48 vs frozen float harness),
fresh exact law table m=49..140, registered law checks P2 + L1..L4, JSON
receipt (schema ORION02.KMIN_ASYM.v1) + logs. Exit 0 KMIN_ASYM_DETERMINED /
1 KMIN_ASYM_LAW_REFUTED / 3 validation fail.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / ".."))

import kmin_asymptotics_v1 as ka  # noqa: E402
import verify_c2c10_profile as harness  # noqa: E402

VALIDATE_LO, VALIDATE_HI = 5, 48
LAW_LO, LAW_HI = 49, 140


def main() -> int:
    # ---- P1: validation gate ----
    p1_rows, p1_ok = [], True
    for m in range(VALIDATE_LO, VALIDATE_HI + 1):
        want, _ = harness.kmin_profile(m, 1)
        got, _ = ka.kmin_dp(m)
        row_ok = got == want
        p1_ok = p1_ok and row_ok
        p1_rows.append({"m": m, "dp": got, "harness": want, "ok": row_ok})
        print(f"P1 m={m:3d}: dp={got} harness={want:.0f} "
              f"{'OK' if row_ok else 'MISMATCH'}", flush=True)
    print(f"P1 {'PASS' if p1_ok else 'FAIL'} ({sum(r['ok'] for r in p1_rows)}/"
          f"{len(p1_rows)} match)", flush=True)
    if not p1_ok:
        out = {"schema": "ORION02.KMIN_ASYM.v1", "p1": {"pass": False,
               "rows": p1_rows}, "terminal": "KMIN_ASYM_VALIDATE_FAIL",
               "environment": {"python": platform.python_version(),
                               "node": platform.node()}}
        (HERE / "RESULTS_KMIN_ASYMPTOTICS_V1.json").write_text(
            json.dumps(out, indent=2, sort_keys=True) + "\n")
        return 3

    # ---- fresh law table ----
    table = []
    for m in range(LAW_LO, LAW_HI + 1):
        got, prof = ka.kmin_dp(m)
        g = ka.gamma(m, got)
        b = ka.bf(m)
        table.append({"m": m, "b": b, "kmin": got, "gamma": g,
                      "gamma_over_2b": g / (1 << b), "profile": prof})
        print(f"LAW m={m:4d} b={b} Kmin={got} gamma*={g:.6f} "
              f"gamma/2^b={g / (1 << b):.5f} prof={prof}", flush=True)

    by_m = {r["m"]: r for r in table}
    g128, g129 = by_m[128]["gamma"], by_m[129]["gamma"]

    # ---- registered law checks ----
    checks = {}
    checks["P2_exponential_not_linear"] = {
        "claim": "gamma*(129) in (14,20), closer to 2^(b-4)=16 than 4b-20=12",
        "gamma_129": g129, "exp_prediction": 16.0, "lin_prediction": 12.0,
        "pass": 14.0 < g129 < 20.0 and abs(g129 - 16.0) < abs(g129 - 12.0)}
    checks["L1_band_jump"] = {
        "claim": "gamma*(129)/gamma*(128) in (1.5, 2.2)",
        "ratio": g129 / g128, "pass": 1.5 < g129 / g128 < 2.2}
    l2 = all(r["gamma"] / (1 << (r["b"] - 4)) <= 1.35
             and r["gamma"] > (1 << (r["b"] - 4)) - 1e-12
             for r in table if r["m"] >= 65)
    checks["L2_band_interior"] = {
        "claim": "for m in [65,140]: gamma* in 2^(b-4)*(1, 1.35]",
        "min_ratio": min(r["gamma"] / (1 << (r["b"] - 4))
                         for r in table if r["m"] >= 65),
        "max_ratio": max(r["gamma"] / (1 << (r["b"] - 4))
                         for r in table if r["m"] >= 65),
        "pass": l2}
    l3 = True
    for r in table:
        if r["m"] < 65:
            continue
        b = r["b"]
        blocks = list(r["profile"][0]) + [r["profile"][1]]
        if max(blocks) not in (1 << (b - 3), 1 << (b - 2)):
            l3 = False
        if r["profile"][1] > (1 << (b - 3)):
            l3 = False
    checks["L3_profile_family"] = {
        "claim": "argmax max-block in {2^(b-3), 2^(b-2)} and anchor <= 2^(b-3)",
        "pass": l3}
    eps = [(r["m"], r["gamma"] / (1 << (r["b"] - 4)) - 1.0)
           for r in table if r["m"] >= 49]
    checks["L4_eps_envelope"] = {
        "claim": "eps(m) in [0, 0.25] for m in [49,140]",
        "min": min(e for _, e in eps), "max": max(e for _, e in eps),
        "pass": all(0.0 <= e <= 0.25 for _, e in eps)}

    n_fail = sum(1 for c in checks.values() if not c["pass"])
    p2_fail = not checks["P2_exponential_not_linear"]["pass"]
    if p2_fail or n_fail >= 2:
        terminal, rc = "KMIN_ASYM_LAW_REFUTED", 1
    else:
        terminal, rc = "KMIN_ASYM_DETERMINED", 0

    out = {"schema": "ORION02.KMIN_ASYM.v1",
           "design": {"validate": [VALIDATE_LO, VALIDATE_HI],
                      "law": [LAW_LO, LAW_HI], "L": 1},
           "p1": {"pass": True, "n_match": len(p1_rows)},
           "law_checks": checks, "table": table, "terminal": terminal,
           "environment": {"python": platform.python_version(),
                           "node": platform.node()}}
    (HERE / "RESULTS_KMIN_ASYMPTOTICS_V1.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v["pass"] for k, v in checks.items()}, indent=2))
    print(f"TERMINAL {terminal}", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
