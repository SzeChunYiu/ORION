from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ACTIONS = ("R0", "R1", "R2", "R3", "R4", "N0", "N1")
HISTORY_LENGTHS = (8, 16, 32, 64)
BRANCH_COUNTS = (2, 4, 8, 16)
DEPTH = 3
PROTECTED_HISTORIES = 4096


@dataclass(frozen=True)
class State:
    q: tuple[int, int, int, int, int]
    n: tuple[int, int, int, int, int]


def seed64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def full_step(state: State, action: int) -> State:
    q = list(state.q)
    n = list(state.n)
    if action == 0:
        q[0] ^= 1
    elif action == 1:
        q[1] ^= q[0]
    elif action == 2:
        q[2] ^= q[1]
    elif action == 3:
        q[3] ^= q[2]
    elif action == 4:
        q[4] ^= q[3]
    elif action == 5:
        n[0] ^= 1
        n[1] ^= n[0]
    elif action == 6:
        n = [n[-1], *n[:-1]]
    else:
        raise ValueError(action)
    return State(tuple(q), tuple(n))


def q_step(q_in: tuple[int, ...], action: int) -> tuple[int, ...]:
    q = list(q_in)
    if action == 0:
        q[0] ^= 1
    elif action == 1:
        q[1] ^= q[0]
    elif action == 2:
        q[2] ^= q[1]
    elif action == 3:
        q[3] ^= q[2]
    elif action == 4:
        q[4] ^= q[3]
    elif action in (5, 6):
        pass
    else:
        raise ValueError(action)
    return tuple(q)


def reward_q(q: tuple[int, ...]) -> int:
    return int(sum(q) >= 3)


