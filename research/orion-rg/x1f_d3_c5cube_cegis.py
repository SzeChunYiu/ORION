#!/usr/bin/env python3
"""Prospectively frozen counterexample-first CEGIS search for D_3(C_5^3)>25.

Scientific target
-----------------
Find a length-25 multiset S over C_5^3 with no three pairwise-disjoint
nonempty zero-sum submultisets.  A positive candidate is an exact obstruction
and must be independently replayed.  Failure to find one is only a bounded
negative unless an independent proof certifies the accumulated master cover.

Method
------
* Master MILP chooses multiplicities x_g summing to 25 and containing a fixed
  standard basis.  Rank<=2 candidates are donor-closed, so GL(3,5) lets us fix
  one basis in every rank-3 orbit.
* Oracle MILP seeks three disjoint zero-sum submultisets of x.
* A found packing has total usage vector w.  Every x' >= w componentwise has
  the same packing, so the master receives the exact monotone disjunctive cut
  'x is not componentwise >= w'.

The script does NOT promote master infeasibility to a theorem.  It serializes
all cuts so a separate verifier/proof route can audit any bounded-negative run.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

P = 5
N = P**3
TARGET_LENGTH = 25
BASIS = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def vec(index: int) -> tuple[int, int, int]:
    return (index // 25, (index // 5) % 5, index % 5)


def idx(v: tuple[int, int, int]) -> int:
    return 25 * v[0] + 5 * v[1] + v[2]


VECTORS = tuple(vec(i) for i in range(N))
BASIS_INDEX = tuple(idx(v) for v in BASIS)


@dataclass(frozen=True)
class PackingCut:
    usage: tuple[int, ...]
    blocks: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]

    def validate(self) -> None:
        if len(self.usage) != N:
            raise ValueError("cut usage length mismatch")
        if any(x < 0 for x in self.usage):
            raise ValueError("negative cut usage")
        summed = [0] * N
        for block in self.blocks:
            if len(block) != N or sum(block) <= 0:
                raise ValueError("invalid zero-sum block")
            total = [0, 0, 0]
            for g, count in enumerate(block):
                if count < 0:
                    raise ValueError("negative block multiplicity")
                summed[g] += count
                v = VECTORS[g]
                for c in range(3):
                    total[c] = (total[c] + count * v[c]) % P
            if total != [0, 0, 0]:
                raise ValueError("block is not zero-sum")
        if tuple(summed) != self.usage:
            raise ValueError("usage != sum of blocks")

    def as_dict(self) -> dict:
        self.validate()
        return {
            "usage": list(self.usage),
            "blocks": [list(block) for block in self.blocks],
        }


def _solve_master(cuts: list[PackingCut], *, time_limit: float):
    # Variables: x_0..x_124 integer in [0,25], followed by one binary blocker
    # for every positive coordinate of every packing cut.
    blocker_rows: list[tuple[int, int]] = []  # (cut index, group index)
    for ci, cut in enumerate(cuts):
        for g, need in enumerate(cut.usage):
            if need > 0:
                blocker_rows.append((ci, g))

    y_offset = N
    nvar = N + len(blocker_rows)
    integrality = np.ones(nvar, dtype=int)
    lb = np.zeros(nvar)
    ub = np.full(nvar, TARGET_LENGTH, dtype=float)
    if blocker_rows:
        ub[y_offset:] = 1.0

    # Objective is deterministic preference only, not scientific evidence.
    objective = np.zeros(nvar)
    objective[:N] = np.arange(N, dtype=float) / (N * N)

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    lo: list[float] = []
    hi: list[float] = []
    row = 0

    # Total length exactly 25.
    for g in range(N):
        rows.append(row); cols.append(g); data.append(1.0)
    lo.append(TARGET_LENGTH); hi.append(TARGET_LENGTH); row += 1

    # Fix one ordered basis occurrence via GL(3,5) symmetry.
    for g in BASIS_INDEX:
        rows.append(row); cols.append(g); data.append(1.0)
        lo.append(1.0); hi.append(np.inf); row += 1

    # Each cut: at least one positive coordinate of usage w must be undersupplied.
    positions_by_cut: dict[int, list[int]] = {ci: [] for ci in range(len(cuts))}
    for pos, (ci, g) in enumerate(blocker_rows):
        positions_by_cut[ci].append(pos)
        need = cuts[ci].usage[g]
        # x_g + M*y <= need-1+M; y=1 forces x_g<=need-1.
        rows.extend((row, row))
        cols.extend((g, y_offset + pos))
        data.extend((1.0, float(TARGET_LENGTH)))
        lo.append(-np.inf)
        hi.append(float(need - 1 + TARGET_LENGTH))
        row += 1
    for ci in range(len(cuts)):
        for pos in positions_by_cut[ci]:
            rows.append(row); cols.append(y_offset + pos); data.append(1.0)
        lo.append(1.0); hi.append(np.inf); row += 1

    A = coo_matrix((data, (rows, cols)), shape=(row, nvar)).tocsr()
    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(A, np.asarray(lo), np.asarray(hi)),
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    return result


def _solve_oracle(counts: tuple[int, ...], *, time_limit: float):
    active = tuple(g for g, count in enumerate(counts) if count > 0)
    m = len(active)
    # z[j,a] integer multiplicity of active type a in zero-sum block j.
    # q[j,c] integer carry for congruence equality sum z*g_c = 5q.
    z_count = 3 * m
    q_offset = z_count
    nvar = z_count + 9
    integrality = np.ones(nvar, dtype=int)
    lb = np.zeros(nvar)
    ub = np.zeros(nvar)
    for j in range(3):
        for a, g in enumerate(active):
            ub[j * m + a] = counts[g]
    ub[q_offset:] = 20.0

    objective = np.zeros(nvar)
    objective[:z_count] = 1.0  # prefer a smaller packing cut

    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    lo: list[float] = []
    hi: list[float] = []
    row = 0

    # Disjointness / available multiplicity.
    for a, g in enumerate(active):
        for j in range(3):
            rows.append(row); cols.append(j * m + a); data.append(1.0)
        lo.append(-np.inf); hi.append(float(counts[g])); row += 1

    # Each block nonempty.
    for j in range(3):
        for a in range(m):
            rows.append(row); cols.append(j * m + a); data.append(1.0)
        lo.append(1.0); hi.append(np.inf); row += 1

    # Three mod-5 coordinate equalities per block.
    for j in range(3):
        for c in range(3):
            for a, g in enumerate(active):
                coeff = VECTORS[g][c]
                if coeff:
                    rows.append(row); cols.append(j * m + a); data.append(float(coeff))
            rows.append(row); cols.append(q_offset + 3 * j + c); data.append(-5.0)
            lo.append(0.0); hi.append(0.0); row += 1

    A = coo_matrix((data, (rows, cols)), shape=(row, nvar)).tocsr()
    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(A, np.asarray(lo), np.asarray(hi)),
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    if not result.success:
        return result, None

    raw = np.rint(result.x[:z_count]).astype(int)
    blocks: list[tuple[int, ...]] = []
    usage = [0] * N
    for j in range(3):
        block = [0] * N
        for a, g in enumerate(active):
            value = int(raw[j * m + a])
            block[g] = value
            usage[g] += value
        blocks.append(tuple(block))
    cut = PackingCut(tuple(usage), tuple(blocks))  # type: ignore[arg-type]
    cut.validate()
    return result, cut


def _candidate_from_result(result) -> tuple[int, ...]:
    if result.x is None:
        raise ValueError("master returned no candidate")
    x = tuple(int(round(v)) for v in result.x[:N])
    if sum(x) != TARGET_LENGTH or any(v < 0 for v in x):
        raise ValueError("invalid master candidate")
    if any(x[g] < 1 for g in BASIS_INDEX):
        raise ValueError("master candidate lost fixed basis")
    return x


def _serialize_candidate(counts: tuple[int, ...]) -> list[dict]:
    return [
        {"vector": list(VECTORS[g]), "multiplicity": count}
        for g, count in enumerate(counts)
        if count
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-iterations", type=int, default=5000)
    parser.add_argument("--master-time-limit", type=float, default=60.0)
    parser.add_argument("--oracle-time-limit", type=float, default=60.0)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    cuts: list[PackingCut] = []
    terminal = "CANNOT_CHECK_RESOURCE_BOUND"
    candidate: tuple[int, ...] | None = None
    detail = "iteration cap reached"

    for iteration in range(args.max_iterations):
        master = _solve_master(cuts, time_limit=args.master_time_limit)
        if master.status == 2:  # HiGHS infeasible
            terminal = "MASTER_INFEASIBLE_BOUNDED_CERTIFICATE_NEEDS_INDEPENDENT_PROOF"
            detail = "accumulated monotone packing cuts cover the symmetry-reduced master according to HiGHS"
            break
        if not master.success:
            terminal = "CANNOT_CHECK_RESOURCE_BOUND"
            detail = f"master failure/status={master.status}: {master.message}"
            break
        counts = _candidate_from_result(master)
        oracle, cut = _solve_oracle(counts, time_limit=args.oracle_time_limit)
        if cut is None:
            if oracle.status == 2:  # exact MIP infeasible for this fixed candidate
                terminal = "LENGTH25_OBSTRUCTION_CANDIDATE_FOUND"
                candidate = counts
                detail = "oracle found no three disjoint zero-sum blocks; independent replay required"
            else:
                terminal = "CANNOT_CHECK_RESOURCE_BOUND"
                detail = f"oracle failure/status={oracle.status}: {oracle.message}"
            break
        cuts.append(cut)

    receipt = {
        "schema": "ORION.RG.X1F.C5CubeD3CEGIS.v1",
        "target": "D_3(C_5^3)",
        "candidate_length": TARGET_LENGTH,
        "terminal": terminal,
        "detail": detail,
        "packing_cuts": len(cuts),
        "candidate": None if candidate is None else _serialize_candidate(candidate),
        "cuts": [cut.as_dict() for cut in cuts],
        "claim_ceiling": "COUNTEREXAMPLE_CANDIDATE_OR_BOUNDED_NEGATIVE_ONLY",
        "exact_D3_authority": False,
        "novelty_authority": False,
    }
    text = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    if args.receipt is not None:
        args.receipt.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
