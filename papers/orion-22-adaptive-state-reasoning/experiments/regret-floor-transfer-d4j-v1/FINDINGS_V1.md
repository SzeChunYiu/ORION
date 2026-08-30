# ORION-22 regret-floor transfer to Defects4J — findings V1

**Terminal: `REGRET_FLOOR_LAW_TRANSFERS`.**

## The prediction, made before the protected half was read

`PREDICTIONS_V1.json` (SHA-256 `5fc333c32bc101a2eeaa02afa0f528010fcdfa95c5dca93055296dbc9b8b3195`)
was written from the prediction half alone: pooled forced regret **23 of 297
bugs**, a floor rate of **0.0774**, Clopper–Pearson 95% interval
**[0.0497, 0.1139]**.

The protected half then gave **19 of 300 = 0.0633** — inside the interval. The
exact aliasing law's magnitude transfers from a quantum/combinatorial family to
software revalidation scheduling, a family sharing nothing with it but the shape
of the observation channel.

| project | bugs | classes | floor | positive-regret | max class floor | refined floor | heuristic regret |
|---|---|---|---|---|---|---|---|
| Chart | 13 | 9 | 0 | 0 | 0 | 0 | 1 |
| Cli | 20 | 3 | 4 | 1 | 4 | 4 | 6 |
| Closure | 87 | 6 | 1 | 1 | 1 | 0 | 3 |
| Codec | 9 | 2 | 0 | 0 | 0 | 0 | 0 |
| Collections | 14 | 8 | 0 | 0 | 0 | 0 | 0 |
| Compress | 24 | 7 | 1 | 1 | 1 | 1 | 1 |
| Csv | 8 | 1 | 0 | 0 | 0 | 0 | 0 |
| Gson | 9 | 4 | 4 | 3 | 2 | 1 | 7 |
| Lang | 31 | 11 | 0 | 0 | 0 | 0 | 0 |
| Math | 53 | 28 | 3 | 3 | 1 | 1 | 5 |
| Mockito | 19 | 9 | 6 | 6 | 1 | 3 | 11 |
| Time | 13 | 4 | 0 | 0 | 0 | 0 | 0 |
| **total** | **300** | **92** | **19** | **15** | **4** | **10** | **34** |

The required contrast holds with room to spare: **77 zero-regret classes and 15
positive-regret classes.** Refinement takes the total floor from 19 to 10 with
**zero monotonicity violations**, and the oracle sits at 0 by construction. The
strongest heuristic — schedule the test package whose name best matches the
modified class's package, using no outcome statistics — incurs **34**, nearly
twice the coarse floor, so aliasing is not the binding constraint for a rule that
ignores the data.

## The first run said the law failed, and it was my checker

The first execution returned `REGRET_FLOOR_LAW_FAILS_ON_D4J` on 5 "exactly-when"
violations. All five had the same shape and three of them had a coarse floor of
**zero** — a class already caught entirely by one action, where refinement cannot
possibly decrease anything. A violation that claims a zero-floor class should have
strictly decreased is not a fact about the world.

The cause: the checker compared **one argmax per sub-class**. When a sub-class has
several tied optimal actions, tie-breaking can hand back a different representative
than a neighbouring sub-class that shares one of them, and the two are then
reported as disagreeing when they do not. The theorem's own condition is a
**common** optimal action, so the correct test is whether the sub-classes' optimal
*sets* intersect. That is what the checker now does.

`PREDICTIONS_V1.json` is byte-identical across both runs (same SHA-256 above): the
fix touched nothing that had been predicted, and no threshold, alias, refinement
or split moved.

The checker was then falsification-tested rather than merely re-run:

- six synthetic fibres with known ground truth, including three distinct tie
  configurations, all correct;
- a **mutation control** on `[{A:2,B:2},{A:5}]`, where the old argmax rule reports
  impure and the corrected rule reports pure — proving the test discriminates the
  two implementations rather than passing both;
- a **no-alarm assertion on the real data**: every one of the 8 classes where
  refinement strictly decreased is impure, and every one of the 84 where it did
  not is pure. Zero exceptions in either direction.

The last of these is the one that matters. A checker that only confirms its
alarms is a checker that has not been tested; this one is required to stay silent
where it should, on real data, and it does.

## What this does not show

The law is transferred for **one** registered refinement on **one** aliasing
channel. Nothing here establishes it for arbitrary observation channels.

Scheduling a single test package is a deliberately austere decision, chosen so the
regret would be an exact integer count rather than an estimate. It is not a claim
that one-package scheduling is a sensible way to revalidate software; the
heuristic arm's 34 against the oracle's 0 says the opposite.

The protected half is 300 bugs across 12 projects, and four projects contribute a
floor of zero. The pooled interval is what carries the quantitative claim; no
per-project floor here is individually well-powered.
