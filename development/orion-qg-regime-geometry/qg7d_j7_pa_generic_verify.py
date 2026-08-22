#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-7d J7 PA closure.

Rebuilds phase-free Pauli multiplication/F3, the complete PA G1-G4 parent
transition domain, J6, and the two-coordinate B' grammar without importing
QG-7c/J6/QG-5b production helpers.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg7d-j7-pa-confirm.json"
PARENT = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG7D_J7_PA_CONFIRMATORY_PROTOCOL_V1.md"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg7d-j7-pa-generic-verification.json"
TOKEN = "ORIONQG_QG7D_J7_GENERIC="
PARENT_DIGEST = "0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
POSITIVE = "QG7D_PA_PINNED_COMM_S2_CLOSED_ALL_N_MACHINE_CHECKED__PP_CHAIN_OPEN"
X, Z = 1, 3


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = {k: v for k, v in raw.items() if k != "result_digest"}
    return raw.get("result_digest") == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def lmul(a: int, b: int) -> int:
    if a == 0:
        return b
    if b == 0:
        return a
    if a == b:
        return 0
    return 6 - a - b


def lsy(a: int, b: int) -> int:
    return int(a != 0 and b != 0 and a != b)


def f3(a: int, b: int, c: int) -> int:
    return 1 if a == b == c != 0 else int(a != 0) + int(b != 0) + int(c != 0)


LM = np.array([[lmul(a, b) for b in range(4)] for a in range(4)], dtype=np.int8)
F3 = np.array([[[f3(a, b, c) for c in range(4)] for b in range(4)] for a in range(4)], dtype=np.int8)
F3E = np.array([[f3(a, u, v) for u in range(4) for v in range(4)] for a in range(4)], dtype=np.int8)
F3T = np.array([[[f3(a, b, e) for e in range(4)] for b in range(4)] for a in range(4)], dtype=np.int8)


def parent_pa_cell(ja: int, rb: int, ra: int, p: int):
    t4 = np.arange(4, dtype=np.int64)
    t0b = np.repeat(t4, 16)
    t1b = np.tile(np.repeat(t4, 4), 4)
    t21b = np.tile(t4, 16)
    t0a, t1a, t21a = t0b, t1b, t21b
    w = lmul(ra, Z)
    o0b = LM[t0b, rb]
    o1b_our = t1b
    o1b_pin = LM[t21b, p]
    o0a = LM[t0a, ra]
    o1a_our = LM[t1a, w]
    o1a_pin = t21a
    old_b = F3E[o0b][:, :, None] + F3T[o1b_our, o1b_pin][:, None, :]
    old_a = F3E[o0a][:, :, None] + F3T[o1a_our, o1a_pin][:, None, :]
    best = np.full((64, 64, 64, 64), 99, dtype=np.int16)

    def group(bparts, aparts, struct: int):
        fb = np.stack([
            F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :] - old_b
            for n0, n1, n1p in bparts
        ]).min(axis=0).reshape(64, 64)
        fa = np.stack([
            F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :] - old_a
            for n0, n1, n1p in aparts
        ]).min(axis=0).reshape(64, 64)
        np.minimum(best, fb[:, :, None, None] + fa[None, None, :, :] + np.int16(struct), out=best)

    for sw in (0, 1):
        s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
        s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
        group([(s0b, s1b, LM[t21b, pp]) for pp in (1, 2)],
              [(LM[s0a, Z], LM[s1a, c], o1a_pin) for c in (1, 2)], -2)
        group([(LM[s0b, Z], LM[s1b, c], LM[t21b, pp])
               for c in (1, 2) for pp in (1, 2)],
              [(s0a, s1a, o1a_pin)], -2 - 2 * ja)
        if ja:
            group([(s0b, LM[s1b, le], LM[t21b, pp])
                   for le in (1, 2) for pp in (1, 2)],
                  [(LM[s0a, m0], LM[s1a, m1], o1a_pin)
                   for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0], -2)
        group([(LM[s0b, m0], LM[s1b, m1], LM[t21b, m12])
               for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0
               for m12 in (1, 2)],
              [(s0a, LM[s1a, le], LM[t21a, l2])
               for le in (1, 2) for l2 in (1, 2)], 0)
    return best, old_b, old_a


