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
./00_build.sh                 # compile the enumerators, and self-check the sampling caps
sbatch 01_calibrate.sbatch    # THE GATE. writes CALIBRATED.ok. nothing runs before it passes
./submit.sh 6                 # D_2(C_3^6) at length 20, 728 units, one per array task
./submit.sh 7                 # D_2(C_3^7) at length 22, 5000 units over 1000 array tasks
./collect.py results/r6_L20   # verdict, with a coverage proof
./collect.py results/r7_L22
```

`-A hep2023-1-3` and `-p hep` are filled in, matching every ORION job this repo has actually
submitted to LUNARC (most recently array job 3550016, 2026-08-28, which ran to `exit 0:0`).
The earlier `-p cosmos` was a placeholder that no submitted job here ever used: COSMOS is the
cluster, not a partition. Check the `module load` line against `module avail` before the first
submit -- that one is still unverified. Nothing else needs editing: `submit.sh` derives the length, the prune depth and the array size from the rank, so they cannot drift apart.

## Why calibration is not optional

The sweeps answer by *not finding* something. That is worth exactly as much as the search's ability to find something when it is there — and this package adds a new prune that could, if wrong, produce a clean, fast, entirely false zero.

`01_calibrate.sbatch` re-decides every `D_2(C_3^r)` value already known, from both directions, with the new prune on: length 10 and 11 at rank 3, 13 and 14 at rank 4, 16 and 17 at rank 5. Witnesses must appear where they must exist and must not appear where they cannot. It then checks that splitting the walk into many units partitions it exactly. It writes `CALIBRATED.ok` only on a clean pass, and `02_sweep.sbatch` refuses to start without that file.

If calibration fails, run the same case with `--nosym`. That flag disables the orbit prune and recovers the previously-validated parent search exactly, which isolates whether the fault is in the new code or somewhere older. `--splitdepth 0` recovers the undivided walk the same way, for a suspected coverage fault rather than a soundness one.

### The two directions cost wildly different amounts

This is worth knowing before you size anything, because the sizing table below is measured **on the negative cases only** and does not transfer:

| case | direction | leaves | wall |
|---|---|---|---|
| `3^4 L=13` | witness | 771,978 | 168 s |
| `3^4 L=14` | none | 624 | 0.2 s |
| `3^5 L=17` | none | **0** | ~80 s (33.7M nodes) |
| `3^5 L=16` | witness | millions | **>11 h, unfinished** |

A "none can exist" check is cheap *because it reaches no leaves at all* — the complement prune kills every branch before depth `L`, so the `O(L·N²)` packing test never runs. A "witness exists" check does reach leaves and pays that test at every one of them.

So the witness half of the gate was never sized, and a 4 h walltime could not pass it. The fix is `--stopfirst`: a witness check needs `found > 0` and nothing else, and the first witness turns up almost immediately — at rank 5 `L=16` it is found at **node 12**, in 0.01 s, versus over half a day to count them all. The gate now runs start to finish in about 80 s. The "none" direction stays exhaustive, which costs nothing extra. Drop `--stopfirst` from `check()` if you ever want the full witness tallies back.

A `--stopfirst` run is marked `TRUNCATED`, because its tallies are partial; `found > 0` still stands on its own and needs no coverage argument, but `collect.py` refuses to build a verdict from such a run.

## What the new prune does

The search fixes the first `r` terms as the basis `e_1 … e_r` and enumerates the tail in nondecreasing order. The subgroup of `GL(r,3)` fixing the basis as a set is the symmetric group `S_r`, permuting coordinates — a monomial matrix with any other diagonal entry sends some `e_i` outside the basis. The parent search does not quotient by `S_r` at all, so it walks up to `r!` isomorphic copies of every tail: **720 at rank 6, 5040 at rank 7.**

`enum_rank_sym_v2.c` — the source `bin/enum_sym` is built from, and the only one implementing
`--maxnodes`/`--maxsecs`; `bin/enum_sym_v1` is kept alongside it for bisection, and the two agree
to the node on every calibration case — prunes any node whose tail is not lexicographically least in its `S_r` orbit, tested against the `C(r,2)` transpositions rather than all `r!` permutations — testing a subgroup generating set is still sound and costs `O(r²m)` instead of `O(r! m)` per node.

Soundness, in one line: if some permutation `b` makes `sort(b(T_d)) < T_d` at depth `d`, then `sort(b(T_L)) < T_L` for every completion, because the `d` smallest entries of `b(T_L)` are entrywise at most `sort(b(T_d))`. So a prefix of an orbit's lex-least tail is never pruned, every orbit still reaches a leaf, and `found = 0` here means `found = 0` in the parent search. That is the only direction the upper bound uses.

**Node, leaf and witness counts are therefore smaller than the recorded parent-search counts and are not comparable to them.** Calibration compares verdicts, never tallies.

## Coverage is the thing that can silently go wrong

A killed shard, an array sized differently from `NSHARD`, a half-written scratch file — each leaves a gap that reads exactly like a clean negative. Three guards:

- `02_sweep.sbatch` aborts if `SLURM_ARRAY_TASK_COUNT != NTASK`, if the prune depth is not `L − r(p−1) − 1`, if `NSHARD < NTASK`, or if a legacy split is asked for more than `N − 1` units.
- `01_calibrate.sbatch` also proves the *split* loses nothing: for three cases it checks that leaves and witnesses summed over many units equal the undivided walk exactly. A split that drops a subtree gives a fast, clean, false zero — the same failure as an unsound prune, from the other direction.
- Each shard writes to scratch and is moved into place atomically, so a partial file never looks finished.
- `collect.py` reports **no verdict at all** until it has seen one `RESULT` line per shard index, taken from the runs' own recorded shard ids rather than from file names.

Resubmitting is safe and cheap: a shard with a `RESULT` line is skipped, so a resubmission after a walltime kill runs only what is missing.

## Sizing

Measured here, on one core, on the negative cases — which are what the sweeps are:

| case | parent search | with orbit prune | speedup | ceiling `r!` | capture |
|---|---|---|---|---|---|
| rank 3, length 11 | 2,032 | 600 | 3.4× | 6 | 57% |
| rank 4, length 14 | 987,944 | 59,497 | 16.6× | 24 | 69% |
| rank 5, length 17 | 2,730,591,587 | 33,758,915 | **80.8×** | 120 | 67% |

Capture sits at about two thirds of `r!` and is not drifting across three ranks, so the
extrapolation has a basis: expect roughly **480×** at rank 6 and **3,400×** at rank 7.

**The rank-5 row also reproduces the recorded sweep exactly.** `D2_C3_5_DECIDED_V6.md` reports
2,730,591,635 nodes summed over 49 shards; the unsharded run here gives 2,730,591,587. The
difference is 48, which is 49 − 1: a sharded run enters the root of the free-term loop once per
shard and counts that node each time. So the two agree to the node, and the recorded 2.73-billion
sweep is independently confirmed.

Note what the pruned tree does that the parent tree does not: the parent grows **2,764×** per rank
step, the pruned tree only **567×**, because the prune strengthens as `r!` does. Extrapolate the
pruned tree, not the parent one:

| target | shards | measured floor | pruned-tree estimate |
|---|---|---|---|
| rank 6, length 20 | 728 | ≥ 49 core-hours | **~51 core-hours** — two routes agree |
| rank 7, length 22 | 2186 | ≥ 146 core-hours | **unknown, plausibly 10⁴–10⁵** |

Rank 6 is solid: an independent extrapolation and a measured floor land within 5% of each other.
Rank 7 is not — length rises by only 2 there rather than 3, so the growth factor is smaller than
567 by an unknown amount, and the honest range spans an order of magnitude. Sample it before
asking for time.

**Measure before you queue — but bound the sample by the clock, not by nodes.**

```bash
./bin/enum_sym 3 7 22 7 --shard 4 2186 --maxsecs 600     # a bound that actually holds
```

`--maxnodes` caps nodes and does **not** bound runtime. Cost is dominated by `two_disjoint()` at
the leaves, which is `O(L*N^2)` per leaf; at rank 7 (`N = 2187`) that is ~1e9 byte-ops, so a leaf
takes on the order of half a second. Measured on one core, rank 7, shard 1:

| cap | wall | reached |
|---|---|---|
| `--maxsecs 10` | 10.8 s | 39 nodes, 23 leaves |
| `--maxsecs 30` | 30.7 s | 90 nodes, 74 leaves |

That is ~2.4 leaves/s and ~3 nodes/s. A `--maxnodes 5000000` sample on this shard would therefore
run for about **19 days** before the cap ever fired. Scale a sample by *leaves*, never by nodes.

Either cap prints `TRUNCATED` on the RESULT line and warns on stderr, and `collect.py` refuses a
verdict from a truncated run.

**Shard cost is decided by the digit structure of the first free term, not by the shard index.**
Shard `i` selects exactly one first free term (`g % NSHARD == i`), so a uniform spread across the
index range is not a sample of the cost distribution. Measured at rank 7, 24 shards, 300 s limit:

| shards | outcome |
|---|---|
| 4, 5, 13, 17, 40 | exceed 300 s, no upper bound established |
| 2, 6, 8, 2000 | 1 node, 0.3 s |
| 3, 10, 22, 30, 55, 75, 100, 137, 200, 300, 500, 800, 1200, 1600, 2185 | 542–2004 nodes, 0.3 s |

About a fifth are heavy and the rest are trivial. Note that 137, 733, 1500 and 2185 all finish in
under a second: sampling those four and extrapolating gives an answer that is wrong by orders of
magnitude. Sample the heavy shards (4, 5, 13, 17, 40 are known heavy) and size off those.

## Why rank 7 is split at depth 10

Splitting on the first free term has a hard ceiling of `N - 1 = 3^r - 1` units, and those units are
wildly unbalanced. Both facts are measured, not assumed, and together they made the rank-7 sweep
unable to finish at all:

- The ceiling is a ceiling, not a default. Asking for more than `N - 1` units yields units with no
  first free term to work on (1 node, nothing to do), so "raise `NSHARD` rather than the time
  limit" was not available. The enumerator now refuses such a request outright instead of silently
  handing out empty units.
- At ~2.4 leaves/s a 24 h job covers ~207,000 leaves, and resubmission only skips units that wrote
  a `RESULT` line. A unit too big for one job therefore restarts from scratch every time and never
  completes, and `collect.py` reports `INCOMPLETE` forever — correct behaviour reporting an
  unfinishable plan.

So `--splitdepth D` splits on the subtrees rooted at depth `D` instead. Measured unit counts at
rank 7, `L = 22`:

| split depth | work units | prefix walk per unit |
|---|---|---|
| 8 (`r+1`) | 2,060 | 0.3 s |
| 9 | 2,837 | 24 s |
| **10** | **662,129** | **55 s** |
| 11 and deeper | >10⁶ | exceeds 120 s — the walk alone |

`submit.sh 7` uses depth 10 and deals those 662,129 subtrees round-robin across 5000 units, so each
unit holds roughly `1/5000` of the total work drawn from all over the tree rather than one
monolithic subtree. `NSHARD` (work units, what coverage is proved against) is decoupled from
`NTASK` (array tasks, 1000 of them), so the unit count can exceed the cluster's `MaxArraySize`.
Rank 6 keeps the legacy split: 728 units at ~4 min each need none of this.

The price is that every unit re-walks the tree above depth 10 first — ~55 s, about 76 core-hours
across the sweep, a few percent of the total, and the reason depth 11 is not used. Node counts are
inflated by that replicated prefix and `collect.py` labels them so; leaves and witnesses live
strictly below the split depth and still sum exactly.

Walltime for rank 7 is `4-00:00:00`. The `hep` partition has allowed that (job 3550016), so the
24 h default in `02_sweep.sbatch` was a choice rather than a limit.
