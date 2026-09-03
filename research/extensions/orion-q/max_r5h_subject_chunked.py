#!/usr/bin/env python3
"""Window-chunked exact runner for frozen MAX-R5H subject semantics.

Revival instrument for the N2 budget-hit (job 3569287, rc=124 at exactly 28800 s
with a zero-byte log: run_subject prints a single terminal marker, so the log
proves the run was still computing -- not crashed, not pareto-saturated).

One-stage attribution (2026-09-03, sizing on LUNARC):
  H4  268 terms, 8 qubits, 23 windows -> frontier 4249/5150, 58.3 s (CI receipt).
  N2  614 terms, 12 qubits, 52 windows -> frontier unbounded within 8 h.
  The failing stage is global_frontier's per-window combine+prune
  (O(|front| x |window|) constructions + O(n x keep) dominance); every other
  stage (parse, Jordan-Wigner, named selection) is seconds.

This script changes NO frozen semantics. It drives the identical
configure_subject -> terms ordering -> WINDOW=12 slices -> exact_window_frontier
-> combine_frontiers sequence, but:
  * processes only windows [next_window, next_window+chunk_windows) per job,
  * serializes the exact combined frontier as a JSON checkpoint after every
    window (State tuples round-trip exactly through json floats/ints),
  * records per-window wall seconds so a single window exceeding the chunk
    budget is MEASURED, not guessed (evidence for the next lever: exact prune
    acceleration).

Parameters (no unexplained constants; defaults justified below):
  ORIONQ_R5H_CHUNK_WINDOWS  windows per chunk job. Default 6: H4 realized
    ~2.5 s/window at frontier <= 5150; N2 is 2.29x terms at 12 qubits, so the
    default assumes <= ~30 min/window late-window cost -> <= 3 h/chunk, inside
    the 8 h job cap with 2.6x headroom. Shrink if a chunk times out; the
    checkpoint resumes from the last completed window either way.
  ORIONQ_R5H_SATURATION     frontier raise guard, mirrors the frozen engine's
    200000 (pareto_saturation) RuntimeError; kept identical by default.

Exactness proof of the chunking: global_frontier is a left fold over windows,
  front_0 = (empty,); front_k = combine(front_{k-1}, local_k),
and each chunk reproduces the same fold suffix from the serialized frontier --
State is a frozen dataclass of floats/ints/tuples, so json round-trip is
value-exact and the fold output is a pure function of (front_{k-1}, window).
The terminal marker is byte-compatible with max_r5h_subject_fast.py (same
schema, authority, subject, result), plus one extra top-level "chunked"
provenance key the receipt builder ignores.

H4 parity gate (must pass BEFORE any N2 chunk is trusted): re-run H4 chunked
and require the result dict to equal the frozen CI receipt's result
(probe_H4.log / committed CI artifact) field-for-field.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import max_r5h_mixed_cardinality_development as b
import max_r5h_mixed_cardinality_development_fast as accel

CHECKPOINT_SCHEMA = "ORIONQ.MAXR5H.SubjectChunk.V1"
CHUNK_WINDOWS_DEFAULT = 6          # justified in module docstring
SATURATION_DEFAULT = 200000        # frozen engine guard, unchanged


def _state_to_dict(s: b.State) -> dict:
    return {
        "lam": s.lam, "cnot": s.cnot, "t": s.t, "blocks": s.blocks,
        "ancilla": s.ancilla,
        "partition": [[kind, list(idx)] for kind, idx in s.partition],
    }


def _state_from_dict(d: dict) -> b.State:
    return b.State(
        float(d["lam"]), int(d["cnot"]), int(d["t"]), int(d["blocks"]),
        int(d["ancilla"]),
        tuple((kind, tuple(idx)) for kind, idx in d["partition"]),
    )


def chunk_paths(ckpt_dir: Path, subject: str, arm: str):
    stem = f"r5h_chunk_{subject}_{arm}"
    return stem, ckpt_dir / f"{stem}.V1.json"


def load_checkpoint(ckpt_dir: Path, subject: str, arm: str):
    _stem, path = chunk_paths(ckpt_dir, subject, arm)
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("schema") != CHECKPOINT_SCHEMA or d.get("subject") != subject or d.get("arm") != arm:
        raise SystemExit(f"checkpoint identity mismatch: {path}")
    return d


def run_chunk(subject: str, arm: str, ckpt_dir: Path, chunk_windows: int, saturation: int):
    b.prune = accel.fast_prune
    b.combine_frontiers = accel.fast_combine_frontiers

    cfg = b.SUBJECTS[subject]
    b.configure_subject(cfg)
    text = b.h.fetch_source()
    one, two = b.h.parse_ducc(text)
    paulis, max_imag = b.h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    total_windows = (len(terms) + b.WINDOW - 1) // b.WINDOW

    ck = load_checkpoint(ckpt_dir, subject, arm)
    if ck is None:
        next_window = 0
        front: tuple[b.State, ...] = (b.State(0.0, 0, 0, 0, 0, tuple()),)
        meta: list[dict] = []
    else:
        if ck["total_windows"] != total_windows or ck["terms"] != len(terms) or ck["window"] != b.WINDOW:
            raise SystemExit("checkpoint frozen-config drift (terms/window/total)")
        next_window = ck["next_window"]
        front = tuple(_state_from_dict(s) for s in ck["frontier"])
        meta = ck["window_meta"]

    if next_window >= total_windows:
        return {"status": "already_complete", "next_window": next_window,
                "total_windows": total_windows, "frontier_size": len(front)}

    end = min(next_window + chunk_windows, total_windows)
    arm_t0 = time.time()
    w = next_window
    for w in range(next_window, end):
        t0 = time.time()
        sub = terms[w * b.WINDOW:min((w + 1) * b.WINDOW, len(terms))]
        lf, m = b.exact_window_frontier(sub, cfg["n_qubits"], w * b.WINDOW, arm)
        front = b.combine_frontiers(front, lf)
        if len(front) > saturation:
            raise RuntimeError({"pareto_saturation": len(front), "arm": arm, "window": w})
        wall = time.time() - t0
        meta = meta + [{"start": w * b.WINDOW, "size": len(sub), **m,
                        "global_frontier_after": len(front), "wall_s": round(wall, 3)}]
        _stem, path = chunk_paths(ckpt_dir, subject, arm)
        path.write_text(json.dumps({
            "schema": CHECKPOINT_SCHEMA, "subject": subject, "arm": arm,
            "terms": len(terms), "window": b.WINDOW,
            "total_windows": total_windows, "next_window": w + 1,
            "frontier": [_state_to_dict(s) for s in front],
            "window_meta": meta,
        }, sort_keys=True), encoding="utf-8")

    return {"status": "chunk_done", "next_window": w + 1, "total_windows": total_windows,
            "frontier_size": len(front), "chunk_wall_s": round(time.time() - arm_t0, 3),
            "last_window_walls_s": [m["wall_s"] for m in meta[-chunk_windows:]]}


def finalize(ckpt_dir: Path, subject: str):
    """Both arms complete -> run the frozen tail (named picks) and emit the
    SubjectFast.v1 marker, byte-compatible with max_r5h_subject_fast.py."""
    cfg = b.SUBJECTS[subject]
    b.configure_subject(cfg)
    text = b.h.fetch_source()
    one, two = b.h.parse_ducc(text)
    paulis, max_imag = b.h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))

    fronts = {}
    metas = {}
    for arm in ("donor", "mixed"):
        ck = load_checkpoint(ckpt_dir, subject, arm)
        if ck is None or ck["next_window"] != ck["total_windows"]:
            raise SystemExit(f"arm {arm} not complete")
        fronts[arm] = tuple(_state_from_dict(s) for s in ck["frontier"])
        metas[arm] = ck["window_meta"]

    b0 = b.pauli_lcu(terms)
    b1 = b.pair_reference_state(cfg)
    b2 = b.pick_named(fronts["donor"], b1)
    b3 = b.pick_named(fronts["mixed"], b1)
    bal = b3["P_BALANCED"]
    donor_bal = b2["P_BALANCED"]
    mixed_value = bal is not None and b.uses_tare(bal) and not any(
        b.same_resource(bal, d) for d in fronts["donor"])
    result = {
        "subject": subject, "source_blob": cfg["blob"], "n_qubits": cfg["n_qubits"],
        "terms": len(terms), "max_imag": max_imag,
        "B0_Pauli_LCU": b.serialize(b0), "B1_R5G_pair_reference": b.serialize(b1),
        "donor_direct_frontier_size": len(fronts["donor"]),
        "mixed_frontier_size": len(fronts["mixed"]),
        "donor_window_meta": metas["donor"], "mixed_window_meta": metas["mixed"],
        "B2_donor_named": {k: (None if v is None else b.serialize(v)) for k, v in b2.items()},
        "B3_mixed_named": {k: (None if v is None else b.serialize(v)) for k, v in b3.items()},
        "mixed_balanced_uses_TARE": b.uses_tare(bal),
        "mixed_balanced_distinct_from_all_donor_resources": bool(mixed_value),
        "r5h_subject_development_pass": bool(mixed_value),
    }
    out = {
        "schema": "ORIONQ.MAXR5H.SubjectFast.v1",
        "authority": "DEVELOPMENT_ONLY__FROZEN_R5H_SEMANTICS",
        "subject": subject,
        "result": result,
        "chunked": {"instrument": "max_r5h_subject_chunked.py",
                    "checkpoint_schema": CHECKPOINT_SCHEMA},
    }
    print("ORIONQ_MAX_R5H_SUBJECT=" + json.dumps(out, sort_keys=True))
    return out


def main() -> int:
    argv = sys.argv[1:]
    mode = argv[0] if argv else ""
    usage = ("usage: max_r5h_subject_chunked.py chunk SUBJECT ARM [ckpt_dir] "
             "| finalize SUBJECT [ckpt_dir] | parity-h4 [ckpt_dir]")
    if not argv or len(argv) > 4:
        raise SystemExit(usage)
    if mode == "chunk" and len(argv) < 3:
        raise SystemExit(usage)
    if mode == "finalize" and len(argv) < 2:
        raise SystemExit(usage)
    if mode == "parity-h4" and len(argv) > 2:
        raise SystemExit(usage)
    if mode == "chunk":
        ckpt_dir = Path(argv[3] if len(argv) > 3 else os.environ.get("ORIONQ_R5H_CKPT_DIR", "."))
    elif mode == "parity-h4":
        ckpt_dir = Path(argv[1] if len(argv) > 1 else os.environ.get("ORIONQ_R5H_CKPT_DIR", "."))
    else:
        ckpt_dir = Path(argv[2] if len(argv) > 2 else os.environ.get("ORIONQ_R5H_CKPT_DIR", "."))
    chunk_windows = int(os.environ.get("ORIONQ_R5H_CHUNK_WINDOWS", CHUNK_WINDOWS_DEFAULT))
    saturation = int(os.environ.get("ORIONQ_R5H_SATURATION", SATURATION_DEFAULT))
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    if mode == "chunk":
        report = run_chunk(argv[1], argv[2], ckpt_dir, chunk_windows, saturation)
    elif mode == "finalize":
        finalize(ckpt_dir, argv[1])
        return 0
    elif mode == "parity-h4":
        finalize(ckpt_dir, "H4")
        return 0
    else:
        raise SystemExit(f"unknown mode {mode}")
    print("CHUNK_REPORT=" + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
