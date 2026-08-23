from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier

ACTIONS = ("R0", "R1", "R2", "R3", "R4", "N0", "N1")
HORIZON = 3
HISTORY_LENGTHS = (8, 16, 32)
TRAIN_SIZES = (256, 512, 1024, 2048, 4096, 8192, 16384)
TEST_N = 8192
PRIMARY_ARMS = ("T_TRANSCRIPT", "H4_HEURISTIC_LAST4", "F_FULL_STATE", "C_CERTIFIED_STATE")
ALL_ARMS = PRIMARY_ARMS + ("I_INVALID_QUOTIENT",)


@dataclass(frozen=True)
class WorldState:
    q: tuple[int, int, int, int, int]
    n: tuple[int, int, int, int, int]

    def bits10(self) -> tuple[int, ...]:
        return self.q + self.n


def seed64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big", signed=False)


def apply_action(state: WorldState, action: int) -> WorldState:
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
    return WorldState(tuple(q), tuple(n))


def run_actions(state: WorldState, actions: Iterable[int]) -> WorldState:
    out = state
    for action in actions:
        out = apply_action(out, int(action))
    return out


def reward(state: WorldState) -> int:
    return int(sum(state.q) >= 3)


def state_from_int(value: int) -> WorldState:
    bits = tuple((value >> i) & 1 for i in range(10))
    return WorldState(bits[:5], bits[5:])


def all_queries() -> list[tuple[int, int, int]]:
    return list(itertools.product(range(len(ACTIONS)), repeat=HORIZON))


def signature(state: WorldState, queries: list[tuple[int, int, int]]) -> bytes:
    values = bytearray()
    current_byte = 0
    offset = 0
    for query in queries:
        bit = reward(run_actions(state, query))
        current_byte |= (bit & 1) << offset
        offset += 1
        if offset == 8:
            values.append(current_byte)
            current_byte = 0
            offset = 0
    if offset:
        values.append(current_byte)
    return bytes(values)


def exact_certificate() -> dict[str, object]:
    queries = all_queries()
    by_c: dict[tuple[int, ...], set[bytes]] = {}
    by_i: dict[tuple[int, ...], set[bytes]] = {}
    for value in range(1 << 10):
        state = state_from_int(value)
        sig = signature(state, queries)
        by_c.setdefault(state.q, set()).add(sig)
        by_i.setdefault(state.q[:4], set()).add(sig)
    c_violations = {str(key): len(vals) for key, vals in by_c.items() if len(vals) != 1}
    i_counterexamples = {str(key): len(vals) for key, vals in by_i.items() if len(vals) > 1}
    if c_violations:
        raise RuntimeError(f"CERTIFIED_STATE_EXACT_FUTURE_EQUIVALENCE_FAILED: {c_violations}")
    if not i_counterexamples:
        raise RuntimeError("INVALID_QUOTIENT_COUNTEREXAMPLE_NOT_FOUND")
    return {
        "states_checked": 1 << 10,
        "queries_checked_per_state": len(queries),
        "certified_groups": len(by_c),
        "certified_violations": 0,
        "invalid_groups_with_counterexamples": len(i_counterexamples),
        "certified_terminal": "CERTIFIED_STATE_EXACT_FUTURE_EQUIVALENCE",
        "invalid_terminal": "INVALID_QUOTIENT_COUNTEREXAMPLE_FOUND",
    }


def onehot_actions(actions: np.ndarray, length: int) -> np.ndarray:
    out = np.zeros((actions.shape[0], length * len(ACTIONS)), dtype=np.float32)
    rows = np.arange(actions.shape[0])[:, None]
    cols = np.arange(length)[None, :] * len(ACTIONS) + actions
    out[rows, cols] = 1.0
    return out