def targets_for_indices(ja: int, idx: np.ndarray) -> np.ndarray:
    cb, eb, ca, ea = (idx[:, k].astype(np.int64) for k in range(4))
    t0b, t1b, t21b = cb // 16, (cb // 4) % 4, cb % 4
    t0a, t1a, t21a = ca // 16, (ca // 4) % 4, ca % 4
    e0b, e1b = eb // 4, eb % 4
    u0b, v0b = e0b // 4, e0b % 4
    e0a, e1a = ea // 4, ea % 4
    u0a, v0a = e0a // 4, e0a % 4
    t = np.empty((len(idx), 3, 2, 2), dtype=np.int8)
    t[:, 0, 0, 0] = t0b; t[:, 0, 0, 1] = t0a
    t[:, 0, 1, 0] = t1b; t[:, 0, 1, 1] = t1a
    t[:, 1, 0, 0] = LM[u0b, Z]; t[:, 1, 0, 1] = u0a
    t[:, 1, 1, 0] = t21b; t[:, 1, 1, 1] = t21a
    t[:, 2, 0, 0] = v0b
    t[:, 2, 0, 1] = LM[v0a, Z] if ja == 0 else v0a
    t[:, 2, 1, 0] = e1b if ja == 0 else LM[e1b, X]
    t[:, 2, 1, 1] = LM[e1a, X] if ja == 0 else e1a
    return t


def j6_configs():
    ac = {s: tuple(x for x in (1, 2, 3) if lsy(s, x)) for s in (1, 2, 3)}
    return [(q, s, *rs, *sg)
            for q in (0, 1) for s in (1, 2, 3)
            for rs in itertools.product(ac[s], repeat=3)
            for sg in itertools.product((0, 1), repeat=3)]


def j6_min(targets: np.ndarray) -> np.ndarray:
    best = np.full(len(targets), 99, dtype=np.int16)
    for q, s, r0, r1, r2, sg0, sg1, sg2 in j6_configs():
        rs = (r0, r1, r2); sig = (sg0, sg1, sg2)
        val = np.zeros(len(targets), dtype=np.int16)
        other = 1 - q
        for branch in (0, 1):
            loc = []
            for j in range(3):
                src = sig[j] if branch == 0 else 1 - sig[j]
                fr = s if branch == 0 else rs[j]
                loc.append(LM[targets[:, j, src, q], fr])
            val += F3[loc[0], loc[1], loc[2]]
            loc = []
            for j in range(3):
                src = sig[j] if branch == 0 else 1 - sig[j]
                loc.append(targets[:, j, src, other])
            val += F3[loc[0], loc[1], loc[2]]
        np.minimum(best, val, out=best)
    return best


