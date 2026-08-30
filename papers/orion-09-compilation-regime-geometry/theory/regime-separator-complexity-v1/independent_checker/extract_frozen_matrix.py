#!/usr/bin/env python3
"""Independent replay: regenerate the frozen L3 feature matrix and labels for
ORION-09 stage 1, and reproduce the receipt's stage-1 statistics from scratch.

This is an INDEPENDENT REPLAY in the sense required by issue #1609 section B:
the committed generating modules are imported unmodified and their SHA-256 is
verified against the receipt before use, but every stage-1 statistic reported
here is recomputed from the regenerated matrix rather than read from the
receipt. The receipt is then compared, not trusted.

Nothing is written outside this packet. The frozen receipt is read-only.

Outputs
    FROZEN_MATRIX.json   feature matrix + labels + cell structure (packet-local)
    REPLAY_REPORT.json   recomputed stage-1 statistics vs the receipt

Exit codes
    0  replay reproduced the receipt's stage-1 statistics exactly
    2  a recomputed statistic disagrees with the receipt
    3  could not run (missing module, hash drift)  -- CANNOT_CHECK
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parent.parent                    # papers/orion-09-compilation-regime-geometry
ROOT = PAPER.parent.parent                      # repository root
QG = ROOT / "research/extensions/orion-qg"
RECEIPT = PAPER / "evidence/R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json"

WMAX = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(code: int, **kw):
    print(json.dumps({"status": "CANNOT_CHECK" if code == 3 else "FAIL", **kw}, indent=2))
    return code


# --- state block: transcribed from the frozen protocol, not imported ----------
# The 41-feature sign-aware block is defined in
# R2_N2_STABPREP_L3_VOCABULARY_PROTOCOL_V1.md. It is reimplemented here from the
# protocol text so that the replay does not depend on the runner script; the
# primitives _sof/_xof/_zof come from the committed, hash-verified module.
def state_block(q15, state, n):
    rows = [(q15._sof(e, n), q15._xof(e, n), q15._zof(e, n)) for e in state]
    neg = sum(1 for s, _, _ in rows if s)
    pw = [0] * (WMAX + 1); nw = [0] * (WMAX + 1)
    py = [0] * (WMAX + 1); ny = [0] * (WMAX + 1)
    pq = [0] * 4; nq = [0] * 4
    for s, x, z in rows:
        w = bin(x | z).count("1"); y = bin(x & z).count("1")
        (nw if s else pw)[w] += 1
        (ny if s else py)[y] += 1
        (nq if s else pq)[(x & 1) | ((z & 1) << 1)] += 1
    cols_x, cols_y, cols_z = [], [], []
    for j in range(n):
        cols_x.append(sum(1 for _, x, z in rows if (x >> j) & 1 and not ((z >> j) & 1)))
        cols_y.append(sum(1 for _, x, z in rows if (x >> j) & 1 and ((z >> j) & 1)))
        cols_z.append(sum(1 for _, x, z in rows if ((z >> j) & 1) and not ((x >> j) & 1)))

    def stats4(xs):
        return (min(xs) if xs else 0, max(xs) if xs else 0,
                sum(v * v for v in xs), sum(1 for v in xs if v == 0))

    vec = [neg] + pw + nw + py + ny + pq + nq
    for cs in (cols_x, cols_y, cols_z):
        vec.extend(stats4(cs))
    assert len(vec) == 41, len(vec)
    return tuple(vec)


def main() -> int:
    if not RECEIPT.is_file():
        return fail(3, error=f"receipt missing: {RECEIPT}")
    receipt = json.loads(RECEIPT.read_text())

    modules = {
        "qg15_third_family": QG / "qg15_third_family.py",
        "qg15c_vocabulary": QG / "qg15c_vocabulary.py",
        "qg15c_enlarged_vocab": QG / "qg15c_enlarged_vocab.py",
    }
    drift = {}
    for name, path in modules.items():
        if not path.is_file():
            return fail(3, error=f"module missing: {path}")
        got = sha256(path)
        want = receipt["modules_sha256"][name]
        if got != want:
            drift[name] = {"receipt": want, "worktree": got}
    if drift:
        return fail(3, error="committed module hash drift; replay would not be of "
                             "the frozen object", drift=drift)

    sys.path.insert(0, str(QG))
    try:
        import qg15_third_family as q15
        import qg15c_vocabulary as v15c
        from qg15c_enlarged_vocab import donor_path_features
    except Exception as exc:                                    # noqa: BLE001
        return fail(3, error=f"import failed: {type(exc).__name__}: {exc}")

    t0 = time.perf_counter()
    rows, per_n = [], {}
    for n in (1, 2, 3):
        dist = q15.referee(n)
        exact = 0
        for state in sorted(dist):
            v1, v2, cd, lb, costs = v15c.feature_vectors(state, n)
            _, _, _, dis = q15.donor(state, n)
            vec = v2 + tuple(donor_path_features(dis, n)) + state_block(q15, state, n)
            lab = dist[state] == cd
            exact += int(lab)
            rows.append((vec, lab))
        per_n[str(n)] = {"instances": len(dist), "donor_exact": exact,
                         "expected": q15.expected_count(n)}
        print(f"[replay] n={n} done  {time.perf_counter()-t0:.1f}s", file=sys.stderr)

    # --- cell structure, recomputed from definition --------------------------
    cells: dict[tuple, list[int]] = {}
    for vec, lab in rows:
        c = cells.setdefault(vec, [0, 0])
        c[0 if lab else 1] += 1
    mixed = [(v, c) for v, c in cells.items() if c[0] and c[1]]
    floor = sum(min(c[0], c[1]) for _, c in mixed)
    singletons = sum(1 for c in cells.values() if c[0] + c[1] == 1)
    n_inst = len(rows)
    feature_count = len(rows[0][0])

    recomputed = {
        "instances": n_inst,
        "feature_count": feature_count,
        "unique_feature_cells": len(cells),
        "singleton_cells": singletons,
        "mixed_cell_count": len(mixed),
        "irreducible_error_floor": floor,
        "compression_ratio_cells_over_instances": round(len(cells) / n_inst, 6),
        "domain": per_n,
    }
    s1 = receipt["stage1"]
    compared = ["instances", "feature_count", "unique_feature_cells",
                "singleton_cells", "mixed_cell_count", "irreducible_error_floor",
                "compression_ratio_cells_over_instances", "domain"]
    mismatches = {k: {"receipt": s1.get(k), "replay": recomputed[k]}
                  for k in compared if s1.get(k) != recomputed[k]}

    (PACKET / "FROZEN_MATRIX.json").write_text(json.dumps({
        "schema": "ORION.ORION09.RegimeSeparatorComplexity.FrozenMatrix.v1",
        "provenance": "regenerated from hash-verified committed modules",
        "modules_sha256": {k: sha256(v) for k, v in modules.items()},
        "feature_count": feature_count,
        "instances": n_inst,
        "labels": [int(lab) for _, lab in rows],
        "matrix": [list(vec) for vec, _ in rows],
    }, separators=(",", ":")) + "\n")

    report = {
        "schema": "ORION.ORION09.RegimeSeparatorComplexity.ReplayReport.v1",
        "independent_replay": "statistics recomputed from regenerated matrix; "
                              "receipt compared, not trusted",
        "module_hashes_match_receipt": True,
        "protocol_sha256_matches_receipt":
            sha256(PAPER / "evidence/R2_N2_STABPREP_L3_VOCABULARY_PROTOCOL_V1.md")
            == receipt["protocol_sha256"],
        "recomputed_stage1": recomputed,
        "receipt_stage1_compared_fields": compared,
        "mismatches": mismatches,
        "elapsed_seconds": round(time.perf_counter() - t0, 1),
        "status": "PASS" if not mismatches else "FAIL",
    }
    (PACKET / "REPLAY_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "recomputed_stage1", "mismatches",
                       "protocol_sha256_matches_receipt")}, indent=2))
    return 0 if not mismatches else 2


if __name__ == "__main__":
    sys.exit(main())
