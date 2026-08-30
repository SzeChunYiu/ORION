# ORION-05 compute provenance: where the C1 landscape was produced, and what it may support

## The constraint, and where it was not met

`run_stage1_control_discovery_v2.py` carries, in its module docstring:

> **HARD CONSTRAINT** (inherited from the v1 compute plan): no control or census solve
> runs on the Mac. Local use is limited to `--smoke`, which performs zero solver
> instances. **Every solving mode here is LUNARC-only.**

Two clauses. The first was met — no solve ran on the Mac at any point. **The second was
not.** The C1 landscape in `results/` was produced on the remote host `billy-old`, not on
LUNARC. That host is not the Mac, so the first clause is satisfied on its face, but
"every solving mode here is LUNARC-only" excludes it as well.

This is recorded rather than quietly resolved, because a reader of the artifact reads the
constraint, not the operating instruction that conflicted with it.

## What this does and does not affect

**Does not affect any claim.** The run's own terminal is `PARTIAL_SCAN_INCOMPLETE`, and
the emitted record states plainly that it *"means the scan ran out of budget and is NOT
evidence for O05-C2 or against O05-C3; it asserts nothing."* Only **18 of 33,755** rows
have both C1 and C2, `first_three_positives` is empty, and no positive control was frozen.
Nothing downstream rests on it, so the provenance defect cannot have propagated into a
claim.

**Does affect reusability.** The C1 landscape (33,755 rows, all `OK`, zero
TIMEOUT/ERROR, 15.28 core-hours) is real measured data, but under the constraint as
written it is **not admissible as Stage-1 evidence**. It should be treated as a cost
model and a feasibility probe, not as census output. If it is wanted as evidence, the
constraint must first be amended deliberately, or the pass repeated on LUNARC.

## The cost model it does support

This is the durable value of the run, and it is independent of where it ran:

| quantity | measured |
|---|---:|
| C1 solves | 33,755, all `OK`, 0 TIMEOUT/ERROR |
| C1 total | 15.28 core-hours |
| C1 slowest | 5.83 s |
| C2 solves timed | 84 |
| C2 median / mean | **2,007 s / 2,186 s** |
| C2 hitting the 3,600 s cap | **10 (12%)** |
| C2 under 600 s | **0** |
| full-domain C2, extrapolated | **~21,878 core-hours (lower bound)** |

Two features matter more than the headline. **No C2 solve finished under 600 s**, so the
cost is uniformly high rather than a prunable tail — there is no cheap majority to skim.
And **12% hit the timeout without finishing**, so the extrapolation is a floor, and some
rows may not terminate at all.

## Consequence for planning

Before any large allocation, the 10 capped rows should be re-run with a long wall clock.
If they are hard-but-finite, a faster runtime lands them; if any are unbounded, no amount
of hardware helps and the protocol's `CANNOT_CHECK` path applies instead. That triage is
cheap and decides whether the job is finite.

## On accelerating it

The solver imports only `dataclasses`, `itertools` and `typing` — **zero**
numpy/torch/cupy/scipy references and **zero** float literals. The hot path is nested
`itertools.combinations`/`product` over Pauli pairs with branch-and-bound pruning. That is
scalar integer work with data-dependent branching: **GPU acceleration does not apply**.

The plausible levers are a JIT (PyPy) and more CPU cores, in that order. **The PyPy
speedup is currently unmeasured** — an attempt here was abandoned because the default
mode runs C2 rather than the cheap C1 pass, so even 25 candidates exceeded the benchmark
window. It should be measured on LUNARC, where solving is permitted, as the first task of
any allocation.
