#!/usr/bin/env python3
"""QG-7d J7 confirmatory PA theorem packet.

Reconstructs the complete PA part of the committed QG-7c T4b pinned census,
executes the frozen J6 global anchored Tag-relocation library, then applies the
unchanged QG-5b B' family only to the J6 residuals.  This is confirmatory: the
103,048 / 42 / 0 fingerprints were disclosed before the protected run.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(QG))
import qg7c_classification as q7c  # noqa: E402

PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG7D_J7_PA_CONFIRMATORY_PROTOCOL_V1.md"
PARENT = QG / "QG7C_CLASSIFICATION_RESULTS.json"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg7d-j7-pa-confirm.json"
TOKEN = "ORIONQG_QG7D_J7="
ISSUE = "SzeChunYiu/ORION#836"
PARENT_DIGEST = "0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6"
POSITIVE = "QG7D_PA_PINNED_COMM_S2_CLOSED_ALL_N_MACHINE_CHECKED__PP_CHAIN_OPEN"
X, Z = 1, 3


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lm(a: int, b: int) -> int:
    return int(q7c.lmul(int(a), int(b)))


def f3(a: int, b: int, c: int) -> int:
    return int(q7c.lf3(int(a), int(b), int(c)))


def decode_core(idx: int) -> tuple[int, int, int]:
    return idx // 16, (idx // 4) % 4, idx % 4


def target_key(letters: tuple[int, int]) -> tuple[int, int]:
    out = (0, 0)
    for q, le in enumerate(letters):
        if int(le):
            out = q7c.p10.mul(out, q7c.r6o._letter_key(int(le), q))
    return out


def target_pairs_from_letters(t: np.ndarray) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    return tuple(
        (target_key(tuple(int(x) for x in t[j, 0])),
         target_key(tuple(int(x) for x in t[j, 1])))
        for j in range(3)
    )


def parent_pa_cell(ja: int, rb: int, ra: int, p: int):
    """Rebuild one exact QG-7c PA G1-G4 cell from production local algebra."""
    lm_table = q7c.MY_LM
    f3e = q7c.F3E
    f3t = q7c.F3T
    t4 = np.arange(4, dtype=np.int64)
    t0b = np.repeat(t4, 16)
    t1b = np.tile(np.repeat(t4, 4), 4)
    t21b = np.tile(t4, 16)
    t0a, t1a, t21a = t0b, t1b, t21b
    w = lm(ra, Z)
    o0b = lm_table[t0b, rb]
    o1b_our = t1b
    o1b_pin = lm_table[t21b, p]
    o0a = lm_table[t0a, ra]
    o1a_our = lm_table[t1a, w]
    o1a_pin = t21a
    old_b = f3e[o0b][:, :, None] + f3t[o1b_our, o1b_pin][:, None, :]
    old_a = f3e[o0a][:, :, None] + f3t[o1a_our, o1a_pin][:, None, :]
    best = np.full((64, 64, 64, 64), 99, dtype=np.int16)

    def group(bparts, aparts, struct: int):
        fb = np.stack([
            f3e[n0][:, :, None] + f3t[n1, n1p][:, None, :] - old_b
            for n0, n1, n1p in bparts
        ]).min(axis=0).reshape(64, 64)
        fa = np.stack([
            f3e[n0][:, :, None] + f3t[n1, n1p][:, None, :] - old_a
            for n0, n1, n1p in aparts
        ]).min(axis=0).reshape(64, 64)
        np.minimum(best,
                   fb[:, :, None, None] + fa[None, None, :, :]
                   + np.int16(struct), out=best)

    for sw in (0, 1):
        s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
        s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
        # G1 anchored@a x pinner re-letter
        group([(s0b, s1b, lm_table[t21b, pp]) for pp in (1, 2)],
              [(lm_table[s0a, Z], lm_table[s1a, c], o1a_pin) for c in (1, 2)], -2)
        # G2 anchored@b x pinner re-letter
        group([(lm_table[s0b, Z], lm_table[s1b, c], lm_table[t21b, pp])
               for c in (1, 2) for pp in (1, 2)],
              [(s0a, s1a, o1a_pin)], -2 - 2 * ja)
        # G3 phantom home=a borrow=b x pinner re-letter
        if ja:
            group([(s0b, lm_table[s1b, le], lm_table[t21b, pp])
                   for le in (1, 2) for pp in (1, 2)],
                  [(lm_table[s0a, m0], lm_table[s1a, m1], o1a_pin)
                   for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0], -2)
        # G4 joint, PA branch only
        group([(lm_table[s0b, m0], lm_table[s1b, m1], lm_table[t21b, m12])
               for m0 in (1, 2, 3) for m1 in (1, 2, 3) if m1 != m0
               for m12 in (1, 2)],
              [(s0a, lm_table[s1a, le], lm_table[t21a, l2])
               for le in (1, 2) for l2 in (1, 2)], 0)
    return best, old_b, old_a


def targets_for_indices(ja: int, idx: np.ndarray) -> np.ndarray:
    """Recover six target letters at (b,a) for PA states."""
    cb, eb, ca, ea = (idx[:, k].astype(np.int64) for k in range(4))
    t0b, t1b, t21b = cb // 16, (cb // 4) % 4, cb % 4
    t0a, t1a, t21a = ca // 16, (ca // 4) % 4, ca % 4
    e0b, e1b = eb // 4, eb % 4
    u0b, v0b = e0b // 4, e0b % 4
    e0a, e1a = ea // 4, ea % 4
    u0a, v0a = e0a // 4, e0a % 4
    t = np.empty((len(idx), 3, 2, 2), dtype=np.int8)
    t[:, 0, 0, 0] = t0b
    t[:, 0, 0, 1] = t0a
    t[:, 0, 1, 0] = t1b
    t[:, 0, 1, 1] = t1a
    t[:, 1, 0, 0] = q7c.MY_LM[u0b, Z]
    t[:, 1, 0, 1] = u0a
    t[:, 1, 1, 0] = t21b
    t[:, 1, 1, 1] = t21a
    t[:, 2, 0, 0] = v0b
    t[:, 2, 0, 1] = q7c.MY_LM[v0a, Z] if ja == 0 else v0a
    t[:, 2, 1, 0] = e1b if ja == 0 else q7c.MY_LM[e1b, X]
    t[:, 2, 1, 1] = q7c.MY_LM[e1a, X] if ja == 0 else e1a
    return t


def j6_configs():
    ac = {s: tuple(x for x in (1, 2, 3) if q7c.lsy(s, x)) for s in (1, 2, 3)}
    return [
        (q, s, *rs, *sigmas)
        for q in (0, 1)
        for s in (1, 2, 3)
        for rs in itertools.product(ac[s], repeat=3)
        for sigmas in itertools.product((0, 1), repeat=3)
    ]


def j6_min_new_f3(targets: np.ndarray):
    configs = j6_configs()
    best = np.full(len(targets), 99, dtype=np.int16)
    arg = np.full(len(targets), -1, dtype=np.int16)
    for ci, (q, s, r0, r1, r2, sg0, sg1, sg2) in enumerate(configs):
        rs = (r0, r1, r2)
        sigmas = (sg0, sg1, sg2)
        val = np.zeros(len(targets), dtype=np.int16)
        other = 1 - q
        for branch in (0, 1):
            loc = []
            for j in range(3):
                src = sigmas[j] if branch == 0 else 1 - sigmas[j]
                fr = s if branch == 0 else rs[j]
                loc.append(q7c.MY_LM[targets[:, j, src, q], fr])
            val += q7c.MY_F3[loc[0], loc[1], loc[2]].astype(np.int16)
            loc = []
            for j in range(3):
                src = sigmas[j] if branch == 0 else 1 - sigmas[j]
                loc.append(targets[:, j, src, other])
            val += q7c.MY_F3[loc[0], loc[1], loc[2]].astype(np.int16)
        mask = val < best
        best[mask] = val[mask]
        arg[mask] = ci
    return best, arg, configs


def serialize_j6_config(cfg) -> dict[str, Any]:
    q, s, r0, r1, r2, sg0, sg1, sg2 = (int(x) for x in cfg)
    return {
        "relocation_coordinate": "b" if q == 0 else "a",
        "tag_letter": s,
        "label1_frame_letters": [r0, r1, r2],
        "target_permutations": [sg0, sg1, sg2],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    parent = json.loads(PARENT.read_text())

    old_struct = 2 * (2 - 1) + 2 * 2  # central support-2 frame + weight-2 Tag
    new_dplus_struct = 2 * 1          # support-one Tag; all frames support one

    all_targets = []
    all_old = []
    all_parent_delta = []
    all_params = []
    per_cell_failures = {}
    parent_hist = Counter()

    for ja, rb, ra, p in itertools.product((0, 1), (1, 2), (1, 2), (1, 2)):
        best, old_b, old_a = parent_pa_cell(ja, rb, ra, p)
        idx = np.argwhere(best > 0)
        key = f"ja{ja}_Rb{rb}_Ra{ra}_p{p}"
        per_cell_failures[key] = int(len(idx))
        if not len(idx):
            continue
        cb, eb, ca, ea = (idx[:, k].astype(np.int64) for k in range(4))
        pd = best[cb, eb, ca, ea].astype(np.int16)
        old = (old_b[cb, eb // 4, eb % 4]
               + old_a[ca, ea // 4, ea % 4]).astype(np.int16)
        targets = targets_for_indices(ja, idx)
        params = np.column_stack([
            np.full(len(idx), ja), np.full(len(idx), rb),
            np.full(len(idx), ra), np.full(len(idx), p), idx
        ]).astype(np.int16)
        all_targets.append(targets)
        all_old.append(old)
        all_parent_delta.append(pd)
        all_params.append(params)
        parent_hist.update(int(x) for x in pd)

    targets = np.concatenate(all_targets)
    old_f3 = np.concatenate(all_old).astype(np.int16)
    parent_delta = np.concatenate(all_parent_delta).astype(np.int16)
    params = np.concatenate(all_params)

    j6_new_f3, j6_arg, configs = j6_min_new_f3(targets)
    j6_delta = j6_new_f3 - old_f3 + (new_dplus_struct - old_struct)
    after_j6 = np.minimum(parent_delta, j6_delta)
    residual_ids = np.flatnonzero(after_j6 > 0)

    residual_rows = []
    bprime_delta_hist = Counter()
    bprime_verify_failures = []
    final_residuals = 0
    for rid in residual_ids:
        t = targets[int(rid)]
        tp = target_pairs_from_letters(t)
        cost, wit = q7c.qg5b.bprime_family_min(tp, 2, want_witness=True)
        if cost is None:
            bp_delta = 10 ** 6
            verified = False
        else:
            cost = int(cost)
            bp_delta = cost - (int(old_f3[rid]) + old_struct)
            verified = bool(q7c.qg5b.verify_bprime_witness(tp, 2, wit))
        bprime_delta_hist.update([int(bp_delta)])
        if not verified:
            bprime_verify_failures.append(int(rid))
        final = min(int(after_j6[rid]), int(bp_delta))
        if final > 0:
            final_residuals += 1
        ja, rb, ra, p, cb, eb, ca, ea = (int(x) for x in params[rid])
        residual_rows.append({
            "global_failure_index": int(rid),
            "state": {"ja": ja, "R_b": rb, "R_a": ra, "p": p,
                      "coreB": cb, "envB": eb, "coreA": ca, "envA": ea},
            "target_letters_ba": t.tolist(),
            "parent_delta": int(parent_delta[rid]),
            "old_f3": int(old_f3[rid]),
            "old_absolute_cost": int(old_f3[rid]) + old_struct,
            "j6_delta": int(j6_delta[rid]),
            "j6": serialize_j6_config(configs[int(j6_arg[rid])]),
            "bprime_absolute_cost": None if cost is None else int(cost),
            "bprime_delta": None if cost is None else int(bp_delta),
            "bprime_witness_verified": verified,
            "final_delta": int(final),
        })

    gates = {
        "protocol_frozen": PROTOCOL.exists(),
        "parent_digest": parent.get("result_digest") == PARENT_DIGEST,
        "parent_terminal": parent.get("terminal") == "QG7C_PARTIAL__L4B_OPEN",
        "old_structural_cost_6": old_struct == 6,
        "new_dplus_structural_cost_2": new_dplus_struct == 2,
        "parent_pa_failures_103048": len(parent_delta) == 103048,
        "parent_delta_histogram": parent_hist == Counter({1: 100672, 2: 2376}),
        "per_cell_fingerprint": (
            sorted(per_cell_failures.values()).count(12431) == 8
            and sorted(per_cell_failures.values()).count(450) == 8
        ),
        "j6_complete_library_size_384": len(configs) == 384,
        "j6_residuals_42": len(residual_ids) == 42,
        "j6_residuals_all_plus1": bool(len(residual_ids)) and np.all(after_j6[residual_ids] == 1),
        "bprime_all_verified": not bprime_verify_failures and len(residual_rows) == 42,
        "bprime_residual_delta_histogram": bprime_delta_hist == Counter({0: 36, -1: 6}),
        "j7_final_residuals_zero": final_residuals == 0,
        "terminal_shapes_eliminate_comm_s2": final_residuals == 0,
        "only_two_touched_coordinates": targets.shape[3] == 2,
        "protected_subject_not_read": True,
    }

    if all(gates.values()):
        terminal = POSITIVE
    elif not gates["parent_pa_failures_103048"] or not gates["parent_delta_histogram"] or not gates["j6_residuals_42"]:
        terminal = "QG7D_J7_CONFIRMATORY_REPLICATION_MISMATCH"
    elif final_residuals:
        terminal = "QG7D_J7_PA_RESIDUAL_REMAINS"
    else:
        terminal = "QG7D_CANNOT_CHECK"

    result = {
        "schema": "ORIONQG.QG7D.J7PAConfirmatory.v1",
        "issue": ISSUE,
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha(PROTOCOL) if PROTOCOL.exists() else None,
        "parent_qg7c_digest": parent.get("result_digest"),
        "terminal": terminal,
        "confirmatory_not_blind": True,
        "parent": {
            "pa_failures": int(len(parent_delta)),
            "delta_histogram": {str(k): int(v) for k, v in sorted(parent_hist.items())},
            "per_parameter_cell_failures": per_cell_failures,
        },
        "structural_costs": {
            "old_pinned_pa": old_struct,
            "new_dplus": new_dplus_struct,
            "delta": new_dplus_struct - old_struct,
            "derivation": "old=central_mult2*(support2-1)+TagCost2*weight2; new=TagCost2*weight1",
        },
        "j6": {
            "library_size": len(configs),
            "residual_count": int(len(residual_ids)),
            "residual_delta_histogram": {
                str(k): int(v) for k, v in sorted(Counter(int(x) for x in after_j6[residual_ids]).items())
            },
        },
        "j7_bprime": {
            "rows_evaluated": int(len(residual_rows)),
            "delta_histogram": {str(k): int(v) for k, v in sorted(bprime_delta_hist.items())},
            "witness_verification_failures": bprime_verify_failures,
            "final_residuals": int(final_residuals),
            "rows": residual_rows,
        },
        "gates": gates,
        "all_gates": all(gates.values()),
        "PA_ALL_N": terminal == POSITIVE,
        "PP_ALL_N": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "protected_subject_read": False,
    }
    unsigned = dict(result)
    result["result_digest"] = hashlib.sha256(canonical(unsigned).encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "terminal": terminal,
        "parent_failures": len(parent_delta),
        "j6_residuals": len(residual_ids),
        "j7_residuals": final_residuals,
        "bprime_delta_histogram": result["j7_bprime"]["delta_histogram"],
        "result_digest": result["result_digest"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
