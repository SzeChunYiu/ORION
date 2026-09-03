#!/usr/bin/env python3
"""Derived execution of the frozen R5F DEV leg from chunked-fold checkpoints.

Why this exists (2026-09-03): the DEV leg = max_r5h_mixed_cardinality_development
.main(), which folds BOTH subjects (H4 + N2) via global_frontier and prints a
single terminal marker. Measured twice it is compute-bound beyond a single
job's budget: rc=124 at 9600 s in CI (job cancelled at the 30-minute timeout)
and rc=124 at exactly 28800 s on LUNARC (job 3569846, 8h internal timeout,
zero-byte log, MaxRSS 1.92 GB -- compute-, not memory-bound). The N2 fold
inside it is the SAME fold the SUBJECT revival already chunks
(max_r5h_subject_chunked.py, H4 parity gate in PR #2204): identical
configure_subject -> terms ordering -> WINDOW=12 -> exact_window_frontier ->
combine_frontiers sequence.

This driver revives the DEV leg the same sanctioned way: it replaces ONLY
b.global_frontier with a loader for the chunker's completed per-arm
checkpoints, then calls the UNTOUCHED b.main(). Every downstream computation
(named picks, donor-absorption gate, marker assembly) is the frozen engine's
own code; no module of the frozen family is edited, exactly like the transport
shim discipline of r5fdev_probe.py.

Exactness of the swap:
  * load_checkpoint validates schema/subject/arm identity; the loader
    additionally binds len(terms) (frozen-config drift) and requires
    next_window == total_windows (fold complete).
  * The chunker's window_meta is b's meta ({"start","size",**m,
    "global_frontier_after"} -- b.global_frontier lines 262-264) plus ONE
    instrumentation key "wall_s" the chunker adds. The loader strips exactly
    that key, so the derived window_meta is what the in-process fold would
    have embedded, and json sort_keys makes the marker byte-comparable.
  * The frontier tuple is restored from the checkpoint's serialized states in
    fast_prune's deterministic output order -- the same order the in-process
    fold holds at the same point.

parity-h4 gate (must pass BEFORE any derived N2 result is trusted, mirroring
the SUBJECT gate): chunk H4 into a temp dir, run b.run_subject("H4") live
(fast engine), run it again derived-from-checkpoints, and assert the results
are JSON-identical. H4 completes in ~1-2 min; N2 is the leg that needs the
chain. Run in CI on every touch of this path.

Usage:
    python3 max_r5f_dev_derived.py derive [ckpt_dir]     # both subjects from ckpts
    python3 max_r5f_dev_derived.py parity-h4 [tmpdir]    # live-vs-derived H4 gate
ckpt_dir defaults to $ORIONQ_R5F_DEV_CKPT_DIR or "."; it must hold completed
r5h_chunk_<SUBJECT>_{donor,mixed}.V1.json checkpoints for every subject in
b.SUBJECTS (on LUNARC: fresh H4 chunks ~60 s/arm + the N2 chain's ckpt dir).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import max_r5h_mixed_cardinality_development as b  # noqa: E402
import max_r5h_mixed_cardinality_development_fast as accel  # noqa: E402
import max_r5h_subject_chunked as chunker  # noqa: E402

# The chunker's only meta addition beyond b.global_frontier's own entries.
CHUNKER_META_EXTRA_KEYS = ("wall_s",)

_ORIGINAL_GLOBAL_FRONTIER = b.global_frontier
_CKPT_DIR: dict = {"path": None}


def _strip_chunker_meta(meta: list[dict]) -> list[dict]:
    return [{k: v for k, v in e.items() if k not in CHUNKER_META_EXTRA_KEYS}
            for e in meta]


def _subject_for(terms_len: int, n_qubits: int) -> str:
    matches = [name for name, cfg in b.SUBJECTS.items()
               if cfg["n_qubits"] == n_qubits]
    if len(matches) != 1:
        raise SystemExit(
            f"n_qubits {n_qubits} does not identify a unique subject: {matches}")
    return matches[0]


def _ckpt_global_frontier(terms, n, alphabet):
    """Checkpoint-loading stand-in for b.global_frontier(terms, n, arm)."""
    subject = _subject_for(len(terms), n)
    ck = chunker.load_checkpoint(Path(_CKPT_DIR["path"]), subject, alphabet)
    if ck is None:
        raise SystemExit(
            f"missing checkpoint: subject {subject} arm {alphabet} in {_CKPT_DIR['path']}")
    if ck["next_window"] != ck["total_windows"]:
        raise SystemExit(
            f"incomplete fold: subject {subject} arm {alphabet} "
            f"next_window {ck['next_window']} != total {ck['total_windows']}")
    if ck["terms"] != len(terms):
        raise SystemExit(
            f"checkpoint frozen-config drift: subject {subject} arm {alphabet} "
            f"ckpt terms {ck['terms']} != live terms {len(terms)}")
    front = tuple(chunker._state_from_dict(s) for s in ck["frontier"])
    return front, _strip_chunker_meta(ck["window_meta"])


def _install_ckpt_patch(ckpt_dir: Path) -> None:
    _CKPT_DIR["path"] = str(ckpt_dir)
    b.global_frontier = _ckpt_global_frontier


def _install_live_engine() -> None:
    """Fast engine for the live in-process fold (same patch run_chunk applies)."""
    b.prune = accel.fast_prune
    b.combine_frontiers = accel.fast_combine_frontiers
    b.global_frontier = _ORIGINAL_GLOBAL_FRONTIER


def _chunk_subject_h4(ckpt_dir: Path) -> None:
    chunk_windows = int(os.environ.get("ORIONQ_R5H_CHUNK_WINDOWS",
                                       chunker.CHUNK_WINDOWS_DEFAULT))
    saturation = int(os.environ.get("ORIONQ_R5H_SATURATION",
                                    chunker.SATURATION_DEFAULT))
    for arm in ("donor", "mixed"):
        # run_chunk is one chunk per call by design (a job each on LUNARC);
        # drive it to completion here so the whole H4 fold is checkpointed.
        while True:
            rep = chunker.run_chunk("H4", arm, ckpt_dir, chunk_windows, saturation)
            if rep["next_window"] == rep["total_windows"]:
                break
        print(f"PARITY_H4_CHUNK arm={arm} {json.dumps(rep, sort_keys=True)}")


def derive(ckpt_dir: Path):
    """Emit the frozen DEV marker with frontiers sourced from checkpoints."""
    _install_ckpt_patch(ckpt_dir)
    return b.main()  # frozen engine prints ORIONQ_MAX_R5H_DEV= itself


def parity_h4(tmpdir: Path) -> int:
    """Live-vs-derived gate on H4: identical results required field-for-field."""
    tmpdir.mkdir(parents=True, exist_ok=True)
    _chunk_subject_h4(tmpdir)

    _install_live_engine()
    live = b.run_subject("H4", b.SUBJECTS["H4"])

    _install_ckpt_patch(tmpdir)
    derived = b.run_subject("H4", b.SUBJECTS["H4"])

    live_json = json.dumps(live, sort_keys=True)
    derived_json = json.dumps(derived, sort_keys=True)
    ok = live_json == derived_json
    print(f"ORIONQ_R5F_DEV_DERIVED_PARITY={'PASS' if ok else 'FAIL'} "
          f"live_bytes={len(live_json)} derived_bytes={len(derived_json)} "
          f"frontiers={live['donor_direct_frontier_size']}/{live['mixed_frontier_size']}")
    if not ok:
        print(f"LIVE={live_json}", file=sys.stderr)
        print(f"DERIVED={derived_json}", file=sys.stderr)
    return 0 if ok else 1


def main() -> int:
    argv = sys.argv[1:]
    usage = ("usage: max_r5f_dev_derived.py derive [ckpt_dir] "
             "| parity-h4 [tmpdir]")
    if not argv or len(argv) > 2 or argv[0] not in ("derive", "parity-h4"):
        raise SystemExit(usage)
    default_dir = os.environ.get("ORIONQ_R5F_DEV_CKPT_DIR", ".")
    target = Path(argv[1] if len(argv) > 1 else default_dir)
    if argv[0] == "derive":
        derive(target)
        return 0
    return parity_h4(target)


if __name__ == "__main__":
    raise SystemExit(main())
