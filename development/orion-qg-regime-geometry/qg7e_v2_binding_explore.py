#!/usr/bin/env python3
"""Exploratory QG-7e V2 residual->target binding diagnostic.

This is NOT an authority packet. QG-7e V1 already returned CANNOT_CHECK.
The only semantic change from V1 is the parent-residual -> raw-target inverse
for the ja=1 third-block branch-0 letter at coordinate b:

    residual v0b, reference frame Z  => raw target v0b*Z.

Everything else (complete domain, relocation, D+, B' and reference witness
checks) is intentionally reused to derive corrected fingerprints before a
fresh successor protocol is frozen.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(QG))
import qg7e_pp_single_pinner as v1  # noqa: E402


def corrected_visible_targets(ja: int, idx: np.ndarray) -> np.ndarray:
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
    t[:, 1, 0, 0] = u0b
    t[:, 1, 0, 1] = u0a
    t[:, 1, 1, 0] = t21b
    t[:, 1, 1, 1] = t21a
    if ja == 0:
        t[:, 2, 0, 0] = v0b
        t[:, 2, 0, 1] = v1.LM[v0a, v1.Z]
        t[:, 2, 1, 0] = e1b
        t[:, 2, 1, 1] = v1.LM[e1a, v1.X]
    else:
        # T4b env values are residual letters. The ja=1 third block carries
        # frame Z at b and X at b, so both raw targets must invert those frames.
        t[:, 2, 0, 0] = v1.LM[v0b, v1.Z]
        t[:, 2, 0, 1] = v0a
        t[:, 2, 1, 0] = v1.LM[e1b, v1.X]
        t[:, 2, 1, 1] = e1a
    return t


v1.visible_targets = corrected_visible_targets

if __name__ == "__main__":
    raise SystemExit(v1.main())