def replay_reward(history: np.ndarray, query: tuple[int, ...]) -> int:
    s = State((0, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    for a in history:
        s = full_step(s, int(a))
    for a in query:
        s = full_step(s, int(a))
    return reward_q(s.q)


def persisted_full(history: np.ndarray) -> State:
    s = State((0, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    for a in history:
        s = full_step(s, int(a))
    return s


def persisted_certified(history: np.ndarray) -> tuple[int, ...]:
    q = (0, 0, 0, 0, 0)
    for a in history:
        q = q_step(q, int(a))
    return q


def branch_full(state: State, query: tuple[int, ...]) -> int:
    s = state
    for a in query:
        s = full_step(s, int(a))
    return reward_q(s.q)


def branch_cert(q0: tuple[int, ...], query: tuple[int, ...]) -> int:
    q = q0
    for a in query:
        q = q_step(q, int(a))
    return reward_q(q)


def heuristic_last4(history: np.ndarray) -> State:
    return persisted_full(history[-4:])


def queries_for(rng: np.random.Generator, b: int) -> list[tuple[int, int, int]]:
    all_q = list(itertools.product(range(len(ACTIONS)), repeat=DEPTH))
    idx = rng.choice(len(all_q), size=b, replace=False)
    return [all_q[int(i)] for i in idx]


def exact_ops(length: int, b: int) -> dict[str, int]:
    return {
        "REPLAY": b * (length + DEPTH),
        "PERSIST_FULL": length + b * DEPTH,
        "PERSIST_CERTIFIED": length + b * DEPTH,
        "HEURISTIC_LAST4": min(4, length) + b * DEPTH,
    }


def run_cell(length: int, b: int) -> dict[str, object]:
    rng = np.random.default_rng(seed64(f"frontier-f6-v1|L={length}|b={b}"))
    histories = rng.integers(0, len(ACTIONS), size=(PROTECTED_HISTORIES, length), dtype=np.int8)
    queries = queries_for(rng, b)
    pf_mismatch = 0
    pc_mismatch = 0
    h_mismatch = 0

    started = time.perf_counter()
    replay_matrix: list[list[int]] = []
    for history in histories:
        replay_matrix.append([replay_reward(history, q) for q in queries])
    replay_seconds = time.perf_counter() - started

    started = time.perf_counter()
    for row_i, history in enumerate(histories):
        s = persisted_full(history)
        vals = [branch_full(s, q) for q in queries]
        pf_mismatch += sum(int(a != b_) for a, b_ in zip(replay_matrix[row_i], vals))
    pf_seconds = time.perf_counter() - started

    started = time.perf_counter()
    for row_i, history in enumerate(histories):
        q0 = persisted_certified(history)
        vals = [branch_cert(q0, q) for q in queries]
        pc_mismatch += sum(int(a != b_) for a, b_ in zip(replay_matrix[row_i], vals))
    pc_seconds = time.perf_counter() - started

    for row_i, history in enumerate(histories):
        s = heuristic_last4(history)
        vals = [branch_full(s, q) for q in queries]
        h_mismatch += sum(int(a != b_) for a, b_ in zip(replay_matrix[row_i], vals))

    ops = exact_ops(length, b)
    return {
        "L": length,
        "b": b,
        "branches_evaluated": PROTECTED_HISTORIES * b,
        "correctness_mismatches": {
            "PERSIST_FULL": pf_mismatch,
            "PERSIST_CERTIFIED": pc_mismatch,
            "HEURISTIC_LAST4": h_mismatch,
        },
        "ops": ops,
        "ReplayTax_ops": ops["REPLAY"] / ops["PERSIST_CERTIFIED"],
        "persisted_state_bits": {"PERSIST_FULL": 10, "PERSIST_CERTIFIED": 5},
        "persisted_state_packed_bytes": {"PERSIST_FULL": math.ceil(10 / 8), "PERSIST_CERTIFIED": math.ceil(5 / 8)},
        "wall_seconds": {"REPLAY": replay_seconds, "PERSIST_FULL": pf_seconds, "PERSIST_CERTIFIED": pc_seconds},
        "ReplayTax_wall": replay_seconds / pc_seconds if pc_seconds > 0 else None,
    }


def checks(cells: list[dict[str, object]]) -> dict[str, bool]:
    by = {(int(c["L"]), int(c["b"])): c for c in cells}
    zero_exact = all(c["correctness_mismatches"]["PERSIST_FULL"] == 0 and c["correctness_mismatches"]["PERSIST_CERTIFIED"] == 0 for c in cells)
    b_monotone = True
    for L in HISTORY_LENGTHS:
        vals = [float(by[(L, b)]["ReplayTax_ops"]) for b in BRANCH_COUNTS]
        b_monotone &= all(vals[i] <= vals[i + 1] + 1e-15 for i in range(len(vals) - 1))
    l_monotone = True
    for b in BRANCH_COUNTS:
        if b < 4:
            continue
        vals = [float(by[(L, b)]["ReplayTax_ops"]) for L in HISTORY_LENGTHS]
        l_monotone &= all(vals[i] <= vals[i + 1] + 1e-15 for i in range(len(vals) - 1))
    high = float(by[(64, 16)]["ReplayTax_ops"])
    smaller = all(c["persisted_state_packed_bytes"]["PERSIST_CERTIFIED"] < c["persisted_state_packed_bytes"]["PERSIST_FULL"] for c in cells)
    heuristic_fails = sum(int(c["correctness_mismatches"]["HEURISTIC_LAST4"]) for c in cells) > 0
    return {
        "zero_PF_PC_correctness_mismatches": zero_exact,
        "ReplayTax_nondecreasing_with_branch_count": bool(b_monotone),
        "ReplayTax_nondecreasing_with_history_length_for_b_ge_4": bool(l_monotone),
        "ReplayTax_ops_L64_b16_ge_4": high >= 4.0,
        "certified_state_strictly_smaller": bool(smaller),
        "heuristic_negative_control_has_mismatch": heuristic_fails,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    cells = [run_cell(L, b) for L in HISTORY_LENGTHS for b in BRANCH_COUNTS]
    ck = checks(cells)
    terminal = "PERSISTENT_SUFFICIENT_STATE_REDUCES_REPLAY_SCALING" if all(ck.values()) else "PERSISTENCE_CORRECT__REPLAY_TAX_TOO_SMALL"
    result = {
        "schema": "ORION.FrontierF6.Result.v1",
        "protocol": "F6_PERSISTENCE_REPLAY_TAX_PROTOCOL_V1.md",
        "f2_certificate_receipt": "results/F2_CERTIFICATE_RECEIPT_V1.json",
        "history_lengths": list(HISTORY_LENGTHS),
        "branch_counts": list(BRANCH_COUNTS),
        "continuation_depth": DEPTH,
        "protected_histories_per_cell": PROTECTED_HISTORIES,
        "cells": cells,
        "checks": ck,
        "terminal": terminal,
        "claim_boundary": "Controlled deterministic replay/persistence result only; not an LLM or Lean snapshot result.",
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"terminal": terminal, "checks": ck, "high_cell": next(c for c in cells if c['L']==64 and c['b']==16)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
