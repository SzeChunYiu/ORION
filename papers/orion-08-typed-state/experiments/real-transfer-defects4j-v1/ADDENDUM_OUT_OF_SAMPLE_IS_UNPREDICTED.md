# Out-of-sample transfer fails on 2 of 12, and nothing measured predicts which

**Post-hoc analysis of an already-reported result. No parameter fitted, no terminal
changed.** `FINDINGS_V1.md` reports that fitting per-fibre actions on the training
half and applying them to held-out bugs helps on 10 of 12 projects and fails on
Cli and Csv. Both failures are the two smallest projects, which suggests an obvious
law. This tests it, and it is false.

## The hypothesis

Refinement should transfer out-of-sample when the candidate set is large enough
that fibre statistics are estimable, and fail when it is small. Csv (12 tests) and
Cli (74) are the failures; the hypothesis is that some size threshold separates
them from the rest.

## It does not

| project | \|T\| | train bugs | in-sample gap captured | fibre coverage | transfers |
|---|---|---|---|---|---|
| Csv | 12 | 8 | 0.000 | 1.000 | **no** |
| Codec | 23 | 9 | 0.508 | 1.000 | yes |
| Collections | 25 | 14 | 0.862 | 0.997 | yes |
| Compress | 68 | 23 | 0.482 | 0.997 | yes |
| **Cli** | **74** | **19** | **0.200** | **1.000** | **no** |
| Lang | 77 | 30 | 0.788 | 1.000 | yes |
| Gson | 84 | 9 | 0.202 | 0.999 | yes |
| Time | 121 | 13 | 0.545 | 0.999 | yes |
| Chart | 137 | 13 | 0.575 | 0.997 | yes |
| Closure | 233 | 87 | 0.513 | 1.000 | yes |
| Mockito | 289 | 19 | 0.386 | 0.989 | yes |
| Math | 514 | 53 | 0.605 | 0.998 | yes |

Every candidate predictor is interleaved:

- **candidate-set size** — fails at 12 and **74**, helps at 23 and 68. A threshold
  separating the failures would have to exclude Codec and Compress, which succeed.
- **training bugs** — fails at 8 and **19**, helps at 9 and at 19 (Mockito). The
  same value appears on both sides.
- **fibre coverage** — 1.000 for *both* failures, and as low as 0.989 for a
  success. Held-out rows almost always land in a fibre seen in training, so this is
  not an unseen-fibre problem.
- **in-sample gain** — Cli captures 0.200 of the oracle gap and fails; Gson
  captures **0.202** and succeeds. Two thousandths apart, opposite outcomes.

## What is explained, and what is not

**Csv is fully explained and is not really a failure.** It has no in-sample value
either — predicted none, observed none, 0.000 of the oracle gap. There is nothing
to transfer, so nothing transfers. Counting it as an out-of-sample failure
overstates the problem.

**Cli is a genuine, unexplained failure.** It has real in-sample value
(regret 0.0286 → 0.0229) and loses it out-of-sample (0.0256 → 0.0278 — refinement
makes held-out regret *worse*). No measured property distinguishes it from Gson,
its nearest neighbour on every axis measured here, which transfers.

## Consequence for the claim

The paper may say the typed binding transfers out-of-sample on 10 of 12 projects.
It may **not** say when it will, and this addendum exists so that no one later
reads the two smallest projects failing and infers a size law that the data
refutes. One project overfits for a reason this study does not identify, and
saying so is the honest bound on the result.
