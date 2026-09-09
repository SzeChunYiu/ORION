# Deciding `D_2(C_3^6)` and `D_2(C_3^7)` on LUNARC

Two numbers are worth cluster time. One of them decides a conjecture.

| target | construction gives | closed form predicts | what a clean sweep at that length proves |
|---|---|---|---|
| `D_2(C_3^6)`, length 20 | `≥ 20` | `20` | `D_2(C_3^6) = 20` — a new exact value, and the reduction the rank-7 sweep needs |
| `D_2(C_3^7)`, length 22 | `≥ 22` | `23` | **the closed form is false** |

The rank-7 run is the one that matters. The two candidate answers come from different places — 22 from an exhaustively-searched construction, 23 from a formula whose constants are forced by the rank-two case alone — and exactly one of them is right.

- **A witness at length 22** ⟹ `D_2(C_3^7) ≥ 23`. The closed form survives, and the algebraic construction class is provably *not* extremal above rank three, which is the more interesting outcome for the theory.
- **No witness at length 22** ⟹ `D_2(C_3^7) = 22`, and the closed form `D_k(C_p^r) = (3/2)r(p−1) + (k−2)p + 2` is **false**, despite matching all 25 exact values known today.

The two outcomes cost very different amounts. A witness can turn up in any shard, early; proving none exists needs every shard. Submit rank 7 straight away for that reason — a positive result may arrive long before the sweep completes.

## Order of operations

```bash
./00_build.sh                 # compile both enumerators
sbatch 01_calibrate.sbatch    # THE GATE. writes CALIBRATED.ok. nothing runs before it passes
./submit.sh 6                 # D_2(C_3^6) at length 20, 728 shards
./submit.sh 7                 # D_2(C_3^7) at length 22, 2186 shards
./collect.py results/r6_L20   # verdict, with a coverage proof
./collect.py results/r7_L22
```

Fill in `-A YOUR_PROJECT_HERE` and check `-p cosmos` and the `module load` line against `module avail` before the first submit. Nothing else needs editing: `submit.sh` derives the length, the prune depth and the array size from the rank, so they cannot drift apart.

## Why calibration is not optional

The sweeps answer by *not finding* something. That is worth exactly as much as the search's ability to find something when it is there — and this package adds a new prune that could, if wrong, produce a clean, fast, entirely false zero.

`01_calibrate.sbatch` re-decides every `D_2(C_3^r)` value already known, from both directions, with the new prune on: length 10 and 11 at rank 3, 13 and 14 at rank 4, 16 and 17 at rank 5. Witnesses must appear where they must exist and must not appear where they cannot. It writes `CALIBRATED.ok` only on a clean pass, and `02_sweep.sbatch` refuses to start without that file.

If calibration fails, run the same case with `--nosym`. That flag disables the orbit prune and recovers the previously-validated parent search exactly, which isolates whether the fault is in the new code or somewhere older.

## What the new prune does

The search fixes the first `r` terms as the basis `e_1 … e_r` and enumerates the tail in nondecreasing order. The subgroup of `GL(r,3)` fixing the basis as a set is the symmetric group `S_r`, permuting coordinates — a monomial matrix with any other diagonal entry sends some `e_i` outside the basis. The parent search does not quotient by `S_r` at all, so it walks up to `r!` isomorphic copies of every tail: **720 at rank 6, 5040 at rank 7.**

`enum_rank_sym_v1.c` prunes any node whose tail is not lexicographically least in its `S_r` orbit, tested against the `C(r,2)` transpositions rather than all `r!` permutations — testing a subgroup generating set is still sound and costs `O(r²m)` instead of `O(r! m)` per node.

Soundness, in one line: if some permutation `b` makes `sort(b(T_d)) < T_d` at depth `d`, then `sort(b(T_L)) < T_L` for every completion, because the `d` smallest entries of `b(T_L)` are entrywise at most `sort(b(T_d))`. So a prefix of an orbit's lex-least tail is never pruned, every orbit still reaches a leaf, and `found = 0` here means `found = 0` in the parent search. That is the only direction the upper bound uses.

**Node, leaf and witness counts are therefore smaller than the recorded parent-search counts and are not comparable to them.** Calibration compares verdicts, never tallies.

## Coverage is the thing that can silently go wrong

A killed shard, an array sized differently from `NSHARD`, a half-written scratch file — each leaves a gap that reads exactly like a clean negative. Three guards:

- `02_sweep.sbatch` aborts if `SLURM_ARRAY_TASK_COUNT != NSHARD`, and if the prune depth is not `L − r(p−1) − 1`.
- Each shard writes to scratch and is moved into place atomically, so a partial file never looks finished.
- `collect.py` reports **no verdict at all** until it has seen one `RESULT` line per shard index, taken from the runs' own recorded shard ids rather than from file names.

Resubmitting is safe and cheap: a shard with a `RESULT` line is skipped, so a resubmission after a walltime kill runs only what is missing.

## Sizing

Measured here, on one core, with the negative cases — which are what the sweeps are:

| case | parent search | with orbit prune | speedup | ceiling `r!` |
|---|---|---|---|---|
| rank 3, length 11 | 2,032 nodes | 600 | 3.4× | 6 |
| rank 4, length 14 | 987,944 nodes | 59,497 | **16.6×** | 24 |

So the prune captures roughly 60–70% of its theoretical ceiling, and the ceiling grows as `r!`.
The parent search grew **2764×** from rank 4 to rank 5 (987,944 → 2,730,591,635 nodes).

Extrapolating both trends at a conservative 63% capture gave ~44 core-hours for rank 6 and
~19,000 for rank 7. **The rank-6 figure is already known to be wrong.** Timing complete
single-element shards with a 240 s cap, *every* shard hit the cap without finishing:

| target | shards | measured floor | earlier extrapolation |
|---|---|---|---|
| rank 6, length 20 | 728 | **≥ 49 core-hours** | ~44 — contradicted |
| rank 7, length 22 | 2186 | **≥ 146 core-hours** | ~19,000 — untested |

These are lower bounds, not estimates: nothing finished, so the true cost is somewhere above them
and the ceiling is unmeasured. The rank-7 number is not contradicted, but it comes from the same
extrapolation that just failed one rank lower, so do not size an allocation on it.

**Measure before you queue.** `--maxnodes` makes that exact and bounded:

```bash
./bin/enum_sym 3 6 20 7 --shard 17 728 --maxnodes 5000000   # time this, then scale by nodes
```

Sample several shards, not one — they split on the first free term and subtree sizes vary by
orders of magnitude. A run stopped by `--maxnodes` prints `TRUNCATED` on the RESULT line and warns
on stderr; `collect.py` refuses to take a verdict from one.

Shards are unbalanced — they split on the first free term, and subtree sizes vary a lot — so time
several, not one, and size the walltime off the worst. If a shard threatens the 24 h limit, raise
`NSHARD` rather than the time limit: more, smaller shards schedule better and lose less to a kill,
and `submit.sh` keeps the array bound consistent with it.