def exact_bprime_local(t: np.ndarray) -> int | None:
    """Exact frozen B' on the two touched coordinates, from primitive letters."""
    union = [q for q in (0, 1) if any(int(t[j, b, q]) != 0 for j in range(3) for b in (0, 1))]
    pool = list(union)
    for q in (0, 1):
        if q not in union:
            pool.append(q)
            break
    pool = sorted(pool)
    qtags = list(union) + [q for q in pool if q not in union]
    best = 10 ** 6
    for qt in qtags:
        homes = [q for q in pool if q != qt]
        if not homes:
            continue
        for v in (1, 2, 3):
            blocks = []
            for j in range(3):
                opts = []
                # anchored option
                for c in (1, 2, 3):
                    if c == v:
                        continue
                    for sigma in (0, 1):
                        r0 = [0, 0]; r1 = [0, 0]
                        r0[qt] = v; r1[qt] = c
                        res0 = [lmul(int(t[j, sigma, q]), r0[q]) for q in (0, 1)]
                        res1 = [lmul(int(t[j, 1 - sigma, q]), r1[q]) for q in (0, 1)]
                        opts.append((0, res0, res1))
                # phantom option
                for qh in homes:
                    for ell in (1, 2, 3):
                        if ell == v:
                            continue
                        for m0 in (1, 2, 3):
                            for m1 in (1, 2, 3):
                                if m1 == m0:
                                    continue
                                for sigma in (0, 1):
                                    r0 = [0, 0]; r1 = [0, 0]
                                    r0[qh] = m0; r1[qt] = ell; r1[qh] = m1
                                    res0 = [lmul(int(t[j, sigma, q]), r0[q]) for q in (0, 1)]
                                    res1 = [lmul(int(t[j, 1 - sigma, q]), r1[q]) for q in (0, 1)]
                                    opts.append((2, res0, res1))
                blocks.append(opts)
            for oa in blocks[0]:
                for ob in blocks[1]:
                    for oc in blocks[2]:
                        if oa[0] == ob[0] == oc[0] == 0:
                            continue
                        val = 2 + oa[0] + ob[0] + oc[0]
                        for branch in (0, 1):
                            for q in (0, 1):
                                val += f3(oa[1 + branch][q], ob[1 + branch][q], oc[1 + branch][q])
                        best = min(best, val)
    return None if best >= 10 ** 6 else int(best)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=RESULT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    source = json.loads(args.input.read_text())
    parent = json.loads(PARENT.read_text())

    all_t = []; all_old = []; all_pd = []; all_params = []
    hist = Counter(); cell_counts = {}
    for ja, rb, ra, p in itertools.product((0, 1), (1, 2), (1, 2), (1, 2)):
        best, old_b, old_a = parent_pa_cell(ja, rb, ra, p)
        idx = np.argwhere(best > 0)
        cell_counts[f"ja{ja}_Rb{rb}_Ra{ra}_p{p}"] = int(len(idx))
        cb, eb, ca, ea = (idx[:, k].astype(np.int64) for k in range(4))
        pd = best[cb, eb, ca, ea].astype(np.int16)
        old = (old_b[cb, eb // 4, eb % 4] + old_a[ca, ea // 4, ea % 4]).astype(np.int16)
        all_t.append(targets_for_indices(ja, idx)); all_old.append(old); all_pd.append(pd)
        all_params.append(np.column_stack([np.full(len(idx), ja), np.full(len(idx), rb),
                                           np.full(len(idx), ra), np.full(len(idx), p), idx]).astype(np.int16))
        hist.update(int(x) for x in pd)
    t = np.concatenate(all_t); old = np.concatenate(all_old); pd = np.concatenate(all_pd); params = np.concatenate(all_params)
    j6new = j6_min(t)
    j6delta = j6new - old.astype(np.int16) - 4
    after = np.minimum(pd.astype(np.int16), j6delta)
    ids = np.flatnonzero(after > 0)
    bp_hist = Counter(); final = 0; rows = []
    for rid in ids:
        bp = exact_bprime_local(t[int(rid)])
        bd = 10 ** 6 if bp is None else int(bp) - (int(old[rid]) + 6)
        bp_hist.update([bd])
        fd = min(int(after[rid]), bd)
        final += int(fd > 0)
        state = tuple(int(x) for x in params[rid])
        rows.append((state, int(pd[rid]), int(j6delta[rid]), None if bp is None else int(bp), bd, fd))

    source_rows = []
    for r in source.get("j7_bprime", {}).get("rows", []):
        s = r["state"]
        source_rows.append(((s["ja"], s["R_b"], s["R_a"], s["p"], s["coreB"], s["envB"], s["coreA"], s["envA"]),
                            r["parent_delta"], r["j6_delta"], r["bprime_absolute_cost"], r["bprime_delta"], r["final_delta"]))

    checks = {
        "source_schema": source.get("schema") == "ORIONQG.QG7D.J7PAConfirmatory.v1",
        "source_digest": verify_digest(source),
        "source_positive": source.get("terminal") == POSITIVE and source.get("all_gates") is True,
        "protocol_sha": source.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "parent_digest": parent.get("result_digest") == PARENT_DIGEST == source.get("parent_qg7c_digest"),
        "parent_failures": len(pd) == 103048 == source.get("parent", {}).get("pa_failures"),
        "parent_histogram": hist == Counter({1: 100672, 2: 2376}),
        "cell_fingerprint": sorted(cell_counts.values()).count(12431) == 8 and sorted(cell_counts.values()).count(450) == 8,
        "j6_library_384": len(j6_configs()) == 384,
        "j6_residuals_42": len(ids) == 42 == source.get("j6", {}).get("residual_count"),
        "j6_residuals_plus1": bool(len(ids)) and np.all(after[ids] == 1),
        "bprime_hist": bp_hist == Counter({0: 36, -1: 6}),
        "j7_zero": final == 0 == source.get("j7_bprime", {}).get("final_residuals"),
        "residual_rows_exact": rows == source_rows,
        "pa_only_authority": source.get("PA_ALL_N") is True and source.get("PP_ALL_N") is False and source.get("CHAIN_ALL_N") is False and source.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False,
        "authority_bounded": source.get("novelty_authority") is False and source.get("r6_authority") is False and source.get("physical_quantum_advantage_claim") is False,
        "protected_subject_not_read": source.get("protected_subject_read") is False,
    }
    decision = "ACCEPT_PA_ALL_N_CLOSURE" if all(checks.values()) else "REJECT"
    out = {
        "schema": "ORIONQG.QG7D.J7PAGenericVerification.v1",
        "issue": "SzeChunYiu/ORION#836",
        "decision": decision,
        "all_checks": all(checks.values()),
        "checks": checks,
        "source_result_digest": source.get("result_digest"),
        "parent_failures": len(pd),
        "parent_delta_histogram": {str(k): int(v) for k, v in sorted(hist.items())},
        "j6_residuals": len(ids),
        "bprime_delta_histogram": {str(k): int(v) for k, v in sorted(bp_hist.items())},
        "j7_final_residuals": final,
        "PA_ALL_N": decision == "ACCEPT_PA_ALL_N_CLOSURE",
        "PP_ALL_N": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "decision": decision, "all_checks": out["all_checks"],
        "parent_failures": len(pd), "j6_residuals": len(ids),
        "j7_residuals": final, "bprime_delta_histogram": out["bprime_delta_histogram"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