def generate_rows(length: int, count: int, split: str) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed64(f"frontier-f2-{split}-v1|{length}"))
    histories = rng.integers(0, len(ACTIONS), size=(count, length), dtype=np.int8)
    queries = rng.integers(0, len(ACTIONS), size=(count, HORIZON), dtype=np.int8)
    states = np.zeros((count, 10), dtype=np.float32)
    labels = np.zeros(count, dtype=np.int8)
    zero = WorldState((0, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    for i in range(count):
        current = run_actions(zero, histories[i])
        states[i] = np.asarray(current.bits10(), dtype=np.float32)
        labels[i] = reward(run_actions(current, queries[i]))
    return {"histories": histories, "queries": queries, "states": states, "labels": labels}


def encode(rows: dict[str, np.ndarray], arm: str, length: int) -> np.ndarray:
    qpart = onehot_actions(rows["queries"], HORIZON)
    if arm == "T_TRANSCRIPT":
        base = onehot_actions(rows["histories"], length)
    elif arm == "H4_HEURISTIC_LAST4":
        base = onehot_actions(rows["histories"][:, -4:], 4)
    elif arm == "F_FULL_STATE":
        base = rows["states"]
    elif arm == "C_CERTIFIED_STATE":
        base = rows["states"][:, :5]
    elif arm == "I_INVALID_QUOTIENT":
        base = rows["states"][:, :4]
    else:
        raise ValueError(arm)
    return np.concatenate([base.astype(np.float32), qpart], axis=1)


def canonical_text_lengths(rows: dict[str, np.ndarray], arm: str, length: int, sample_n: int = 1024) -> dict[str, float]:
    take = min(sample_n, rows["labels"].shape[0])
    sizes: list[int] = []
    for i in range(take):
        hist = [ACTIONS[int(v)] for v in rows["histories"][i]]
        query = [ACTIONS[int(v)] for v in rows["queries"][i]]
        state = [int(v) for v in rows["states"][i]]
        if arm == "T_TRANSCRIPT":
            text = "history=" + ",".join(hist) + ";query=" + ",".join(query)
        elif arm == "H4_HEURISTIC_LAST4":
            text = "last4=" + ",".join(hist[-4:]) + ";query=" + ",".join(query)
        elif arm == "F_FULL_STATE":
            text = "state=" + "".join(map(str, state)) + ";query=" + ",".join(query)
        elif arm == "C_CERTIFIED_STATE":
            text = "q=" + "".join(map(str, state[:5])) + ";query=" + ",".join(query)
        elif arm == "I_INVALID_QUOTIENT":
            text = "q4=" + "".join(map(str, state[:4])) + ";query=" + ",".join(query)
        else:
            raise ValueError(arm)
        sizes.append(len(text.encode("utf-8")))
    return {"mean_bytes": float(np.mean(sizes)), "max_bytes": int(max(sizes))}


def fit_mlp(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> float:
    clf = MLPClassifier(
        hidden_layer_sizes=(64, 64),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        learning_rate_init=1e-3,
        batch_size=128,
        max_iter=300,
        early_stopping=False,
        random_state=914211,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        clf.fit(x_train, y_train)
    return float(clf.score(x_test, y_test))


def fit_rf(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> float:
    clf = RandomForestClassifier(n_estimators=256, random_state=914213, n_jobs=-1)
    clf.fit(x_train, y_train)
    return float(clf.score(x_test, y_test))


def first_threshold(curve: dict[str, float], threshold: float) -> int | None:
    for n in TRAIN_SIZES:
        if curve[str(n)] >= threshold:
            return n
    return None


def run_learning() -> dict[str, object]:
    results: dict[str, object] = {}
    for length in HISTORY_LENGTHS:
        train = generate_rows(length, max(TRAIN_SIZES), "train")
        test = generate_rows(length, TEST_N, "test")
        length_result: dict[str, object] = {}
        for arm in ALL_ARMS:
            x_all = encode(train, arm, length)
            x_test = encode(test, arm, length)
            y_all = train["labels"]
            y_test = test["labels"]
            curve: dict[str, float] = {}
            for n in TRAIN_SIZES:
                curve[str(n)] = fit_mlp(x_all[:n], y_all[:n], x_test, y_test)
            rf_acc = fit_rf(x_all[: max(TRAIN_SIZES)], y_all[: max(TRAIN_SIZES)], x_test, y_test)
            length_result[arm] = {
                "input_dimension": int(x_all.shape[1]),
                "canonical_text": canonical_text_lengths(test, arm, length),
                "mlp_accuracy": curve,
                "n90": first_threshold(curve, 0.90),
                "n95": first_threshold(curve, 0.95),
                "rf_accuracy_at_16384": rf_acc,
            }
        results[str(length)] = length_result
    return results


def terminal_from(cert: dict[str, object], results: dict[str, object]) -> tuple[str, dict[str, bool]]:
    r32 = results["32"]
    c = r32["C_CERTIFIED_STATE"]
    f = r32["F_FULL_STATE"]
    t = r32["T_TRANSCRIPT"]
    c_acc = float(c["mlp_accuracy"]["16384"])
    f_acc = float(f["mlp_accuracy"]["16384"])
    c_n90 = c["n90"]
    t_n90 = t["n90"]
    if t_n90 is None:
        sample_gate = c_n90 is not None and int(c_n90) <= 4096
    else:
        sample_gate = c_n90 is not None and int(c_n90) <= 0.5 * int(t_n90)
    checks = {
        "certificate_zero_violations": int(cert["certified_violations"]) == 0,
        "invalid_counterexample_found": int(cert["invalid_groups_with_counterexamples"]) > 0,
        "certified_acc_ge_0_95": c_acc >= 0.95,
        "certified_noninferior_full_within_0_01": c_acc >= f_acc - 0.01,
        "sample_efficiency_gate": bool(sample_gate),
        "certified_dimension_smaller_than_full": int(c["input_dimension"]) < int(f["input_dimension"]),
        "transcript_dimension_grows": int(results["8"]["T_TRANSCRIPT"]["input_dimension"]) < int(results["16"]["T_TRANSCRIPT"]["input_dimension"]) < int(results["32"]["T_TRANSCRIPT"]["input_dimension"]),
        "certified_dimension_constant": len({int(results[str(L)]["C_CERTIFIED_STATE"]["input_dimension"]) for L in HISTORY_LENGTHS}) == 1,
    }
    if not checks["certificate_zero_violations"] or not checks["invalid_counterexample_found"]:
        terminal = "INVALID_CERTIFICATE_STAGE"
    elif all(checks.values()):
        terminal = "CERTIFIED_STATE_COMPACTION_ACCESSIBILITY_SUPPORTED"
    else:
        terminal = "CERTIFIED_STATE_EXISTS_BUT_ACCESSIBILITY_GATE_NOT_MET"
    return terminal, checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--certificate-only", action="store_true")
    args = parser.parse_args()

    cert = exact_certificate()
    if args.certificate_only:
        result = {"schema": "ORION.FrontierF2.Certificate.v1", "certificate": cert}
    else:
        learning = run_learning()
        terminal, checks = terminal_from(cert, learning)
        result = {
            "schema": "ORION.FrontierF2.Result.v1",
            "protocol": "F2_CERTIFIED_STATE_COMPACTION_PROTOCOL_V1.md",
            "certificate": cert,
            "history_lengths": list(HISTORY_LENGTHS),
            "train_sizes": list(TRAIN_SIZES),
            "protected_test_n_per_length": TEST_N,
            "results": learning,
            "checks": checks,
            "terminal": terminal,
        }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result if args.certificate_only else {"terminal": result["terminal"], "checks": result["checks"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
